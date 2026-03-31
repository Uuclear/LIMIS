from django.conf import settings
from django.db import models

from core.models import BaseModel


class Standard(BaseModel):
    STATUS_CHOICES = [
        ('active', '现行'),
        ('upcoming', '即将实施'),
        ('abolished', '已废止'),
    ]

    standard_no = models.CharField(
        max_length=100,
        verbose_name='标准号',
        # 唯一性见 Meta：仅对未软删记录唯一，避免「列表里看不见但编号仍被占用」
    )
    name = models.CharField(max_length=300, verbose_name='标准名称')
    category = models.CharField(max_length=50, verbose_name='标准分类')
    publish_date = models.DateField(
        null=True, blank=True, verbose_name='发布日期',
    )
    implement_date = models.DateField(
        null=True, blank=True, verbose_name='实施日期',
    )
    abolish_date = models.DateField(
        null=True, blank=True, verbose_name='废止日期',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='active', verbose_name='状态',
    )
    replaced_by = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='替代标准',
    )
    replaced_case = models.CharField(
        max_length=200, blank=True, verbose_name='替代情况',
    )
    attachment = models.FileField(
        upload_to='standards/', blank=True, null=True,
        verbose_name='标准文件',
    )
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '标准'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['standard_no'],
                condition=models.Q(is_deleted=False),
                name='standards_standard_no_unique_if_active',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.standard_no} {self.name}'


class MethodValidation(BaseModel):
    CONCLUSION_CHOICES = [
        ('valid', '验证通过'),
        ('invalid', '验证不通过'),
    ]

    standard = models.ForeignKey(
        Standard, on_delete=models.CASCADE,
        related_name='validations', verbose_name='标准',
    )
    validation_date = models.DateField(verbose_name='验证日期')
    validator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='验证人',
    )
    conclusion = models.CharField(
        max_length=20, choices=CONCLUSION_CHOICES,
        verbose_name='结论',
    )
    report = models.TextField(blank=True, verbose_name='验证报告')
    attachment = models.FileField(
        upload_to='validations/', blank=True, null=True,
        verbose_name='验证附件',
    )

    class Meta:
        verbose_name = '方法验证'
        verbose_name_plural = verbose_name
        ordering = ['-validation_date']

    def __str__(self) -> str:
        return f'{self.standard.standard_no} 验证 ({self.validation_date})'
