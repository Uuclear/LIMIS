#!/bin/bash

# Limis 项目开发环境启动脚本

echo "==========================================="
echo "Limis 实验室信息管理系统 - 开发环境启动脚本"
echo "==========================================="

echo ""
echo "重要提醒：此项目需要以下环境依赖："
echo "1. Python 3.12+ (当前系统版本: $(python3 --version 2>&1))"
echo "2. Docker 和 Docker Compose (推荐方式)"
echo "3. PostgreSQL 16 (或本地安装)"
echo "4. Redis 7 (或本地安装)"
echo ""

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "检测到的 Python 版本: $PYTHON_VERSION"

# 检查是否满足最低要求 (3.12)
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$MAJOR_VERSION" -ge 3 ] && [ "$MINOR_VERSION" -ge 12 ]; then
    echo "✓ Python 版本满足要求"
else
    echo "✗ Python 版本不满足要求 (需要 3.12+)，请升级 Python 版本"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3.12 python3.12-venv python3.12-dev"
    echo "  CentOS/RHEL: 需要从源码编译或使用软件仓库安装 Python 3.12"
    echo ""
    echo "或者使用 Docker 方式启动 (推荐):"
    echo "  1. 安装 Docker: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    echo "  2. 安装 Docker Compose: sudo apt install docker-compose-plugin"
    echo "  3. 运行: docker compose up -d --build"
    exit 1
fi

# 检查 Docker
if command -v docker &> /dev/null; then
    echo "✓ Docker 已安装: $(docker --version)"
else
    echo "✗ Docker 未安装，建议安装 Docker 以简化部署"
    echo "  安装命令: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
fi

# 检查 Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✓ Docker Compose 已安装: $(docker-compose --version)"
elif docker compose version &> /dev/null; then
    echo "✓ Docker Compose (V2) 已安装: $(docker compose version)"
else
    echo "✗ Docker Compose 未安装"
    echo "  安装命令: sudo apt install docker-compose-plugin"
fi

echo ""
echo "==========================================="
echo "启动方式选择："
echo "==========================================="
echo ""
echo "方式一：Docker Compose (推荐)"
echo "  1. 确保已安装 Docker 和 Docker Compose"
echo "  2. 在项目根目录执行: docker compose up -d --build"
echo "  3. 访问: http://localhost"
echo ""
echo "方式二：本地开发 (需要安装 Python 3.12+, PostgreSQL, Redis)"
echo "  1. 安装依赖: pip install -r backend/requirements.txt"
echo "  2. 配置数据库连接 (修改 .env 文件)"
echo "  3. 运行后端: cd backend && python manage.py runserver 0.0.0.0:8000"
echo "  4. 在另一个终端运行前端: cd frontend && npm install && npm run dev"
echo ""
echo "==========================================="
echo "初始化数据 (任选其一):"
echo "==========================================="
echo "进入后端容器或虚拟环境后执行以下命令之一："
echo "- python manage.py createsuperuser  # 创建管理员账户"
echo "- python manage.py seed_demo_data   # 轻量演示数据"
echo "- python manage.py seed_full_workflow  # 全流程演示数据"
echo ""