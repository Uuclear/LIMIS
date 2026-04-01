from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.system.models import Role


class Command(BaseCommand):
    help = '检查关键角色的流程权限矩阵（允许/拒绝）'

    MATRIX = {
        'reception': ['commission:view', 'sample:view', 'report:edit'],
        'tech_director': ['task:edit', 'report:approve'],
        'tester': ['task:view', 'testing:edit', 'report:edit'],
        'auth_signer': ['report:approve', 'report:export'],
    }

    def handle(self, *args, **options):
        self.stdout.write('=== Flow Permission Matrix ===')
        for role_code, perms in self.MATRIX.items():
            role = Role.objects.filter(code=role_code).first()
            if not role:
                self.stdout.write(self.style.ERROR(f'{role_code}: role missing'))
                continue
            owned = set(role.permissions.values_list('code', flat=True))
            miss = [p for p in perms if p not in owned]
            if miss:
                self.stdout.write(self.style.WARNING(f'{role_code}: missing -> {", ".join(miss)}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'{role_code}: ok'))

