"""
Merge Bloomberg dot plot medians + FRB SEP medians, then regenerate labels.

Priority for duplicate (meeting_date, horizon) entries:
  1. frb_sep   (authoritative — straight from FRB)
  2. single    (Bloomberg single-meeting dot plot)
  3. history   (Bloomberg history table)

Labels (per meeting):
  hawkish  if Y+1 median rose >= 0.125pp vs the prior labelable meeting
  dovish   if it fell <= -0.125pp
  neutral  otherwise (between -0.125 and +0.125)

Then re-run downstream:
  - update analysis/dotplot_medians.csv  (merged)
  - update analysis/dotplot_labels.csv   (new labels using Y+1 horizon)
"""
from __future__ import annotations
import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"

PRIORITY = {"frb_sep": 3, "single": 2, "history": 1}

def load_csv(p: Path) -> list[dict]:
    if not p.exists(): return []
    with p.open() as f:
        return list(csv.DictReader(f))

def main():
    bloom = load_csv(ANALYSIS / "dotplot_medians.csv")
    sep   = load_csv(ANALYSIS / "frb_sep_medians.csv")
    print(f"Bloomberg medians: {len(bloom)}    FRB SEP medians: {len(sep)}")

    merged: dict[tuple, dict] = {}
    for r in bloom + sep:
        if not r["meeting_date"] or not r["projection_horizon"]:
            continue
        # Normalize horizon
        h = r["projection_horizon"]
        if h.lower().startswith("longer"):
            h = "longer_run"
        key = (r["meeting_date"], h)
        score = PRIORITY.get(r["source_kind"], 0)
        if key not in merged or score > PRIORITY.get(merged[key]["source_kind"], 0):
            r2 = dict(r); r2["projection_horizon"] = h
            try:
                r2["median_pct"] = float(r2["median_pct"])
            except (ValueError, TypeError):
                continue
            merged[key] = r2

    rows = sorted(merged.values(), key=lambda r: (r["meeting_date"], r["projection_horizon"]))

    # Write merged medians
    cols = ["meeting_date","projection_horizon","median_pct","source_file","source_kind","history_year"]
    with (ANALYSIS / "dotplot_medians.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print(f"Merged medians: {len(rows)} rows  (covering {len({r['meeting_date'] for r in rows})} meetings)")

    # Build labels using Y+1 horizon
    meetings = sorted({r["meeting_date"] for r in rows})
    by_key = {(r["meeting_date"], r["projection_horizon"]): r["median_pct"] for r in rows}

    labels = []
    last_labelable = None  # most recent meeting we used to compare from
    for i, m in enumerate(meetings):
        m_yr = int(m[:4])
        # Choose horizon: Y+1 preferred, fall back Y, Y-1
        h_choice = None
        cur_val = None
        for h in (str(m_yr + 1), str(m_yr), str(m_yr + 2), str(m_yr - 1)):
            if (m, h) in by_key:
                h_choice = h
                cur_val = by_key[(m, h)]
                break
        if h_choice is None:
            labels.append({"meeting_date": m, "label": "no_data",
                           "delta_pct": None, "horizon": "", "prior_meeting": ""})
            continue
        if last_labelable is None:
            labels.append({"meeting_date": m, "label": "baseline",
                           "delta_pct": None, "horizon": h_choice, "prior_meeting": ""})
            last_labelable = m
            continue
        # Find matching horizon at the prior meeting; if not present, fall back
        prior_val = None; prior_h = None
        for h in (h_choice, str(int(last_labelable[:4]) + 1), str(int(last_labelable[:4])),
                  str(int(last_labelable[:4]) + 2)):
            if (last_labelable, h) in by_key:
                prior_val = by_key[(last_labelable, h)]; prior_h = h; break
        if prior_val is None:
            labels.append({"meeting_date": m, "label": "no_comparable",
                           "delta_pct": None, "horizon": h_choice,
                           "prior_meeting": last_labelable})
            continue
        delta = cur_val - prior_val
        if delta >= 0.125: lab = "hawkish"
        elif delta <= -0.125: lab = "dovish"
        else: lab = "neutral"
        labels.append({"meeting_date": m, "label": lab,
                       "delta_pct": round(delta, 4),
                       "horizon": h_choice,
                       "prior_meeting": last_labelable})
        last_labelable = m

    with (ANALYSIS / "dotplot_labels.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["meeting_date","label","delta_pct","horizon","prior_meeting"])
        w.writeheader(); w.writerows(labels)

    counts = Counter(l["label"] for l in labels)
    usable = sum(counts.get(k, 0) for k in ("hawkish","dovish","neutral"))
    print(f"Labels written: {len(labels)} meetings")
    print(f"  usable (hawkish/dovish/neutral): {usable}")
    print(f"  class balance: hawkish={counts.get('hawkish',0)}  "
          f"dovish={counts.get('dovish',0)}  neutral={counts.get('neutral',0)}")
    print(f"  baseline: {counts.get('baseline',0)}  no_data: {counts.get('no_data',0)}  "
          f"no_comparable: {counts.get('no_comparable',0)}")

if __name__ == "__main__":
    main()
