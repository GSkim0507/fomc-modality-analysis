"""
06_macro_data.py — Download macro series (FRED) and align them to FOMC documents.

Policy (per advisor): MAIN test variables = CFNAI (activity; Kawamura's leading-index analogue)
and VIX (uncertainty). Unemployment gap and core-PCE inflation gap are ROBUSTNESS-ONLY.

Real-time alignment (Kawamura 2019 use a 2-month lag for composite indexes):
  cfnai_lag2 / cfnai_ma3_lag2 : CFNAI (and its 3-month MA) for calendar month m-2 of the document date
  cfnai_ma3_lag1              : alt lag (robustness)
  vix_pre28                   : mean VIXCLS over the 28 calendar days ending the day before the document date
  vix_intermeeting            : mean VIXCLS since the previous scheduled statement (statement docs only)
  unrate_gap_lag1             : UNRATE(m-1) − NROU(quarter, ffilled)      [robustness]
  corepce_gap_lag2            : yoy % of PCEPILFE(m-2) − 2.0              [robustness]
Leads for predictive analysis:
  cfnai_ma3_lead{1,3,6}       : CFNAI_MA3 at m+1, m+3, m+6
  d_cfnai_ma3_3m              : CFNAI_MA3(m+3) − CFNAI_MA3(m-2)
  vix_post28                  : mean VIX over 28 days after the document date
Outputs:
  results/macro_raw/<id>.csv         raw FRED downloads (cached; delete to refresh)
  results/tables/macro_monthly.csv   monthly panel
  results/tables/macro_by_doc.csv    one row per corpus document (all genres)
"""
from __future__ import annotations
import io, sys, time
from pathlib import Path
import pandas as pd, numpy as np, requests
from common import ROOT, TAB, load_docs

RAW = ROOT / "results" / "macro_raw"; RAW.mkdir(parents=True, exist_ok=True)
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
SERIES = ["CFNAI", "CFNAIMA3", "VIXCLS", "UNRATE", "NROU", "PCEPILFE"]

def fetch(sid: str) -> pd.DataFrame:
    f = RAW / f"{sid}.csv"
    if not f.exists():
        r = requests.get(FRED.format(sid=sid), timeout=60,
                         headers={"User-Agent": "Mozilla/5.0 (research script)"})
        r.raise_for_status()
        f.write_bytes(r.content)
        time.sleep(1)
    df = pd.read_csv(f)
    df.columns = ["date", sid]
    df["date"] = pd.to_datetime(df["date"])
    df[sid] = pd.to_numeric(df[sid], errors="coerce")
    return df.dropna()

def main():
    data = {sid: fetch(sid) for sid in SERIES}
    for sid, df in data.items():
        print(f"{sid}: {len(df)} obs {df.date.min().date()} .. {df.date.max().date()}", file=sys.stderr)

    # ---- monthly panel ----
    m = data["CFNAI"].set_index("date").resample("MS").last()
    m["CFNAIMA3"] = data["CFNAIMA3"].set_index("date").resample("MS").last()["CFNAIMA3"]
    if m["CFNAIMA3"].isna().all():
        m["CFNAIMA3"] = m["CFNAI"].rolling(3).mean()
    m["UNRATE"] = data["UNRATE"].set_index("date").resample("MS").last()["UNRATE"]
    nrou = data["NROU"].set_index("date").resample("MS").ffill()["NROU"]
    m["NROU"] = nrou
    m["NROU"] = m["NROU"].ffill()
    pce = data["PCEPILFE"].set_index("date").resample("MS").last()["PCEPILFE"]
    m["COREPCE_YOY"] = pce.pct_change(12) * 100
    vix_d = data["VIXCLS"].set_index("date")["VIXCLS"]
    m["VIX_M"] = vix_d.resample("MS").mean()
    m["UNRATE_GAP"] = m["UNRATE"] - m["NROU"]
    m["COREPCE_GAP"] = m["COREPCE_YOY"] - 2.0
    m = m.loc["2008-01-01":]
    m.to_csv(TAB / "macro_monthly.csv")
    print(f"monthly panel: {len(m)} months", file=sys.stderr)

    # ---- per-document alignment ----
    docs = load_docs(window=False)   # keep 2010+ for robustness
    docs = docs[docs["date"] >= "2010-01-01"].copy()
    dts = pd.to_datetime(docs["date"])
    def month_val(col, dt, lag):
        key = (dt.to_period("M") - lag).to_timestamp()
        return m[col].get(key, np.nan)
    rows = []
    stmt_dates = sorted(pd.to_datetime(docs[docs.doc_type == "statement"]["date"]).unique())
    for (_, d), dt in zip(docs.iterrows(), dts):
        prev_stmt = max([s for s in stmt_dates if s < dt], default=dt - pd.Timedelta(days=42))
        win_pre = vix_d.loc[dt - pd.Timedelta(days=28): dt - pd.Timedelta(days=1)]
        win_post = vix_d.loc[dt + pd.Timedelta(days=1): dt + pd.Timedelta(days=28)]
        win_im = vix_d.loc[prev_stmt: dt - pd.Timedelta(days=1)]
        rows.append(dict(
            doc_id=d.doc_id, doc_type=d.doc_type, date=d.date,
            cfnai_lag2=month_val("CFNAI", dt, 2),
            cfnai_ma3_lag2=month_val("CFNAIMA3", dt, 2),
            cfnai_ma3_lag1=month_val("CFNAIMA3", dt, 1),
            vix_pre28=win_pre.mean(), vix_intermeeting=win_im.mean(),
            unrate_gap_lag1=month_val("UNRATE_GAP", dt, 1),
            corepce_gap_lag2=month_val("COREPCE_GAP", dt, 2),
            cfnai_ma3_lead1=month_val("CFNAIMA3", dt, -1),
            cfnai_ma3_lead3=month_val("CFNAIMA3", dt, -3),
            cfnai_ma3_lead6=month_val("CFNAIMA3", dt, -6),
            vix_post28=win_post.mean(),
        ))
    out = pd.DataFrame(rows)
    out["d_cfnai_ma3_3m"] = out["cfnai_ma3_lead3"] - out["cfnai_ma3_lag2"]
    out["d_vix_28"] = out["vix_post28"] - out["vix_pre28"]
    out.to_csv(TAB / "macro_by_doc.csv", index=False)
    print(f"macro_by_doc: {len(out)} docs; NA cfnai_ma3_lag2={out.cfnai_ma3_lag2.isna().sum()}, "
          f"NA vix_pre28={out.vix_pre28.isna().sum()}, NA lead3={out.cfnai_ma3_lead3.isna().sum()}", file=sys.stderr)
    print(out[out.doc_type=='statement'][["date","cfnai_ma3_lag2","vix_pre28","unrate_gap_lag1","corepce_gap_lag2"]].describe().round(2))

if __name__ == "__main__":
    main()
