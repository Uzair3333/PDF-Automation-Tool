# PDF Automation Tool

A Python application for common PDF tasks: merge multiple files, split by page range, extract text, and add watermarks. Includes a **tkinter GUI** and a **CLI menu** for the same operations.

## Features

| Feature | Description | Output |
|---------|-------------|--------|
| **Merge** | Combine two or more PDFs into one file | `output/merged.pdf` |
| **Split** | Extract a page range (1-based, inclusive) | `output/split_<name>_pages_X-Y.pdf` |
| **Extract Text** | Pull text from every page into a TXT file | `output/<name>.txt` |
| **Watermark** | Stamp diagonal text on every page (default: `CONFIDENTIAL`) | `output/watermarked_<name>.pdf` |

## Project Structure

```
PDF-Automation-Tool/
├── input/              # Place source PDFs here (optional for GUI file picker)
├── output/             # Generated files
├── utils/
│   ├── merge.py
│   ├── split.py
│   ├── extract.py
│   └── watermark.py
├── gui.py              # tkinter GUI
├── main.py             # Entry point (GUI by default)
├── paths.py            # Shared input/output paths
└── requirements.txt
```

## Requirements

- Python 3.10+
- [pypdf](https://pypi.org/project/pypdf/) — read, merge, split, and extract text
- [reportlab](https://pypi.org/project/reportlab/) — generate watermark overlays

## Installation

```bash
git clone https://github.com/yourusername/PDF-Automation-Tool.git
cd PDF-Automation-Tool
pip install -r requirements.txt
```

## Usage

### GUI (default)

```bash
python main.py
```

Or run the GUI directly:

```bash
python gui.py
```

The window has four tabs:

- **Merge** — add PDFs to a list, then merge them
- **Split** — pick a file, set start/end pages, split
- **Extract Text** — pick a file, save text and preview the first page
- **Watermark** — pick a file, set watermark text, apply

Use **Open Input Folder** / **Open Output Folder** in the header to jump to those directories.

### CLI

```bash
python main.py --cli
```

The CLI lists PDFs from `input/` and prompts you to choose files and options in the terminal.

## Example Workflow

1. Copy your PDFs into `input/`
2. Run `python main.py`
3. Use the Merge tab to combine files, or Split / Extract / Watermark as needed
4. Find results in `output/`

## Using the Utilities Directly

```python
from utils.merge import merge_pdfs
from utils.split import split_pdf
from utils.extract import extract_text
from utils.watermark import watermark_pdf

merge_pdfs(["input/a.pdf", "input/b.pdf"], "output/merged.pdf")
split_pdf("input/doc.pdf", 1, 5, "output/pages_1-5.pdf")
extract_text("input/doc.pdf", "output/doc.txt")
watermark_pdf("input/doc.pdf", "output/watermarked_doc.pdf", text="CONFIDENTIAL")
```

## License

See [LICENSE](LICENSE).
