# 配置项与密钥管理

- **SECRET_KEY**、**JWT 签名密钥**：仅存于环境变量或密钥管理，**不入库 Git**。
- **DATABASE_URL**、**REDIS_URL**：分环境维护。
- **ALLOWED_HOSTS**、**CORS**：与域名一致，避免 `*` 与敏感接口并存。

轮换密钥影响 [会话](../07-faq/01-login-permission-and-session-faq.md)。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
