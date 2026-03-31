# 报告管理用户指南

## 适用对象

- 报告编制人：创建草稿、上传 PDF、维护结论。
- 审核人、批准人：按流程推进 `status`（以后端业务规则与界面按钮为准）。
- 发放岗：登记发放记录。

## 前置条件

- 存在 **委托单** `/entrustment/:id`，且检测业务数据足以支撑报告结论。
- 权限：`report:list`；若有编制/审核/批准细分权限，以角色配置为准。
- 建议预先了解 **报告模板** 命名与类型约定：**`/quality/report-templates`**。

## 页面入口

| 功能 | 路由 | 侧栏 |
|------|------|------|
| 报告列表 | `/reports` | 报告管理 → 报告列表 |
| 报告详情 | `/reports/:id` | 列表点击进入 |

## 字段说明

### 报告（Report）

| 字段 | 含义 |
|------|------|
| `report_no` | 报告编号（唯一） |
| `commission` | 所属委托单 |
| `report_type` | 报告类型 |
| `template_name` | 所选报告模板名称（文本） |
| `status` | 草稿/待审核/待批准/已批准/已发放/已归档/已作废 |
| `compiler` / `compile_date` | 编制人、编制日期 |
| `auditor` / `audit_date` | 审核人、审核日期 |
| `approver` / `approve_date` | 批准人、批准日期 |
| `conclusion` | 检测结论 |
| `pdf_file` | 报告 PDF 附件 |
| `qr_code` | 防伪二维码内容或标识 |
| `has_cma` | 是否带 CMA 标识 |
| `issue_date` | 发放日期 |
| `remark` | 备注 |

### 报告审批记录（ReportApproval）

| 字段 | 含义 |
|------|------|
| `role` | 编制/审核/批准 |
| `action` | 提交/通过/退回 |
| `user` | 操作人 |
| `comment` | 意见 |
| `signature` | 电子签名（如有） |

### 报告发放（ReportDistribution）

| 字段 | 含义 |
|------|------|
| `recipient` / `recipient_unit` | 接收人、单位 |
| `method` | 纸质/电子/纸质+电子 |
| `copies` | 份数 |
| `distribution_date` | 发放日期 |

### 报告模板（ReportTemplate，维护在质量侧）

| 字段 | 含义 |
|------|------|
| `code` / `name` | 模板编号、名称 |
| `report_type` | 类型 |
| `test_method` / `test_parameter` | 可选关联方法与参数 |
| `schema` | 模板定义（JSON） |
| `is_active` | 是否启用 |

## 标准操作步骤（SOP）

### 新建与编辑报告

1. 进入 **`/reports`**，使用「新建」或等价入口（以界面为准）。
2. 选择 **委托单**，填写 **报告类型**、**模板名称**（与 `/quality/report-templates` 约定一致便于检索）。
3. 录入 **检测结论** `conclusion`，上传 **PDF**（若流程要求）。
4. 保存为 **草稿** 后按流程 **提交审核**。

### 审核与批准

1. 打开 **`/reports/:id`**，查看当前 `status` 与审批记录。
2. 按实验室角色依次 **审核**、**批准**（界面按钮与后端状态机一致）。
3. 退回时填写 **意见**，编制人修改后重新提交。

### 发放与归档

1. 批准后按制度 **发放**，可登记 **ReportDistribution**（若界面提供）。
2. 维护 **`issue_date`**；需要时更新 **二维码** 与 **CMA** 标识。
3. 最终 **归档** 或 **作废** 需权限与审计要求支持。

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| 选不到委托 | 无权限或委托已取消 | 核对委托 `status` 与账号 |
| 模板名称混乱 | 未与质量库统一 | 查阅 **`/quality/report-templates`** |
| 结论与原始记录不符 | 编制未核对任务/记录 | 回溯 **`/testing/records`** |
| PDF 无法下载 | 文件未上传或存储异常 | 检查 MinIO/媒体配置 |

## 数据核对清单

- [ ] `report_no` 对外唯一，与纸质/电子存档一致。
- [ ] `commission` 与客户委托单一致。
- [ ] `conclusion` 与检测数据、判定规则一致（见 **`/testing`** 结果）。
- [ ] 审批记录时间与签字人符合授权体系。

## 与上下游模块关系

- **上游**：
  - **委托** `/entrustment`：`Report.commission`。
  - **检测任务与原始记录** `/testing/*`：提供技术事实与追溯。
  - **报告模板** `/quality/report-templates`：约定类型与结构。
- **下游**：对外交付、档案管理；统计看板 **`/dashboard`** 中「本月报告」等指标。
- **质量体系**：模板与 CMA 标识、不符合项关闭等可联动（流程依实验室制度）。

相关路由：**`/reports`**、**`/reports/:id`**；关联 **`/quality/report-templates`**。
