# 管理概览与日常巡检清单

本文面向 **LIMIS 系统管理员 / 实验室信息化负责人**，说明后台职责边界、与代码的对应关系，以及建议的每日/每周巡检项。

## 1. 系统架构速览（与仓库路径）

| 层级 | 说明 | 典型路径 |
|------|------|----------|
| 前端 | Vue 3 + Vue Router + Pinia | `frontend/src/` |
| 后端 API | Django REST Framework | `backend/apps/*/views.py`，统一前缀 ` /api/v1/`（见 `backend/limis/urls.py`） |
| 认证 | JWT（SimpleJWT）+ 会话版本 `sv` | `backend/apps/system/authentication.py`、`tokens.py` |
| 权限 | 模块 `lims_module` + `LimsModulePermission` | `backend/core/permissions.py` |
| 缓存/限流 | Redis | `backend/limis/settings/base.py` 中 `CACHES`、`LOGIN_*` |
| 对象存储 | MinIO（附件等） | `MINIO_*` 环境变量 |
| 编排（开发） | Docker Compose | `docker-compose.yml` |

## 2. 管理员职责边界

1. **账号与角色**：用户/角色/权限分配（页面：`/system/users`、`/system/roles`；API：`/api/v1/system/users/`、`roles/`）。
2. **安全与会话**：踢出会话、登录失败策略、密码策略（见 `05-password-policy-and-login-throttling.md`、`04-session-security-and-kickout.md`）。
3. **审计与合规**：操作日志查询、异常路径排查（页面：`/system/audit-logs`）。
4. **运行与发布**：备份、迁移、发版窗口（见 `09-backup-and-restore-sop.md`、`10-release-and-change-management.md`）。

## 3. 日常巡检清单（建议）

### 3.1 每日（约 10–15 分钟）

```
[1] 登录管理端 → 首页 /dashboard
    ↓
[2] 系统管理 → 操作日志 /system/audit-logs
    - 筛选 4xx/5xx 或关键字「AuthenticationFailed」「InvalidToken」
    ↓
[3] 抽查 1～2 条敏感操作（用户禁用、踢出、角色权限变更）
    - 路径是否来自预期 IP、时间
    ↓
[4] （若用容器）检查 backend / db / redis 容器健康
    docker compose ps  （或编排平台等价指标）
```

**对应实现**：HTTP 审计由 `backend/core/middleware.py` 中 `AuditLogMiddleware` 写入 `system.AuditLog`；登录/刷新等路径在 `SKIP_PATHS` 中**不记录请求体**。

### 3.2 每周

- **磁盘与数据库**：PostgreSQL 连接数、慢查询；MinIO 桶用量；`media` 卷增长。
- **证书与密钥**：`SECRET_KEY`、JWT 有效期策略是否仍符合制度（`SIMPLE_JWT` 于 `base.py`）。
- **依赖与漏洞**：关注 Django / Vue 安全公告。

### 3.3 发版日/变更日（额外）

- 迁移 `migrate` 是否成功、是否有回滚脚本或数据快照。
- 新环境变量是否已同步（见 `07-system-configuration-reference.md`）。

## 4. 配置项速查（管理员常用）

| 配置 | 位置 | 作用 |
|------|------|------|
| `LOGIN_FAILURE_MAX_ATTEMPTS` | `base.py` / 环境变量 | 登录失败锁定阈值，`0` 关闭 |
| `LOGIN_FAILURE_LOCKOUT_SECONDS` | 同上 | 锁定时长（秒） |
| `PASSWORD_CHANGE_THROTTLE_RATE` | 同上 | 改密接口限流 |
| `REDIS_URL` | 同上 | 缓存与 Celery |
| `DATABASES` | 同上 | PostgreSQL 连接 |

## 5. 风险与应对

| 风险 | 表现 | 建议 |
|------|------|------|
| 审计表膨胀 | 查询变慢 | 归档策略、按时间分区或定期导出冷数据 |
| Redis 不可用 | 登录限流异常、缓存异常 | 监控 Redis；生产应高可用 |
| 密钥泄露 | 伪造 Token | 轮换 `SECRET_KEY`、全量用户重新登录并配合踢出 |

## 6. 回滚思路（概览）

- **配置回滚**：恢复环境变量与 `settings` 上一版本，重启进程。
- **数据回滚**：优先用 **发布前快照**（PostgreSQL + MinIO + 媒体卷）恢复，而非仅 `migrate` 反向（可能丢数据）。

## 7. 相关文档

- `02-user-and-role-management.md`
- `06-audit-log-operations.md`
- `07-system-configuration-reference.md`
