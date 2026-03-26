from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)

ROLE_PERMISSION_MAP = {
    'compile': 'reports.compile_report',
    'audit': 'reports.audit_report',
    'approve': 'reports.approve_report',
}


def verify_signature_permission(user, role: str) -> bool:
    perm = ROLE_PERMISSION_MAP.get(role)
    if not perm:
        return False
    return user.has_perm(perm)


def embed_signature(
    pdf_bytes: bytes,
    signature_image,
    position: dict | None = None,
) -> bytes:
    """Overlay a signature image onto a PDF page.

    Args:
        pdf_bytes: Original PDF content.
        signature_image: File-like object or path to signature image.
        position: Dict with keys 'page', 'x', 'y', 'width', 'height'.
                  Defaults to bottom-right of first page.
    """
    pos = position or {'page': 0, 'x': 350, 'y': 680, 'width': 120, 'height': 50}

    try:
        return _embed_with_pypdf(pdf_bytes, signature_image, pos)
    except ImportError:
        logger.warning('PyPDF not installed, returning original PDF')
        return pdf_bytes


def _embed_with_pypdf(
    pdf_bytes: bytes,
    signature_image,
    pos: dict,
) -> bytes:
    from pypdf import PdfReader, PdfWriter
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    sig_buffer = io.BytesIO()
    c = canvas.Canvas(sig_buffer)
    img = ImageReader(signature_image)
    c.drawImage(
        img, pos['x'], pos['y'],
        width=pos['width'], height=pos['height'],
        mask='auto',
    )
    c.save()
    sig_buffer.seek(0)

    reader = PdfReader(io.BytesIO(pdf_bytes))
    sig_reader = PdfReader(sig_buffer)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if i == pos.get('page', 0):
            page.merge_page(sig_reader.pages[0])
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()
