# 本地开发环境

本文说明如何在本地搭建 **LIMIS**（Django + DRF + Vue3 + TS + PostgreSQL + Redis + JWT + Celery + MinIO）开发环境，与仓库当前结构一致。

## 技术栈版本参考

| 组件 | 说明 |
|------|------|
| Python | CI 使用 3.11（见 `.github/workflows/backend-ci.yml`）；`requirements.txt` 约束 Django 5.x–6.x |
| Node | CI 使用 Node 18；前端 `package.json` 使用 Vite 8、Vue 3.5、TypeScript 5.9 |
| 数据库 | PostgreSQL（Docker 示例为 16；CI 为 15） |
| 缓存/队列 | Redis 7 |
| 对象存储 | MinIO（可选，用于附件等） |

---

## 方式一：Docker Compose（推荐全栈）

仓库根目录 **`docker-compose.yml`** 定义：

- **db**：PostgreSQL，默认库名/用户 `limis`，宿主机端口 **5434→5432**（避免与本地 5432 冲突）
- **redis**：6379
- **minio**：9000（API）、9001（控制台）
- **backend**：`DJANGO_SETTINGS_MODULE=limis.settings.dev`，启动前执行 `migrate` 与 `collectstatic`，**Gunicorn** 监听 8000
- **celery** / **celery-beat**：异步与定时任务
- **frontend**：Nginx 构建产物，映射 **80**

常用环境变量（可通过 `.env` 覆盖）见 `docker-compose.yml` 中 `environment` 段，例如：

- `DB_NAME`、`DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`
- `REDIS_URL`（默认 `redis://redis:6379/0`）
- `SECRET_KEY`、`ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS`
- `MINIO_*`

启动（示例）：

```bash
cd /opt/limis
docker compose up -d --build
```

首次部署后按需执行 **`createsuperuser`**、数据种子命令（见 `backend/apps/system/management/commands/`）等。

---

## 方式二：前后端分离本地运行（热重载）

适合前端改 UI、后端改接口时的日常开发。

### 1. 数据库与 Redis

可用 Docker 只启动依赖：

```bash
docker compose up -d db redis
```

本地连接 PostgreSQL 时使用 **`localhost:5434`**（与 compose 映射一致），并设置：

```bash
export DB_HOST=127.0.0.1
export DB_PORT=5434
export DB_NAME=limis
export DB_USER=limis
export DB_PASSWORD=limis123
export REDIS_URL=redis://127.0.0.1:6379/0
export DJANGO_SETTINGS_MODULE=limis.settings.dev
```

### 2. 后端

```bash
cd /opt/limis/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

- 管理命令需在 **`backend`** 目录执行，或设置 `PYTHONPATH` 指向 `backend`。
- 开发设置见 **`backend/limis/settings/dev.py`**（在 `base.py` 基础上打开 DEBUG、CORS 等）。

### 3. 前端

```bash
cd /opt/limis/frontend
npm ci
npm run dev
```

**Vite 开发服务器**默认 `http://localhost:3000`，并将 **`/api`** 代理到 **`http://127.0.0.1:8000`**（`frontend/vite.config.ts`）。因此浏览器访问前端时，API 请求形如 `/api/v1/...` 会转到本机 Django。

若后端跑在其他主机/端口，请修改 `vite.config.ts` 中 `server.proxy['/api'].target`。

### 4. Celery / MinIO

- 异步任务：需单独终端运行 `celery -A limis worker`（工作目录 `backend`，同样设置 `DJANGO_SETTINGS_MODULE`）。
- MinIO：若功能依赖对象存储，可 `docker compose up -d minio` 并配置与 `base.py` 一致的 `MINIO_*` 环境变量。

---

## API 文档（本地）

后端启动后访问：

- Swagger：`http://127.0.0.1:8000/api/docs/`
- ReDoc：`http://127.0.0.1:8000/api/redoc/`

---

## 常见问题

1. **端口占用**：5434、6379、8000、3000 被占用时，修改 compose 映射或本地服务端口。
2. **CORS**：前后端分离时确保 `dev.py` / 环境变量中 `CORS_ALLOWED_ORIGINS` 包含前端源（如 `http://localhost:3000`）。
3. **静态/媒体文件**：DEBUG 下 Django 可对 `/media/` 提供开发服务（见根 `urls.py`）；生产由 Nginx/对象存储承载。
4. **HTTPS**：`USE_HTTPS` 等用于生成绝对 URL 类场景，按部署环境配置。

---

## 相关路径速查

| 用途 | 路径 |
|------|------|
| Compose | `/opt/limis/docker-compose.yml` |
| Django 配置 | `/opt/limis/backend/limis/settings/` |
| 前端代理 | `/opt/limis/frontend/vite.config.ts` |
| Axios 基址 | `/opt/limis/frontend/src/utils/request.ts`（`baseURL: '/api'`） |
