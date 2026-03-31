"""
补充机场工地试验室演示数据：用户姓名/手机/部门、工程子项、工标网标准、检测方法/参数/原始记录模板。
"""
from __future__ import annotations

import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.projects.models import Contract, Organization, Project, Witness
from apps.standards.csres_crawl import crawl_standard_metadata
from apps.standards.models import Standard
from apps.system.models import User
from apps.testing.models import RecordTemplate, TestCategory, TestMethod, TestParameter


# test_<code> 用户展示信息（姓名存在 first_name，与系统用户管理一致）
USER_PROFILES = {
    'admin': ('系统管理员', '13800000000', '综合管理部'),
    'test_admin': ('张明', '13800001001', '综合管理部'),
    'test_tech_director': ('李建华', '13800001002', '技术部'),
    'test_quality_director': ('王秀英', '13800001003', '质量部'),
    'test_auth_signer': ('赵志刚', '13800001004', '报告签发室'),
    'test_reviewer': ('陈静', '13800001005', '审核室'),
    'test_supervisor': ('刘洋', '13800001006', '质量监督组'),
    'test_tester': ('周伟', '13800001007', '检测一室'),
    'test_sample_clerk': ('吴敏', '13800001008', '样品管理室'),
    'test_equip_manager': ('郑强', '13800001009', '设备管理室'),
    'test_reception': ('孙丽', '13800001010', '业务受理室'),
    'test_client': ('钱磊', '13800001011', '委托方代表'),
}

STANDARDS_TO_IMPORT = [
    'GB/T 50081-2019',
    'GB 1499.1-2024',
]


class Command(BaseCommand):
    help = '补充用户资料、工程关联信息、工标网标准及检测参数与原始记录模板'

    def handle(self, *args, **options):
        with transaction.atomic():
            self._users()
            self._projects_nested()
            self._standards_from_csres()
            self._methods_params_templates()
        self.stdout.write(self.style.SUCCESS('seed_airport_lab_demo 完成'))

    def _users(self) -> None:
        for username, (name, phone, dept) in USER_PROFILES.items():
            u = User.objects.filter(username=username).first()
            if not u:
                continue
            u.first_name = name[:150]
            u.phone = phone
            u.department = dept
            u.save(update_fields=['first_name', 'phone', 'department'])
        self.stdout.write('  用户姓名/手机/部门已更新')

    def _projects_nested(self) -> None:
        """补全两示例工程：参建单位联系人、合同日期、见证人证件类型等。"""
        p1 = Project.objects.filter(code='PDIV-2026-AIR-T4').first()
        p2 = Project.objects.filter(code='PD-MUN-2026-ZD-ROAD').first()
        if p1:
            extra = '【工程类型】机场工程（航站区）；开工2025-06-01，计划竣工2028-05-30。'
            base = (p1.description or '').strip()
            if extra not in base:
                p1.description = (base + '\n' + extra).strip()
            if p1.start_date is None:
                p1.start_date = datetime.date(2025, 6, 1)
            if p1.end_date is None:
                p1.end_date = datetime.date(2028, 5, 30)
            p1.save()
            for org in p1.organizations.filter(is_deleted=False):
                if not org.contact_person:
                    org.contact_person = '待补'
                if not org.contact_phone:
                    org.contact_phone = '021-00000000'
                org.save()
            for c in p1.contracts.filter(is_deleted=False):
                if not c.sign_date:
                    c.sign_date = datetime.date(2025, 5, 18)
                if not c.start_date:
                    c.start_date = datetime.date(2025, 6, 1)
                if not c.end_date:
                    c.end_date = datetime.date(2028, 12, 31)
                c.save()
            Witness.objects.filter(project=p1).update(id_type='id_card')

        if p2:
            if p2.start_date is None:
                p2.start_date = datetime.date(2025, 9, 15)
            if p2.end_date is None:
                p2.end_date = datetime.date(2027, 3, 31)
            p2.save()
            for org in p2.organizations.filter(is_deleted=False):
                if not org.contact_person:
                    org.contact_person = '待补'
                if not org.contact_phone:
                    org.contact_phone = '021-00000000'
                org.save()
            for c in p2.contracts.filter(is_deleted=False):
                if not c.sign_date:
                    c.sign_date = datetime.date(2025, 8, 20)
                if not c.start_date:
                    c.start_date = datetime.date(2025, 9, 15)
                if not c.end_date:
                    c.end_date = datetime.date(2027, 6, 30)
                c.save()
            Witness.objects.filter(project=p2).update(id_type='id_card')
        self.stdout.write('  工程子表与见证人证件类型已补全')

    def _standards_from_csres(self) -> None:
        for std_no in STANDARDS_TO_IMPORT:
            try:
                meta = crawl_standard_metadata(std_no)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  工标网抓取失败 {std_no}: {e}'))
                continue
            pub = meta.get('publish_date')
            imp = meta.get('implement_date')
            if isinstance(pub, str):
                pub = datetime.date.fromisoformat(pub)
            if isinstance(imp, str):
                imp = datetime.date.fromisoformat(imp)
            Standard.objects.update_or_create(
                standard_no=meta['standard_no'],
                defaults={
                    'name': meta['name'] or std_no,
                    'category': meta['category'],
                    'status': meta['status'],
                    'publish_date': pub,
                    'implement_date': imp,
                    'remark': meta.get('remark') or '',
                    'replaced_case': meta.get('replaced_case') or '',
                },
            )
            self.stdout.write(f'  标准入库: {meta["standard_no"]}')

    def _methods_params_templates(self) -> None:
        """基于 GB/T 50081-2019（立方体抗压）与 GB 1499.1-2024（拉伸）配置方法、参数与原始记录 schema。"""
        cat_conc, _ = TestCategory.objects.get_or_create(
            code='MAT-CONC',
            defaults={'name': '混凝土与砂浆', 'sort_order': 10},
        )
        cat_steel, _ = TestCategory.objects.get_or_create(
            code='MAT-STEEL',
            defaults={'name': '钢材', 'sort_order': 20},
        )

        s50081 = Standard.objects.filter(standard_no__icontains='50081').first()
        s1499 = Standard.objects.filter(standard_no__icontains='1499.1').first()

        m_conc, _ = TestMethod.objects.update_or_create(
            standard_no='GB/T 50081-2019',
            name='混凝土立方体抗压强度试验',
            defaults={
                'standard_name': s50081.name if s50081 else '混凝土物理力学性能试验方法标准',
                'category': cat_conc,
                'description': (
                    '依据 GB/T 50081-2019：立方体试件抗压强度试验；'
                    '环境宜 20±5℃、相对湿度≥50%；试件尺寸与骨料最大粒径匹配。'
                ),
                'is_active': True,
            },
        )
        m_steel, _ = TestMethod.objects.update_or_create(
            standard_no='GB 1499.1-2024',
            name='热轧光圆钢筋拉伸试验',
            defaults={
                'standard_name': s1499.name if s1499 else '钢筋混凝土用钢 第1部分：热轧光圆钢筋',
                'category': cat_steel,
                'description': (
                    '依据 GB 1499.1-2024：拉伸试验测定下屈服强度、抗拉强度、断后伸长率等；'
                    '含弯曲试验（产品标准检验项目以标准正文为准）。'
                ),
                'is_active': True,
            },
        )

        def p(method, name, code, unit, prec, **kwargs):
            o, _ = TestParameter.objects.update_or_create(
                method=method, code=code,
                defaults={
                    'name': name, 'unit': unit, 'precision': prec,
                    'is_required': kwargs.get('is_required', True),
                    'min_value': kwargs.get('min_value'),
                    'max_value': kwargs.get('max_value'),
                },
            )
            return o

        # GB/T 50081 立方体抗压 — 常见原始记录字段
        p(m_conc, '试件边长', 'a_mm', 'mm', 0)
        p(m_conc, '龄期', 'age_d', 'd', 0)
        p(m_conc, '破坏荷载', 'F_kN', 'kN', 2)
        p_fc = p(m_conc, '抗压强度', 'fcu', 'MPa', 1)

        # GB 1499.1 拉伸
        p(m_steel, '公称直径', 'd_nom', 'mm', 1)
        p_rel = p(m_steel, '下屈服强度', 'Rel', 'MPa', 0)
        p(m_steel, '抗拉强度', 'Rm', 'MPa', 0)
        p(m_steel, '断后伸长率', 'A', '%', 1)
        p(m_steel, '最大力总延伸率', 'Agt', '%', 1)

        sch_50081 = {
            'title': '混凝土立方体抗压强度原始记录',
            'standard': 'GB/T 50081-2019',
            'fields': [
                {'name': 'specimen_no', 'label': '试件编号', 'type': 'text', 'required': True},
                {'name': 'a_mm', 'label': '试件边长(mm)', 'type': 'number', 'required': True},
                {'name': 'age_d', 'label': '龄期(d)', 'type': 'number', 'required': True},
                {'name': 'area_mm2', 'label': '受压面积(mm²)', 'type': 'number', 'required': True},
                {'name': 'F_kN', 'label': '破坏荷载(kN)', 'type': 'number', 'required': True},
                {'name': 'fcu', 'label': '抗压强度(MPa)', 'type': 'number', 'required': True},
                {'name': 'env_t', 'label': '环境温度(℃)', 'type': 'number', 'required': False},
                {'name': 'env_rh', 'label': '环境相对湿度(%)', 'type': 'number', 'required': False},
            ],
        }
        sch_1499 = {
            'title': '热轧光圆钢筋拉伸试验原始记录',
            'standard': 'GB 1499.1-2024',
            'fields': [
                {'name': 'batch_no', 'label': '炉批号', 'type': 'text', 'required': True},
                {'name': 'd_nom', 'label': '公称直径(mm)', 'type': 'number', 'required': True},
                {'name': 'S0', 'label': '原始截面积(mm²)', 'type': 'number', 'required': True},
                {'name': 'Rel', 'label': '下屈服强度(MPa)', 'type': 'number', 'required': True},
                {'name': 'Rm', 'label': '抗拉强度(MPa)', 'type': 'number', 'required': True},
                {'name': 'A', 'label': '断后伸长率(%)', 'type': 'number', 'required': True},
                {'name': 'Agt', 'label': '最大力总延伸率(%)', 'type': 'number', 'required': False},
            ],
        }

        RecordTemplate.objects.update_or_create(
            code='TPL-GB50081-CUBE-01',
            defaults={
                'name': '混凝土立方体抗压强度原始记录（GB/T 50081-2019）',
                'test_method': m_conc,
                'test_parameter': p_fc,
                'version': '1.0',
                'schema': sch_50081,
                'is_active': True,
            },
        )
        RecordTemplate.objects.update_or_create(
            code='TPL-GB14991-TENSILE-01',
            defaults={
                'name': '热轧光圆钢筋拉伸试验原始记录（GB 1499.1-2024）',
                'test_method': m_steel,
                'test_parameter': p_rel,
                'version': '1.0',
                'schema': sch_1499,
                'is_active': True,
            },
        )
        self.stdout.write('  检测方法、参数与原始记录模板已就绪')
