from __future__ import annotations

from typing import Optional

from django.db.models import Q
from django.utils import timezone

from .models import QualificationProfile


def get_active_qualification_profile() -> Optional[QualificationProfile]:
    """
    返回当前“有效”的资质配置（简化为：按最近创建时间取一条）。

    规则：
    - is_active=True
    - valid_from 为空 或 valid_from <= today
    - valid_to 为空 或 valid_to >= today
    """
    today = timezone.now().date()
    qs = QualificationProfile.objects.filter(
        is_deleted=False,
        is_active=True,
    ).filter(
        Q(valid_from__isnull=True) | Q(valid_from__lte=today),
    ).filter(
        Q(valid_to__isnull=True) | Q(valid_to__gte=today),
    )
    return qs.order_by('-created_at').first()

