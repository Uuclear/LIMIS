from __future__ import annotations

from rest_framework import permissions

from core.views import BaseModelViewSet

from .filters import StandardFilter
from .models import MethodValidation, Standard
from .serializers import (
    MethodValidationSerializer,
    StandardDetailSerializer,
    StandardListSerializer,
)


class StandardViewSet(BaseModelViewSet):
    queryset = Standard.objects.select_related('replaced_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = StandardFilter
    search_fields = ['standard_no', 'name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StandardDetailSerializer
        return StandardListSerializer


class MethodValidationViewSet(BaseModelViewSet):
    queryset = MethodValidation.objects.select_related(
        'standard', 'validator',
    ).all()
    serializer_class = MethodValidationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['standard', 'conclusion']
