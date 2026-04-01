from django.db import models

from core.models import BaseModel


class TestCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='检测类别')
    code = models.CharField(max_length=20, unique=True, verbose_name='类别代码')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children',
        verbose_name='上级类别',
    )
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '检测类别'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'code']

    def __str__(self) -> str:
        return f'{self.code} - {self.name}'


class TestParameter(BaseModel):
    category = models.ForeignKey(
        TestCategory, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='parameters', verbose_name='检测类别',
    )
    standard = models.ForeignKey(
        'standards.Standard', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='parameters', verbose_name='依据标准',
    )
    standard_no = models.CharField(max_length=100, blank=True, verbose_name='标准号')
    standard_name = models.CharField(max_length=300, blank=True, verbose_name='标准名称')
    name = models.CharField(max_length=100, verbose_name='参数名称')
    code = models.CharField(max_length=50, verbose_name='参数代码')
    unit = models.CharField(max_length=20, blank=True, verbose_name='单位')
    precision = models.IntegerField(default=1, verbose_name='修约精度(小数位数)')
    min_value = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True,
        verbose_name='最小值',
    )
    max_value = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True,
        verbose_name='最大值',
    )
    is_required = models.BooleanField(default=True, verbose_name='是否必填')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    description = models.TextField(blank=True, verbose_name='说明')

    class Meta:
        verbose_name = '检测参数'
        verbose_name_plural = verbose_name
        ordering = ['category', 'code']
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'standard_no'],
                condition=models.Q(is_deleted=False),
                name='unique_param_code_per_standard',
            ),
        ]

    def __str__(self) -> str:
        label = f'{self.name} ({self.unit})' if self.unit else self.name
        if self.standard_no:
            label = f'{self.standard_no} - {label}'
        return label
