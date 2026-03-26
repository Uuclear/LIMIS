# Limis 实验室信息管理系统 - 部署文档

本文档提供完整的部署指南，包括开发环境、本地部署和生产环境部署。

## 1. 环境要求

### 基础要求
- **操作系统**：Linux、macOS 或 Windows（推荐 Linux）
- **Docker**：20.10+（推荐使用 Docker 部署）
- **Docker Compose**：v2.0+
- **Git**：2.20+

### 资源推荐（生产环境）
- **CPU**：2核以上
- **内存**：4GB以上（推荐 8GB）
- **存储**：20GB以上可用空间

---

## 2. 快速部署（推荐方式）

### 方式一：使用 Docker Compose（最简单）

```bash
# 1. 克隆项目
git clone https://github.com/Uuclear/limis.git
cd limis

# 2. 复制环境变量配置
cp .env.example .env

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps
```

**服务端口映射：**
- 前端：`http://your-ip:3000`
- 后端 API：`http://your-ip:8000`
- PostgreSQL：`5432`（仅内部访问）
- Redis：`6379`（仅内部访问）

---

## 3. 本地开发环境部署

### 3.1 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example .env
# 编辑 .env 文件，修改 DB_HOST=localhost

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 3.2 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 4. 生产环境部署

### 4.1 使用 Docker（推荐）

修改 `docker-compose.yml` 中的配置：

```yaml
services:
  web:
    build: ./backend
    environment:
      - DEBUG=false
      - ALLOWED_HOSTS=your-domain.com
      - SECRET_KEY=your-very-secure-random-key
```

### 4.2 使用 Gunicorn + Nginx（高级）

```bash
# 安装生产依赖
cd backend
pip install gunicorn

# 使用 Gunicorn 启动
gunicorn limis.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 5. 初始化数据

```bash
# 创建初始数据
cd backend
python manage.py init_data
```

默认账号：
- **管理员**：`admin` / `admin123`
- **技术负责人**：`zhangsan` / `123456`
- **检测员**：`lisi` / `123456`

---

## 6. 常用命令

### Docker 相关
```bash
# 查看日志
docker-compose logs -f web
docker-compose logs -f frontend

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

### 数据库相关
```bash
# 进入数据库容器
docker-compose exec db psql -U limis

# 备份数据库
docker-compose exec db pg_dump -U limis limis > backup.sql
```

### 后端管理命令
```bash
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## 7. 目录说明

```
limis/
├── .env.example          # 环境变量模板
├── docker-compose.yml    # Docker 编排文件
├── DEPLOY.md             # 本部署文档
├── PROJECT_STATUS.md     # 项目状态跟踪
├── backend/              # Django 项目
├── frontend/             # Vue3 前端
├── nginx/                # Nginx 配置
└── docs/                 # 其他文档
```

---

## 8. 常见问题

**Q1: 启动后访问不了前端？**
- 检查 `frontend/.env` 中的 `VITE_API_BASE_URL` 是否正确
- 确认端口 `3000` 是否被占用

**Q2: 数据库连接失败？**
- 确认 `.env` 中的数据库配置是否正确
- 检查 Docker 网络是否正常

**Q3: 如何修改管理员密码？**
```bash
docker-compose exec web python manage.py changepassword admin
```

---

## 9. 安全建议

1. **生产环境必须修改**：
   - `SECRET_KEY`
   - 所有默认密码
   - `DEBUG=false`

2. **定期备份**数据库和重要数据

3. **使用 HTTPS** 保护生产环境

---

**如遇到问题，请在 GitHub Issues 中提交，或查看 `PROJECT_STATUS.md` 了解最新状态。**

---

*最后更新时间：2026年3月26日*
