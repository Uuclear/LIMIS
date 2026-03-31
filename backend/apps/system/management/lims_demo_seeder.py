"""
LIMIS 演示数据写入器：由 seed_full_workflow 管理命令调用。

设计要点见 management/commands/seed_full_workflow.py 顶部说明。
"""
from __future__ import annotations

import datetime
import random
from decimal import Decimal
from typing import Any

from django.utils import timezone

P = 'LIMIS-DEMO'
PWD = 'Limis@demo123'

STANDARDS: list[tuple[str, str, str]] = [
    ('GB/T 50081-2019', '混凝土物理力学性能试验方法标准', 'concrete'),
    ('GB/T 228.1-2021', '金属材料 拉伸试验 第1部分：室温试验方法', 'steel'),
    ('JGJ 52-2006', '普通混凝土用砂、石质量及检验方法标准', 'aggregate'),
]
# 产品标准（库中单独条目，检测方法仍按 GB/T 228.1-2021）
STANDARD_REBAR_PRODUCT = ('GB/T 1499.2-2024', '钢筋混凝土用钢 第2部分：热轧带肋钢筋', 'steel')


class LimsDemoSeeder:
    """按阶段写入演示数据；阶段顺序由外键依赖决定。"""

    def __init__(self, stdout, style) -> None:
        self.stdout = stdout
        self.style = style
        self.users: dict[str, Any] = {}
        self.project = None
        self.sub: dict[str, Any] = {}
        self.witness = None
        self.witness_b = None
        self.methods: dict[str, Any] = {}
        self.params: dict[str, Any] = {}
        self.templates: dict[str, Any] = {}
        self.equipment: dict[str, Any] = {}
        self.commissions: dict[str, Any] = {}

    def log(self, msg: str, ok: bool = False) -> None:
        if ok:
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stdout.write(msg)

    def clear(self) -> None:
        from apps.system.management.lims_demo_clear import clear_lims_demo_data

        self.log('清除 LIMIS-DEMO 数据…')
        clear_lims_demo_data()
        self.log('  清理完成', ok=True)

    def phase_users(self) -> None:
        from apps.system.models import Role, User
        self.log('阶段：角色用户（每个角色一个 demo 账号）')
        for role in Role.objects.order_by('code'):
            u, _ = User.objects.get_or_create(
                username=f'demo_{role.code}',
                defaults={
                    'first_name': role.name[:30],
                    'last_name': '',
                    'email': f'demo_{role.code}@demo.local',
                    'is_active': True,
                },
            )
            u.set_password(PWD)
            u.save()
            u.roles.set([role])
            self.users[role.code] = u
        self.log(f'  共 {len(self.users)} 个 demo 用户，密码 {PWD}', ok=True)

    def phase_standards_and_parameters(self) -> None:
        from apps.standards.models import Standard
        from apps.testing.models import TestCategory, TestMethod, TestParameter
        self.log('阶段：标准规范 → 检测类别 → 方法 → 参数（项目参数库数据源）')
        cats: dict[str, Any] = {}
        for code, name, order in [
            (f'{P}-CAT-HNT', '混凝土与砂浆', 1),
            (f'{P}-CAT-GJ', '金属材料', 2),
            (f'{P}-CAT-GU', '骨料', 3),
        ]:
            c, _ = TestCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'sort_order': order},
            )
            cats[code] = c

        std_dates: dict[str, tuple[datetime.date, datetime.date]] = {
            'GB/T 50081-2019': (datetime.date(2019, 12, 1), datetime.date(2020, 7, 1)),
            'GB/T 228.1-2021': (datetime.date(2021, 8, 20), datetime.date(2022, 7, 1)),
            'JGJ 52-2006': (datetime.date(2006, 12, 1), datetime.date(2007, 6, 1)),
        }
        for std_no, std_name, cat_key in STANDARDS:
            pub, imp = std_dates.get(std_no, (datetime.date(2019, 1, 1), datetime.date(2020, 1, 1)))
            Standard.objects.update_or_create(
                standard_no=std_no,
                defaults={
                    'name': std_name,
                    'category': cat_key,
                    'status': 'active',
                    'publish_date': pub,
                    'implement_date': imp,
                },
            )
        Standard.objects.update_or_create(
            standard_no=STANDARD_REBAR_PRODUCT[0],
            defaults={
                'name': STANDARD_REBAR_PRODUCT[1],
                'category': STANDARD_REBAR_PRODUCT[2],
                'status': 'active',
                'publish_date': datetime.date(2024, 6, 25),
                'implement_date': datetime.date(2024, 9, 25),
            },
        )

        m_conc, _ = TestMethod.objects.get_or_create(
            standard_no=STANDARDS[0][0],
            name='立方体抗压强度',
            defaults={
                'standard_name': STANDARDS[0][1],
                'category': cats[f'{P}-CAT-HNT'],
                'description': '演示：混凝土立方体抗压强度',
                'is_active': True,
            },
        )
        m_steel, _ = TestMethod.objects.get_or_create(
            standard_no=STANDARDS[1][0],
            name='钢筋拉伸试验',
            defaults={
                'standard_name': STANDARDS[1][1],
                'category': cats[f'{P}-CAT-GJ'],
                'description': '演示：钢筋拉伸',
                'is_active': True,
            },
        )
        m_sand, _ = TestMethod.objects.get_or_create(
            standard_no=STANDARDS[2][0],
            name='砂筛分析（细度模数）',
            defaults={
                'standard_name': STANDARDS[2][1],
                'category': cats[f'{P}-CAT-GU'],
                'description': '演示：细度模数',
                'is_active': True,
            },
        )
        self.methods = {'conc': m_conc, 'steel': m_steel, 'sand': m_sand}

        def p(method, name, code, unit, prec):
            o, _ = TestParameter.objects.get_or_create(
                method=method, code=code,
                defaults={'name': name, 'unit': unit, 'precision': prec, 'is_required': True},
            )
            return o

        self.params['fc'] = p(m_conc, '抗压强度', 'fcu', 'MPa', 1)
        self.params['ReL'] = p(m_steel, '下屈服强度', 'Rel', 'MPa', 0)
        self.params['Rm'] = p(m_steel, '抗拉强度', 'Rm', 'MPa', 0)
        self.params['A'] = p(m_steel, '断后伸长率', 'A', '%', 1)
        self.params['Mx'] = p(m_sand, '细度模数', 'Mx', '', 2)
        self.log('  标准、方法、参数就绪', ok=True)

    def phase_templates(self) -> None:
        from apps.testing.models import RecordTemplate
        self.log('阶段：原始记录模板（JSON schema）')
        sch_conc = {
            'fields': [
                {'name': 'specimen', 'label': '试件尺寸(mm)', 'type': 'text', 'required': True},
                {'name': 'age', 'label': '龄期(d)', 'type': 'number', 'required': True},
                {'name': 'load_kn', 'label': '破坏荷载(kN)', 'type': 'number', 'required': True},
                {'name': 'fcu', 'label': '抗压强度(MPa)', 'type': 'number', 'required': True},
            ],
        }
        sch_steel = {
            'fields': [
                {'name': 'd', 'label': '公称直径(mm)', 'type': 'number', 'required': True},
                {'name': 'Rel', 'label': '屈服(MPa)', 'type': 'number', 'required': True},
                {'name': 'Rm', 'label': '抗拉(MPa)', 'type': 'number', 'required': True},
                {'name': 'A', 'label': '伸长率(%)', 'type': 'number', 'required': True},
            ],
        }
        sch_sand = {
            'fields': [
                {'name': 'sieve', 'label': '各筛累计筛余(%)', 'type': 'text', 'required': True},
                {'name': 'Mx', 'label': '细度模数', 'type': 'number', 'required': True},
            ],
        }
        pairs = [
            (
                f'{P}-TPL-CONC-01',
                f'混凝土立方体抗压原始记录（{STANDARDS[0][0]}）',
                self.methods['conc'], None, sch_conc,
            ),
            (
                f'{P}-TPL-STEEL-01',
                f'钢筋拉伸试验原始记录（{STANDARDS[1][0]}；产品 {STANDARD_REBAR_PRODUCT[0]}）',
                self.methods['steel'], self.params['ReL'], sch_steel,
            ),
            (
                f'{P}-TPL-SAND-01',
                f'砂筛分与细度模数原始记录（{STANDARDS[2][0]}）',
                self.methods['sand'], self.params['Mx'], sch_sand,
            ),
        ]
        for code, name, m, param, schema in pairs:
            t, _ = RecordTemplate.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'test_method': m,
                    'test_parameter': param,
                    'version': '1.0',
                    'schema': schema,
                    'is_active': True,
                },
            )
            self.templates[m.standard_no] = t
        self.log('  模板 3 套', ok=True)

    def phase_equipment(self) -> None:
        from apps.equipment.models import Calibration, Equipment
        self.log('阶段：仪器设备与校准')
        today = timezone.now().date()
        specs = [
            (f'{P}-EQ-001', '压力试验机', 'YAW-2000', 'A', '0–2000kN'),
            (f'{P}-EQ-002', '万能试验机', 'WDW-100', 'A', '0–100kN'),
            (f'{P}-EQ-003', '电子天平', 'ME204', 'B', '0–220g'),
        ]
        for mno, name, model, cat, rng in specs:
            eq, _ = Equipment.objects.update_or_create(
                manage_no=mno,
                defaults={
                    'name': name,
                    'model_no': model,
                    'serial_no': f'{mno}-SN',
                    'manufacturer': '演示厂商',
                    'category': cat,
                    'measure_range': rng,
                    'accuracy': '1级',
                    'purchase_date': today - datetime.timedelta(days=800),
                    'status': 'in_use',
                    'location': '检测一室',
                    'calibration_cycle': 12,
                    'next_calibration_date': today + datetime.timedelta(days=120),
                },
            )
            self.equipment[mno] = eq
            if not eq.calibrations.exists():
                Calibration.objects.create(
                    equipment=eq,
                    certificate_no=f'{mno}-CAL-2025',
                    calibration_date=today - datetime.timedelta(days=30),
                    valid_until=today + datetime.timedelta(days=335),
                    calibration_org='省级计量院(演示)',
                    conclusion='qualified',
                )
        self.log('  设备与校准记录已写入', ok=True)

    def phase_staff_extras(self) -> None:
        from apps.staff.models import Authorization, Certificate, StaffProfile, Training
        from apps.testing.models import TestCategory
        self.log('阶段：人员档案、证书、培训、授权（人员管理延伸）')
        tester = self.users.get('tester')
        if not tester:
            return
        sp, _ = StaffProfile.objects.update_or_create(
            user=tester,
            defaults={
                'employee_no': f'{P}-EMP-TESTER',
                'education': 'bachelor',
                'major': '土木工程',
                'hire_date': datetime.date(2019, 7, 1),
            },
        )
        Certificate.objects.get_or_create(
            staff=sp,
            cert_no=f'{P}-CERT-001',
            defaults={
                'cert_type': '上岗证',
                'issuing_authority': '演示检测机构',
                'issue_date': datetime.date(2022, 1, 10),
                'expiry_date': datetime.date(2027, 1, 9),
            },
        )
        Training.objects.get_or_create(
            staff=sp,
            title='记录填写与修约规范',
            training_date=datetime.date(2024, 6, 1),
            defaults={'hours': Decimal('8.0'), 'trainer': '质量部', 'assessment_result': 'pass'},
        )
        cat = TestCategory.objects.filter(code=f'{P}-CAT-HNT').first()
        if cat:
            auth, _ = Authorization.objects.update_or_create(
                staff=sp,
                test_category=cat,
                defaults={
                    'authorized_date': datetime.date(2023, 1, 1),
                    'authorized_by': self.users.get('tech_director'),
                    'is_active': True,
                },
            )
            auth.test_methods.set([self.methods['conc']])
        self.log('  人员扩展信息已写入', ok=True)

    def phase_project(self) -> None:
        from apps.projects.models import Contract, Organization, Project, SubProject, Witness
        self.log('阶段：工程项目、合同、参建单位、分部、见证人')
        self.project, _ = Project.objects.update_or_create(
            code=f'{P}-PRJ-001',
            defaults={
                'name': '演示工程：综合交通枢纽与机场配套检测项目',
                'address': '演示市演示区机场大道与枢纽一路交叉口东北侧',
                'project_type': 'airport',
                'status': 'active',
                'start_date': datetime.date(2024, 3, 18),
                'end_date': datetime.date(2027, 12, 31),
                'description': '用于 LIMIS 全流程联调的虚构机场配套工程；材料检测覆盖混凝土抗压、钢筋拉伸、骨料等。',
            },
        )
        Contract.objects.update_or_create(
            contract_no=f'{P}-CONT-001',
            defaults={
                'project': self.project,
                'title': '检测技术服务合同（演示）',
                'amount': Decimal('586000.00'),
                'sign_date': datetime.date(2024, 4, 2),
                'start_date': datetime.date(2024, 4, 15),
                'end_date': datetime.date(2027, 12, 31),
                'scope': '土建材料检测：混凝土、钢筋、砂、石等；报告加盖 CMA 章（演示）。',
            },
        )
        org_roles: list[tuple[str, str, str, str]] = [
            ('演示机场建设投资有限公司', 'builder', '张明', '021-58880101'),
            ('演示建工集团有限公司', 'contractor', '赵铁军', '13800138001'),
            ('演示工程监理咨询有限公司', 'supervisor', '李监理', '13900139002'),
            ('演示建筑设计研究院有限公司', 'designer', '王结构', '021-58880303'),
            ('演示交通检测中心（本实验室）', 'inspector', '刘主任', '021-58880000'),
        ]
        org_by_role: dict[str, Any] = {}
        for oname, orole, cp, phone in org_roles:
            o, _ = Organization.objects.update_or_create(
                project=self.project,
                name=oname,
                role=orole,
                defaults={'contact_person': cp, 'contact_phone': phone},
            )
            org_by_role[orole] = o
        org_sup = org_by_role['builder']
        self.sub['A'], _ = SubProject.objects.update_or_create(
            project=self.project,
            code='FB-A',
            defaults={'name': '主体结构', 'description': '主体混凝土与钢筋'},
        )
        self.sub['B'], _ = SubProject.objects.update_or_create(
            project=self.project,
            code='FB-B',
            defaults={'name': '站房附属', 'description': '砂、石骨料等'},
        )
        self.witness, _ = Witness.objects.update_or_create(
            project=self.project,
            name='王见证',
            defaults={
                'id_number': '110101199001011234',
                'organization': org_sup,
                'phone': '13900001111',
                'certificate_no': 'JZ2023-110108-00156',
                'is_active': True,
            },
        )
        self.witness_b, _ = Witness.objects.update_or_create(
            project=self.project,
            name='刘见证',
            defaults={
                'id_number': '320102198805152468',
                'organization': org_by_role['supervisor'],
                'phone': '13900002222',
                'certificate_no': 'JZ2022-320102-00888',
                'is_active': True,
            },
        )
        self.log('  工程树已建立', ok=True)

    def phase_consumables(self) -> None:
        from apps.consumables.models import Consumable, ConsumableIn, ConsumableOut, Supplier
        self.log('阶段：耗材与入出库')
        sup, _ = Supplier.objects.get_or_create(
            name=f'{P}-SUP-化学试剂',
            defaults={'contact_person': '李供', 'phone': '021-61111111', 'is_qualified': True},
        )
        op = self.users.get('tester')
        for i, (code, name) in enumerate([
            (f'{P}-HC-001', '蒸馏水'),
            (f'{P}-HC-002', '脱模剂'),
        ], 1):
            c, _ = Consumable.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'specification': '分析纯',
                    'unit': '瓶',
                    'category': '试剂',
                    'supplier': sup,
                    'stock_quantity': 50,
                    'safety_stock': 10,
                    'storage_location': '试剂柜A',
                },
            )
            if not c.in_records.exists():
                ConsumableIn.objects.create(
                    consumable=c,
                    quantity=100,
                    batch_no=f'B{i}',
                    purchase_date=datetime.date(2025, 1, 1),
                    operator=op,
                )
        c0 = Consumable.objects.get(code=f'{P}-HC-001')
        if not c0.out_records.exists():
            ConsumableOut.objects.create(
                consumable=c0,
                quantity=3,
                purpose='试块养护用水',
                recipient=op,
                out_date=datetime.date(2025, 3, 1),
            )
        self.log('  耗材流水已写入', ok=True)

    def phase_environment(self) -> None:
        from apps.environment.models import EnvRecord, MonitoringPoint
        self.log('阶段：环境监控点与历史曲线')
        pt, _ = MonitoringPoint.objects.update_or_create(
            code=f'{P}-ENV-YS',
            defaults={
                'name': '标养室',
                'location': '一层标养室',
                'temp_min': Decimal('18.0'),
                'temp_max': Decimal('22.0'),
                'humidity_min': Decimal('95.0'),
                'humidity_max': Decimal('99.0'),
                'is_active': True,
            },
        )
        if not pt.records.exists():
            now = timezone.now()
            rows = []
            for h in range(48):
                rows.append(EnvRecord(
                    point=pt,
                    temperature=Decimal(str(round(random.uniform(19.0, 21.5), 1))),
                    humidity=Decimal(str(round(random.uniform(95.5, 98.0), 1))),
                    recorded_at=now - datetime.timedelta(hours=47 - h),
                    is_alarm=False,
                ))
            EnvRecord.objects.bulk_create(rows)
        self.log('  环境数据已写入', ok=True)

    def phase_commissions(self) -> None:
        from apps.commissions.models import Commission, CommissionItem, ContractReview
        self.log('阶段：委托单（多状态）与合同评审')
        u_rev = self.users.get('reviewer')
        today = timezone.now().date()
        # 委托日期分布在当月内，便于仪表盘「本月委托」与列表展示一致
        steel_std = f'{STANDARDS[1][0]}；产品 {STANDARD_REBAR_PRODUCT[0]}'
        defs: list[tuple[Any, ...]] = [
            (
                f'{P}-WT-001', 'reviewed', self.sub['A'],
                'T2 航站楼地下室墙柱（C30 混凝土）',
                today - datetime.timedelta(days=5),
                self.witness,
                [
                    (
                        '混凝土试块', '立方体抗压强度', STANDARDS[0][0],
                        '按 GB/T 50081-2019 制作与试验', 'C30', '150×150×150mm', 3, '组',
                    ),
                ],
            ),
            (
                f'{P}-WT-002', 'reviewed', self.sub['A'],
                '主梁上部钢筋（HRB400）',
                today - datetime.timedelta(days=3),
                self.witness,
                [
                    (
                        '热轧带肋钢筋', '拉伸试验（屈服、抗拉、伸长率）', steel_std,
                        'GB/T 228.1-2021 方法A', 'HRB400 Φ20mm', 'Φ20', 2, '根',
                    ),
                ],
            ),
            (
                f'{P}-WT-003', 'pending_review', self.sub['B'],
                '站房二层砌筑砂浆用砂',
                today - datetime.timedelta(days=1),
                self.witness_b,
                [
                    (
                        '天然砂', '筛分析、细度模数、含泥量', STANDARDS[2][0],
                        '筛分法、水洗法', '中砂', '', 1, '批',
                    ),
                ],
            ),
            (
                f'{P}-WT-004', 'draft', self.sub['B'],
                '进场粗骨料（碎石，草稿未提交）',
                today,
                self.witness_b,
                [
                    (
                        '碎石', '颗粒级配、针片状、含泥量', STANDARDS[2][0],
                        '筛分法', '5–25mm 连续级配', '', 1, '批',
                    ),
                ],
            ),
        ]
        for row in defs:
            no, st, sub, part, comm_date, wit, items = row
            c, _ = Commission.objects.update_or_create(
                commission_no=no,
                defaults={
                    'project': self.project,
                    'sub_project': sub,
                    'construction_part': part,
                    'commission_date': comm_date,
                    'client_unit': '演示建工集团有限公司',
                    'client_contact': '赵铁军',
                    'client_phone': '13800138001',
                    'witness': wit,
                    'is_witnessed': True,
                    'status': st,
                    'reviewer': u_rev if st == 'reviewed' else None,
                    'review_date': timezone.now() - datetime.timedelta(days=2) if st == 'reviewed' else None,
                    'review_comment': '同意受理' if st == 'reviewed' else '',
                },
            )
            CommissionItem.objects.filter(commission=c).delete()
            for (
                obj, ti, ts, tm, grade, spec, qty, unit,
            ) in items:
                CommissionItem.objects.create(
                    commission=c,
                    test_object=obj,
                    test_item=ti,
                    test_standard=ts,
                    test_method=tm,
                    grade=grade or '',
                    specification=spec or '',
                    quantity=qty,
                    unit=unit,
                )
            if st == 'reviewed':
                ContractReview.objects.update_or_create(
                    commission=c,
                    defaults={
                        'has_capability': True,
                        'has_equipment': True,
                        'has_personnel': True,
                        'method_valid': True,
                        'sample_representative': True,
                        'conclusion': 'accept',
                        'reviewer': u_rev,
                        'comment': '合同评审通过（演示）',
                    },
                )
            self.commissions[no] = c
        self.log('  委托与合同评审已写入', ok=True)

    def phase_samples_and_tasks(self) -> None:
        from apps.samples.models import Sample, SampleGroup
        from apps.testing.models import TestTask
        self.log('阶段：样品、组样、检测任务（覆盖待分配/待检/已完成）')
        today = timezone.now().date()
        g1, _ = SampleGroup.objects.get_or_create(
            group_no=f'{P}-SG-001',
            defaults={'name': 'C30 试块组', 'sample_count': 3, 'description': '演示组样'},
        )
        ut = self.users.get('tester')
        e1, e2 = self.equipment[f'{P}-EQ-001'], self.equipment[f'{P}-EQ-002']

        plan = [
            (f'{P}-YP-001', f'{P}-WT-001', '混凝土试块', 'C30', g1, 'tested', self.methods['conc'], e1, 'completed'),
            (f'{P}-YP-002', f'{P}-WT-002', '热轧带肋钢筋', 'HRB400 Φ20', None, 'tested', self.methods['steel'], e2, 'completed'),
            (f'{P}-YP-003', f'{P}-WT-003', '河砂', '中砂', None, 'pending', self.methods['sand'], None, 'unassigned'),
            (f'{P}-YP-004', f'{P}-WT-004', '碎石', '5–25mm', None, 'pending', self.methods['sand'], None, 'unassigned'),
            (f'{P}-YP-005', f'{P}-WT-002', '热轧带肋钢筋', 'HRB400 Φ25', None, 'pending', self.methods['steel'], e2, 'assigned'),
            (f'{P}-YP-006', f'{P}-WT-001', '混凝土试块', 'C30', g1, 'testing', self.methods['conc'], e1, 'in_progress'),
        ]
        for sno, cno, name, spec, grp, samp_st, method, eq, tstatus in plan:
            comm = self.commissions[cno]
            qty = 1
            unit = '组' if grp else '批'
            if '钢筋' in name or '热轧' in name:
                unit = '根'
                qty = 2 if f'{P}-YP-002' in sno else 1
            grade = 'C30' if '混凝土' in name else ''
            sa, _ = Sample.objects.update_or_create(
                sample_no=sno,
                defaults={
                    'commission': comm,
                    'group': grp,
                    'name': name,
                    'specification': spec,
                    'grade': grade,
                    'quantity': qty,
                    'unit': unit,
                    'sampling_date': today - datetime.timedelta(days=12),
                    'received_date': today - datetime.timedelta(days=11),
                    'sampling_location': comm.construction_part,
                    'status': samp_st,
                },
            )
            tt_no = sno.replace('YP', 'TT')
            if tstatus == 'unassigned':
                planned = today + datetime.timedelta(days=3)
            elif tstatus == 'assigned':
                planned = today
            elif tstatus == 'in_progress':
                planned = today - datetime.timedelta(days=1)
            else:
                planned = today - datetime.timedelta(days=5)
            TestTask.objects.update_or_create(
                task_no=tt_no,
                defaults={
                    'sample': sa,
                    'commission': comm,
                    'test_method': method,
                    'test_parameter': None,
                    'assigned_tester': ut if tstatus != 'unassigned' else None,
                    'assigned_equipment': eq,
                    'planned_date': planned,
                    'actual_date': today - datetime.timedelta(days=4) if tstatus == 'completed' else None,
                    'status': tstatus,
                    'age_days': 28 if '混凝土' in name else None,
                },
            )
        self.log('  样品与任务已写入', ok=True)

    def phase_records_and_results(self) -> None:
        from apps.testing.models import JudgmentRule, OriginalRecord, TestResult, TestTask
        self.log('阶段：原始记录、判定规则、检测结果')
        u_t = self.users.get('tester')
        u_r = self.users.get('reviewer')
        tpl_c = self.templates[STANDARDS[0][0]]
        tpl_s = self.templates[STANDARDS[1][0]]
        JudgmentRule.objects.get_or_create(
            test_parameter=self.params['fc'], grade='C30',
            defaults={'min_value': Decimal('30.0'), 'standard_ref': STANDARDS[0][0]},
        )
        t1 = TestTask.objects.get(task_no=f'{P}-TT-001')
        if not hasattr(t1, 'record'):
            OriginalRecord.objects.create(
                task=t1,
                template=tpl_c,
                template_version='1.0',
                record_data={'specimen': '150', 'age': 28, 'load_kn': 980.0, 'fcu': 43.5},
                env_temperature=Decimal('20.0'),
                env_humidity=Decimal('60.0'),
                status='reviewed',
                recorder=u_t,
                reviewer=u_r,
                review_date=timezone.now() - datetime.timedelta(days=2),
                review_comment='符合要求',
            )
        TestResult.objects.get_or_create(
            task=t1,
            parameter=self.params['fc'],
            defaults={
                'raw_value': Decimal('43.5'),
                'rounded_value': Decimal('43.5'),
                'display_value': '43.5',
                'unit': 'MPa',
                'judgment': 'qualified',
                'standard_value': '≥30.0',
                'design_value': '30.0',
            },
        )
        t2 = TestTask.objects.get(task_no=f'{P}-TT-002')
        if not hasattr(t2, 'record'):
            OriginalRecord.objects.create(
                task=t2,
                template=tpl_s,
                template_version='1.0',
                record_data={'d': 20, 'Rel': 420, 'Rm': 580, 'A': 16},
                env_temperature=Decimal('21.0'),
                env_humidity=Decimal('55.0'),
                status='pending_review',
                recorder=u_t,
            )
        for param, val, disp, unit, j in [
            (self.params['ReL'], Decimal('420'), '420', 'MPa', 'qualified'),
            (self.params['Rm'], Decimal('580'), '580', 'MPa', 'qualified'),
            (self.params['A'], Decimal('16.0'), '16.0', '%', 'qualified'),
        ]:
            TestResult.objects.get_or_create(
                task=t2,
                parameter=param,
                defaults={
                    'raw_value': val,
                    'rounded_value': val,
                    'display_value': disp,
                    'unit': unit,
                    'judgment': j,
                    'standard_value': '—',
                    'design_value': '—',
                },
            )
        self.log('  记录与结果已写入', ok=True)

    def phase_reports(self) -> None:
        from apps.reports.models import Report, ReportDistribution
        self.log('阶段：检测报告（多状态）与发放记录')
        c1 = self.commissions[f'{P}-WT-001']
        c2 = self.commissions[f'{P}-WT-002']
        comp = self.users.get('tester')
        aud = self.users.get('reviewer')
        app = self.users.get('auth_signer')
        today = timezone.now().date()
        r1, _ = Report.objects.update_or_create(
            report_no=f'{P}-RPT-001',
            defaults={
                'commission': c1,
                'report_type': 'material',
                'template_name': '混凝土抗压报告（演示）',
                'status': 'issued',
                'conclusion': '所检混凝土抗压强度满足设计要求。',
                'compiler': comp,
                'compile_date': timezone.now() - datetime.timedelta(days=6),
                'auditor': aud,
                'audit_date': timezone.now() - datetime.timedelta(days=5),
                'approver': app,
                'approve_date': timezone.now() - datetime.timedelta(days=4),
                'issue_date': today - datetime.timedelta(days=3),
                'has_cma': True,
            },
        )
        if not r1.distributions.exists():
            ReportDistribution.objects.create(
                report=r1,
                recipient='张工',
                recipient_unit='演示施工单位',
                method='electronic',
                copies=1,
                distribution_date=today - datetime.timedelta(days=2),
                receiver_signature='张工',
            )
        Report.objects.update_or_create(
            report_no=f'{P}-RPT-002',
            defaults={
                'commission': c2,
                'report_type': 'material',
                'template_name': '钢筋拉伸报告（演示）',
                'status': 'pending_approve',
                'conclusion': '所检钢筋力学性能满足标准要求。',
                'compiler': comp,
                'compile_date': timezone.now() - datetime.timedelta(days=1),
                'auditor': aud,
                'audit_date': timezone.now() - datetime.timedelta(hours=20),
                'has_cma': True,
            },
        )
        self.log('  报告已写入', ok=True)

    def phase_quality(self) -> None:
        from apps.quality.models import (
            AuditFinding, Complaint, CorrectiveAction, InternalAudit,
            ManagementReview, NonConformity, ReviewDecision,
        )
        self.log('阶段：内审、纠正措施、管评、决议、不符合项、投诉')
        wq = self.users.get('quality_director')
        td = self.users.get('tech_director')
        aud, _ = InternalAudit.objects.update_or_create(
            audit_no=f'{P}-NB-001',
            defaults={
                'title': '年度内部审核（演示）',
                'audit_type': 'scheduled',
                'scope': '全部门、全要素抽样',
                'planned_date': datetime.date(2025, 3, 1),
                'actual_date': datetime.date(2025, 3, 5),
                'lead_auditor': wq,
                'status': 'closed',
            },
        )
        fg, _ = AuditFinding.objects.get_or_create(
            audit=aud,
            clause='6.4',
            defaults={
                'finding_type': 'observation',
                'description': '个别设备标识欠清晰（演示）',
                'department': '设备室',
            },
        )
        CorrectiveAction.objects.update_or_create(
            finding=fg,
            defaults={
                'root_cause': '标识管理执行不到位',
                'action_plan': '统一张贴设备状态标识',
                'responsible_person': self.users.get('equip_manager'),
                'deadline': datetime.date(2025, 4, 1),
                'status': 'verified',
                'completion_date': datetime.date(2025, 3, 28),
                'verification_result': '已完成',
            },
        )
        mr, _ = ManagementReview.objects.update_or_create(
            review_no=f'{P}-PG-001',
            defaults={
                'title': '管理评审会议（演示）',
                'review_date': datetime.date(2025, 6, 30),
                'chairperson': td,
                'participants': '各部门负责人',
                'input_materials': '内审总结、客户反馈',
                'minutes': '持续改进检测质量',
                'status': 'closed',
            },
        )
        if not mr.decisions.exists():
            ReviewDecision.objects.create(
                review=mr,
                content='加强人员培训与设备管理',
                responsible_person=wq,
                deadline=datetime.date(2025, 12, 31),
                status='open',
            )
        NonConformity.objects.update_or_create(
            nc_no=f'{P}-BF-001',
            defaults={
                'source': 'audit',
                'description': '记录修改未留痕（演示）',
                'impact_assessment': '可追溯性风险',
                'corrective_action': '启用修订留痕流程',
                'responsible_person': self.users.get('tester'),
                'status': 'closed',
                'close_date': datetime.date(2025, 4, 15),
            },
        )
        Complaint.objects.update_or_create(
            complaint_no=f'{P}-TS-001',
            defaults={
                'complainant': '匿名客户',
                'complaint_date': datetime.date(2025, 2, 1),
                'content': '报告领取等待时间偏长（演示）',
                'investigation': '已协调窗口加派人手',
                'handling_result': '客户接受解释',
                'handler': self.users.get('reception'),
                'status': 'closed',
            },
        )
        self.log('  质量体系相关记录已写入', ok=True)

    def phase_notifications(self) -> None:
        from apps.system.models import Notification
        self.log('阶段：站内通知')
        pairs = [
            ('reviewer', 'report_audit', '报告待批准', f'{P}-RPT-002 待您处理', '/reports'),
            ('tester', 'task_assigned', '检测任务提醒', '请查看检测任务列表', '/testing/tasks'),
        ]
        for role, ntype, title, body, path in pairs:
            u = self.users.get(role)
            if not u:
                continue
            Notification.objects.get_or_create(
                recipient=u,
                title=title,
                defaults={
                    'notification_type': ntype,
                    'content': body,
                    'link_path': path,
                    'is_read': False,
                },
            )
        self.log('  通知已写入', ok=True)

    def run(self) -> None:
        self.phase_users()
        self.phase_standards_and_parameters()
        self.phase_templates()
        self.phase_equipment()
        self.phase_staff_extras()
        self.phase_project()
        self.phase_consumables()
        self.phase_environment()
        self.phase_commissions()
        self.phase_samples_and_tasks()
        self.phase_records_and_results()
        self.phase_reports()
        self.phase_quality()
        self.phase_notifications()
