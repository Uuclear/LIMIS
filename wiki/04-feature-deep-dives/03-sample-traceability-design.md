# 样品可追溯性设计

本文从 **数据模型** 说明样品从委托到留样/处置的追溯链路，并标注代码与页面位置。

## 1. 核心实体

**文件**：`backend/apps/samples/models.py`

| 模型 | 作用 |
|------|------|
| `SampleGroup` | 组样（`group_no`） |
| `Sample` | 单件样品（`sample_no`、`blind_no` 等） |
| `SampleDisposal` | 处置记录（退还/销毁/丢弃等） |

## 2. 关键外键与追溯链

```
Project（工程）
    ↓
Commission（委托单 commission_no）
    ↓
Sample（sample_no, commission_id）
    ├─ 可选 SampleGroup（组样）
    └─ SampleDisposal（多条处置历史）
```

**业务含义**：

- 由 `Sample.commission` 可追溯到 **委托单** → **项目**。
- `blind_no` 支持盲样管理（唯一约束允许 null）。
- `status`：`pending` / `testing` / `tested` / `retained` / `disposed` / `returned`。

## 3. 属性与辅助逻辑

- `Sample.project`：property，经 `commission.project` 访问。
- `is_overdue_retention`：留样超期判断（`status == retained` 且日期过线）。

## 4. 前端入口

**路由模块**：`frontend/src/router/modules/samples.ts`

| 路径 | permission |
|------|------------|
| `/sample` | `sample:list` |
| `/sample/register` | `sample:create` |
| `/sample/:id` | `sample:list` |

**视图**：`SampleList.vue`、`SampleRegister.vue`、`SampleDetail.vue`（目录 `frontend/src/views/samples/`）。

**API**：`frontend/src/api/samples.ts` → `backend/apps/samples/views.py`。

## 5. 文字流程：收样到处置

```
委托评审通过 → 创建/关联样品
    ↓
检测中 status=testing → tested
    ↓
留样 retained + retention_deadline
    ↓
到期处置 → SampleDisposal 记录 → disposed / returned 等
```

## 6. 风险与合规

| 风险 | 建议 |
|------|------|
| 编号唯一性冲突 | 依赖 DB 唯一约束；并发创建需重试策略 |
| 盲样泄露 | 权限控制 `blind_no` 可见范围（若需细化应扩展模型或字段级权限） |
| 追溯断裂 | 禁止硬删委托；使用软删或状态约束 |

## 7. 回滚

删除样品或委托可能导致 **级联删除**（`on_delete=CASCADE`）；生产应禁用硬删或改为软删策略（若后续迭代提供）。

## 8. 相关路径

- `backend/apps/samples/models.py`
- `backend/apps/samples/views.py`
- `frontend/src/views/samples/`
- `frontend/src/api/samples.ts`
