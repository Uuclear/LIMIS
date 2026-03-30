from __future__ import annotations

import re

from django.core.files.storage import default_storage
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
            'status', 'status_display',
            'replaced_by',
            'replaced_by_no',
            'replaced_case',
            'attachment',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StandardWriteSerializer(BaseModelSerializer):
    """创建/更新：可写字段与模型一致，避免 list 序列化器缺少字段导致写入失败。"""

    class Meta:
        model = Standard
        fields = [
            'id', 'standard_no', 'name', 'category',
            'publish_date', 'implement_date', 'abolish_date',
            'status', 'replaced_by', 'replaced_case',
            'attachment', 'remark',
        ]
        read_only_fields = ['id']

    def _maybe_resolve_replaced_by(self, validated_data: dict) -> None:
        """
        前端现在输入的是“替代情况(replaced_case)”而不是替代标准ID。
        若 replaced_by 未提供/为空，则尝试从 replaced_case 中解析标准号并反查 replaced_by。
        """
        if validated_data.get('replaced_by'):
            return

        replaced_case = (validated_data.get('replaced_case') or '').strip()
        if not replaced_case:
            return

        # replaced_case 期望形如：GB/T 50081-2002（来自抓取）
        standard_no = replaced_case
        standard_no = standard_no.replace('替代', '').strip()
        standard_no = standard_no.strip('[]（）()（） ')

        # 简单清洗：去掉多余空格，但保留 GB/T 中的空格与格式
        standard_no = re.sub(r'\\s+', ' ', standard_no).strip()

        try:
            replaced = Standard.objects.filter(standard_no=standard_no).first()
            validated_data['replaced_by'] = replaced
        except Exception:
            validated_data['replaced_by'] = None

    def _sanitize_standard_no_filename(self, standard_no: str) -> str:
        """保留完整标准编号语义：将非法文件名字符替换为空格，/ 替换为空格（与业务展示一致）。"""
        s = str(standard_no).strip()
        if not s:
            return ''
        # Windows 非法字符
        s = re.sub(r'[\\/:*?"<>|]+', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def _maybe_rename_attachment(
        self, validated_data: dict, instance: Standard | None = None,
    ) -> None:
        """
        将上传文件重命名为：标准编号（清洗后）+ 原扩展名。
        若目标路径已存在则先删除，避免出现 Django 自动追加的随机后缀。
        """
        attachment = validated_data.get('attachment')
        if not attachment:
            return

        standard_no = validated_data.get('standard_no') or ''
        if instance is not None and 'standard_no' not in validated_data:
            standard_no = instance.standard_no
        base = self._sanitize_standard_no_filename(str(standard_no))
        if not base:
            return

        original_name = getattr(attachment, 'name', '') or ''
        ext = ''
        if '.' in original_name:
            ext = original_name.rsplit('.', 1)[-1]
            if ext:
                ext = f'.{ext}'

        rel_path = f'standards/{base}{ext}'
        if default_storage.exists(rel_path):
            default_storage.delete(rel_path)
        if instance is not None and instance.attachment:
            try:
                old = instance.attachment.name
                if old and old != rel_path and default_storage.exists(old):
                    default_storage.delete(old)
            except Exception:
                pass

        attachment.name = f'{base}{ext}'

    def create(self, validated_data: dict) -> Standard:
        self._maybe_resolve_replaced_by(validated_data)
        self._maybe_rename_attachment(validated_data, instance=None)
        return super().create(validated_data)

    def update(self, instance: Standard, validated_data: dict) -> Standard:
        self._maybe_resolve_replaced_by(validated_data)
        # update 时 standard_no 可能改过；以 validated_data 优先，其次用 instance
        if 'standard_no' not in validated_data:
            validated_data['standard_no'] = instance.standard_no
        self._maybe_rename_attachment(validated_data, instance=instance)
        return super().update(instance, validated_data)


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
            'replaced_case',
            'validations', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
