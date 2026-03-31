"""
全流程种子数据命令 - 浦东机场四期扩建工程 LIMIS 系统演示数据
覆盖：用户/角色、标准规范、设备、人员、环境监控、项目、委托、样品、
      检测任务、原始记录模板、检测结果、报告、耗材、质量体系、通知
"""
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction


class Command(BaseCommand):
    help = '创建LIMIS全流程演示数据（浦东机场四期扩建工程）'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='清除现有演示数据后重建')

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('=== 开始创建全流程演示数据 ===')

            if options.get('clear'):
                self.clear_data()

            users = self.create_users()
            self.create_staff_profiles(users)
            self.create_standards()
            categories, methods, parameters = self.create_test_methods()
            templates = self.create_record_templates(methods)
            equipment_map = self.create_equipment()
            self.create_monitoring_points()
            project, sub_projects, witness = self.create_project(users)
            self.create_consumables(users)
            commissions = self.create_commissions(project, sub_projects, witness, users)
            samples = self.create_samples(commissions)
            tasks = self.create_test_tasks(samples, methods, users, equipment_map)
            self.create_original_records(tasks, templates, users)
            self.create_test_results(tasks, parameters)
            self.create_reports(commissions, users)
            self.create_quality_records(users)
            self.create_notifications(users)
            self.stdout.write(self.style.SUCCESS('=== 全流程演示数据创建完成 ==='))

    def clear_data(self):
        self.stdout.write('清除旧演示数据...')
        from apps.system.models import Notification
        from apps.quality.models import NonConformity, ManagementReview, InternalAudit
        from apps.reports.models import Report
        from apps.testing.models import TestResult, OriginalRecord, TestTask, RecordTemplate, TestParameter, TestMethod, TestCategory
        from apps.samples.models import Sample
        from apps.commissions.models import Commission
        from apps.projects.models import Project
        from apps.environment.models import MonitoringPoint
        from apps.equipment.models import Equipment
        from apps.consumables.models import Consumable, Supplier
        from apps.staff.models import StaffProfile
        from apps.standards.models import Standard

        NonConformity.objects.filter(nc_no__startswith='BF-2024').delete()
        ManagementReview.objects.filter(review_no__startswith='PG-2024').delete()
        InternalAudit.objects.filter(audit_no__startswith='NB-2024').delete()
        Report.objects.filter(report_no__startswith='JC-2024').delete()
        TestTask.objects.filter(task_no__startswith='TT-2024').delete()
        Sample.objects.filter(sample_no__startswith='YP-2024').delete()
        Commission.objects.filter(commission_no__startswith='WT-2024').delete()
        Project.objects.filter(code='PDJC-2024-001').delete()
        MonitoringPoint.objects.filter(code__in=['YHR-001', 'BYR-001', 'LX-001']).delete()
        Equipment.objects.filter(manage_no__in=['E001', 'E002', 'E003', 'E004', 'E005']).delete()
        Consumable.objects.filter(code__in=['HC-001', 'HC-002', 'HC-003']).delete()
        Supplier.objects.filter(name='上海实验耗材供应商').delete()
        RecordTemplate.objects.filter(code__startswith='TPL-').delete()
        TestParameter.objects.filter(code__in=['compressive_strength', 'yield_strength', 'tensile_strength', 'elongation', 'fineness_modulus']).delete()
        TestMethod.objects.filter(name__in=['混凝土抗压强度试验', '钢筋拉伸性能试验', '钢筋弯曲性能试验', '砂细度模数试验']).delete()
        TestCategory.objects.filter(code__in=['concrete', 'steel', 'aggregate', 'cement']).delete()
        Standard.objects.filter(standard_no__in=['GB/T 50081-2019', 'GB/T 228.1-2021', 'GB 1499.2-2018', 'JGJ 52-2006', 'GB/T 17671-2021']).delete()
        self.stdout.write('  ✓ 旧演示数据清除完成')

    # ─────────────────────────────────────────────────────────────
    # 1. 用户和角色
    # ─────────────────────────────────────────────────────────────
    def create_users(self):
        from apps.system.models import User, Role
        self.stdout.write('创建用户...')

        users_data = [
            ('ltech',      '李',   '技术', 'tech_director',     '技术管理部', '高级工程师',  '13901000001'),
            ('wquality',   '王',   '质量', 'quality_director',  '质量管理部', '质量工程师',  '13901000002'),
            ('zsigner',    '赵',   '签字', 'auth_signer',       '技术管理部', '总工程师',    '13901000003'),
            ('qreviewer',  '钱',   '审核', 'reviewer',          '技术管理部', '工程师',      '13901000004'),
            ('ssupervisor','孙',   '监督', 'supervisor',        '质量管理部', '质量监督员',  '13901000005'),
            ('ztester',    '周',   '检测', 'tester',            '检测一部',   '检测员',      '13901000006'),
            ('wsample',    '吴',   '样品', 'sample_clerk',      '样品管理部', '样品员',      '13901000007'),
            ('zequip',     '郑',   '设备', 'equip_manager',     '设备管理部', '设备工程师',  '13901000008'),
            ('freception', '冯',   '受理', 'reception',         '业务受理部', '受理员',      '13901000009'),
            ('cclient',    '陈',   '委托方','client',           '上海建工集团','见证员',     '13901000010'),
        ]

        users = {}
        # 确保 admin 用户在字典中
        try:
            admin = User.objects.get(username='admin')
            users['admin'] = admin
        except User.DoesNotExist:
            pass

        for username, first_name, last_name, role_code, dept, title, phone in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@limis.local',
                    'phone': phone,
                    'department': dept,
                    'title': title,
                    'is_active': True,
                }
            )
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.department = dept
                user.title = title
                user.phone = phone
                user.save()
            if created:
                user.set_password('Limis@123')
                user.save()
            try:
                role = Role.objects.get(code=role_code)
                user.roles.set([role])
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  角色 {role_code} 不存在，跳过'))
            users[role_code] = user

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建/更新 {len(users)} 个用户'))
        return users

    # ─────────────────────────────────────────────────────────────
    # 2. 人员档案
    # ─────────────────────────────────────────────────────────────
    def create_staff_profiles(self, users):
        from apps.staff.models import StaffProfile
        self.stdout.write('创建人员档案...')

        profile_roles = [
            ('tech_director',    'SP001'),
            ('quality_director', 'SP002'),
            ('auth_signer',      'SP003'),
            ('reviewer',         'SP004'),
            ('supervisor',       'SP005'),
            ('tester',           'SP006'),
            ('sample_clerk',     'SP007'),
            ('equip_manager',    'SP008'),
        ]

        count = 0
        for role_code, emp_no in profile_roles:
            user = users.get(role_code)
            if not user:
                continue
            profile, created = StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    'employee_no': emp_no,
                    'education': 'bachelor',
                    'major': '土木工程',
                    'hire_date': datetime.date(2020, 1, 15),
                }
            )
            if not created and profile.employee_no != emp_no:
                profile.employee_no = emp_no
                profile.save()
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 个人员档案'))

    # ─────────────────────────────────────────────────────────────
    # 3. 标准规范
    # ─────────────────────────────────────────────────────────────
    def create_standards(self):
        from apps.standards.models import Standard
        self.stdout.write('创建标准规范...')

        standards_data = [
            ('GB/T 50081-2019', '混凝土物理力学性能试验方法标准',        'concrete',  datetime.date(2019, 11,  1), datetime.date(2020,  5,  1)),
            ('GB/T 228.1-2021', '金属材料拉伸试验第1部分：室温试验方法', 'steel',     datetime.date(2021,  4, 30), datetime.date(2022,  4,  1)),
            ('GB 1499.2-2018',  '钢筋混凝土用钢第2部分：热轧带肋钢筋',  'steel',     datetime.date(2018, 11,  1), datetime.date(2019, 11,  1)),
            ('JGJ 52-2006',     '普通混凝土用砂、石质量及检验方法标准',  'aggregate', datetime.date(2006, 12,  1), datetime.date(2007,  6,  1)),
            ('GB/T 17671-2021', '水泥胶砂强度检验方法（ISO法）',         'cement',    datetime.date(2021,  4, 30), datetime.date(2022,  4,  1)),
        ]

        count = 0
        for std_no, name, category, pub_date, impl_date in standards_data:
            _, created = Standard.objects.get_or_create(
                standard_no=std_no,
                defaults={
                    'name': name,
                    'category': category,
                    'publish_date': pub_date,
                    'implement_date': impl_date,
                    'status': 'active',
                    'abolish_date': None,
                    'replaced_case': '',
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 条标准规范'))

    # ─────────────────────────────────────────────────────────────
    # 4. 检测类别、方法、参数
    # ─────────────────────────────────────────────────────────────
    def create_test_methods(self):
        from apps.testing.models import TestCategory, TestMethod, TestParameter
        self.stdout.write('创建检测方法和参数...')

        cat_data = [
            ('concrete',  '混凝土检测', 1),
            ('steel',     '钢筋检测',   2),
            ('aggregate', '骨料检测',   3),
            ('cement',    '水泥检测',   4),
        ]
        categories = {}
        for code, name, order in cat_data:
            cat, _ = TestCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'sort_order': order}
            )
            categories[code] = cat

        method_data = [
            ('混凝土抗压强度试验', 'GB/T 50081-2019', '混凝土物理力学性能试验方法标准', 'concrete'),
            ('钢筋拉伸性能试验',   'GB/T 228.1-2021', '金属材料拉伸试验第1部分：室温试验方法', 'steel'),
            ('钢筋弯曲性能试验',   'GB 1499.2-2018',  '钢筋混凝土用钢第2部分：热轧带肋钢筋', 'steel'),
            ('砂细度模数试验',     'JGJ 52-2006',     '普通混凝土用砂、石质量及检验方法标准', 'aggregate'),
        ]
        methods = {}
        for name, std_no, std_name, cat_code in method_data:
            method, _ = TestMethod.objects.get_or_create(
                name=name,
                defaults={
                    'standard_no': std_no,
                    'standard_name': std_name,
                    'category': categories[cat_code],
                    'is_active': True,
                    'description': name,
                }
            )
            methods[name] = method

        param_data = [
            ('混凝土抗压强度', 'compressive_strength', 'MPa', 1, '混凝土抗压强度试验'),
            ('屈服强度',       'yield_strength',        'MPa', 0, '钢筋拉伸性能试验'),
            ('抗拉强度',       'tensile_strength',      'MPa', 0, '钢筋拉伸性能试验'),
            ('断后伸长率',     'elongation',            '%',   1, '钢筋拉伸性能试验'),
            ('细度模数',       'fineness_modulus',      '',    2, '砂细度模数试验'),
        ]
        parameters = {}
        for name, code, unit, precision, method_name in param_data:
            param, _ = TestParameter.objects.get_or_create(
                method=methods[method_name],
                code=code,
                defaults={
                    'name': name,
                    'unit': unit,
                    'precision': precision,
                    'is_required': True,
                }
            )
            parameters[code] = param

        self.stdout.write(self.style.SUCCESS(
            f'  ✓ 创建 {len(categories)} 个类别, {len(methods)} 个方法, {len(parameters)} 个参数'
        ))
        return categories, methods, parameters

    # ─────────────────────────────────────────────────────────────
    # 5. 原始记录模板
    # ─────────────────────────────────────────────────────────────
    def create_record_templates(self, methods):
        from apps.testing.models import RecordTemplate
        self.stdout.write('创建原始记录模板...')

        concrete_schema = {
            "fields": [
                {"name": "specimen_size",  "label": "试件尺寸(mm)",     "type": "text",   "required": True,  "default": "150×150×150"},
                {"name": "test_age",       "label": "试验龄期(d)",       "type": "number", "required": True},
                {"name": "load_1",         "label": "第1块破坏荷载(kN)", "type": "number", "required": True,  "precision": 0.1},
                {"name": "load_2",         "label": "第2块破坏荷载(kN)", "type": "number", "required": True,  "precision": 0.1},
                {"name": "load_3",         "label": "第3块破坏荷载(kN)", "type": "number", "required": True,  "precision": 0.1},
                {"name": "strength_1",     "label": "第1块强度(MPa)",    "type": "number", "calc": "load_1*1000/(150*150)", "precision": 0.1},
                {"name": "strength_2",     "label": "第2块强度(MPa)",    "type": "number", "calc": "load_2*1000/(150*150)", "precision": 0.1},
                {"name": "strength_3",     "label": "第3块强度(MPa)",    "type": "number", "calc": "load_3*1000/(150*150)", "precision": 0.1},
                {"name": "avg_strength",   "label": "平均强度(MPa)",     "type": "number", "calc": "(strength_1+strength_2+strength_3)/3", "precision": 0.1},
                {"name": "equipment_name", "label": "试验设备",           "type": "text",   "required": True},
                {"name": "env_temp",       "label": "环境温度(℃)",       "type": "number", "required": True},
                {"name": "env_humidity",   "label": "环境湿度(%)",        "type": "number", "required": True},
            ]
        }

        steel_schema = {
            "fields": [
                {"name": "diameter",         "label": "公称直径(mm)",    "type": "number", "required": True},
                {"name": "gauge_length",     "label": "标距(mm)",        "type": "number", "required": True},
                {"name": "yield_force",      "label": "屈服力(kN)",      "type": "number", "required": True, "precision": 0.01},
                {"name": "tensile_force",    "label": "极限力(kN)",      "type": "number", "required": True, "precision": 0.01},
                {"name": "final_gauge",      "label": "断后标距(mm)",    "type": "number", "required": True, "precision": 0.5},
                {"name": "cross_section",    "label": "横截面积(mm²)",   "type": "number", "calc": "3.14159*(diameter/2)**2", "precision": 0.01},
                {"name": "yield_strength",   "label": "屈服强度(MPa)",   "type": "number", "calc": "yield_force*1000/cross_section", "precision": 1},
                {"name": "tensile_strength", "label": "抗拉强度(MPa)",   "type": "number", "calc": "tensile_force*1000/cross_section", "precision": 1},
                {"name": "elongation",       "label": "断后伸长率(%)",   "type": "number", "calc": "(final_gauge-gauge_length)/gauge_length*100", "precision": 0.5},
            ]
        }

        bend_schema = {
            "fields": [
                {"name": "diameter",       "label": "公称直径(mm)",  "type": "number", "required": True},
                {"name": "bend_angle",     "label": "弯曲角度(°)",   "type": "number", "required": True, "default": 90},
                {"name": "mandrel_dia",    "label": "弯芯直径(mm)",  "type": "number", "required": True},
                {"name": "bend_result",    "label": "弯曲结果",       "type": "select", "required": True,
                 "options": ["无裂缝", "有裂缝", "断裂"]},
                {"name": "judgment",       "label": "判定",           "type": "text"},
            ]
        }

        sand_schema = {
            "fields": [
                {"name": "sieve_475",    "label": "4.75mm筛余量(g)", "type": "number", "required": True},
                {"name": "sieve_236",    "label": "2.36mm筛余量(g)", "type": "number", "required": True},
                {"name": "sieve_118",    "label": "1.18mm筛余量(g)", "type": "number", "required": True},
                {"name": "sieve_060",    "label": "0.60mm筛余量(g)", "type": "number", "required": True},
                {"name": "sieve_030",    "label": "0.30mm筛余量(g)", "type": "number", "required": True},
                {"name": "sieve_015",    "label": "0.15mm筛余量(g)", "type": "number", "required": True},
                {"name": "fineness_mod", "label": "细度模数",         "type": "number",
                 "calc": "((sieve_475+sieve_236+sieve_118+sieve_060+sieve_030)-5*sieve_015)/100", "precision": 0.01},
            ]
        }

        templates_data = [
            ('TPL-CONCRETE-001', '混凝土抗压强度检测原始记录', '混凝土抗压强度试验', concrete_schema),
            ('TPL-STEEL-001',    '钢筋拉伸性能检测原始记录',   '钢筋拉伸性能试验',   steel_schema),
            ('TPL-STEELBEND-001','钢筋弯曲性能检测原始记录',   '钢筋弯曲性能试验',   bend_schema),
            ('TPL-SAND-001',     '砂细度模数检测原始记录',     '砂细度模数试验',     sand_schema),
        ]

        templates = {}
        count = 0
        for code, name, method_name, schema in templates_data:
            method = methods.get(method_name)
            if not method:
                continue
            tpl, created = RecordTemplate.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'test_method': method,
                    'version': '1.0',
                    'schema': schema,
                    'is_active': True,
                }
            )
            templates[method_name] = tpl
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 个记录模板'))
        return templates

    # ─────────────────────────────────────────────────────────────
    # 6. 仪器设备
    # ─────────────────────────────────────────────────────────────
    def create_equipment(self):
        from apps.equipment.models import Equipment, Calibration
        self.stdout.write('创建仪器设备...')

        today = datetime.date.today()
        year_end = datetime.date(today.year, 12, 31)

        equipment_data = [
            ('YAW-2000B', '微机控制压力试验机', 'YAW-2000B-SN001', 'E001', '济南试金集团',       '2000kN',       '±1%',  datetime.date(2022,  3,  1), 'A'),
            ('UTM-100',   '万能试验机',         'UTM-100-SN001',   'E002', 'MTS系统公司',         '100kN',        '±0.5%',datetime.date(2021,  6, 15), 'A'),
            ('BS-200',    '电子天平',           'BS-200-SN001',    'E003', '梅特勒-托利多',       '200g',         '0.001g',datetime.date(2023, 1, 10), 'B'),
            ('ZS-15',     '水泥净浆搅拌机',     'ZS-15-SN001',     'E004', '无锡建仪',            '-',            '-',    datetime.date(2020,  5, 20), 'C'),
            ('HBY-60B',   '标准养护箱',         'HBY-60B-SN001',   'E005', '天津工程仪器',        '60×40×50cm',   '±1℃', datetime.date(2021,  9,  1), 'B'),
        ]

        equipment_map = {}
        eq_count = 0
        cal_count = 0
        for model_no, name, serial_no, manage_no, manufacturer, measure_range, accuracy, purchase_date, category in equipment_data:
            eq, created = Equipment.objects.get_or_create(
                manage_no=manage_no,
                defaults={
                    'name': name,
                    'model_no': model_no,
                    'serial_no': serial_no,
                    'manufacturer': manufacturer,
                    'category': category,
                    'measure_range': measure_range,
                    'accuracy': accuracy,
                    'purchase_date': purchase_date,
                    'status': 'in_use',
                    'calibration_cycle': 12,
                    'next_calibration_date': year_end,
                }
            )
            equipment_map[manage_no] = eq
            if created:
                eq_count += 1

            # 为每个设备创建一条校准记录
            if not eq.calibrations.exists():
                Calibration.objects.create(
                    equipment=eq,
                    certificate_no=f'CAL-{manage_no}-2024',
                    calibration_date=datetime.date(2024, 1, 10),
                    valid_until=year_end,
                    calibration_org='上海市计量测试技术研究院',
                    conclusion='qualified',
                )
                cal_count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {eq_count} 台设备, {cal_count} 条校准记录'))
        return equipment_map

    # ─────────────────────────────────────────────────────────────
    # 7. 环境监控点
    # ─────────────────────────────────────────────────────────────
    def create_monitoring_points(self):
        from apps.environment.models import MonitoringPoint, EnvRecord
        self.stdout.write('创建环境监控点...')

        points_data = [
            ('养护室',     'YHR-001', '一楼养护室',     18.0, 22.0, 95.0, 100.0),
            ('标养室',     'BYR-001', '二楼标准养护室', 19.0, 21.0, 95.0, 100.0),
            ('力学检测室', 'LX-001',  '一楼力学检测室', 15.0, 25.0, 40.0,  70.0),
        ]

        point_count = 0
        record_count = 0
        now = timezone.now()

        for name, code, location, t_min, t_max, h_min, h_max in points_data:
            point, created = MonitoringPoint.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'location': location,
                    'temp_min': t_min,
                    'temp_max': t_max,
                    'humidity_min': h_min,
                    'humidity_max': h_max,
                    'is_active': True,
                }
            )
            if created:
                point_count += 1

            # 创建24条历史记录（过去24小时，每小时一条）
            if not point.records.exists():
                import random
                records = []
                for h in range(24):
                    recorded_at = now - datetime.timedelta(hours=24 - h)
                    temp = round(random.uniform(t_min + 0.5, t_max - 0.5), 1)
                    humi = round(random.uniform(h_min + 1.0, min(h_max - 1.0, 99.0)), 1)
                    records.append(EnvRecord(
                        point=point,
                        temperature=temp,
                        humidity=humi,
                        recorded_at=recorded_at,
                        is_alarm=False,
                    ))
                EnvRecord.objects.bulk_create(records)
                record_count += len(records)

        self.stdout.write(self.style.SUCCESS(
            f'  ✓ 创建 {point_count} 个监控点, {record_count} 条环境记录'
        ))

    # ─────────────────────────────────────────────────────────────
    # 8. 工程项目
    # ─────────────────────────────────────────────────────────────
    def create_project(self, users):
        from apps.projects.models import Project, Organization, SubProject, Witness
        self.stdout.write('创建工程项目...')

        project, created = Project.objects.get_or_create(
            code='PDJC-2024-001',
            defaults={
                'name': '浦东国际机场四期扩建工程',
                'address': '上海市浦东新区迎宾大道',
                'project_type': 'airport',
                'status': 'active',
                'start_date': datetime.date(2024, 1, 1),
                'end_date': datetime.date(2028, 5, 31),
                'description': '浦东国际机场四期扩建工程，包括新建T3航站楼及配套设施',
            }
        )

        orgs_data = [
            ('上海机场（集团）有限公司',         'builder',     '张建设', '021-96990000'),
            ('上海建工集团股份有限公司',          'contractor',  '李总包', '021-63700000'),
            ('华东建筑设计研究院有限公司',        'designer',    '王设计', '021-22208888'),
            ('上海市建设工程监理咨询有限公司',    'supervisor',  '赵监理', '021-54380000'),
            ('浦东工程检测中心',                  'inspector',   '钱检测', '021-68888888'),
        ]
        for org_name, role, contact, phone in orgs_data:
            Organization.objects.get_or_create(
                project=project,
                name=org_name,
                role=role,
                defaults={'contact_person': contact, 'contact_phone': phone}
            )

        sub_projects_data = [
            ('T3航站楼主体结构', 'T3-ZT', 'T3航站楼主体结构工程'),
            ('站坪及道面工程',   'ZP-DM', '机坪道面混凝土'),
            ('地下综合管廊',     'DX-GL', '地下管廊结构'),
        ]
        sub_projects = {}
        for sp_name, sp_code, sp_desc in sub_projects_data:
            sp, _ = SubProject.objects.get_or_create(
                project=project,
                code=sp_code,
                defaults={'name': sp_name, 'description': sp_desc}
            )
            sub_projects[sp_code] = sp

        # 见证人（需要关联 Organization）
        supervision_org = Organization.objects.filter(
            project=project, name='上海市建设工程监理咨询有限公司'
        ).first()

        witness, _ = Witness.objects.get_or_create(
            project=project,
            name='李见证',
            defaults={
                'id_number': '310101199001011234',
                'organization': supervision_org,
                'phone': '13900000011',
                'certificate_no': 'JZ-SH-2024-001',
                'is_active': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ 创建项目、5个参建单位、3个分部工程、1个见证人'))
        return project, sub_projects, witness

    # ─────────────────────────────────────────────────────────────
    # 9. 委托单
    # ─────────────────────────────────────────────────────────────
    def create_commissions(self, project, sub_projects, witness, users):
        from apps.commissions.models import Commission, CommissionItem
        self.stdout.write('创建委托单...')

        qreviewer = users.get('reviewer')
        sp_t3 = sub_projects.get('T3-ZT')
        sp_zp = sub_projects.get('ZP-DM')

        commissions_data = [
            {
                'commission_no': 'WT-2024-0001',
                'construction_part': 'T3航站楼地下一层承台C40混凝土',
                'commission_date': datetime.date(2024, 3, 1),
                'client_unit': '上海建工集团股份有限公司',
                'client_contact': '李工',
                'client_phone': '13800001111',
                'status': 'reviewed',
                'sub_project': sp_t3,
                'reviewer': qreviewer,
                'review_date': timezone.now() - datetime.timedelta(days=25),
                'items': [
                    {'test_object': '混凝土试块', 'test_item': '抗压强度',
                     'specification': 'C40', 'quantity': 3, 'unit': '组',
                     'test_standard': 'GB/T 50081-2019', 'grade': 'C40'},
                ]
            },
            {
                'commission_no': 'WT-2024-0002',
                'construction_part': 'T3航站楼地下室墙体HRB400钢筋',
                'commission_date': datetime.date(2024, 3, 5),
                'client_unit': '上海建工集团股份有限公司',
                'client_contact': '王工',
                'client_phone': '13800002222',
                'status': 'reviewed',
                'sub_project': sp_t3,
                'reviewer': qreviewer,
                'review_date': timezone.now() - datetime.timedelta(days=20),
                'items': [
                    {'test_object': '热轧带肋钢筋', 'test_item': '拉伸性能',
                     'specification': 'HRB400 φ25', 'quantity': 3, 'unit': '根',
                     'test_standard': 'GB/T 228.1-2021', 'grade': 'HRB400'},
                    {'test_object': '热轧带肋钢筋', 'test_item': '弯曲性能',
                     'specification': 'HRB400 φ25', 'quantity': 3, 'unit': '根',
                     'test_standard': 'GB 1499.2-2018', 'grade': 'HRB400'},
                ]
            },
            {
                'commission_no': 'WT-2024-0003',
                'construction_part': '站坪道面沥青混凝土',
                'commission_date': datetime.date(2024, 3, 10),
                'client_unit': '上海建工集团股份有限公司',
                'client_contact': '张工',
                'client_phone': '13800003333',
                'status': 'pending_review',
                'sub_project': sp_zp,
                'reviewer': None,
                'review_date': None,
                'items': [
                    {'test_object': '粗骨料（碎石）', 'test_item': '压碎指标',
                     'specification': '5-25mm', 'quantity': 1, 'unit': '批',
                     'test_standard': 'JGJ 52-2006', 'grade': ''},
                ]
            },
        ]

        commissions = {}
        comm_count = 0
        item_count = 0

        for cd in commissions_data:
            comm, created = Commission.objects.get_or_create(
                commission_no=cd['commission_no'],
                defaults={
                    'project': project,
                    'sub_project': cd['sub_project'],
                    'construction_part': cd['construction_part'],
                    'commission_date': cd['commission_date'],
                    'client_unit': cd['client_unit'],
                    'client_contact': cd['client_contact'],
                    'client_phone': cd['client_phone'],
                    'witness': witness,
                    'is_witnessed': True,
                    'status': cd['status'],
                    'reviewer': cd['reviewer'],
                    'review_date': cd['review_date'],
                    'review_comment': '资料齐全，符合检测要求' if cd['status'] == 'reviewed' else '',
                }
            )
            commissions[cd['commission_no']] = comm
            if created:
                comm_count += 1
                for item in cd['items']:
                    CommissionItem.objects.create(
                        commission=comm,
                        test_object=item['test_object'],
                        test_item=item['test_item'],
                        test_standard=item.get('test_standard', ''),
                        specification=item.get('specification', ''),
                        grade=item.get('grade', ''),
                        quantity=item['quantity'],
                        unit=item['unit'],
                    )
                    item_count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {comm_count} 个委托单, {item_count} 个委托项目'))
        return commissions

    # ─────────────────────────────────────────────────────────────
    # 10. 样品
    # ─────────────────────────────────────────────────────────────
    def create_samples(self, commissions):
        from apps.samples.models import Sample, SampleGroup
        self.stdout.write('创建样品...')

        today = datetime.date.today()
        comm1 = commissions.get('WT-2024-0001')
        comm2 = commissions.get('WT-2024-0002')

        # 混凝土样品组
        group1, _ = SampleGroup.objects.get_or_create(
            group_no='SG-2024-0001',
            defaults={'name': 'C40混凝土试块组', 'sample_count': 3, 'description': 'T3航站楼地下一层承台C40混凝土'}
        )

        comm3 = commissions.get('WT-2024-0003')

        samples_data = [
            ('YP-2024-0001', '混凝土试块', 'C40',        comm1, 'tested', 28,  group1),
            ('YP-2024-0002', '混凝土试块', 'C40',        comm1, 'tested', 28,  group1),
            ('YP-2024-0003', '混凝土试块', 'C40',        comm1, 'tested', 28,  group1),
            ('YP-2024-0004', '热轧带肋钢筋', 'HRB400 φ25', comm2, 'tested', None, None),
            ('YP-2024-0005', '热轧带肋钢筋', 'HRB400 φ25', comm2, 'tested', None, None),
            ('YP-2024-0006', '热轧带肋钢筋', 'HRB400 φ25', comm2, 'tested', None, None),
            # 待评审委托：仍登记样品与待分配任务，便于全流程界面有数据可看
            ('YP-2024-0007', '粗骨料（碎石）', '5-25mm', comm3, 'pending', None, None),
        ]

        samples = {}
        count = 0
        for s_no, name, spec, comm, status, age_days, group in samples_data:
            if not comm:
                continue
            loc = 'T3航站楼地下一层'
            recv = datetime.date(2024, 3, 1)
            if comm == comm3:
                loc = '站坪道面施工区'
                recv = datetime.date(2024, 3, 10)
            sample, created = Sample.objects.get_or_create(
                sample_no=s_no,
                defaults={
                    'commission': comm,
                    'group': group,
                    'name': name,
                    'specification': spec,
                    'quantity': 1,
                    'unit': '组' if comm == comm3 else '个',
                    'sampling_date': recv,
                    'received_date': recv,
                    'sampling_location': loc,
                    'status': status,
                    'retention_deadline': today + datetime.timedelta(days=60) if age_days else None,
                }
            )
            samples[s_no] = sample
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 个样品'))
        return samples

    # ─────────────────────────────────────────────────────────────
    # 11. 检测任务
    # ─────────────────────────────────────────────────────────────
    def create_test_tasks(self, samples, methods, users, equipment_map):
        from apps.testing.models import TestTask
        self.stdout.write('创建检测任务...')

        today = datetime.date.today()
        ztester = users.get('tester')
        eq_e001 = equipment_map.get('E001')
        eq_e002 = equipment_map.get('E002')

        concrete_method = methods.get('混凝土抗压强度试验')
        steel_method = methods.get('钢筋拉伸性能试验')
        sand_method = methods.get('砂细度模数试验')

        tasks_data = [
            ('TT-2024-0001', 'YP-2024-0001', concrete_method, eq_e001, 'WT-2024-0001'),
            ('TT-2024-0002', 'YP-2024-0002', concrete_method, eq_e001, 'WT-2024-0001'),
            ('TT-2024-0003', 'YP-2024-0003', concrete_method, eq_e001, 'WT-2024-0001'),
            ('TT-2024-0004', 'YP-2024-0004', steel_method,    eq_e002, 'WT-2024-0002'),
            ('TT-2024-0005', 'YP-2024-0005', steel_method,    eq_e002, 'WT-2024-0002'),
            ('TT-2024-0006', 'YP-2024-0006', steel_method,    eq_e002, 'WT-2024-0002'),
            # 待评审委托：骨料检测任务（待分配，与演示「受理后待评审」场景并存）
            ('TT-2024-0007', 'YP-2024-0007', sand_method,     None,    'WT-2024-0003'),
        ]

        tasks = {}
        count = 0
        for task_no, sample_no, method, equip, comm_no in tasks_data:
            sample = samples.get(sample_no)
            if not sample or not method:
                continue
            pending = task_no == 'TT-2024-0007'
            task, created = TestTask.objects.get_or_create(
                task_no=task_no,
                defaults={
                    'sample': sample,
                    'commission': sample.commission,
                    'test_method': method,
                    'assigned_tester': None if pending else ztester,
                    'assigned_equipment': equip,
                    'planned_date': today + datetime.timedelta(days=3) if pending else today - datetime.timedelta(days=5),
                    'actual_date': None if pending else today - datetime.timedelta(days=3),
                    'status': 'unassigned' if pending else 'completed',
                }
            )
            tasks[task_no] = task
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 个检测任务'))
        return tasks

    # ─────────────────────────────────────────────────────────────
    # 12. 原始记录
    # ─────────────────────────────────────────────────────────────
    def create_original_records(self, tasks, templates, users):
        from apps.testing.models import OriginalRecord
        self.stdout.write('创建原始记录...')

        today = datetime.date.today()
        ztester = users.get('tester')
        qreviewer = users.get('reviewer')
        review_dt = timezone.now() - datetime.timedelta(days=2)

        concrete_tpl = templates.get('混凝土抗压强度试验')
        steel_tpl = templates.get('钢筋拉伸性能试验')

        concrete_record_data = {
            "specimen_size": "150×150×150",
            "test_age": 28,
            "load_1": 1012.5,
            "load_2": 985.0,
            "load_3": 1023.0,
            "strength_1": 45.0,
            "strength_2": 43.8,
            "strength_3": 45.5,
            "avg_strength": 44.8,
            "equipment_name": "YAW-2000B微机控制压力试验机",
            "env_temp": 20.0,
            "env_humidity": 65.0,
        }
        steel_record_data = {
            "diameter": 25,
            "gauge_length": 125,
            "yield_force": 196.0,
            "tensile_force": 283.0,
            "final_gauge": 151.3,
            "cross_section": 490.87,
            "yield_strength": 400,
            "tensile_strength": 577,
            "elongation": 21.0,
        }

        tasks_records = [
            ('TT-2024-0001', concrete_tpl, concrete_record_data),
            ('TT-2024-0002', concrete_tpl, concrete_record_data),
            ('TT-2024-0003', concrete_tpl, concrete_record_data),
            ('TT-2024-0004', steel_tpl,    steel_record_data),
            ('TT-2024-0005', steel_tpl,    steel_record_data),
            ('TT-2024-0006', steel_tpl,    steel_record_data),
        ]

        count = 0
        for task_no, tpl, record_data in tasks_records:
            task = tasks.get(task_no)
            if not task or not tpl:
                continue
            if not hasattr(task, 'record') or not OriginalRecord.objects.filter(task=task).exists():
                OriginalRecord.objects.create(
                    task=task,
                    template=tpl,
                    template_version='1.0',
                    record_data=record_data,
                    env_temperature=20.0,
                    env_humidity=65.0,
                    status='reviewed',
                    recorder=ztester,
                    reviewer=qreviewer,
                    review_date=review_dt,
                    review_comment='记录填写规范，数据真实可信',
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 条原始记录'))

    # ─────────────────────────────────────────────────────────────
    # 13. 检测结果
    # ─────────────────────────────────────────────────────────────
    def create_test_results(self, tasks, parameters):
        from apps.testing.models import TestResult, JudgmentRule
        self.stdout.write('创建检测结果...')

        compressive = parameters.get('compressive_strength')
        yield_p = parameters.get('yield_strength')
        tensile_p = parameters.get('tensile_strength')
        elongation_p = parameters.get('elongation')

        # 判定规则
        if compressive:
            JudgmentRule.objects.get_or_create(
                test_parameter=compressive,
                grade='C40',
                defaults={'min_value': 40.0, 'standard_ref': 'GB/T 50081-2019'}
            )
        if yield_p:
            JudgmentRule.objects.get_or_create(
                test_parameter=yield_p,
                grade='HRB400',
                defaults={'min_value': 400.0, 'standard_ref': 'GB/T 228.1-2021'}
            )
        if tensile_p:
            JudgmentRule.objects.get_or_create(
                test_parameter=tensile_p,
                grade='HRB400',
                defaults={'min_value': 540.0, 'standard_ref': 'GB/T 228.1-2021'}
            )
        if elongation_p:
            JudgmentRule.objects.get_or_create(
                test_parameter=elongation_p,
                grade='HRB400',
                defaults={'min_value': 16.0, 'standard_ref': 'GB/T 228.1-2021'}
            )

        # 混凝土结果（3个任务各一条）
        concrete_task_nos = ['TT-2024-0001', 'TT-2024-0002', 'TT-2024-0003']
        steel_task_nos    = ['TT-2024-0004', 'TT-2024-0005', 'TT-2024-0006']

        count = 0
        for task_no in concrete_task_nos:
            task = tasks.get(task_no)
            if not task or not compressive:
                continue
            if not task.results.filter(parameter=compressive).exists():
                TestResult.objects.create(
                    task=task,
                    parameter=compressive,
                    raw_value=44.8,
                    rounded_value=44.8,
                    display_value='44.8',
                    unit='MPa',
                    judgment='qualified',
                    standard_value='≥40.0',
                    design_value='40.0',
                )
                count += 1

        for task_no in steel_task_nos:
            task = tasks.get(task_no)
            if not task:
                continue
            steel_results = [
                (yield_p,    400,  400,  '400',  'MPa', '≥400', '400'),
                (tensile_p,  577,  577,  '577',  'MPa', '≥540', '540'),
                (elongation_p, 21.0, 21.0, '21.0', '%',  '≥16',  '16'),
            ]
            for param, raw, rounded, display, unit, std_val, design_val in steel_results:
                if not param:
                    continue
                if not task.results.filter(parameter=param).exists():
                    TestResult.objects.create(
                        task=task,
                        parameter=param,
                        raw_value=raw,
                        rounded_value=rounded,
                        display_value=display,
                        unit=unit,
                        judgment='qualified',
                        standard_value=std_val,
                        design_value=design_val,
                    )
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 条检测结果'))

    # ─────────────────────────────────────────────────────────────
    # 14. 检测报告
    # ─────────────────────────────────────────────────────────────
    def create_reports(self, commissions, users):
        from apps.reports.models import Report
        self.stdout.write('创建检测报告...')

        today = datetime.date.today()
        ztester = users.get('tester')
        qreviewer = users.get('reviewer')
        zsigner = users.get('auth_signer')
        comm1 = commissions.get('WT-2024-0001')
        comm2 = commissions.get('WT-2024-0002')

        count = 0

        if comm1:
            report1, created = Report.objects.get_or_create(
                report_no='JC-2024-0001',
                defaults={
                    'commission': comm1,
                    'report_type': 'material',
                    'template_name': '混凝土抗压强度检测报告',
                    'status': 'issued',
                    'conclusion': '经检测，所送样品混凝土抗压强度满足C40设计要求，判定合格。',
                    'has_cma': True,
                    'compile_date': timezone.now() - datetime.timedelta(days=5),
                    'issue_date': today - datetime.timedelta(days=1),
                    'compiler': ztester,
                    'auditor': qreviewer,
                    'audit_date': timezone.now() - datetime.timedelta(days=3),
                    'approver': zsigner,
                    'approve_date': timezone.now() - datetime.timedelta(days=2),
                }
            )
            if created:
                count += 1

        if comm2:
            report2, created = Report.objects.get_or_create(
                report_no='JC-2024-0002',
                defaults={
                    'commission': comm2,
                    'report_type': 'material',
                    'template_name': '钢筋力学性能检测报告',
                    'status': 'pending_audit',
                    'conclusion': '经检测，所送样品钢筋力学性能满足HRB400要求，判定合格。',
                    'has_cma': True,
                    'compile_date': timezone.now() - datetime.timedelta(days=1),
                    'compiler': ztester,
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 份检测报告'))

    # ─────────────────────────────────────────────────────────────
    # 15. 耗材管理
    # ─────────────────────────────────────────────────────────────
    def create_consumables(self, users):
        from apps.consumables.models import Supplier, Consumable, ConsumableIn, ConsumableOut
        self.stdout.write('创建耗材管理数据...')

        today = datetime.date.today()
        ztester = users.get('tester')

        supplier, _ = Supplier.objects.get_or_create(
            name='上海实验耗材供应商',
            defaults={
                'contact_person': '张供应',
                'phone': '021-55550000',
                'address': '上海市静安区',
                'evaluation_score': 90,
                'is_qualified': True,
            }
        )

        consumables_data = [
            ('游标卡尺', 'HC-001', '0-300mm',   '把', '测量器具', 5,  2,  datetime.date(2025, 12, 31)),
            ('砂浆搅拌棒','HC-002','标准型',     '根', '辅助工具', 20, 5,  None),
            ('塑料薄膜',  'HC-003','宽度1.2m',  '卷', '辅助材料', 10, 3,  None),
        ]

        consumable_map = {}
        con_count = 0
        in_count = 0
        out_count = 0

        for name, code, spec, unit, category, stock, safety, expiry in consumables_data:
            con, created = Consumable.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'specification': spec,
                    'unit': unit,
                    'category': category,
                    'supplier': supplier,
                    'stock_quantity': stock,
                    'safety_stock': safety,
                    'expiry_date': expiry,
                    'storage_location': '一楼耗材室',
                }
            )
            consumable_map[code] = con
            if created:
                con_count += 1

            # 入库记录
            if not con.in_records.exists():
                ConsumableIn.objects.create(
                    consumable=con,
                    quantity=stock + 5,
                    batch_no=f'BATCH-2024-{code}',
                    purchase_date=datetime.date(2024, 1, 15),
                    expiry_date=expiry,
                    operator=ztester,
                )
                in_count += 1

            # 出库记录（仅游标卡尺）
            if code == 'HC-001' and not con.out_records.exists():
                ConsumableOut.objects.create(
                    consumable=con,
                    quantity=5,
                    purpose='混凝土试件尺寸测量',
                    recipient=ztester,
                    out_date=datetime.date(2024, 3, 1),
                )
                out_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'  ✓ 创建 {con_count} 种耗材, {in_count} 条入库, {out_count} 条出库记录'
        ))

    # ─────────────────────────────────────────────────────────────
    # 16. 质量管理
    # ─────────────────────────────────────────────────────────────
    def create_quality_records(self, users):
        from apps.quality.models import (
            InternalAudit, AuditFinding, CorrectiveAction,
            ManagementReview, NonConformity,
        )
        self.stdout.write('创建质量管理记录...')

        wquality = users.get('quality_director')
        ltech = users.get('tech_director')
        zequip = users.get('equip_manager')
        ztester = users.get('tester')

        # 内部审核
        audit, audit_created = InternalAudit.objects.get_or_create(
            audit_no='NB-2024-001',
            defaults={
                'title': '2024年度第一次内部审核',
                'audit_type': 'scheduled',
                'scope': '全体系审核，覆盖12个质量要素',
                'planned_date': datetime.date(2024, 2, 15),
                'actual_date': datetime.date(2024, 2, 15),
                'lead_auditor': wquality,
                'status': 'closed',
            }
        )

        # 审核发现
        if audit_created or not audit.findings.exists():
            finding = AuditFinding.objects.create(
                audit=audit,
                finding_type='observation',
                clause='6.4.1',
                description='设备校准记录存档不够规范，部分记录缺少校准机构印章',
                department='设备管理部',
            )

            # 纠正措施
            CorrectiveAction.objects.create(
                finding=finding,
                root_cause='设备管理员对校准记录要求理解不到位',
                action_plan='组织设备管理员培训，重新梳理校准记录要求',
                responsible_person=zequip,
                deadline=datetime.date(2024, 3, 15),
                status='verified',
                completion_date=datetime.date(2024, 3, 10),
                verification_result='已完成培训，校准记录规范化',
            )

        # 管理评审
        ManagementReview.objects.get_or_create(
            review_no='PG-2024-001',
            defaults={
                'title': '2024年上半年管理评审',
                'review_date': datetime.date(2024, 6, 30),
                'chairperson': ltech,
                'participants': '技术负责人、质量负责人、各部门负责人',
                'input_materials': '内部审核报告、客户投诉统计、能力验证结果、质量指标统计',
                'minutes': '评审会议顺利召开，各部门报告工作情况，提出改进措施',
                'status': 'closed',
            }
        )

        # 不符合项
        NonConformity.objects.get_or_create(
            nc_no='BF-2024-001',
            defaults={
                'source': 'internal',
                'description': '部分原始记录填写不规范，存在涂改现象',
                'impact_assessment': '影响记录真实性，需立即整改',
                'corrective_action': '加强人员培训，建立原始记录填写规范',
                'responsible_person': ztester,
                'status': 'closed',
                'close_date': datetime.date(2024, 3, 20),
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ 创建内部审核、管理评审、不符合项记录'))

    # ─────────────────────────────────────────────────────────────
    # 17. 通知
    # ─────────────────────────────────────────────────────────────
    def create_notifications(self, users):
        from apps.system.models import Notification
        self.stdout.write('创建通知...')

        notifications_data = [
            ('reviewer',         'report_audit',      '报告待审核',   'JC-2024-0002钢筋检测报告待您审核',             '/reports'),
            ('auth_signer',      'commission_review',  '委托待评审',   'WT-2024-0003待评审',                           '/entrustment'),
            ('equip_manager',    'equipment_expiring', '设备校准提醒', 'UTM-100万能试验机将于30天后到期',              '/equipment'),
            ('tester',           'task_assigned',      '任务已分配',   '您有新的检测任务待执行',                        '/testing/tasks'),
            ('quality_director', 'quality_audit',      '内部审核提醒', '年度内部审核计划已生成',                        '/quality/audit'),
        ]

        count = 0
        for role_code, n_type, title, content, link_path in notifications_data:
            user = users.get(role_code)
            if not user:
                continue
            if not Notification.objects.filter(recipient=user, title=title).exists():
                Notification.objects.create(
                    recipient=user,
                    notification_type=n_type,
                    title=title,
                    content=content,
                    link_path=link_path,
                    is_read=False,
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ 创建 {count} 条通知'))
