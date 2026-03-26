from django.db import models

from core.models import BaseModel

from .method import TestParameter
from .task import TestTask


class JudgmentRule(BaseModel):
    test_parameter = models.ForeignKey(
        TestParameter, on_delete=models.CASCADE,
        related_name='rules', verbose_name='检测参数',
    )
    grade = models.CharField(max_length=100, verbose_name='强度等级/技术要求')
    min_value = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True,
        verbose_name='下限值',
    )
    max_value = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True,
        verbose_name='上限值',
    )
    standard_ref = models.CharField(
        max_length=200, blank=True, verbose_name='标准依据',
    )

    class Meta:
        verbose_name = '判定规则'
        verbose_name_plural = verbose_name
        ordering = ['test_parameter', 'grade']

    def __str__(self) -> str:
        return f'{self.test_parameter.name} - {self.grade}'


class TestResult(BaseModel):
    JUDGMENT_CHOICES = (
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('na', '不判定'),
    )

    task = models.ForeignKey(
        TestTask, on_delete=models.CASCADE,
        related_name='results', verbose_name='检测任务',
    )
    parameter = models.ForeignKey(
        TestParameter, on_delete=models.CASCADE,
        verbose_name='检测参数',
    )
    raw_value = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True,
        verbose_name='原始值',
    )
    rounded_value = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True,
        verbose_name='修约后值',
    )
    display_value = models.CharField(max_length=100, blank=True, verbose_name='显示值')
    unit = models.CharField(max_length=20, blank=True, verbose_name='单位')
    judgment = models.CharField(
        max_length=20, choices=JUDGMENT_CHOICES,
        default='na', verbose_name='判定结论',
    )
    standard_value = models.CharField(
        max_length=100, blank=True, verbose_name='标准限值',
    )
    design_value = models.CharField(max_length=100, blank=True, verbose_name='设计值')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '检测结果'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'parameter'], name='idx_result_task_param'),
        ]

    def __str__(self) -> str:
        return f'{self.task.task_no} - {self.parameter.name}: {self.display_value}'
