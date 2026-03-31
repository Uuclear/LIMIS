from __future__ import annotations

import json
import logging
import hashlib
from typing import Any, Callable

from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse, JsonResponse

logger = logging.getLogger('audit')

SENSITIVE_FIELDS = {'password', 'password1', 'password2', 'token', 'secret', 'access_token', 'refresh_token'}
SKIP_PATHS = {'/api/v1/system/login/', '/api/v1/system/token/refresh/'}
LOGGED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
IDEMPOTENT_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}


class IdempotencyMiddleware:
    _IDEMPOTENCY_RESOLVE_MAX_STEPS = 32

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method not in IDEMPOTENT_METHODS or not request.path.startswith('/api/v1/'):
            return self.get_response(request)

        key = (request.headers.get('Idempotency-Key') or '').strip()
        if not key:
            return self.get_response(request)
        if len(key) > 128:
            return JsonResponse({'code': 409, 'message': 'Idempotency-Key 过长'}, status=409)

        try:
            from apps.system.models import IdempotencyRecord
        except ImportError:
            return self.get_response(request)

        raw_body = self._cache_body(request)
        request_hash = hashlib.sha256(raw_body).hexdigest()
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        request._idempotency_key = key
        request._idempotency_replayed = False

        record = self._lock_or_create_record(
            IdempotencyRecord=IdempotencyRecord,
            user=user,
            key=key,
            method=request.method,
            path=request.path,
            request_hash=request_hash,
        )
        request._idempotency_record_id = record.id

        record, outcome = self._resolve_record_state(
            IdempotencyRecord=IdempotencyRecord,
            record=record,
            request_hash=request_hash,
        )
        if outcome == 'completed_mismatch':
            return JsonResponse({'code': 409, 'message': '幂等键已被不同请求体占用'}, status=409)
        if outcome == 'replay':
            request._idempotency_replayed = True
            response = HttpResponse(
                content=record.response_body or '',
                status=record.response_status or 200,
                content_type=record.content_type or 'application/json',
            )
            response['X-Idempotency-Replayed'] = 'true'
            return response
        if outcome == 'conflict_processing':
            return JsonResponse({'code': 409, 'message': '幂等键冲突（处理中）'}, status=409)
        if outcome == 'duplicate_in_flight':
            return JsonResponse({'code': 409, 'message': '重复请求处理中，请稍后重试'}, status=409)
        if outcome == 'unexpected_state':
            logger.warning(
                'IdempotencyMiddleware: could not claim record id=%s state=%s',
                getattr(record, 'pk', None),
                getattr(record, 'state', None),
            )
            return JsonResponse({'code': 409, 'message': '重复请求处理中，请稍后重试'}, status=409)

        try:
            response = self.get_response(request)
        except Exception:
            try:
                IdempotencyRecord.objects.filter(pk=record.pk).update(state='failed')
            except Exception as cleanup_err:
                logger.warning('IdempotencyMiddleware: failed to mark record failed: %s', cleanup_err)
            raise

        self._persist_completed_safe(IdempotencyRecord, record.pk, response)
        response['X-Idempotency-Replayed'] = 'false'
        return response

    def _resolve_record_state(self, IdempotencyRecord, record, request_hash: str):
        """Return (record, outcome). Single writer: only one request CAS-es failed→processing."""
        steps = 0
        while steps < self._IDEMPOTENCY_RESOLVE_MAX_STEPS:
            steps += 1
            record.refresh_from_db()
            if record.state == 'completed':
                if record.request_hash != request_hash:
                    return record, 'completed_mismatch'
                return record, 'replay'
            if record.state == 'processing':
                if record.request_hash != request_hash:
                    return record, 'conflict_processing'
                return record, 'duplicate_in_flight'
            if record.state == 'failed':
                updated = IdempotencyRecord.objects.filter(pk=record.pk, state='failed').update(
                    state='processing',
                    request_hash=request_hash,
                    response_status=None,
                    response_body='',
                    content_type='',
                )
                if updated:
                    record.refresh_from_db()
                    return record, 'claimed'
                continue
            logger.warning('IdempotencyMiddleware: unknown state %r on record %s', record.state, record.pk)
            return record, 'unexpected_state'
        logger.warning('IdempotencyMiddleware: resolve loop exceeded max steps for record %s', record.pk)
        return record, 'unexpected_state'

    def _persist_completed_safe(self, IdempotencyRecord, record_pk: int, response: HttpResponse) -> None:
        body_text = self._response_text(response)
        ct = (response.get('Content-Type', '') or '')[:120]
        try:
            IdempotencyRecord.objects.filter(pk=record_pk).update(
                state='completed',
                response_status=response.status_code,
                response_body=body_text,
                content_type=ct,
            )
        except Exception:
            logger.exception('IdempotencyMiddleware: persist completed failed')
            try:
                IdempotencyRecord.objects.filter(pk=record_pk, state='processing').update(state='failed')
            except Exception as cleanup_err:
                logger.warning('IdempotencyMiddleware: rollback to failed after persist error: %s', cleanup_err)

    def _cache_body(self, request: HttpRequest) -> bytes:
        try:
            return request.body
        except Exception:
            return b''

    def _response_text(self, response: HttpResponse) -> str:
        """Persist at most 20k chars; tolerate binary/non-UTF8. Uses .content so StreamingHttpResponse is buffered once by Django."""
        max_chars = 20000
        try:
            raw = bytes(response.content)
        except MemoryError:
            logger.warning('IdempotencyMiddleware: response body too large to cache')
            return ''
        except Exception as exc:
            logger.warning('IdempotencyMiddleware: could not read response body: %s', exc)
            return ''

        if len(raw) > max_chars * 4:
            raw = raw[: max_chars * 4]

        charset = getattr(response, 'charset', None) or 'utf-8'
        try:
            payload = raw.decode(charset, errors='replace')
        except LookupError:
            payload = raw.decode('utf-8', errors='replace')
        return payload[:max_chars]

    def _lock_or_create_record(self, IdempotencyRecord, user, key: str, method: str, path: str, request_hash: str):
        with transaction.atomic():
            try:
                record = IdempotencyRecord.objects.create(
                    user=user,
                    key=key,
                    method=method,
                    path=path,
                    request_hash=request_hash,
                    state='failed',
                )
                return record
            except IntegrityError:
                return IdempotencyRecord.objects.select_for_update().get(
                    user=user,
                    key=key,
                    method=method,
                    path=path,
                )


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
                idempotency_key=getattr(request, '_idempotency_key', '')[:128],
                is_idempotent_replay=bool(
                    getattr(request, '_idempotency_replayed', False),
                ),
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
