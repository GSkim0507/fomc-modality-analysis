"""
Correlate the dot-plot median change (delta_pct) with the Modality Strength Index
(MSI signed score) for matching FOMC documents.

For each labeled meeting we have:
  delta_pct from analysis/dotplot_labels.csv
  MSI signed score from analysis/modality_index.csv (Statement, and additionally
  Minutes and Press Conference Transcript on the same date for triangulation)

Outputs:
  analysis/correlations.csv
  figures/12_corr_scatter.png
"""
from __future__ import annotations
from pathlib import Path

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"

DOC_TYPES = ["statement", "minutes", "press_conf_transcript"]

def main():
    labels = pd.read_csv(ANALYSIS / "dotplot_labels.csv")
    mi = pd.read_csv(ANALYSIS / "modality_index.csv")
    labels = labels[labels["delta_pct"].notna()].copy()

    results = []
    fig, axes = plt.subplots(1, len(DOC_TYPES), figsize=(5 * len(DOC_TYPES), 5), sharey=True)

    for ax, dtype in zip(axes, DOC_TYPES):
        sub = mi[mi["doc_type"] == dtype]
        df = labels.merge(sub, left_on="meeting_date", right_on="date", how="inner")
        if df.empty:
            ax.set_title(f"{dtype}\n(no matches)")
            continue
        for target in ["msi_signed_per_1000", "msi_avg_modal_strength",
                       "msi_modal_density", "msi_total_density"]:
            x = df["delta_pct"].values
            y = df[target].values
            if len(x) < 3 or np.std(y) == 0:
                pear = (np.nan, np.nan); spear = (np.nan, np.nan)
            else:
                pear = stats.pearsonr(x, y)
                spear = stats.spearmanr(x, y)
            results.append({
                "doc_type": dtype, "msi_variant": target, "n": len(df),
                "pearson_r": round(pear[0], 3) if not np.isnan(pear[0]) else None,
                "pearson_p": round(pear[1], 4) if not np.isnan(pear[1]) else None,
                "spearman_r": round(spear[0], 3) if not np.isnan(spear[0]) else None,
                "spearman_p": round(spear[1], 4) if not np.isnan(spear[1]) else None,
            })

        # Plot the primary scatter: delta_pct vs msi_signed_per_1000
        x = df["delta_pct"].values
        y = df["msi_signed_per_1000"].values
        colors = df["label"].map({"hawkish":"#d62728","neutral":"#7f7f7f","dovish":"#1f77b4"}).fillna("gray")
        ax.scatter(x, y, c=colors, s=60, edgecolor="black", linewidth=0.4)
        if len(x) >= 3 and np.std(y) > 0:
            r, p = stats.pearsonr(x, y)
            sl, ic, _, _, _ = stats.linregress(x, y)
            xx = np.linspace(x.min(), x.max(), 50)
            ax.plot(xx, sl*xx + ic, color="black", linewidth=1, linestyle="--")
            ax.set_title(f"{dtype}\nn={len(df)}, Pearson r={r:.2f} (p={p:.3f})")
        else:
            ax.set_title(f"{dtype}\nn={len(df)}")
        ax.axhline(0, color="gray", linewidth=0.5)
        ax.axvline(0, color="gray", linewidth=0.5)
        ax.set_xlabel("Δ dot-plot median (pp)")
        if ax is axes[0]:
            ax.set_ylabel("MSI signed / 1k tokens")
        # legend handles
        from matplotlib.lines import Line2D
        ax.legend(handles=[
            Line2D([0],[0], marker='o', color='w', markerfacecolor='#d62728', markersize=8, label='hawkish'),
            Line2D([0],[0], marker='o', color='w', markerfacecolor='#7f7f7f', markersize=8, label='neutral'),
            Line2D([0],[0], marker='o', color='w', markerfacecolor='#1f77b4', markersize=8, label='dovish'),
        ], fontsize=8, loc="best")

    fig.tight_layout()
    fig.savefig(FIG / "12_corr_scatter.png", dpi=150)
    plt.close(fig)

    out = pd.DataFrame(results)
    out.to_csv(ANALYSIS / "correlations.csv", index=False)
    print(out.to_string(index=False))
    print(f"\nfig: {FIG/'12_corr_scatter.png'}")
    print(f"csv: {ANALYSIS/'correlations.csv'}")

if __name__ == "__main__":
    main()
