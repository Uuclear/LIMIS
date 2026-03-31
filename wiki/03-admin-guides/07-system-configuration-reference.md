# 系统配置项参考

本文汇总 **后端 `base.py` 与环境变量** 中与运维/安全相关的配置，便于对照部署。具体以运行环境实际值为准。

## 1. Django 核心

| 项 | 环境变量 / 代码 | 说明 |
|----|-----------------|------|
| `SECRET_KEY` | `SECRET_KEY` | 生产必须替换；泄露需轮换并全员重登 |
| `DEBUG` | `dev.py` / 部署 | 生产必须为 False |
| `ALLOWED_HOSTS` | `ALLOWED_HOSTS` | 逗号分隔主机名 |
| `AUTH_USER_MODEL` | 固定 `system.User` | 迁移后不可改 |

## 2. 数据库

| 项 | 环境变量 | 默认（base.py） |
|----|----------|-----------------|
| 引擎 | - | PostgreSQL |
| `NAME` | `DB_NAME` | `limis` |
| `USER` | `DB_USER` | `limis` |
| `PASSWORD` | `DB_PASSWORD` | 空 |
| `HOST` | `DB_HOST` | `db` |
| `PORT` | `DB_PORT` | `5432` |

**Compose 参考**：`docker-compose.yml` 中 `db` 服务端口映射 `5434:5432`（避免与宿主机冲突）。

## 3. Redis 与 Celery

| 项 | 环境变量 | 说明 |
|----|----------|------|
| `REDIS_URL` | `REDIS_URL` | 默认 `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | 继承 | 与 `REDIS_URL` 同 |
| `CELERY_RESULT_BACKEND` | 继承 | 同上 |

## 4. JWT

**位置**：`SIMPLE_JWT` in `backend/limis/settings/base.py`

| 项 | 典型值 |
|----|--------|
| `ACCESS_TOKEN_LIFETIME` | 2 小时 |
| `REFRESH_TOKEN_LIFETIME` | 7 天 |
| `ROTATE_REFRESH_TOKENS` | True |
| `BLACKLIST_AFTER_ROTATION` | True |
| `AUTH_TOKEN_CLASSES` | `SessionVersionAccessToken` |

## 5. 登录与密码

| 项 | 环境变量 | 说明 |
|----|----------|------|
| `LOGIN_FAILURE_MAX_ATTEMPTS` | 同左 | `0` 关闭锁定 |
| `LOGIN_FAILURE_LOCKOUT_SECONDS` | 同左 | 秒 |
| `LOGIN_FAILURE_WINDOW_SECONDS` | 同左 | 秒 |
| `PASSWORD_CHANGE_THROTTLE_RATE` | 同左 | 如 `5/hour` |

## 6. MinIO / 对象存储

| 项 | 环境变量 | 默认 |
|----|----------|------|
| `MINIO_ENDPOINT` | `MINIO_ENDPOINT` | `minio:9000` |
| `MINIO_ACCESS_KEY` | `MINIO_ACCESS_KEY` | 空 |
| `MINIO_SECRET_KEY` | `MINIO_SECRET_KEY` | 空 |
| `MINIO_BUCKET` | `MINIO_BUCKET` | `limis` |

## 7. REST Framework

| 项 | 说明 |
|----|------|
| `DEFAULT_AUTHENTICATION_CLASSES` | `SessionVersionJWTAuthentication` |
| `DEFAULT_PAGINATION_CLASS` | `core.pagination.StandardPagination` |
| `PAGE_SIZE` | 20 |
| `EXCEPTION_HANDLER` | `core.exceptions.custom_exception_handler` |

## 8. 中间件链（与审计/幂等相关）

`backend/limis/settings/base.py` → `MIDDLEWARE`：

- `IdempotencyMiddleware`
- `AuditLogMiddleware`

详见 `backend/core/middleware.py`。

## 9. CORS / HTTPS

部署层常通过环境变量注入（见 `docker-compose.yml` 中 `CORS_ALLOWED_ORIGINS`、`USE_HTTPS` 等引用方式；以实际 `dev.py` / `production` 覆盖为准）。

## 10. 风险提示

- **默认密钥与数据库口令**仅用于开发，上线前必须更换。
- 修改 `SIMPLE_JWT` 生存期会影响用户体验与风控，需公告。

## 11. 相关文件路径

- `backend/limis/settings/base.py`
- `backend/limis/settings/dev.py`（若存在覆盖）
- `docker-compose.yml`
