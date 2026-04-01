from __future__ import annotations

from typing import Any

from django.apps import apps


def get_project_stats(project_id: int) -> dict[str, Any]:
    stats: dict[str, Any] = {
        'commission_count': 0,
        'sample_count': 0,
        'report_count': 0,
        'organization_count': 0,
        'contract_count': 0,
        'witness_count': 0,
        'sampler_count': 0,
    }

    from .models import Contract, Organization, Sampler, Witness
    stats['organization_count'] = Organization.objects.filter(
        project_id=project_id,
    ).count()
    stats['contract_count'] = Contract.objects.filter(
        project_id=project_id,
    ).count()
    stats['witness_count'] = Witness.objects.filter(
        project_id=project_id,
    ).count()
    stats['sampler_count'] = Sampler.objects.filter(
        project_id=project_id,
    ).count()

    try:
        Commission = apps.get_model('commissions', 'Commission')
        stats['commission_count'] = Commission.objects.filter(
            project_id=project_id,
        ).count()
    except LookupError:
        pass

    try:
        Sample = apps.get_model('samples', 'Sample')
        stats['sample_count'] = Sample.objects.filter(
            commission__project_id=project_id,
        ).count()
    except LookupError:
        pass

    try:
        Report = apps.get_model('reports', 'Report')
        stats['report_count'] = Report.objects.filter(
            commission__project_id=project_id,
        ).count()
    except LookupError:
        pass

    try:
        TestTask = apps.get_model('testing', 'TestTask')
        qs = TestTask.objects.filter(commission__project_id=project_id)
        stats['completed_count'] = qs.filter(status='completed').count()
        stats['unassigned_count'] = qs.filter(status='unassigned').count()
        stats['in_progress_count'] = qs.filter(status='in_progress').count()
        stats['task_total'] = qs.count()
    except LookupError:
        stats['completed_count'] = 0
        stats['unassigned_count'] = 0
        stats['in_progress_count'] = 0
        stats['task_total'] = 0

    return stats
