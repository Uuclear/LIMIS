# 反向代理与 TLS

- Nginx 将 `/api` 转发至 upstream，注意 **超时** 与 **请求体大小**。
- 传递 `X-Forwarded-For`、`X-Forwarded-Proto` 以便 Django 识别 HTTPS 与客户端 IP。
- TLS 证书自动续期（Let's Encrypt / 机构证书）。

与 [运维 FAQ](../07-faq/03-operation-and-maintenance-faq.md) 联动。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
