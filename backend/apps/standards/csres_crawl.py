"""
从工标网抓取标准元数据，供 Standard 模型与 /v1/standards/crawl/ 使用。

解析与 HTTP 逻辑见 csres_parse.py（与 scripts/csres_fetch_demo.py 共用）。
"""
from __future__ import annotations

import re

from apps.standards.models import Standard

from .csres_parse import fetch_csres_metadata


def crawl_standard_metadata(standard_no: str) -> dict:
    """
    抓取并返回可写入 Standard 的字段 dict。

    字段与 StandardWriteSerializer / 前端表单一致：
    standard_no, category, status, name, publish_date, implement_date,
    replaced_by, replaced_case, remark

    另含 status_label 便于展示（现行 / 即将实施 / 已作废）。
    """
    data = fetch_csres_metadata(standard_no)
    data.pop('detail_id', None)

    replaced_case = (data.get('replaced_case') or '').strip()

    replaced_by_id = None
    m = re.search(r'(GB/?T?\s*[0-9.]+-\d{4})', replaced_case)
    if m:
        sub_no = re.sub(r'\s+', ' ', m.group(1).strip())
        old = Standard.objects.filter(standard_no=sub_no).first()
        if old:
            replaced_by_id = old.id

    return {**data, 'replaced_by': replaced_by_id}
