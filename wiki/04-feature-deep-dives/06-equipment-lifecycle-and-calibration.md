# 仪器设备生命周期与校准

本文基于 `equipment` 应用模型说明设备状态、校准记录与前端入口。

## 1. 设备模型

**文件**：`backend/apps/equipment/models.py` → `Equipment`

| 字段组 | 说明 |
|--------|------|
| 标识 | `name`、`model_no`、`serial_no`、**`manage_no`（唯一管理编号）** |
| 分类 | `category`：A/B/C 类 |
| 状态 `status` | `in_use`、`stopped`、`calibrating`、`scrapped` |
| 校准 | `calibration_cycle`（月）、`next_calibration_date` |

## 2. 校准记录

**模型**：`Calibration`（同文件）

- 关联 `Equipment`
- `CONCLUSION_CHOICES`：`qualified` / `unqualified` / `limited`
- 具体字段（证书编号、机构等）见模型定义全文。

## 3. 生命周期（文字图）

```
采购入库 → in_use
    ↓
到期送检 → calibrating（可选状态，依业务录入习惯）
    ↓
校准结论 qualified → 回到 in_use，更新 next_calibration_date
    ↓
停用 stopped / 报废 scrapped
```

**通知类型**：系统通知枚举含 `equipment_expiring`（`Notification.TYPES` in `system/models.py`），用于即将到检提醒（具体触发逻辑以任务/服务为准）。

## 4. 前端页面

**路由**：`frontend/src/router/modules/equipment.ts`（若存在；侧边栏指向 `/equipment`）。

**视图**：`frontend/src/views/equipment/EquipmentList.vue`、`EquipmentDetail.vue`。

**API**：`frontend/src/api/equipment.ts` → `backend/apps/equipment/views.py`。

## 5. 风险与回滚

| 风险 | 说明 |
|------|------|
| 超期仍使用 | 需流程上锁定任务分配时校验设备有效期（若已实现于 `testing` 服务则一并排查） |
| 管理编号冲突 | DB 唯一约束；导入数据时注意 |

**回滚**：修正 `Calibration` 或 `Equipment` 记录；重大错误用数据库快照恢复。

## 6. 相关路径

- `backend/apps/equipment/models.py`
- `backend/apps/equipment/views.py`
- `backend/apps/equipment/services.py`
- `frontend/src/views/equipment/`
