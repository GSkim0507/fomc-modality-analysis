"""
Step 2/2: Download FOMC Statements, Minutes, Press Conference Transcripts, Chair Speeches.
Save each as JSON with metadata.

Usage:
    python3 collect_fomc_docs.py [--types statements,minutes,transcripts,speeches]
                                 [--years 2010-2026]
                                 [--limit N]
"""
from __future__ import annotations
import argparse
import io
import json
import re
import sys
import time
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "_meta"
HEADERS = {"User-Agent": "Mozilla/5.0 (academic research; contact: go8382@gmail.com)"}
BASE = "https://www.federalreserve.gov"

# Chair tenure (start date inclusive). Used to label each FOMC doc / filter Chair speeches.
CHAIR_TENURE = [
    (date(2006, 2, 1),  date(2014, 1, 31), "Bernanke"),
    (date(2014, 2, 3),  date(2018, 2, 3),  "Yellen"),
    (date(2018, 2, 5),  date(2030, 1, 1),  "Powell"),
]

def chair_for(d: date) -> str:
    for s, e, name in CHAIR_TENURE:
        if s <= d <= e:
            return name
    return "Unknown"

def ymd(s: str) -> date:
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))

def fetch(url: str, binary: bool = False, retries: int = 3) -> bytes | str | None:
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=45)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.content if binary else r.text
        except Exception as e:
            if attempt == retries - 1:
                print(f"    FETCH FAIL {url}: {e}", file=sys.stderr)
                return None
            time.sleep(1.5 * (attempt + 1))
    return None

def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def html_main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer"]):
        tag.decompose()
    article = (soup.find("div", id="article")
               or soup.find("div", class_="col-xs-12 col-sm-8 col-md-8")
               or soup.find("main")
               or soup.body
               or soup)
    return clean_text(article.get_text("\n"))

def pdf_text(b: bytes) -> str:
    parts = []
    with fitz.open(stream=b, filetype="pdf") as doc:
        for page in doc:
            parts.append(page.get_text())
    return clean_text("\n".join(parts))

def save_json(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))

def already_done(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 200

# ---------- Statements ----------
def collect_statement(meeting: dict, out_dir: Path) -> dict | None:
    d = meeting["meeting_date"]
    fname = out_dir / f"statement_{d}.json"
    if already_done(fname):
        return {"status": "skip", "path": str(fname)}
    # HTML page first; some legacy statements may only exist as PDF
    url_html = f"{BASE}/newsevents/pressreleases/monetary{d}a.htm"
    html = fetch(url_html)
    text, src = None, None
    if html:
        text = html_main_text(html)
        src = url_html
    else:
        url_pdf = f"{BASE}/monetarypolicy/files/monetary{d}a1.pdf"
        b = fetch(url_pdf, binary=True)
        if b:
            text = pdf_text(b)
            src = url_pdf
    if not text:
        return {"status": "missing", "doc_id": f"statement_{d}"}
    dt = ymd(d)
    save_json(fname, {
        "doc_id": f"statement_{d}",
        "doc_type": "statement",
        "date": dt.isoformat(),
        "meeting_date": dt.isoformat(),
        "chair": chair_for(dt),
        "source_url": src,
        "text": text,
        "word_count": len(text.split()),
        "collected_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    })
    return {"status": "ok", "path": str(fname), "words": len(text.split())}

# ---------- Minutes ----------
def collect_minutes(meeting: dict, out_dir: Path) -> dict | None:
    d = meeting["meeting_date"]
    fname = out_dir / f"minutes_{d}.json"
    if already_done(fname):
        return {"status": "skip", "path": str(fname)}
    url_html = f"{BASE}/monetarypolicy/fomcminutes{d}.htm"
    html = fetch(url_html)
    text, src = None, None
    if html:
        text = html_main_text(html)
        src = url_html
    else:
        url_pdf = f"{BASE}/monetarypolicy/files/fomcminutes{d}.pdf"
        b = fetch(url_pdf, binary=True)
        if b:
            text = pdf_text(b)
            src = url_pdf
    if not text:
        return {"status": "missing", "doc_id": f"minutes_{d}"}
    dt = ymd(d)
    save_json(fname, {
        "doc_id": f"minutes_{d}",
        "doc_type": "minutes",
        "date": dt.isoformat(),
        "meeting_date": dt.isoformat(),
        "chair": chair_for(dt),
        "source_url": src,
        "text": text,
        "word_count": len(text.split()),
        "collected_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    })
    return {"status": "ok", "path": str(fname), "words": len(text.split())}

# ---------- Press Conference Transcripts ----------
def collect_transcript(meeting: dict, out_dir: Path) -> dict | None:
    d = meeting["meeting_date"]
    fname = out_dir / f"transcript_{d}.json"
    if already_done(fname):
        return {"status": "skip", "path": str(fname)}
    # Confirmed pattern: /mediacenter/files/FOMCpresconf{YYYYMMDD}.pdf
    candidates = [
        f"{BASE}/mediacenter/files/FOMCpresconf{d}.pdf",
        f"{BASE}/mediacenter/files/fomcpresconf{d}.pdf",
        f"{BASE}/mediacenter/files/FOMCpressconf{d}.pdf",
    ]
    text, src = None, None
    for url in candidates:
        b = fetch(url, binary=True)
        if b:
            text = pdf_text(b)
            src = url
            break
    if not text:
        return {"status": "missing", "doc_id": f"transcript_{d}"}
    dt = ymd(d)
    save_json(fname, {
        "doc_id": f"transcript_{d}",
        "doc_type": "press_conf_transcript",
        "date": dt.isoformat(),
        "meeting_date": dt.isoformat(),
        "chair": chair_for(dt),
        "source_url": src,
        "text": text,
        "word_count": len(text.split()),
        "collected_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    })
    return {"status": "ok", "path": str(fname), "words": len(text.split())}

# ---------- Chair Speeches ----------
SPEECH_LINK_RE = re.compile(r"/newsevents/speech/([a-z]+)(\d{8})([a-z])\.htm", re.I)

def list_chair_speeches(year: int) -> list[dict]:
    """Return [{url, speaker_surname, date, suffix}] for speeches in year by the sitting Chair(s)."""
    url = f"{BASE}/newsevents/speech/{year}-speeches.htm"
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    found = []
    for a in soup.find_all("a", href=True):
        m = SPEECH_LINK_RE.match(a["href"])
        if not m:
            continue
        surname, dstr, suffix = m.group(1).lower(), m.group(2), m.group(3).lower()
        dt = ymd(dstr)
        if chair_for(dt).lower() != surname:
            continue
        found.append({
            "url": BASE + a["href"],
            "speaker_surname": surname.capitalize(),
            "date": dstr,
            "suffix": suffix,
            "title_anchor": (a.get_text() or "").strip()[:200],
        })
    # Dedupe by URL
    seen, uniq = set(), []
    for s in found:
        if s["url"] in seen: continue
        seen.add(s["url"]); uniq.append(s)
    return uniq

def collect_speech(meta: dict, out_dir: Path) -> dict | None:
    d = meta["date"]; suf = meta["suffix"]; surname = meta["speaker_surname"]
    fname = out_dir / f"speech_{surname.lower()}_{d}{suf}.json"
    if already_done(fname):
        return {"status": "skip", "path": str(fname)}
    html = fetch(meta["url"])
    if not html:
        return {"status": "missing", "doc_id": fname.stem}
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.find("h3", class_="title") or soup.find("h1")
             or soup.find("h2") or soup.title)
    title_text = title.get_text(strip=True) if title else meta["title_anchor"]
    text = html_main_text(html)
    dt = ymd(d)
    save_json(fname, {
        "doc_id": fname.stem,
        "doc_type": "speech",
        "date": dt.isoformat(),
        "chair": surname,
        "speaker": surname,
        "title": title_text,
        "source_url": meta["url"],
        "text": text,
        "word_count": len(text.split()),
        "collected_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    })
    return {"status": "ok", "path": str(fname), "words": len(text.split())}

# ---------- Runner ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--types", default="statements,minutes,transcripts,speeches",
                    help="Comma list: statements,minutes,transcripts,speeches")
    ap.add_argument("--years", default="2010-2026", help="Range, e.g. 2010-2026")
    ap.add_argument("--limit", type=int, default=0, help="Per-type limit (smoke test); 0 = no limit")
    ap.add_argument("--sleep", type=float, default=0.4, help="Delay between requests (s)")
    args = ap.parse_args()

    y0, y1 = (int(x) for x in args.years.split("-"))
    wanted_types = set(t.strip() for t in args.types.split(",") if t.strip())

    meetings = json.loads((META / "meeting_dates.json").read_text())
    meetings = [m for m in meetings if y0 <= m["year"] <= y1]
    print(f"Meetings in range {y0}-{y1}: {len(meetings)}", file=sys.stderr)

    summary = {"statements": [], "minutes": [], "transcripts": [], "speeches": []}

    if "statements" in wanted_types:
        out = ROOT / "statements"
        for i, m in enumerate(meetings):
            if args.limit and i >= args.limit: break
            r = collect_statement(m, out)
            summary["statements"].append(r)
            print(f"  S {m['meeting_date']} -> {r.get('status')}", file=sys.stderr)
            time.sleep(args.sleep)

    if "minutes" in wanted_types:
        out = ROOT / "minutes"
        for i, m in enumerate(meetings):
            if args.limit and i >= args.limit: break
            r = collect_minutes(m, out)
            summary["minutes"].append(r)
            print(f"  M {m['meeting_date']} -> {r.get('status')}", file=sys.stderr)
            time.sleep(args.sleep)

    if "transcripts" in wanted_types:
        out = ROOT / "transcripts"
        for i, m in enumerate(meetings):
            if args.limit and i >= args.limit: break
            r = collect_transcript(m, out)
            summary["transcripts"].append(r)
            print(f"  T {m['meeting_date']} -> {r.get('status')}", file=sys.stderr)
            time.sleep(args.sleep)

    if "speeches" in wanted_types:
        out = ROOT / "speeches"
        seen_total = 0
        for y in range(y0, y1 + 1):
            speeches = list_chair_speeches(y)
            print(f"  [speeches {y}] {len(speeches)} by Chair", file=sys.stderr)
            for s in speeches:
                if args.limit and seen_total >= args.limit: break
                r = collect_speech(s, out)
                summary["speeches"].append(r)
                seen_total += 1
                print(f"    SP {s['speaker_surname']} {s['date']}{s['suffix']} -> {r.get('status')}",
                      file=sys.stderr)
                time.sleep(args.sleep)
            time.sleep(args.sleep)

    # Final index
    index = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "years": [y0, y1],
        "counts": {k: {"ok": sum(1 for r in v if r and r.get("status") == "ok"),
                       "skip": sum(1 for r in v if r and r.get("status") == "skip"),
                       "missing": sum(1 for r in v if r and r.get("status") == "missing")}
                   for k, v in summary.items()},
    }
    (META / "collection_index.json").write_text(json.dumps(index, indent=2))
    print("\nDONE\n" + json.dumps(index, indent=2), file=sys.stderr)

if __name__ == "__main__":
    main()
