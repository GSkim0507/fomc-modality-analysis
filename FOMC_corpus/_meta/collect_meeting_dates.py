"""
Step 1/2: Enumerate FOMC meeting dates 2010-2026 by scraping calendar pages.
Output: _meta/meeting_dates.json — list of {year, meeting_date (decision day, YYYYMMDD), had_presconf (bool)}.
"""
from __future__ import annotations
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parent / "meeting_dates.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (academic research; contact: go8382@gmail.com)"}

MONTHS = {m: i for i, m in enumerate(
    ["January","February","March","April","May","June",
     "July","August","September","October","November","December"], start=1)}

def fetch(url: str) -> str:
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    return ""

def extract_meetings_from_calendar(html: str, year: int) -> list[dict]:
    """
    Parse a calendar page. Look for statement/minutes anchor URLs which embed YYYYMMDD,
    plus presconf URLs. This is more robust than parsing the visual table.
    """
    soup = BeautifulSoup(html, "html.parser")
    dates: dict[str, dict] = {}
    # All anchors that include monetary{YYYYMMDD}a.htm or fomcminutes{YYYYMMDD}.htm
    stmt_re = re.compile(r"monetary(\d{8})a")
    min_re = re.compile(r"fomcminutes(\d{8})")
    pres_re = re.compile(r"fomcpres+conf(\d{8})")  # presconf or pressconf
    for a in soup.find_all("a", href=True):
        href = a["href"]
        for rx, key in ((stmt_re, "has_statement"),
                        (min_re, "has_minutes"),
                        (pres_re, "has_presconf")):
            m = rx.search(href)
            if m:
                d = m.group(1)
                if d.startswith(str(year)):
                    dates.setdefault(d, {"meeting_date": d, "year": year,
                                         "has_statement": False,
                                         "has_minutes": False,
                                         "has_presconf": False})[key] = True
    return sorted(dates.values(), key=lambda x: x["meeting_date"])

def main():
    all_meetings: list[dict] = []
    current_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    print(f"[curr] {current_url}", file=sys.stderr)
    html = fetch(current_url)
    for y in range(2020, 2027):
        ms = extract_meetings_from_calendar(html, y)
        all_meetings.extend(ms)
    # Historical pages for older years (the current page may include some recent years too,
    # so we dedupe by meeting_date)
    for y in range(2010, 2021):
        url = f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm"
        print(f"[hist] {url}", file=sys.stderr)
        try:
            html = fetch(url)
            ms = extract_meetings_from_calendar(html, y)
            all_meetings.extend(ms)
        except Exception as e:
            print(f"  ERROR {y}: {e}", file=sys.stderr)
        time.sleep(0.5)

    # Dedupe by meeting_date, OR flags so a True in any source survives
    merged: dict[str, dict] = {}
    for m in all_meetings:
        d = m["meeting_date"]
        if d not in merged:
            merged[d] = m
        else:
            for k in ("has_statement", "has_minutes", "has_presconf"):
                merged[d][k] = merged[d][k] or m[k]
    out = sorted(merged.values(), key=lambda x: x["meeting_date"])
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\n{len(out)} meetings written to {OUT}", file=sys.stderr)
    # Quick breakdown
    by_year: dict[int, int] = {}
    for m in out:
        by_year[m["year"]] = by_year.get(m["year"], 0) + 1
    for y in sorted(by_year):
        print(f"  {y}: {by_year[y]}", file=sys.stderr)

if __name__ == "__main__":
    main()
