from __future__ import annotations

from typing import Any

from rest_framework import serializers


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
