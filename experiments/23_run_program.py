"""
23_run_program.py — Run the full experiment programme (Phase 14): every corpus definition x unit.

  .venv/bin/python experiments/23_run_program.py --corpus all --unit all [--workers 4]
  .venv/bin/python experiments/23_run_program.py --corpus main            # the six aliased corpora S1–S6
  .venv/bin/python experiments/23_run_program.py --corpus C11 --unit U2
Outputs results/program/<Cxx>_<U>/{tables,figures,summary.json,README.md}
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")   # one BLAS thread per worker: 4 workers x multi-threaded BLAS was 100x slower
import argparse, json, sys, time, traceback
from pathlib import Path
from types import SimpleNamespace
import pandas as pd
import importlib.util

HERE = Path(__file__).resolve().parent
def _load(name, fn):
    s = importlib.util.spec_from_file_location(name, HERE / fn); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
pc = _load("pc", "20_program_common.py"); L = _load("L", "21_exp_linguistic.py"); E = _load("E", "22_exp_econometric.py")

_DATA = {}


def _data():
    if not _DATA:
        _DATA["tokens"] = pc.load_tokens(); _DATA["docs"] = pc.load_docs(); _DATA["macro"] = pc.load_macro(); _DATA["monthly"] = pc.load_monthly()
    return _DATA


def readme(ctx):
    s = ctx.summary; L_ = [f"# {ctx.cid} {s['alias'] or ''} — {s['name']} × {s['unit']}", ""]
    L_ += ["## 코퍼스 (T1)", "", "| 층위 | 문서 | 토큰 | 6대 조동사 | pmw (95% CI) |", "|---|---:|---:|---:|---|"]
    for r in s.get("L1", {}).get("layers", []): L_.append(f"| {r['label']} | {r['n_docs']} | {r['tokens']:,} | {r['six_modal']:,} | {r['pmw']:,.0f} ({r['ci_lo']:,.0f}–{r['ci_hi']:,.0f}) |")
    if s.get("L2", {}).get("cramers_v"): L_ += ["", f"- L2 층위 × 조동사: χ²={s['L2']['chi2']}, V={s['L2']['cramers_v']}"]
    st = s.get("L3", {}).get("staircase_T1")
    if st: L_ += [f"- L3 성명서 계단: 변화점 {st['n_cp']}개, 사건 ±1회의 {st['n_cp_event']}개"]
    if s.get("L5", {}).get("half_life"): L_ += [f"- L5 보유율 반감기: " + ", ".join(f"{k}={('%.1f' % v) if v else '≥24'}" for k, v in s['L5']['half_life'].items())]
    e5 = s.get("E5", {}).get("counts", {})
    if e5: L_ += [f"- E5 ledger: VIX 확정 {e5['vix']['confirmed']} / 시대구성 {e5['vix']['era_composition']} / 2020의존 {e5['vix']['T1_only']}; CFNAI 확정 {e5['cfnai']['confirmed']} / {e5['cfnai']['era_composition']} / {e5['cfnai']['T1_only']}"]
    H = s.get("H", {})
    if H: L_ += ["", "## 가설", ""] + [f"- {k}: **{v['verdict']}** — {v['evidence']}" for k, v in H.items()]
    if s.get("errors"): L_ += ["", "## 오류", ""] + [f"- {k}: {v}" for k, v in s["errors"].items()]
    (ctx.out / "README.md").write_text("\n".join(L_), encoding="utf-8")


def run_one(cid: str, U: str) -> dict:
    d = _data(); cdef = pc.CORPUS_DEFS[cid]; layers = cdef["layers"]
    out = pc.PROG / f"{cid}_{U}"; (out / "tables").mkdir(parents=True, exist_ok=True); (out / "figures").mkdir(exist_ok=True)
    tokens, docs = d["tokens"], d["docs"]
    tk9 = tokens[tokens.layer.isin(layers) & tokens.modal.isin(pc.NINE)].copy(); tk = tk9[tk9.modal.isin(pc.SIX)].copy()
    dl = docs[docs.layer.isin(layers)].copy()
    ctx = SimpleNamespace(cid=cid, cdef=cdef, U=U, unit_col=U, layers=layers, main_layer=pc.main_layer(layers), out=out, tk=tk, tk9=tk9, dl=dl,
                          macro=d["macro"], monthly=d["monthly"], summary=dict(cid=cid, alias=cdef["alias"], name=cdef["name"], layers=layers, U=U, unit=pc.UNITS[U], unfiltered=cdef["unfiltered"], errors={}, blocks_ok=[]))
    t0 = time.time()
    for block in L.BLOCKS + E.BLOCKS:
        try:
            block(ctx); ctx.summary["blocks_ok"].append(block.__name__)
        except Exception as e:
            ctx.summary["errors"][block.__name__] = f"{type(e).__name__}: {e}"[:300]
            print(f"[{cid}_{U}] {block.__name__} failed: {e}", file=sys.stderr); traceback.print_exc(limit=2)
    try: ctx.summary["H"] = E.hypotheses(ctx)
    except Exception as e: ctx.summary["errors"]["hypotheses"] = str(e)[:200]
    ctx.summary["runtime_s"] = round(time.time() - t0, 1)
    (out / "summary.json").write_text(json.dumps(ctx.summary, indent=1, ensure_ascii=False, default=pc.jsonable))
    readme(ctx); print(f"{cid}_{U} ({cdef['alias'] or cdef['name']}) done in {ctx.summary['runtime_s']}s; errors={list(ctx.summary['errors'])}", file=sys.stderr)
    return ctx.summary


def _worker(args):
    return run_one(*args)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", default="all"); ap.add_argument("--unit", default="all"); ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--skip-existing", action="store_true", help="skip runs whose summary.json already exists"); a = ap.parse_args()
    cids = list(pc.CORPUS_DEFS) if a.corpus == "all" else (pc.MAIN_CORPORA if a.corpus == "main" else a.corpus.split(","))
    Us = list(pc.UNITS) if a.unit == "all" else a.unit.split(",")
    jobs = [(c, u) for c in cids for u in Us]
    if a.skip_existing: jobs = [(c, u) for c, u in jobs if not (pc.PROG / f"{c}_{u}" / "summary.json").exists()]
    print(f"{len(jobs)} runs to do", file=sys.stderr); t0 = time.time()
    if a.workers > 1:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(a.workers) as pool:
            for _ in pool.imap_unordered(_worker, jobs): pass
    else:
        for j in jobs: run_one(*j)
    print(f"all {len(jobs)} runs done in {time.time()-t0:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
