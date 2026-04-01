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
    """权限码列表；短时缓存减轻 /me 与鉴权路径上的重复查询（按用户与会话版本键）。"""
    if not user.is_authenticated:
        return []
    sv = int(getattr(user, 'session_version', 0) or 0)
    cache_key = f'lims:user_permissions:{user.pk}:{sv}'
    cached = cache.get(cache_key)
    if cached is not None:
        return list(cached)
    if user.is_superuser:
        codes = list(Permission.objects.values_list('code', flat=True))
    else:
        codes = list(
            Permission.objects.filter(
                roles__users=user,
            ).distinct().values_list('code', flat=True)
        )
    timeout = int(getattr(settings, 'USER_PERMISSIONS_CACHE_SECONDS', 120))
    cache.set(cache_key, codes, timeout=timeout)
    return codes


def has_permission(user: User, module: str, action: str) -> bool:
    if user.is_superuser:
        return True
    return Permission.objects.filter(
        roles__users=user,
        module=module,
        action=action,
    ).exists()


def has_permission_code(user: User, permission_code: str) -> bool:
    if user.is_superuser:
        return True
    return Permission.objects.filter(
        roles__users=user,
        code=permission_code,
    ).exists()


def notify_user(
    user_id: int,
    notification_type: str,
    title: str,
    content: str = '',
    link_path: str = '',
) -> None:
    """写入站内通知（顶栏消息中心数据源）。"""
    from .models import Notification

    Notification.objects.create(
        recipient_id=user_id,
        notification_type=notification_type,
        title=title[:200],
        content=content or '',
        link_path=(link_path or '')[:200],
    )


def notify_users_by_permission_code(
    permission_code: str,
    notification_type: str,
    title: str,
    content: str = '',
    link_path: str = '',
) -> int:
    """向拥有指定权限码的全部活跃用户各发一条通知。"""
    ids = (
        User.objects.filter(
            is_active=True,
            roles__permissions__code=permission_code,
        )
        .distinct()
        .values_list('pk', flat=True)
    )
    n = 0
    for uid in ids:
        notify_user(
            int(uid), notification_type, title, content, link_path,
        )
        n += 1
    return n


def notify_users_by_role_code(
    role_code: str,
    notification_type: str,
    title: str,
    content: str = '',
    link_path: str = '',
) -> int:
    ids = (
        User.objects.filter(
            is_active=True,
            roles__code=role_code,
        )
        .distinct()
        .values_list('pk', flat=True)
    )
    n = 0
    for uid in ids:
        notify_user(int(uid), notification_type, title, content, link_path)
        n += 1
    return n


def notify_flow_targets(
    *,
    role_code: str,
    fallback_permission_code: str,
    notification_type: str,
    title: str,
    content: str = '',
    link_path: str = '',
) -> int:
    sent = notify_users_by_role_code(
        role_code, notification_type, title, content, link_path,
    )
    if sent > 0:
        return sent
    return notify_users_by_permission_code(
        fallback_permission_code, notification_type, title, content, link_path,
    )
