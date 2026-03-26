from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.utils.export import export_to_excel
from core.views import BaseModelViewSet

from . import services
from .filters import SampleFilter
from .models import Sample, SampleGroup
from .serializers import (
    SampleBatchCreateSerializer,
    SampleCreateSerializer,
    SampleDetailSerializer,
    SampleDisposalSerializer,
    SampleGroupSerializer,
    SampleListSerializer,
    SampleStatusChangeSerializer,
)


class SampleViewSet(BaseModelViewSet):
    queryset = Sample.objects.select_related(
        'commission', 'commission__project', 'group',
    ).all()
    permission_classes = [permissions.IsAuthenticated]
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


class SampleGroupViewSet(BaseModelViewSet):
    queryset = SampleGroup.objects.all()
    serializer_class = SampleGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['group_no', 'name']
    ordering_fields = ['created_at', 'group_no']
