# 委托单状态工作流

本文描述 **委托单（Commission）** 从草稿到评审结束的状态迁移、API 与页面入口，以及异常与回滚思路。

## 1. 状态定义

**模型**：`backend/apps/commissions/models.py` → `Commission.STATUS_CHOICES`

| 值 | 显示名 |
|----|--------|
| `draft` | 草稿 |
| `pending_review` | 待评审 |
| `reviewed` | 已评审 |
| `rejected` | 已退回 |
| `cancelled` | 已取消 |

## 2. 状态迁移（业务规则）

**服务层**：`backend/apps/commissions/services.py`

### 2.1 提交 `submit_commission`

```
前置：status == draft
    ↓
校验：至少一条 CommissionItem
    ↓
status → pending_review
```

### 2.2 评审 `review_commission`

```
前置：status == pending_review
    ↓
approved == True  → status = reviewed
approved == False → status = rejected
    ↓
记录 reviewer、review_date、review_comment
```

## 3. API 与权限

**视图**：`backend/apps/commissions/views.py` → `CommissionViewSet`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/commissions/commissions/` | CRUD | `lims_module = 'commission'` |
| `.../{id}/submit/` | POST | `submit` → `lims_action_map['submit'] = 'edit'` |
| `.../{id}/review/` | POST | `review` → `'approve'`（body: `approved`, `comment`） |

**注意**：评审动作需要 `commission` 模块的 **`approve`** 能力，而非普通 `edit`。

## 4. 前端页面

**路由模块**：`frontend/src/router/modules/commissions.ts`

| 路径 | 说明 | permission |
|------|------|------------|
| `/entrustment` | 列表 | `entrustment:list` |
| `/entrustment/create` | 新建 | `entrustment:create` |
| `/entrustment/:id` | 详情 | `entrustment:list` |
| `/entrustment/:id/edit` | 编辑 | `entrustment:edit` |

**组件**：`CommissionList.vue`、`CommissionForm.vue`、`CommissionDetail.vue`。

## 5. 文字流程图（端到端）

```
[接待] 新建委托 draft → 填写项目、明细项
    ↓
[接待] 提交 submit → pending_review
    ↓
[评审人] 评审 review → reviewed 或 rejected
    ↓
若 reviewed → 后续可关联样品、检测任务等业务（按实际模块）
```

**合同评审**：`ContractReview` 相关 API 在 `ContractReviewViewSet`（嵌套在 commission 下），`lims_module = 'commission'`。

## 6. 风险与回滚

| 风险 | 说明 |
|------|------|
| 无明细提交 | 服务端拒绝；需前端同步校验提升体验 |
| 并发评审 | `select_for_update` 在扩展前应评估 |
| 误评审 | 业务上可能需「重新打开草稿」流程——若代码未实现则需线下审批 + DB 修复 |

**数据回滚**：将 `status` 与评审字段改回需 **权限与制度授权**；优先通过正规业务流（若产品支持）。

## 7. 相关路径

- `backend/apps/commissions/models.py`
- `backend/apps/commissions/services.py`
- `backend/apps/commissions/views.py`
- `frontend/src/router/modules/commissions.ts`
- `frontend/src/views/commissions/*.vue`
