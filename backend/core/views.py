from __future__ import annotations

from typing import Any

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .pagination import StandardPagination
from .permissions import LimsModulePermission
from .serializers import CreatedByMixin


class BaseModelViewSet(CreatedByMixin, ModelViewSet):
    pagination_class = StandardPagination
    permission_classes = [permissions.IsAuthenticated, LimsModulePermission]
    lims_module: str | None = None

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(qs.model, 'is_deleted'):
            qs = qs.filter(is_deleted=False)
        # 为分页提供稳定顺序，避免 unordered queryset 警告。
        if not getattr(qs, 'ordered', False):
            model = getattr(qs, 'model', None)
            field_names = {f.name for f in model._meta.fields} if model else set()
            if 'created_at' in field_names:
                qs = qs.order_by('-created_at', '-id')
            elif 'id' in field_names:
                qs = qs.order_by('-id')
        return qs

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        if hasattr(instance, 'soft_delete'):
            instance.soft_delete()
        else:
            self.perform_destroy(instance)
        return Response(
            {'code': 200, 'message': '删除成功'},
            status=status.HTTP_200_OK,
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'code': 201, 'message': '创建成功', 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {'code': 200, 'message': '更新成功', 'data': serializer.data},
            status=status.HTTP_200_OK,
        )
