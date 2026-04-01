from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models import BaseModel


class SampleGroup(BaseModel):
    group_no = models.CharField(max_length=50, unique=True, verbose_name='组样编号')
    name = models.CharField(max_length=200, verbose_name='组样名称')
    sample_count = models.IntegerField(default=3, verbose_name='组内样品数')
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = '样品组'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.group_no} - {self.name}'


class Sample(BaseModel):
    STATUS_CHOICES = [
        ('pending', '待检'),
        ('testing', '检测中'),
        ('tested', '已检'),
        ('retained', '留样'),
        ('disposed', '已处置'),
        ('returned', '已退还'),
    ]
    
    # 定义合法的状态转换
    VALID_TRANSITIONS = {
        'pending': ['testing', 'returned'],
        'testing': ['tested', 'pending'],
        'tested': ['retained', 'disposed', 'returned'],
        'retained': ['disposed', 'returned'],
        'disposed': [],  # 已处置状态不能再转换
        'returned': [],  # 已退还状态不能再转换
    }

    sample_no = models.CharField(max_length=50, unique=True, verbose_name='样品编号')
    blind_no = models.CharField(
        max_length=50, unique=True, null=True, blank=True, verbose_name='盲样编号',
    )
    commission = models.ForeignKey(
        'commissions.Commission', on_delete=models.CASCADE,
        related_name='samples', verbose_name='委托单',
    )
    group = models.ForeignKey(
        SampleGroup, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='samples', verbose_name='所属组样',
    )
    name = models.CharField(max_length=200, verbose_name='样品名称')
    specification = models.CharField(max_length=200, blank=True, verbose_name='规格型号')
    grade = models.CharField(max_length=100, blank=True, verbose_name='设计强度/等级')
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    unit = models.CharField(max_length=20, default='个', verbose_name='单位')
    sampling_date = models.DateField(verbose_name='取样日期')
    received_date = models.DateField(verbose_name='收样日期')
    production_date = models.DateField(null=True, blank=True, verbose_name='生产/成型日期')
    sampling_location = models.CharField(max_length=200, blank=True, verbose_name='取样地点')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态',
    )
    retention_deadline = models.DateField(null=True, blank=True, verbose_name='留样到期日')
    disposal_date = models.DateField(null=True, blank=True, verbose_name='处置日期')
    disposal_method = models.CharField(max_length=100, blank=True, verbose_name='处置方式')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '样品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_sample_status'),
            models.Index(fields=['commission'], name='idx_sample_commission'),
            models.Index(fields=['sampling_date'], name='idx_sample_sampling_date'),
        ]

    def __str__(self) -> str:
        return f'{self.sample_no} - {self.name}'
    
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
        if new_status == 'retained':
            # 设置默认留样期限（如90天）
            if not self.retention_deadline:
                from datetime import timedelta
                self.retention_deadline = timezone.now().date() + timedelta(days=90)
        elif new_status in ('disposed', 'returned'):
            self.disposal_date = timezone.now().date()
        
        self.save()
        
        # 记录状态变更日志
        SampleStatusLog.objects.create(
            sample=self,
            old_status=old_status,
            new_status=new_status,
            operator=user,
            comment=comment,
        )
        
        return True
    
    def start_testing(self, user=None) -> bool:
        """开始检测"""
        return self.transition_to('testing', user, '开始检测')
    
    def complete_testing(self, user=None) -> bool:
        """完成检测"""
        return self.transition_to('tested', user, '检测完成')
    
    def retain(self, user=None, days: int = 90) -> bool:
        """留样"""
        from datetime import timedelta
        self.retention_deadline = timezone.now().date() + timedelta(days=days)
        return self.transition_to('retained', user, f'留样{days}天')
    
    def dispose(self, user=None, method: str = '') -> bool:
        """处置样品"""
        self.disposal_method = method
        return self.transition_to('disposed', user, f'处置方式: {method}')
    
    def return_sample(self, user=None) -> bool:
        """退还样品"""
        return self.transition_to('returned', user, '退还样品')

    @property
    def project(self):
        return self.commission.project if self.commission_id else None

    @property
    def is_overdue_retention(self) -> bool:
        if self.status != 'retained' or not self.retention_deadline:
            return False
        return timezone.now().date() > self.retention_deadline
    
    @property
    def days_to_expire(self) -> int | None:
        """距离留样到期还有多少天"""
        if self.status != 'retained' or not self.retention_deadline:
            return None
        delta = self.retention_deadline - timezone.now().date()
        return delta.days


class SampleStatusLog(BaseModel):
    """样品状态变更日志"""
    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE,
        related_name='status_logs', verbose_name='样品',
    )
    old_status = models.CharField(
        max_length=20, choices=Sample.STATUS_CHOICES, verbose_name='原状态',
    )
    new_status = models.CharField(
        max_length=20, choices=Sample.STATUS_CHOICES, verbose_name='新状态',
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='操作人',
    )
    comment = models.TextField(blank=True, verbose_name='操作备注')
    operated_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '样品状态变更日志'
        verbose_name_plural = verbose_name
        ordering = ['-operated_at']

    def __str__(self) -> str:
        return f'{self.sample.sample_no}: {self.old_status} → {self.new_status}'


class SampleDisposal(BaseModel):
    DISPOSAL_TYPE_CHOICES = [
        ('return', '退还'),
        ('destroy', '销毁'),
        ('discard', '丢弃'),
    ]

    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE,
        related_name='disposals', verbose_name='样品',
    )
    disposal_type = models.CharField(
        max_length=20, choices=DISPOSAL_TYPE_CHOICES, verbose_name='处置方式',
    )
    disposal_date = models.DateField(verbose_name='处置日期')
    handler = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='处置人',
    )
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '样品处置'
        verbose_name_plural = verbose_name
        ordering = ['-disposal_date']

    def __str__(self) -> str:
        return f'{self.sample.sample_no} - {self.get_disposal_type_display()}'
