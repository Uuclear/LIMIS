# 后端技术栈（Django / DRF）

- **框架**：Django、`django-rest-framework`。
- **认证**：`rest_framework_simplejwt`，自定义 `SessionVersionJWTAuthentication`。
- **权限**：`core.permissions.LimsModulePermission`，按模块与 HTTP 方法映射动作。
- **应用划分**：`apps.system`、`apps.projects`、`apps.commissions`、`apps.samples`、`apps.reports` 等（以仓库为准）。

开发入口：[本地开发](../03-development/01-local-development-setup.md) · [API 约定](../05-api-and-integration/02-rest-conventions.md)

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
