from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
import json

from core.models import BaseModel

from .method import TestMethod
from .task import TestTask


class RecordTemplate(BaseModel):
    name = models.CharField(max_length=200, verbose_name='模板名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='模板编号')
    test_method = models.ForeignKey(
        TestMethod, on_delete=models.CASCADE,
        related_name='templates', verbose_name='检测方法',
    )
    test_parameter = models.ForeignKey(
        'testing.TestParameter', null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='record_templates', verbose_name='检测参数',
    )
    version = models.CharField(max_length=20, default='1.0', verbose_name='版本号')
    schema = models.JSONField(verbose_name='表单定义')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        verbose_name = '记录模板'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def clean(self) -> None:
        super().clean()
        if self.test_parameter_id and self.test_method_id:
            if self.test_parameter.method_id != self.test_method_id:
                raise ValidationError(
                    {'test_parameter': '检测参数必须属于所选检测方法'},
                )

    def __str__(self) -> str:
        return f'{self.code} - {self.name} v{self.version}'


class OriginalRecord(BaseModel):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending_review', '待复核'),
        ('reviewed', '已复核'),
        ('returned', '已退回'),
    ]
    
    # 定义合法的状态转换
    VALID_TRANSITIONS = {
        'draft': ['pending_review'],
        'pending_review': ['reviewed', 'returned'],
        'reviewed': [],  # 已复核不能再修改
        'returned': ['draft', 'pending_review'],
    }

    task = models.OneToOneField(
        TestTask, on_delete=models.CASCADE,
        related_name='record', verbose_name='检测任务',
    )
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.PROTECT,
        verbose_name='记录模板',
    )
    template_version = models.CharField(max_length=20, verbose_name='使用模板版本')
    record_data = models.JSONField(default=dict, verbose_name='记录数据')
    env_temperature = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        verbose_name='环境温度(°C)',
    )
    env_humidity = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        verbose_name='环境湿度(%)',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='draft', verbose_name='状态',
    )
    recorder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='recorded_records', verbose_name='记录人',
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_records', verbose_name='复核人',
    )
    review_date = models.DateTimeField(null=True, blank=True, verbose_name='复核日期')
    review_comment = models.TextField(blank=True, verbose_name='复核意见')
    # 数据完整性校验
    data_hash = models.CharField(max_length=64, blank=True, verbose_name='数据哈希')
    is_locked = models.BooleanField(default=False, verbose_name='是否锁定')

    class Meta:
        verbose_name = '原始记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_record_status'),
        ]

    def __str__(self) -> str:
        return f'原始记录 - {self.task.task_no}'
    
    def can_transition_to(self, new_status: str) -> bool:
        """检查是否可以转换到新状态"""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])
    
    def is_editable(self) -> bool:
        """检查记录是否可编辑"""
        return self.status in ('draft', 'returned') and not self.is_locked
    
    def update_data(self, new_data: dict, user, comment: str = '') -> bool:
        """
        更新记录数据并自动记录修改痕迹
        :param new_data: 新的记录数据
        :param user: 操作用户
        :param comment: 修改备注
        :return: 是否成功更新
        """
        if not self.is_editable():
            raise ValidationError('当前状态不允许修改记录')
        
        old_data = self.record_data or {}
        
        # 记录字段级别的变更
        self._record_changes(old_data, new_data, user, comment)
        
        # 更新数据
        self.record_data = new_data
        self._update_data_hash()
        self.save(update_fields=['record_data', 'data_hash', 'updated_at'])
        
        return True
    
    def _record_changes(self, old_data: dict, new_data: dict, user, comment: str = ''):
        """记录字段级别的变更"""
        changes = self._find_changes(old_data, new_data)
        
        for field_path, (old_val, new_val) in changes.items():
            RecordRevision.objects.create(
                record=self,
                field_path=field_path,
                old_value=self._serialize_value(old_val),
                new_value=self._serialize_value(new_val),
                changed_by=user,
                comment=comment,
            )
    
    def _find_changes(self, old_data: dict, new_data: dict, prefix: str = '') -> dict:
        """递归查找数据变更"""
        changes = {}
        
        all_keys = set(old_data.keys()) | set(new_data.keys())
        
        for key in all_keys:
            field_path = f'{prefix}.{key}' if prefix else key
            old_val = old_data.get(key)
            new_val = new_data.get(key)
            
            if isinstance(old_val, dict) and isinstance(new_val, dict):
                # 递归处理嵌套字典
                nested_changes = self._find_changes(old_val, new_val, field_path)
                changes.update(nested_changes)
            elif old_val != new_val:
                changes[field_path] = (old_val, new_val)
        
        return changes
    
    def _serialize_value(self, value) -> str:
        """序列化值为字符串"""
        if value is None:
            return ''
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
    
    def _update_data_hash(self):
        """更新数据哈希值，用于完整性校验"""
        import hashlib
        data_str = json.dumps(self.record_data, sort_keys=True, ensure_ascii=False)
        self.data_hash = hashlib.sha256(data_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """验证数据完整性"""
        if not self.data_hash:
            return True
        import hashlib
        data_str = json.dumps(self.record_data, sort_keys=True, ensure_ascii=False)
        current_hash = hashlib.sha256(data_str.encode()).hexdigest()
        return current_hash == self.data_hash
    
    def submit_for_review(self, user) -> bool:
        """提交复核"""
        if not self.can_transition_to('pending_review'):
            raise ValidationError('当前状态不允许提交复核')
        
        self.status = 'pending_review'
        self.save(update_fields=['status', 'updated_at'])
        
        RecordRevision.objects.create(
            record=self,
            field_path='status',
            old_value='draft',
            new_value='pending_review',
            changed_by=user,
            comment='提交复核',
        )
        
        return True
    
    def pass_review(self, user, comment: str = '') -> bool:
        """复核通过"""
        if not self.can_transition_to('reviewed'):
            raise ValidationError('当前状态不允许复核')
        
        self.status = 'reviewed'
        self.reviewer = user
        self.review_date = timezone.now()
        self.review_comment = comment
        self.is_locked = True  # 复核通过后锁定
        self.save(update_fields=['status', 'reviewer', 'review_date', 'review_comment', 'is_locked', 'updated_at'])
        
        RecordRevision.objects.create(
            record=self,
            field_path='status',
            old_value='pending_review',
            new_value='reviewed',
            changed_by=user,
            comment=comment or '复核通过',
        )
        
        return True
    
    def return_record(self, user, comment: str) -> bool:
        """退回记录"""
        if not self.can_transition_to('returned'):
            raise ValidationError('当前状态不允许退回')
        
        if not comment:
            raise ValidationError('退回必须填写原因')
        
        self.status = 'returned'
        self.reviewer = user
        self.review_date = timezone.now()
        self.review_comment = comment
        self.save(update_fields=['status', 'reviewer', 'review_date', 'review_comment', 'updated_at'])
        
        RecordRevision.objects.create(
            record=self,
            field_path='status',
            old_value='pending_review',
            new_value='returned',
            changed_by=user,
            comment=comment,
        )
        
        return True
    
    def get_change_history(self) -> list:
        """获取变更历史"""
        revisions = self.revisions.select_related('changed_by').all()
        return [
            {
                'id': rev.id,
                'field_path': rev.field_path,
                'old_value': rev.old_value,
                'new_value': rev.new_value,
                'changed_by': str(rev.changed_by) if rev.changed_by else '',
                'changed_at': rev.changed_at,
                'comment': rev.comment,
            }
            for rev in revisions
        ]


class RecordRevision(models.Model):
    record = models.ForeignKey(
        OriginalRecord, on_delete=models.CASCADE,
        related_name='revisions', verbose_name='原始记录',
    )
    field_path = models.CharField(max_length=200, verbose_name='修改字段路径')
    old_value = models.TextField(blank=True, verbose_name='原值')
    new_value = models.TextField(blank=True, verbose_name='新值')
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        verbose_name='修改人',
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')
    comment = models.TextField(blank=True, verbose_name='修改备注')

    class Meta:
        verbose_name = '记录修改痕迹'
        verbose_name_plural = verbose_name
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['record', '-changed_at'], name='idx_revision_record_time'),
        ]

    def __str__(self) -> str:
        return f'{self.record} - {self.field_path}'
    
    @property
    def field_display(self) -> str:
        """获取字段的显示名称"""
        # 可以根据field_path返回更友好的字段名称
        field_names = {
            'status': '状态',
            'env_temperature': '环境温度',
            'env_humidity': '环境湿度',
        }
        return field_names.get(self.field_path, self.field_path)
