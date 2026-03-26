from __future__ import annotations

import django_filters
from django.db import models

from .models import (
    Complaint,
    InternalAudit,
    ManagementReview,
    NonConformity,
    ProficiencyTest,
    QualitySupervision,
)


class InternalAuditFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='exact')
    audit_type = django_filters.CharFilter(lookup_expr='exact')
    search = django_filters.CharFilter(method='filter_search', label='搜索')
    date_from = django_filters.DateFilter(
        field_name='planned_date', lookup_expr='gte',
    )
    date_to = django_filters.DateFilter(
        field_name='planned_date', lookup_expr='lte',
    )

    class Meta:
        model = InternalAudit
        fields = ['status', 'audit_type']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(audit_no__icontains=value)
            | models.Q(title__icontains=value),
        )


class ManagementReviewFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='exact')
    year = django_filters.NumberFilter(
        field_name='review_date', lookup_expr='year',
    )

    class Meta:
        model = ManagementReview
        fields = ['status']


class NonConformityFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='exact')
    source = django_filters.CharFilter(lookup_expr='exact')
    search = django_filters.CharFilter(method='filter_search', label='搜索')

    class Meta:
        model = NonConformity
        fields = ['status', 'source']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(nc_no__icontains=value)
            | models.Q(description__icontains=value),
        )


class ComplaintFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='exact')
    date_from = django_filters.DateFilter(
        field_name='complaint_date', lookup_expr='gte',
    )
    date_to = django_filters.DateFilter(
        field_name='complaint_date', lookup_expr='lte',
    )

    class Meta:
        model = Complaint
        fields = ['status']


class ProficiencyTestFilter(django_filters.FilterSet):
    result = django_filters.CharFilter(lookup_expr='exact')
    year = django_filters.NumberFilter(
        field_name='participation_date', lookup_expr='year',
    )

    class Meta:
        model = ProficiencyTest
        fields = ['result']


class QualitySupervisionFilter(django_filters.FilterSet):
    conclusion = django_filters.CharFilter(lookup_expr='exact')
    date_from = django_filters.DateFilter(
        field_name='supervision_date', lookup_expr='gte',
    )
    date_to = django_filters.DateFilter(
        field_name='supervision_date', lookup_expr='lte',
    )

    class Meta:
        model = QualitySupervision
        fields = ['conclusion']
