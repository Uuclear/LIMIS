"""
机场工程检测原始记录模板管理命令
为浦东国际机场四期扩建工程创建检测原始记录模板
"""

import os
import sys
import json
import django
from django.core.management.base import BaseCommand

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limis.settings')
django.setup()

from apps.testing.models.method import TestMethod
from apps.testing.models.record import RecordTemplate


class Command(BaseCommand):
    help = '为机场工程创建检测原始记录模板'

    def handle(self, *args, **options):
        self.stdout.write('正在创建机场工程检测原始记录模板...')
        
        # 混凝土抗压强度试验模板
        concrete_compression_template = {
            "fields": [
                {
                    "id": "specimen_info",
                    "type": "section",
                    "label": "试件信息",
                    "children": [
                        {
                            "id": "specimen_size",
                            "type": "text",
                            "label": "试件尺寸(mm)",
                            "placeholder": "如: 150×150×150"
                        },
                        {
                            "id": "curing_age",
                            "type": "number",
                            "label": "养护龄期(天)",
                            "min": 1,
                            "max": 999
                        },
                        {
                            "id": "failure_load_1",
                            "type": "number",
                            "label": "破坏荷载1(kN)",
                            "step": 0.01
                        },
                        {
                            "id": "failure_load_2",
                            "type": "number",
                            "label": "破坏荷载2(kN)",
                            "step": 0.01
                        },
                        {
                            "id": "failure_load_3",
                            "type": "number",
                            "label": "破坏荷载3(kN)",
                            "step": 0.01
                        },
                        {
                            "id": "calculated_strength_1",
                            "type": "number",
                            "label": "计算强度值1(MPa)",
                            "readonly": True,
                            "step": 0.1
                        },
                        {
                            "id": "calculated_strength_2",
                            "type": "number",
                            "label": "计算强度值2(MPa)",
                            "readonly": True,
                            "step": 0.1
                        },
                        {
                            "id": "calculated_strength_3",
                            "type": "number",
                            "label": "计算强度值3(MPa)",
                            "readonly": True,
                            "step": 0.1
                        },
                        {
                            "id": "average_strength",
                            "type": "number",
                            "label": "平均强度(MPa)",
                            "readonly": True,
                            "step": 0.1
                        },
                        {
                            "id": "strength_result",
                            "type": "text",
                            "label": "强度结果(MPa)",
                            "readonly": True
                        }
                    ]
                },
                {
                    "id": "test_conditions",
                    "type": "section",
                    "label": "试验条件",
                    "children": [
                        {
                            "id": "test_date",
                            "type": "date",
                            "label": "试验日期"
                        },
                        {
                            "id": "temperature",
                            "type": "number",
                            "label": "环境温度(℃)",
                            "step": 0.1
                        },
                        {
                            "id": "humidity",
                            "type": "number",
                            "label": "环境湿度(%)",
                            "step": 0.1
                        },
                        {
                            "id": "tester",
                            "type": "text",
                            "label": "试验人员"
                        },
                        {
                            "id": "reviewer",
                            "type": "text",
                            "label": "复核人员"
                        }
                    ]
                },
                {
                    "id": "remarks",
                    "type": "section",
                    "label": "备注",
                    "children": [
                        {
                            "id": "notes",
                            "type": "textarea",
                            "label": "试验备注",
                            "rows": 4
                        }
                    ]
                }
            ]
        }
        
        # 获取混凝土抗压强度试验方法
        method = TestMethod.objects.filter(name='混凝土立方体抗压强度试验').first()
        if method:
            template, created = RecordTemplate.objects.get_or_create(
                code='CONC_COMPRESS_001',
                defaults={
                    'name': '混凝土立方体抗压强度试验记录',
                    'test_method': method,
                    'version': '1.0',
                    'schema': concrete_compression_template,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  创建模板: {template.code} - {template.name}')
        
        # 钢筋拉伸试验模板
        rebar_tension_template = {
            "fields": [
                {
                    "id": "specimen_info",
                    "type": "section",
                    "label": "试件信息",
                    "children": [
                        {
                            "id": "specimen_diameter",
                            "type": "number",
                            "label": "公称直径(mm)",
                            "step": 0.1
                        },
                        {
                            "id": "cross_section_area",
                            "type": "number",
                            "label": "公称横截面积(mm²)",
                            "step": 0.01
                        },
                        {
                            "id": "original_gauge_length",
                            "type": "number",
                            "label": "原始标距(mm)",
                            "step": 0.1
                        },
                        {
                            "id": "yield_force",
                            "type": "number",
                            "label": "屈服力(kN)",
                            "step": 0.01
                        },
                        {
                            "id": "tensile_force",
                            "type": "number",
                            "label": "最大力(kN)",
                            "step": 0.01
                        },
                        {
                            "id": "fracture_gauge_length",
                            "type": "number",
                            "label": "断后标距(mm)",
                            "step": 0.1
                        },
                        {
                            "id": "yield_strength",
                            "type": "number",
                            "label": "屈服强度(MPa)",
                            "readonly": True,
                            "step": 0.1
                        },
                        {
                            "id": "tensile_strength",
                            "type": "number",
                            "label": "抗拉强度(MPa)",
                            "readonly": True,
                            "step": 0.1
                        },
                        {
                            "id": "elongation",
                            "type": "number",
                            "label": "断后伸长率(%)",
                            "readonly": True,
                            "step": 0.1
                        }
                    ]
                },
                {
                    "id": "test_conditions",
                    "type": "section",
                    "label": "试验条件",
                    "children": [
                        {
                            "id": "test_date",
                            "type": "date",
                            "label": "试验日期"
                        },
                        {
                            "id": "temperature",
                            "type": "number",
                            "label": "环境温度(℃)",
                            "step": 0.1
                        },
                        {
                            "id": "humidity",
                            "type": "number",
                            "label": "环境湿度(%)",
                            "step": 0.1
                        },
                        {
                            "id": "tester",
                            "type": "text",
                            "label": "试验人员"
                        },
                        {
                            "id": "reviewer",
                            "type": "text",
                            "label": "复核人员"
                        }
                    ]
                },
                {
                    "id": "remarks",
                    "type": "section",
                    "label": "备注",
                    "children": [
                        {
                            "id": "notes",
                            "type": "textarea",
                            "label": "试验备注",
                            "rows": 4
                        }
                    ]
                }
            ]
        }
        
        # 获取钢筋拉伸试验方法
        method = TestMethod.objects.filter(name='钢筋拉伸试验').first()
        if method:
            template, created = RecordTemplate.objects.get_or_create(
                code='REBAR_TENSION_001',
                defaults={
                    'name': '钢筋拉伸试验记录',
                    'test_method': method,
                    'version': '1.0',
                    'schema': rebar_tension_template,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  创建模板: {template.code} - {template.name}')
        
        # 沥青针入度试验模板
        asphalt_penetration_template = {
            "fields": [
                {
                    "id": "specimen_info",
                    "type": "section",
                    "label": "试样信息",
                    "children": [
                        {
                            "id": "sample_temp",
                            "type": "number",
                            "label": "试样温度(℃)",
                            "step": 0.1
                        },
                        {
                            "id": "penetration_time",
                            "type": "number",
                            "label": "针入时间(s)",
                            "step": 0.1
                        },
                        {
                            "id": "needle_weight",
                            "type": "number",
                            "label": "针及针连杆重量(g)",
                            "step": 0.01
                        },
                        {
                            "id": "penetration_1",
                            "type": "number",
                            "label": "针入度1(0.1mm)",
                            "step": 1
                        },
                        {
                            "id": "penetration_2",
                            "type": "number",
                            "label": "针入度2(0.1mm)",
                            "step": 1
                        },
                        {
                            "id": "penetration_3",
                            "type": "number",
                            "label": "针入度3(0.1mm)",
                            "step": 1
                        },
                        {
                            "id": "average_penetration",
                            "type": "number",
                            "label": "平均针入度(0.1mm)",
                            "readonly": True,
                            "step": 0.1
                        }
                    ]
                },
                {
                    "id": "test_conditions",
                    "type": "section",
                    "label": "试验条件",
                    "children": [
                        {
                            "id": "test_date",
                            "type": "date",
                            "label": "试验日期"
                        },
                        {
                            "id": "temperature",
                            "type": "number",
                            "label": "试验温度(℃)",
                            "step": 0.1
                        },
                        {
                            "id": "tester",
                            "type": "text",
                            "label": "试验人员"
                        },
                        {
                            "id": "reviewer",
                            "type": "text",
                            "label": "复核人员"
                        }
                    ]
                },
                {
                    "id": "remarks",
                    "type": "section",
                    "label": "备注",
                    "children": [
                        {
                            "id": "notes",
                            "type": "textarea",
                            "label": "试验备注",
                            "rows": 4
                        }
                    ]
                }
            ]
        }
        
        # 获取沥青针入度试验方法
        method = TestMethod.objects.filter(name='沥青针入度试验').first()
        if method:
            template, created = RecordTemplate.objects.get_or_create(
                code='ASPHALT_PEN_001',
                defaults={
                    'name': '沥青针入度试验记录',
                    'test_method': method,
                    'version': '1.0',
                    'schema': asphalt_penetration_template,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  创建模板: {template.code} - {template.name}')
        
        # 道面平整度检测模板
        runway_smoothness_template = {
            "fields": [
                {
                    "id": "measurement_info",
                    "type": "section",
                    "label": "测量信息",
                    "children": [
                        {
                            "id": "measurement_point",
                            "type": "text",
                            "label": "测点位置"
                        },
                        {
                            "id": "distance_interval",
                            "type": "number",
                            "label": "测点间距(m)",
                            "step": 0.1
                        },
                        {
                            "id": "elevation_1",
                            "type": "number",
                            "label": "高程1(m)",
                            "step": 0.001
                        },
                        {
                            "id": "elevation_2",
                            "type": "number",
                            "label": "高程2(m)",
                            "step": 0.001
                        },
                        {
                            "id": "elevation_3",
                            "type": "number",
                            "label": "高程3(m)",
                            "step": 0.001
                        },
                        {
                            "id": "elevation_4",
                            "type": "number",
                            "label": "高程4(m)",
                            "step": 0.001
                        },
                        {
                            "id": "elevation_5",
                            "type": "number",
                            "label": "高程5(m)",
                            "step": 0.001
                        },
                        {
                            "id": "ir_value",
                            "type": "number",
                            "label": "IRI值(m/km)",
                            "readonly": True,
                            "step": 0.01
                        },
                        {
                            "id": "standard_deviation",
                            "type": "number",
                            "label": "标准差(mm)",
                            "readonly": True,
                            "step": 0.01
                        }
                    ]
                },
                {
                    "id": "test_conditions",
                    "type": "section",
                    "label": "检测条件",
                    "children": [
                        {
                            "id": "test_date",
                            "type": "date",
                            "label": "检测日期"
                        },
                        {
                            "id": "weather",
                            "type": "text",
                            "label": "天气状况"
                        },
                        {
                            "id": "temperature",
                            "type": "number",
                            "label": "环境温度(℃)",
                            "step": 0.1
                        },
                        {
                            "id": "tester",
                            "type": "text",
                            "label": "检测人员"
                        },
                        {
                            "id": "reviewer",
                            "type": "text",
                            "label": "复核人员"
                        }
                    ]
                },
                {
                    "id": "remarks",
                    "type": "section",
                    "label": "备注",
                    "children": [
                        {
                            "id": "notes",
                            "type": "textarea",
                            "label": "检测备注",
                            "rows": 4
                        }
                    ]
                }
            ]
        }
        
        # 获取道面平整度检测方法
        method = TestMethod.objects.filter(name='道面平整度检测').first()
        if method:
            template, created = RecordTemplate.objects.get_or_create(
                code='RUNWAY_SMOOTH_001',
                defaults={
                    'name': '道面平整度检测记录',
                    'test_method': method,
                    'version': '1.0',
                    'schema': runway_smoothness_template,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  创建模板: {template.code} - {template.name}')
        
        self.stdout.write(
            self.style.SUCCESS('机场工程检测原始记录模板创建完成!')
        )