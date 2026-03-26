from __future__ import annotations

import django_filters
from django.db import models

from .models import Report


class ReportFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        field_name='status', lookup_expr='exact',
    )
    commission = django_filters.NumberFilter(field_name='commission_id')
    has_cma = django_filters.BooleanFilter(field_name='has_cma')
    compile_date_from = django_filters.DateFilter(
        field_name='compile_date', lookup_expr='gte', label='编制日期起',
    )
    compile_date_to = django_filters.DateFilter(
        field_name='compile_date', lookup_expr='lte', label='编制日期止',
    )
    issue_date_from = django_filters.DateFilter(
        field_name='issue_date', lookup_expr='gte', label='发放日期起',
    )
    issue_date_to = django_filters.DateFilter(
        field_name='issue_date', lookup_expr='lte', label='发放日期止',
    )
    search = django_filters.CharFilter(method='filter_search', label='搜索')

    class Meta:
        model = Report
        fields = [
            'status', 'commission', 'has_cma',
            'compile_date_from', 'compile_date_to',
            'issue_date_from', 'issue_date_to',
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(report_no__icontains=value)
            | models.Q(commission__commission_no__icontains=value),
        )
