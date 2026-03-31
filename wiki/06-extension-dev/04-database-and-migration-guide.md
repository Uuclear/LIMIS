# 数据库与迁移指南（PostgreSQL）

LIMIS 使用 **PostgreSQL**，引擎配置在 **`backend/limis/settings/base.py`** 的 `DATABASES['default']`，连接参数来自环境变量：

| 变量 | 含义 | 默认（示例） |
|------|------|----------------|
| `DB_NAME` | 数据库名 | `limis` |
| `DB_USER` | 用户 | `limis` |
| `DB_PASSWORD` | 密码 | 空字符串（生产必须设置） |
| `DB_HOST` | 主机 | `db`（Compose 内） |
| `DB_PORT` | 端口 | `5432` |

本地 Docker 映射宿主机时常见 **`DB_PORT=5434`**（见 `docker-compose.yml`）。

---

## 迁移工作流

在 **`backend`** 目录、激活虚拟环境后：

```bash
export DJANGO_SETTINGS_MODULE=limis.settings.dev  # 或生产 settings
python manage.py makemigrations <app_label>
python manage.py migrate
```

### 提交前检查

CI 会执行：

```bash
python manage.py makemigrations --check
python manage.py migrate --noinput
```

若 **`makemigrations --check`** 失败，说明模型与迁移不一致，需补交迁移文件。

---

## 规范

1. **禁止** 直接在生产手工改库结构而不迁移；例外情况需补迁移并文档化。
2. 迁移文件纳入版本控制；合并冲突时谨慎处理，必要时本地重建迁移（仅限未发布分支）。
3. 大数据量迁移：使用 `RunPython` 时分批提交，避免长时间锁表；可配合维护窗口。
4. 索引与约束：优先在 `Meta.indexes`、`UniqueConstraint` 中声明，让 Django 生成迁移。

---

## 软删除

多个模型继承 **`core.models.BaseModel`**，含 `is_deleted` 等字段时：

- **查询**：`BaseModelViewSet.get_queryset()` 默认过滤 `is_deleted=False`。
- **删除**：`destroy` 调用实例 `soft_delete()` 若存在。

新增实体若需软删，与现有模式保持一致，避免物理删除业务主表。

---

## Redis 与 JWT 黑名单

Redis 用于：

- Django **缓存**（`CACHES['default']` → `REDIS_URL`）
- **Celery** broker/result
- **JWT 黑名单**（simplejwt blacklist 应用）

数据库迁移与 Redis 无直接 DDL 关系，但部署新环境时需同时保证 Redis 可用，否则黑名单与缓存功能异常。

---

## 备份与恢复（运维向）

生产应定期对 PostgreSQL 做逻辑或物理备份；恢复流程按运维规范执行，并在恢复后验证迁移版本：

```bash
python manage.py showmigrations
```

---

## 常见问题

| 现象 | 可能原因 |
|------|----------|
| `relation does not exist` | 未执行 `migrate` 或连错库 |
| 迁移冲突 | 多人改同一 app，需合并迁移 |
| 连接拒绝 | `DB_HOST`/`DB_PORT` 或防火墙错误 |

---

## 种子数据

演示/测试数据通过 **`management commands`** 注入，例如 `seed_*`、`lims_demo_seeder` 等（位于 `apps/system/management/commands/`）。仅用于开发或演示环境，生产使用需评估数据安全与合规。
