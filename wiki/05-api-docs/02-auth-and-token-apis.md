# 认证与令牌 API

LIMIS 使用 **djangorestframework-simplejwt**，并扩展 **会话版本号**（`session_version`）：用户被踢下线或管理员重置会话后，旧 access/refresh 令牌失效。配置见 `backend/limis/settings/base.py` 中 `REST_FRAMEWORK`、`SIMPLE_JWT` 与 `apps.system.authentication.SessionVersionJWTAuthentication`。

## 令牌声明与存储

- Access token 使用自定义类 `apps.system.tokens.SessionVersionAccessToken`，内含 **`sv`**（会话版本）声明，须与数据库用户 `session_version` 一致。
- Refresh token 使用 `SessionVersionRefreshToken`；刷新时同样校验 `sv`（`apps.system.jwt_serializers.SessionVersionTokenRefreshSerializer`）。
- 前端将 **access** 存 `localStorage` 键 `lims_access_token`，**refresh** 存 `lims_refresh_token`（`frontend/src/utils/auth.ts`），请求头：`Authorization: Bearer <access>`。

默认寿命（可在 `SIMPLE_JWT` 中调整）：

- Access：约 **2 小时**
- Refresh：约 **7 天**，且启用 **轮换 + 黑名单**（`ROTATE_REFRESH_TOKENS` / `BLACKLIST_AFTER_ROTATION`）

---

## POST `/api/v1/system/login/`

**权限**：匿名可访问。

**请求体：**

```json
{
  "username": "demo",
  "password": "********"
}
```

**成功响应（HTTP 200）——注意：非 `{ code, message, data }` 信封**，与 SimpleJWT 常见教程一致，便于前端直接取令牌：

```json
{
  "access": "<jwt-access>",
  "refresh": "<jwt-refresh>",
  "user": {
    "id": 1,
    "username": "demo",
    "first_name": "",
    "last_name": "",
    "real_name": "",
    "email": "",
    "phone": "",
    "department": "",
    "title": "",
    "avatar": null,
    "is_active": true,
    "roles": [
      { "id": 1, "name": "管理员", "code": "admin" }
    ],
    "date_joined": "2026-01-01T08:00:00+08:00",
    "last_login": "2026-04-01T10:00:00+08:00"
  }
}
```

登录失败时走 DRF 异常处理，可能为带 `code` / `message` 的错误体，或 `detail` 字段，以实际响应为准（含登录失败锁定策略时由 `apps.system.services` 抛出）。

---

## POST `/api/v1/system/token/refresh/`

**权限**：匿名（凭 refresh 换 access）。

**请求体（SimpleJWT 默认）：**

```json
{
  "refresh": "<jwt-refresh>"
}
```

**成功响应（HTTP 200）示例：**

```json
{
  "access": "<new-access-token>",
  "refresh": "<new-refresh-if-rotated>"
}
```

若 `sv` 与数据库不一致（例如管理员对该用户执行了「踢出会话」），刷新失败，返回 401 及 JWT 相关 `detail`/`code`（具体以 `rest_framework_simplejwt` 与异常处理器输出为准）。

---

## POST `/api/v1/system/logout/`

**权限**：需登录（`IsAuthenticated`）。

**请求体（可选）：**

```json
{
  "refresh": "<jwt-refresh>"
}
```

若提供 `refresh`，服务端尝试将 refresh 列入黑名单；失败时仍返回成功语义，避免客户端卡住。

**成功响应示例：**

```json
{
  "detail": "已退出登录"
}
```

---

## GET `/api/v1/system/me/`

**权限**：需登录。

**成功响应（HTTP 200）——裸用户对象 + 权限列表**，非统一信封：

```json
{
  "id": 1,
  "username": "demo",
  "first_name": "",
  "last_name": "",
  "real_name": "",
  "email": "",
  "phone": "",
  "department": "",
  "title": "",
  "avatar": null,
  "is_active": true,
  "roles": [ { "id": 1, "name": "管理员", "code": "admin" } ],
  "date_joined": "2026-01-01T08:00:00+08:00",
  "last_login": "2026-04-01T10:00:00+08:00",
  "permissions": [
    "project:view",
    "commission:create"
  ]
}
```

`permissions` 由 `apps.system.services.get_user_permissions` 生成，供前端路由与按钮级鉴权使用。

---

## PUT `/api/v1/system/password/change/`

**权限**：需登录。

**请求体示例：**

```json
{
  "old_password": "********",
  "new_password": "********"
}
```

**成功示例：**

```json
{
  "detail": "密码修改成功"
}
```

该接口配置了 DRF 限流 scope `password_change`（速率见环境变量 `PASSWORD_CHANGE_THROTTLE_RATE`，默认 `5/hour`）。触发限流时 HTTP 429。

---

## 认证失败示例（401）

当 access 过期、`sv` 不匹配或令牌无效时，请求业务接口可能返回：

```json
{
  "detail": "Given token not valid for any token type"
}
```

或经异常处理器包装后的：

```json
{
  "code": 401,
  "message": "..."
}
```

前端在 `request.ts` 中对 `code === 401` 会清理本地 token 并跳转登录页。

---

## 路由定义参考

`backend/apps/system/urls.py`：

- `login/` → `LoginView`
- `logout/` → `LogoutView`
- `me/` → `CurrentUserView`
- `password/change/` → `PasswordChangeView`
- `token/refresh/` → `TokenRefreshView`（simplejwt）

---

## 安全与运维提示

1. **生产环境**务必使用 HTTPS，并妥善配置 `SECRET_KEY`、JWT 寿命与 CORS。
2. **踢出会话**：用户管理中有 `kickout-sessions` 类操作会递增 `session_version`，已签发令牌全部失效。
3. **审计**：登录与刷新路径在审计中间件中跳过记录请求体（`SKIP_PATHS`），避免敏感信息落库。
