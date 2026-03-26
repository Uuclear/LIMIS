from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from .filters import (
    CertificateFilter,
    CompetencyEvalFilter,
    StaffProfileFilter,
    TrainingFilter,
)
from .models import (
    Authorization,
    Certificate,
    CompetencyEval,
    StaffProfile,
    Training,
)
from .serializers import (
    AuthorizationSerializer,
    CertificateSerializer,
    CompetencyEvalSerializer,
    StaffProfileDetailSerializer,
    StaffProfileListSerializer,
    TrainingSerializer,
)


class StaffProfileViewSet(BaseModelViewSet):
    queryset = StaffProfile.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = StaffProfileFilter
    search_fields = ['employee_no', 'user__first_name', 'user__last_name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StaffProfileDetailSerializer
        return StaffProfileListSerializer

    @action(detail=False, methods=['get'], url_path='expiring-certs')
    def expiring_certs(self, request: Request) -> Response:
        threshold = timezone.now().date() + timedelta(days=90)
        certs = Certificate.objects.filter(
            expiry_date__isnull=False,
            expiry_date__lte=threshold,
            is_deleted=False,
        ).select_related('staff', 'staff__user')
        serializer = CertificateSerializer(certs, many=True)
        return Response({'code': 200, 'data': serializer.data})


class CertificateViewSet(BaseModelViewSet):
    queryset = Certificate.objects.select_related('staff').all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CertificateFilter
    search_fields = ['cert_type', 'cert_no']


class AuthorizationViewSet(BaseModelViewSet):
    queryset = Authorization.objects.select_related(
        'staff', 'test_category',
    ).all()
    serializer_class = AuthorizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['staff', 'test_category', 'is_active']


class TrainingViewSet(BaseModelViewSet):
    queryset = Training.objects.select_related('staff').all()
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = TrainingFilter
    search_fields = ['title', 'trainer']


class CompetencyEvalViewSet(BaseModelViewSet):
    queryset = CompetencyEval.objects.select_related(
        'staff', 'evaluator',
    ).all()
    serializer_class = CompetencyEvalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CompetencyEvalFilter
