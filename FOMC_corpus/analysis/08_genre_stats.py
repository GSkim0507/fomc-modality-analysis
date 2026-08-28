"""
Paper B — Genre Analysis: formal statistics.

For the 4 FOMC genres (Statement / Minutes / PressConf Transcript / Chair Speech)
we test whether epistemic stance differs significantly.

Tests:
  1. One-way ANOVA over msi_avg_modal_strength ~ doc_type
  2. Welch's ANOVA (heteroscedasticity-safe)
  3. Tukey HSD post-hoc (which pairs differ)
  4. Effect size (eta-squared, omega-squared)
  5. Repeat (1)-(4) within each Chair tenure (Bernanke / Yellen / Powell)
     -> tests robustness of the genre effect across speaker
  6. Chi-square: modal lemma × genre contingency
     -> which modals drive the difference
  7. Friedman-style follow-up: modal_density, signed_msi as secondary DVs

Output:
  analysis/paper_b_stats.txt
  analysis/paper_b_modal_by_genre.csv
  figures/13_paperB_msi_anova.png
  figures/14_paperB_chair_strat.png
  figures/15_paperB_modal_share_by_genre.png
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"

GENRE_ORDER = ["statement", "minutes", "press_conf_transcript", "speech"]
GENRE_LABEL = {
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

def eta_squared(groups: list[np.ndarray]) -> float:
    grand = np.concatenate(groups)
    ss_between = sum(len(g) * (g.mean() - grand.mean()) ** 2 for g in groups)
    ss_total = ((grand - grand.mean()) ** 2).sum()
    return ss_between / ss_total if ss_total > 0 else 0.0

def omega_squared(groups: list[np.ndarray]) -> float:
    """Hays' omega-squared, less biased than eta-squared for small samples."""
    grand = np.concatenate(groups)
    k = len(groups); N = len(grand)
    ss_between = sum(len(g) * (g.mean() - grand.mean()) ** 2 for g in groups)
    ss_within = sum(((g - g.mean()) ** 2).sum() for g in groups)
    ms_within = ss_within / (N - k) if N > k else np.nan
    num = ss_between - (k - 1) * ms_within
    den = ss_between + ss_within + ms_within
    return num / den if den > 0 else np.nan

def tukey_hsd(groups: dict[str, np.ndarray]) -> list[dict]:
    """Manual Tukey HSD using studentized range distribution."""
    names = list(groups.keys())
    arrs = [groups[n] for n in names]
    ns = [len(a) for a in arrs]
    means = [a.mean() for a in arrs]
    grand_n = sum(ns); k = len(arrs)
    ss_within = sum(((a - a.mean()) ** 2).sum() for a in arrs)
    df = grand_n - k
    ms_within = ss_within / df
    se = np.sqrt(ms_within)
    rows = []
    for i in range(k):
        for j in range(i + 1, k):
            diff = means[i] - means[j]
            # harmonic mean of group sizes
            n_h = 2 / (1 / ns[i] + 1 / ns[j])
            q = abs(diff) / (se / np.sqrt(n_h))
            # p-value from studentized range
            p = 1.0 - stats.studentized_range.cdf(q, k, df)
            rows.append({
                "pair": f"{names[i]} vs {names[j]}",
                "mean_diff": round(diff, 4),
                "q_stat": round(q, 3),
                "p_value": round(p, 5),
                "significant_05": p < 0.05,
            })
    return rows

def run_anova(label: str, df: pd.DataFrame, dv: str, lines: list[str]):
    groups = {g: df[df["doc_type"] == g][dv].values
              for g in GENRE_ORDER if (df["doc_type"] == g).any()}
    arrs = list(groups.values())
    if len(arrs) < 2 or any(len(a) < 2 for a in arrs):
        lines.append(f"  [{label}/{dv}] insufficient sample")
        return
    # Standard one-way ANOVA
    F, p = stats.f_oneway(*arrs)
    # Welch's ANOVA (more robust if variances differ)
    try:
        F_w, p_w = stats.alexandergovern(*arrs).statistic, stats.alexandergovern(*arrs).pvalue
    except Exception:
        F_w, p_w = np.nan, np.nan
    eta = eta_squared(arrs)
    om = omega_squared(arrs)
    lines.append(f"\n  [{label}] DV = {dv}")
    lines.append(f"    n by genre: {{{', '.join(f'{k}={len(v)}' for k,v in groups.items())}}}")
    lines.append(f"    one-way ANOVA  F={F:.3f}  p={p:.3e}")
    lines.append(f"    Welch (Alexander-Govern)  F={F_w:.3f}  p={p_w:.3e}")
    lines.append(f"    eta-squared = {eta:.3f}    omega-squared = {om:.3f}")
    lines.append("    Tukey HSD pairwise:")
    for row in tukey_hsd(groups):
        sig = " ★" if row["significant_05"] else ""
        lines.append(f"      {row['pair']:<45} Δ={row['mean_diff']:+.3f}  q={row['q_stat']:.2f}  p={row['p_value']:.4f}{sig}")

def fig_msi_anova(df: pd.DataFrame, anova_summary: str):
    fig, ax = plt.subplots(figsize=(9, 6))
    data = [df[df["doc_type"] == g]["msi_avg_modal_strength"].values for g in GENRE_ORDER]
    bp = ax.boxplot(data, tick_labels=[GENRE_LABEL[g] for g in GENRE_ORDER],
                    patch_artist=True, showmeans=True, meanline=True,
                    meanprops={"color": "black", "linewidth": 1.5, "linestyle": "--"})
    for patch, g in zip(bp["boxes"], GENRE_ORDER):
        patch.set_facecolor(PALETTE[g]); patch.set_alpha(0.7)
    ax.set_ylabel("Modality Strength Index  (avg modal certainty, 0–1)")
    ax.set_title(f"Epistemic Stance Across FOMC Genres\n{anova_summary}")
    ax.grid(axis="y", alpha=0.3)
    # Annotate means
    for i, g in enumerate(GENRE_ORDER, start=1):
        vals = df[df["doc_type"] == g]["msi_avg_modal_strength"]
        ax.text(i, vals.max() + 0.02, f"M={vals.mean():.3f}\nn={len(vals)}",
                ha="center", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "13_paperB_msi_anova.png", dpi=150); plt.close(fig)

def fig_chair_stratified(df: pd.DataFrame):
    chairs = ["Bernanke", "Yellen", "Powell"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax, chair in zip(axes, chairs):
        sub = df[df["chair"] == chair]
        if sub.empty:
            ax.set_title(f"{chair}\n(no data)"); continue
        data = [sub[sub["doc_type"] == g]["msi_avg_modal_strength"].values
                for g in GENRE_ORDER]
        bp = ax.boxplot(data, tick_labels=[GENRE_LABEL[g][:8] for g in GENRE_ORDER],
                        patch_artist=True)
        for patch, g in zip(bp["boxes"], GENRE_ORDER):
            patch.set_facecolor(PALETTE[g]); patch.set_alpha(0.7)
        arrs = [a for a in data if len(a) >= 2]
        if len(arrs) >= 2:
            F, p = stats.f_oneway(*arrs)
            ax.set_title(f"{chair}  (n={len(sub)})\nANOVA F={F:.2f}, p={p:.1e}")
        else:
            ax.set_title(f"{chair}  (n={len(sub)})")
        ax.tick_params(axis="x", rotation=15)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("MSI")
    fig.suptitle("Genre × MSI within each Chair tenure", y=1.02)
    fig.tight_layout(); fig.savefig(FIG / "14_paperB_chair_strat.png", dpi=150); plt.close(fig)

def chi_square_modal_genre(pos_summary: pd.DataFrame, lines: list[str]):
    """Contingency: modal lemma × doc_type, chi-square test."""
    modal_cols = [c for c in pos_summary.columns
                  if c.startswith("mod_") and c not in {"mod_’s", "mod_’d", "mod_’ll"}]
    # Keep only legitimate modals (top 7)
    keep = ["mod_will","mod_would","mod_could","mod_can",
            "mod_may","mod_might","mod_should","mod_must","mod_shall"]
    modal_cols = [c for c in keep if c in pos_summary.columns]
    table = pos_summary.groupby("doc_type")[modal_cols].sum().reindex(GENRE_ORDER)
    table.to_csv(ANALYSIS / "paper_b_modal_by_genre.csv")
    chi2, p, dof, expected = stats.chi2_contingency(table.values)
    lines.append(f"\n  Chi-square: modal lemma × genre  (table {table.shape})")
    lines.append(f"    chi2 = {chi2:.2f}   df = {dof}   p = {p:.3e}")
    # Cramer's V
    n = table.values.sum()
    cramers_v = np.sqrt(chi2 / (n * (min(table.shape) - 1)))
    lines.append(f"    Cramer's V = {cramers_v:.3f}  (effect size)")
    # Standardized residuals (>|2| = notable cell)
    resid = (table.values - expected) / np.sqrt(expected)
    lines.append("    standardized residuals (|>2| are notable):")
    res_df = pd.DataFrame(resid, index=table.index, columns=table.columns)
    for g in res_df.index:
        notable = [(c.replace("mod_",""), v) for c, v in res_df.loc[g].items() if abs(v) > 2]
        if notable:
            joined = ", ".join(f"{c}({v:+.1f})" for c, v in notable)
            lines.append(f"      {g}: {joined}")
    return table

def fig_modal_share_by_genre(table: pd.DataFrame):
    share = table.div(table.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bottom = np.zeros(len(share.index))
    cmap = plt.get_cmap("tab10")
    for i, col in enumerate(share.columns):
        ax.bar(range(len(share)), share[col].values, bottom=bottom,
               label=col.replace("mod_",""), color=cmap(i))
        bottom += share[col].values
    ax.set_xticks(range(len(share)))
    ax.set_xticklabels([GENRE_LABEL[g] for g in share.index])
    ax.set_ylabel("share of modal verb")
    ax.set_title("Modal Verb Composition by Genre")
    ax.legend(loc="lower right", ncol=3)
    fig.tight_layout(); fig.savefig(FIG / "15_paperB_modal_share_by_genre.png", dpi=150); plt.close(fig)

def main():
    mi = pd.read_csv(ANALYSIS / "modality_index.csv")
    ps = pd.read_csv(ANALYSIS / "pos_summary.csv")
    lines = ["=== Paper B — Genre Analysis: Inferential Statistics ==="]

    lines.append(f"\nTotal docs: {len(mi)}   genres: {sorted(mi['doc_type'].unique())}")

    # 1. ANOVA on three DVs
    for dv in ["msi_avg_modal_strength", "msi_modal_density",
               "msi_signed_per_1000", "msi_epistemic_density"]:
        run_anova("OVERALL", mi, dv, lines)

    # 2. Chair-stratified
    for chair in sorted(mi["chair"].dropna().unique()):
        sub = mi[mi["chair"] == chair]
        if len(sub) < 4: continue
        run_anova(f"CHAIR={chair}", sub, "msi_avg_modal_strength", lines)

    # 3. Chi-square: modal × genre
    table = chi_square_modal_genre(ps, lines)

    # Figures
    F, p = stats.f_oneway(*[mi[mi["doc_type"] == g]["msi_avg_modal_strength"].values
                            for g in GENRE_ORDER])
    fig_msi_anova(mi, f"one-way ANOVA  F={F:.2f},  p={p:.2e}")
    fig_chair_stratified(mi)
    fig_modal_share_by_genre(table)

    out = ANALYSIS / "paper_b_stats.txt"
    out.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {out}")
    print(f"Figures: 13_paperB_msi_anova.png  14_paperB_chair_strat.png  15_paperB_modal_share_by_genre.png")

if __name__ == "__main__":
    main()
