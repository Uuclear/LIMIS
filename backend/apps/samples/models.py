from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class SampleGroup(BaseModel):
    group_no = models.CharField(max_length=50, unique=True, verbose_name='组样编号')
    name = models.CharField(max_length=200, verbose_name='组样名称')
    sample_count = models.IntegerField(default=3, verbose_name='组内样品数')
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = '样品组'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.group_no} - {self.name}'


class Sample(BaseModel):
    STATUS_CHOICES = (
        ('pending', '待检'),
        ('testing', '检测中'),
        ('tested', '已检'),
        ('retained', '留样'),
        ('disposed', '已处置'),
        ('returned', '已退还'),
    )

    sample_no = models.CharField(max_length=50, unique=True, verbose_name='样品编号')
    blind_no = models.CharField(
        max_length=50, unique=True, null=True, blank=True, verbose_name='盲样编号',
    )
    commission = models.ForeignKey(
        'commissions.Commission', on_delete=models.CASCADE,
        related_name='samples', verbose_name='委托单',
    )
    group = models.ForeignKey(
        SampleGroup, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='samples', verbose_name='所属组样',
    )
    name = models.CharField(max_length=200, verbose_name='样品名称')
    specification = models.CharField(max_length=200, blank=True, verbose_name='规格型号')
    grade = models.CharField(max_length=100, blank=True, verbose_name='设计强度/等级')
    quantity = models.IntegerField(default=1, verbose_name='数量')
    unit = models.CharField(max_length=20, default='个', verbose_name='单位')
    sampling_date = models.DateField(verbose_name='取样日期')
    received_date = models.DateField(verbose_name='收样日期')
    production_date = models.DateField(null=True, blank=True, verbose_name='生产/成型日期')
    sampling_location = models.CharField(max_length=200, blank=True, verbose_name='取样地点')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态',
    )
    retention_deadline = models.DateField(null=True, blank=True, verbose_name='留样到期日')
    disposal_date = models.DateField(null=True, blank=True, verbose_name='处置日期')
    disposal_method = models.CharField(max_length=100, blank=True, verbose_name='处置方式')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '样品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_sample_status'),
            models.Index(fields=['commission'], name='idx_sample_commission'),
            models.Index(fields=['sampling_date'], name='idx_sample_sampling_date'),
        ]

    def __str__(self) -> str:
        return f'{self.sample_no} - {self.name}'

    @property
    def project(self):
        return self.commission.project if self.commission_id else None

    @property
    def is_overdue_retention(self) -> bool:
        if self.status != 'retained' or not self.retention_deadline:
            return False
        return timezone.now().date() > self.retention_deadline


class SampleDisposal(BaseModel):
    DISPOSAL_TYPE_CHOICES = (
        ('return', '退还'),
        ('destroy', '销毁'),
        ('discard', '丢弃'),
    )

    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE,
        related_name='disposals', verbose_name='样品',
    )
    disposal_type = models.CharField(
        max_length=20, choices=DISPOSAL_TYPE_CHOICES, verbose_name='处置方式',
    )
    disposal_date = models.DateField(verbose_name='处置日期')
    handler = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='处置人',
    )
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '样品处置'
        verbose_name_plural = verbose_name
        ordering = ['-disposal_date']

    def __str__(self) -> str:
        return f'{self.sample.sample_no} - {self.get_disposal_type_display()}'
