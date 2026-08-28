"""
Paper A — Loughran-McDonald (2014/2018) dictionary comparison.

For each FOMC document, compute LM-based densities (counts per 1k tokens) for:
  - LM Strong Modal   (19 words)   — committed certainty markers
  - LM Weak Modal     (27 words)   — hedged uncertainty markers
  - LM Uncertainty    (297 words)  — broad uncertainty / hedging vocabulary
  - LM Net Modal Tone = (Strong - Weak) / total tokens * 1000

Then test the same downstream questions as MSI:
  1. Pearson/Spearman correlation between LM features and dot-plot delta_pct
  2. Classification accuracy (LogReg LOOCV) using LM features ONLY

This contrasts our theory-grounded MSI against the de-facto standard finance
sentiment dictionary used in Loughran-McDonald, Hansen & McMahon (2016), etc.

Outputs:
  analysis/lm_features.csv
  analysis/lm_vs_msi.txt
  figures/17_paperA_lm_vs_msi_corr.png
"""
from __future__ import annotations
from pathlib import Path
import re
import json
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"

DOC_TYPES_DIRS = ["statements", "minutes", "transcripts", "speeches"]

TOKEN_RE = re.compile(r"[A-Za-z']+")

def load_lm_lists() -> dict[str, set[str]]:
    df = pd.read_csv(ANALYSIS / "lm_master.csv")
    lists = {}
    for cat in ["Strong_Modal", "Weak_Modal", "Uncertainty"]:
        lists[cat] = set(df[df[cat] > 0]["Word"].str.lower().tolist())
    return lists

def score_doc(text: str, lm: dict[str, set[str]]) -> dict:
    tokens = [t.lower() for t in TOKEN_RE.findall(text)]
    n = len(tokens) or 1
    counts = {cat: 0 for cat in lm}
    for w in tokens:
        for cat, words in lm.items():
            if w in words:
                counts[cat] += 1
    return {
        "lm_strong_modal_n": counts["Strong_Modal"],
        "lm_weak_modal_n":   counts["Weak_Modal"],
        "lm_uncertainty_n":  counts["Uncertainty"],
        "lm_strong_per_1000": round(1000 * counts["Strong_Modal"] / n, 3),
        "lm_weak_per_1000":   round(1000 * counts["Weak_Modal"] / n, 3),
        "lm_uncertainty_per_1000": round(1000 * counts["Uncertainty"] / n, 3),
        "lm_net_modal_per_1000":   round(1000 * (counts["Strong_Modal"]
                                                  - counts["Weak_Modal"]) / n, 3),
        "lm_strong_minus_weak":    counts["Strong_Modal"] - counts["Weak_Modal"],
        "n_tokens": n,
    }

def iter_doc_jsons():
    for sub in DOC_TYPES_DIRS:
        for p in sorted((ROOT / sub).glob("*.json")):
            yield p

def main():
    print("Loading LM lists...")
    lm = load_lm_lists()
    for cat, ws in lm.items():
        print(f"  {cat}: {len(ws)} words")

    print(f"\nScoring corpus with LM dictionary...")
    rows = []
    paths = list(iter_doc_jsons())
    for i, p in enumerate(paths, 1):
        d = json.loads(p.read_text())
        s = score_doc(d["text"], lm)
        s["doc_id"] = d["doc_id"]
        s["doc_type"] = d["doc_type"]
        s["date"] = d["date"]
        s["chair"] = d.get("chair", "")
        rows.append(s)
        if i % 100 == 0:
            print(f"  [{i}/{len(paths)}]")
    feat = pd.DataFrame(rows)
    feat.to_csv(ANALYSIS / "lm_features.csv", index=False)
    print(f"\nwrote lm_features.csv ({len(feat)} rows)")

    # ---- Join with MSI + labels ----
    mi = pd.read_csv(ANALYSIS / "modality_index.csv")
    labels = pd.read_csv(ANALYSIS / "dotplot_labels.csv")
    labels = labels[labels["delta_pct"].notna()].copy()

    out_lines = ["=== Paper A — LM vs MSI comparison ==="]
    out_lines.append(f"\nCorpus tokens covered by LM scoring: {feat['n_tokens'].sum():,}")

    # ---- Genre comparison: LM features by genre ----
    out_lines.append("\n[Genre means — LM features]")
    g = feat.groupby("doc_type")[
        ["lm_strong_per_1000","lm_weak_per_1000",
         "lm_uncertainty_per_1000","lm_net_modal_per_1000"]
    ].mean().round(3)
    out_lines.append(g.to_string())

    # ---- Convergent validity: LM features vs MSI ----
    msi_lm = feat.merge(mi[["doc_id","msi_avg_modal_strength","msi_signed_per_1000",
                            "msi_modal_density","msi_epistemic_density"]],
                        on="doc_id", how="inner")
    out_lines.append("\n[Convergent validity — LM × MSI correlations across all docs]")
    pairs = [("lm_strong_per_1000",  "msi_modal_density"),
             ("lm_strong_per_1000",  "msi_avg_modal_strength"),
             ("lm_weak_per_1000",    "msi_epistemic_density"),
             ("lm_uncertainty_per_1000","msi_epistemic_density"),
             ("lm_net_modal_per_1000","msi_signed_per_1000")]
    for a, b in pairs:
        x, y = msi_lm[a].values, msi_lm[b].values
        r, p = stats.pearsonr(x, y)
        rho, p2 = stats.spearmanr(x, y)
        out_lines.append(f"  {a:<28} × {b:<28}  Pearson r={r:+.3f} (p={p:.3e})  "
                         f"Spearman ρ={rho:+.3f} (p={p2:.3e})")

    # ---- LM × dot plot delta ----
    out_lines.append("\n[LM features × dot-plot Δ — Statement only]")
    df = labels.merge(feat[feat["doc_type"] == "statement"],
                      left_on="meeting_date", right_on="date", how="inner")
    for feat_col in ["lm_strong_per_1000","lm_weak_per_1000",
                     "lm_uncertainty_per_1000","lm_net_modal_per_1000"]:
        x, y = df["delta_pct"].values, df[feat_col].values
        r, p = stats.pearsonr(x, y)
        rho, p2 = stats.spearmanr(x, y)
        star = " ★" if p < 0.05 else ""
        out_lines.append(f"  Δ × {feat_col:<28}  Pearson r={r:+.3f} (p={p:.3f}){star}  "
                         f"Spearman ρ={rho:+.3f} (p={p2:.3f})")

    # ---- Classifier with LM features ONLY ----
    out_lines.append("\n[LM-only classifier — LOOCV, Statement, n=" + str(len(df)) + "]")
    X_lm = df[["lm_strong_per_1000","lm_weak_per_1000",
               "lm_uncertainty_per_1000","lm_net_modal_per_1000"]].values
    y = df["label"].values
    pipe = Pipeline([("sc", StandardScaler()),
                     ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))])
    y_pred = cross_val_predict(pipe, X_lm, y, cv=LeaveOneOut())
    out_lines.append(classification_report(y, y_pred, digits=3, zero_division=0))

    out_lines.append("\n[MSI-only classifier — LOOCV, same docs, for comparison]")
    X_msi = msi_lm.merge(labels, left_on="date", right_on="meeting_date")\
                  [["msi_avg_modal_strength","msi_modal_density",
                    "msi_signed_per_1000","msi_epistemic_density"]].values
    y2 = msi_lm.merge(labels, left_on="date", right_on="meeting_date")["label"].values
    # restrict to statement docs
    statement_mask = (msi_lm.merge(labels, left_on="date", right_on="meeting_date")
                     ["doc_type"] == "statement").values
    X_msi = X_msi[statement_mask]; y2 = y2[statement_mask]
    if len(X_msi) >= 5:
        pipe2 = Pipeline([("sc", StandardScaler()),
                          ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))])
        y2_pred = cross_val_predict(pipe2, X_msi, y2, cv=LeaveOneOut())
        out_lines.append(classification_report(y2, y2_pred, digits=3, zero_division=0))

    # ---- Combined classifier (LM + MSI features) ----
    out_lines.append("\n[Combined LM + MSI classifier — LOOCV, Statement]")
    combined = df.merge(mi[["doc_id","msi_avg_modal_strength","msi_modal_density",
                            "msi_signed_per_1000","msi_epistemic_density"]],
                        on="doc_id", how="inner")
    feat_cols = ["lm_strong_per_1000","lm_weak_per_1000","lm_uncertainty_per_1000",
                 "lm_net_modal_per_1000","msi_avg_modal_strength","msi_modal_density",
                 "msi_signed_per_1000","msi_epistemic_density"]
    Xc = combined[feat_cols].values; yc = combined["label"].values
    if len(Xc) >= 5:
        pipe3 = Pipeline([("sc", StandardScaler()),
                          ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))])
        yc_pred = cross_val_predict(pipe3, Xc, yc, cv=LeaveOneOut())
        out_lines.append(classification_report(yc, yc_pred, digits=3, zero_division=0))

    # ---- Figure: LM Net Modal Tone vs dot-plot Δ (single panel) ----
    fig, ax = plt.subplots(figsize=(8.5, 6.0))
    colors = df["label"].map({"hawkish":"#d62728","neutral":"#7f7f7f","dovish":"#1f77b4"})
    x = df["delta_pct"].values
    y = df["lm_net_modal_per_1000"].values
    r, p = stats.pearsonr(x, y)
    rho, p_sp = stats.spearmanr(x, y)
    ax.scatter(x, y, c=colors, s=100, edgecolor="black", linewidth=0.5, alpha=0.85)
    sl, ic, _, _, _ = stats.linregress(x, y)
    xx = np.linspace(x.min() - 0.05, x.max() + 0.05, 50)
    ax.plot(xx, sl*xx + ic, color="black", linewidth=1.4, linestyle="--",
            label=f"OLS slope = {sl:+.3f}")
    ax.axhline(0, color="gray", linewidth=0.4)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.set_xlabel("Δ dot-plot median (percentage points)  →  hawkish shift", fontsize=11)
    ax.set_ylabel("LM Net Modal Tone (Strong − Weak) / 1k tokens", fontsize=11)
    ax.set_title(
        f"LM Net Modal Tone × Δ dot-plot (Statements, n={len(df)})\n"
        f"Pearson r = {r:+.3f} (p = {p:.3f}) ★    "
        f"Spearman ρ = {rho:+.3f} (p = {p_sp:.3f})",
        fontsize=11)
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#d62728',
               markersize=10, label='hawkish (rate ↑)'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#7f7f7f',
               markersize=10, label='neutral'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#1f77b4',
               markersize=10, label='dovish (rate ↓)'),
        Line2D([0],[0], color='black', linestyle='--', label=f"OLS  ({sl:+.3f})"),
    ], fontsize=10, loc="upper right")
    ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / "17_paperA_lm_vs_msi_corr.png", dpi=160); plt.close(fig)

    out_path = ANALYSIS / "lm_vs_msi.txt"
    out_path.write_text("\n".join(out_lines))
    print("\n" + "\n".join(out_lines))
    print(f"\nReport:  {out_path}")
    print(f"Figure:  {FIG / '17_paperA_lm_vs_msi_corr.png'}")

if __name__ == "__main__":
    main()
