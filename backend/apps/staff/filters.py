from __future__ import annotations

import django_filters
from django.db import models

from .models import Certificate, CompetencyEval, StaffProfile, Training


class StaffProfileFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='搜索')
    department = django_filters.CharFilter(
        field_name='user__department', lookup_expr='exact',
    )
    education = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = StaffProfile
        fields = ['department', 'education']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(employee_no__icontains=value)
            | models.Q(user__first_name__icontains=value)
            | models.Q(user__last_name__icontains=value)
            | models.Q(user__username__icontains=value),
        )


class CertificateFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name='staff_id')
    cert_type = django_filters.CharFilter(lookup_expr='icontains')
    expiring_before = django_filters.DateFilter(
        field_name='expiry_date', lookup_expr='lte',
    )

    class Meta:
        model = Certificate
        fields = ['staff', 'cert_type']


class TrainingFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name='staff_id')
    assessment_result = django_filters.CharFilter(lookup_expr='exact')
    date_from = django_filters.DateFilter(
        field_name='training_date', lookup_expr='gte',
    )
    date_to = django_filters.DateFilter(
        field_name='training_date', lookup_expr='lte',
    )

    class Meta:
        model = Training
        fields = ['staff', 'assessment_result']


class CompetencyEvalFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name='staff_id')
    conclusion = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = CompetencyEval
        fields = ['staff', 'conclusion']
