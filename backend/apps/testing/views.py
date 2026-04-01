from __future__ import annotations

import os
import json
import logging
import traceback
import time
from typing import Any

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from core.audit import log_sensitive_audit
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
from apps.system.models import AuditLog

logger = logging.getLogger(__name__)


def _test_result_audit_snapshot(obj: TestResult) -> dict[str, Any]:
    task = getattr(obj, 'task', None)
    param = getattr(obj, 'parameter', None)
    return {
        'id': obj.pk,
        'task_id': obj.task_id,
        'task_no': getattr(task, 'task_no', None) if task else None,
        'parameter_id': obj.parameter_id,
        'parameter_name': getattr(param, 'name', None) if param else None,
        'raw_value': str(obj.raw_value) if obj.raw_value is not None else None,
        'rounded_value': str(obj.rounded_value) if obj.rounded_value is not None else None,
        'display_value': obj.display_value,
        'unit': obj.unit,
        'judgment': obj.judgment,
        'standard_value': obj.standard_value,
        'design_value': obj.design_value,
        'remark': (obj.remark or '')[:500],
        'is_deleted': getattr(obj, 'is_deleted', False),
    }


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
        scope = (self.request.query_params.get('scope') or '').strip().lower()
        if scope == 'all':
            return qs
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
        scope = (self.request.query_params.get('scope') or '').strip().lower()
        if scope == 'all':
            return qs
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
    lims_module = 'task'
    lims_action_map = {
        'assign': 'edit',
        'return_task': 'edit',
        'return_commission': 'edit',
        'complete': 'edit',
        'timeline': 'view',
        'merged_record_schema': 'view',
    }
    filterset_class = TestTaskFilter
    search_fields = ['task_no']
    ordering_fields = ['id', 'planned_date', 'created_at', 'task_no']

    def get_serializer_class(self) -> type:
        if self.action == 'retrieve':
            return TestTaskDetailSerializer
        return TestTaskListSerializer

    def dispatch(self, request: Request, *args, **kwargs):
        # region agent log
        try:
            os.makedirs('/opt/limis/.cursor', exist_ok=True)
            with open('/opt/limis/.cursor/debug-66f994.log', 'a', encoding='utf-8') as _f:
                _f.write(json.dumps({
                    'sessionId': '66f994',
                    'runId': 'initial',
                    'hypothesisId': 'H3',
                    'location': 'testing/views.py:TestTaskViewSet.dispatch',
                    'message': 'task_dispatch_entry',
                    'data': {'method': request.method, 'path': request.path},
                    'timestamp': int(time.time() * 1000),
                }, ensure_ascii=False) + os.linesep)
        except Exception:
            pass
        # endregion
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as exc:
            logger.exception('TestTaskViewSet.dispatch')
            # region agent log
            try:
                with open('/opt/limis/.cursor/debug-66f994.log', 'a', encoding='utf-8') as _f:
                    _f.write(json.dumps({
                        'sessionId': '66f994',
                        'runId': 'initial',
                        'hypothesisId': 'H3',
                        'location': 'testing/views.py:TestTaskViewSet.dispatch:exc',
                        'message': 'task_dispatch_error',
                        'data': {'error': str(exc), 'traceback': traceback.format_exc()},
                        'timestamp': int(time.time() * 1000),
                    }, ensure_ascii=False) + os.linesep)
            except Exception:
                pass
            # endregion
            raise



    @action(detail=True, methods=['get'], url_path='word-preview')
    def word_preview(self, request: Request, pk: str = None) -> Response:
        template = self.get_object()
        task_id = request.query_params.get('task_id')
        if not task_id:
            raise NotFound('缺少 task_id')
        try:
            task_id_int = int(task_id)
        except Exception:
            raise NotFound('task_id 非法')
        task = TestTask.objects.select_related('commission__project', 'sample').filter(pk=task_id_int, is_deleted=False).first()
        if task is None:
            raise NotFound('检测任务不存在')
        sample = task.sample
        commission = task.commission
        project = commission.project if commission else None
        placeholders = {
            '%工程名称%': getattr(project, 'name', '') if project else '',
            '%委托编号%': getattr(commission, 'commission_no', '') if commission else '',
            '%样品编号%': getattr(sample, 'sample_no', '') if sample else '',
            '%样品名称%': getattr(sample, 'name', '') if sample else '',
            '%规格型号%': getattr(sample, 'specification', '') if sample else '',
        }
        word_url = ''
        if template.word_template:
            word_url = request.build_absolute_uri(template.word_template.url)
        return Response({'code': 200, 'data': {
            'template_id': template.id,
            'template_name': template.name,
            'task_id': task.id,
            'placeholders': placeholders,
            'word_template_url': word_url,
            'has_word_template': bool(template.word_template),
        }})

    def list(self, request: Request, *args, **kwargs) -> Response:
        # region agent log
        try:
            os.makedirs('/opt/limis/.cursor', exist_ok=True)
            with open('/opt/limis/.cursor/debug-66f994.log', 'a', encoding='utf-8') as _f:
                _f.write(json.dumps({
                    'sessionId': '66f994',
                    'runId': 'initial',
                    'hypothesisId': 'H3',
                    'location': 'testing/views.py:TestTaskViewSet.list:entry',
                    'message': 'task_list_api_entry',
                    'data': {'query_params': dict(request.query_params)},
                    'timestamp': int(time.time() * 1000),
                }, ensure_ascii=False) + os.linesep)
        except Exception:
            pass
        # endregion
        try:
            return super().list(request, *args, **kwargs)
        except Exception as exc:
            logger.exception('TestTaskViewSet.list')
            # region agent log
            try:
                with open('/opt/limis/.cursor/debug-66f994.log', 'a', encoding='utf-8') as _f:
                    _f.write(json.dumps({
                        'sessionId': '66f994',
                        'runId': 'initial',
                        'hypothesisId': 'H3',
                        'location': 'testing/views.py:TestTaskViewSet.list:error',
                        'message': 'task_list_api_error',
                        'data': {'error': str(exc), 'traceback': traceback.format_exc()},
                        'timestamp': int(time.time() * 1000),
                    }, ensure_ascii=False) + os.linesep)
            except Exception:
                pass
            # endregion
            raise

    def perform_create(self, serializer) -> None:
        task_no = services.generate_task_no()
        if self.request.user.is_authenticated:
            serializer.save(task_no=task_no, created_by=self.request.user)
        else:
            serializer.save(task_no=task_no)

    @action(detail=True, methods=['get'], url_path='merged-record-schema')
    def merged_record_schema(self, request: Request, pk: str = None) -> Response:
        # region agent log
        try:
            with open('/opt/limis/.cursor/debug-66f994.log', 'a', encoding='utf-8') as _f:
                _f.write(json.dumps({
                    'sessionId': '66f994',
                    'runId': 'initial',
                    'hypothesisId': 'H6',
                    'location': 'testing/views.py:TestTaskViewSet.merged_record_schema:entry',
                    'message': 'merged_schema_request',
                    'data': {'pk': pk},
                    'timestamp': int(time.time() * 1000),
                }, ensure_ascii=False) + os.linesep)
        except Exception:
            pass
        # endregion
        task = self.get_object()
        try:
            data = services.build_merged_record_schema_for_task(task.id)
        except TestTask.DoesNotExist:
            # region agent log
            try:
                with open('/opt/limis/.cursor/debug-66f994.log', 'a', encoding='utf-8') as _f:
                    _f.write(json.dumps({
                        'sessionId': '66f994',
                        'runId': 'initial',
                        'hypothesisId': 'H6',
                        'location': 'testing/views.py:TestTaskViewSet.merged_record_schema:not_found',
                        'message': 'merged_schema_task_not_found',
                        'data': {'pk': pk},
                        'timestamp': int(time.time() * 1000),
                    }, ensure_ascii=False) + os.linesep)
            except Exception:
                pass
            # endregion
            raise NotFound('任务不存在或已删除')
        return Response({'code': 200, 'data': data})

    @action(detail=True, methods=['post'])
    def assign(self, request: Request, pk: str = None) -> Response:
        ser = TestTaskAssignSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        task = services.assign_task(
            task_id=int(pk),
            user=request.user,
            tester_id=ser.validated_data['tester'],
            equipment_id=ser.validated_data.get('equipment'),
            planned_date=ser.validated_data.get('planned_date'),
        )
        return Response({
            'code': 200,
            'message': '分配成功',
            'data': TestTaskDetailSerializer(task).data,
        })

    @action(detail=True, methods=['post'], url_path='return')
    def return_task(self, request: Request, pk: str = None) -> Response:
        reason = request.data.get('reason', '')
        task = services.return_task(int(pk), request.user, reason)
        return Response({
            'code': 200,
            'message': '任务已退回待分配',
            'data': TestTaskDetailSerializer(task).data,
        })


    @action(detail=True, methods=['post'], url_path='return-commission')
    def return_commission(self, request: Request, pk: str = None) -> Response:
        reason = request.data.get('reason', '')
        task = services.return_to_commission(int(pk), request.user, reason)
        return Response({
            'code': 200,
            'message': '已退回到委托提交流程',
            'data': {'task_id': task.id, 'commission_id': task.commission_id},
        })

    @action(detail=True, methods=['get'])
    def timeline(self, request: Request, pk: str = None) -> Response:
        task = self.get_object()
        rows = [{
            'time': task.created_at,
            'label': '任务创建',
            'actor': task.created_by_name or '',
            'detail': f'任务号：{task.task_no}',
        }]
        if task.assigned_tester_id:
            rows.append({
                'time': task.updated_at,
                'label': '任务分配',
                'actor': getattr(task.assigned_tester, 'first_name', '') or '',
                'detail': '已分配检测人员',
            })
        biz_logs = AuditLog.objects.filter(
            method='BIZ_EVENT',
            path__icontains=f'/testing/tasks/{task.pk}/',
        ).order_by('timestamp')
        for log in biz_logs:
            try:
                body = json.loads(log.body or '{}')
            except Exception:
                body = {}
            payload = body.get('payload') or {}
            rows.append({
                'time': log.timestamp,
                'label': f"任务{body.get('action') or '事件'}",
                'actor': log.username or '',
                'detail': payload.get('reason') or payload.get('task_no') or '',
            })
        return Response({'code': 200, 'data': rows})

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
    ).prefetch_related('test_parameters')
    serializer_class = RecordTemplateSerializer
    lims_module = 'testing'
    filterset_class = RecordTemplateFilter
    search_fields = ['name', 'code']

    def get_queryset(self):
        qs = super().get_queryset()
        # 模板管理页应可见全部模板（否则新建模板会因资质映射未同步而“消失”）。
        return qs



    @action(detail=True, methods=['get'], url_path='word-preview')
    def word_preview(self, request: Request, pk: str = None) -> Response:
        template = self.get_object()
        task_id = request.query_params.get('task_id')
        if not task_id:
            raise NotFound('缺少 task_id')
        try:
            task_id_int = int(task_id)
        except Exception:
            raise NotFound('task_id 非法')
        task = TestTask.objects.select_related('commission__project', 'sample').filter(pk=task_id_int, is_deleted=False).first()
        if task is None:
            raise NotFound('检测任务不存在')
        sample = task.sample
        commission = task.commission
        project = commission.project if commission else None
        placeholders = {
            '%工程名称%': getattr(project, 'name', '') if project else '',
            '%委托编号%': getattr(commission, 'commission_no', '') if commission else '',
            '%样品编号%': getattr(sample, 'sample_no', '') if sample else '',
            '%样品名称%': getattr(sample, 'name', '') if sample else '',
            '%规格型号%': getattr(sample, 'specification', '') if sample else '',
        }
        word_url = ''
        if template.word_template:
            word_url = request.build_absolute_uri(template.word_template.url)
        return Response({'code': 200, 'data': {
            'template_id': template.id,
            'template_name': template.name,
            'task_id': task.id,
            'placeholders': placeholders,
            'word_template_url': word_url,
            'has_word_template': bool(template.word_template),
        }})

    def list(self, request: Request, *args, **kwargs) -> Response:
        # region agent log
        try:
            os.makedirs('/opt/limis/.cursor', exist_ok=True)
            with open('/opt/limis/.cursor/debug-66f994.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': '66f994',
                    'runId': 'initial',
                    'hypothesisId': 'H4',
                    'location': 'testing/views.py:RecordTemplateViewSet.list',
                    'message': 'record_template_list_api_entry',
                    'data': {'query_params': dict(request.query_params)},
                    'timestamp': int(__import__('time').time() * 1000),
                }, ensure_ascii=False) + os.linesep)
        except Exception:
            pass
        # endregion
        return super().list(request, *args, **kwargs)


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
        task = serializer.validated_data['task']
        if not serializer.validated_data.get('record_data'):
            serializer.validated_data['record_data'] = (
                services.build_initial_record_data_from_task(task.pk)
            )
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

    def perform_update(self, serializer) -> None:
        before = _test_result_audit_snapshot(serializer.instance)
        super().perform_update(serializer)
        after = _test_result_audit_snapshot(serializer.instance)
        log_sensitive_audit(
            user=self.request.user,
            module='testing',
            action='update',
            entity='test_result',
            entity_id=serializer.instance.pk,
            path=self.request.path[:500],
            before=before,
            after=after,
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        before = _test_result_audit_snapshot(instance)
        instance.soft_delete()
        log_sensitive_audit(
            user=request.user,
            module='testing',
            action='delete',
            entity='test_result',
            entity_id=instance.pk,
            path=request.path[:500],
            before=before,
            after={**before, 'is_deleted': True},
        )
        return Response(
            {'code': 200, 'message': '删除成功'},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def calculate(self, request: Request, pk: str = None) -> Response:
        result = self.get_object()
        before = _test_result_audit_snapshot(result)
        result.judgment = judgment.judge_result(result)
        result.save(update_fields=['judgment', 'updated_at'])
        after = _test_result_audit_snapshot(result)
        log_sensitive_audit(
            user=request.user,
            module='testing',
            action='recalculate_judgment',
            entity='test_result',
            entity_id=result.pk,
            path=request.path[:500],
            before=before,
            after=after,
            extra={'source': 'calculate_action'},
        )
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
