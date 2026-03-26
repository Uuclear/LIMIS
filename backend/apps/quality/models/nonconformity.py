from django.conf import settings
from django.db import models

from core.models import BaseModel


class NonConformity(BaseModel):
    SOURCE_CHOICES = [
        ('internal', '内部发现'),
        ('audit', '审核发现'),
        ('complaint', '投诉'),
        ('proficiency', '能力验证'),
        ('other', '其他'),
    ]
    STATUS_CHOICES = [
        ('open', '待处理'),
        ('in_progress', '进行中'),
        ('closed', '已关闭'),
    ]

    nc_no = models.CharField(
        max_length=50, unique=True, verbose_name='不符合项编号',
    )
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES,
        verbose_name='来源',
    )
    description = models.TextField(verbose_name='描述')
    impact_assessment = models.TextField(
        blank=True, verbose_name='影响评价',
    )
    corrective_action = models.TextField(
        blank=True, verbose_name='纠正措施',
    )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='责任人',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='open', verbose_name='状态',
    )
    close_date = models.DateField(
        null=True, blank=True, verbose_name='关闭日期',
    )

    class Meta:
        verbose_name = '不符合项'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.nc_no} ({self.get_source_display()})'


class Complaint(BaseModel):
    STATUS_CHOICES = [
        ('received', '已接收'),
        ('investigating', '调查中'),
        ('resolved', '已处理'),
        ('closed', '已关闭'),
    ]

    complaint_no = models.CharField(
        max_length=50, unique=True, verbose_name='投诉编号',
    )
    complainant = models.CharField(
        max_length=100, verbose_name='投诉人',
    )
    complaint_date = models.DateField(verbose_name='投诉日期')
    content = models.TextField(verbose_name='投诉内容')
    investigation = models.TextField(
        blank=True, verbose_name='调查结果',
    )
    handling_result = models.TextField(
        blank=True, verbose_name='处理意见',
    )
    handler = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='处理人',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='received', verbose_name='状态',
    )

    class Meta:
        verbose_name = '投诉'
        verbose_name_plural = verbose_name
        ordering = ['-complaint_date']

    def __str__(self) -> str:
        return f'{self.complaint_no} - {self.complainant}'
