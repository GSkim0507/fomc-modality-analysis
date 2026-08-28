"""
Paper A — figure showing the SIGNIFICANT inverse correlation in Statement language.

The headline finding: when the FOMC raises its dot-plot projection (hawkish move),
the accompanying Statement actually uses MORE hedged modals (lower MSI). This is
the 'Hedging as Policy' signature: hawkish moves are linguistically softened to
avoid market overshoot.
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

def main():
    labels = pd.read_csv(ANALYSIS / "dotplot_labels.csv")
    labels = labels[labels["delta_pct"].notna()].copy()
    mi = pd.read_csv(ANALYSIS / "modality_index.csv")
    df = labels.merge(mi[mi["doc_type"] == "statement"],
                      left_on="meeting_date", right_on="date", how="inner")

    x = df["delta_pct"].values
    y = df["msi_avg_modal_strength"].values

    r, p = stats.pearsonr(x, y)
    sl, ic, _, _, _ = stats.linregress(x, y)
    rho, p_sp = stats.spearmanr(x, y)

    # Theil–Sen robust regression (resistant to leverage points)
    ts_sl, ts_ic, ts_lo, ts_hi = stats.theilslopes(y, x, 0.95)

    # Leave-two-out sensitivity: drop the x-min and x-max observations
    order = np.argsort(x)
    keep = np.ones(len(x), dtype=bool)
    keep[order[0]] = False
    keep[order[-1]] = False
    r_l2o, p_l2o = stats.pearsonr(x[keep], y[keep])
    rho_l2o, ps_l2o = stats.spearmanr(x[keep], y[keep])

    colors = df["label"].map({"hawkish":"#d62728","neutral":"#7f7f7f","dovish":"#1f77b4"})

    fig, ax = plt.subplots(figsize=(9, 6.2))
    ax.scatter(x, y, c=colors, s=90, edgecolor="black", linewidth=0.5, alpha=0.85)

    # Mark the two x-extremes that drive sensitivity
    for idx in (order[0], order[-1]):
        ax.scatter(x[idx], y[idx], s=220, facecolors='none',
                   edgecolor='black', linewidth=1.6, linestyle='--', zorder=3)

    xx = np.linspace(x.min() - 0.1, x.max() + 0.1, 50)
    ax.plot(xx, sl * xx + ic, color="#888888", linewidth=1.2, linestyle="--",
            label=f"OLS slope = {sl:+.3f}")
    ax.plot(xx, ts_sl * xx + ts_ic, color="black", linewidth=1.6, linestyle="-",
            label=f"Theil–Sen slope = {ts_sl:+.3f}")
    ax.axhline(y.mean(), color="gray", linewidth=0.4, linestyle=":")
    ax.axvline(0, color="gray", linewidth=0.5)

    ax.set_xlabel("Δ dot-plot median (percentage points)  →  hawkish shift", fontsize=11)
    ax.set_ylabel("Statement MSI: avg modal strength  [0–1]", fontsize=11)
    ax.set_title(
        f"Statement MSI × Δ dot-plot — exploratory, sensitive to x-extremes\n"
        f"Full sample (n={len(df)}):  Pearson r = {r:+.3f} (p = {p:.3f}) ★    "
        f"Spearman ρ = {rho:+.3f} (p = {p_sp:.3f}) ★\n"
        f"Leave-two-out (drop x-min & x-max, n={keep.sum()}):  "
        f"r = {r_l2o:+.3f} (p = {p_l2o:.3f}),  ρ = {rho_l2o:+.3f} (p = {ps_l2o:.3f})    |    "
        f"Theil–Sen 95% CI: [{ts_lo:+.3f}, {ts_hi:+.3f}]",
        fontsize=9.5)

    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#d62728',
               markersize=10, label='hawkish (rate ↑)'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#7f7f7f',
               markersize=10, label='neutral'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#1f77b4',
               markersize=10, label='dovish (rate ↓)'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='none',
               markeredgecolor='black', markersize=12, linestyle='',
               label='leave-two-out points'),
        Line2D([0],[0], color='#888888', linestyle='--', label=f"OLS  ({sl:+.3f})"),
        Line2D([0],[0], color='black', linestyle='-', label=f"Theil–Sen  ({ts_sl:+.3f})"),
    ], fontsize=9, loc="upper right")

    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "16_paperA_inverse_corr.png", dpi=160)
    plt.close(fig)
    print(f"Wrote {FIG / '16_paperA_inverse_corr.png'}")
    print(f"  n = {len(df)}, Pearson r = {r:.3f} (p={p:.4f}), Spearman ρ = {rho:.3f} (p={p_sp:.4f})")
    print(f"  Leave-two-out  : r = {r_l2o:.3f} (p={p_l2o:.4f}), ρ = {rho_l2o:.3f} (p={ps_l2o:.4f})")
    print(f"  Theil–Sen slope = {ts_sl:.4f}  95% CI [{ts_lo:.4f}, {ts_hi:.4f}]")

if __name__ == "__main__":
    main()
