# 权限模型与故障排查

本文说明 **后端 API 权限** 与 **前端路由权限** 的两套体系如何对齐，以及常见 403/菜单消失问题的排查步骤。

## 1. 后端：`LimsModulePermission`

**文件**：`backend/core/permissions.py`

**逻辑概要**：

1. 未登录 → 拒绝。
2. `is_superuser` → 允许。
3. ViewSet 未设置 `lims_module` → **仅登录即可**（兼容旧接口）。
4. 已设置 `lims_module`（如 `'system'`、`'commission'`）：
   - 默认将 HTTP 方法映射为 `view` / `create` / `edit` / `delete`。
   - 自定义 `@action` 可通过 `lims_action_map` 映射到某一 `action`（如 `submit` → `edit`）。

**判定**：`User.has_lims_permission(module, action)` → 查询 `Permission` 表中是否存在对应 `module` + `action`，且用户任一角色关联。

**示例**（委托评审）：

- `CommissionViewSet.lims_module = 'commission'`
- `review` 动作映射为 `approve`：`lims_action_map = {'submit': 'edit', 'review': 'approve'}`  
  **代码**：`backend/apps/commissions/views.py`

## 2. 前端：路由 `meta.permission`

**文件**：`frontend/src/router/index.ts` 守卫逻辑：

1. 非公开页需登录（本地 `access_token`）。
2. `userStore.ensureProfile()` 拉取 `/api/v1/system/me/`。
3. `getRoutePermission` 从最深匹配路由取 `meta.permission`。
4. `canAccessRoutePermission`：若未定义 permission 则**放行**；否则检查 `permissions` 数组是否包含该字符串或 `*`。

**权限数据来源**：`/me` 返回的 `permissions` 为数据库 `Permission.code` 列表（超级用户为全部 code）。

## 3. 两套体系对齐检查表

| 检查项 | 后端 | 前端 |
|--------|------|------|
| 模块名 | `Permission.module` + `action` | 无直接对应，靠 **code** 字符串 |
| 列表页 | `GET` → `view` | `meta.permission` 如 `commission:...` 需与 **code** 一致 |
| 自定义动作 | `lims_action_map` | 若仅控制按钮，可用 `vPermission` 指令 |

**常见不一致**：前端使用 `entrustment:list`，后端 `Permission.code` 若登记为别的字符串 → 菜单被过滤或接口 403。

## 4. 故障排查流程（文字图）

```
现象：点击菜单提示「无权访问该页面」或接口 403
    ↓
[1] 浏览器 Network 查看 /api/v1/system/me/ 是否 200
    - 401 → Token 过期/被踢 → 重新登录
    ↓
[2] 响应体 permissions 是否包含当前路由 meta.permission
    - 不包含 → 角色未分配对应 Permission 行
    ↓
[3] 接口 403 但菜单能进 → 后端 ViewSet lims_module/action 与前端不一致
    - 对比 views.py 的 module 与 Permission 表
    ↓
[4] 仅超级用户正常 → 检查 is_superuser 与 Permission 种子是否完整
```

## 5. Django `has_perm` 与报告工作流

报告编制/审核/批准在 `backend/apps/reports/workflow.py` 中使用 `user.has_perm('reports.compile_report')` 等 **Django 默认权限**，与 `LimsModulePermission` 的 `Permission` 表是 **不同机制**。若需统一，需在数据迁移或自定义 `User.has_perm` 中桥接（当前代码以 `has_perm` 为准）。

**排查报告流程失败时**：除 `Permission` 表外，还需检查 Django `auth_permission` / 用户组是否分配了 `reports.*` 权限。

## 6. 风险

| 风险 | 说明 |
|------|------|
| 路由未设置 permission | 任何登录用户可访问该页（依赖后端再拦） |
| 仅前端隐藏 | 恶意直接调 API 仍可能操作 → 必须以服务端为准 |
| code 拼写错误 | 难以肉眼发现 → 建议以数据库导出或单元测试校验 |

## 7. 回滚

- **误改角色权限**：通过 `assign-permissions` 恢复上一组 permission id（事先导出 JSON）。
- **误删 Permission 行**：从备份恢复或重新运行种子命令（注意 `unique_together` on module+action）。

## 8. 相关路径

- `backend/core/permissions.py`
- `frontend/src/utils/permission.ts`
- `frontend/src/router/modules/*.ts`（各业务模块 permission 字符串）
