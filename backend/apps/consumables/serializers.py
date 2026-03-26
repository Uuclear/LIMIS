from __future__ import annotations

from rest_framework import serializers

from core.serializers import BaseModelSerializer

from .models import Consumable, ConsumableIn, ConsumableOut, Supplier


class SupplierSerializer(BaseModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'phone', 'address',
            'evaluation_score', 'is_qualified',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConsumableListSerializer(BaseModelSerializer):
    supplier_name = serializers.CharField(
        source='supplier.name', read_only=True, default='',
    )
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Consumable
        fields = [
            'id', 'name', 'code', 'specification', 'unit',
            'category', 'manufacturer', 'supplier', 'supplier_name',
            'stock_quantity', 'safety_stock', 'is_low_stock',
            'expiry_date', 'storage_location', 'created_at',
        ]
        read_only_fields = ['id', 'stock_quantity', 'created_at']


class ConsumableDetailSerializer(BaseModelSerializer):
    supplier_name = serializers.CharField(
        source='supplier.name', read_only=True, default='',
    )
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Consumable
        fields = [
            'id', 'name', 'code', 'specification', 'unit',
            'category', 'manufacturer', 'supplier', 'supplier_name',
            'stock_quantity', 'safety_stock', 'is_low_stock',
            'expiry_date', 'storage_location',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'stock_quantity', 'created_at', 'updated_at']


class ConsumableInSerializer(BaseModelSerializer):
    consumable_name = serializers.CharField(
        source='consumable.name', read_only=True,
    )
    operator_name = serializers.SerializerMethodField()

    class Meta:
        model = ConsumableIn
        fields = [
            'id', 'consumable', 'consumable_name', 'quantity',
            'batch_no', 'purchase_date', 'expiry_date',
            'operator', 'operator_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'operator', 'created_at', 'updated_at']

    def get_operator_name(self, obj: ConsumableIn) -> str:
        if obj.operator:
            return obj.operator.get_full_name() or str(obj.operator)
        return ''


class ConsumableOutSerializer(BaseModelSerializer):
    consumable_name = serializers.CharField(
        source='consumable.name', read_only=True,
    )
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = ConsumableOut
        fields = [
            'id', 'consumable', 'consumable_name', 'quantity',
            'purpose', 'recipient', 'recipient_name', 'out_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_recipient_name(self, obj: ConsumableOut) -> str:
        if obj.recipient:
            return obj.recipient.get_full_name() or str(obj.recipient)
        return ''
