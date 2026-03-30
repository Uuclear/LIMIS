# Generated manually for RBAC seed data

from __future__ import annotations

from django.db import migrations


def seed_permissions(apps, schema_editor) -> None:
    Permission = apps.get_model('system', 'Permission')
    Role = apps.get_model('system', 'Role')

    role_defs = [
        ('admin', '系统管理员'),
        ('tech_director', '技术负责人'),
        ('quality_director', '质量负责人'),
        ('auth_signer', '授权签字人'),
        ('reviewer', '审核人'),
        ('supervisor', '监督员'),
        ('tester', '检测人员'),
        ('sample_clerk', '样品管理员'),
        ('equip_manager', '设备管理员'),
        ('reception', '接待员'),
        ('client', '委托方'),
    ]
    for code, name in role_defs:
        Role.objects.get_or_create(
            code=code,
            defaults={'name': name, 'description': ''},
        )

    modules = [
        ('system', '系统管理'),
        ('project', '工程项目'),
        ('commission', '委托受理'),
        ('testing', '检测管理'),
        ('report', '报告管理'),
        ('quality', '质量管理'),
        ('equipment', '设备管理'),
        ('consumables', '耗材管理'),
        ('staff', '人员管理'),
        ('standards', '标准规范'),
        ('environment', '环境监控'),
        ('sample', '样品管理'),
    ]
    actions = [
        ('view', '查看'),
        ('create', '创建'),
        ('edit', '编辑'),
        ('delete', '删除'),
        ('approve', '审批'),
        ('export', '导出'),
    ]
    for mod, mod_label in modules:
        for action, alabel in actions:
            code = f'{mod}:{action}'
            name = f'{mod_label}-{alabel}'
            Permission.objects.update_or_create(
                module=mod,
                action=action,
                defaults={'name': name, 'code': code},
            )

    all_perms = list(Permission.objects.all())

    def set_role(code: str, perm_codes: list[str] | None) -> None:
        try:
            role = Role.objects.get(code=code)
        except Role.DoesNotExist:
            return
        if perm_codes is None:
            role.permissions.set(all_perms)
            return
        perms = Permission.objects.filter(code__in=perm_codes)
        role.permissions.set(perms)

    # 系统管理员：全部权限
    set_role('admin', None)

    # 接待/业务受理：委托与项目查看、登记委托
    set_role('reception', [
        'project:view',
        'commission:view', 'commission:create', 'commission:edit',
        'sample:view',
    ])

    # 检测人员：检测任务、样品、原始记录
    set_role('tester', [
        'testing:view', 'testing:create', 'testing:edit',
        'sample:view', 'sample:create', 'sample:edit',
        'report:view',
    ])

    # 样品管理员
    set_role('sample_clerk', [
        'sample:view', 'sample:create', 'sample:edit', 'sample:delete',
        'commission:view',
    ])

    # 设备管理员
    set_role('equip_manager', [
        'equipment:view', 'equipment:create', 'equipment:edit', 'equipment:delete',
    ])

    # 审核人：委托评审、报告审核
    set_role('reviewer', [
        'commission:view', 'commission:approve',
        'report:view', 'report:approve',
        'testing:view',
    ])

    # 授权签字人
    set_role('auth_signer', [
        'report:view', 'report:create', 'report:edit', 'report:approve', 'report:export',
        'commission:view',
    ])

    # 质量负责人
    set_role('quality_director', [
        'quality:view', 'quality:create', 'quality:edit', 'quality:approve',
        'report:view', 'report:approve',
    ])

    # 技术负责人
    set_role('tech_director', [
        'testing:view', 'testing:edit', 'testing:approve',
        'report:view', 'report:approve',
        'standards:view', 'standards:edit',
    ])

    # 监督员
    set_role('supervisor', [
        'testing:view', 'quality:view', 'report:view',
    ])

    # 委托方：仅查看与自己相关的（接口层仍按业务过滤）
    set_role('client', [
        'commission:view', 'report:view',
    ])


def noop_reverse(apps, schema_editor) -> None:
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_permissions, noop_reverse),
    ]
