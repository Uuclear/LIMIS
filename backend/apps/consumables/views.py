from __future__ import annotations

from django.db import models, transaction
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from .models import Consumable, ConsumableIn, ConsumableOut, Supplier
from .serializers import (
    ConsumableDetailSerializer,
    ConsumableInSerializer,
    ConsumableListSerializer,
    ConsumableOutSerializer,
    SupplierSerializer,
)


class SupplierViewSet(BaseModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    lims_module = 'consumables'
    filterset_fields = ['is_qualified']
    search_fields = ['name', 'contact_person']


class ConsumableViewSet(BaseModelViewSet):
    queryset = Consumable.objects.select_related('supplier').all()
    lims_module = 'consumables'
    filterset_fields = ['category', 'supplier']
    search_fields = ['name', 'code', 'specification']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConsumableDetailSerializer
        return ConsumableListSerializer

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request: Request) -> Response:
        qs = self.get_queryset().filter(
            stock_quantity__lte=models.F('safety_stock'),
        )
        serializer = ConsumableListSerializer(qs, many=True)
        return Response({'code': 200, 'data': serializer.data})


class ConsumableInViewSet(BaseModelViewSet):
    queryset = ConsumableIn.objects.select_related(
        'consumable', 'operator',
    ).all()
    serializer_class = ConsumableInSerializer
    lims_module = 'consumables'
    filterset_fields = ['consumable']

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save(operator=self.request.user)
            consumable = instance.consumable
            consumable.stock_quantity += instance.quantity
            consumable.save(update_fields=['stock_quantity', 'updated_at'])


class ConsumableOutViewSet(BaseModelViewSet):
    queryset = ConsumableOut.objects.select_related(
        'consumable', 'recipient',
    ).all()
    serializer_class = ConsumableOutSerializer
    lims_module = 'consumables'
    filterset_fields = ['consumable', 'recipient']

    def perform_create(self, serializer):
        consumable = Consumable.objects.get(
            pk=self.request.data.get('consumable'),
        )
        quantity = int(self.request.data.get('quantity', 0))
        if consumable.stock_quantity < quantity:
            raise serializers.ValidationError(
                {'quantity': f'库存不足，当前库存: {consumable.stock_quantity}'},
            )
        with transaction.atomic():
            serializer.save()
            consumable.stock_quantity -= quantity
            consumable.save(update_fields=['stock_quantity', 'updated_at'])
