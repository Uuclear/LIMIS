from __future__ import annotations

import django_filters
from django.db import models

from .models import Commission


class CommissionFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        field_name='status', lookup_expr='exact',
    )
    project = django_filters.NumberFilter(field_name='project_id')
    is_witnessed = django_filters.BooleanFilter(field_name='is_witnessed')
    date_from = django_filters.DateFilter(
        field_name='commission_date', lookup_expr='gte', label='委托日期起',
    )
    date_to = django_filters.DateFilter(
        field_name='commission_date', lookup_expr='lte', label='委托日期止',
    )
    search = django_filters.CharFilter(method='filter_search', label='搜索')

    class Meta:
        model = Commission
        fields = ['status', 'project', 'is_witnessed', 'date_from', 'date_to']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(commission_no__icontains=value)
            | models.Q(construction_part__icontains=value),
        )
