from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from .models import Calibration, Equipment, EquipUsageLog, PeriodCheck

logger = logging.getLogger(__name__)


def get_expiring_equipment(days: int = 15) -> QuerySet:
    threshold = date.today() + timedelta(days=days)
    return Equipment.objects.filter(
        status='in_use',
        next_calibration_date__isnull=False,
        next_calibration_date__lte=threshold,
    )


def check_calibration_expiry() -> list[dict]:
    """Find equipment expiring within 30/7 days; mark expired ones as stopped."""
    today = date.today()
    results = []

    expired = Equipment.objects.filter(
        status='in_use',
        next_calibration_date__isnull=False,
        next_calibration_date__lt=today,
    )
    for eq in expired:
        eq.status = 'stopped'
        eq.save(update_fields=['status', 'updated_at'])
        results.append({
            'equipment': eq.manage_no,
            'level': 'expired',
            'next_calibration_date': eq.next_calibration_date,
        })

    for days, level in [(30, 'warning_30'), (7, 'warning_7')]:
        threshold = today + timedelta(days=days)
        upcoming = Equipment.objects.filter(
            status='in_use',
            next_calibration_date__isnull=False,
            next_calibration_date__gt=today,
            next_calibration_date__lte=threshold,
        )
        for eq in upcoming:
            results.append({
                'equipment': eq.manage_no,
                'level': level,
                'next_calibration_date': eq.next_calibration_date,
            })

    logger.info('Calibration expiry check: %d items found', len(results))
    return results


@transaction.atomic
def create_period_check_plans(equipment_id: int) -> list[dict]:
    equipment = Equipment.objects.get(pk=equipment_id)
    latest_cal = equipment.calibrations.order_by('-calibration_date').first()
    if not latest_cal:
        return []

    start = latest_cal.calibration_date
    end = latest_cal.valid_until
    interval_months = max(equipment.calibration_cycle // 4, 1)

    plans = []
    check_date = start + relativedelta(months=interval_months)
    while check_date < end:
        plans.append({
            'equipment_id': equipment.pk,
            'planned_date': check_date,
        })
        check_date += relativedelta(months=interval_months)

    return plans


def get_equipment_traceability(equipment_id: int) -> dict[str, Any]:
    equipment = Equipment.objects.get(pk=equipment_id)
    calibrations = equipment.calibrations.order_by(
        '-calibration_date',
    ).values(
        'id', 'certificate_no', 'calibration_date',
        'valid_until', 'calibration_org', 'conclusion',
    )

    return {
        'equipment': {
            'id': equipment.pk,
            'manage_no': equipment.manage_no,
            'name': equipment.name,
            'model_no': equipment.model_no,
            'category': equipment.category,
        },
        'calibration_chain': list(calibrations),
    }


def log_equipment_usage(
    equipment_id: int,
    task_id: int | None,
    user_id: int,
) -> EquipUsageLog:
    return EquipUsageLog.objects.create(
        equipment_id=equipment_id,
        task_id=task_id,
        user_id=user_id,
        start_time=timezone.now(),
    )
