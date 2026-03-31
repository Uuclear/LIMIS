from __future__ import annotations

import hashlib
from typing import Any

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import AuthenticationFailed, Throttled, ValidationError
from rest_framework.request import Request

from .models import Permission, User
from .tokens import SessionVersionRefreshToken


def bump_session_version(user: User) -> None:
    """递增会话版本，使该用户已签发的 JWT 全部失效。"""
    User.objects.filter(pk=user.pk).update(session_version=F('session_version') + 1)


def get_client_ip(request: Request) -> str:
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return (request.META.get('REMOTE_ADDR') or '').strip()


def _login_digest(username: str, client_ip: str) -> str:
    raw = f'{username.strip()}:{client_ip}'.encode()
    return hashlib.sha256(raw).hexdigest()[:40]


def _fail_key(digest: str) -> str:
    return f'login:fail:{digest}'


def _lock_key(digest: str) -> str:
    return f'login:lock:{digest}'


def check_login_lockout(username: str, client_ip: str) -> None:
    max_attempts = getattr(settings, 'LOGIN_FAILURE_MAX_ATTEMPTS', 0)
    if max_attempts <= 0:
        return
    digest = _login_digest(username, client_ip)
    if cache.get(_lock_key(digest)):
        lock_sec = int(getattr(settings, 'LOGIN_FAILURE_LOCKOUT_SECONDS', 300))
        mins = max(1, (lock_sec + 59) // 60)
        raise Throttled(detail=f'登录失败次数过多，请约 {mins} 分钟后再试')


def record_login_failure(username: str, client_ip: str) -> None:
    max_attempts = getattr(settings, 'LOGIN_FAILURE_MAX_ATTEMPTS', 0)
    if max_attempts <= 0:
        return
    digest = _login_digest(username, client_ip)
    fk = _fail_key(digest)
    lk = _lock_key(digest)
    window = int(getattr(settings, 'LOGIN_FAILURE_WINDOW_SECONDS', 900))
    lock_sec = int(getattr(settings, 'LOGIN_FAILURE_LOCKOUT_SECONDS', 300))

    if cache.get(lk):
        return

    n = cache.get(fk)
    if n is None:
        cache.set(fk, 1, timeout=window)
        n = 1
    else:
        n = cache.incr(fk)
        cache.touch(fk, timeout=window)

    if n >= max_attempts:
        cache.set(lk, 1, timeout=lock_sec)
        cache.delete(fk)


def clear_login_attempts(username: str, client_ip: str) -> None:
    digest = _login_digest(username, client_ip)
    cache.delete(_fail_key(digest))
    cache.delete(_lock_key(digest))


def authenticate_user(username: str, password: str, client_ip: str = '') -> dict[str, Any]:
    check_login_lockout(username, client_ip)

    user = authenticate(username=username, password=password)
    if user is None:
        record_login_failure(username, client_ip)
        raise AuthenticationFailed('用户名或密码错误')
    if not user.is_active:
        record_login_failure(username, client_ip)
        raise AuthenticationFailed('该账号已被禁用')
    clear_login_attempts(username, client_ip)
    bump_session_version(user)
    user.refresh_from_db(fields=['session_version'])
    refresh = SessionVersionRefreshToken.for_user(user)
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
