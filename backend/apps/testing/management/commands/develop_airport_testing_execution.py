"""
机场工程检测执行模块开发
为浦东国际机场四期扩建工程开发检测执行功能
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
from apps.testing.models.method import TestMethod, TestParameter
from apps.testing.models.record import OriginalRecord
from apps.samples.models import Sample
from apps.system.models import User


class Command(BaseCommand):
    help = '开发机场工程检测执行模块'

    def handle(self, *args, **options):
        self.stdout.write('正在开发机场工程检测执行模块...')
        
        # 获取测试用户
        tester = User.objects.filter(is_superuser=True).first()
        if not tester:
            tester = User.objects.first()
        
        if not tester:
            self.stderr.write('  错误: 没有可用的用户')
            return
        
        # 获取样品和检测方法
        samples = Sample.objects.filter(name__contains='机场').all()[:4]  # 取前4个样品
        if not samples:
            self.stderr.write('  警告: 没有找到机场工程相关的样品，将使用任意样品')
            samples = Sample.objects.all()[:4]
        
        # 获取检测方法
        methods = TestMethod.objects.filter(name__in=[
            '混凝土立方体抗压强度试验',
            '钢筋拉伸试验', 
            '沥青针入度试验',
            '道面平整度检测'
        ]).all()
        
        if not methods:
            self.stderr.write('  警告: 没有找到预设的检测方法，将使用任意方法')
            methods = TestMethod.objects.all()[:4]
        
        # 创建检测任务
        for i, sample in enumerate(samples):
            method = list(methods)[i % len(methods)]  # 循环使用方法
            
            task, created = TestTask.objects.get_or_create(
                task_no=f'TASK-AIRPORT-{i+1:03d}',
                defaults={
                    'sample': sample,
                    'commission': sample.commission if hasattr(sample, 'commission') else None,
                    'test_method': method,
                    'status': 'unassigned',
                    'planned_date': timezone.now().date() + timedelta(days=i+1),
                    'age_days': 28 if '混凝土' in method.name else None,
                    'remark': f'机场工程检测任务 - {method.name}'
                }
            )
            if created:
                self.stdout.write(f'  创建检测任务: {task.task_no} - {method.name}')
        
        # 获取刚创建的任务
        tasks = TestTask.objects.filter(task_no__startswith='TASK-AIRPORT-').all()
        
        # 为任务分配检测员和设备
        for i, task in enumerate(tasks):
            # 更新任务状态为已分配
            task.assigned_tester = tester
            task.status = 'assigned'
            task.save()
            self.stdout.write(f'  分配任务: {task.task_no} 给 {tester.username}')
        
        # 创建检测结果示例
        for task in tasks:
            # 获取任务对应的参数
            parameters = TestParameter.objects.filter(method=task.test_method)[:3]  # 取前3个参数
            
            for j, param in enumerate(parameters):
                result, created = TestResult.objects.get_or_create(
                    task=task,
                    parameter=param,
                    defaults={
                        'raw_value': self._generate_sample_result(param.name, j),
                        'rounded_value': self._generate_sample_result(param.name, j),
                        'display_value': f"{self._generate_sample_result(param.name, j)}{param.unit}",
                        'unit': param.unit,
                        'standard_value': self._get_standard_value(param.name),
                        'design_value': self._get_design_value(param.name),
                        'remark': f'机场工程检测结果 - {param.name}'
                    }
                )
                if created:
                    self.stdout.write(f'  创建检测结果: {task.task_no} - {param.name}')
        
        # 创建原始记录示例
        for task in tasks:
            record, created = OriginalRecord.objects.get_or_create(
                task=task,
                defaults={
                    'template': task.test_method.templates.first() if task.test_method.templates.exists() else None,
                    'template_version': '1.0',
                    'record_data': self._generate_record_data(task),
                    'env_temperature': 20.0,
                    'env_humidity': 60.0,
                    'status': 'draft',
                    'recorder': tester
                }
            )
            if created:
                self.stdout.write(f'  创建原始记录: {task.task_no}')
        
        # 创建机场工程检测执行流程说明
        self.stdout.write('  机场工程检测执行流程:')
        self.stdout.write('    1. 任务分配 - 系统自动分配或人工分配')
        self.stdout.write('    2. 任务领取 - 检测员领取待检任务')
        self.stdout.write('    3. 样品准备 - 准备检测样品和设备')
        self.stdout.write('    4. 检测执行 - 按标准方法进行检测')
        self.stdout.write('    5. 数据记录 - 填写原始记录')
        self.stdout.write('    6. 结果判定 - 系统自动判定或人工判定')
        self.stdout.write('    7. 复核确认 - 二级复核确认结果')
        self.stdout.write('    8. 任务完成 - 更新任务状态')
        
        # 创建检测设备管理
        self.stdout.write('  机场工程检测设备管理:')
        self.stdout.write('    - 万能试验机 - 混凝土、钢筋检测')
        self.stdout.write('    - 压力试验机 - 混凝土抗压检测')
        self.stdout.write('    - 沥青针入度仪 - 沥青性能检测')
        self.stdout.write('    - 平整度仪 - 道面平整度检测')
        self.stdout.write('    - 游标卡尺 - 尺寸测量')
        self.stdout.write('    - 温湿度计 - 环境监测')
        
        # 创建检测环境要求
        self.stdout.write('  机场工程检测环境要求:')
        self.stdout.write('    - 温度: 20±5℃')
        self.stdout.write('    - 湿度: ≤75%RH')
        self.stdout.write('    - 无振动干扰')
        self.stdout.write('    - 无电磁干扰')
        self.stdout.write('    - 清洁无尘')
        
        # 创建检测质量控制
        self.stdout.write('  机场工程检测质量控制:')
        self.stdout.write('    - 标准样品对比')
        self.stdout.write('    - 重复性试验')
        self.stdout.write('    - 再现性试验')
        self.stdout.write('    - 设备期间核查')
        self.stdout.write('    - 人员比对')
        
        self.stdout.write(
            self.style.SUCCESS('机场工程检测执行模块开发完成!')
        )
    
    def _generate_sample_result(self, param_name, index):
        """生成示例检测结果"""
        import random
        
        if '强度' in param_name or '抗压' in param_name:
            return round(random.uniform(30, 60), 1)
        elif '屈服' in param_name:
            return round(random.uniform(400, 500), 1)
        elif '伸长率' in param_name:
            return round(random.uniform(16, 25), 1)
        elif '针入度' in param_name:
            return round(random.uniform(60, 100), 0)
        elif '平整度' in param_name:
            return round(random.uniform(1.0, 3.0), 2)
        else:
            return round(random.uniform(20, 30), 1)
    
    def _get_standard_value(self, param_name):
        """获取标准值"""
        if '强度' in param_name or '抗压' in param_name:
            return '≥30.0 MPa'
        elif '屈服' in param_name:
            return '≥400 MPa'
        elif '伸长率' in param_name:
            return '≥16%'
        elif '针入度' in param_name:
            return '60-100 0.1mm'
        elif '平整度' in param_name:
            return '≤2.5 m/km'
        else:
            return '-'
    
    def _get_design_value(self, param_name):
        """获取设计值"""
        if '强度' in param_name or '抗压' in param_name:
            return 'C30'
        elif '屈服' in param_name:
            return 'HRB400'
        elif '伸长率' in param_name:
            return '≥16%'
        elif '针入度' in param_name:
            return '80 0.1mm'
        elif '平整度' in param_name:
            return '≤2.0 m/km'
        else:
            return '-'
    
    def _generate_record_data(self, task):
        """生成原始记录数据"""
        import random
        
        data = {
            "specimen_info": {
                "specimen_size": "150×150×150 mm" if '混凝土' in task.test_method.name else "Φ25 mm",
                "curing_age": 28 if '混凝土' in task.test_method.name else 0,
                "failure_load_1": round(random.uniform(100, 300), 2) if '混凝土' in task.test_method.name else None,
                "failure_load_2": round(random.uniform(100, 300), 2) if '混凝土' in task.test_method.name else None,
                "failure_load_3": round(random.uniform(100, 300), 2) if '混凝土' in task.test_method.name else None,
                "yield_force": round(random.uniform(200, 300), 2) if '钢筋' in task.test_method.name else None,
                "tensile_force": round(random.uniform(300, 400), 2) if '钢筋' in task.test_method.name else None,
                "penetration_1": round(random.uniform(60, 100), 0) if '沥青' in task.test_method.name else None,
                "penetration_2": round(random.uniform(60, 100), 0) if '沥青' in task.test_method.name else None,
                "penetration_3": round(random.uniform(60, 100), 0) if '沥青' in task.test_method.name else None,
            },
            "test_conditions": {
                "test_date": timezone.now().date().isoformat(),
                "temperature": round(random.uniform(18, 25), 1),
                "humidity": round(random.uniform(50, 70), 1),
                "tester": "张检测员",
                "reviewer": "李工程师"
            },
            "remarks": {
                "notes": f"机场工程检测任务 {task.task_no} 的原始记录"
            }
        }
        return data