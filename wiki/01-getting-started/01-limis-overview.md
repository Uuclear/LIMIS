# LIMIS 系统概览

LIMIS（Laboratory Information Management Information System）面向检测实验室，覆盖 **业务管理**（工程、委托、样品）、**检测管理**（任务、原始记录、结果）、**报告**、**资源**（人员、设备、耗材）、**质量体系**（标准、模板、资质、内审等）与 **系统管理**。

## 产品定位与价值

- **过程可追溯**：从委托到报告的数据链与操作日志支撑质量与合规要求。
- **角色分工**：通过模块权限与角色绑定适配实验室岗位。
- **可扩展**：后端 Django REST Framework，前端 Vue，便于集成与定制。

延伸阅读：[产品定位](../01-system-overview/01-product-positioning.md) · [架构总览](../02-architecture/01-system-architecture-overview.md) · [术语表](02-terminology-glossary.md)

## 功能域（与菜单对应）

| 域 | 说明 |
|----|------|
| 业务管理 | 工程项目、委托、样品 |
| 检测管理 | 检测任务、原始记录、检测结果 |
| 报告管理 | 报告列表与编制签发 |
| 资源管理 | 设备、人员、耗材 |
| 监控管理 | 环境监控 |
| 质量体系 | 基础配置、标准、参数库、模板、资质、内审、管理评审、不符合项等 |
| 系统管理 | 用户、角色、操作日志 |

## 读者指引

- 新用户：[首次登录](04-first-login-and-profile.md) → [界面导航](05-ui-navigation-map.md)
- 管理员：[系统管理界面](../06-user-guide/06-system-administration-ui.md)
- 研发：[架构](../02-architecture/01-system-architecture-overview.md)

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
