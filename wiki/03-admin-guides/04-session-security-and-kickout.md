# 会话安全与踢出（强制下线）

LIMIS 使用 **JWT** 访问接口，并通过 **会话版本号 `session_version`** 与 Token 中的声明 **`sv`** 对齐，实现「单点踢出」与「登录后旧 Token 作废」。

## 1. 机制说明

| 组件 | 路径 | 作用 |
|------|------|------|
| 用户字段 | `User.session_version` | `backend/apps/system/models.py` |
| Access Token | `SessionVersionAccessToken`，claim `sv` | `backend/apps/system/tokens.py` |
| 认证 | 校验 `sv` 与数据库一致 | `backend/apps/system/authentication.py` → `SessionVersionJWTAuthentication` |
| 刷新 | `SessionVersionTokenRefreshSerializer` | `backend/apps/system/jwt_serializers.py`（如存在） |
| 登录递增 | `bump_session_version` | `backend/apps/system/services.py` → `authenticate_user` |

**成功登录时**：会对 `session_version` **自增**（`bump_session_version`），使**该用户此前签发的 access/refresh** 在校验 `sv` 时失败（`InvalidToken` 会话已失效）。

**管理员踢出**：`POST /api/v1/system/users/{id}/kickout-sessions/` 对 `session_version` 做 `F('session_version') + 1`（`backend/apps/system/views.py` → `kickout_sessions`）。

## 2. 文字流程图：请求鉴权

```
客户端携带 Authorization: Bearer <access>
    ↓
SessionVersionJWTAuthentication 解析 JWT
    ↓
取出 claim sv
    ↓
与 User.session_version 比较
    ├─ 一致 → 通过
    └─ 不一致 → InvalidToken「会话已失效，请重新登录」
```

## 3. 文字流程图：踢出用户

```
[管理员] 用户管理 → 选择用户 → 踢出会话（kickout-sessions）
    ↓
DB: session_version += 1
    ↓
该用户所有设备上旧 JWT 立即失效
    ↓
用户需重新登录（新 Token 带新 sv）
```

## 4. 配置项（JWT）

| 配置 | 位置 | 默认值（参考） |
|------|------|----------------|
| `ACCESS_TOKEN_LIFETIME` | `backend/limis/settings/base.py` → `SIMPLE_JWT` | 2 小时 |
| `REFRESH_TOKEN_LIFETIME` | 同上 | 7 天 |
| `ROTATE_REFRESH_TOKENS` / `BLACKLIST_AFTER_ROTATION` | 同上 | True |

刷新端点：`POST /api/v1/system/token/refresh/`（`backend/apps/system/urls.py`）。

## 5. 前端行为

- Token 存于 `localStorage`（`frontend/src/utils/auth.ts`）。
- 401/刷新失败时 `userStore.resetState()` 清空并跳转登录（见 `stores/user.ts`）。

## 6. 风险与回滚

| 风险 | 说明 | 建议 |
|------|------|------|
| 误踢大量用户 | 若脚本错误批量 `session_version++` | 从备份恢复 `users` 表该字段；或通知全员重登 |
| sv 缺失 | 旧 Token 无 `sv` | 认证层会抛「缺少会话版本信息」→ 用户重新登录 |
| 时钟不同步 | 一般不影响 sv；影响 JWT exp | NTP 同步 |

**回滚**：通常不需要回滚代码；数据层可将某用户 `session_version` 设回旧值（**仅当**仍持有对应旧 JWT 且需紧急恢复会话时，安全风险高，一般禁止）。

## 7. 与审计的关系

踢出、登录、改密等操作应结合 `AuditLog` 与业务日志查看（`06-audit-log-operations.md`）。

## 8. 相关代码路径

- `backend/apps/system/authentication.py`
- `backend/apps/system/tokens.py`
- `backend/apps/system/services.py`（`authenticate_user`、`bump_session_version`）
- `backend/apps/system/views.py`（`kickout_sessions`、`LoginView`）
