from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def _create_watermark_page(text: str, width: float, height: float) -> PdfReader:
    """Create a single-page PDF with diagonal watermark text."""
    packet = BytesIO()
    page = canvas.Canvas(packet, pagesize=(width, height))
    page.setFont("Helvetica-Bold", 60)
    page.setFillAlpha(0.3)
    page.saveState()
    page.translate(width / 2, height / 2)
    page.rotate(45)
    page.drawCentredString(0, 0, text)
    page.restoreState()
    page.save()
    packet.seek(0)
    return PdfReader(packet)


def watermark_pdf(
    input_path: str | Path,
    output_path: str | Path,
    text: str = "CONFIDENTIAL",
) -> int:
    """Add a watermark to every page. Returns the number of pages processed."""
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        watermark = _create_watermark_page(text, width, height)
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        writer.write(f)

    return len(writer.pages)
