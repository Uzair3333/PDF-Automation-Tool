from pathlib import Path

from pypdf import PdfReader


def extract_text(input_path: str | Path, output_path: str | Path) -> dict:
    """
    Extract all text from a PDF and save it to a TXT file.
    Returns metadata about the extraction.
    """
    reader = PdfReader(str(input_path))
    pages = reader.pages
    total_pages = len(pages)

    if total_pages == 0:
        raise ValueError("PDF has no pages")

    text_parts: list[str] = []
    for page in pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    full_text = "\n".join(text_parts)
    first_page_text = pages[0].extract_text() or ""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    return {
        "total_pages": total_pages,
        "first_page_text": first_page_text,
        "output_path": str(output_path),
    }
