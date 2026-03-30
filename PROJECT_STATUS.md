# LIMIS 实验室信息管理系统 — 项目开发状态文档（详细分层版）

> **更新时间**：2026年3月30日
> **当前环境**：开发模式 Django 5.x + Vue 3 + TypeScript + PostgreSQL 16 + Redis
> **访问地址**：前端 `http://<LAN_IP>:3000` · 后端 `http://<LAN_IP>:8000`
> **管理员账号**：`admin` / `admin123` · 测试用户 `zhangsan`/`lisi`/`wangwu` / `test123`
> **API 文档**：`http://<LAN_IP>:8000/api/docs/`（Swagger）、`http://<LAN_IP>:8000/api/redoc/`

---

## 目录

1. [已完成模块总览](#1-已完成模块总览)
2. [后端详细清单](#2-后端详细清单)
3. [前端详细清单](#3-前端详细清单)
4. [已知 Bug 与问题](#4-已知-bug-与问题)
5. [待完善功能清单（分层优先级）](#5-待完善功能清单分层优先级)
6. [接口清单速查表](#6-接口清单速查表)
7. [数据库模型速查表](#7-数据库模型速查表)
8. [项目目录结构](#8-项目目录结构)
9. [启动与调试说明](#9-启动与调试说明)
10. [后续 Agent 开发规范](#10-后续-agent-开发规范)

---

## 1. 已完成模块总览

| 阶段 | 模块 | 后端 | 前端页面 | 前端路由 | 状态 |
|------|------|------|----------|----------|------|
| 一 | 项目骨架搭建 | ✅ | ✅ | ✅ | 完成 |
| 一 | 用户认证与 RBAC | ✅ | ✅ | ✅ | 完成（部分Bug待修） |
| 一 | 工程项目管理 | ✅ | ✅ | ✅ | 完成 |
| 一 | 委托管理 | ✅ | ✅ | ✅ | 完成 |
| 一 | 样品管理 | ✅ | ✅ | ✅ | 完成 |
| 二 | 检测任务管理 | ✅ | ✅ 有页面 | ❌ 路由未注册 | **前端路由断开** |
| 二 | 原始记录模板引擎 | ✅ | ✅ 有页面 | ❌ 路由未注册 | **前端路由断开** |
| 二 | 计算引擎与结果判定 | ✅ | — | ❌ 无页面 | **缺前端** |
| 三 | 报告管理 | ✅ | ✅ 有页面 | ❌ 路由未注册 | **前端路由断开** |
| 三 | 仪器设备管理 | ✅ | ✅ | ✅ | 完成 |
| 四 | 人员管理 | ✅ | ✅ | ✅ | 完成 |
| 四 | 环境监控 | ✅ | ✅ | ✅ | 完成 |
| 四 | 标准规范管理 | ✅ | ✅ | ✅ | 完成 |
| 四 | 质量管理体系 | ✅ | ✅ | ✅ | 完成（侧边栏链接断开） |
| 四 | 耗材管理 | ✅ | ✅ | ✅ | 完成 |
| 五 | 统计分析 | ✅ | ✅ Dashboard | ✅ | 完成（图表需验证） |

---

## 2. 后端详细清单

### 2.1 基础架构层 (`core/`)

| 文件 | 内容 | 状态 |
|------|------|------|
| `core/models.py` | `BaseModel`（created_at, updated_at, created_by, is_deleted, soft_delete）、`BaseManager` | ✅ |
| `core/views.py` | `BaseModelViewSet`（软删除 destroy、包装 create/update 响应为 code/message/data） | ✅ |
| `core/serializers.py` | `CreatedByMixin`、`BaseModelSerializer`（含 created_by_name） | ✅ |
| `core/pagination.py` | `StandardPagination`（page_size=20, max=100, 响应包装 code/message/data） | ✅ |
| `core/permissions.py` | `IsAuthenticated`、`RoleBasedPermission`、`ModulePermission` | ✅ 有逻辑缺陷 |
| `core/exceptions.py` | `BusinessException`、`ValidationException`、`PermissionDeniedException`、`custom_exception_handler` | ✅ |
| `core/filters.py` | `DateRangeFilterMixin`、`BaseFilterSet` | ✅ |
| `core/middleware.py` | `AuditLogMiddleware`（缓存 request.body、记录 POST/PUT/PATCH/DELETE） | ✅ |
| `core/utils/numbering.py` | `NumberGenerator`（Redis INCR + SQL fallback `core_sequence`） | ⚠️ SQL表可能缺迁移 |
| `core/utils/barcode.py` | QR 码、条码、标签 PDF 生成 | ✅ |
| `core/utils/export.py` | Excel（openpyxl）/ CSV 导出、PDF（WeasyPrint）辅助 | ✅ |
| `core/utils/rounding.py` | GB/T 8170 四舍六入五成双修约 | ✅ |

### 2.2 系统管理 (`apps/system/`)

**模型：**
| 模型 | 字段 | 说明 |
|------|------|------|
| `User` | username, phone, department, title, avatar, is_active, roles(M2M→Role) | 继承 AbstractUser |
| `Role` | name, code(11种角色choices), description, permissions(M2M→Permission) | BaseModel |
| `Permission` | name, code, module, action(view/create/edit/delete/approve/export) | BaseModel, unique(module,action) |
| `AuditLog` | user, username, method, path, body, ip_address, status_code, timestamp | 独立模型 |

**视图与接口：**
| ViewSet/View | 路径 | 特殊 Action |
|---|---|---|
| `UserViewSet` | `/api/v1/system/users/` | `reset_password`, `toggle_active` |
| `RoleViewSet` | `/api/v1/system/roles/` | `assign_permissions` |
| `PermissionViewSet` | `/api/v1/system/permissions/` | `grouped` |
| `AuditLogViewSet` | `/api/v1/system/audit-logs/` | — |
| `LoginView` | POST `/api/v1/system/login/` | — |
| `LogoutView` | POST `/api/v1/system/logout/` | — |
| `CurrentUserView` | GET `/api/v1/system/me/` | — |
| `PasswordChangeView` | PUT `/api/v1/system/password/change/` | — |
| Token Refresh | POST `/api/v1/system/token/refresh/` | SimpleJWT |

**服务层** (`services.py`)：`authenticate_user`, `create_user`, `get_user_permissions`, `has_permission`

### 2.3 工程项目管理 (`apps/projects/`)

**模型：**
| 模型 | 关键字段 |
|------|----------|
| `Project` | name, code, address, project_type, status, start_date, end_date, description |
| `Organization` | FK→project, name, role, contact_person, contact_phone; unique(project,name,role) |
| `SubProject` | FK→project, name, code, FK→parent(self), description |
| `Contract` | FK→project, contract_no, title, amount, sign_date, start/end_date, scope, attachment |
| `Witness` | FK→project, name, id_number, FK→organization, phone, certificate_no, is_active |

**视图：** `ProjectViewSet`（`stats` action）+ 嵌套 `OrganizationViewSet`, `SubProjectViewSet`, `ContractViewSet`, `WitnessViewSet`

**URL 模式：** `/api/v1/projects/` + `<project_pk>/organizations/` / `sub-projects/` / `contracts/` / `witnesses/`

### 2.4 委托管理 (`apps/commissions/`)

**模型：**
| 模型 | 关键字段 |
|------|----------|
| `Commission` | commission_no, FK→project, FK→sub_project, construction_part, commission_date, client_unit/contact/phone, FK→witness, is_witnessed, status(draft→pending_review→reviewed→rejected→cancelled), FK→reviewer, review_date/comment, remark |
| `CommissionItem` | FK→commission, test_object, test_item, test_standard, test_method, specification, grade, quantity, unit, remark |
| `ContractReview` | O2O→commission, has_capability/equipment/personnel, method_valid, sample_representative, conclusion, FK→reviewer, review_date/comment |

**视图：** `CommissionViewSet`（`submit`, `review`）、`CommissionItemViewSet`、`ContractReviewViewSet`

**服务层：** `generate_commission_no`, `submit_commission`, `review_commission`

### 2.5 样品管理 (`apps/samples/`)

**模型：**
| 模型 | 关键字段 |
|------|----------|
| `SampleGroup` | group_no, name, sample_count, description |
| `Sample` | sample_no, blind_no, FK→commission, FK→group, name, specification, grade, quantity, unit, sampling_date, received_date, production_date, sampling_location, status(pending→testing→tested→retention→disposed), retention_deadline, disposal_date/method, remark |
| `SampleDisposal` | FK→sample, disposal_type, disposal_date, FK→handler, remark |

**视图 Action：** `change-status`, `timeline`, `label`, `batch-register`, `retention-list`, `dispose`, `export`

**服务层：** 编号生成、状态流转、批量创建、时间线、标签二维码、处置等

### 2.6 检测任务与数据 (`apps/testing/`)

**模型（models/ 包）：**
| 模型 | 关键字段 | 文件 |
|------|----------|------|
| `TestCategory` | name, code, FK→parent(self), sort_order | method.py |
| `TestMethod` | name, standard_no, standard_name, FK→category, description, is_active | method.py |
| `TestParameter` | FK→method, name, code, unit, precision, min/max_value, is_required; unique(method,code) | method.py |
| `TestTask` | task_no, FK→sample, FK→commission, FK→test_method, FK→test_parameter, FK→assigned_tester, FK→assigned_equipment, planned_date, actual_date, status(unassigned→assigned→in_progress→completed), age_days, remark; `is_overdue` property | task.py |
| `RecordTemplate` | name, code, FK→test_method, version, schema(JSON), is_active | record.py |
| `OriginalRecord` | O2O→task, FK→template, template_version, record_data(JSON), env_temperature/humidity, status(draft→pending_review→reviewed→returned), FK→recorder, FK→reviewer, review_date/comment | record.py |
| `RecordRevision` | FK→record, field_path, old_value, new_value, FK→changed_by, changed_at | record.py |
| `JudgmentRule` | FK→test_parameter, grade, min_value, max_value, standard_ref | result.py |
| `TestResult` | FK→task, FK→parameter, raw_value, rounded_value, display_value, unit, judgment, standard_value, design_value, remark | result.py |

**计算公式库（`formulas/`）：**
| 文件 | 函数 | 标准依据 |
|------|------|----------|
| `concrete.py` | `calc_compressive_strength` | GB/T 50081 §6.0.4 |
| `concrete.py` | `calc_flexural_strength` | GB/T 50081 §7.0.4 |
| `concrete.py` | `calc_average_strength`（异常值剔除 15%） | GB/T 50081 |
| `rebar.py` | `calc_yield_strength`, `calc_tensile_strength` | GB 1499.2 |
| `rebar.py` | `calc_elongation` | GB/T 228.1 |
| `rebar.py` | `calc_weight_deviation` | GB 1499.2 §7.4 |
| `cement.py` | `calc_mortar_flexural`, `calc_mortar_compressive` | GB/T 17671 §9 |
| `cement.py` | `calc_cement_strength`（抗折 10% 剔除、抗压去极值四均值） | GB/T 17671 |
| `aggregate.py` | `calc_fineness_modulus` | JGJ 52 §7.3 |
| `aggregate.py` | `calc_mud_content` | JGJ 52 §7.7 |
| `aggregate.py` | `calc_crushing_value` | JGJ 52 §7.13 |

**判定引擎（`judgment.py`）：**
- `judge_result`：通用参数级判定
- `evaluate_concrete_strength`：GB/T 50107 混凝土强度统计/非统计评定
- `evaluate_rebar_mechanics`：GB 1499.2 钢筋力学性能评定（含强屈比 ≥ 1.25）

**视图 Action：** `assign`, `start`, `complete`, `today_list`, `overdue_list`, `age_calendar`, `submit`(record), `review`(record), `calculate`(result)

### 2.7 报告管理 (`apps/reports/`)

**模型：**
| 模型 | 关键字段 |
|------|----------|
| `Report` | report_no, FK→commission, report_type, template_name, status(draft→pending_audit→pending_approve→approved→issued→voided), FK→compiler/auditor/approver, compile/audit/approve_date, conclusion, pdf_file, qr_code, has_cma, issue_date, remark |
| `ReportApproval` | FK→report, role, action, FK→user, comment, signature |
| `ReportDistribution` | FK→report, recipient, recipient_unit, method, copies, distribution_date, receiver_signature |

**工作流（`workflow.py`）：** `submit_for_audit` → `audit_report`（pass/reject）→ `approve_report`（pass/reject）→ `issue_report` / `void_report`

**PDF 生成（`generator.py`）：** WeasyPrint 优先，fallback 文本占位；报告编号 `NumberGenerator.generate(prefix='BG')`

**电子签名（`signature.py`）：** `embed_signature` 用 pypdf + reportlab 叠加签名图片

**视图 Action：** `generate`, `submit_audit`, `audit`, `approve`, `issue`, `void`, `preview`, `download`, `distribute`, `verify`

### 2.8 仪器设备管理 (`apps/equipment/`)

**模型：** `Equipment`, `Calibration`, `PeriodCheck`, `Maintenance`, `EquipUsageLog`

**视图 Action：** `expiring`, `traceability` + 嵌套 calibrations/period-checks/maintenances/usage-logs

### 2.9 人员管理 (`apps/staff/`)

**模型：** `StaffProfile`(O2O→User), `Certificate`, `Authorization`(M2M→TestMethod), `Training`, `CompetencyEval`

**视图 Action：** `expiring-certs`

### 2.10 环境监控 (`apps/environment/`)

**模型：** `MonitoringPoint`, `EnvRecord`, `EnvAlarm`

**服务层：** `ingest_record`, `check_thresholds`, `get_point_latest_records`

**视图 Action：** `latest-records`, `ingest`, `resolve`

### 2.11 标准规范管理 (`apps/standards/`)

**模型：** `Standard`(standard_no, name, category, status, FK→replaced_by), `MethodValidation`

### 2.12 质量管理体系 (`apps/quality/`)

**模型（models/ 包）：**
| 模型 | 文件 |
|------|------|
| `InternalAudit`, `AuditFinding`, `CorrectiveAction` | audit.py |
| `ManagementReview`, `ReviewDecision` | review.py |
| `NonConformity`, `Complaint` | nonconformity.py |
| `ProficiencyTest`, `QualitySupervision` | proficiency.py |

### 2.13 耗材管理 (`apps/consumables/`)

**模型：** `Supplier`, `Consumable`(含 safety_stock, is_low_stock property), `ConsumableIn`, `ConsumableOut`

**视图 Action：** `low-stock`

### 2.14 统计分析 (`apps/statistics/`)

纯 API，无模型。

**视图（APIView）：** `DashboardView`, `TestVolumeView`, `QualificationRateView`, `StrengthCurveView`, `CycleAnalysisView`, `WorkloadView`, `EquipmentUsageView`

---

## 3. 前端详细清单

### 3.1 路由注册状态

| 路由路径 | 组件 | 是否注册到 router | 侧边栏可达 | 状态 |
|----------|------|:-:|:-:|------|
| `/login` | `LoginPage.vue` | ✅ | — | 正常 |
| `/dashboard` | `DashboardPage.vue` | ✅ | ✅ | 正常 |
| `/project` | `ProjectList.vue` | ✅ | ✅ | 正常 |
| `/project/:id` | `ProjectDetail.vue` | ✅ | — | 正常 |
| `/entrustment` | `CommissionList.vue` | ✅ | ✅ | 正常 |
| `/entrustment/create` | `CommissionForm.vue` | ✅ | — | 正常 |
| `/entrustment/:id` | `CommissionDetail.vue` | ✅ | — | 正常 |
| `/entrustment/:id/edit` | `CommissionForm.vue` | ✅ | — | 正常 |
| `/sample` | `SampleList.vue` | ✅ | ✅ | 正常 |
| `/sample/register` | `SampleRegister.vue` | ✅ | — | 正常 |
| `/sample/:id` | `SampleDetail.vue` | ✅ | — | 正常 |
| `/equipment` | `EquipmentList.vue` | ✅ | ✅ | 正常 |
| `/equipment/:id` | `EquipmentDetail.vue` | ✅ | — | 正常 |
| `/staff` | `StaffList.vue` | ✅ | ✅ | 正常 |
| `/staff/:id` | `StaffDetail.vue` | ✅ | — | 正常 |
| `/environment` | `EnvironmentMonitor.vue` | ✅ | ✅ | 正常 |
| `/consumable` | `ConsumableList.vue` | ✅ | ✅ | 正常 |
| `/standard` | `StandardList.vue` | ✅ | ✅ | 正常 |
| `/quality/audit` | `AuditList.vue` | ✅ | ❌ 侧边栏指向 `/internal-audit` | **侧边栏链接错误** |
| `/quality/review` | `ReviewList.vue` | ✅ | ❌ 侧边栏指向 `/management-review` | **侧边栏链接错误** |
| `/quality/nonconformity` | `NonConformityList.vue` | ✅ | ❌ 侧边栏指向 `/nonconformity` | **侧边栏链接错误** |
| `/system/users` | `UserList.vue` | ✅ | ✅ | 正常 |
| `/system/roles` | `RoleList.vue` | ✅ | ✅ | 正常 |
| `/system/audit-logs` | `AuditLogList.vue` | ✅ | ✅ | 正常 |
| `/task` | **PlaceholderPage.vue** | ✅ | ✅ | **占位符页面** |
| `/record` | **PlaceholderPage.vue** | ✅ | ✅ | **占位符页面** |
| `/result` | **PlaceholderPage.vue** | ✅ | ✅ | **占位符页面** |
| `/report` | **PlaceholderPage.vue** | ✅ | ✅ | **占位符页面** |
| `/testing/tasks` | `TaskList.vue` | ❌ **未导入** | ❌ | **路由断开** |
| `/testing/tasks/:id` | `TaskDetail.vue` | ❌ **未导入** | ❌ | **路由断开** |
| `/testing/records` | `RecordList.vue` | ❌ **未导入** | ❌ | **路由断开** |
| `/testing/records/new` | `RecordForm.vue` | ❌ **未导入** | ❌ | **路由断开** |
| `/testing/records/:id` | `RecordForm.vue` | ❌ **未导入** | ❌ | **路由断开** |
| `/reports` | `ReportList.vue` | ❌ **未导入** | ❌ | **路由断开** |
| `/reports/:id` | `ReportDetail.vue` | ❌ **未导入** | ❌ | **路由断开** |

### 3.2 前端 API 层 (`api/`)

| 文件 | 函数数量 | 对应后端模块 | 状态 |
|------|----------|------------|------|
| `auth.ts` | 5 | system (login/logout/me/refresh/password) | ✅ |
| `system.ts` | 12 | system (users/roles/permissions/audit-logs) | ✅ |
| `projects.ts` | 17 | projects (全CRUD + 嵌套子资源) | ✅ |
| `commissions.ts` | 8 | commissions | ✅ |
| `samples.ts` | 10 | samples | ✅ |
| `testing.ts` | 26 | testing (tasks/records/results/categories/methods) | ✅ |
| `reports.ts` | 12 | reports | ✅ |
| `equipment.ts` | 12 | equipment | ✅ |
| `staff.ts` | 12 | staff | ✅ |
| `environment.ts` | 5 | environment | ✅ |
| `quality.ts` | 14 | quality | ✅ |
| `consumables.ts` | 6 | consumables | ✅ |
| `statistics.ts` | 7 | statistics | ✅ |
| **standards** | 0（`StandardList.vue` 直接用 `request`） | standards | ⚠️ 缺独立 API 文件 |

### 3.3 Pinia Store

| Store | 关键 State | Actions | 状态 |
|-------|-----------|---------|------|
| `user.ts` | userInfo, token, permissions, roles | login, logout, getUserInfo, refreshUserToken | ✅ |
| `dict.ts` | dictMap(Map) | loadDict, getDict, getDictLabel, clearDict | ✅ 但 API `/v1/system/dict/:dictType/` 后端无此端点 |

### 3.4 布局组件

| 组件 | 功能 | 问题 |
|------|------|------|
| `MainLayout.vue` | 固定侧边栏 + Header + router-view | ✅ |
| `Sidebar.vue` | 硬编码菜单项，`el-menu` | ⚠️ 质量体系3条链接路径错误；检测/报告指向占位符 |
| `Header.vue` | 面包屑、通知铃铛（硬编码badge）、用户下拉 | ⚠️ "修改密码"跳转到用户列表而非密码表单 |

### 3.5 冗余/空白文件

| 文件 | 说明 |
|------|------|
| `views/system/UserManagement.vue` | el-empty 占位，实际使用 `UserList.vue` |
| `views/system/RoleManagement.vue` | el-empty 占位，实际使用 `RoleList.vue` |
| `views/system/AuditLogs.vue` | el-empty 占位，实际使用 `AuditLogList.vue` |
| `views/placeholder/PlaceholderPage.vue` | 通用 "功能开发中" 占位页面 |

---

## 4. 已知 Bug 与问题

### 4.1 严重（影响核心功能使用）

| # | 问题描述 | 涉及文件 | 修复建议 |
|---|---------|----------|----------|
| BUG-001 | **检测任务/原始记录/报告路由未注册**：`router/modules/testing.ts` 和 `reports.ts` 已定义路由模块但未在 `router/index.ts` 中导入，导致实际页面（TaskList/TaskDetail/RecordList/RecordForm/ReportList/ReportDetail）无法访问，侧边栏点击进入占位符页面 | `frontend/src/router/index.ts` | 导入 `testingRoutes` 和 `reportRoutes`，替换占位符路由 |
| BUG-002 | **侧边栏质量体系链接路径错误**：侧边栏 `Sidebar.vue` 中质量体系子菜单路径为 `/internal-audit`、`/management-review`、`/nonconformity`，但路由注册路径为 `/quality/audit`、`/quality/review`、`/quality/nonconformity` | `frontend/src/components/Layout/Sidebar.vue` | 改为正确路径 |
| BUG-003 | **前端 testing API 路径与后端不匹配**：前端 `api/testing.ts` 使用 `/v1/test-tasks/`、`/v1/original-records/` 等，但后端 URL 注册在 `testing/` 前缀下，实际路径为 `/api/v1/testing/tasks/`、`/api/v1/testing/records/` 等 | `frontend/src/api/testing.ts` | 修正所有 URL 路径前缀 |
| BUG-004 | **`create_samples_from_commission`** 中使用 `getattr(item, 'name', '')` 但 `CommissionItem` 无 `name` 字段（应为 `test_object`），且取 `commission.sampling_date` 等不存在的字段 | `backend/apps/samples/services.py` | 修正字段映射 |

### 4.2 中等（影响部分功能或用户体验）

| # | 问题描述 | 涉及文件 | 修复建议 |
|---|---------|----------|----------|
| BUG-005 | **权限体系 action 命名不一致**：`Permission.ACTION_CHOICES` 用 `create` 而 `ModulePermission.action_map` 用 `add`；报告工作流用 `has_perm('reports.compile_report')` 而非数据库 Permission 模型 | `core/permissions.py`、`reports/workflow.py` | 统一为一套 action 命名 |
| BUG-006 | **`NumberGenerator` SQL fallback 的 `core_sequence` 表无迁移文件**，Redis 不可用时 DB fallback 会报错 | `core/utils/numbering.py` | 添加 migration 创建 core_sequence 表 |
| BUG-007 | **`dict.ts` store 调用 `/v1/system/dict/:dictType/` 但后端无此接口** | `frontend/src/stores/dict.ts` | 后端增加字典接口或前端删除 |
| BUG-008 | **Header "修改密码" 导航到 `/system/users`** 而非密码修改表单 | `frontend/src/components/Layout/Header.vue` | 改为弹窗或独立密码修改页 |
| BUG-009 | **检测任务分配使用数字 ID 输入**，而非检测人员下拉选择 | `frontend/src/views/testing/tasks/TaskDetail.vue` | 改为人员选择器 |
| BUG-010 | **Dashboard "查看全部" 按钮无导航** | `frontend/src/views/dashboard/DashboardPage.vue` | 添加 router-link |
| BUG-011 | **`consumables` 前端 API 路径问题**：使用 `/v1/consumables/:id/in/` 但后端注册为 `/v1/consumables/items/` 和 `/v1/consumables/in-records/`、`/v1/consumables/out-records/` | `frontend/src/api/consumables.ts` | 修正路径 |
| BUG-012 | **标准管理无独立 API 文件**：`StandardList.vue` 直接使用 `request` 实例 | `frontend/src/views/standards/StandardList.vue` | 抽取为 `api/standards.ts` |

### 4.3 轻微（UI/代码质量）

| # | 问题描述 |
|---|---------|
| BUG-013 | 3个空白 stub 文件（UserManagement/RoleManagement/AuditLogs.vue）应删除或重命名 |
| BUG-014 | `router.beforeEach` 仅检查登录态，未检查 `meta.permission` 字段 |
| BUG-015 | `CommissionDetail.vue` 中权限检查用 `commission:review`，与后端 `ModulePermission` 配置需对齐 |
| BUG-016 | 通知铃铛 badge 硬编码，无真实通知数据源 |

---

## 5. 待完善功能清单（分层优先级）

### 5.1 P0 — 必须立即修复（前端路由/链接断裂）

- [ ] **5.1.1** 在 `router/index.ts` 导入 `testingRoutes` 和 `reportRoutes`，移除占位符路由
- [ ] **5.1.2** 修正 `Sidebar.vue` 质量体系菜单路径（`/internal-audit` → `/quality/audit` 等）
- [ ] **5.1.3** 修正 `Sidebar.vue` 检测管理菜单路径（`/task` → `/testing/tasks` 等）
- [ ] **5.1.4** 修正 `Sidebar.vue` 报告管理菜单路径（`/report` → `/reports`）
- [ ] **5.1.5** 修正 `api/testing.ts` 中所有 URL 前缀（加上 `testing/` 前缀）
- [ ] **5.1.6** 修正 `api/consumables.ts` 路径与后端一致
- [ ] **5.1.7** 删除或清理 3 个 stub Vue 文件

### 5.2 P1 — 高优先级（核心功能稳定性）

#### 5.2.1 认证与会话管理
- [ ] 验证 `LogoutView` 正确接收并拉黑 refresh token
- [ ] 实现 Token 过期自动刷新（401 拦截器中静默 refresh）
- [ ] 多设备登录踢出机制
- [ ] 密码修改弹窗组件（替代跳转用户列表）
- [ ] 登录失败次数限制

#### 5.2.2 权限体系
- [ ] 统一 `Permission.action` 与 `ModulePermission.action_map` 的命名（create vs add）
- [ ] `router.beforeEach` 增加 `meta.permission` 校验
- [ ] 实现 `v-permission` 指令在所有页面的应用
- [ ] 菜单动态渲染（根据用户角色过滤菜单项）
- [ ] 报告工作流权限与 Permission 模型对齐

#### 5.2.3 数据完整性
- [ ] 修复 `create_samples_from_commission` 字段映射
- [ ] 添加 `core_sequence` 表的数据库迁移
- [ ] 实现或移除 `dict` store 的后端接口

### 5.3 P2 — 中优先级（业务完整性）

#### 5.3.1 报告管理完善
- [ ] 报告 HTML 模板文件（`templates/reports/report_template.html`）
- [ ] 安装 WeasyPrint 并验证 PDF 生成
- [ ] 报告预览页面（PDF 内嵌 iframe）
- [ ] 报告审批流全程 UI 测试
- [ ] 电子签名上传与 PDF 叠加功能验证（需 pypdf + reportlab）
- [ ] CMA 标识自动插入
- [ ] 报告二维码防伪验证页面
- [ ] 报告台账导出

#### 5.3.2 检测业务完善
- [ ] 检测任务分配改为人员/设备下拉选择器
- [ ] 龄期日历视图实现（前端 ECharts 热力图或日历组件）
- [ ] 超期预警通知（Celery 定时任务 + 系统消息）
- [ ] 原始记录 JSON Schema 预置模板数据（混凝土/钢筋/水泥/砂石）
- [ ] 动态表单渲染组件（根据 RecordTemplate.schema 渲染）
- [ ] 记录修改追踪对比视图（RecordRevision）
- [ ] 计算引擎前端触发 + 结果展示（当前后端有 `calculate` 接口）

#### 5.3.3 统计分析与 Dashboard
- [ ] 验证 Dashboard 图表数据源正确性
- [ ] 补充检测量趋势图时间维度筛选
- [ ] 合格率饼图
- [ ] 混凝土强度发展曲线页面
- [ ] 设备利用率统计页面
- [ ] 人员工作量统计页面
- [ ] 自定义时间范围筛选

#### 5.3.4 数据导入导出
- [ ] Excel 模板下载与批量导入（委托、样品）
- [ ] 标准规范数据初始化脚本
- [ ] 耗材入库/出库台账导出
- [ ] 抽取 `api/standards.ts` API 文件

### 5.4 P3 — 低优先级（优化与扩展）

#### 5.4.1 部署与运维
- [ ] 生产环境 Docker Compose 完善（Gunicorn + Nginx）
- [ ] HTTPS 配置
- [ ] 数据库自动备份脚本
- [ ] 日志轮转与监控告警
- [ ] Celery Worker + Beat 启动配置
- [ ] MinIO 文件存储对接

#### 5.4.2 代码质量
- [ ] 单元测试（每个 app 的 `tests/` 目录已存在但为空）
- [ ] API 集成测试
- [ ] 前端 TypeScript 类型完善（减少 `any`）
- [ ] ESLint / Prettier 配置
- [ ] 后端 ruff / flake8 检查

#### 5.4.3 高级功能
- [ ] 通知中心（站内信、邮件推送）
- [ ] 移动端 H5 适配（响应式布局优化）
- [ ] PWA 离线支持
- [ ] 仪器设备数据自动采集接口（压力机/万能试验机）
- [ ] 环境传感器 MQTT 接入
- [ ] 见证取样统计报表
- [ ] 数据加密存储

---

## 6. 接口清单速查表

### 6.1 系统管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/system/login/` | 登录 |
| POST | `/api/v1/system/logout/` | 登出 |
| GET | `/api/v1/system/me/` | 当前用户信息 |
| POST | `/api/v1/system/token/refresh/` | 刷新 Token |
| PUT | `/api/v1/system/password/change/` | 修改密码 |
| GET/POST | `/api/v1/system/users/` | 用户列表/创建 |
| GET/PUT/DELETE | `/api/v1/system/users/:id/` | 用户详情/更新/删除 |
| POST | `/api/v1/system/users/:id/reset_password/` | 重置密码 |
| POST | `/api/v1/system/users/:id/toggle_active/` | 启用/禁用 |
| GET/POST | `/api/v1/system/roles/` | 角色列表/创建 |
| POST | `/api/v1/system/roles/:id/assign_permissions/` | 分配权限 |
| GET | `/api/v1/system/permissions/` | 权限列表 |
| GET | `/api/v1/system/permissions/grouped/` | 按模块分组权限 |
| GET | `/api/v1/system/audit-logs/` | 审计日志 |

### 6.2 业务模块

| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/v1/projects/` | 工程项目 |
| GET | `/api/v1/projects/:id/stats/` | 项目统计 |
| CRUD | `/api/v1/projects/:pid/organizations/` | 参建单位 |
| CRUD | `/api/v1/projects/:pid/sub-projects/` | 分部分项工程 |
| CRUD | `/api/v1/projects/:pid/contracts/` | 合同 |
| CRUD | `/api/v1/projects/:pid/witnesses/` | 见证人 |
| CRUD | `/api/v1/commissions/` | 委托单 |
| POST | `/api/v1/commissions/:id/submit/` | 提交审批 |
| POST | `/api/v1/commissions/:id/review/` | 审批 |
| CRUD | `/api/v1/commissions/:cid/items/` | 委托项目明细 |
| CRUD | `/api/v1/commissions/:cid/contract-review/` | 合同评审 |
| CRUD | `/api/v1/samples/` | 样品 |
| POST | `/api/v1/samples/batch-register/` | 批量登记 |
| POST | `/api/v1/samples/:id/change-status/` | 状态变更 |
| GET | `/api/v1/samples/:id/timeline/` | 流转时间线 |
| GET | `/api/v1/samples/:id/label/` | 标签二维码 |
| GET | `/api/v1/samples/retention-list/` | 留样列表 |
| POST | `/api/v1/samples/:id/dispose/` | 处置 |
| GET | `/api/v1/samples/export/` | 台账导出 |
| CRUD | `/api/v1/samples/sample-groups/` | 样品组 |

### 6.3 检测模块

| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/v1/testing/categories/` | 检测类别 |
| CRUD | `/api/v1/testing/methods/` | 检测方法 |
| CRUD | `/api/v1/testing/parameters/` | 检测参数 |
| CRUD | `/api/v1/testing/tasks/` | 检测任务 |
| POST | `/api/v1/testing/tasks/:id/assign/` | 分配任务 |
| POST | `/api/v1/testing/tasks/:id/start/` | 开始检测 |
| POST | `/api/v1/testing/tasks/:id/complete/` | 完成检测 |
| GET | `/api/v1/testing/tasks/today_list/` | 今日待检 |
| GET | `/api/v1/testing/tasks/overdue_list/` | 超期任务 |
| GET | `/api/v1/testing/tasks/age_calendar/` | 龄期日历 |
| CRUD | `/api/v1/testing/templates/` | 记录模板 |
| CRUD | `/api/v1/testing/records/` | 原始记录 |
| POST | `/api/v1/testing/records/:id/submit/` | 提交复核 |
| POST | `/api/v1/testing/records/:id/review/` | 复核 |
| CRUD | `/api/v1/testing/results/` | 检测结果 |
| POST | `/api/v1/testing/results/calculate/` | 自动计算 |
| CRUD | `/api/v1/testing/judgment-rules/` | 判定规则 |

### 6.4 报告模块

| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/v1/reports/` | 报告 |
| POST | `/api/v1/reports/:id/generate/` | 生成报告 |
| POST | `/api/v1/reports/:id/submit_audit/` | 提交审核 |
| POST | `/api/v1/reports/:id/audit/` | 审核 |
| POST | `/api/v1/reports/:id/approve/` | 批准 |
| POST | `/api/v1/reports/:id/issue/` | 发放 |
| POST | `/api/v1/reports/:id/void/` | 作废 |
| GET | `/api/v1/reports/:id/preview/` | 预览 |
| GET | `/api/v1/reports/:id/download/` | 下载 |
| POST | `/api/v1/reports/:id/distribute/` | 发放登记 |
| GET | `/api/v1/reports/verify/:code/` | 二维码验证 |

### 6.5 资源管理

| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/v1/equipment/` | 设备 |
| GET | `/api/v1/equipment/expiring/` | 即将到期 |
| GET | `/api/v1/equipment/:id/traceability/` | 量值溯源 |
| CRUD | `/api/v1/equipment/:eid/calibrations/` | 校准记录 |
| CRUD | `/api/v1/equipment/:eid/period-checks/` | 期间核查 |
| CRUD | `/api/v1/equipment/:eid/maintenances/` | 维保记录 |
| GET | `/api/v1/equipment/:eid/usage-logs/` | 使用记录 |
| CRUD | `/api/v1/staff/profiles/` | 人员档案 |
| GET | `/api/v1/staff/profiles/expiring-certs/` | 到期证书 |
| CRUD | `/api/v1/staff/certificates/` | 资质证书 |
| CRUD | `/api/v1/staff/authorizations/` | 授权管理 |
| CRUD | `/api/v1/staff/trainings/` | 培训记录 |
| CRUD | `/api/v1/staff/evaluations/` | 能力评价 |
| CRUD | `/api/v1/environment/points/` | 监控点位 |
| POST | `/api/v1/environment/records/ingest/` | 数据采集 |
| CRUD | `/api/v1/environment/alarms/` | 报警记录 |
| POST | `/api/v1/environment/alarms/:id/resolve/` | 解除报警 |

### 6.6 质量与辅助

| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/v1/quality/audits/` | 内部审核 |
| CRUD | `/api/v1/quality/audit-findings/` | 审核发现 |
| CRUD | `/api/v1/quality/corrective-actions/` | 纠正措施 |
| CRUD | `/api/v1/quality/reviews/` | 管理评审 |
| CRUD | `/api/v1/quality/review-decisions/` | 评审决议 |
| CRUD | `/api/v1/quality/nonconformities/` | 不符合项 |
| CRUD | `/api/v1/quality/complaints/` | 投诉记录 |
| CRUD | `/api/v1/quality/proficiency-tests/` | 能力验证 |
| CRUD | `/api/v1/quality/supervisions/` | 质量监督 |
| CRUD | `/api/v1/standards/standards/` | 标准规范 |
| CRUD | `/api/v1/standards/validations/` | 方法验证 |
| CRUD | `/api/v1/consumables/suppliers/` | 供应商 |
| CRUD | `/api/v1/consumables/items/` | 耗材 |
| GET | `/api/v1/consumables/items/low-stock/` | 低库存 |
| CRUD | `/api/v1/consumables/in-records/` | 入库记录 |
| CRUD | `/api/v1/consumables/out-records/` | 出库记录 |

### 6.7 统计分析

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/statistics/dashboard/` | 仪表盘 |
| GET | `/api/v1/statistics/test-volume/` | 检测量 |
| GET | `/api/v1/statistics/qualification-rate/` | 合格率 |
| GET | `/api/v1/statistics/strength-curve/` | 强度曲线 |
| GET | `/api/v1/statistics/cycle-analysis/` | 周期分析 |
| GET | `/api/v1/statistics/workload/` | 工作量 |
| GET | `/api/v1/statistics/equipment-usage/` | 设备利用率 |

### 6.8 文档

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schema/` | OpenAPI Schema |
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/redoc/` | ReDoc |

---

## 7. 数据库模型速查表

| App | 模型 | 表名 | 继承 |
|-----|------|------|------|
| system | User | system_user | AbstractUser |
| system | Role | system_role | BaseModel |
| system | Permission | system_permission | BaseModel |
| system | AuditLog | system_auditlog | Model |
| projects | Project | projects_project | BaseModel |
| projects | Organization | projects_organization | BaseModel |
| projects | SubProject | projects_subproject | BaseModel |
| projects | Contract | projects_contract | BaseModel |
| projects | Witness | projects_witness | BaseModel |
| commissions | Commission | commissions_commission | BaseModel |
| commissions | CommissionItem | commissions_commissionitem | BaseModel |
| commissions | ContractReview | commissions_contractreview | BaseModel |
| samples | SampleGroup | samples_samplegroup | BaseModel |
| samples | Sample | samples_sample | BaseModel |
| samples | SampleDisposal | samples_sampledisposal | BaseModel |
| testing | TestCategory | testing_testcategory | BaseModel |
| testing | TestMethod | testing_testmethod | BaseModel |
| testing | TestParameter | testing_testparameter | BaseModel |
| testing | TestTask | testing_testtask | BaseModel |
| testing | RecordTemplate | testing_recordtemplate | BaseModel |
| testing | OriginalRecord | testing_originalrecord | BaseModel |
| testing | RecordRevision | testing_recordrevision | Model |
| testing | JudgmentRule | testing_judgmentrule | BaseModel |
| testing | TestResult | testing_testresult | BaseModel |
| reports | Report | reports_report | BaseModel |
| reports | ReportApproval | reports_reportapproval | BaseModel |
| reports | ReportDistribution | reports_reportdistribution | BaseModel |
| equipment | Equipment | equipment_equipment | BaseModel |
| equipment | Calibration | equipment_calibration | BaseModel |
| equipment | PeriodCheck | equipment_periodcheck | BaseModel |
| equipment | Maintenance | equipment_maintenance | BaseModel |
| equipment | EquipUsageLog | equipment_equipusagelog | BaseModel |
| staff | StaffProfile | staff_staffprofile | BaseModel |
| staff | Certificate | staff_certificate | BaseModel |
| staff | Authorization | staff_authorization | BaseModel |
| staff | Training | staff_training | BaseModel |
| staff | CompetencyEval | staff_competencyeval | BaseModel |
| environment | MonitoringPoint | environment_monitoringpoint | BaseModel |
| environment | EnvRecord | environment_envrecord | Model |
| environment | EnvAlarm | environment_envalarm | BaseModel |
| standards | Standard | standards_standard | BaseModel |
| standards | MethodValidation | standards_methodvalidation | BaseModel |
| quality | InternalAudit | quality_internalaudit | BaseModel |
| quality | AuditFinding | quality_auditfinding | BaseModel |
| quality | CorrectiveAction | quality_correctiveaction | BaseModel |
| quality | ManagementReview | quality_managementreview | BaseModel |
| quality | ReviewDecision | quality_reviewdecision | BaseModel |
| quality | NonConformity | quality_nonconformity | BaseModel |
| quality | Complaint | quality_complaint | BaseModel |
| quality | ProficiencyTest | quality_proficiencytest | BaseModel |
| quality | QualitySupervision | quality_qualitysupervision | BaseModel |
| consumables | Supplier | consumables_supplier | BaseModel |
| consumables | Consumable | consumables_consumable | BaseModel |
| consumables | ConsumableIn | consumables_consumablein | BaseModel |
| consumables | ConsumableOut | consumables_consumableout | BaseModel |

共计 **13 个 Django App**，**45+ 个数据模型**。

---

## 8. 项目目录结构

```
/workspace/
├── docker-compose.yml          # Docker 编排
├── PROJECT_STATUS.md            # 本文件
├── README.md                    # 项目说明
├── DEPLOY.md                    # 部署文档
├── docs/
│   ├── PLAN.md                  # 系统规划文档
│   └── TODO.md                  # 原始任务拆分
├── memory/                      # Agent 记忆文件
├── nginx/                       # Nginx 配置
│   └── nginx.conf
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── limis/                   # Django 项目配置
│   │   ├── settings/
│   │   │   ├── base.py          # 基础配置
│   │   │   ├── dev.py           # 开发环境
│   │   │   └── prod.py          # 生产环境
│   │   ├── urls.py              # 根 URL 路由
│   │   ├── celery.py            # Celery 配置
│   │   ├── wsgi.py / asgi.py
│   │   └── __init__.py
│   ├── core/                    # 公共基础模块
│   │   ├── models.py            # BaseModel
│   │   ├── views.py             # BaseModelViewSet
│   │   ├── serializers.py       # BaseModelSerializer
│   │   ├── permissions.py       # RBAC 权限类
│   │   ├── middleware.py        # AuditLog 中间件
│   │   ├── pagination.py        # 统一分页
│   │   ├── exceptions.py        # 统一异常处理
│   │   ├── filters.py           # 基础过滤器
│   │   └── utils/
│   │       ├── numbering.py     # 编号生成器
│   │       ├── barcode.py       # 二维码/条码
│   │       ├── export.py        # 导出工具
│   │       └── rounding.py      # 数值修约
│   └── apps/
│       ├── system/              # 用户/角色/权限/审计
│       ├── projects/            # 工程项目
│       ├── commissions/         # 委托管理
│       ├── samples/             # 样品管理
│       ├── testing/             # 检测（含 models/ formulas/ judgment.py）
│       ├── reports/             # 报告（含 workflow.py generator.py signature.py）
│       ├── equipment/           # 仪器设备
│       ├── staff/               # 人员管理
│       ├── environment/         # 环境监控
│       ├── standards/           # 标准规范
│       ├── quality/             # 质量体系（含 models/ 包）
│       ├── consumables/         # 耗材管理
│       └── statistics/          # 统计分析（纯 API）
├── frontend/
│   ├── package.json
│   ├── vite.config.ts           # Vite 配置（host: 0.0.0.0, port: 3000, /api 代理）
│   ├── Dockerfile
│   └── src/
│       ├── main.ts              # 入口
│       ├── App.vue              # 根组件
│       ├── router/
│       │   ├── index.ts         # 主路由（⚠️ testing/reports 未导入）
│       │   └── modules/         # 路由模块（13个文件）
│       ├── api/                 # API 接口层（13个文件）
│       ├── stores/              # Pinia（user.ts, dict.ts）
│       ├── types/               # TypeScript 类型（7个文件）
│       ├── utils/               # 工具函数（auth.ts, request.ts, permission.ts）
│       ├── components/
│       │   └── Layout/          # 布局组件（MainLayout, Sidebar, Header）
│       └── views/
│           ├── login/           # 登录页
│           ├── dashboard/       # 仪表盘
│           ├── system/          # 系统管理（6个文件，含3个空白stub）
│           ├── projects/        # 项目管理（2个文件）
│           ├── commissions/     # 委托管理（3个文件）
│           ├── samples/         # 样品管理（3个文件）
│           ├── testing/         # 检测管理（4个文件）⚠️ 路由未注册
│           ├── reports/         # 报告管理（2个文件）⚠️ 路由未注册
│           ├── equipment/       # 设备管理（2个文件）
│           ├── staff/           # 人员管理（2个文件）
│           ├── environment/     # 环境监控（1个文件）
│           ├── quality/         # 质量体系（3个文件）
│           ├── consumables/     # 耗材管理（1个文件）
│           ├── standards/       # 标准管理（1个文件）
│           └── placeholder/     # 占位页面（1个文件）
```

---

## 9. 启动与调试说明

### 9.1 环境准备

```bash
# 数据库
sudo systemctl start postgresql redis

# 后端虚拟环境（若 /opt/limis/venv 存在则 source 它，否则从 /workspace 创建）
cd /workspace/backend
python -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt

# 数据库初始化
export DB_PASSWORD=limis123 DB_HOST=127.0.0.1
python manage.py migrate
python manage.py createsuperuser  # 或用脚本创建

# 前端
cd /workspace/frontend
npm install
```

### 9.2 启动服务

```bash
# 后端（终端1）
cd /workspace/backend
source ../venv/bin/activate
export DB_PASSWORD=limis123 DB_HOST=127.0.0.1
python manage.py runserver 0.0.0.0:8000

# 前端（终端2）
cd /workspace/frontend
npm run dev
```

### 9.3 局域网访问

- 前端：`http://<服务器局域网IP>:3000`
- API 文档：`http://<服务器局域网IP>:8000/api/docs/`
- 确认 IP：`hostname -I | awk '{print $1}'`

---

## 10. 后续 Agent 开发规范

### 10.1 文档维护规则
- 本文件是多 Agent 协同开发的**唯一状态真实记录**
- 完成一个子任务后将 `[ ]` 改为 `[x]` 并注明日期
- 新发现的 Bug 按编号追加到第 4 节
- 每次开发前先读取此文件了解当前状态

### 10.2 开发优先级建议
1. **先修路由和菜单**（5.1 节，全部 P0），让所有已有页面都能正常访问
2. **再修 Bug**（4.1/4.2 节），确保核心流程跑通
3. **然后完善报告和检测模块**（5.3.1/5.3.2），这是业务核心价值
4. **最后做优化**（5.4 节），包括测试、部署、移动端

### 10.3 代码规范
- 后端：Django REST Framework ViewSet + Service 层分离
- 前端：Vue 3 Composition API + `<script setup>` + TypeScript
- API 命名：`/api/v1/<module>/<resource>/`，RESTful 风格
- 统一响应格式：`{code: 200, message: 'success', data: {...}}`（分页额外含 count/page/page_size/results）

---

*此文档由 AI 助手基于完整代码扫描自动生成，作为后续多 Agent 协同开发的权威参考。*
