"""
Milestone 3 - Part 1: Load and clean documents.

Loads every .txt and .pdf in documents/, saves a raw copy to documents/raw/,
then writes a cleaned copy to documents/clean/. Chunking happens in a later
step - this script's only job is to produce clean, readable plain text.

Run (with the venv that has pdfplumber), from the project root:
    source .venv-1/bin/activate
    python src/ingest.py
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # project root (this file lives in src/)
DATA_DIR = ROOT / "data"
DOCS_DIR = DATA_DIR / "documents"             # original source files (.txt, .pdf)
RAW_DIR = DATA_DIR / "raw"                     # extracted raw text
CLEAN_DIR = DATA_DIR / "clean"                 # cleaned text

# Smart punctuation -> plain ASCII, so "why" and "why" don't look different
# to the embedding model.
PUNCT_MAP = {
    "‘": "'", "’": "'",   # curly single quotes
    "“": '"', "”": '"',   # curly double quotes
    "–": "-", "—": "-",   # en dash, em dash
    "…": "...",                 # ellipsis
    " ": " ",                   # non-breaking space
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_txt(path: Path) -> str:
    """Read a .txt file. utf-8-sig strips the BOM if one is present."""
    return path.read_text(encoding="utf-8-sig")


def load_pdf(path: Path) -> str:
    """Extract text from a PDF page by page, then clean PDF-specific junk."""
    import pdfplumber  # imported here so .txt-only runs don't need pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(_extract_page(page))
    return _strip_pdf_boilerplate(pages)


def _extract_page(page) -> str:
    """Extract one page, handling two-column layouts.

    pdfplumber reads across the full page width row by row, so a two-column
    page comes out with the left and right columns interleaved line-by-line
    (scrambled prose). When a page has two clear columns - words split between
    the halves and almost none crossing the centerline gutter - we extract each
    column separately and concatenate them. Single-column pages (title pages,
    full-width tables) are extracted whole.

    x_tolerance=1: pdfplumber's default (3) drops spaces in these PDFs, gluing
    words together ("Spacedrepetition"); 1 restores them.
    """
    width, height = page.width, page.height
    center = width / 2
    words = page.extract_words()
    if not words:
        return ""

    crossing = sum(1 for w in words if w["x0"] < center < w["x1"])
    left = sum(1 for w in words if w["x1"] <= center)
    right = sum(1 for w in words if w["x0"] >= center)
    two_column = crossing <= 0.04 * len(words) and left > 0 and right > 0

    if two_column:
        lt = page.within_bbox((0, 0, center, height)).extract_text(x_tolerance=1) or ""
        rt = page.within_bbox((center, 0, width, height)).extract_text(x_tolerance=1) or ""
        return lt + "\n" + rt
    return page.extract_text(x_tolerance=1) or ""


def _strip_pdf_boilerplate(pages: list[str]) -> str:
    """Drop page numbers and lines that repeat across many pages.

    Academic PDFs put the journal name / running header / page number on
    every page. Body text almost never repeats verbatim, so a line that
    shows up on a large share of pages is boilerplate.
    """
    # Count how many pages each (stripped) line appears on.
    line_pages = {}
    for page in pages:
        for line in set(l.strip() for l in page.splitlines() if l.strip()):
            line_pages[line] = line_pages.get(line, 0) + 1

    n_pages = len(pages)
    threshold = max(3, int(0.4 * n_pages))  # repeats on >=40% of pages (min 3)
    boilerplate = {line for line, count in line_pages.items() if count >= threshold}

    kept = []
    for page in pages:
        for line in page.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.isdigit():          # bare page number
                continue
            if stripped in boilerplate:      # repeated header/footer
                continue
            kept.append(line)
    return "\n".join(kept)


# ---------------------------------------------------------------------------
# Cleaning (applied to every document)
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    text = html.unescape(text)              # &amp; -> &, &nbsp; -> space, etc.
    text = re.sub(r"<[^>]+>", " ", text)    # strip any stray HTML tags
    for bad, good in PUNCT_MAP.items():     # normalize smart punctuation
        text = text.replace(bad, good)

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))  # trailing spaces
    text = re.sub(r"[ \t]{2,}", " ", text)  # collapse runs of spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse 3+ blank lines -> 1
    return text.strip()


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    RAW_DIR.mkdir(exist_ok=True)
    CLEAN_DIR.mkdir(exist_ok=True)

    sources = sorted(
        p for p in DOCS_DIR.iterdir()
        if p.suffix.lower() in (".txt", ".pdf") and p.is_file()
    )
    if not sources:
        print("No .txt or .pdf files found in documents/")
        return

    summary = []
    for path in sources:
        raw = load_pdf(path) if path.suffix.lower() == ".pdf" else load_txt(path)
        cleaned = clean_text(raw)

        stem = path.stem
        (RAW_DIR / f"{stem}.txt").write_text(raw, encoding="utf-8")
        (CLEAN_DIR / f"{stem}.txt").write_text(cleaned, encoding="utf-8")

        summary.append((path.name, path.suffix.lower().lstrip("."),
                        len(raw), len(cleaned)))

    # --- report -----------------------------------------------------------
    print(f"\nProcessed {len(summary)} documents "
          f"-> raw in {RAW_DIR}/, cleaned in {CLEAN_DIR}/\n")
    print(f"{'file':45} {'type':5} {'raw chars':>10} {'clean chars':>12}")
    print("-" * 76)
    for name, kind, raw_len, clean_len in summary:
        print(f"{name[:44]:45} {kind:5} {raw_len:>10,} {clean_len:>12,}")

    # Print one cleaned doc so you can actually read it (milestone requirement).
    preview = sorted(CLEAN_DIR.glob("*.txt"))[0]
    text = preview.read_text(encoding="utf-8")
    print(f"\n--- PREVIEW of cleaned '{preview.name}' (first 1500 chars) ---\n")
    print(text[:1500])
    print(f"\n--- end preview --- (open documents/clean/ to read any doc in full)")


if __name__ == "__main__":
    main()
