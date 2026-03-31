from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.system.models import Role, User


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
            user, is_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': role.name[:50],
                    'last_name': '',
                    'email': f'{username}@example.local',
                    'is_active': True,
                },
            )
            user.set_password(pwd)
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
