"""
03_timeseries.py — Experiment B: time-series properties of the six modals, 2014–2026.

Per document (meeting/speech): raw count, per-1k-token density, share among the six modals.
Tests: Mann–Kendall trend + Sen's slope (per modal × genre), PELT change points (statements),
AR(1) persistence half-life, quasi-modal substitutes (statements).
Outputs:
  B1_modal_doc_series.csv         per-document counts/density/share
  B2_modal_year_genre.csv         yearly density and share by genre
  B3_trend_tests.csv              Mann–Kendall, Sen slope per modal × genre × metric
  B4_changepoints_statement.csv   PELT change points on statement share/density series
  B5_persistence.csv              AR(1) rho and half-life per modal (statements, meeting-level)
  B6_quasimodals_statement.csv    be going to / expected to / likely to / need to / have to / intend to per statement
Figures: B_fig1_density_by_genre.png, B_fig2_statement_share_changepoints.png, B_fig3_statement_counts.png
"""
from __future__ import annotations
import numpy as np, pandas as pd, json, re
import pymannkendall as mk
import ruptures as rpt
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

def doc_series(df, docs):
    ct = pd.crosstab(df["doc_id"], df["modal"]).reindex(columns=SIX, fill_value=0)
    out = docs.set_index("doc_id")[["doc_type", "date", "chair", "n_tokens", "year"]].join(ct, how="left").fillna(0)
    for m in SIX:
        out[f"{m}_per1k"] = 1000 * out[m] / out["n_tokens"].clip(lower=1)
    tot = out[SIX].sum(axis=1)
    for m in SIX:
        out[f"{m}_share"] = np.where(tot > 0, out[m] / tot.clip(lower=1), np.nan)
    out["six_total"] = tot
    out["six_per1k"] = 1000 * tot / out["n_tokens"].clip(lower=1)
    return out.reset_index().sort_values("date")

def trend_tests(ds):
    rows = []
    for g in GENRES:
        sub = ds[ds.doc_type == g].sort_values("date")
        if g == "speech":  # speeches are irregular; aggregate to quarterly means
            sub = sub.assign(q=pd.PeriodIndex(sub["date"], freq="Q")).groupby("q").mean(numeric_only=True).reset_index()
        for m in SIX:
            for metric in ["per1k", "share"]:
                x = sub[f"{m}_{metric}"].dropna().values
                if len(x) < 8: continue
                r = mk.original_test(x)
                rows.append(dict(genre=g, modal=m, metric=metric, n=len(x), trend=r.trend, p=round(r.p, 4),
                                 tau=round(r.Tau, 3), sen_slope_per_obs=round(r.slope, 5),
                                 mean_2014_16=round(np.mean(x[:max(1, len(x)//4)]), 3),
                                 mean_last_quarter=round(np.mean(x[-max(1, len(x)//4):]), 3)))
    return pd.DataFrame(rows)

def changepoints(ds, pen_scale=2.0, min_size=4):
    st = ds[ds.doc_type == "statement"].sort_values("date").reset_index(drop=True)
    dates = st["date"].tolist()
    rows = []
    for m in SIX:
        for metric in ["share", "per1k", ""]:
            col = f"{m}_{metric}" if metric else m
            x = st[col].fillna(0).values.astype(float)
            if x.std() == 0: continue
            z = (x - x.mean()) / x.std()
            algo = rpt.Pelt(model="l2", min_size=min_size, jump=1).fit(z)
            pen = pen_scale * np.log(len(z))
            bk = algo.predict(pen=pen)
            segs = [0] + bk
            for i in range(1, len(segs) - 1):
                cp = segs[i]
                before = x[segs[i-1]:cp]; after = x[cp:segs[i+1]]
                rows.append(dict(modal=m, metric=metric or "count", cp_index=cp, cp_date=dates[cp],
                                 prev_date=dates[cp-1], mean_before=round(before.mean(), 3),
                                 mean_after=round(after.mean(), 3), n_before=len(before), n_after=len(after)))
    return pd.DataFrame(rows), st

def persistence(st):
    rows = []
    for m in SIX:
        for metric in ["share", "per1k"]:
            x = st[f"{m}_{metric}"].fillna(0).values
            if x.std() == 0: continue
            rho = np.corrcoef(x[:-1], x[1:])[0, 1]
            hl = np.log(0.5) / np.log(abs(rho)) if 0 < abs(rho) < 1 else np.nan
            rows.append(dict(modal=m, metric=metric, ar1_rho=round(rho, 3), half_life_meetings=round(hl, 2) if not np.isnan(hl) else np.nan))
    return pd.DataFrame(rows)

def quasimodals():
    sents = pd.read_csv(TAB / "corpus_sentences.csv")
    st = sents[(sents.doc_type == "statement") & (sents.date >= START)]
    pats = {"be_going_to": r"\b(?:is|are|am|was|were|be|'s|'re)\s+going to\b",
            "be_expected_to": r"\b(?:is|are|was|were|be)\s+expected to\b",
            "be_likely_to": r"\b(?:is|are|was|were|be)\s+likely to\b",
            "need_to": r"\bneeds? to\b", "have_to": r"\b(?:has|have|had) to\b",
            "intend_to": r"\bintends? to\b", "be_prepared_to": r"\b(?:is|are|be)\s+prepared to\b",
            "expect(s)": r"\b(?:expects?|anticipates?)\b", "judge(s)": r"\bjudges?\b",
            "remain(s)": r"\bremains?\b"}
    rows = []
    for doc_id, sub in st.groupby("doc_id"):
        text = " ".join(sub["text"].tolist())
        r = dict(doc_id=doc_id, date=sub["date"].iloc[0])
        for k, p in pats.items():
            r[k] = len(re.findall(p, text, flags=re.I))
        rows.append(r)
    return pd.DataFrame(rows).sort_values("date")

def main():
    df = load_modals(); docs = load_docs()
    ds = doc_series(df, docs); ds.to_csv(TAB / "B1_modal_doc_series.csv", index=False)

    # yearly by genre
    yr = ds.groupby(["doc_type", "year"]).agg(n_docs=("doc_id", "count"), n_tokens=("n_tokens", "sum"),
                                              **{m: (m, "sum") for m in SIX}).reset_index()
    for m in SIX:
        yr[f"{m}_per1k"] = 1000 * yr[m] / yr["n_tokens"]
        yr[f"{m}_share"] = yr[m] / yr[SIX].sum(axis=1)
    yr.to_csv(TAB / "B2_modal_year_genre.csv", index=False)

    tt = trend_tests(ds); tt.to_csv(TAB / "B3_trend_tests.csv", index=False)
    cps, st = changepoints(ds); cps.to_csv(TAB / "B4_changepoints_statement.csv", index=False)
    pers = persistence(st); pers.to_csv(TAB / "B5_persistence.csv", index=False)
    qm = quasimodals(); qm.to_csv(TAB / "B6_quasimodals_statement.csv", index=False)

    # ---- Fig1: yearly density by genre (2x2), six lines each
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True)
    for ax, g in zip(axes.flat, GENRES):
        sub = yr[yr.doc_type == g]
        for m in SIX:
            ax.plot(sub["year"], sub[f"{m}_per1k"], marker="o", ms=3, label=m)
        ax.set_title(GENRE_LABEL[g]); ax.grid(alpha=.3); ax.set_ylabel("per 1,000 tokens")
    axes[0, 0].legend(ncol=3, fontsize=8)
    fig.suptitle("Density of the six modals by year and genre, 2014–2026")
    fig.tight_layout(); fig.savefig(FIG / "B_fig1_density_by_genre.png", dpi=160); plt.close(fig)

    # ---- Fig2: statement share per meeting with change points and events
    fig, axes = plt.subplots(3, 2, figsize=(14, 10), sharex=True)
    x = pd.to_datetime(st["date"])
    for ax, m in zip(axes.flat, SIX):
        ax.plot(x, st[f"{m}_share"] * 100, marker="o", ms=3, color="#4c72b0", label="share (%)")
        ax2 = ax.twinx(); ax2.plot(x, st[m], color="#dd8452", alpha=.6, lw=1, label="count"); ax2.set_ylabel("count", color="#dd8452")
        for _, r in cps[(cps.modal == m) & (cps.metric == "share")].iterrows():
            ax.axvline(pd.to_datetime(r.cp_date), color="red", ls="--", lw=1)
        for d, lab in EVENTS:
            ax.axvline(pd.to_datetime(d), color="grey", ls=":", lw=.8)
        ax.set_title(f"{m} — share of six modals in each statement (red dashed = PELT change point)")
        ax.set_ylabel("share (%)"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(FIG / "B_fig2_statement_share_changepoints.png", dpi=160); plt.close(fig)

    # ---- Fig3: statement counts stacked per meeting + length
    fig, ax = plt.subplots(figsize=(14, 5))
    bottom = np.zeros(len(st))
    for m in SIX:
        ax.bar(x, st[m], bottom=bottom, label=m, width=20); bottom += st[m].values
    ax.set_ylim(0, st[SIX].sum(axis=1).max() * 1.18)
    ax2 = ax.twinx(); ax2.plot(x, st["n_tokens"], color="black", lw=1, label="statement length (tokens)"); ax2.set_ylabel("tokens")
    for d, lab in EVENTS:
        ax.axvline(pd.to_datetime(d), color="grey", ls=":", lw=.8); ax.text(pd.to_datetime(d), ax.get_ylim()[1]*0.98, lab, rotation=90, fontsize=7, va="top")
    ax.legend(ncol=6, fontsize=8, loc="upper left"); ax.set_ylabel("modal tokens per statement")
    ax.set_title("Modal-verb counts per FOMC statement (stacked) and statement length, 2014–2026")
    fig.tight_layout(); fig.savefig(FIG / "B_fig3_statement_counts.png", dpi=160); plt.close(fig)

    print("Trend tests (statements):"); print(tt[tt.genre == "statement"].to_string(index=False))
    print("\nChange points (statement share):"); print(cps[cps.metric == "share"].to_string(index=False))
    print("\nPersistence:"); print(pers.to_string(index=False))
    print("\nYearly statement shares (%):")
    print((yr[yr.doc_type == "statement"].set_index("year")[[f"{m}_share" for m in SIX]] * 100).round(1).to_string())

if __name__ == "__main__":
    main()
