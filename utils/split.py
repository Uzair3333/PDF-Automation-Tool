from pathlib import Path

from pypdf import PdfReader, PdfWriter


def split_pdf(
    input_path: str | Path,
    start_page: int,
    end_page: int,
    output_path: str | Path,
) -> int:
    """
    Extract a page range from a PDF (1-based, inclusive).
    Returns the number of pages written.
    """
    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)

    if start_page < 1 or end_page < start_page or start_page > total_pages:
        raise ValueError(
            f"Invalid page range {start_page}-{end_page} "
            f"(PDF has {total_pages} page(s))"
        )

    end_page = min(end_page, total_pages)
    writer = PdfWriter()

    for page_num in range(start_page, end_page + 1):
        writer.add_page(reader.pages[page_num - 1])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        writer.write(f)

    return len(writer.pages)
