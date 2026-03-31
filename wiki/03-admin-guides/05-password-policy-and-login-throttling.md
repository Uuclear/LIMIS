# 密码策略与登录限流

本文覆盖：**Django 内置密码校验**、**登录失败锁定**、**修改密码接口限流**，并给出配置项、风险与回滚建议。

## 1. Django 密码校验器

**位置**：`backend/limis/settings/base.py` → `AUTH_PASSWORD_VALIDATORS`

默认包含：

- 与用户属性相似性
- 最小长度（由 Django 内置 MinimumLengthValidator 处理）
- 常见密码、纯数字等

**管理员重置密码**：`UserViewSet.reset_password` 要求 **至少 8 位**（`backend/apps/system/views.py`），与 Django 校验器并行生效。

**用户自助改密**：`PasswordChangeView` + `PasswordChangeSerializer`（`backend/apps/system/views.py`）。

## 2. 登录失败锁定（Redis 缓存）

**实现**：`backend/apps/system/services.py`

| 函数 | 作用 |
|------|------|
| `check_login_lockout` | 登录前检查是否处于锁定 |
| `record_login_failure` | 失败计数；达阈值则写锁定键 |
| `clear_login_attempts` | 成功登录后清零 |

**键设计**（概念）：

- `login:fail:{digest}`：失败次数，带滑动窗口
- `login:lock:{digest}`：锁定标记，TTL = 锁定时长

`digest` 由 **用户名 + 客户端 IP** 哈希（`get_client_ip` 支持 `X-Forwarded-For` 首段）。

## 3. 配置项（环境变量 / settings）

| 变量 | 默认值（base.py） | 含义 |
|------|-------------------|------|
| `LOGIN_FAILURE_MAX_ATTEMPTS` | `5` | 窗口内允许失败次数；**`0` 关闭整个锁定功能** |
| `LOGIN_FAILURE_LOCKOUT_SECONDS` | `300` | 锁定时长（秒） |
| `LOGIN_FAILURE_WINDOW_SECONDS` | `900` | 统计窗口（秒） |
| `PASSWORD_CHANGE_THROTTLE_RATE` | `5/hour` | DRF 限流 scope `password_change` |

**REST_FRAMEWORK** 中注册：`DEFAULT_THROTTLE_RATES['password_change']`（`base.py`）。

**应用位置**：`PasswordChangeThrottle` → `backend/apps/system/throttles.py`（需在 `PasswordChangeView.throttle_classes` 引用，见 `views.py`）。

## 4. 登录接口行为

**端点**：`POST /api/v1/system/login/`（`LoginView`）

**流程**：

```
LoginSerializer 校验
    ↓
check_login_lockout
    ↓
authenticate
    ├─ 失败 → record_login_failure → AuthenticationFailed
    └─ 成功 → clear_login_attempts → bump_session_version → 签发 JWT
```

## 5. 风险与回滚

| 风险 | 场景 | 处理 |
|------|------|------|
| NAT 下误锁大量用户 | 同出口 IP | 调高窗口/阈值；或前置独立认证（VPN） |
| Redis 宕机 | 缓存操作异常 | 监控 Redis；Django cache 后端需可用 |
| 关闭锁定 `MAX_ATTEMPTS=0` | 暴力破解 | 仅内网或配合 WAF/网关限流 |

**回滚配置**：恢复上一版环境变量并重启 worker；**无需**改数据库。

**紧急解锁**（运维）：删除 Redis 中对应 `login:lock:*` / `login:fail:*`（键规则见 `_fail_key`/`_lock_key`），或等待 TTL 过期。

## 6. 相关代码路径

- `backend/limis/settings/base.py`
- `backend/apps/system/services.py`
- `backend/apps/system/throttles.py`
- `backend/apps/system/views.py`（`LoginView`、`PasswordChangeView`）
