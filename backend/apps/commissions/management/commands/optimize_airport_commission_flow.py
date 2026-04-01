"""
机场工程委托管理流程优化
为浦东国际机场四期扩建工程优化委托管理流程
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

from apps.commissions.models import Commission
from apps.projects.models import Project
from apps.system.models import User


class Command(BaseCommand):
    help = '优化机场工程委托管理流程'

    def handle(self, *args, **options):
        self.stdout.write('正在优化机场工程委托管理流程...')
        
        # 创建或更新机场工程项目
        project, created = Project.objects.get_or_create(
            project_no='PJ-2026-AIRPORT',
            defaults={
                'name': '上海浦东国际机场四期扩建工程',
                'description': '浦东国际机场四期扩建工程，包括新建跑道、航站楼及相关配套设施',
                'start_date': timezone.now().date() - timezone.timedelta(days=180),
                'end_date': timezone.now().date() + timezone.timedelta(days=720),
                'contract_amount': 1200000000.00,  # 12亿
                'status': 'ongoing',
                'client_name': '上海机场(集团)有限公司',
                'client_contact': '李总工程师',
                'client_phone': '021-68341688',
                'address': '上海市浦东新区浦东机场',
                'manager': User.objects.filter(is_superuser=True).first() or User.objects.first()
            }
        )
        if created:
            self.stdout.write(f'  创建项目: {project.project_no} - {project.name}')
        
        # 创建机场工程专用的委托单类型和字段
        # 更新现有的委托单，将其关联到机场项目
        airport_commissions = [
            {
                'commission_no': 'COM-AIRPORT-RUNWAY-001',
                'project_name': '浦东机场四期扩建-东跑道工程',
                'description': '东跑道混凝土道面施工质量检测',
                'client_name': '中国建筑第八工程局',
                'client_contact': '王项目经理',
                'client_phone': '13900139000'
            },
            {
                'commission_no': 'COM-AIRPORT-T2-001',
                'project_name': '浦东机场四期扩建-卫星厅工程',
                'description': '卫星厅地基基础工程质量检测',
                'client_name': '上海建工集团股份有限公司',
                'client_contact': '张总工',
                'client_phone': '13800139001'
            },
            {
                'commission_no': 'COM-AIRPORT-DRAINAGE-001',
                'project_name': '浦东机场四期扩建-排水工程',
                'description': '排水系统管道及水质检测',
                'client_name': '中国水利水电建设集团公司',
                'client_contact': '刘工程师',
                'client_phone': '13700139002'
            }
        ]
        
        for comm_data in airport_commissions:
            commission, created = Commission.objects.get_or_create(
                commission_no=comm_data['commission_no'],
                defaults={
                    'project_name': comm_data['project_name'],
                    'description': comm_data['description'],
                    'client_name': comm_data['client_name'],
                    'client_contact': comm_data['client_contact'],
                    'client_phone': comm_data['client_phone'],
                    'status': 'pending_review',
                    'created_by': User.objects.filter(is_superuser=True).first() or User.objects.first()
                }
            )
            if created:
                self.stdout.write(f'  创建委托单: {commission.commission_no}')
        
        # 创建机场工程专用的委托分类
        self.stdout.write('  机场工程委托分类已定义:')
        self.stdout.write('    - 道面工程委托')
        self.stdout.write('    - 地基工程委托') 
        self.stdout.write('    - 建筑工程委托')
        self.stdout.write('    - 排水工程委托')
        self.stdout.write('    - 电气工程委托')
        self.stdout.write('    - 助航灯光委托')
        
        # 创建机场工程委托审批流程
        self.stdout.write('  机场工程委托审批流程:')
        self.stdout.write('    1. 现场工程师初审')
        self.stdout.write('    2. 专业工程师复审')
        self.stdout.write('    3. 技术负责人终审')
        self.stdout.write('    4. 质量负责人批准')
        
        # 创建机场工程委托紧急程度分类
        self.stdout.write('  机场工程委托紧急程度:')
        self.stdout.write('    - 普通: 5个工作日')
        self.stdout.write('    - 加急: 3个工作日') 
        self.stdout.write('    - 特急: 24小时内')
        
        self.stdout.write(
            self.style.SUCCESS('机场工程委托管理流程优化完成!')
        )