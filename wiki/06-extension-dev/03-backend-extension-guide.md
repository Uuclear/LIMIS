# 后端扩展指南（Django + DRF）

## 应用布局

业务代码位于 **`backend/apps/`** 下，每个 Django app 通常包含：

| 文件/目录 | 说明 |
|-----------|------|
| `models.py` 或 `models/` | 领域模型 |
| `serializers.py` | DRF 序列化器 |
| `views.py` | ViewSet / APIView |
| `urls.py` | 路由注册 |
| `filters.py` | `django-filter` 过滤（可选） |
| `services.py` | 复杂业务逻辑（推荐从视图剥离） |
| `migrations/` | 数据库迁移 |

根 URL 将各 app 挂到 **`/api/v1/`**（`backend/limis/urls.py`）。

---

## 基类与权限

### `BaseModelViewSet`（`core.views`）

多数业务资源继承 **`BaseModelViewSet`**，自动具备：

- 分页：`StandardPagination`（信封列表）
- 权限：`IsAuthenticated` + **`LimsModulePermission`**
- **软删除**：若模型含 `is_deleted` / `soft_delete`，默认 queryset 过滤未删除；`destroy` 优先软删
- **写响应信封**：`create` → 201 + `message`；`update` → 200 + `data`；`destroy` → 200 + 固定 `message`

新建 ViewSet 时设置：

```python
class FooViewSet(BaseModelViewSet):
    queryset = Foo.objects.all()
    serializer_class = FooSerializer
    lims_module = 'your_module'  # 与权限配置一致
```

按需增加：`filterset_class`、`search_fields`、`ordering_fields`、`lims_action_map`（自定义 `@action` 的权限映射）。

### 权限模型

- **`LimsModulePermission`**：按模块 + 动作（`view` / `create` / `edit` / `delete`）校验，超级用户直通。
- 未设置 `lims_module` 时仅要求登录（兼容旧接口）。

权限数据来自 **`system`** 应用中的 Role / Permission 及用户关联（详见管理端文档）。

---

## 序列化与审计字段

- 公共基类见 **`core.serializers`**（如 `CreatedByMixin` 自动填创建人）。
- 保持字段 **snake_case** 输出，与前端 `apiField` 约定一致。

---

## 自定义接口示例

**只读统计或报表**可用 **`APIView`**，返回体建议统一为：

```python
return Response({'code': 200, 'data': payload})
```

与 `statistics` 应用风格一致，便于前端拦截器解包。

**自定义 `@action`** 若返回 200，可按业务选择信封或裸数据；同一模块内建议风格一致。

---

## 中间件（全局行为）

- **`IdempotencyMiddleware`**：`Idempotency-Key` 处理（仅 `/api/v1/` 下写方法）。
- **`AuditLogMiddleware`**：记录写操作审计（登录/刷新跳过 body 记录）。

新增敏感路径时评估是否加入审计 `SKIP_PATHS`。

---

## 认证

默认 **`SessionVersionJWTAuthentication`**：JWT 中 **`sv`** 必须与 `User.session_version` 一致。踢出会话、改密等场景注意是否使令牌失效。

---

## 第三方与异步

- **Celery**：`celery -A limis worker`，broker/backend 使用 **`REDIS_URL`**（`base.py`）。
- **MinIO**：附件上传等通过 `MINIO_*` 环境变量配置。
- **WeasyPrint / 文档**：见各业务 `services`。

---

## 管理命令

`backend/apps/system/management/commands/` 下提供演示数据、同步脚本等。新增命令：

```bash
python manage.py your_command
```

---

## 提交流程建议

1. **迁移**：模型变更必须包含迁移文件；提交前在干净库执行 `migrate`。
2. **权限**：新模块在权限种子或后台中配置对应 `Permission`，与 `lims_module` 对齐。
3. **API 契约**：若影响前端，更新 OpenAPI（drf-spectacular 多数可自动反映）并在 MR 说明破坏性变更。
4. **安全**：避免在日志/审计中输出密码与令牌；敏感操作用 `@transaction.atomic`。

---

## 参考路径

| 内容 | 路径 |
|------|------|
| 设置 | `backend/limis/settings/base.py` |
| 异常与业务错误 | `backend/core/exceptions.py` |
| 基类 ViewSet | `backend/core/views.py` |
| 权限 | `backend/core/permissions.py` |
