# 核心业务对象与数据域

以下为概念模型，便于跨模块沟通；具体字段以 `backend/apps/*/models.py` 为准。

| 对象 | 简述 |
|------|------|
| Project | 工程项目 |
| Commission / Entrustment | 委托 |
| Sample | 样品 |
| TestingTask | 检测任务 |
| RawRecord | 原始记录 |
| TestResult | 检测结果 |
| Report | 报告 |
| User / Role / Permission | 账户与授权 |

业务 FAQ：[业务流程 FAQ](../07-faq/02-business-process-faq.md)

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
