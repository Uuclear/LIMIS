"""
设备校准到期预警服务

设备校准管理是实验室质量保证的重要环节：
- 跟踪设备校准有效期
- 提前预警即将到期设备
- 自动标记过期设备
- 发送通知提醒
"""

from datetime import datetime, timedelta, date
from typing import Optional, list
from dataclasses import dataclass

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


@dataclass
class CalibrationStatus:
    """校准状态"""
    status: str
    status_display: str
    color: str
    message: str
    remaining_days: int


class CalibrationAlertService:
    """设备校准预警服务"""
    
    # 预警阈值配置（天数）
    WARNING_THRESHOLD = 30  # 提前30天预警
    CRITICAL_THRESHOLD = 7  # 提前7天紧急预警
    
    @classmethod
    def get_calibration_status(cls, calibration_expiry: date, current_date: date = None) -> CalibrationStatus:
        """
        获取校准状态
        
        :param calibration_expiry: 校准有效期
        :param current_date: 当前日期
        :return: 校准状态
        """
        if current_date is None:
            current_date = timezone.now().date()
        
        if not calibration_expiry:
            return CalibrationStatus(
                status='unknown',
                status_display='未知',
                color='info',
                message='校准信息缺失',
                remaining_days=0,
            )
        
        remaining_days = (calibration_expiry - current_date).days
        
        if remaining_days < 0:
            return CalibrationStatus(
                status='expired',
                status_display='已过期',
                color='danger',
                message=f'已过期 {abs(remaining_days)} 天，设备不可使用',
                remaining_days=remaining_days,
            )
        elif remaining_days == 0:
            return CalibrationStatus(
                status='expiring_today',
                status_display='今日到期',
                color='danger',
                message='今日到期，请立即安排校准',
                remaining_days=0,
            )
        elif remaining_days <= cls.CRITICAL_THRESHOLD:
            return CalibrationStatus(
                status='critical',
                status_display='紧急',
                color='danger',
                message=f'{remaining_days} 天后到期，请立即安排校准',
                remaining_days=remaining_days,
            )
        elif remaining_days <= cls.WARNING_THRESHOLD:
            return CalibrationStatus(
                status='warning',
                status_display='预警',
                color='warning',
                message=f'{remaining_days} 天后到期，请安排校准',
                remaining_days=remaining_days,
            )
        else:
            return CalibrationStatus(
                status='valid',
                status_display='有效',
                color='success',
                message=f'校准有效，{remaining_days} 天后到期',
                remaining_days=remaining_days,
            )
    
    @classmethod
    def get_expiring_equipment(cls, days_threshold: int = None) -> list[dict]:
        """
        获取即将到期或已过期的设备
        
        :param days_threshold: 天数阈值（默认使用WARNING_THRESHOLD）
        :return: 设备列表
        """
        from apps.equipment.models import Equipment
        
        if days_threshold is None:
            days_threshold = cls.WARNING_THRESHOLD
        
        today = timezone.now().date()
        threshold_date = today + timedelta(days=days_threshold)
        
        # 查询有校准有效期且即将到期或已过期的设备
        equipment = Equipment.objects.filter(
            calibration_expiry__isnull=False,
            is_active=True,
        ).select_related('category')
        
        expiring_list = []
        for equip in equipment:
            status = cls.get_calibration_status(equip.calibration_expiry)
            
            if status.remaining_days <= days_threshold:
                expiring_list.append({
                    'equipment': equip,
                    'equipment_id': equip.id,
                    'equipment_no': equip.equipment_no,
                    'name': equip.name,
                    'category': str(equip.category) if equip.category else '',
                    'calibration_expiry': equip.calibration_expiry,
                    'remaining_days': status.remaining_days,
                    'status': status.status,
                    'status_display': status.status_display,
                    'color': status.color,
                    'message': status.message,
                })
        
        # 按剩余天数排序
        expiring_list.sort(key=lambda x: x['remaining_days'])
        
        return expiring_list
    
    @classmethod
    def get_expired_equipment(cls) -> list:
        """
        获取已过期的设备
        
        :return: 过期设备列表
        """
        return [item for item in cls.get_expiring_equipment() if item['status'] == 'expired']
    
    @classmethod
    def get_critical_equipment(cls) -> list:
        """
        获取紧急状态的设备（7天内到期）
        
        :return: 紧急设备列表
        """
        return [item for item in cls.get_expiring_equipment(cls.CRITICAL_THRESHOLD) 
                if item['status'] in ('critical', 'expiring_today', 'expired')]
    
    @classmethod
    def generate_calibration_report(cls) -> dict:
        """
        生成校准状态报告
        
        :return: 报告数据
        """
        all_equipment = cls.get_expiring_equipment(days_threshold=365)  # 获取一年内的
        
        report = {
            'generated_at': timezone.now(),
            'total_count': len(all_equipment),
            'expired': [],
            'critical': [],
            'warning': [],
            'valid': [],
            'summary': {},
        }
        
        for item in all_equipment:
            status = item['status']
            if status == 'expired':
                report['expired'].append(item)
            elif status in ('critical', 'expiring_today'):
                report['critical'].append(item)
            elif status == 'warning':
                report['warning'].append(item)
            else:
                report['valid'].append(item)
        
        report['summary'] = {
            'expired_count': len(report['expired']),
            'critical_count': len(report['critical']),
            'warning_count': len(report['warning']),
            'valid_count': len(report['valid']),
        }
        
        return report
    
    @classmethod
    def send_calibration_alerts(cls, force: bool = False) -> dict:
        """
        发送校准预警通知
        
        :param force: 是否强制发送（忽略已发送标记）
        :return: 发送结果
        """
        from apps.system.models import Notification, User
        
        results = {
            'sent_count': 0,
            'recipients': [],
            'errors': [],
        }
        
        # 获取需要预警的设备
        critical_equipment = cls.get_critical_equipment()
        warning_equipment = [item for item in cls.get_expiring_equipment(cls.WARNING_THRESHOLD)
                           if item['status'] == 'warning']
        
        if not critical_equipment and not warning_equipment:
            return results
        
        # 获取设备管理员和技术负责人
        recipients = User.objects.filter(
            roles__code__in=['equip_manager', 'tech_director', 'admin'],
            is_active=True,
        ).distinct()
        
        if not recipients:
            return results
        
        # 发送紧急预警
        if critical_equipment:
            message = cls._build_critical_message(critical_equipment)
            for user in recipients:
                try:
                    Notification.objects.create(
                        recipient=user,
                        notification_type='equipment_expiring',
                        title='设备校准紧急预警',
                        content=message,
                        link_path='/equipment/calibration',
                    )
                    results['sent_count'] += 1
                    results['recipients'].append(user.username)
                except Exception as e:
                    results['errors'].append(str(e))
        
        # 发送普通预警
        if warning_equipment:
            message = cls._build_warning_message(warning_equipment)
            for user in recipients:
                try:
                    Notification.objects.create(
                        recipient=user,
                        notification_type='equipment_expiring',
                        title='设备校准到期提醒',
                        content=message,
                        link_path='/equipment/calibration',
                    )
                    results['sent_count'] += 1
                except Exception as e:
                    results['errors'].append(str(e))
        
        return results
    
    @classmethod
    def _build_critical_message(cls, equipment_list: list) -> str:
        """构建紧急预警消息"""
        lines = ['以下设备校准即将到期或已过期，请立即处理：\n']
        
        for item in equipment_list[:10]:  # 最多显示10个
            lines.append(f"- {item['equipment_no']} {item['name']}: {item['message']}")
        
        if len(equipment_list) > 10:
            lines.append(f"\n... 还有 {len(equipment_list) - 10} 台设备")
        
        lines.append('\n请登录系统查看详情并安排校准。')
        
        return '\n'.join(lines)
    
    @classmethod
    def _build_warning_message(cls, equipment_list: list) -> str:
        """构建普通预警消息"""
        lines = ['以下设备校准将在30天内到期，请提前安排：\n']
        
        for item in equipment_list[:10]:
            lines.append(f"- {item['equipment_no']} {item['name']}: {item['remaining_days']}天后到期")
        
        if len(equipment_list) > 10:
            lines.append(f"\n... 还有 {len(equipment_list) - 10} 台设备")
        
        return '\n'.join(lines)
    
    @classmethod
    def check_equipment_availability(cls, equipment) -> bool:
        """
        检查设备是否可用于检测
        
        :param equipment: 设备对象
        :return: 是否可用
        """
        if not equipment.calibration_expiry:
            return False
        
        status = cls.get_calibration_status(equipment.calibration_expiry)
        
        # 过期设备不可使用
        if status.status in ('expired', 'expiring_today'):
            return False
        
        return True
    
    @classmethod
    def get_available_equipment_for_test(cls, test_method) -> list:
        """
        获取可用于指定检测方法的设备
        
        :param test_method: 检测方法
        :return: 可用设备列表
        """
        from apps.equipment.models import Equipment
        
        equipment = Equipment.objects.filter(
            test_methods__contains=[test_method.id] if hasattr(test_method, 'id') else [],
            is_active=True,
            calibration_expiry__isnull=False,
        )
        
        available = []
        for equip in equipment:
            if cls.check_equipment_availability(equip):
                available.append(equip)
        
        return available


class CalibrationMixin(models.Model):
    """
    校准混入模型
    可用于设备模型
    """
    
    calibration_date = models.DateField(
        null=True, blank=True,
        verbose_name='校准日期',
    )
    calibration_expiry = models.DateField(
        null=True, blank=True,
        verbose_name='校准有效期',
    )
    calibration_certificate = models.CharField(
        max_length=100, blank=True,
        verbose_name='校准证书编号',
    )
    calibration_organization = models.CharField(
        max_length=200, blank=True,
        verbose_name='校准机构',
    )
    calibration_cycle = models.IntegerField(
        default=12,
        verbose_name='校准周期(月)',
    )
    
    class Meta:
        abstract = True
    
    def get_calibration_status(self) -> CalibrationStatus:
        """获取校准状态"""
        return CalibrationAlertService.get_calibration_status(self.calibration_expiry)
    
    def is_calibration_valid(self) -> bool:
        """检查校准是否有效"""
        return CalibrationAlertService.check_equipment_availability(self)
    
    def update_calibration(self, calibration_date: date, certificate_no: str = '', organization: str = ''):
        """
        更新校准信息
        
        :param calibration_date: 校准日期
        :param certificate_no: 证书编号
        :param organization: 校准机构
        """
        self.calibration_date = calibration_date
        self.calibration_certificate = certificate_no
        self.calibration_organization = organization
        
        # 根据校准周期计算有效期
        expiry_date = calibration_date + timedelta(days=self.calibration_cycle * 30)
        self.calibration_expiry = expiry_date
        
        self.save(update_fields=[
            'calibration_date', 'calibration_expiry',
            'calibration_certificate', 'calibration_organization',
        ])
    
    def schedule_calibration(self, scheduled_date: date):
        """安排校准"""
        # 可以创建校准计划记录
        pass