from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.db.models import F, QuerySet

from django.utils import timezone
from django_filters import rest_framework as django_filters
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from .tokens import SessionVersionRefreshToken

from core.permissions import LimsModulePermission

from . import services
from .models import AuditLog, Notification, Permission, Role, User
from .throttles import PasswordChangeThrottle
from .serializers import (
    AuditLogSerializer,
    LoginSerializer,
    NotificationSerializer,
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
    # 与前端 value-format=YYYY-MM-DD 对齐：按「日期」含首尾全天，避免 end 被解析为当日 00:00 导致漏数据
    start_date = django_filters.DateFilter(
        field_name='timestamp', lookup_expr='date__gte',
    )
    end_date = django_filters.DateFilter(
        field_name='timestamp', lookup_expr='date__lte',
    )
    user = django_filters.NumberFilter(field_name='user_id')
    method = django_filters.CharFilter(lookup_expr='iexact')
    path = django_filters.CharFilter(field_name='path', lookup_expr='icontains')
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    status_code = django_filters.NumberFilter(field_name='status_code')
    idempotency_key = django_filters.CharFilter(
        field_name='idempotency_key', lookup_expr='icontains',
    )
    is_idempotent_replay = django_filters.BooleanFilter(
        field_name='is_idempotent_replay',
    )
    keyword = django_filters.CharFilter(method='filter_keyword')

    class Meta:
        model = AuditLog
        fields = [
            'user', 'method', 'path', 'username', 'status_code',
            'idempotency_key', 'is_idempotent_replay',
            'start_date', 'end_date', 'keyword',
        ]

    def filter_keyword(self, queryset, name, value):
        return queryset.filter(body__icontains=value)


# ───────────────────── ViewSets ─────────────────────


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('roles').all()
    permission_classes = [permissions.IsAuthenticated, LimsModulePermission]
    lims_module = 'system'
    lims_action_map = {
        'reset_password': 'edit',
        'toggle_active': 'edit',
        'kickout_sessions': 'edit',
    }
    search_fields = ['username', 'first_name', 'last_name', 'phone', 'department']
    filterset_fields = ['is_active', 'department']
    ordering_fields = ['date_joined', 'username']

    def get_queryset(self) -> QuerySet:
        from django.db.models import Q

        qs = super().get_queryset()
        real_name = self.request.query_params.get('real_name')
        if real_name:
            qs = qs.filter(
                Q(first_name__icontains=real_name)
                | Q(last_name__icontains=real_name),
            )
        return qs

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

    @action(detail=True, methods=['post'], url_path='kickout-sessions')
    def kickout_sessions(self, request: Request, pk: str = None) -> Response:
        user = self.get_object()
        User.objects.filter(pk=user.pk).update(session_version=F('session_version') + 1)
        return Response({'detail': '已使该用户全部会话失效'})


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
            services.get_client_ip(request),
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
            return Response({'detail': '已退出登录'})
        try:
            token = SessionVersionRefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass
        except Exception:
            # 黑名单表未迁移、已列入等仍视为登出成功，避免 500
            pass
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
    throttle_classes = [PasswordChangeThrottle]

    def put(self, request: Request) -> Response:
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response({'detail': '密码修改成功'})


class NotificationViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'code': 200, 'data': {'count': count}})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        from django.utils import timezone
        self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return Response({'code': 200, 'message': '已全部标记已读'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        from django.utils import timezone
        notif = self.get_object()
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=['is_read', 'read_at'])
        return Response({'code': 200, 'data': NotificationSerializer(notif).data})
