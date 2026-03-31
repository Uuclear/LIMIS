# REST API 约定

- **资源路径**：复数名词、嵌套表示关联（以具体 ViewSet 为准）。
- **方法**：GET 查询、POST 创建、PATCH 部分更新、DELETE 删除。
- **分页**：DRF 标准分页参数（`page`、`page_size` 等，以配置为准）。
- **权限**：`LimsModulePermission` + `lims_module`。

错误与信封：[错误响应](03-error-response-and-codes.md)

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
