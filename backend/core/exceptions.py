from __future__ import annotations

import json
import logging
import os
import time
import traceback
from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class BusinessException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        code: int = 400,
        message: str = '业务异常',
        detail: Any = None,
    ) -> None:
        self.code = code
        self.message = message
        super().__init__(detail=detail or message)


class ValidationException(BusinessException):
    def __init__(self, message: str = '数据验证失败', errors: Any = None) -> None:
        super().__init__(code=422, message=message, detail=errors)
        self.errors = errors


class PermissionDeniedException(BusinessException):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, message: str = '权限不足') -> None:
        super().__init__(code=403, message=message)


def _first_validation_message(detail: Any) -> str | None:
    """取 DRF ValidationError 中第一条可读说明，便于前端直接展示。"""
    if isinstance(detail, dict):
        for k, v in detail.items():
            if isinstance(v, list) and v:
                # 让前端能明确“哪个字段”缺失/不合法
                return f'{k}: {v[0]}'
            if isinstance(v, str):
                return f'{k}: {v}'
    elif isinstance(detail, list) and detail:
        return str(detail[0])
    elif isinstance(detail, str):
        return detail
    return None


def custom_exception_handler(
    exc: Exception,
    context: dict,
) -> Response | None:
    response = exception_handler(exc, context)

    if isinstance(exc, BusinessException):
        return _build_error_response(exc.code, exc.message, getattr(exc, 'errors', None))

    if isinstance(exc, ValidationError):
        msg = _first_validation_message(exc.detail) or '数据验证失败'
        return _build_error_response(422, msg, exc.detail)

    if response is not None:
        return _build_error_response(
            response.status_code,
            _extract_message(response.data),
            response.data if isinstance(response.data, (dict, list)) else None,
        )

    # region agent log
    _debug_log_drf_uncaught_for_testing_tasks(exc, context)
    try:
        req = context.get('request')
        req_path = getattr(req, 'path', '') if req is not None else ''
        if '/api/v1/testing/tasks' in (req_path or ''):
            logger.exception('DRF uncaught testing-task exception path=%s exc=%s', req_path, type(exc).__name__)
    except Exception:
        pass
    # endregion
    return None


def _debug_log_drf_uncaught_for_testing_tasks(exc: Exception, context: dict) -> None:
    """DRF 在 exception_handler 返回 None 时会将异常视为未处理（通常对应 HTTP 500）。"""
    request = context.get('request')
    if request is None:
        return
    path = getattr(request, 'path', '') or ''
    if '/api/v1/testing/tasks' not in path:
        return
    try:
        os.makedirs('/opt/limis/.cursor', exist_ok=True)
        with open('/opt/limis/.cursor/debug-66f994.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': '66f994',
                'runId': 'initial',
                'hypothesisId': 'H3',
                'location': 'core/exceptions.py:custom_exception_handler',
                'message': 'drf_uncaught_exception',
                'data': {
                    'path': path,
                    'exc_type': type(exc).__name__,
                    'error': str(exc),
                    'traceback': traceback.format_exc(),
                },
                'timestamp': int(time.time() * 1000),
            }, ensure_ascii=False) + os.linesep)
    except Exception:
        pass


def _build_error_response(
    code: int,
    message: str,
    errors: Any = None,
) -> Response:
    payload: dict[str, Any] = {
        'code': code,
        'message': message,
    }
    if errors is not None:
        payload['errors'] = errors

    http_status = code if 100 <= code < 600 else status.HTTP_400_BAD_REQUEST
    return Response(payload, status=http_status)


def _extract_message(data: Any) -> str:
    if isinstance(data, dict):
        return str(data.get('detail', '请求错误'))
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)
