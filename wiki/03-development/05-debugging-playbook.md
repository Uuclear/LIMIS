# 调试手册（前后端）

## 后端

- `runserver` + 断点；或 `LOGGING` 提高 `django.request` 级别。
- DRF 权限拒绝：检查 `lims_module`、用户 `has_lims_permission`。

## 前端

- Vue DevTools：路由、Pinia 状态。
- 网络面板：401/403、`code` 解包、`data` 是否嵌套。

## 典型问题

- **爬取回填空字段**：信封与 `unwrapCrawlPayload`（见 [前端信封](../05-api-and-integration/04-frontend-api-envelope.md)）。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
