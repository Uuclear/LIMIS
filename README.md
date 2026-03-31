# Limis 实验室信息管理系统

一个现代化、功能完整的**实验室信息管理系统**，基于 Django + Vue3 开发。

![Python](https://img.shields.io/badge/Python-3.12-%233776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-%23092E20?logo=django&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-%2342b883?logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-%23007ACC?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-%23316192?logo=postgresql&logoColor=white)

## ✨ 主要特性

### 核心功能
- **用户权限管理系统** - 基于角色的访问控制 (RBAC)
- **项目全生命周期管理** - 从立项到结项完整流程
- **委托管理** - 委托编号自动生成、状态流转
- **样品管理** - 样品登记、编号生成、二维码管理
- **检测业务管理** - 检测任务、原始记录、结果判定
- **报告管理** - 报告模板、审批流、电子签名
- **质量管理体系** - 不符合项、内部审核、能力验证

### 技术亮点
- **前后端分离架构** - Django REST Framework + Vue3 + TypeScript
- **JWT 认证** - 安全的 Token 认证机制
- **操作审计** - 敏感操作自动记录
- **API 文档** - drf-spectacular（Swagger/OpenAPI）
- **响应式设计** - 支持 PC 端访问
- **容器化部署** - Docker + Docker Compose

## 🚀 快速开始

### 环境要求
- **Docker + Docker Compose**（推荐一键起全栈）
- 或本地开发：**Python 3.12+**、**Node.js 20+**、本机 PostgreSQL / Redis（与 `docker-compose` 二选一）

### 方式一：Docker Compose（推荐）

```bash
git clone https://github.com/Uuclear/limis.git
cd limis
cp .env.example .env   # 按需修改密钥与密码
docker compose up -d --build
docker compose ps
```

默认对外端口（见 `docker-compose.yml`）：
- **Web 前端（Nginx）**：`http://<主机IP>/`（映射宿主机 **80**）
- **PostgreSQL**：宿主机 **5434** → 容器 5432（避免与本机 5432 冲突）
- **Redis**：宿主机 **6379**
- **MinIO**：**9000**（API）、**9001**（控制台）
- **后端 API**：由 Nginx 反代到同一域名下的 **`/api/`**（容器内 Gunicorn 监听 8000，不单独映射宿主机端口）

容器内当前使用 **`limis.settings.dev`**（`DEBUG=True`、开发向 CORS/Hosts 策略）。生产上线前请改回 `limis.settings.prod` 并收紧域名与密钥。

### 方式二：本地前后端分离开发（Vite + runserver）

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# 配置 DB_HOST/DB_PORT 指向你的 PostgreSQL
export DJANGO_SETTINGS_MODULE=limis.settings.dev
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# 前端（新终端，默认端口 3000，见 frontend/vite.config.ts）
cd frontend
npm install
npm run dev
```

开发时前端通过 Vite 将 `/api` 代理到 `http://127.0.0.1:8000`。

### 初始化账号与演示数据

全新数据库**不会**自动存在业务文档里写的全部测试用户，请任选其一：

- **管理员**：`python manage.py createsuperuser`（或容器内执行）
- **轻量演示数据**：`python manage.py seed_demo_data`
- **全流程演示数据**：`python manage.py seed_full_workflow`（可选 `--clear` 先清演示数据）

演示账号约定见 `docs/QUALITY_AND_ROADMAP.md`。

## 📁 项目结构

```
limis/
├── backend/                 # Django 后端
├── frontend/                # Vue3 + Vite 前端
├── nginx/                   # 前端镜像内 Nginx 配置（反代 /api）
├── docs/                    # 规划与质量文档
├── docker-compose.yml
├── DEPLOY.md
├── PROJECT_STATUS.md
└── README.md
```

## 🛠 技术栈

**后端：** Django 5.x、DRF、PostgreSQL、Redis、Celery、JWT、MinIO  

**前端：** Vue 3、TypeScript、Pinia、Element Plus、Axios、Vue Router  

**部署：** Docker Compose、Nginx、Gunicorn（容器内）

## 📋 功能模块（概览）

核心业务模块（项目/委托/样品/检测/报告/设备/标准/质量/统计等）已在代码中落地；细节与完成度以 `PROJECT_STATUS.md` 为准。

## 📖 文档

| 文档 | 说明 |
|------|------|
| [DEPLOY.md](./DEPLOY.md) | 部署、端口、初始化命令 |
| [PROJECT_STATUS.md](./PROJECT_STATUS.md) | 功能与开发状态（主状态源） |
| [docs/PLAN.md](./docs/PLAN.md) | 机场工地试验室业务规划 |
| [docs/TODO.md](./docs/TODO.md) | 历史任务拆分（对照现状见文内说明） |
| [docs/QUALITY_AND_ROADMAP.md](./docs/QUALITY_AND_ROADMAP.md) | 质量改进、种子数据、回归建议 |
| API | 后端运行后访问 `/api/docs/`（drf-spectacular） |

## 🤝 贡献

欢迎提交 Issue 与 Pull Request。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 协议。

---

如有问题，欢迎在 [Issues](https://github.com/Uuclear/limis/issues) 反馈。
