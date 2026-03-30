from __future__ import annotations

from typing import Any

from django.db.models import Count, Q, QuerySet
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from . import services
from .filters import ProjectFilter
from .models import Contract, Organization, Project, SubProject, Witness
from .serializers import (
    ContractSerializer,
    OrganizationSerializer,
    ProjectCreateUpdateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    SubProjectSerializer,
    WitnessSerializer,
)


class ProjectViewSet(BaseModelViewSet):
    lims_module = 'project'
    filterset_class = ProjectFilter
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'start_date', 'created_at']

    def get_queryset(self) -> QuerySet:
        qs = Project.objects.filter(is_deleted=False)
        if self.action == 'list':
            qs = qs.annotate(
                organization_count=Count(
                    'organizations',
                    filter=Q(organizations__is_deleted=False),
                ),
                commission_count=Count(
                    'commissions',
                    filter=Q(commissions__is_deleted=False),
                ),
            )
        return qs

    def get_serializer_class(self) -> type:
        if self.action == 'list':
            return ProjectListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    @action(detail=True, methods=['get'])
    def stats(self, request: Request, pk: str = None) -> Response:
        project = self.get_object()
        data = services.get_project_stats(project.id)
        return Response({'code': 200, 'data': data})


class ProjectNestedMixin:
    """Scopes queryset to the parent project from URL kwargs."""
    lims_module = 'project'

    def get_project_id(self) -> int:
        return int(self.kwargs['project_pk'])

    def get_queryset(self) -> QuerySet:
        return (
            super().get_queryset()
            .filter(project_id=self.get_project_id())
        )

    def perform_create(self, serializer: Any) -> None:
        serializer.save(project_id=self.get_project_id())


class OrganizationViewSet(ProjectNestedMixin, BaseModelViewSet):
    queryset = Organization.objects.filter(is_deleted=False)
    serializer_class = OrganizationSerializer
    search_fields = ['name', 'contact_person']
    filterset_fields = ['role']


class SubProjectViewSet(ProjectNestedMixin, BaseModelViewSet):
    serializer_class = SubProjectSerializer
    search_fields = ['name', 'code']

    def get_queryset(self) -> QuerySet:
        qs = SubProject.objects.filter(
            project_id=self.get_project_id(),
            is_deleted=False,
        )
        if self.action == 'list':
            qs = qs.filter(parent__isnull=True)
        return qs


class ContractViewSet(ProjectNestedMixin, BaseModelViewSet):
    queryset = Contract.objects.filter(is_deleted=False)
    serializer_class = ContractSerializer
    search_fields = ['contract_no', 'title']


class WitnessViewSet(ProjectNestedMixin, BaseModelViewSet):
    queryset = Witness.objects.select_related('organization').filter(
        is_deleted=False,
    )
    serializer_class = WitnessSerializer
    search_fields = ['name', 'certificate_no']
    filterset_fields = ['is_active']
