"""
02_following_verbs.py — Experiment A: exhaustive analysis of verbs following the six modals (2014–2026).

Feedback-1 revision: analyses run over `predicate` (= head verb, or be+<complement> for copular be),
so passives/futures resolve to the true lexical verb and copular uses expose their complement.
Adds A7_be_complements.csv (modal × be-complement inventory).

Outputs (results/tables):
  A1_following_verbs_all.csv         modal × head_verb counts and within-modal share, per genre + overall
  A2_top_following_verbs.csv         top-25 following verbs per modal per genre
  A3_collostruction.csv              distinctive collexeme analysis (Fisher exact; signed -log10 p; G2)
  A4_semantic_class_by_modal.csv     semantic-class distribution per modal (overall + per genre)
  A5_jsd_between_modals.csv          Jensen–Shannon divergence of verb distributions between modals
  A6_following_verbs_by_period.csv   top verbs per modal for early (2014–2019) vs late (2020–2026), statements & all
Figures (results/figures):
  A_fig1_semantic_heatmap.png, A_fig2_top_verbs_statement.png, A_fig3_collostruction.png
"""
from __future__ import annotations
import numpy as np, pandas as pd
from scipy import stats
from scipy.spatial.distance import jensenshannon
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from common import *

def pred_class(hv, bt):
    if hv == "be":
        return {"adjectival": "copular_adj", "nominal": "copular_nom",
                "prepositional": "copular_prep", "adverbial": "copular_other"}.get(bt or "", "copular_bare")
    return verb_class(hv)

def collostruction(df: pd.DataFrame, min_count=3) -> pd.DataFrame:
    """Distinctive collexeme analysis: for each modal M and verb V,
    2x2 table [V&M, V&notM ; notV&M, notV&notM]."""
    ct = pd.crosstab(df["predicate"], df["modal"])
    N = ct.values.sum()
    rows = []
    for v in ct.index:
        for m in ct.columns:
            a = ct.loc[v, m]
            if a < min_count: continue
            b = ct.loc[v].sum() - a
            c = ct[m].sum() - a
            d = N - a - b - c
            exp = (a + b) * (a + c) / N
            odds, p = stats.fisher_exact([[a, b], [c, d]])
            sign = 1 if a > exp else -1
            # log-likelihood G2
            tbl = np.array([[a, b], [c, d]], dtype=float)
            e = np.outer(tbl.sum(1), tbl.sum(0)) / N
            with np.errstate(divide="ignore", invalid="ignore"):
                g2 = 2 * np.nansum(tbl * np.log(tbl / e))
            rows.append(dict(modal=m, verb=v, obs=int(a), exp=round(exp, 2),
                             ratio=round(a / exp, 2), odds_ratio=round(odds, 3),
                             p=p, signed_log10p=round(sign * -np.log10(max(p, 1e-300)), 2), G2=round(g2, 2)))
    out = pd.DataFrame(rows).sort_values(["modal", "signed_log10p"], ascending=[True, False])
    return out

def main():
    df = load_modals()
    docs = load_docs()
    print("modal tokens 2014-2026 (six):", len(df))
    df["predicate"] = df["predicate"].fillna(df["head_verb"])
    df["be_comp_type"] = df["be_comp_type"].fillna("")
    df["vclass"] = [pred_class(h, b) for h, b in zip(df["head_verb"], df["be_comp_type"])]

    # A1: full counts
    parts = []
    for g, sub in [("all", df)] + [(g, df[df.doc_type == g]) for g in GENRES]:
        ct = sub.groupby(["modal", "predicate"]).size().rename("n").reset_index()
        ct["share_within_modal"] = ct["n"] / ct.groupby("modal")["n"].transform("sum")
        ct["genre"] = g
        parts.append(ct)
    a1 = pd.concat(parts).sort_values(["genre", "modal", "n"], ascending=[True, True, False])
    a1.to_csv(TAB / "A1_following_verbs_all.csv", index=False)

    # A2: top-25 per modal per genre
    a2 = a1.groupby(["genre", "modal"]).head(25)
    a2.to_csv(TAB / "A2_top_following_verbs.csv", index=False)

    # A3: collostruction per genre and overall
    cparts = []
    for g, sub in [("all", df)] + [(g, df[df.doc_type == g]) for g in GENRES]:
        c = collostruction(sub); c["genre"] = g; cparts.append(c)
    a3 = pd.concat(cparts); a3.to_csv(TAB / "A3_collostruction.csv", index=False)

    # A4: semantic class distribution
    sparts = []
    for g, sub in [("all", df)] + [(g, df[df.doc_type == g]) for g in GENRES]:
        ct = pd.crosstab(sub["modal"], sub["vclass"], normalize="index").round(4)
        ct["genre"] = g; ct["n"] = sub.groupby("modal").size()
        sparts.append(ct.reset_index())
    a4 = pd.concat(sparts); a4.to_csv(TAB / "A4_semantic_class_by_modal.csv", index=False)

    # A5: JSD between modals (overall and statements)
    jrows = []
    for g, sub in [("all", df), ("statement", df[df.doc_type == "statement"])]:
        ct = pd.crosstab(sub["predicate"], sub["modal"])
        P = ct / ct.sum()
        for i, m1 in enumerate(SIX):
            for m2 in SIX[i+1:]:
                if m1 in P and m2 in P:
                    jrows.append(dict(genre=g, m1=m1, m2=m2, jsd=round(float(jensenshannon(P[m1], P[m2], base=2) ** 2), 4)))
    pd.DataFrame(jrows).to_csv(TAB / "A5_jsd_between_modals.csv", index=False)

    # A6: period contrast
    df["period"] = np.where(df["year"] <= 2019, "2014-2019", "2020-2026")
    pparts = []
    for g, sub in [("all", df), ("statement", df[df.doc_type == "statement"])]:
        ct = sub.groupby(["period", "modal", "predicate"]).size().rename("n").reset_index()
        ct["share"] = ct["n"] / ct.groupby(["period", "modal"])["n"].transform("sum")
        ct = ct.sort_values(["period", "modal", "n"], ascending=[True, True, False]).groupby(["period", "modal"]).head(15)
        ct["genre"] = g; pparts.append(ct)
    pd.concat(pparts).to_csv(TAB / "A6_following_verbs_by_period.csv", index=False)

    # A7: be-complement inventory
    be = df[df.head_verb == "be"].copy()
    for c in ["be_comp_type", "be_comp", "be_xcomp"]:
        be[c] = be[c].fillna("")
    a7 = (be.groupby(["doc_type", "modal", "be_comp_type", "be_comp", "be_xcomp"]).size()
            .rename("n").reset_index().sort_values(["doc_type", "modal", "n"], ascending=[True, True, False]))
    a7.to_csv(TAB / "A7_be_complements.csv", index=False)
    resolved = (be.be_comp.fillna("") != "").mean()
    print(f"\nbe-heads: {len(be)}  complement resolved: {resolved:.1%}")

    # ---- Figures ----
    # Fig1: semantic class heatmap, per genre (2x2 panels)
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    classes = ["policy_action", "copular_adj", "copular_nom", "copular_prep", "existence", "mental", "communication", "activity", "causative", "occurrence", "aspectual", "other"]
    for ax, g in zip(axes.flat, GENRES):
        sub = df[df.doc_type == g]
        ct = pd.crosstab(sub["modal"], sub["vclass"], normalize="index").reindex(index=SIX, columns=classes).fillna(0)
        sns.heatmap(ct * 100, annot=True, fmt=".0f", cmap="Blues", ax=ax, cbar=False, vmin=0, vmax=60, annot_kws={"fontsize":7})
        ax.set_title(f"{GENRE_LABEL[g]} (n={len(sub):,})"); ax.set_xlabel(""); ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=40)
    fig.suptitle("Semantic class of the verb following each modal (% within modal), 2014–2026", y=1.0)
    fig.tight_layout(); fig.savefig(FIG / "A_fig1_semantic_heatmap.png", dpi=160); plt.close(fig)

    # Fig2: top-10 following verbs per modal, statements
    st = df[df.doc_type == "statement"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    for ax, m in zip(axes.flat, SIX):
        vc = st[st.modal == m]["predicate"].value_counts().head(10)
        ax.barh(vc.index[::-1], vc.values[::-1], color="#4c72b0")
        ax.set_title(f"{m}  (n={int((st.modal==m).sum())})")
    fig.suptitle("FOMC statements 2014–2026: top-10 verbs following each modal")
    fig.tight_layout(); fig.savefig(FIG / "A_fig2_top_verbs_statement.png", dpi=160); plt.close(fig)

    # Fig3: collostruction (all genres), top 8 attracted per modal
    c_all = a3[a3.genre == "all"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    for ax, m in zip(axes.flat, SIX):
        sub = c_all[(c_all.modal == m) & (c_all.signed_log10p > 0)].head(8)
        ax.barh(sub["verb"][::-1], sub["signed_log10p"][::-1], color="#dd8452")
        ax.set_title(f"{m}: most attracted collexemes"); ax.set_xlabel("-log10 p (Fisher)")
    fig.tight_layout(); fig.savefig(FIG / "A_fig3_collostruction.png", dpi=160); plt.close(fig)

    # console summary
    print("\nTop following verbs per modal (all genres):")
    for m in SIX:
        vc = df[df.modal == m]["predicate"].value_counts().head(8)
        print(f"  {m:7s} n={int((df.modal==m).sum()):6d} | " + ", ".join(f"{v}({c})" for v, c in vc.items()))
    print("\nTop following verbs per modal (statements):")
    for m in SIX:
        vc = st[st.modal == m]["predicate"].value_counts().head(8)
        print(f"  {m:7s} n={int((st.modal==m).sum()):6d} | " + ", ".join(f"{v}({c})" for v, c in vc.items()))
    print("\nSemantic classes (all):"); print((pd.crosstab(df["modal"], df["vclass"], normalize="index")*100).round(1).reindex(SIX).to_string())

if __name__ == "__main__":
    main()
