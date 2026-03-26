from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Permission, User


def authenticate_user(username: str, password: str) -> dict[str, Any]:
    user = authenticate(username=username, password=password)
    if user is None:
        raise AuthenticationFailed('用户名或密码错误')
    if not user.is_active:
        raise AuthenticationFailed('该账号已被禁用')
    refresh = RefreshToken.for_user(user)
    return {
        'user': user,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@transaction.atomic
def create_user(data: dict[str, Any], created_by: User | None = None) -> User:
    password = data.pop('password', None)
    role_ids = data.pop('roles', [])
    if not password:
        raise ValidationError({'password': '密码不能为空'})
    user = User(**data)
    user.set_password(password)
    user.save()
    if role_ids:
        user.roles.set(role_ids)
    return user


def get_user_permissions(user: User) -> list[str]:
    if user.is_superuser:
        return list(
            Permission.objects.values_list('code', flat=True)
        )
    return list(
        Permission.objects.filter(
            roles__users=user,
        ).distinct().values_list('code', flat=True)
    )


def has_permission(user: User, module: str, action: str) -> bool:
    if user.is_superuser:
        return True
    return Permission.objects.filter(
        roles__users=user,
        module=module,
        action=action,
    ).exists()
