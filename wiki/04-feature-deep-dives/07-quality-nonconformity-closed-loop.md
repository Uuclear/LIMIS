# 质量不符合项闭环

本文说明 **不符合项（NonConformity）** 与关联能力 **投诉（Complaint）** 的数据结构、状态及质量体系菜单入口。

## 1. 不符合项模型

**文件**：`backend/apps/quality/models/nonconformity.py` → `NonConformity`

| 字段 | 说明 |
|------|------|
| `nc_no` | 唯一编号 |
| `source` | 来源：`internal` / `audit` / `complaint` / `proficiency` / `other` |
| `description` | 描述 |
| `impact_assessment` | 影响评价 |
| `corrective_action` | 纠正措施 |
| `responsible_person` | 责任人（FK User） |
| `status` | `open` → `in_progress` → `closed` |
| `close_date` | 关闭日期 |

## 2. 闭环文字流程

```
发现（内审/外审/投诉等）→ 登记 NonConformity (open)
    ↓
分析影响 + 制定纠正措施 (in_progress)
    ↓
验证有效 → closed + close_date
```

**说明**：具体审批流是否在 ViewSet 层强制，以 `backend/apps/quality/views.py` 为准；本仓库模型层提供状态字段支撑闭环。

## 3. 投诉

**模型**：`Complaint`（同文件）

- `complaint_no`、`complainant`、`complaint_date`、`content`
- `status`：`received` → `investigating` → `resolved` → `closed`

可与不符合项在业务上关联（若需 FK，以后续迭代为准；当前为独立实体）。

## 4. 前端入口

**路由模块**：`frontend/src/router/modules/quality.ts`

**侧边栏**：`Sidebar.vue` → 质量体系 → **不符合项** `/quality/nonconformity`。

**API**：`backend/apps/quality/urls.py` 注册 `nonconformities` ViewSet（basename `nonconformity`）。

## 5. 风险与回滚

| 风险 | 说明 |
|------|------|
| 编号唯一 | 并发创建需服务端生成策略（若存在编号生成器） |
| 未关闭项积压 | 管理报表与提醒（依赖统计模块或导出） |

**回滚**：状态回退需授权；删除记录可能影响追溯，建议「作废」态而非物理删除。

## 6. 相关路径

- `backend/apps/quality/models/nonconformity.py`
- `backend/apps/quality/views.py`
- `backend/apps/quality/urls.py`
- `frontend/src/router/modules/quality.ts`
- `frontend/src/views/quality/`（不符合项列表页面以实际文件名准）
