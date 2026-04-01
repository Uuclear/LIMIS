# 反向代理与 TLS

- Nginx 将 `/api` 转发至 upstream，注意 **超时** 与 **请求体大小**。
- 传递 `X-Forwarded-For`、`X-Forwarded-Proto` 以便 Django 识别 HTTPS 与客户端 IP。
- TLS 证书自动续期（Let's Encrypt / 机构证书）。

与 [运维 FAQ](../07-faq/03-operation-and-maintenance-faq.md) 联动。

---

## 生产 HTTPS 检查清单（简要）

以下为 **文档级** 核对项；自动化与具体证书路径由现场 Nginx/网关决定。

| 项 | 说明 |
|----|------|
| 环境变量 `USE_HTTPS` | 使用 `limis.settings.prod` 时设为 **`true`**（或 `1`/`yes`），以开启 HSTS、Cookie Secure、`SECURE_SSL_REDIRECT` 等（见 `backend/limis/settings/prod.py`）。 |
| 反向代理头 | 终止 TLS 的一端向 Django 转发 **`X-Forwarded-Proto: https`**，与 `SECURE_PROXY_SSL_HEADER` 一致；勿丢 `X-Forwarded-For`。 |
| 证书路径 | Nginx 示例：`ssl_certificate`、`ssl_certificate_key`（或 acme/Let’s Encrypt 目录）；容器外路径按实际挂载填写。 |
| `ALLOWED_HOSTS` / `CORS_ALLOWED_ORIGINS` | 生产填 **HTTPS** 域名；CORS 源与前端部署地址一致。 |
| `REPORT_VERIFICATION_URL` | 报告二维码防伪链接前缀；**生产须为 HTTPS**，且与前端路由 `/verify/report/:id` 一致，例如 `https://<你的域名>/verify/report/`（末尾斜杠与 `backend/limis/settings/base.py` 默认风格一致）。 |

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.1 | Wiki | 补充 HTTPS 检查清单与 `REPORT_VERIFICATION_URL` |
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
