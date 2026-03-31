from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from . import judgment, services
from .filters import (
    OriginalRecordFilter,
    RecordTemplateFilter,
    TestMethodFilter,
    TestResultFilter,
    TestTaskFilter,
)
from .models import (
    JudgmentRule,
    OriginalRecord,
    RecordTemplate,
    TestCategory,
    TestMethod,
    TestParameter,
    TestResult,
    TestTask,
)
from .serializers import (
    JudgmentRuleSerializer,
    OriginalRecordCreateSerializer,
    OriginalRecordSerializer,
    RecordTemplateSerializer,
    TestCategorySerializer,
    TestMethodDetailSerializer,
    TestMethodSerializer,
    TestParameterSerializer,
    TestResultCreateSerializer,
    TestResultSerializer,
    TestTaskAssignSerializer,
    TestTaskDetailSerializer,
    TestTaskListSerializer,
)

from apps.quality.services import get_active_qualification_profile


class TestCategoryViewSet(BaseModelViewSet):
    queryset = TestCategory.objects.filter(parent__isnull=True)
    serializer_class = TestCategorySerializer
    lims_module = 'testing'
    search_fields = ['name', 'code']


class TestMethodViewSet(BaseModelViewSet):
    queryset = TestMethod.objects.select_related('category')
    lims_module = 'testing'
    filterset_class = TestMethodFilter
    search_fields = ['name', 'standard_no', 'standard_name']

    def get_serializer_class(self) -> type:
        if self.action == 'retrieve':
            return TestMethodDetailSerializer
        return TestMethodSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve'):
            profile = get_active_qualification_profile()
            if profile:
                allowed_ids = profile.allowed_test_methods.values_list('id', flat=True)
                qs = qs.filter(id__in=allowed_ids)
        return qs


class TestParameterViewSet(BaseModelViewSet):
    queryset = TestParameter.objects.select_related('method')
    serializer_class = TestParameterSerializer
    lims_module = 'testing'
    filterset_fields = ['method']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve'):
            profile = get_active_qualification_profile()
            if profile:
                allowed_method_ids = profile.allowed_test_methods.values_list('id', flat=True)
                qs = qs.filter(method_id__in=allowed_method_ids)
        return qs


class TestTaskViewSet(BaseModelViewSet):
    queryset = TestTask.objects.select_related(
        'sample', 'commission', 'test_method',
        'test_parameter', 'assigned_tester',
    )
    lims_module = 'testing'
    lims_action_map = {
        'assign': 'edit',
        'start': 'edit',
        'complete': 'edit',
        'merged_record_schema': 'view',
    }
    filterset_class = TestTaskFilter
    search_fields = ['task_no']
    ordering_fields = ['planned_date', 'created_at', 'task_no']

    def get_serializer_class(self) -> type:
        if self.action == 'retrieve':
            return TestTaskDetailSerializer
        return TestTaskListSerializer

    def perform_create(self, serializer) -> None:
        task_no = services.generate_task_no()
        if self.request.user.is_authenticated:
            serializer.save(task_no=task_no, created_by=self.request.user)
        else:
            serializer.save(task_no=task_no)

    @action(detail=True, methods=['get'], url_path='merged-record-schema')
    def merged_record_schema(self, request: Request, pk: str = None) -> Response:
        data = services.build_merged_record_schema_for_task(int(pk))
        return Response({'code': 200, 'data': data})

    @action(detail=True, methods=['post'])
    def assign(self, request: Request, pk: str = None) -> Response:
        ser = TestTaskAssignSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        task = services.assign_task(
            task_id=int(pk),
            tester_id=ser.validated_data['tester'],
            equipment_id=ser.validated_data.get('equipment'),
            planned_date=ser.validated_data.get('planned_date'),
        )
        return Response({
            'code': 200,
            'message': '分配成功',
            'data': TestTaskDetailSerializer(task).data,
        })

    @action(detail=True, methods=['post'])
    def start(self, request: Request, pk: str = None) -> Response:
        task = services.start_task(int(pk))
        return Response({
            'code': 200,
            'message': '已开始检测',
            'data': TestTaskDetailSerializer(task).data,
        })

    @action(detail=True, methods=['post'])
    def complete(self, request: Request, pk: str = None) -> Response:
        task = services.complete_task(int(pk))
        return Response({
            'code': 200,
            'message': '检测完成',
            'data': TestTaskDetailSerializer(task).data,
        })

    @action(detail=False, methods=['get'])
    def today_list(self, request: Request) -> Response:
        user = request.user if request.query_params.get('mine') else None
        tasks = services.get_today_tasks(user=user)
        page = self.paginate_queryset(tasks)
        if page is not None:
            ser = TestTaskListSerializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = TestTaskListSerializer(tasks, many=True)
        return Response({'code': 200, 'data': ser.data})

    @action(detail=False, methods=['get'])
    def overdue_list(self, request: Request) -> Response:
        tasks = services.get_overdue_tasks()
        page = self.paginate_queryset(tasks)
        if page is not None:
            ser = TestTaskListSerializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = TestTaskListSerializer(tasks, many=True)
        return Response({'code': 200, 'data': ser.data})

    @action(detail=False, methods=['get'])
    def age_calendar(self, request: Request) -> Response:
        from datetime import date
        year = int(request.query_params.get('year', date.today().year))
        month = int(request.query_params.get('month', date.today().month))
        data = services.get_age_calendar_data(year, month)
        return Response({'code': 200, 'data': data})


class RecordTemplateViewSet(BaseModelViewSet):
    queryset = RecordTemplate.objects.select_related(
        'test_method', 'test_parameter',
    )
    serializer_class = RecordTemplateSerializer
    lims_module = 'testing'
    filterset_class = RecordTemplateFilter
    search_fields = ['name', 'code']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve'):
            profile = get_active_qualification_profile()
            if profile:
                allowed_ids = profile.allowed_record_templates.values_list('id', flat=True)
                qs = qs.filter(id__in=allowed_ids)
        return qs


class OriginalRecordViewSet(BaseModelViewSet):
    queryset = OriginalRecord.objects.select_related(
        'task', 'template', 'recorder', 'reviewer',
    ).prefetch_related('revisions')
    lims_module = 'testing'
    lims_action_map = {
        'submit': 'edit',
        'review': 'approve',
    }
    filterset_class = OriginalRecordFilter
    search_fields = ['task__task_no']

    def get_serializer_class(self) -> type:
        if self.action == 'create':
            return OriginalRecordCreateSerializer
        return OriginalRecordSerializer

    def perform_create(self, serializer) -> None:
        if self.request.user.is_authenticated:
            serializer.save(
                recorder=self.request.user,
                created_by=self.request.user,
            )
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def submit(self, request: Request, pk: str = None) -> Response:
        record = services.submit_record(int(pk))
        return Response({
            'code': 200,
            'message': '提交成功',
            'data': OriginalRecordSerializer(record).data,
        })

    @action(detail=True, methods=['post'])
    def review(self, request: Request, pk: str = None) -> Response:
        approved = request.data.get('approved', True)
        comment = request.data.get('comment', '')
        record = services.review_record(
            int(pk), request.user, approved, comment,
        )
        return Response({
            'code': 200,
            'message': '复核完成',
            'data': OriginalRecordSerializer(record).data,
        })


class TestResultViewSet(BaseModelViewSet):
    queryset = TestResult.objects.select_related('task', 'parameter')
    lims_module = 'testing'
    lims_action_map = {'calculate': 'edit'}
    filterset_class = TestResultFilter

    def get_serializer_class(self) -> type:
        if self.action == 'create':
            return TestResultCreateSerializer
        return TestResultSerializer

    @action(detail=True, methods=['post'])
    def calculate(self, request: Request, pk: str = None) -> Response:
        result = self.get_object()
        result.judgment = judgment.judge_result(result)
        result.save(update_fields=['judgment', 'updated_at'])
        return Response({
            'code': 200,
            'message': '判定完成',
            'data': TestResultSerializer(result).data,
        })


class JudgmentRuleViewSet(BaseModelViewSet):
    queryset = JudgmentRule.objects.select_related('test_parameter')
    serializer_class = JudgmentRuleSerializer
    lims_module = 'testing'
    filterset_fields = ['test_parameter']
    search_fields = ['grade']
