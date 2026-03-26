from django.conf import settings
from django.db import models

from core.models import BaseModel


class ProficiencyTest(BaseModel):
    RESULT_CHOICES = [
        ('satisfactory', '满意'),
        ('questionable', '有问题'),
        ('unsatisfactory', '不满意'),
        ('pending', '待评'),
    ]

    name = models.CharField(max_length=200, verbose_name='项目名称')
    organizer = models.CharField(max_length=200, verbose_name='组织单位')
    test_item = models.CharField(max_length=200, verbose_name='检测项目')
    participation_date = models.DateField(verbose_name='参加日期')
    result = models.CharField(
        max_length=20, choices=RESULT_CHOICES,
        default='pending', verbose_name='结果',
    )
    report = models.TextField(blank=True, verbose_name='报告')
    attachment = models.FileField(
        upload_to='proficiency/', blank=True, null=True,
        verbose_name='附件',
    )

    class Meta:
        verbose_name = '能力验证'
        verbose_name_plural = verbose_name
        ordering = ['-participation_date']

    def __str__(self) -> str:
        return f'{self.name} - {self.test_item}'


class QualitySupervision(BaseModel):
    CONCLUSION_CHOICES = [
        ('conforming', '符合'),
        ('nonconforming', '不符合'),
    ]

    plan_no = models.CharField(
        max_length=50, unique=True, verbose_name='监督计划编号',
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='监督员',
    )
    supervision_date = models.DateField(verbose_name='监督日期')
    scope = models.TextField(verbose_name='监督范围')
    findings = models.TextField(blank=True, verbose_name='发现')
    conclusion = models.CharField(
        max_length=20, choices=CONCLUSION_CHOICES,
        verbose_name='结论',
    )

    class Meta:
        verbose_name = '质量监督'
        verbose_name_plural = verbose_name
        ordering = ['-supervision_date']

    def __str__(self) -> str:
        return f'{self.plan_no} ({self.supervision_date})'
