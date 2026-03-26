from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


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


def custom_exception_handler(
    exc: Exception,
    context: dict,
) -> Response | None:
    response = exception_handler(exc, context)

    if isinstance(exc, BusinessException):
        return _build_error_response(exc.code, exc.message, getattr(exc, 'errors', None))

    if isinstance(exc, ValidationError):
        return _build_error_response(422, '数据验证失败', exc.detail)

    if response is not None:
        return _build_error_response(
            response.status_code,
            _extract_message(response.data),
            response.data if isinstance(response.data, (dict, list)) else None,
        )

    return None


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
