# 📚 Kindle Annotations Transfer
A powerful tool to transfer your Kindle highlights directly into PDF files, making your digital reading experience seamless and organized.

> :memo: **Note:** This project started as a fork of [nsourlos/kindle_to_pdf](https://github.com/nsourlos/kindle_to_pdf).
> It has since diverged significantly to focus on precision and robustness in matching text.
> 
> **Key Differences:**
> - Currently, this project specializes in Kindle highlights (without notes) and is optimized for the Italian language.
> - Implements advanced heuristics (fuzzy matching, sliding windows) instead of relying solely on exact text matches.
> - Automatically calculates page offsets between the Kindle indexing and the actual PDF pagination.
> - Handles overlapping highlights to prevent visual clutter.

---

## 💻 Quick Installation

You can use `venv` to create a local Python virtual environment and `pip` to install the requirements:

### Linux / MacOS

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Windows

Make sure you have set the appropriate ExecutionPolicy environment variable for the `CurrentUser` Scope using the following command, run from a terminal with administrator privileges:

```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

So, run the following commands to create a Python environment in which to install the required files:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

---

## 🚀 Usage

Run the main script passing the path to your PDF and your Kindle `My Clippings.txt` file.

```bash
python apply_kindle_highlights_to_pdf.py "relative/path/to/pdf_file.pdf" "relative/path/to/My_Clippings.txt"
```

> 💡*Tip:* If your `My Clippings.txt` is in the same folder as the script, you can omit the second argument.

```bash
python apply_kindle_highlights_to_pdf.py "relative/path/to/pdf_file.pdf"
```

---

## 🧠 Core Heuristics and Features

This tool doesn't just "find and replace." It employs several intelligent heuristics to ensure highlights are applied accurately, even when the formatting between the Kindle clipping and the PDF text differs.

### 1. Dynamic Page Offset Calculation
Kindle page numbers rarely match PDF page numbers (due to covers, prefaces, or formatting). 
- The script automatically checks the first few highlights to find a reliable anchor point in the PDF.
- It calculates the `offset` (difference between Kindle page X and PDF page Y) and applies this correction to all subsequent highlights, drastically reducing search space and time.

### 2. Fuzzy Searching and Sliding Windows
PDF text extraction is notoriously messy (hyphenation, weird spacing, hidden characters).
- **Text Normalization:** Both the clipping and the PDF text are stripped of special characters, converted to lowercase ASCII, and normalized to ensure clean comparisons.
- **Sliding Windows:** If an exact match fails, the tool divides the PDF page into overlapping "windows" of text.
- **Fuzzy Matching (`rapidfuzz`):** It compares the highlight against these windows, calculating a similarity score. If the score passes a strict threshold, the text is highlighted despite minor typos or formatting glitches.

### 3. Match Validation & Ambiguity Resolution
To prevent highlighting the wrong sentence (e.g., repeating phrases):
- **Lexical Coverage:** Ensures the matched section actually contains the core vocabulary of the highlight.
- **Relative Length & Boundaries:** Checks that the found text isn't significantly shorter or longer than the original clipping, and verifies that the start/end words match.
- **Unambiguous Matching:** If a phrase appears multiple times on the same page, the script evaluates the geometric coordinates (`quads`) to ensure it only highlights the intended instance.

### 4. Overlap Prevention
When multiple highlights are made close to each other on the Kindle, they can merge or overlap on the PDF.
- The script tracks the geometric rectangles (`rects`) of all applied annotations on a page.
- Before applying a new highlight, it checks for intersection (`rects_overlap`). If an overlap is detected, the redundant highlight is safely skipped and logged.

---

## 🛠️ Working Progress

- [x] **Clipping Filtering:** Added `clipping_selector.py` to automatically extract only the clippings related to the specific PDF being processed, saving them in a dedicated `_Clippings.txt` file.
- [x] **Comprehensive Logging:** Generates output files detailing exactly what happened during execution:
  - `[PDF_Name]_annotated.pdf`: The final result.
  - `[PDF_Name]_overlapped.txt`: Highlights that were skipped because they overlapped with existing ones.
  - `[PDF_Name]_notFound.txt`: Highlights that could not be matched even with fuzzy logic.
- [ ] **Improve highlight matches:** At present, around 20–30% of the highlighted sections do not match. Further heuristic rules or a different strategy are required. 
- [ ] **Multi-language Support:** Expand the regex and parsing logic (currently tailored for Italian metadata like "pagina X") to automatically detect and handle English, Spanish, etc.
- [ ] **Note Support:** Extend the parser to capture and inject user notes as PDF comments/pop-ups, not just highlights.
