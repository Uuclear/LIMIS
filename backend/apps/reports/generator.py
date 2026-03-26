from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from django.conf import settings
from django.template.loader import render_to_string

from core.utils.numbering import NumberGenerator

if TYPE_CHECKING:
    from .models import Report

logger = logging.getLogger(__name__)

REPORT_TEMPLATE = 'reports/report_template.html'
VERIFICATION_URL_PREFIX = getattr(
    settings, 'REPORT_VERIFICATION_URL', 'https://verify.example.com/report/',
)


def generate_report_no(commission) -> str:
    return NumberGenerator.generate(prefix='BG')


def generate_qr_verification(report_id: int) -> str:
    return f'{VERIFICATION_URL_PREFIX}{report_id}'


def _build_report_context(report: Report) -> dict:
    commission = report.commission
    items = commission.items.all() if hasattr(commission, 'items') else []

    signatures = {}
    for approval in report.approvals.select_related('user').order_by('created_at'):
        signatures[approval.role] = {
            'user': str(approval.user) if approval.user else '',
            'date': approval.created_at,
            'signature': approval.signature.url if approval.signature else None,
        }

    return {
        'report': report,
        'commission': commission,
        'items': items,
        'signatures': signatures,
        'has_cma': report.has_cma,
        'qr_code': report.qr_code,
        'conclusion': report.conclusion,
    }


def generate_report_pdf(report_id: int) -> bytes:
    from .models import Report

    report = Report.objects.select_related(
        'commission', 'compiler', 'auditor', 'approver',
    ).prefetch_related(
        'approvals__user', 'commission__items',
    ).get(pk=report_id)

    context = _build_report_context(report)

    try:
        return _generate_via_weasyprint(context)
    except ImportError:
        logger.warning('WeasyPrint not installed, falling back to placeholder')
        return _generate_placeholder(context)


def _generate_via_weasyprint(context: dict) -> bytes:
    from weasyprint import HTML

    html_content = render_to_string(REPORT_TEMPLATE, context)
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    return pdf_buffer.getvalue()


def _generate_placeholder(context: dict) -> bytes:
    report = context['report']
    text = (
        f'报告编号: {report.report_no}\n'
        f'委托编号: {context["commission"]}\n'
        f'检测结论: {report.conclusion}\n'
    )
    return text.encode('utf-8')
