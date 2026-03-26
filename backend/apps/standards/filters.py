from __future__ import annotations

import django_filters
from django.db import models

from .models import Standard


class StandardFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='exact')
    category = django_filters.CharFilter(lookup_expr='exact')
    search = django_filters.CharFilter(method='filter_search', label='搜索')
    implement_after = django_filters.DateFilter(
        field_name='implement_date', lookup_expr='gte',
    )
    implement_before = django_filters.DateFilter(
        field_name='implement_date', lookup_expr='lte',
    )

    class Meta:
        model = Standard
        fields = ['status', 'category']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(standard_no__icontains=value)
            | models.Q(name__icontains=value),
        )
