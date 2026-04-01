from __future__ import annotations

from django.db import migrations


def add_task_permissions(apps, schema_editor) -> None:
    Permission = apps.get_model('system', 'Permission')
    Role = apps.get_model('system', 'Role')

    actions = [
        ('view', '查看'),
        ('create', '创建'),
        ('edit', '编辑'),
        ('delete', '删除'),
        ('approve', '审批'),
        ('export', '导出'),
    ]
    created_codes: list[str] = []
    for action, label in actions:
        code = f'task:{action}'
        created_codes.append(code)
        Permission.objects.update_or_create(
            module='task',
            action=action,
            defaults={'name': f'任务管理-{label}', 'code': code},
        )

    role_codes = ['admin', 'tester', 'tech_director', 'reviewer', 'quality_director']
    perms = list(Permission.objects.filter(code__in=created_codes))
    for rc in role_codes:
        role = Role.objects.filter(code=rc).first()
        if not role:
            continue
        role.permissions.add(*perms)


def noop_reverse(apps, schema_editor) -> None:
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0005_user_session_version'),
    ]

    operations = [
        migrations.RunPython(add_task_permissions, noop_reverse),
    ]

