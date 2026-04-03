from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.utils.numbering import NumberGenerator

from .models import Commission, CommissionItem, ContractReview


def generate_commission_no(project) -> str:
    return NumberGenerator.generate(prefix='WT')


@transaction.atomic
def submit_commission(commission_id: int, user) -> Commission:
    commission = Commission.objects.select_for_update().get(pk=commission_id)

    if commission.status not in ('draft', 'rejected'):
        raise ValidationError('只有草稿或已退回状态的委托单可以提交')

    if not commission.items.exists():
        raise ValidationError('委托单至少需要一个检测项目')

    commission.status = 'pending_review'
    commission.save(update_fields=['status', 'updated_at'])

    # Auto-create tasks for any samples already registered under this commission
    from apps.samples.models import Sample
    from apps.testing.services import create_tasks_for_sample
    existing_samples = list(Sample.objects.filter(
        commission=commission, is_deleted=False,
    ))
    for sample in existing_samples:
        try:
            create_tasks_for_sample(sample.id, user=user)
        except Exception:
            pass

    from apps.system.services import notify_users_by_permission_code
    notify_users_by_permission_code(
        'commission:approve',
        'commission_review',
        f'委托待评审：{commission.commission_no}',
        f'项目：{commission.project.name}' if commission.project_id else '',
        f'/entrustment/{commission.pk}',
    )
    return commission


@transaction.atomic
def review_commission(
    commission_id: int,
    user,
    approved: bool,
    comment: str = '',
) -> Commission:
    commission = Commission.objects.select_for_update().get(pk=commission_id)

    if commission.status != 'pending_review':
        raise ValidationError('只有待评审状态的委托单可以评审')

    commission.reviewer = user
    commission.review_date = timezone.now()
    commission.review_comment = comment
    commission.status = 'reviewed' if approved else 'rejected'
    commission.save(update_fields=[
        'status', 'reviewer', 'review_date', 'review_comment', 'updated_at',
    ])

    if approved:
        # Auto-create samples from commission items
        from apps.samples.services import create_samples_from_commission
        try:
            create_samples_from_commission(commission.id)
        except Exception:
            pass  # Don't fail the review if sample creation has issues

    return commission


@transaction.atomic
def cascade_soft_delete_commission(commission_id: int) -> None:
    """
    软删除委托及其在系统内的业务从属数据，避免仅标记委托导致外键仍可查但默认管理器取不到、接口 500。

    规则：仅 **草稿** 可删除；已提交及后续状态须使用「终止」而非删除。
    若存在已发放或已归档的报告，亦禁止删除（双保险）。
    """
    from apps.reports.models import Report, ReportApproval, ReportDistribution
    from apps.samples.models import Sample
    from apps.testing.models import OriginalRecord, TestResult, TestTask

    commission = Commission.objects.select_for_update().get(pk=commission_id)
    if commission.status != 'draft':
        raise ValidationError(
            '仅草稿状态的委托可删除；已提交或已进入流程的委托请使用「终止」。',
        )

    if Report.objects.filter(
        commission_id=commission_id,
        status__in=['issued', 'archived'],
        is_deleted=False,
    ).exists():
        raise ValidationError(
            '存在已发放或已归档的检测报告，无法删除委托。请先作废报告后再操作。',
        )

    now = timezone.now()

    task_ids = list(
        TestTask.objects.filter(
            commission_id=commission_id,
            is_deleted=False,
        ).values_list('id', flat=True),
    )
    if task_ids:
        TestResult.objects.filter(
            task_id__in=task_ids,
            is_deleted=False,
        ).update(is_deleted=True, updated_at=now)
        OriginalRecord.objects.filter(
            task_id__in=task_ids,
            is_deleted=False,
        ).update(is_deleted=True, updated_at=now)
        TestTask.objects.filter(pk__in=task_ids).update(
            is_deleted=True, updated_at=now,
        )

    report_ids = list(
        Report.objects.filter(
            commission_id=commission_id,
            is_deleted=False,
        ).values_list('id', flat=True),
    )
    if report_ids:
        ReportApproval.objects.filter(
            report_id__in=report_ids,
            is_deleted=False,
        ).update(is_deleted=True, updated_at=now)
        ReportDistribution.objects.filter(
            report_id__in=report_ids,
            is_deleted=False,
        ).update(is_deleted=True, updated_at=now)
        Report.objects.filter(pk__in=report_ids).update(
            is_deleted=True, updated_at=now,
        )

    Sample.objects.filter(
        commission_id=commission_id,
        is_deleted=False,
    ).update(is_deleted=True, updated_at=now)

    CommissionItem.objects.filter(
        commission_id=commission_id,
        is_deleted=False,
    ).update(is_deleted=True, updated_at=now)
    ContractReview.objects.filter(
        commission_id=commission_id,
        is_deleted=False,
    ).update(is_deleted=True, updated_at=now)

    Commission.objects.filter(pk=commission_id).update(
        is_deleted=True, updated_at=now,
    )


@transaction.atomic
def terminate_commission(commission_id: int, user, reason: str = '') -> Commission:
    """
    终止委托：将状态置为已取消，不执行级联软删，保留业务追溯。
    草稿应使用删除；已终止不可重复操作。
    """
    commission = Commission.objects.select_for_update().get(pk=commission_id)
    if commission.status == 'draft':
        raise ValidationError('草稿委托请使用删除，无需终止')
    if commission.status == 'cancelled':
        raise ValidationError('该委托已终止')
    commission.status = 'cancelled'
    if reason and str(reason).strip():
        prefix = (commission.remark or '').strip()
        line = f'终止原因：{str(reason).strip()}'
        commission.remark = f'{prefix}\n{line}'.strip() if prefix else line
    commission.save(update_fields=['status', 'remark', 'updated_at'])
    return commission
