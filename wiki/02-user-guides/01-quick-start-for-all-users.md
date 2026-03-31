# 全用户快速入门

## 适用对象

- 首次登录系统的所有角色（检测员、样品管理员、报告编制人、质量负责人、系统管理员等）。
- 需要「最小路径」完成一次从登录到理解菜单结构的用户。

## 前置条件

- 已获得账号，或由管理员在 **`/system/users`** 创建用户并在 **`/system/roles`** 分配角色与权限。
- 浏览器可访问系统地址；推荐使用现代浏览器（Chromium / Firefox / Safari 新版本）。

## 页面入口

| 目的 | 路由 | 侧栏位置 |
|------|------|----------|
| 登录 | `/login` | — |
| 首页看板 | `/dashboard` | 首页 |
| 业务主线 | `/project`、`/entrustment`、`/sample` | 业务管理 |
| 检测与记录 | `/testing/tasks`、`/testing/records`、`/testing/results` | 检测管理 |
| 报告 | `/reports` | 报告管理 |
| 质量与配置 | `/quality/foundation` 等 | 质量体系 |
| 系统维护 | `/system/users`、`/system/roles`、`/system/audit-logs` | 系统管理 |

登录成功后默认进入 **`/dashboard`**。若直接访问无权限路由，系统提示「无权访问该页面」并返回首页。

## 字段说明

本页为通览，不涉及具体业务表字段；各模块字段见对应用户指南。

与登录相关的概念：

- **JWT**：登录成功后令牌存储于本地，后续请求自动带 `Authorization`。
- **权限码**：与路由 `meta.permission` 对应，如 `project:list`、`entrustment:create`；超级权限可能为 `*`。

## 标准操作步骤（SOP）

### 第一次登录

1. 打开 `/login`，输入用户名、密码。
2. 登录成功后进入 **`/dashboard`**，浏览本月委托、待检任务、本月报告、设备预警等卡片与图表。
3. 展开左侧菜单，确认自己可见的模块（由权限过滤，看不到即无权限）。

### 理解菜单与路由的对应关系

- **业务管理**：工程项目 → `/project`；委托 → `/entrustment`；样品 → `/sample`。
- **检测管理**：检测任务 → `/testing/tasks`；原始记录 → `/testing/records`；检测结果 → `/testing/results`（与任务列表共用页面，便于切换视角）。
- **报告管理**：报告列表 → `/reports`。
- **质量体系**：从「检测基础配置」`/quality/foundation` 可进入标准、参数库、记录模板、报告模板等子功能。

### 典型日操作路径（举例）

| 角色 | 建议路径 |
|------|----------|
| 接样岗 | `/sample/register` → `/sample` |
| 调度/组长 | `/testing/tasks`（分配、跟踪） |
| 检测员 | `/testing/tasks` → `/testing/tasks/:id` → `/testing/records` |
| 报告岗 | `/reports` → `/reports/:id` |
| 质量岗 | `/quality/audit` 或 `/quality/nonconformity` |

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| 点击菜单无反应或空白 | 权限不足被重定向 | 联系管理员分配 `meta.permission` |
| 登录后立即退出 | Token 失效或 401 | 重新登录；检查服务器时间与时区 |
| 接口报错但无明确提示 | 非标准信封或网络 | 查看浏览器控制台与 Network 响应体 |
| 找不到「标准」菜单 | 旧书签 `/standard` | 使用 `/quality/foundation` 或 `/quality/standards` |

## 数据核对清单

- [ ] 登录后 **`/dashboard`** 能加载统计（若后端有数据）。
- [ ] 侧栏仅显示有权限的菜单项。
- [ ] 直接输入 URL 访问业务页时，权限与菜单一致（无菜单但有 URL 时仍以权限为准）。

## 与上下游模块关系

- **首页** 聚合统计模块数据，依赖委托、任务、报告、设备等后端服务。
- **权限** 贯穿所有路由；无权限则无法进入对应 **上游** 数据维护或 **下游** 审批环节。
- 详细流程衔接见 **`03-business-process-map.md`** 与各模块用户指南。
