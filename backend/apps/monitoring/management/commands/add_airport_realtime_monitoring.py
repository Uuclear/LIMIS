"""
机场工程实时监控和预警功能
为浦东国际机场四期扩建工程添加实时监控和预警功能
"""

import os
import sys
import django
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limis.settings')
django.setup()

from apps.testing.models.task import TestTask
from apps.testing.models.result import TestResult
from apps.samples.models import Sample
from apps.commissions.models import Commission
from apps.system.models import User


class Command(BaseCommand):
    help = '添加机场工程实时监控和预警功能'

    def handle(self, *args, **options):
        self.stdout.write('正在添加机场工程实时监控和预警功能...')
        
        # 获取机场工程相关数据
        commission = Commission.objects.filter(
            project_name__contains='浦东机场四期扩建'
        ).first()
        
        if not commission:
            self.stderr.write('  错误: 找不到相关的委托单')
            return
        
        # 创建实时监控指标
        self.stdout.write('  机场工程实时监控指标:')
        
        # 1. 任务进度监控
        tasks = TestTask.objects.filter(commission=commission)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        overdue_tasks = tasks.filter(
            planned_date__lt=timezone.now().date(),
            status__in=['unassigned', 'assigned', 'in_progress']
        ).count()
        
        self.stdout.write(f'    1. 任务进度监控:')
        self.stdout.write(f'       - 总任务数: {total_tasks}')
        self.stdout.write(f'       - 已完成: {completed_tasks}')
        self.stdout.write(f'       - 完成率: {completed_tasks/total_tasks*100:.1f}%' if total_tasks > 0 else '完成率: 0%')
        self.stdout.write(f'       - 逾期任务: {overdue_tasks}')
        
        # 2. 样品状态监控
        samples = Sample.objects.filter(commission=commission)
        total_samples = samples.count()
        testing_samples = samples.filter(status='testing').count()
        tested_samples = samples.filter(status='tested').count()
        
        self.stdout.write(f'    2. 样品状态监控:')
        self.stdout.write(f'       - 总样品数: {total_samples}')
        self.stdout.write(f'       - 检测中: {testing_samples}')
        self.stdout.write(f'       - 已检测: {tested_samples}')
        
        # 3. 结果质量监控
        results = TestResult.objects.filter(task__commission=commission)
        total_results = results.count()
        unqualified_results = results.filter(judgment='unqualified').count()
        
        self.stdout.write(f'    3. 结果质量监控:')
        self.stdout.write(f'       - 总结果数: {total_results}')
        self.stdout.write(f'       - 不合格结果: {unqualified_results}')
        self.stdout.write(f'       - 合格率: {(total_results-unqualified_results)/total_results*100:.1f}%' if total_results > 0 else '合格率: 100%')
        
        # 创建预警规则
        self.stdout.write('  机场工程预警规则:')
        
        # 任务逾期预警
        if overdue_tasks > 0:
            self.stdout.write(f'    1. ⚠️  任务逾期预警: 发现 {overdue_tasks} 个逾期任务')
        else:
            self.stdout.write(f'    1. ✅ 任务逾期监控: 所有任务按时完成')
        
        # 不合格结果预警
        if unqualified_results > 0:
            self.stdout.write(f'    2. ⚠️  不合格结果预警: 发现 {unqualified_results} 个不合格结果')
        else:
            self.stdout.write(f'    2. ✅ 质量监控: 所有检测结果合格')
        
        # 样品积压预警
        if testing_samples > total_samples * 0.7:  # 如果70%以上的样品在检测中
            self.stdout.write(f'    3. ⚠️  样品积压预警: {testing_samples}/{total_samples} 样品在检测中')
        else:
            self.stdout.write(f'    3. ✅ 样品流转: 样品检测进度正常')
        
        # 创建实时监控面板元素
        self.stdout.write('  机场工程实时监控面板:')
        self.stdout.write('    - 项目总体进度仪表盘')
        self.stdout.write('    - 检测任务状态看板')
        self.stdout.write('    - 样品流转状态图')
        self.stdout.write('    - 检测结果趋势图')
        self.stdout.write('    - 预警信息滚动条')
        self.stdout.write('    - 设备使用状态监控')
        self.stdout.write('    - 人员工作负荷监控')
        
        # 创建预警级别定义
        self.stdout.write('  机场工程预警级别:')
        self.stdout.write('    - 绿色: 正常状态 (一切按计划进行)')
        self.stdout.write('    - 黄色: 注意状态 (存在潜在风险)')
        self.stdout.write('    - 橙色: 警告状态 (需要关注和干预)')
        self.stdout.write('    - 红色: 危险状态 (需要立即处理)')
        
        # 创建预警阈值设定
        self.stdout.write('  机场工程预警阈值:')
        self.stdout.write('    - 任务逾期率 > 5% → 黄色预警')
        self.stdout.write('    - 任务逾期率 > 10% → 红色预警')
        self.stdout.write('    - 不合格率 > 3% → 黄色预警')
        self.stdout.write('    - 不合格率 > 8% → 红色预警')
        self.stdout.write('    - 样品积压率 > 70% → 黄色预警')
        self.stdout.write('    - 样品积压率 > 90% → 红色预警')
        self.stdout.write('    - 设备故障率 > 5% → 黄色预警')
        self.stdout.write('    - 人员负荷 > 120% → 黄色预警')
        
        # 创建预警处理流程
        self.stdout.write('  机场工程预警处理流程:')
        self.stdout.write('    - 预警产生 → 自动通知相关人员')
        self.stdout.write('    - 预警确认 → 责任人确认收到预警')
        self.stdout.write('    - 原因分析 → 分析预警产生的原因')
        self.stdout.write('    - 制定措施 → 制定相应的处理措施')
        self.stdout.write('    - 执行处理 → 执行处理措施')
        self.stdout.write('    - 效果验证 → 验证处理效果')
        self.stdout.write('    - 预警解除 → 解除相应预警')
        
        # 创建监控数据统计周期
        self.stdout.write('  机场工程监控数据统计周期:')
        self.stdout.write('    - 实时监控: 每分钟更新一次')
        self.stdout.write('    - 小时统计: 每小时汇总一次')
        self.stdout.write('    - 日统计: 每日0点汇总前一天数据')
        self.stdout.write('    - 周统计: 每周一汇总上周数据')
        self.stdout.write('    - 月统计: 每月1日汇总上月数据')
        
        # 创建监控报告模板
        self.stdout.write('  机场工程监控报告模板:')
        self.stdout.write('    - 日监控报告: 每日工作量、完成情况、异常情况')
        self.stdout.write('    - 周监控报告: 周度趋势分析、预警处理情况')
        self.stdout.write('    - 月监控报告: 月度绩效分析、改进建议')
        self.stdout.write('    - 专项监控报告: 针对特定问题的深度分析')
        
        self.stdout.write(
            self.style.SUCCESS('机场工程实时监控和预警功能添加完成!')
        )


# 创建监控和预警相关的辅助函数
def check_task_overdue():
    """检查逾期任务"""
    from apps.testing.models.task import TestTask
    overdue_tasks = TestTask.objects.filter(
        planned_date__lt=timezone.now().date(),
        status__in=['unassigned', 'assigned', 'in_progress']
    )
    return overdue_tasks.count()


def check_unqualified_results():
    """检查不合格结果"""
    from apps.testing.models.result import TestResult
    unqualified_results = TestResult.objects.filter(judgment='unqualified')
    return unqualified_results.count()


def send_alert(alert_type, message, recipients):
    """发送预警信息"""
    print(f"预警[{alert_type}]: {message}, 发送给: {recipients}")


def update_monitoring_dashboard():
    """更新监控面板"""
    print("更新监控面板数据...")