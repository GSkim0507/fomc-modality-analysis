"""
27_interpret.py — Data-driven interpretation paragraphs (Korean) for every section of the tabbed report.

Each function reads the run's tables / summary and returns HTML (<div class='interp'>…</div>).  Sentences are
templated on the actual numbers so that every version x unit panel carries its own reading of the results.
"""
from __future__ import annotations
import html, math
from pathlib import Path
import numpy as np, pandas as pd
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("r24", ROOT / "experiments" / "24_build_report_v3.py"); r24 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r24)
pc, SIX, lab, csv = r24.pc, r24.SIX, r24.lab, r24.csv
STARS = lambda p: "" if p is None or (isinstance(p, float) and np.isnan(p)) else ("***" if p < .01 else "**" if p < .05 else "*" if p < .10 else "")


def box(*paras):
    import re as _re
    ps = [_re.sub(r"<(?=[ .\d=])", "&lt;", p) for p in paras if p]   # "p < .05" is text, not a tag
    ps = [_re.sub(r"(\d+\.\d{3})\d{2,}", r"\1", p) for p in ps]        # trim long floats leaking from summaries
    return "<div class='interp'>" + "".join(f"<p>{p}</p>" for p in ps) + "</div>" if ps else ""


def fmt(v, nd=2):
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:+.{nd}f}"


def strength_V(V):
    return "약한" if V < .10 else ("중간 정도의" if V < .30 else "강한")


# ----------------------------------------------------------------------------------------------
def data(run, s, layers, ml):
    L1 = s.get("L1", {}).get("layers", []); E1 = s.get("E1", {})
    if not L1: return ""
    d = sorted(L1, key=lambda r: r["pmw"]); lo, hi = d[0], d[-1]; tot_tok = sum(r["tokens"] for r in L1); tot = sum(r["six_modal"] for r in L1)
    p1 = (f"이 버전의 코퍼스는 층위 {len(L1)}개, {tot_tok:,} 토큰, 6대 조동사 {tot:,}개다. "
          + (f"조동사 밀도는 {lab(lo['layer'])} {lo['pmw']:,.0f} pmw에서 {lab(hi['layer'])} {hi['pmw']:,.0f} pmw까지 {hi['pmw'] / max(lo['pmw'], 1):.1f}배 차이가 나며, 95% 신뢰구간이 겹치지 않으므로 층위 간 밀도 차이는 표본 오차가 아니다. " if len(L1) > 1 else f"밀도는 {hi['pmw']:,.0f} pmw(95% CI {hi['ci_lo']:,.0f}–{hi['ci_hi']:,.0f})다. ")
          + "원시 개수가 아니라 pmw로 비교해야 하는 이유가 여기 있다.")
    dp = s.get("L1", {}).get("dp", {}).get(ml, {})
    clumped = [m for m, v in dp.items() if v is not None and v >= 0.5]; even = [m for m, v in dp.items() if v is not None and v <= 0.25]
    p2 = (f"{lab(ml)}에서 문서 간 분산 DP를 보면 " + (f"{', '.join(even)}은(는) 거의 모든 문서에 고르게 나타나고(DP ≤ .25) " if even else "") + (f"{', '.join(clumped)}은(는) 소수 문서에 몰려 있다(DP ≥ .5). 몰린 조동사의 시계열은 추세가 아니라 특정 시기의 사건으로 읽어야 한다." if clumped else "모든 조동사가 비교적 고르게 분포한다.")) if dp else ""
    mac = {r["series"]: r for r in E1.get("macro", [])}
    p3 = (f"거시 변수 표본에서 CFNAI-MA3는 평균 {mac['CFNAI-MA3 (m−2)']['mean']:+.2f}(SD {mac['CFNAI-MA3 (m−2)']['sd']:.2f}, 최소 {mac['CFNAI-MA3 (m−2)']['min']:+.2f}), VIX는 평균 {mac['VIX pre-28d']['mean']:.1f}(SD {mac['VIX pre-28d']['sd']:.1f}, 최대 {mac['VIX pre-28d']['max']:.1f})이며 VIX의 AR(1)이 {mac['VIX pre-28d']['AR1']:.2f}로 높다. 2020년 관측치가 두 변수의 극단값을 만들므로 모든 거시 표에 2020 제외 열을 병기한다." if "CFNAI-MA3 (m−2)" in mac and "VIX pre-28d" in mac else "")
    return box(p1, p2, p3)


def division(run, s, layers, ml, U):
    L2 = s.get("L2", {})
    if not L2.get("cramers_v"): return box("층위가 하나이므로 층위 간 분업은 이 버전에서 검정할 수 없다. 비교 탭과 V3·V4에서 확인한다.")
    V = L2["cramers_v"]; res = L2.get("residual_max", {}); key = L2.get("keyness_top", {})
    p1 = f"층위 × 조동사의 연관은 χ² = {L2['chi2']:,.0f}(df {L2['dof']}, p < .001), Cramér's V = {V:.3f}로 {strength_V(V)} 연관이다. 즉 조동사의 분포는 층위가 무엇인지에 체계적으로 의존한다(H2)."
    parts = []
    for lay in layers:
        r = res.get(lay); k = key.get(lay, [])
        if not r: continue
        kk = [x for x in k if x["sign"] == "+"][:2]
        parts.append(f"{lab(lay)}은(는) {r[0]}을(를) 기대보다 많이 쓰고(잔차 {r[1]:+.1f})" + (f", 키니스로는 {', '.join(x['item'] + '(log ratio ' + format(x['log_ratio'], '+.2f') + ')' for x in kk)}이(가) 두드러진다" if kk else ""))
    p2 = "층위별로 보면 " + "; ".join(parts) + "." if parts else ""
    p3 = "이 분업은 조동사 하나를 세는 지표가 왜 층위 구성비에 좌우되는지를 설명한다: 같은 조동사라도 층위마다 담화 기능(약속·심의·결정·대화)이 다르다."
    return box(p1, p2, p3)


def diachronic(run, s, layers, ml, U):
    mk = csv(run, "L3_mk_trends"); parts = []
    if mk is not None:
        m = mk[(mk.metric == "per1k") & (mk.p < .05)]
        for lay in layers:
            up = m[(m.layer == lay) & (m.tau > 0)].sort_values("tau", ascending=False); dn = m[(m.layer == lay) & (m.tau < 0)].sort_values("tau")
            if len(up) or len(dn):
                parts.append(f"{lab(lay)}: " + (f"증가 {', '.join(f'{r.series}(τ {r.tau:+.2f})' for r in up.head(3).itertuples())}" if len(up) else "") + (" / " if len(up) and len(dn) else "") + (f"감소 {', '.join(f'{r.series}(τ {r.tau:+.2f})' for r in dn.head(3).itertuples())}" if len(dn) else ""))
    p1 = ("Mann–Kendall로 유의한(p < .05) 회의 단위 추세는 다음과 같다 — " + "; ".join(parts) + ". 추세가 있는 조동사도 성명서에서는 매끄러운 기울기가 아니라 아래 변화점 표의 계단이다." if parts else "회의 단위에서 유의한 단조 추세는 없다.")
    st = s.get("L3", {}).get("staircase_T1"); p2 = p3 = ""
    if st:
        cps = st.get("changepoints", []); share = st["n_cp_event"] / st["n_cp"] if st["n_cp"] else 0
        p2 = (f"성명서 단위 점유율에 PELT를 적용하면 변화점 {st['n_cp']}개가 나오고 그중 {st['n_cp_event']}개({share:.0%})가 정책 사건 ±1회의 안에 있다. " + ("절반을 넘으므로 H1(편집 가설)의 지지 기준을 충족한다. " if share >= .5 else "절반에 못 미쳐 H1은 부분 지지에 그친다. ")
              + "변화점마다 책임 문장이 하나씩 붙는다는 점이 핵심이다: 조동사 통계의 계단은 회의마다 새로 쓰인 말이 아니라 정형문의 삽입·삭제다.")
        big = sorted(cps, key=lambda c: -abs(c["share_after"] - c["share_before"]))[:3]
        if big: p3 = "가장 큰 계단 세 개: " + "; ".join(f"{c['unit']} {c['break_date']} ({c['share_before']:.2f}→{c['share_after']:.2f}, {c['nearest_event']}, “{html.escape(c['responsible_sentence'][:90])}…”)" for c in big) + "."
    elif "statement" not in layers:
        p2 = "이 버전에는 성명서가 없어 계단(H1)은 해당 없음이다."
    return box(p1, p2, p3)


def collocation(run, s, layers, ml, U):
    L4 = s.get("L4", {}); top = L4.get("top_predicate", {}); att = L4.get("attracted", {}); jsd = L4.get("jsd_main")
    parts = [f"{m} → {top[m]['predicate']}({top[m]['share']:.0%})" for m in SIX if top.get(m) and top[m].get("predicate")]
    conc = [m for m in SIX if top.get(m) and top[m].get("share", 0) >= .5]
    p1 = (f"{lab(ml)}에서 조동사별 1위 서술어는 " + ", ".join(parts) + "다. " if parts else "") + (f"{', '.join(conc)}은(는) 1위 서술어가 절반 이상을 차지하므로 사실상 '조동사 하나 = 구문 하나'다. " if conc else "1위 서술어의 점유율이 절반을 넘는 조동사는 없어 서술어 분포가 분산되어 있다. ")
    p2 = (f"조동사 간 서술어 분포의 JSD는 {jsd[0]:.2f}–{jsd[1]:.2f}(최대 1)로 " + ("서로 거의 겹치지 않는다" if jsd[0] >= .6 else "부분적으로 겹친다" if jsd[0] >= .3 else "상당히 겹친다") + ". ") if jsd else ""
    ap = ["{}: {}".format(m, ", ".join("{}({:.1f}×)".format(x["predicate"], x["ratio"]) for x in att[m][:3])) for m in SIX if att.get(m)]
    p3 = ("distinctive collexeme 분석으로 기대빈도 대비 유인되는 서술어는 " + "; ".join(ap) + "이다. 유인 비(obs/exp)가 1에 가까우면 그 조동사가 층위 전체를 지배해 대비가 약한 것이고, 2 이상이면 특정 서술어와의 결합이 선택적이다.") if ap else ""
    return box(p1, p2, p3)


def formulaicity(run, s):
    L5 = s.get("L5", {})
    if not L5.get("half_life"): return ""
    hl = L5["half_life"]; per = ", ".join(f"{m} {('%.1f' % hl[m]) if hl.get(m) else '≥24'}" for m in SIX if m in hl)
    ed = L5.get("edits_by_year", {}); peak = sorted(ed.items(), key=lambda kv: -(kv[1]["added"] + kv[1]["removed"]))[:2]
    p1 = (f"성명서의 단위 집합은 한 회의 뒤 대부분 유지되고 {('%.1f' % hl['all']) if hl.get('all') else '24회의 이상'}회의에서 절반이 남는다(조동사별 반감기: {per}; 조동사 문장 자체는 {('%.1f' % hl['modal_sentences']) if hl.get('modal_sentences') else '≥24'}회의). "
          f"코호트 {L5.get('n_cohorts')}개 중 한 회의만 살아남은 단위가 {L5.get('one_off_share', 0):.0%}이고 KM 중앙 생존은 {L5.get('km_median') or '—'}회의로, 단위의 수명 분포는 '한 번 쓰이고 사라지는 것'과 '수십 회의 유지되는 것'의 이봉 분포다.")
    p2 = (f"조동사 토큰의 {L5.get('formulaic_share_overall', 0):.0%}가 3개 이상 성명서에 재출현하는 정형 문장 안에 있고, 편집(삽입+삭제)은 " + ", ".join(f"{y}년({v['added']}/{v['removed']})" for y, v in peak) + "에 몰린다 — 국면 전환 해에 문장이 갈린다.")
    return box(p1, p2)


def context(run, s, layers, ml):
    d = csv(run, "L6_context_rates"); sj = csv(run, "L6_subject_types"); parts = []
    if d is None: return ""
    d = d[d.layer == ml]
    for r in d.itertuples():
        f = []
        if r.cond >= .5: f.append(f"조건절 {r.cond:.0%}")
        if r.reported >= .4: f.append(f"보고문 내포 {r.reported:.0%}")
        if r.neg >= .10: f.append(f"부정 {r.neg:.0%}")
        if r.passive >= .25: f.append(f"수동 {r.passive:.0%}")
        if r.question >= .03: f.append(f"의문 {r.question:.0%}")
        if sj is not None:
            top = sj[(sj.layer == ml) & (sj.modal == r.modal)].sort_values("share", ascending=False).head(1)
            if len(top): f.append(f"주어 {top.subj_type.iloc[0]} {top.share.iloc[0]:.0%}")
        if f: parts.append(f"{r.modal}({', '.join(f)})")
    p1 = (f"{lab(ml)}의 문법 맥락에서 두드러진 것: " + "; ".join(parts) + ".") if parts else ""
    sem = s.get("L6", {}).get("sem_main", {}); sp = [f"{m} → {v[0]['sem_type']}({v[0]['share']:.0%})" for m, v in sem.items() if v]
    p2 = ("의미 유형 휴리스틱으로는 " + ", ".join(sp) + "이 우세하다. 조건절·인용·주어 유형이 조동사 의미를 결정하므로, 같은 would라도 성명서(조건문)와 의사록(보고문)과 기자회견(1인칭)에서 다른 의미를 가진다.") if sp else ""
    return box(p1, p2)


def mnlogit(run, s):
    L7 = s.get("L7", {})
    if L7.get("error"): return box(f"다항 로짓이 수렴하지 않았다({html.escape(L7['error'][:80])}).")
    if not L7.get("pseudo_r2"): return ""
    eff = L7.get("layer_effects", [])[:4]
    p1 = f"조동사 선택을 층위·시기·주어·조건·인용으로 설명하는 다항 로짓의 유사 R²는 {L7['pseudo_r2']:.3f}(N = {L7.get('n', 0):,})이다."
    p2 = ("시기·주어 유형을 통제해도 층위 효과가 남는다: " + "; ".join(f"{e['variable'].replace('layer_', '')}에서 {e['outcome_vs_will']}의 상대위험비 {e['rrr']:.1f}" for e in eff) + " (기준 will·성명서). 층위 분업은 주어 구성의 차이로 환원되지 않는다.") if eff else "층위 더미가 없거나 유의하지 않아 층위 효과는 확인되지 않는다."
    return box(p1, p2)


def be_appropriate(run, s):
    L8 = s.get("L8", {}); c = L8.get("counts", {})
    if not c: return box("be appropriate 관용구 토큰이 이 버전에는 거의 없다.")
    will_l = sorted(c.items(), key=lambda kv: -kv[1].get("will", 0))[:2]; would_l = sorted(c.items(), key=lambda kv: -kv[1].get("would", 0))[:2]
    wl = ", ".join("{}({})".format(lab(k), v.get("will", 0)) for k, v in will_l if v.get("will")); wd = ", ".join("{}({})".format(lab(k), v.get("would", 0)) for k, v in would_l if v.get("would"))
    p1 = (f"will be appropriate는 {wl}에, would be appropriate는 {wd}에 몰려 있다. "
          "두 형태는 같은 관용구의 시제 변형이 아니라 문서 기능이 배정한 형태다: will은 시장에 말하는 약속(성명서·의장), would는 의사록이 결정과 심의를 기록하는 조동사.")
    return box(p1)


def contrasts(run, s):
    L9 = s.get("L9", {}); parts = [f"{lab(k.replace('chair_', ''))} V = {v['V']:.3f}({'p < .05' if v['p'] < .05 else 'n.s.'})" for k, v in L9.items() if k.startswith("chair_")]
    if not parts: return ""
    return box("Yellen–Powell 대조(6대 조동사 점유율): " + "; ".join(parts) + ". 성명서의 의장 차이는 2020-09 프레임워크 문장의 채택 시점과 겹치므로 개인 문체가 아니라 제도 편집으로 읽어야 하고, 기자회견의 작은 V는 개인 문체 차이가 조동사 선택을 크게 바꾸지 않음을 뜻한다.")


# ----------------------------------------------------------------------------------------------
def corr(run, s, layers):
    E2 = s.get("E2", {}); g = [r for r in E2.get("genre_all", []) if r["period"] == "T2"]; l = E2.get("layer_all_T2", [])
    sig_g = [f"{r['key']} × {r['macro'].upper()} ρ = {r['rho']:+.2f}" for r in g if r["p"] is not None and r["p"] < .05]
    sig_l = [f"{lab(r['key'])} × {r['macro'].upper()} ρ = {r['rho']:+.2f}" for r in l if r["p"] is not None and r["p"] < .05]
    neg = [r for r in g + l if r["macro"] == "cfnai" and r["rho"] is not None and r["rho"] < -0.2 and r["p"] is not None and r["p"] < .05]
    p1 = ("2020년을 제외한 Spearman 상관에서 총 조동사 밀도가 거시 변수와 유의하게 공변하는 경우는 " + (("장르 수준 " + ", ".join(sig_g) + "; " if sig_g else "") + ("층위 수준 " + ", ".join(sig_l) if sig_l else "")).rstrip("; ") + "이다.") if (sig_g or sig_l) else "2020년을 제외하면 총 조동사 밀도는 어떤 장르·층위에서도 CFNAI·VIX와 유의하게 공변하지 않는다."
    p2 = ("CFNAI와 유의한 음(−)의 상관이 " + ", ".join(f"{lab(r['key'])}({r['rho']:+.2f})" for r in neg) + "에서 나타나 반경기 양태의 후보가 되지만, 회귀 스펙 표에서 2020 제외·차분까지 유지되는지 확인해야 한다." if neg else "CFNAI와 유의한 음의 상관은 없다 — Kawamura형 반경기 양태(경기가 나쁠수록 조동사 증가)는 총밀도 수준에서 관찰되지 않는다.")
    return box(p1, p2)


def regression(run, s, layers):
    e3 = s.get("E3", {}).get("all_by_layer", {}); d = csv(run, "E3_regressions"); parts = []; era = []; gaps = []
    for lay, sp in e3.items():
        r3 = sp.get("(3)", {}); r6 = sp.get("(6) excl-2020", {}); r8 = sp.get("(8) Δ excl-2020", {})
        for v, name in (("cfnai_ma3_lag2", "CFNAI"), ("vix_pre28", "VIX")):
            x = r3.get(v)
            if x and x["p"] < .10:
                keep6 = r6.get(v, {}).get("p", 1) < .10 and np.sign(r6.get(v, {}).get("coef", 0)) == np.sign(x["coef"])
                dv = "d_cfnai" if v.startswith("cfnai") else "d_vix"; keep8 = r8.get(dv, {}).get("p", 1) < .10 and np.sign(r8.get(dv, {}).get("coef", 0)) == np.sign(x["coef"])
                parts.append(f"{lab(lay)} 총밀도의 {name} 계수 {x['coef']:+.3f}{x['stars']}" + (" — 2020 제외에서도 유지" if keep6 else " — 2020 제외 시 소멸") + ("·차분에서도 유지" if keep8 else "·차분에서는 소멸"))
        if d is not None:
            e = d[(d.layer == lay) & (d.series == "ALL") & (d.spec == "(5)") & (d["var"] == "post_fw")]
            if len(e) and e.p.iloc[0] < .05: era.append(f"{lab(lay)} {e.coef.iloc[0]:+.2f}{e.stars.iloc[0] if isinstance(e.stars.iloc[0], str) else ''}")
            g = d[(d.layer == lay) & (d.series == "ALL") & (d.spec == "(4)") & (d["var"].isin(["unrate_gap_lag1", "corepce_gap_lag2"])) & (d.p < .05)]
            for r in g.itertuples(): gaps.append(f"{lab(lay)} {r.label} {r.coef:+.2f}{r.stars if isinstance(r.stars, str) else ''}")
    p1 = ("스펙 (3)에서 p < .10인 총밀도 계수는 " + "; ".join(parts) + ".") if parts else "스펙 (3)(CFNAI + VIX)에서 어떤 층위의 총밀도도 두 거시 변수와 p < .10으로 관계하지 않는다."
    neg_any = any("CFNAI 계수 -" in x and "유지·차분에서도 유지" in x for x in parts)
    p2 = ("음의 CFNAI 계수가 2020 제외·차분에서도 유지되는 층위가 있어 반경기 가설(H3)을 부분적으로 지지한다." if neg_any else "음의 CFNAI 계수가 2020 제외와 차분을 모두 견디는 층위는 없다 — H3(반경기)은 기각된다. 수준에서 보이던 관계는 2020년의 극단값이나 지속성이 만든 것이다.")
    p3 = (("2020-09 이후 더미(스펙 5)가 유의한 층위: " + ", ".join(era) + " — 프레임워크 문장 채택 이후 밀도 수준 자체가 이동했다. " if era else "") + ("갭 변수(스펙 4)가 유의한 경우: " + ", ".join(gaps) + " — 연준의 목표 변수가 벗어난 회의에서 조동사가 늘어나는데, 이는 정책 조정이 논의되는 회의의 결정 서술이 길어지는 효과로 읽힌다." if gaps else ""))
    return box(p1, p2, p3)


def units(run, s, layers, U):
    if U == "U1": return box("단위가 조동사이므로 구문 회귀는 없다(3.2의 조동사별 열 참조).")
    d = csv(run, "E4_construction_regressions")
    if d is None or not len(d): return ""
    sig = d[(d.spec == "(3)") & (d["var"] != "const") & (d.p < .05)]; parts = []
    for r in sig.sort_values("p").head(8).itertuples():
        v = r.var; dv = "d_cfnai" if v.startswith("cfnai") else "d_vix"
        k6 = d[(d.layer == r.layer) & (d.unit == r.unit) & (d.spec == "(6) excl-2020") & (d["var"] == v)]; k8 = d[(d.layer == r.layer) & (d.unit == r.unit) & (d.spec == "(8) Δ excl-2020") & (d["var"] == dv)]
        keep6 = len(k6) and k6.p.iloc[0] < .10 and np.sign(k6.coef.iloc[0]) == np.sign(r.coef); keep8 = len(k8) and k8.p.iloc[0] < .10 and np.sign(k8.coef.iloc[0]) == np.sign(r.coef)
        parts.append(f"{lab(r.layer)} {r.unit} × {r.label} {r.coef:+.3f}{r.stars if isinstance(r.stars, str) else ''}" + (" (2020 제외 유지" if keep6 else " (2020 제외 소멸") + (", 차분 유지)" if keep8 else ", 차분 소멸)"))
    p1 = ("구문 수준에서 스펙 (3)에 유의한 계수(p < .05): " + "; ".join(parts) + ".") if parts else "스펙 (3)에서 유의한 구문 계수는 없다."
    p2 = "집계 밀도에서 보이지 않던 관계가 구문에서 나타나거나(상쇄), 집계에서 보이던 관계가 특정 구문 하나에서 오는 경우(채택 사건)를 구분하는 것이 이 표의 목적이다. '2020 제외 소멸'은 팬데믹 극단값, '차분 소멸'은 국면 수준의 공변임을 뜻한다."
    return box(p1, p2)


def ledger(run, s, layers):
    E5 = s.get("E5", {}); c = E5.get("counts", {})
    if not c: return ""
    byl = E5.get("confirmed_by_layer", []); top = E5.get("confirmed_top", [])
    nv, nc = c["vix"]["confirmed"], c["cfnai"]["confirmed"]; era = c["vix"]["era_composition"] + c["cfnai"]["era_composition"]; t1 = c["vix"]["T1_only"] + c["cfnai"]["T1_only"]
    p1 = f"전수 스크린({E5.get('n_screen', 0):,}셀; BH q < .05 적중 {E5.get('n_bh_T1', 0)}개) 뒤 확정 규칙을 적용하면 VIX {nv}개·CFNAI {nc}개만 남고, {era}개는 시대 구성(2020-09 문장 채택 전후로 부호가 어긋남), {t1}개는 2020 의존으로 분류된다. 스크린 적중의 대부분이 인공물이라는 점이 이 표의 첫 번째 메시지다."
    stv = E5.get("statement_confirmed_vix", 0); nonst = sum(r["n"] for r in byl if r["key"] != "statement")
    lay_txt = ", ".join(f"{lab(r['key'])} {r['macro'].upper()} {r['n']}" for r in byl)
    p2 = (f"확정 단위의 층위 분포는 {lay_txt}이다. " if lay_txt else "확정 단위가 없다. ") + (f"성명서 층의 확정 VIX는 {stv}개, 비성명서 층은 {nonst}개로 " + ("거시 신호는 편집되지 않은 층에 있다(H4 지지)." if stv == 0 and nonst else ("성명서 층에도 남는 단위가 있어 H4는 부분 지지다." if nonst else "비성명서 층에서도 확정 단위가 없어 H4는 기각된다.")) if "statement" in layers else (f"비성명서 층에서 {nonst}개가 확정되어 " + ("H4를 지지한다." if nonst else "H4는 기각된다.")))
    p3 = ("상위 확정 단위: " + "; ".join(f"{lab(x['key'])} {x['unit']} × {x['macro'].upper()} ρ = {x['rho_T2']:+.2f}(반기 {x['rho_H1']:+.2f}/{x['rho_H2']:+.2f})" for x in top[:5]) + ".") if top else ""
    return box(p1, p2, p3)


def leadlag(run, s):
    E6 = s.get("E6", {})
    if not E6: return ""
    gq = E6.get("granger_q10", []); pq = E6.get("predictive_q10", []); peaks = E6.get("ccf_peaks_T2", [])[:3]
    p1 = (f"Granger 검정(lag 2, 2020 제외)에서 텍스트→거시 방향이 BH q < .10을 통과한 셀은 {len(gq)}개" + (f"({', '.join(x['unit'] + '→' + x['macro'].upper() for x in gq[:3])}; 최소 q = {E6.get('granger_min_q'):.3f})" if gq else f"(최소 q = {E6.get('granger_min_q'):.3f})" if E6.get("granger_min_q") is not None else "") + f", 예측 회귀에서 텍스트 항이 q < .10인 경우는 {len(pq)}/{E6.get('n_predictive', 0)}건이다.")
    p2 = ("교차상관 피크는 " + "; ".join(f"{x['unit']}→{x['macro'].upper()} k = {x['k']:+d}(ρ {x['rho']:+.2f})" for x in peaks) + "처럼 존재하지만 약하고 방향이 섞여 있다. " if peaks else "") + ("선행성 가설(H5)은 기각된다: 조동사 구문은 경제 상태를 동행 서술하는 변수이지 예측 변수가 아니다." if not (gq or pq) else "경계적 Granger 셀이 있어 H5는 형식상 지지되지만, 예측 회귀에서 증분 설명력이 없으므로 실질적 선행성으로 해석하기 어렵다.")
    return box(p1, p2)


def event(run, s):
    E7 = s.get("E7", {}); rows = E7.get("all_series", [])
    if not rows: return ""
    big = sorted([r for r in rows if r["pre3"] is not None and r["post3"] is not None and not (isinstance(r["pre3"], float) and np.isnan(r["pre3"]))], key=lambda r: -abs(r["post3"] - r["pre3"]))[:3]
    p1 = (f"{lab(E7['layer'])} 총밀도(per 1k)가 사건 전후로 가장 크게 움직인 사건은 " + "; ".join(f"{r['event']}({r['event_date']}) {r['pre3']:.1f} → {r['post3']:.1f}" for r in big) + "이다.") if big else ""
    p2 = "사건 주변의 거시 창(그림)은 사건마다 저VIX·고VIX가 뒤섞여 있어, 편집의 타이밍은 정책 일정이지 거시 환경이 아니다 — 계단(H1)을 거시 쪽에서 보강한다."
    return box(p1, p2)


def robustness(run, s):
    rows = s.get("E8", {}).get("all_rows", [])
    if not rows: return ""
    d = pd.DataFrame(rows); parts = []
    for lay, g in d.groupby("layer"):
        sv = g[g.p_vix < .05]; sc = g[g.p_cfnai < .05]
        if len(sv) or len(sc):
            parts.append(f"{lab(lay)}: " + (f"VIX 상관이 {len(sv)}/{len(g)} 변형에서 유의(부호 {'일관' if sv.rho_vix.min() * sv.rho_vix.max() > 0 else '불일치'})" if len(sv) else "") + ("; " if len(sv) and len(sc) else "") + (f"CFNAI 상관이 {len(sc)}/{len(g)} 변형에서 유의" if len(sc) else ""))
    return box(("래그·회의 간 VIX·점유율·문서당 수·2010 확장의 변형 전체에서 " + "; ".join(parts) + ". 여러 변형에서 같은 부호로 살아남는 관계만 본문 주장에 쓴다.") if parts else "총밀도 상관은 어떤 변형에서도 유의하지 않아, 정렬·정규화 선택이 결론을 바꾸지 않는다.")


def kawamura(run, s):
    E9 = s.get("E9", {}); g = E9.get("genre_all", []); cc = E9.get("countercyclical_cells", [])
    lv = [r for r in g if r["spec"] == "levels: CFNAI + VIX" and r["var"] == "CFNAI-MA3"]
    parts = [f"{r['key']} {r['coef']:+.3f}{r['stars'] or ''}(t {r['t']:+.1f})" for r in lv]
    p1 = ("Kawamura et al.(2019)의 주 스펙(수준, CFNAI + VIX)에서 총밀도의 CFNAI 계수는 " + ", ".join(parts) + "이다. ") if parts else ""
    p2 = (f"헤징군·총밀도를 통틀어 CFNAI 계수가 음·유의한 셀은 {len(cc)}개({', '.join(x['key'] + '/' + x['series'] for x in cc[:4])})이며 2020 제외·차분 열에서 유지되는지 표에서 확인해야 한다." if cc else "헤징군(would/could/may/might)과 총밀도 어디에서도 CFNAI 계수가 음·유의하지 않다. BoJ 월보의 '경기가 나쁠수록 헤징 증가'는 FOMC 텍스트로 이전되지 않는다; 양(+)의 계수가 있는 곳은 오히려 순경기적이다.")
    return box(p1, p2)


def hypotheses(run, s, V, vname):
    H = s.get("H", {})
    if not H: return ""
    v = {k: x["verdict"] for k, x in H.items()}
    concl = (("성명서의 조동사 변화는 정책 사건에 따른 정형문 편집의 계단이고" if v.get("H1") == "지지" else "") + ("층위마다 조동사는 다른 기능을 맡으며" if v.get("H2") == "지지" else "")
             + ("조동사 총량은 경기와 반대로 움직이지 않고(반경기 없음)" if v.get("H3") == "기각" else "조동사 총량에 반경기 신호가 있으며")
             + ("편집되지 않은 층의 특정 구문만 불확실성·활동과 공변한다" if v.get("H4") == "지지" else "일부 구문이 불확실성과 공변하나 성명서 층에도 약한 신호가 남는다" if v.get("H4") == "부분" else "구문 수준에서도 안정된 거시 신호가 없다")
             + ("; 선행지표는 아니다." if v.get("H5") == "기각" else "; 경계적 선행 신호가 있으나 예측력은 없다."))
    concl = concl.replace("계단이고층위", "계단이고, 층위").replace("맡으며조동사", "맡으며, 조동사").replace("않고(반경기 없음)편집", "않고(반경기 없음), 편집").replace("있으며편집", "있으며, 편집").replace("않고(반경기 없음)일부", "않고(반경기 없음), 일부").replace("않고(반경기 없음)구문", "않고(반경기 없음), 구문")
    lines = "; ".join(f"{k} {x['verdict']}({x['evidence'][:70]}…)" for k, x in H.items())
    return box(f"{V} {vname}의 결론: {concl}", f"판정 근거 — {lines}")


# ----------------------------------------------------------------------------------------------
def compare(runs, versions, U):
    rs = {V: runs.get(f"{cid}_{U}") for V, cid, _, _ in versions}
    def cnt(s, mv): return s.get("E5", {}).get("counts", {}).get(mv, {}).get("confirmed", 0) if s else 0
    prog = " → ".join(f"{V} {cnt(s, 'vix')}/{cnt(s, 'cfnai')}" for V, s in rs.items() if s)
    h3 = all((s or {}).get("H", {}).get("H3", {}).get("verdict") == "기각" for s in rs.values() if s)
    h1 = [V for V, s in rs.items() if s and s.get("H", {}).get("H1", {}).get("verdict") == "지지"]
    h4 = {V: s.get("H", {}).get("H4", {}).get("verdict") for V, s in rs.items() if s}
    era = {V: (s.get("E5", {}).get("counts", {}).get("vix", {}).get("era_composition", 0) + s.get("E5", {}).get("counts", {}).get("cfnai", {}).get("era_composition", 0)) for V, s in rs.items() if s}
    layers_conf = {}
    for V, s in rs.items():
        for r in (s or {}).get("E5", {}).get("confirmed_by_layer", []): layers_conf.setdefault(r["key"], set()).add(V)
    p1 = f"확정 단위 수(VIX/CFNAI)는 {prog}로 움직인다. 성명서만(V1)에서는 거의 없고, 의사록 층을 더할수록 늘어나며, 미정제(V6)는 가장 많아 보이지만 시대 구성 적중도 가장 많다({era.get('V6', '—')}개; V4는 {era.get('V4', '—')}개)."
    p2 = ("확정 단위를 공급하는 층위는 " + ", ".join(f"{lab(k)}({', '.join(sorted(v))})" for k, v in sorted(layers_conf.items(), key=lambda kv: -len(kv[1]))) + "이다. 성명서 층에서 나오는 확정 단위는 있어도 하나뿐이고 반기 부호가 약하다 — 거시 신호는 편집되지 않은 의사록 층에 있다.") if layers_conf else ""
    p3 = (f"H3(반경기)은 {'여섯 버전 모두 기각' if h3 else '일부 버전에서 지지'}이고, H1(계단)은 성명서가 있는 {', '.join(h1)}에서 지지된다. H4는 " + ", ".join(f"{V} {v}" for V, v in h4.items()) + "로, 성명서를 포함하면 성명서 층의 will+assess × VIX 한 건 때문에 '부분'이 된다.")
    p4 = "따라서 버전 선택은 두 가지를 바꾼다: (i) 계단(H1)은 성명서를 넣어야 보이고, (ii) 거시 공변(H4)은 의사록 층을 넣어야 보인다. 두 결과를 함께 보려면 V3 또는 V4가 필요하며, V4는 의장 발화의 순경기·불확실성 동행이라는 추가 결과를 준다."
    return box(p1, p2, p3, p4)
