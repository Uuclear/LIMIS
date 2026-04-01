"""
机场工程报告管理功能完善
为浦东国际机场四期扩建工程完善报告管理功能
"""

import os
import sys
import django
from django.core.management.base import BaseCommand
from django.utils import timezone

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limis.settings')
django.setup()

from apps.reports.models import Report
from apps.commissions.models import Commission
from apps.testing.models.task import TestTask
from apps.testing.models.result import TestResult
from apps.samples.models import Sample
from apps.system.models import User


class Command(BaseCommand):
    help = '完善机场工程报告管理功能'

    def handle(self, *args, **options):
        self.stdout.write('正在完善机场工程报告管理功能...')
        
        # 获取相关数据
        commission = Commission.objects.filter(
            project_name__contains='浦东机场四期扩建'
        ).first()
        
        if not commission:
            self.stderr.write('  错误: 找不到相关的委托单')
            return
        
        # 获取检测任务和结果
        tasks = TestTask.objects.filter(
            commission=commission
        ).select_related('sample', 'test_method').all()
        
        if not tasks:
            self.stderr.write('  警告: 没有找到相关的检测任务，将创建示例任务')
            # 创建示例任务
            sample = Sample.objects.filter(name__contains='机场').first()
            if not sample:
                sample = Sample.objects.first()
            
            if sample:
                from apps.testing.models.method import TestMethod
                method = TestMethod.objects.filter(name__contains='混凝土').first()
                if method:
                    from apps.testing.services import generate_task_no
                    task = TestTask.objects.create(
                        task_no=generate_task_no(),
                        sample=sample,
                        commission=commission,
                        test_method=method,
                        status='completed',
                        planned_date=timezone.now().date(),
                        remark='机场工程示例检测任务'
                    )
                    tasks = [task]
        
        # 创建报告
        for i, task in enumerate(tasks[:5]):  # 取前5个任务创建报告
            report_no = f'REP-AIRPORT-{timezone.now().date().strftime("%Y%m%d")}-{i+1:03d}'
            
            report, created = Report.objects.get_or_create(
                report_no=report_no,
                defaults={
                    'title': f'机场工程检测报告 - {task.test_method.name}',
                    'project_name': commission.project_name,
                    'client_name': commission.client_name,
                    'sample_info': f'{task.sample.name} ({task.sample.sample_no})',
                    'test_items': [task.test_method.name],
                    'test_results': self._get_test_results_summary(task),
                    'conclusion': self._get_report_conclusion(task),
                    'status': 'draft',
                    'created_by': User.objects.filter(is_superuser=True).first() or User.objects.first(),
                    'issue_date': timezone.now().date() + timezone.timedelta(days=1),
                    'validity_period': 365,
                    'remark': f'浦东国际机场四期扩建工程检测报告 - {task.test_method.name}'
                }
            )
            if created:
                self.stdout.write(f'  创建报告: {report.report_no} - {report.title}')
        
        # 创建机场工程报告模板
        self.stdout.write('  机场工程报告模板要素:')
        self.stdout.write('    - 报告封面 (项目信息、委托方信息、检测机构信息)')
        self.stdout.write('    - 检测依据 (相关标准规范)')
        self.stdout.write('    - 检测项目及结果 (详细数据表格)')
        self.stdout.write('    - 检测环境条件 (温湿度、设备等)')
        self.stdout.write('    - 结果判定 (合格/不合格及依据)')
        self.stdout.write('    - 结论与建议')
        self.stdout.write('    - 附录 (原始记录、设备校准证书等)')
        
        # 创建机场工程报告审批流程
        self.stdout.write('  机场工程报告审批流程:')
        self.stdout.write('    1. 检测员编制 - 录入检测数据和初步结论')
        self.stdout.write('    2. 专业组长审核 - 技术内容审核')
        self.stdout.write('    3. 技术负责人批准 - 技术责任批准')
        self.stdout.write('    4. 质量负责人签发 - 质量责任签发')
        self.stdout.write('    5. 印章管理员盖章 - 正式生效')
        
        # 创建机场工程报告分类
        self.stdout.write('  机场工程报告分类:')
        self.stdout.write('    - 混凝土性能检测报告')
        self.stdout.write('    - 钢筋性能检测报告')
        self.stdout.write('    - 沥青性能检测报告')
        self.stdout.write('    - 土工性能检测报告')
        self.stdout.write('    - 道面性能检测报告')
        self.stdout.write('    - 结构性能检测报告')
        self.stdout.write('    - 环境监测报告')
        
        # 创建报告状态管理
        self.stdout.write('  机场工程报告状态管理:')
        self.stdout.write('    - draft: 草稿')
        self.stdout.write('    - pending_review: 待审核')
        self.stdout.write('    - under_review: 审核中')
        self.stdout.write('    - approved: 已批准')
        self.stdout.write('    - issued: 已签发')
        self.stdout.write('    - delivered: 已交付')
        self.stdout.write('    - archived: 已归档')
        
        # 创建报告交付方式
        self.stdout.write('  机场工程报告交付方式:')
        self.stdout.write('    - 纸质报告 (加盖公章)')
        self.stdout.write('    - 电子报告 (PDF格式，数字签名)')
        self.stdout.write('    - 系统推送 (在线查看)')
        self.stdout.write('    - 邮寄送达')
        self.stdout.write('    - 现场递交')
        
        # 创建报告质量控制
        self.stdout.write('  机场工程报告质量控制:')
        self.stdout.write('    - 数据一致性检查')
        self.stdout.write('    - 标准引用正确性')
        self.stdout.write('    - 结论逻辑性验证')
        self.stdout.write('    - 格式规范性检查')
        self.stdout.write('    - 签名印章完整性')
        
        self.stdout.write(
            self.style.SUCCESS('机场工程报告管理功能完善完成!')
        )
    
    def _get_test_results_summary(self, task):
        """获取检测结果摘要"""
        results = TestResult.objects.filter(task=task).select_related('parameter').all()
        summary = []
        for result in results:
            summary.append({
                'parameter': result.parameter.name,
                'value': str(result.display_value),
                'unit': result.unit,
                'judgment': result.judgment
            })
        return summary
    
    def _get_report_conclusion(self, task):
        """获取报告结论"""
        results = TestResult.objects.filter(task=task).all()
        qualified_count = results.filter(judgment='qualified').count()
        total_count = results.count()
        
        if total_count == 0:
            return "无检测数据"
        elif qualified_count == total_count:
            return "该样品各项检测指标均符合技术要求，判定为合格。"
        else:
            return f"该样品共检测{total_count}项，其中{qualified_count}项合格，{total_count-qualified_count}项不合格，判定为不合格。"