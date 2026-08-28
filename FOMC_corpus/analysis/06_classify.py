"""
Document classification: hawkish / dovish / neutral.

Targets:  analysis/dotplot_labels.csv     (label per meeting)
Features: analysis/modality_index.csv     (per-doc MSI scores)
          analysis/pos_summary.csv        (per-doc modal lemma counts, density)

We pair each labeled meeting with the matching FOMC document(s) of a given
doc_type (default: statement). With ~21 usable labels and ~17 features, this
is a tiny supervised problem — we use LOOCV and report:
  - confusion matrix
  - per-class precision/recall/F1
  - feature importance (LogReg coefficients, RF importance)

Outputs:
  analysis/classification_report.txt
  figures/10_confusion_matrix.png
  figures/11_feature_importance.png
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import (classification_report, confusion_matrix,
                              ConfusionMatrixDisplay)
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"

DOC_TYPE = "statement"  # use statements (most committal language tracks closest to FOMC vote)

def main():
    labels = pd.read_csv(ANALYSIS / "dotplot_labels.csv")
    mi = pd.read_csv(ANALYSIS / "modality_index.csv")
    ps = pd.read_csv(ANALYSIS / "pos_summary.csv")

    # Keep only usable labels
    labels = labels[labels["label"].isin(["hawkish", "dovish", "neutral"])].copy()

    # Match: dotplot meeting_date (YYYY-MM-DD) -> doc with same date and doc_type
    mi = mi[mi["doc_type"] == DOC_TYPE].copy()
    ps = ps[ps["doc_type"] == DOC_TYPE].copy()
    df = labels.merge(mi, left_on="meeting_date", right_on="date", how="inner")
    feats = ps[["doc_id"] + [c for c in ps.columns if c.startswith("mod_")]]
    df = df.merge(feats, on="doc_id", how="left").fillna(0)

    print(f"Matched labeled meetings (target = '{DOC_TYPE}'): {len(df)}")
    print(df["label"].value_counts().to_string())
    if len(df) < 5:
        print("Too few matches — aborting.")
        return

    feature_cols = (["msi_modal_density", "msi_epistemic_density",
                     "msi_total_density", "msi_avg_modal_strength",
                     "msi_avg_epistemic_strength", "msi_signed_per_1000",
                     "modal_count", "epistemic_count"]
                    + [c for c in df.columns if c.startswith("mod_")])
    feature_cols = [c for c in feature_cols if c in df.columns]
    X = df[feature_cols].values.astype(float)
    y = df["label"].values

    report_lines = [f"Documents (doc_type={DOC_TYPE}): {len(df)}",
                    f"Class balance: {dict(df['label'].value_counts())}",
                    f"Features ({len(feature_cols)}): {feature_cols}",
                    "",
                    "Cross-validation: Leave-One-Out", ""]

    models = {
        "LogReg":
            Pipeline([("sc", StandardScaler()),
                      ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))]),
        "RandomForest":
            RandomForestClassifier(n_estimators=300, random_state=0,
                                   class_weight="balanced", min_samples_leaf=1),
    }

    fig_cm, axes_cm = plt.subplots(1, len(models), figsize=(6 * len(models), 5))
    if len(models) == 1: axes_cm = [axes_cm]

    rf_importances = None
    lr_coef = None

    for ax, (name, model) in zip(axes_cm, models.items()):
        y_pred = cross_val_predict(model, X, y, cv=LeaveOneOut())
        rep = classification_report(y, y_pred, digits=3, zero_division=0)
        report_lines += [f"=== {name} ===", rep, ""]
        labels_sorted = sorted(set(y))
        cm = confusion_matrix(y, y_pred, labels=labels_sorted)
        disp = ConfusionMatrixDisplay(cm, display_labels=labels_sorted)
        disp.plot(ax=ax, colorbar=False, cmap="Blues")
        ax.set_title(f"{name} (LOOCV)")

        # Fit on full data to get feature importances
        model.fit(X, y)
        if name == "RandomForest":
            rf_importances = pd.Series(model.feature_importances_, index=feature_cols)
        else:
            clf = model.named_steps["clf"]
            # multinomial coefs: (n_classes, n_feats). Aggregate by mean |coef|
            coef_abs = np.mean(np.abs(clf.coef_), axis=0)
            lr_coef = pd.Series(coef_abs, index=feature_cols)

    fig_cm.tight_layout()
    fig_cm.savefig(FIG / "10_confusion_matrix.png", dpi=150)
    plt.close(fig_cm)

    # Feature importance bar plots
    fig_fi, axes_fi = plt.subplots(1, 2, figsize=(14, 6))
    if lr_coef is not None:
        top = lr_coef.sort_values(ascending=False).head(12)[::-1]
        axes_fi[0].barh(top.index, top.values, color="#4c72b0")
        axes_fi[0].set_title("LogReg |coef| (top 12)")
    if rf_importances is not None:
        top = rf_importances.sort_values(ascending=False).head(12)[::-1]
        axes_fi[1].barh(top.index, top.values, color="#dd8452")
        axes_fi[1].set_title("RandomForest feature importance (top 12)")
    fig_fi.tight_layout()
    fig_fi.savefig(FIG / "11_feature_importance.png", dpi=150)
    plt.close(fig_fi)

    out = ANALYSIS / "classification_report.txt"
    out.write_text("\n".join(report_lines))
    print(f"\nReport written to {out}")
    print(f"Figures: 10_confusion_matrix.png  11_feature_importance.png")
    print("\n" + "\n".join(report_lines))

if __name__ == "__main__":
    main()
