# 委托管理用户指南

## 适用对象

- 委托受理岗：创建、修改委托单与委托项目行。
- 评审人员：进行合同/技术评审，推进 `status`。
- 样品与检测岗：根据委托编号查找关联样品与任务。

## 前置条件

- 已存在 **`/project`** 中的工程项目。
- 权限：`entrustment:list`（列表与详情）；`entrustment:create`（新建）；`entrustment:edit`（编辑）。

## 页面入口

| 功能 | 路由 | 侧栏 |
|------|------|------|
| 委托列表 | `/entrustment` | 业务管理 → 委托管理 |
| 新建委托 | `/entrustment/create` | 列表页「新增」或直达 URL |
| 委托详情 | `/entrustment/:id` | 列表点击进入 |
| 编辑委托 | `/entrustment/:id/edit` | 详情页「编辑」 |

## 字段说明

### 委托单（Commission）

| 字段 | 含义 |
|------|------|
| `commission_no` | 委托编号（系统唯一） |
| `project` | 所属工程项目 |
| `sub_project` | 分部分项工程（可选） |
| `construction_part` | 施工部位 |
| `commission_date` | 委托日期 |
| `client_unit` | 委托单位 |
| `client_contact` / `client_phone` | 联系人、电话 |
| `witness` | 见证人（来自项目的 Witness） |
| `is_witnessed` | 是否见证取样 |
| `status` | 草稿/待评审/已评审/已退回/已取消 |
| `reviewer` / `review_date` / `review_comment` | 评审人、时间、意见 |
| `remark` | 备注 |

### 委托项目行（CommissionItem）

| 字段 | 含义 |
|------|------|
| `test_object` | 检测对象 |
| `test_item` | 检测项目 |
| `test_standard` | 检测标准 |
| `test_method` | 检测方法（文本；与质量库中方法可对照） |
| `specification` | 规格型号 |
| `grade` | 设计强度/等级 |
| `quantity` / `unit` | 数量与单位 |
| `remark` | 备注 |

### 合同评审（ContractReview）

与委托一对一，包含能力、设备、人员、方法有效性、样品代表性等勾选及 `conclusion`（接受/拒绝/有条件接受）、`comment`。

## 标准操作步骤（SOP）

### 新建委托

1. 进入 **`/entrustment/create`**。
2. 选择 **工程项目**；选填 **分部分项**。
3. 填写 **施工部位**、**委托日期**、**委托单位**与联系方式。
4. 选择或确认 **见证人**，勾选是否 **见证取样**。
5. 在委托项目表中逐行添加 **检测对象、检测项目、标准、方法** 等。
6. 保存，记录系统生成的 **委托编号**。

### 查询与打开详情

1. 在 **`/entrustment`** 使用筛选/搜索定位委托。
2. 点击行进入 **`/entrustment/:id`**，查看状态、评审信息、关联样品与任务（若界面提供跳转）。

### 编辑与评审流转

1. 在允许编辑的状态下进入 **`/entrustment/:id/edit`** 修改正文。
2. 按实验室制度提交评审；评审通过后 **`status`** 应为已评审，方可进入大批量收样与任务生成（具体规则以配置与后端校验为准）。

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| 无法选择见证人 | 项目下未维护 Witness | 在 **`/project/:id`** 补录见证人 |
| 委托编号重复 | 异常重试或并发 | 联系管理员查日志；避免重复提交 |
| 样品无法关联 | 委托未生效或 ID 错误 | 确认委托 `status` 与 `commission_no` |
| 检测任务参数不匹配 | 委托行填写的方法/标准与参数库不一致 | 统一质量库命名或调整委托行 |

## 数据核对清单

- [ ] `project` 与现场工程一致；`construction_part` 表述清晰。
- [ ] 委托项目行 **数量/单位** 与收样计划一致。
- [ ] `status` 与业务实际（是否可收样）一致。
- [ ] 合同评审结论与 `conclusion`、纸质记录一致。

## 与上下游模块关系

- **上游**：**工程项目** `/project`（项目、分部分项、见证人）。
- **下游**：
  - **样品** `/sample`、`/sample/register`：`Sample.commission` 指向本委托。
  - **检测任务** `/testing/tasks`：`TestTask.commission` 关联委托。
  - **报告** `/reports`：`Report.commission` 关联委托。
- **质量体系**：委托行填写的标准/方法应对照 **`/quality/standards`** 与 **`/quality/parameter-library`**，保证可执行。

相关路由：**`/entrustment`**、**`/entrustment/create`**、**`/entrustment/:id`**、**`/entrustment/:id/edit`**。
