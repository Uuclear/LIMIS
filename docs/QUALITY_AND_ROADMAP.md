# LIMIS 质量改进与路线图建议

本文档说明近期典型故障根因、演示数据用法，以及建议在后续迭代中逐步落实的工程化与功能完善方向。

**当前运行模式提示**：`docker-compose.yml` 默认使用 **`limis.settings.dev`**（`DEBUG=True`、`ALLOWED_HOSTS=['*']`、开发向 CORS）。使用 **Docker** 时，请在 `backend` 容器内执行管理命令，例如：

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_full_workflow
```

本地虚拟环境则设置 `DJANGO_SETTINGS_MODULE=limis.settings.dev` 后执行相同命令。

---

## 1. 「Request failed with status code 500」常见根因（通知模块）

| 现象 | 根因 | 处理 |
|------|------|------|
| 登录后首页或头部立即报 500 | 后端存在未执行的迁移（例如 `system.0003_notification`），查询 `system_notification` 表时数据库报错 | 部署或拉代码后执行：`python manage.py migrate` |
| 仅通知相关接口 500 | 同上，或 Redis/数据库连接配置错误 | 检查 `DB_*`、`REDIS_URL` 与进程是否可达 |

**前端补充**：通知接口返回字段为 **snake_case**（`is_read`、`link_path` 等）。已在 `Header.vue` 中做字段映射，避免未读状态与跳转路径失效。

---

## 2. 全流程演示数据（避免各模块「空列表」）

管理命令 **`seed_full_workflow`** 的实现类为 **`apps.system.management.lims_demo_seeder.LimsDemoSeeder`**（与命令文件分离，便于维护与单测）。

数据约定：**编号前缀 `LIMIS-DEMO-`**；演示用户 **`demo_<角色编码>`**，密码 **`Limis@demo123`**。`--clear` 会删除上述前缀及 `demo_*` 用户，并尝试清理历史旧版演示前缀（如 `TT-2024-`、`PDJC-2024-001` 等），避免外键残留阻塞重建。

```bash
cd backend
export DB_HOST=127.0.0.1 DB_NAME=limis DB_USER=limis DB_PASSWORD=<密码>
export REDIS_URL=redis://127.0.0.1:6379/0
python manage.py migrate
python manage.py seed_full_workflow
```

在 **Docker** 中（数据库主机名为 `db`、Redis 为 `redis`）无需手动 export，直接：

```bash
docker compose exec backend python manage.py seed_full_workflow
```

- 干净重建：`python manage.py seed_full_workflow --clear`（**勿在生产未经评估使用**）。
- 另有 **`seed_role_test_users`**：为每个角色生成 `test_<角色编码>` 测试账号（与 `demo_*` 不同），便于权限回归。

---

## 3. 缺陷与风险：建议的排查优先级

### 高优先级（影响可用性）

1. **部署流水线执行迁移**：将 `migrate` 纳入 CI/CD 必跑步骤，避免「代码已合并但表未创建」。
2. **API 命名风格统一**：后端 DRF 默认 snake_case，前端部分页面若按 camelCase 手写类型，易出现静默错误；建议统一约定（全局 camelCase 中间件 **或** 前端统一映射层）。
3. **关键路径冒烟**：登录 → `/me` → 通知 `unread_count` → 列表页；任一环节应用自动化接口测试。

### 中优先级（数据与一致性）

4. **种子数据幂等性**：`seed_full_workflow` 对「已存在主键」多为 `get_or_create`，迭代模型后建议增加 `--clear` 与文档说明，避免演示库脏数据。
5. **委托与检测项一致性**：演示中部分委托检测项描述与所选检测方法可能不完全一一对应，业务上应通过「委托项 → 方法/参数」约束或校验加强。

### 低优先级（体验与性能）

6. **通知轮询**：头部每 60s 拉取未读数，可改为 WebSocket/SSE 或拉长间隔并配合可见性 API（Page Visibility）。
7. **前端构建体积**：构建日志提示主 chunk 偏大，可按路由做懒加载与分包。

---

## 4. 功能完善建议（按业务域）

| 域 | 建议 |
|----|------|
| 通知 | 增加后台定时任务：将「待评审委托」「待审核报告」等从统计表同步为 `Notification` 记录，避免与真实待办重复或遗漏 |
| 检测流程 | 对「委托未评审即登记样品」等业务规则加后端校验与明确错误码 |
| 报告 | 完善工作流单元测试（提交审核 → 批准 → 发放）与状态机文档 |
| 质量 | 内部审核/不符合项与检测任务的关联（可选） |
| 审计 | 对敏感操作已有审计中间件，建议补充检索与导出权限 |

---

## 5. 测试策略建议

1. **后端**：对 `services` 层核心业务用 `pytest` + SQLite/事务回滚做单元测试；对 API 用 DRF `APITestCase` 覆盖鉴权与分页。
2. **前端**：对请求封装与 Pinia 关键流做最小单测；E2E 可选用 Playwright 跑「登录 + 一屏列表」。
3. **回归清单**：每次发版前执行：`migrate` → `seed_full_workflow`（测试库）→ 手动走通委托→任务→记录→报告主路径。

---

## 6. 安全与运维

- 生产环境务必使用强 `SECRET_KEY`、HTTPS、受限 `ALLOWED_HOSTS`。
- 演示种子账号密码不可用于生产；生产部署前删除或禁用 `seed_*` 创建的用户。
- 定期备份 PostgreSQL 与媒体文件目录。

---

*文档随迭代更新；若你希望将其中某条落实为具体 issue/任务，可直接指定条目编号。*

---

*最后更新：2026 年 3 月 31 日*
