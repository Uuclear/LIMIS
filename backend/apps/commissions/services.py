from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.utils.numbering import NumberGenerator

from .models import Commission


def generate_commission_no(project) -> str:
    return NumberGenerator.generate(prefix='WT')


@transaction.atomic
def submit_commission(commission_id: int, user) -> Commission:
    commission = Commission.objects.select_for_update().get(pk=commission_id)

    if commission.status != 'draft':
        raise ValidationError('只有草稿状态的委托单可以提交')

    if not commission.items.exists():
        raise ValidationError('委托单至少需要一个检测项目')

    commission.status = 'pending_review'
    commission.save(update_fields=['status', 'updated_at'])

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
    return commission
