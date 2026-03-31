# 本地开发调试（dev 模式，尽量少打镜像）

目标：**改 Python/Vue 代码后能立刻验证**，而不是每次 `docker compose build`。

## 推荐方式 A：只起依赖容器 + 本机前后端

1. 启动数据库、Redis、MinIO（按需）：

```bash
docker compose up -d db redis minio
```

2. 后端（使用 `limis.settings.dev`）：

```bash
cd backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=limis.settings.dev
export DB_HOST=127.0.0.1 DB_PORT=5434 DB_NAME=limis DB_USER=limis DB_PASSWORD=limis123
export REDIS_URL=redis://127.0.0.1:6379/0
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

3. 前端（Vite，默认 3000，带 `/api` 代理）：

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 `http://<本机IP>:3000`，**无需**每次 `docker compose build frontend`。

## 方式 B：仍用 compose 跑全栈

若必须用容器里的 Gunicorn/Nginx，代码在镜像构建时打进去了，**改代码后需要重建对应服务镜像**（这是 Docker 镜像模型的限制）。开发阶段更推荐方式 A。

## 说明

- `docker-compose.yml` 里 `DJANGO_SETTINGS_MODULE=limis.settings.dev` 表示**容器内 Django 用 dev 配置**；与「是否打镜像」无关。
- 登出接口依赖 `rest_framework_simplejwt.token_blacklist` 的迁移；若登出曾报 500，请确认已执行 `migrate`。
