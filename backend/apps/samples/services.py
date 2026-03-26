from __future__ import annotations

import base64
import random
import string
from datetime import datetime
from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.utils.barcode import generate_qrcode
from core.utils.numbering import NumberGenerator

from .models import Sample, SampleDisposal


VALID_TRANSITIONS: dict[str, set[str]] = {
    'pending': {'testing'},
    'testing': {'tested'},
    'tested': {'retained', 'returned', 'disposed'},
    'retained': {'disposed', 'returned'},
    'disposed': set(),
    'returned': set(),
}


def generate_sample_no(commission) -> str:
    return NumberGenerator.generate(
        prefix='YP',
        project_code=getattr(commission, 'commission_no', None),
    )


def generate_blind_no() -> str:
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(chars, k=8))
    return f'BL-{random_part}'


@transaction.atomic
def create_samples_from_commission(commission_id: int) -> list[Sample]:
    from apps.commissions.models import Commission

    commission = Commission.objects.select_related('project').get(pk=commission_id)
    items = commission.items.all() if hasattr(commission, 'items') else []
    samples = []

    for item in items:
        for _ in range(getattr(item, 'quantity', 1)):
            sample = Sample.objects.create(
                sample_no=generate_sample_no(commission),
                blind_no=generate_blind_no(),
                commission=commission,
                name=getattr(item, 'name', ''),
                specification=getattr(item, 'specification', ''),
                grade=getattr(item, 'grade', ''),
                quantity=1,
                unit=getattr(item, 'unit', '个'),
                sampling_date=getattr(
                    commission, 'sampling_date', timezone.now().date(),
                ),
                received_date=getattr(
                    commission, 'received_date', timezone.now().date(),
                ),
                sampling_location=getattr(commission, 'sampling_location', ''),
            )
            samples.append(sample)

    return samples


def change_sample_status(
    sample_id: int,
    new_status: str,
    user,
) -> Sample:
    sample = Sample.objects.get(pk=sample_id)
    allowed = VALID_TRANSITIONS.get(sample.status, set())

    if new_status not in allowed:
        current_display = sample.get_status_display()
        target_display = dict(Sample.STATUS_CHOICES).get(new_status, new_status)
        raise ValidationError(
            f'样品状态不能从「{current_display}」变更为「{target_display}」'
        )

    sample.status = new_status
    sample.save(update_fields=['status', 'updated_at'])

    _log_status_change(sample, new_status, user)
    return sample


def _log_status_change(sample: Sample, new_status: str, user) -> None:
    try:
        from apps.system.models import AuditLog
        AuditLog.objects.create(
            user=user if user and user.is_authenticated else None,
            username=getattr(user, 'username', ''),
            method='STATUS_CHANGE',
            path=f'/samples/{sample.pk}/change_status/',
            body=f'{{"sample_no":"{sample.sample_no}","new_status":"{new_status}"}}',
            ip_address=None,
            status_code=200,
        )
    except Exception:
        pass


def get_sample_timeline(sample_id: int) -> list[dict[str, Any]]:
    try:
        from apps.system.models import AuditLog
    except ImportError:
        return []

    logs = AuditLog.objects.filter(
        path__contains=f'/samples/{sample_id}/',
    ).order_by('timestamp')

    return [
        {
            'timestamp': log.timestamp,
            'user': log.username,
            'method': log.method,
            'action': _parse_action(log),
        }
        for log in logs
    ]


def _parse_action(log) -> str:
    if log.method == 'STATUS_CHANGE':
        return f'状态变更: {log.body}'
    return f'{log.method} {log.path}'


def get_retention_samples() -> QuerySet:
    return Sample.objects.filter(
        status='retained',
    ).select_related(
        'commission', 'commission__project',
    ).order_by('retention_deadline')


def generate_sample_label(sample_id: int) -> dict[str, Any]:
    sample = Sample.objects.select_related(
        'commission', 'commission__project',
    ).get(pk=sample_id)

    qr_data = f'LIMIS:SAMPLE:{sample.sample_no}'
    qr_bytes = generate_qrcode(qr_data, size=200)
    qr_base64 = base64.b64encode(qr_bytes).decode('ascii')

    return {
        'sample_no': sample.sample_no,
        'blind_no': sample.blind_no or '',
        'name': sample.name,
        'specification': sample.specification,
        'grade': sample.grade,
        'commission_no': getattr(sample.commission, 'commission_no', ''),
        'project_name': (
            sample.commission.project.name
            if sample.commission and sample.commission.project
            else ''
        ),
        'sampling_date': str(sample.sampling_date),
        'received_date': str(sample.received_date),
        'qr_code': f'data:image/png;base64,{qr_base64}',
    }


@transaction.atomic
def dispose_sample(
    sample_id: int,
    disposal_type: str,
    disposal_date,
    handler,
    remark: str = '',
) -> SampleDisposal:
    sample = Sample.objects.get(pk=sample_id)
    target = 'returned' if disposal_type == 'return' else 'disposed'
    allowed = VALID_TRANSITIONS.get(sample.status, set())

    if target not in allowed:
        raise ValidationError(
            f'当前状态「{sample.get_status_display()}」不允许处置操作'
        )

    disposal = SampleDisposal.objects.create(
        sample=sample,
        disposal_type=disposal_type,
        disposal_date=disposal_date,
        handler=handler,
        remark=remark,
    )

    sample.status = target
    sample.disposal_date = disposal_date
    sample.disposal_method = dict(SampleDisposal.DISPOSAL_TYPE_CHOICES).get(
        disposal_type, disposal_type,
    )
    sample.save(update_fields=[
        'status', 'disposal_date', 'disposal_method', 'updated_at',
    ])

    _log_status_change(sample, target, handler)
    return disposal
