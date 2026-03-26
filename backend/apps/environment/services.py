from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.utils import timezone

from .models import EnvAlarm, EnvRecord, MonitoringPoint


def ingest_record(point_id: int, temperature: Decimal, humidity: Decimal,
                  recorded_at=None) -> EnvRecord:
    """Create an environment record and trigger alarm check."""
    point = MonitoringPoint.objects.get(pk=point_id)
    if recorded_at is None:
        recorded_at = timezone.now()

    alarms = check_thresholds(point, temperature, humidity, recorded_at)
    is_alarm = len(alarms) > 0

    record = EnvRecord.objects.create(
        point=point,
        temperature=temperature,
        humidity=humidity,
        recorded_at=recorded_at,
        is_alarm=is_alarm,
    )
    return record


def check_thresholds(point: MonitoringPoint, temperature: Decimal,
                     humidity: Decimal, recorded_at) -> list[EnvAlarm]:
    """Check values against point thresholds and create alarms."""
    alarms: list[EnvAlarm] = []

    alarm_checks = [
        (temperature > point.temp_max, 'temp_high', temperature, point.temp_max),
        (temperature < point.temp_min, 'temp_low', temperature, point.temp_min),
        (humidity > point.humidity_max, 'humidity_high', humidity, point.humidity_max),
        (humidity < point.humidity_min, 'humidity_low', humidity, point.humidity_min),
    ]

    for is_triggered, alarm_type, value, threshold in alarm_checks:
        if is_triggered:
            alarm = EnvAlarm.objects.create(
                point=point,
                alarm_type=alarm_type,
                alarm_value=value,
                threshold=threshold,
                alarm_time=recorded_at,
            )
            alarms.append(alarm)

    return alarms


def get_point_latest_records(point_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """Retrieve the latest records for a monitoring point."""
    records = EnvRecord.objects.filter(
        point_id=point_id,
    ).order_by('-recorded_at')[:limit]
    return [
        {
            'temperature': r.temperature,
            'humidity': r.humidity,
            'recorded_at': r.recorded_at,
            'is_alarm': r.is_alarm,
        }
        for r in records
    ]
