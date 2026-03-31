# RBAC 与菜单路由

本文说明 **后端基于模块的 RBAC** 与 **前端路由 + 侧边栏菜单** 如何协同，并给出路径对照。

## 1. 后端 RBAC

**核心类**：`LimsModulePermission`（`backend/core/permissions.py`）

- ViewSet 设置 `lims_module`（如 `'system'`、`'commission'`）。
- HTTP 方法映射到 `action`：`GET`→`view`，`POST`→`create`，`PUT/PATCH`→`edit`，`DELETE`→`delete`。
- `@action` 可通过 `lims_action_map` 覆盖（如 `review`→`approve`）。

**数据模型**：`Permission` 表字段 `module`、`action`、**`code`**（唯一，供前端使用）。

**用户权限列表**：`get_user_permissions` 返回所有关联 `Permission.code`（`backend/apps/system/services.py`）。

## 2. 前端路由权限

**入口**：`frontend/src/router/index.ts`

- `beforeEach`：`ensureProfile()` 后检查 `getRoutePermission` → `canAccessRoutePermission`。
- 各子模块在 `frontend/src/router/modules/*.ts` 中为路由设置 `meta: { permission: '...' }`。

**示例**（系统管理）：

| 路径 | permission |
|------|------------|
| `/system/users` | `system:user:list` |
| `/system/roles` | `system:role:list` |
| `/system/audit-logs` | `system:audit:list` |

文件：`frontend/src/router/modules/system.ts`。

## 3. 侧边栏菜单

**文件**：`frontend/src/components/Layout/Sidebar.vue`

- `rawMenuItems` 定义树形菜单（业务、检测、报告、质量体系、系统管理等）。
- `filterMenuItem` 递归：对叶子 `index` 用 `router.resolve` 取匹配路由，再用 `getRoutePermission` + `canAccessRoutePermission` 过滤。

**结论**：菜单可见性 **完全依赖** 与叶子路径对应的路由 `meta.permission`，与后端 API 的 `lims_module` **无自动映射**，需数据上保证 `Permission.code` 与路由一致。

## 4. 指令级控制

**文件**：`frontend/src/utils/permission.ts`

- `vPermission`：无权限时移除 DOM 元素。
- **注意**：仅 UI 隐藏，不能替代后端校验。

## 5. 文字流程：用户登录后加载权限

```
登录成功 → 存 access/refresh
    ↓
进入受保护路由 → ensureProfile
    ↓
GET /api/v1/system/me/ → permissions[], roles[]
    ↓
路由守卫比对 meta.permission
    ↓
Sidebar 过滤无权限叶子菜单
```

## 6. 风险与回滚

| 风险 | 处理 |
|------|------|
| code 不一致 | 建立权限对照表；发版前脚本校验 |
| 超级用户依赖 | 生产减少超管；用角色模拟验收 |

**回滚**：恢复 `Permission` 数据或前端路由上一版本；无需改 JWT 机制。

## 7. 相关代码路径

- `backend/core/permissions.py`
- `backend/apps/system/models.py`、`services.py`
- `frontend/src/router/index.ts`、`router/modules/*.ts`
- `frontend/src/components/Layout/Sidebar.vue`
- `frontend/src/stores/user.ts`
