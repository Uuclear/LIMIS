"""
管理命令：填充机场工程检测相关的标准规范和参数库
适用于浦东国际机场四期扩建工程
"""

import os
import sys
import django
from django.core.management.base import BaseCommand

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limis.settings')
django.setup()

from apps.standards.models import Standard
from apps.testing.models.method import TestCategory, TestMethod, TestParameter
from apps.testing.models.result import JudgmentRule
from apps.standards.airport_standards_data import (
    AIRPORT_STANDARDS_DATA,
    TEST_CATEGORIES,
    TEST_METHODS,
    TEST_PARAMETERS,
    JUDGMENT_RULES
)


class Command(BaseCommand):
    help = '填充机场工程检测相关的标准规范和参数库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后再填充',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('正在清除现有数据...')
            JudgmentRule.objects.all().delete()
            TestParameter.objects.all().delete()
            TestMethod.objects.all().delete()
            TestCategory.objects.all().delete()
            Standard.objects.all().delete()
        
        # 填充标准规范数据
        self.stdout.write('正在填充标准规范数据...')
        for std_data in AIRPORT_STANDARDS_DATA:
            standard, created = Standard.objects.get_or_create(
                standard_no=std_data['standard_no'],
                defaults={
                    'name': std_data['name'],
                    'category': std_data['category'],
                    'status': std_data['status'],
                    'replaced_case': std_data['replaced_case'],
                    'remark': std_data['remark']
                }
            )
            if created:
                self.stdout.write(f'  创建标准: {standard.standard_no} - {standard.name}')
            else:
                self.stdout.write(f'  已存在: {standard.standard_no} - {standard.name}')

        # 填充检测类别数据
        self.stdout.write('正在填充检测类别数据...')
        category_map = {}  # 用于后续关联
        for cat_data in TEST_CATEGORIES:
            category, created = TestCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'sort_order': cat_data['sort_order']
                }
            )
            category_map[cat_data['code']] = category
            if created:
                self.stdout.write(f'  创建类别: {category.code} - {category.name}')
            else:
                self.stdout.write(f'  已存在: {category.code} - {category.name}')

        # 填充检测方法数据
        self.stdout.write('正在填充检测方法数据...')
        method_map = {}  # 用于后续关联
        for method_data in TEST_METHODS:
            category = category_map.get(method_data['category_code'])
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
            method_map[f"{method_data['standard_no']}_{method_data['name']}"] = method
            if created:
                self.stdout.write(f'  创建方法: {method.standard_no} - {method.name}')
            else:
                self.stdout.write(f'  已存在: {method.standard_no} - {method.name}')

        # 填充检测参数数据
        self.stdout.write('正在填充检测参数数据...')
        for param_data in TEST_PARAMETERS:
            method_key = f"{param_data['method_name'].split(' ')[0]}_{param_data['method_name']}"
            method = method_map.get(method_key)
            if not method:
                # 尝试更精确的匹配
                for key, m in method_map.items():
                    if m.name == param_data['method_name']:
                        method = m
                        break
            
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
            else:
                self.stdout.write(f'  已存在: {parameter.code} - {parameter.name}')

        # 填充判定规则数据
        self.stdout.write('正在填充判定规则数据...')
        for rule_data in JUDGMENT_RULES:
            # 查找对应的参数
            parameter = TestParameter.objects.filter(
                name=rule_data['parameter_name']
            ).first()
            
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
            else:
                self.stdout.write(f'  已存在: {rule.test_parameter.name} - {rule.grade}')

        self.stdout.write(
            self.style.SUCCESS('机场工程检测标准规范和参数库填充完成!')
        )