from __future__ import annotations

import html as html_module
import re
from urllib.parse import quote

import requests
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.views import BaseModelViewSet

from .filters import StandardFilter
from .models import MethodValidation, Standard
from .serializers import (
    MethodValidationSerializer,
    StandardDetailSerializer,
    StandardListSerializer,
    StandardWriteSerializer,
)


class StandardViewSet(BaseModelViewSet):
    queryset = Standard.objects.select_related('replaced_by').all()
    lims_module = 'standards'
    filterset_class = StandardFilter
    search_fields = ['standard_no', 'name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StandardDetailSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return StandardWriteSerializer
        return StandardListSerializer

    @action(detail=False, methods=['post'], url_path='crawl')
    def crawl(self, request: Request) -> Response:
        """
        从工标网（csres.com）按标准编号抓取信息，并返回给前端自动填充表单。
        返回的数据不直接落库；前端提交保存即可。
        """
        standard_no = (request.data.get('standard_no') or '').strip()
        if not standard_no:
            return Response({'code': 400, 'message': '缺少 standard_no'})

        category = 'method'
        if standard_no.startswith('GB'):
            category = 'GB'
        elif standard_no.startswith('JT'):
            category = 'JT'
        elif standard_no.startswith('DB'):
            category = 'DB'
        elif standard_no.startswith('QB'):
            category = 'QB'

        def _cleanup_text(s: str) -> str:
            s = re.sub(r'<[^>]+>', ' ', s or '')
            # HTML entity that appears after 去标签后的文本里
            s = (s or '').replace('&nbsp;', ' ')
            s = re.sub(r'\s+', ' ', s).strip()
            return s

        def _decode_csres(resp: requests.Response) -> str:
            """工标网页面多为 GB18030/GBK，requests 默认按 HTTP 头易误判为 ISO-8859-1。"""
            raw = resp.content or b''
            for enc in ('gb18030', 'gbk', 'utf-8'):
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    continue
            return raw.decode('utf-8', errors='replace')

        def _parse_iso_dates_from_text(text: str) -> tuple[str | None, str | None]:
            """从正文提取 发布日期 / 实施日期（YYYY-MM-DD）。"""
            publish_date = None
            implement_date = None
            m = re.search(
                r'发布日期\s*[:：]\s*([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})',
                text,
            )
            if m:
                publish_date = (
                    f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
                )
            m = re.search(
                r'实施日期\s*[:：]\s*([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})',
                text,
            )
            if m:
                implement_date = (
                    f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
                )
            if not publish_date:
                m = re.search(
                    r'发布日期\s*[:：]\s*([0-9]{4})\s*年\s*([0-9]{1,2})\s*月\s*([0-9]{1,2})\s*日',
                    text,
                )
                if m:
                    publish_date = (
                        f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
                    )
            if not implement_date:
                m = re.search(
                    r'实施日期\s*[:：]\s*([0-9]{4})\s*年\s*([0-9]{1,2})\s*月\s*([0-9]{1,2})\s*日',
                    text,
                )
                if m:
                    implement_date = (
                        f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
                    )
            return publish_date, implement_date

        def _dates_from_search_row_title(search_html_raw: str) -> tuple[str | None, str | None]:
            """搜索结果行 title 属性内常含：发布日期：2019-06-19&#xA;实施日期：2019-12-01"""
            pub = imp = None
            for m in re.finditer(r'title="([^"]+)"', search_html_raw):
                raw_title = html_module.unescape(m.group(1).replace('&#xA;', '\n'))
                p, i = _parse_iso_dates_from_text(raw_title)
                if p:
                    pub = p
                if i:
                    imp = i
                if pub and imp:
                    break
            return pub, imp

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120 Safari/537.36',
        }

        # 1) search page: find detail link id
        search_url = f'http://www.csres.com/s.jsp?keyword={quote(standard_no)}'
        r = requests.get(search_url, headers=headers, timeout=20)
        r.raise_for_status()
        search_html = _decode_csres(r)

        # pick best detail link from search page
        detail_id = None
        keyword_norm = standard_no.replace(' ', '')
        # anchor inner text usually contains standard number, e.g.:
        # <a href="http://www.csres.com/detail/333787.html">GB/T 50081-2019 ...</a>
        for m in re.finditer(
            r'href="[^"]*/detail/(\d+)\.html"[^>]*>\s*(.*?)\s*</a>',
            search_html,
            re.DOTALL,
        ):
            current_id = m.group(1)
            anchor_text = _cleanup_text(m.group(2))
            if not detail_id:
                detail_id = current_id  # fallback: first detail link
            if keyword_norm and keyword_norm in anchor_text.replace(' ', ''):
                detail_id = current_id
                break

        if not detail_id:
            return Response({'code': 404, 'message': '未在 csres.com 搜索结果中找到该标准'})

        detail_url = f'http://www.csres.com/detail/{detail_id}.html'
        d = requests.get(detail_url, headers=headers, timeout=20)
        d.raise_for_status()
        detail_html = _decode_csres(d)
        plain = _cleanup_text(detail_html)

        publish_date, implement_date = _parse_iso_dates_from_text(detail_html)
        if not publish_date or not implement_date:
            sp, si = _parse_iso_dates_from_text(plain)
            publish_date = publish_date or sp
            implement_date = implement_date or si
        if not publish_date or not implement_date:
            sp, si = _dates_from_search_row_title(search_html)
            publish_date = publish_date or sp
            implement_date = implement_date or si

        # 2) parse key fields
        scraped_standard_no = None
        m = re.search(r'标准编号\s*：\s*([^ ]+.*?)(?: 标准状态| 标准价格| 标准简介| 出版社| 英文名称| 替代情况| 发布日期)', plain)
        if m:
            scraped_standard_no = m.group(1).strip()

        english_name = ''
        m = re.search(r'英文名称\s*：\s*(.*?)\s*替代', plain)
        if m:
            english_name = m.group(1).strip()

        scraped_status = ''
        m = re.search(r'标准状态\s*：\s*(现行|即将实施|作废|废止|废止)\s*', plain)
        if m:
            scraped_status = m.group(1)

        status = 'active'
        if '即将' in scraped_status:
            status = 'upcoming'
        elif '作废' in scraped_status or '废止' in scraped_status:
            status = 'abolished'

        # replaced by standard no (if exists)
        replaced_by_no = None
        replaced_case = ''
        idx_replaced = plain.find('替代情况')
        idx_mark = plain.find('中标分类', idx_replaced) if idx_replaced >= 0 else -1
        if idx_replaced >= 0 and idx_mark > idx_replaced:
            segment = plain[idx_replaced:idx_mark]
            # segment example: "替代情况： 替代 GB/T 50081-2002 ..."
            m = re.search(r'替代\s*([A-Z]{1,3}\\/?.+?)\\s*$', segment)
            # fallback: take substring after first '替代'
            if m:
                replaced_case = m.group(1).strip()
            else:
                # take after last "替代"
                parts = segment.split('替代')
                replaced_case = (parts[-1] if parts else segment).strip()

            replaced_case = replaced_case.strip('[]（）()（） ')
            replaced_case = re.sub(r'\s+', ' ', replaced_case).strip()
            replaced_by_no = replaced_case or None

        chinese_name = ''
        # title usually includes: <h1>GB/T xxx 混凝土物理... -工标网</h1>
        m = re.search(r'>\s*([^<]+?)\s*-工标网\s*<', detail_html)
        if m:
            chinese_name = _cleanup_text(m.group(1))
            # remove leading standard_no if present
            if scraped_standard_no and chinese_name.startswith(scraped_standard_no):
                chinese_name = chinese_name[len(scraped_standard_no):].strip(' -')

        # standard intro
        intro = ''
        m = re.search(r'标准简介\s*(.*?)\s*英文名称：', plain)
        if m:
            intro = m.group(1).strip()

        remark = ''
        if english_name:
            remark += f'英文名称：{english_name}\\n'
        if intro:
            remark += f'标准简介：{intro}'

        replaced_by_id = None
        if replaced_by_no:
            replaced = Standard.objects.filter(standard_no=replaced_by_no).first()
            replaced_by_id = replaced.id if replaced else None

        return Response({
            'code': 200,
            'message': '抓取成功',
            'data': {
                'standard_no': scraped_standard_no or standard_no,
                'category': category,
                'status': status,
                'name': chinese_name or '',
                'publish_date': publish_date,
                'implement_date': implement_date,
                'replaced_by': replaced_by_id,
                'replaced_case': replaced_case,
                'remark': remark,
            },
        })


class MethodValidationViewSet(BaseModelViewSet):
    queryset = MethodValidation.objects.select_related(
        'standard', 'validator',
    ).all()
    serializer_class = MethodValidationSerializer
    lims_module = 'standards'
    filterset_fields = ['standard', 'conclusion']
