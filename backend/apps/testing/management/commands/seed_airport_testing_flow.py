"""
机场工程检测流程管理命令
为浦东国际机场四期扩建工程创建完整的检测流程数据
"""

import os
import sys
import django
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limis.settings')
django.setup()

from apps.commissions.models import Commission
from apps.samples.models import Sample
from apps.testing.models.task import TestTask
from apps.testing.models.method import TestMethod
from apps.testing.services import generate_task_no
from apps.system.models import User


class Command(BaseCommand):
    help = '为机场工程创建完整的检测流程数据'

    def handle(self, *args, **options):
        self.stdout.write('正在创建机场工程检测流程数据...')
        
        # 获取或创建测试用户
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.create_superuser(
                    username='admin',
                    password='admin123',
                    email='admin@example.com'
                )
        except:
            # 如果创建失败，尝试获取现有用户
            admin_user = User.objects.first()
            if not admin_user:
                self.stderr.write('错误: 没有可用的用户')
                return
        
        # 创建委托单
        commission, created = Commission.objects.get_or_create(
            commission_no='PJ-2026-AIRPORT-001',
            defaults={
                'project_name': '上海浦东国际机场四期扩建工程',
                'client_name': '上海机场集团',
                'client_contact': '张经理',
                'client_phone': '13800138000',
                'description': '浦东国际机场四期扩建工程道面混凝土检测',
                'status': 'pending_review',
                'created_by': admin_user
            }
        )
        if created:
            self.stdout.write(f'  创建委托单: {commission.commission_no}')
        
        # 创建样品
        samples_data = [
            {
                'name': '道面混凝土试件-001',
                'sample_no': 'SP-2026-AIRPORT-001',
                'category': '混凝土试件',
                'material_type': 'C40混凝土',
                'production_date': timezone.now().date() - timedelta(days=28),
                'quantity': 3,
                'unit': '组',
                'storage_location': '养护室-01区',
                'remark': '28天龄期抗压试件'
            },
            {
                'name': '钢筋样品-HRB400-001',
                'sample_no': 'SP-2026-AIRPORT-002',
                'category': '钢筋',
                'material_type': 'HRB400螺纹钢',
                'production_date': timezone.now().date(),
                'quantity': 1,
                'unit': '批',
                'storage_location': '钢筋库-02区',
                'remark': '直径25mm螺纹钢'
            },
            {
                'name': '沥青混合料-001',
                'sample_no': 'SP-2026-AIRPORT-003',
                'category': '沥青混合料',
                'material_type': 'AC-20C',
                'production_date': timezone.now().date(),
                'quantity': 1,
                'unit': '批',
                'storage_location': '材料库-03区',
                'remark': '道面沥青混合料'
            },
            {
                'name': '道砟样品-001',
                'sample_no': 'SP-2026-AIRPORT-004',
                'category': '道砟',
                'material_type': '一级道砟',
                'production_date': timezone.now().date(),
                'quantity': 1,
                'unit': '批',
                'storage_location': '道砟库-04区',
                'remark': '道面基层用道砟'
            }
        ]
        
        for sample_data in samples_data:
            sample, created = Sample.objects.get_or_create(
                sample_no=sample_data['sample_no'],
                defaults={
                    'name': sample_data['name'],
                    'category': sample_data['category'],
                    'material_type': sample_data['material_type'],
                    'production_date': sample_data['production_date'],
                    'quantity': sample_data['quantity'],
                    'unit': sample_data['unit'],
                    'storage_location': sample_data['storage_location'],
                    'remark': sample_data['remark'],
                    'status': 'registered',
                    'received_date': timezone.now().date(),
                    'received_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'  创建样品: {sample.sample_no}')
        
        # 创建检测任务
        # 获取一些常用的检测方法
        methods = {
            '混凝土抗压': TestMethod.objects.filter(name='混凝土立方体抗压强度试验').first(),
            '钢筋拉伸': TestMethod.objects.filter(name='钢筋拉伸试验').first(),
            '沥青针入': TestMethod.objects.filter(name='沥青针入度试验').first(),
        }
        
        # 创建检测任务
        tasks_data = [
            {
                'sample_no': 'SP-2026-AIRPORT-001',
                'method_name': '混凝土立方体抗压强度试验',
                'parameter_code': 'COMPRESSIVE_STRENGTH',
                'planned_date': timezone.now().date() + timedelta(days=1),
                'remark': 'C40混凝土28天抗压强度检测'
            },
            {
                'sample_no': 'SP-2026-AIRPORT-002',
                'method_name': '钢筋拉伸试验',
                'parameter_code': 'YIELD_STRENGTH',
                'planned_date': timezone.now().date() + timedelta(days=1),
                'remark': 'HRB400钢筋屈服强度检测'
            },
            {
                'sample_no': 'SP-2026-AIRPORT-003',
                'method_name': '沥青针入度试验',
                'parameter_code': 'PENETRATION',
                'planned_date': timezone.now().date() + timedelta(days=1),
                'remark': 'AC-20C沥青针入度检测'
            }
        ]
        
        for task_data in tasks_data:
            sample = Sample.objects.filter(sample_no=task_data['sample_no']).first()
            method = TestMethod.objects.filter(name=task_data['method_name']).first()
            
            if not sample or not method:
                self.stderr.write(f'  错误: 找不到样品或方法 {task_data["sample_no"]} - {task_data["method_name"]}')
                continue
            
            task, created = TestTask.objects.get_or_create(
                task_no=generate_task_no(),
                defaults={
                    'sample': sample,
                    'commission': commission,
                    'test_method': method,
                    'status': 'unassigned',
                    'planned_date': task_data['planned_date'],
                    'remark': task_data['remark']
                }
            )
            if created:
                self.stdout.write(f'  创建检测任务: {task.task_no}')
        
        # 创建更多类型的检测任务
        additional_tasks = [
            {
                'sample_no': 'SP-2026-AIRPORT-001',
                'method_name': '混凝土抗折强度试验',
                'parameter_code': 'FLEXURAL_STRENGTH',
                'planned_date': timezone.now().date() + timedelta(days=2),
                'remark': 'C40混凝土抗折强度检测'
            },
            {
                'sample_no': 'SP-2026-AIRPORT-002',
                'method_name': '钢筋弯曲试验',
                'parameter_code': 'BENDING_ANGLE',
                'planned_date': timezone.now().date() + timedelta(days=2),
                'remark': 'HRB400钢筋弯曲性能检测'
            }
        ]
        
        for task_data in additional_tasks:
            sample = Sample.objects.filter(sample_no=task_data['sample_no']).first()
            method = TestMethod.objects.filter(name=task_data['method_name']).first()
            
            if not sample or not method:
                self.stderr.write(f'  错误: 找不到样品或方法 {task_data["sample_no"]} - {task_data["method_name"]}')
                continue
            
            task, created = TestTask.objects.get_or_create(
                task_no=generate_task_no(),
                defaults={
                    'sample': sample,
                    'commission': commission,
                    'test_method': method,
                    'status': 'unassigned',
                    'planned_date': task_data['planned_date'],
                    'remark': task_data['remark']
                }
            )
            if created:
                self.stdout.write(f'  创建检测任务: {task.task_no}')
        
        self.stdout.write(
            self.style.SUCCESS('机场工程检测流程数据创建完成!')
        )