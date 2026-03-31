from django.conf import settings
from django.db import models

from core.models import BaseModel


class ReportTemplate(BaseModel):
    name = models.CharField(max_length=200, verbose_name='模板名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='模板编号')
    report_type = models.CharField(max_length=50, blank=True, verbose_name='报告类型')
    test_method = models.ForeignKey(
        'testing.TestMethod',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='report_templates',
        verbose_name='关联检测方法',
    )
    test_parameter = models.ForeignKey(
        'testing.TestParameter',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='report_templates',
        verbose_name='关联检测参数',
    )
    version = models.CharField(max_length=20, default='1.0', verbose_name='版本号')
    schema = models.JSONField(default=dict, verbose_name='模板定义')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        verbose_name = '报告模板'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type'], name='idx_rpt_tpl_type'),
            models.Index(fields=['is_active'], name='idx_rpt_tpl_active'),
        ]

    def __str__(self) -> str:
        return f'{self.code} - {self.name} v{self.version}'


class Report(BaseModel):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending_audit', '待审核'),
        ('pending_approve', '待批准'),
        ('approved', '已批准'),
        ('issued', '已发放'),
        ('archived', '已归档'),
        ('voided', '已作废'),
    ]

    report_no = models.CharField(
        max_length=50, unique=True, verbose_name='报告编号',
    )
    commission = models.ForeignKey(
        'commissions.Commission',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='委托单',
    )
    report_type = models.CharField(
        max_length=50, blank=True, verbose_name='报告类型',
    )
    template_name = models.CharField(
        max_length=200, blank=True, verbose_name='报告模板',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft',
        verbose_name='状态',
    )
    compiler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='compiled_reports',
        verbose_name='编制人',
    )
    compile_date = models.DateTimeField(
        null=True, blank=True, verbose_name='编制日期',
    )
    auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audited_reports',
        verbose_name='审核人',
    )
    audit_date = models.DateTimeField(
        null=True, blank=True, verbose_name='审核日期',
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_reports',
        verbose_name='批准人',
    )
    approve_date = models.DateTimeField(
        null=True, blank=True, verbose_name='批准日期',
    )
    conclusion = models.TextField(blank=True, verbose_name='检测结论')
    pdf_file = models.FileField(
        upload_to='reports/pdf/', blank=True, null=True,
        verbose_name='报告PDF',
    )
    qr_code = models.CharField(
        max_length=200, blank=True, verbose_name='防伪二维码',
    )
    has_cma = models.BooleanField(default=True, verbose_name='CMA标识')
    issue_date = models.DateField(
        null=True, blank=True, verbose_name='发放日期',
    )
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '检测报告'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.report_no


class ReportApproval(BaseModel):
    ROLE_CHOICES = [
        ('compile', '编制'),
        ('audit', '审核'),
        ('approve', '批准'),
    ]
    ACTION_CHOICES = [
        ('submit', '提交'),
        ('pass', '通过'),
        ('reject', '退回'),
    ]

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='approvals',
        verbose_name='报告',
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, verbose_name='审批角色',
    )
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, verbose_name='审批动作',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='审批人',
    )
    comment = models.TextField(blank=True, verbose_name='意见')
    signature = models.ImageField(
        upload_to='signatures/', blank=True, null=True,
        verbose_name='电子签名',
    )

    class Meta:
        verbose_name = '报告审批记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['report', 'role'],
                name='idx_rpt_appr_report_role',
            ),
            models.Index(
                fields=['report', 'created_at'],
                name='idx_rpt_appr_report_created',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.report.report_no} - {self.get_role_display()}'


class ReportDistribution(BaseModel):
    METHOD_CHOICES = [
        ('paper', '纸质'),
        ('electronic', '电子'),
        ('both', '纸质+电子'),
    ]

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='distributions',
        verbose_name='报告',
    )
    recipient = models.CharField(max_length=100, verbose_name='接收人')
    recipient_unit = models.CharField(
        max_length=200, blank=True, verbose_name='接收单位',
    )
    method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, verbose_name='发放方式',
    )
    copies = models.IntegerField(default=1, verbose_name='份数')
    distribution_date = models.DateField(verbose_name='发放日期')
    receiver_signature = models.CharField(
        max_length=100, blank=True, verbose_name='签收人',
    )

    class Meta:
        verbose_name = '报告发放记录'
        verbose_name_plural = verbose_name
        ordering = ['-distribution_date']

    def __str__(self) -> str:
        return f'{self.report.report_no} -> {self.recipient}'
