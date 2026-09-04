"""
15_render_report_doc.py — Build the HTML experiment report from paper/report_v3.md (single source of truth).

  paper/report_v3.html                     standalone page: sticky table of contents, summary panel, numeric
                                           table alignment, recommended-scenario highlight, inlined figures,
                                           light/dark themes, print stylesheet
  results/report/report_v3_artifact.html   the same page as an Artifact fragment (<title> + <style> + body)
  paper/report_v3.docx                     optional (--docx), via pandoc
"""
from __future__ import annotations
import base64, re, subprocess, sys, html, argparse
from pathlib import Path
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"; REP = ROOT / "results" / "report"; REP.mkdir(parents=True, exist_ok=True)
md = MarkdownIt("commonmark").enable("table")

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600&family=Noto+Serif+KR:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">'
CSS = """
:root{--bg:#F2F4F6;--surface:#FFFFFF;--ink:#1A222C;--muted:#5A6572;--line:#D6DCE3;--accent:#24507A;--accent-ink:#FFFFFF;
--warn:#A8501F;--ok:#2C6E5C;--tint:#E6EEF6;--tint2:#EEF3F8;--hl:#FFF4DC;
--mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
--body:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;
--display:"Noto Serif KR","Apple Myungjo","Nanum Myeongjo",Georgia,serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#11161C;--surface:#181F27;--ink:#E5EAF0;--muted:#98A5B3;--line:#2C3640;
--accent:#7FB0E0;--accent-ink:#0F1B27;--warn:#E0955F;--ok:#6FBFA8;--tint:#1E2B3A;--tint2:#1A2431;--hl:#3A3120}}
:root[data-theme="dark"]{--bg:#11161C;--surface:#181F27;--ink:#E5EAF0;--muted:#98A5B3;--line:#2C3640;
--accent:#7FB0E0;--accent-ink:#0F1B27;--warn:#E0955F;--ok:#6FBFA8;--tint:#1E2B3A;--tint2:#1A2431;--hl:#3A3120}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15.5px;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:36px 24px 96px}
.layout{display:grid;grid-template-columns:230px minmax(0,1fr);gap:40px;align-items:start}
aside.toc{position:sticky;top:20px;max-height:calc(100vh - 40px);overflow:auto;font-size:13px;line-height:1.5;padding-right:6px}
aside.toc .lbl{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
aside.toc a{display:block;color:var(--ink);text-decoration:none;padding:3px 0 3px 10px;border-left:2px solid var(--line)}
aside.toc a.l2{padding-left:20px;color:var(--muted);font-size:12.5px}
aside.toc a:hover{color:var(--accent);border-left-color:var(--accent)}
main{min-width:0}
header.masthead{padding-bottom:22px;border-bottom:2px solid var(--ink);margin-bottom:26px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
header h1{font-family:var(--display);font-weight:700;font-size:clamp(26px,3.6vw,34px);line-height:1.25;margin:8px 0 6px;text-wrap:balance;border:none;padding:0}
header .sub{font-size:16px;color:var(--muted);margin:0 0 12px;max-width:70ch}
.chips{display:flex;flex-wrap:wrap;gap:6px 14px;font-family:var(--mono);font-size:12px;color:var(--muted)}
h1{font-family:var(--display);font-weight:600;font-size:23px;line-height:1.3;margin:54px 0 14px;padding-top:18px;border-top:1px solid var(--line);text-wrap:balance;scroll-margin-top:16px}
h2{font-size:17px;font-weight:600;margin:30px 0 10px;scroll-margin-top:16px}
h3{font-size:15.5px;font-weight:600;margin:22px 0 8px}
p{max-width:74ch;margin:0 0 14px}
ul,ol{max-width:74ch;padding-left:22px;margin:0 0 14px}
li{margin:5px 0}
li>p{margin:0}
strong{font-weight:600}
code{font-family:var(--mono);font-size:.88em;background:var(--tint);padding:1px 5px;border-radius:3px}
pre{background:var(--tint);padding:12px 14px;border-radius:6px;overflow-x:auto;font-size:13px}
pre code{background:none;padding:0}
hr{border:none;border-top:1px solid var(--line);margin:32px 0}
blockquote{border-left:3px solid var(--accent);margin:14px 0;padding:8px 16px;background:var(--surface)}
.summary{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:22px 26px;margin:0 0 10px}
.summary h1{border:none;padding:0;margin:0 0 12px;font-size:20px}
.summary p{max-width:none}
.summary ol,.summary ul{max-width:none}
.summary .reco{background:var(--accent);color:var(--accent-ink);padding:14px 18px;border-radius:6px;margin-top:6px}
.summary .reco strong{color:inherit}
.summary .reco em{color:inherit}
.tw{overflow-x:auto;margin:14px 0 22px;border:1px solid var(--line);border-radius:6px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.55}
th,td{padding:8px 11px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{font-weight:600;background:var(--tint);white-space:nowrap}
tr:last-child td{border-bottom:none}
td.n{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}
tr.reco td{background:var(--hl)}
figure{margin:18px 0 26px}
figure img{max-width:100%;border:1px solid var(--line);border-radius:4px;background:#fff;display:block}
figcaption{font-size:12.5px;color:var(--muted);margin-top:6px;max-width:80ch}
.small{font-size:13px;color:var(--muted)}
a{color:var(--accent)}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:900px){.layout{grid-template-columns:1fr}aside.toc{position:static;max-height:none;display:flex;flex-wrap:wrap;gap:4px 12px;border-bottom:1px solid var(--line);padding-bottom:12px}aside.toc a{border:none;padding:2px 0}aside.toc a.l2{display:none}aside.toc .lbl{width:100%}}
@media print{body{background:#fff;color:#000}.wrap{padding:0}.layout{display:block}aside.toc{display:none}.tw{overflow:visible;border:none}figure img{border:none}h1{break-before:auto}}
"""

NUM_RE = re.compile(r"^\s*(?:[+\-−–]?\s*[\d.,]+%?\*{0,3}|—|-|≥\s*\d+|[\d.]+\s*\(\d+\)|[+\-−][\d.]+\*?(?:\s*/\s*[+\-−—][\d.]*\*?)*|[.\d]+\s*/\s*[.\d]+(?:\s*/\s*[.\d]+)?)\s*$")


def parse_front_matter(text: str):
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); meta[k.strip()] = v.strip().strip('"')
        text = text[m.end():]
    return meta, text


def slug(text: str, used: set) -> str:
    s = re.sub(r"[^\w가-힣]+", "-", text.strip().lower()).strip("-")[:60] or "s"
    base, i = s, 2
    while s in used:
        s = f"{base}-{i}"; i += 1
    used.add(s); return s


def postprocess(body: str, inline_images: bool):
    # headings: ids + toc
    used, toc = set(), []
    def head(mm):
        level, inner = mm.group(1), mm.group(2)
        text = re.sub(r"<[^>]+>", "", inner)
        sid = slug(text, used)
        if level in ("1", "2"):
            toc.append((level, sid, text))
        return f"<h{level} id='{sid}'>{inner}</h{level}>"
    body = re.sub(r"<h([1-3])>(.*?)</h\1>", head, body, flags=re.S)
    # figures
    def fig(mm):
        src, alt = mm.group(1), mm.group(2)
        path = PAPER / src
        if inline_images and path.exists():
            src = "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
        return f"<figure><img src='{src}' alt='{html.escape(html.unescape(alt))}' loading='lazy'><figcaption>{alt}</figcaption></figure>"
    body = re.sub(r"<p><img src=\"([^\"]+)\" alt=\"([^\"]*)\"\s*/?></p>", fig, body)
    # tables: wrap, numeric alignment, recommended row highlight
    def tbl(mm):
        t = mm.group(0)
        t = re.sub(r"<td>(.*?)</td>", lambda c: (f"<td class='n'>{c.group(1)}</td>" if NUM_RE.match(re.sub(r'<[^>]+>', '', c.group(1))) else c.group(0)), t, flags=re.S)
        t = re.sub(r"<tr>(?=(?:(?!</tr>).)*S4 4장르 정제\(권장\)(?:(?!</tr>).)*U2 구문)", "<tr class='reco'>", t, flags=re.S)
        return f"<div class='tw'>{t}</div>"
    body = re.sub(r"<table>.*?</table>", tbl, body, flags=re.S)
    # summary panel = everything from the first <h1> to the first <hr>
    first_h1 = body.find("<h1 "); first_hr = body.find("<hr", first_h1)
    if 0 <= first_h1 < first_hr:
        block = body[first_h1:first_hr]
        block = re.sub(r"<p><strong>추천\.</strong>(.*?)</p>", r"<div class='reco'><strong>추천.</strong>\1</div>", block, flags=re.S)
        body = body[:first_h1] + f"<section class='summary'>{block}</section>" + body[first_hr:]
    return body, toc


def build(meta, body, toc, commit: str, standalone: bool):
    title = meta.get("title", "Report"); sub = meta.get("subtitle", ""); date = meta.get("date", "")
    nav = "<aside class='toc'><div class='lbl'>목차</div>" + "".join(f"<a class='l{l}' href='#{sid}'>{html.escape(t)}</a>" for l, sid, t in toc) + "</aside>"
    masthead = (f"<header class='masthead'><div class='eyebrow'>FOMC modal constructions · experiment report v3 · {html.escape(date)}</div>"
                f"<h1>{html.escape(title)}</h1><p class='sub'>{html.escape(sub)}</p>"
                f"<div class='chips'><span>코퍼스 v3 · 404문서 · 층위 18종</span><span>시나리오 18개 (S1–S6 × U1–U3)</span><span>확정 규칙 D15</span><span>repo airlab-tsw/fomc-modality-analysis @ {commit}</span></div></header>")
    content = f"<div class='wrap'><div class='layout'>{nav}<main>{masthead}{body}</main></div></div>"
    if standalone:
        return (f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                f"<title>FOMC 조동사 재실험 보고서</title>{FONTS}<style>{CSS}</style></head><body>{content}</body></html>")
    return f"<title>FOMC 조동사 재실험 보고서</title>\n{FONTS}\n<style>{CSS}</style>\n{content}"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--docx", action="store_true"); a = ap.parse_args()
    meta, text = parse_front_matter((PAPER / "report_v3.md").read_text(encoding="utf-8"))
    body = md.render(text).replace("�", "&#xFFFD;")
    body, toc = postprocess(body, inline_images=True)
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = ""
    (PAPER / "report_v3.html").write_text(build(meta, body, toc, commit, standalone=True), encoding="utf-8")
    (REP / "report_v3_artifact.html").write_text(build(meta, body, toc, commit, standalone=False), encoding="utf-8")
    print("html:", (PAPER / "report_v3.html").stat().st_size // 1024, "KB;", len(toc), "toc entries")
    if a.docx:
        r = subprocess.run(["pandoc", "report_v3.md", "-o", "report_v3.docx", "--resource-path=."], cwd=PAPER, capture_output=True, text=True)
        print("pandoc:", r.returncode, r.stderr[:200])


if __name__ == "__main__":
    main()
