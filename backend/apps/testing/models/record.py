from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel

from .method import TestMethod
from .task import TestTask


class RecordTemplate(BaseModel):
    name = models.CharField(max_length=200, verbose_name='模板名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='模板编号')
    test_method = models.ForeignKey(
        TestMethod, on_delete=models.CASCADE,
        related_name='templates', verbose_name='检测方法',
    )
    test_parameter = models.ForeignKey(
        'testing.TestParameter', null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='record_templates', verbose_name='检测参数',
    )
    version = models.CharField(max_length=20, default='1.0', verbose_name='版本号')
    schema = models.JSONField(verbose_name='表单定义')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        verbose_name = '记录模板'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def clean(self) -> None:
        super().clean()
        if self.test_parameter_id and self.test_method_id:
            if self.test_parameter.method_id != self.test_method_id:
                raise ValidationError(
                    {'test_parameter': '检测参数必须属于所选检测方法'},
                )

    def __str__(self) -> str:
        return f'{self.code} - {self.name} v{self.version}'


class OriginalRecord(BaseModel):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('pending_review', '待复核'),
        ('reviewed', '已复核'),
        ('returned', '已退回'),
    )

    task = models.OneToOneField(
        TestTask, on_delete=models.CASCADE,
        related_name='record', verbose_name='检测任务',
    )
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.PROTECT,
        verbose_name='记录模板',
    )
    template_version = models.CharField(max_length=20, verbose_name='使用模板版本')
    record_data = models.JSONField(default=dict, verbose_name='记录数据')
    env_temperature = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        verbose_name='环境温度(°C)',
    )
    env_humidity = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        verbose_name='环境湿度(%)',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='draft', verbose_name='状态',
    )
    recorder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='recorded_records', verbose_name='记录人',
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_records', verbose_name='复核人',
    )
    review_date = models.DateTimeField(null=True, blank=True, verbose_name='复核日期')
    review_comment = models.TextField(blank=True, verbose_name='复核意见')

    class Meta:
        verbose_name = '原始记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_record_status'),
        ]

    def __str__(self) -> str:
        return f'原始记录 - {self.task.task_no}'


class RecordRevision(models.Model):
    record = models.ForeignKey(
        OriginalRecord, on_delete=models.CASCADE,
        related_name='revisions', verbose_name='原始记录',
    )
    field_path = models.CharField(max_length=200, verbose_name='修改字段路径')
    old_value = models.TextField(blank=True, verbose_name='原值')
    new_value = models.TextField(blank=True, verbose_name='新值')
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '记录修改痕迹'
        verbose_name_plural = verbose_name
        ordering = ['-changed_at']

    def __str__(self) -> str:
        return f'{self.record} - {self.field_path}'
