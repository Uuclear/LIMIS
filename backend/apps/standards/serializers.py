from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer

from .models import MethodValidation, Standard


class MethodValidationSerializer(BaseModelSerializer):
    conclusion_display = serializers.CharField(
        source='get_conclusion_display', read_only=True,
    )
    validator_name = serializers.SerializerMethodField()

    class Meta:
        model = MethodValidation
        fields = [
            'id', 'standard', 'validation_date', 'validator',
            'validator_name', 'conclusion', 'conclusion_display',
            'report', 'attachment', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_validator_name(self, obj: MethodValidation) -> str:
        if obj.validator:
            return obj.validator.get_full_name() or str(obj.validator)
        return ''


class StandardListSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    replaced_by_no = serializers.CharField(
        source='replaced_by.standard_no', read_only=True, default='',
    )

    class Meta:
        model = Standard
        fields = [
            'id', 'standard_no', 'name', 'category',
            'publish_date', 'implement_date', 'abolish_date',
            'status', 'status_display', 'replaced_by',
            'replaced_by_no', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StandardWriteSerializer(BaseModelSerializer):
    """创建/更新：可写字段与模型一致，避免 list 序列化器缺少字段导致写入失败。"""

    class Meta:
        model = Standard
        fields = [
            'id', 'standard_no', 'name', 'category',
            'publish_date', 'implement_date', 'abolish_date',
            'status', 'replaced_by', 'attachment', 'remark',
        ]
        read_only_fields = ['id']


class StandardDetailSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    replaced_by_no = serializers.CharField(
        source='replaced_by.standard_no', read_only=True, default='',
    )
    validations = MethodValidationSerializer(many=True, read_only=True)

    class Meta:
        model = Standard
        fields = [
            'id', 'standard_no', 'name', 'category',
            'publish_date', 'implement_date', 'abolish_date',
            'status', 'status_display', 'replaced_by',
            'replaced_by_no', 'attachment', 'remark',
            'validations', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
