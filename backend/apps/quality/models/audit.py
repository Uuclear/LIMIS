from django.conf import settings
from django.db import models

from core.models import BaseModel


class InternalAudit(BaseModel):
    AUDIT_TYPE_CHOICES = [
        ('scheduled', '例行审核'),
        ('special', '专项审核'),
    ]
    STATUS_CHOICES = [
        ('planned', '计划中'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('closed', '已关闭'),
    ]

    audit_no = models.CharField(
        max_length=50, unique=True, verbose_name='审核编号',
    )
    title = models.CharField(max_length=200, verbose_name='审核主题')
    audit_type = models.CharField(
        max_length=20, choices=AUDIT_TYPE_CHOICES,
        verbose_name='审核类型',
    )
    scope = models.TextField(verbose_name='审核范围')
    planned_date = models.DateField(verbose_name='计划日期')
    actual_date = models.DateField(
        null=True, blank=True, verbose_name='实际日期',
    )
    lead_auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='审核组长',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='planned', verbose_name='状态',
    )

    class Meta:
        verbose_name = '内部审核'
        verbose_name_plural = verbose_name
        ordering = ['-planned_date']

    def __str__(self) -> str:
        return f'{self.audit_no} {self.title}'


class AuditFinding(BaseModel):
    FINDING_TYPE_CHOICES = [
        ('nonconformity', '不符合项'),
        ('observation', '观察项'),
        ('improvement', '改进建议'),
    ]

    audit = models.ForeignKey(
        InternalAudit, on_delete=models.CASCADE,
        related_name='findings', verbose_name='审核',
    )
    finding_type = models.CharField(
        max_length=20, choices=FINDING_TYPE_CHOICES,
        verbose_name='发现类型',
    )
    clause = models.CharField(
        max_length=100, blank=True, verbose_name='涉及条款',
    )
    description = models.TextField(verbose_name='描述')
    department = models.CharField(
        max_length=100, blank=True, verbose_name='责任部门',
    )

    class Meta:
        verbose_name = '审核发现'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.audit.audit_no} - {self.get_finding_type_display()}'


class CorrectiveAction(BaseModel):
    STATUS_CHOICES = [
        ('open', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('verified', '已验证'),
    ]

    finding = models.ForeignKey(
        AuditFinding, on_delete=models.CASCADE,
        related_name='actions', verbose_name='审核发现',
    )
    root_cause = models.TextField(verbose_name='原因分析')
    action_plan = models.TextField(verbose_name='纠正措施')
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='责任人',
    )
    deadline = models.DateField(verbose_name='完成期限')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='open', verbose_name='状态',
    )
    completion_date = models.DateField(
        null=True, blank=True, verbose_name='完成日期',
    )
    verification_result = models.TextField(
        blank=True, verbose_name='验证结果',
    )

    class Meta:
        verbose_name = '纠正措施'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.finding} - {self.get_status_display()}'
