"""
Collect FRB Summary of Economic Projections (SEP) projection-table PDFs and parse
the median federal funds rate projection.

SEPs are released at quarterly FOMC meetings (Mar / Jun / Sep / Dec) since 2012.
URL pattern: /monetarypolicy/files/fomcprojtabl{YYYYMMDD}.pdf

For each SEP we extract:
  median federal funds rate for {YYYY, YYYY+1, YYYY+2, longer_run}
where YYYY is the meeting year (table column structure is stable).

Output:
  sep_pdfs/fomcprojtabl{YYYYMMDD}.pdf
  analysis/frb_sep_medians.csv   (compatible columns with analysis/dotplot_medians.csv)
"""
from __future__ import annotations
import csv
import json
import re
import sys
import time
from pathlib import Path

import requests
import fitz

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
PDF_DIR = ROOT / "sep_pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (academic research; go8382@gmail.com)"}
BASE = "https://www.federalreserve.gov"

QUARTERLY_MONTHS = {3, 6, 9, 12}

NUM_RE = re.compile(r"^-?\d+\.\d+$")           # single number (median value)
RANGE_RE = re.compile(r"^[\d.]+\s*[–-]\s*[\d.]+$")  # range like "3.9–4.4"

def fetch_pdf(url: str, dest: Path) -> bool:
    """Download PDF if not already present. Returns True iff file exists after call."""
    if dest.exists() and dest.stat().st_size > 5000:
        return True
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=45, stream=True)
            if r.status_code == 404:
                return False
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return True
        except Exception as e:
            if attempt == 2:
                print(f"    FETCH FAIL {url}: {e}", file=sys.stderr)
                return False
            time.sleep(1.5 * (attempt + 1))
    return False

def parse_sep_pdf(pdf_path: Path, meeting_date: str) -> list[dict]:
    """
    Parse the median federal funds rate from a SEP projection-table PDF.

    Robust strategy: after locating the literal line 'Federal funds rate', take the
    FIRST 3 single-decimal numbers as medians for {Y, Y+1, Y+2}. We intentionally
    skip longer_run because PyMuPDF text extraction sometimes pulls in adjacent
    row values when the table has many year columns.

    Returns empty if it cannot find the row (handled later).
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"    OPEN FAIL {pdf_path.name}: {e}", file=sys.stderr)
        return []

    medians: list[float] = []
    # The "Federal funds rate" anchor may appear in different layouts across years.
    # Strategy: search ALL pages, find each anchor, and collect the FIRST run of
    # >=2 single-decimal numbers that appears within 30 lines after the anchor and
    # before the next text anchor like 'projection' / 'Range' / 'Central'.
    for page in doc:
        text = page.get_text()
        if "Federal funds rate" not in text:
            continue
        lines = [l.strip() for l in text.split("\n")]
        for i, line in enumerate(lines):
            if line != "Federal funds rate":
                continue
            run: list[float] = []
            stop_markers = ("projection", "Range", "Central", "Memo", "Note", "Variable", "tendency")
            for j in range(i + 1, min(i + 30, len(lines))):
                s = lines[j].strip()
                if not s:
                    continue
                if NUM_RE.match(s):
                    run.append(float(s))
                    if len(run) == 3:
                        break
                elif RANGE_RE.match(s):
                    break
                elif any(m in s for m in stop_markers):
                    if run:
                        break
                    # If we hit "December projection" with no medians yet, skip; we'll
                    # look for the next anchor below.
                    run = []
                    break
                else:
                    # Unknown token (column header etc.) — keep scanning
                    continue
            if len(run) >= 2:
                medians = run
                break
        if medians:
            break
    doc.close()

    if not medians:
        return []

    yr = int(meeting_date[:4])
    horizons = [str(yr + k) for k in range(len(medians))]
    iso = f"{meeting_date[:4]}-{meeting_date[4:6]}-{meeting_date[6:8]}"
    rows = []
    for h, v in zip(horizons, medians):
        rows.append({
            "meeting_date": iso,
            "projection_horizon": h,
            "median_pct": v,
            "source_file": pdf_path.name,
            "source_kind": "frb_sep",
            "history_year": "",
        })
    return rows

def main():
    meetings = json.loads((ROOT / "_meta" / "meeting_dates.json").read_text())
    candidates = [m["meeting_date"] for m in meetings
                  if int(m["meeting_date"][4:6]) in QUARTERLY_MONTHS
                  and int(m["meeting_date"][:4]) >= 2012]
    print(f"Quarterly SEP candidates: {len(candidates)}", file=sys.stderr)

    parsed_rows = []
    ok, missing, parse_fail = 0, 0, 0
    for d in candidates:
        url = f"{BASE}/monetarypolicy/files/fomcprojtabl{d}.pdf"
        dest = PDF_DIR / f"fomcprojtabl{d}.pdf"
        got = fetch_pdf(url, dest)
        if not got:
            missing += 1
            print(f"  - {d}  (no PDF)", file=sys.stderr)
            continue
        rows = parse_sep_pdf(dest, d)
        if not rows:
            parse_fail += 1
            print(f"  ? {d}  (parsed 0 rows — investigate {dest.name})", file=sys.stderr)
            continue
        parsed_rows.extend(rows)
        print(f"  + {d}  -> {[(r['projection_horizon'], r['median_pct']) for r in rows]}",
              file=sys.stderr)
        ok += 1
        time.sleep(0.2)

    # Write
    out = ANALYSIS / "frb_sep_medians.csv"
    cols = ["meeting_date", "projection_horizon", "median_pct",
            "source_file", "source_kind", "history_year"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(parsed_rows)

    print(f"\nSEP parsed: {ok}   missing: {missing}   parse_fail: {parse_fail}",
          file=sys.stderr)
    print(f"Wrote {out} ({len(parsed_rows)} rows)", file=sys.stderr)

if __name__ == "__main__":
    main()
