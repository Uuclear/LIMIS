from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class TestTask(BaseModel):
    STATUS_CHOICES = (
        ('unassigned', '待分配'),
        ('in_progress', '检测中'),
        ('completed', '已完成'),
        ('abnormal', '异常'),
    )

    task_no = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    sample = models.ForeignKey(
        'samples.Sample', on_delete=models.CASCADE,
        related_name='tasks', verbose_name='样品',
    )
    commission = models.ForeignKey(
        'commissions.Commission', on_delete=models.CASCADE,
        related_name='tasks', verbose_name='委托单',
    )
    test_method = models.ForeignKey(
        'testing.TestMethod', on_delete=models.CASCADE,
        verbose_name='检测方法',
    )
    test_parameter = models.ForeignKey(
        'testing.TestParameter', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='检测参数',
    )
    assigned_tester = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks', verbose_name='检测员',
    )
    assigned_equipment = models.ForeignKey(
        'equipment.Equipment', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='使用设备',
    )
    planned_date = models.DateField(null=True, blank=True, verbose_name='计划检测日期')
    actual_date = models.DateField(null=True, blank=True, verbose_name='实际检测日期')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='unassigned', verbose_name='状态',
    )
    age_days = models.IntegerField(null=True, blank=True, verbose_name='龄期(天)')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '检测任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_task_status'),
            models.Index(fields=['planned_date'], name='idx_task_planned_date'),
            models.Index(fields=['assigned_tester'], name='idx_task_tester'),
        ]

    def __str__(self) -> str:
        return self.task_no

    @property
    def is_overdue(self) -> bool:
        if not self.planned_date or self.status == 'completed':
            return False
        return timezone.now().date() > self.planned_date
