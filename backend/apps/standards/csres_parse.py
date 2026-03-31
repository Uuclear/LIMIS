"""
工标网 csres.com 抓取（纯解析 + HTTP，无 Django 依赖）。

供 csres_crawl.py 与 scripts/csres_fetch_demo.py 共用。
选条策略：结构化候选优先「现行」>「即将实施」> 其它 > 作废/废止，其次标准号年号较新，
再次关键词与标准号匹配度；无结构化行时对详情链接按关键词 + 年号择优。
"""
from __future__ import annotations

import html as html_module
import re
from dataclasses import dataclass
from urllib.parse import quote

import requests

CSRES_BASE = 'http://www.csres.com'


def decode_csres(resp: requests.Response) -> str:
    raw = resp.content or b''
    for enc in ('gb18030', 'gbk', 'utf-8'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='replace')


def clean_visible(s: str) -> str:
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = (s or '').replace('&nbsp;', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def strip_standard_name(name: str) -> str:
    s = (name or '').strip()
    s = re.sub(r'\s*国家标准\s*\(GB\)\s*$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*行业标准\s*\([^)]+\)\s*$', '', s)
    s = re.sub(r'\s*-\s*工标网\s*$', '', s)
    return s.strip(' -')


def year_from_std_no(std_no: str) -> int:
    m = re.search(r'-(\d{4})\s*$', (std_no or '').replace(' ', ''))
    return int(m.group(1)) if m else 0


def status_rank_cn(label: str) -> int:
    s = (label or '').strip()
    if s == '现行':
        return 3
    if s == '即将实施':
        return 2
    if s in ('作废', '废止'):
        return 0
    return 1


def map_status_to_model(scraped: str) -> str:
    s = (scraped or '').strip()
    if '即将' in s:
        return 'upcoming'
    if s in ('作废', '废止'):
        return 'abolished'
    return 'active'


@dataclass
class SearchCandidate:
    detail_id: str
    standard_no: str
    name_hint: str
    status_cn: str
    publish_date: str | None
    implement_date: str | None


def norm_date(s: str) -> str:
    parts = s.strip().split('-')
    if len(parts) == 3:
        return f'{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}'
    return s


def parse_title_block(title: str) -> dict:
    t = html_module.unescape(title.replace('&#xA;', '\n'))
    out: dict[str, str | None] = {
        'standard_no': None,
        'name': None,
        'publish_date': None,
        'implement_date': None,
    }
    m = re.search(r'编号[：:]\s*([A-Z0-9/\s\.]+-\d{4})', t)
    if m:
        out['standard_no'] = re.sub(r'\s+', ' ', m.group(1).strip())
    m = re.search(r'标题[：:]\s*([^\n]+)', t)
    if m:
        out['name'] = m.group(1).strip()
    pubs = [
        norm_date(x)
        for x in re.findall(r'发布日期[：:]\s*([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})', t)
    ]
    imps = [
        norm_date(x)
        for x in re.findall(r'实施日期[：:]\s*([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})', t)
    ]
    if len(pubs) >= 2:
        out['publish_date'], out['implement_date'] = pubs[0], pubs[1]
    elif len(pubs) == 1:
        out['publish_date'] = pubs[0]
        if imps:
            out['implement_date'] = imps[0]
    elif imps:
        out['implement_date'] = imps[0]
    return out


def parse_search_candidates(search_html: str) -> list[SearchCandidate]:
    found: list[SearchCandidate] = []
    for m in re.finditer(
        r'<tr\s[^>]*bgcolor[^>]*>(.*?)</tr>',
        search_html,
        re.DOTALL | re.IGNORECASE,
    ):
        block = m.group(0)
        if 'onclick="mClk(' not in block:
            continue
        mid = re.search(r'onclick="mClk\((\d+)\);"', block)
        mt = re.search(r'title="([^"]+)"', block)
        if not mid or not mt:
            continue
        title = mt.group(1)
        meta = parse_title_block(title)
        std_no = meta.get('standard_no')
        if not std_no:
            continue
        status_cn = ''
        if re.search(r'>作废<', block):
            status_cn = '作废'
        elif re.search(r'>废止<', block):
            status_cn = '废止'
        elif re.search(r'>现行<', block):
            status_cn = '现行'
        elif re.search(r'>即将实施<', block):
            status_cn = '即将实施'
        found.append(
            SearchCandidate(
                detail_id=mid.group(1),
                standard_no=std_no,
                name_hint=(meta.get('name') or '')[:300],
                status_cn=status_cn,
                publish_date=meta.get('publish_date'),
                implement_date=meta.get('implement_date'),
            ),
        )
    return found


def pick_best_candidate(keyword: str, cands: list[SearchCandidate]) -> SearchCandidate | None:
    """
    优先现行/即将实施，其次年号较新，再次关键词与标准号匹配。
    """
    if not cands:
        return None
    kw = keyword.replace(' ', '').upper()

    def score(c: SearchCandidate) -> tuple:
        sr = status_rank_cn(c.status_cn)
        yr = year_from_std_no(c.standard_no)
        kn = c.standard_no.replace(' ', '').upper()
        match = 0
        if kw and kw in kn:
            match = 2
        elif kw and any(ch.isdigit() for ch in kw) and kn in kw:
            match = 1
        return (sr, yr, match)

    return max(cands, key=score)


def pick_best_fallback_link(search_html: str, keyword: str) -> str | None:
    """
    无 bgcolor 结构化行时：在所有含关键词的详情链接中，取标准号年号最大的一条
    （模糊搜「GB/T 50081」时避免落到旧版 2002）。
    """
    kw = keyword.replace(' ', '').upper()
    best: tuple[str, int] | None = None
    for m in re.finditer(
        r'href="[^"]*/detail/(\d+)\.html"[^>]*>\s*(.*?)\s*</a>',
        search_html,
        re.DOTALL | re.IGNORECASE,
    ):
        did, anchor = m.group(1), clean_visible(m.group(2))
        an = anchor.replace(' ', '').upper()
        if kw and kw not in an:
            continue
        ym = re.search(r'-(\d{4})\b', an)
        yr = int(ym.group(1)) if ym else 0
        if best is None or yr > best[1]:
            best = (did, yr)
    if best:
        return best[0]
    picked = None
    for m in re.finditer(
        r'href="[^"]*/detail/(\d+)\.html"[^>]*>\s*(.*?)\s*</a>',
        search_html,
        re.DOTALL | re.IGNORECASE,
    ):
        if not picked:
            picked = m.group(1)
        anchor = clean_visible(m.group(2))
        an = anchor.replace(' ', '').upper()
        if kw and kw in an:
            return m.group(1)
    return picked


def choose_detail_id(search_html: str, keyword: str) -> tuple[str | None, SearchCandidate | None]:
    cands = parse_search_candidates(search_html)
    best = pick_best_candidate(keyword, cands)
    if best:
        return best.detail_id, best
    did = pick_best_fallback_link(search_html, keyword)
    return did, None


def parse_detail(html: str) -> dict:
    plain = clean_visible(html)

    std_no = ''
    m = re.search(
        r'标准编号\s*[:：]\s*[\s\S]{0,120}?<strong>([^<]+)</strong>',
        html,
        re.IGNORECASE,
    )
    if m:
        std_no = re.sub(r'\s+', ' ', m.group(1).strip())

    status_cn = ''
    m = re.search(
        r'标准状态\s*[:：]\s*[\s\S]{0,200}?<strong>(现行|即将实施|作废|废止)</strong>',
        html,
        re.IGNORECASE,
    )
    if m:
        status_cn = m.group(1)

    publish_date = implement_date = None
    m = re.search(
        r'发布日期\s*：[\s\S]*?</td>\s*<td[^>]*>\s*&nbsp;<span[^>]*>\s*([0-9]{4}-[0-9]{2}-[0-9]{2})',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        publish_date = m.group(1)
    m = re.search(
        r'实施日期\s*：[\s\S]*?</td>\s*<td[^>]*>\s*&nbsp;<span[^>]*>\s*([0-9]{4}-[0-9]{2}-[0-9]{2})',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        implement_date = m.group(1)

    if not publish_date:
        m = re.search(r'发布日期\s*[:：]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', plain)
        if m:
            publish_date = m.group(1)
    if not implement_date:
        m = re.search(r'实施日期\s*[:：]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', plain)
        if m:
            implement_date = m.group(1)

    name = ''
    m = re.search(r'<h3>\s*([\s\S]*?)</h3>', html, re.IGNORECASE)
    if m:
        inner = re.sub(r'<[^>]+>', '', m.group(1))
        name = strip_standard_name(clean_visible(inner))
    if not name:
        m = re.search(r'>\s*([^<]+?)\s*-\s*工标网\s*<', html)
        if m:
            raw = clean_visible(m.group(1))
            if std_no and raw.upper().startswith(std_no.replace(' ', '').upper()):
                raw = raw[len(std_no) :].strip(' -')
            name = strip_standard_name(raw)

    intro = ''
    m = re.search(
        r'标准简介[\s\S]{0,800}?<td[^>]*class="f14"[^>]*>\s*([\s\S]*?)</td>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        intro = clean_visible(m.group(1))

    english_name = ''
    m = re.search(
        r'英文名称\s*：[\s\S]*?</td>\s*<td[^>]*>\s*&nbsp;<span[^>]*>([^<]+)</span>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        english_name = (m.group(1) or '').strip()

    replaced_case = ''
    m = re.search(
        r'替代\s*<a[^>]+>([^<]+)</a>',
        html,
        re.IGNORECASE,
    )
    if m:
        replaced_case = f'替代{m.group(1).strip()}'
    else:
        m = re.search(
            r'替代情况[：:][\s\S]{0,400}?<span[^>]*>([\s\S]*?)</span>\s*</td>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if m:
            replaced_case = clean_visible(m.group(1))

    if not std_no:
        m = re.search(
            r'标准编号\s*[:：]\s*([^\s<]+[^\n<]*?)(?:\s+标准状态|\s+标准价格|\s+标准简介|\s+英文名称|\s+替代)',
            plain,
        )
        if m:
            std_no = re.sub(r'\s+', ' ', m.group(1).strip())

    return {
        'standard_no': std_no,
        'name': name,
        'status_cn': status_cn,
        'publish_date': publish_date,
        'implement_date': implement_date,
        'intro': intro,
        'replaced_case': replaced_case,
        'english_name': english_name,
    }


def infer_category(standard_no: str) -> str:
    s = (standard_no or '').strip().upper()
    if s.startswith('GB'):
        return 'GB'
    if s.startswith('JT'):
        return 'JT'
    if s.startswith('DB'):
        return 'DB'
    if s.startswith('QB'):
        return 'QB'
    return 'method'


def build_remark(intro: str, english_name: str) -> str:
    lines: list[str] = []
    if intro.strip():
        lines.append(f'标准简介：{intro.strip()}')
    if english_name.strip():
        lines.append(f'英文名称：{english_name.strip()}')
    return '\n'.join(lines)


def fetch_csres_metadata(standard_no: str) -> dict:
    """
    抓取工标网并返回与 LIMS crawl 接口一致的业务字段（replaced_by 恒为 None，由 ORM 层补全）。

    键：standard_no, category, status, status_label, name,
    publish_date, implement_date, replaced_by, replaced_case, remark
    """
    standard_no = (standard_no or '').strip()
    if not standard_no:
        raise RuntimeError('标准号为空')

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120 Safari/537.36'
        ),
    }

    search_url = f'{CSRES_BASE}/s.jsp?keyword={quote(standard_no)}'
    r = requests.get(search_url, headers=headers, timeout=25)
    r.raise_for_status()
    search_html = decode_csres(r)

    detail_id, best = choose_detail_id(search_html, standard_no)
    if not detail_id:
        raise RuntimeError('未在 csres.com 搜索结果中找到该标准')

    detail_url = f'{CSRES_BASE}/detail/{detail_id}.html'
    d = requests.get(detail_url, headers=headers, timeout=25)
    d.raise_for_status()
    detail_html = decode_csres(d)

    p = parse_detail(detail_html)
    final_no = (p.get('standard_no') or '').strip() or standard_no
    status_cn = (p.get('status_cn') or '').strip()
    if not status_cn and best:
        status_cn = best.status_cn
    model_status = map_status_to_model(status_cn)

    name = strip_standard_name(p.get('name') or '')
    if not name and best and best.name_hint:
        name = strip_standard_name(best.name_hint)

    pub = p.get('publish_date')
    imp = p.get('implement_date')
    if best is not None:
        pub = pub or best.publish_date
        imp = imp or best.implement_date

    intro = (p.get('intro') or '').strip()
    english_name = (p.get('english_name') or '').strip()
    remark = build_remark(intro, english_name)

    replaced_case = (p.get('replaced_case') or '').strip()
    replaced_case = re.sub(r'\s+', ' ', replaced_case)
    replaced_case = re.sub(r'替代\s+', '替代', replaced_case)

    category = infer_category(final_no)

    return {
        'standard_no': final_no,
        'category': category,
        'status': model_status,
        'status_label': {
            'active': '现行',
            'upcoming': '即将实施',
            'abolished': '已作废',
        }.get(model_status, model_status),
        'name': name,
        'publish_date': pub,
        'implement_date': imp,
        'replaced_by': None,
        'replaced_case': replaced_case,
        'remark': remark,
        # 非模型字段，仅供调试；csres_crawl 在返回 API 前会移除
        'detail_id': detail_id,
    }
