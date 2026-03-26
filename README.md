# Limis 实验室信息管理系统

一个现代化、功能完整的**实验室信息管理系统**，基于 Django + Vue3 开发。

![Python](https://img.shields.io/badge/Python-3.11-%233776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-%23092E20?logo=django&logoColor=white)
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
- **操作审计** - 所有敏感操作自动记录
- **响应式设计** - 支持 PC 端和移动端访问
- **容器化部署** - Docker + docker-compose 一键部署

## 🚀 快速开始

### 环境要求
- Docker 和 Docker Compose（推荐）
- 或者本地环境：Python 3.11 + Node.js 18+

### 使用 Docker 启动（推荐）

```bash
# 克隆项目
git clone https://github.com/Uuclear/limis.git
cd limis

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 本地开发环境

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# 前端（新终端）
cd frontend
npm install
npm run dev
```

### 默认账号

- **管理员账号**：`admin` / `admin123`
- **测试账号**：`zhangsan` / `123456`（不同角色）

## 📁 项目结构

```
limis/
├── backend/                 # Django 后端
│   ├── apps/               # 业务应用模块
│   ├── limis/              # 项目配置
│   ├── core/               # 核心基础模块
│   └── requirements.txt
├── frontend/               # Vue3 前端
│   ├── src/
│   ├── components/
│   └── views/
├── nginx/                  # Nginx 配置
├── docs/                   # 文档
├── .github/workflows/      # CI/CD 工作流
├── docker-compose.yml
├── PROJECT_STATUS.md       # 项目状态跟踪
└── README.md
```

## 🛠 技术栈

**后端：**
- Django 5.0 + Django REST Framework
- PostgreSQL + Redis
- Celery (异步任务)
- JWT 认证

**前端：**
- Vue 3 + TypeScript
- Pinia 状态管理
- Element Plus UI 组件库
- Axios + Vue Router

**部署：**
- Docker + Docker Compose
- Nginx 反向代理
- Gunicorn (生产环境)

## 📋 功能模块

- [x] 用户管理与权限控制
- [x] 项目管理
- [x] 委托管理
- [x] 样品管理
- [x] 检测任务管理
- [x] 报告管理
- [x] 设备管理
- [x] 质量管理
- [x] 标准规范管理
- [ ] 数据统计可视化（待完善）
- [ ] 移动端支持（待完善）

## 📖 文档

- [项目状态跟踪](./PROJECT_STATUS.md)
- [开发计划](./docs/PLAN.md)
- [待办事项](./docs/TODO.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 [MIT License](LICENSE) 协议。

---

**Made with ❤️ for Laboratory Information Management**

如有问题或建议，欢迎在 [Issues](https://github.com/Uuclear/limis/issues) 中反馈。
