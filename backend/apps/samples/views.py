from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

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
from .services.blind_sample import BlindSampleService


class SampleViewSet(BaseModelViewSet):
    queryset = Sample.objects.select_related(
        'commission', 'commission__project', 'group',
    ).all()
    lims_module = 'sample'
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
    
    # ==================== 盲样管理API ====================
    
    @action(detail=True, methods=['post'], url_path='assign-blind')
    def assign_blind_no(self, request: Request, pk: str = None) -> Response:
        """为单个样品分配盲样编号"""
        sample = self.get_object()
        
        if sample.blind_no:
            return Response({
                'code': 400,
                'message': f'该样品已有盲样编号: {sample.blind_no}',
                'data': {'blind_no': sample.blind_no},
            })
        
        blind_no = BlindSampleService.assign_blind_no(sample)
        return Response({
            'code': 200,
            'message': '盲样编号分配成功',
            'data': {
                'sample_no': sample.sample_no,
                'blind_no': blind_no,
            },
        })
    
    @action(detail=False, methods=['post'], url_path='batch-assign-blind')
    def batch_assign_blind_no(self, request: Request) -> Response:
        """批量分配盲样编号"""
        sample_ids = request.data.get('sample_ids', [])
        commission_id = request.data.get('commission_id')
        
        if not sample_ids and not commission_id:
            return Response({
                'code': 400,
                'message': '请提供样品ID列表或委托单ID',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取样品
        if sample_ids:
            samples = list(Sample.objects.filter(id__in=sample_ids))
        else:
            samples = list(Sample.objects.filter(commission_id=commission_id))
        
        if not samples:
            return Response({
                'code': 400,
                'message': '未找到符合条件的样品',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 批量分配盲样编号
        mapping = BlindSampleService.batch_assign_blind_no(samples)
        
        return Response({
            'code': 200,
            'message': f'成功为 {len(mapping)} 个样品分配盲样编号',
            'data': mapping,
        })
    
    @action(detail=False, methods=['get'], url_path='blind-mapping')
    def blind_mapping(self, request: Request) -> Response:
        """获取盲样映射表（需要特定权限）"""
        # 检查权限
        if not BlindSampleService.can_view_mapping(request.user):
            raise PermissionDenied('您没有权限查看盲样映射表')
        
        commission_id = request.query_params.get('commission_id')
        project_id = request.query_params.get('project_id')
        
        mapping = BlindSampleService.get_blind_mapping(
            commission_id=commission_id,
            project_id=project_id,
        )
        
        return Response({
            'code': 200,
            'data': mapping,
        })
    
    @action(detail=True, methods=['post'], url_path='remove-blind')
    def remove_blind_no(self, request: Request, pk: str = None) -> Response:
        """移除盲样编号（需要特定权限）"""
        # 检查权限
        if not BlindSampleService.can_view_mapping(request.user):
            raise PermissionDenied('您没有权限移除盲样编号')
        
        sample = self.get_object()
        
        if not sample.blind_no:
            return Response({
                'code': 400,
                'message': '该样品没有盲样编号',
            })
        
        old_blind_no = sample.blind_no
        BlindSampleService.remove_blind_no(sample)
        
        return Response({
            'code': 200,
            'message': f'已移除盲样编号: {old_blind_no}',
        })
    
    @action(detail=False, methods=['get'], url_path='search-by-blind')
    def search_by_blind_no(self, request: Request) -> Response:
        """通过盲样编号查询样品（检测人员使用）"""
        blind_no = request.query_params.get('blind_no')
        
        if not blind_no:
            return Response({
                'code': 400,
                'message': '请提供盲样编号',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sample = BlindSampleService.get_sample_by_blind_no(blind_no)
        
        if not sample:
            return Response({
                'code': 404,
                'message': '未找到对应的样品',
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 返回有限的信息（不包含委托方信息）
        return Response({
            'code': 200,
            'data': {
                'blind_no': sample.blind_no,
                'name': sample.name,
                'specification': sample.specification,
                'grade': sample.grade,
                'status': sample.status,
                'status_display': sample.get_status_display(),
            },
        })


class SampleGroupViewSet(BaseModelViewSet):
    queryset = SampleGroup.objects.all()
    serializer_class = SampleGroupSerializer
    lims_module = 'sample'
    search_fields = ['group_no', 'name']
    ordering_fields = ['created_at', 'group_no']
