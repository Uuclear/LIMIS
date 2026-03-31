# 测试与质量门禁

## 后端

### 单元测试与集成测试

使用 Django 内置 **`manage.py test`**：

```bash
cd /opt/limis/backend
export DJANGO_SETTINGS_MODULE=limis.settings.dev
export DB_NAME=limis DB_USER=limis DB_PASSWORD=limis123 DB_HOST=127.0.0.1 DB_PORT=5432
export SECRET_KEY=dummy-key-for-local
python manage.py test --verbosity=2
```

CI（`.github/workflows/backend-ci.yml`）在 **PostgreSQL 服务容器** 上执行：

1. `pip install -r requirements.txt`
2. `makemigrations --check`
3. `migrate --noinput`
4. `manage.py test --verbosity=2`
5. **flake8**（排除 `migrations`、`venv`，`max-line-length=120`，失败不阻断 CI 时以 `|| echo` 吞掉）

**规范建议**：新增业务逻辑时补充 `tests.py` 或 `tests/` 包；对关键权限、状态流转、序列化边界写测试。

### 代码风格

- 推荐使用 **flake8** 或与团队一致的 formatter；与 CI 的排除项对齐，避免无意义告警。

---

## 前端

### 构建与类型

`package.json` 中 **`npm run build`** 执行：

```text
vue-tsc -b && vite build
```

即先 **TypeScript 检查** 再打包。本地提交前务必执行 **`npm run build`** 确保通过。

### CI

`.github/workflows/frontend-ci.yml` 在 Node 18 下执行：

- `npm ci`
- `npm run type-check`（若脚本缺失需在前端补齐，否则 CI 中可能仅 echo）
- `npm run lint`（同上）
- `npm run build`

**规范建议**：为仓库补齐 `type-check` / `lint` 脚本（如 `vue-tsc --noEmit`、`eslint`）并与 CI 一致，避免“本地能跑、CI 无检查”。

---

## Docker 全栈

`.github/workflows/docker-ci.yml`（若存在）可能构建镜像或编排冒烟测试；发版前建议在目标环境执行一次 **`docker compose build`** 与核心路径手工验证。

---

## API 契约

- 后端启用 **drf-spectacular**，接口变更时检查 **`/api/schema/`** 或 Swagger。
- 破坏性变更（字段重命名、删除、语义变更）需在 MR 中 **显式说明** 并协调前端版本。

---

## 提交流程（质量清单）

1. **自测**：核心流程在本地或 Compose 环境走通。
2. **后端**：迁移可应用、`test` 通过（若项目要求零失败）。
3. **前端**：`build` 通过；关键页面无控制台报错。
4. **文档**：若引入新环境变量、新服务依赖，更新部署/开发文档（本 `wiki` 或运维文档）。
5. **MR**：描述范围、风险、回滚方式；需要数据库迁移的变更打标签便于发布顺序。

---

## 已知缺口与改进方向（可选）

- 若 `package.json` 未定义 `lint`/`type-check`，与 CI 不一致，建议统一。
- 可增加 **pre-commit**（格式化、import 排序）提升一致性。
- E2E（Playwright/Cypress）未在默认 CI 中强制时，关键路径可逐步补自动化。

---

## 相关文件

| 用途 | 路径 |
|------|------|
| 后端 CI | `.github/workflows/backend-ci.yml` |
| 前端 CI | `.github/workflows/frontend-ci.yml` |
| 依赖 | `backend/requirements.txt`、`frontend/package.json` |
