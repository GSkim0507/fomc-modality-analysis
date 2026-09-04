"""
24_build_report_v3.py — Experiment-results report (Phase 15) from the programme outputs.

Narrative lives in paper/report_v3_program.md (Korean, single source).  Tables and figures are pulled from
results/program/<run>/ through include tags so that numbers are never retyped:

  {{tbl:C11_U2:corpus}}                      named views (see VIEWS) rendered as HTML tables
  {{tbl:C11_U2:regtable:min_committee:ALL}}  view with arguments (":"-separated)
  {{fig:C11_U2:L3_staircase_T1|caption}}     figure with caption (inlined as data URI)
  {{grid}}  {{hgrid}}  {{ledger_grid}}         cross-run grids over all runs

Outputs: results/report_v3/index.html (main), results/report_v3/run_<run>.html (appendix per run),
         results/report_v3/report_v3_artifact.html (single-file fragment for the Artifact host).
"""
from __future__ import annotations
import base64, html, json, re, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
PROG = ROOT / "results" / "program"; REP = ROOT / "results" / "report_v3"; REP.mkdir(parents=True, exist_ok=True)
PAPER = ROOT / "paper"
sys.path.insert(0, str(ROOT / "experiments"))
import importlib.util
_s = importlib.util.spec_from_file_location("pc", ROOT / "experiments" / "20_program_common.py"); pc = importlib.util.module_from_spec(_s); _s.loader.exec_module(pc)
SIX, LAYER_LABEL, CORPUS_DEFS, UNITS = pc.SIX, pc.LAYER_LABEL, pc.CORPUS_DEFS, pc.UNITS
md = MarkdownIt("commonmark").enable("table")

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600&family=Noto+Serif+KR:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">'
CSS = """
:root{--bg:#F2F4F6;--surface:#FFFFFF;--ink:#1A222C;--muted:#5A6572;--line:#D6DCE3;--accent:#24507A;--accent-ink:#FFFFFF;--warn:#A8501F;--ok:#2C6E5C;--tint:#E6EEF6;--hl:#FFF4DC;
--mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;--body:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;--display:"Noto Serif KR","Apple Myungjo",Georgia,serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#11161C;--surface:#181F27;--ink:#E5EAF0;--muted:#98A5B3;--line:#2C3640;--accent:#7FB0E0;--accent-ink:#0F1B27;--warn:#E0955F;--ok:#6FBFA8;--tint:#1E2B3A;--hl:#3A3120}}
:root[data-theme="dark"]{--bg:#11161C;--surface:#181F27;--ink:#E5EAF0;--muted:#98A5B3;--line:#2C3640;--accent:#7FB0E0;--accent-ink:#0F1B27;--warn:#E0955F;--ok:#6FBFA8;--tint:#1E2B3A;--hl:#3A3120}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:1200px;margin:0 auto;padding:36px 24px 96px}.layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:40px;align-items:start}
aside.toc{position:sticky;top:20px;max-height:calc(100vh - 40px);overflow:auto;font-size:13px;line-height:1.5}
aside.toc .lbl{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
aside.toc a{display:block;color:var(--ink);text-decoration:none;padding:3px 0 3px 10px;border-left:2px solid var(--line)}aside.toc a.l2{padding-left:20px;color:var(--muted);font-size:12.5px}
aside.toc a:hover{color:var(--accent);border-left-color:var(--accent)}main{min-width:0}
header.masthead{padding-bottom:22px;border-bottom:2px solid var(--ink);margin-bottom:26px}.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
header h1{font-family:var(--display);font-weight:700;font-size:clamp(26px,3.6vw,34px);line-height:1.25;margin:8px 0 6px;text-wrap:balance;border:none;padding:0}
header .sub{font-size:16px;color:var(--muted);margin:0 0 12px;max-width:72ch}.chips{display:flex;flex-wrap:wrap;gap:6px 14px;font-family:var(--mono);font-size:12px;color:var(--muted)}
h1{font-family:var(--display);font-weight:600;font-size:23px;line-height:1.3;margin:54px 0 14px;padding-top:18px;border-top:1px solid var(--line);text-wrap:balance;scroll-margin-top:16px}
h2{font-size:17px;font-weight:600;margin:32px 0 10px;scroll-margin-top:16px}h3{font-size:15px;font-weight:600;margin:22px 0 8px}
p{max-width:76ch;margin:0 0 14px}ul,ol{max-width:76ch;padding-left:22px;margin:0 0 14px}li{margin:5px 0}li>p{margin:0}
code{font-family:var(--mono);font-size:.88em;background:var(--tint);padding:1px 5px;border-radius:3px}pre{background:var(--tint);padding:12px 14px;border-radius:6px;overflow-x:auto;font-size:13px}pre code{background:none;padding:0}
hr{border:none;border-top:1px solid var(--line);margin:32px 0}blockquote{border-left:3px solid var(--accent);margin:14px 0;padding:8px 16px;background:var(--surface)}
.summary{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:22px 26px;margin:0 0 10px}.summary h1{border:none;padding:0;margin:0 0 12px;font-size:20px}.summary p,.summary ul,.summary ol{max-width:none}
div.reco{background:var(--accent);color:var(--accent-ink);padding:14px 18px;border-radius:6px;margin-top:6px}div.reco strong,div.reco em{color:inherit}
.tw{overflow-x:auto;margin:12px 0 20px;border:1px solid var(--line);border-radius:6px;background:var(--surface)}.tw .cap{font-size:12.5px;color:var(--muted);padding:8px 11px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.55}th,td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}th{font-weight:600;background:var(--tint);white-space:nowrap}
tr:last-child td{border-bottom:none}td.n,th.n{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}tr.hl td{background:var(--hl);color:var(--ink);font-weight:500}tr.hl td:first-child{border-left:4px solid var(--accent)}
.pill{display:inline-block;padding:0 7px;border-radius:9px;font-family:var(--mono);font-size:11px;background:var(--tint)}.pill.ok{background:var(--ok);color:#fff}.pill.warn{background:var(--warn);color:#fff}.pill.na{opacity:.6}
figure{margin:18px 0 26px}figure img{max-width:100%;border:1px solid var(--line);border-radius:4px;background:#fff;display:block}figcaption{font-size:12.5px;color:var(--muted);margin-top:6px;max-width:84ch}
.small{font-size:13px;color:var(--muted)}a{color:var(--accent)}details{margin:10px 0}summary{cursor:pointer;font-weight:600}
@media (max-width:900px){.layout{grid-template-columns:1fr}aside.toc{position:static;max-height:none;display:flex;flex-wrap:wrap;gap:4px 12px;border-bottom:1px solid var(--line);padding-bottom:12px}aside.toc a{border:none;padding:2px 0}aside.toc a.l2{display:none}aside.toc .lbl{width:100%}}
@media print{body{background:#fff;color:#000}.wrap{padding:0}.layout{display:block}aside.toc{display:none}.tw{overflow:visible;border:none}}
"""
NUM_RE = re.compile(r"^\s*[+\-−–]?\s*[\d.,]+%?\s*(\*{0,3})?\s*$|^\s*—\s*$|^\s*≥\s*\d+\s*$")


# ----------------------------------------------------------------------------------------------
def load_runs():
    runs = {}
    for d in sorted(PROG.glob("C*_U*")):
        f = d / "summary.json"
        if f.exists(): runs[d.name] = json.loads(f.read_text())
    return runs


def csv(run, name):
    p = PROG / run / "tables" / f"{name}.csv"
    if not p.exists() or p.stat().st_size == 0: return None
    try: return pd.read_csv(p)
    except pd.errors.EmptyDataError: return None


def tbl(df: pd.DataFrame, caption="", reco_pred=None, max_rows=60, fmt=None) -> str:
    if df is None or not len(df): return f"<p class='small'>(표 없음: {html.escape(caption)})</p>"
    df = df.head(max_rows)
    cols = list(df.columns)
    out = ["<div class='tw'>"]
    if caption: out.append(f"<div class='cap'>{caption}</div>")
    out.append("<table><thead><tr>" + "".join(f"<th{' class=n' if pd.api.types.is_numeric_dtype(df[c]) else ''}>{html.escape(str(c))}</th>" for c in cols) + "</tr></thead><tbody>")
    for _, r in df.iterrows():
        cls = " class='hl'" if (reco_pred and reco_pred(r)) else ""
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                s = "" if np.isnan(v) else (fmt.get(c, "{:.3f}").format(v) if fmt and c in fmt else (f"{v:,.0f}" if abs(v) >= 1000 and float(v).is_integer() else f"{v:.3f}".rstrip("0").rstrip(".") if abs(v) < 1000 else f"{v:,.1f}"))
                cells.append(f"<td class='n'>{s}</td>")
            elif isinstance(v, (int, np.integer)): cells.append(f"<td class='n'>{v:,}</td>")
            else:
                s = "" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v)
                cells.append(f"<td{' class=n' if NUM_RE.match(s) else ''}>{html.escape(s)}</td>" if not s.startswith("<") else f"<td>{s}</td>")
        out.append(f"<tr{cls}>" + "".join(cells) + "</tr>")
    out.append("</tbody></table></div>"); return "".join(out)


def img(run, name, caption="", inline=True):
    p = PROG / run / "figures" / f"{name}.png"
    if not p.exists(): return f"<p class='small'>(그림 없음: {run}/{name})</p>"
    src = ("data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()) if inline else f"../program/{run}/figures/{name}.png"
    return f"<figure><img src='{src}' alt='{html.escape(caption)}' loading='lazy'><figcaption>{caption}</figcaption></figure>"


def pill(v):
    cls = {"지지": "ok", "부분": "", "기각": "warn", "해당 없음": "na"}.get(v, "")
    return f"<span class='pill {cls}'>{html.escape(str(v))}</span>"


def lab(l): return LAYER_LABEL.get(l, l)


# ----------------------------------------------------------------------------------------------
# named table views
# ----------------------------------------------------------------------------------------------
def v_corpus(run):
    d = csv(run, "L1_corpus"); d = d[["label", "n_docs", "tokens", "sentences", "six_modal", "nine_modal", "pmw", "ci_lo", "ci_hi", "per1k"]]
    d = d.rename(columns={"label": "층위", "n_docs": "문서", "tokens": "토큰", "sentences": "문장", "six_modal": "6대 조동사", "nine_modal": "9개 조동사", "pmw": "pmw", "ci_lo": "CI 하한", "ci_hi": "CI 상한", "per1k": "per 1k"})
    return tbl(d, "L1 코퍼스 기술 (T1 2014–2026). pmw = 백만 단어당 빈도, 95% Poisson CI.", fmt={"pmw": "{:,.0f}", "CI 하한": "{:,.0f}", "CI 상한": "{:,.0f}", "per 1k": "{:.2f}"})


def v_modal_pmw(run, layer=None):
    d = csv(run, "L1_modal_pmw_dp")
    if d is None: return ""
    d = d[d.modal.isin(SIX)]
    if layer: d = d[d.layer == layer]
    p = d.pivot_table(index="layer", columns="modal", values="pmw").reindex(columns=SIX); p.index = [lab(i) for i in p.index]
    dp = d.pivot_table(index="layer", columns="modal", values="DP").reindex(columns=SIX); dp.index = [lab(i) for i in dp.index]
    a = tbl(p.reset_index().rename(columns={"index": "층위"}), "L1 조동사별 pmw (T1)", fmt={m: "{:,.0f}" for m in SIX})
    b = tbl(dp.reset_index().rename(columns={"index": "층위"}), "L1 문서 간 분산 DP (Gries 2008; 0 = 균등, 1 = 편중)", fmt={m: "{:.2f}" for m in SIX})
    return a + b


def v_keyness(run, layer):
    d = csv(run, "L2_keyness")
    if d is None: return "<p class='small'>(키니스: 층위 1개)</p>"
    d = d[d.layer == layer].sort_values("LL", ascending=False).head(15)[["item", "kind", "freq_in", "pmw_in", "pmw_out", "LL", "log_ratio", "pct_diff", "q", "sign"]]
    d = d.rename(columns={"item": "항목", "kind": "종류", "freq_in": "빈도(층위)", "pmw_in": "pmw(층위)", "pmw_out": "pmw(나머지)", "log_ratio": "log ratio", "pct_diff": "%DIFF", "sign": "방향"})
    return tbl(d, f"L2 키니스 — {lab(layer)} vs 나머지 층위 (log-likelihood, Hardie log ratio, %DIFF, BH q)", fmt={"pmw(층위)": "{:,.0f}", "pmw(나머지)": "{:,.0f}", "LL": "{:.1f}", "log ratio": "{:+.2f}", "%DIFF": "{:+.0f}", "q": "{:.3f}"})


def v_residuals(run):
    d = csv(run, "L2_std_residuals")
    if d is None: return ""
    d["layer"] = d.layer.map(lab); return tbl(d.rename(columns={"layer": "층위"}), "L2 층위 × 조동사 표준화 잔차 (|z| > 2 유의)", fmt={m: "{:+.1f}" for m in SIX})


def v_mk(run, layer=None):
    d = csv(run, "L3_mk_trends")
    if d is None: return ""
    d = d[d.metric == "per1k"]
    if layer: d = d[d.layer == layer]
    d = d[d.p < .05].sort_values(["layer", "p"])[["layer", "series", "n", "trend", "tau", "sen_slope", "p"]]; d["layer"] = d.layer.map(lab)
    return tbl(d.rename(columns={"layer": "층위", "series": "조동사", "trend": "추세", "sen_slope": "Sen 기울기(회의당 per 1k)"}), "L3 Mann–Kendall 추세 (per 1k, 회의 단위; p < .05만)", fmt={"tau": "{:+.3f}", "Sen 기울기(회의당 per 1k)": "{:+.4f}", "p": "{:.4f}"})


def v_changepoints(run):
    d = csv(run, "L3_changepoints_T1")
    if d is None: return ""
    d = d[["unit", "break_date", "share_before", "share_after", "direction", "nearest_event", "days_to_event", "responsible_sentence"]].rename(columns={"unit": "단위", "break_date": "변화점", "share_before": "전", "share_after": "후", "direction": "방향", "nearest_event": "최근접 사건", "days_to_event": "거리(일)", "responsible_sentence": "책임 문장"})
    return tbl(d, "L3 성명서 PELT 변화점(점유율 N2, min size 4, pen 2 ln n)과 책임 문장", max_rows=40, fmt={"전": "{:.2f}", "후": "{:.2f}"})


def v_profiles(run, layer):
    d = csv(run, "L4_predicate_profiles")
    if d is None: return ""
    d = d[d.layer == layer]
    rows = []
    for m in SIX:
        s = d[d.modal == m].head(6)
        if not len(s): continue
        rows.append({"조동사": f"{m} (n={int(s.modal_n.iloc[0]):,})", "상위 서술어 (점유율)": ", ".join(f"{r.predicate} {r.share:.0%}" for r in s.itertuples()), "상위 6 누적": f"{s.cum_share.iloc[-1]:.0%}"})
    return tbl(pd.DataFrame(rows), f"L4 서술어 프로파일 — {lab(layer)}")


def v_collo(run, layer):
    d = csv(run, "L4_collostruction")
    if d is None: return ""
    d = d[d.layer == layer]; rows = []
    for m in SIX:
        s = d[(d.modal == m) & (d.collostruction_strength > 0)].sort_values("collostruction_strength", ascending=False).head(5); r_ = d[(d.modal == m) & (d.collostruction_strength < 0)].sort_values("collostruction_strength").head(3)
        rows.append({"조동사": m, "유인 collexeme (obs/exp, −log10 p)": "; ".join(f"{x.predicate} ({x.ratio:.1f}×, {x.collostruction_strength:.1f})" for x in s.itertuples()), "배척 collexeme": "; ".join(f"{x.predicate} ({x.collostruction_strength:.1f})" for x in r_.itertuples())})
    return tbl(pd.DataFrame(rows), f"L4 distinctive collexeme 분석 — {lab(layer)} (Fisher exact; Gries & Stefanowitsch 2004)")


def v_jsd(run, layer):
    d = csv(run, "L4_jsd")
    if d is None: return ""
    d = d[d.layer == layer]
    if not len(d): return ""
    p = pd.DataFrame(index=SIX, columns=SIX, dtype=float)
    for r in d.itertuples(): p.loc[r.modal_a, r.modal_b] = r.jsd; p.loc[r.modal_b, r.modal_a] = r.jsd
    return tbl(p.reset_index().rename(columns={"index": ""}), f"L4 조동사 간 서술어 분포의 Jensen–Shannon 발산(base 2) — {lab(layer)}", fmt={m: "{:.2f}" for m in SIX})


def v_kwic(run, layer=None, n=12):
    d = csv(run, "L4_kwic")
    if d is None: return ""
    if layer: d = d[d.layer == layer]
    d = d.groupby("modal").head(2).head(n)[["modal", "predicate", "date", "kwic"]]
    return tbl(d.rename(columns={"modal": "조동사", "predicate": "서술어", "date": "날짜", "kwic": "KWIC"}), f"L4 용례 (KWIC) — {lab(d.layer.iloc[0]) if 'layer' in d and len(d) else ''}")


def v_retention(run):
    s = load_runs()[run].get("L5", {}); hl = s.get("half_life", {})
    if not hl: return ""
    rows = [{"지표": "보유율 반감기(회의)", **{k: (f"{v:.1f}" if v else "≥24") for k, v in hl.items()}}]
    a = tbl(pd.DataFrame(rows), "L5 구문 보유율 반감기: 회의 t의 구문 집합이 t+k에 남아 있는 비율이 0.5를 지나는 k")
    fy = csv(run, "L5_formulaic_share_year"); b = tbl(fy.rename(columns={"year": "연도", "tokens": "조동사 토큰", "formulaic": "정형 문장 내", "formulaic_share": "정형 비율"}), "L5 정형 문장(≥3개 성명서에 재출현) 안의 조동사 토큰 비율", fmt={"정형 비율": "{:.2f}"}) if fy is not None else ""
    ev = csv(run, "L5_edit_events"); c = tbl(ev.groupby("year")[["n_added", "n_removed"]].sum().reset_index().rename(columns={"year": "연도", "n_added": "삽입", "n_removed": "삭제"}), "L5 연도별 구문 삽입·삭제(연속 성명서 간)") if ev is not None else ""
    return a + b + c


def v_context(run, layer):
    d = csv(run, "L6_context_rates")
    if d is None: return ""
    d = d[d.layer == layer][["modal", "n", "neg", "passive", "perfect", "progressive", "cond", "reported", "question", "contracted"]]
    a = tbl(d.rename(columns={"modal": "조동사"}), f"L6 문법 맥락 비율 — {lab(layer)}", fmt={c: "{:.2f}" for c in ["neg", "passive", "perfect", "progressive", "cond", "reported", "question", "contracted"]})
    sj = csv(run, "L6_subject_types"); sj = sj[sj.layer == layer] if sj is not None else pd.DataFrame(columns=["modal", "subj_type", "share"]); p = sj.pivot_table(index="modal", columns="subj_type", values="share").reindex(SIX).fillna(0)
    b = tbl(p.reset_index().rename(columns={"modal": "조동사"}), f"L6 주어 유형 분포 — {lab(layer)}", fmt={c: "{:.2f}" for c in p.columns})
    se = csv(run, "L6_semantic_types"); se = se[se.layer == layer] if se is not None else pd.DataFrame(columns=["modal", "sem_type", "share"]); q = se.pivot_table(index="modal", columns="sem_type", values="share").reindex(SIX).fillna(0)
    c = tbl(q.reset_index().rename(columns={"modal": "조동사"}), f"L6 의미 유형(휴리스틱) 분포 — {lab(layer)}", fmt={c_: "{:.2f}" for c_ in q.columns})
    return a + b + c


def v_mnlogit(run):
    d = csv(run, "L7_mnlogit"); s = load_runs()[run].get("L7", {})
    if d is None: return f"<p class='small'>(L7 실패: {s.get('error')})</p>"
    d = d[d.variable != "const"]; d = d[d.p < .05].sort_values(["variable", "outcome_vs_will"])[["variable", "outcome_vs_will", "coef", "rrr", "p"]]
    return tbl(d.rename(columns={"variable": "변수", "outcome_vs_will": "결과(vs will)", "rrr": "상대위험비"}), f"L7 다항 로짓(기준 will; 유사 R² = {s.get('pseudo_r2')}, N = {s.get('n'):,}); p < .05만", max_rows=80, fmt={"coef": "{:+.2f}", "상대위험비": "{:.2f}", "p": "{:.4f}"})


def v_be_appropriate(run):
    d = csv(run, "L8_counts")
    if d is None: return ""
    d["layer"] = d.layer.map(lab); a = tbl(d.rename(columns={"layer": "층위"}), "L8 modal + be appropriate 토큰 수(T1)")
    k = csv(run, "L8_kwic"); b = tbl(k.assign(layer=k.layer.map(lab)).rename(columns={"layer": "층위", "modal": "조동사", "date": "날짜"}), "L8 용례", max_rows=18) if k is not None and len(k) else ""
    return a + b


def v_descriptives(run):
    d = csv(run, "E1_descriptives")
    if d is None: return ""
    a = tbl(d[d.block == "macro"].drop(columns=["block", "zero_share"]).rename(columns={"layer": "표본(층위)", "series": "변수"}), "E1 거시 변수 기술통계 (회의 표본, T1)")
    t = d[(d.block == "text") & (d.series == "ALL")].drop(columns=["block", "series"]); t["layer"] = t.layer.map(lab)
    b = tbl(t.rename(columns={"layer": "층위"}), "E1 텍스트 지표 기술통계: 층위별 6대 조동사 총밀도 (per 1k)")
    return a + b


def v_corr_all(run):
    d = csv(run, "E2_correlations")
    if d is None: return ""
    d = d[(d.series == "ALL") & d.period.isin(["T1", "T2", "T3"])]
    p = d.pivot_table(index=["level", "key"], columns=["macro", "period"], values="rho"); pv = d.pivot_table(index=["level", "key"], columns=["macro", "period"], values="p_rho")
    rows = []
    for idx in p.index:
        r = {"수준": idx[0], "키": lab(idx[1])}
        for mv in ("cfnai", "vix"):
            for T in ("T1", "T2", "T3"):
                v = p.loc[idx].get((mv, T), np.nan); q = pv.loc[idx].get((mv, T), np.nan)
                r[f"ρ {mv.upper()} {T}"] = "" if pd.isna(v) else f"{v:+.2f}{'***' if q < .01 else '**' if q < .05 else '*' if q < .10 else ''}"
        rows.append(r)
    return tbl(pd.DataFrame(rows), "E2 총 조동사 밀도 × CFNAI / VIX — Spearman ρ (T1 전체, T2 2020 제외, T3 2010–). *** p<.01 ** p<.05 * p<.10")


def v_regtable(run, layer, series="ALL"):
    d = csv(run, "E3_regressions")
    if d is None: return ""
    d = d[(d.layer == layer) & (d.series == series)]
    if not len(d): return f"<p class='small'>(회귀표 없음: {layer}/{series})</p>"
    specs = list(dict.fromkeys(d.spec)); vars_ = [v for v in dict.fromkeys(d["var"]) if v != "const"]
    rows = []
    for v in vars_:
        r = {"": d[d["var"] == v].label.iloc[0]}
        for sp in specs:
            x = d[(d.spec == sp) & (d["var"] == v)]
            r[sp] = (f"{x.coef.iloc[0]:+.3f}{x.stars.iloc[0] if isinstance(x.stars.iloc[0], str) else ''}<br><span class='small'>({x.se.iloc[0]:.3f})</span>") if len(x) else ""
        rows.append(r)
    for stat in ("n", "r2"):
        r = {"": {"n": "N", "r2": "R²"}[stat]}
        for sp in specs:
            x = d[d.spec == sp]; r[sp] = (f"{int(x.n.iloc[0])}" if stat == "n" else f"{x.r2.iloc[0]:.3f}") if len(x) else ""
        rows.append(r)
    return tbl(pd.DataFrame(rows), f"E3 회귀표 — 종속: {lab(layer)} {series} 밀도(per 1k). 계수(HAC Newey–West SE, 4 lag). *** p<.01 ** p<.05 * p<.10. (1) CFNAI (2) VIX (3) 둘 다 (4) +실업률갭·근원PCE갭 (5) +2020-09 이후 더미 (6) 2020 제외 (7) 1차 차분 (8) 1차 차분·2020 제외")


def v_regtable_units(run, layer, spec="(3)"):
    d = csv(run, "E4_construction_regressions")
    if d is None: return "<p class='small'>(단위 = 조동사; E3 참조)</p>"
    d = d[(d.layer == layer)]
    if not len(d): return ""
    units = list(dict.fromkeys(d.unit)); rows = []
    for u in units:
        r = {"구문": u, "토큰": int(d[d.unit == u].n_tokens.iloc[0]), "제로 회의": f"{d[d.unit == u].zero_share.iloc[0]:.2f}"}
        for sp in ("(3)", "(6) excl-2020", "(7) Δ", "(8) Δ excl-2020"):
            for v in (["cfnai_ma3_lag2", "vix_pre28"] if not sp.startswith(("(7)", "(8)")) else ["d_cfnai", "d_vix"]):
                x = d[(d.unit == u) & (d.spec == sp) & (d["var"] == v)]
                r[f"{sp} {('CFNAI' if 'cfnai' in v else 'VIX')}"] = (f"{x.coef.iloc[0]:+.3f}{x.stars.iloc[0] if isinstance(x.stars.iloc[0], str) else ''}") if len(x) else ""
        rows.append(r)
    return tbl(pd.DataFrame(rows), f"E4 구문 회귀 — {lab(layer)}: 종속 = 구문 밀도(per 1k), HAC. (3) CFNAI+VIX (6) 2020 제외 (7) 1차 차분 (8) 차분·2020 제외", max_rows=40)


def v_ledger(run, category="confirmed", n=25):
    n = int(n); d = csv(run, "E5_ledger")
    if d is None or not len(d): return "<p class='small'>(ledger 없음)</p>"
    d = d[(d.level == "layer") & (d.category == category)].assign(a=lambda x: x.rho_T2.abs()).sort_values("a", ascending=False).drop(columns="a").head(n)
    d = d[["key", "unit", "macro", "rho_T1", "rho_T2", "rho_T3", "rho_H1", "rho_H2", "n_tokens_T1", "zero_share_T1"]]; d["key"] = d.key.map(lab)
    ttl = {"confirmed": "확정(T1·T2 유의·동부호 + 반기 동부호)", "era_composition": "시대 구성(T1·T2 유의, 반기 부호 불일치)", "T1_only": "2020 의존(T1만 유의)"}[category]
    return tbl(d.rename(columns={"key": "층위", "unit": "단위", "macro": "거시", "rho_T1": "ρ T1", "rho_T2": "ρ 2020 제외", "rho_T3": "ρ 2010–", "rho_H1": "ρ 14–19", "rho_H2": "ρ 21–26", "n_tokens_T1": "토큰", "zero_share_T1": "제로 회의"}), f"E5 ledger — {ttl}", fmt={"ρ T1": "{:+.2f}", "ρ 2020 제외": "{:+.2f}", "ρ 2010–": "{:+.2f}", "ρ 14–19": "{:+.2f}", "ρ 21–26": "{:+.2f}", "제로 회의": "{:.2f}"})


def v_granger(run):
    d = csv(run, "E6_granger")
    if d is None: return ""
    d = d[(d.period == "T2") & (d.lag == 2)].sort_values("q_text_to_macro").head(12)[["key", "unit", "macro", "p_text_to_macro", "q_text_to_macro", "p_macro_to_text", "n"]]
    a = tbl(d.rename(columns={"key": "장르", "unit": "계열", "macro": "거시", "p_text_to_macro": "p text→macro", "q_text_to_macro": "q (BH)", "p_macro_to_text": "p macro→text"}), "E6 Granger 인과(lag 2, 2020 제외; text→macro q 오름차순 상위 12)", fmt={"p text→macro": "{:.3f}", "q (BH)": "{:.3f}", "p macro→text": "{:.3f}"})
    p = csv(run, "E6_predictive")
    b = tbl(p.sort_values("q_text").head(10)[["key", "unit", "target", "r2_base", "r2_with", "delta_r2", "coef_text", "p_text", "q_text"]].rename(columns={"key": "장르", "unit": "계열", "target": "목표", "r2_base": "R² 기준", "r2_with": "R² +텍스트", "delta_r2": "ΔR²", "coef_text": "텍스트 계수", "p_text": "p", "q_text": "q"}), "E6 예측 회귀: CFNAI(m+3) 또는 ΔVIX(후 28일) ~ 거시 + 텍스트; 증분 R²와 텍스트 계수(HAC)", fmt={"R² 기준": "{:.3f}", "R² +텍스트": "{:.3f}", "ΔR²": "{:+.3f}", "p": "{:.3f}", "q": "{:.3f}"}) if p is not None else ""
    return a + b


def v_event_text(run):
    d = csv(run, "E7_event_text")
    if d is None or not len(d): return ""
    d = d[d.series == "ALL"][["event", "event_date", "pre3", "at", "post3"]]
    return tbl(d.rename(columns={"event": "사건", "event_date": "날짜", "pre3": "직전 3회의 평균", "at": "사건 회의", "post3": "직후 3회의 평균"}), f"E7 사건 창: {lab(load_runs()[run]['E7']['layer'])} 총밀도(per 1k)", fmt={"직전 3회의 평균": "{:.2f}", "사건 회의": "{:.2f}", "직후 3회의 평균": "{:.2f}"})


def v_robustness(run, layer=None):
    d = csv(run, "E8_robustness")
    if d is None: return ""
    d = d[d.series == "ALL"]
    if layer: d = d[d.layer == layer]
    d["layer"] = d.layer.map(lab); rows = []
    for (l_, v), s in d.groupby(["layer", "variant"], sort=False):
        r = s.iloc[0]; rows.append({"층위": l_, "변형": v, "ρ CFNAI": ("" if pd.isna(r.rho_cfnai) else f"{r.rho_cfnai:+.2f}{'*' if r.p_cfnai < .05 else ''}"), "ρ VIX": ("" if pd.isna(r.rho_vix) else f"{r.rho_vix:+.2f}{'*' if r.p_vix < .05 else ''}")})
    return tbl(pd.DataFrame(rows), "E8 강건성 — 총밀도의 Spearman ρ, 변형별 (* p < .05)", max_rows=80)


def v_kawamura(run):
    d = csv(run, "E9_kawamura")
    if d is None: return ""
    d = d[d.level == "genre"]
    rows = []
    for (key, ser), s in d.groupby(["key", "series"]):
        r = {"장르": key, "계열": {"ALL": "총밀도", "hedge": "헤징군(would/could/may/might)", "commit": "약속군(will)"}[ser]}
        for sp in ("levels: CFNAI", "levels: CFNAI + VIX", "levels excl-2020: CFNAI + VIX", "Δ: ΔCFNAI + ΔVIX", "Δ excl-2020"):
            x = s[s.spec == sp]
            for v in ("CFNAI-MA3", "VIX", "ΔCFNAI", "ΔVIX"):
                y = x[x["var"] == v]
                if len(y): r[f"{sp} · {v}"] = f"{y.coef.iloc[0]:+.3f}{y.stars.iloc[0] if isinstance(y.stars.iloc[0], str) else ''} (t={y.t.iloc[0]:.1f})"
        rows.append(r)
    return tbl(pd.DataFrame(rows), "E9 Kawamura et al.(2019) 방식 재현: 조동사 밀도 ~ 경기지수(+VIX), 수준과 1차 차분 (HAC t)", max_rows=40)


def v_hypotheses(run):
    H = load_runs()[run].get("H", {}); rows = [{"가설": k, "판정": pill(v["verdict"]), "근거": v["evidence"]} for k, v in H.items()]
    return tbl(pd.DataFrame(rows), f"가설 판정 — {run}")


def v_contrasts(run):
    d = csv(run, "L9_contrasts")
    if d is None or not len(d): return ""
    d["layer"] = d.layer.map(lab); cols = ["layer", "contrast", "group", "n"] + SIX + ["chi2", "p", "cramers_v"]
    return tbl(d[cols].rename(columns={"layer": "층위", "contrast": "대조", "group": "집단"}), "L9 의장·정책 국면 대조: 6대 조동사 점유율", fmt={**{m: "{:.2f}" for m in SIX}, "chi2": "{:.1f}", "p": "{:.4f}", "cramers_v": "{:.3f}"})


VIEWS = {"corpus": v_corpus, "modal_pmw": v_modal_pmw, "keyness": v_keyness, "residuals": v_residuals, "mk": v_mk, "changepoints": v_changepoints, "profiles": v_profiles, "collo": v_collo,
         "jsd": v_jsd, "kwic": v_kwic, "retention": v_retention, "context": v_context, "mnlogit": v_mnlogit, "be_appropriate": v_be_appropriate, "descriptives": v_descriptives, "corr_all": v_corr_all,
         "regtable": v_regtable, "regtable_units": v_regtable_units, "ledger": v_ledger, "granger": v_granger, "event_text": v_event_text, "robustness": v_robustness, "kawamura": v_kawamura,
         "hypotheses": v_hypotheses, "contrasts": v_contrasts}


# ----------------------------------------------------------------------------------------------
# cross-run grids
# ----------------------------------------------------------------------------------------------
def grid(runs, inline=True):
    rows = []
    for name, s in runs.items():
        cd = CORPUS_DEFS[s["cid"]]; e5 = s.get("E5", {}).get("counts", {}); st = s.get("L3", {}).get("staircase_T1"); hl = s.get("L5", {}).get("half_life", {}).get("all")
        e2 = {(r["key"], r["macro"]): r for r in s.get("E2", {}).get("genre_all", []) if r["period"] == "T2"}
        def rp(k, mv):
            r = e2.get((k, mv)); return "" if not r or r["rho"] is None else f"{r['rho']:+.2f}{'*' if (r['p'] or 1) < .05 else ''}"
        H = s.get("H", {})
        rows.append({"run": name, "별칭": cd["alias"], "성명서": "✓" if cd["statement"] else "", "의사록": {"0": "", "C": "위원회", "S": "실질", "A": "전부(미정제)"}[cd["minutes"]], "기자회견": {"0": "", "C": "의장", "A": "전부(미정제)"}[cd["press_conf"]], "연설": "✓" if cd["speech"] else "",
                     "단위": s["U"], "변화점(사건)": (f"{st['n_cp']} ({st['n_cp_event']})" if st else "—"), "반감기": (f"{hl:.1f}" if hl else ("≥24" if s.get("L5", {}).get("half_life") else "—")),
                     "V": (f"{s['L2']['cramers_v']:.3f}" if s.get("L2", {}).get("cramers_v") else "—"),
                     "확정 VIX": e5.get("vix", {}).get("confirmed", ""), "확정 CFNAI": e5.get("cfnai", {}).get("confirmed", ""), "시대구성": (e5.get("vix", {}).get("era_composition", 0) + e5.get("cfnai", {}).get("era_composition", 0)) if e5 else "",
                     "ρ stmt×CFNAI": rp("statement", "cfnai"), "ρ min×CFNAI": rp("minutes", "cfnai"), "ρ pc×CFNAI": rp("press_conf", "cfnai"), "ρ stmt×VIX": rp("statement", "vix"), "ρ min×VIX": rp("minutes", "vix"), "ρ pc×VIX": rp("press_conf", "vix"),
                     "H1": pill(H.get("H1", {}).get("verdict", "—")), "H2": pill(H.get("H2", {}).get("verdict", "—")), "H3": pill(H.get("H3", {}).get("verdict", "—")), "H4": pill(H.get("H4", {}).get("verdict", "—")), "H5": pill(H.get("H5", {}).get("verdict", "—")),
                     "상세": (f"<a href='run_{name}.html'>열기</a>" if not inline else "")})
    df = pd.DataFrame(rows)
    return tbl(df, "전 조합 격자: 24개 코퍼스 정의 × 3 단위. 변화점(사건) = 성명서 PELT 변화점 수(정책 사건 ±1회의 이내 수); 반감기 = 구문 보유율 반감기(회의); V = 층위×조동사 Cramér's V; 확정 = E5 ledger 확정 단위 수(층위 수준); ρ = 장르 총밀도 Spearman(2020 제외, * p<.05)",
               reco_pred=lambda r: (r["별칭"] == "S4" and r["단위"] == "U2"), max_rows=100)


def hgrid(runs):
    rows = []
    for name, s in runs.items():
        cd = CORPUS_DEFS[s["cid"]]; H = s.get("H", {})
        rows.append({"run": name, "별칭": cd["alias"], "코퍼스": cd["name"], "단위": s["U"], **{k: pill(v["verdict"]) for k, v in H.items()}})
    df = pd.DataFrame(rows)
    counts = {k: df[k].str.extract(r">([^<]+)<")[0].value_counts().to_dict() for k in ("H1", "H2", "H3", "H4", "H5") if k in df}
    summ = tbl(pd.DataFrame([{"가설": k, **{v: c.get(v, 0) for v in ("지지", "부분", "기각", "해당 없음")}} for k, c in counts.items()]), "가설별 판정 분포 (72 run)")
    return summ + tbl(df, "run별 가설 판정", max_rows=100, reco_pred=lambda r: (r["별칭"] == "S4" and r["단위"] == "U2"))


# ----------------------------------------------------------------------------------------------
def render_narrative(text: str, runs: dict, inline=True) -> str:
    def rep_tbl(m):
        parts = m.group(1).split(":"); run = parts[0]; view = parts[1]; args = parts[2:]
        if run not in runs: return f"<p class='small'>(run 없음: {run})</p>"
        try: return VIEWS[view](run, *args)
        except Exception as e: return f"<p class='small'>(표 오류 {run}:{view}: {html.escape(str(e))})</p>"
    def rep_fig(m):
        spec, _, cap = m.group(1).partition("|"); run, _, name = spec.partition(":"); return img(run, name, cap, inline)
    text = re.sub(r"\{\{tbl:([^}]+)\}\}", rep_tbl, text)
    text = re.sub(r"\{\{fig:([^}]+)\}\}", rep_fig, text)
    text = text.replace("{{grid}}", grid(runs, inline)).replace("{{hgrid}}", hgrid(runs))
    return text


def parse_front_matter(text):
    meta = {}; m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line: k, v = line.split(":", 1); meta[k.strip()] = v.strip().strip('"')
        text = text[m.end():]
    return meta, text


def slug(text, used):
    s = re.sub(r"[^\w가-힣]+", "-", text.strip().lower()).strip("-")[:60] or "s"; base, i = s, 2
    while s in used: s = f"{base}-{i}"; i += 1
    used.add(s); return s


def html_from_md(md_text: str):
    body = md.render(md_text).replace("�", "&#xFFFD;")
    used, toc = set(), []
    def head(mm):
        level, inner = mm.group(1), mm.group(2); text = re.sub(r"<[^>]+>", "", inner); sid = slug(text, used)
        if level in ("1", "2"): toc.append((level, sid, text))
        return f"<h{level} id='{sid}'>{inner}</h{level}>"
    body = re.sub(r"<h([1-3])>(.*?)</h\1>", head, body, flags=re.S)
    # tables written in markdown -> wrap
    body = re.sub(r"<table>.*?</table>", lambda mm: "<div class='tw'>" + mm.group(0) + "</div>", body, flags=re.S)
    first_h1 = body.find("<h1 "); first_hr = body.find("<hr", first_h1)
    if 0 <= first_h1 < first_hr:
        block = body[first_h1:first_hr]; block = re.sub(r"<p><strong>추천\.</strong>(.*?)</p>", r"<div class='reco'><strong>추천.</strong>\1</div>", block, flags=re.S)
        body = body[:first_h1] + f"<section class='summary'>{block}</section>" + body[first_hr:]
    return body, toc


def page(meta, body, toc, commit, standalone=True, title="FOMC 조동사 실험 결과보고서"):
    nav = "<aside class='toc'><div class='lbl'>목차</div>" + "".join(f"<a class='l{l}' href='#{sid}'>{html.escape(t)}</a>" for l, sid, t in toc) + "</aside>"
    masthead = (f"<header class='masthead'><div class='eyebrow'>FOMC modal constructions · experiment results report · {html.escape(meta.get('date', ''))}</div>"
                f"<h1>{html.escape(meta.get('title', title))}</h1><p class='sub'>{html.escape(meta.get('subtitle', ''))}</p>"
                f"<div class='chips'><span>코퍼스 v3 · 층위 18종</span><span>코퍼스 정의 24 × 단위 3 = 72 run</span><span>실험군 L1–L9 · E1–E9</span><span>local git @ {commit}</span></div></header>")
    content = f"<div class='wrap'><div class='layout'>{nav}<main>{masthead}{body}</main></div></div>"
    if standalone:
        return f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title>{FONTS}<style>{CSS}</style></head><body>{content}</body></html>"
    return f"<title>{html.escape(title)}</title>\n{FONTS}\n<style>{CSS}</style>\n{content}"


def run_page(name, s):
    cd = CORPUS_DEFS[s["cid"]]; L_ = [f"<div class='eyebrow'>appendix · run {name}</div><h1 style='border:none;padding:0;margin:6px 0 4px'>{s['cid']} {cd['alias']} — {html.escape(cd['name'])} × {html.escape(s['unit'])}</h1>",
                                     f"<p class='small'>층위: {', '.join(lab(l) for l in s['layers'])} · 실행 {s.get('runtime_s')}s · 오류 {len(s.get('errors', {}))}</p>", v_hypotheses(name)]
    ml = pc.main_layer(s["layers"])
    secs = [("L1 코퍼스", v_corpus(name) + v_modal_pmw(name)), ("L2 키니스·층위 분업", (v_residuals(name) + "".join(v_keyness(name, l) for l in s["layers"][:4])) if len(s["layers"]) > 1 else "<p class='small'>층위 1개</p>"),
            ("L3 통시", img(name, "L3_yearly_main", "연도별 pmw(주 층위)") + (img(name, "L3_staircase_T1", "성명서 계단") + v_changepoints(name) if "statement" in s["layers"] else "") + v_mk(name)),
            ("L4 연어·구문", v_profiles(name, ml) + v_collo(name, ml) + v_jsd(name, ml) + img(name, "L4_verb_class_main", "서술어 의미 부류") + v_kwic(name, ml)),
            ("L5 정형성", (img(name, "L5_retention_edits", "보유율·편집") + v_retention(name)) if "statement" in s["layers"] else ""), ("L6 문법 맥락", img(name, "L6_context_main", "문법 맥락") + v_context(name, ml)),
            ("L7 다항로짓", v_mnlogit(name)), ("L8 be appropriate", v_be_appropriate(name)), ("L9 대조", v_contrasts(name)),
            ("E1 기술통계", v_descriptives(name)), ("E2 상관", img(name, "E2_heatmap", "조동사 밀도 × 거시") + v_corr_all(name)), ("E3 회귀표", "".join(v_regtable(name, l) for l in s["layers"])),
            ("E4 구문 회귀", "".join(v_regtable_units(name, l) for l in s["layers"][:5])), ("E5 ledger", v_ledger(name, "confirmed") + v_ledger(name, "era_composition", 12) + v_ledger(name, "T1_only", 12)),
            ("E6 선행성", v_granger(name)), ("E7 사건 연구", img(name, "E7_event_macro", "사건 주변 거시") + v_event_text(name)), ("E8 강건성", v_robustness(name)), ("E9 Kawamura", v_kawamura(name))]
    for t, b in secs: L_.append(f"<details><summary>{t}</summary>{b}</details>")
    if s.get("errors"): L_.append("<h2>오류</h2><ul>" + "".join(f"<li><code>{k}</code>: {html.escape(v)}</li>" for k, v in s["errors"].items()) + "</ul>")
    return "\n".join(L_)


def main():
    runs = load_runs(); commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    src = PAPER / "report_v3_program.md"
    meta, text = parse_front_matter(src.read_text(encoding="utf-8")) if src.exists() else ({"title": "실험 결과보고서 (본문 미작성)"}, "# 본문 없음\n\n{{grid}}\n\n{{hgrid}}")
    body_md = render_narrative(text, runs, inline=True); body, toc = html_from_md(body_md)
    (REP / "index.html").write_text(page(meta, body, toc, commit, True), encoding="utf-8")
    (REP / "report_v3_artifact.html").write_text(page(meta, body, toc, commit, False), encoding="utf-8")
    for name, s in runs.items():
        (REP / f"run_{name}.html").write_text(page({"title": f"run {name}", "date": ""}, run_page(name, s), [], commit, True, title=f"run {name}"), encoding="utf-8")
    print(f"report: {len(runs)} runs -> {REP}; index {((REP / 'index.html').stat().st_size) // 1024} KB")


if __name__ == "__main__":
    main()
