from __future__ import annotations

import logging
import threading
from datetime import datetime

from django.db import connection, transaction
from django.db.utils import ProgrammingError

logger = logging.getLogger(__name__)


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
        # 优先使用Redis，性能更好
        redis_seq = cls._try_redis(key)
        if redis_seq is not None:
            return redis_seq
        # Redis不可用时使用数据库，确保并发安全
        return cls._db_fallback(key)

    @classmethod
    def _try_redis(cls, key: str) -> int | None:
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection('default')
            redis_key = f'limis:seq:{key}'
            # 使用INCR保证原子性
            return conn.incr(redis_key)
        except Exception as e:
            logger.warning(f'Redis序列生成失败，切换到数据库: {e}')
            return None

    @classmethod
    def _db_fallback(cls, key: str) -> int:
        """使用数据库事务和行锁确保并发安全"""
        with cls._lock:
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        # 确保表存在
                        cursor.execute(
                            """
                            CREATE TABLE IF NOT EXISTS core_sequence (
                                seq_key varchar(255) PRIMARY KEY,
                                current_val bigint NOT NULL DEFAULT 0
                            )
                            """,
                        )
                        
                        # 使用SELECT FOR UPDATE获取行锁，确保并发安全
                        cursor.execute(
                            """
                            SELECT current_val FROM core_sequence 
                            WHERE seq_key = %s FOR UPDATE
                            """,
                            [key],
                        )
                        row = cursor.fetchone()
                        
                        if row:
                            new_val = row[0] + 1
                            cursor.execute(
                                """
                                UPDATE core_sequence SET current_val = %s 
                                WHERE seq_key = %s
                                """,
                                [new_val, key],
                            )
                        else:
                            # 行不存在，插入新行
                            new_val = 1
                            cursor.execute(
                                """
                                INSERT INTO core_sequence (seq_key, current_val) 
                                VALUES (%s, %s)
                                """,
                                [key, new_val],
                            )
                        
                        return new_val
            except Exception as e:
                logger.error(f'数据库序列生成失败: {e}')
                # 最后的fallback：使用时间戳+随机数
                import random
                fallback_seq = int(datetime.now().timestamp() % 10000) + random.randint(1, 999)
                logger.warning(f'使用fallback序列号: {fallback_seq}')
                return fallback_seq
