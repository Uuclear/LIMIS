from __future__ import annotations

from django.db import migrations


def forwards(apps, schema_editor):
    Role = apps.get_model('system', 'Role')
    Permission = apps.get_model('system', 'Permission')

    def set_additional(role_code: str, perm_codes: list[str]):
        role = Role.objects.filter(code=role_code).first()
        if not role:
            return
        perms = list(Permission.objects.filter(code__in=perm_codes))
        if perms:
            role.permissions.add(*perms)

    # 业务受理员：委托+样品+报告发放（report:edit）
    set_additional('reception', [
        'commission:view', 'commission:create', 'commission:edit', 'commission:delete',
        'sample:view', 'sample:create', 'sample:edit',
        'report:view', 'report:edit',
    ])

    # 技术负责人：任务分配与报告审核
    set_additional('tech_director', [
        'task:view', 'task:edit', 'task:create',
        'report:view', 'report:approve',
    ])

    # 检测人员：检测任务执行、原始记录与报告编制
    set_additional('tester', [
        'task:view', 'task:edit', 'task:create',
        'testing:view', 'testing:create', 'testing:edit',
        'report:view', 'report:create', 'report:edit',
    ])

    # 授权签字人：报告批准与导出
    set_additional('auth_signer', [
        'report:view', 'report:approve', 'report:export',
    ])


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_add_task_permissions'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

