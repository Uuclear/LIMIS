"""
龄期管理服务

龄期管理是混凝土检测的重要功能：
- 跟踪样品的龄期（如7天、28天）
- 提醒到期检测
- 自动计算到期日期
"""

from datetime import datetime, timedelta, date
from typing import Optional, list
from dataclasses import dataclass

from django.db import models
from django.utils import timezone


@dataclass
class AgePeriod:
    """龄期定义"""
    days: int
    name: str
    description: str
    is_standard: bool = False  # 是否标准龄期


# 标准龄期定义
STANDARD_AGE_PERIODS = [
    AgePeriod(3, '3天', '3天龄期', False),
    AgePeriod(7, '7天', '7天龄期', True),
    AgePeriod(14, '14天', '14天龄期', False),
    AgePeriod(28, '28天', '28天标准龄期', True),
    AgePeriod(56, '56天', '56天龄期', False),
    AgePeriod(60, '60天', '60天龄期', False),
    AgePeriod(90, '90天', '90天龄期', False),
]


class AgeManagementService:
    """龄期管理服务"""
    
    # 默认龄期配置
    DEFAULT_AGE_PERIODS = [3, 7, 28]  # 混凝土常用龄期
    
    @classmethod
    def calculate_due_date(cls, sampling_date: date, age_days: int) -> date:
        """
        计算到期日期
        
        :param sampling_date: 取样日期
        :param age_days: 龄期天数
        :return: 到期日期
        """
        return sampling_date + timedelta(days=age_days)
    
    @classmethod
    def get_remaining_days(cls, due_date: date, current_date: date = None) -> int:
        """
        获取剩余天数
        
        :param due_date: 到期日期
        :param current_date: 当前日期（默认今天）
        :return: 剩余天数（负数表示已过期）
        """
        if current_date is None:
            current_date = timezone.now().date()
        
        delta = due_date - current_date
        return delta.days
    
    @classmethod
    def get_age_status(cls, remaining_days: int) -> dict:
        """
        获取龄期状态
        
        :param remaining_days: 剩余天数
        :return: 状态信息
        """
        if remaining_days < 0:
            return {
                'status': 'overdue',
                'status_display': '已过期',
                'color': 'danger',
                'message': f'已过期 {abs(remaining_days)} 天',
            }
        elif remaining_days == 0:
            return {
                'status': 'due_today',
                'status_display': '今日到期',
                'color': 'warning',
                'message': '今日到期，请及时检测',
            }
        elif remaining_days <= 3:
            return {
                'status': 'due_soon',
                'status_display': '即将到期',
                'color': 'warning',
                'message': f'{remaining_days} 天后到期',
            }
        elif remaining_days <= 7:
            return {
                'status': 'approaching',
                'status_display': '临近到期',
                'color': 'info',
                'message': f'{remaining_days} 天后到期',
            }
        else:
            return {
                'status': 'pending',
                'status_display': '待检测',
                'color': 'success',
                'message': f'{remaining_days} 天后到期',
            }
    
    @classmethod
    def get_age_periods_for_sample(cls, sample_type: str) -> list[AgePeriod]:
        """
        根据样品类型获取适用的龄期
        
        :param sample_type: 样品类型
        :return: 龄期列表
        """
        # 根据样品类型返回不同的龄期配置
        if sample_type in ('concrete', '混凝土'):
            return [p for p in STANDARD_AGE_PERIODS if p.days in (7, 28)]
        elif sample_type in ('cement', '水泥'):
            return [p for p in STANDARD_AGE_PERIODS if p.days in (3, 7, 28)]
        elif sample_type in ('mortar', '砂浆'):
            return [p for p in STANDARD_AGE_PERIODS if p.days in (7, 28)]
        else:
            return [p for p in STANDARD_AGE_PERIODS if p.is_standard]
    
    @classmethod
    def create_age_schedule(cls, sample, age_days: list[int] = None) -> list[dict]:
        """
        创建龄期检测计划
        
        :param sample: 样品对象
        :param age_days: 龄期天数列表（默认使用标准龄期）
        :return: 龄期计划列表
        """
        if age_days is None:
            age_days = cls.DEFAULT_AGE_PERIODS
        
        sampling_date = sample.sampling_date
        if not sampling_date:
            sampling_date = sample.created_at.date()
        
        schedules = []
        for days in age_days:
            due_date = cls.calculate_due_date(sampling_date, days)
            remaining = cls.get_remaining_days(due_date)
            status = cls.get_age_status(remaining)
            
            schedules.append({
                'age_days': days,
                'due_date': due_date,
                'remaining_days': remaining,
                'status': status['status'],
                'status_display': status['status_display'],
                'color': status['color'],
                'message': status['message'],
                'is_completed': False,  # 是否已完成检测
            })
        
        return schedules
    
    @classmethod
    def get_due_samples(cls, days_threshold: int = 7) -> list:
        """
        获取即将到期或已过期的样品
        
        :param days_threshold: 天数阈值（默认7天内）
        :return: 样品列表
        """
        from apps.samples.models import Sample
        
        today = timezone.now().date()
        threshold_date = today + timedelta(days=days_threshold)
        
        # 查询有龄期要求且未完成检测的样品
        # 这里假设样品有age_days字段记录龄期要求
        samples = Sample.objects.filter(
            status__in=['received', 'testing'],
            sampling_date__isnull=False,
        ).select_related('commission')
        
        due_samples = []
        for sample in samples:
            # 获取样品的龄期计划
            age_days = sample.age_days or cls.DEFAULT_AGE_PERIODS
            
            for days in age_days:
                due_date = cls.calculate_due_date(sample.sampling_date, days)
                remaining = cls.get_remaining_days(due_date)
                
                if remaining <= days_threshold:
                    due_samples.append({
                        'sample': sample,
                        'age_days': days,
                        'due_date': due_date,
                        'remaining_days': remaining,
                        'status': cls.get_age_status(remaining),
                    })
        
        # 按剩余天数排序
        due_samples.sort(key=lambda x: x['remaining_days'])
        
        return due_samples
    
    @classmethod
    def check_age_completion(cls, sample, age_days: int) -> bool:
        """
        检查指定龄期是否已完成检测
        
        :param sample: 样品对象
        :param age_days: 龄期天数
        :return: 是否已完成
        """
        # 检查是否有对应龄期的检测任务已完成
        from apps.testing.models import TestTask
        
        sampling_date = sample.sampling_date
        if not sampling_date:
            return False
        
        due_date = cls.calculate_due_date(sampling_date, age_days)
        
        # 查找该样品的检测任务
        completed_tasks = TestTask.objects.filter(
            sample=sample,
            status='completed',
        )
        
        # 检查是否有在到期日期附近完成的任务
        for task in completed_tasks:
            if task.completed_at:
                # 允许±1天的误差
                task_date = task.completed_at.date()
                if abs(task_date - due_date) <= timedelta(days=1):
                    return True
        
        return False
    
    @classmethod
    def generate_age_report(cls, samples: list) -> dict:
        """
        生成龄期状态报告
        
        :param samples: 样品列表
        :return: 报告数据
        """
        today = timezone.now().date()
        
        report = {
            'generated_at': timezone.now(),
            'total_samples': len(samples),
            'overdue': [],
            'due_today': [],
            'due_soon': [],
            'approaching': [],
            'pending': [],
            'summary': {},
        }
        
        for sample in samples:
            age_days = sample.age_days or cls.DEFAULT_AGE_PERIODS
            
            for days in age_days:
                if not sample.sampling_date:
                    continue
                
                due_date = cls.calculate_due_date(sample.sampling_date, days)
                remaining = cls.get_remaining_days(due_date)
                status_info = cls.get_age_status(remaining)
                
                item = {
                    'sample_id': sample.id,
                    'sample_no': sample.sample_no,
                    'sample_name': sample.name,
                    'age_days': days,
                    'due_date': due_date,
                    'remaining_days': remaining,
                    'status': status_info,
                }
                
                status = status_info['status']
                if status == 'overdue':
                    report['overdue'].append(item)
                elif status == 'due_today':
                    report['due_today'].append(item)
                elif status == 'due_soon':
                    report['due_soon'].append(item)
                elif status == 'approaching':
                    report['approaching'].append(item)
                else:
                    report['pending'].append(item)
        
        # 统计摘要
        report['summary'] = {
            'overdue_count': len(report['overdue']),
            'due_today_count': len(report['due_today']),
            'due_soon_count': len(report['due_soon']),
            'approaching_count': len(report['approaching']),
            'pending_count': len(report['pending']),
        }
        
        return report


class AgeMixin(models.Model):
    """
    龄期混入模型
    可用于需要龄期管理的模型
    """
    
    age_days = models.JSONField(
        default=list,
        verbose_name='龄期要求',
        help_text='如: [7, 28] 表示需要7天和28天龄期检测',
    )
    age_schedules = models.JSONField(
        default=list,
        verbose_name='龄期计划',
        blank=True,
    )
    
    class Meta:
        abstract = True
    
    def update_age_schedules(self):
        """更新龄期计划"""
        self.age_schedules = AgeManagementService.create_age_schedule(self)
        self.save(update_fields=['age_schedules'])
    
    def get_current_age_status(self) -> dict:
        """获取当前龄期状态"""
        if not self.age_schedules:
            return None
        
        # 返回最近的未完成龄期状态
        for schedule in sorted(self.age_schedules, key=lambda x: x['remaining_days']):
            if not schedule.get('is_completed'):
                return schedule
        
        return None
    
    def mark_age_completed(self, age_days: int):
        """标记指定龄期已完成"""
        for schedule in self.age_schedules:
            if schedule['age_days'] == age_days:
                schedule['is_completed'] = True
                schedule['status'] = 'completed'
                schedule['status_display'] = '已完成'
        
        self.save(update_fields=['age_schedules'])