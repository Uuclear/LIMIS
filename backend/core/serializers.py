from __future__ import annotations

from typing import Any

from rest_framework import serializers


def safe_related_attr(obj: Any, *path: str) -> Any:
    """
    安全读取一层或多层外键/属性，避免软删除导致默认管理器取不到关联对象时抛
    RelatedObjectDoesNotExist 进而在序列化阶段变成 500。
    """
    cur: Any = obj
    try:
        for name in path:
            cur = getattr(cur, name)
            if cur is None:
                return None
        return cur
    except Exception:
        return None


class CreatedByMixin:
    """Mixin for views: auto-sets created_by from request.user on create."""

    def perform_create(self, serializer: serializers.Serializer) -> None:
        request = getattr(self, 'request', None)
        if request and request.user and request.user.is_authenticated:
            serializer.save(created_by=request.user)
        else:
            serializer.save()


class BaseModelSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        abstract = True
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')

    def get_created_by_name(self, obj: Any) -> str:
        if obj.created_by:
            return getattr(obj.created_by, 'get_full_name', lambda: str(obj.created_by))()
        return ''
