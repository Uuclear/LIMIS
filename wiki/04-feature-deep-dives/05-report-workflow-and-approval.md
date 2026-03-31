# 报告工作流与审批

本文描述 **报告（Report）** 从草稿到发放/作废的状态机、**Django 权限** 校验点，以及 API 与页面位置。

## 1. 工作流函数

**文件**：`backend/apps/reports/workflow.py`

| 函数 | 前置状态 | 结果状态 | 权限检查 |
|------|----------|----------|----------|
| `submit_for_audit` | `draft` | `pending_audit` | `reports.compile_report`（角色 `compile`） |
| `audit_report` | `pending_audit` | 通过→`pending_approve`；驳回→`draft` | `reports.audit_report`（`audit`） |
| `approve_report` | `pending_approve` | 通过→`approved`；驳回→`pending_audit` | `reports.approve_report`（`approve`） |
| `issue_report` | `approved` | `issued` | （函数内未重复 `_check_permission`，以视图层为准） |
| `void_report` | 非 `voided` | `voided` | 写入审批轨迹 |

**幂等**：若目标状态已达成，直接返回当前 `report`（避免重复 `select_for_update` 副作用）。

**审计**：各步骤调用 `log_business_event`（`core/audit.py`），`AuditLog.method = BIZ_EVENT`。

## 2. 状态迁移文字图

```
draft
  → submit_for_audit → pending_audit
        ↓ audit (pass)
pending_approve
        ↓ approve (pass)
approved
        ↓ issue_report
issued

分支：
  pending_audit + audit(reject) → draft
  pending_approve + approve(reject) → pending_audit
  任意(除 voided) + void_report → voided
```

## 3. 权限模型说明

工作流使用 **`user.has_perm('reports.xxx')`**（Django 内置权限名），与 `LimsModulePermission` 的 `Permission` 表 **不是同一套**，运维需在 **Django Admin** 或数据迁移中为用户/组分配 `reports` app 的权限。

**映射**（`workflow._check_permission`）：

- `compile` → `reports.compile_report`
- `audit` → `reports.audit_report`
- `approve` → `reports.approve_report`

## 4. API 与路由

**后端**：`backend/apps/reports/views.py`、`urls.py`（注册在 `/api/v1/reports/` 下）。

典型动作（以实际路由为准）：

- `submit_audit`、`audit`、`approve`、`issue`、`void` 等 `@action`

**前端**：

- 路由：`frontend/src/router/modules/reports.ts`
- 页面：`ReportList.vue`、`ReportDetail.vue`

**侧边栏**：`Sidebar.vue` → 报告管理 → `/reports`。

## 5. 数据库痕迹

**模型**：`ReportApproval`（`workflow._create_approval` 写入角色、动作、意见、签名人等）。

**索引**：见 `backend/apps/reports/migrations/0004_reportapproval_indexes.py`。

## 6. 风险与回滚

| 风险 | 说明 |
|------|------|
| 权限未配置 | 接口 `PermissionDenied`；需在 Django 权限中分配 |
| 并发审批 | 依赖 `select_for_update`；同状态重复请求幂等返回 |
| 作废不可恢复 | `voided` 后业务上应禁止再发放 |

**回滚**：无自动业务回滚；若误操作需 **制度授权** 下数据库修复并补审计说明。

## 7. 相关路径

- `backend/apps/reports/workflow.py`
- `backend/apps/reports/models.py`
- `backend/apps/reports/views.py`
- `frontend/src/views/reports/`
- `core/audit.py`
