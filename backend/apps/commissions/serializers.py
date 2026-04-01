from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer, safe_related_attr

from .models import Commission, CommissionItem, ContractReview


class CommissionItemSerializer(BaseModelSerializer):
    parameter_name = serializers.SerializerMethodField()
    standard_no = serializers.SerializerMethodField()
    standard_name = serializers.SerializerMethodField()

    class Meta:
        model = CommissionItem
        fields = [
            'id', 'commission', 'test_parameter', 'parameter_name',
            'standard_no', 'standard_name',
            'test_object', 'test_item',
            'test_standard', 'test_method', 'specification',
            'grade', 'quantity', 'unit', 'remark',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'commission': {'required': False}}

    def get_parameter_name(self, obj: CommissionItem) -> str:
        p = safe_related_attr(obj, 'test_parameter')
        return getattr(p, 'name', '') if p else ''

    def get_standard_no(self, obj: CommissionItem) -> str:
        p = safe_related_attr(obj, 'test_parameter')
        return getattr(p, 'standard_no', '') if p else ''

    def get_standard_name(self, obj: CommissionItem) -> str:
        p = safe_related_attr(obj, 'test_parameter')
        return getattr(p, 'standard_name', '') if p else ''


class ContractReviewSerializer(BaseModelSerializer):
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = ContractReview
        fields = [
            'id', 'commission', 'has_capability', 'has_equipment',
            'has_personnel', 'method_valid', 'sample_representative',
            'conclusion', 'reviewer', 'reviewer_name', 'review_date',
            'comment', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'reviewer', 'review_date', 'created_at', 'updated_at',
        ]

    def get_reviewer_name(self, obj: ContractReview) -> str:
        if obj.reviewer:
            return obj.reviewer.get_full_name() or str(obj.reviewer)
        return ''


class CommissionListSerializer(BaseModelSerializer):
    project_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    item_count = serializers.IntegerField(
        source='items.count', read_only=True,
    )
    sample_names = serializers.SerializerMethodField()

    class Meta:
        model = Commission
        fields = [
            'id', 'commission_no', 'project', 'project_name',
            'construction_part', 'sample_names', 'commission_date', 'client_unit',
            'is_witnessed', 'status', 'status_display', 'item_count',
            'created_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'commission_no', 'created_at', 'created_by',
        ]

    def get_project_name(self, obj: Commission) -> str:
        p = safe_related_attr(obj, 'project')
        return getattr(p, 'name', '') if p else ''

    def get_sample_names(self, obj: Commission) -> str:
        samples = list(obj.samples.all())
        if not samples:
            return ''
        names = [s.name for s in samples[:12]]
        if len(samples) > 12:
            return '、'.join(names) + ' 等'
        return '、'.join(names)


class CommissionDetailSerializer(BaseModelSerializer):
    items = CommissionItemSerializer(many=True, read_only=True)
    contract_review = ContractReviewSerializer(read_only=True)
    project_name = serializers.SerializerMethodField()
    sub_project_name = serializers.SerializerMethodField()
    witness_name = serializers.SerializerMethodField()
    sampler_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Commission
        fields = [
            'id', 'commission_no', 'project', 'project_name',
            'sub_project', 'sub_project_name', 'construction_part', 'commission_date',
            'client_unit', 'client_contact', 'client_phone',
            'witness', 'witness_name', 'sampler', 'sampler_name',
            'is_witnessed', 'status', 'status_display',
            'reviewer', 'reviewer_name', 'review_date', 'review_comment',
            'remark', 'items', 'contract_review',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'commission_no', 'status', 'reviewer',
            'review_date', 'review_comment',
            'created_at', 'updated_at', 'created_by',
        ]

    def get_project_name(self, obj: Commission) -> str:
        p = safe_related_attr(obj, 'project')
        return getattr(p, 'name', '') if p else ''

    def get_reviewer_name(self, obj: Commission) -> str:
        if obj.reviewer:
            return obj.reviewer.get_full_name() or str(obj.reviewer)
        return ''

    def get_sub_project_name(self, obj: Commission) -> str:
        sp = safe_related_attr(obj, 'sub_project')
        return getattr(sp, 'name', '') if sp else ''

    def get_witness_name(self, obj: Commission) -> str:
        if obj.witness_id and obj.witness:
            return obj.witness.name
        return ''

    def get_sampler_name(self, obj: Commission) -> str:
        if obj.sampler_id and obj.sampler:
            return obj.sampler.name
        return ''



class _NestedItemSerializer(serializers.ModelSerializer):
    """Write-only serializer for nested item creation/update."""

    class Meta:
        model = CommissionItem
        fields = [
            'test_parameter', 'test_object', 'test_item', 'test_standard',
            'test_method', 'specification', 'grade',
            'quantity', 'unit', 'remark',
        ]


class CommissionCreateSerializer(BaseModelSerializer):
    items = _NestedItemSerializer(many=True, required=False)

    class Meta:
        model = Commission
        fields = [
            'id', 'project', 'sub_project', 'construction_part',
            'commission_date', 'client_unit', 'client_contact',
            'client_phone', 'witness', 'sampler', 'is_witnessed', 'remark', 'items',
        ]
        read_only_fields = ['id']

    def create(self, validated_data: dict) -> Commission:
        items_data = validated_data.pop('items', [])
        commission = Commission.objects.create(**validated_data)
        for item_data in items_data:
            CommissionItem.objects.create(
                commission=commission, **item_data,
            )
        return commission

    def validate(self, attrs: dict) -> dict:
        if attrs.get('is_witnessed') is False:
            attrs['witness'] = None
            attrs['sampler'] = None
        return attrs


class CommissionUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Commission
        fields = [
            'sub_project', 'construction_part', 'commission_date',
            'client_unit', 'client_contact', 'client_phone',
            'witness', 'sampler', 'is_witnessed', 'remark',
        ]

    def validate(self, attrs: dict) -> dict:
        if self.instance and self.instance.status != 'draft':
            raise serializers.ValidationError('只有草稿状态的委托单可以编辑')
        if attrs.get('is_witnessed') is False:
            attrs['witness'] = None
            attrs['sampler'] = None
        return attrs
