# Limis 实验室信息管理系统 - 部署文档

本文档描述 **Docker Compose 全栈部署** 与 **本地开发** 两种方式的要点。细节功能状态以 `PROJECT_STATUS.md` 为准。

## 1. 环境要求

- **操作系统**：Linux（推荐）、macOS、Windows（WSL2）
- **Docker**：20.10+
- **Docker Compose**：v2（命令一般为 `docker compose`）
- **Git**：2.20+

**资源建议**：CPU ≥ 2 核，内存 ≥ 4 GB（全栈容器 + Celery）。

---

## 2. Docker Compose 快速部署

### 2.1 启动

```bash
git clone https://github.com/Uuclear/limis.git
cd limis
cp .env.example .env
docker compose up -d --build
docker compose ps
```

### 2.2 服务与端口（宿主机）

| 服务 | 说明 | 宿主机端口 |
|------|------|------------|
| `frontend` | Nginx 托管前端静态资源，并反代 `/api`、`/admin`、`/static`、`/media` | **80** |
| `db` | PostgreSQL 16 | **5434** → 容器内 5432 |
| `redis` | Redis 7 | **6379** |
| `minio` | 对象存储 | **9000** / **9001**（控制台） |
| `backend` | Gunicorn（容器内 **8000**，由 Nginx 访问，不单独映射） | （无对外端口） |
| `celery` / `celery-beat` | 异步与定时任务 | （无对外端口） |

若本机 **80 / 6379 / 5434** 已被占用，需先释放端口或修改 `docker-compose.yml` 映射后再启动。

### 2.3 配置说明

- 仓库内 `docker-compose.yml` 将 **`DJANGO_SETTINGS_MODULE` 设为 `limis.settings.dev`**，便于联调（`DEBUG=True`、`ALLOWED_HOSTS=['*']`、开发向 CORS）。**正式生产**请改为 `limis.settings.prod`，并设置 `SECRET_KEY`、`ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS` 等。
- 数据库默认库名/用户见 compose 中 `DB_NAME` / `DB_USER`（默认 `limis` / `limis123`，以 `.env` 为准）。

### 2.4 访问方式

- 浏览器打开：`http://<服务器IP>/`（局域网访问时使用真实 IP，勿混用仅本机可用的地址）。
- API 前缀：`/api/v1/...`（与前端同源，由 Nginx 转发到 `backend:8000`）。

### 2.5 更新后重建

```bash
git pull
docker compose up -d --build
```

---

## 3. 初始化数据

仓库**不包含**已废弃的 `init_data` 命令。请使用下列管理命令（在 **`backend` 容器内** 或本地虚拟环境中执行）：

```bash
# 进入后端容器
docker compose exec backend sh

# 迁移（compose 启动命令已执行 migrate，此处用于手动补跑）
python manage.py migrate

# 最小演示数据（设备、耗材等占位）
python manage.py seed_demo_data

# 全流程演示数据（编号前缀 LIMIS-DEMO- 等，见 docs/QUALITY_AND_ROADMAP.md）
python manage.py seed_full_workflow
# 或先清空再写入：
python manage.py seed_full_workflow --clear

# 管理员（若库中尚无账号）
python manage.py createsuperuser
```

其他命令：`seed_role_test_users`（按角色生成 `test_<角色编码>` 账号，用于权限回归）。

---

## 4. 本地开发（不用 Docker 跑后端时）

### 4.1 后端

```bash
cd backend
python -m venv venv
source venv/activate
pip install -r requirements.txt
cp ../.env.example .env
# 编辑 .env：DB_HOST、DB_PORT、DB_NAME、DB_USER、DB_PASSWORD、REDIS_URL
export DJANGO_SETTINGS_MODULE=limis.settings.dev
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 4.2 前端

```bash
cd frontend
npm install
npm run dev
```

默认 **Vite** 端口 **3000**，`vite.config.ts` 将 `/api` 代理到 `http://127.0.0.1:8000`。若后端不在本机 8000，请同步修改代理或 `frontend` 环境变量中的 API 基地址（按项目既有约定）。

---

## 5. 常用运维命令

```bash
# 日志（服务名以 docker compose ps 为准）
docker compose logs -f backend
docker compose logs -f frontend

docker compose restart frontend
docker compose restart backend

docker compose down
docker compose down -v
```

```bash
# 数据库备份示例
docker compose exec db pg_dump -U limis limis > backup.sql
```

```bash
# 修改管理员密码（容器内）
docker compose exec backend python manage.py changepassword admin
```

---

## 6. 目录说明

```
limis/
├── .env.example
├── docker-compose.yml
├── DEPLOY.md
├── PROJECT_STATUS.md
├── backend/
├── frontend/
├── nginx/nginx.conf
└── docs/
```

---

## 7. 常见问题

**Q：浏览器登录报 400/502？**  
- 400：检查是否用局域网 IP 访问而仍使用生产 `ALLOWED_HOSTS`；当前 compose 使用 **dev** 设置一般可接受任意 Host。  
- 502：多见于 **backend 重建后** Nginx 上游未就绪，可执行 `docker compose restart frontend` 后再试。

**Q：数据库连不上？**  
- 容器内应使用主机名 **`db`**、端口 **5432**；宿主机调试应使用 **`127.0.0.1:5434`**（映射端口以 `docker-compose.yml` 为准）。

**Q：迁移报错？**  
- 拉取新代码后执行：`docker compose exec backend python manage.py migrate`

---

## 8. 安全提示

生产环境务必：**强 `SECRET_KEY`、关闭调试、收紧 `ALLOWED_HOSTS` 与 CORS、HTTPS、定期备份数据库与媒体卷**。

---

*最后更新：2026 年 3 月 31 日*
