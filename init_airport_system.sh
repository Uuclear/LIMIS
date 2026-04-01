#!/bin/bash

# 机场工程检测系统初始化脚本
# 为浦东国际机场四期扩建工程初始化完整的检测系统

echo "==========================================="
echo "机场工程检测系统初始化脚本"
echo "==========================================="
echo ""

echo "1. 初始化标准规范数据..."
cd /opt/limis/backend && python manage.py seed_airport_standards
if [ $? -eq 0 ]; then
    echo "   ✓ 标准规范数据初始化成功"
else
    echo "   ✗ 标准规范数据初始化失败"
fi

echo ""
echo "2. 初始化检测参数库..."
cd /opt/limis/backend && python manage.py seed_airport_testing_params
if [ $? -eq 0 ]; then
    echo "   ✓ 检测参数库初始化成功"
else
    echo "   ✗ 检测参数库初始化失败"
fi

echo ""
echo "3. 初始化检测流程数据..."
cd /opt/limis/backend && python manage.py seed_airport_testing_flow
if [ $? -eq 0 ]; then
    echo "   ✓ 检测流程数据初始化成功"
else
    echo "   ✗ 检测流程数据初始化失败"
fi

echo ""
echo "4. 初始化原始记录模板..."
cd /opt/limis/backend && python manage.py seed_airport_record_templates
if [ $? -eq 0 ]; then
    echo "   ✓ 原始记录模板初始化成功"
else
    echo "   ✗ 原始记录模板初始化失败"
fi

echo ""
echo "5. 优化委托管理流程..."
cd /opt/limis/backend && python manage.py optimize_airport_commission_flow
if [ $? -eq 0 ]; then
    echo "   ✓ 委托管理流程优化成功"
else
    echo "   ✗ 委托管理流程优化失败"
fi

echo ""
echo "6. 优化样品管理功能..."
cd /opt/limis/backend && python manage.py optimize_airport_sample_mgmt
if [ $? -eq 0 ]; then
    echo "   ✓ 样品管理功能优化成功"
else
    echo "   ✗ 样品管理功能优化失败"
fi

echo ""
echo "7. 开发检测执行模块..."
cd /opt/limis/backend && python manage.py develop_airport_testing_execution
if [ $? -eq 0 ]; then
    echo "   ✓ 检测执行模块开发成功"
else
    echo "   ✗ 检测执行模块开发失败"
fi

echo ""
echo "8. 优化报告管理功能..."
cd /opt/limis/backend && python manage.py optimize_airport_report_mgmt
if [ $? -eq 0 ]; then
    echo "   ✓ 报告管理功能优化成功"
else
    echo "   ✗ 报告管理功能优化失败"
fi

echo ""
echo "9. 实现全程追溯功能..."
cd /opt/limis/backend && python manage.py implement_airport_tracking_system
if [ $? -eq 0 ]; then
    echo "   ✓ 全程追溯功能实现成功"
else
    echo "   ✗ 全程追溯功能实现失败"
fi

echo ""
echo "10. 添加实时监控功能..."
cd /opt/limis/backend && python manage.py add_airport_realtime_monitoring
if [ $? -eq 0 ]; then
    echo "   ✓ 实时监控功能添加成功"
else
    echo "   ✗ 实时监控功能添加失败"
fi

echo ""
echo "11. 确保资质认证合规..."
cd /opt/limis/backend && python manage.py ensure_airport_certification_compliance
if [ $? -eq 0 ]; then
    echo "   ✓ 资质认证合规功能实现成功"
else
    echo "   ✗ 资质认证合规功能实现失败"
fi

echo ""
echo "==========================================="
echo "机场工程检测系统初始化完成!"
echo "==========================================="
echo ""
echo "系统功能概览:"
echo "  - 标准规范管理: 包含机场工程相关标准"
echo "  - 检测参数库: 涵盖土木、混凝土、钢筋、沥青等"
echo "  - 检测流程: 完整的委托-样品-检测-报告流程"
echo "  - 原始记录: 标准化的记录模板"
echo "  - 质量追溯: 全程可追溯的质量管控"
echo "  - 实时监控: 实时监控和预警功能"
echo "  - 资质合规: 符合ISO/IEC 17025等标准"
echo ""
echo "下一步操作建议:"
echo "  1. 创建管理员账户: python manage.py createsuperuser"
echo "  2. 启动开发服务器: python manage.py runserver 0.0.0.0:8000"
echo "  3. 访问管理后台: http://<your-ip>:8000/admin/"
echo "  4. 访问API文档: http://<your-ip>:8000/api/docs/"
echo ""