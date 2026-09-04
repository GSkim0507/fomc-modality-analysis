"""
22_exp_econometric.py — Econometric experiment family E1–E9 (Phase 14; docs/12 §4).

Dependent variables are per-document text densities (per 1,000 tokens) at layer and genre level; regressors are the
advisor-fixed pair CFNAI-MA3 (two-month real-time lag) and VIX (28 days before the meeting), with gaps, an era dummy,
2020 exclusion and first differences as robustness.  Standard errors are Newey-West HAC (4 lags).
"""
from __future__ import annotations
import math, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util
_s = importlib.util.spec_from_file_location("pc", Path(__file__).resolve().parent / "20_program_common.py"); pc = importlib.util.module_from_spec(_s); _s.loader.exec_module(pc)
SIX, EVENTS, LAYER_LABEL, MACRO_VARS = pc.SIX, pc.EVENTS, pc.LAYER_LABEL, pc.MACRO_VARS
plt.rcParams.update({"figure.dpi": 100, "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9})
HEDGE = ["would", "could", "may", "might"]


def _fig(fig, ctx, name):
    (ctx.out / "figures").mkdir(parents=True, exist_ok=True); fig.tight_layout(); fig.savefig(ctx.out / "figures" / f"{name}.png", bbox_inches="tight"); plt.close(fig)


def _series(ctx, level, unit_col, min_tokens=pc.MIN_TOKENS, extra=()):
    return pc.unit_series(ctx.tk, ctx.dl, level, unit_col, min_tokens=min_tokens, extra_units=extra)


def _with_macro(ser, macro):
    df = ser.merge(macro, on="doc_id", how="left"); df["post_fw"] = (df.date >= pc.NEW_FRAMEWORK).astype(float); return df


def _ar1(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    return float(np.corrcoef(x[:-1], x[1:])[0, 1]) if len(x) > 3 and x.std() > 0 else np.nan


# ----------------------------------------------------------------------------------------------
def E1_descriptives(ctx):
    ser = _series(ctx, "layer", "modal"); df = _with_macro(ser, ctx.macro); t1 = df[pc.period_mask(df.date, "T1")]
    rows = []
    ml = ctx.main_layer; base = t1[(t1.key == ml) & (t1.unit == "ALL")].sort_values("date").drop_duplicates("doc_id")
    for v, lab in [("cfnai_ma3_lag2", "CFNAI-MA3 (m−2)"), ("vix_pre28", "VIX pre-28d"), ("unrate_gap_lag1", "Unemployment gap (m−1)"), ("corepce_gap_lag2", "Core PCE gap (m−2)")]:
        x = base[v].astype(float); rows.append(dict(block="macro", layer=ml, series=lab, N=int(x.notna().sum()), mean=round(x.mean(), 3), sd=round(x.std(), 3), min=round(x.min(), 3), max=round(x.max(), 3), zero_share=np.nan, AR1=round(_ar1(x), 3)))
    for (lay, u), s in t1.groupby(["key", "unit"]):
        if u not in ["ALL"] + SIX: continue
        s = s.sort_values("date"); x = s.per1k
        rows.append(dict(block="text", layer=lay, series=u, N=len(s), mean=round(x.mean(), 3), sd=round(x.std(), 3), min=round(x.min(), 3), max=round(x.max(), 3), zero_share=round(float((s["count"] == 0).mean()), 3), AR1=round(_ar1(x), 3)))
    d = pd.DataFrame(rows); pc.save(d, ctx.out, "E1_descriptives")
    ctx.summary["E1"] = dict(macro=d[d.block == "macro"].to_dict("records"), text_all={r.layer: dict(mean=r.mean, sd=r.sd, AR1=r.AR1) for r in d[(d.block == "text") & (d.series == "ALL")].itertuples()})
    ctx._ser_modal_layer = ser


# ----------------------------------------------------------------------------------------------
def E2_correlations(ctx):
    ser = pd.concat([ctx._ser_modal_layer, _series(ctx, "genre", "modal")], ignore_index=True); df = _with_macro(ser, ctx.macro)
    rows = []
    for (level, key, u), s in df.groupby(["level", "key", "unit"]):
        if u not in ["ALL"] + SIX: continue
        s = s.sort_values("date")
        for T in pc.PERIODS:
            st = s[pc.period_mask(s.date, T)]
            if len(st) < pc.MIN_N: continue
            for mv, col in MACRO_VARS.items():
                c = pc.corr_pair(st.per1k, st[col]); rows.append(dict(level=level, key=key, series=u, period=T, macro=mv, zero_share=round(float((st["count"] == 0).mean()), 3), **c))
    d = pd.DataFrame(rows).round(4); pc.save(d, ctx.out, "E2_correlations")
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5)); im = None
    for ax, (mv, T) in zip(axes.ravel(), [("cfnai", "T1"), ("cfnai", "T2"), ("vix", "T1"), ("vix", "T2")]):
        sub = d[(d.macro == mv) & (d.period == T) & (d.level == "layer")]; piv = sub.pivot_table(index="series", columns="key", values="rho").reindex(["ALL"] + SIX)
        if piv.empty: ax.axis("off"); continue
        im = ax.imshow(piv.values.astype(float), cmap="RdBu_r", vmin=-0.6, vmax=0.6, aspect="auto")
        ax.set_xticks(range(piv.shape[1])); ax.set_xticklabels([LAYER_LABEL.get(c, c) for c in piv.columns], rotation=30, ha="right", fontsize=6); ax.set_yticks(range(len(piv))); ax.set_yticklabels(piv.index)
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                v = piv.values[i, j]
                if not np.isnan(v):
                    pv = sub[(sub.series == piv.index[i]) & (sub.key == piv.columns[j])].p_rho.iloc[0]; ax.text(j, i, f"{v:.2f}{'*' if pv < .05 else ''}", ha="center", va="center", fontsize=6)
        ax.set_title(f"Spearman ρ × {mv.upper()} [{T}{' excl. 2020' if T == 'T2' else ''}]")
    if im is not None: plt.colorbar(im, ax=axes, shrink=0.6)
    fig.suptitle("E2 modal density × macro by layer"); fig.savefig(ctx.out / "figures" / "E2_heatmap.png", bbox_inches="tight"); plt.close(fig)
    g = d[(d.level == "genre") & (d.series == "ALL") & (d.period.isin(pc.MAIN_PERIODS))]
    ctx.summary["E2"] = dict(genre_all=[dict(key=r.key, period=r.period, macro=r.macro, rho=r.rho, p=r.p_rho, n=r.n) for r in g.itertuples()],
                             layer_all_T2=[dict(key=r.key, macro=r.macro, rho=r.rho, p=r.p_rho) for r in d[(d.level == "layer") & (d.series == "ALL") & (d.period == "T2")].itertuples()])


# ----------------------------------------------------------------------------------------------
SPECS = {"(1)": ["cfnai_ma3_lag2"], "(2)": ["vix_pre28"], "(3)": ["cfnai_ma3_lag2", "vix_pre28"], "(4)": ["cfnai_ma3_lag2", "vix_pre28", "unrate_gap_lag1", "corepce_gap_lag2"],
         "(5)": ["cfnai_ma3_lag2", "vix_pre28", "post_fw"], "(6) excl-2020": ["cfnai_ma3_lag2", "vix_pre28"], "(7) Δ": ["d_cfnai", "d_vix"], "(8) Δ excl-2020": ["d_cfnai", "d_vix"]}
VAR_LABEL = {"cfnai_ma3_lag2": "CFNAI-MA3", "vix_pre28": "VIX", "unrate_gap_lag1": "Unemp. gap", "corepce_gap_lag2": "Core PCE gap", "post_fw": "post-2020-09", "d_cfnai": "ΔCFNAI", "d_vix": "ΔVIX", "const": "const"}


def _run_specs(s: pd.DataFrame, ycol="per1k"):
    """s: one series sorted by date with macro columns. Returns list of rows (spec, var, coef, se, p, n, r2)."""
    s = s.sort_values("date").copy(); s["d_y"] = s[ycol].diff(); s["d_cfnai"] = s["cfnai_ma3_lag2"].diff(); s["d_vix"] = s["vix_pre28"].diff()
    rows = []
    for spec, xs in SPECS.items():
        st = s[pc.period_mask(s.date, "T2")] if ("excl-2020" in spec) else s
        y = st["d_y"] if spec.startswith(("(7)", "(8)")) else st[ycol]
        m = pc.hac_ols(y, st[xs])
        if m is None: continue
        for v in ["const"] + xs:
            rows.append(dict(spec=spec, var=v, label=VAR_LABEL.get(v, v), coef=m["coef"].get(v, np.nan), se=m["se"].get(v, np.nan), p=m["p"].get(v, np.nan), stars=pc.stars(m["p"].get(v, np.nan)), n=m["n"], r2=m["r2"], adj_r2=m["adj_r2"]))
    return rows


def E3_regressions(ctx):
    df = _with_macro(ctx._ser_modal_layer, ctx.macro); df = df[pc.period_mask(df.date, "T1")]; rows = []
    for (lay, u), s in df.groupby(["key", "unit"]):
        if u not in ["ALL"] + SIX or len(s) < pc.MIN_N: continue
        for r in _run_specs(s): rows.append(dict(layer=lay, series=u, **r))
    d = pd.DataFrame(rows); pc.save(d.round(5), ctx.out, "E3_regressions")
    key = {}
    for lay in ctx.layers:
        sub = d[(d.layer == lay) & (d.series == "ALL")]
        if not len(sub): continue
        key[lay] = {sp: {r.var: dict(coef=round(r.coef, 4), p=round(r.p, 4), stars=r.stars, n=int(r.n), r2=round(r.r2, 3)) for r in sub[sub.spec == sp].itertuples() if r.var != "const"} for sp in ("(3)", "(5)", "(6) excl-2020", "(7) Δ", "(8) Δ excl-2020")}
    ctx.summary["E3"] = dict(all_by_layer=key)


# ----------------------------------------------------------------------------------------------
def E4_construction_regressions(ctx):
    if ctx.U == "U1": ctx.summary["E4"] = {"note": "unit = modal; see E3"}; return
    extra = [u for u in ctx.tk[ctx.unit_col].unique() if "be+appropriate" in u]
    ser = _series(ctx, "layer", ctx.unit_col, extra=extra); df = _with_macro(ser, ctx.macro); df = df[pc.period_mask(df.date, "T1")]; rows = []
    for lay, s_all in df.groupby("key"):
        counts = s_all.groupby("unit")["count"].sum().sort_values(ascending=False); units = [u for u in counts.index if u != "ALL"][:8] + [u for u in extra if u in counts.index and u not in counts.index[:9]]
        for u in units:
            s = s_all[s_all.unit == u]
            if len(s) < pc.MIN_N: continue
            for r in _run_specs(s):
                if r["spec"] in ("(3)", "(6) excl-2020", "(7) Δ", "(8) Δ excl-2020"): rows.append(dict(layer=lay, unit=u, n_tokens=int(counts[u]), zero_share=round(float((s["count"] == 0).mean()), 3), **r))
    d = pd.DataFrame(rows); pc.save(d.round(5), ctx.out, "E4_construction_regressions")
    sig = d[(d.spec == "(3)") & (d.var != "const") & (d.p < .05)] if len(d) else d
    ctx.summary["E4"] = dict(n_units=int(d.unit.nunique()) if len(d) else 0, significant_spec3=sig[["layer", "unit", "var", "coef", "p", "n_tokens"]].round(4).to_dict("records")[:40] if len(sig) else [])
    ctx._ser_unit_layer = ser


# ----------------------------------------------------------------------------------------------
def _screen(series, macro):
    df = series.merge(macro, on="doc_id", how="left"); rows = []
    for (level, key, unit), s in df.groupby(["level", "key", "unit"]):
        s = s.sort_values("date")
        for T in pc.PERIODS:
            st = s[pc.period_mask(s.date, T)]
            if len(st) < pc.MIN_N: continue
            zero = float((st["count"] == 0).mean())
            for mv, col in MACRO_VARS.items():
                c = pc.corr_pair(st.per1k, st[col]); rows.append(dict(level=level, key=key, unit=unit, period=T, macro=mv, n_tokens=int(st["count"].sum()), zero_share=round(zero, 3), **c))
    scr = pd.DataFrame(rows)
    if len(scr):
        scr["q_rho"] = np.nan
        for (T, mv, level), idx in scr.groupby(["period", "macro", "level"]).groups.items(): scr.loc[idx, "q_rho"] = pc.bh(scr.loc[idx, "p_rho"])
        scr["eligible"] = (scr.n_tokens >= pc.MIN_TOKENS) & (scr.zero_share <= pc.MAX_ZERO)
    return scr


def _ledger(scr):
    if not len(scr): return pd.DataFrame()
    p = scr.pivot_table(index=["level", "key", "unit", "macro"], columns="period", values=["rho", "p_rho", "eligible", "n_tokens", "zero_share"], aggfunc="first"); out = []
    for idx, row in p.iterrows():
        try:
            r1, r2, p1, p2 = row[("rho", "T1")], row[("rho", "T2")], row[("p_rho", "T1")], row[("p_rho", "T2")]; e1, e2 = bool(row[("eligible", "T1")]), bool(row[("eligible", "T2")])
        except KeyError: continue
        if any(pd.isna(v) for v in (r1, r2, p1, p2)): continue
        rh1 = row.get(("rho", "H1"), np.nan); rh2 = row.get(("rho", "H2"), np.nan); r3 = row.get(("rho", "T3"), np.nan)
        halves_ok = (not pd.isna(rh1)) and (not pd.isna(rh2)) and np.sign(rh1) == np.sign(r2) and np.sign(rh2) == np.sign(r2)
        both = e1 and e2 and p1 < .05 and p2 < .05 and np.sign(r1) == np.sign(r2); conf = both and halves_ok
        cat = "confirmed" if conf else ("era_composition" if both else ("T1_only" if (e1 and p1 < .05) else "none"))
        out.append(dict(level=idx[0], key=idx[1], unit=idx[2], macro=idx[3], rho_T1=round(r1, 3), p_T1=round(p1, 4), rho_T2=round(r2, 3), p_T2=round(p2, 4), rho_T3=(round(r3, 3) if not pd.isna(r3) else np.nan),
                        rho_H1=(round(rh1, 3) if not pd.isna(rh1) else np.nan), rho_H2=(round(rh2, 3) if not pd.isna(rh2) else np.nan), n_tokens_T1=int(row[("n_tokens", "T1")]), zero_share_T1=row[("zero_share", "T1")], category=cat))
    return pd.DataFrame(out)


def E5_screen_ledger(ctx):
    ser_m = pd.concat([ctx._ser_modal_layer, _series(ctx, "genre", "modal")], ignore_index=True); scr_m = _screen(ser_m, ctx.macro); scr_m["unit_level"] = "modal"
    if ctx.U != "U1":
        ser_u = pd.concat([getattr(ctx, "_ser_unit_layer", _series(ctx, "layer", ctx.unit_col)), _series(ctx, "genre", ctx.unit_col)], ignore_index=True)
        scr_u = _screen(ser_u[ser_u.unit != "ALL"], ctx.macro); scr_u["unit_level"] = ctx.U
    else: scr_u = scr_m.iloc[0:0].copy()
    scr = pd.concat([scr_m, scr_u], ignore_index=True); pc.save(scr.round(4), ctx.out, "E5_screen")
    led = pd.concat([_ledger(scr_m).assign(unit_level="modal"), _ledger(scr_u).assign(unit_level=ctx.U)], ignore_index=True) if len(scr_u) else _ledger(scr_m).assign(unit_level="modal")
    led = led[led.category != "none"] if len(led) else led; pc.save(led, ctx.out, "E5_ledger")
    cl = led[led.level == "layer"] if len(led) else led
    cnt = cl.groupby(["macro", "category"]).size().unstack(fill_value=0) if len(cl) else pd.DataFrame()
    top = cl[cl.category == "confirmed"].assign(a=lambda d: d.rho_T2.abs()).sort_values("a", ascending=False).drop(columns="a").head(15) if len(cl) else cl
    ctx.summary["E5"] = dict(n_screen=int(len(scr)), n_bh_T1=int(((scr.period == "T1") & scr.eligible & (scr.q_rho < .05)).sum()) if len(scr) else 0,
                             counts={mv: {c: int(cnt.loc[mv, c]) if (mv in cnt.index and c in cnt.columns) else 0 for c in ("confirmed", "era_composition", "T1_only")} for mv in ("vix", "cfnai")},
                             confirmed_top=top.to_dict("records") if len(top) else [], confirmed_by_layer=(cl[cl.category == "confirmed"].groupby(["key", "macro"]).size().reset_index(name="n").to_dict("records") if len(cl) else []),
                             statement_confirmed_vix=int(((cl.key == "statement") & (cl.macro == "vix") & (cl.category == "confirmed")).sum()) if len(cl) else 0)


# ----------------------------------------------------------------------------------------------
def E6_leadlag(ctx):
    mon = ctx.monthly; ser_g = _series(ctx, "genre", "modal")
    feats = ser_g[ser_g.unit.isin(["ALL"] + SIX)].copy()
    if ctx.U != "U1":
        su = _series(ctx, "genre", ctx.unit_col); top = su[su.unit != "ALL"].groupby("unit")["count"].sum().sort_values(ascending=False).head(6).index.tolist(); feats = pd.concat([feats, su[su.unit.isin(top)]], ignore_index=True)
    feats["ym"] = pd.to_datetime(feats.date).dt.to_period("M"); df = feats.merge(ctx.macro, on="doc_id", how="left")
    ccf, gr, pred = [], [], []
    for (key, unit), s in df.groupby(["key", "unit"]):
        s = s.sort_values("date")
        for T in ("T1", "T2"):
            st = s[pc.period_mask(s.date, T)]
            if len(st) < pc.MIN_N or (st["count"] == 0).mean() > pc.MAX_ZERO or st["count"].sum() < pc.MIN_TOKENS: continue
            for mv, col in (("cfnai", "CFNAIMA3"), ("vix", "VIX_M")):
                for k in range(-9, 10):
                    mac = [mon[col].get(ym + k, np.nan) for ym in st.ym]; c = pc.corr_pair(st.per1k, mac); ccf.append(dict(key=key, unit=unit, period=T, macro=mv, k=k, **c))
                mac = np.array([mon[col].get(ym, np.nan) for ym in st.ym], float); y = st.per1k.values.astype(float); ok = ~np.isnan(mac)
                if ok.sum() >= pc.MIN_N:
                    d = pd.DataFrame({"text": y[ok], "macro": mac[ok]})
                    for lag in (1, 2, 3):
                        try:
                            g1 = grangercausalitytests(d[["macro", "text"]], maxlag=lag, verbose=False)[lag][0]["ssr_ftest"][1]; g2 = grangercausalitytests(d[["text", "macro"]], maxlag=lag, verbose=False)[lag][0]["ssr_ftest"][1]
                        except Exception: g1 = g2 = np.nan
                        gr.append(dict(key=key, unit=unit, period=T, macro=mv, lag=lag, p_text_to_macro=float(g1), p_macro_to_text=float(g2), n=int(ok.sum())))
            if T == "T1":
                for target, base_x in (("cfnai_ma3_lead3", ["cfnai_ma3_lag2", "vix_pre28"]), ("d_vix_28", ["vix_pre28", "cfnai_ma3_lag2"])):
                    if target not in st.columns: continue
                    m0 = pc.hac_ols(st[target], st[base_x]); X1 = st[base_x].copy(); X1["text"] = st.per1k.values; m1 = pc.hac_ols(st[target], X1)
                    if m0 and m1: pred.append(dict(key=key, unit=unit, target=target, r2_base=round(m0["r2"], 4), r2_with=round(m1["r2"], 4), delta_r2=round(m1["r2"] - m0["r2"], 4), coef_text=round(m1["coef"]["text"], 4), p_text=m1["p"]["text"], n=m1["n"]))
    ccfd = pd.DataFrame(ccf); grd = pd.DataFrame(gr); prd = pd.DataFrame(pred)
    if len(ccfd): pc.save(ccfd.round(4), ctx.out, "E6_ccf")
    if len(grd):
        grd["q_text_to_macro"] = np.nan
        for (T, lag), idx in grd.groupby(["period", "lag"]).groups.items(): grd.loc[idx, "q_text_to_macro"] = pc.bh(grd.loc[idx, "p_text_to_macro"])
        pc.save(grd.round(4), ctx.out, "E6_granger")
    if len(prd): prd["q_text"] = pc.bh(prd.p_text); pc.save(prd.round(4), ctx.out, "E6_predictive")
    peaks = []
    if len(ccfd):
        for (key, unit, T, mv), s in ccfd[ccfd.period == "T2"].dropna(subset=["r"]).groupby(["key", "unit", "period", "macro"]):
            best = s.iloc[s.r.abs().argmax()]
            if best.p_r < .05 and best.p_rho < .05: peaks.append(dict(key=key, unit=unit, macro=mv, k=int(best.k), r=round(best.r, 3), rho=round(best.rho, 3)))
    ctx.summary["E6"] = dict(ccf_peaks_T2=peaks[:25], granger_q10=(grd[(grd.period == "T2") & (grd.q_text_to_macro < .10)][["key", "unit", "macro", "lag", "p_text_to_macro", "q_text_to_macro"]].to_dict("records") if len(grd) else []),
                             granger_min_q=(float(grd[grd.period == "T2"].q_text_to_macro.min()) if len(grd) else None),
                             predictive_q10=(prd[prd.q_text < .10].to_dict("records") if len(prd) else []), predictive_min_q=(float(prd.q_text.min()) if len(prd) else None), n_predictive=int(len(prd)))


# ----------------------------------------------------------------------------------------------
def E7_event_study(ctx):
    mon = ctx.monthly; rows, mrows = [], []
    ml = "statement" if "statement" in ctx.layers else ctx.main_layer
    ser = ctx._ser_modal_layer[(ctx._ser_modal_layer.key == ml)]
    if ctx.U != "U1" and hasattr(ctx, "_ser_unit_layer"):
        su = ctx._ser_unit_layer[(ctx._ser_unit_layer.key == ml) & (ctx._ser_unit_layer.unit != "ALL")]; top = su.groupby("unit")["count"].sum().sort_values(ascending=False).head(6).index.tolist(); ser = pd.concat([ser, su[su.unit.isin(top)]], ignore_index=True)
    ser = ser.sort_values("date"); dates = sorted(ser.date.unique())
    for d, lab in EVENTS:
        if not (dates[0] <= d <= dates[-1]): continue
        i0 = int(np.searchsorted(np.array(dates), d)); i0 = min(i0, len(dates) - 1)
        for u, s in ser.groupby("unit"):
            s = s.groupby("date").per1k.mean()   # several speeches can share a date
            def win(a, b): idx = [dates[j] for j in range(max(0, i0 + a), min(len(dates), i0 + b + 1))]; return float(s.reindex(idx).mean()) if idx else np.nan
            rows.append(dict(event=lab, event_date=d, layer=ml, series=u, pre3=round(win(-3, -1), 3), at=round(win(0, 0), 3), post3=round(win(1, 3), 3)))
        ym = pd.Period(d[:7], freq="M")
        for k in range(-6, 7): mrows.append(dict(event=lab, event_date=d, k=k, cfnai_ma3=mon["CFNAIMA3"].get(ym + k, np.nan), vix=mon["VIX_M"].get(ym + k, np.nan)))
    ev = pd.DataFrame(rows); mv = pd.DataFrame(mrows); pc.save(ev, ctx.out, "E7_event_text"); pc.save(mv, ctx.out, "E7_event_macro")
    if len(mv):
        evs = [e for e in EVENTS if e[0] in set(mv.event_date)][:8]; fig, axes = plt.subplots(2, 4, figsize=(13, 5.2)); axes = axes.ravel()
        for ax, (d, lab) in zip(axes, evs):
            sub = mv[mv.event_date == d]; ax.plot(sub.k, sub.cfnai_ma3, color="#24507A", marker="."); ax.set_ylabel("CFNAI-MA3", color="#24507A"); ax2 = ax.twinx(); ax2.plot(sub.k, sub.vix, color="#A8501F", marker="."); ax2.set_ylabel("VIX", color="#A8501F")
            ax.axvline(0, color="k", lw=0.6, ls=":"); ax.set_title(f"{lab} ({d})", fontsize=8); ax.set_xlabel("months from event")
        for ax in axes[len(evs):]: ax.axis("off")
        fig.suptitle("E7 macro environment around policy events (k = 0 event month)"); _fig(fig, ctx, "E7_event_macro")
    ctx.summary["E7"] = dict(layer=ml, all_series=ev[ev.series == "ALL"][["event", "event_date", "pre3", "at", "post3"]].to_dict("records") if len(ev) else [])


# ----------------------------------------------------------------------------------------------
def E8_robustness(ctx):
    ser = ctx._ser_modal_layer; df = _with_macro(ser, ctx.macro); rows = []
    variants = [("baseline per1k, T1", "per1k", MACRO_VARS, "T1"), ("per1k, excl-2020", "per1k", MACRO_VARS, "T2"), ("per1k, 2010–2026", "per1k", MACRO_VARS, "T3"),
                ("CFNAI lag 1", "per1k", {"cfnai": "cfnai_ma3_lag1", "vix": "vix_pre28"}, "T1"), ("VIX inter-meeting", "per1k", {"cfnai": "cfnai_ma3_lag2", "vix": "vix_intermeeting"}, "T1"),
                ("share (N2)", "share", MACRO_VARS, "T1"), ("count (N3)", "count", MACRO_VARS, "T1")]
    for (lay, u), s in df.groupby(["key", "unit"]):
        if u not in ["ALL"] + SIX: continue
        s = s.sort_values("date")
        for name, ycol, mvars, T in variants:
            st = s[pc.period_mask(s.date, T)]
            if len(st) < pc.MIN_N: continue
            r = dict(layer=lay, series=u, variant=name)
            for mv, col in mvars.items():
                if col not in st.columns or st[col].notna().sum() < pc.MIN_N: r[f"rho_{mv}"] = np.nan; r[f"p_{mv}"] = np.nan; continue
                c = pc.corr_pair(st[ycol], st[col]); r[f"rho_{mv}"] = round(c["rho"], 3) if not pd.isna(c["rho"]) else np.nan; r[f"p_{mv}"] = round(c["p_rho"], 4) if not pd.isna(c["p_rho"]) else np.nan
            rows.append(r)
    d = pd.DataFrame(rows); pc.save(d, ctx.out, "E8_robustness")
    ctx.summary["E8"] = dict(all_rows=d[d.series == "ALL"].to_dict("records"))


# ----------------------------------------------------------------------------------------------
def E9_kawamura(ctx):
    tk9 = ctx.tk9.copy(); tk9["grp"] = np.where(tk9.modal.isin(HEDGE), "hedge", np.where(tk9.modal == "will", "commit", "other")); rows = []
    for level in ("genre", "layer"):
        ser = pc.unit_series(tk9, ctx.dl, level, "grp", min_tokens=1); df = _with_macro(ser, ctx.macro); df = df[pc.period_mask(df.date, "T1")]
        for (key, u), s in df.groupby(["key", "unit"]):
            if u not in ("ALL", "hedge", "commit") or len(s) < pc.MIN_N: continue
            s = s.sort_values("date").copy(); s["d_y"] = s.per1k.diff(); s["d_cfnai"] = s.cfnai_ma3_lag2.diff(); s["d_vix"] = s.vix_pre28.diff()
            for spec, xs, ycol in (("levels: CFNAI", ["cfnai_ma3_lag2"], "per1k"), ("levels: CFNAI + VIX", ["cfnai_ma3_lag2", "vix_pre28"], "per1k"), ("Δ: ΔCFNAI + ΔVIX", ["d_cfnai", "d_vix"], "d_y"),
                                    ("levels excl-2020: CFNAI + VIX", ["cfnai_ma3_lag2", "vix_pre28"], "per1k"), ("Δ excl-2020", ["d_cfnai", "d_vix"], "d_y")):
                ss = s[pc.period_mask(s.date, "T2")] if "excl-2020" in spec else s
                m = pc.hac_ols(ss[ycol], ss[xs])
                if m is None: continue
                for v in xs: rows.append(dict(level=level, key=key, series=u, spec=spec, var=VAR_LABEL.get(v, v), coef=round(m["coef"][v], 4), se=round(m["se"][v], 4), t=round(m["t"][v], 2), p=round(m["p"][v], 4), stars=pc.stars(m["p"][v]), n=m["n"], r2=round(m["r2"], 3)))
    d = pd.DataFrame(rows); pc.save(d, ctx.out, "E9_kawamura")
    neg = d[(d.var == "CFNAI-MA3") & (d.spec == "levels: CFNAI + VIX") & (d.coef < 0) & (d.p < .05)] if len(d) else d
    ctx.summary["E9"] = dict(countercyclical_cells=neg[["level", "key", "series", "coef", "p"]].to_dict("records") if len(neg) else [],
                             genre_all=d[(d.level == "genre") & (d.series == "ALL")][["key", "spec", "var", "coef", "t", "p", "stars", "n"]].to_dict("records") if len(d) else [])


BLOCKS = [E1_descriptives, E2_correlations, E3_regressions, E4_construction_regressions, E5_screen_ledger, E6_leadlag, E7_event_study, E8_robustness, E9_kawamura]


# ----------------------------------------------------------------------------------------------
def hypotheses(ctx) -> dict:
    s = ctx.summary; H = {}
    st = s.get("L3", {}).get("staircase_T1"); hl = s.get("L5", {}).get("half_life", {}).get("all")
    if st: H["H1"] = dict(verdict=("지지" if st["n_cp"] > 0 and st["n_cp_event"] >= 0.5 * st["n_cp"] else "부분"), evidence=f"변화점 {st['n_cp']}개 중 사건 ±1회의 {st['n_cp_event']}개; 보유율 반감기 {hl if hl else '≥24'}")
    else: H["H1"] = dict(verdict="해당 없음", evidence="성명서 층 없음")
    l2 = s.get("L2", {})
    H["H2"] = dict(verdict=("지지" if l2.get("cramers_v") and l2["p"] < .001 and l2["cramers_v"] >= 0.1 else ("해당 없음" if not l2.get("cramers_v") else "기각")), evidence=(f"χ²={l2.get('chi2')}, V={l2.get('cramers_v')}" if l2.get("cramers_v") else "층위 1개"))
    e9 = s.get("E9", {}).get("countercyclical_cells", []); e3 = s.get("E3", {}).get("all_by_layer", {})
    neg_layers = [lay for lay, sp in e3.items() if sp.get("(3)", {}).get("cfnai_ma3_lag2", {}).get("p", 1) < .05 and sp["(3)"]["cfnai_ma3_lag2"]["coef"] < 0 and sp.get("(6) excl-2020", {}).get("cfnai_ma3_lag2", {}).get("p", 1) < .05]
    neg_diff = [lay for lay, sp in e3.items() if sp.get("(7) Δ", {}).get("d_cfnai", {}).get("p", 1) < .05 and sp["(7) Δ"]["d_cfnai"]["coef"] < 0 and sp.get("(8) Δ excl-2020", {}).get("d_cfnai", {}).get("p", 1) < .05 and sp["(8) Δ excl-2020"]["d_cfnai"]["coef"] < 0]
    H["H3"] = dict(verdict=("지지" if neg_layers else ("부분" if neg_diff else "기각")),
                   evidence=((f"총밀도 CFNAI 계수 음·유의(수준, T1·T2): {neg_layers}" if neg_layers else "수준 회귀에서 어떤 층위의 총밀도도 CFNAI와 유의한 음의 관계 없음")
                             + (f"; 1차 차분(2020 포함·제외 모두)에서 음·유의: {neg_diff}" if neg_diff else "; 1차 차분에서도 없음") + (f"; 헤징군 반경기 셀 {len(e9)}" if e9 else "")))
    e5 = s.get("E5", {}); nv = e5.get("counts", {}).get("vix", {}).get("confirmed", 0); stv = e5.get("statement_confirmed_vix", 0); byl = e5.get("confirmed_by_layer", [])
    nonst = sum(r["n"] for r in byl if r["macro"] == "vix" and r["key"] != "statement")
    H["H4"] = dict(verdict=("지지" if (nonst >= 1 and stv == 0) else ("부분" if nv >= 1 else "기각")), evidence=f"확정 VIX 단위 {nv} (비성명서 층 {nonst}, 성명서 층 {stv})")
    e6 = s.get("E6", {}); n_g = len(e6.get("granger_q10", [])); n_p = len(e6.get("predictive_q10", []))
    H["H5"] = dict(verdict=("지지" if (n_g or n_p) else "기각"), evidence=f"Granger text→macro q<.10: {n_g}건 (최소 q={e6.get('granger_min_q')}); 예측 회귀 q<.10: {n_p}/{e6.get('n_predictive')} (최소 q={e6.get('predictive_min_q')})")
    return H
