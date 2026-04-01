from __future__ import annotations

import django_filters
from django.db import models

from .models import OriginalRecord, RecordTemplate, TestResult, TestTask


class TestTaskFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    assigned_tester = django_filters.NumberFilter(field_name='assigned_tester_id')
    commission = django_filters.NumberFilter(field_name='commission_id')
    sample = django_filters.NumberFilter(field_name='sample_id')
    test_parameter = django_filters.NumberFilter(field_name='test_parameter_id')
    planned_date_from = django_filters.DateFilter(
        field_name='planned_date', lookup_expr='gte', label='计划日期起',
    )
    planned_date_to = django_filters.DateFilter(
        field_name='planned_date', lookup_expr='lte', label='计划日期止',
    )
    search = django_filters.CharFilter(method='filter_search', label='搜索')

    class Meta:
        model = TestTask
        fields = [
            'status', 'assigned_tester', 'commission', 'sample',
            'test_parameter', 'planned_date_from', 'planned_date_to',
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(task_no__icontains=value)
            | models.Q(sample__sample_no__icontains=value),
        )


class OriginalRecordFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    recorder = django_filters.NumberFilter(field_name='recorder_id')
    review_date_from = django_filters.DateTimeFilter(
        field_name='review_date', lookup_expr='gte', label='复核日期起',
    )
    review_date_to = django_filters.DateTimeFilter(
        field_name='review_date', lookup_expr='lte', label='复核日期止',
    )

    class Meta:
        model = OriginalRecord
        fields = ['status', 'recorder', 'review_date_from', 'review_date_to']


class RecordTemplateFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(method='filter_keyword', label='关键词')
    test_parameter = django_filters.NumberFilter(field_name='test_parameter_id')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = RecordTemplate
        fields = ['test_parameter', 'is_active']

    def filter_keyword(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            models.Q(name__icontains=value)
            | models.Q(code__icontains=value),
        )


class TestResultFilter(django_filters.FilterSet):
    judgment = django_filters.CharFilter(field_name='judgment', lookup_expr='exact')
    task = django_filters.NumberFilter(field_name='task_id')

    class Meta:
        model = TestResult
        fields = ['judgment', 'task']
