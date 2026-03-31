# 数据迁移与种子数据

本文说明 **Django 迁移** 与仓库内 **管理命令种子** 的用途、执行顺序建议及风险。

## 1. 数据库迁移

**命令**：`python manage.py migrate`（`DJANGO_SETTINGS_MODULE` 指向目标环境）

**位置**：各 app 下 `migrations/`（如 `backend/apps/system/migrations/`）。

**注意**：

- `AUTH_USER_MODEL = system.User` 已定型，勿随意删改早期迁移。
- `rest_framework_simplejwt.token_blacklist` 需迁移以支持 refresh 黑名单。

## 2. 种子与演示脚本（仓库内示例）

以下路径为 **代码库中实际存在的管理命令**（`backend/apps/system/management/commands/` 等），名称以仓库为准：

| 命令/模块 | 用途（概括） |
|-----------|----------------|
| `seed_airport_lab_demo.py` | 机场实验室类演示数据 |
| `seed_site_lab_commercial_pack.py` | 站点/商业打包种子 |
| `seed_role_test_users.py` | 角色与测试用户 |
| `seed_full_workflow.py` | 全流程演示 |
| `lims_demo_seeder.py` / `lims_demo_clear.py` | 演示数据填充与清理 |

**执行示例**：

```bash
cd /opt/limis/backend
PYTHONPATH=. DJANGO_SETTINGS_MODULE=limis.settings.dev python manage.py <command_name>
```

（具体参数以各命令 `add_arguments` 为准。）

## 3. 推荐流程（文字图）

```
新环境部署
    ↓
配置环境变量与数据库
    ↓
migrate
    ↓
（可选）创建超级用户 createsuperuser
    ↓
（可选）导入权限/角色种子 → 再导入业务种子
    ↓
验证登录与关键业务流程
```

## 4. 与工标网/标准同步

`sync_pudong_t4_standards.py`（若存在）用于标准数据同步场景，执行前确认 **外部数据源与合规要求**。

## 5. 风险与回滚

| 风险 | 说明 | 建议 |
|------|------|------|
| 生产误跑 demo seed | 污染真实数据 | 生产禁用此类命令或加 `--confirm` |
| 迁移不可逆 | 字段删除类迁移 | 发版前备份；大表迁移维护窗口 |
| 跨环境迁移文件不一致 | 分支合并冲突 | 仅保留一条迁移链，团队规范 rebase |

**回滚**：

- **数据**：用迁移前 **PostgreSQL 快照** 恢复最可靠。
- **代码**：回退到上一 Git tag 并重新 migrate（仅当迁移未破坏性时）。

## 6. 相关路径

- `backend/apps/system/management/commands/`
- `backend/apps/system/management/lims_demo_seeder.py`
- `backend/apps/system/management/lims_demo_clear.py`
