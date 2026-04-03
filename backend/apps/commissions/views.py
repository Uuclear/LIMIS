from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from . import services
from .filters import CommissionFilter
from .models import Commission, CommissionItem, ContractReview
from .serializers import (
    CommissionCreateSerializer,
    CommissionDetailSerializer,
    CommissionItemSerializer,
    CommissionListSerializer,
    CommissionUpdateSerializer,
    ContractReviewSerializer,
)


class CommissionViewSet(BaseModelViewSet):
    queryset = Commission.objects.select_related(
        'project', 'sub_project', 'witness', 'sampler', 'reviewer', 'created_by',
    ).prefetch_related('items', 'samples')
    lims_module = 'commission'
    lims_action_map = {
        'submit': 'edit',
        'review': 'approve',
        'terminate': 'edit',
    }
    filterset_class = CommissionFilter
    search_fields = ['commission_no', 'construction_part']
    ordering_fields = ['commission_date', 'created_at', 'commission_no']

    def get_serializer_class(self) -> type:
        if self.action == 'list':
            return CommissionListSerializer
        if self.action == 'create':
            return CommissionCreateSerializer
        if self.action in ('update', 'partial_update'):
            return CommissionUpdateSerializer
        return CommissionDetailSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer) -> None:
        commission_no = services.generate_commission_no(
            serializer.validated_data.get('project'),
        )
        if self.request.user.is_authenticated:
            serializer.save(
                commission_no=commission_no,
                created_by=self.request.user,
            )
        else:
            serializer.save(commission_no=commission_no)

    @action(detail=True, methods=['post'])
    def submit(self, request: Request, pk: str = None) -> Response:
        commission = services.submit_commission(int(pk), request.user)
        return Response({
            'code': 200,
            'message': '提交成功',
            'data': CommissionDetailSerializer(commission).data,
        })

    @action(detail=True, methods=['post'])
    def review(self, request: Request, pk: str = None) -> Response:
        approved = request.data.get('approved', True)
        comment = request.data.get('comment', '')
        commission = services.review_commission(
            int(pk), request.user, approved, comment,
        )
        return Response({
            'code': 200,
            'message': '评审完成',
            'data': CommissionDetailSerializer(commission).data,
        })

    @action(detail=True, methods=['post'], url_path='terminate')
    def terminate(self, request: Request, pk: str = None) -> Response:
        reason = (request.data.get('reason') or '').strip()
        commission = services.terminate_commission(int(pk), request.user, reason)
        return Response({
            'code': 200,
            'message': '委托已终止',
            'data': CommissionDetailSerializer(commission).data,
        })

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        services.cascade_soft_delete_commission(instance.pk)
        return Response(
            {'code': 200, 'message': '删除成功'},
            status=status.HTTP_200_OK,
        )


class CommissionItemViewSet(BaseModelViewSet):
    serializer_class = CommissionItemSerializer
    lims_module = 'commission'

    def get_queryset(self):
        return CommissionItem.objects.filter(
            commission_id=self.kwargs['commission_pk'],
        )

    def perform_create(self, serializer) -> None:
        commission = Commission.objects.get(
            pk=self.kwargs['commission_pk'],
        )
        if self.request.user.is_authenticated:
            serializer.save(
                commission=commission, created_by=self.request.user,
            )
        else:
            serializer.save(commission=commission)


class ContractReviewViewSet(BaseModelViewSet):
    serializer_class = ContractReviewSerializer
    lims_module = 'commission'
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        return ContractReview.objects.filter(
            commission_id=self.kwargs['commission_pk'],
        ).select_related('reviewer')

    def perform_create(self, serializer) -> None:
        commission = Commission.objects.get(
            pk=self.kwargs['commission_pk'],
        )
        serializer.save(
            commission=commission,
            reviewer=self.request.user,
        )
