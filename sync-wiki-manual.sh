#!/bin/bash
# 手动同步Wiki到GitHub Wiki脚本
# 使用方法: ./sync-wiki-manual.sh <你的GitHub用户名> <你的PAT令牌>

set -e

USERNAME=$1
TOKEN=$2
REPO="Uuclear/limis"

if [ -z "$USERNAME" ] || [ -z "$TOKEN" ]; then
    echo "❌ 错误: 请提供GitHub用户名和PAT令牌"
    echo "用法: ./sync-wiki-manual.sh <用户名> <PAT令牌>"
    exit 1
fi

echo "🔄 开始同步Wiki到GitHub Wiki..."

# 创建临时目录
WIKI_TEMP=$(mktemp -d)
trap "rm -rf $WIKI_TEMP" EXIT

# 复制wiki内容
cp -r wiki/* "$WIKI_TEMP/"

cd "$WIKI_TEMP"

# 处理文件名（移除序号前缀）
echo "📝 处理文件名..."

# 处理目录名
mv "01-系统概述" "系统概述" 2>/dev/null || true
mv "02-用户指南" "用户指南" 2>/dev/null || true
mv "03-管理员指南" "管理员指南" 2>/dev/null || true
mv "04-功能详解" "功能详解" 2>/dev/null || true
mv "05-API文档" "API文档" 2>/dev/null || true
mv "06-扩展开发" "扩展开发" 2>/dev/null || true
mv "07-常见问题" "常见问题" 2>/dev/null || true

# 处理系统概述目录下的文件
if [ -d "系统概述" ]; then
    cd "系统概述"
    mv "01-系统简介.md" "系统简介.md" 2>/dev/null || true
    mv "02-快速开始.md" "快速开始.md" 2>/dev/null || true
    mv "03-术语定义.md" "术语定义.md" 2>/dev/null || true
    cd ..
fi

# 处理用户指南目录下的文件
if [ -d "用户指南" ]; then
    cd "用户指南"
    mv "01-角色权限说明.md" "角色权限说明.md" 2>/dev/null || true
    mv "02-委托管理.md" "委托管理.md" 2>/dev/null || true
    mv "03-样品管理.md" "样品管理.md" 2>/dev/null || true
    mv "04-检测任务.md" "检测任务.md" 2>/dev/null || true
    mv "05-原始记录.md" "原始记录.md" 2>/dev/null || true
    mv "06-检测报告.md" "检测报告.md" 2>/dev/null || true
    mv "07-个人中心.md" "个人中心.md" 2>/dev/null || true
    cd ..
fi

# 处理管理员指南目录下的文件
if [ -d "管理员指南" ]; then
    cd "管理员指南"
    mv "01-系统配置.md" "系统配置.md" 2>/dev/null || true
    mv "02-用户管理.md" "用户管理.md" 2>/dev/null || true
    mv "03-项目管理.md" "项目管理.md" 2>/dev/null || true
    mv "04-设备管理.md" "设备管理.md" 2>/dev/null || true
    mv "05-人员管理.md" "人员管理.md" 2>/dev/null || true
    mv "06-标准库管理.md" "标准库管理.md" 2>/dev/null || true
    mv "07-模板管理.md" "模板管理.md" 2>/dev/null || true
    mv "08-质量管理.md" "质量管理.md" 2>/dev/null || true
    mv "09-耗材管理.md" "耗材管理.md" 2>/dev/null || true
    mv "10-环境监控.md" "环境监控.md" 2>/dev/null || true
    mv "11-审计日志.md" "审计日志.md" 2>/dev/null || true
    cd ..
fi

# 处理功能详解目录下的文件
if [ -d "功能详解" ]; then
    cd "功能详解"
    mv "01-状态机流转.md" "状态机流转.md" 2>/dev/null || true
    mv "02-电子签名.md" "电子签名.md" 2>/dev/null || true
    mv "03-盲样管理.md" "盲样管理.md" 2>/dev/null || true
    mv "04-自动计算.md" "自动计算.md" 2>/dev/null || true
    mv "05-龄期管理.md" "龄期管理.md" 2>/dev/null || true
    mv "06-设备预警.md" "设备预警.md" 2>/dev/null || true
    mv "07-实时监控.md" "实时监控.md" 2>/dev/null || true
    mv "08-数据导出.md" "数据导出.md" 2>/dev/null || true
    cd ..
fi

# 处理API文档目录下的文件
if [ -d "API文档" ]; then
    cd "API文档"
    mv "01-API概述.md" "API概述.md" 2>/dev/null || true
    mv "02-系统模块API.md" "系统模块API.md" 2>/dev/null || true
    mv "03-业务模块API.md" "业务模块API.md" 2>/dev/null || true
    mv "04-支撑模块API.md" "支撑模块API.md" 2>/dev/null || true
    cd ..
fi

# 处理扩展开发目录下的文件
if [ -d "扩展开发" ]; then
    cd "扩展开发"
    mv "01-开发环境搭建.md" "开发环境搭建.md" 2>/dev/null || true
    mv "02-后端开发指南.md" "后端开发指南.md" 2>/dev/null || true
    mv "03-前端开发指南.md" "前端开发指南.md" 2>/dev/null || true
    mv "04-新增检测类型.md" "新增检测类型.md" 2>/dev/null || true
    mv "05-自定义报表.md" "自定义报表.md" 2>/dev/null || true
    cd ..
fi

# 处理常见问题目录下的文件
if [ -d "常见问题" ]; then
    cd "常见问题"
    mv "01-常见问题FAQ.md" "常见问题FAQ.md" 2>/dev/null || true
    mv "02-已知问题.md" "已知问题.md" 2>/dev/null || true
    mv "03-Bug预计与排查.md" "Bug预计与排查.md" 2>/dev/null || true
    cd ..
fi

# 复制README.md为Home.md
if [ -f "README.md" ]; then
    cp "README.md" "Home.md"
fi

echo "📦 克隆Wiki仓库..."
cd /tmp
rm -rf limis.wiki
git clone "https://${USERNAME}:${TOKEN}@github.com/${REPO}.wiki.git" limis.wiki 2>/dev/null || mkdir limis.wiki

cd limis.wiki

# 如果目录为空，初始化git
if [ ! -d .git ]; then
    git init
    git remote add origin "https://${USERNAME}:${TOKEN}@github.com/${REPO}.wiki.git"
fi

# 清空现有内容
rm -rf *

# 复制新内容
cp -r "$WIKI_TEMP"/* .

# 配置git
git config user.name "${USERNAME}"
git config user.email "${USERNAME}@users.noreply.github.com"

# 添加并提交
git add -A

# 检查是否有更改
if git diff --staged --quiet; then
    echo "ℹ️ 没有更改需要提交"
    exit 0
fi

git commit -m "Sync wiki from manual script"

# 推送
echo "🚀 推送到GitHub Wiki..."
git push origin master --force

echo "✅ Wiki同步完成！"
echo "📚 访问地址: https://github.com/${REPO}/wiki"