from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


def _parse_date_range(request: Request) -> tuple:
    """Extract start_date/end_date from query params with defaults."""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if request.query_params.get('start_date'):
        from datetime import date as date_type
        start_date = date_type.fromisoformat(
            request.query_params['start_date'],
        )
    if request.query_params.get('end_date'):
        from datetime import date as date_type
        end_date = date_type.fromisoformat(
            request.query_params['end_date'],
        )
    return start_date, end_date


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        summary = services.get_dashboard_summary()
        recent_tasks = services.get_recent_tasks(limit=10)
        return Response({
            'code': 200,
            'data': {**summary, 'recent_tasks': recent_tasks},
        })


class TestVolumeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        start_date, end_date = _parse_date_range(request)
        group_by = request.query_params.get('group_by', 'day')
        data = services.get_test_volume(start_date, end_date, group_by)
        return Response({'code': 200, 'data': data})


class QualificationRateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        start_date, end_date = _parse_date_range(request)
        data = services.get_qualification_rate(start_date, end_date)
        return Response({'code': 200, 'data': data})


class StrengthCurveView(APIView):
    """Concrete strength development over age days."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        from apps.testing.models import TestResult
        from django.db.models import Avg, F

        start_date, end_date = _parse_date_range(request)
        results = TestResult.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            task__age_days__isnull=False,
            rounded_value__isnull=False,
        ).values(
            age_days=F('task__age_days'),
        ).annotate(
            avg_strength=Avg('rounded_value'),
        ).order_by('age_days')

        return Response({
            'code': 200,
            'data': list(results),
        })


class CycleAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        start_date, end_date = _parse_date_range(request)
        data = services.get_cycle_analysis(start_date, end_date)
        return Response({'code': 200, 'data': data})


class WorkloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        start_date, end_date = _parse_date_range(request)
        data = services.get_workload(start_date, end_date)
        return Response({'code': 200, 'data': data})


class EquipmentUsageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        start_date, end_date = _parse_date_range(request)
        data = services.get_equipment_usage(start_date, end_date)
        return Response({'code': 200, 'data': data})
