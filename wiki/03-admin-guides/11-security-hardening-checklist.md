# 安全加固检查清单

本文面向生产部署，结合本仓库实现列出可落地的检查项；**勾选后请在贵方制度中归档证据**。

## 1. 身份与访问

| 项 | 说明 | 代码/配置参考 |
|----|------|----------------|
| JWT 与密钥 | `SECRET_KEY` 强随机；定期轮换 | `base.py` |
| 会话失效 | `session_version` + `sv` claim | `tokens.py`、`authentication.py` |
| 超级用户数量 | 最小化 | Django Admin + 业务用户分离 |
| 权限最小化 | 角色只分配必要 Permission | `Permission` 表 |

## 2. 传输与网关

| 项 | 说明 |
|----|------|
| HTTPS | 全站 TLS，Cookie（若使用）标记 Secure |
| CORS | `CORS_ALLOWED_ORIGINS` 白名单，禁用 `*` 对生产 |
| 反向代理 | 正确传递 `X-Forwarded-For` 以便 IP 限流与审计 |

## 3. 认证与防刷

| 项 | 说明 | 参考 |
|----|------|------|
| 登录失败锁定 | Redis + 阈值 | `LOGIN_FAILURE_*` |
| 改密限流 | `password_change` scope | `PasswordChangeThrottle` |
| 密码强度 | Django validators + 8 位重置 | `AUTH_PASSWORD_VALIDATORS`、`views.py` |

## 4. 审计与完整性

| 项 | 说明 |
|----|------|
| HTTP 审计 | 敏感字段脱敏 | `AuditLogMiddleware` |
| 幂等键 | 重复提交保护 | `IdempotencyMiddleware` |
| 业务审计 | 关键状态机打点 | `core/audit.py` |

## 5. 依赖与构建

| 项 | 说明 |
|----|------|
| 依赖漏洞扫描 | pip/npm audit 或 SCA 工具 |
| 镜像 | 非 root 运行、固定基础镜像版本 |

## 6. 数据与存储

| 项 | 说明 |
|----|------|
| PostgreSQL | 独立账号、最小权限、网络隔离 |
| MinIO | 访问密钥轮换、桶策略、私有读 |
| 备份加密 | 离线备份与介质加密（见 09） |

## 7. 风险接受与回滚

- 未实施项应记录在「风险登记册」。
- 发生安全事件时：**先踢出可疑账号**（`kickout-sessions`）、**强制改密**、**从审计反查**。

## 8. 相关路径

- `backend/limis/settings/base.py`
- `backend/core/middleware.py`
- `backend/apps/system/views.py`、`services.py`
