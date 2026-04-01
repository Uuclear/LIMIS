from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.utils.numbering import NumberGenerator
from core.audit import log_business_event
from apps.system.services import has_permission_code

from .models import OriginalRecord, TestTask


def _require_permission(user, permission_code: str, action_label: str) -> None:
    if has_permission_code(user, permission_code):
        return
    raise ValidationError(f'无权限执行{action_label}')


def generate_task_no() -> str:
    return NumberGenerator.generate(prefix='RW')


@transaction.atomic
def create_tasks_for_sample(sample_id: int, user=None) -> list[TestTask]:
    from apps.commissions.models import CommissionItem
    from apps.samples.models import Sample

    sample = Sample.objects.select_for_update().get(pk=sample_id)
    if not sample.commission_id:
        raise ValidationError('样品未关联委托单')

    items = CommissionItem.objects.filter(
        commission_id=sample.commission_id, is_deleted=False,
    ).select_related('test_parameter')

    created: list[TestTask] = []
    for item in items:
        if not item.test_parameter_id:
            continue
        if item.specification and sample.specification and item.specification != sample.specification:
            continue
        if item.grade and sample.grade and item.grade != sample.grade:
            continue
        if TestTask.objects.filter(
            sample=sample, test_parameter=item.test_parameter, is_deleted=False,
        ).exists():
            continue
        task = TestTask.objects.create(
            task_no=generate_task_no(),
            sample=sample,
            commission=sample.commission,
            test_parameter=item.test_parameter,
            status='unassigned',
            created_by=user if user and user.is_authenticated else None,
        )
        created.append(task)

    if created and sample.status == 'pending':
        sample.status = 'testing'
        sample.save(update_fields=['status', 'updated_at'])
    return created


@transaction.atomic
def assign_task(
    task_id: int,
    user,
    tester_id: int,
    equipment_id: int | None = None,
    planned_date: datetime.date | None = None,
) -> TestTask:
    _require_permission(user, 'task:edit', '任务分配')
    task = TestTask.objects.select_for_update().get(pk=task_id)

    if task.status not in ('unassigned', 'in_progress'):
        raise ValidationError('只有待分配或检测中状态的任务可以分配')
    if (
        task.status == 'in_progress'
        and task.assigned_tester_id == tester_id
        and task.assigned_equipment_id == equipment_id
        and task.planned_date == planned_date
    ):
        return task

    task.assigned_tester_id = tester_id
    task.assigned_equipment_id = equipment_id
    task.planned_date = planned_date
    task.status = 'in_progress'
    if task.actual_date is None:
        task.actual_date = timezone.now().date()
    task.save(update_fields=[
        'assigned_tester_id', 'assigned_equipment_id',
        'planned_date', 'status', 'actual_date', 'updated_at',
    ])
    log_business_event(
        user=None,
        module='testing',
        action='assign_task',
        entity='test_task',
        entity_id=task.pk,
        path=f'/api/v1/testing/tasks/{task.pk}/assign/',
        payload={
            'task_no': task.task_no,
            'tester_id': tester_id,
            'equipment_id': equipment_id,
            'planned_date': str(planned_date) if planned_date else None,
        },
    )
    from apps.system.services import notify_user

    notify_user(
        tester_id,
        'task_assigned',
        f'检测任务已分配：{task.task_no}',
        '',
        f'/testing/tasks/{task.pk}',
    )
    return task


@transaction.atomic
def return_to_commission(task_id: int, user, reason: str = '') -> TestTask:
    _require_permission(user, 'task:edit', '任务退回委托')
    reason = (reason or '').strip()
    if len(reason) < 4:
        raise ValidationError('退回原因至少 4 个字符')

    task = TestTask.objects.select_related('commission').select_for_update().get(pk=task_id)
    if task.status != 'unassigned':
        raise ValidationError('仅待分配任务可退回到委托流程')

    commission = task.commission
    related_tasks = TestTask.objects.select_for_update().filter(commission_id=commission.id, is_deleted=False)
    busy = related_tasks.exclude(status='unassigned').exists()
    if busy:
        raise ValidationError('存在非待分配任务，无法退回到委托流程')

    commission.status = 'rejected'
    commission.reviewer_id = None
    commission.review_date = None
    commission.review_comment = reason[:500]
    commission.save(update_fields=['status', 'reviewer_id', 'review_date', 'review_comment', 'updated_at'])

    sample_ids = list(related_tasks.values_list('sample_id', flat=True))
    for t in related_tasks:
        t.soft_delete()

    if sample_ids:
        from apps.samples.models import Sample
        Sample.objects.filter(id__in=sample_ids, is_deleted=False).update(status='pending')

    log_business_event(
        user=user,
        module='commission',
        action='task_return_to_commission',
        entity='commission',
        entity_id=commission.pk,
        path=f'/api/v1/testing/tasks/{task.pk}/return-commission/',
        payload={'commission_no': commission.commission_no, 'task_no': task.task_no, 'reason': reason[:500]},
    )
    return task


def return_task(task_id: int, user, reason: str = '') -> TestTask:
    _require_permission(user, 'task:edit', '任务退回')
    reason = (reason or '').strip()
    if len(reason) < 4:
        raise ValidationError('退回原因至少 4 个字符')
    task = TestTask.objects.select_for_update().get(pk=task_id)
    if task.status == 'unassigned':
        return task
    task.status = 'unassigned'
    task.assigned_tester_id = None
    task.assigned_equipment_id = None
    task.save(update_fields=[
        'status', 'assigned_tester_id', 'assigned_equipment_id', 'updated_at',
    ])
    log_business_event(
        user=user,
        module='task',
        action='return',
        entity='test_task',
        entity_id=task.pk,
        path=f'/api/v1/testing/tasks/{task.pk}/return/',
        payload={'task_no': task.task_no, 'reason': reason[:500]},
    )
    from apps.system.services import notify_flow_targets
    notify_flow_targets(
        role_code='tech_director',
        fallback_permission_code='task:edit',
        notification_type='task_returned',
        title=f'任务已退回待分配：{task.task_no}',
        content=reason[:200],
        link_path=f'/testing/tasks/{task.pk}',
    )
    return task


@transaction.atomic
def start_task(task_id: int) -> TestTask:
    task = TestTask.objects.select_for_update().get(pk=task_id)
    if task.status == 'in_progress':
        return task

    if task.status == 'unassigned':
        raise ValidationError('请先分配检测人员')

    task.status = 'in_progress'
    task.actual_date = timezone.now().date()
    task.save(update_fields=['status', 'actual_date', 'updated_at'])

    task.sample.status = 'testing'
    task.sample.save(update_fields=['status', 'updated_at'])
    log_business_event(
        module='testing',
        action='start_task',
        entity='test_task',
        entity_id=task.pk,
        path=f'/api/v1/testing/tasks/{task.pk}/start/',
        payload={'task_no': task.task_no},
    )
    return task


@transaction.atomic
def complete_task(task_id: int) -> TestTask:
    task = TestTask.objects.select_for_update().get(pk=task_id)
    if task.status == 'completed':
        return task

    if task.status != 'in_progress':
        raise ValidationError('只有检测中的任务可以完成')

    task.status = 'completed'
    task.save(update_fields=['status', 'updated_at'])

    pending = task.sample.tasks.exclude(status='completed').exists()
    if not pending:
        task.sample.status = 'tested'
        task.sample.save(update_fields=['status', 'updated_at'])
    log_business_event(
        module='testing',
        action='complete_task',
        entity='test_task',
        entity_id=task.pk,
        path=f'/api/v1/testing/tasks/{task.pk}/complete/',
        payload={'task_no': task.task_no, 'sample_id': task.sample_id},
    )
    return task


def get_today_tasks(user=None) -> QuerySet:
    qs = TestTask.objects.filter(
        planned_date=timezone.now().date(),
    ).select_related('sample', 'test_parameter', 'assigned_tester')
    if user is not None:
        qs = qs.filter(assigned_tester=user)
    return qs


def get_overdue_tasks() -> QuerySet:
    return TestTask.objects.filter(
        planned_date__lt=timezone.now().date(),
    ).exclude(
        status='completed',
    ).select_related('sample', 'test_parameter', 'assigned_tester')


def get_age_calendar_data(year: int, month: int) -> list[dict]:
    start = datetime.date(year, month, 1)
    if month == 12:
        end = datetime.date(year + 1, 1, 1)
    else:
        end = datetime.date(year, month + 1, 1)

    tasks = TestTask.objects.filter(
        planned_date__gte=start,
        planned_date__lt=end,
    ).select_related('sample', 'test_parameter').order_by('planned_date')

    grouped: dict[datetime.date, list] = defaultdict(list)
    for task in tasks:
        grouped[task.planned_date].append({
            'id': task.id,
            'task_no': task.task_no,
            'sample_name': task.sample.name,
            'status': task.status,
            'age_days': task.age_days,
        })
    return [
        {'date': str(date), 'tasks': items}
        for date, items in sorted(grouped.items())
    ]


def calculate_planned_date(
    production_date: datetime.date,
    age_days: int,
) -> datetime.date:
    return production_date + datetime.timedelta(days=age_days)


@transaction.atomic
def submit_record(record_id: int) -> OriginalRecord:
    record = OriginalRecord.objects.select_for_update().get(pk=record_id)
    if record.status == 'pending_review':
        return record

    if record.status != 'draft':
        raise ValidationError('只有草稿状态的记录可以提交')

    record.status = 'pending_review'
    record.save(update_fields=['status', 'updated_at'])
    log_business_event(
        module='testing',
        action='submit_record',
        entity='original_record',
        entity_id=record.pk,
        path=f'/api/v1/testing/records/{record.pk}/submit/',
        payload={'task_id': record.task_id},
    )
    return record


@transaction.atomic
def review_record(
    record_id: int,
    user,
    approved: bool,
    comment: str = '',
) -> OriginalRecord:
    record = OriginalRecord.objects.select_for_update().get(pk=record_id)
    target_status = 'reviewed' if approved else 'returned'
    if record.status == target_status:
        return record

    if record.status != 'pending_review':
        raise ValidationError('只有待复核状态的记录可以复核')

    record.reviewer = user
    record.review_date = timezone.now()
    record.review_comment = comment
    record.status = 'reviewed' if approved else 'returned'
    record.save(update_fields=[
        'status', 'reviewer', 'review_date',
        'review_comment', 'updated_at',
    ])
    log_business_event(
        user=user,
        module='testing',
        action='review_record',
        entity='original_record',
        entity_id=record.pk,
        path=f'/api/v1/testing/records/{record.pk}/review/',
        payload={
            'approved': approved,
            'status': record.status,
        },
    )
    return record


def build_merged_record_schema_for_task(task_id: int) -> dict:
    """
    Build a merged record schema for a task based on its test_parameter.
    Finds matching RecordTemplates by test_parameter.
    """
    from django.db.models import Q
    from .models import RecordTemplate, TestParameter, TestTask

    task = (
        TestTask.objects.select_related('test_parameter')
        .get(pk=task_id)
    )
    param = task.test_parameter

    if not param:
        return {
            'task_id': task.id,
            'task_no': task.task_no,
            'sections': [],
            'merged_fields': {'fields': []},
        }

    # Find template for this parameter
    tpl = (
        RecordTemplate.objects.filter(
            is_active=True,
        ).filter(
            Q(test_parameter=param) | Q(test_parameters=param)
        ).distinct().order_by('-created_at').first()
    )

    if tpl is None:
        # Fallback: generic template with no parameter
        tpl = (
            RecordTemplate.objects.filter(
                test_parameter__isnull=True,
                is_active=True,
            ).order_by('-created_at').first()
        )

    schema = (tpl.schema if tpl else {}) or {}
    sections = [{
        'parameter_id': param.id,
        'parameter_code': param.code,
        'parameter_name': param.name,
        'template_id': tpl.id if tpl else None,
        'template_code': tpl.code if tpl else None,
        'template_name': tpl.name if tpl else None,
        'schema': schema,
    }]

    merged_field_list: list[dict] = []
    if isinstance(schema, dict):
        fields = schema.get('fields')
        if isinstance(fields, list):
            for f in fields:
                if isinstance(f, dict):
                    merged_field_list.append({
                        **f,
                        '_parameter_id': param.id,
                        '_parameter_name': param.name,
                    })

    return {
        'task_id': task.id,
        'task_no': task.task_no,
        'sections': sections,
        'merged_fields': {'fields': merged_field_list},
    }


def build_initial_record_data_from_task(task_id: int) -> dict[str, Any]:
    merged = build_merged_record_schema_for_task(task_id)
    fields = merged.get('merged_fields', {}).get('fields', [])
    values: dict[str, Any] = {}
    for f in fields:
        if isinstance(f, dict):
            name = f.get('name')
            if name:
                values[str(name)] = None
    return {
        'merged_schema': merged,
        'values': values,
    }
