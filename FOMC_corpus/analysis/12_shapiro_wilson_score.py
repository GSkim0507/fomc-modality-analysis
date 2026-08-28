"""
Paper A — Shapiro & Wilson (2022)-style hawk/dove sentiment score.

Shapiro & Wilson estimate Fed policy stance by combining LM sentiment with
domain-specific keywords for monetary policy tone. We implement a faithful
simplification:

  hawk_score(doc) =
      (inflation focus + tightening verbs + LM negative density) -
      (employment focus + accommodation verbs + LM positive density)

Then test:
  1. correlation of hawk_score with dot-plot Δ (predictive validity)
  2. correlation of hawk_score with MSI (convergent validity)
  3. classifier with hawk_score added to MSI (incremental validity)

Output:
  analysis/sw_features.csv
  analysis/sw_vs_msi.txt
  figures/18_paperA_sw_vs_msi.png
"""
from __future__ import annotations
from pathlib import Path
import re, json
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

# ---- Domain lexicons (Shapiro-Wilson 2022 spirit, adapted for FOMC text) ----
INFLATION_TERMS = {
    "inflation","inflationary","prices","price","cpi","pce",
    "deflation","disinflation","overheat","overheating",
}
EMPLOYMENT_TERMS = {
    "employment","unemployment","labor","jobs","workforce","payrolls",
    "underemployment","laid","layoffs","hiring","slack",
}
TIGHTENING_VERBS = {
    "raise","raises","raised","raising","tighten","tightening","tightened",
    "hike","hikes","hiked","hiking","firm","firming","increase","increased","increasing",
    "restrict","restrictive","restrain","restraining","reduce","reduces","reducing","reduction",
}
ACCOMMODATION_VERBS = {
    "lower","lowered","lowering","ease","easing","eased","cut","cuts","cutting",
    "accommodate","accommodative","accommodation","support","supports","supportive",
    "stimulate","stimulating","stimulus","expand","expanding","expansion",
}

def load_lm_lists() -> dict[str, set[str]]:
    df = pd.read_csv(ANALYSIS / "lm_master.csv")
    return {
        "Negative": set(df[df["Negative"] > 0]["Word"].str.lower().tolist()),
        "Positive": set(df[df["Positive"] > 0]["Word"].str.lower().tolist()),
    }

def score_doc(text: str, lm: dict[str, set[str]]) -> dict:
    tokens = [t.lower() for t in TOKEN_RE.findall(text)]
    n = max(1, len(tokens))
    counts = {
        "inflation": 0, "employment": 0,
        "tightening": 0, "accommodation": 0,
        "lm_neg": 0, "lm_pos": 0,
    }
    for w in tokens:
        if w in INFLATION_TERMS: counts["inflation"] += 1
        if w in EMPLOYMENT_TERMS: counts["employment"] += 1
        if w in TIGHTENING_VERBS: counts["tightening"] += 1
        if w in ACCOMMODATION_VERBS: counts["accommodation"] += 1
        if w in lm["Negative"]: counts["lm_neg"] += 1
        if w in lm["Positive"]: counts["lm_pos"] += 1
    # Normalize per 1000 tokens
    norm = {k: round(1000 * v / n, 3) for k, v in counts.items()}
    # Composite hawk score (S&W spirit):
    #   hawkish: inflation focus, tightening verbs, LM negative tone
    #   dovish:  employment focus, accommodation verbs, LM positive tone
    hawk = (norm["inflation"] + norm["tightening"] + 0.5 * norm["lm_neg"])
    dove = (norm["employment"] + norm["accommodation"] + 0.5 * norm["lm_pos"])
    return {
        **norm,
        "sw_hawk_minus_dove": round(hawk - dove, 3),
        "sw_hawk_score": round(hawk, 3),
        "sw_dove_score": round(dove, 3),
        "n_tokens": n,
    }

def iter_doc_jsons():
    for sub in DOC_TYPES_DIRS:
        for p in sorted((ROOT / sub).glob("*.json")):
            yield p

def main():
    lm = load_lm_lists()
    print(f"LM Neg: {len(lm['Negative'])}  LM Pos: {len(lm['Positive'])}")

    rows = []
    paths = list(iter_doc_jsons())
    print(f"Scoring {len(paths)} docs...")
    for i, p in enumerate(paths, 1):
        d = json.loads(p.read_text())
        s = score_doc(d["text"], lm)
        s["doc_id"] = d["doc_id"]
        s["doc_type"] = d["doc_type"]
        s["date"] = d["date"]
        rows.append(s)
        if i % 100 == 0: print(f"  [{i}/{len(paths)}]")
    feat = pd.DataFrame(rows)
    feat.to_csv(ANALYSIS / "sw_features.csv", index=False)

    out = ["=== Paper A — Shapiro-Wilson hawk/dove score ==="]
    out.append(f"\nDocuments scored: {len(feat)}   total tokens: {feat['n_tokens'].sum():,}")

    # --- Genre means
    out.append("\n[Genre means per 1k tokens]")
    g = feat.groupby("doc_type")[
        ["inflation","employment","tightening","accommodation",
         "lm_neg","lm_pos","sw_hawk_minus_dove"]
    ].mean().round(2)
    out.append(g.to_string())

    # --- Convergent: SW × MSI
    mi = pd.read_csv(ANALYSIS / "modality_index.csv")
    j = feat.merge(mi[["doc_id","msi_avg_modal_strength","msi_signed_per_1000"]],
                   on="doc_id")
    out.append("\n[Convergent validity — SW × MSI across all docs]")
    for a, b in [("sw_hawk_minus_dove","msi_avg_modal_strength"),
                 ("sw_hawk_minus_dove","msi_signed_per_1000"),
                 ("sw_hawk_score","msi_signed_per_1000")]:
        r, p = stats.pearsonr(j[a], j[b])
        out.append(f"  {a:<22} × {b:<22}  Pearson r={r:+.3f} (p={p:.3e})")

    # --- Predictive: SW × dot plot delta
    labels = pd.read_csv(ANALYSIS / "dotplot_labels.csv")
    labels = labels[labels["delta_pct"].notna()]
    df = labels.merge(feat[feat["doc_type"] == "statement"],
                      left_on="meeting_date", right_on="date")
    out.append(f"\n[Predictive validity — SW × dot-plot Δ — Statement, n={len(df)}]")
    for f in ["sw_hawk_minus_dove","sw_hawk_score","sw_dove_score",
              "inflation","employment","tightening","accommodation",
              "lm_neg","lm_pos"]:
        r, p = stats.pearsonr(df["delta_pct"], df[f])
        rho, p2 = stats.spearmanr(df["delta_pct"], df[f])
        star = " ★" if p < 0.05 else ""
        out.append(f"  Δ × {f:<22}  Pearson r={r:+.3f} (p={p:.3f}){star}  "
                   f"Spearman ρ={rho:+.3f} (p={p2:.3f})")

    # --- Classifier: SW only vs SW + MSI
    out.append("\n[SW-only classifier — LOOCV, Statement]")
    X_sw = df[["sw_hawk_minus_dove","inflation","employment","tightening",
               "accommodation","lm_neg","lm_pos"]].values
    y = df["label"].values
    pipe = Pipeline([("sc", StandardScaler()),
                     ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))])
    y_pred = cross_val_predict(pipe, X_sw, y, cv=LeaveOneOut())
    out.append(classification_report(y, y_pred, digits=3, zero_division=0))

    out.append("\n[SW + MSI combined — LOOCV, Statement]")
    j2 = df.merge(mi[["doc_id","msi_avg_modal_strength","msi_modal_density",
                      "msi_signed_per_1000","msi_epistemic_density"]], on="doc_id")
    X_c = j2[["sw_hawk_minus_dove","inflation","employment","tightening","accommodation",
              "lm_neg","lm_pos","msi_avg_modal_strength","msi_modal_density",
              "msi_signed_per_1000","msi_epistemic_density"]].values
    y_c = j2["label"].values
    y_pred2 = cross_val_predict(pipe, X_c, y_c, cv=LeaveOneOut())
    out.append(classification_report(y_c, y_pred2, digits=3, zero_division=0))

    # --- Figure
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    colors = df["label"].map({"hawkish":"#d62728","neutral":"#7f7f7f","dovish":"#1f77b4"})
    for ax, col, title in [
        (axes[0], "sw_hawk_minus_dove", "SW Hawk - Dove score"),
        (axes[1], "tightening", "Tightening verbs / 1k tokens"),
    ]:
        x = df["delta_pct"]; y = df[col]
        r, p = stats.pearsonr(x, y); sl, ic, _, _, _ = stats.linregress(x, y)
        xx = np.linspace(x.min(), x.max(), 50)
        ax.scatter(x, y, c=colors, s=80, edgecolor="black", linewidth=0.4)
        ax.plot(xx, sl*xx + ic, color="black", linestyle="--", linewidth=1.2)
        ax.set_title(f"{title}\nPearson r={r:+.3f} (p={p:.3f})")
        ax.set_xlabel("Δ dot-plot median (pp)"); ax.set_ylabel(col)
        ax.axhline(0, color="gray", linewidth=0.3)
        ax.axvline(0, color="gray", linewidth=0.5)
        ax.grid(alpha=0.3)
    fig.suptitle("Shapiro-Wilson style features × dot-plot Δ (Statements, n=39)", y=1.02)
    fig.tight_layout(); fig.savefig(FIG / "18_paperA_sw_vs_msi.png", dpi=150); plt.close(fig)

    (ANALYSIS / "sw_vs_msi.txt").write_text("\n".join(out))
    print("\n".join(out))

if __name__ == "__main__":
    main()
