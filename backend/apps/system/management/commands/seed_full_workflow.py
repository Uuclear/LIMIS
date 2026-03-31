"""
全流程演示数据管理命令。

实现逻辑在 `apps.system.management.lims_demo_seeder` 中维护，本文件仅负责 CLI 入口。

约定摘要：
- 编号前缀 `LIMIS-DEMO-`，`--clear` 时删除该前缀及 `demo_*` 用户数据；并尽力清理旧版演示前缀（TT/WT/YP-2024 等）。
- 为每个系统角色创建 `demo_<角色编码>`，密码 `Limis@demo123`。
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.system.management.lims_demo_seeder import LimsDemoSeeder


class Command(BaseCommand):
    help = '写入 LIMIS 全流程演示数据（实现见 lims_demo_seeder.LimsDemoSeeder）'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--clear',
            action='store_true',
            help='先删除本命令管理的演示数据再重建',
        )

    def handle(self, *args, **options) -> None:
        seeder = LimsDemoSeeder(self.stdout, self.style)
        with transaction.atomic():
            if options.get('clear'):
                seeder.clear()
            seeder.run()
        self.stdout.write(self.style.SUCCESS('=== seed_full_workflow 完成 ==='))
