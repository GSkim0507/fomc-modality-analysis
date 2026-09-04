"""
15_render_report_doc.py — Render paper/report_v3.md to HTML (standalone + artifact fragment) and DOCX.

  paper/report_v3.html                 standalone page (figures inlined as data URIs)
  results/report/report_v3_artifact.html  fragment for the Artifact host (<title> + <style> + content)
  paper/report_v3.docx                 via pandoc (figures resolved relative to paper/)
"""
from __future__ import annotations
import base64, re, subprocess, sys, html
from pathlib import Path
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"; REP = ROOT / "results" / "report"
sys.path.insert(0, str(ROOT / "experiments"))
import importlib.util
spec = importlib.util.spec_from_file_location("r14", ROOT / "experiments" / "14_build_report.py"); r14 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r14)

EXTRA_CSS = """
.page{max-width:920px}
h1{font-size:24px;margin-top:40px;padding-top:16px;border-top:2px solid var(--ink)}
h1:first-of-type{border-top:none;padding-top:0;margin-top:0}
.masthead h1{font-size:30px;border:none;margin:0 0 6px}
.masthead .sub{font-size:16px;color:var(--muted);margin:0 0 4px}
img{max-width:100%;border:1px solid var(--line);border-radius:4px;background:#fff;margin:6px 0}
p>img+em, p em:only-child{display:block;font-size:12.5px;color:var(--muted)}
hr{border:none;border-top:1px solid var(--line);margin:28px 0}
td,th{font-size:12.5px}
"""


def render(md_text: str, inline_images: bool) -> tuple[str, dict]:
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", md_text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); meta[k.strip()] = v.strip().strip('"')
        md_text = md_text[m.end():]
    body = r14.md.render(md_text)
    # wrap figures so that <img> inside <p> keeps its caption; inline images
    def repl(mm):
        src = mm.group(1); alt = mm.group(2)
        path = PAPER / src
        if inline_images and path.exists():
            src = "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
        return f"<figure><img src='{src}' alt='{html.escape(alt)}'><figcaption>{html.escape(alt)}</figcaption></figure>"
    body = re.sub(r"<p><img src=\"([^\"]+)\" alt=\"([^\"]*)\"\s*/?></p>", repl, body)
    body = re.sub(r"<img src=\"([^\"]+)\" alt=\"([^\"]*)\"\s*/?>", lambda mm: repl(mm), body)
    head = (f"<div class='masthead'><div class='eyebrow'>paper/report_v3.md · {html.escape(meta.get('date', ''))}</div>"
            f"<h1>{html.escape(meta.get('title', 'Report'))}</h1><p class='sub'>{html.escape(meta.get('subtitle', ''))}</p></div>")
    return head + r14.safe(body), meta


def main():
    md_text = (PAPER / "report_v3.md").read_text(encoding="utf-8")
    body, meta = render(md_text, inline_images=True)
    css = r14.CSS + EXTRA_CSS
    title = "FOMC 조동사 재실험 보고서"
    (PAPER / "report_v3.html").write_text(f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title><style>{css}</style></head><body><div class='page'>{body}</div></body></html>", encoding="utf-8")
    (REP / "report_v3_artifact.html").write_text(f"<title>{title}</title>\n<style>{css}</style>\n<div class='page'>{body}</div>", encoding="utf-8")
    r = subprocess.run(["pandoc", "report_v3.md", "-o", "report_v3.docx", "--resource-path=.", "--from=markdown+pipe_tables"], cwd=PAPER, capture_output=True, text=True)
    print("pandoc:", r.returncode, r.stderr[:300])
    print("html:", (PAPER / "report_v3.html").stat().st_size // 1024, "KB; artifact:", (REP / "report_v3_artifact.html").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
