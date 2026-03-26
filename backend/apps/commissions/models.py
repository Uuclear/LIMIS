from django.conf import settings
from django.db import models

from core.models import BaseModel


class Commission(BaseModel):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending_review', '待评审'),
        ('reviewed', '已评审'),
        ('rejected', '已退回'),
        ('cancelled', '已取消'),
    ]

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
