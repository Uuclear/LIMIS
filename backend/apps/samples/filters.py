from __future__ import annotations

import django_filters

from .models import Sample


class SampleFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    commission = django_filters.NumberFilter(field_name='commission_id')
    project = django_filters.NumberFilter(
        field_name='commission__project_id', label='项目',
    )
    sampling_date_start = django_filters.DateFilter(
        field_name='sampling_date', lookup_expr='gte', label='取样日期起',
    )
    sampling_date_end = django_filters.DateFilter(
        field_name='sampling_date', lookup_expr='lte', label='取样日期止',
    )
    received_date_start = django_filters.DateFilter(
        field_name='received_date', lookup_expr='gte', label='收样日期起',
    )
    received_date_end = django_filters.DateFilter(
        field_name='received_date', lookup_expr='lte', label='收样日期止',
    )
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains', label='样品名称',
    )
    sample_no = django_filters.CharFilter(
        field_name='sample_no', lookup_expr='icontains', label='样品编号',
    )

    class Meta:
        model = Sample
        fields = [
            'status', 'commission', 'project',
            'sampling_date_start', 'sampling_date_end',
            'received_date_start', 'received_date_end',
            'name', 'sample_no',
        ]
