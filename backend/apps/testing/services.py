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

from .models import OriginalRecord, TestTask


def generate_task_no() -> str:
    return NumberGenerator.generate(prefix='RW')


def _clean_text(v: str | None) -> str:
    v = (v or '').strip()
    if v in ('', '-', '—', '－'):
        return ''
    return v


def _commission_item_matches_sample(item, sample) -> bool:
    """
    用样品在创建时继承自委托项目（CommissionItem）的字段做弱匹配：
    - specification/grade 必须尽量一致（为空不强校验）
    - name 需能对上 item.test_object 或 item.test_item
    """
    if item is None or sample is None:
        return False

    if item.specification and sample.specification and item.specification != sample.specification:
        return False
    if item.grade and sample.grade and item.grade != sample.grade:
        return False

    sample_name = _clean_text(getattr(sample, 'name', ''))
    # 兼容历史数据：样品 name 可能为空（例如你之前修复过“样品 name 为空”的问题）
    # 若 name 缺失，则仅依赖 specification/grade 的匹配结果来放行委托项目。
    if not sample_name:
        return True

    return (
        _clean_text(getattr(item, 'test_object', '')) == sample_name
        or _clean_text(getattr(item, 'test_item', '')) == sample_name
    )


def _deduped_task_slots(sample, items) -> list[tuple[Any, Any]]:
    """
    与 create_tasks_for_sample 中逐项解析逻辑一致，但对 (方法, 参数) 去重，
    避免并发下重复创建同一组合的任务。
    """
    from apps.testing.models import TestMethod, TestParameter

    seen: set[tuple[int, int | None]] = set()
    slots: list[tuple[Any, Any]] = []
    for item in items:
        if not _commission_item_matches_sample(item, sample):
            continue

        method_name = _clean_text(getattr(item, 'test_method', ''))
        if not method_name:
            continue

        test_method = TestMethod.objects.filter(
            name__iexact=method_name,
            is_active=True,
        ).first()
        if not test_method:
            std_no = _clean_text(getattr(item, 'test_standard', ''))
            if std_no:
                test_method = TestMethod.objects.filter(
                    standard_no__iexact=std_no,
                    is_active=True,
                ).first()

        if not test_method:
            continue

        test_item_name = _clean_text(getattr(item, 'test_item', ''))
        test_parameter = None
        if test_item_name:
            test_parameter = TestParameter.objects.filter(
                method_id=test_method.id,
                name__iexact=test_item_name,
                is_deleted=False,
            ).first()

        key = (test_method.id, test_parameter.id if test_parameter else None)
        if key in seen:
            continue
        seen.add(key)
        slots.append((test_method, test_parameter))
    return slots


@transaction.atomic
def create_tasks_for_sample(sample_id: int, user=None) -> list[TestTask]:
    """
    当“样品检测中但检测任务为空”时：根据样品所属委托单中的委托项目，
    生成对应 TestTask（默认状态为 unassigned）。
    """
    from apps.commissions.models import CommissionItem
    from apps.samples.models import Sample

    sample = (
        Sample.objects.select_for_update()
        .select_related('commission')
        .get(pk=sample_id)
    )
    # 样品检测中：保持与任务流一致
    if sample.status != 'testing':
        sample.status = 'testing'
        sample.save(update_fields=['status', 'updated_at'])

    commission: Any = sample.commission
    if not commission:
        raise ValidationError('样品缺少所属委托单，无法生成检测任务。')

    # 以样品继承的字段为依据，筛选出最可能匹配的委托项目
    items = CommissionItem.objects.filter(commission_id=commission.pk, is_deleted=False) \
        if hasattr(CommissionItem, 'is_deleted') else commission.items.all()

    slots = _deduped_task_slots(sample, items)
    if not slots:
        raise ValidationError('未能为该样品生成检测任务：请检查委托项目中的“检测方法/参数”配置。')

    planned_date = timezone.now().date()
    created: list[TestTask] = []
    for test_method, test_parameter in slots:
        existing = TestTask.objects.filter(
            sample_id=sample.pk,
            test_method_id=test_method.id,
            test_parameter_id=(test_parameter.id if test_parameter else None),
        ).first()
        if existing:
            created.append(existing)
            continue

        task = TestTask.objects.create(
            task_no=generate_task_no(),
            sample=sample,
            commission=commission,
            test_method=test_method,
            test_parameter=test_parameter,
            planned_date=planned_date,
            created_by=user if user and user.is_authenticated else None,
        )
        created.append(task)

    return created


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
    if (
        task.status == 'assigned'
        and task.assigned_tester_id == tester_id
        and task.assigned_equipment_id == equipment_id
        and task.planned_date == planned_date
    ):
        return task

    task.assigned_tester_id = tester_id
    task.assigned_equipment_id = equipment_id
    task.planned_date = planned_date
    task.status = 'assigned'
    task.save(update_fields=[
        'assigned_tester_id', 'assigned_equipment_id',
        'planned_date', 'status', 'updated_at',
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
    return task


@transaction.atomic
def start_task(task_id: int) -> TestTask:
    task = TestTask.objects.select_for_update().get(pk=task_id)
    if task.status == 'in_progress':
        return task

    if task.status != 'assigned':
        raise ValidationError('只有待检状态的任务可以开始检测')

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
        payload={'record_no': record.record_no, 'task_id': record.task_id},
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
            'record_no': record.record_no,
            'approved': approved,
            'status': record.status,
        },
    )
    return record


def build_merged_record_schema_for_task(task_id: int) -> dict:
    """
    按检测方法下参数（若任务指定了 test_parameter 则仅该参数）合并各参数对应的
    原始记录模板 schema；无参数级模板时回退到方法级通用模板。
    """
    from .models import RecordTemplate, TestParameter, TestTask

    task = (
        TestTask.objects.select_related('test_method', 'test_parameter')
        .get(pk=task_id)
    )
    method = task.test_method
    param_qs = TestParameter.objects.filter(
        method=method, is_deleted=False,
    ).order_by('id')
    if task.test_parameter_id:
        param_qs = param_qs.filter(pk=task.test_parameter_id)
    params: list[TestParameter] = list(param_qs)

    if not params:
        tpl = (
            RecordTemplate.objects.filter(
                test_method=method,
                test_parameter__isnull=True,
                is_active=True,
            ).order_by('-created_at').first()
        )
        schema = (tpl.schema if tpl else {}) or {}
        return {
            'task_id': task.id,
            'task_no': task.task_no,
            'sections': [{
                'parameter_id': None,
                'parameter_code': None,
                'parameter_name': None,
                'template_id': tpl.id if tpl else None,
                'template_code': tpl.code if tpl else None,
                'template_name': tpl.name if tpl else None,
                'schema': schema,
            }],
            'merged_fields': schema if isinstance(schema, dict) else {'fields': []},
        }

    sections: list[dict] = []
    merged_field_list: list[dict] = []

    for param in params:
        tpl = (
            RecordTemplate.objects.filter(
                test_method=method,
                test_parameter=param,
                is_active=True,
            ).order_by('-created_at').first()
        )
        if tpl is None:
            tpl = (
                RecordTemplate.objects.filter(
                    test_method=method,
                    test_parameter__isnull=True,
                    is_active=True,
                ).order_by('-created_at').first()
            )
        schema = (tpl.schema if tpl else {}) or {}
        sections.append({
            'parameter_id': param.id,
            'parameter_code': param.code,
            'parameter_name': param.name,
            'template_id': tpl.id if tpl else None,
            'template_code': tpl.code if tpl else None,
            'template_name': tpl.name if tpl else None,
            'schema': schema,
        })
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
    """
    创建原始记录时，用 merged-record-schema 的合并结果生成初始 record_data，
    便于与「单 template FK」并存：values 为各字段名占位，merged_schema 为完整合并结构。
    """
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
