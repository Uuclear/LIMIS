from __future__ import annotations

import json
from io import BytesIO

from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import SampleCreateOrEditPermission
from core.utils.export import export_to_excel
from core.views import BaseModelViewSet

from . import services
from .filters import SampleFilter
from .models import Sample, SampleGroup
from .serializers import (
    SampleBatchCreateSerializer,
    SampleBatchRowSerializer,
    SampleCreateSerializer,
    SampleDetailSerializer,
    SampleDisposalSerializer,
    SampleGroupSerializer,
    SampleListSerializer,
    SampleStatusChangeSerializer,
)


class PublicSampleVerifyView(APIView):
    """无需登录：扫码或打开链接查看样品/委托进度摘要（仅返回非敏感字段）。"""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request: Request, sample_no: str | None = None, pk: int | None = None) -> Response:
        qs = Sample.objects.select_related('commission', 'commission__project')
        try:
            if pk is not None:
                sample = qs.get(pk=pk)
            else:
                sample = qs.get(sample_no=sample_no)
        except Sample.DoesNotExist:
            return Response(
                {'code': 404, 'message': '样品不存在'},
                status=status.HTTP_404_NOT_FOUND,
            )
        project_name = ''
        if sample.commission_id and sample.commission.project_id:
            project_name = sample.commission.project.name
        commission_no = sample.commission.commission_no if sample.commission_id else ''
        return Response({
            'code': 200,
            'data': {
                'sample_no': sample.sample_no,
                'name': sample.name,
                'status': sample.status,
                'status_display': sample.get_status_display(),
                'commission_no': commission_no,
                'project_name': project_name,
            },
        })


class SampleViewSet(BaseModelViewSet):
    queryset = Sample.objects.select_related(
        'commission', 'commission__project', 'group',
    ).all()
    lims_module = 'sample'
    lims_action_map = {
        # 状态流转属于编辑行为，避免仅拥有 edit 权限时被错误拦截为 create
        'change_status': 'edit',
        'create_testing_tasks': 'edit',
    }
    filterset_class = SampleFilter
    search_fields = ['sample_no', 'blind_no', 'name']
    ordering_fields = ['created_at', 'sampling_date', 'received_date', 'sample_no']

    def get_serializer_class(self) -> type:
        if self.action == 'list':
            return SampleListSerializer
        if self.action == 'create':
            return SampleCreateSerializer
        if self.action in ('retrieve', 'update', 'partial_update'):
            return SampleDetailSerializer
        return SampleDetailSerializer

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        services.cascade_soft_delete_sample(instance.pk)
        return Response(
            {'code': 200, 'message': '删除成功'},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request: Request, pk: str = None) -> Response:
        sample = self.get_object()
        serializer = SampleStatusChangeSerializer(
            data=request.data, context={'sample': sample},
        )
        serializer.is_valid(raise_exception=True)

        updated = services.change_sample_status(
            sample.pk,
            serializer.validated_data['new_status'],
            request.user,
        )
        return Response({
            'code': 200,
            'message': '状态变更成功',
            'data': SampleDetailSerializer(updated).data,
        })

    @action(detail=True, methods=['post'], url_path='create-testing-tasks')
    def create_testing_tasks(self, request: Request, pk: str = None) -> Response:
        """
        样品状态为“检测中”但检测任务为空时：一键生成检测任务（unassigned），供用户继续分配/开始检测。
        """
        sample = self.get_object()
        # 这里把 task 生成放在 testing/services：复用其 TestMethod/TestParameter 映射逻辑
        from apps.testing import services as testing_services
        from apps.testing.serializers import TestTaskListSerializer

        tasks = testing_services.create_tasks_for_sample(sample.pk, user=request.user)
        return Response({
            'code': 200,
            'message': '检测任务已生成',
            'data': TestTaskListSerializer(tasks, many=True).data,
        })

    @action(detail=True, methods=['get'])
    def timeline(self, request: Request, pk: str = None) -> Response:
        sample = self.get_object()
        data = services.get_sample_timeline(sample.pk)
        return Response({'code': 200, 'data': data})

    @action(detail=True, methods=['get'])
    def label(self, request: Request, pk: str = None) -> Response:
        sample = self.get_object()
        data = services.generate_sample_label(sample.pk)
        return Response({'code': 200, 'data': data})

    @action(detail=False, methods=['post'], url_path='batch-register')
    def batch_register(self, request: Request) -> Response:
        serializer = SampleBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        samples = serializer.save()
        return Response(
            {
                'code': 201,
                'message': f'成功创建 {len(samples)} 个样品',
                'data': SampleListSerializer(samples, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], url_path='retention-list')
    def retention_list(self, request: Request) -> Response:
        qs = services.get_retention_samples()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = SampleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SampleListSerializer(qs, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(detail=True, methods=['post'])
    def dispose(self, request: Request, pk: str = None) -> Response:
        sample = self.get_object()
        serializer = SampleDisposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        disposal = services.dispose_sample(
            sample_id=sample.pk,
            disposal_type=serializer.validated_data['disposal_type'],
            disposal_date=serializer.validated_data['disposal_date'],
            handler=request.user,
            remark=serializer.validated_data.get('remark', ''),
        )
        return Response({
            'code': 200,
            'message': '处置成功',
            'data': SampleDisposalSerializer(disposal).data,
        })

    @action(detail=False, methods=['get'])
    def export(self, request: Request) -> Response:
        qs = self.filter_queryset(self.get_queryset())
        return export_to_excel(
            queryset=qs,
            fields=[
                'sample_no', 'blind_no', 'name', 'specification', 'grade',
                'quantity', 'unit', 'get_status_display',
                'sampling_date', 'received_date',
                'commission__commission_no',
            ],
            headers=[
                '样品编号', '盲样编号', '样品名称', '规格型号', '设计强度/等级',
                '数量', '单位', '状态',
                '取样日期', '收样日期', '委托单号',
            ],
            filename='样品台账.xlsx',
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='import-template',
        permission_classes=[permissions.IsAuthenticated, SampleCreateOrEditPermission],
    )
    def import_template(self, request: Request) -> HttpResponse:
        wb = services.build_import_template_workbook()
        buf = BytesIO()
        wb.save(buf)
        response = HttpResponse(
            buf.getvalue(),
            content_type=(
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ),
        )
        response['Content-Disposition'] = 'attachment; filename="sample_import_template.xlsx"'
        return response

    @action(
        detail=False,
        methods=['post'],
        url_path='batch-import',
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[permissions.IsAuthenticated, SampleCreateOrEditPermission],
    )
    def batch_import(self, request: Request) -> Response:
        raw_cid = request.POST.get('commission_id')
        if raw_cid is None or str(raw_cid).strip() == '':
            return Response(
                {
                    'code': 400,
                    'message': '请选择委托单',
                    'data': {
                        'success_count': 0,
                        'errors': [{'row': 0, 'message': '缺少 commission_id'}],
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            cid = int(raw_cid)
        except (TypeError, ValueError):
            return Response(
                {
                    'code': 400,
                    'message': '委托单 ID 无效',
                    'data': {
                        'success_count': 0,
                        'errors': [{'row': 0, 'message': 'commission_id 必须为整数'}],
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.commissions.models import Commission
        if not Commission.objects.filter(pk=cid).exists():
            return Response(
                {
                    'code': 400,
                    'message': '委托单不存在',
                    'data': {
                        'success_count': 0,
                        'errors': [{'row': 0, 'message': '委托单不存在'}],
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload = request.FILES.get('file')
        if not upload:
            return Response(
                {
                    'code': 400,
                    'message': '请上传 Excel 文件',
                    'data': {
                        'success_count': 0,
                        'errors': [{'row': 0, 'message': '缺少 file'}],
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_rows, parse_errors = services.parse_samples_import_excel(upload)
        if parse_errors:
            return Response(
                {
                    'code': 400,
                    'message': '文件解析失败',
                    'data': {'success_count': 0, 'errors': parse_errors},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        row_errors: list[dict[str, str | int]] = []
        validated_rows: list[dict] = []
        for excel_row_idx, row in raw_rows:
            ser = SampleBatchRowSerializer(data=row)
            if not ser.is_valid():
                row_errors.append({
                    'row': excel_row_idx,
                    'message': json.dumps(ser.errors, ensure_ascii=False),
                })
            else:
                validated_rows.append(ser.validated_data)

        if row_errors:
            return Response(
                {
                    'code': 400,
                    'message': '数据校验未通过',
                    'data': {'success_count': 0, 'errors': row_errors},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        samples = services.create_samples_from_rows(cid, validated_rows)
        return Response(
            {
                'code': 201,
                'message': f'成功导入 {len(samples)} 条样品',
                'data': {
                    'success_count': len(samples),
                    'errors': [],
                    'samples': SampleListSerializer(samples, many=True).data,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class SampleGroupViewSet(BaseModelViewSet):
    queryset = SampleGroup.objects.all()
    serializer_class = SampleGroupSerializer
    lims_module = 'sample'
    search_fields = ['group_no', 'name']
    ordering_fields = ['created_at', 'group_no']
