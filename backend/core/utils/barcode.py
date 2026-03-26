from __future__ import annotations

import io
from typing import Any


def generate_qrcode(data: str, size: int = 200) -> bytes:
    import qrcode
    from qrcode.image.pil import PilImage

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color='black', back_color='white')
    img = img.resize((size, size))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def generate_barcode(data: str) -> bytes:
    import barcode as barcode_lib
    from barcode.writer import ImageWriter

    code128 = barcode_lib.get_barcode_class('code128')
    bc = code128(data, writer=ImageWriter())

    buf = io.BytesIO()
    bc.write(buf, options={'write_text': True})
    return buf.getvalue()


def generate_label_pdf(
    sample_no: str,
    qr_data: str,
    sample_info: dict[str, Any],
) -> bytes:
    from reportlab.lib.pagesizes import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    label_w, label_h = 60 * mm, 40 * mm
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(label_w, label_h))

    _draw_qr_on_label(c, qr_data, label_h)
    _draw_text_on_label(c, sample_no, sample_info, label_h)

    c.showPage()
    c.save()
    return buf.getvalue()


def _draw_qr_on_label(c: Any, qr_data: str, label_h: float) -> None:
    from reportlab.lib.pagesizes import mm
    from reportlab.lib.utils import ImageReader

    qr_bytes = generate_qrcode(qr_data, size=150)
    qr_reader = ImageReader(io.BytesIO(qr_bytes))
    qr_size = 20 * mm
    c.drawImage(qr_reader, 2 * mm, label_h - qr_size - 2 * mm, qr_size, qr_size)


def _draw_text_on_label(
    c: Any,
    sample_no: str,
    sample_info: dict[str, Any],
    label_h: float,
) -> None:
    from reportlab.lib.pagesizes import mm

    x_text = 24 * mm
    y = label_h - 8 * mm
    c.setFont('Helvetica-Bold', 8)
    c.drawString(x_text, y, sample_no)

    c.setFont('Helvetica', 6)
    for key, value in list(sample_info.items())[:4]:
        y -= 6 * mm
        c.drawString(x_text, y, f'{key}: {value}')
