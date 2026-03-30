from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.utils import timezone
from django_filters import rest_framework as django_filters
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import LimsModulePermission

from . import services
from .models import AuditLog, Permission, Role, User
from .serializers import (
    AuditLogSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PermissionSerializer,
    RoleCreateUpdateSerializer,
    RoleSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


# ───────────────────── Filters ─────────────────────


class AuditLogFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(
        field_name='timestamp', lookup_expr='gte',
    )
    end_date = django_filters.DateTimeFilter(
        field_name='timestamp', lookup_expr='lte',
    )
    user = django_filters.NumberFilter(field_name='user_id')
    method = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = AuditLog
        fields = ['user', 'method', 'start_date', 'end_date']


# ───────────────────── ViewSets ─────────────────────


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('roles').all()
    permission_classes = [permissions.IsAuthenticated, LimsModulePermission]
    lims_module = 'system'
    lims_action_map = {
        'reset_password': 'edit',
        'toggle_active': 'edit',
    }
    search_fields = ['username', 'first_name', 'last_name', 'phone', 'department']
    filterset_fields = ['is_active', 'department']
    ordering_fields = ['date_joined', 'username']

    def get_serializer_class(self) -> type:
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request: Request, pk: str = None) -> Response:
        user = self.get_object()
        password = request.data.get('password', '')
        if len(password) < 8:
            return Response(
                {'detail': '密码长度不能小于8位'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(password)
        user.save(update_fields=['password'])
        return Response({'detail': '密码已重置'})

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request: Request, pk: str = None) -> Response:
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        state = '启用' if user.is_active else '禁用'
        return Response({'detail': f'用户已{state}'})


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related('permissions').all()
    permission_classes = [permissions.IsAuthenticated, LimsModulePermission]
    lims_module = 'system'
    lims_action_map = {'assign_permissions': 'edit'}
    search_fields = ['name', 'code']

    def get_serializer_class(self) -> type:
        if self.action in ('create', 'update', 'partial_update'):
            return RoleCreateUpdateSerializer
        return RoleSerializer

    @action(detail=True, methods=['post'], url_path='assign-permissions')
    def assign_permissions(self, request: Request, pk: str = None) -> Response:
        role = self.get_object()
        permission_ids = request.data.get('permissions', [])
        perms = Permission.objects.filter(id__in=permission_ids)
        role.permissions.set(perms)
        return Response(RoleSerializer(role).data)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, LimsModulePermission]
    lims_module = 'system'
    lims_action_map = {'grouped': 'view'}
    pagination_class = None

    @action(detail=False, methods=['get'], url_path='grouped')
    def grouped(self, request: Request) -> Response:
        permissions_qs = self.get_queryset()
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for perm in permissions_qs:
            grouped[perm.module].append(PermissionSerializer(perm).data)
        return Response(grouped)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, LimsModulePermission]
    lims_module = 'system'
    filterset_class = AuditLogFilter
    ordering_fields = ['timestamp']


# ───────────────────── Auth Views ─────────────────────


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.authenticate_user(
            serializer.validated_data['username'],
            serializer.validated_data['password'],
        )
        user = result['user']
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return Response({
            'access': result['access'],
            'refresh': result['refresh'],
            'user': UserSerializer(user).data,
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            # 前端未带 refresh 时仍允许登出（本地会话已清），避免首次退出报错
            return Response({'detail': '已退出登录'})
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({'detail': '已退出登录'})
        return Response({'detail': '已退出登录'})


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = request.user
        user_data = UserSerializer(user).data
        user_data['permissions'] = services.get_user_permissions(user)
        return Response(user_data)


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request: Request) -> Response:
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response({'detail': '密码修改成功'})
