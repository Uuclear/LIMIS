# 标准规范元数据与工标网爬取说明

从工标网等平台 **爬取标准元数据** 时，应保证：

1. **后端解析** 与演示脚本 `scripts/csres_fetch_demo.py` / `fetch_csres_metadata` 同源逻辑。
2. **前端** 正确解包 `{ code, message, data }`，兼容 `code` 为字符串；对多层 `data` 使用 `unwrapCrawlPayload`。
3. **字段名** 同时兼容 snake_case 与 camelCase（如 `standard_no` / `standardNo`）。

详见工作区规则「工标网爬取」与 [前端信封](../05-api-and-integration/04-frontend-api-envelope.md)。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
