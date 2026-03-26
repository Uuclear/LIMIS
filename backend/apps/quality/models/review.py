from django.conf import settings
from django.db import models

from core.models import BaseModel


class ManagementReview(BaseModel):
    STATUS_CHOICES = [
        ('planned', '计划中'),
        ('completed', '已完成'),
        ('closed', '已关闭'),
    ]

    review_no = models.CharField(
        max_length=50, unique=True, verbose_name='评审编号',
    )
    title = models.CharField(max_length=200, verbose_name='评审主题')
    review_date = models.DateField(verbose_name='评审日期')
    chairperson = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='主持人',
    )
    participants = models.TextField(
        blank=True, verbose_name='参会人员',
    )
    input_materials = models.TextField(
        blank=True, verbose_name='输入材料',
    )
    minutes = models.TextField(blank=True, verbose_name='会议纪要')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='planned', verbose_name='状态',
    )

    class Meta:
        verbose_name = '管理评审'
        verbose_name_plural = verbose_name
        ordering = ['-review_date']

    def __str__(self) -> str:
        return f'{self.review_no} {self.title}'


class ReviewDecision(BaseModel):
    STATUS_CHOICES = [
        ('open', '待处理'),
        ('completed', '已完成'),
    ]

    review = models.ForeignKey(
        ManagementReview, on_delete=models.CASCADE,
        related_name='decisions', verbose_name='管理评审',
    )
    content = models.TextField(verbose_name='决议内容')
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='责任人',
    )
    deadline = models.DateField(verbose_name='完成期限')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='open', verbose_name='状态',
    )

    class Meta:
        verbose_name = '评审决议'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.review.review_no} 决议: {self.content[:30]}'
