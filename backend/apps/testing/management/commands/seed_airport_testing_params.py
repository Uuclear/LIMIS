"""
机场工程检测项目参数库管理命令
为浦东国际机场四期扩建工程添加完整的检测参数库
"""

import os
import sys
import django
from django.core.management.base import BaseCommand

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limis.settings')
django.setup()

from apps.testing.models.method import TestCategory, TestMethod, TestParameter
from apps.testing.models.result import JudgmentRule


class Command(BaseCommand):
    help = '为机场工程添加完整的检测项目参数库'

    def handle(self, *args, **options):
        self.stdout.write('正在添加机场工程检测项目参数库...')
        
        # 添加更多检测类别
        categories_data = [
            {"name": "道面检测", "code": "RUNWAY", "sort_order": 8},
            {"name": "地基检测", "code": "FOUNDATION", "sort_order": 9},
            {"name": "排水检测", "code": "DRAINAGE", "sort_order": 10},
            {"name": "环保检测", "code": "ENVIRONMENT", "sort_order": 11}
        ]
        
        for cat_data in categories_data:
            category, created = TestCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'sort_order': cat_data['sort_order']
                }
            )
            if created:
                self.stdout.write(f'  创建类别: {category.code} - {category.name}')
        
        # 添加更多检测方法
        methods_data = [
            # 道面检测方法
            {
                "name": "道面平整度检测",
                "standard_no": "MH/T 5010-2017",
                "standard_name": "民用机场沥青混凝土道面施工技术规范",
                "category_code": "RUNWAY"
            },
            {
                "name": "道面摩擦系数检测",
                "standard_no": "MH/T 5010-2017",
                "standard_name": "民用机场沥青混凝土道面施工技术规范",
                "category_code": "RUNWAY"
            },
            {
                "name": "道面厚度检测",
                "standard_no": "MH/T 5024-2018",
                "standard_name": "民用机场水泥混凝土面层施工技术规范",
                "category_code": "RUNWAY"
            },
            
            # 地基检测方法
            {
                "name": "地基承载力检测",
                "standard_no": "GB 50007-2011",
                "standard_name": "建筑地基基础设计规范",
                "category_code": "FOUNDATION"
            },
            {
                "name": "地基压实度检测",
                "standard_no": "JTG F10-2006",
                "standard_name": "公路路基施工技术规范",
                "category_code": "FOUNDATION"
            },
            
            # 排水检测方法
            {
                "name": "排水管道渗漏检测",
                "standard_no": "GB 50268-2008",
                "standard_name": "给水排水管道工程施工及验收规范",
                "category_code": "DRAINAGE"
            },
            {
                "name": "水质检测",
                "standard_no": "GB 3838-2002",
                "standard_name": "地表水环境质量标准",
                "category_code": "ENVIRONMENT"
            },
            
            # 环保检测方法
            {
                "name": "噪声检测",
                "standard_no": "GB 3096-2008",
                "standard_name": "声环境质量标准",
                "category_code": "ENVIRONMENT"
            },
            {
                "name": "粉尘浓度检测",
                "standard_no": "GB/T 15432-1995",
                "standard_name": "环境空气 总悬浮颗粒物的测定 重量法",
                "category_code": "ENVIRONMENT"
            }
        ]
        
        for method_data in methods_data:
            category = TestCategory.objects.filter(code=method_data['category_code']).first()
            if not category:
                self.stderr.write(f'  错误: 找不到类别 {method_data["category_code"]}')
                continue
            
            method, created = TestMethod.objects.get_or_create(
                standard_no=method_data['standard_no'],
                defaults={
                    'name': method_data['name'],
                    'standard_name': method_data['standard_name'],
                    'category': category,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  创建方法: {method.standard_no} - {method.name}')
        
        # 添加更多检测参数
        parameters_data = [
            # 道面参数
            {
                "method_name": "道面平整度检测",
                "name": "IRI值",
                "code": "IRI",
                "unit": "m/km",
                "precision": 2,
                "min_value": 0,
                "max_value": 10
            },
            {
                "method_name": "道面平整度检测",
                "name": "标准差",
                "code": "SD",
                "unit": "mm",
                "precision": 2,
                "min_value": 0,
                "max_value": 10
            },
            {
                "method_name": "道面摩擦系数检测",
                "name": "摩擦系数",
                "code": "FC",
                "unit": "",
                "precision": 2,
                "min_value": 0,
                "max_value": 1
            },
            {
                "method_name": "道面厚度检测",
                "name": "厚度",
                "code": "THICKNESS",
                "unit": "mm",
                "precision": 1,
                "min_value": 0,
                "max_value": 1000
            },
            
            # 地基参数
            {
                "method_name": "地基承载力检测",
                "name": "承载力特征值",
                "code": "BEARING_CAPACITY",
                "unit": "kPa",
                "precision": 0,
                "min_value": 0,
                "max_value": 10000
            },
            {
                "method_name": "地基压实度检测",
                "name": "压实度",
                "code": "COMPACTION_DEGREE",
                "unit": "%",
                "precision": 1,
                "min_value": 0,
                "max_value": 100
            },
            
            # 排水参数
            {
                "method_name": "排水管道渗漏检测",
                "name": "渗漏量",
                "code": "LEAKAGE",
                "unit": "L/min",
                "precision": 2,
                "min_value": 0,
                "max_value": 100
            },
            {
                "method_name": "水质检测",
                "name": "浊度",
                "code": "TURBIDITY",
                "unit": "NTU",
                "precision": 2,
                "min_value": 0,
                "max_value": 10
            },
            {
                "method_name": "水质检测",
                "name": "pH值",
                "code": "PH_VALUE",
                "unit": "",
                "precision": 2,
                "min_value": 0,
                "max_value": 14
            },
            
            # 环保参数
            {
                "method_name": "噪声检测",
                "name": "等效声级",
                "code": "LA_EQ",
                "unit": "dB(A)",
                "precision": 1,
                "min_value": 0,
                "max_value": 120
            },
            {
                "method_name": "粉尘浓度检测",
                "name": "总悬浮颗粒物",
                "code": "TSP",
                "unit": "mg/m³",
                "precision": 3,
                "min_value": 0,
                "max_value": 1
            }
        ]
        
        for param_data in parameters_data:
            method = TestMethod.objects.filter(name=param_data['method_name']).first()
            if not method:
                self.stderr.write(f'  错误: 找不到方法 {param_data["method_name"]}')
                continue

            parameter, created = TestParameter.objects.get_or_create(
                method=method,
                code=param_data['code'],
                defaults={
                    'name': param_data['name'],
                    'unit': param_data['unit'],
                    'precision': param_data['precision'],
                    'min_value': param_data['min_value'],
                    'max_value': param_data['max_value'],
                    'is_required': True
                }
            )
            if created:
                self.stdout.write(f'  创建参数: {parameter.code} - {parameter.name}')
        
        # 添加更多判定规则
        rules_data = [
            # 道面判定规则
            {
                "parameter_name": "IRI值",
                "grade": "机场道面",
                "min_value": None,
                "max_value": 2.5,
                "standard_ref": "MH/T 5010-2017"
            },
            {
                "parameter_name": "摩擦系数",
                "grade": "机场道面",
                "min_value": 0.4,
                "max_value": 1.0,
                "standard_ref": "MH/T 5010-2017"
            },
            {
                "parameter_name": "厚度",
                "grade": "AC面层",
                "min_value": 40.0,
                "max_value": 80.0,
                "standard_ref": "MH/T 5024-2018"
            },
            
            # 地基判定规则
            {
                "parameter_name": "承载力特征值",
                "grade": "一般地基",
                "min_value": 100.0,
                "max_value": 10000.0,
                "standard_ref": "GB 50007-2011"
            },
            {
                "parameter_name": "压实度",
                "grade": "路基",
                "min_value": 95.0,
                "max_value": 100.0,
                "standard_ref": "JTG F10-2006"
            },
            
            # 环保判定规则
            {
                "parameter_name": "等效声级",
                "grade": "机场周边",
                "min_value": None,
                "max_value": 70.0,
                "standard_ref": "GB 3096-2008"
            },
            {
                "parameter_name": "总悬浮颗粒物",
                "grade": "施工场地",
                "min_value": None,
                "max_value": 0.3,
                "standard_ref": "GB/T 15432-1995"
            }
        ]
        
        for rule_data in rules_data:
            parameter = TestParameter.objects.filter(name=rule_data['parameter_name']).first()
            if not parameter:
                self.stderr.write(f'  错误: 找不到参数 {rule_data["parameter_name"]}')
                continue

            rule, created = JudgmentRule.objects.get_or_create(
                test_parameter=parameter,
                grade=rule_data['grade'],
                defaults={
                    'min_value': rule_data['min_value'],
                    'max_value': rule_data['max_value'],
                    'standard_ref': rule_data['standard_ref']
                }
            )
            if created:
                self.stdout.write(f'  创建规则: {rule.test_parameter.name} - {rule.grade}')
        
        self.stdout.write(
            self.style.SUCCESS('机场工程检测项目参数库添加完成!')
        )