from __future__ import annotations

import threading
from datetime import datetime

from django.db import connection
from django.db.utils import ProgrammingError


class NumberGenerator:
    _lock = threading.Lock()

    @classmethod
    def generate(
        cls,
        prefix: str,
        category_code: str | None = None,
        project_code: str | None = None,
    ) -> str:
        now = datetime.now()
        date_part = now.strftime('%Y%m')

        parts = [prefix, date_part]
        if category_code:
            parts.append(category_code)
        if project_code:
            parts.append(project_code)

        key = '-'.join(parts)
        seq = cls._next_sequence(key)

        return f'{key}-{seq:04d}'

    @classmethod
    def _next_sequence(cls, key: str) -> int:
        redis_seq = cls._try_redis(key)
        if redis_seq is not None:
            return redis_seq
        return cls._db_fallback(key)

    @classmethod
    def _try_redis(cls, key: str) -> int | None:
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection('default')
            redis_key = f'limis:seq:{key}'
            return conn.incr(redis_key)
        except Exception:
            return None

    @classmethod
    def _db_fallback(cls, key: str) -> int:
        with cls._lock:
            with connection.cursor() as cursor:
                # In some dev environments the `core_sequence` table/migration may be missing.
                # Fallback to create it on-the-fly to avoid Commission/Project number generation failing.
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS core_sequence (
                        seq_key varchar(255) PRIMARY KEY,
                        current_val bigint NOT NULL
                    )
                    """,
                )
                cursor.execute(
                    """
                    INSERT INTO core_sequence (seq_key, current_val)
                    VALUES (%s, 1)
                    ON CONFLICT (seq_key)
                    DO UPDATE SET current_val = core_sequence.current_val + 1
                    RETURNING current_val
                    """,
                    [key],
                )
                row = cursor.fetchone()
                return row[0] if row else 1
