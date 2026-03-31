from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from django.db import models
from django.db.models import Avg, Count, F, Q
from django.utils import timezone


def get_dashboard_summary() -> dict[str, Any]:
    from apps.commissions.models import Commission
    from apps.testing.models import OriginalRecord, TestTask
    from apps.reports.models import Report

    today = timezone.now().date()
    month_start = today.replace(day=1)

    return {
        'today_commissions': Commission.objects.filter(
            commission_date=today, is_deleted=False,
        ).count(),
        'pending_tasks': TestTask.objects.filter(
            status__in=['unassigned', 'assigned'], is_deleted=False,
        ).count(),
        'month_reports': Report.objects.filter(
            created_at__date__gte=month_start, is_deleted=False,
        ).count(),
        'equipment_warnings': _get_equipment_warning_count(),
        # 与 Header 消息提醒、待办统计对齐
        'pending_commission_reviews': Commission.objects.filter(
            status='pending_review', is_deleted=False,
        ).count(),
        'pending_report_reviews': Report.objects.filter(
            status__in=['pending_audit', 'pending_approve'], is_deleted=False,
        ).count(),
        'records_pending_review': OriginalRecord.objects.filter(
            status='pending_review',
        ).count(),
    }


def _get_equipment_warning_count() -> int:
    from apps.equipment.models import Equipment

    threshold = timezone.now().date() + timedelta(days=30)
    return Equipment.objects.filter(
        status='in_use', is_deleted=False,
    ).filter(
        Q(next_calibration_date__lte=threshold)
        | Q(next_calibration_date__isnull=True),
    ).count()


def get_recent_tasks(limit: int = 10) -> list[dict[str, Any]]:
    from apps.testing.models import TestTask

    tasks = TestTask.objects.filter(
        is_deleted=False,
    ).select_related(
        'sample', 'assigned_tester',
    ).order_by('-created_at')[:limit]

    return [
        {
            'task_no': t.task_no,
            'sample_name': str(t.sample) if t.sample else '',
            'tester': (
                t.assigned_tester.get_full_name()
                if t.assigned_tester else ''
            ),
            'status': t.status,
            'planned_date': t.planned_date,
        }
        for t in tasks
    ]


def get_test_volume(start_date: date, end_date: date,
                    group_by: str = 'day') -> list[dict[str, Any]]:
    from apps.testing.models import TestTask

    qs = TestTask.objects.filter(
        is_deleted=False,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    )
    trunc_fn = _get_trunc_function(group_by)
    return list(
        qs.annotate(period=trunc_fn('created_at'))
        .values('period')
        .annotate(count=Count('id'))
        .order_by('period')
    )


def _get_trunc_function(group_by: str):
    from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
    mapping = {
        'day': TruncDay,
        'week': TruncWeek,
        'month': TruncMonth,
    }
    return mapping.get(group_by, TruncDay)


def get_qualification_rate(start_date: date, end_date: date) -> list[dict[str, Any]]:
    from apps.testing.models import TestResult

    qs = TestResult.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        judgment__in=['qualified', 'unqualified'],
    )
    results = qs.values(
        category=F('task__test_method__category__name'),
    ).annotate(
        total=Count('id'),
        qualified=Count('id', filter=Q(judgment='qualified')),
    ).order_by('category')

    return [
        {
            'category': r['category'],
            'total': r['total'],
            'qualified': r['qualified'],
            'rate': round(r['qualified'] / r['total'] * 100, 1) if r['total'] else 0,
        }
        for r in results
    ]


def get_cycle_analysis(start_date: date, end_date: date) -> dict[str, Any]:
    from apps.reports.models import Report

    reports = Report.objects.filter(
        is_deleted=False,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status__in=['approved', 'issued', 'archived'],
        commission__commission_date__isnull=False,
        approve_date__isnull=False,
    ).select_related('commission')

    if not reports.exists():
        return {'avg_days': 0, 'count': 0}

    cycle_data = reports.annotate(
        cycle=F('approve_date') - F('commission__commission_date'),
    ).aggregate(
        avg_cycle=Avg('cycle'),
        count=Count('id'),
    )

    avg_days = 0
    if cycle_data['avg_cycle']:
        avg_days = cycle_data['avg_cycle'].days

    return {'avg_days': avg_days, 'count': cycle_data['count']}


def get_workload(start_date: date, end_date: date) -> list[dict[str, Any]]:
    from apps.testing.models import TestTask

    return list(
        TestTask.objects.filter(
            is_deleted=False,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            assigned_tester__isnull=False,
        ).values(
            tester_id=F('assigned_tester'),
            tester_name=F('assigned_tester__first_name'),
        ).annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
        ).order_by('-total')
    )


def get_equipment_usage(start_date: date, end_date: date) -> list[dict[str, Any]]:
    from apps.testing.models import TestTask
    from apps.equipment.models import Equipment

    total_equipment = Equipment.objects.filter(
        status='in_use', is_deleted=False,
    ).count()

    used = TestTask.objects.filter(
        is_deleted=False,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        assigned_equipment__isnull=False,
    ).values(
        equipment_id=F('assigned_equipment'),
        equipment_name=F('assigned_equipment__name'),
    ).annotate(
        usage_count=Count('id'),
    ).order_by('-usage_count')

    return {
        'total_equipment': total_equipment,
        'used_equipment': used.count(),
        'details': list(used[:20]),
    }
