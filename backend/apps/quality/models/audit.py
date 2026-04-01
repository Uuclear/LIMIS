from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class InternalAudit(BaseModel):
    AUDIT_TYPE_CHOICES = [
        ('scheduled', '例行审核'),
        ('special', '专项审核'),
        ('follow_up', '跟踪审核'),
    ]
    STATUS_CHOICES = [
        ('planned', '计划中'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('closed', '已关闭'),
    ]
    
    # 状态转换定义
    VALID_TRANSITIONS = {
        'planned': ['in_progress'],
        'in_progress': ['completed'],
        'completed': ['closed'],
        'closed': [],
    }

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
    auditors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        related_name='participated_audits', verbose_name='审核员',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='planned', verbose_name='状态',
    )
    # 审核结果统计
    total_findings = models.IntegerField(default=0, verbose_name='发现项总数')
    nonconformity_count = models.IntegerField(default=0, verbose_name='不符合项数')
    observation_count = models.IntegerField(default=0, verbose_name='观察项数')
    improvement_count = models.IntegerField(default=0, verbose_name='改进建议数')
    # 审核报告
    report_file = models.FileField(
        upload_to='quality/audit_reports/', blank=True, null=True,
        verbose_name='审核报告',
    )
    conclusion = models.TextField(blank=True, verbose_name='审核结论')

    class Meta:
        verbose_name = '内部审核'
        verbose_name_plural = verbose_name
        ordering = ['-planned_date']

    def __str__(self) -> str:
        return f'{self.audit_no} {self.title}'
    
    def can_transition_to(self, new_status: str) -> bool:
        """检查是否可以转换到新状态"""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])
    
    def start_audit(self, user) -> bool:
        """开始审核"""
        if not self.can_transition_to('in_progress'):
            raise ValueError('当前状态不允许开始审核')
        
        self.status = 'in_progress'
        self.actual_date = timezone.now().date()
        self.save(update_fields=['status', 'actual_date', 'updated_at'])
        return True
    
    def complete_audit(self, user, conclusion: str = '') -> bool:
        """完成审核"""
        if not self.can_transition_to('completed'):
            raise ValueError('当前状态不允许完成审核')
        
        self.status = 'completed'
        self.conclusion = conclusion
        self._update_finding_counts()
        self.save(update_fields=['status', 'conclusion', 'total_findings', 
                                  'nonconformity_count', 'observation_count', 
                                  'improvement_count', 'updated_at'])
        return True
    
    def close_audit(self, user) -> bool:
        """关闭审核"""
        if not self.can_transition_to('closed'):
            raise ValueError('当前状态不允许关闭审核')
        
        # 检查所有纠正措施是否已验证
        open_actions = CorrectiveAction.objects.filter(
            finding__audit=self,
            status__in=['open', 'in_progress'],
        ).count()
        
        if open_actions > 0:
            raise ValueError(f'还有 {open_actions} 个纠正措施未完成')
        
        self.status = 'closed'
        self.save(update_fields=['status', 'updated_at'])
        return True
    
    def _update_finding_counts(self):
        """更新发现项统计"""
        findings = self.findings.all()
        self.total_findings = findings.count()
        self.nonconformity_count = findings.filter(finding_type='nonconformity').count()
        self.observation_count = findings.filter(finding_type='observation').count()
        self.improvement_count = findings.filter(finding_type='improvement').count()


class AuditFinding(BaseModel):
    FINDING_TYPE_CHOICES = [
        ('nonconformity', '不符合项'),
        ('observation', '观察项'),
        ('improvement', '改进建议'),
    ]
    SEVERITY_CHOICES = [
        ('major', '严重'),
        ('minor', '一般'),
        ('low', '轻微'),
    ]
    STATUS_CHOICES = [
        ('open', '待处理'),
        ('action_planned', '措施已制定'),
        ('action_completed', '措施已完成'),
        ('verified', '已验证有效'),
        ('closed', '已关闭'),
    ]
    
    VALID_TRANSITIONS = {
        'open': ['action_planned'],
        'action_planned': ['action_completed'],
        'action_completed': ['verified'],
        'verified': ['closed'],
        'closed': [],
    }

    audit = models.ForeignKey(
        InternalAudit, on_delete=models.CASCADE,
        related_name='findings', verbose_name='审核',
    )
    finding_type = models.CharField(
        max_length=20, choices=FINDING_TYPE_CHOICES,
        verbose_name='发现类型',
    )
    severity = models.CharField(
        max_length=20, choices=SEVERITY_CHOICES,
        default='minor', verbose_name='严重程度',
    )
    clause = models.CharField(
        max_length=100, blank=True, verbose_name='涉及条款',
    )
    description = models.TextField(verbose_name='描述')
    evidence = models.TextField(blank=True, verbose_name='证据/依据')
    department = models.CharField(
        max_length=100, blank=True, verbose_name='责任部门',
    )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='责任人',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='open', verbose_name='状态',
    )

    class Meta:
        verbose_name = '审核发现'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.audit.audit_no} - {self.get_finding_type_display()}'
    
    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])
    
    def create_corrective_action(self, root_cause: str, action_plan: str, 
                                  responsible_person, deadline) -> 'CorrectiveAction':
        """创建纠正措施"""
        action = CorrectiveAction.objects.create(
            finding=self,
            root_cause=root_cause,
            action_plan=action_plan,
            responsible_person=responsible_person,
            deadline=deadline,
        )
        self.status = 'action_planned'
        self.save(update_fields=['status', 'updated_at'])
        return action


class CorrectiveAction(BaseModel):
    STATUS_CHOICES = [
        ('open', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('verified', '已验证'),
        ('rejected', '验证未通过'),
    ]
    
    VALID_TRANSITIONS = {
        'open': ['in_progress'],
        'in_progress': ['completed'],
        'completed': ['verified', 'rejected'],
        'verified': [],
        'rejected': ['in_progress'],
    }

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
    completion_evidence = models.TextField(blank=True, verbose_name='完成证据')
    verification_result = models.TextField(
        blank=True, verbose_name='验证结果',
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_actions',
        verbose_name='验证人',
    )
    verification_date = models.DateField(
        null=True, blank=True, verbose_name='验证日期',
    )

    class Meta:
        verbose_name = '纠正措施'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.finding} - {self.get_status_display()}'
    
    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])
    
    def start_action(self, user) -> bool:
        """开始执行纠正措施"""
        if not self.can_transition_to('in_progress'):
            raise ValueError('当前状态不允许开始执行')
        
        self.status = 'in_progress'
        self.save(update_fields=['status', 'updated_at'])
        return True
    
    def complete_action(self, user, evidence: str = '') -> bool:
        """完成纠正措施"""
        if not self.can_transition_to('completed'):
            raise ValueError('当前状态不允许完成')
        
        self.status = 'completed'
        self.completion_date = timezone.now().date()
        self.completion_evidence = evidence
        self.save(update_fields=['status', 'completion_date', 'completion_evidence', 'updated_at'])
        
        # 更新发现项状态
        self.finding.status = 'action_completed'
        self.finding.save(update_fields=['status', 'updated_at'])
        
        return True
    
    def verify_action(self, user, result: str, is_effective: bool) -> bool:
        """验证纠正措施"""
        if not self.can_transition_to('verified') and not self.can_transition_to('rejected'):
            raise ValueError('当前状态不允许验证')
        
        self.verified_by = user
        self.verification_date = timezone.now().date()
        self.verification_result = result
        
        if is_effective:
            self.status = 'verified'
            self.finding.status = 'verified'
        else:
            self.status = 'rejected'
            # 验证不通过，需要重新执行
        
        self.save(update_fields=['status', 'verified_by', 'verification_date', 
                                  'verification_result', 'updated_at'])
        self.finding.save(update_fields=['status', 'updated_at'])
        
        return True
    
    def is_overdue(self) -> bool:
        """检查是否超期"""
        if self.status in ('verified', 'closed'):
            return False
        return timezone.now().date() > self.deadline
