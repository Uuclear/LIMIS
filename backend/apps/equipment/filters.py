from __future__ import annotations

import django_filters
from django.db import models

from .models import Equipment


class EquipmentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        field_name='status', lookup_expr='exact',
    )
    category = django_filters.CharFilter(
        field_name='category', lookup_expr='exact',
    )
    location = django_filters.CharFilter(
        field_name='location', lookup_expr='icontains',
    )
    calibration_before = django_filters.DateFilter(
        field_name='next_calibration_date', lookup_expr='lte',
        label='校准到期日(截止)',
    )
    calibration_after = django_filters.DateFilter(
        field_name='next_calibration_date', lookup_expr='gte',
        label='校准到期日(起始)',
    )
    search = django_filters.CharFilter(method='filter_search', label='搜索')

    class Meta:
        model = Equipment
        fields = [
            'status', 'category', 'location',
            'calibration_before', 'calibration_after',
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value)
            | models.Q(manage_no__icontains=value)
            | models.Q(model_no__icontains=value)
            | models.Q(serial_no__icontains=value),
        )
