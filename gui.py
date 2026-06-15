import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from pypdf import PdfReader

from paths import INPUT_DIR, OUTPUT_DIR
from utils.extract import extract_text
from utils.merge import merge_pdfs
from utils.split import split_pdf
from utils.watermark import watermark_pdf


class PDFToolApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF Automation Tool")
        self.root.minsize(640, 480)

        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        self._busy = False
        self._merge_files: list[Path] = []

        self._build_ui()

    def _build_ui(self) -> None:
        header = ttk.Frame(self.root, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="PDF Automation Tool",
            font=("Segoe UI", 14, "bold"),
        ).pack(side=tk.LEFT)

        ttk.Button(header, text="Open Input Folder", command=self._open_input).pack(
            side=tk.RIGHT, padx=(6, 0)
        )
        ttk.Button(header, text="Open Output Folder", command=self._open_output).pack(
            side=tk.RIGHT, padx=(6, 0)
        )

        notebook = ttk.Notebook(self.root, padding=8)
        notebook.pack(fill=tk.BOTH, expand=True)

        self._merge_tab = ttk.Frame(notebook, padding=12)
        self._split_tab = ttk.Frame(notebook, padding=12)
        self._extract_tab = ttk.Frame(notebook, padding=12)
        self._watermark_tab = ttk.Frame(notebook, padding=12)

        notebook.add(self._merge_tab, text="Merge")
        notebook.add(self._split_tab, text="Split")
        notebook.add(self._extract_tab, text="Extract Text")
        notebook.add(self._watermark_tab, text="Watermark")

        self._build_merge_tab()
        self._build_split_tab()
        self._build_extract_tab()
        self._build_watermark_tab()

        status_frame = ttk.Frame(self.root, padding=(12, 8))
        status_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)

    def _build_merge_tab(self) -> None:
        ttk.Label(
            self._merge_tab,
            text="Select two or more PDFs to merge into one file.",
        ).pack(anchor=tk.W)

        list_frame = ttk.Frame(self._merge_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 8))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.merge_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set,
            height=10,
        )
        self.merge_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.merge_listbox.yview)

        btn_row = ttk.Frame(self._merge_tab)
        btn_row.pack(fill=tk.X)

        self.merge_add_btn = ttk.Button(
            btn_row, text="Add PDFs...", command=self._merge_add_files
        )
        self.merge_add_btn.pack(side=tk.LEFT)

        self.merge_remove_btn = ttk.Button(
            btn_row, text="Remove Selected", command=self._merge_remove_selected
        )
        self.merge_remove_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.merge_clear_btn = ttk.Button(
            btn_row, text="Clear All", command=self._merge_clear
        )
        self.merge_clear_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.merge_run_btn = ttk.Button(
            btn_row, text="Merge PDFs", command=self._run_merge
        )
        self.merge_run_btn.pack(side=tk.RIGHT)

    def _build_split_tab(self) -> None:
        ttk.Label(self._split_tab, text="PDF file:").grid(
            row=0, column=0, sticky=tk.W, pady=4
        )

        self.split_path = tk.StringVar()
        ttk.Entry(self._split_tab, textvariable=self.split_path, width=50).grid(
            row=0, column=1, sticky=tk.EW, padx=(8, 0), pady=4
        )
        ttk.Button(self._split_tab, text="Browse...", command=self._split_browse).grid(
            row=0, column=2, padx=(8, 0), pady=4
        )

        self.split_page_info = ttk.Label(self._split_tab, text="")
        self.split_page_info.grid(row=1, column=1, sticky=tk.W, padx=(8, 0))

        ttk.Label(self._split_tab, text="Start page:").grid(
            row=2, column=0, sticky=tk.W, pady=4
        )
        self.split_start = tk.Spinbox(self._split_tab, from_=1, to=9999, width=8)
        self.split_start.grid(row=2, column=1, sticky=tk.W, padx=(8, 0), pady=4)

        ttk.Label(self._split_tab, text="End page:").grid(
            row=3, column=0, sticky=tk.W, pady=4
        )
        self.split_end = tk.Spinbox(self._split_tab, from_=1, to=9999, width=8)
        self.split_end.grid(row=3, column=1, sticky=tk.W, padx=(8, 0), pady=4)

        self.split_run_btn = ttk.Button(
            self._split_tab, text="Split PDF", command=self._run_split
        )
        self.split_run_btn.grid(row=4, column=1, sticky=tk.W, padx=(8, 0), pady=(12, 0))

        self._split_tab.columnconfigure(1, weight=1)

    def _build_extract_tab(self) -> None:
        ttk.Label(self._extract_tab, text="PDF file:").grid(
            row=0, column=0, sticky=tk.W, pady=4
        )

        self.extract_path = tk.StringVar()
        ttk.Entry(self._extract_tab, textvariable=self.extract_path, width=50).grid(
            row=0, column=1, sticky=tk.EW, padx=(8, 0), pady=4
        )
        ttk.Button(
            self._extract_tab, text="Browse...", command=self._extract_browse
        ).grid(row=0, column=2, padx=(8, 0), pady=4)

        self.extract_run_btn = ttk.Button(
            self._extract_tab, text="Extract Text", command=self._run_extract
        )
        self.extract_run_btn.grid(row=1, column=1, sticky=tk.W, padx=(8, 0), pady=(8, 0))

        ttk.Label(self._extract_tab, text="Preview (first page):").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(12, 4)
        )

        preview_frame = ttk.Frame(self._extract_tab)
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=tk.NSEW, pady=(0, 4))

        preview_scroll = ttk.Scrollbar(preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.extract_preview = tk.Text(
            preview_frame,
            height=12,
            wrap=tk.WORD,
            yscrollcommand=preview_scroll.set,
            state=tk.DISABLED,
        )
        self.extract_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.extract_preview.yview)

        self._extract_tab.columnconfigure(1, weight=1)
        self._extract_tab.rowconfigure(3, weight=1)

    def _build_watermark_tab(self) -> None:
        ttk.Label(self._watermark_tab, text="PDF file:").grid(
            row=0, column=0, sticky=tk.W, pady=4
        )

        self.watermark_path = tk.StringVar()
        ttk.Entry(
            self._watermark_tab, textvariable=self.watermark_path, width=50
        ).grid(row=0, column=1, sticky=tk.EW, padx=(8, 0), pady=4)
        ttk.Button(
            self._watermark_tab, text="Browse...", command=self._watermark_browse
        ).grid(row=0, column=2, padx=(8, 0), pady=4)

        ttk.Label(self._watermark_tab, text="Watermark text:").grid(
            row=1, column=0, sticky=tk.W, pady=4
        )
        self.watermark_text = tk.StringVar(value="CONFIDENTIAL")
        ttk.Entry(
            self._watermark_tab, textvariable=self.watermark_text, width=30
        ).grid(row=1, column=1, sticky=tk.W, padx=(8, 0), pady=4)

        self.watermark_run_btn = ttk.Button(
            self._watermark_tab, text="Apply Watermark", command=self._run_watermark
        )
        self.watermark_run_btn.grid(
            row=2, column=1, sticky=tk.W, padx=(8, 0), pady=(12, 0)
        )

        self._watermark_tab.columnconfigure(1, weight=1)

    def _open_input(self) -> None:
        self._open_folder(INPUT_DIR)

    def _open_output(self) -> None:
        self._open_folder(OUTPUT_DIR)

    def _open_folder(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        import os

        os.startfile(path)

    def _browse_pdf(self, var: tk.StringVar, on_select=None) -> None:
        path = filedialog.askopenfilename(
            title="Select PDF",
            initialdir=INPUT_DIR,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if path:
            var.set(path)
            if on_select:
                on_select(path)

    def _split_browse(self) -> None:
        self._browse_pdf(self.split_path, self._update_split_page_info)

    def _extract_browse(self) -> None:
        self._browse_pdf(self.extract_path)

    def _watermark_browse(self) -> None:
        self._browse_pdf(self.watermark_path)

    def _update_split_page_info(self, path: str) -> None:
        try:
            total = len(PdfReader(path).pages)
            self.split_page_info.config(text=f"This PDF has {total} page(s).")
            self.split_start.config(to=total)
            self.split_end.config(to=total)
            self.split_start.delete(0, tk.END)
            self.split_start.insert(0, "1")
            self.split_end.delete(0, tk.END)
            self.split_end.insert(0, str(total))
        except Exception as e:
            self.split_page_info.config(text=f"Could not read PDF: {e}")

    def _merge_add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select PDFs to merge",
            initialdir=INPUT_DIR,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        for path in paths:
            pdf = Path(path)
            if pdf not in self._merge_files:
                self._merge_files.append(pdf)
                self.merge_listbox.insert(tk.END, str(pdf))

    def _merge_remove_selected(self) -> None:
        selected = list(self.merge_listbox.curselection())
        for index in reversed(selected):
            self.merge_listbox.delete(index)
            del self._merge_files[index]

    def _merge_clear(self) -> None:
        self.merge_listbox.delete(0, tk.END)
        self._merge_files.clear()

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        for btn in (
            self.merge_add_btn,
            self.merge_remove_btn,
            self.merge_clear_btn,
            self.merge_run_btn,
            self.split_run_btn,
            self.extract_run_btn,
            self.watermark_run_btn,
        ):
            btn.config(state=state)

    def _set_status(self, text: str) -> None:
        self.status_label.config(text=text)

    def _run_in_thread(self, task, on_success, on_error=None) -> None:
        if self._busy:
            return

        self._set_busy(True)
        self._set_status("Working...")

        def work() -> None:
            try:
                result = task()
                self.root.after(0, lambda: self._finish_success(on_success, result))
            except Exception as e:
                self.root.after(0, lambda: self._finish_error(on_error, e))

        threading.Thread(target=work, daemon=True).start()

    def _finish_success(self, callback, result) -> None:
        self._set_busy(False)
        callback(result)

    def _finish_error(self, callback, error: Exception) -> None:
        self._set_busy(False)
        if callback:
            callback(error)
        else:
            self._set_status("Error")
            messagebox.showerror("Error", str(error))

    def _run_merge(self) -> None:
        if len(self._merge_files) < 2:
            messagebox.showwarning(
                "Merge PDFs", "Select at least two PDF files to merge."
            )
            return

        output_path = OUTPUT_DIR / "merged.pdf"
        files = list(self._merge_files)

        def task():
            pages = merge_pdfs(files, output_path)
            return {"pages": pages, "count": len(files), "path": output_path}

        def on_success(result) -> None:
            self._set_status(f"Merged {result['count']} PDF(s) -> {result['path'].name}")
            messagebox.showinfo(
                "Merge complete",
                f"Merged {result['count']} PDF(s).\n"
                f"Total pages: {result['pages']}\n"
                f"Saved to: {result['path']}",
            )

        self._run_in_thread(task, on_success)

    def _run_split(self) -> None:
        path = self.split_path.get().strip()
        if not path:
            messagebox.showwarning("Split PDF", "Select a PDF file.")
            return

        try:
            start = int(self.split_start.get())
            end = int(self.split_end.get())
        except ValueError:
            messagebox.showwarning("Split PDF", "Enter valid page numbers.")
            return

        pdf = Path(path)
        output_path = OUTPUT_DIR / f"split_{pdf.stem}_pages_{start}-{end}.pdf"

        def task():
            written = split_pdf(pdf, start, end, output_path)
            return {"written": written, "path": output_path}

        def on_success(result) -> None:
            self._set_status(f"Split saved to {result['path'].name}")
            messagebox.showinfo(
                "Split complete",
                f"Created {result['written']} page(s).\nSaved to: {result['path']}",
            )

        def on_error(error: Exception) -> None:
            self._set_status("Split failed")
            messagebox.showerror("Split failed", str(error))

        self._run_in_thread(task, on_success, on_error)

    def _run_extract(self) -> None:
        path = self.extract_path.get().strip()
        if not path:
            messagebox.showwarning("Extract Text", "Select a PDF file.")
            return

        pdf = Path(path)
        output_path = OUTPUT_DIR / f"{pdf.stem}.txt"

        def task():
            return extract_text(pdf, output_path)

        def on_success(result) -> None:
            preview = result["first_page_text"][:2000]
            self.extract_preview.config(state=tk.NORMAL)
            self.extract_preview.delete("1.0", tk.END)
            self.extract_preview.insert(
                tk.END, preview or "(no text on first page)"
            )
            self.extract_preview.config(state=tk.DISABLED)

            self._set_status(f"Text saved to {Path(result['output_path']).name}")
            messagebox.showinfo(
                "Extract complete",
                f"Total pages: {result['total_pages']}\n"
                f"Saved to: {result['output_path']}",
            )

        self._run_in_thread(task, on_success)

    def _run_watermark(self) -> None:
        path = self.watermark_path.get().strip()
        if not path:
            messagebox.showwarning("Watermark", "Select a PDF file.")
            return

        text = self.watermark_text.get().strip() or "CONFIDENTIAL"
        pdf = Path(path)
        output_path = OUTPUT_DIR / f"watermarked_{pdf.name}"

        def task():
            pages = watermark_pdf(pdf, output_path, text=text)
            return {"pages": pages, "path": output_path, "text": text}

        def on_success(result) -> None:
            self._set_status(f"Watermarked {result['path'].name}")
            messagebox.showinfo(
                "Watermark complete",
                f"Applied \"{result['text']}\" to {result['pages']} page(s).\n"
                f"Saved to: {result['path']}",
            )

        self._run_in_thread(task, on_success)


def run_gui() -> None:
    root = tk.Tk()
    PDFToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
