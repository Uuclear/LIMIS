"""
机场工程样品管理功能优化
为浦东国际机场四期扩建工程优化样品管理流程
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

from apps.samples.models import Sample
from apps.commissions.models import Commission
from apps.system.models import User


class Command(BaseCommand):
    help = '优化机场工程样品管理功能'

    def handle(self, *args, **options):
        self.stdout.write('正在优化机场工程样品管理功能...')
        
        # 获取相关委托单
        commission = Commission.objects.filter(
            project_name__contains='浦东机场四期扩建'
        ).first()
        
        if not commission:
            self.stderr.write('  错误: 找不到相关的委托单')
            return
        
        # 创建机场工程专用的样品类型
        sample_types = [
            {
                'name': '道面混凝土试件',
                'category': '混凝土试件',
                'material_type': 'C40混凝土',
                'storage_location': '道面实验室-养护室A区',
                'remark': '用于道面混凝土强度检测'
            },
            {
                'name': '地基混凝土试件',
                'category': '混凝土试件',
                'material_type': 'C35混凝土',
                'storage_location': '地基实验室-养护室B区',
                'remark': '用于地基混凝土强度检测'
            },
            {
                'name': '钢筋样品',
                'category': '钢筋',
                'material_type': 'HRB400螺纹钢',
                'storage_location': '材料实验室-钢筋存放区',
                'remark': '直径20-32mm螺纹钢'
            },
            {
                'name': '沥青混合料',
                'category': '沥青混合料',
                'material_type': 'AC-20C',
                'storage_location': '道路实验室-样品室',
                'remark': '道面沥青混合料'
            },
            {
                'name': '道砟样品',
                'category': '道砟',
                'material_type': '一级道砟',
                'storage_location': '道路实验室-道砟存放区',
                'remark': '道面基层用道砟'
            },
            {
                'name': '土工材料',
                'category': '土工材料',
                'material_type': '粘土',
                'storage_location': '土工实验室-样品室',
                'remark': '地基处理用土样'
            },
            {
                'name': '防水材料',
                'category': '防水材料',
                'material_type': 'SBS改性沥青防水卷材',
                'storage_location': '材料实验室-防水材料区',
                'remark': '地下室防水用材料'
            },
            {
                'name': '钢筋连接件',
                'category': '钢筋连接',
                'material_type': '直螺纹套筒连接件',
                'storage_location': '材料实验室-连接件区',
                'remark': '钢筋机械连接件'
            }
        ]
        
        # 创建样品
        for i, sample_data in enumerate(sample_types, start=1):
            sample_no = f'SP-AIRPORT-{i:03d}'
            sample, created = Sample.objects.get_or_create(
                sample_no=sample_no,
                defaults={
                    'name': sample_data['name'],
                    'category': sample_data['category'],
                    'material_type': sample_data['material_type'],
                    'production_date': timezone.now().date() - timezone.timedelta(days=i*7),
                    'quantity': 1,
                    'unit': '批' if '批' in sample_data['remark'] else '组',
                    'storage_location': sample_data['storage_location'],
                    'remark': sample_data['remark'],
                    'status': 'registered',
                    'received_date': timezone.now().date(),
                    'received_by': User.objects.filter(is_superuser=True).first() or User.objects.first(),
                    'commission': commission
                }
            )
            if created:
                self.stdout.write(f'  创建样品: {sample.sample_no} - {sample.name}')
        
        # 创建样品状态流转说明
        self.stdout.write('  机场工程样品状态流转:')
        self.stdout.write('    registered → assigned → testing → tested → reported → archived')
        self.stdout.write('    - registered: 已登记')
        self.stdout.write('    - assigned: 已分配')
        self.stdout.write('    - testing: 检测中')
        self.stdout.write('    - tested: 已检测')
        self.stdout.write('    - reported: 已出报告')
        self.stdout.write('    - archived: 已归档')
        
        # 创建样品存储区域
        storage_areas = [
            '道面实验室-养护室A区',
            '地基实验室-养护室B区',
            '材料实验室-钢筋存放区',
            '道路实验室-样品室',
            '土工实验室-样品室',
            '材料实验室-防水材料区',
            '材料实验室-连接件区',
            '留样室-长期保存区',
            '留样室-短期保存区',
            '危废暂存区'
        ]
        
        self.stdout.write('  机场工程样品存储区域:')
        for area in storage_areas:
            self.stdout.write(f'    - {area}')
        
        # 创建样品标签模板
        self.stdout.write('  机场工程样品标签包含信息:')
        self.stdout.write('    - 样品编号')
        self.stdout.write('    - 样品名称')
        self.stdout.write('    - 委托单号')
        self.stdout.write('    - 项目名称')
        self.stdout.write('    - 取样日期')
        self.stdout.write('    - 有效期')
        self.stdout.write('    - 存放位置')
        self.stdout.write('    - 二维码标识')
        
        # 创建样品追溯信息
        self.stdout.write('  机场工程样品追溯信息:')
        self.stdout.write('    - 来源工程部位')
        self.stdout.write('    - 施工单位')
        self.stdout.write('    - 取样人员')
        self.stdout.write('    - 取样时间')
        self.stdout.write('    - 运输记录')
        self.stdout.write('    - 接收记录')
        self.stdout.write('    - 检测记录')
        self.stdout.write('    - 结果报告')
        
        self.stdout.write(
            self.style.SUCCESS('机场工程样品管理功能优化完成!')
        )