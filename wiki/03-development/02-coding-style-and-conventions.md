# 编码规范与工程约定

- **Python**：遵循 PEP 8，使用类型提示（`from __future__ import annotations`）。
- **Django**：业务逻辑优先放在 `services` 或 `selectors`，避免臃肿的 `views`。
- **TypeScript**：严格模式，公共 API 响应类型与后端字段对齐。
- **命名**：后端模块/权限用 **snake_case**；前端若混用 camelCase，API 层需兼容（见 [前端信封](../05-api-and-integration/04-frontend-api-envelope.md)）。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
