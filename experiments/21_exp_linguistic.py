"""
21_exp_linguistic.py — Corpus-linguistic experiment family L1–L9 (Phase 14; docs/12 §3).

Every block takes a context `ctx` (see 23_run_program.py) with:
  ctx.tk   six-modal tokens of the scenario layers (all years)      ctx.tk9  nine-modal tokens
  ctx.dl   document x layer denominators                          ctx.U / ctx.unit_col ("U1"|"U2"|"U3")
  ctx.layers, ctx.main_layer, ctx.out (Path), ctx.summary (dict), ctx.stmt_sents (statement sentences or None)
and writes tables to ctx.out/tables/L*_*.csv, figures to ctx.out/figures/L*_*.png, and a compact summary to ctx.summary["L*"].
"""
from __future__ import annotations
import math, re, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util
_s = importlib.util.spec_from_file_location("pc", Path(__file__).resolve().parent / "20_program_common.py"); pc = importlib.util.module_from_spec(_s); _s.loader.exec_module(pc)
SIX, NINE, EVENTS, LAYER_LABEL = pc.SIX, pc.NINE, pc.EVENTS, pc.LAYER_LABEL
plt.rcParams.update({"figure.dpi": 100, "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9})


def _fig(fig, ctx, name):
    (ctx.out / "figures").mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(ctx.out / "figures" / f"{name}.png", bbox_inches="tight"); plt.close(fig)


def _t1(df): return df[pc.period_mask(df.date, "T1")]


# ----------------------------------------------------------------------------------------------
def L1_corpus_description(ctx):
    tk, tk9, dl = _t1(ctx.tk), _t1(ctx.tk9), _t1(ctx.dl)
    rows, per_modal, yearly = [], [], []
    for lay in ctx.layers:
        d = dl[dl.layer == lay]; t = tk[tk.layer == lay]; t9 = tk9[tk9.layer == lay]
        toks = int(d.n_tokens.sum())
        lo, hi = pc.poisson_ci(len(t), toks)
        rows.append(dict(layer=lay, label=LAYER_LABEL.get(lay, lay), n_docs=int(d.doc_id.nunique()), tokens=toks, sentences=int(d.n_sents.sum()),
                         six_modal=len(t), nine_modal=len(t9), pmw=round(pc.pmw(len(t), toks), 1), ci_lo=round(lo, 1), ci_hi=round(hi, 1), per1k=round(len(t) / max(toks, 1) * 1000, 2)))
        sizes = d.groupby("doc_id").n_tokens.sum()
        for m in NINE:
            c = t9[t9.modal == m].groupby("doc_id").size().reindex(sizes.index, fill_value=0)
            lo, hi = pc.poisson_ci(int(c.sum()), toks)
            per_modal.append(dict(layer=lay, modal=m, n=int(c.sum()), pmw=round(pc.pmw(c.sum(), toks), 1), ci_lo=round(lo, 1), ci_hi=round(hi, 1),
                                  DP=round(pc.dispersion_dp(c.values, sizes.values), 3), docs_with=int((c > 0).sum()), n_docs=len(sizes)))
        for yr, dy in d.groupby("year"):
            ty = t[t.year == yr]; toks_y = int(dy.n_tokens.sum())
            r = dict(layer=lay, year=int(yr), tokens=toks_y, six_modal=len(ty), pmw=round(pc.pmw(len(ty), toks_y), 1))
            for m in SIX: r[f"{m}_pmw"] = round(pc.pmw((ty.modal == m).sum(), toks_y), 1)
            yearly.append(r)
    L1 = pd.DataFrame(rows); pm = pd.DataFrame(per_modal); yr = pd.DataFrame(yearly)
    pc.save(L1, ctx.out, "L1_corpus"); pc.save(pm, ctx.out, "L1_modal_pmw_dp"); pc.save(yr, ctx.out, "L1_yearly_pmw")
    ctx.summary["L1"] = dict(layers=L1.to_dict("records"),
                             modal_pmw={lay: {r.modal: r.pmw for r in pm[pm.layer == lay].itertuples()} for lay in ctx.layers},
                             dp={lay: {r.modal: r.DP for r in pm[(pm.layer == lay) & pm.modal.isin(SIX)].itertuples()} for lay in ctx.layers})


# ----------------------------------------------------------------------------------------------
def L2_keyness_division(ctx):
    tk, dl = _t1(ctx.tk), _t1(ctx.dl)
    res = {}
    toks = dl.groupby("layer").n_tokens.sum()
    rows = []
    if len(ctx.layers) >= 2:
        for lay in ctx.layers:
            n1 = int(toks.get(lay, 0)); n2 = int(toks.sum() - n1)
            if n1 == 0 or n2 == 0: continue
            tin, tout = tk[tk.layer == lay], tk[tk.layer != lay]
            items = list(SIX)
            if ctx.U != "U1":
                items += tin[ctx.unit_col].value_counts().head(20).index.tolist()
            for it in items:
                col = "modal" if it in SIX else ctx.unit_col
                a = int((tin[col] == it).sum()); b = int((tout[col] == it).sum())
                if a + b < 5: continue
                k = pc.keyness(a, n1, b, n2)
                rows.append(dict(layer=lay, item=it, kind=("modal" if it in SIX else "unit"), freq_in=a, tokens_in=n1, freq_out=b, tokens_out=n2,
                                 pmw_in=round(pc.pmw(a, n1), 1), pmw_out=round(pc.pmw(b, n2), 1), **k))
        key = pd.DataFrame(rows)
        if len(key):
            key["q"] = np.nan
            for lay, idx in key.groupby("layer").groups.items(): key.loc[idx, "q"] = pc.bh(key.loc[idx, "p"])
            pc.save(key.round(4), ctx.out, "L2_keyness")
            res["keyness_top"] = {lay: key[(key.layer == lay) & (key.kind == "modal")].sort_values("LL", ascending=False).head(3)[["item", "sign", "LL", "log_ratio"]].to_dict("records") for lay in ctx.layers}
    ct = tk.groupby(["layer", "modal"]).size().unstack(fill_value=0).reindex(columns=SIX, fill_value=0)
    big = ct[ct.sum(axis=1) >= 200]
    if len(big) >= 2:
        chi2, p, dof, exp = stats.chi2_contingency(big.values)
        V = math.sqrt(chi2 / (big.values.sum() * (min(big.shape) - 1)))
        resid = pd.DataFrame((big.values - exp) / np.sqrt(exp), index=big.index, columns=big.columns)
        pc.save(resid.round(2).reset_index(), ctx.out, "L2_std_residuals"); pc.save(big.reset_index(), ctx.out, "L2_layer_modal_counts")
        res.update(chi2=round(float(chi2), 1), dof=int(dof), p=float(p), cramers_v=round(V, 3), n_layers=int(len(big)),
                   residual_max={lay: (resid.loc[lay].idxmax(), round(float(resid.loc[lay].max()), 1)) for lay in big.index})
        fig, ax = plt.subplots(figsize=(7, 0.5 * len(big) + 1.6))
        im = ax.imshow(resid.values, cmap="RdBu_r", vmin=-25, vmax=25, aspect="auto")
        ax.set_xticks(range(len(SIX))); ax.set_xticklabels(SIX); ax.set_yticks(range(len(big))); ax.set_yticklabels([LAYER_LABEL.get(l, l) for l in big.index], fontsize=7)
        for i in range(resid.shape[0]):
            for j in range(resid.shape[1]): ax.text(j, i, f"{resid.values[i, j]:.0f}", ha="center", va="center", fontsize=7)
        plt.colorbar(im, ax=ax, label="standardised residual"); ax.set_title(f"L2 layer × modal — χ²={chi2:.0f}, df={dof}, Cramér's V={V:.3f}")
        _fig(fig, ctx, "L2_residuals")
    ctx.summary["L2"] = res


# ----------------------------------------------------------------------------------------------
def L3_diachronic(ctx):
    tk, dl = ctx.tk, ctx.dl
    res = {}
    # meeting-level series per layer (T1) for MK
    ser = pc.unit_series(_t1(tk).assign(unit=lambda d: d.modal), _t1(dl), "layer", "unit", min_tokens=1)
    rows = []
    for (lay, u), s in ser.groupby(["key", "unit"]):
        s = s.sort_values("date")
        if lay == "speech_chair":
            s = s.assign(q=pd.PeriodIndex(s.date, freq="Q")).groupby("q")[["per1k", "share"]].mean().reset_index()
        for metric in ("per1k", "share"):
            r = pc.mk_trend(s[metric].fillna(0).values)
            if r: rows.append(dict(layer=lay, series=u, metric=metric, **r))
    mk = pd.DataFrame(rows)
    if len(mk): pc.save(mk.round(4), ctx.out, "L3_mk_trends")
    res["mk_significant"] = mk[(mk.p < .05) & (mk.metric == "per1k")][["layer", "series", "tau", "sen_slope", "p"]].round(3).to_dict("records") if len(mk) else []
    # yearly figure for main layer
    yr = pd.read_csv(ctx.out / "tables" / "L1_yearly_pmw.csv"); y = yr[yr.layer == ctx.main_layer].sort_values("year")
    if len(y):
        fig, ax = plt.subplots(figsize=(9, 3.6))
        for m in SIX: ax.plot(y.year, y[f"{m}_pmw"], marker=".", label=m)
        ax.set_ylabel("per million words"); ax.set_title(f"L3 modal frequency by year — {LAYER_LABEL.get(ctx.main_layer, ctx.main_layer)}"); ax.legend(fontsize=7, ncol=6)
        _fig(fig, ctx, "L3_yearly_main")
    # statement staircase + change points
    if "statement" in ctx.layers:
        for T in ("T1", "T3"):
            st = tk[(tk.layer == "statement") & pc.period_mask(tk.date, T)]
            sd = dl[(dl.layer == "statement") & pc.period_mask(dl.date, T)].sort_values("date").drop_duplicates("doc_id")
            if len(sd) < 10: continue
            cnt = st.groupby(["doc_id", ctx.unit_col]).size().unstack(fill_value=0).reindex(sd.doc_id, fill_value=0)
            tot = cnt.sum(axis=1); share = cnt.div(tot.replace(0, np.nan), axis=0).fillna(0)
            totals = cnt.sum().sort_values(ascending=False); top = totals.head(10).index.tolist()
            for m in SIX:
                cand = [u for u in totals.index if pc.modal_of_unit(u) == m]
                if cand and cand[0] not in top and totals[cand[0]] >= 5: top.append(cand[0])
            top = top[:14]; dates = sd.date.tolist(); n = len(dates); cps = []
            for u in top:
                for b in pc.pelt_breaks(share[u].values):
                    y_ = share[u].values; before, after = y_[max(0, b - 8):b].mean(), y_[b:b + 8].mean()
                    win = sd.doc_id.iloc[b:b + 8] if after > before else sd.doc_id.iloc[max(0, b - 8):b]
                    ex = st[(st[ctx.unit_col] == u) & st.doc_id.isin(win)].sentence
                    ev = min(EVENTS, key=lambda e: abs(pd.Timestamp(e[0]) - pd.Timestamp(dates[b]))); gap = abs((pd.Timestamp(ev[0]) - pd.Timestamp(dates[b])).days)
                    cps.append(dict(period=T, unit=u, break_date=dates[b], meeting_index=int(b), share_before=round(before, 3), share_after=round(after, 3),
                                    direction=("up" if after > before else "down"), nearest_event=ev[1], event_date=ev[0], days_to_event=int(gap), within_1_meeting=bool(gap <= 50),
                                    responsible_sentence=(str(ex.iloc[0])[:240] if len(ex) else "")))
            cpdf = pd.DataFrame(cps); pc.save(cpdf, ctx.out, f"L3_changepoints_{T}")
            long = share[top].stack().rename("share").reset_index(); long.columns = ["doc_id", "unit", "share"]; long["date"] = long.doc_id.map(sd.set_index("doc_id").date)
            pc.save(long, ctx.out, f"L3_staircase_series_{T}")
            fig, ax = plt.subplots(figsize=(12, 4.6)); other = 1 - share[top].sum(axis=1); bottom = np.zeros(n); cmap = plt.get_cmap("tab20"); x = np.arange(n)
            for i, u in enumerate(top):
                ax.bar(x, share[u].values, bottom=bottom, width=0.9, color=cmap(i % 20), label=u); bottom += share[u].values
            ax.bar(x, other.values, bottom=bottom, width=0.9, color="#CCCCCC", label="other")
            yrs = [d[:4] for d in dates]; ticks = [i for i in range(n) if i == 0 or yrs[i] != yrs[i - 1]]
            ax.set_xticks(ticks); ax.set_xticklabels([yrs[i] for i in ticks])
            for c in cps: ax.axvline(c["meeting_index"] - 0.5, color="k", lw=0.6, ls="--", alpha=0.6)
            for d, lab in EVENTS:
                if dates[0] <= d <= dates[-1]:
                    i = int(np.searchsorted(np.array(dates), d)); ax.text(i, 0.99, lab, rotation=90, fontsize=6, va="top", ha="center", color="#222", bbox=dict(facecolor="white", alpha=0.7, lw=0, pad=1))
            ax.set_ylim(0, 1); ax.set_ylabel("share of six-modal tokens (N2)"); ax.legend(fontsize=6, ncol=7, loc="upper center", bbox_to_anchor=(0.5, -0.12))
            fig.suptitle(f"L3 statement staircase — {pc.UNITS[ctx.U]}, {pc.PERIODS[T][0][:4]}–2026 (dashed = PELT change points)", y=1.02)
            _fig(fig, ctx, f"L3_staircase_{T}")
            res[f"staircase_{T}"] = dict(n_meetings=n, top_units=top, n_cp=len(cps), n_cp_event=int(sum(c["within_1_meeting"] for c in cps)),
                                         changepoints=cps if T == "T1" else [])
    ctx.summary["L3"] = res


# ----------------------------------------------------------------------------------------------
def _collostruction(df: pd.DataFrame, unit_col: str, min_count=3) -> pd.DataFrame:
    """Distinctive collexeme analysis (Gries & Stefanowitsch 2004): for each modal M and predicate V the 2x2 table
    [V&M, V&¬M ; ¬V&M, ¬V&¬M]; Fisher exact p, signed -log10 p, G² and observed/expected ratio."""
    ct = pd.crosstab(df["predicate"], df["modal"]); N = ct.values.sum(); rows = []
    for v in ct.index:
        for m in ct.columns:
            a = int(ct.loc[v, m])
            if a < min_count: continue
            b = int(ct.loc[v].sum() - a); c = int(ct[m].sum() - a); d = int(N - a - b - c)
            exp = (a + b) * (a + c) / N
            _, p = stats.fisher_exact([[a, b], [c, d]]); sign = 1 if a > exp else -1
            tbl = np.array([[a, b], [c, d]], float); e = np.outer(tbl.sum(1), tbl.sum(0)) / N
            with np.errstate(divide="ignore", invalid="ignore"):
                g2 = 2 * np.nansum(np.where(tbl > 0, tbl * np.log(tbl / e), 0))
            rows.append(dict(modal=m, predicate=v, obs=a, exp=round(exp, 2), ratio=round(a / exp, 2), p=p, collostruction_strength=round(sign * -math.log10(max(p, 1e-300)), 2), G2=round(float(g2), 2)))
    return pd.DataFrame(rows)


def L4_collocation(ctx):
    tk = _t1(ctx.tk); res = {}
    prof, coll, jsd_rows, cls_rows, kw = [], [], [], [], []
    for lay in ctx.layers:
        sub = tk[tk.layer == lay]
        if len(sub) < 300: continue
        for m in SIX:
            s2 = sub[sub.modal == m]
            if len(s2) < 20: continue
            vc = s2.predicate.value_counts(); cum = 0
            for rank, (v, n) in enumerate(vc.head(15).items(), 1):
                cum += n; prof.append(dict(layer=lay, modal=m, rank=rank, predicate=v, n=int(n), share=round(n / len(s2), 4), cum_share=round(cum / len(s2), 4), modal_n=len(s2)))
            for cl, n in s2.vclass.value_counts().items():
                cls_rows.append(dict(layer=lay, modal=m, vclass=cl, n=int(n), share=round(n / len(s2), 4)))
        c = _collostruction(sub, ctx.unit_col); c["layer"] = lay
        coll.append(c)
        P = sub.groupby(["modal", "predicate"]).size().unstack(fill_value=0).reindex(SIX).fillna(0); P = P.div(P.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        for i, a in enumerate(SIX):
            for b in SIX[i + 1:]:
                p_, q_ = P.loc[a].values, P.loc[b].values
                if p_.sum() == 0 or q_.sum() == 0: continue
                mid = (p_ + q_) / 2
                kl = lambda x, y: float(np.sum(x[x > 0] * np.log2(x[x > 0] / y[x > 0])))
                jsd_rows.append(dict(layer=lay, modal_a=a, modal_b=b, jsd=round(0.5 * kl(p_, mid) + 0.5 * kl(q_, mid), 3)))
    profd = pd.DataFrame(prof); pc.save(profd, ctx.out, "L4_predicate_profiles")
    if coll:
        colld = pd.concat(coll, ignore_index=True).sort_values(["layer", "modal", "collostruction_strength"], ascending=[True, True, False]); pc.save(colld, ctx.out, "L4_collostruction")
    pc.save(pd.DataFrame(jsd_rows), ctx.out, "L4_jsd"); pc.save(pd.DataFrame(cls_rows), ctx.out, "L4_verb_class")
    # KWIC for main layer: 2 examples per top-5 predicate per modal
    ml = ctx.main_layer; sub = tk[tk.layer == ml]
    for m in SIX:
        s2 = sub[sub.modal == m]
        for v in s2.predicate.value_counts().head(5).index:
            ex = s2[s2.predicate == v].sample(min(2, int((s2.predicate == v).sum())), random_state=1)
            for r in ex.itertuples():
                kw.append(dict(layer=ml, modal=m, predicate=v, doc_id=r.doc_id, date=r.date, kwic=pc.kwic(r.sentence, m)))
    pc.save(pd.DataFrame(kw), ctx.out, "L4_kwic")
    if coll:
        top = colld[colld.layer == ml]
        res["main_layer"] = ml
        res["attracted"] = {m: top[(top.modal == m) & (top.collostruction_strength > 0)].head(5)[["predicate", "obs", "ratio", "collostruction_strength"]].to_dict("records") for m in SIX}
        res["top_predicate"] = {m: (profd[(profd.layer == ml) & (profd.modal == m)].head(1)[["predicate", "share"]].to_dict("records") or [{}])[0] for m in SIX}
    j = pd.DataFrame(jsd_rows); res["jsd_main"] = (float(j[j.layer == ml].jsd.min()), float(j[j.layer == ml].jsd.max())) if len(j) and (j.layer == ml).any() else None
    # figure: verb class heatmap for main layer
    cl = pd.DataFrame(cls_rows)
    if len(cl) and (cl.layer == ml).any():
        piv = cl[cl.layer == ml].pivot_table(index="vclass", columns="modal", values="share", aggfunc="sum").reindex(columns=SIX).fillna(0)
        fig, ax = plt.subplots(figsize=(7, 0.35 * len(piv) + 1.5)); im = ax.imshow(piv.values, cmap="Blues", aspect="auto", vmin=0, vmax=max(0.5, piv.values.max()))
        ax.set_xticks(range(len(SIX))); ax.set_xticklabels(SIX); ax.set_yticks(range(len(piv))); ax.set_yticklabels(piv.index, fontsize=7)
        for i in range(piv.shape[0]):
            for j_ in range(piv.shape[1]): ax.text(j_, i, f"{piv.values[i, j_]:.2f}", ha="center", va="center", fontsize=6, color=("white" if piv.values[i, j_] > 0.35 else "black"))
        ax.set_title(f"L4 predicate semantic class by modal — {LAYER_LABEL.get(ml, ml)}"); _fig(fig, ctx, "L4_verb_class_main")
    ctx.summary["L4"] = res


# ----------------------------------------------------------------------------------------------
def _retention(P: np.ndarray, kmax=24):
    r = []
    for k in range(1, kmax + 1):
        vals = [(P[t] & P[t + k]).sum() / P[t].sum() for t in range(P.shape[0] - k) if P[t].sum() > 0]
        r.append(np.mean(vals) if vals else np.nan)
    r = np.array(r); hl = None
    for k in range(len(r)):
        if not np.isnan(r[k]) and r[k] < 0.5:
            prev = 1.0 if k == 0 else r[k - 1]; hl = k + (prev - 0.5) / (prev - r[k]) if prev != r[k] else k + 1; break
    return r, (float(hl) if hl is not None else None)


def _km(durations, events):
    d = np.asarray(durations); e = np.asarray(events); times = np.sort(np.unique(d[e == 1])); S = 1.0; out = [(0, 1.0)]
    for t in times:
        at_risk = np.sum(d >= t); died = np.sum((d == t) & (e == 1))
        if at_risk == 0: continue
        S *= (1 - died / at_risk); out.append((int(t), float(S)))
    return pd.DataFrame(out, columns=["t", "S"])


def L5_formulaicity(ctx):
    if "statement" not in ctx.layers: ctx.summary["L5"] = {"note": "no statement layer"}; return
    tk, dl = ctx.tk, ctx.dl
    st = tk[(tk.layer == "statement") & pc.period_mask(tk.date, "T1")]
    sd = dl[(dl.layer == "statement") & pc.period_mask(dl.date, "T1")].sort_values("date").drop_duplicates("doc_id")
    res = {}
    # formulaic sentences: normalised sentence appearing in >= 3 statements
    st = st.assign(ns=st.sentence.map(pc.norm_sentence))
    n_stmts = st.groupby("ns").doc_id.nunique(); st["formulaic"] = st.ns.map(n_stmts) >= 3
    fy = st.groupby("year").agg(tokens=("modal", "size"), formulaic=("formulaic", "sum")).reset_index(); fy["formulaic_share"] = (fy.formulaic / fy.tokens).round(3)
    fm = st.groupby(["year", "modal"]).formulaic.mean().unstack().round(3).reindex(columns=SIX); pc.save(fy, ctx.out, "L5_formulaic_share_year"); pc.save(fm.reset_index(), ctx.out, "L5_formulaic_share_year_modal")
    # cohorts (runs) of units across consecutive statements -> KM
    cnt = st.groupby(["doc_id", ctx.unit_col]).size().unstack(fill_value=0).reindex(sd.doc_id, fill_value=0); P = cnt.values > 0
    durs, evs, units_ = [], [], []
    for j, u in enumerate(cnt.columns):
        col = P[:, j]; i = 0
        while i < len(col):
            if col[i]:
                k = i
                while k < len(col) and col[k]: k += 1
                durs.append(k - i); evs.append(0 if k == len(col) else 1); units_.append(u); i = k
            else: i += 1
    km = _km(durs, evs); pc.save(km, ctx.out, "L5_km_survival")
    med = float(km[km.S <= 0.5].t.iloc[0]) if (km.S <= 0.5).any() else None
    coh = pd.DataFrame(dict(unit=units_, duration=durs, event=evs)); pc.save(coh, ctx.out, "L5_cohorts")
    r_all, hl_all = _retention(P); rows = [dict(group="all", k=k + 1, retention=r_all[k]) for k in range(len(r_all))]; hls = {"all": hl_all}
    modal_of = np.array([pc.modal_of_unit(u) for u in cnt.columns])
    for m in SIX:
        cols = modal_of == m
        if cols.sum():
            r, hl = _retention(P[:, cols]); hls[m] = hl; rows += [dict(group=m, k=k + 1, retention=r[k]) for k in range(len(r))]
    sent = st.groupby(["doc_id", "ns"]).size().unstack(fill_value=0).reindex(sd.doc_id, fill_value=0); r_s, hl_s = _retention(sent.values > 0); hls["modal_sentences"] = hl_s
    rows += [dict(group="modal_sentences", k=k + 1, retention=r_s[k]) for k in range(len(r_s))]; pc.save(pd.DataFrame(rows), ctx.out, "L5_retention")
    # edit events
    ev = []
    for i in range(1, P.shape[0]):
        added = [cnt.columns[j] for j in range(P.shape[1]) if P[i, j] and not P[i - 1, j]]; removed = [cnt.columns[j] for j in range(P.shape[1]) if P[i - 1, j] and not P[i, j]]
        ev.append(dict(date=sd.date.iloc[i], year=int(sd.date.iloc[i][:4]), n_added=len(added), n_removed=len(removed), added=", ".join(map(str, added[:6])), removed=", ".join(map(str, removed[:6]))))
    evd = pd.DataFrame(ev); pc.save(evd, ctx.out, "L5_edit_events"); by_year = evd.groupby("year")[["n_added", "n_removed"]].sum()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
    for g, s in pd.DataFrame(rows).groupby("group"): a1.plot(s.k, s.retention, marker=".", label=f"{g} (½={('%.1f' % hls[g]) if hls.get(g) else '≥24'})")
    a1.axhline(0.5, color="k", lw=0.5, ls=":"); a1.set_xlabel("meetings later (k)"); a1.set_ylabel("retention"); a1.legend(fontsize=6); a1.set_title("L5 retention of statement units")
    by_year.plot(kind="bar", ax=a2, color=["#2C6E5C", "#A8501F"]); a2.set_title("units added / removed between consecutive statements"); _fig(fig, ctx, "L5_retention_edits")
    res.update(half_life=hls, km_median=med, n_cohorts=len(durs), one_off_share=round(float(np.mean(np.array(durs) == 1)), 3), formulaic_share_overall=round(float(st.formulaic.mean()), 3),
               formulaic_share_by_year={int(r.year): r.formulaic_share for r in fy.itertuples()}, edits_by_year={int(k): dict(added=int(v.n_added), removed=int(v.n_removed)) for k, v in by_year.iterrows()})
    ctx.summary["L5"] = res


# ----------------------------------------------------------------------------------------------
FEATS = ["neg", "passive", "perfect", "progressive", "cond", "reported", "question", "contracted"]


def L6_context(ctx):
    tk = _t1(ctx.tk); rows, chi, subj, sem = [], [], [], []
    for lay in ctx.layers:
        sub = tk[tk.layer == lay]
        if len(sub) < 100: continue
        for m in SIX:
            s2 = sub[sub.modal == m]
            if len(s2) < 20: continue
            r = dict(layer=lay, modal=m, n=len(s2)); r.update({f: round(float(s2[f].mean()), 3) for f in FEATS}); rows.append(r)
            for stp, n in s2.subj_type.value_counts().items(): subj.append(dict(layer=lay, modal=m, subj_type=stp, n=int(n), share=round(n / len(s2), 3)))
            for t_, n in s2.sem_type.value_counts().items(): sem.append(dict(layer=lay, modal=m, sem_type=t_, n=int(n), share=round(n / len(s2), 3)))
        for f in FEATS:
            ct = pd.crosstab(sub.modal, sub[f])
            if ct.shape[1] == 2 and (ct.sum(axis=1) >= 20).sum() >= 2:
                c2, p, dof, _ = stats.chi2_contingency(ct.values); V = math.sqrt(c2 / (ct.values.sum() * (min(ct.shape) - 1)))
                chi.append(dict(layer=lay, feature=f, chi2=round(float(c2), 1), dof=int(dof), p=float(p), cramers_v=round(V, 3)))
    rates = pd.DataFrame(rows); pc.save(rates, ctx.out, "L6_context_rates"); pc.save(pd.DataFrame(chi), ctx.out, "L6_feature_chi2")
    pc.save(pd.DataFrame(subj), ctx.out, "L6_subject_types"); pc.save(pd.DataFrame(sem), ctx.out, "L6_semantic_types")
    ml = ctx.main_layer; r = rates[rates.layer == ml]
    if len(r):
        fig, axes = plt.subplots(2, 4, figsize=(12, 5))
        for ax, f in zip(axes.ravel(), FEATS):
            ax.bar(r.modal, r[f] * 100, color="#24507A"); ax.set_title(f"% {f}"); ax.tick_params(axis="x", labelsize=7)
        fig.suptitle(f"L6 grammatical context by modal — {LAYER_LABEL.get(ml, ml)}"); _fig(fig, ctx, "L6_context_main")
    semd = pd.DataFrame(sem)
    ctx.summary["L6"] = dict(rates_main=r.to_dict("records"), chi2_significant=[c for c in chi if c["p"] < .05][:40],
                             sem_main={m: semd[(semd.layer == ml) & (semd.modal == m)].sort_values("share", ascending=False).head(2)[["sem_type", "share"]].to_dict("records") for m in SIX} if len(semd) else {})


# ----------------------------------------------------------------------------------------------
def L7_mnlogit(ctx):
    import statsmodels.api as sm
    d = _t1(ctx.tk).copy(); res = {}
    d["period"] = np.where(d.year <= 2019, "early", "late")
    cols = ["period", "subj_type"] + (["layer"] if len(ctx.layers) >= 2 else [])
    X = pd.get_dummies(d[cols], drop_first=True).astype(float); X["cond"] = d.cond.astype(float).values; X["reported"] = d.reported.astype(float).values
    X = sm.add_constant(X); y = pd.Categorical(d.modal, categories=SIX).codes
    try:
        mod = sm.MNLogit(y, X).fit(method="lbfgs", maxiter=400, disp=False)
        params = mod.params; pv = mod.pvalues; params.columns = SIX[1:]; pv.columns = SIX[1:]
        rows = []
        for var in params.index:
            for outc in SIX[1:]:
                rows.append(dict(variable=var, outcome_vs_will=outc, coef=round(float(params.loc[var, outc]), 3), rrr=round(float(np.exp(params.loc[var, outc])), 3), p=float(pv.loc[var, outc])))
        tab = pd.DataFrame(rows); pc.save(tab, ctx.out, "L7_mnlogit"); (ctx.out / "tables" / "L7_mnlogit_summary.txt").write_text(str(mod.summary()))
        res.update(pseudo_r2=round(float(mod.prsquared), 4), n=int(len(y)), llf=float(mod.llf),
                   layer_effects=tab[tab.variable.str.startswith("layer_") & (tab.p < .05)].sort_values("rrr", ascending=False).head(12).to_dict("records"))
    except Exception as e:
        res["error"] = str(e)[:200]
    ctx.summary["L7"] = res


# ----------------------------------------------------------------------------------------------
def L8_be_appropriate(ctx):
    tk = _t1(ctx.tk); ba = tk[tk.predicate == "be+appropriate"]
    if len(ba) < 5: ctx.summary["L8"] = {"n": int(len(ba))}; return
    ct = ba.groupby(["layer", "modal"]).size().unstack(fill_value=0); pc.save(ct.reset_index(), ctx.out, "L8_counts")
    yr = ba.groupby(["layer", "year", "modal"]).size().unstack(fill_value=0).reset_index(); pc.save(yr, ctx.out, "L8_yearly")
    kw = []
    for lay in ctx.layers:
        for m in ("will", "would", "may"):
            ex = ba[(ba.layer == lay) & (ba.modal == m)]
            for r in ex.sample(min(2, len(ex)), random_state=2).itertuples():
                kw.append(dict(layer=lay, modal=m, date=r.date, kwic=pc.kwic(r.sentence, m, 80)))
    pc.save(pd.DataFrame(kw), ctx.out, "L8_kwic")
    ctx.summary["L8"] = dict(n=int(len(ba)), counts={lay: {m: int(ct.loc[lay].get(m, 0)) for m in ("will", "would", "may", "could")} for lay in ct.index})


# ----------------------------------------------------------------------------------------------
def L9_contrasts(ctx):
    tk = _t1(ctx.tk); rows, res = [], {}
    for lay in [l for l in ("statement", "pc_chair", "min_participants", "min_committee") if l in ctx.layers]:
        sub = tk[(tk.layer == lay) & tk.chair.isin(["Yellen", "Powell"])]
        if len(sub) < 100: continue
        ct = pd.crosstab(sub.chair, sub.modal).reindex(columns=SIX, fill_value=0)
        if len(ct) == 2:
            c2, p, dof, _ = stats.chi2_contingency(ct.values); V = math.sqrt(c2 / (ct.values.sum() * (min(ct.shape) - 1)))
            sh = ct.div(ct.sum(axis=1), axis=0).round(3)
            for ch in ct.index: rows.append(dict(layer=lay, contrast="chair", group=ch, n=int(ct.loc[ch].sum()), **{m: float(sh.loc[ch, m]) for m in SIX}, chi2=round(float(c2), 1), p=float(p), cramers_v=round(V, 3)))
            res[f"chair_{lay}"] = dict(chi2=round(float(c2), 1), p=float(p), V=round(V, 3))
    if "statement" in ctx.layers:
        sub = tk[tk.layer == "statement"]; ct = pd.crosstab(sub.phase, sub.modal).reindex(columns=SIX, fill_value=0)
        sh = ct.div(ct.sum(axis=1).replace(0, np.nan), axis=0).round(3)
        for ph in ct.index: rows.append(dict(layer="statement", contrast="phase", group=ph, n=int(ct.loc[ph].sum()), **{m: float(sh.loc[ph, m]) for m in SIX}, chi2=np.nan, p=np.nan, cramers_v=np.nan))
    pc.save(pd.DataFrame(rows), ctx.out, "L9_contrasts"); ctx.summary["L9"] = res


BLOCKS = [L1_corpus_description, L2_keyness_division, L3_diachronic, L4_collocation, L5_formulaicity, L6_context, L7_mnlogit, L8_be_appropriate, L9_contrasts]
