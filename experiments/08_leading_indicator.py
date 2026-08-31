"""
08_leading_indicator.py — Feedback 3: can modal constructions serve as leading indicators?

Discovery posture: run lead–lag cross-correlations and Granger tests over a broad feature set,
report everything with multiplicity control; predictive HAC regressions test incremental power.

Features (meeting-frequency, per genre where sensible):
  - modal densities (six, per genre)
  - novel-sentence modal density (statements)
  - selected construction densities: any (modal, predicate) with |r|-screen n>=40 in minutes/press_conf
    plus the E5 q<.05 survivors
  - negated-can density (press_conf), could+causative (minutes)
Tests:
  F1: cross-correlation corr(text_t, CFNAI_MA3 at month(t)+k), k=-9..+9  (also VIX)
  F2: Granger causality (meeting frequency, both directions, AIC lags<=4, ADF-checked, diff if needed)
  F3: predictive HAC: CFNAI_MA3(m+3) ~ CFNAI_MA3(m-2) + VIX_pre + feature_t ; ΔadjR2 and p(feature)
      likewise for ΔVIX (post28−pre28)
  F4: event windows — construction introduction/removal dates vs CFNAI/VIX ±12 months (descriptive)
Outputs: F1_ccf.csv, F2_granger.csv, F3_predictive.csv, F4_event_windows.csv
Figures: F_fig1_ccf.png, F_fig2_event_windows.png
"""
from __future__ import annotations
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

def bh_fdr(pvals):
    p = np.asarray(pvals, dtype=float); n = len(p); order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n); out[order] = np.minimum(q, 1.0); return out

def build_features():
    macro = pd.read_csv(TAB / "macro_by_doc.csv")
    b1 = pd.read_csv(TAB / "B1_modal_doc_series.csv")
    df = pd.read_csv(TAB / "modal_tokens.csv", low_memory=False)
    df = df[~df.doc_id.isin(EXCLUDE_DOCS) & df.modal.isin(SIX)]
    df = df[(df.date >= START) & (df.date <= END)]
    df["predicate"] = df["predicate"].fillna(df["head_verb"])
    for c in ["neg", "cond", "reported"]:
        df[c] = df[c].astype(str).str.lower().eq("true")
    feats = {}   # (genre, name) -> Series indexed by doc_id
    docs = load_docs().set_index("doc_id")
    for g in ["statement", "minutes", "press_conf"]:
        base = b1[(b1.doc_type == g) & (b1.date >= START)].set_index("doc_id").sort_values("date")
        for mo in SIX:
            feats[(g, f"{mo}_per1k")] = base[f"{mo}_per1k"]
        feats[(g, "six_per1k")] = base["six_per1k"]
        sub = df[df.doc_type == g]
        # negated modals
        negs = sub[sub.neg].groupby(["doc_id", "modal"]).size().unstack(fill_value=0)
        for mo in ["can", "would", "will"]:
            if mo in negs:
                feats[(g, f"neg_{mo}_per1k")] = (negs[mo].reindex(base.index).fillna(0) * 1000 / base["n_tokens"])
    # novel modal density in statements
    reuse = pd.read_csv(TAB / "C1_statement_sentence_reuse.csv")[["doc_id", "sent_id", "formulaic"]]
    st = df[df.doc_type == "statement"].merge(reuse, on=["doc_id", "sent_id"], how="left")
    st["formulaic"] = st["formulaic"].fillna(False).astype(bool)
    baseS = b1[(b1.doc_type == "statement") & (b1.date >= START)].set_index("doc_id").sort_values("date")
    nv = st[~st.formulaic].groupby("doc_id").size().reindex(baseS.index).fillna(0)
    feats[("statement", "novel_modal_per1k")] = nv * 1000 / baseS["n_tokens"]
    # constructions from E5 (q<.05) + high-frequency constructions
    e5 = pd.read_csv(TAB / "E5_discovery_screen.csv")
    sel = e5[(e5.q_bh < .05)][["genre", "modal", "predicate"]].drop_duplicates()
    hi = e5[e5.total_n >= 120][["genre", "modal", "predicate"]].drop_duplicates()
    sel = pd.concat([sel, hi]).drop_duplicates()
    for _, r in sel.iterrows():
        g = r.genre
        if g == "speech": continue
        base = b1[(b1.doc_type == g) & (b1.date >= START)].set_index("doc_id").sort_values("date")
        ser = df[(df.doc_type == g) & (df.modal == r.modal) & (df.predicate == r.predicate)]\
              .groupby("doc_id").size().reindex(base.index).fillna(0) * 1000 / base["n_tokens"]
        feats[(g, f"{r.modal}+{r.predicate}")] = ser
    meta = {}
    for (g, name), ser in feats.items():
        base = b1[(b1.doc_type == g) & (b1.date >= START)].set_index("doc_id").sort_values("date")
        meta[(g, name)] = pd.DataFrame({"y": ser.reindex(base.index).values,
                                        "date": pd.to_datetime(base["date"]).values}).dropna()
    return meta, macro

def main():
    mm = pd.read_csv(TAB / "macro_monthly.csv", parse_dates=["date"]).set_index("date")
    cfn = mm["CFNAIMA3"]; vixm = mm["VIX_M"]
    meta, macro = build_features()
    macro_by_doc = pd.read_csv(TAB / "macro_by_doc.csv").set_index("doc_id")

    # ---------- F1: CCF over month shifts ----------
    rows = []
    for (g, name), dfx in meta.items():
        if dfx["y"].std() == 0 or len(dfx) < 20: continue
        for target, series in [("CFNAI_MA3", cfn), ("VIX_M", vixm)]:
            for k in range(-9, 10):
                vals = []
                for _, r in dfx.iterrows():
                    key = (pd.Period(r["date"], freq="M") + k).to_timestamp()
                    vals.append(series.get(key, np.nan))
                vals = np.array(vals, dtype=float)
                ok = ~np.isnan(vals)
                if ok.sum() < 20: continue
                r_, p_ = stats.pearsonr(dfx["y"].values[ok], vals[ok])
                rows.append(dict(genre=g, feature=name, target=target, k_months=k,
                                 n=int(ok.sum()), r=round(r_, 3), p=round(p_, 4)))
    f1 = pd.DataFrame(rows)
    # summarize peak lag per feature × target
    peaks = (f1.assign(absr=f1.r.abs())
               .sort_values("absr", ascending=False)
               .groupby(["genre", "feature", "target"]).head(1)
               .rename(columns={"k_months": "peak_k", "r": "peak_r", "p": "peak_p"}))
    f1.to_csv(TAB / "F1_ccf.csv", index=False)
    peaks.to_csv(TAB / "F1b_ccf_peaks.csv", index=False)

    # ---------- F2: Granger (meeting frequency) ----------
    g2 = []
    for (g, name), dfx in meta.items():
        if len(dfx) < 30 or dfx["y"].std() == 0: continue
        md = macro_by_doc.reindex(
            pd.read_csv(TAB / "B1_modal_doc_series.csv").query("doc_type==@g and date>=@START")
              .sort_values("date")["doc_id"]).reset_index()
        for target in ["cfnai_ma3_lag2", "vix_pre28"]:
            x = md[target].values.astype(float)
            y = dfx["y"].values.astype(float)
            n = min(len(x), len(y)); x, y = x[:n], y[:n]
            def stationary(z):
                try: return adfuller(z, autolag="AIC")[1] < .05
                except Exception: return False
            xs = x if stationary(x) else np.diff(x)
            ys = y if stationary(y) else np.diff(y)
            n2 = min(len(xs), len(ys)); xs, ys = xs[-n2:], ys[-n2:]
            if n2 < 25: continue
            try:
                # does TEXT Granger-cause MACRO?
                res = grangercausalitytests(np.column_stack([xs, ys]), maxlag=4, verbose=False)
                p_txt2mac = min(res[l][0]["ssr_ftest"][1] for l in res)
                res2 = grangercausalitytests(np.column_stack([ys, xs]), maxlag=4, verbose=False)
                p_mac2txt = min(res2[l][0]["ssr_ftest"][1] for l in res2)
                g2.append(dict(genre=g, feature=name, target=target, n=n2,
                               p_text_to_macro=round(p_txt2mac, 4), p_macro_to_text=round(p_mac2txt, 4)))
            except Exception:
                continue
    f2 = pd.DataFrame(g2)
    if len(f2):
        f2["q_text_to_macro"] = bh_fdr(f2["p_text_to_macro"].values).round(4)
        f2["q_macro_to_text"] = bh_fdr(f2["p_macro_to_text"].values).round(4)
    f2.to_csv(TAB / "F2_granger.csv", index=False)

    # ---------- F3: predictive HAC regressions ----------
    f3rows = []
    for (g, name), dfx in meta.items():
        b1g = pd.read_csv(TAB / "B1_modal_doc_series.csv").query("doc_type==@g and date>=@START").sort_values("date")
        md = macro_by_doc.reindex(b1g["doc_id"]).reset_index()
        n = min(len(md), len(dfx))
        d = pd.DataFrame({
            "y_lead": md["cfnai_ma3_lead3"].values[:n],
            "cfnai": md["cfnai_ma3_lag2"].values[:n],
            "vix": md["vix_pre28"].values[:n],
            "feat": dfx["y"].values[:n]}).dropna()
        if len(d) < 25 or d.feat.std() == 0: continue
        X0 = sm.add_constant(d[["cfnai", "vix"]]); X1 = sm.add_constant(d[["cfnai", "vix", "feat"]])
        m0 = sm.OLS(d.y_lead, X0).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
        m1 = sm.OLS(d.y_lead, X1).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
        f3rows.append(dict(genre=g, feature=name, target="CFNAI_MA3(+3m)", n=len(d),
                           b_feat=round(m1.params["feat"], 4), p_feat=round(m1.pvalues["feat"], 4),
                           adjR2_base=round(m0.rsquared_adj, 3), adjR2_with=round(m1.rsquared_adj, 3),
                           d_adjR2=round(m1.rsquared_adj - m0.rsquared_adj, 3)))
        d2 = pd.DataFrame({"y_lead": (md["vix_post28"] - md["vix_pre28"]).values[:n],
                           "cfnai": md["cfnai_ma3_lag2"].values[:n],
                           "vix": md["vix_pre28"].values[:n],
                           "feat": dfx["y"].values[:n]}).dropna()
        if len(d2) >= 25 and d2.feat.std() > 0:
            X0 = sm.add_constant(d2[["cfnai", "vix"]]); X1 = sm.add_constant(d2[["cfnai", "vix", "feat"]])
            m0 = sm.OLS(d2.y_lead, X0).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
            m1 = sm.OLS(d2.y_lead, X1).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
            f3rows.append(dict(genre=g, feature=name, target="dVIX(+28d)", n=len(d2),
                               b_feat=round(m1.params["feat"], 4), p_feat=round(m1.pvalues["feat"], 4),
                               adjR2_base=round(m0.rsquared_adj, 3), adjR2_with=round(m1.rsquared_adj, 3),
                               d_adjR2=round(m1.rsquared_adj - m0.rsquared_adj, 3)))
    f3 = pd.DataFrame(f3rows)
    if len(f3):
        f3["q_bh"] = bh_fdr(f3["p_feat"].values).round(4)
        f3 = f3.sort_values("q_bh")
    f3.to_csv(TAB / "F3_predictive.csv", index=False)

    # ---------- F4: event windows ----------
    events = [("2015-12-16", "may-warrant deleted / will guidance in"),
              ("2017-06-14", "should sentence deleted"),
              ("2019-01-30", "may be appropriate (patient) in"),
              ("2020-09-16", "would/could sentence in"),
              ("2023-03-22", "may firming episode in"),
              ("2024-01-31", "may firming episode out")]
    rows4 = []
    for dstr, lab in events:
        p0 = pd.Period(dstr, freq="M")
        for k in range(-12, 13):
            key = (p0 + k).to_timestamp()
            rows4.append(dict(event=lab, event_date=dstr, k_months=k,
                              cfnai_ma3=cfn.get(key, np.nan), vix_m=vixm.get(key, np.nan)))
    f4 = pd.DataFrame(rows4); f4.to_csv(TAB / "F4_event_windows.csv", index=False)

    # ---------- figures ----------
    key_feats = [("press_conf", "neg_can_per1k"), ("statement", "novel_modal_per1k"),
                 ("minutes", "could_per1k"), ("press_conf", "can_per1k"),
                 ("minutes", "would_per1k"), ("statement", "will_per1k")]
    fig, axes = plt.subplots(2, 3, figsize=(15, 7), sharex=True)
    for ax, (g, name) in zip(axes.flat, key_feats):
        for target, colr in [("CFNAI_MA3", "#4c72b0"), ("VIX_M", "#dd8452")]:
            sub = f1[(f1.genre == g) & (f1.feature == name) & (f1.target == target)]
            if len(sub): ax.plot(sub.k_months, sub.r, marker="o", ms=3, label=target, color=colr)
        n0 = f1[(f1.genre == g) & (f1.feature == name)].n.max()
        if not np.isnan(n0): ax.axhline(1.96/np.sqrt(n0), color="grey", ls=":"); ax.axhline(-1.96/np.sqrt(n0), color="grey", ls=":")
        ax.axvline(0, color="black", lw=.5); ax.set_title(f"{g}: {name}", fontsize=9); ax.grid(alpha=.3)
    axes[0, 0].legend(fontsize=7); axes[1, 1].set_xlabel("macro shifted k months (k>0: text leads)")
    fig.suptitle("Cross-correlation of text features with CFNAI-MA3 / VIX at month shifts")
    fig.tight_layout(); fig.savefig(FIG / "F_fig1_ccf.png", dpi=160); plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(15, 6), sharex=True)
    for ax, (dstr, lab) in zip(axes.flat, events):
        sub = f4[f4.event_date == dstr]
        ax.plot(sub.k_months, sub.cfnai_ma3, color="#4c72b0", label="CFNAI-MA3")
        ax2 = ax.twinx(); ax2.plot(sub.k_months, sub.vix_m, color="#dd8452", label="VIX")
        ax.axvline(0, color="black", lw=1); ax.set_title(lab, fontsize=8); ax.grid(alpha=.3)
    fig.suptitle("CFNAI-MA3 (blue) and VIX (orange) around construction edit events (k=0 = event month)")
    fig.tight_layout(); fig.savefig(FIG / "F_fig2_event_windows.png", dpi=160); plt.close(fig)

    pd.set_option("display.width", 220)
    print("=== F1b peak lags (|r| max), selected ===")
    print(peaks[peaks.peak_p < .05].sort_values(["genre", "feature"]).head(40).to_string(index=False))
    print("\n=== F2 Granger q<.10 (text→macro) ===")
    if len(f2): print(f2[f2.q_text_to_macro < .10].to_string(index=False))
    print("\n=== F3 predictive: q<.10 ===")
    if len(f3): print(f3[f3.q_bh < .10].to_string(index=False))

if __name__ == "__main__":
    main()
