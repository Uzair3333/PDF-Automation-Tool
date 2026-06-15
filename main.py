import sys

from paths import INPUT_DIR, OUTPUT_DIR
from pypdf import PdfReader

from utils.extract import extract_text
from utils.merge import merge_pdfs
from utils.split import split_pdf
from utils.watermark import watermark_pdf


def list_pdfs(directory):
  if not directory.exists():
    directory.mkdir(parents=True, exist_ok=True)
  return sorted(directory.glob("*.pdf"))


def select_pdf(prompt: str = "Select a PDF"):
  pdfs = list_pdfs(INPUT_DIR)

  if not pdfs:
    print(f"\nNo PDF files found in {INPUT_DIR}\n")
    return None

  print(f"\n{prompt}:")
  for i, pdf in enumerate(pdfs, start=1):
    print(f"  {i}. {pdf.name}")

  try:
    choice = int(input("Enter number: "))
    if 1 <= choice <= len(pdfs):
      return pdfs[choice - 1]
  except ValueError:
    pass

  print("\nInvalid selection.\n")
  return None


def select_multiple_pdfs():
  pdfs = list_pdfs(INPUT_DIR)

  if not pdfs:
    print(f"\nNo PDF files found in {INPUT_DIR}\n")
    return []

  print("\nAvailable PDFs:")
  for i, pdf in enumerate(pdfs, start=1):
    print(f"  {i}. {pdf.name}")

  print("Enter numbers separated by commas (e.g. 1,2,3):")
  raw = input().strip()

  try:
    indices = [int(x.strip()) for x in raw.split(",")]
    selected = [pdfs[i - 1] for i in indices if 1 <= i <= len(pdfs)]
    if selected:
      return selected
  except ValueError:
    pass

  print("\nInvalid selection.\n")
  return []


def handle_merge():
  selected = select_multiple_pdfs()
  if len(selected) < 2:
    print("\nSelect at least 2 PDFs to merge.\n")
    return

  output_path = OUTPUT_DIR / "merged.pdf"
  try:
    page_count = merge_pdfs(selected, output_path)
    print(f"\nMerged {len(selected)} PDF(s) -> {output_path}")
    print(f"Total pages: {page_count}\n")
  except Exception as e:
    print(f"\nError merging PDFs: {e}\n")


def handle_split():
  pdf = select_pdf("Select a PDF to split")
  if not pdf:
    return

  reader_pages = PdfReader(str(pdf)).pages
  total = len(reader_pages)
  print(f"\nPDF has {total} page(s). Pages are numbered from 1.\n")

  try:
    start = int(input("Start page: "))
    end = int(input("End page: "))
  except ValueError:
    print("\nInvalid page numbers.\n")
    return

  output_path = OUTPUT_DIR / f"split_{pdf.stem}_pages_{start}-{end}.pdf"
  try:
    written = split_pdf(pdf, start, end, output_path)
    print(f"\nCreated {output_path} ({written} page(s))\n")
  except ValueError as e:
    print(f"\n{e}\n")
  except Exception as e:
    print(f"\nError splitting PDF: {e}\n")


def handle_extract():
  pdf = select_pdf("Select a PDF to extract text from")
  if not pdf:
    return

  output_path = OUTPUT_DIR / f"{pdf.stem}.txt"
  try:
    result = extract_text(pdf, output_path)
    print(f"\nText saved to {result['output_path']}")
    print(f"Total pages: {result['total_pages']}")
    print("----- First Page Preview -----")
    preview = result["first_page_text"][:500]
    print(preview if preview else "(no text on first page)")
    if len(result["first_page_text"]) > 500:
      print("...")
    print()
  except Exception as e:
    print(f"\nError extracting text: {e}\n")


def handle_watermark():
  pdf = select_pdf("Select a PDF to watermark")
  if not pdf:
    return

  output_path = OUTPUT_DIR / f"watermarked_{pdf.name}"
  try:
    pages = watermark_pdf(pdf, output_path)
    print(f"\nWatermarked PDF saved to {output_path}")
    print(f"Pages processed: {pages}\n")
  except Exception as e:
    print(f"\nError adding watermark: {e}\n")


def show_menu():
  print("\n--- PDF Automation Tool ---\n")
  print("1. Merge PDFs")
  print("2. Split PDF")
  print("3. Extract Text from PDF")
  print("4. Add Watermark")
  print("5. Exit")

  try:
    return int(input("\nEnter your choice: "))
  except ValueError:
    print("\nInvalid value. Choose one of the options above.\n")
    return None


def run_cli():
  INPUT_DIR.mkdir(parents=True, exist_ok=True)
  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

  actions = {
    1: handle_merge,
    2: handle_split,
    3: handle_extract,
    4: handle_watermark,
  }

  while True:
    choice = show_menu()

    if choice == 5:
      print("\nGoodbye!\n")
      break

    if choice in actions:
      actions[choice]()
    elif choice is not None:
      print("\nInvalid input. Please select a valid option.\n")


if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "--cli":
    run_cli()
  else:
    from gui import run_gui

    run_gui()
