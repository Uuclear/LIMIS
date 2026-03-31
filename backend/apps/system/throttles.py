"""DRF throttles scoped to system endpoints."""

from __future__ import annotations

from rest_framework.throttling import UserRateThrottle


class PasswordChangeThrottle(UserRateThrottle):
    """已登录用户修改密码：按用户限频（见 settings 中 password_change scope）。"""

    scope = 'password_change'
