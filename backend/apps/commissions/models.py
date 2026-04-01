from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models import BaseModel


class Commission(BaseModel):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('pending_review', '待评审'),
        ('reviewed', '已评审'),
        ('rejected', '已退回'),
        ('cancelled', '已取消'),
    ]
    
    # 定义合法的状态转换
    VALID_TRANSITIONS = {
        'draft': ['submitted', 'cancelled'],
        'submitted': ['pending_review', 'draft'],
        'pending_review': ['reviewed', 'rejected', 'draft'],
        'reviewed': [],  # 已评审状态不能再转换
        'rejected': ['draft', 'submitted'],  # 已退回可以重新提交
        'cancelled': [],  # 已取消状态不能再转换
    }

    commission_no = models.CharField(
        max_length=50, unique=True, verbose_name='委托编号',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name='所属项目',
    )
    sub_project = models.ForeignKey(
        'projects.SubProject',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='分部分项工程',
    )
    construction_part = models.CharField(
        max_length=200, verbose_name='施工部位',
    )
    commission_date = models.DateField(verbose_name='委托日期')
    client_unit = models.CharField(max_length=200, verbose_name='委托单位')
    client_contact = models.CharField(
        max_length=50, blank=True, verbose_name='联系人',
    )
    client_phone = models.CharField(
        max_length=20, blank=True, verbose_name='联系电话',
    )
    witness = models.ForeignKey(
        'projects.Witness',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='见证人',
    )
    is_witnessed = models.BooleanField(default=False, verbose_name='是否见证取样')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态',
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_commissions',
        verbose_name='评审人',
    )
    review_date = models.DateTimeField(
        null=True, blank=True, verbose_name='评审日期',
    )
    review_comment = models.TextField(blank=True, verbose_name='评审意见')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '委托单'
        verbose_name_plural = verbose_name
        ordering = ['-commission_date', '-created_at']

    def __str__(self) -> str:
        return self.commission_no
    
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
        if new_status == 'reviewed':
            self.reviewer = user
            self.review_date = timezone.now()
            if comment:
                self.review_comment = comment
        elif new_status == 'rejected':
            self.reviewer = user
            self.review_date = timezone.now()
            self.review_comment = comment
        
        self.save(update_fields=['status', 'reviewer', 'review_date', 'review_comment', 'updated_at'])
        
        # 记录状态变更日志
        CommissionStatusLog.objects.create(
            commission=self,
            old_status=old_status,
            new_status=new_status,
            operator=user,
            comment=comment,
        )
        
        return True
    
    def submit(self, user=None) -> bool:
        """提交委托单"""
        return self.transition_to('submitted', user, '提交委托单')
    
    def request_review(self, user=None) -> bool:
        """请求评审"""
        return self.transition_to('pending_review', user, '请求评审')
    
    def approve(self, user=None, comment: str = '') -> bool:
        """评审通过"""
        return self.transition_to('reviewed', user, comment or '评审通过')
    
    def reject(self, user=None, comment: str = '') -> bool:
        """评审退回"""
        if not comment:
            raise ValidationError('退回必须填写退回原因')
        return self.transition_to('rejected', user, comment)
    
    def cancel(self, user=None, comment: str = '') -> bool:
        """取消委托"""
        return self.transition_to('cancelled', user, comment or '取消委托')
    
    def resubmit(self, user=None) -> bool:
        """重新提交（从退回状态）"""
        if self.status == 'rejected':
            return self.transition_to('draft', user, '重新编辑')
        return False


class CommissionStatusLog(BaseModel):
    """委托状态变更日志"""
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name='委托单',
    )
    old_status = models.CharField(
        max_length=20,
        choices=Commission.STATUS_CHOICES,
        verbose_name='原状态',
    )
    new_status = models.CharField(
        max_length=20,
        choices=Commission.STATUS_CHOICES,
        verbose_name='新状态',
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='操作人',
    )
    comment = models.TextField(blank=True, verbose_name='操作备注')
    operated_at = models.DateTimeField(
        auto_now_add=True, verbose_name='操作时间',
    )

    class Meta:
        verbose_name = '委托状态变更日志'
        verbose_name_plural = verbose_name
        ordering = ['-operated_at']

    def __str__(self) -> str:
        return f'{self.commission.commission_no}: {self.old_status} → {self.new_status}'


class CommissionItem(BaseModel):
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='委托单',
    )
    test_object = models.CharField(max_length=100, verbose_name='检测对象')
    test_item = models.CharField(max_length=200, verbose_name='检测项目')
    test_standard = models.CharField(
        max_length=200, blank=True, verbose_name='检测标准',
    )
    test_method = models.CharField(
        max_length=200, blank=True, verbose_name='检测方法',
    )
    specification = models.CharField(
        max_length=200, blank=True, verbose_name='规格型号',
    )
    grade = models.CharField(
        max_length=100, blank=True, verbose_name='设计强度/等级',
    )
    quantity = models.IntegerField(default=1, verbose_name='数量')
    unit = models.CharField(max_length=20, default='组', verbose_name='单位')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '委托项目'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.commission.commission_no} - {self.test_object}'


class ContractReview(BaseModel):
    CONCLUSION_CHOICES = [
        ('accept', '接受'),
        ('reject', '拒绝'),
        ('conditional', '有条件接受'),
    ]

    commission = models.OneToOneField(
        Commission,
        on_delete=models.CASCADE,
        related_name='contract_review',
        verbose_name='委托单',
    )
    has_capability = models.BooleanField(
        default=True, verbose_name='具备检测能力',
    )
    has_equipment = models.BooleanField(
        default=True, verbose_name='设备满足要求',
    )
    has_personnel = models.BooleanField(
        default=True, verbose_name='人员满足要求',
    )
    method_valid = models.BooleanField(
        default=True, verbose_name='方法标准有效',
    )
    sample_representative = models.BooleanField(
        default=True, verbose_name='样品具有代表性',
    )
    conclusion = models.CharField(
        max_length=20, choices=CONCLUSION_CHOICES, verbose_name='评审结论',
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='评审人',
    )
    review_date = models.DateTimeField(
        auto_now_add=True, verbose_name='评审日期',
    )
    comment = models.TextField(blank=True, verbose_name='评审意见')

    class Meta:
        verbose_name = '合同评审'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f'{self.commission.commission_no} - {self.get_conclusion_display()}'
