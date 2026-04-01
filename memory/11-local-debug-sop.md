# 本地调试与 500 排障 SOP（Vite + runserver）

## 1. 调试模式约定

- 默认使用本地前后端分离调试：`frontend` 用 Vite，`backend` 用 Django `runserver`。
- 默认数据库使用本机 PostgreSQL（`127.0.0.1:5432`），禁止把 Docker 数据库当作主调试库。
- 若临时启用 Docker，仅允许用于对照排查，不能作为最终修复验证依据。

## 2. 后端本地启动基线

```bash
cd /opt/limis/backend
DB_HOST=127.0.0.1 \
DB_PORT=5432 \
DB_NAME=limis \
DB_USER=limis \
DB_PASSWORD=limis123 \
DJANGO_SETTINGS_MODULE=limis.settings.dev \
/opt/limis/venv/bin/python manage.py runserver 0.0.0.0:8000
```

## 3. 前端本地启动基线

```bash
cd /opt/limis/frontend
npm run dev
```

## 4. 500 高频根因（本项目）

近期高频根因为：代码依赖了新迁移（新表/新字段），但本地 `5432` 数据库未执行 `migrate`，导致接口访问触发 ORM 报错。

典型表现：
- 委托管理、样品管理、项目详情等页面打开即 `Request failed with status code 500`。
- 不同终端使用了不同 DB 端口（`5432` vs `5434`）时，问题反复出现。

## 5. 标准排障流程

1. 先确认当前 `runserver` 使用的 DB 环境变量（`DB_HOST/DB_PORT/DB_NAME/DB_USER`）。
2. 在同一组环境变量下执行：
   - `python manage.py showmigrations`
   - `python manage.py migrate`
3. 再做接口 smoke：
   - `/api/v1/commissions/`
   - `/api/v1/samples/samples/`
   - `/api/v1/testing/tasks/`
   - `/api/v1/projects/`
4. 若仍 500，抓后端 traceback 定位具体模型/字段。

## 6. 本地验证清单

- `python -m py_compile` 对改动后端文件通过。
- `frontend npm run typecheck` 通过。
- 页面链路验证：项目 -> 委托 -> 样品 -> 任务 -> 报告主链路不报 500。

## 7. 建议固定命令

- 迁移检查：`bash /opt/limis/scripts/local_migration_check.sh`
- 关键回归：`bash /opt/limis/scripts/local_regression_smoke.sh`

