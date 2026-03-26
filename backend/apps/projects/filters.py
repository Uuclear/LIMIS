import django_filters
from django.db import models

from .models import Project


class ProjectFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='exact')
    project_type = django_filters.CharFilter(lookup_expr='exact')
    start_date_after = django_filters.DateFilter(
        field_name='start_date', lookup_expr='gte', label='开工日期起',
    )
    start_date_before = django_filters.DateFilter(
        field_name='start_date', lookup_expr='lte', label='开工日期止',
    )
    search = django_filters.CharFilter(method='filter_search', label='搜索')

    class Meta:
        model = Project
        fields = ['status', 'project_type']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) | models.Q(code__icontains=value)
        )
