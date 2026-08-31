"""
07_macro_correlation.py — Feedback 2.1 / 2.2: modals × business conditions, following verbs × business conditions.

MAIN spec (advisor policy): CFNAI_MA3 (2-month real-time lag) + VIX (28-day pre-meeting mean).
ROBUSTNESS-ONLY: unemployment gap, core-PCE inflation gap, alt CFNAI lag, excl. 2020, 2010-2026 window.
Discovery posture: exhaustive screens with BH-FDR correction; no cherry-picking.

Outputs (results/tables):
  E1_modal_macro_corr.csv       Pearson+Spearman, modal × genre × metric × {CFNAI_MA3, VIX}
  E2_hac_regressions.csv        density ~ CFNAI_MA3 + VIX (Newey-West, 4 lags), + robustness columns
  E3_novel_formulaic_macro.csv  statements: modal tokens in novel vs formulaic sentences × macro
  E4_class_macro.csv            modal × verb-semantic-class densities × macro (per genre)
  E5_discovery_screen.csv       ALL (modal, predicate) constructions n>=min × macro, BH-FDR q-values
  E6_subperiod_robustness.csv   E1 for excl-2020 and 2010-2026 samples
Figures: E_fig1_modal_macro_heatmap.png, E_fig2_top_constructions.png, E_fig3_scatter_key.png
"""
from __future__ import annotations
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from common import *

MAIN_X = ["cfnai_ma3_lag2", "vix_pre28"]
ROBUST_X = ["unrate_gap_lag1", "corepce_gap_lag2"]

def pred_class(hv, bt):
    if hv == "be":
        return {"adjectival": "copular_adj", "nominal": "copular_nom",
                "prepositional": "copular_prep", "adverbial": "copular_other"}.get(bt or "", "copular_bare")
    return verb_class(hv)

def load_all(window=True):
    df = pd.read_csv(TAB / "modal_tokens.csv", low_memory=False)
    df = df[~df["doc_id"].isin(EXCLUDE_DOCS)]
    df = df[df["modal"].isin(SIX)]
    if window:
        df = df[(df["date"] >= START) & (df["date"] <= END)]
    df["subj_type"] = [refine_subj_type(a, b) for a, b in zip(df["subj_lemma"], df["subj_text"])]
    df = df.assign(year=df["date"].str[:4].astype(int))
    df["predicate"] = df["predicate"].fillna(df["head_verb"])
    df["pclass"] = [pred_class(h, b) for h, b in zip(df["head_verb"], df["be_comp_type"].fillna(""))]
    for c in ["neg", "cond", "reported", "question"]:
        df[c] = df[c].astype(str).str.lower().eq("true")
    return df

def corr_row(x, y):
    ok = (~np.isnan(x)) & (~np.isnan(y))
    x, y = x[ok], y[ok]
    if len(x) < 10 or np.std(y) == 0:
        return dict(n=len(x), r=np.nan, p=np.nan, rho=np.nan, p_rho=np.nan)
    r, p = stats.pearsonr(x, y)
    rho, pr = stats.spearmanr(x, y)
    return dict(n=len(x), r=round(r, 3), p=round(p, 4), rho=round(rho, 3), p_rho=round(pr, 4))

def bh_fdr(pvals):
    p = np.asarray(pvals, dtype=float)
    n = len(p); order = np.argsort(p); ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n); out[order] = np.minimum(q, 1.0)
    return out

def hac_reg(dfm, ycol, xcols, maxlags=4):
    d = dfm[[ycol] + xcols].dropna()
    if len(d) < 15: return None
    X = sm.add_constant(d[xcols].astype(float))
    res = sm.OLS(d[ycol].astype(float), X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    return res, len(d)

def main():
    macro = pd.read_csv(TAB / "macro_by_doc.csv")
    b1 = pd.read_csv(TAB / "B1_modal_doc_series.csv")
    ds = b1.merge(macro.drop(columns=["doc_type", "date"]), on="doc_id")
    ds14 = ds[(ds.date >= START)]
    df = load_all()

    # ---------- E1: modal-level correlations ----------
    rows = []
    for g in GENRES:
        sub = ds14[ds14.doc_type == g]
        for mvar in ["cfnai_ma3_lag2", "vix_pre28"]:
            for mo in SIX:
                for met in ["per1k", "share"]:
                    rr = corr_row(sub[mvar].values, sub[f"{mo}_{met}"].values)
                    rows.append(dict(genre=g, macro=mvar, modal=mo, metric=met, **rr))
            rr = corr_row(sub[mvar].values, sub["six_per1k"].values)
            rows.append(dict(genre=g, macro=mvar, modal="ALL6", metric="per1k", **rr))
    e1 = pd.DataFrame(rows)
    e1["q_bh"] = np.nan
    mask = e1.p.notna()
    e1.loc[mask, "q_bh"] = bh_fdr(e1.loc[mask, "p"].values).round(4)
    e1.to_csv(TAB / "E1_modal_macro_corr.csv", index=False)

    # ---------- E2: HAC regressions (Kawamura Table-8 analogue) ----------
    regs = []
    for g in GENRES:
        sub = ds14[ds14.doc_type == g].sort_values("date")
        for mo in SIX + ["six"]:
            ycol = f"{mo}_per1k" if mo != "six" else "six_per1k"
            for spec, xs in [("main", MAIN_X), ("robust+gaps", MAIN_X + ROBUST_X),
                             ("altlag", ["cfnai_ma3_lag1", "vix_pre28"])]:
                out = hac_reg(sub, ycol, xs)
                if out is None: continue
                res, n = out
                row = dict(genre=g, modal=mo, spec=spec, n=n, adjR2=round(res.rsquared_adj, 3))
                for x in xs:
                    row[f"b_{x}"] = round(res.params[x], 4)
                    row[f"p_{x}"] = round(res.pvalues[x], 4)
                regs.append(row)
    e2 = pd.DataFrame(regs); e2.to_csv(TAB / "E2_hac_regressions.csv", index=False)

    # ---------- E3: novel vs formulaic (statements) ----------
    reuse = pd.read_csv(TAB / "C1_statement_sentence_reuse.csv")[["doc_id", "sent_id", "formulaic"]]
    st = df[df.doc_type == "statement"].merge(reuse, on=["doc_id", "sent_id"], how="left")
    st["formulaic"] = st["formulaic"].fillna(False).astype(bool)
    agg = st.groupby(["doc_id", "formulaic"]).size().unstack(fill_value=0)
    agg.columns = ["novel_n" if not c else "formulaic_n" for c in agg.columns]
    docs = load_docs(); tok = docs.set_index("doc_id")["n_tokens"]
    agg["novel_per1k"] = 1000 * agg.get("novel_n", 0) / tok
    agg["formulaic_per1k"] = 1000 * agg.get("formulaic_n", 0) / tok
    # per-modal novel densities
    nv = st[~st.formulaic].groupby(["doc_id", "modal"]).size().unstack(fill_value=0)
    for mo in SIX:
        if mo in nv: agg[f"novel_{mo}_per1k"] = 1000 * nv[mo] / tok
    agg = agg.merge(macro.set_index("doc_id"), left_index=True, right_index=True)
    e3rows = []
    for ycol in [c for c in agg.columns if c.endswith("per1k")]:
        for mvar in ["cfnai_ma3_lag2", "vix_pre28"]:
            rr = corr_row(agg[mvar].values, agg[ycol].fillna(0).values)
            e3rows.append(dict(series=ycol, macro=mvar, **rr))
    e3 = pd.DataFrame(e3rows); e3.to_csv(TAB / "E3_novel_formulaic_macro.csv", index=False)

    # ---------- E4: verb-class densities × macro ----------
    cls_rows = []
    for g in GENRES:
        sub = df[df.doc_type == g]
        cc = sub.groupby(["doc_id", "modal", "pclass"]).size().rename("n").reset_index()
        for (mo, pc), grp in cc.groupby(["modal", "pclass"]):
            if grp.n.sum() < 40: continue
            ser = grp.set_index("doc_id")["n"]
            base = ds14[ds14.doc_type == g].set_index("doc_id")
            y = (ser.reindex(base.index).fillna(0) * 1000 / base["n_tokens"])
            for mvar in ["cfnai_ma3_lag2", "vix_pre28"]:
                rr = corr_row(base[mvar].values, y.values)
                cls_rows.append(dict(genre=g, modal=mo, pclass=pc, total_n=int(grp.n.sum()), macro=mvar, **rr))
    e4 = pd.DataFrame(cls_rows)
    if len(e4):
        m4 = e4.p.notna(); e4["q_bh"] = np.nan
        e4.loc[m4, "q_bh"] = bh_fdr(e4.loc[m4, "p"].values).round(4)
    e4.to_csv(TAB / "E4_class_macro.csv", index=False)

    # ---------- E5: exhaustive construction screen (feedback 2.2 / discovery) ----------
    scr = []
    MIN_N = {"statement": 15, "minutes": 40, "press_conf": 40, "speech": 30}
    for g in GENRES:
        sub = df[df.doc_type == g]
        base = ds14[ds14.doc_type == g].set_index("doc_id")
        cc = sub.groupby(["modal", "predicate"]).size()
        keep = cc[cc >= MIN_N[g]].index
        per = sub.groupby(["doc_id", "modal", "predicate"]).size().rename("n").reset_index()
        for mo, pr in keep:
            ser = per[(per.modal == mo) & (per.predicate == pr)].set_index("doc_id")["n"]
            y = (ser.reindex(base.index).fillna(0) * 1000 / base["n_tokens"])
            for mvar in ["cfnai_ma3_lag2", "vix_pre28"]:
                rr = corr_row(base[mvar].values, y.values)
                scr.append(dict(genre=g, modal=mo, predicate=pr, total_n=int(cc[(mo, pr)]), macro=mvar, **rr))
    e5 = pd.DataFrame(scr)
    m5 = e5.p.notna(); e5["q_bh"] = np.nan
    e5.loc[m5, "q_bh"] = bh_fdr(e5.loc[m5, "p"].values).round(4)
    e5 = e5.sort_values("q_bh")
    e5.to_csv(TAB / "E5_discovery_screen.csv", index=False)

    # ---------- E6: subperiod robustness of E1 ----------
    rows6 = []
    for tag, dsx in [("excl2020", ds14[~ds14.date.str.startswith("2020")]),
                     ("2010_2026", ds)]:
        for g in GENRES:
            sub = dsx[dsx.doc_type == g]
            for mvar in ["cfnai_ma3_lag2", "vix_pre28"]:
                for mo in SIX:
                    rr = corr_row(sub[mvar].values, sub[f"{mo}_per1k"].values)
                    rows6.append(dict(sample=tag, genre=g, macro=mvar, modal=mo, metric="per1k", **rr))
    pd.DataFrame(rows6).to_csv(TAB / "E6_subperiod_robustness.csv", index=False)

    # ---------- figures ----------
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for ax, mvar, ttl in zip(axes, ["cfnai_ma3_lag2", "vix_pre28"], ["CFNAI-MA3 (t−2)", "VIX (28d pre)"]):
        piv = e1[(e1.metric == "per1k") & (e1.macro == mvar) & (e1.modal != "ALL6")].pivot(
            index="genre", columns="modal", values="r").reindex(index=GENRES, columns=SIX)
        sig = e1[(e1.metric == "per1k") & (e1.macro == mvar) & (e1.modal != "ALL6")].pivot(
            index="genre", columns="modal", values="q_bh").reindex(index=GENRES, columns=SIX)
        annot = piv.round(2).astype(str) + np.where(sig < .05, "*", "")
        sns.heatmap(piv, annot=annot, fmt="", cmap="RdBu_r", center=0, vmin=-.6, vmax=.6, ax=ax, cbar=(ax is axes[1]))
        ax.set_title(f"Pearson r: modal density × {ttl}  (* = BH q<.05)"); ax.set_xlabel(""); ax.set_ylabel("")
    fig.tight_layout(); fig.savefig(FIG / "E_fig1_modal_macro_heatmap.png", dpi=160); plt.close(fig)

    top = e5[(e5.q_bh < 0.05)].drop_duplicates(["genre", "modal", "predicate"]).head(12)
    if len(top):
        fig, axes = plt.subplots(3, 4, figsize=(16, 9), sharex=False)
        mm = pd.read_csv(TAB / "macro_monthly.csv", parse_dates=["date"]).set_index("date")
        for ax, (_, r) in zip(axes.flat, top.iterrows()):
            g = r.genre
            sub = df[(df.doc_type == g) & (df.modal == r.modal) & (df.predicate == r.predicate)]
            base = ds14[ds14.doc_type == g].set_index("doc_id")
            ser = sub.groupby("doc_id").size().reindex(base.index).fillna(0) * 1000 / base["n_tokens"]
            x = pd.to_datetime(base["date"])
            ax.plot(x, ser.values, lw=1, marker=".", ms=3, color="#4c72b0")
            ax2 = ax.twinx(); ax2.plot(mm.index, mm["CFNAIMA3"], color="grey", lw=.8, alpha=.7)
            ax2.set_ylim(-3, 3)
            ax.set_title(f"{g}: {r.modal}+{r.predicate}\nr={r.r} (q={r.q_bh})", fontsize=8)
        fig.suptitle("Constructions passing BH q<.05 vs CFNAI-MA3 (grey)", y=1.0)
        fig.tight_layout(); fig.savefig(FIG / "E_fig2_top_constructions.png", dpi=160); plt.close(fig)

    # console
    pd.set_option("display.width", 220)
    print("=== E1 significant after BH (q<.05) ===")
    print(e1[e1.q_bh < .05].sort_values(["genre", "macro", "modal"]).to_string(index=False))
    print("\n=== E5 discovery screen: q<.05 ===")
    print(e5[e5.q_bh < .05].to_string(index=False))
    print("\n=== E3 novel/formulaic ===")
    print(e3[e3.p < .1].to_string(index=False))
    print("\n=== E4 class screen q<.05 ===")
    if len(e4): print(e4[e4.q_bh < .05].to_string(index=False))

if __name__ == "__main__":
    main()
