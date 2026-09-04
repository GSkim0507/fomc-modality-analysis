"""
25_md_to_html.py — Render any project markdown document (docs/*.md, HANDOVER.md, ...) to a designed HTML page
using the report stylesheet (sticky TOC, tables, light/dark themes).

  .venv/bin/python experiments/25_md_to_html.py docs/12_experiment_program_v3.md [more.md ...]
Outputs: docs/html/<name>.html (standalone) and docs/html/<name>_artifact.html (fragment for the Artifact host).
"""
from __future__ import annotations
import html, re, subprocess, sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "html"; OUT.mkdir(parents=True, exist_ok=True)
_s = importlib.util.spec_from_file_location("r24", ROOT / "experiments" / "24_build_report_v3.py"); r24 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r24)


def render(path: Path):
    text = path.read_text(encoding="utf-8")
    meta, text = r24.parse_front_matter(text)
    # first-level title: use the first "# " heading as the page title, drop it from the body
    m = re.match(r"^\s*# (.+?)\n", text)
    title = meta.get("title") or (m.group(1).strip() if m else path.stem)
    if m and not meta.get("title"): text = text[m.end():]
    body, toc = r24.html_from_md(text)
    body = re.sub(r"<section class='summary'>(.*?)</section>", r"\1", body, flags=re.S)  # no summary panel for plain docs
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    meta = {"title": title, "subtitle": meta.get("subtitle", ""), "date": meta.get("date", path.relative_to(ROOT).as_posix())}
    name = path.stem
    (OUT / f"{name}.html").write_text(r24.page(meta, body, toc, commit, True, title=title), encoding="utf-8")
    (OUT / f"{name}_artifact.html").write_text(r24.page(meta, body, toc, commit, False, title=title), encoding="utf-8")
    print(f"{path.name} -> docs/html/{name}.html ({(OUT / f'{name}.html').stat().st_size // 1024} KB, {len(toc)} headings)")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        render((ROOT / arg) if not Path(arg).is_absolute() else Path(arg))
