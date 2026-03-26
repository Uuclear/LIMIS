from __future__ import annotations

import json
import logging
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger('audit')

SENSITIVE_FIELDS = {'password', 'password1', 'password2', 'token', 'secret', 'access_token', 'refresh_token'}
SKIP_PATHS = {'/api/v1/system/login/', '/api/v1/system/token/refresh/'}
LOGGED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}


class AuditLogMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        raw_body = self._cache_body(request)
        response = self.get_response(request)

        if self._should_log(request):
            self._record(request, response, raw_body)

        return response

    def _cache_body(self, request: HttpRequest) -> bytes:
        try:
            return request.body
        except Exception:
            return b''

    def _should_log(self, request: HttpRequest) -> bool:
        if request.method not in LOGGED_METHODS:
            return False
        return request.path not in SKIP_PATHS

    def _record(self, request: HttpRequest, response: HttpResponse, raw_body: bytes) -> None:
        try:
            from apps.system.models import AuditLog
        except ImportError:
            return

        body = self._sanitize_body(raw_body)
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

        try:
            AuditLog.objects.create(
                user=user,
                username=getattr(user, 'username', '') if user else '',
                method=request.method,
                path=request.path[:500],
                body=body,
                ip_address=self._get_client_ip(request),
                status_code=response.status_code,
            )
        except Exception as e:
            logger.warning('Failed to create audit log: %s', e)

    def _sanitize_body(self, raw_body: bytes) -> str:
        try:
            data: dict[str, Any] = json.loads(raw_body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ''

        sanitized = {
            k: '***' if k.lower() in SENSITIVE_FIELDS else v
            for k, v in data.items()
        }
        return json.dumps(sanitized, ensure_ascii=False, default=str)[:4096]

    def _get_client_ip(self, request: HttpRequest) -> str:
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
