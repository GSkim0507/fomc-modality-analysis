"""
Empirically test the claim that Bloomberg side-by-side highlights match
ONLY the linguistically/semantically meaningful subset of automatic diffs.

Procedure for each of the 3 Bloomberg PDFs we have:
  1. Run difflib word-level diff on the corresponding FRB Statement pair.
  2. Extract the highlighted-segment text from the Bloomberg PDF.
     (Highlights are stored either as PDF annotations OR as text drawn over
     a yellow rectangle. We try the simplest route first: extract the text
     spans that appear inside yellow-fill rectangles via PyMuPDF.)
  3. Compare overlap: how many diffed tokens does Bloomberg highlight?
     How many highlighted tokens are NOT in the diff (=false claim)?

Inputs (manually mapped because Bloomberg uses release date vs FRB meeting date):
  20260128 vs 20251210   (Bloomberg PDF: 20260129)
  20260318 vs 20260128   (Bloomberg PDF: 20260319)
  20260429 vs 20260318   (Bloomberg PDF: 20260430)
"""
from __future__ import annotations
import json
import re
import difflib
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
BLOOMBERG_DIR = Path("/Users/gohyeonjeong/Documents/hz/FOMC 블룸버그")
STATEMENTS = ROOT / "statements"

PAIRS = [
    # (bloomberg_pdf_date, current_stmt_date, prior_stmt_date)
    ("20260129", "20260128", "20251210"),
    ("20260319", "20260318", "20260128"),
    ("20260430", "20260429", "20260318"),
]

def load_statement_text(date: str) -> str:
    """Statement text minus the boilerplate header / release-date matter."""
    rec = json.loads((STATEMENTS / f"statement_{date}.json").read_text())
    text = rec["text"]
    # Strip the press-release boilerplate before the substantive paragraph
    m = re.search(r"Information received|Available indicators|Recent indicators|Economic activity", text)
    if m:
        text = text[m.start():]
    # Cut off at voting list (we want the substantive policy text)
    m2 = re.search(r"Voting for the monetary policy action", text)
    if m2:
        text = text[: m2.start()]
    return text.strip()

def tokenize(text: str) -> list[str]:
    # word-level tokens including punctuation
    return re.findall(r"\w+|[^\w\s]", text)

def automatic_diff(curr_text: str, prior_text: str):
    """
    Return added/removed token spans between prior -> curr.
    Uses difflib.SequenceMatcher at word level.
    """
    curr_tokens = tokenize(curr_text)
    prior_tokens = tokenize(prior_text)
    sm = difflib.SequenceMatcher(a=prior_tokens, b=curr_tokens, autojunk=False)
    added, removed = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag in ("delete", "replace"):
            removed.append((i1, i2, " ".join(prior_tokens[i1:i2])))
        if tag in ("insert", "replace"):
            added.append((j1, j2, " ".join(curr_tokens[j1:j2])))
    return curr_tokens, prior_tokens, added, removed

def extract_yellow_highlights(pdf_path: Path):
    """
    Bloomberg side-by-side renders highlights either as:
      (a) PDF /Highlight annotations with quad-points and yellow stroke color
      (b) Yellow filled rectangles with text drawn on top
    We try (a) first; if no annotations exist we extract via (b) by scanning
    drawing operations for yellow-fill rects and collecting overlapping text.
    Returns: list of (page_no, side {'left','right'}, highlighted_text)
    """
    doc = fitz.open(pdf_path)
    highlights = []
    for page_no, page in enumerate(doc):
        page_w = page.rect.width
        # ----- (a) Annotations route -----
        n_annot = 0
        annot = page.first_annot
        while annot is not None:
            if annot.type[0] == 8:  # Highlight
                # Each annot has vertices defining quads; iterate quads
                for q in annot.vertices or []:
                    pass
                # Simpler: pull text inside the annotation rect
                rect = annot.rect
                text = page.get_textbox(rect).strip()
                if text:
                    side = "left" if rect.x0 + rect.width / 2 < page_w / 2 else "right"
                    highlights.append((page_no, side, text))
                    n_annot += 1
            annot = annot.next
        if n_annot > 0:
            continue
        # ----- (b) Yellow rectangle fallback -----
        # Iterate drawing instructions; collect yellow-fill rectangles.
        drawings = page.get_drawings()
        yellow_rects = []
        for d in drawings:
            fill = d.get("fill")
            if fill is None:
                continue
            # PyMuPDF returns sRGB floats; yellow ≈ (1.0, 1.0, 0.0)
            if (abs(fill[0] - 1.0) < 0.15 and abs(fill[1] - 1.0) < 0.15
                    and fill[2] < 0.5):
                for item in d.get("items", []):
                    if item[0] == "re":
                        yellow_rects.append(item[1])
        # Extract text inside each yellow rect
        for rect in yellow_rects:
            text = page.get_textbox(rect).strip()
            if not text:
                continue
            side = "left" if rect.x0 + rect.width / 2 < page_w / 2 else "right"
            highlights.append((page_no, side, text))
    doc.close()
    return highlights

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

def main():
    report = ["=== Empirical test: Bloomberg highlight vs automatic diff ===\n"]

    for bloom_date, curr_date, prior_date in PAIRS:
        report.append(f"\n--- {bloom_date}   ({curr_date}  vs  {prior_date}) ---")
        pdf_path = BLOOMBERG_DIR / f"{bloom_date}Statement_sidebysidecomparison.pdf"
        if not pdf_path.exists():
            report.append(f"  ✗ Bloomberg PDF missing: {pdf_path}")
            continue
        curr_text = load_statement_text(curr_date)
        prior_text = load_statement_text(prior_date)

        # --- Automatic diff ---
        ct, pt, added, removed = automatic_diff(curr_text, prior_text)
        all_diff_phrases = [(s, "added") for _, _, s in added if s.strip()] \
                         + [(s, "removed") for _, _, s in removed if s.strip()]
        diff_phrases_norm = {normalize(p): kind for p, kind in all_diff_phrases}
        report.append(f"  automatic diff produces {len(added)} added + {len(removed)} removed spans")
        # Show first 8 changes for the human reader
        report.append("  sample automatic-diff spans:")
        for s, kind in all_diff_phrases[:8]:
            report.append(f"    [{kind:>7}] {s[:120]}")

        # --- Bloomberg highlights ---
        highlights = extract_yellow_highlights(pdf_path)
        report.append(f"  Bloomberg highlights extracted: {len(highlights)}")
        bloom_phrases_norm = {normalize(h[2]) for h in highlights if h[2].strip()}
        for ph, side, txt in highlights[:8]:
            report.append(f"    [bloom/{side}] {txt[:120]}")

        # --- Comparison ---
        if not highlights:
            report.append("  ⚠  No highlights extracted — likely yellow rendered as flat color,")
            report.append("      not as a /Highlight annotation. Need OCR or screenshot-color route.")
            continue

        # Check (i): how many diff phrases are covered by some highlight?
        covered = 0
        for dp in diff_phrases_norm:
            if any(dp in bh or bh in dp for bh in bloom_phrases_norm):
                covered += 1
        # Check (ii): are there highlights that don't correspond to any diff?
        only_in_bloom = []
        for bh in bloom_phrases_norm:
            if not any(bh in dp or dp in bh for dp in diff_phrases_norm):
                only_in_bloom.append(bh)
        # Check (iii): diff phrases NOT highlighted by Bloomberg
        only_in_diff = []
        for dp in diff_phrases_norm:
            if not any(dp in bh or bh in dp for bh in bloom_phrases_norm):
                only_in_diff.append(dp)

        report.append(f"  → diff phrases covered by ≥1 highlight: {covered}/{len(diff_phrases_norm)}")
        report.append(f"  → diff phrases NOT highlighted: {len(only_in_diff)}")
        for d in only_in_diff[:6]:
            report.append(f"    [not-highlighted] {d[:120]}")
        report.append(f"  → highlights with no diff match: {len(only_in_bloom)}")
        for d in only_in_bloom[:6]:
            report.append(f"    [highlight-only] {d[:120]}")

    out = ANALYSIS / "bloomberg_vs_diff.txt"
    out.write_text("\n".join(report))
    print("\n".join(report))
    print(f"\n→ wrote {out}")

if __name__ == "__main__":
    main()
