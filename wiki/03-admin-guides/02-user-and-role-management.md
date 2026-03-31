# 用户与角色管理

本页说明 LIMIS 中 **用户（User）**、**角色（Role）**、**权限（Permission）** 的关系，以及管理界面与 API、数据库的对应关系。

## 1. 概念模型

```
User (system.User)
  └─ M2M ─→ Role (system.Role)
              └─ M2M ─→ Permission (system.Permission)
```

- **超级用户** `is_superuser=True`：绕过 `LimsModulePermission` 的模块校验（见 `backend/core/permissions.py`）。
- **普通用户**：通过角色关联的 `Permission` 行（`module` + `action`）判定是否允许操作。

**代码位置**：`backend/apps/system/models.py`（`User`、`Role`、`Permission`）。

## 2. 页面与路由

| 功能 | 前端路径 | 路由模块文件 |
|------|----------|----------------|
| 用户列表/维护 | `/system/users` | `frontend/src/router/modules/system.ts` |
| 角色列表/分配权限 | `/system/roles` | 同上 |
| 登录 | `/login` | `frontend/src/router/index.ts` |

**菜单**：侧边栏在 `frontend/src/components/Layout/Sidebar.vue` 的 `rawMenuItems` 中定义；子项通过 `router.resolve` 与 `getRoutePermission` 过滤，无权限则不显示。

## 3. API 端点（前缀 `/api/v1/system/`）

| 资源 | 方法 | 说明 |
|------|------|------|
| `users/` | GET/POST/PUT/PATCH/DELETE | CRUD；`lims_module = 'system'` |
| `users/{id}/reset-password/` | POST | 管理员重置密码（最少 8 位） |
| `users/{id}/toggle-active/` | POST | 启用/禁用 |
| `users/{id}/kickout-sessions/` | POST | 会话版本 +1，使 JWT 失效 |
| `roles/` | CRUD | 角色维护 |
| `roles/{id}/assign-permissions/` | POST | body: `{ "permissions": [id, ...] }` |
| `permissions/` | GET | 权限列表 |
| `permissions/grouped/` | GET | 按 `module` 分组 |
| `me/` | GET | 当前用户 + `permissions` 列表 |

**实现**：`backend/apps/system/views.py`（`UserViewSet`、`RoleViewSet`、`PermissionViewSet`、`CurrentUserView`）。

## 4. 操作流程（文字流程图）

### 4.1 新建用户并分配角色

```
[管理员] 打开 用户管理 /system/users
    ↓
点击新建 → 填写用户名、姓名、初始密码、部门等
    ↓
选择角色（多选）→ 提交
    ↓
后端 UserCreateSerializer + services.create_user
    ↓
用户首次登录 → 建议强制改密（制度层面；技术可选实现）
```

### 4.2 调整角色权限

```
[管理员] 打开 角色管理 /system/roles
    ↓
编辑目标角色 → 勾选 Permission 行
    ↓
保存 → assign-permissions 或序列化器更新
    ↓
已登录用户：需重新拉取 /me 或重新登录，前端 permissions 才更新
    （JWT 内不含业务权限列表，权限来自 CurrentUserView）
```

**注意**：前端路由 `meta.permission`（如 `system:user:list`）必须与后端 `Permission.code` **一致**，否则菜单可见但接口 403 或反之。详见 `03-permission-model-and-troubleshooting.md`。

## 5. 预置角色编码（Role.code）

在 `Role` 模型中定义了 `ROLE_CHOICES`，例如：`admin`、`tech_director`、`tester`、`sample_clerk` 等（`backend/apps/system/models.py`）。种子数据可能通过 `seed_*` 管理命令导入（见 `08-data-migration-and-seeding.md`）。

## 6. 风险与回滚

| 操作 | 风险 | 缓解 / 回滚 |
|------|------|-------------|
| 禁用用户 | 业务中断 | 立即 `toggle-active` 恢复；记录审计 |
| 误删角色 | 用户无权限 | 从备份恢复 `Role`/`Permission` M2M；或重建角色并重新分配 |
| 超级用户滥用 | 越权 | 最小化超管数量；审计 + 双因素（若外接） |

## 7. 相关代码路径

- 后端权限聚合：`backend/apps/system/services.py` → `get_user_permissions`、`has_permission`
- 前端权限与指令：`frontend/src/utils/permission.ts`、`vPermission`
- 用户 Store：`frontend/src/stores/user.ts`
