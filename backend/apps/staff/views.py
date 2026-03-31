from __future__ import annotations

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
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
    StaffProfileCreateSerializer,
    TrainingSerializer,
)


class StaffProfileViewSet(BaseModelViewSet):
    queryset = StaffProfile.objects.select_related('user').all()
    lims_module = 'staff'
    filterset_class = StaffProfileFilter
    search_fields = ['employee_no', 'user__first_name', 'user__last_name']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return StaffProfileCreateSerializer
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

    @action(detail=False, methods=['get'], url_path='assignable-testers')
    def assignable_testers(self, request: Request) -> Response:
        """
        按检测方法过滤可分配检测员：
        - 人员需存在有效授权（Authorization.is_active=True）
        - 授权方式满足其一：
          1) 直接授权了该 test_method
          2) 授权了该方法所属 test_category
        """
        method_id = request.query_params.get('method_id')
        qs = self.get_queryset()
        if method_id:
            try:
                from apps.testing.models import TestMethod
                method = TestMethod.objects.select_related('category').get(pk=int(method_id))
                qs = qs.filter(
                    authorizations__is_active=True,
                ).filter(
                    Q(authorizations__test_methods=method)
                    | Q(authorizations__test_category=method.category),
                )
            except Exception:
                qs = qs.none()
        serializer = StaffProfileListSerializer(qs.distinct(), many=True)
        return Response({'code': 200, 'data': serializer.data})


class CertificateViewSet(BaseModelViewSet):
    queryset = Certificate.objects.select_related('staff').all()
    serializer_class = CertificateSerializer
    lims_module = 'staff'
    filterset_class = CertificateFilter
    search_fields = ['cert_type', 'cert_no']


class AuthorizationViewSet(BaseModelViewSet):
    queryset = Authorization.objects.select_related(
        'staff', 'test_category',
    ).all()
    serializer_class = AuthorizationSerializer
    lims_module = 'staff'
    filterset_fields = ['staff', 'test_category', 'is_active']


class TrainingViewSet(BaseModelViewSet):
    queryset = Training.objects.select_related('staff').all()
    serializer_class = TrainingSerializer
    lims_module = 'staff'
    filterset_class = TrainingFilter
    search_fields = ['title', 'trainer']


class CompetencyEvalViewSet(BaseModelViewSet):
    queryset = CompetencyEval.objects.select_related(
        'staff', 'evaluator',
    ).all()
    serializer_class = CompetencyEvalSerializer
    lims_module = 'staff'
    filterset_class = CompetencyEvalFilter
