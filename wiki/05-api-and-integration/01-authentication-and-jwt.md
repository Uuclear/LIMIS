# 认证与 JWT（含会话版本）

## 登录

登录成功后返回 **access** 与 **refresh** 令牌。Access 请求头：`Authorization: Bearer <access>`。

## session_version（`sv`）

Refresh 签发时在 payload 写入 `sv`，与 `User.session_version` 对齐。重新登录或 **踢出会话** 会递增数据库中的版本，使旧 Token 失效。

实现类：`SessionVersionJWTAuthentication`、`SessionVersionRefreshToken`（`apps/system/`）。

## 相关接口

细节与路径见 [既有：认证 API 文档](../05-api-docs/02-auth-and-token-apis.md) 与 [登录 FAQ](../07-faq/01-login-permission-and-session-faq.md)。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
