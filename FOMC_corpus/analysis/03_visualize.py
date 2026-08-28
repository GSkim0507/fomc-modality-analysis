"""
Sanity-check + analytic visualizations from pos_summary.csv and modality_index.csv.

Generates:
  figures/01_doc_counts_by_year_type.png   corpus shape sanity check
  figures/02_word_counts_by_type.png       per-doc word distribution
  figures/03_modal_top10.png               top-10 modal verb lemmas
  figures/04_modal_freq_by_year.png        modal verbs per 1000 tokens, by year & type
  figures/05_msi_by_type_box.png           Modality Strength Index distribution by doc_type
  figures/06_msi_time_series.png           MSI over time, faceted by doc_type
  figures/07_modal_share_stacked.png       share of each modal lemma by year (statements)
"""
from __future__ import annotations
import csv
from collections import defaultdict, Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"
FIG.mkdir(parents=True, exist_ok=True)

DOC_TYPE_ORDER = ["statement", "minutes", "press_conf_transcript", "speech"]
DOC_TYPE_LABEL = {
    "statement": "Statement",
    "minutes": "Minutes",
    "press_conf_transcript": "Press Conf Transcript",
    "speech": "Chair Speech",
}
PALETTE = {
    "statement": "#1f77b4",
    "minutes": "#ff7f0e",
    "press_conf_transcript": "#2ca02c",
    "speech": "#d62728",
}

def load_csv(p: Path) -> list[dict]:
    with p.open() as f:
        return list(csv.DictReader(f))

def fnum(x):
    try: return float(x)
    except: return 0.0

def fig01_doc_counts(summary):
    by_year_type = defaultdict(lambda: Counter())
    for r in summary:
        y = int(r["date"][:4])
        by_year_type[y][r["doc_type"]] += 1
    years = sorted(by_year_type)
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = [0] * len(years)
    for t in DOC_TYPE_ORDER:
        vals = [by_year_type[y].get(t, 0) for y in years]
        ax.bar(years, vals, bottom=bottom, label=DOC_TYPE_LABEL[t], color=PALETTE[t])
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_title("FOMC Corpus: Document Counts by Year and Type")
    ax.set_xlabel("Year"); ax.set_ylabel("# of documents")
    ax.legend(); ax.set_xticks(years); ax.tick_params(axis="x", rotation=45)
    fig.tight_layout(); fig.savefig(FIG / "01_doc_counts_by_year_type.png", dpi=150); plt.close(fig)

def fig02_word_counts(summary):
    data = defaultdict(list)
    for r in summary:
        data[r["doc_type"]].append(fnum(r["n_tokens"]))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot([data[t] for t in DOC_TYPE_ORDER],
               labels=[DOC_TYPE_LABEL[t] for t in DOC_TYPE_ORDER],
               patch_artist=True)
    for patch, t in zip(ax.artists if hasattr(ax, "artists") else [], DOC_TYPE_ORDER):
        patch.set_facecolor(PALETTE[t])
    ax.set_yscale("log")
    ax.set_title("Tokens per Document (log scale)")
    ax.set_ylabel("tokens")
    fig.tight_layout(); fig.savefig(FIG / "02_word_counts_by_type.png", dpi=150); plt.close(fig)

def fig03_modal_top10(summary):
    cnt = Counter()
    for r in summary:
        for k, v in r.items():
            if k.startswith("mod_"):
                cnt[k[4:]] += int(float(v or 0))
    top = cnt.most_common(10)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh([x[0] for x in top[::-1]], [x[1] for x in top[::-1]], color="#4c72b0")
    ax.set_title("Top-10 Modal Verbs (corpus-wide)")
    ax.set_xlabel("count")
    fig.tight_layout(); fig.savefig(FIG / "03_modal_top10.png", dpi=150); plt.close(fig)

def fig04_modal_freq_year(summary):
    by = defaultdict(lambda: {"tok": 0, "mod": 0})
    for r in summary:
        y = int(r["date"][:4])
        key = (y, r["doc_type"])
        by[key]["tok"] += fnum(r["n_tokens"])
        by[key]["mod"] += fnum(r["modal_count"])
    years = sorted({k[0] for k in by})
    fig, ax = plt.subplots(figsize=(10, 5))
    for t in DOC_TYPE_ORDER:
        ys, vs = [], []
        for y in years:
            d = by.get((y, t))
            if d and d["tok"] > 0:
                ys.append(y); vs.append(1000 * d["mod"] / d["tok"])
        ax.plot(ys, vs, marker="o", label=DOC_TYPE_LABEL[t], color=PALETTE[t])
    ax.set_title("Modal Verbs per 1,000 Tokens by Year")
    ax.set_xlabel("Year"); ax.set_ylabel("modals / 1,000 tokens")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / "04_modal_freq_by_year.png", dpi=150); plt.close(fig)

def fig05_msi_box(msi):
    data = defaultdict(list)
    for r in msi:
        data[r["doc_type"]].append(fnum(r["msi_avg_modal_strength"]))
    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot([data[t] for t in DOC_TYPE_ORDER],
                    labels=[DOC_TYPE_LABEL[t] for t in DOC_TYPE_ORDER],
                    patch_artist=True)
    for patch, t in zip(bp["boxes"], DOC_TYPE_ORDER):
        patch.set_facecolor(PALETTE[t]); patch.set_alpha(0.7)
    ax.set_title("Modality Strength Index (avg modal strength) by Document Type")
    ax.set_ylabel("MSI: avg modal strength  [0=weak, 1=strong commitment]")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / "05_msi_by_type_box.png", dpi=150); plt.close(fig)

def fig06_msi_timeseries(msi):
    fig, axes = plt.subplots(4, 1, figsize=(11, 11), sharex=True)
    for ax, t in zip(axes, DOC_TYPE_ORDER):
        rows = [r for r in msi if r["doc_type"] == t]
        rows.sort(key=lambda r: r["date"])
        xs = [datetime.fromisoformat(r["date"]) for r in rows]
        ys = [fnum(r["msi_signed_per_1000"]) for r in rows]
        ax.plot(xs, ys, marker=".", linestyle="-", color=PALETTE[t], alpha=0.8)
        ax.axhline(0, color="gray", linewidth=0.7)
        ax.set_title(f"{DOC_TYPE_LABEL[t]}  —  Signed MSI per 1,000 tokens (positive = committed/booster, negative = hedged)")
        ax.set_ylabel("signed MSI / 1k tok")
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("Date")
    axes[-1].xaxis.set_major_locator(mdates.YearLocator(2))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.tight_layout(); fig.savefig(FIG / "06_msi_time_series.png", dpi=150); plt.close(fig)

def fig07_modal_share_stmt(summary):
    rows = [r for r in summary if r["doc_type"] == "statement"]
    by_year = defaultdict(lambda: Counter())
    for r in rows:
        y = int(r["date"][:4])
        for k, v in r.items():
            if k.startswith("mod_"):
                by_year[y][k[4:]] += int(float(v or 0))
    years = sorted(by_year)
    # Pick the lemmas to display: top 6 overall
    overall = Counter()
    for y in years:
        overall.update(by_year[y])
    top_lemmas = [k for k, _ in overall.most_common(6)]
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = [0.0] * len(years)
    cmap = plt.get_cmap("tab10")
    for i, lem in enumerate(top_lemmas):
        vals = []
        for y in years:
            total = sum(by_year[y].values())
            vals.append(by_year[y][lem] / total if total else 0)
        ax.bar(years, vals, bottom=bottom, label=lem, color=cmap(i))
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_title("Statements — Share of Each Modal Verb by Year (top 6)")
    ax.set_xlabel("Year"); ax.set_ylabel("share")
    ax.set_xticks(years); ax.tick_params(axis="x", rotation=45)
    ax.legend(loc="lower right", ncol=3)
    fig.tight_layout(); fig.savefig(FIG / "07_modal_share_stacked.png", dpi=150); plt.close(fig)

def main():
    summary = load_csv(ANALYSIS / "pos_summary.csv")
    msi     = load_csv(ANALYSIS / "modality_index.csv")
    print(f"summary rows: {len(summary)}, msi rows: {len(msi)}")
    fig01_doc_counts(summary);          print("  01 done")
    fig02_word_counts(summary);         print("  02 done")
    fig03_modal_top10(summary);         print("  03 done")
    fig04_modal_freq_year(summary);     print("  04 done")
    fig05_msi_box(msi);                 print("  05 done")
    fig06_msi_timeseries(msi);          print("  06 done")
    fig07_modal_share_stmt(summary);    print("  07 done")
    print(f"\nFigures written to {FIG}")

if __name__ == "__main__":
    main()
