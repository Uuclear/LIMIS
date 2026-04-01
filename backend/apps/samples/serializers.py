from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer, safe_related_attr

from . import services
from .models import Sample, SampleDisposal, SampleGroup


# ───────────────────── SampleGroup ─────────────────────


class SampleGroupSerializer(BaseModelSerializer):
    class Meta:
        model = SampleGroup
        fields = [
            'id', 'group_no', 'name', 'sample_count',
            'description', 'created_at', 'updated_at',
            'created_by', 'created_by_name',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')


# ───────────────────── SampleDisposal ─────────────────────


class SampleDisposalSerializer(BaseModelSerializer):
    handler_name = serializers.SerializerMethodField()
    disposal_type_display = serializers.CharField(
        source='get_disposal_type_display', read_only=True,
    )

    class Meta:
        model = SampleDisposal
        fields = [
            'id', 'sample', 'disposal_type', 'disposal_type_display',
            'disposal_date', 'handler', 'handler_name', 'remark',
            'created_at',
        ]
        read_only_fields = ('id', 'created_at', 'handler')

    def get_handler_name(self, obj: SampleDisposal) -> str:
        if obj.handler:
            return obj.handler.get_full_name() or obj.handler.username
        return ''


# ───────────────────── Sample List ─────────────────────


class SampleListSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    project_name = serializers.SerializerMethodField()
    commission_no = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        fields = [
            'id', 'sample_no', 'blind_no', 'name',
            'specification', 'grade', 'status', 'status_display',
            'quantity', 'unit', 'sampling_date', 'received_date',
            'commission', 'commission_no', 'project_name',
            'created_at',
        ]
        read_only_fields = ('id', 'created_at')

    def get_project_name(self, obj: Sample) -> str:
        project = safe_related_attr(obj, 'commission', 'project')
        return getattr(project, 'name', '') if project else ''

    def get_commission_no(self, obj: Sample) -> str:
        c = safe_related_attr(obj, 'commission')
        return getattr(c, 'commission_no', '') if c else ''


# ───────────────────── Sample Detail ─────────────────────


class SampleDetailSerializer(BaseModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    project_name = serializers.SerializerMethodField()
    commission_no = serializers.SerializerMethodField()
    group_info = SampleGroupSerializer(source='group', read_only=True)
    disposals = SampleDisposalSerializer(many=True, read_only=True)
    is_overdue_retention = serializers.BooleanField(read_only=True)
    timeline = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        fields = [
            'id', 'sample_no', 'blind_no', 'commission', 'commission_no',
            'group', 'group_info', 'name', 'specification', 'grade',
            'quantity', 'unit', 'sampling_date', 'received_date',
            'production_date', 'sampling_location', 'status', 'status_display',
            'retention_deadline', 'disposal_date', 'disposal_method',
            'remark', 'project_name', 'is_overdue_retention',
            'disposals', 'timeline',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'created_by',
        )

    def get_project_name(self, obj: Sample) -> str:
        project = safe_related_attr(obj, 'commission', 'project')
        return getattr(project, 'name', '') if project else ''

    def get_commission_no(self, obj: Sample) -> str:
        c = safe_related_attr(obj, 'commission')
        return getattr(c, 'commission_no', '') if c else ''

    def get_timeline(self, obj: Sample) -> list:
        return services.get_sample_timeline(obj.pk)


# ───────────────────── Sample Create ─────────────────────


class SampleCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Sample
        fields = [
            'id', 'sample_no', 'blind_no', 'commission', 'group',
            'name', 'specification', 'grade', 'quantity', 'unit',
            'sampling_date', 'received_date', 'production_date',
            'sampling_location', 'status', 'retention_deadline', 'remark',
        ]
        read_only_fields = ('id', 'sample_no', 'blind_no')

    def create(self, validated_data: dict) -> Sample:
        commission = validated_data.get('commission')
        validated_data['sample_no'] = services.generate_sample_no(commission)
        validated_data['blind_no'] = services.generate_blind_no()
        return super().create(validated_data)


# ───────────────────── Sample Batch Create ─────────────────────


class SampleBatchRowSerializer(serializers.Serializer):
    """与样品登记表格行、Excel 导入列一致。"""

    name = serializers.CharField(max_length=200)
    specification = serializers.CharField(
        max_length=200, allow_blank=True, required=False, default='',
    )
    grade = serializers.CharField(
        max_length=100, allow_blank=True, required=False, default='',
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    unit = serializers.CharField(max_length=20, required=False, default='个')
    sampling_date = serializers.DateField()
    received_date = serializers.DateField()
    production_date = serializers.DateField(required=False, allow_null=True)
    sampling_location = serializers.CharField(
        max_length=200, allow_blank=True, required=False, default='',
    )
    remark = serializers.CharField(allow_blank=True, required=False, default='')


class SampleBatchCreateSerializer(serializers.Serializer):
    commission_id = serializers.IntegerField(help_text='委托单ID')
    samples = SampleBatchRowSerializer(
        many=True, required=False, allow_null=True,
        help_text='有值时按行创建；省略或空列表时从委托项目批量生成',
    )

    def validate_commission_id(self, value: int) -> int:
        from apps.commissions.models import Commission
        if not Commission.objects.filter(pk=value).exists():
            raise serializers.ValidationError('委托单不存在')
        return value

    def create(self, validated_data: dict) -> list[Sample]:
        cid = validated_data['commission_id']
        samples = validated_data.get('samples')
        if samples is None or len(samples) == 0:
            return services.create_samples_from_commission(cid)
        return services.create_samples_from_rows(cid, samples)


# ───────────────────── Sample Status Change ─────────────────────


class SampleStatusChangeSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(
        choices=Sample.STATUS_CHOICES, help_text='目标状态',
    )

    def validate_new_status(self, value: str) -> str:
        sample = self.context.get('sample')
        if sample:
            allowed = services.VALID_TRANSITIONS.get(sample.status, set())
            if value not in allowed:
                current = sample.get_status_display()
                target = dict(Sample.STATUS_CHOICES).get(value, value)
                raise serializers.ValidationError(
                    f'不能从「{current}」变更为「{target}」'
                )
        return value
