"""
实时监控预警服务

整合系统各类预警信息，提供统一的监控和预警功能：
- 设备校准预警
- 样品龄期预警
- 任务超期预警
- 质量异常预警
- 系统运行状态监控
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from django.db import models
from django.utils import timezone
from django.core.cache import cache


class AlertLevel(Enum):
    """预警级别"""
    INFO = 'info'       # 信息提示
    WARNING = 'warning' # 一般预警
    CRITICAL = 'critical'  # 紧急预警
    EMERGENCY = 'emergency'  # 紧急事件


class AlertType(Enum):
    """预警类型"""
    # 设备相关
    EQUIPMENT_CALIBRATION = 'equipment_calibration'  # 设备校准到期
    EQUIPMENT_FAULT = 'equipment_fault'  # 设备故障
    
    # 样品相关
    SAMPLE_AGING = 'sample_aging'  # 样品龄期到期
    SAMPLE_OVERDUE = 'sample_overdue'  # 样品超期
    SAMPLE_RETENTION = 'sample_retention'  # 样品留样到期
    
    # 任务相关
    TASK_OVERDUE = 'task_overdue'  # 任务超期
    TASK_PENDING = 'task_pending'  # 任务待处理
    
    # 报告相关
    REPORT_PENDING = 'report_pending'  # 报告待审批
    REPORT_OVERDUE = 'report_overdue'  # 报告超期
    
    # 质量相关
    QUALITY_NONCONFORMITY = 'quality_nonconformity'  # 不符合项
    QUALITY_ACTION_OVERDUE = 'quality_action_overdue'  # 纠正措施超期
    
    # 系统相关
    SYSTEM_ERROR = 'system_error'  # 系统错误
    SYSTEM_STORAGE = 'system_storage'  # 存储空间不足


@dataclass
class AlertItem:
    """预警项"""
    alert_type: AlertType
    level: AlertLevel
    title: str
    message: str
    source: str  # 来源模块
    source_id: Optional[int] = None  # 来源对象ID
    source_no: Optional[str] = None  # 来源对象编号
    created_at: datetime = field(default_factory=timezone.now)
    expires_at: Optional[datetime] = None  # 过期时间
    action_url: Optional[str] = None  # 处理链接
    action_text: Optional[str] = None  # 处理按钮文本
    is_handled: bool = False
    handled_by: Optional[str] = None
    handled_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'alert_type': self.alert_type.value,
            'level': self.level.value,
            'level_display': self.level.name,
            'title': self.title,
            'message': self.message,
            'source': self.source,
            'source_id': self.source_id,
            'source_no': self.source_no,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'action_url': self.action_url,
            'action_text': self.action_text,
            'is_handled': self.is_handled,
            'handled_by': self.handled_by,
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
        }


class MonitoringService:
    """实时监控服务"""
    
    CACHE_KEY_PREFIX = 'limis:monitoring:'
    CACHE_TIMEOUT = 300  # 5分钟缓存
    
    @classmethod
    def get_all_alerts(cls, include_handled: bool = False) -> List[AlertItem]:
        """
        获取所有预警
        
        :param include_handled: 是否包含已处理的
        :return: 预警列表
        """
        alerts = []
        
        # 设备校准预警
        alerts.extend(cls._get_calibration_alerts())
        
        # 样品龄期预警
        alerts.extend(cls._get_aging_alerts())
        
        # 任务超期预警
        alerts.extend(cls._get_task_alerts())
        
        # 报告预警
        alerts.extend(cls._get_report_alerts())
        
        # 质量预警
        alerts.extend(cls._get_quality_alerts())
        
        # 按级别和创建时间排序
        level_order = {'emergency': 0, 'critical': 1, 'warning': 2, 'info': 3}
        alerts.sort(key=lambda x: (level_order.get(x.level.value, 4), -x.created_at.timestamp()))
        
        if not include_handled:
            alerts = [a for a in alerts if not a.is_handled]
        
        return alerts
    
    @classmethod
    def get_alerts_by_level(cls, level: AlertLevel) -> List[AlertItem]:
        """按级别获取预警"""
        return [a for a in cls.get_all_alerts() if a.level == level]
    
    @classmethod
    def get_alerts_by_type(cls, alert_type: AlertType) -> List[AlertItem]:
        """按类型获取预警"""
        return [a for a in cls.get_all_alerts() if a.alert_type == alert_type]
    
    @classmethod
    def get_alert_summary(cls) -> Dict[str, Any]:
        """
        获取预警摘要
        
        :return: 摘要统计
        """
        alerts = cls.get_all_alerts()
        
        summary = {
            'total_count': len(alerts),
            'emergency_count': len([a for a in alerts if a.level == AlertLevel.EMERGENCY]),
            'critical_count': len([a for a in alerts if a.level == AlertLevel.CRITICAL]),
            'warning_count': len([a for a in alerts if a.level == AlertLevel.WARNING]),
            'info_count': len([a for a in alerts if a.level == AlertLevel.INFO]),
            'by_type': {},
            'last_updated': timezone.now().isoformat(),
        }
        
        # 按类型统计
        for alert in alerts:
            type_key = alert.alert_type.value
            if type_key not in summary['by_type']:
                summary['by_type'][type_key] = 0
            summary['by_type'][type_key] += 1
        
        return summary
    
    @classmethod
    def _get_calibration_alerts(cls) -> List[AlertItem]:
        """获取设备校准预警"""
        from core.services.calibration_alert import CalibrationAlertService
        
        alerts = []
        
        # 获取过期设备
        expired = CalibrationAlertService.get_expired_equipment()
        for item in expired:
            alerts.append(AlertItem(
                alert_type=AlertType.EQUIPMENT_CALIBRATION,
                level=AlertLevel.EMERGENCY,
                title='设备校准已过期',
                message=f'{item["equipment_no"]} {item["name"]} 校准已过期，设备不可使用',
                source='equipment',
                source_id=item['equipment_id'],
                source_no=item['equipment_no'],
                action_url=f'/equipment/{item["equipment_id"]}',
                action_text='安排校准',
            ))
        
        # 获取紧急设备（7天内到期）
        critical = CalibrationAlertService.get_critical_equipment()
        for item in critical:
            if item['status'] != 'expired':  # 排除已过期的
                alerts.append(AlertItem(
                    alert_type=AlertType.EQUIPMENT_CALIBRATION,
                    level=AlertLevel.CRITICAL,
                    title='设备校准即将到期',
                    message=f'{item["equipment_no"]} {item["name"]} {item["message"]}',
                    source='equipment',
                    source_id=item['equipment_id'],
                    source_no=item['equipment_no'],
                    action_url=f'/equipment/{item["equipment_id"]}',
                    action_text='安排校准',
                ))
        
        return alerts
    
    @classmethod
    def _get_aging_alerts(cls) -> List[AlertItem]:
        """获取样品龄期预警"""
        from core.age_management import AgeManagementService
        
        alerts = []
        
        due_samples = AgeManagementService.get_due_samples(days_threshold=7)
        
        for item in due_samples:
            level = AlertLevel.EMERGENCY if item['remaining_days'] < 0 else \
                    AlertLevel.CRITICAL if item['remaining_days'] <= 1 else \
                    AlertLevel.WARNING
            
            alerts.append(AlertItem(
                alert_type=AlertType.SAMPLE_AGING,
                level=level,
                title='样品龄期到期',
                message=f'{item["sample"].sample_no} {item["sample"].name} {item["status"]["message"]}',
                source='sample',
                source_id=item['sample'].id,
                source_no=item['sample'].sample_no,
                action_url=f'/samples/{item["sample"].id}',
                action_text='安排检测',
            ))
        
        return alerts
    
    @classmethod
    def _get_task_alerts(cls) -> List[AlertItem]:
        """获取任务超期预警"""
        from apps.testing.models import TestTask
        
        alerts = []
        
        today = timezone.now().date()
        
        # 获取超期任务
        overdue_tasks = TestTask.objects.filter(
            status__in=['assigned', 'in_progress'],
            deadline__lt=today,
        ).select_related('sample', 'test_method')
        
        for task in overdue_tasks[:20]:  # 最多显示20个
            overdue_days = (today - task.deadline).days
            
            alerts.append(AlertItem(
                alert_type=AlertType.TASK_OVERDUE,
                level=AlertLevel.CRITICAL if overdue_days > 3 else AlertLevel.WARNING,
                title='检测任务超期',
                message=f'{task.task_no} 已超期 {overdue_days} 天',
                source='testing',
                source_id=task.id,
                source_no=task.task_no,
                action_url=f'/testing/tasks/{task.id}',
                action_text='查看任务',
            ))
        
        return alerts
    
    @classmethod
    def _get_report_alerts(cls) -> List[AlertItem]:
        """获取报告预警"""
        from apps.reports.models import Report
        
        alerts = []
        
        # 获取待审批报告
        pending_reports = Report.objects.filter(
            status__in=['draft', 'pending_review', 'pending_approval'],
        ).count()
        
        if pending_reports > 10:
            alerts.append(AlertItem(
                alert_type=AlertType.REPORT_PENDING,
                level=AlertLevel.WARNING,
                title='报告待审批',
                message=f'当前有 {pending_reports} 份报告待审批',
                source='reports',
                action_url='/reports',
                action_text='查看报告',
            ))
        
        # 获取超期报告（超过承诺期限）
        overdue_reports = Report.objects.filter(
            status__in=['draft', 'pending_review', 'pending_approval'],
            promised_date__lt=timezone.now().date(),
        ).select_related('commission')
        
        for report in overdue_reports[:10]:
            alerts.append(AlertItem(
                alert_type=AlertType.REPORT_OVERDUE,
                level=AlertLevel.CRITICAL,
                title='报告超期',
                message=f'{report.report_no} 已超过承诺期限',
                source='reports',
                source_id=report.id,
                source_no=report.report_no,
                action_url=f'/reports/{report.id}',
                action_text='处理报告',
            ))
        
        return alerts
    
    @classmethod
    def _get_quality_alerts(cls) -> List[AlertItem]:
        """获取质量预警"""
        from apps.quality.models import CorrectiveAction
        
        alerts = []
        
        # 获取超期纠正措施
        overdue_actions = CorrectiveAction.objects.filter(
            status__in=['open', 'in_progress'],
            deadline__lt=timezone.now().date(),
        ).select_related('finding', 'finding__audit')
        
        for action in overdue_actions[:10]:
            alerts.append(AlertItem(
                alert_type=AlertType.QUALITY_ACTION_OVERDUE,
                level=AlertLevel.CRITICAL,
                title='纠正措施超期',
                message=f'{action.finding.audit.audit_no} 的纠正措施已超期',
                source='quality',
                source_id=action.id,
                action_url=f'/quality/actions/{action.id}',
                action_text='处理措施',
            ))
        
        return alerts
    
    @classmethod
    def get_dashboard_data(cls) -> Dict[str, Any]:
        """
        获取仪表盘数据
        
        :return: 仪表盘数据
        """
        # 尝试从缓存获取
        cache_key = cls.CACHE_KEY_PREFIX + 'dashboard'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        data = {
            'alerts': cls.get_alert_summary(),
            'statistics': cls._get_statistics(),
            'trends': cls._get_trends(),
        }
        
        # 缓存5分钟
        cache.set(cache_key, data, cls.CACHE_TIMEOUT)
        
        return data
    
    @classmethod
    def _get_statistics(cls) -> Dict[str, Any]:
        """获取统计数据"""
        from apps.commissions.models import Commission
        from apps.samples.models import Sample
        from apps.testing.models import TestTask
        from apps.reports.models import Report
        
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        
        stats = {
            'commissions': {
                'total': Commission.objects.filter(is_deleted=False).count(),
                'this_month': Commission.objects.filter(
                    created_at__date__gte=this_month_start, is_deleted=False
                ).count(),
                'pending': Commission.objects.filter(
                    status='pending_review', is_deleted=False
                ).count(),
            },
            'samples': {
                'total': Sample.objects.filter(is_deleted=False).count(),
                'this_month': Sample.objects.filter(
                    created_at__date__gte=this_month_start, is_deleted=False
                ).count(),
                'testing': Sample.objects.filter(
                    status='testing', is_deleted=False
                ).count(),
            },
            'tasks': {
                'total': TestTask.objects.count(),
                'pending': TestTask.objects.filter(
                    status__in=['assigned', 'in_progress']
                ).count(),
                'overdue': TestTask.objects.filter(
                    status__in=['assigned', 'in_progress'],
                    deadline__lt=today,
                ).count(),
            },
            'reports': {
                'total': Report.objects.filter(is_deleted=False).count(),
                'this_month': Report.objects.filter(
                    created_at__date__gte=this_month_start, is_deleted=False
                ).count(),
                'pending': Report.objects.filter(
                    status__in=['draft', 'pending_review', 'pending_approval'],
                    is_deleted=False
                ).count(),
            },
        }
        
        return stats
    
    @classmethod
    def _get_trends(cls) -> Dict[str, Any]:
        """获取趋势数据（最近7天）"""
        from apps.commissions.models import Commission
        from apps.reports.models import Report
        
        trends = {
            'commissions': [],
            'reports': [],
        }
        
        today = timezone.now().date()
        
        for i in range(7):
            date = today - timedelta(days=i)
            
            trends['commissions'].append({
                'date': date.isoformat(),
                'count': Commission.objects.filter(
                    created_at__date=date, is_deleted=False
                ).count(),
            })
            
            trends['reports'].append({
                'date': date.isoformat(),
                'count': Report.objects.filter(
                    created_at__date=date, is_deleted=False
                ).count(),
            })
        
        return trends
    
    @classmethod
    def refresh_cache(cls) -> None:
        """刷新缓存"""
        cache_key = cls.CACHE_KEY_PREFIX + 'dashboard'
        cache.delete(cache_key)
        cls.get_dashboard_data()


class AlertNotificationService:
    """预警通知服务"""
    
    @classmethod
    def send_alert_notifications(cls) -> Dict[str, Any]:
        """
        发送预警通知
        
        :return: 发送结果
        """
        from apps.system.models import Notification, User
        
        results = {
            'sent': 0,
            'recipients': [],
            'errors': [],
        }
        
        # 获取紧急和严重级别的预警
        alerts = MonitoringService.get_alerts_by_level(AlertLevel.EMERGENCY) + \
                 MonitoringService.get_alerts_by_level(AlertLevel.CRITICAL)
        
        if not alerts:
            return results
        
        # 获取需要通知的用户
        recipients = User.objects.filter(
            roles__code__in=['admin', 'tech_director', 'quality_director'],
            is_active=True,
        ).distinct()
        
        if not recipients:
            return results
        
        # 构建通知内容
        message = cls._build_alert_message(alerts)
        
        for user in recipients:
            try:
                Notification.objects.create(
                    recipient=user,
                    notification_type='system',
                    title='系统预警通知',
                    content=message,
                    link_path='/monitoring',
                )
                results['sent'] += 1
                results['recipients'].append(str(user))
            except Exception as e:
                results['errors'].append(str(e))
        
        return results
    
    @classmethod
    def _build_alert_message(cls, alerts: List[AlertItem]) -> str:
        """构建预警消息"""
        lines = ['系统当前有以下预警需要处理：\n']
        
        for alert in alerts[:10]:
            lines.append(f'- [{alert.level.name}] {alert.title}: {alert.message}')
        
        if len(alerts) > 10:
            lines.append(f'\n... 还有 {len(alerts) - 10} 项预警')
        
        lines.append('\n请登录系统查看详情并及时处理。')
        
        return '\n'.join(lines)