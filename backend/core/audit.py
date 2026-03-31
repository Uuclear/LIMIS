from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger('audit')


def log_business_event(
    *,
    user: Any = None,
    module: str,
    action: str,
    entity: str,
    entity_id: int | None = None,
    path: str = '',
    payload: dict[str, Any] | None = None,
    status_code: int = 200,
) -> None:
    """
    结构化业务审计日志（补充 HTTP 中间件日志）。

    统一写入 system.AuditLog，body 中保留可检索结构：
    {
      "kind": "business_event",
      "module": "...",
      "action": "...",
      "entity": "...",
      "entity_id": 123,
      "payload": {...}
    }
    """
    try:
        from apps.system.models import AuditLog
    except Exception:
        return

    body = {
        'kind': 'business_event',
        'module': module,
        'action': action,
        'entity': entity,
        'entity_id': entity_id,
        'payload': payload or {},
    }
    try:
        AuditLog.objects.create(
            user=user if user and getattr(user, 'is_authenticated', False) else None,
            username=getattr(user, 'username', '') if user else '',
            method='BIZ_EVENT',
            path=(path or f'/{module}/{entity}/{action}/')[:500],
            body=json.dumps(body, ensure_ascii=False, default=str)[:4096],
            ip_address=None,
            status_code=status_code,
        )
    except Exception:
        # 审计不能影响主业务
        return


def log_sensitive_audit(
    *,
    user: Any = None,
    module: str,
    action: str,
    entity: str,
    entity_id: int | None = None,
    path: str = '',
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
    status_code: int = 200,
    ip_address: str | None = None,
) -> None:
    """
    敏感操作强制审计（删除报告、改检测结果等）。
    失败时记录日志但不抛异常，不影响主流程。
    """
    try:
        from apps.system.models import AuditLog
    except Exception as exc:
        logger.warning('sensitive audit skipped (import): %s', exc)
        return

    body = {
        'kind': 'sensitive_operation',
        'module': module,
        'action': action,
        'entity': entity,
        'entity_id': entity_id,
        'before': before or {},
        'after': after or {},
        'extra': extra or {},
    }
    try:
        AuditLog.objects.create(
            user=user if user and getattr(user, 'is_authenticated', False) else None,
            username=getattr(user, 'username', '') if user else '',
            method='SENSITIVE',
            path=(path or f'/{module}/{entity}/{action}/')[:500],
            body=json.dumps(body, ensure_ascii=False, default=str)[:4096],
            ip_address=ip_address,
            status_code=status_code,
        )
    except Exception:
        logger.exception(
            'sensitive audit write failed module=%s action=%s entity=%s id=%s',
            module, action, entity, entity_id,
        )

