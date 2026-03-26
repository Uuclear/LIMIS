from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from .models import EnvAlarm, EnvRecord, MonitoringPoint
from .serializers import (
    EnvAlarmSerializer,
    EnvRecordSerializer,
    MonitoringPointSerializer,
)
from . import services


class MonitoringPointViewSet(BaseModelViewSet):
    queryset = MonitoringPoint.objects.all()
    serializer_class = MonitoringPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'location']

    @action(detail=True, methods=['get'], url_path='latest-records')
    def latest_records(self, request: Request, pk=None) -> Response:
        limit = int(request.query_params.get('limit', 50))
        data = services.get_point_latest_records(int(pk), limit=limit)
        return Response({'code': 200, 'data': data})


class EnvRecordViewSet(BaseModelViewSet):
    queryset = EnvRecord.objects.select_related('point').all()
    serializer_class = EnvRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['point', 'is_alarm']

    def get_queryset(self):
        qs = EnvRecord.objects.select_related('point').all()
        return qs

    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest(self, request: Request) -> Response:
        """Bulk or single record ingestion endpoint."""
        try:
            point_id = int(request.data['point'])
            temperature = Decimal(str(request.data['temperature']))
            humidity = Decimal(str(request.data['humidity']))
        except (KeyError, ValueError, InvalidOperation):
            return Response(
                {'detail': '参数错误: 需要 point, temperature, humidity'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        record = services.ingest_record(point_id, temperature, humidity)
        return Response(
            {'code': 201, 'data': EnvRecordSerializer(record).data},
            status=status.HTTP_201_CREATED,
        )


class EnvAlarmViewSet(BaseModelViewSet):
    queryset = EnvAlarm.objects.select_related('point', 'resolved_by').all()
    serializer_class = EnvAlarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['point', 'alarm_type', 'is_resolved']

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request: Request, pk=None) -> Response:
        alarm = self.get_object()
        alarm.is_resolved = True
        alarm.resolved_by = request.user
        alarm.resolved_at = timezone.now()
        alarm.save(update_fields=[
            'is_resolved', 'resolved_by', 'resolved_at', 'updated_at',
        ])
        serializer = self.get_serializer(alarm)
        return Response({'code': 200, 'data': serializer.data})
