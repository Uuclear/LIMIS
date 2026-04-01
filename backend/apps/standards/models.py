from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class StandardCategory(BaseModel):
    """标准分类"""
    CATEGORY_TYPES = [
        ('national', '国家标准'),
        ('industry', '行业标准'),
        ('local', '地方标准'),
        ('enterprise', '企业标准'),
        ('international', '国际标准'),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name='分类编码')
    name = models.CharField(max_length=100, verbose_name='分类名称')
    category_type = models.CharField(
        max_length=20, choices=CATEGORY_TYPES,
        verbose_name='标准类型',
    )
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children',
        verbose_name='上级分类',
    )
    description = models.TextField(blank=True, verbose_name='描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    
    class Meta:
        verbose_name = '标准分类'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'code']
    
    def __str__(self) -> str:
        return self.name
    
    def get_full_path(self) -> str:
        """获取完整分类路径"""
        if self.parent:
            return f'{self.parent.get_full_path()} / {self.name}'
        return self.name


class Standard(BaseModel):
    STATUS_CHOICES = [
        ('active', '现行'),
        ('upcoming', '即将实施'),
        ('abolished', '已废止'),
        ('draft', '草案'),
    ]
    
    # 机场工程常用标准分类
    AIRPORT_STANDARDS = {
        'concrete': '混凝土检测',
        'steel': '钢筋检测',
        'asphalt': '沥青检测',
        'soil': '土工检测',
        'aggregate': '骨料检测',
        'water': '水质检测',
        'environment': '环境检测',
        'equipment': '设备标准',
        'method': '检测方法',
        'quality': '质量管理',
    }

    standard_no = models.CharField(
        max_length=100,
        verbose_name='标准号',
        # 唯一性见 Meta：仅对未软删记录唯一，避免「列表里看不见但编号仍被占用」
    )
    name = models.CharField(max_length=300, verbose_name='标准名称')
    category = models.ForeignKey(
        StandardCategory, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='standards',
        verbose_name='标准分类',
        db_constraint=False,  # 不创建数据库外键约束
    )
    category_legacy = models.CharField(
        max_length=50, blank=True, verbose_name='标准分类(旧)',
    )
    # 适用领域
    applicable_fields = models.JSONField(
        default=list, blank=True,
        verbose_name='适用领域',
        help_text='如: ["concrete", "steel"]',
    )
    publish_date = models.DateField(
        null=True, blank=True, verbose_name='发布日期',
    )
    implement_date = models.DateField(
        null=True, blank=True, verbose_name='实施日期',
    )
    abolish_date = models.DateField(
        null=True, blank=True, verbose_name='废止日期',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='active', verbose_name='状态',
    )
    replaced_by = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='替代标准',
    )
    replaced_case = models.CharField(
        max_length=200, blank=True, verbose_name='替代情况',
    )
    # 标准内容摘要
    scope = models.TextField(blank=True, verbose_name='适用范围')
    main_content = models.TextField(blank=True, verbose_name='主要内容')
    key_parameters = models.JSONField(
        default=list, blank=True,
        verbose_name='关键参数',
        help_text='标准涉及的主要检测参数',
    )
    attachment = models.FileField(
        upload_to='standards/', blank=True, null=True,
        verbose_name='标准文件',
    )
    remark = models.TextField(blank=True, verbose_name='备注')
    
    # 关联检测方法
    test_methods = models.ManyToManyField(
        'testing.TestMethod', blank=True,
        related_name='standards', verbose_name='关联检测方法',
    )

    class Meta:
        verbose_name = '标准'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['standard_no'],
                condition=models.Q(is_deleted=False),
                name='standards_standard_no_unique_if_active',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.standard_no} {self.name}'
    
    def is_effective(self) -> bool:
        """检查标准是否有效"""
        if self.status == 'abolished':
            return False
        if self.abolish_date and self.abolish_date <= timezone.now().date():
            return False
        return True
    
    def get_status_display_with_date(self) -> str:
        """获取状态显示（包含日期信息）"""
        status_display = self.get_status_display()
        
        if self.status == 'upcoming' and self.implement_date:
            days = (self.implement_date - timezone.now().date()).days
            return f'{status_display}（{days}天后实施）'
        elif self.status == 'abolished' and self.abolish_date:
            return f'{status_display}（{self.abolish_date}废止）'
        
        return status_display
    
    @classmethod
    def get_airport_standards(cls) -> dict:
        """获取机场工程常用标准列表"""
        return cls.AIRPORT_STANDARDS
    
    @classmethod
    def get_standards_by_field(cls, field: str) -> models.QuerySet:
        """按适用领域获取标准"""
        return cls.objects.filter(
            applicable_fields__contains=field,
            status='active',
            is_deleted=False,
        )


class StandardParameter(BaseModel):
    """标准参数（标准中规定的检测参数）"""
    
    standard = models.ForeignKey(
        Standard, on_delete=models.CASCADE,
        related_name='parameters', verbose_name='标准',
    )
    parameter_name = models.CharField(max_length=100, verbose_name='参数名称')
    parameter_code = models.CharField(max_length=50, blank=True, verbose_name='参数编码')
    unit = models.CharField(max_length=20, blank=True, verbose_name='单位')
    
    # 技术要求
    requirement_type = models.CharField(
        max_length=20, choices=[
            ('value', '数值要求'),
            ('range', '范围要求'),
            ('grade', '分级要求'),
            ('formula', '公式计算'),
            ('text', '文字描述'),
        ],
        verbose_name='要求类型',
    )
    min_value = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='最小值',
    )
    max_value = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='最大值',
    )
    target_value = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='目标值',
    )
    tolerance = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='允许偏差',
    )
    requirement_text = models.TextField(blank=True, verbose_name='要求描述')
    
    # 检测方法引用
    test_method_clause = models.CharField(
        max_length=100, blank=True, verbose_name='检测方法条款',
    )
    
    # 判定规则
    judgment_rule = models.TextField(blank=True, verbose_name='判定规则')
    
    class Meta:
        verbose_name = '标准参数'
        verbose_name_plural = verbose_name
        ordering = ['standard', 'parameter_code']
    
    def __str__(self) -> str:
        return f'{self.standard.standard_no} - {self.parameter_name}'
    
    def get_requirement_display(self) -> str:
        """获取要求显示文本"""
        if self.requirement_type == 'value':
            return f'{self.target_value} {self.unit}'
        elif self.requirement_type == 'range':
            return f'{self.min_value}~{self.max_value} {self.unit}'
        elif self.requirement_type == 'grade':
            return self.requirement_text
        else:
            return self.requirement_text
    
    def judge_result(self, value) -> dict:
        """判定结果是否符合要求"""
        from decimal import Decimal
        
        result = {
            'value': value,
            'requirement': self.get_requirement_display(),
            'is_compliant': None,
            'judgment': '待判定',
        }
        
        if value is None:
            return result
        
        try:
            value_dec = Decimal(str(value))
            
            if self.requirement_type == 'value':
                if self.tolerance:
                    lower = self.target_value - self.tolerance
                    upper = self.target_value + self.tolerance
                    result['is_compliant'] = lower <= value_dec <= upper
                else:
                    result['is_compliant'] = value_dec == self.target_value
            
            elif self.requirement_type == 'range':
                result['is_compliant'] = self.min_value <= value_dec <= self.max_value
            
            result['judgment'] = '合格' if result['is_compliant'] else '不合格'
            
        except (ValueError, TypeError):
            result['judgment'] = '无法判定'
        
        return result


class MethodValidation(BaseModel):
    CONCLUSION_CHOICES = [
        ('valid', '验证通过'),
        ('invalid', '验证不通过'),
        ('partial', '部分通过'),
    ]

    standard = models.ForeignKey(
        Standard, on_delete=models.CASCADE,
        related_name='validations', verbose_name='标准',
    )
    validation_no = models.CharField(
        max_length=50, unique=True, blank=True, default='', verbose_name='验证编号',
    )
    validation_date = models.DateField(verbose_name='验证日期')
    validator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='验证人',
    )
    conclusion = models.CharField(
        max_length=20, choices=CONCLUSION_CHOICES,
        verbose_name='结论',
    )
    # 验证内容
    validation_scope = models.TextField(blank=True, default='', verbose_name='验证范围')
    validation_method = models.TextField(blank=True, default='', verbose_name='验证方法')
    validation_results = models.JSONField(
        default=dict, verbose_name='验证结果数据',
    )
    report = models.TextField(blank=True, verbose_name='验证报告')
    attachment = models.FileField(
        upload_to='validations/', blank=True, null=True,
        verbose_name='验证附件',
    )
    # 有效期
    valid_until = models.DateField(
        null=True, blank=True, verbose_name='有效期至',
    )

    class Meta:
        verbose_name = '方法验证'
        verbose_name_plural = verbose_name
        ordering = ['-validation_date']

    def __str__(self) -> str:
        return f'{self.standard.standard_no} 验证 ({self.validation_date})'
    
    def is_valid(self) -> bool:
        """检查验证是否有效"""
        if self.conclusion != 'valid':
            return False
        if self.valid_until and self.valid_until < timezone.now().date():
            return False
        return True
