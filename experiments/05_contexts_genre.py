"""
05_contexts_genre.py — Experiment C: contexts of use for each modal (subject, negation, passive, conditional,
reported speech, question), genre division of labour, semantic-type heuristics, chair/phase contrasts.

Outputs: D1_context_rates.csv, D2_subject_by_modal.csv, D3_chi2_modal_genre.csv, D4_semantic_type.csv,
         D5_chair_contrast.csv, D6_phase_contrast_statement.csv, D7_validation_sample.csv, D8_mnlogit.txt
Figures: D_fig1_genre_residuals.png, D_fig2_context_rates.png, D_fig3_subject_by_modal.png, D_fig4_semantic_type.png
"""
from __future__ import annotations
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from common import *

EPISTEMIC_ADV = {"likely", "probably", "perhaps", "possibly", "certainly", "well"}
def semantic_type(r) -> str:
    """Coarse modal-meaning heuristic (Coates 1983; Palmer 1990):
       epistemic (likelihood of proposition) / deontic (obligation, permission, advisability)
       / dynamic (ability, volition/commitment, circumstantial possibility) / conditional-hypothetical / reported."""
    m, v, st, cond, rep = r.modal, r.head_verb, r.subj_type, bool(r.cond), bool(r.reported)
    agentive = st in {"committee", "fed", "we_I", "person"}
    if m == "will":
        if agentive: return "dynamic_volitional"          # the Committee will continue/assess/take
        return "epistemic_predictive"                     # inflation will decline
    if m == "would":
        if rep: return "reported_backshift"               # participants noted that it would ...
        if v in {"say", "like", "argue", "note", "add", "think", "call", "describe", "characterize"} and st == "we_I": return "dynamic_tentative"   # I would say
        if cond: return "conditional_hypothetical"
        return "conditional_hypothetical" if not agentive else "dynamic_volitional_conditional"
    if m == "could":
        if agentive and v not in {"be", "have"}: return "dynamic_ability"
        return "epistemic_possibility"                    # risks that could impede
    if m == "can":
        if agentive: return "dynamic_ability"
        if v in {"be", "have"} and st in {"it_there_rel", "econ", "other"}: return "epistemic_possibility"
        return "dynamic_circumstantial"
    if m == "should":
        if agentive: return "deontic_advisability"        # the Committee should be patient
        if v in {"help", "support", "maintain", "keep", "continue", "be", "remain", "put", "lead", "contribute", "promote", "foster", "provide", "boost"} : return "epistemic_expectation"  # policy should help maintain
        return "deontic_advisability"
    if m == "may":
        if v in {"warrant", "be", "have", "take", "need", "reflect", "prove", "come", "become", "remain", "continue", "restrain", "affect", "lead", "contribute", "put"}: return "epistemic_possibility"
        if agentive and v in {"authorize", "use", "find", "choose", "decide", "want"}: return "deontic_permission"
        return "epistemic_possibility"
    return "other"

def main():
    df = load_modals(); df = df.assign(phase=df["date"].map(phase_of))
    df["vclass"] = df["head_verb"].map(verb_class)
    for c in ["neg", "passive", "perfect", "progressive", "cond", "reported", "question", "contracted"]:
        df[c] = df[c].astype(str).str.lower().eq("true")

    # D1 context rates: modal × genre
    rates = df.groupby(["doc_type", "modal"])[["neg", "passive", "perfect", "progressive", "cond", "reported", "question", "contracted"]].mean().round(3)
    rates["n"] = df.groupby(["doc_type", "modal"]).size()
    rates.reset_index().to_csv(TAB / "D1_context_rates.csv", index=False)

    # D2 subject type × modal (per genre)
    subj = (df.groupby(["doc_type", "modal", "subj_type"]).size().rename("n").reset_index())
    subj["share"] = subj["n"] / subj.groupby(["doc_type", "modal"])["n"].transform("sum")
    subj.to_csv(TAB / "D2_subject_by_modal.csv", index=False)
    top_subj = df.groupby(["doc_type", "modal"])["subj_lemma"].agg(lambda s: ", ".join(f"{k}({v})" for k, v in s.value_counts().head(6).items()))
    top_subj.reset_index().to_csv(TAB / "D2b_top_subject_lemmas.csv", index=False)

    # D3 chi-square modal × genre + standardized residuals
    ct = pd.crosstab(df["doc_type"], df["modal"]).reindex(index=GENRES, columns=SIX)
    chi2, p, dof, exp = stats.chi2_contingency(ct.values)
    resid = (ct.values - exp) / np.sqrt(exp)
    V = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
    rdf = pd.DataFrame(resid, index=ct.index, columns=ct.columns).round(2)
    with (TAB / "D3_chi2_modal_genre.csv").open("w") as f:
        f.write(f"# chi2={chi2:.1f} df={dof} p={p:.3g} CramersV={V:.3f}\n")
        rdf.to_csv(f)
    ct.to_csv(TAB / "D3b_modal_genre_counts.csv")

    # D4 semantic type heuristic
    df["sem_type"] = df.apply(semantic_type, axis=1)
    sem = df.groupby(["doc_type", "modal", "sem_type"]).size().rename("n").reset_index()
    sem["share"] = sem["n"] / sem.groupby(["doc_type", "modal"])["n"].transform("sum")
    sem.to_csv(TAB / "D4_semantic_type.csv", index=False)

    # D5 chair contrast (Yellen vs Powell), statements + press conferences: share of each modal, per1k
    docs = load_docs()
    ch = df[df.chair.isin(["Yellen", "Powell"])]
    tok = docs.groupby(["doc_type", "chair"])["n_tokens"].sum()
    cc = ch.groupby(["doc_type", "chair", "modal"]).size().rename("n").reset_index()
    cc["per1k"] = cc.apply(lambda r: 1000 * r.n / tok.get((r.doc_type, r.chair), np.nan), axis=1)
    cc["share"] = cc["n"] / cc.groupby(["doc_type", "chair"])["n"].transform("sum")
    cc.to_csv(TAB / "D5_chair_contrast.csv", index=False)
    # chi2 within statements and press conf
    chairs_stats = []
    for g in ["statement", "press_conf", "minutes", "speech"]:
        t = pd.crosstab(ch[ch.doc_type == g]["chair"], ch[ch.doc_type == g]["modal"]).reindex(columns=SIX).fillna(0)
        if t.shape[0] == 2:
            c2, pp, d, _ = stats.chi2_contingency(t.values); chairs_stats.append(dict(genre=g, chi2=round(c2, 1), p=pp, V=round(np.sqrt(c2 / (t.values.sum() * 1)), 3)))
    pd.DataFrame(chairs_stats).to_csv(TAB / "D5b_chair_chi2.csv", index=False)

    # D6 policy-phase contrast (statements)
    st = df[df.doc_type == "statement"]
    ph = pd.crosstab(st["phase"], st["modal"]).reindex(columns=SIX).fillna(0)
    phs = (ph.div(ph.sum(axis=1), axis=0) * 100).round(1)
    phs["n"] = ph.sum(axis=1)
    order_ph = [p[2] for p in PHASES]
    phs.reindex(order_ph).to_csv(TAB / "D6_phase_contrast_statement.csv")

    # D7 validation sample: 200 stratified sentences for manual coding
    samp = pd.concat([g.sample(min(len(g), 9), random_state=7) for _, g in df.groupby(["doc_type", "modal"])])
    samp = samp.sample(min(len(samp), 200), random_state=7)[["doc_id", "doc_type", "date", "modal", "head_verb", "subj_type", "neg", "cond", "reported", "sem_type", "sentence"]]
    samp["manual_head_verb_ok"] = ""; samp["manual_sem_type"] = ""; samp["note"] = ""
    samp.to_csv(TAB / "D7_validation_sample.csv", index=False)

    # D8 multinomial logit: modal ~ genre + period + subj_type (statsmodels)
    try:
        import statsmodels.api as sm
        d = df[df.modal.isin(SIX)].copy()
        d["period"] = np.where(d.year <= 2019, "early", "late")
        X = pd.get_dummies(d[["doc_type", "period", "subj_type"]], drop_first=True).astype(float)
        X = sm.add_constant(X)
        y = pd.Categorical(d["modal"], categories=SIX).codes
        mod = sm.MNLogit(y, X).fit(method="lbfgs", maxiter=300, disp=False)
        with (TAB / "D8_mnlogit.txt").open("w") as f:
            f.write("Reference category: will (code 0). Categories: " + ", ".join(SIX) + "\n")
            f.write(str(mod.summary()))
            f.write(f"\n\npseudo R2 = {mod.prsquared:.4f}\n")
    except Exception as e:
        (TAB / "D8_mnlogit.txt").write_text(f"MNLogit failed: {e}")

    # ---- figures
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(rdf, annot=True, fmt=".1f", cmap="RdBu_r", center=0, ax=ax)
    ax.set_title(f"Standardized residuals, modal × genre (2014–2026)\nχ²={chi2:.0f}, df={dof}, Cramér's V={V:.3f}")
    fig.tight_layout(); fig.savefig(FIG / "D_fig1_genre_residuals.png", dpi=160); plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    for ax, feat in zip(axes.flat, ["neg", "passive", "cond", "reported", "question", "contracted"]):
        piv = df.groupby(["doc_type", "modal"])[feat].mean().unstack().reindex(index=GENRES, columns=SIX) * 100
        piv.T.plot(kind="bar", ax=ax, width=.8); ax.set_title(f"% {feat}"); ax.legend(fontsize=6); ax.grid(alpha=.3, axis="y")
    fig.suptitle("Context features by modal and genre"); fig.tight_layout(); fig.savefig(FIG / "D_fig2_context_rates.png", dpi=160); plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for ax, g in zip(axes.flat, GENRES):
        piv = subj[subj.doc_type == g].pivot(index="modal", columns="subj_type", values="share").reindex(index=SIX, columns=SUBJ_ORDER).fillna(0)
        piv.plot(kind="barh", stacked=True, ax=ax, colormap="tab10", legend=False); ax.set_title(GENRE_LABEL[g]); ax.set_xlabel("share")
        if g == "speech": ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    fig.suptitle("Subject type of the modal clause, by modal and genre"); fig.tight_layout(); fig.savefig(FIG / "D_fig3_subject_by_modal.png", dpi=160); plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for ax, g in zip(axes.flat, GENRES):
        piv = sem[sem.doc_type == g].pivot(index="modal", columns="sem_type", values="share").reindex(index=SIX).fillna(0)
        piv.plot(kind="barh", stacked=True, ax=ax, colormap="tab20", legend=True); ax.legend(fontsize=6); ax.set_title(GENRE_LABEL[g])
    fig.suptitle("Heuristic modal-meaning type by modal and genre"); fig.tight_layout(); fig.savefig(FIG / "D_fig4_semantic_type.png", dpi=160); plt.close(fig)

    print(f"chi2={chi2:.1f} df={dof} p={p:.3g} V={V:.3f}\n", rdf.to_string())
    print("\nContext rates (statement):"); print(rates.loc["statement"].to_string())
    print("\nPhase contrast (statement shares %):"); print(phs.reindex(order_ph).to_string())
    print("\nSemantic types (statement):"); print(sem[sem.doc_type == "statement"].pivot(index="modal", columns="sem_type", values="share").round(2).fillna(0).to_string())

if __name__ == "__main__":
    main()
