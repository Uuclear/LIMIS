from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer

from .models import Commission, CommissionItem, ContractReview


class CommissionItemSerializer(BaseModelSerializer):
    class Meta:
        model = CommissionItem
        fields = [
            'id', 'commission', 'test_object', 'test_item',
            'test_standard', 'test_method', 'specification',
            'grade', 'quantity', 'unit', 'remark',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'commission': {'required': False}}


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
    project_name = serializers.CharField(
        source='project.name', read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    item_count = serializers.IntegerField(
        source='items.count', read_only=True,
    )

    class Meta:
        model = Commission
        fields = [
            'id', 'commission_no', 'project', 'project_name',
            'construction_part', 'commission_date', 'client_unit',
            'is_witnessed', 'status', 'status_display', 'item_count',
            'created_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'commission_no', 'created_at', 'created_by',
        ]


class CommissionDetailSerializer(BaseModelSerializer):
    items = CommissionItemSerializer(many=True, read_only=True)
    contract_review = ContractReviewSerializer(read_only=True)
    project_name = serializers.CharField(
        source='project.name', read_only=True,
    )
    sub_project_name = serializers.SerializerMethodField()
    witness_name = serializers.SerializerMethodField()
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
            'witness', 'witness_name', 'is_witnessed', 'status', 'status_display',
            'reviewer', 'reviewer_name', 'review_date', 'review_comment',
            'remark', 'items', 'contract_review',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'commission_no', 'status', 'reviewer',
            'review_date', 'review_comment',
            'created_at', 'updated_at', 'created_by',
        ]

    def get_reviewer_name(self, obj: Commission) -> str:
        if obj.reviewer:
            return obj.reviewer.get_full_name() or str(obj.reviewer)
        return ''

    def get_sub_project_name(self, obj: Commission) -> str:
        if obj.sub_project_id and obj.sub_project:
            return obj.sub_project.name
        return ''

    def get_witness_name(self, obj: Commission) -> str:
        if obj.witness_id and obj.witness:
            return obj.witness.name
        return ''


class _NestedItemSerializer(serializers.ModelSerializer):
    """Write-only serializer for nested item creation/update."""

    class Meta:
        model = CommissionItem
        fields = [
            'test_object', 'test_item', 'test_standard',
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
            'client_phone', 'witness', 'is_witnessed', 'remark', 'items',
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


class CommissionUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Commission
        fields = [
            'sub_project', 'construction_part', 'commission_date',
            'client_unit', 'client_contact', 'client_phone',
            'witness', 'is_witnessed', 'remark',
        ]

    def validate(self, attrs: dict) -> dict:
        if self.instance and self.instance.status != 'draft':
            raise serializers.ValidationError('只有草稿状态的委托单可以编辑')
        return attrs
