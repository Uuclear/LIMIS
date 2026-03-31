from __future__ import annotations

import json
from typing import Any


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

