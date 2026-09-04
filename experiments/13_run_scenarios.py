"""
13_run_scenarios.py — Scenario-matrix experiments (Phase 11; docs/08 §3.3).

One code path, many settings.  A scenario folder is defined by (S corpus definition, U analysis unit);
period (T1 full / T2 excl. 2020 / T3 2010-2026) and normalisation (N1 density / N2 share / N3 count) appear as
variant columns *inside* each block so that they can be read side by side.

Blocks (all run in every scenario where the required layers exist):
  X-A inventory            top units per modal per layer, JSD between modals
  X-B staircase            statement unit shares per meeting + PELT change points + responsible sentences  (needs statement)
  X-C retention            construction retention half-life, edit events per year                        (needs statement)
  X-D division of labour   layer x modal chi2 / Cramer's V / residuals, pragmatic contrast will/would/can/could
  X-E macro                exhaustive screen (BH-FDR) + pre-specified main table (T1/T2/T3, HAC) + Kawamura test
  X-F be appropriate       will/would/may + be appropriate by layer vs VIX/CFNAI
  X-G lead-lag (appendix)  CCF k=-9..+9 with monthly CFNAI-MA3 / VIX, Granger both directions

Usage:
  .venv/bin/python experiments/13_run_scenarios.py --corpus all --unit all
  .venv/bin/python experiments/13_run_scenarios.py --corpus S4 --unit U2
Outputs: results/scenarios/<S>_<U>/{tables,figures,summary.json,README.md}
"""
from __future__ import annotations
import argparse, json, math, sys, time, re, warnings
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import ruptures as rpt
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.tsa.stattools import grangercausalitytests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_v3 import (ROOT, TAB, SCEN, SIX, EVENTS, SCENARIOS, UNITS, PERIODS, MAIN_PERIODS, NORMS, LAYER_LABEL,
                       load_tokens_v3, load_docs_v3, load_macro, unit_key, period_mask, genre_of)

warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.dpi": 100, "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9})
MACRO_VARS = {"cfnai": "cfnai_ma3_lag2", "vix": "vix_pre28"}
MIN_TOKENS, MAX_ZERO, MIN_N = 40, 0.60, 30


# ----------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------
def norm_sentence(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r"\d+([./-]\d+)*", "#", s)
    s = re.sub(r"[^a-z# ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def corr_pair(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    x, y = x[ok], y[ok]
    if len(x) < 8 or x.std() == 0 or y.std() == 0:
        return dict(n=int(len(x)), r=np.nan, p_r=np.nan, rho=np.nan, p_rho=np.nan)
    r, pr = stats.pearsonr(x, y); rho, prho = stats.spearmanr(x, y)
    return dict(n=int(len(x)), r=float(r), p_r=float(pr), rho=float(rho), p_rho=float(prho))


def hac(y, X, lags=4):
    X = sm.add_constant(np.asarray(X, float)); y = np.asarray(y, float)
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
    if ok.sum() < 12:
        return None
    m = sm.OLS(y[ok], X[ok]).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return m


def bh(p):
    p = np.asarray(p, float); q = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    if ok.sum():
        q[ok] = multipletests(p[ok], method="fdr_bh")[1]
    return q


def modal_of_unit(u: str) -> str:
    return re.split(r"[+/]", u, 1)[0]


def savefig(fig, path):
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


# ----------------------------------------------------------------------------------------------
# per-document series
# ----------------------------------------------------------------------------------------------
def doc_layer_index(dl: pd.DataFrame, key_col: str) -> pd.DataFrame:
    """token denominators per (doc, key) where key is a layer or a genre (pooled over scenario layers)."""
    g = dl.groupby(["doc_id", key_col]).agg(date=("date", "first"), tokens=("n_tokens", "sum")).reset_index()
    return g.rename(columns={key_col: "key"})


def unit_series(tk: pd.DataFrame, dl: pd.DataFrame, level: str, min_tokens=MIN_TOKENS, extra_units=()):
    """Long table: doc_id, date, level, key, unit, count, tokens, six_total, density, share."""
    key_col = "layer" if level == "layer" else "genre"
    idx = doc_layer_index(dl, key_col)
    out = []
    for key, sub in tk.groupby(key_col):
        docs_k = idx[idx.key == key].set_index("doc_id")
        cnt = sub.groupby(["doc_id", "unit"]).size().unstack(fill_value=0)
        cnt = cnt.reindex(docs_k.index, fill_value=0)
        total = cnt.sum(axis=1)
        keep = [u for u in cnt.columns if cnt[u].sum() >= min_tokens or u in extra_units]
        cnt = cnt[keep]
        cnt["ALL"] = total
        long = cnt.reset_index().melt(id_vars="doc_id", var_name="unit", value_name="count")
        long["date"] = long.doc_id.map(docs_k.date); long["tokens"] = long.doc_id.map(docs_k.tokens)
        long["six_total"] = long.doc_id.map(total)
        long["level"] = level; long["key"] = key
        out.append(long)
    if not out:
        return pd.DataFrame(columns=["doc_id", "date", "level", "key", "unit", "count", "tokens", "six_total", "density", "share"])
    df = pd.concat(out, ignore_index=True)
    df["density"] = df["count"] / df["tokens"].replace(0, np.nan) * 1000
    df["share"] = df["count"] / df["six_total"].replace(0, np.nan)
    return df


# ----------------------------------------------------------------------------------------------
# blocks
# ----------------------------------------------------------------------------------------------
def corpus_table(tk, dl, out, summary):
    rows = []
    for T in MAIN_PERIODS:
        m_t = period_mask(tk.date, T); m_d = period_mask(dl.date, T)
        for lay in summary["layers"]:
            d = dl[m_d & (dl.layer == lay)]; t = tk[m_t & (tk.layer == lay)]
            rows.append(dict(period=T, layer=lay, label=LAYER_LABEL.get(lay, lay), n_docs=d.doc_id.nunique(),
                             tokens=int(d.n_tokens.sum()), six_modal_tokens=len(t),
                             per_1k=round(len(t) / max(d.n_tokens.sum(), 1) * 1000, 2)))
    df = pd.DataFrame(rows); df.to_csv(out / "tables" / "corpus.csv", index=False)
    summary["corpus"] = df[df.period == "T1"].drop(columns="period").to_dict("records")


def block_A(tk, out, summary, U):
    t1 = tk[period_mask(tk.date, "T1")]
    rows = []
    for lay, sub in t1.groupby("layer"):
        for modal, s2 in sub.groupby("modal"):
            vc = s2.unit.value_counts()
            for rank, (u, n) in enumerate(vc.head(15).items(), 1):
                rows.append(dict(layer=lay, modal=modal, unit=u, n=int(n), share=round(n / len(s2), 4), rank=rank, modal_n=len(s2)))
    inv = pd.DataFrame(rows); inv.to_csv(out / "tables" / "A1_inventory.csv", index=False)
    # JSD between modals per layer
    jrows = []
    for lay, sub in t1.groupby("layer"):
        P = sub.groupby(["modal", "unit"]).size().unstack(fill_value=0).reindex(SIX).fillna(0)
        P = P.div(P.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        for i, a in enumerate(SIX):
            for b in SIX[i + 1:]:
                p, q = P.loc[a].values, P.loc[b].values
                if p.sum() == 0 or q.sum() == 0: continue
                m = (p + q) / 2
                def kl(x, y):
                    mask = x > 0
                    return float(np.sum(x[mask] * np.log2(x[mask] / y[mask])))
                jrows.append(dict(layer=lay, modal_a=a, modal_b=b, jsd=round(0.5 * kl(p, m) + 0.5 * kl(q, m), 3)))
    jsd = pd.DataFrame(jrows); jsd.to_csv(out / "tables" / "A2_jsd.csv", index=False)
    # figure: main layer top units per modal
    main_layer = "statement" if "statement" in summary["layers"] else summary["layers"][0]
    sub = inv[inv.layer == main_layer]
    fig, axes = plt.subplots(2, 3, figsize=(11, 6))
    for ax, modal in zip(axes.ravel(), SIX):
        s = sub[(sub.modal == modal)].head(8).iloc[::-1]
        ax.barh(s.unit, s.n, color="#24507A"); ax.set_title(f"{modal} (n={int(s.modal_n.iloc[0]) if len(s) else 0})")
        ax.tick_params(axis="y", labelsize=7)
    fig.suptitle(f"X-A  Top units per modal — {LAYER_LABEL.get(main_layer, main_layer)}, 2014–2026 ({UNITS[U]})")
    savefig(fig, out / "figures" / "A_top_units.png")
    js = jsd[jsd.layer == main_layer].jsd
    summary["blocks"]["A"] = dict(main_layer=main_layer, jsd_min=float(js.min()) if len(js) else None,
                                  jsd_max=float(js.max()) if len(js) else None,
                                  top_unit_per_modal={m: (sub[sub.modal == m].unit.iloc[0] if (sub.modal == m).any() else None) for m in SIX},
                                  top_share_per_modal={m: (float(sub[sub.modal == m].share.iloc[0]) if (sub.modal == m).any() else None) for m in SIX})


def block_B(tk, dl, out, summary, U):
    res = {}
    stmt_dates = None
    for T in ("T1", "T3"):
        st = tk[(tk.layer == "statement") & period_mask(tk.date, T)]
        sd = dl[(dl.layer == "statement") & period_mask(dl.date, T)].sort_values("date").drop_duplicates("doc_id")
        if len(sd) < 10: continue
        cnt = st.groupby(["doc_id", "unit"]).size().unstack(fill_value=0).reindex(sd.doc_id, fill_value=0)
        tot = cnt.sum(axis=1)
        totals = cnt.sum().sort_values(ascending=False)
        top = totals.head(10).index.tolist()
        for m in SIX:  # guarantee each modal's leading construction is visible (e.g. should+help, may+warrant)
            cand = [u for u in totals.index if modal_of_unit(u) == m]
            if cand and cand[0] not in top and totals[cand[0]] >= 5: top.append(cand[0])
        top = top[:14]
        share = cnt.div(tot.replace(0, np.nan), axis=0).fillna(0)
        dens = cnt.div(sd.set_index("doc_id").n_tokens, axis=0) * 1000
        long = pd.concat([cnt[top].stack().rename("count"), dens[top].stack().rename("density"), share[top].stack().rename("share")], axis=1).reset_index()
        long.columns = ["doc_id", "unit", "count", "density", "share"]; long["date"] = long.doc_id.map(sd.set_index("doc_id").date)
        long["period"] = T; long.to_csv(out / "tables" / f"B1_series_{T}.csv", index=False)
        # change points on shares
        dates = sd.date.tolist(); n = len(dates)
        cps = []
        for u in top:
            y = share[u].values
            if y.std() == 0: continue
            z = (y - y.mean()) / y.std()
            bk = rpt.Pelt(model="l2", min_size=4, jump=1).fit(z.reshape(-1, 1)).predict(pen=2 * math.log(n))
            for b in bk[:-1]:
                before, after = y[max(0, b - 8):b].mean(), y[b:b + 8].mean()
                docs_before, docs_after = sd.doc_id.iloc[max(0, b - 8):b], sd.doc_id.iloc[b:b + 8]
                s_after = st[(st.unit == u) & st.doc_id.isin(docs_after)].sentence.map(norm_sentence).value_counts()
                s_before = st[(st.unit == u) & st.doc_id.isin(docs_before)].sentence.map(norm_sentence).value_counts()
                ex_after = st[(st.unit == u) & st.doc_id.isin(docs_after)].sentence.iloc[0] if len(s_after) else ""
                ex_before = st[(st.unit == u) & st.doc_id.isin(docs_before)].sentence.iloc[0] if len(s_before) else ""
                # nearest event
                ev = min(EVENTS, key=lambda e: abs(pd.Timestamp(e[0]) - pd.Timestamp(dates[b])))
                gap_days = abs((pd.Timestamp(ev[0]) - pd.Timestamp(dates[b])).days)
                cps.append(dict(period=T, unit=u, break_date=dates[b], meeting_index=int(b), share_before=round(before, 3), share_after=round(after, 3),
                                direction="up" if after > before else "down", nearest_event=ev[1], event_date=ev[0], days_to_event=int(gap_days),
                                within_1_meeting=bool(gap_days <= 50),
                                sentence_after=(ex_after[:220] if after > before else ""), sentence_before=(ex_before[:220] if after < before else "")))
        cpdf = pd.DataFrame(cps); cpdf.to_csv(out / "tables" / f"B2_changepoints_{T}.csv", index=False)
        # figure: stacked bars
        fig, ax = plt.subplots(figsize=(12, 4.6))
        other = 1 - share[top].sum(axis=1)
        bottom = np.zeros(n); cmap = plt.get_cmap("tab20")
        x = np.arange(n)
        for i, u in enumerate(top):
            ax.bar(x, share[u].values, bottom=bottom, width=0.9, color=cmap(i % 20), label=u); bottom += share[u].values
        ax.bar(x, other.values, bottom=bottom, width=0.9, color="#CCCCCC", label="other")
        yrs = [d[:4] for d in dates]; ticks = [i for i in range(n) if i == 0 or yrs[i] != yrs[i - 1]]
        ax.set_xticks(ticks); ax.set_xticklabels([yrs[i] for i in ticks], rotation=0)
        for c in cps:
            if c["period"] == T: ax.axvline(c["meeting_index"] - 0.5, color="k", lw=0.6, ls="--", alpha=0.6)
        for d, lab in EVENTS:
            if dates[0] <= d <= dates[-1]:
                i = int(np.searchsorted(np.array(dates), d))
                ax.text(i, 0.99, lab, rotation=90, fontsize=6, va="top", ha="center", color="#222", bbox=dict(facecolor="white", alpha=0.7, lw=0, pad=1))
        ax.set_ylim(0, 1); ax.set_ylabel("share of six-modal tokens (N2)")
        ax.legend(fontsize=6, ncol=7, loc="upper center", bbox_to_anchor=(0.5, -0.12))
        fig.suptitle(f"X-B  Statement construction staircase — {UNITS[U]}, {PERIODS[T][0][:4]}–2026 (dashed = PELT change points)", y=1.02)
        savefig(fig, out / "figures" / f"B_staircase_{T}.png")
        res[T] = dict(top_units=top, n_meetings=n, changepoints=cps, n_cp=len(cps),
                      cp_within_1_meeting_of_event=int(sum(c["within_1_meeting"] for c in cps)))
        if T == "T1": stmt_dates = dates
    summary["blocks"]["B"] = res


def retention_curve(P: np.ndarray, kmax=24):
    r = []
    for k in range(1, kmax + 1):
        vals = []
        for t in range(P.shape[0] - k):
            base = P[t].sum()
            if base > 0: vals.append((P[t] & P[t + k]).sum() / base)
        r.append(np.mean(vals) if vals else np.nan)
    r = np.array(r)
    hl = np.nan
    for k in range(len(r)):
        if not np.isnan(r[k]) and r[k] < 0.5:
            prev = 1.0 if k == 0 else r[k - 1]
            hl = k + (prev - 0.5) / (prev - r[k]) if prev != r[k] else k + 1
            break
    return r, (float(hl) if not np.isnan(hl) else None)


def block_C(tk, dl, out, summary, U):
    st = tk[(tk.layer == "statement") & period_mask(tk.date, "T1")]
    sd = dl[(dl.layer == "statement") & period_mask(dl.date, "T1")].sort_values("date").drop_duplicates("doc_id")
    cnt = st.groupby(["doc_id", "unit"]).size().unstack(fill_value=0).reindex(sd.doc_id, fill_value=0)
    P = (cnt.values > 0)
    r_all, hl_all = retention_curve(P)
    rows = [dict(group="all constructions", k=k + 1, retention=r_all[k]) for k in range(len(r_all))]
    hls = {"all": hl_all}
    modal_of = np.array([modal_of_unit(u) for u in cnt.columns])
    for m in SIX:
        cols = modal_of == m
        if cols.sum() == 0: continue
        r, hl = retention_curve(P[:, cols]); hls[m] = hl
        rows += [dict(group=m, k=k + 1, retention=r[k]) for k in range(len(r))]
    # sentence-level retention
    sent = st.assign(ns=st.sentence.map(norm_sentence)).groupby(["doc_id", "ns"]).size().unstack(fill_value=0).reindex(sd.doc_id, fill_value=0)
    r_s, hl_s = retention_curve(sent.values > 0); hls["modal_sentences"] = hl_s
    rows += [dict(group="modal-bearing sentences", k=k + 1, retention=r_s[k]) for k in range(len(r_s))]
    pd.DataFrame(rows).to_csv(out / "tables" / "C1_retention.csv", index=False)
    # edit events
    ev = []
    for i in range(1, P.shape[0]):
        added = int((P[i] & ~P[i - 1]).sum()); removed = int((~P[i] & P[i - 1]).sum())
        ev.append(dict(date=sd.date.iloc[i], year=int(sd.date.iloc[i][:4]), added=added, removed=removed))
    ev = pd.DataFrame(ev); ev.to_csv(out / "tables" / "C2_edit_events.csv", index=False)
    by_year = ev.groupby("year")[["added", "removed"]].sum()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
    for g, s in pd.DataFrame(rows).groupby("group"):
        a1.plot(s.k, s.retention, marker=".", label=f"{g} (½ = {hls.get(g if g in SIX else ('all' if g.startswith('all') else 'modal_sentences'))})")
    a1.axhline(0.5, color="k", lw=0.5, ls=":"); a1.set_xlabel("meetings later (k)"); a1.set_ylabel("retention"); a1.legend(fontsize=6); a1.set_title("X-C retention of statement constructions")
    by_year.plot(kind="bar", ax=a2, color=["#2C6E5C", "#A8501F"]); a2.set_title("units added / removed between consecutive statements")
    savefig(fig, out / "figures" / "C_retention_edits.png")
    summary["blocks"]["C"] = dict(half_life=hls, edit_events_by_year={int(k): dict(added=int(v.added), removed=int(v.removed)) for k, v in by_year.iterrows()},
                                  n_units=int(P.shape[1]))


def block_D(tk, dl, out, summary, U):
    t1 = tk[period_mask(tk.date, "T1")]; d1 = dl[period_mask(dl.date, "T1")]
    ct = t1.groupby(["layer", "modal"]).size().unstack(fill_value=0).reindex(columns=SIX, fill_value=0)
    toks = d1.groupby("layer").n_tokens.sum()
    dens = ct.div(toks.reindex(ct.index), axis=0) * 1000
    tab = pd.concat([ct.add_suffix("_n"), dens.round(2).add_suffix("_per1k")], axis=1); tab["tokens"] = toks.reindex(ct.index)
    tab.to_csv(out / "tables" / "D1_layer_modal.csv")
    res = {}
    big = ct[ct.sum(axis=1) >= 200]
    if len(big) >= 2:
        chi2, p, dof, exp = stats.chi2_contingency(big.values)
        V = math.sqrt(chi2 / (big.values.sum() * (min(big.shape) - 1)))
        resid = pd.DataFrame((big.values - exp) / np.sqrt(exp), index=big.index, columns=big.columns)
        resid.round(1).to_csv(out / "tables" / "D2_std_residuals.csv")
        res.update(chi2=float(chi2), dof=int(dof), cramers_v=round(V, 3), n_layers=int(len(big)))
        fig, ax = plt.subplots(figsize=(7, 0.5 * len(big) + 1.5))
        im = ax.imshow(resid.values, cmap="RdBu_r", vmin=-25, vmax=25, aspect="auto")
        ax.set_xticks(range(len(SIX))); ax.set_xticklabels(SIX); ax.set_yticks(range(len(big))); ax.set_yticklabels([LAYER_LABEL.get(l, l) for l in big.index], fontsize=7)
        for i in range(resid.shape[0]):
            for j in range(resid.shape[1]): ax.text(j, i, f"{resid.values[i, j]:.0f}", ha="center", va="center", fontsize=7)
        plt.colorbar(im, ax=ax, label="standardised residual"); ax.set_title(f"X-D  layer × modal (χ²={chi2:.0f}, V={V:.3f})")
        savefig(fig, out / "figures" / "D_layer_residuals.png")
    # top units per layer
    rows = []
    for lay, sub in t1.groupby("layer"):
        for u, n in sub.unit.value_counts().head(10).items():
            rows.append(dict(layer=lay, unit=u, n=int(n), share=round(n / len(sub), 4)))
    pd.DataFrame(rows).to_csv(out / "tables" / "D3_top_units_by_layer.csv", index=False)
    # pragmatic contrast
    prag = []
    for (lay, modal), sub in t1[t1.modal.isin(["will", "would", "can", "could"])].groupby(["layer", "modal"]):
        if len(sub) < 20: continue
        prag.append(dict(layer=lay, modal=modal, n=len(sub), neg=sub.neg.mean(), question=sub.question.mean(), cond=sub.cond.mean(),
                         reported=sub.reported.mean(), contracted=sub.contracted.mean(),
                         subj_we_I=(sub.subj_type == "we_I").mean(), subj_person=(sub.subj_type == "person").mean(),
                         subj_committee_fed=sub.subj_type.isin(["committee", "fed"]).mean(), subj_econ=(sub.subj_type == "econ").mean(),
                         passive=sub.passive.mean(), perfect=sub.perfect.mean()))
    pd.DataFrame(prag).round(3).to_csv(out / "tables" / "D4_pragmatic_contrast.csv", index=False)
    summary["blocks"]["D"] = res


def screen(series: pd.DataFrame, macro: pd.DataFrame):
    df = series.merge(macro, on="doc_id", how="left")
    rows = []
    for (level, key, unit), s in df.groupby(["level", "key", "unit"]):
        s = s.sort_values("date")
        for T in PERIODS:
            st = s[period_mask(s.date, T)]
            if len(st) < MIN_N: continue
            zero = float((st["count"] == 0).mean())
            for mv, col in MACRO_VARS.items():
                c = corr_pair(st.density, st[col])
                rows.append(dict(level=level, key=key, unit=unit, period=T, macro=mv, n_tokens=int(st["count"].sum()), zero_share=round(zero, 3), **c))
    scr = pd.DataFrame(rows)
    if len(scr):
        scr["q_rho"] = np.nan
        for (T, mv, level), idx in scr.groupby(["period", "macro", "level"]).groups.items():
            scr.loc[idx, "q_rho"] = bh(scr.loc[idx, "p_rho"])
        scr["eligible"] = (scr.n_tokens >= MIN_TOKENS) & (scr.zero_share <= MAX_ZERO)
    return scr


def confirmed_table(scr: pd.DataFrame):
    """A unit x macro is 'confirmed' if Spearman is significant (p<.05) with the same sign in T1 and T2 and eligible in both."""
    if not len(scr): return pd.DataFrame()
    p = scr.pivot_table(index=["level", "key", "unit", "macro"], columns="period", values=["rho", "p_rho", "eligible", "n_tokens", "zero_share"], aggfunc="first")
    out = []
    for idx, row in p.iterrows():
        try:
            r1, r2, p1, p2 = row[("rho", "T1")], row[("rho", "T2")], row[("p_rho", "T1")], row[("p_rho", "T2")]
            e1, e2 = bool(row[("eligible", "T1")]), bool(row[("eligible", "T2")])
        except KeyError:
            continue
        if any(pd.isna(v) for v in (r1, r2, p1, p2)): continue
        rh1 = row[("rho", "H1")] if ("rho", "H1") in row.index else np.nan
        rh2 = row[("rho", "H2")] if ("rho", "H2") in row.index else np.nan
        halves_ok = (not pd.isna(rh1)) and (not pd.isna(rh2)) and np.sign(rh1) == np.sign(r2) and np.sign(rh2) == np.sign(r2)
        conf = e1 and e2 and p1 < .05 and p2 < .05 and np.sign(r1) == np.sign(r2) and halves_ok
        r3 = row[("rho", "T3")] if ("rho", "T3") in row.index else np.nan
        out.append(dict(level=idx[0], key=idx[1], unit=idx[2], macro=idx[3], rho_T1=round(r1, 3), p_T1=round(p1, 4), rho_T2=round(r2, 3), p_T2=round(p2, 4),
                        rho_T3=(round(r3, 3) if not pd.isna(r3) else np.nan), rho_H1=(round(rh1, 3) if not pd.isna(rh1) else np.nan), rho_H2=(round(rh2, 3) if not pd.isna(rh2) else np.nan),
                        n_tokens_T1=int(row[("n_tokens", "T1")]), zero_share_T1=row[("zero_share", "T1")],
                        T1_only=bool(e1 and p1 < .05 and not (e2 and p2 < .05 and np.sign(r1) == np.sign(r2))),
                        era_composition=bool(e1 and e2 and p1 < .05 and p2 < .05 and np.sign(r1) == np.sign(r2) and not halves_ok),
                        confirmed=bool(conf)))
    return pd.DataFrame(out)


def block_E(tk, dl, out, summary, U, macro):
    res = {}
    # modal-level series are always computed (baseline), unit-level for the scenario's U
    tk_m = tk.assign(unit=tk.modal)
    ser_layer_m = unit_series(tk_m, dl, "layer"); ser_genre_m = unit_series(tk_m, dl, "genre")
    ser_layer_u = unit_series(tk, dl, "layer", extra_units=[u for u in tk.unit.unique() if "be+appropriate" in u])
    ser_genre_u = unit_series(tk, dl, "genre")
    ser_m = pd.concat([ser_layer_m, ser_genre_m], ignore_index=True); ser_u = pd.concat([ser_layer_u, ser_genre_u], ignore_index=True)
    scr_m = screen(ser_m, macro); scr_m["unit_level"] = "modal"
    if U == "U1":   # unit == modal: avoid double-counting the modal-level screen
        scr_u = scr_m.iloc[0:0].copy()
    else:
        scr_u = screen(ser_u[ser_u.unit != "ALL"], macro); scr_u["unit_level"] = U
    scr = pd.concat([scr_m, scr_u], ignore_index=True)
    scr.round(4).to_csv(out / "tables" / "E1_screen.csv", index=False)
    conf_m = confirmed_table(scr_m); conf_u = confirmed_table(scr_u)
    conf = pd.concat([conf_m.assign(unit_level="modal"), conf_u.assign(unit_level=U)], ignore_index=True) if (len(conf_u) or len(conf_m)) else pd.DataFrame()
    if len(conf): conf.to_csv(out / "tables" / "E2_confirmed.csv", index=False)
    # Kawamura test: aggregate density (ALL) per genre / layer vs CFNAI and VIX
    kaw = scr_m[(scr_m.unit == "ALL")].copy()
    kaw.round(4).to_csv(out / "tables" / "E3_kawamura_aggregate.csv", index=False)
    res["kawamura"] = [dict(level=r.level, key=r.key, period=r.period, macro=r.macro, rho=round(r.rho, 3) if not pd.isna(r.rho) else None,
                            p=round(r.p_rho, 4) if not pd.isna(r.p_rho) else None, n=int(r.n)) for r in kaw.itertuples()]
    # main table: per layer, ALL + top-8 units + be+appropriate units, T1/T2/T3 rho + HAC
    mrows = []
    dfu = ser_u.merge(macro, on="doc_id", how="left")
    for key, s_all in dfu[dfu.level == "layer"].groupby("key"):
        counts = s_all[period_mask(s_all.date, "T1")].groupby("unit")["count"].sum().sort_values(ascending=False)
        units = ["ALL"] + [u for u in counts.index if u != "ALL"][:8] + [u for u in counts.index if "be+appropriate" in u and u not in counts.index[:9]]
        for u in units:
            s = s_all[s_all.unit == u].sort_values("date")
            row = dict(layer=key, unit=u, n_tokens=int(counts.get(u, s["count"].sum())))
            for T in MAIN_PERIODS:
                st = s[period_mask(s.date, T)]
                row[f"zero_{T}"] = round(float((st["count"] == 0).mean()), 2) if len(st) else np.nan
                for mv, col in MACRO_VARS.items():
                    c = corr_pair(st.density, st[col]); row[f"rho_{mv}_{T}"] = round(c["rho"], 3) if not pd.isna(c["rho"]) else np.nan; row[f"p_{mv}_{T}"] = round(c["p_rho"], 4) if not pd.isna(c["p_rho"]) else np.nan
                if T in ("T1", "T2"):
                    m = hac(st.density, st[[MACRO_VARS["cfnai"], MACRO_VARS["vix"]]]) if len(st) >= 12 else None
                    if m is not None:
                        row[f"hac_b_cfnai_{T}"] = round(m.params[1], 4); row[f"hac_p_cfnai_{T}"] = round(m.pvalues[1], 4)
                        row[f"hac_b_vix_{T}"] = round(m.params[2], 4); row[f"hac_p_vix_{T}"] = round(m.pvalues[2], 4)
            mrows.append(row)
    main = pd.DataFrame(mrows); main.to_csv(out / "tables" / "E4_main_constructions.csv", index=False)
    # figures
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5))
    for ax, (mv, T) in zip(axes.ravel(), [("cfnai", "T1"), ("cfnai", "T2"), ("vix", "T1"), ("vix", "T2")]):
        sub = scr_m[(scr_m.macro == mv) & (scr_m.period == T) & (scr_m.level == "layer") & (scr_m.unit != "ALL")]
        piv = sub.pivot_table(index="unit", columns="key", values="rho").reindex(SIX)
        if piv.empty: ax.axis("off"); continue
        im = ax.imshow(piv.values.astype(float), cmap="RdBu_r", vmin=-0.6, vmax=0.6, aspect="auto")
        ax.set_xticks(range(piv.shape[1])); ax.set_xticklabels([LAYER_LABEL.get(c, c) for c in piv.columns], rotation=30, ha="right", fontsize=6)
        ax.set_yticks(range(len(SIX))); ax.set_yticklabels(SIX)
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                v = piv.values[i, j]
                if not np.isnan(v):
                    pv = sub[(sub.unit == piv.index[i]) & (sub.key == piv.columns[j])].p_rho.iloc[0]
                    ax.text(j, i, f"{v:.2f}{'*' if pv < .05 else ''}", ha="center", va="center", fontsize=6)
        ax.set_title(f"Spearman ρ: modal density × {mv.upper()}  [{T}{' excl. 2020' if T == 'T2' else ''}]")
    plt.colorbar(im, ax=axes, shrink=0.6)
    fig.suptitle("X-E  modal-level correlations by layer (N1 density)"); fig.savefig(out / "figures" / "E_modal_heatmap.png", bbox_inches="tight"); plt.close(fig)
    # overlay figure for the strongest confirmed VIX units
    if len(conf_u):
        cand = conf_u[(conf_u.macro == "vix") & conf_u.confirmed & (conf_u.level == "layer")].assign(a=lambda d: d.rho_T2.abs()).sort_values("a", ascending=False).head(4)
        if len(cand):
            fig, axes = plt.subplots(len(cand), 1, figsize=(11, 2.3 * len(cand)), squeeze=False)
            for ax, r in zip(axes.ravel(), cand.itertuples()):
                s = dfu[(dfu.level == "layer") & (dfu.key == r.key) & (dfu.unit == r.unit) & period_mask(dfu.date, "T1")].sort_values("date")
                x = pd.to_datetime(s.date)
                ax.bar(x, s.density, width=20, color="#24507A", label=f"{r.unit} density (per 1k)")
                ax2 = ax.twinx(); ax2.plot(x, s[MACRO_VARS["vix"]], color="#A8501F", lw=1, label="VIX pre-28d"); ax2.set_ylabel("VIX", color="#A8501F")
                ax.set_title(f"{LAYER_LABEL.get(r.key, r.key)} · {r.unit}   ρ(VIX) T1={r.rho_T1}, excl-2020={r.rho_T2}", fontsize=8)
                ax.set_ylabel("per 1k")
            fig.suptitle("X-E  confirmed VIX correlates (density vs pre-meeting VIX)"); savefig(fig, out / "figures" / "E_vix_overlay.png")
    n_hits_T1 = int(((scr.period == "T1") & scr.eligible & (scr.q_rho < .05)).sum()) if len(scr) else 0
    cl = conf[conf.level == "layer"] if len(conf) else conf
    res.update(n_screen_rows=int(len(scr)), n_bh_hits_T1=n_hits_T1,
               n_confirmed_vix=int(cl[(cl.macro == "vix") & cl.confirmed].shape[0]) if len(cl) else 0,
               n_confirmed_cfnai=int(cl[(cl.macro == "cfnai") & cl.confirmed].shape[0]) if len(cl) else 0,
               n_T1_only=int(cl.T1_only.sum()) if len(cl) else 0,
               n_era_composition=int(cl.era_composition.sum()) if len(cl) else 0,
               confirmed_top=(cl[cl.confirmed].assign(a=lambda d: d.rho_T2.abs()).sort_values("a", ascending=False).head(12)
                              .drop(columns="a").to_dict("records") if len(cl) else []),
               confirmed_modal_level=(conf_m[conf_m.confirmed & (conf_m.level == "layer")].to_dict("records") if len(conf_m) else []))
    summary["blocks"]["E"] = res


def block_F(tk, dl, out, summary, macro):
    ba = tk[(tk.predicate == "be+appropriate") & tk.modal.isin(["will", "would", "may", "could"])].assign(unit=lambda d: d.modal + "+be+appropriate")
    if len(ba) < 20:
        summary["blocks"]["F"] = dict(note="too few be+appropriate tokens"); return
    ser = unit_series(ba, dl, "layer", min_tokens=10)
    ser = ser[ser.unit != "ALL"].merge(macro, on="doc_id", how="left")
    rows = []
    for (key, u), s in ser.groupby(["key", "unit"]):
        s = s.sort_values("date"); row = dict(layer=key, unit=u, n_tokens=int(s[period_mask(s.date, "T1")]["count"].sum()))
        for T in ("T1", "T2"):
            st = s[period_mask(s.date, T)]
            for mv, col in MACRO_VARS.items():
                c = corr_pair(st.density, st[col]); row[f"rho_{mv}_{T}"] = round(c["rho"], 3) if not pd.isna(c["rho"]) else np.nan; row[f"p_{mv}_{T}"] = round(c["p_rho"], 4) if not pd.isna(c["p_rho"]) else np.nan
            row[f"zero_{T}"] = round(float((st["count"] == 0).mean()), 2) if len(st) else np.nan
        rows.append(row)
    F1 = pd.DataFrame(rows); F1.to_csv(out / "tables" / "F1_be_appropriate.csv", index=False)
    cnt = ba[period_mask(ba.date, "T1")].groupby(["layer", "modal"]).size().unstack(fill_value=0)
    cnt.to_csv(out / "tables" / "F2_be_appropriate_counts.csv")
    # figure: annual counts per modal for up to 3 layers + VIX
    layers = [l for l in ["min_participants", "min_committee", "statement", "pc_chair", "speech_chair"] if l in ba.layer.unique()][:3]
    if layers:
        fig, axes = plt.subplots(1, len(layers), figsize=(4.2 * len(layers), 3.4), squeeze=False)
        vix_y = macro.merge(dl[["doc_id", "date"]].drop_duplicates(), on="doc_id").assign(year=lambda d: d.date.str[:4].astype(int)).groupby("year")[MACRO_VARS["vix"]].mean()
        for ax, lay in zip(axes.ravel(), layers):
            yc = ba[ba.layer == lay].groupby(["year", "modal"]).size().unstack(fill_value=0).reindex(range(2014, 2027), fill_value=0)
            yc.plot(ax=ax, marker=".", lw=1); ax.set_title(LAYER_LABEL.get(lay, lay), fontsize=8); ax.set_ylabel("tokens / year")
            vy = vix_y.reindex(yc.index)
            ax2 = ax.twinx(); ax2.plot(vy.index, vy.values, color="#A8501F", ls=":", lw=1); ax2.set_ylabel("VIX (yr mean)", color="#A8501F")
            ax.legend(fontsize=6)
        fig.suptitle("X-F  modal + be appropriate by layer (annual tokens) with VIX"); savefig(fig, out / "figures" / "F_be_appropriate.png")
    summary["blocks"]["F"] = dict(counts=cnt.to_dict(), table=F1.to_dict("records"))


def block_G(tk, dl, out, summary, macro, monthly):
    mon = monthly.copy(); mon["ym"] = pd.to_datetime(mon.date).dt.to_period("M")
    mon = mon.set_index("ym")[["CFNAIMA3", "VIX_M"]]
    tk_m = tk.assign(unit=tk.modal)
    ser = pd.concat([unit_series(tk_m, dl, "genre"), unit_series(tk, dl, "genre")[lambda d: d.unit != "ALL"]], ignore_index=True)
    # restrict units: modal-level + top-6 scenario units by count
    top_units = ser[~ser.unit.isin(SIX + ["ALL"])].groupby("unit")["count"].sum().sort_values(ascending=False).head(6).index.tolist()
    ser = ser[ser.unit.isin(SIX + ["ALL"] + top_units)]
    ser["ym"] = pd.to_datetime(ser.date).dt.to_period("M")
    rows, grows = [], []
    for (key, unit), s in ser.groupby(["key", "unit"]):
        s = s.sort_values("date")
        for T in ("T1", "T2"):
            st = s[period_mask(s.date, T)]
            if len(st) < MIN_N or (st["count"] == 0).mean() > MAX_ZERO or st["count"].sum() < MIN_TOKENS: continue
            for mv, col in (("cfnai", "CFNAIMA3"), ("vix", "VIX_M")):
                for k in range(-9, 10):
                    mac = [mon[col].get(ym + k, np.nan) for ym in st.ym]
                    c = corr_pair(st.density, mac)
                    rows.append(dict(key=key, unit=unit, period=T, macro=mv, k=k, **c))
            # Granger (lag 2) both directions with contemporaneous monthly macro
            for mv, col in (("cfnai", "CFNAIMA3"), ("vix", "VIX_M")):
                mac = np.array([mon[col].get(ym, np.nan) for ym in st.ym], float); y = st.density.values.astype(float)
                ok = ~np.isnan(mac)
                if ok.sum() < MIN_N: continue
                d = pd.DataFrame({"text": y[ok], "macro": mac[ok]})
                try:
                    g1 = grangercausalitytests(d[["macro", "text"]], maxlag=2, verbose=False)[2][0]["ssr_ftest"][1]
                    g2 = grangercausalitytests(d[["text", "macro"]], maxlag=2, verbose=False)[2][0]["ssr_ftest"][1]
                except Exception:
                    g1 = g2 = np.nan
                grows.append(dict(key=key, unit=unit, period=T, macro=mv, p_text_to_macro=round(float(g1), 4), p_macro_to_text=round(float(g2), 4), n=int(ok.sum())))
    ccf = pd.DataFrame(rows); ccf.round(4).to_csv(out / "tables" / "G1_ccf.csv", index=False)
    gr = pd.DataFrame(grows)
    if len(gr):
        gr["q_text_to_macro"] = bh(gr.p_text_to_macro); gr["q_macro_to_text"] = bh(gr.p_macro_to_text)
        gr.to_csv(out / "tables" / "G2_granger.csv", index=False)
    peaks = []
    if len(ccf):
        for (key, unit, T, mv), s in ccf.groupby(["key", "unit", "period", "macro"]):
            s = s.dropna(subset=["r"])
            if not len(s): continue
            best = s.iloc[s.r.abs().argmax()]
            if best.p_r < .05 and best.p_rho < .05:
                peaks.append(dict(key=key, unit=unit, period=T, macro=mv, k=int(best.k), r=round(best.r, 3), rho=round(best.rho, 3)))
    summary["blocks"]["G"] = dict(peaks_T2=[p for p in peaks if p["period"] == "T2"][:20],
                                  granger_text_to_macro_q10=(gr[(gr.period == "T2") & (gr.q_text_to_macro < .10)].to_dict("records") if len(gr) else []))


# ----------------------------------------------------------------------------------------------
def readme(summary, out):
    S, U = summary["S"], summary["U"]; b = summary["blocks"]
    L = [f"# 시나리오 {S}_{U} — {summary['name']} × {summary['unit']}", "", f"> {summary['note']}", ""]
    L += ["## 코퍼스 (T1 2014–2026)", "", "| 층위 | 문서 | 토큰 | 6대 조동사 | per 1k |", "|---|---:|---:|---:|---:|"]
    for r in summary["corpus"]:
        L.append(f"| {r['label']} | {r['n_docs']} | {r['tokens']:,} | {r['six_modal_tokens']:,} | {r['per_1k']} |")
    L.append("")
    if "A" in b:
        a = b["A"]; L += ["## X-A 구문 인벤토리", "", f"- 주 층위 {LAYER_LABEL.get(a['main_layer'], a['main_layer'])}: 조동사별 1위 단위 " +
                          ", ".join(f"{m}→{a['top_unit_per_modal'][m]} ({(a['top_share_per_modal'][m] or 0):.0%})" for m in SIX if a['top_unit_per_modal'].get(m)) +
                          (f"; 조동사 간 JSD {a['jsd_min']:.2f}–{a['jsd_max']:.2f}" if a.get('jsd_min') is not None else ""), ""]
    if "B" in b and "T1" in b["B"]:
        bb = b["B"]["T1"]; L += ["## X-B 구문 계단 (성명서)", "", f"- 회의 {bb['n_meetings']}회, 상위 단위 {len(bb['top_units'])}개에서 PELT 변화점 {bb['n_cp']}개, 그중 정책 사건 ±1회의 이내 {bb['cp_within_1_meeting_of_event']}개.", ""]
        L += ["| 단위 | 변화점 | 전→후 점유율 | 최근접 사건 | 원인 문장 |", "|---|---|---|---|---|"]
        for c in bb["changepoints"]:
            sent = (c["sentence_after"] or c["sentence_before"]).replace("|", "/")
            L.append(f"| {c['unit']} | {c['break_date']} | {c['share_before']:.2f}→{c['share_after']:.2f} | {c['nearest_event']} ({c['days_to_event']}d) | {sent[:140]} |")
        L.append("")
    if "C" in b and "half_life" in b["C"]:
        hl = b["C"]["half_life"]; L += ["## X-C 지속성", "", "- 보유율 반감기(회의 수): " + ", ".join(f"{k}={('%.1f' % v) if v else '≥24'}" for k, v in hl.items()), ""]
    if "D" in b and b["D"]:
        d = b["D"]; L += ["## X-D 층위 분업", "", f"- 층위({d['n_layers']}) × 조동사 χ²={d['chi2']:.0f}, Cramér's V={d['cramers_v']}", ""]
    if "E" in b:
        e = b["E"]; L += ["## X-E 구문 × 거시", ""]
        kaw = [k for k in e["kawamura"] if k["level"] == "genre" and k["macro"] == "cfnai" and k["period"] in MAIN_PERIODS]
        L.append("- Kawamura 검정(총 조동사 밀도 × CFNAI, Spearman): " + "; ".join(f"{k['key']} {k['period']} ρ={k['rho']} (p={k['p']})" for k in kaw))
        kawv = [k for k in e["kawamura"] if k["level"] == "genre" and k["macro"] == "vix" and k["period"] in MAIN_PERIODS]
        kawh = [k for k in e["kawamura"] if k["level"] == "genre" and k["period"] in ("H1", "H2") and k["p"] is not None and k["p"] < .05]
        if kawh:
            L.append("- 반기별 유의(총 밀도): " + "; ".join(f"{k['key']} × {k['macro']} {k['period']} ρ={k['rho']} (p={k['p']})" for k in kawh))
        L.append("- 총 조동사 밀도 × VIX: " + "; ".join(f"{k['key']} {k['period']} ρ={k['rho']} (p={k['p']})" for k in kawv))
        L.append(f"- 전수 스크린 {e['n_screen_rows']}행(층위 수준 집계): T1 BH q<.05 적중 {e['n_bh_hits_T1']}; **확정**(T1·T2 유의·동부호 + 2014–19/2021–26 반기 동부호) VIX {e['n_confirmed_vix']}건 / CFNAI {e['n_confirmed_cfnai']}건; T1에서만 유의(2020 의존) {e['n_T1_only']}건; T1·T2 유의하나 반기 부호 불일치(시대 구성 효과) {e.get('n_era_composition', 0)}건")
        if e["confirmed_top"]:
            L += ["", "| 층위 | 단위 | 거시 | ρ T1 | ρ excl-2020 | ρ 2010– | ρ 2014–19 | ρ 2021–26 | 토큰 |", "|---|---|---|---:|---:|---:|---:|---:|---:|"]
            for c in e["confirmed_top"]:
                L.append(f"| {c['key']} | {c['unit']} | {c['macro']} | {c['rho_T1']} | {c['rho_T2']} | {c['rho_T3']} | {c.get('rho_H1')} | {c.get('rho_H2')} | {c['n_tokens_T1']} |")
        L.append("")
    if "F" in b and "table" in b["F"]:
        L += ["## X-F will/would + be appropriate", "", "| 층위 | 단위 | 토큰 | ρ VIX T1 | ρ VIX excl-2020 | ρ CFNAI T1 | 제로 비율 T1 |", "|---|---|---:|---:|---:|---:|---:|"]
        for r in b["F"]["table"]:
            L.append(f"| {r['layer']} | {r['unit']} | {r['n_tokens']} | {r.get('rho_vix_T1')} (p={r.get('p_vix_T1')}) | {r.get('rho_vix_T2')} (p={r.get('p_vix_T2')}) | {r.get('rho_cfnai_T1')} | {r.get('zero_T1')} |")
        L.append("")
    if "G" in b:
        g = b["G"]; L += ["## X-G 선행성 (부록)", "", f"- excl-2020 CCF 피크(Pearson·Spearman 동시 유의) {len(g['peaks_T2'])}건; Granger text→macro q<.10 {len(g['granger_text_to_macro_q10'])}건", ""]
    (out / "README.md").write_text("\n".join(L), encoding="utf-8")


def run_scenario(S, U, tokens, docs, macro, monthly):
    cfg = SCENARIOS[S]; layers = cfg["layers"]
    out = SCEN / f"{S}_{U}"; (out / "tables").mkdir(parents=True, exist_ok=True); (out / "figures").mkdir(exist_ok=True)
    tk = tokens[tokens.layer.isin(layers) & tokens.modal.isin(SIX)].copy(); tk["unit"] = unit_key(tk, U)
    dl = docs[docs.layer.isin(layers)].copy()
    summary = dict(S=S, U=U, name=cfg["name"], layers=layers, unit=UNITS[U], note=cfg["note"], blocks={})
    t0 = time.time()
    corpus_table(tk, dl, out, summary)
    block_A(tk, out, summary, U)
    if "statement" in layers:
        block_B(tk, dl, out, summary, U); block_C(tk, dl, out, summary, U)
    else:
        summary["blocks"]["B"] = {"note": "no statement layer"}; summary["blocks"]["C"] = {"note": "no statement layer"}
    block_D(tk, dl, out, summary, U)
    block_E(tk, dl, out, summary, U, macro)
    block_F(tk, dl, out, summary, macro)
    block_G(tk, dl, out, summary, macro, monthly)
    summary["runtime_s"] = round(time.time() - t0, 1)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    readme(summary, out)
    print(f"{S}_{U} done in {summary['runtime_s']}s", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", default="all"); ap.add_argument("--unit", default="all")
    a = ap.parse_args()
    Ss = list(SCENARIOS) if a.corpus == "all" else a.corpus.split(","); Us = list(UNITS) if a.unit == "all" else a.unit.split(",")
    tokens = load_tokens_v3(); docs = load_docs_v3(); macro = load_macro(); monthly = pd.read_csv(TAB / "macro_monthly.csv")
    for S in Ss:
        for U in Us:
            run_scenario(S, U, tokens, docs, macro, monthly)


if __name__ == "__main__":
    main()
