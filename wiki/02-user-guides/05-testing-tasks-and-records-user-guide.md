# 检测任务、原始记录与检测结果用户指南

## 适用对象

- 调度/组长：分配任务、跟踪进度。
- 检测员：开始/完成检测、填写原始记录。
- 复核人：对原始记录进行复核（权限以后端为准）。
- 技术岗：在任务详情查看 **检测结果** 列表。

## 前置条件

- 已存在 **样品** 及由其生成的 **检测任务**（`/sample/:id` 或后端服务生成）。
- 质量体系已配置 **检测方法**、**检测参数**、**原始记录模板**（`/quality/parameter-library`、`/quality/record-templates`）。
- 权限：`task:list`（任务列表与详情、检测结果列表）；`record:list`、`record:create`（原始记录）。

## 页面入口

| 功能 | 路由 | 侧栏 |
|------|------|------|
| 检测任务（看板/列表） | `/testing/tasks` | 检测管理 → 检测任务 |
| 检测结果（同页组件） | `/testing/results` | 检测管理 → 检测结果 |
| 任务详情 | `/testing/tasks/:id` | 从任务列表/看板进入 |
| 原始记录列表 | `/testing/records` | 检测管理 → 原始记录 |
| 新建原始记录 | `/testing/records/new` | 列表「新建」或直达 |
| 编辑/查看记录 | `/testing/records/:id` | 列表行进入 |

### 关于 `/testing/tasks` 与 `/testing/results`

两路由 **共用同一 Vue 组件**（`TaskList.vue`），菜单名称不同便于用户从「任务调度」与「结果关注」两个入口进入 **同一数据源**。可在列表中通过 **状态** 等条件筛选：例如仅看 **已完成** 任务以侧重检测结果场景。

### 快捷筛选

从其他页带入查询参数时，任务列表会初始化筛选（示例）：

- `?sample=<样品ID>`：仅看某样品下的任务。
- `?status=<状态>`：如 `completed` 等。

## 字段说明

### 检测任务（TestTask）

| 字段 | 含义 |
|------|------|
| `task_no` | 任务编号 |
| `sample` | 关联样品 |
| `commission` | 关联委托单 |
| `test_method` | 检测方法（外键至质量库） |
| `test_parameter` | 检测参数（可选） |
| `assigned_tester` | 检测员用户 |
| `assigned_equipment` | 使用设备（可选） |
| `planned_date` / `actual_date` | 计划/实际检测日期 |
| `status` | 待分配/待检/检测中/已完成/异常 |
| `age_days` | 龄期(天)（如混凝土等） |
| `remark` | 备注 |

前端列表展示常用：`task_no`、`sample_name`、`method_name`、`tester_name`、`planned_date` 等（来自序列化器扩展字段）。

### 原始记录（OriginalRecord）

| 字段 | 含义 |
|------|------|
| `task` | 一对一绑定检测任务 |
| `template` | 记录模板 |
| `template_version` | 使用的模板版本 |
| `record_data` | JSON 表单数据 |
| `env_temperature` / `env_humidity` | 环境温湿度 |
| `status` | 草稿/待复核/已复核/已退回 |
| `recorder` / `reviewer` | 记录人、复核人 |

### 检测结果（TestResult）

在 **`/testing/tasks/:id`** 任务详情页会请求 **`getTestResults({ task_id })`** 展示结果列表（具体列以后端序列化为准）。

## 标准操作步骤（SOP）

### 分配与执行检测任务

1. 打开 **`/testing/tasks`**，选择 **看板** 或 **列表** 视图。
2. 对待分配任务点击 **分配**，选择检测员（可选人员依赖 **`getAssignableTesters`**，与检测方法相关）。
3. 对已分配任务点击 **开始**，状态变为 **检测中**。
4. 试验完成后点击 **完成**，状态变为 **已完成**。
5. 点击卡片/行进入 **`/testing/tasks/:id`** 查看详情与 **检测结果**。

### 填写原始记录

1. 进入 **`/testing/records`**，查找对应任务记录；或从 **`/testing/records/new`** 新建（需选择任务与模板，以界面为准）。
2. 在 **`/testing/records/:id`** 按 JSON 模板填写试验数据，填写环境温湿度等。
3. 保存草稿后，在列表中 **提交**（界面调用 `submitRecord`），提交后按提示可能 **不可再改**，需谨慎。

### 侧重「检测结果」的查阅

1. 使用侧栏 **检测结果** 进入 **`/testing/results`**（与任务列表相同）。
2. 将 **状态** 筛为 **已完成**，结合日期、检测员筛选。
3. 进入任务详情查看 **`getTestResults`** 返回的结果明细。

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| 任务列表为空且提示无任务 | 未对样品生成任务 | 回 **`/sample/:id`** 生成任务 |
| 分配时无检测员 | 该方法无可分配人员 | 在人员/岗位能力中维护 |
| 无法提交原始记录 | 已提交或状态不允许 | 查看 `status` 是否已复核 |
| 认为「检测结果」是单独模块 | 路由复用 | 使用筛选或任务详情中结果区 |

## 数据核对清单

- [ ] 任务 `sample`、`commission` 与样品、委托一致。
- [ ] `test_method` / `test_parameter` 与原始记录模板绑定关系正确。
- [ ] 原始记录 `task` 与目标任务一对一，无重复记录。
- [ ] 任务 `status` 与实验室实际进度一致；计划日期与逾期提示（看板逾期样式）合理。

## 与上下游模块关系

- **上游**：**样品** `/sample` → 生成任务；**质量体系** `/quality/*` 提供方法、参数、记录模板。
- **下游**：**检测结果** 支撑判定与报告；**报告** `/reports` 引用委托与检测结论。
- **资源**：任务可关联 **设备** `/equipment`、**人员** `/staff`（分配与能力）。

相关路由：**`/testing/tasks`**、**`/testing/results`**、**`/testing/tasks/:id`**、**`/testing/records`**、**`/testing/records/new`**、**`/testing/records/:id`**。
