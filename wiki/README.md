# LIMIS 知识库（Wiki）首页

欢迎来到 **LIMIS（实验室信息管理系统）** 官方知识库。本文档集面向最终用户、业务管理员、运维人员与研发人员，采用分层目录与交叉引用，便于按角色、场景与问题类型快速定位。

> **范围说明**：本仓库 Wiki 以当前代码库行为与约定为准；若与现场定制部署不一致，请以环境内的《部署说明》或变更单为准，并建议将差异回写至本 Wiki（见 [维护约定](#维护约定)）。

---

## 文档统计与完整目录

**共计正文文档 42 篇**（不含本 `README.md` 首页），按 9 个一级分类组织如下。

| 分类 | 目录 | 篇数 | 内容侧重 |
|------|------|------|----------|
| 入门与概念 | [`01-getting-started/`](01-getting-started/) | **5** | 系统概览、术语、环境、首次登录、界面导航 |
| 架构 | [`02-architecture/`](02-architecture/) | **5** | 前后端架构、领域模型、集成边界 |
| 研发 | [`03-development/`](03-development/) | **6** | 本地开发、规范、测试、Git、调试、贡献 |
| 部署 | [`04-deployment/`](04-deployment/) | **5** | 部署形态、配置、代理、备份恢复 |
| API 与对接 | [`05-api-and-integration/`](05-api-and-integration/) | **4** | JWT、REST 约定、错误码、前端请求信封 |
| 用户功能指南 | [`06-user-guide/`](06-user-guide/) | **6** | 委托/检测/报告/质量/资源/系统管理界面 |
| 常见问题（FAQ） | [`07-faq/`](07-faq/) | **3** | 登录与会话、业务流程、运维 |
| 安全与合规 | [`08-security-compliance/`](08-security-compliance/) | **4** | 授权模型、审计、数据安全、标准元数据爬取 |
| 运维专题 | [`09-operations-maintenance/`](09-operations-maintenance/) | **4** | 巡检清单、日志监控、数据库、事件响应 |

**合计**：5 + 5 + 6 + 5 + 4 + 6 + 3 + 4 + 4 = **42**。

### 完整文档列表（含相对链接）

#### `01-getting-started/`（5）

1. [LIMIS 系统概览](01-getting-started/01-limis-overview.md)
2. [术语与缩写表](01-getting-started/02-terminology-glossary.md)
3. [运行环境与浏览器要求](01-getting-started/03-environment-requirements.md)
4. [首次登录与个人资料](01-getting-started/04-first-login-and-profile.md)
5. [界面导航与菜单地图](01-getting-started/05-ui-navigation-map.md)

#### `02-architecture/`（5）

6. [系统架构总览](02-architecture/01-system-architecture-overview.md)
7. [后端技术栈（Django / DRF）](02-architecture/02-backend-django-stack.md)
8. [前端技术栈（Vue）](02-architecture/03-frontend-vue-stack.md)
9. [核心业务对象与数据域](02-architecture/04-domain-model-overview.md)
10. [外部系统集成点](02-architecture/05-integration-points.md)

#### `03-development/`（6）

11. [本地开发环境搭建](03-development/01-local-development-setup.md)
12. [编码规范与工程约定](03-development/02-coding-style-and-conventions.md)
13. [测试策略与执行](03-development/03-testing-and-quality.md)
14. [Git 分支与协作流程](03-development/04-git-workflow.md)
15. [调试手册（前后端）](03-development/05-debugging-playbook.md)
16. [贡献指南](03-development/06-contributing-guide.md)

#### `04-deployment/`（5）

17. [部署总览](04-deployment/01-deployment-overview.md)
18. [运行时与进程模型](04-deployment/02-runtime-and-process.md)
19. [配置项与密钥管理](04-deployment/03-configuration-and-secrets.md)
20. [反向代理与 TLS](04-deployment/04-reverse-proxy-and-tls.md)
21. [备份与恢复](04-deployment/05-backup-and-recovery.md)

#### `05-api-and-integration/`（4）

22. [认证与 JWT（含会话版本）](05-api-and-integration/01-authentication-and-jwt.md)
23. [REST API 约定](05-api-and-integration/02-rest-conventions.md)
24. [错误响应与业务码](05-api-and-integration/03-error-response-and-codes.md)
25. [前端请求信封与字段兼容](05-api-and-integration/04-frontend-api-envelope.md)

#### `06-user-guide/`（6）

26. [工程项目与委托管理](06-user-guide/01-entrustment-and-projects.md)
27. [样品、检测任务与结果](06-user-guide/02-sampling-and-testing.md)
28. [报告编制与签发流程](06-user-guide/03-reports-workflow.md)
29. [质量体系相关模块](06-user-guide/04-quality-system-modules.md)
30. [仪器设备、耗材与环境监控](06-user-guide/05-resources-equipment-environment.md)
31. [系统管理（用户、角色、日志）](06-user-guide/06-system-administration-ui.md)

#### `07-faq/`（3）

32. [登录、权限与会话 FAQ](07-faq/01-login-permission-and-session-faq.md)
33. [业务流程 FAQ](07-faq/02-business-process-faq.md)
34. [运维 FAQ](07-faq/03-operation-and-maintenance-faq.md)

#### `08-security-compliance/`（4）

35. [授权模型与模块权限](08-security-compliance/01-authorization-model.md)
36. [审计与操作日志](08-security-compliance/02-audit-trail.md)
37. [数据安全与敏感信息](08-security-compliance/03-data-security.md)
38. [标准规范元数据与工标网爬取说明](08-security-compliance/04-standards-crawl-metadata.md)

#### `09-operations-maintenance/`（4）

39. [例行巡检清单](09-operations-maintenance/01-routine-inspection-checklist.md)
40. [日志与监控](09-operations-maintenance/02-logs-and-monitoring.md)
41. [数据库运维](09-operations-maintenance/03-database-operations.md)
42. [事件响应与通报](09-operations-maintenance/04-incident-handling.md)

---

## 与既有 Wiki 章节的对应关系（迁移说明）

仓库中另有一套按主题渐进补充的文档（如 `01-system-overview/`、`02-user-guides/`、`03-admin-guides/`、`05-api-docs/`）。**两套目录互为补充**：本页列出的 **42 篇** 为结构化主干；阅读时可对照下表跳转，避免内容重复维护时产生冲突。

| 新结构（本索引） | 既有文档（参考） |
|------------------|------------------|
| [01-limis-overview](01-getting-started/01-limis-overview.md) | [产品定位](01-system-overview/01-product-positioning.md) |
| [02-architecture 总览](02-architecture/01-system-architecture-overview.md) | [架构与技术栈](01-system-overview/02-architecture-and-tech-stack.md) |
| [06 用户指南 · 委托/项目](06-user-guide/01-entrustment-and-projects.md) | [项目管理用户指南](02-user-guides/02-project-management-user-guide.md)、[委托管理](02-user-guides/03-commission-management-user-guide.md) |
| [07-faq 登录权限](07-faq/01-login-permission-and-session-faq.md) | [权限排错](03-admin-guides/03-permission-model-and-troubleshooting.md)、[会话安全](03-admin-guides/04-session-security-and-kickout.md) |
| [05-api 认证](05-api-and-integration/01-authentication-and-jwt.md) | [认证与 Token API](05-api-docs/02-auth-and-token-apis.md) |
| [05-api 信封](05-api-and-integration/04-frontend-api-envelope.md) | [API 约定与信封](05-api-docs/01-api-conventions-and-envelope.md) |

---

## 按角色阅读路径

| 角色 | 建议路径 | 说明 |
|------|----------|------|
| **新入职检测/报告人员** | [入门 1～5](01-getting-started/) → [用户指南 26～29](06-user-guide/) → [业务流程 FAQ](07-faq/02-business-process-faq.md) | 先建立全局概念，再跟业务主链路，遇到卡点查 FAQ。 |
| **质量负责人 / 体系管理员** | [质量体系模块](06-user-guide/04-quality-system-modules.md) → [授权模型](08-security-compliance/01-authorization-model.md) → [审计日志](08-security-compliance/02-audit-trail.md) → [标准爬取](08-security-compliance/04-standards-crawl-metadata.md) | 覆盖标准、模板、内审与管理评审相关能力及合规留痕。 |
| **系统 / 实验室管理员** | [系统管理界面](06-user-guide/06-system-administration-ui.md) → [登录权限 FAQ](07-faq/01-login-permission-and-session-faq.md) → [部署与配置 17～21](04-deployment/) → [巡检清单](09-operations-maintenance/01-routine-inspection-checklist.md) | 用户角色、日常巡检与变更窗口。 |
| **运维 / 基础设施** | [部署总览](04-deployment/01-deployment-overview.md) → [运行时](04-deployment/02-runtime-and-process.md) → [日志与监控](09-operations-maintenance/02-logs-and-monitoring.md) → [运维 FAQ](07-faq/03-operation-and-maintenance-faq.md) → [事件响应](09-operations-maintenance/04-incident-handling.md) | 上线、排障、容量与应急。 |
| **后端研发** | [架构 6～10](02-architecture/) → [认证 JWT](05-api-and-integration/01-authentication-and-jwt.md) → [REST 约定](05-api-and-integration/02-rest-conventions.md) → [本地开发](03-development/01-local-development-setup.md) | API 与领域扩展的入口。 |
| **前端研发** | [前端栈](02-architecture/03-frontend-vue-stack.md) → [前端请求信封](05-api-and-integration/04-frontend-api-envelope.md) → [界面导航](01-getting-started/05-ui-navigation-map.md) → [调试手册](03-development/05-debugging-playbook.md) | 路由权限、接口信封与字段兼容。 |

---

## 按场景阅读路径

| 场景 | 入口文档 | 延伸阅读 |
|------|----------|----------|
| 首次登录后菜单空白或 403 | [登录权限 FAQ](07-faq/01-login-permission-and-session-faq.md) | [授权模型](08-security-compliance/01-authorization-model.md)、[系统管理](06-user-guide/06-system-administration-ui.md) |
| 委托—样品—检测—报告主链路不熟 | [工程项目与委托](06-user-guide/01-entrustment-and-projects.md) | [业务流程 FAQ](07-faq/02-business-process-faq.md)、[样品与检测](06-user-guide/02-sampling-and-testing.md)、[报告流程](06-user-guide/03-reports-workflow.md) |
| Token 过期、被踢下线、多端登录 | [登录权限 FAQ § 会话](07-faq/01-login-permission-and-session-faq.md) | [认证 JWT](05-api-and-integration/01-authentication-and-jwt.md) |
| 工标网爬取回填字段不全 | [标准爬取说明](08-security-compliance/04-standards-crawl-metadata.md) | [前端信封](05-api-and-integration/04-frontend-api-envelope.md) |
| 生产环境升级与回滚 | [部署总览](04-deployment/01-deployment-overview.md) | [备份恢复](04-deployment/05-backup-and-recovery.md)、[运维 FAQ](07-faq/03-operation-and-maintenance-faq.md) |
| 接口联调异常、HTTP 200 但业务失败 | [错误响应与业务码](05-api-and-integration/03-error-response-and-codes.md) | [REST 约定](05-api-and-integration/02-rest-conventions.md) |

---

## 按问题类型阅读路径

| 问题类型 | 优先查阅 |
|----------|----------|
| **账号 / 密码 / 锁定 / 会话失效** | [登录权限 FAQ](07-faq/01-login-permission-and-session-faq.md) → [认证 JWT](05-api-and-integration/01-authentication-and-jwt.md) |
| **角色、模块权限、菜单不可见** | [授权模型](08-security-compliance/01-authorization-model.md) → [登录权限 FAQ](07-faq/01-login-permission-and-session-faq.md) |
| **业务状态、单据流转、谁能改** | [业务流程 FAQ](07-faq/02-business-process-faq.md) → 对应 [用户指南](06-user-guide/) 章节 |
| **性能、宕机、日志、备份** | [运维 FAQ](07-faq/03-operation-and-maintenance-faq.md) → [巡检清单](09-operations-maintenance/01-routine-inspection-checklist.md) → [日志与监控](09-operations-maintenance/02-logs-and-monitoring.md) |
| **合规、审计、留痕** | [审计与操作日志](08-security-compliance/02-audit-trail.md) → [数据安全](08-security-compliance/03-data-security.md) |

---

## 新手 1 小时路径（建议）

目标：能在系统中完成一次「从菜单找到模块 → 理解主业务名词 → 知道遇到问题去哪查」。

| 时段 | 动作 | 文档 |
|------|------|------|
| 0～10 分钟 | 了解系统边界与模块划分 | [LIMIS 系统概览](01-getting-started/01-limis-overview.md)、[界面导航与菜单地图](01-getting-started/05-ui-navigation-map.md) |
| 10～25 分钟 | 弄清委托—样品—检测—报告主路径 | [工程项目与委托](06-user-guide/01-entrustment-and-projects.md)、[样品、检测任务与结果](06-user-guide/02-sampling-and-testing.md)（可跳读小节） |
| 25～40 分钟 | 登录、权限、会话常见现象 | [登录、权限与会话 FAQ](07-faq/01-login-permission-and-session-faq.md)（至少读完「会话与 JWT」与「菜单与权限」两节） |
| 40～55 分钟 | 质量体系与报告相关入口 | [质量体系相关模块](06-user-guide/04-quality-system-modules.md) 或 [报告编制与签发](06-user-guide/03-reports-workflow.md)（二选一深读） |
| 55～60 分钟 | 收藏首页与 FAQ，建立查找习惯 | 回到本 `README.md`，将 [业务流程 FAQ](07-faq/02-business-process-faq.md) 加入书签 |

若岗位偏管理或运维，可将最后 20 分钟替换为 [系统管理界面](06-user-guide/06-system-administration-ui.md) + [例行巡检清单](09-operations-maintenance/01-routine-inspection-checklist.md) 扫读。

---

## 管理员日常巡检路径（建议）

面向：**系统管理员、运维值班、实验室负责人（兼管系统）**。每日 10～15 分钟；发版日或故障后按扩展项执行。

**每日（10～15 分钟）**

1. [例行巡检清单](09-operations-maintenance/01-routine-inspection-checklist.md) 中的「快速项」：应用可用性、错误日志摘要、磁盘与数据库连通性。
2. 抽查 [操作日志](06-user-guide/06-system-administration-ui.md) 中异常删除或批量导出行为（与 [审计](08-security-compliance/02-audit-trail.md) 要求一致时）。
3. 若有用户报「突然全部下线」或「权限变了」，对照 [登录权限 FAQ](07-faq/01-login-permission-and-session-faq.md) 中的会话与踢出条目。

**每周**

- 备份任务成功性确认（见 [备份与恢复](04-deployment/05-backup-and-recovery.md)）。
- 依赖与安全补丁窗口评估（与研发/运维负责人对齐）。

**每月**

- 角色与账号复核（离职转岗、外包账号）。
- 回顾 [运维 FAQ](07-faq/03-operation-and-maintenance-faq.md) 是否需增补现场特例。

**扩展（发版 / 故障后）**

- [事件响应与通报](09-operations-maintenance/04-incident-handling.md)
- [数据库运维](09-operations-maintenance/03-database-operations.md) 中的慢查询与连接数检查

---

## 维护约定

### 文档更新频率

| 文档类型 | 最低更新频率 | 触发条件 |
|----------|----------------|----------|
| 本 `README.md` 目录索引 | 随文档增删改即时 | 新增/重命名/删除任意正文文档 |
| FAQ（`07-faq/`） | 每季度复盘，或每 10 条同类工单 | 重复咨询 ≥3 次即评估入库 |
| 部署与运维（`04-deployment/`、`09-operations-maintenance/`） | 每次发版或基础设施变更后 | 配置项、端口、备份策略变化 |
| API 与前端信封（`05-api-and-integration/`） | 每次公共 API 契约变更 | 认证方式、统一响应结构、字段命名变更 |
| 用户指南（`06-user-guide/`） | 每个大版本界面或流程变更后 | 菜单重组、状态机变更 |

### 责任角色（RACI 简述）

| 活动 | 负责（R） | 审批（A） | 咨询（C） | 知会（I） |
|------|-----------|-----------|-----------|-----------|
| 目录结构与交叉链接正确 | 研发负责人或指定 Wiki 编辑 | 项目经理或产品负责人 | 运维与测试代表 | 全团队 |
| FAQ 条目技术准确性 | 对应模块开发者 | 研发负责人 | 技术支持 | 用户代表 |
| 运维类步骤可执行性 | 运维负责人 | 安全/合规接口人（如涉及） | 研发 | 管理层（重大变更） |

现场若无明确岗位，可由 **项目经理指定单一 Wiki Owner** 代行「负责」列职责。

### 变更记录模板

在文档 **底部** 或项目变更单中记录；重大变更建议同时在版本控制系统提交信息中引用 Issue/工单号。

```text
## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| YYYY-MM-DD | 1.0 | 姓名 | 初版 |
| YYYY-MM-DD | 1.1 | 姓名 | 增补 XXX 章节；修正与 YYY 文档的链接 |
```

单篇文档内可使用简化版：

```text
> **修订**：2026-04-01，某某：补充 Z 场景说明。
```

### 关于 `SYSTEM_USER_MANUAL.md`

仓库中的 **`wiki/SYSTEM_USER_MANUAL.md`** 为 **全角色长篇操作手册**（与本文档集的 42 篇 **并列互补**）。需要「单文件通读」全流程时可优先阅读该手册；需要 **按角色/场景检索** 时使用本 `README.md` 索引与分类目录。若某处表述冲突，以 **当前代码与现场部署说明** 为准，并建议更新其中一侧后同步另一侧的交叉链接。

---

## 反馈与改进

若发现文档错误或希望补充场景，请通过团队约定的工单渠道或 Merge Request 提交；提交时请注明「受影响章节」「期望行为」与「现场环境差异（若有）」，便于 [变更记录模板](#变更记录模板) 追溯。

返回：[本页顶部](#limis-知识库wiki首页)
