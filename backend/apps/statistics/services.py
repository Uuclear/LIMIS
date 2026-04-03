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
        # 与「本月」业务感知一致：委托按委托日期落在当月统计
        'month_commissions': Commission.objects.filter(
            commission_date__gte=month_start,
            commission_date__lte=today,
            is_deleted=False,
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
    # 仅统计「已录入到期日且 30 日内到期」的设备；未填到期日单独在设备模块处理
    return Equipment.objects.filter(
        status='in_use', is_deleted=False,
        next_calibration_date__isnull=False,
        next_calibration_date__lte=threshold,
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
        category=F('task__test_parameter__category__name'),
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


def get_task_counts_by_project(
    start_date: date, end_date: date, limit: int = 20,
) -> list[dict[str, Any]]:
    """按委托所属项目统计检测任务数（时间范围：任务创建日）。"""
    from apps.testing.models import TestTask

    qs = (
        TestTask.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )
        .values(project_name=F('commission__project__name'))
        .annotate(count=Count('id'))
        .order_by('-count')[:limit]
    )
    return [
        {
            'label': (r['project_name'] or '') or '（未关联项目）',
            'count': r['count'],
        }
        for r in qs
    ]


def get_task_counts_by_method(
    start_date: date, end_date: date, limit: int = 20,
) -> list[dict[str, Any]]:
    """按检测方法统计任务数（时间范围：任务创建日）。"""
    from apps.testing.models import TestTask

    qs = (
        TestTask.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )
        .values(method_name=F('test_parameter__name'))
        .annotate(count=Count('id'))
        .order_by('-count')[:limit]
    )
    return [
        {
            'label': (r['method_name'] or '') or '（未命名方法）',
            'count': r['count'],
        }
        for r in qs
    ]


def get_flow_kpis(start_date: date, end_date: date) -> dict[str, Any]:
    from apps.testing.models import TestTask
    from apps.reports.models import Report

    task_total = TestTask.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    ).count()
    task_returned = TestTask.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='unassigned',
        assigned_tester__isnull=True,
    ).count()
    report_total = Report.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    ).count()
    pending_audit = Report.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='pending_audit',
    ).count()
    pending_approve = Report.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='pending_approve',
    ).count()

    return {
        'task_total': task_total,
        'task_returned': task_returned,
        'task_return_rate': round((task_returned / task_total * 100), 1) if task_total else 0,
        'report_total': report_total,
        'pending_audit': pending_audit,
        'pending_approve': pending_approve,
    }


def get_operational_reporting(start_date: date, end_date: date) -> list[dict[str, Any]]:
    from apps.system.models import Role

    rows = []
    for role in Role.objects.filter(code__in=['reception', 'tech_director', 'tester', 'auth_signer']):
        user_count = role.users.filter(is_active=True).count()
        rows.append({
            'role_code': role.code,
            'role_name': role.name,
            'active_users': user_count,
            'start_date': str(start_date),
            'end_date': str(end_date),
        })
    return rows
