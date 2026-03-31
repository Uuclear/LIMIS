from __future__ import annotations

from django.conf import settings
from django.db import models

from core.models import BaseModel


class QualificationProfile(BaseModel):
    """
    公司级“资质管理 / 能力范围”配置。

    用于限制系统在“标准规范、项目参数库、原始记录模板”等选项上只展示/可用符合能力范围的内容。
    """

    name = models.CharField(max_length=200, unique=True, verbose_name='资质配置名称')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    valid_from = models.DateField(
        null=True, blank=True, verbose_name='生效日期（可选）',
    )
    valid_to = models.DateField(null=True, blank=True, verbose_name='失效日期（可选）')

    # 简化实现：用附件描述/上传资质材料（PDF/图片等）
    attachment = models.FileField(
        upload_to='qualification/', null=True, blank=True, verbose_name='资质附件',
    )

    allowed_standards = models.ManyToManyField(
        'standards.Standard',
        blank=True,
        related_name='qualification_profiles',
        verbose_name='允许使用的标准规范',
    )
    allowed_test_methods = models.ManyToManyField(
        'testing.TestMethod',
        blank=True,
        related_name='qualification_profiles',
        verbose_name='允许使用的检测方法',
    )
    allowed_record_templates = models.ManyToManyField(
        'testing.RecordTemplate',
        blank=True,
        related_name='qualification_profiles',
        verbose_name='允许使用的原始记录模板',
    )

    class Meta:
        verbose_name = '资质配置'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name

