from django.conf import settings
from django.db import models

from core.models import BaseModel


class MonitoringPoint(BaseModel):
    name = models.CharField(max_length=100, verbose_name='监控点位名称')
    code = models.CharField(
        max_length=50, unique=True, verbose_name='点位编码',
    )
    location = models.CharField(
        max_length=200, blank=True, verbose_name='位置描述',
    )
    temp_min = models.DecimalField(
        max_digits=5, decimal_places=1, verbose_name='温度下限(°C)',
    )
    temp_max = models.DecimalField(
        max_digits=5, decimal_places=1, verbose_name='温度上限(°C)',
    )
    humidity_min = models.DecimalField(
        max_digits=5, decimal_places=1, verbose_name='湿度下限(%)',
    )
    humidity_max = models.DecimalField(
        max_digits=5, decimal_places=1, verbose_name='湿度上限(%)',
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        verbose_name = '监控点位'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self) -> str:
        return f'{self.code} - {self.name}'


class EnvRecord(models.Model):
    """High-volume sensor data — uses plain Model for performance."""

    point = models.ForeignKey(
        MonitoringPoint, on_delete=models.CASCADE,
        related_name='records', verbose_name='监控点位',
    )
    temperature = models.DecimalField(
        max_digits=5, decimal_places=1, verbose_name='温度(°C)',
    )
    humidity = models.DecimalField(
        max_digits=5, decimal_places=1, verbose_name='湿度(%)',
    )
    recorded_at = models.DateTimeField(verbose_name='记录时间')
    is_alarm = models.BooleanField(default=False, verbose_name='是否报警')

    class Meta:
        verbose_name = '环境记录'
        verbose_name_plural = verbose_name
        ordering = ['-recorded_at']
        indexes = [
            models.Index(
                fields=['point', '-recorded_at'],
                name='idx_envrecord_point_time',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.point.code} {self.recorded_at:%Y-%m-%d %H:%M}'


class EnvAlarm(BaseModel):
    ALARM_TYPE_CHOICES = [
        ('temp_high', '温度偏高'),
        ('temp_low', '温度偏低'),
        ('humidity_high', '湿度偏高'),
        ('humidity_low', '湿度偏低'),
    ]

    point = models.ForeignKey(
        MonitoringPoint, on_delete=models.CASCADE,
        related_name='alarms', verbose_name='监控点位',
    )
    alarm_type = models.CharField(
        max_length=20, choices=ALARM_TYPE_CHOICES,
        verbose_name='报警类型',
    )
    alarm_value = models.DecimalField(
        max_digits=5, decimal_places=1, verbose_name='报警值',
    )
    threshold = models.DecimalField(
        max_digits=5, decimal_places=1, verbose_name='阈值',
    )
    alarm_time = models.DateTimeField(verbose_name='报警时间')
    is_resolved = models.BooleanField(
        default=False, verbose_name='是否已处理',
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='处理人',
    )
    resolved_at = models.DateTimeField(
        null=True, blank=True, verbose_name='处理时间',
    )

    class Meta:
        verbose_name = '环境报警'
        verbose_name_plural = verbose_name
        ordering = ['-alarm_time']

    def __str__(self) -> str:
        return f'{self.point.code} {self.get_alarm_type_display()} {self.alarm_time}'
