from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models import BaseModel


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
    
    # 定义合法的状态转换
    VALID_TRANSITIONS = {
        'draft': ['pending_audit', 'voided'],
        'pending_audit': ['pending_approve', 'draft', 'voided'],
        'pending_approve': ['approved', 'pending_audit', 'draft', 'voided'],
        'approved': ['issued', 'voided'],
        'issued': ['archived', 'voided'],
        'archived': [],  # 已归档状态不能再转换
        'voided': [],  # 已作废状态不能再转换
    }

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
    
    def can_transition_to(self, new_status: str) -> bool:
        """检查是否可以转换到新状态"""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])
    
    def transition_to(self, new_status: str, user=None, comment: str = '') -> bool:
        """
        状态转换方法
        :param new_status: 新状态
        :param user: 操作用户
        :param comment: 操作备注
        :return: 是否成功转换
        """
        if not self.can_transition_to(new_status):
            raise ValidationError(
                f'无法从 {self.get_status_display()} 状态转换到 {dict(self.STATUS_CHOICES).get(new_status, new_status)} 状态'
            )
        
        old_status = self.status
        self.status = new_status
        
        # 根据状态更新相关字段
        if new_status == 'pending_audit':
            if not self.compile_date:
                self.compile_date = timezone.now()
            if user and not self.compiler:
                self.compiler = user
        elif new_status == 'pending_approve':
            if not self.audit_date:
                self.audit_date = timezone.now()
            if user and not self.auditor:
                self.auditor = user
        elif new_status == 'approved':
            if not self.approve_date:
                self.approve_date = timezone.now()
            if user and not self.approver:
                self.approver = user
        elif new_status == 'issued':
            if not self.issue_date:
                self.issue_date = timezone.now().date()
        elif new_status == 'voided':
            # 作废时记录原因
            if comment:
                self.remark = f'作废原因: {comment}'
        
        self.save()
        
        # 记录状态变更日志
        ReportStatusLog.objects.create(
            report=self,
            old_status=old_status,
            new_status=new_status,
            operator=user,
            comment=comment,
        )
        
        return True
    
    def submit_for_audit(self, user=None) -> bool:
        """提交审核"""
        return self.transition_to('pending_audit', user, '提交审核')
    
    def pass_audit(self, user=None, comment: str = '') -> bool:
        """审核通过"""
        return self.transition_to('pending_approve', user, comment or '审核通过')
    
    def reject_audit(self, user=None, comment: str = '') -> bool:
        """审核退回"""
        if not comment:
            raise ValidationError('审核退回必须填写退回原因')
        return self.transition_to('draft', user, comment)
    
    def pass_approval(self, user=None, comment: str = '') -> bool:
        """批准通过"""
        return self.transition_to('approved', user, comment or '批准通过')
    
    def reject_approval(self, user=None, comment: str = '') -> bool:
        """批准退回"""
        if not comment:
            raise ValidationError('批准退回必须填写退回原因')
        return self.transition_to('pending_audit', user, comment)
    
    def issue(self, user=None) -> bool:
        """发放报告"""
        return self.transition_to('issued', user, '报告发放')
    
    def archive(self, user=None) -> bool:
        """归档报告"""
        return self.transition_to('archived', user, '报告归档')
    
    def void(self, user=None, reason: str = '') -> bool:
        """作废报告"""
        if not reason:
            raise ValidationError('作废报告必须填写作废原因')
        return self.transition_to('voided', user, reason)
    
    @property
    def is_editable(self) -> bool:
        """是否可编辑"""
        return self.status in ('draft', 'pending_audit')
    
    @property
    def is_final(self) -> bool:
        """是否为终态"""
        return self.status in ('archived', 'voided')


class ReportStatusLog(BaseModel):
    """报告状态变更日志"""
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE,
        related_name='status_logs', verbose_name='报告',
    )
    old_status = models.CharField(
        max_length=20, choices=Report.STATUS_CHOICES, verbose_name='原状态',
    )
    new_status = models.CharField(
        max_length=20, choices=Report.STATUS_CHOICES, verbose_name='新状态',
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='操作人',
    )
    comment = models.TextField(blank=True, verbose_name='操作备注')
    operated_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '报告状态变更日志'
        verbose_name_plural = verbose_name
        ordering = ['-operated_at']

    def __str__(self) -> str:
        return f'{self.report.report_no}: {self.old_status} → {self.new_status}'


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
