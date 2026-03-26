from __future__ import annotations

import django_filters
from django.db import models


class DateRangeFilterMixin(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='created_at', lookup_expr='date__gte', label='开始日期',
    )
    end_date = django_filters.DateFilter(
        field_name='created_at', lookup_expr='date__lte', label='结束日期',
    )


class BaseFilterSet(DateRangeFilterMixin):
    """
    Base filterset that excludes soft-deleted records and includes date range.
    Subclass this and set Meta.model / Meta.fields.
    """

    class Meta:
        model = None
        exclude = ('is_deleted',)

    @property
    def qs(self) -> models.QuerySet:
        parent_qs = super().qs
        if hasattr(parent_qs.model, 'is_deleted'):
            parent_qs = parent_qs.filter(is_deleted=False)
        return parent_qs
