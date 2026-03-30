from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.consumables.models import Consumable, Supplier
from apps.equipment.models import Equipment
from apps.staff.models import StaffProfile
from apps.system.models import User
from apps.testing.models.method import TestCategory, TestMethod, TestParameter
from apps.standards.models import Standard


class Command(BaseCommand):
    help = 'Seed demo/test data for local verification.'

    def handle(self, *args, **options) -> None:
        created = {
            'test_categories': 0,
            'test_methods': 0,
            'test_parameters': 0,
            'equipment': 0,
            'staff_profiles': 0,
            'suppliers': 0,
            'consumables': 0,
        }

        # 1) Testing categories/methods/parameters
        category, cat_created = TestCategory.objects.get_or_create(
            code='GB',
            defaults={'name': '国家标准（示例）'},
        )
        if cat_created:
            created['test_categories'] += 1

        standards = list(Standard.objects.all())
        if not standards:
            self.stdout.write(self.style.WARNING('No Standard found, skip TestMethod/TestParameter seed.'))

        for std in standards:
            method = TestMethod.objects.filter(
                standard_no=std.standard_no,
                category=category,
            ).first()
            if not method:
                method = TestMethod.objects.create(
                    name=f'检测方法（示例）-{std.standard_no}',
                    standard_no=std.standard_no,
                    standard_name=std.name,
                    category=category,
                    description='Seed by seed_demo_data.',
                    is_active=True,
                )
                created['test_methods'] += 1

            # create 1-2 parameters per method (codes must be unique per method)
            for idx in range(1, 3):
                p_code = f'P{idx}'
                param = TestParameter.objects.filter(method=method, code=p_code).first()
                if not param:
                    TestParameter.objects.create(
                        method=method,
                        name=f'参数{idx}（示例）',
                        code=p_code,
                        unit='',
                        precision=1,
                        min_value=None,
                        max_value=None,
                        is_required=True,
                    )
                    created['test_parameters'] += 1

        # 2) Equipment
        equipment, eq_created = Equipment.objects.get_or_create(
            manage_no='EQ-001',
            defaults={
                'name': '示例设备1',
                'model_no': 'M-001',
                'serial_no': 'SN-001',
                'manufacturer': '示例制造商',
                'category': 'A',
                'status': 'in_use',
                'purchase_date': timezone.now().date(),
                'location': '机房A',
                'next_calibration_date': timezone.now().date(),
                'accuracy': '',
                'measure_range': '',
                'remark': 'Seed by seed_demo_data.',
            },
        )
        if eq_created:
            created['equipment'] += 1
        else:
            # keep fields fresh for demo runs
            equipment.status = 'in_use'
            equipment.save(update_fields=['status'])

        # 3) Staff profile (+ underlying User)
        user, user_created = User.objects.get_or_create(
            username='S-1001',
            defaults={
                'first_name': '张',
                'last_name': '三',
                'department': '技术管理部',
                'title': '工程师',
                'phone': '13800000001',
                'email': 'zhangsan@example.com',
                'is_active': True,
            },
        )
        if user_created:
            user.set_password('Limis@123456')
            user.save()

        profile, prof_created = StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'employee_no': 'S-1001',
                'education': 'bachelor',
                'major': '',
                'hire_date': timezone.now().date(),
            },
        )
        if prof_created:
            created['staff_profiles'] += 1

        # 4) Consumables
        supplier, sup_created = Supplier.objects.get_or_create(
            name='示例供应商A',
            defaults={
                'contact_person': '',
                'phone': '',
                'address': '',
                'is_qualified': True,
            },
        )
        if sup_created:
            created['suppliers'] += 1

        consumable, con_created = Consumable.objects.get_or_create(
            code='C-0001',
            defaults={
                'name': '示例耗材1',
                'specification': '规格示例',
                'unit': '个',
                'category': '耗材类',
                'manufacturer': '示例厂家',
                'supplier': supplier,
                'stock_quantity': 20,
                'safety_stock': 10,
                'expiry_date': timezone.now().date(),
                'storage_location': '仓库1',
            },
        )
        if con_created:
            created['consumables'] += 1

        self.stdout.write(self.style.SUCCESS('Seed demo data finished.'))
        self.stdout.write(str(created))

