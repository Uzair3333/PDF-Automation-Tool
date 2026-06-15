from pathlib import Path

from pypdf import PdfReader, PdfWriter


def merge_pdfs(input_paths: list[str | Path], output_path: str | Path) -> int:
    """Merge multiple PDFs into a single file. Returns total page count."""
    writer = PdfWriter()

    for path in input_paths:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        writer.write(f)

    return len(writer.pages)
