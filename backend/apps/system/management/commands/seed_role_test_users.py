from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.system.models import Role, User

# 与 seed_airport_lab_demo.USER_PROFILES 中 test_* 保持一致（姓名/手机/部门）
_ROLE_PROFILES = {
    'admin': ('张明', '13800001001', '综合管理部'),
    'tech_director': ('李建华', '13800001002', '技术部'),
    'quality_director': ('王秀英', '13800001003', '质量部'),
    'auth_signer': ('赵志刚', '13800001004', '报告签发室'),
    'reviewer': ('陈静', '13800001005', '审核室'),
    'supervisor': ('刘洋', '13800001006', '质量监督组'),
    'tester': ('周伟', '13800001007', '检测一室'),
    'sample_clerk': ('吴敏', '13800001008', '样品管理室'),
    'equip_manager': ('郑强', '13800001009', '设备管理室'),
    'reception': ('孙丽', '13800001010', '业务受理室'),
    'client': ('钱磊', '13800001011', '委托方代表'),
}


class Command(BaseCommand):
    help = '为每个系统角色各创建一个测试账号（用户名 test_<角色编码>，密码 Limis@test123）。'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--password',
            default='Limis@test123',
            help='统一测试密码（默认 Limis@test123）',
        )

    def handle(self, *args, **options) -> None:
        pwd = options['password']
        created = 0
        updated = 0
        for role in Role.objects.order_by('code'):
            username = f'test_{role.code}'
            prof = _ROLE_PROFILES.get(role.code, (role.name[:50], '', ''))
            disp_name, phone, dept = prof[0], prof[1], prof[2]
            user, is_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': disp_name[:150],
                    'last_name': '',
                    'email': f'{username}@example.local',
                    'phone': phone,
                    'department': dept,
                    'is_active': True,
                },
            )
            user.set_password(pwd)
            user.first_name = disp_name[:150]
            user.phone = phone
            user.department = dept
            user.save()
            user.roles.set([role])
            if is_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'创建 {username} -> {role.name}'))
            else:
                updated += 1
                self.stdout.write(f'更新 {username} -> {role.name}')
        self.stdout.write(
            self.style.SUCCESS(f'完成：新建 {created} 个，更新 {updated} 个。密码：{pwd}'),
        )
