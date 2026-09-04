"""
14_build_report.py — Static comparison report for the scenario matrix (Phase 12).

Reads results/scenarios/<S>_<U>/{summary.json, README.md, tables/*.csv, figures/*.png} and the docs, and writes
  results/report/index.html            scenario grid with headline metrics
  results/report/scenario_<S>_<U>.html one page per scenario (README + figures + key tables)
  results/report/claims.html           C1–C3 support matrix (rule-based flags; humans decide)
  results/report/{plan,macro,qa,data_card}.html   docs/08, docs/10, results/qa/QA_report.md, docs/09
  results/report/report_all.html       single file with inlined images (for sharing as an artifact)
"""
from __future__ import annotations
import base64, json, sys, html, re
from pathlib import Path
import pandas as pd
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
SCEN = ROOT / "results" / "scenarios"; REP = ROOT / "results" / "report"; REP.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "experiments"))
from common_v3 import SCENARIOS, UNITS, LAYER_LABEL

md = MarkdownIt("commonmark").enable("table")
CSS = """
:root{--bg:#F2F4F6;--surface:#fff;--ink:#1A222C;--muted:#5A6572;--line:#D6DCE3;--accent:#24507A;--warn:#A8501F;--ok:#2C6E5C;--tint:#E6EEF6;
--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;--body:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;--display:"Noto Serif KR","Apple Myungjo",Georgia,serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#11161C;--surface:#181F27;--ink:#E5EAF0;--muted:#98A5B3;--line:#2C3640;--accent:#7FB0E0;--warn:#E0955F;--ok:#6FBFA8;--tint:#1E2B3A}}
:root[data-theme="dark"]{--bg:#11161C;--surface:#181F27;--ink:#E5EAF0;--muted:#98A5B3;--line:#2C3640;--accent:#7FB0E0;--warn:#E0955F;--ok:#6FBFA8;--tint:#1E2B3A}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.65}
.page{max-width:1080px;margin:0 auto;padding:32px 22px 80px}
nav.top{display:flex;flex-wrap:wrap;gap:6px 16px;font-family:var(--mono);font-size:12.5px;padding-bottom:14px;border-bottom:2px solid var(--ink);margin-bottom:22px}
nav.top a{color:var(--accent);text-decoration:none}nav.top a:hover{text-decoration:underline}
h1{font-family:var(--display);font-size:28px;line-height:1.25;margin:0 0 8px;text-wrap:balance}
h2{font-family:var(--display);font-size:21px;margin:36px 0 10px;padding-top:14px;border-top:1px solid var(--line)}
h3{font-size:16px;margin:22px 0 8px}p{max-width:78ch}.lede{color:var(--muted);font-size:16px;max-width:70ch}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:13px;line-height:1.5;background:var(--surface)}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}th{background:var(--tint);font-weight:600;white-space:nowrap}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:6px;margin:12px 0 20px}
td.n{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0 24px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:14px 16px}
.card .k{font-family:var(--mono);font-size:12px;color:var(--accent)}.card .t{font-weight:600;margin:4px 0 6px}.card .d{font-size:13px;color:var(--muted);margin:0}
.card a{color:var(--accent)}
.pill{display:inline-block;padding:1px 8px;border-radius:10px;font-family:var(--mono);font-size:11.5px;background:var(--tint);margin-right:4px}
.pill.ok{background:var(--ok);color:#fff}.pill.warn{background:var(--warn);color:#fff}
figure{margin:16px 0 22px}figure img{max-width:100%;border:1px solid var(--line);border-radius:4px;background:#fff}figcaption{font-size:12.5px;color:var(--muted);margin-top:4px}
details{margin:10px 0}summary{cursor:pointer;font-weight:600}
code{font-family:var(--mono);font-size:.9em;background:var(--tint);padding:1px 4px;border-radius:3px}
blockquote{border-left:3px solid var(--accent);margin:12px 0;padding:6px 14px;background:var(--surface)}
.small{font-size:12.5px;color:var(--muted)}
@media(max-width:760px){.grid{grid-template-columns:1fr}}
"""
NAV = [("index.html", "개요·시나리오 격자"), ("claims.html", "주장 후보 C1–C3"), ("plan.html", "전략(docs/08)"), ("macro.html", "CFNAI·VIX 근거(docs/10)"),
       ("data_card.html", "데이터 카드(docs/09)"), ("qa.html", "QA 리포트")]


def page(title, body, inline=False):
    nav = "" if inline else '<nav class="top">' + "".join(f'<a href="{h}">{t}</a>' for h, t in NAV) + "</nav>"
    return f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title><style>{CSS}</style></head><body><div class='page'>{nav}{body}</div></body></html>"


def img(path: Path, caption="", inline=False):
    if not path.exists(): return ""
    src = ("data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()) if inline else path.relative_to(REP.parent).as_posix().replace("scenarios/", "../scenarios/")
    return f"<figure><img src='{src}' alt='{html.escape(caption)}'><figcaption>{html.escape(caption)}</figcaption></figure>"


def csv_table(path: Path, max_rows=30, cols=None, sort=None, ascending=False, round_=3):
    if not path.exists(): return "<p class='small'>(표 없음)</p>"
    df = pd.read_csv(path)
    if cols: df = df[[c for c in cols if c in df.columns]]
    if sort and sort in df.columns: df = df.sort_values(sort, ascending=ascending)
    df = df.head(max_rows).round(round_)
    return "<div class='tw'>" + df.to_html(index=False, border=0, na_rep="", escape=True) + "</div>"


def fmt(v, nd=2):
    return "—" if v is None or (isinstance(v, float) and pd.isna(v)) else (f"{v:.{nd}f}" if isinstance(v, (int, float)) else str(v))


def load_summaries():
    out = {}
    for d in sorted(SCEN.glob("S*_U*")):
        f = d / "summary.json"
        if f.exists(): out[d.name] = json.loads(f.read_text())
    return out


def headline(s):
    b = s["blocks"]; e = b.get("E", {}); kaw = e.get("kawamura", [])
    def kv(key, mv, T):
        r = [k for k in kaw if k["level"] == "genre" and k["key"] == key and k["macro"] == mv and k["period"] == T]
        return (r[0]["rho"], r[0]["p"]) if r else (None, None)
    st_c = kv("statement", "cfnai", "T2"); mn_c = kv("minutes", "cfnai", "T2"); mn_v = kv("minutes", "vix", "T2"); st_v = kv("statement", "vix", "T2")
    B = b.get("B", {}).get("T1", {}); C = b.get("C", {}).get("half_life", {})
    return dict(n_cp=B.get("n_cp"), cp_event=B.get("cp_within_1_meeting_of_event"), hl=C.get("all"),
                conf_vix=e.get("n_confirmed_vix"), conf_cfnai=e.get("n_confirmed_cfnai"), t1_only=e.get("n_T1_only"),
                st_cfnai=st_c, mn_cfnai=mn_c, mn_vix=mn_v, st_vix=st_v, V=b.get("D", {}).get("cramers_v"))


def index_page(sums, inline=False):
    L = ["<div class='eyebrow'>FOMC modal constructions · scenario matrix · v3 corpus</div>",
         "<h1>시나리오 비교 보고서</h1>",
         "<p class='lede'>코퍼스 정의(S1–S6) × 분석 단위(U1–U3)의 18개 시나리오를 같은 코드로 돌린 결과. 각 블록 안에서 기간(T1 전체 / T2 2020 제외 / T3 2010–)과 정규화(N1 밀도 / N2 점유율 / N3 문서당 수)를 나란히 둔다. 결론이 설정에 따라 바뀌는지 자체가 결과다.</p>"]
    L.append("<h2>코퍼스 정의</h2><div class='tw'><table><tr><th>S</th><th>이름</th><th>층위</th><th>메모</th></tr>")
    for k, v in SCENARIOS.items():
        L.append(f"<tr><td>{k}</td><td>{html.escape(v['name'])}</td><td class='small'>{', '.join(LAYER_LABEL.get(l, l) for l in v['layers'])}</td><td class='small'>{html.escape(v['note'])}</td></tr>")
    L.append("</table></div>")
    L.append("<h2>격자: 핵심 지표</h2><p class='small'>변화점 = 성명서 계단(X-B, T1)의 PELT 변화점 수(정책 사건 ±1회의 이내 수) · 반감기 = 구문 보유율 반감기(회의) · 확정 VIX/CFNAI = 전수 스크린에서 T1·T2(2020 제외) 동부호 유의한 단위 수 · T1-only = 2020에 의존하는 적중 수 · ρ = 장르 총 조동사 밀도와의 Spearman(T2)</p>")
    L.append("<div class='tw'><table><tr><th>시나리오</th><th>단위</th><th>변화점(사건)</th><th>반감기</th><th>확정 VIX</th><th>확정 CFNAI</th><th>T1-only</th><th>ρ stmt×CFNAI</th><th>ρ min×CFNAI</th><th>ρ stmt×VIX</th><th>ρ min×VIX</th><th>V(층위×조동사)</th><th></th></tr>")
    for name, s in sums.items():
        h = headline(s)
        def rp(t): return "—" if t[0] is None else f"{t[0]:+.2f}{'*' if (t[1] is not None and t[1] < .05) else ''}"
        link = f"scenario_{name}.html" if not inline else f"#sc-{name}"
        L.append(f"<tr><td><b>{s['S']}</b> {html.escape(s['name'])}</td><td>{s['U']} {html.escape(s['unit'])}</td><td class='n'>{fmt(h['n_cp'],0)} ({fmt(h['cp_event'],0)})</td><td class='n'>{fmt(h['hl'],1)}</td>"
                 f"<td class='n'>{fmt(h['conf_vix'],0)}</td><td class='n'>{fmt(h['conf_cfnai'],0)}</td><td class='n'>{fmt(h['t1_only'],0)}</td>"
                 f"<td class='n'>{rp(h['st_cfnai'])}</td><td class='n'>{rp(h['mn_cfnai'])}</td><td class='n'>{rp(h['st_vix'])}</td><td class='n'>{rp(h['mn_vix'])}</td><td class='n'>{fmt(h['V'],3)}</td><td><a href='{link}'>열기</a></td></tr>")
    L.append("</table></div>")
    return "\n".join(L)


def scenario_page(name, s, inline=False):
    d = SCEN / name
    L = [f"<div class='eyebrow'>scenario {name}</div><h1>{s['S']} {html.escape(s['name'])} × {s['U']} {html.escape(s['unit'])}</h1><p class='lede'>{html.escape(s['note'])}</p>"]
    readme = (d / "README.md").read_text(encoding="utf-8") if (d / "README.md").exists() else ""
    readme = re.sub(r"^# .*\n", "", readme)
    L.append(md.render(readme))
    figs = [("A_top_units.png", "X-A 조동사별 상위 단위(주 층위)"), ("B_staircase_T1.png", "X-B 성명서 구문 계단, 2014–2026"), ("B_staircase_T3.png", "X-B 성명서 구문 계단, 2010–2026"),
            ("C_retention_edits.png", "X-C 보유율·편집 이벤트"), ("D_layer_residuals.png", "X-D 층위×조동사 표준화 잔차"), ("E_modal_heatmap.png", "X-E 조동사 밀도 × CFNAI/VIX (T1 vs 2020 제외)"),
            ("E_vix_overlay.png", "X-E 확정 VIX 상관 구문의 시계열"), ("F_be_appropriate.png", "X-F be appropriate × 조동사 × 층위")]
    if inline:  # single-file version: keep the page under the 16 MB artifact limit
        figs = [f for f in figs if f[0] not in ("A_top_units.png", "B_staircase_T3.png")]
    L.append("<h2>그림</h2>")
    for f, cap in figs: L.append(img(d / "figures" / f, cap, inline))
    L.append("<h2>표 (발췌)</h2>")
    L.append("<h3>corpus.csv — 층위별 코퍼스 (T1/T2/T3)</h3>" + csv_table(d / "tables" / "corpus.csv", 40))
    if (d / "tables" / "B2_changepoints_T1.csv").exists():
        L.append("<h3>B2 변화점과 원인 문장 (T1)</h3>" + csv_table(d / "tables" / "B2_changepoints_T1.csv", 40, cols=["unit", "break_date", "share_before", "share_after", "direction", "nearest_event", "days_to_event", "sentence_after", "sentence_before"]))
    L.append("<h3>D1 층위 × 조동사 (수, per 1k)</h3>" + csv_table(d / "tables" / "D1_layer_modal.csv", 20))
    L.append("<h3>D4 화용 대조 will/would/can/could (비율)</h3>" + csv_table(d / "tables" / "D4_pragmatic_contrast.csv", 40))
    L.append("<h3>E3 Kawamura 검정: 총 조동사 밀도 × CFNAI/VIX</h3>" + csv_table(d / "tables" / "E3_kawamura_aggregate.csv", 60, cols=["level", "key", "period", "macro", "n", "r", "p_r", "rho", "p_rho", "q_rho"]))
    L.append("<h3>E2 확정/2020-의존 단위 (|ρ excl-2020| 순)</h3>")
    if (d / "tables" / "E2_confirmed.csv").exists():
        df = pd.read_csv(d / "tables" / "E2_confirmed.csv"); df = df[df.confirmed | df.T1_only].assign(a=lambda x: x.rho_T2.abs()).sort_values(["confirmed", "a"], ascending=[False, False]).drop(columns="a").head(40)
        L.append("<div class='tw'>" + df.to_html(index=False, border=0, na_rep="") + "</div>")
    L.append("<h3>E4 사전 지정 구문 표 (층위별 ALL + 상위 8 + be appropriate; ρ와 HAC)</h3>" + csv_table(d / "tables" / "E4_main_constructions.csv", 80, cols=["layer", "unit", "n_tokens", "rho_cfnai_T1", "rho_cfnai_T2", "rho_cfnai_T3", "rho_vix_T1", "p_vix_T1", "rho_vix_T2", "p_vix_T2", "rho_vix_T3", "hac_b_vix_T1", "hac_p_vix_T1", "hac_b_vix_T2", "hac_p_vix_T2", "hac_b_cfnai_T2", "hac_p_cfnai_T2", "zero_T1"]))
    L.append("<h3>F1 be appropriate</h3>" + csv_table(d / "tables" / "F1_be_appropriate.csv", 40))
    L.append("<h3>G2 Granger (lag 2), text→macro / macro→text</h3>" + csv_table(d / "tables" / "G2_granger.csv", 40, sort="q_text_to_macro", ascending=True))
    return "\n".join(L)


def claims_page(sums, inline=False):
    L = ["<div class='eyebrow'>claims</div><h1>한 문장 주장 후보와 시나리오별 근거</h1>",
         "<p class='lede'>규칙 기반 플래그다. 최종 판단은 팀이 한다. 규칙: ① 반경기 양태(Kawamura형) = 장르 총 조동사 밀도 × CFNAI의 T2 Spearman ρ < −0.20 이고 p < .05 인 장르가 존재. ② 불확실성 신호 = T1·T2 동부호 유의한 VIX 단위(확정) ≥ 1. ③ 구문 특이성 = 확정 VIX 단위 수(단위 수준) > 확정 VIX 조동사 수(조동사 수준). ④ 계단 = 변화점의 절반 이상이 정책 사건 ±1회의 이내. ⑤ 편집층 무신호 = 성명서 층에서 확정 VIX 단위 0.</p>",
         "<div class='grid'>",
         "<div class='card'><div class='k'>C1 긍정·조건부</div><div class='t'>실물이 아니라 불확실성, 그것도 특정 구문에서만</div><p class='d'>지지 조건: ¬① ∧ ② ∧ ③</p></div>",
         "<div class='card'><div class='k'>C2 편집 우선</div><div class='t'>성명서 조동사 변화는 편집의 흔적, 거시 공변은 비편집층에서만</div><p class='d'>지지 조건: ④ ∧ ⑤ ∧ ②</p></div>",
         "<div class='card'><div class='k'>C3 부정·명확</div><div class='t'>조동사를 세는 것으로는 경제 상황을 읽을 수 없다</div><p class='d'>지지 조건: 조동사 수준 확정 VIX·CFNAI 0 ∧ ¬①</p></div>",
         "</div>",
         "<div class='tw'><table><tr><th>시나리오</th><th>① 반경기</th><th>② VIX 확정(단위)</th><th>③ 조동사 수준 확정</th><th>④ 계단(사건 일치)</th><th>⑤ 성명서층 확정 VIX</th><th>C1</th><th>C2</th><th>C3</th></tr>"]
    for name, s in sums.items():
        b = s["blocks"]; e = b.get("E", {}); kaw = e.get("kawamura", [])
        cc = [k for k in kaw if k["level"] == "genre" and k["macro"] == "cfnai" and k["period"] == "T2" and k["rho"] is not None and k["rho"] < -0.20 and k["p"] is not None and k["p"] < .05]
        f1 = len(cc) > 0
        n_vix = e.get("n_confirmed_vix", 0) or 0; f2 = n_vix >= 1
        modal_conf = e.get("confirmed_modal_level", []); n_mod_vix = sum(1 for c in modal_conf if c.get("macro") == "vix"); n_mod_cf = sum(1 for c in modal_conf if c.get("macro") == "cfnai")
        f3 = n_vix > n_mod_vix
        B = b.get("B", {}).get("T1", {}); f4 = (B.get("n_cp", 0) > 0 and B.get("cp_within_1_meeting_of_event", 0) >= 0.5 * B.get("n_cp", 1)) if B else None
        st_conf = sum(1 for c in e.get("confirmed_top", []) if c.get("key") == "statement" and c.get("macro") == "vix")
        # count precisely from E2 file
        f = SCEN / name / "tables" / "E2_confirmed.csv"
        if f.exists():
            df = pd.read_csv(f); st_conf = int(((df.key == "statement") & (df.macro == "vix") & df.confirmed).sum())
        f5 = st_conf == 0
        c1 = (not f1) and f2 and f3; c2 = bool(f4) and f5 and f2; c3 = (n_mod_vix == 0 and n_mod_cf == 0) and (not f1)
        cc_txt = ", ".join("{} ρ={}".format(k["key"], k["rho"]) for k in cc)
        def yn(v): return "<span class='pill ok'>예</span>" if v else ("<span class='pill'>—</span>" if v is None else "<span class='pill warn'>아니오</span>")
        L.append(f"<tr><td><b>{name}</b> <span class='small'>{html.escape(s['name'])} × {html.escape(s['unit'])}</span></td><td>{yn(f1)} <span class='small'>{cc_txt}</span></td>"
                 f"<td>{yn(f2)} <span class='small'>{n_vix}</span></td><td><span class='small'>VIX {n_mod_vix} / CFNAI {n_mod_cf}</span></td><td>{yn(f4)} <span class='small'>{B.get('cp_within_1_meeting_of_event','—')}/{B.get('n_cp','—')}</span></td>"
                 f"<td>{yn(f5)} <span class='small'>{st_conf}</span></td><td>{yn(c1)}</td><td>{yn(c2)}</td><td>{yn(c3)}</td></tr>")
    L.append("</table></div>")
    L.append("<h2>확정 VIX 단위 상위 (시나리오별)</h2>")
    for name, s in sums.items():
        top = s["blocks"].get("E", {}).get("confirmed_top", [])
        if not top: continue
        L.append(f"<h3>{name}</h3><div class='tw'><table><tr><th>수준</th><th>키</th><th>단위</th><th>거시</th><th>ρ T1</th><th>ρ excl-2020</th><th>ρ 2010–</th><th>토큰</th><th>제로비율</th></tr>")
        for c in top:
            L.append(f"<tr><td>{c['level']}</td><td>{LAYER_LABEL.get(c['key'], c['key'])}</td><td>{html.escape(str(c['unit']))}</td><td>{c['macro']}</td><td class='n'>{c['rho_T1']}</td><td class='n'>{c['rho_T2']}</td><td class='n'>{c.get('rho_T3','')}</td><td class='n'>{c['n_tokens_T1']}</td><td class='n'>{c.get('zero_share_T1','')}</td></tr>")
        L.append("</table></div>")
    return "\n".join(L)


def doc_page(title, path: Path):
    if not path.exists(): return f"<h1>{html.escape(title)}</h1><p>(없음: {path})</p>"
    return f"<div class='eyebrow'>{html.escape(path.relative_to(ROOT).as_posix())}</div>" + md.render(path.read_text(encoding="utf-8"))


def main():
    sums = load_summaries()
    (REP / "index.html").write_text(page("시나리오 비교 보고서", index_page(sums)), encoding="utf-8")
    (REP / "claims.html").write_text(page("주장 후보", claims_page(sums)), encoding="utf-8")
    for name, s in sums.items():
        (REP / f"scenario_{name}.html").write_text(page(f"시나리오 {name}", scenario_page(name, s)), encoding="utf-8")
    docs = {"plan": ("전략", ROOT / "docs" / "08_meeting_260904_direction_and_replan.md"), "macro": ("CFNAI·VIX 근거", ROOT / "docs" / "10_macro_indicator_rationale.md"),
            "data_card": ("데이터 카드", ROOT / "docs" / "09_data_card_v3.md"), "qa": ("QA 리포트", ROOT / "results" / "qa" / "QA_report.md")}
    for key, (title, path) in docs.items():
        (REP / f"{key}.html").write_text(page(title, doc_page(title, path)), encoding="utf-8")
    # single file
    body = [index_page(sums, inline=True), "<h1 id='claims'>주장 후보</h1>", claims_page(sums, inline=True)]
    for name, s in sums.items():
        body.append(f"<details id='sc-{name}'><summary>시나리오 {name} — {html.escape(s['name'])} × {html.escape(s['unit'])}</summary>{scenario_page(name, s, inline=True)}</details>")
    for key, (title, path) in docs.items():
        body.append(f"<details id='{key}'><summary>{html.escape(title)}</summary>{doc_page(title, path)}</details>")
    (REP / "report_all.html").write_text(page("FOMC 조동사 시나리오 보고서", "\n".join(body), inline=True), encoding="utf-8")
    print(f"report: {len(sums)} scenarios -> {REP}")


if __name__ == "__main__":
    main()
