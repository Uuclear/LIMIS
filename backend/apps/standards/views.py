from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from .csres_crawl import crawl_standard_metadata
from .filters import StandardFilter
from .models import MethodValidation, Standard
from .serializers import (
    MethodValidationSerializer,
    StandardDetailSerializer,
    StandardListSerializer,
    StandardWriteSerializer,
)
from apps.quality.services import get_active_qualification_profile


class StandardViewSet(BaseModelViewSet):
    queryset = Standard.objects.select_related('replaced_by').all()
    lims_module = 'standards'
    # crawl 为 POST 但仅拉取工标网元数据、不落库；按「查看」鉴权，避免仅有 view/edit 的角色（如技术负责人）无法爬取
    lims_action_map = {'crawl': 'view'}
    filterset_class = StandardFilter
    search_fields = ['standard_no', 'name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StandardDetailSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return StandardWriteSerializer
        return StandardListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # 能力范围限制：只在“拉取可选项”时过滤（list/retrieve）。
        if self.action in ('list', 'retrieve'):
            profile = get_active_qualification_profile()
            if profile:
                allowed_ids = profile.allowed_standards.values_list('id', flat=True)
                qs = qs.filter(id__in=allowed_ids)
        return qs

    @action(detail=False, methods=['post'], url_path='crawl')
    def crawl(self, request: Request) -> Response:
        """
        从工标网（csres.com）按标准编号抓取信息，并返回给前端自动填充表单。
        返回的数据不直接落库；前端提交保存即可。
        """
        standard_no = (request.data.get('standard_no') or '').strip()
        if not standard_no:
            return Response({'code': 400, 'message': '缺少 standard_no'})
        try:
            data = crawl_standard_metadata(standard_no)
        except Exception as e:
            return Response({'code': 404, 'message': str(e)})
        return Response({'code': 200, 'message': '抓取成功', 'data': data})


class MethodValidationViewSet(BaseModelViewSet):
    queryset = MethodValidation.objects.select_related(
        'standard', 'validator',
    ).all()
    serializer_class = MethodValidationSerializer
    lims_module = 'standards'
    filterset_fields = ['standard', 'conclusion']
