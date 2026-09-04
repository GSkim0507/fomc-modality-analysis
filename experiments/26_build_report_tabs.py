"""
26_build_report_tabs.py — Paper-grade, tabbed experiment-results report (Phase 15.5).

Layout
  탭 0 개요      narrative (summary, hypotheses, data, design, 72-run comparison, discussion, limitations)
  탭 비교        side-by-side tables across the versions (per unit)
  탭 V1..V6      one corpus version each; unit sub-tabs U1/U2/U3; inside: hierarchical numbered sections
                 1 데이터 → 2 언어학적 결과 (2.1–2.9) → 3 계량경제 결과 (3.1–3.8) → 4 가설 판정,
                 tables "표 n." and figures "그림 n." with paper-style notes.
Versions (docs/12 aliases): V1 성명서만(S1) · V2 성명서+의사록 위원회 층(S2) · V3 성명서+의사록 실질 층(S3)
                            · V4 4장르 정제(S4, 권장) · V5 의사록만(S5) · V6 미정제 v2 방식(S6)
Outputs: results/report_v3/report_tabs.html (standalone; figures inlined), results/report_v3/report_tabs_artifact.html (fragment).
"""
from __future__ import annotations
import html, json, re, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("r24", ROOT / "experiments" / "24_build_report_v3.py"); r24 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r24)
pc, SIX, lab, tbl, csv, pill = r24.pc, r24.SIX, r24.lab, r24.tbl, r24.csv, r24.pill
_i = importlib.util.spec_from_file_location("interp", ROOT / "experiments" / "27_interpret.py"); interp = importlib.util.module_from_spec(_i); _i.loader.exec_module(interp)
REP = r24.REP; PAPER = r24.PAPER

VERSIONS = [("V1", "C02", "성명서만", "S1"), ("V2", "C06", "성명서 + 의사록(위원회 층)", "S2"), ("V3", "C10", "성명서 + 의사록(실질 층 전부)", "S3"),
            ("V4", "C11", "4장르 정제(권장): 성명서 + 의사록 실질 층 + 의장 기자회견 + 연설", "S4"), ("V5", "C21", "의사록만(실질 층)", "S5"), ("V6", "C24", "미정제 4장르(v2 방식)", "S6")]
UNITS = [("U2", "구문 (modal + predicate)"), ("U1", "조동사"), ("U3", "조동사 + 동사 부류")]
VERSION_INFO = {
    "V1": dict(why="세미나의 출발 관찰(should 소멸, will 감소, would/could 등장)이 나온 장르. 가장 강하게 편집되는 정형문이며, 의사록 없이 연구질문에 답할 수 있는지를 재는 기준선(baseline).",
               how="회의 후 성명서 101건(비회의 성명서 4건 제외), 표결 문단 제외. 층위 1개이므로 층위 분업(L2·L7)은 해당 없음."),
    "V2": dict(why="의사록 포함의 최소 형태. 위원회 정책조치 섹션의 결정 서술만 더한다 — 같은 회의·같은 위원회의 텍스트이면서 성명서 문장의 인용은 제외했으므로 성명서와 이중 집계되지 않는 '성명서의 확장판'.",
               how="성명서 + 의사록 위원회 층(인용 성명서·지침·삽입 문서·표결 제외). 층위 2개."),
    "V3": dict(why="의사록의 모든 실질 발화(스태프 리뷰·데스크 보고·참가자 견해·위원회 결정·특별 주제)를 귀속 라벨과 함께 포함. 사실 서술→심의→결정의 담화 기능 차이를 검정할 수 있는 최소 구성.",
               how="성명서 + 의사록 실질 층 5개(규정문·명단·인용문·표결 제외). 층위 6개."),
    "V4": dict(why="연준의 공식 발화 전체. 기자·진행자 발화를 제거한 의장 기자회견과 의장 연설을 더해, 편집된 문서(성명서)–기록(의사록)–즉흥 발화(기자회견)–준비된 발화(연설)를 한 틀에서 비교한다. 권장안.",
               how="성명서 + 의사록 실질 층 5개 + 의장 기자회견 발화 + 의장 연설(제목·참고문헌·각주 제거). 층위 8개."),
    "V5": dict(why="진단용 대조군. 성명서를 빼면 무엇이 남는지 — 거시 연계 신호가 의사록 층에 있다는 주장의 직접 검정. 계단(H1)은 성명서 고유이므로 해당 없음.",
               how="의사록 실질 층 5개만. 층위 5개."),
    "V6": dict(why="v2 방식의 재현(대조군). 기자·진행자 발화, 1월 규정문, 인용 성명서, 표결 문단을 제거하지 않은 코퍼스로, 정제가 결과를 어떻게 바꾸는지 보여 준다.",
               how="4장르 전 층위(제외 층 포함). 층위 17개."),
}


def version_result_line(s):
    if not s: return "run 없음"
    H = s.get("H", {}); c = s.get("E5", {}).get("counts", {}); L3 = s.get("L3", {}).get("staircase_T1"); L2 = s.get("L2", {})
    parts = []
    if L3: parts.append(f"계단 변화점 {L3['n_cp']}개(사건 일치 {L3['n_cp_event']})")
    if L2.get("cramers_v"): parts.append(f"층위 × 조동사 V = {L2['cramers_v']:.3f}")
    if c: parts.append(f"확정 VIX {c['vix']['confirmed']} / CFNAI {c['cfnai']['confirmed']}, 시대 구성 {c['vix']['era_composition'] + c['cfnai']['era_composition']}, 2020 의존 {c['vix']['T1_only'] + c['cfnai']['T1_only']}")
    top = s.get("E5", {}).get("confirmed_top", [])[:3]
    if top: parts.append("상위 확정: " + ", ".join(f"{lab(x['key'])} {x['unit']}×{x['macro'].upper()} ρ={x['rho_T2']:+.2f}" for x in top))
    return "; ".join(parts) + ". 가설: " + " ".join(f"{k} {pill(v['verdict'])}" for k, v in H.items())


def versions_overview(runs, U="U2"):
    rows = []
    for V, cid, vname, alias in VERSIONS:
        s = runs.get(f"{cid}_{U}"); info = VERSION_INFO[V]
        rows.append({"버전": f"<b>{V}</b> {alias}", "구성": vname, "선택 기준(왜 이 버전인가)": info["why"], "진행(무엇으로 어떻게)": info["how"] + f" 단위 {pc.UNITS[U]} 기준으로 L1–L9·E1–E9 전 블록 실행.", "결과(핵심)": version_result_line(s)})
    return ("<h1 style='border:none;padding:0;margin:0 0 6px' id='versions-overview'>버전 개요: 여섯 탭이 무엇이고, 왜 있으며, 무엇이 나왔나</h1>"
            "<p class='small'>여섯 버전은 '의사록을 넣을 것인가, 어떤 층까지 넣을 것인가, 기자회견·연설을 넣을 것인가, 정제할 것인가'라는 재량 선택을 단계적으로 바꾼 것이다(§3.1 다중우주 설계). 아래 결과 열은 구문 단위(U2) 기준이며, 각 버전 탭에서 조동사·동사 부류 단위로 바꿔 볼 수 있다.</p>"
            + tbl(pd.DataFrame(rows), "표 0. 버전별 선택 기준·진행·결과 요약 (단위 U2 기준)", reco_pred=lambda r: r["버전"].startswith("<b>V4"), max_rows=10))


def version_intro(V, s):
    info = VERSION_INFO[V]
    return (f"<div class='keys' style='border-left-color:var(--muted)'><b>이 버전</b><ul><li><b>선택 기준</b>: {info['why']}</li><li><b>진행</b>: {info['how']}</li>"
            f"<li><b>결과</b>: {version_result_line(s)}</li></ul></div>")
NOTE_REG = "주: 회의 단위 OLS, 괄호 안은 Newey–West HAC(4 lag) 표준오차. *** p<.01, ** p<.05, * p<.10. (1) CFNAI-MA3(m−2) (2) VIX(회의 전 28일) (3) 둘 다 (4) + 실업률 갭·근원 PCE 갭 (5) + 2020-09 이후 더미 (6) 2020년 제외 (7) 1차 차분 (8) 1차 차분·2020년 제외."
NOTE_LEDGER = "주: 확정 = Spearman ρ가 T1(2014–26)과 T2(2020 제외)에서 모두 p<.05·동부호이고 반기(2014–19, 2021–26) 부호도 같으며 토큰 ≥ 40·제로 회의 ≤ 60%. 시대 구성 = T1·T2 유의하나 반기 부호 불일치. 2020 의존 = T1에서만 유의."
NOTE_KEY = "주: LL = log-likelihood(Rayson & Garside 2000); log ratio = 상대빈도비의 이진 로그(Hardie 2014, +0.5 평활); %DIFF = Gabrielatos & Marchi(2011); q = BH 보정 p."
NOTE_COLLO = "주: distinctive collexeme 분석(Gries & Stefanowitsch 2004). obs/exp = 관측/기대 비; 강도 = 부호 있는 −log₁₀ p(Fisher exact)."
NOTE_PMW = "주: pmw = 백만 단어당 빈도; CI = Poisson 95% 신뢰구간; DP = Gries(2008)의 문서 간 분산(0 균등 – 1 편중)."
EXTRA_CSS = """
.tabs{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:2px solid var(--ink);display:flex;flex-wrap:wrap;gap:4px;padding:10px 0 8px;margin-bottom:18px}
.tabs button{font:inherit;font-size:13.5px;padding:6px 12px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:6px;cursor:pointer}
.tabs button.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.tabs button.v4{font-weight:600}
.subtabs{display:flex;gap:4px;margin:6px 0 16px;flex-wrap:wrap}.subtabs button{font:inherit;font-size:12.5px;padding:4px 10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:14px;cursor:pointer}
.subtabs button.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.panel{display:none}.panel.on{display:block}
.vhead{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:baseline;margin:0 0 6px}.vhead h1{border:none;padding:0;margin:0;font-size:24px}.vhead .small{font-family:var(--mono)}
.keys{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:6px;padding:12px 18px;margin:12px 0 22px}.keys ul{margin:0;max-width:none}.keys li{margin:3px 0}
.ptoc{font-size:13px;columns:2;column-gap:28px;margin:8px 0 18px;padding:10px 14px;background:var(--surface);border:1px solid var(--line);border-radius:6px}.ptoc a{display:block;color:var(--ink);text-decoration:none;padding:1px 0}.ptoc a.l2{padding-left:14px;color:var(--muted)}
.note{font-size:12.5px;color:var(--muted);margin:-14px 0 20px;max-width:90ch}
.interp{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--ok);border-radius:6px;padding:10px 16px;margin:8px 0 16px;max-width:96ch}.interp p{margin:6px 0;max-width:none}.interp p:first-child::before{content:'해석 · ';font-family:var(--mono);font-size:11.5px;color:var(--ok);letter-spacing:.06em}
.tw .cap b,figcaption b{color:var(--ink)}
.cmp td:first-child{white-space:nowrap}
.wrap{max-width:1240px}.layout{grid-template-columns:1fr}aside.toc{display:none}
"""
JS = """
<script>
(function(){
  function q(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
  function show(v,u){
    q('.tabs button').forEach(function(b){b.classList.toggle('on',b.dataset.v===v);});
    q('.panel[data-v]').forEach(function(p){p.classList.toggle('on',p.dataset.v===v);});
    var pv=document.querySelector('.panel[data-v="'+v+'"]');
    if(pv){ var subs=q('.subtabs button',pv); if(subs.length){ var uu=u||(subs.filter(function(b){return b.classList.contains('on')})[0]||subs[0]).dataset.u;
      subs.forEach(function(b){b.classList.toggle('on',b.dataset.u===uu);}); q('.upanel',pv).forEach(function(p){p.classList.toggle('on',p.dataset.u===uu);}); u=uu; } }
    try{ history.replaceState(null,'','#v='+v+(u?('&u='+u):'')); }catch(e){}
    window.scrollTo(0,0);
  }
  q('.tabs button').forEach(function(b){b.addEventListener('click',function(){show(b.dataset.v);});});
  q('.subtabs button').forEach(function(b){b.addEventListener('click',function(){show(b.closest('.panel').dataset.v,b.dataset.u);});});
  var m=/v=([^&]+)(?:&u=([^&]+))?/.exec(location.hash||''); show(m?m[1]:'V0', m?m[2]:null);
})();
</script>
"""


def number(htmls: str) -> str:
    """Number tables (표 n.) and figures (그림 n.) sequentially within a panel."""
    t = [0]; f = [0]
    def rt(m): t[0] += 1; return f"<div class='cap'><b>표 {t[0]}.</b> "
    def rf(m): f[0] += 1; return f"<figcaption><b>그림 {f[0]}.</b> "
    htmls = re.sub(r"<div class='cap'>", rt, htmls); htmls = re.sub(r"<figcaption>", rf, htmls)
    return htmls


def note(text): return f"<p class='note'>{text}</p>"


def key_findings(run, s):
    L1 = s.get("L1", {}); L2 = s.get("L2", {}); L3 = s.get("L3", {}).get("staircase_T1"); L5 = s.get("L5", {}); L7 = s.get("L7", {}); E5 = s.get("E5", {}); E6 = s.get("E6", {}); H = s.get("H", {})
    tot_tok = sum(r["tokens"] for r in L1.get("layers", [])); tot_mod = sum(r["six_modal"] for r in L1.get("layers", []))
    b = [f"<li><b>코퍼스</b>: 층위 {len(s['layers'])}개, {tot_tok:,} 토큰, 6대 조동사 {tot_mod:,}개 (2014–2026).</li>"]
    if L2.get("cramers_v"): b.append(f"<li><b>층위 분업</b>: 층위 × 조동사 χ² = {L2['chi2']:,.0f} (df {L2['dof']}), Cramér's V = {L2['cramers_v']:.3f}; 다항 로짓 유사 R² = {L7.get('pseudo_r2', '—')}.</li>")
    if L3: b.append(f"<li><b>성명서 계단</b>: PELT 변화점 {L3['n_cp']}개 중 정책 사건 ±1회의 이내 {L3['n_cp_event']}개; 구문 보유율 반감기 {('%.1f회의' % L5['half_life']['all']) if L5.get('half_life', {}).get('all') else '≥ 24회의'}; 정형 문장 안 조동사 비율 {L5.get('formulaic_share_overall', '—')}.</li>")
    e2 = {(r["key"], r["macro"]): r for r in s.get("E2", {}).get("genre_all", []) if r["period"] == "T2"}
    rho = "; ".join(f"{k} CFNAI {e2[(k,'cfnai')]['rho']:+.2f}{'*' if (e2[(k,'cfnai')]['p'] or 1) < .05 else ''} / VIX {e2[(k,'vix')]['rho']:+.2f}{'*' if (e2[(k,'vix')]['p'] or 1) < .05 else ''}" for k in ("statement", "minutes", "press_conf", "speech") if (k, "cfnai") in e2 and (k, "vix") in e2)
    if rho: b.append(f"<li><b>총밀도 × 거시</b> (Spearman, 2020 제외): {rho}.</li>")
    c = E5.get("counts", {})
    if c: b.append(f"<li><b>전수 스크린 ledger</b>: 확정 VIX {c['vix']['confirmed']} / CFNAI {c['cfnai']['confirmed']}; 시대 구성 {c['vix']['era_composition'] + c['cfnai']['era_composition']}; 2020 의존 {c['vix']['T1_only'] + c['cfnai']['T1_only']}. 상위 확정: " + "; ".join(f"{lab(x['key'])} {x['unit']} × {x['macro'].upper()} ρ={x['rho_T2']:+.2f}" for x in E5.get("confirmed_top", [])[:4]) + ".</li>")
    if E6: b.append(f"<li><b>선행성</b>: Granger text→macro 최소 q = {E6.get('granger_min_q') and round(E6['granger_min_q'], 3)}; 예측 회귀 q<.10 {len(E6.get('predictive_q10', []))}/{E6.get('n_predictive')}.</li>")
    if H: b.append("<li><b>가설</b>: " + " · ".join(f"{k} {pill(v['verdict'])}" for k, v in H.items()) + "</li>")
    return "<div class='keys'><b>핵심 결과</b><ul>" + "".join(b) + "</ul></div>"


def panel_toc(sections):
    return "<nav class='ptoc'>" + "".join(f"<a class='l{lvl}' href='#{sid}'>{html.escape(t)}</a>" for lvl, sid, t in sections) + "</nav>"


def version_panel(V, cid, vname, alias, U, runs, inline, full_figs):
    run = f"{cid}_{U}"; s = runs.get(run)
    if not s: return "<p class='small'>(run 없음)</p>"
    counts = {r["layer"]: r["six_modal"] for r in s.get("L1", {}).get("layers", [])}
    layers = [l for l in s["layers"] if counts.get(l, 0) >= 100] or s["layers"]   # drop near-empty layers (e.g. vote lines, SEP addendum)
    ml = pc.main_layer(layers); has_st = "statement" in layers; multi = len(layers) > 1
    img = lambda name, cap: (r24.img(run, name, cap, inline) if (full_figs or name in ("L3_staircase_T1", "E2_heatmap", "L2_residuals")) else "")
    sec = []; body = []
    def H1(t, sid): sec.append((1, f"{V}{U}-{sid}", t)); body.append(f"<h1 id='{V}{U}-{sid}'>{t}</h1>")
    def H2(t, sid): sec.append((2, f"{V}{U}-{sid}", t)); body.append(f"<h2 id='{V}{U}-{sid}'>{t}</h2>")
    # 1 데이터
    H1("1. 데이터", "d"); body.append(interp.data(run, s, layers, ml) + r24.v_corpus(run) + note(NOTE_PMW) + r24.v_modal_pmw(run) + r24.v_descriptives(run))
    # 2 언어학
    H1("2. 코퍼스 언어학적 결과", "l")
    H2("2.1 층위 분업: χ², 표준화 잔차, 키니스", "l2")
    body.append(interp.division(run, s, layers, ml, U))
    if multi:
        body.append(img("L2_residuals", "층위 × 조동사 표준화 잔차.") + r24.v_residuals(run) + "".join(r24.v_keyness(run, l) for l in layers) + note(NOTE_KEY))
    else: body.append("<p class='small'>층위가 하나이므로 층위 간 대조는 없음(비교 탭 참조).</p>")
    H2("2.2 통시: 추세와 변화점", "l3")
    body.append(interp.diachronic(run, s, layers, ml, U) + img("L3_yearly_main", f"{lab(ml)} 조동사의 연도별 pmw.") + r24.v_mk(run) + note("주: Mann–Kendall 검정(회의 단위 per 1k; 연설은 분기 평균); Sen 기울기는 회의당 변화."))
    if has_st: body.append(img("L3_staircase_T1", f"성명서 회의별 단위 점유율(N2)과 PELT 변화점(점선), 정책 사건(라벨), 2014–2026 — 단위 = {pc.UNITS[U]}.") + r24.v_changepoints(run) + note("주: PELT(l2, 최소 구간 4회의, 벌점 2 ln n)를 표준화 점유율에 적용. 책임 문장 = 변화 이후(상승) 또는 이전(하락) 8회의 안의 해당 단위 문장."))
    H2("2.3 연어와 구문: 서술어 프로파일, collexeme, JSD, 용례", "l4")
    body.append(interp.collocation(run, s, layers, ml, U) + "".join(r24.v_profiles(run, l) for l in layers[:4]) + r24.v_collo(run, ml) + note(NOTE_COLLO) + r24.v_jsd(run, ml) + img("L4_verb_class_main", f"{lab(ml)} 서술어의 의미 부류 × 조동사.") + r24.v_kwic(run, ml))
    if has_st:
        H2("2.4 정형성: 보유율 반감기, 정형 문장 비율, 편집 이벤트", "l5")
        body.append(interp.formulaicity(run, s) + img("L5_retention_edits", "성명서 단위 보유율 곡선과 연도별 삽입·삭제.") + r24.v_retention(run) + note("주: 보유율 r(k) = 회의 t의 단위 집합 중 t+k에도 남아 있는 비율의 평균; 반감기 = r(k) < 0.5가 되는 k(선형 보간)."))
    H2("2.5 문법 맥락과 의미 유형", "l6")
    body.append(interp.context(run, s, layers, ml) + img("L6_context_main", f"{lab(ml)} 조동사의 문법 맥락 비율.") + "".join(r24.v_context(run, l) for l in layers[:3]) + note("주: 비율 = 해당 자질을 가진 토큰의 비율. 의미 유형은 Coates(1983)·Palmer(1990) 기준의 규칙 휴리스틱(저자 표본 일치 90%)."))
    H2("2.6 다항 로짓: 조동사 선택 모형", "l7"); body.append(interp.mnlogit(run, s) + r24.v_mnlogit(run) + note("주: 기준 범주 will. 상대위험비 = exp(계수). 설명변수: 층위, 시기(2019년 이전/이후), 주어 유형, 조건절, 인용."))
    H2("2.7 be appropriate 관용구", "l8"); body.append(interp.be_appropriate(run, s) + r24.v_be_appropriate(run))
    H2("2.8 의장·정책 국면 대조", "l9"); body.append(interp.contrasts(run, s) + r24.v_contrasts(run))
    # 3 계량경제
    H1("3. 계량경제적 결과", "e")
    H2("3.1 상관: 조동사 밀도 × CFNAI / VIX", "e2"); body.append(interp.corr(run, s, layers) + img("E2_heatmap", "층위별 조동사 밀도 × 거시 변수 Spearman ρ, T1과 2020 제외.") + r24.v_corr_all(run) + note("주: 밀도 = 층위 토큰 1,000개당 6대 조동사(또는 조동사별) 수. CFNAI = 3개월 이동평균, 회의 월 −2; VIX = 회의 전 28일 평균."))
    H2("3.2 회귀 스펙 표: 총밀도", "e3"); body.append(interp.regression(run, s, layers) + "".join(r24.v_regtable(run, l) for l in layers) + note(NOTE_REG))
    if U != "U1":
        H2("3.3 구문 회귀", "e4"); body.append(interp.units(run, s, layers, U) + "".join(r24.v_regtable_units(run, l) for l in layers[:5]) + note(NOTE_REG))
    H2("3.4 전수 스크린과 ledger", "e5"); body.append(interp.ledger(run, s, layers) + r24.v_ledger(run, "confirmed") + r24.v_ledger(run, "era_composition", 15) + r24.v_ledger(run, "T1_only", 15) + note(NOTE_LEDGER))
    H2("3.5 선행성: Granger, 예측 회귀", "e6"); body.append(interp.leadlag(run, s) + r24.v_granger(run) + note("주: Granger는 월별 CFNAI-MA3·VIX와 회의 단위 밀도, lag 2, 2020 제외; q = BH. 예측 회귀는 CFNAI(m+3) 또는 후 28일 ΔVIX를 거시 통제 + 텍스트로 설명, HAC."))
    H2("3.6 사건 연구", "e7"); body.append(interp.event(run, s) + img("E7_event_macro", "정책 사건 ±6개월의 CFNAI-MA3와 VIX.") + r24.v_event_text(run))
    H2("3.7 강건성", "e8"); body.append(interp.robustness(run, s) + r24.v_robustness(run))
    H2("3.8 Kawamura et al.(2019) 재현", "e9"); body.append(interp.kawamura(run, s) + r24.v_kawamura(run) + note("주: 헤징군 = would/could/may/might, 약속군 = will. 수준·1차 차분·2020 제외, HAC t."))
    H1("4. 가설 판정", "h"); body.append(interp.hypotheses(run, s, V, vname) + r24.v_hypotheses(run))
    head = (f"<div class='vhead'><h1>{V} · {html.escape(vname)}</h1><span class='small'>{alias} · run {run} · 단위 {pc.UNITS[U]} · 층위: {', '.join(lab(l) for l in layers)}</span></div>")
    return head + version_intro(V, s) + key_findings(run, s) + panel_toc(sec) + number("".join(body))


# ----------------------------------------------------------------------------------------------
def compare_panel(U, runs):
    rs = {V: runs.get(f"{cid}_{U}") for V, cid, _, _ in VERSIONS}; out = []
    # 정의
    rows = []
    for V, cid, vname, alias in VERSIONS:
        s = rs[V]; L1 = s.get("L1", {}).get("layers", []) if s else []
        rows.append({"버전": V, "별칭": alias, "구성": vname, "층위 수": len(s["layers"]) if s else "", "문서(층위 합)": sum(r["n_docs"] for r in L1), "토큰": sum(r["tokens"] for r in L1), "6대 조동사": sum(r["six_modal"] for r in L1)})
    out.append(tbl(pd.DataFrame(rows), "버전 정의와 규모 (T1 2014–2026)", reco_pred=lambda r: str(r["버전"]).startswith("V4")))
    # 가설
    rows = []
    for V, cid, vname, alias in VERSIONS:
        s = rs[V]; H = s.get("H", {}) if s else {}
        rows.append({"버전": f"{V} {alias}", **{k: pill(H[k]["verdict"]) if k in H else "" for k in ("H1", "H2", "H3", "H4", "H5")}, "H4 근거": H.get("H4", {}).get("evidence", ""), "H5 근거": H.get("H5", {}).get("evidence", "")[:80]})
    out.append(tbl(pd.DataFrame(rows), "가설 판정 H1–H5 (버전별)", reco_pred=lambda r: r["버전"].startswith("V4")))
    # 핵심 통계
    rows = []
    for V, cid, vname, alias in VERSIONS:
        s = rs[V]
        if not s: continue
        L2 = s.get("L2", {}); L3 = s.get("L3", {}).get("staircase_T1"); L5 = s.get("L5", {}); c = s.get("E5", {}).get("counts", {}); E6 = s.get("E6", {})
        rows.append({"버전": f"{V} {alias}", "χ² / V": (f"{L2['chi2']:,.0f} / {L2['cramers_v']:.3f}" if L2.get("cramers_v") else "—"), "다항로짓 유사 R²": s.get("L7", {}).get("pseudo_r2", "—"),
                     "변화점(사건)": (f"{L3['n_cp']} ({L3['n_cp_event']})" if L3 else "—"), "반감기": (f"{L5['half_life']['all']:.1f}" if L5.get("half_life", {}).get("all") else ("≥24" if L5.get("half_life") else "—")),
                     "확정 VIX": c.get("vix", {}).get("confirmed", ""), "확정 CFNAI": c.get("cfnai", {}).get("confirmed", ""), "시대구성": (c["vix"]["era_composition"] + c["cfnai"]["era_composition"]) if c else "", "2020의존": (c["vix"]["T1_only"] + c["cfnai"]["T1_only"]) if c else "",
                     "Granger 최소 q": (f"{E6['granger_min_q']:.3f}" if E6.get("granger_min_q") is not None else "—"), "예측 q<.10": f"{len(E6.get('predictive_q10', []))}/{E6.get('n_predictive', 0)}" if E6 else "—"})
    out.append(tbl(pd.DataFrame(rows), "핵심 통계 (버전별)", reco_pred=lambda r: r["버전"].startswith("V4")))
    # 총밀도 × 거시 by genre
    rows = []
    for V, cid, vname, alias in VERSIONS:
        s = rs[V]
        if not s: continue
        e2 = {(r["key"], r["macro"], r["period"]): r for r in s.get("E2", {}).get("genre_all", [])}
        r_ = {"버전": f"{V} {alias}"}
        for g in ("statement", "minutes", "press_conf", "speech"):
            for mv in ("cfnai", "vix"):
                for T in ("T1", "T2"):
                    x = e2.get((g, mv, T)); r_[f"{g} × {mv.upper()} {T}"] = ("" if not x or x["rho"] is None else f"{x['rho']:+.2f}{'*' if (x['p'] or 1) < .05 else ''}")
        rows.append(r_)
    out.append(tbl(pd.DataFrame(rows), "장르 총밀도 × CFNAI / VIX — Spearman ρ (T1, 2020 제외; * p<.05)", reco_pred=lambda r: r["버전"].startswith("V4")))
    # E3 spec (3) coefficients per layer ALL across versions
    rows = []
    for V, cid, vname, alias in VERSIONS:
        s = rs[V]
        if not s: continue
        for lay, sp in s.get("E3", {}).get("all_by_layer", {}).items():
            r3 = sp.get("(3)", {}); r6 = sp.get("(6) excl-2020", {}); r8 = sp.get("(8) Δ excl-2020", {})
            f = lambda d, v: ("" if v not in d else f"{d[v]['coef']:+.3f}{d[v]['stars'] or ''}")
            rows.append({"버전": f"{V} {alias}", "층위": lab(lay), "(3) CFNAI": f(r3, "cfnai_ma3_lag2"), "(3) VIX": f(r3, "vix_pre28"), "(6) CFNAI": f(r6, "cfnai_ma3_lag2"), "(6) VIX": f(r6, "vix_pre28"), "(8) ΔCFNAI": f(r8, "d_cfnai"), "(8) ΔVIX": f(r8, "d_vix"), "N": r3.get("cfnai_ma3_lag2", {}).get("n", "")})
    out.append(tbl(pd.DataFrame(rows), "총밀도 회귀 계수 (버전 × 층위): 스펙 (3) CFNAI+VIX, (6) 2020 제외, (8) 1차 차분·2020 제외; HAC", max_rows=120, reco_pred=lambda r: r["버전"].startswith("V4")) + note(NOTE_REG))
    # confirmed units union
    allc = {}
    for V, cid, vname, alias in VERSIONS:
        d = csv(f"{cid}_{U}", "E5_ledger")
        if d is None: continue
        d = d[(d.level == "layer") & (d.category == "confirmed")]
        for r in d.itertuples(): allc.setdefault((r.key, r.unit, r.macro), {})[V] = f"{r.rho_T2:+.2f}"
    rows = [{"층위": lab(k[0]), "단위": k[1], "거시": k[2].upper(), **{V: v.get(V, "") for V, _, _, _ in VERSIONS}} for k, v in sorted(allc.items(), key=lambda kv: (-len(kv[1]), kv[0]))]
    out.append(tbl(pd.DataFrame(rows), "확정 단위의 합집합 (셀 = ρ, 2020 제외; 빈칸 = 해당 버전에서 미확정 또는 층위 없음)", max_rows=80) + note(NOTE_LEDGER))
    # Kawamura genre ALL
    rows = []
    for V, cid, vname, alias in VERSIONS:
        d = csv(f"{cid}_{U}", "E9_kawamura")
        if d is None: continue
        d = d[(d.level == "genre") & (d.series.isin(["ALL", "hedge"]))]
        for (g, ser), s_ in d.groupby(["key", "series"]):
            f = lambda spec, var: (lambda x: (f"{x.coef.iloc[0]:+.3f}{x.stars.iloc[0] if isinstance(x.stars.iloc[0], str) else ''}" if len(x) else ""))(s_[(s_.spec == spec) & (s_["var"] == var)])
            rows.append({"버전": f"{V} {alias}", "장르": g, "계열": ("총밀도" if ser == "ALL" else "헤징군"), "수준 CFNAI": f("levels: CFNAI + VIX", "CFNAI-MA3"), "수준 VIX": f("levels: CFNAI + VIX", "VIX"), "2020 제외 CFNAI": f("levels excl-2020: CFNAI + VIX", "CFNAI-MA3"), "Δ CFNAI": f("Δ: ΔCFNAI + ΔVIX", "ΔCFNAI"), "Δ 2020 제외 CFNAI": f("Δ excl-2020", "ΔCFNAI")})
    out.append(tbl(pd.DataFrame(rows), "Kawamura 재현 (버전 × 장르): CFNAI 계수, HAC", max_rows=120, reco_pred=lambda r: r["버전"].startswith("V4")))
    return "<div class='cmp'>" + interp.compare(runs, VERSIONS, U) + number("".join(out)) + "</div>"


# ----------------------------------------------------------------------------------------------
def overview_md(text: str) -> str:
    """Keep the narrative sections that are not run-specific."""
    keep_h1 = ("0.", "1.", "3.", "6.", "7.", "8.", "9.", "부록"); parts = re.split(r"\n(?=# )", text); out = []   # §3 = 방법론과 학술적 근거; parts = re.split(r"\n(?=# )", text); out = []
    for p in parts:
        m = re.match(r"# (\S+)", p)
        if not m: out.append(p); continue
        if m.group(1).startswith("2."):
            subs = re.split(r"\n(?=## )", p); out.append("\n".join(s for s in subs if not re.match(r"## 2\.[34]", s)))
        elif m.group(1).startswith(keep_h1):
            if m.group(1).startswith("7."): p = re.sub(r"\{\{tbl:C11_U2:hypotheses\}\}", "(버전별 판정은 각 버전 탭 §4와 비교 탭 참조)", p)
            out.append(p)
    return "\n".join(out)


def main():
    runs = r24.load_runs(); commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    src = PAPER / "report_v3_program.md"; meta, text = r24.parse_front_matter(src.read_text(encoding="utf-8"))
    for inline, fname in ((True, "report_tabs_artifact.html"), (True, "report_tabs.html")):
        ov_md = r24.render_narrative(overview_md(text), runs, inline=inline); ov_body, _ = r24.html_from_md(ov_md)
        ov_body = versions_overview(runs) + "<hr><p class='small'>아래는 요약·가설·데이터·방법론과 학술적 근거·72 run 비교·논의·한계. 버전별 결과는 상단 탭(V1–V6), 버전 간 대조는 '비교' 탭.</p>" + ov_body
        tabs = ["<div class='tabs'><button data-v='V0'>개요</button><button data-v='VC'>비교</button>"] + [f"<button data-v='{V}' class='{'v4' if V == 'V4' else ''}' title='{html.escape(vname)}'>{V} {alias} · {html.escape(vname.split('(')[0].split(':')[0].strip())}</button>" for V, cid, vname, alias in VERSIONS] + ["</div>"]
        panels = [f"<section class='panel' data-v='V0'>{ov_body}</section>"]
        sub = lambda Vid: "<div class='subtabs'>" + "".join(f"<button data-u='{u}' class='{'on' if u == 'U2' else ''}'>{u} {html.escape(n)}</button>" for u, n in UNITS) + "</div>"
        cmp_body = "".join(f"<div class='upanel panel{' on' if u == 'U2' else ''}' data-u='{u}'><h1 style='border:none;padding:0;margin:0 0 8px'>버전 비교 — 단위 {html.escape(n)}</h1><p class='small'>같은 코드·같은 규칙으로 산출한 여섯 버전을 나란히 놓는다. 강조 행 = 권장 버전 V4.</p>{compare_panel(u, runs)}</div>" for u, n in UNITS)
        panels.append(f"<section class='panel' data-v='VC'>{sub('VC')}{cmp_body}</section>")
        for V, cid, vname, alias in VERSIONS:
            ub = "".join(f"<div class='upanel panel{' on' if u == 'U2' else ''}' data-u='{u}'>{version_panel(V, cid, vname, alias, u, runs, inline, full_figs=(u == 'U2'))}</div>" for u, n in UNITS)
            panels.append(f"<section class='panel' data-v='{V}'>{sub(V)}{ub}</section>")
        masthead = (f"<header class='masthead'><div class='eyebrow'>FOMC modal constructions · experiment results report v3 · tabbed edition · {html.escape(meta.get('date', ''))}</div>"
                    f"<h1>{html.escape(meta.get('title', ''))}</h1><p class='sub'>{html.escape(meta.get('subtitle', ''))}</p>"
                    f"<div class='chips'><span>버전 6 (V1 성명서만 … V6 미정제) × 단위 3</span><span>실험군 L1–L9 · E1–E9</span><span>표·그림은 버전 탭마다 새로 번호</span><span>local git @ {commit}</span></div></header>")
        content = f"<div class='wrap'><div class='layout'><main>{masthead}{''.join(tabs)}{''.join(panels)}</main></div></div>{JS}"
        css = r24.CSS + EXTRA_CSS; title = "FOMC 조동사 실험 결과보고서 (버전 비교판)"
        if fname.endswith("artifact.html"):
            (REP / fname).write_text(f"<title>{title}</title>\n{r24.FONTS}\n<style>{css}</style>\n{content}", encoding="utf-8")
        else:
            (REP / fname).write_text(f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title>{r24.FONTS}<style>{css}</style></head><body>{content}</body></html>", encoding="utf-8")
        print(fname, (REP / fname).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
