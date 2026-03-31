#!/usr/bin/env python3
"""
独立演示：与 LIMS「从工标网爬取」共用 apps.standards.csres_parse.fetch_csres_metadata。

选条策略：优先现行标准、年号较新；与后端 /v1/standards/crawl/ 一致。

用法:
  PYTHONPATH=/opt/limis/backend python3 scripts/csres_fetch_demo.py
  PYTHONPATH=/opt/limis/backend python3 scripts/csres_fetch_demo.py "gb/t 50081"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.standards.csres_parse import fetch_csres_metadata  # noqa: E402

DEFAULT_KEYWORD = "GB/T 50081-2019"


def main() -> None:
    p = argparse.ArgumentParser(description="工标网抓取演示（与 LIMS crawl 同源逻辑）")
    p.add_argument(
        "keyword",
        nargs="?",
        default=DEFAULT_KEYWORD,
        help=f"搜索关键词，默认 {DEFAULT_KEYWORD!r}",
    )
    args = p.parse_args()
    keyword = (args.keyword or "").strip() or DEFAULT_KEYWORD

    raw = fetch_csres_metadata(keyword)
    detail_id = raw.pop("detail_id", None)

    print(f"关键词: {keyword!r}")
    print(f"选用详情页 ID={detail_id}（优先现行 / 较新年号）\n")

    print("========== LIMS crawl 返回字段（与系统标准规范 / API data 一致）==========")
    for k in (
        "standard_no",
        "category",
        "status",
        "status_label",
        "name",
        "publish_date",
        "implement_date",
        "replaced_by",
        "replaced_case",
        "remark",
    ):
        print(f"{k}: {raw.get(k)!r}")
    print("==============================================================")


if __name__ == "__main__":
    main()
