from __future__ import annotations

import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.commissions.models import Commission, CommissionItem
from apps.projects.models import Project
from apps.reports.models import Report, ReportTemplate
from apps.samples.models import Sample
from apps.standards.csres_crawl import crawl_standard_metadata
from apps.standards.models import Standard
from apps.testing.models import (
    OriginalRecord,
    RecordTemplate,
    TestCategory,
    TestMethod,
    TestParameter,
    TestResult,
    TestTask,
)


CSRES_STANDARD_NO_POOL = [
    'GB/T 50080-2016',
    'GB/T 50081-2019',
    'GB/T 50082-2009',
    'GB/T 50107-2010',
    'GB 50204-2015',
    'GB 175-2023',
    'GB/T 1346-2011',
    'GB/T 17671-2021',
    'GB/T 14684-2022',
    'GB/T 14685-2022',
    'JGJ/T 52-2006',
    'GB 1499.1-2024',
    'GB 1499.2-2024',
    'GB/T 232-2010',
    'JGJ 107-2016',
    'JGJ 18-2012',
    'JGJ/T 70-2009',
    'JGJ/T 23-2011',
    'JGJ/T 152-2019',
    'JGJ 63-2006',
    'GB 8076-2008',
    'JTG 3430-2020',
    'JTG 3432-2024',
    'JTG E20-2011',
    'JTG E30-2005',
    'JTG E41-2005',
    'JTG E50-2006',
    'JTG E51-2009',
    'JTG 3450-2019',
    'JTG/T 3650-2020',
]


PACK_METHODS = [
    {
        'category_code': 'SITE-CONC',
        'category_name': '混凝土工程',
        'standard_no': 'GB/T 50081-2019',
        'standard_name': '混凝土物理力学性能试验方法标准',
        'method_name': '混凝土立方体抗压强度',
        'report_type': '混凝土强度',
        'parameters': [
            ('fcu', '抗压强度', 'MPa', 1, Decimal('10'), Decimal('120')),
            ('F_kN', '破坏荷载', 'kN', 2, Decimal('1'), None),
            ('age_d', '龄期', 'd', 0, Decimal('1'), Decimal('365')),
        ],
    },
    {
        'category_code': 'SITE-STEEL',
        'category_name': '钢筋工程',
        'standard_no': 'GB 1499.1-2024',
        'standard_name': '钢筋混凝土用钢 第1部分：热轧光圆钢筋',
        'method_name': '钢筋拉伸性能',
        'report_type': '钢筋力学',
        'parameters': [
            ('Rel', '下屈服强度', 'MPa', 0, Decimal('100'), None),
            ('Rm', '抗拉强度', 'MPa', 0, Decimal('100'), None),
            ('A', '断后伸长率', '%', 1, Decimal('1'), Decimal('60')),
        ],
    },
    {
        'category_code': 'SITE-SOIL',
        'category_name': '土工试验',
        'standard_no': 'JTG 3430-2020',
        'standard_name': '公路土工试验规程',
        'method_name': '土的含水率与密度',
        'report_type': '土工指标',
        'parameters': [
            ('w', '含水率', '%', 1, Decimal('0'), Decimal('100')),
            ('rho', '密度', 'g/cm3', 3, Decimal('0.1'), Decimal('3.5')),
            ('rd', '干密度', 'g/cm3', 3, Decimal('0.1'), Decimal('3.5')),
        ],
    },
    {
        'category_code': 'SITE-ASPHALT',
        'category_name': '沥青与沥青混合料',
        'standard_no': 'JTG E20-2011',
        'standard_name': '公路工程沥青及沥青混合料试验规程',
        'method_name': '沥青混合料马歇尔试验',
        'report_type': '沥青混合料',
        'parameters': [
            ('stab', '稳定度', 'kN', 2, Decimal('1'), None),
            ('flow', '流值', '0.1mm', 1, Decimal('1'), None),
            ('va', '空隙率', '%', 1, Decimal('0'), Decimal('30')),
        ],
    },
    {
        'category_code': 'SITE-CEMENT',
        'category_name': '水泥试验',
        'standard_no': 'GB 175-2023',
        'standard_name': '通用硅酸盐水泥',
        'method_name': '水泥物理性能',
        'report_type': '水泥性能',
        'parameters': [
            ('fineness', '细度', '%', 1, Decimal('0'), Decimal('30')),
            ('consistency', '标准稠度用水量', '%', 1, Decimal('15'), Decimal('40')),
            ('setting_i', '初凝时间', 'min', 0, Decimal('45'), None),
            ('setting_f', '终凝时间', 'min', 0, None, Decimal('600')),
            ('fc3', '3d抗压强度', 'MPa', 1, Decimal('10'), Decimal('80')),
            ('fc28', '28d抗压强度', 'MPa', 1, Decimal('20'), Decimal('100')),
        ],
    },
    {
        'category_code': 'SITE-AGG',
        'category_name': '集料试验',
        'standard_no': 'JTG 3432-2024',
        'standard_name': '公路工程集料试验规程',
        'method_name': '粗细集料常规指标',
        'report_type': '集料指标',
        'parameters': [
            ('mud', '含泥量', '%', 1, Decimal('0'), Decimal('20')),
            ('crush', '压碎值', '%', 1, Decimal('0'), Decimal('40')),
            ('needle', '针片状含量', '%', 1, Decimal('0'), Decimal('40')),
            ('density', '表观密度', 'g/cm3', 3, Decimal('1.5'), Decimal('3.5')),
            ('absorb', '吸水率', '%', 1, Decimal('0'), Decimal('20')),
            ('gradation', '级配偏差', '%', 1, Decimal('0'), Decimal('30')),
        ],
    },
    {
        'category_code': 'SITE-SOIL',
        'category_name': '土工试验',
        'standard_no': 'JTG 3430-2020',
        'standard_name': '公路土工试验规程',
        'method_name': '土工力学指标',
        'report_type': '土工力学',
        'parameters': [
            ('wl', '液限', '%', 1, Decimal('10'), Decimal('100')),
            ('wp', '塑限', '%', 1, Decimal('5'), Decimal('80')),
            ('ip', '塑性指数', '', 1, Decimal('0'), Decimal('60')),
            ('comp_k', '压实系数', '', 3, Decimal('0.8'), Decimal('1.2')),
            ('cbr', 'CBR值', '%', 1, Decimal('1'), Decimal('100')),
            ('ev2', '回弹模量', 'MPa', 1, Decimal('10'), Decimal('600')),
        ],
    },
    {
        'category_code': 'SITE-CONC',
        'category_name': '混凝土工程',
        'standard_no': 'GB/T 50082-2009',
        'standard_name': '普通混凝土长期性能和耐久性能试验方法标准',
        'method_name': '混凝土耐久性指标',
        'report_type': '混凝土耐久',
        'parameters': [
            ('rcpt', '电通量', 'C', 0, Decimal('100'), Decimal('10000')),
            ('carbonation', '碳化深度', 'mm', 1, Decimal('0'), Decimal('50')),
            ('water_perm', '抗渗等级', '', 0, Decimal('1'), Decimal('20')),
            ('freeze_loss', '冻融质量损失率', '%', 1, Decimal('0'), Decimal('30')),
            ('freeze_strength', '冻融强度损失率', '%', 1, Decimal('0'), Decimal('40')),
        ],
    },
    {
        'category_code': 'SITE-STEEL',
        'category_name': '钢筋工程',
        'standard_no': 'GB/T 232-2010',
        'standard_name': '金属材料 弯曲试验方法',
        'method_name': '钢筋弯曲与反弯',
        'report_type': '钢筋工艺',
        'parameters': [
            ('bend_ok', '弯曲试验结果', '', 0, None, None),
            ('rebend_ok', '反弯试验结果', '', 0, None, None),
            ('diameter', '弯心直径', 'mm', 1, Decimal('1'), Decimal('200')),
            ('angle', '弯曲角度', 'deg', 0, Decimal('1'), Decimal('180')),
        ],
    },
    {
        'category_code': 'SITE-WATER',
        'category_name': '拌合用水试验',
        'standard_no': 'JGJ 63-2006',
        'standard_name': '混凝土用水标准',
        'method_name': '拌合用水水质指标',
        'report_type': '拌合用水',
        'parameters': [
            ('ph', 'pH值', '', 1, Decimal('1'), Decimal('14')),
            ('cl', '氯离子含量', 'mg/L', 0, Decimal('0'), Decimal('20000')),
            ('so4', '硫酸根含量', 'mg/L', 0, Decimal('0'), Decimal('20000')),
            ('insoluble', '不溶物', 'mg/L', 0, Decimal('0'), Decimal('10000')),
            ('soluble', '可溶物', 'mg/L', 0, Decimal('0'), Decimal('50000')),
        ],
    },
    {
        'category_code': 'SITE-ADMIX',
        'category_name': '外加剂试验',
        'standard_no': 'GB 8076-2008',
        'standard_name': '混凝土外加剂',
        'method_name': '外加剂性能指标',
        'report_type': '外加剂',
        'parameters': [
            ('water_reduce', '减水率', '%', 1, Decimal('1'), Decimal('50')),
            ('bleed_ratio', '泌水率比', '%', 1, Decimal('1'), Decimal('300')),
            ('set_diff_i', '凝结时间差(初凝)', 'min', 0, Decimal('-300'), Decimal('600')),
            ('set_diff_f', '凝结时间差(终凝)', 'min', 0, Decimal('-300'), Decimal('600')),
            ('strength_ratio_28', '28d抗压强度比', '%', 1, Decimal('50'), Decimal('200')),
        ],
    },
    {
        'category_code': 'SITE-CONC',
        'category_name': '混凝土工程',
        'standard_no': 'GB/T 50080-2016',
        'standard_name': '普通混凝土拌合物性能试验方法标准',
        'method_name': '混凝土拌合物工作性',
        'report_type': '混凝土拌合物',
        'parameters': [
            ('slump', '坍落度', 'mm', 0, Decimal('10'), Decimal('250')),
            ('spread', '扩展度', 'mm', 0, Decimal('200'), Decimal('800')),
            ('air', '含气量', '%', 1, Decimal('0'), Decimal('10')),
            ('vebe', '维勃稠度', 's', 0, Decimal('5'), Decimal('60')),
            ('temp_mix', '拌合物温度', '℃', 1, Decimal('5'), Decimal('40')),
        ],
    },
    {
        'category_code': 'SITE-MORTAR',
        'category_name': '砂浆试验',
        'standard_no': 'JGJ/T 70-2009',
        'standard_name': '建筑砂浆基本性能试验方法标准',
        'method_name': '砂浆力学与稠度',
        'report_type': '砂浆性能',
        'parameters': [
            ('consistency_m', '稠度', 'mm', 0, Decimal('30'), Decimal('130')),
            ('m7', '7d抗压强度', 'MPa', 1, Decimal('1'), Decimal('50')),
            ('m28', '28d抗压强度', 'MPa', 1, Decimal('2'), Decimal('60')),
            ('strat', '分层度', 'mm', 0, Decimal('0'), Decimal('30')),
        ],
    },
    {
        'category_code': 'SITE-BRICK',
        'category_name': '墙体材料',
        'standard_no': 'GB/T 2542-2012',
        'standard_name': '砌墙砖试验方法',
        'method_name': '烧结砖抗压强度',
        'report_type': '砖强度',
        'parameters': [
            ('mu', '抗压强度平均值', 'MPa', 1, Decimal('5'), Decimal('60')),
            ('mu_min', '抗压强度最小值', 'MPa', 1, Decimal('5'), Decimal('60')),
        ],
    },
    {
        'category_code': 'SITE-SOIL',
        'category_name': '土工试验',
        'standard_no': 'JTG 3450-2019',
        'standard_name': '公路路基路面现场测试规程',
        'method_name': '现场压实度与含水率',
        'report_type': '现场土工',
        'parameters': [
            ('gamma_field', '现场干密度', 'g/cm3', 3, Decimal('1.0'), Decimal('2.6')),
            ('moist_field', '现场含水率', '%', 1, Decimal('0'), Decimal('40')),
            ('comp_ratio', '压实度', '%', 1, Decimal('80'), Decimal('100')),
        ],
    },
    {
        'category_code': 'SITE-CONC',
        'category_name': '混凝土工程',
        'standard_no': 'GB/T 50204-2015',
        'standard_name': '混凝土结构工程施工质量验收规范',
        'method_name': '钢筋保护层厚度',
        'report_type': '结构实体',
        'parameters': [
            ('cover_max', '保护层厚度最大值', 'mm', 0, Decimal('5'), Decimal('80')),
            ('cover_mean', '保护层厚度平均值', 'mm', 0, Decimal('5'), Decimal('80')),
        ],
    },
    {
        'category_code': 'SITE-CONC',
        'category_name': '混凝土工程',
        'standard_no': 'JGJ/T 23-2011',
        'standard_name': '回弹法检测混凝土抗压强度技术规程',
        'method_name': '回弹法推定强度',
        'report_type': '回弹检测',
        'parameters': [
            ('r_mean', '回弹值平均值', '', 0, Decimal('10'), Decimal('60')),
            ('fcu_est', '推定抗压强度', 'MPa', 1, Decimal('5'), Decimal('80')),
        ],
    },
    {
        'category_code': 'SITE-STEEL',
        'category_name': '钢筋工程',
        'standard_no': 'JGJ 107-2016',
        'standard_name': '钢筋机械连接技术规程',
        'method_name': '机械连接抗拉强度',
        'report_type': '钢筋连接',
        'parameters': [
            ('f0mst', '接头抗拉强度', 'MPa', 0, Decimal('400'), None),
            ('u_strength', '残余变形', 'mm', 2, Decimal('0'), Decimal('0.6')),
        ],
    },
    {
        'category_code': 'SITE-GEO',
        'category_name': '岩石与地基',
        'standard_no': 'JTG E41-2005',
        'standard_name': '公路工程岩石试验规程',
        'method_name': '岩石单轴抗压与变形指标',
        'report_type': '岩石试验',
        'parameters': [
            ('ucs', '饱和单轴抗压强度', 'MPa', 1, Decimal('1'), Decimal('300')),
            ('ucs_dry', '烘干单轴抗压强度', 'MPa', 1, Decimal('1'), Decimal('300')),
            ('e_elastic', '弹性模量', 'GPa', 2, Decimal('1'), Decimal('200')),
            ('poisson_r', '泊松比', '', 3, Decimal('0'), Decimal('0.5')),
            ('rho_r', '岩石密度', 'g/cm3', 3, Decimal('1.5'), Decimal('4')),
            ('por', '孔隙率', '%', 1, Decimal('0'), Decimal('50')),
            ('wa_r', '吸水率', '%', 1, Decimal('0'), Decimal('30')),
            ('soft_k', '软化系数', '', 2, Decimal('0'), Decimal('1')),
        ],
    },
    {
        'category_code': 'SITE-FOUND',
        'category_name': '地基与基桩',
        'standard_no': 'JGJ 106-2014',
        'standard_name': '建筑基桩检测技术规范',
        'method_name': '低应变反射波完整性',
        'report_type': '基桩检测',
        'parameters': [
            ('v_pile', '桩身波速', 'm/s', 0, Decimal('1000'), Decimal('5000')),
            ('f_dom', '主频', 'Hz', 1, Decimal('10'), Decimal('5000')),
            ('len_est', '桩长估算值', 'm', 2, Decimal('5'), Decimal('120')),
            ('sig_ref', '反射系数', '', 3, Decimal('-1'), Decimal('1')),
            ('intg_score', '完整性指数', '', 2, Decimal('0'), Decimal('1')),
            ('tdr', '时域分辨率', 'ms', 2, Decimal('0.01'), Decimal('10')),
        ],
    },
    {
        'category_code': 'SITE-AGG',
        'category_name': '集料试验',
        'standard_no': 'JTG E42-2005',
        'standard_name': '公路工程轻集料试验规程',
        'method_name': '轻集料物理力学性能',
        'report_type': '轻集料',
        'parameters': [
            ('bulk_l', '堆积密度', 'kg/m3', 0, Decimal('200'), Decimal('1200')),
            ('particle_l', '表观密度', 'kg/m3', 0, Decimal('400'), Decimal('2000')),
            ('strength_l', '筒压强度', 'MPa', 2, Decimal('0.1'), Decimal('20')),
            ('abs_l', '吸水率', '%', 1, Decimal('0'), Decimal('30')),
            ('clay_l', '含泥量', '%', 1, Decimal('0'), Decimal('15')),
            ('loss_l', '烧失量', '%', 1, Decimal('0'), Decimal('25')),
        ],
    },
    {
        'category_code': 'SITE-ASPHALT',
        'category_name': '沥青与沥青混合料',
        'standard_no': 'JTG E20-2011',
        'standard_name': '公路工程沥青及沥青混合料试验规程',
        'method_name': '沥青针入度延度软化点',
        'report_type': '沥青常规',
        'parameters': [
            ('pen25', '针入度(25℃)', '0.1mm', 0, Decimal('20'), Decimal('400')),
            ('duct15', '延度(15℃)', 'cm', 0, Decimal('1'), Decimal('150')),
            ('soft_r', '软化点', '℃', 1, Decimal('20'), Decimal('100')),
            ('sol_b', '溶解度', '%', 1, Decimal('90'), Decimal('100')),
            ('evap_b', '蒸发损失', '%', 1, Decimal('0'), Decimal('5')),
        ],
    },
    {
        'category_code': 'SITE-CONC',
        'category_name': '混凝土工程',
        'standard_no': 'GB/T 50081-2019',
        'standard_name': '混凝土物理力学性能试验方法标准',
        'method_name': '混凝土劈裂抗拉强度',
        'report_type': '混凝土劈裂',
        'parameters': [
            ('fts', '劈裂抗拉强度', 'MPa', 2, Decimal('0.5'), Decimal('15')),
            ('F_split', '劈裂破坏荷载', 'kN', 2, Decimal('1'), Decimal('500')),
            ('d_cyl', '圆柱试件直径', 'mm', 0, Decimal('100'), Decimal('200')),
        ],
    },
    {
        'category_code': 'SITE-SOIL',
        'category_name': '土工试验',
        'standard_no': 'JTG 3430-2020',
        'standard_name': '公路土工试验规程',
        'method_name': '土渗透试验',
        'report_type': '土渗透',
        'parameters': [
            ('k_cm', '渗透系数', 'cm/s', 6, Decimal('0.000001'), Decimal('1')),
            ('grad_h', '水力梯度', '', 3, Decimal('0.1'), Decimal('5')),
            ('q_perm', '渗流量', 'mL/s', 3, Decimal('0.001'), Decimal('100')),
            ('temp_perm', '试验水温', '℃', 1, Decimal('5'), Decimal('35')),
        ],
    },
    {
        'category_code': 'SITE-BRICK',
        'category_name': '墙体材料',
        'standard_no': 'GB/T 50315-2011',
        'standard_name': '砌体工程现场检测技术标准',
        'method_name': '砌体抗压强度原位',
        'report_type': '砌体强度',
        'parameters': [
            ('fm', '抗压强度平均值', 'MPa', 2, Decimal('0.5'), Decimal('20')),
            ('fmin_m', '抗压强度最小值', 'MPa', 2, Decimal('0.5'), Decimal('20')),
            ('cv_m', '变异系数', '%', 1, Decimal('0'), Decimal('40')),
        ],
    },
    {
        'category_code': 'SITE-CONC',
        'category_name': '混凝土工程',
        'standard_no': 'GB 50204-2015',
        'standard_name': '混凝土结构工程施工质量验收规范',
        'method_name': '结构实体超声波测强',
        'report_type': '超声测强',
        'parameters': [
            ('v_wave', '超声波声速', 'km/s', 2, Decimal('2'), Decimal('6')),
            ('t_travel', '声时', 'us', 2, Decimal('10'), Decimal('500')),
            ('amp_ratio', '波幅比', '%', 1, Decimal('0'), Decimal('200')),
        ],
    },
    {
        'category_code': 'SITE-SOIL',
        'category_name': '土工试验',
        'standard_no': 'JTG E51-2009',
        'standard_name': '公路工程无机结合料试验规程',
        'method_name': '无机结合料无侧限抗压',
        'report_type': '无机结合料',
        'parameters': [
            ('qud7', '7d无侧限抗压强度', 'MPa', 2, Decimal('0.1'), Decimal('15')),
            ('qud28', '28d无侧限抗压强度', 'MPa', 2, Decimal('0.2'), Decimal('20')),
            ('cb_ucs', '加州承载比', '%', 1, Decimal('20'), Decimal('300')),
            ('dry_density', '最大干密度', 'g/cm3', 3, Decimal('1.5'), Decimal('2.6')),
            ('opt_moist', '最佳含水率', '%', 1, Decimal('3'), Decimal('25')),
        ],
    },
]


class Command(BaseCommand):
    help = '初始化工地试验室商用数据包（标准方法、参数、模板、模拟报告）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--strict',
            action='store_true',
            help='开启严格校验：若覆盖率不达标则命令失败',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        owner = (
            User.objects.filter(is_superuser=True).order_by('id').first()
            or User.objects.order_by('id').first()
        )
        if not owner:
            self.stdout.write(self.style.ERROR('缺少用户，请先创建管理员账号'))
            return

        project = Project.objects.filter(is_deleted=False).order_by('id').first()
        if not project:
            project = Project.objects.create(
                name='工地试验室示范项目',
                code='SITE-DEMO-001',
                project_type='airport',
                status='active',
                start_date=timezone.now().date(),
                description='系统自动创建，用于商用数据包初始化',
                created_by=owner,
            )

        self._sync_standards_from_csres()

        created_params = 0
        for item in PACK_METHODS:
            category, _ = TestCategory.objects.get_or_create(
                code=item['category_code'],
                defaults={
                    'name': item['category_name'],
                    'sort_order': 100,
                    'created_by': owner,
                },
            )
            method, _ = TestMethod.objects.update_or_create(
                standard_no=item['standard_no'],
                name=item['method_name'],
                defaults={
                    'standard_name': item['standard_name'],
                    'category': category,
                    'description': f"自动初始化：{item['method_name']}",
                    'is_active': True,
                    'created_by': owner,
                },
            )

            for code, name, unit, precision, min_value, max_value in item['parameters']:
                param, created = TestParameter.objects.update_or_create(
                    method=method,
                    code=code,
                    defaults={
                        'name': name,
                        'unit': unit,
                        'precision': precision,
                        'min_value': min_value,
                        'max_value': max_value,
                        'is_required': True,
                        'created_by': owner,
                    },
                )
                if created:
                    created_params += 1

                record_tpl = self._ensure_record_template(owner, method, param)
                report_tpl = self._ensure_report_template(owner, method, param, item['report_type'])
                self._ensure_mock_report_chain(owner, project, method, param, record_tpl, report_tpl)

        self._ensure_reports_for_all_parameters(owner, project)
        coverage = self._coverage_stats()
        if options.get('strict'):
            if coverage['missing_record_template'] > 0:
                raise CommandError(
                    f"存在 {coverage['missing_record_template']} 个参数缺少原始记录模板",
                )
            if coverage['missing_report_template'] > 0:
                raise CommandError(
                    f"存在 {coverage['missing_report_template']} 个参数缺少报告模板",
                )
            if coverage['missing_mock_report'] > 0:
                raise CommandError(
                    f"存在 {coverage['missing_mock_report']} 个参数缺少模拟报告",
                )
        total_params = TestParameter.objects.filter(is_deleted=False).count()
        total_reports = Report.objects.filter(report_no__startswith='MOCK-RPT-').count()
        self.stdout.write(self.style.SUCCESS(
            f'初始化完成：新增参数 {created_params}，参数总数 {total_params}，模拟报告 {total_reports}',
        ))
        self.stdout.write(
            self.style.SUCCESS(
                '覆盖率校验：'
                f"缺原始记录模板={coverage['missing_record_template']}，"
                f"缺报告模板={coverage['missing_report_template']}，"
                f"缺模拟报告={coverage['missing_mock_report']}",
            ),
        )

    def _sync_standards_from_csres(self) -> None:
        success = 0
        failed = 0
        for std_no in CSRES_STANDARD_NO_POOL:
            try:
                meta = crawl_standard_metadata(std_no)
                pub = meta.get('publish_date')
                imp = meta.get('implement_date')
                if isinstance(pub, str):
                    pub = datetime.date.fromisoformat(pub)
                if isinstance(imp, str):
                    imp = datetime.date.fromisoformat(imp)
                Standard.objects.update_or_create(
                    standard_no=meta['standard_no'],
                    defaults={
                        'name': meta.get('name') or std_no,
                        'category': meta.get('category') or 'national',
                        'status': meta.get('status') or 'active',
                        'publish_date': pub,
                        'implement_date': imp,
                        'remark': meta.get('remark') or '',
                        'replaced_case': meta.get('replaced_case') or '',
                    },
                )
                success += 1
            except Exception:
                failed += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'工标网标准同步完成：成功 {success}，失败 {failed}',
            ),
        )

    def _ensure_record_template(
        self, owner, method: TestMethod, parameter: TestParameter,
    ) -> RecordTemplate:
        code = f'TPL-AUTO-{parameter.id}'
        schema = {
            'title': f'{method.name}原始记录',
            'method': method.standard_no,
            'parameter': parameter.code,
            'fields': [
                {'name': 'sample_no', 'label': '样品编号', 'type': 'text', 'required': True},
                {'name': 'operator', 'label': '检测人', 'type': 'text', 'required': True},
                {'name': 'raw_value', 'label': f'{parameter.name}原始值', 'type': 'number', 'required': True},
                {'name': 'remark', 'label': '备注', 'type': 'text', 'required': False},
            ],
        }
        tpl, _ = RecordTemplate.objects.update_or_create(
            code=code,
            defaults={
                'name': f'{method.name}-{parameter.name}-自动模板',
                'test_method': method,
                'test_parameter': parameter,
                'version': '1.0',
                'schema': schema,
                'is_active': True,
                'created_by': owner,
            },
        )
        return tpl

    def _ensure_report_template(
        self, owner, method: TestMethod, parameter: TestParameter, report_type: str,
    ) -> ReportTemplate:
        code = f'RPT-AUTO-{parameter.id}'
        schema = {
            'title': f'{report_type}检测报告',
            'sections': [
                {'name': 'basic', 'label': '基础信息'},
                {'name': 'result', 'label': '检测结果'},
                {'name': 'conclusion', 'label': '结论'},
            ],
            'mapping': {
                'method': method.name,
                'standard_no': method.standard_no,
                'parameter_name': parameter.name,
                'parameter_unit': parameter.unit,
            },
        }
        tpl, _ = ReportTemplate.objects.update_or_create(
            code=code,
            defaults={
                'name': f'{method.name}-{parameter.name}-报告模板',
                'report_type': report_type,
                'test_method': method,
                'test_parameter': parameter,
                'version': '1.0',
                'schema': schema,
                'is_active': True,
                'created_by': owner,
            },
        )
        return tpl

    def _ensure_mock_report_chain(
        self,
        owner,
        project: Project,
        method: TestMethod,
        parameter: TestParameter,
        record_tpl: RecordTemplate,
        report_tpl: ReportTemplate,
    ) -> None:
        today = timezone.now().date()
        suffix = f'{parameter.id:05d}'
        commission_no = f'MOCK-COM-{suffix}'
        sample_no = f'MOCK-SMP-{suffix}'
        task_no = f'MOCK-TSK-{suffix}'
        report_no = f'MOCK-RPT-{suffix}'

        commission, _ = Commission.objects.update_or_create(
            commission_no=commission_no,
            defaults={
                'project': project,
                'construction_part': '自动化示例部位',
                'commission_date': today,
                'client_unit': '系统自动生成',
                'status': 'reviewed',
                'remark': '用于确保每个检测参数至少一份模拟报告',
                'created_by': owner,
            },
        )
        CommissionItem.objects.update_or_create(
            commission=commission,
            test_object=method.name,
            test_item=parameter.name,
            defaults={
                'test_standard': method.standard_no,
                'test_method': method.name,
                'specification': 'AUTO',
                'grade': 'AUTO',
                'quantity': 1,
                'unit': '组',
                'created_by': owner,
            },
        )
        sample, _ = Sample.objects.update_or_create(
            sample_no=sample_no,
            defaults={
                'blind_no': f'MOCK-BLD-{suffix}',
                'commission': commission,
                'name': method.name,
                'specification': 'AUTO',
                'grade': 'AUTO',
                'quantity': 1,
                'unit': '组',
                'sampling_date': today,
                'received_date': today,
                'sampling_location': '自动化示例现场',
                'status': 'tested',
                'created_by': owner,
            },
        )
        task, _ = TestTask.objects.update_or_create(
            task_no=task_no,
            defaults={
                'sample': sample,
                'commission': commission,
                'test_method': method,
                'test_parameter': parameter,
                'assigned_tester': owner,
                'planned_date': today,
                'actual_date': today,
                'status': 'completed',
                'remark': '自动生成模拟任务',
                'created_by': owner,
            },
        )
        value = self._mock_value_for_parameter(parameter)
        TestResult.objects.update_or_create(
            task=task,
            parameter=parameter,
            defaults={
                'raw_value': value,
                'rounded_value': value,
                'display_value': str(value),
                'unit': parameter.unit,
                'judgment': 'qualified',
                'standard_value': self._format_standard_value(parameter),
                'design_value': '',
                'remark': '自动生成模拟结果',
                'created_by': owner,
            },
        )
        OriginalRecord.objects.update_or_create(
            task=task,
            defaults={
                'template': record_tpl,
                'template_version': record_tpl.version,
                'record_data': {
                    'sample_no': sample.sample_no,
                    'operator': owner.get_full_name() or owner.username,
                    'raw_value': str(value),
                    'remark': '自动生成',
                },
                'env_temperature': Decimal('20.0'),
                'env_humidity': Decimal('55.0'),
                'status': 'reviewed',
                'recorder': owner,
                'reviewer': owner,
                'review_date': timezone.now(),
                'review_comment': '自动通过',
                'created_by': owner,
            },
        )
        Report.objects.update_or_create(
            report_no=report_no,
            defaults={
                'commission': commission,
                'report_type': report_tpl.report_type,
                'template_name': report_tpl.name,
                'status': 'issued',
                'compiler': owner,
                'compile_date': timezone.now(),
                'auditor': owner,
                'audit_date': timezone.now(),
                'approver': owner,
                'approve_date': timezone.now(),
                'conclusion': '模拟样本结果满足技术要求',
                'has_cma': True,
                'issue_date': today,
                'remark': f'自动报告，关联参数 {parameter.code}',
                'created_by': owner,
            },
        )

    def _ensure_reports_for_all_parameters(self, owner, project: Project) -> None:
        for parameter in TestParameter.objects.filter(is_deleted=False).select_related('method'):
            record_tpl = self._ensure_record_template(owner, parameter.method, parameter)
            report_tpl = self._ensure_report_template(owner, parameter.method, parameter, '自动报告')
            self._ensure_mock_report_chain(
                owner=owner,
                project=project,
                method=parameter.method,
                parameter=parameter,
                record_tpl=record_tpl,
                report_tpl=report_tpl,
            )

    def _mock_value_for_parameter(self, parameter: TestParameter) -> Decimal:
        if parameter.min_value is not None and parameter.max_value is not None:
            mid = (Decimal(parameter.min_value) + Decimal(parameter.max_value)) / Decimal('2')
            return mid.quantize(Decimal('1') / (Decimal('10') ** parameter.precision))
        if parameter.min_value is not None:
            base = Decimal(parameter.min_value) + Decimal('1')
            return base.quantize(Decimal('1') / (Decimal('10') ** parameter.precision))
        return Decimal('1').quantize(Decimal('1') / (Decimal('10') ** parameter.precision))

    def _format_standard_value(self, parameter: TestParameter) -> str:
        min_value = parameter.min_value
        max_value = parameter.max_value
        if min_value is not None and max_value is not None:
            return f'[{min_value}, {max_value}]'
        if min_value is not None:
            return f'>= {min_value}'
        if max_value is not None:
            return f'<= {max_value}'
        return ''

    def _coverage_stats(self) -> dict[str, int]:
        missing_record_template = 0
        missing_report_template = 0
        missing_mock_report = 0
        for parameter in TestParameter.objects.filter(is_deleted=False).select_related('method'):
            if not RecordTemplate.objects.filter(
                is_deleted=False,
                test_parameter=parameter,
            ).exists():
                missing_record_template += 1
            if not ReportTemplate.objects.filter(
                is_deleted=False,
                test_parameter=parameter,
            ).exists():
                missing_report_template += 1
            suffix = f'{parameter.id:05d}'
            if not Report.objects.filter(
                is_deleted=False,
                report_no=f'MOCK-RPT-{suffix}',
            ).exists():
                missing_mock_report += 1
        return {
            'missing_record_template': missing_record_template,
            'missing_report_template': missing_report_template,
            'missing_mock_report': missing_mock_report,
        }
