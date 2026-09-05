"""
28_build_seminar.py — 세미나 발표용 실험 결과보고서 (Phase 16).

기존 26(탭판)은 '버전'이 최상위 탭이라 조합을 비교하려면 보고서를 통째로 다시 읽어야 했다.
이 빌더는 그 축을 뒤집는다: 서사는 하나로 흐르고, 각 결과 지점마다 시나리오 탭이 붙는다.
탭은 문서 전체에서 동기화되므로, 한 번 고르면 보고서 전체가 그 조합의 수치로 읽힌다.

원고: paper/report_v3_seminar.md
지시자
  {{cmp:tbl:VIEW[:arg…]}}        시나리오 탭 + 표
  {{cmp:fig:NAME|캡션}}          시나리오 탭 + 그림
  {{scnbar}}                     본문 상단의 조합 선택 막대
  {{tbl:RUN:…}} {{fig:RUN:…}} {{grid}} {{hgrid}}   기존 지시자(24가 처리)
출력: results/report_v3/seminar.html
"""
from __future__ import annotations
import html, json, re, subprocess
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("r24", ROOT / "experiments" / "24_build_report_v3.py")
r24 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r24)
REP, PAPER = r24.REP, r24.PAPER

# docs/08 §3.3 "주 비교 3종(S1·S2·S4)을 나란히, 나머지는 강건성 부록"
SCEN = [
    ("C02", "성명서만",            "회의 후 성명서만. 가장 강하게 편집되는 정형문이며, 의사록 없이 연구질문에 답할 수 있는지를 재는 기준선."),
    ("C06", "성명서 + 위원회 층",   "같은 회의·같은 위원회의 결정 서술만 더한 최소 확장. 성명서 문장의 인용은 제외했다."),
    ("C11", "4장르 정제",          "연준의 공식 발화 전체. 기자·진행자 발화를 제거한 의장 기자회견과 연설을 더했다. 권장 조합."),
]
DEFAULT_CID, UNIT = "C11", "U2"
LABELS = {cid: name for cid, name, _ in SCEN}

CSS_EXTRA = """
/* 한국어 조판: 단어 중간 줄바꿈 금지 (제목이 "설명하는/가"로 갈라지던 문제) */
main :is(h1,h2,h3,p,li,td,th,figcaption), aside.toc a, .masthead .sub{word-break:keep-all;overflow-wrap:break-word}
.scn{margin:16px 0 8px;border:1px solid var(--line);border-radius:8px;background:var(--surface);overflow:hidden}
.scntabs{display:flex;flex-wrap:wrap;border-bottom:1px solid var(--line);background:var(--bg)}
.scntabs button{font:inherit;font-size:13px;padding:9px 16px;border:0;border-right:1px solid var(--line);
  background:transparent;color:var(--muted);cursor:pointer;white-space:nowrap}
.scntabs button:hover{color:var(--ink)}
.scntabs button.on{background:var(--surface);color:var(--accent);font-weight:600;box-shadow:inset 0 -2px 0 var(--accent)}
.scntabs button:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.scnpanel{display:none;padding:14px 16px 4px}
.scnpanel.on{display:block}
.scnbar{position:sticky;top:0;z-index:6;background:var(--bg);border-bottom:2px solid var(--ink);
  padding:10px 0 9px;margin:0 0 20px;display:flex;flex-wrap:wrap;gap:10px;align-items:baseline}
.scnbar .lbl{font-size:12.5px;color:var(--muted)}
.scnbar .opts{display:flex;flex-wrap:wrap;gap:6px}
.scnbar button{font:inherit;font-size:13px;padding:5px 13px;border:1px solid var(--line);border-radius:15px;
  background:var(--surface);color:var(--ink);cursor:pointer}
.scnbar button.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent);font-weight:600}
.takeaway{border-left:4px solid var(--accent);background:var(--tint);border-radius:0 6px 6px 0;
  padding:11px 16px;margin:6px 0 26px;max-width:96ch}
.takeaway::before{content:'그래서 ';font-weight:600;color:var(--accent)}
.answer{border:2px solid var(--accent);border-radius:8px;padding:18px 22px;margin:18px 0 24px;background:var(--surface)}
.answer p{font-size:17.5px;line-height:1.62;margin:0;max-width:none;font-weight:500}
.decide{border:1px solid var(--warn);border-left:4px solid var(--warn);border-radius:0 6px 6px 0;
  background:var(--surface);padding:12px 18px;margin:14px 0 24px}
.decide b{color:var(--warn)}
"""

JS_EXTRA = """
<script>
(function(){
  var KEY='fomc-scenario', LABELS=__LABELS__;
  function apply(cid, anchor){
    var before = anchor ? anchor.getBoundingClientRect().top : null;
    Array.prototype.forEach.call(document.querySelectorAll('.scn,.scnbar'), function(g){
      Array.prototype.forEach.call(g.querySelectorAll('button[data-cid]'), function(b){
        var on = b.dataset.cid === cid;
        b.classList.toggle('on', on); b.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      Array.prototype.forEach.call(g.querySelectorAll('.scnpanel'), function(p){
        p.classList.toggle('on', p.dataset.cid === cid);
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-scn-label]'), function(e){
      e.textContent = LABELS[cid] || cid;
    });
    /* 클릭한 탭이 화면에서 튀지 않도록 패널 높이 변화만큼 되돌린다 */
    if (anchor && before !== null) { window.scrollBy(0, anchor.getBoundingClientRect().top - before); }
    try { sessionStorage.setItem(KEY, cid); } catch(e){}
  }
  document.addEventListener('click', function(ev){
    var b = ev.target.closest ? ev.target.closest('button[data-cid]') : null;
    if (!b) return;
    apply(b.dataset.cid, b.closest('.scn'));
  });
  var saved = null; try { saved = sessionStorage.getItem(KEY); } catch(e){}
  if (saved && LABELS[saved]) apply(saved, null);
})();
</script>
"""


def _absent_reason(s) -> str:
    """이 조합에서 결과가 나올 수 없는 이유를 사람 말로."""
    if not s:
        return "이 조합은 실행되지 않았다."
    n = len(s.get("layers", []))
    if n <= 1:
        return ("이 조합은 층위가 하나(성명서)뿐이라 층위 간 비교가 성립하지 않는다. "
                "층을 나누려면 의사록이 필요하다 — 그것이 바로 §3.2의 논점이다.")
    return "이 조합에서는 해당 분석의 최소 조건(표본·층위)이 충족되지 않아 산출되지 않았다."


def _tabs_html():
    return "".join(
        f"<button type='button' role='tab' data-cid='{cid}'"
        f"{' class=on' if cid == DEFAULT_CID else ''}"
        f" aria-selected='{'true' if cid == DEFAULT_CID else 'false'}'"
        f" title='{html.escape(why)}'>{html.escape(name)}</button>"
        for cid, name, why in SCEN)


def cmp_block(kind: str, spec: str, runs: dict, inline=True) -> str:
    panels = []
    for cid, name, _ in SCEN:
        run = f"{cid}_{UNIT}"
        if run not in runs:
            inner = "<p class='small'>(이 조합에는 해당 결과가 없다.)</p>"
        elif kind == "tbl":
            parts = spec.split(":"); view, args = parts[0], parts[1:]
            try:
                inner = r24.VIEWS[view](run, *args)
            except Exception as e:
                inner = f"<p class='small'>(이 조합에는 해당 표가 없다: {html.escape(str(e))})</p>"
        else:
            fname, _, cap = spec.partition("|")
            inner = r24.img(run, fname, cap, inline)
        # 결과가 없는 것이 '누락'이 아니라 '그 조합에서는 성립하지 않음'인 경우가 있다.
        # 기술적 메시지 대신 왜 없는지를 말한다 — 그 부재 자체가 논거이기 때문이다.
        if (not inner or not inner.strip()
                or any(k in inner for k in ("(그림 없음", "(표 없음", "(이 조합에는", "(층위 1개", "(단위 ="))):
            inner = f"<p class='small'>{_absent_reason(runs.get(run))}</p>"
        on = " on" if cid == DEFAULT_CID else ""
        panels.append(f"<div class='scnpanel{on}' data-cid='{cid}' role='tabpanel'>{inner}</div>")
    return (f"<div class='scn'><div class='scntabs' role='tablist' aria-label='코퍼스 조합'>"
            f"{_tabs_html()}</div>{''.join(panels)}</div>")


def scnbar() -> str:
    return ("<div class='scnbar'><span class='lbl'>코퍼스 조합</span>"
            f"<span class='opts'>{_tabs_html()}</span></div>")


def render(text: str, runs: dict, inline=True) -> str:
    text = re.sub(r"\{\{cmp:(tbl|fig):([^}]+)\}\}",
                  lambda m: cmp_block(m.group(1), m.group(2), runs, inline), text)
    text = text.replace("{{scnbar}}", scnbar())
    return r24.render_narrative(text, runs, inline)


def main():
    runs = r24.load_runs()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    src = PAPER / "report_v3_seminar.md"
    if not src.exists():
        raise SystemExit(f"원고 없음: {src}")
    meta, text = r24.parse_front_matter(src.read_text(encoding="utf-8"))
    body, toc = r24.html_from_md(render(text, runs, inline=True))
    doc = r24.page(meta, body, toc, commit, True, title=meta.get("title", "FOMC 조동사 실험 결과 보고"))
    doc = doc.replace("</style>", CSS_EXTRA + "</style>", 1)
    doc = doc.replace("</body>", JS_EXTRA.replace("__LABELS__", json.dumps(LABELS, ensure_ascii=False)) + "</body>", 1)
    out = REP / "seminar.html"
    out.write_text(doc, encoding="utf-8")
    print(f"seminar: {out} ({out.stat().st_size // 1024} KB), 시나리오 {len(SCEN)}종 × 단위 {UNIT}")


if __name__ == "__main__":
    main()
