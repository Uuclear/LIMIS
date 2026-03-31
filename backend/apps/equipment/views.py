from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from . import services
from .filters import EquipmentFilter
from .models import (
    Calibration,
    Equipment,
    EquipUsageLog,
    Maintenance,
    PeriodCheck,
)
from .serializers import (
    CalibrationSerializer,
    EquipmentCreateUpdateSerializer,
    EquipmentDetailSerializer,
    EquipmentListSerializer,
    EquipUsageLogSerializer,
    MaintenanceSerializer,
    PeriodCheckSerializer,
)


class EquipmentViewSet(BaseModelViewSet):
    queryset = Equipment.objects.all()
    lims_module = 'equipment'
    filterset_class = EquipmentFilter
    search_fields = ['name', 'manage_no', 'model_no', 'serial_no']
    ordering_fields = ['manage_no', 'name', 'created_at', 'next_calibration_date']

    def get_serializer_class(self) -> type:
        if self.action == 'list':
            return EquipmentListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return EquipmentCreateUpdateSerializer
        return EquipmentDetailSerializer

    @action(detail=False, methods=['get'])
    def expiring(self, request: Request) -> Response:
        # 提醒阈值：仅当距离校准到期日 <= 15 天时提醒
        days = int(request.query_params.get('days', 15))
        qs = services.get_expiring_equipment(days)
        serializer = EquipmentListSerializer(qs, many=True)
        return Response({
            'code': 200,
            'data': serializer.data,
        })

    @action(detail=True, methods=['get'])
    def traceability(self, request: Request, pk: str = None) -> Response:
        data = services.get_equipment_traceability(int(pk))
        return Response({
            'code': 200,
            'data': data,
        })


class CalibrationViewSet(BaseModelViewSet):
    serializer_class = CalibrationSerializer
    lims_module = 'equipment'

    def get_queryset(self):
        return Calibration.objects.filter(
            equipment_id=self.kwargs['equipment_pk'],
        )

    def perform_create(self, serializer) -> None:
        equipment = Equipment.objects.get(
            pk=self.kwargs['equipment_pk'],
        )
        kwargs = {'equipment': equipment}
        if self.request.user.is_authenticated:
            kwargs['created_by'] = self.request.user
        serializer.save(**kwargs)

        if serializer.validated_data.get('valid_until'):
            equipment.next_calibration_date = serializer.validated_data['valid_until']
            equipment.save(update_fields=['next_calibration_date', 'updated_at'])


class PeriodCheckViewSet(BaseModelViewSet):
    serializer_class = PeriodCheckSerializer
    lims_module = 'equipment'

    def get_queryset(self):
        return PeriodCheck.objects.filter(
            equipment_id=self.kwargs['equipment_pk'],
        ).select_related('checker')

    def perform_create(self, serializer) -> None:
        equipment = Equipment.objects.get(
            pk=self.kwargs['equipment_pk'],
        )
        kwargs = {'equipment': equipment}
        if self.request.user.is_authenticated:
            # PeriodCheck/维护保养页面需要展示“核查人/操作人”
            # 后端统一用当前登录用户回填，避免前端字段名不一致或未传导致展示为空。
            kwargs['created_by'] = self.request.user
            kwargs['checker'] = self.request.user
        serializer.save(**kwargs)


class MaintenanceViewSet(BaseModelViewSet):
    serializer_class = MaintenanceSerializer
    lims_module = 'equipment'

    def get_queryset(self):
        return Maintenance.objects.filter(
            equipment_id=self.kwargs['equipment_pk'],
        ).select_related('handler')

    def perform_create(self, serializer) -> None:
        equipment = Equipment.objects.get(
            pk=self.kwargs['equipment_pk'],
        )
        kwargs = {'equipment': equipment}
        if self.request.user.is_authenticated:
            kwargs['created_by'] = self.request.user
            kwargs['handler'] = self.request.user
        serializer.save(**kwargs)


class EquipUsageLogViewSet(BaseModelViewSet):
    serializer_class = EquipUsageLogSerializer
    lims_module = 'equipment'
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        return EquipUsageLog.objects.filter(
            equipment_id=self.kwargs['equipment_pk'],
        ).select_related('user')
