# 检测原始记录模板合并

本文说明 **按检测任务合并多个原始记录模板 schema** 的规则，对应 API 与实现文件。

## 1. 功能概述

对某一 **检测任务（TestTask）**，系统根据 **检测方法（TestMethod）** 与 **检测参数（TestParameter）** 解析应使用的 `RecordTemplate`，并将多个模板中的 `fields` **合并** 为前端表单可用的结构。

**核心函数**：`build_merged_record_schema_for_task`  
**文件**：`backend/apps/testing/services.py`

## 2. 合并规则（逻辑摘要）

```
加载任务 → select_related(test_method, test_parameter)
    ↓
解析参数列表 param_qs：
    - 若任务指定 test_parameter_id → 仅该参数
    - 否则该方法下全部未删除参数
    ↓
若无参数：
    → 取「方法级」模板（test_parameter 为空）最新激活模板
    ↓
若有参数：
    对每个参数：
        优先：该方法 + 该参数 的激活模板
        回退：该方法 + 无参数 的通用模板
    ↓
输出：
    - sections[]：每参数一段 schema
    - merged_fields.fields[]：将所有字段打平并附 _parameter_id / _parameter_name
```

## 3. API

**视图**：`backend/apps/testing/views.py` → `TestTaskViewSet`

- `@action(detail=True, methods=['get'], url_path='merged-record-schema')`
- 内部调用 `services.build_merged_record_schema_for_task(int(pk))`
- `lims_action_map` 含 `'merged_record_schema': 'view'`

**请求示例**：`GET /api/v1/testing/tasks/{id}/merged-record-schema/`

## 4. 与资质/模板的约束

同文件中可见与 **`QualificationProfile`**、**`allowed_record_templates`** 相关的过滤（具体以 `views.py` 查询为准），用于限制某类任务可选模板范围。

## 5. 前端

**检测任务**：`frontend/src/views/testing/tasks/TaskDetail.vue`（合并 schema 展示/填录入口常见于此）。

**原始记录**：`RecordForm.vue`、`RecordList.vue`（`frontend/src/views/testing/records/`）。

## 6. 风险与回滚

| 风险 | 说明 |
|------|------|
| 字段名冲突 | 合并打平时依赖模板设计；冲突时后者覆盖或需人工调整模板 JSON |
| 模板未激活 | 回退到方法级；再无则空 schema |
| 性能 | 参数极多时 sections 很大 → 考虑缓存或分页填录（产品层） |

**回滚**：恢复模板库数据或任务上的 `test_parameter` 指定；无需改代码。

## 7. 相关路径

- `backend/apps/testing/services.py`（`build_merged_record_schema_for_task`）
- `backend/apps/testing/views.py`
- `backend/apps/testing/models/record.py`（`RecordTemplate`、`Record`）
- `frontend/src/views/testing/tasks/TaskDetail.vue`
- `frontend/src/views/testing/records/RecordForm.vue`
