# 审计日志运维说明

LIMIS 审计数据主要落在 **`system.AuditLog`**，由 **HTTP 中间件** 与 **业务显式打点** 两部分组成。

## 1. HTTP 层审计（中间件）

**文件**：`backend/core/middleware.py` → `AuditLogMiddleware`

| 规则 | 说明 |
|------|------|
| 记录方法 | `POST`、`PUT`、`PATCH`、`DELETE` |
| 排除路径 | `SKIP_PATHS`：`/api/v1/system/login/`、`/api/v1/system/token/refresh/`（避免记录明文密码环境） |
| 请求体 | JSON 时脱敏 `SENSITIVE_FIELDS`（password、token 等），再截断至约 4k |
| 幂等 | 记录 `Idempotency-Key` 与是否重放（来自 `IdempotencyMiddleware`） |

**顺序**：`IdempotencyMiddleware` 先于业务，`AuditLogMiddleware` 在 `MIDDLEWARE` 链后部（见 `base.py`），响应后写入。

## 2. 业务事件审计

**文件**：`backend/core/audit.py` → `log_business_event`

写入同一 `AuditLog` 表，`method` 为 **`BIZ_EVENT`**，`body` 为 JSON 字符串，内含 `kind: business_event`、`module`、`action`、`entity`、`entity_id`、`payload`。

**示例调用**：`backend/apps/reports/workflow.py` 在报告提交审核、审核、批准等节点调用。

## 3. 管理端查询

**页面**：`/system/audit-logs`  
**组件**：`frontend/src/views/system/AuditLogList.vue`  
**API**：`GET /api/v1/system/audit-logs/`（`AuditLogViewSet`，`lims_module = 'system'`）

**过滤器**（`AuditLogFilter`）：

- `start_date` / `end_date`：按日期（含全天）
- `user`、`method`、`path`、`username`、`status_code`
- `idempotency_key`、`is_idempotent_replay`
- `keyword`：请求体模糊搜

## 4. 运维操作流程（文字图）

```
收到安全工单：某账号异常操作
    ↓
打开 操作日志，筛选 username / user id
    ↓
缩小时间范围 + path 关键字（如 /users/ /kickout-sessions/）
    ↓
若需请求体细节：注意脱敏字段显示为 ***
    ↓
对业务链路：筛选 method=BIZ_EVENT 或 body 含 "business_event"
```

## 5. 数据库字段（摘要）

见 `backend/apps/system/models.py` → `AuditLog`：`user`、`username`、`method`、`path`、`body`、`ip_address`、`status_code`、`idempotency_key`、`is_idempotent_replay`、`timestamp`。

**索引**：`timestamp`、`user`、`idempotency_key`。

## 6. 风险与归档

| 风险 | 建议 |
|------|------|
| 表体积无限增长 | 按月归档到冷存储；或分区表 |
| 日志写入失败 | 中间件捕获异常不阻断主流程；需监控 warning |
| 合规要求完整请求 | 当前 body 截断+脱敏，敏感业务需额外专用审计表 |

## 7. 回滚

审计为**追加写**，一般无「业务回滚」；误删数据只能从 **DB 备份** 恢复。

## 8. 相关路径

- `backend/core/middleware.py`（`AuditLogMiddleware`、`SENSITIVE_FIELDS`、`SKIP_PATHS`）
- `backend/core/audit.py`
- `backend/apps/system/views.py`（`AuditLogViewSet`）
