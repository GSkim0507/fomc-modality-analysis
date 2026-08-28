"""
16_vader_sentiment.py
---------------------
수업 9강(문서분류·감성분석)에서 다룬 VADER(SentimentIntensityAnalyzer)를
FOMC 코퍼스 535개 문서 전체에 적용한다.

수업 코드 패턴 (직접 인용):
    nltk.download('vader_lexicon')
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    sia.polarity_scores(text)  # -> {'neg', 'neu', 'pos', 'compound'}

+α: 문장 단위 감성을 집계해 문서 단위 평균/표준편차/극성 비율까지 산출.
출력:
    analysis/vader_sentiment.csv         (535 row)
    analysis/vader_vs_msi.txt            (Pearson/Spearman 상관)
    analysis/figures/21_vader_msi_scatter.png
    analysis/figures/22_vader_compound_by_genre.png
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from scipy.stats import f_oneway, pearsonr, spearmanr

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"
FIG.mkdir(exist_ok=True)

for resource in ("vader_lexicon", "punkt", "punkt_tab"):
    try:
        nltk.data.find(f"sentiment/{resource}" if resource == "vader_lexicon" else f"tokenizers/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

sia = SentimentIntensityAnalyzer()

GENRES = {
    "statements": "Statement",
    "minutes": "Minutes",
    "transcripts": "Press Conf",
    "speeches": "Chair Speech",
}


def iter_docs():
    for sub, label in GENRES.items():
        path = ROOT / sub
        if not path.exists():
            continue
        for fn in sorted(os.listdir(path)):
            if not fn.endswith(".json"):
                continue
            try:
                with open(path / fn, encoding="utf-8") as f:
                    d = json.load(f)
            except Exception:
                continue
            yield label, d


def score_document(text: str):
    if not text:
        return dict(compound=np.nan, pos=np.nan, neu=np.nan, neg=np.nan,
                    n_sent=0, share_pos=np.nan, share_neg=np.nan)
    sents = nltk.sent_tokenize(text)
    if not sents:
        return dict(compound=np.nan, pos=np.nan, neu=np.nan, neg=np.nan,
                    n_sent=0, share_pos=np.nan, share_neg=np.nan)
    scores = [sia.polarity_scores(s) for s in sents]
    comp = np.array([s["compound"] for s in scores])
    pos = np.array([s["pos"] for s in scores])
    neu = np.array([s["neu"] for s in scores])
    neg = np.array([s["neg"] for s in scores])
    share_pos = (comp >= 0.05).mean()
    share_neg = (comp <= -0.05).mean()
    return dict(
        compound=float(comp.mean()),
        pos=float(pos.mean()),
        neu=float(neu.mean()),
        neg=float(neg.mean()),
        n_sent=int(len(sents)),
        share_pos=float(share_pos),
        share_neg=float(share_neg),
    )


def main():
    rows = []
    for genre, d in iter_docs():
        s = score_document(d.get("text", ""))
        rows.append({
            "doc_id": d.get("doc_id"),
            "doc_type": genre,
            "date": d.get("date") or d.get("meeting_date"),
            "chair": d.get("chair"),
            "word_count": d.get("word_count"),
            **s,
        })
    df = pd.DataFrame(rows)
    df.to_csv(ANALYSIS / "vader_sentiment.csv", index=False)
    print(f"saved {len(df)} rows -> vader_sentiment.csv")

    msi = pd.read_csv(ANALYSIS / "modality_index.csv")
    merged = df.merge(msi[["doc_id", "msi_avg_modal_strength",
                           "msi_modal_density", "msi_signed_per_1000"]],
                      on="doc_id", how="inner")
    print(f"merged with MSI: {len(merged)} rows")

    report = []
    report.append("VADER × MSI correlations (n = {})".format(len(merged)))
    report.append("=" * 56)
    for msi_col in ["msi_avg_modal_strength", "msi_modal_density", "msi_signed_per_1000"]:
        for vader_col in ["compound", "share_pos", "share_neg"]:
            sub = merged[[msi_col, vader_col]].dropna()
            r, p_r = pearsonr(sub[msi_col], sub[vader_col])
            rho, p_s = spearmanr(sub[msi_col], sub[vader_col])
            report.append(f"{msi_col:28s} × {vader_col:10s}  "
                          f"Pearson r = {r:+.3f} (p={p_r:.3g})   "
                          f"Spearman ρ = {rho:+.3f} (p={p_s:.3g})")

    report.append("")
    report.append("By genre (mean ± sd of compound):")
    by_genre = merged.groupby("doc_type").agg(
        compound_mean=("compound", "mean"),
        compound_sd=("compound", "std"),
        msi_mean=("msi_avg_modal_strength", "mean"),
        n=("doc_id", "count"),
    )
    report.append(by_genre.round(3).to_string())

    groups = [g["compound"].dropna().values for _, g in merged.groupby("doc_type")]
    F, p = f_oneway(*groups)
    report.append("")
    report.append(f"ANOVA on compound by genre: F = {F:.2f}, p = {p:.3g}")

    with open(ANALYSIS / "vader_vs_msi.txt", "w") as f:
        f.write("\n".join(report))
    print("\n".join(report))

    fig, ax = plt.subplots(figsize=(8, 5.5))
    colors = {"Statement": "#d62728", "Minutes": "#1f77b4",
              "Press Conf": "#2ca02c", "Chair Speech": "#9467bd"}
    for genre, sub in merged.groupby("doc_type"):
        ax.scatter(sub["msi_avg_modal_strength"], sub["compound"],
                   s=22, alpha=0.55, label=f"{genre} (n={len(sub)})",
                   color=colors.get(genre, "#666"))
    sub = merged.dropna(subset=["msi_avg_modal_strength", "compound"])
    r, p_r = pearsonr(sub["msi_avg_modal_strength"], sub["compound"])
    z = np.polyfit(sub["msi_avg_modal_strength"], sub["compound"], 1)
    xs = np.linspace(sub["msi_avg_modal_strength"].min(),
                     sub["msi_avg_modal_strength"].max(), 100)
    ax.plot(xs, np.polyval(z, xs), "k--", alpha=0.6,
            label=f"OLS fit (r = {r:+.3f}, p = {p_r:.3g})")
    ax.set_xlabel("MSI — avg modal strength (epistemic certainty 0–1)")
    ax.set_ylabel("VADER compound (mean over sentences)")
    ax.set_title("Modality strength × Sentiment tone — 535 FOMC documents")
    ax.axhline(0, color="grey", lw=0.6)
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "21_vader_msi_scatter.png", dpi=160)
    plt.close(fig)
    print(f"saved -> figures/21_vader_msi_scatter.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    order = ["Statement", "Minutes", "Press Conf", "Chair Speech"]
    data = [merged.loc[merged["doc_type"] == g, "compound"].dropna() for g in order]
    bp = ax.boxplot(data, labels=order, patch_artist=True, showmeans=True)
    for patch, g in zip(bp["boxes"], order):
        patch.set_facecolor(colors.get(g, "#ccc"))
        patch.set_alpha(0.7)
    ax.set_ylabel("VADER compound (per-sentence mean)")
    ax.set_title(f"Sentiment tone by FOMC genre   |   ANOVA F={F:.1f}, p={p:.2g}")
    ax.axhline(0, color="grey", lw=0.6)
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "22_vader_compound_by_genre.png", dpi=160)
    plt.close(fig)
    print(f"saved -> figures/22_vader_compound_by_genre.png")


if __name__ == "__main__":
    main()
