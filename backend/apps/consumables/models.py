from django.conf import settings
from django.db import models

from core.models import BaseModel


class Supplier(BaseModel):
    name = models.CharField(max_length=200, verbose_name='供应商名称')
    contact_person = models.CharField(
        max_length=100, blank=True, verbose_name='联系人',
    )
    phone = models.CharField(
        max_length=50, blank=True, verbose_name='联系电话',
    )
    address = models.CharField(
        max_length=300, blank=True, verbose_name='地址',
    )
    evaluation_score = models.DecimalField(
        max_digits=5, decimal_places=1,
        null=True, blank=True, verbose_name='评价得分',
    )
    is_qualified = models.BooleanField(
        default=True, verbose_name='是否合格',
    )

    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Consumable(BaseModel):
    name = models.CharField(max_length=200, verbose_name='耗材名称')
    code = models.CharField(
        max_length=50, unique=True, verbose_name='耗材编码',
    )
    specification = models.CharField(
        max_length=200, blank=True, verbose_name='规格型号',
    )
    unit = models.CharField(max_length=20, verbose_name='计量单位')
    category = models.CharField(
        max_length=100, blank=True, verbose_name='分类',
    )
    manufacturer = models.CharField(
        max_length=200, blank=True, verbose_name='生产厂家',
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='consumables', verbose_name='供应商',
    )
    stock_quantity = models.IntegerField(
        default=0, verbose_name='库存数量',
    )
    safety_stock = models.IntegerField(
        default=10, verbose_name='安全库存',
    )
    expiry_date = models.DateField(
        null=True, blank=True, verbose_name='有效期至',
    )
    storage_location = models.CharField(
        max_length=200, blank=True, verbose_name='存放位置',
    )

    class Meta:
        verbose_name = '耗材'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self) -> str:
        return f'{self.code} - {self.name}'

    @property
    def is_low_stock(self) -> bool:
        return self.stock_quantity <= self.safety_stock


class ConsumableIn(BaseModel):
    consumable = models.ForeignKey(
        Consumable, on_delete=models.CASCADE,
        related_name='in_records', verbose_name='耗材',
    )
    quantity = models.IntegerField(verbose_name='入库数量')
    batch_no = models.CharField(max_length=100, verbose_name='批次号')
    purchase_date = models.DateField(verbose_name='采购日期')
    expiry_date = models.DateField(
        null=True, blank=True, verbose_name='有效期至',
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='操作人',
    )

    class Meta:
        verbose_name = '入库记录'
        verbose_name_plural = verbose_name
        ordering = ['-purchase_date']

    def __str__(self) -> str:
        return f'{self.consumable.code} 入库 {self.quantity}'


class ConsumableOut(BaseModel):
    consumable = models.ForeignKey(
        Consumable, on_delete=models.CASCADE,
        related_name='out_records', verbose_name='耗材',
    )
    quantity = models.IntegerField(verbose_name='出库数量')
    purpose = models.CharField(max_length=200, verbose_name='用途')
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='领用人',
    )
    out_date = models.DateField(verbose_name='出库日期')

    class Meta:
        verbose_name = '出库记录'
        verbose_name_plural = verbose_name
        ordering = ['-out_date']

    def __str__(self) -> str:
        return f'{self.consumable.code} 出库 {self.quantity}'
