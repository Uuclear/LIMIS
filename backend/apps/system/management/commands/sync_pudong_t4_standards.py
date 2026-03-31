from __future__ import annotations

import datetime
import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.standards.csres_crawl import crawl_standard_metadata
from apps.standards.models import Standard


PUDONG_T4_STANDARD_QUEUE = [
    # 混凝土/结构
    'GB/T 50080-2016',
    'GB/T 50081-2019',
    'GB/T 50082-2009',
    'GB/T 50107-2010',
    'GB 50204-2015',
    'JGJ/T 23-2011',
    'JGJ/T 152-2019',
    # 水泥/砂浆/外加剂
    'GB 175-2023',
    'GB/T 1346-2011',
    'GB/T 17671-2021',
    'JGJ/T 70-2009',
    'GB 8076-2008',
    # 集料/土工/路面
    'GB/T 14684-2022',
    'GB/T 14685-2022',
    'JGJ/T 52-2006',
    'JTG 3430-2020',
    'JTG 3432-2024',
    'JTG E20-2011',
    'JTG E30-2005',
    'JTG E41-2005',
    'JTG E50-2006',
    'JTG E51-2009',
    'JTG 3450-2019',
    # 钢筋/连接
    'GB 1499.1-2024',
    'GB 1499.2-2024',
    'GB/T 232-2010',
    'JGJ 107-2016',
    'JGJ 18-2012',
    # 桩基/地基/现场检测
    'JGJ 79-2012',
    'JGJ 106-2014',
    'JGJ 94-2008',
    'JGJ/T 403-2017',
    'JGJ/T 384-2016',
    'JGJ/T 456-2019',
    # 机场工程相关规范（现场常见）
    'MH/T 5027-2013',
    'MH/T 5033-2017',
    # 水与耐久
    'JGJ 63-2006',
    'GB/T 50046-2018',
]


class Command(BaseCommand):
    help = '同步浦东机场四期扩建工程适配标准到标准规范表（工标网爬取）'

    def add_arguments(self, parser):
        parser.add_argument('--offset', type=int, default=0, help='起始偏移')
        parser.add_argument('--limit', type=int, default=0, help='抓取数量限制，0 表示全部')
        parser.add_argument('--sleep-ms', type=int, default=120, help='每条抓取间隔毫秒')

    def handle(self, *args, **options):
        offset = max(0, int(options.get('offset') or 0))
        limit = max(0, int(options.get('limit') or 0))
        sleep_ms = max(0, int(options.get('sleep_ms') or 0))

        queue = PUDONG_T4_STANDARD_QUEUE[offset:]
        if limit > 0:
            queue = queue[:limit]

        User = get_user_model()
        owner = (
            User.objects.filter(is_superuser=True).order_by('id').first()
            or User.objects.order_by('id').first()
        )

        ok = 0
        failed = 0
        self.stdout.write(f'准备同步 {len(queue)} 条标准（offset={offset}, limit={limit or "ALL"}）')
        for idx, std_no in enumerate(queue, start=1):
            try:
                with transaction.atomic():
                    meta = crawl_standard_metadata(std_no)
                    pub = meta.get('publish_date')
                    imp = meta.get('implement_date')
                    if isinstance(pub, str):
                        pub = datetime.date.fromisoformat(pub)
                    if isinstance(imp, str):
                        imp = datetime.date.fromisoformat(imp)
                    obj, created = Standard.objects.update_or_create(
                        standard_no=meta['standard_no'],
                        defaults={
                            'name': meta.get('name') or std_no,
                            'category': meta.get('category') or 'national',
                            'status': meta.get('status') or 'active',
                            'publish_date': pub,
                            'implement_date': imp,
                            'replaced_case': meta.get('replaced_case') or '',
                            'remark': meta.get('remark') or '',
                        },
                    )
                    if owner and not obj.created_by_id:
                        obj.created_by = owner
                        obj.save(update_fields=['created_by', 'updated_at'])
                ok += 1
                self.stdout.write(f'[{idx}/{len(queue)}] OK   {std_no}')
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.WARNING(f'[{idx}/{len(queue)}] FAIL {std_no}: {exc}'))
            if sleep_ms:
                time.sleep(sleep_ms / 1000.0)

        self.stdout.write(self.style.SUCCESS(f'完成：成功 {ok}，失败 {failed}'))
