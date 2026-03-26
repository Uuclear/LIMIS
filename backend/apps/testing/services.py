from __future__ import annotations

import datetime
from collections import defaultdict

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.utils.numbering import NumberGenerator

from .models import OriginalRecord, TestTask


def generate_task_no() -> str:
    return NumberGenerator.generate(prefix='RW')


@transaction.atomic
def assign_task(
    task_id: int,
    tester_id: int,
    equipment_id: int | None = None,
    planned_date: datetime.date | None = None,
) -> TestTask:
    task = TestTask.objects.select_for_update().get(pk=task_id)

    if task.status not in ('unassigned', 'assigned'):
        raise ValidationError('只有待分配或待检状态的任务可以分配')

    task.assigned_tester_id = tester_id
    task.assigned_equipment_id = equipment_id
    task.planned_date = planned_date
    task.status = 'assigned'
    task.save(update_fields=[
        'assigned_tester_id', 'assigned_equipment_id',
        'planned_date', 'status', 'updated_at',
    ])
    return task


@transaction.atomic
def start_task(task_id: int) -> TestTask:
    task = TestTask.objects.select_for_update().get(pk=task_id)

    if task.status != 'assigned':
        raise ValidationError('只有待检状态的任务可以开始检测')

    task.status = 'in_progress'
    task.actual_date = timezone.now().date()
    task.save(update_fields=['status', 'actual_date', 'updated_at'])

    task.sample.status = 'testing'
    task.sample.save(update_fields=['status', 'updated_at'])
    return task


@transaction.atomic
def complete_task(task_id: int) -> TestTask:
    task = TestTask.objects.select_for_update().get(pk=task_id)

    if task.status != 'in_progress':
        raise ValidationError('只有检测中的任务可以完成')

    task.status = 'completed'
    task.save(update_fields=['status', 'updated_at'])

    pending = task.sample.tasks.exclude(status='completed').exists()
    if not pending:
        task.sample.status = 'tested'
        task.sample.save(update_fields=['status', 'updated_at'])
    return task


def get_today_tasks(user=None) -> QuerySet:
    qs = TestTask.objects.filter(
        planned_date=timezone.now().date(),
    ).select_related('sample', 'test_method', 'assigned_tester')
    if user is not None:
        qs = qs.filter(assigned_tester=user)
    return qs


def get_overdue_tasks() -> QuerySet:
    return TestTask.objects.filter(
        planned_date__lt=timezone.now().date(),
    ).exclude(
        status='completed',
    ).select_related('sample', 'test_method', 'assigned_tester')


def get_age_calendar_data(year: int, month: int) -> list[dict]:
    start = datetime.date(year, month, 1)
    if month == 12:
        end = datetime.date(year + 1, 1, 1)
    else:
        end = datetime.date(year, month + 1, 1)

    tasks = TestTask.objects.filter(
        planned_date__gte=start,
        planned_date__lt=end,
    ).select_related('sample', 'test_method').order_by('planned_date')

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

    if record.status != 'draft':
        raise ValidationError('只有草稿状态的记录可以提交')

    record.status = 'pending_review'
    record.save(update_fields=['status', 'updated_at'])
    return record


@transaction.atomic
def review_record(
    record_id: int,
    user,
    approved: bool,
    comment: str = '',
) -> OriginalRecord:
    record = OriginalRecord.objects.select_for_update().get(pk=record_id)

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
    return record
