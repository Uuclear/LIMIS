from django.conf import settings
from django.db import models

from core.models import BaseModel


class Equipment(BaseModel):
    STATUS_CHOICES = [
        ('in_use', '在用'),
        ('stopped', '停用'),
        ('calibrating', '送检中'),
        ('scrapped', '已报废'),
    ]
    CATEGORY_CHOICES = [
        ('A', 'A类(强检)'),
        ('B', 'B类(非强检)'),
        ('C', 'C类(辅助)'),
    ]

    name = models.CharField(max_length=200, verbose_name='设备名称')
    model_no = models.CharField(
        max_length=100, blank=True, verbose_name='型号',
    )
    serial_no = models.CharField(
        max_length=100, blank=True, verbose_name='出厂编号',
    )
    manage_no = models.CharField(
        max_length=50, unique=True, verbose_name='管理编号',
    )
    manufacturer = models.CharField(
        max_length=200, blank=True, verbose_name='制造商',
    )
    category = models.CharField(
        max_length=5, choices=CATEGORY_CHOICES, verbose_name='设备分类',
    )
    accuracy = models.CharField(
        max_length=100, blank=True, verbose_name='精度/分辨力',
    )
    measure_range = models.CharField(
        max_length=200, blank=True, verbose_name='量程/测量范围',
    )
    purchase_date = models.DateField(
        null=True, blank=True, verbose_name='购入日期',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_use',
        verbose_name='状态',
    )
    location = models.CharField(
        max_length=200, blank=True, verbose_name='存放位置',
    )
    calibration_cycle = models.IntegerField(
        default=12, verbose_name='校准周期(月)',
    )
    next_calibration_date = models.DateField(
        null=True, blank=True, verbose_name='下次校准到期日',
    )
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '仪器设备'
        verbose_name_plural = verbose_name
        ordering = ['manage_no']

    def __str__(self) -> str:
        return f'{self.manage_no} - {self.name}'


class Calibration(BaseModel):
    CONCLUSION_CHOICES = [
        ('qualified', '合格'),
        ('unqualified', '不合格'),
        ('limited', '限用'),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='calibrations',
        verbose_name='设备',
    )
    certificate_no = models.CharField(
        max_length=100, verbose_name='证书编号',
    )
    calibration_date = models.DateField(verbose_name='检定/校准日期')
    valid_until = models.DateField(verbose_name='有效期至')
    calibration_org = models.CharField(
        max_length=200, verbose_name='校准机构',
    )
    conclusion = models.CharField(
        max_length=20, choices=CONCLUSION_CHOICES, verbose_name='结论',
    )
    attachment = models.FileField(
        upload_to='calibrations/', blank=True, null=True,
        verbose_name='证书附件',
    )
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '检定/校准记录'
        verbose_name_plural = verbose_name
        ordering = ['-calibration_date']

    def __str__(self) -> str:
        return f'{self.equipment.manage_no} - {self.certificate_no}'


class PeriodCheck(BaseModel):
    CONCLUSION_CHOICES = [
        ('normal', '正常'),
        ('abnormal', '异常'),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='period_checks',
        verbose_name='设备',
    )
    check_date = models.DateField(verbose_name='核查日期')
    check_method = models.TextField(verbose_name='核查方法')
    check_result = models.TextField(verbose_name='核查结果')
    conclusion = models.CharField(
        max_length=20, choices=CONCLUSION_CHOICES, verbose_name='结论',
    )
    checker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='核查人',
    )

    class Meta:
        verbose_name = '期间核查'
        verbose_name_plural = verbose_name
        ordering = ['-check_date']

    def __str__(self) -> str:
        return f'{self.equipment.manage_no} - {self.check_date}'


class Maintenance(BaseModel):
    TYPE_CHOICES = [
        ('routine', '日常保养'),
        ('repair', '维修'),
        ('overhaul', '大修'),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenances',
        verbose_name='设备',
    )
    maintenance_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, verbose_name='维护类型',
    )
    maintenance_date = models.DateField(verbose_name='维护日期')
    description = models.TextField(verbose_name='维护内容')
    result = models.TextField(blank=True, verbose_name='维护结果')
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='费用',
    )
    handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='维护人',
    )

    class Meta:
        verbose_name = '维护保养记录'
        verbose_name_plural = verbose_name
        ordering = ['-maintenance_date']

    def __str__(self) -> str:
        return f'{self.equipment.manage_no} - {self.get_maintenance_type_display()}'


class EquipUsageLog(BaseModel):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        verbose_name='设备',
    )
    task = models.ForeignKey(
        'testing.TestTask',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='关联任务',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='使用人',
    )
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(
        null=True, blank=True, verbose_name='结束时间',
    )
    condition_before = models.CharField(
        max_length=200, blank=True, verbose_name='使用前状态',
    )
    condition_after = models.CharField(
        max_length=200, blank=True, verbose_name='使用后状态',
    )
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '设备使用记录'
        verbose_name_plural = verbose_name
        ordering = ['-start_time']

    def __str__(self) -> str:
        return f'{self.equipment.manage_no} - {self.start_time}'
