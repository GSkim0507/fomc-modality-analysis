"""
20_program_common.py — Shared definitions for the full re-run programme (Phase 14; docs/12).

Corpus definitions: every combination of statement {in,out} x minutes {none, committee layer, substantive layers}
x press conference {none, chair only} x speech {in,out}, plus one unfiltered (v2-like) comparison corpus.
Units: U1 modal, U2 modal+predicate, U3 modal+verb class.
Statistics helpers used by both experiment families (pmw + CI, Gries DP, log-likelihood keyness, HAC OLS, BH, MK, PELT).
"""
from __future__ import annotations
import itertools, json, math, re, sys, importlib.util
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "results" / "tables"
PROG = ROOT / "results" / "program"; PROG.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "experiments"))
import common_v3 as c3
from common_v3 import SIX, EVENTS, PHASES, EXCLUDE_DOCS, LAYER_LABEL, MINUTES_SUBSTANTIVE, MINUTES_ALL, PC_ALL, genre_of, verb_class, refine_subj_type
NINE = SIX + ["might", "must", "shall"]
_spec05 = importlib.util.spec_from_file_location("x05", ROOT / "experiments" / "05_contexts_genre.py")
x05 = importlib.util.module_from_spec(_spec05); _spec05.loader.exec_module(x05)
semantic_type = x05.semantic_type

MACRO_VARS = {"cfnai": "cfnai_ma3_lag2", "vix": "vix_pre28"}
PERIODS = {"T1": ("2014-01-01", "2026-12-31", False), "T2": ("2014-01-01", "2026-12-31", True), "T3": ("2010-01-01", "2026-12-31", False),
           "H1": ("2014-01-01", "2019-12-31", False), "H2": ("2021-01-01", "2026-12-31", False)}
MAIN_PERIODS = ("T1", "T2", "T3")
UNITS = {"U1": "modal", "U2": "modal + predicate", "U3": "modal + verb class"}
MIN_TOKENS, MAX_ZERO, MIN_N = 40, 0.60, 30
NEW_FRAMEWORK = "2020-09-16"
LAYER_PRIORITY = ["statement", "min_participants", "min_committee", "pc_chair", "speech_chair", "min_staff", "min_staff_desk", "min_special"]


# ----------------------------------------------------------------------------------------------
# corpus definitions
# ----------------------------------------------------------------------------------------------
def build_corpus_defs() -> dict:
    defs, n = {}, 0
    MIN = {"0": [], "C": ["min_committee"], "S": MINUTES_SUBSTANTIVE}
    PC = {"0": [], "C": ["pc_chair"]}
    for st, mn, pc, sp in itertools.product((1, 0), ("0", "C", "S"), ("0", "C"), (1, 0)):
        layers = (["statement"] if st else []) + MIN[mn] + PC[pc] + (["speech_chair"] if sp else [])
        if not layers:
            continue
        n += 1
        cid = f"C{n:02d}"
        name = " + ".join(x for x in [("statement" if st else ""), {"0": "", "C": "minutes[committee]", "S": "minutes[substantive]"}[mn],
                                       ("press_conf[chair]" if pc == "C" else ""), ("speech" if sp else "")] if x)
        defs[cid] = dict(id=cid, name=name, layers=layers, statement=bool(st), minutes=mn, press_conf=pc, speech=bool(sp), unfiltered=False, alias="")
    n += 1
    defs[f"C{n:02d}"] = dict(id=f"C{n:02d}", name="unfiltered 4 genres (v2-like)", layers=["statement", "statement_vote"] + MINUTES_ALL + PC_ALL + ["speech_chair"],
                             statement=True, minutes="A", press_conf="A", speech=True, unfiltered=True, alias="S6")
    alias = {("statement",): "S1", ("statement", "min_committee"): "S2", tuple(["statement"] + MINUTES_SUBSTANTIVE): "S3",
             tuple(["statement"] + MINUTES_SUBSTANTIVE + ["pc_chair", "speech_chair"]): "S4", tuple(MINUTES_SUBSTANTIVE): "S5"}
    for d in defs.values():
        d["alias"] = d["alias"] or alias.get(tuple(d["layers"]), "")
    return defs


CORPUS_DEFS = build_corpus_defs()
MAIN_CORPORA = [cid for cid, d in CORPUS_DEFS.items() if d["alias"]]


def main_layer(layers: list) -> str:
    for l in LAYER_PRIORITY:
        if l in layers: return l
    return layers[0]


# ----------------------------------------------------------------------------------------------
# loaders
# ----------------------------------------------------------------------------------------------
def load_tokens() -> pd.DataFrame:
    df = pd.read_csv(TAB / "modal_tokens_v3.csv", low_memory=False)
    df = df[~df["doc_id"].isin(EXCLUDE_DOCS)].copy()
    for c in ("neg", "passive", "perfect", "progressive", "cond", "reported", "question", "contracted"):
        df[c] = df[c].astype(str).str.lower().eq("true")
    df["subj_type"] = [refine_subj_type(a, b) for a, b in zip(df["subj_lemma"], df["subj_text"])]
    df["predicate"] = df["predicate"].fillna(df["head_verb"]).astype(str)
    df["year"] = df["date"].str[:4].astype(int); df["genre"] = df["layer"].map(genre_of)
    df["vclass"] = [("copular_adj" if str(bt) == "adjectival" else "copular_nom" if str(bt) == "nominal" else "copular_prep" if str(bt) == "prepositional"
                     else "copular_adv" if str(bt) == "adverbial" else verb_class(str(hv))) for bt, hv in zip(df["be_comp_type"], df["head_verb"])]
    df["sem_type"] = [semantic_type(r) for r in df[["modal", "head_verb", "subj_type", "cond", "reported"]].itertuples(index=False)]
    df["U1"] = df["modal"]; df["U2"] = df["modal"] + "+" + df["predicate"]; df["U3"] = df["modal"] + "/" + df["vclass"]
    df["phase"] = df["date"].map(c3.phase_of if hasattr(c3, "phase_of") else c3.common_v2.phase_of)
    return df


def load_docs() -> pd.DataFrame:
    d = pd.read_csv(TAB / "corpus_docs_v3.csv"); d = d[~d["doc_id"].isin(EXCLUDE_DOCS)].copy()
    d["year"] = d["date"].str[:4].astype(int); d["genre"] = d["layer"].map(genre_of)
    return d


def load_macro() -> pd.DataFrame:
    m = pd.read_csv(TAB / "macro_by_doc.csv")
    return m.drop(columns=[c for c in ("doc_type", "date") if c in m.columns])


def load_monthly() -> pd.DataFrame:
    mon = pd.read_csv(TAB / "macro_monthly.csv"); mon["ym"] = pd.to_datetime(mon.date).dt.to_period("M")
    return mon.set_index("ym")


def load_statement_sentences() -> pd.DataFrame:
    s = pd.read_csv(TAB / "corpus_sentences_v3.csv", usecols=["doc_id", "date", "layer", "sent_id", "text"])
    return s[(s.layer == "statement") & ~s.doc_id.isin(EXCLUDE_DOCS)].copy()


def period_mask(dates: pd.Series, T: str) -> pd.Series:
    a, b, ex = PERIODS[T]; m = (dates >= a) & (dates <= b)
    if ex: m &= ~dates.str.startswith("2020")
    return m


# ----------------------------------------------------------------------------------------------
# statistics helpers
# ----------------------------------------------------------------------------------------------
def pmw(count, tokens) -> float:
    return float(count) / max(float(tokens), 1) * 1e6


def poisson_ci(count, tokens, alpha=0.05):
    """Exact Poisson 95% CI for a rate, returned per million words."""
    k = float(count)
    lo = 0.0 if k == 0 else stats.chi2.ppf(alpha / 2, 2 * k) / 2
    hi = stats.chi2.ppf(1 - alpha / 2, 2 * (k + 1)) / 2
    return lo / max(tokens, 1) * 1e6, hi / max(tokens, 1) * 1e6


def dispersion_dp(counts: np.ndarray, sizes: np.ndarray) -> float:
    """Gries (2008) DP: 0 = perfectly even, 1 = maximally clumped."""
    counts = np.asarray(counts, float); sizes = np.asarray(sizes, float)
    if counts.sum() == 0 or sizes.sum() == 0: return np.nan
    return float(0.5 * np.abs(counts / counts.sum() - sizes / sizes.sum()).sum())


def keyness(a, n1, b, n2):
    """Log-likelihood keyness of a word with freq a in corpus of size n1 vs freq b in corpus of size n2 (Rayson & Garside 2000);
    effect sizes: Hardie's log ratio (binary log of relative-frequency ratio, +0.5 smoothing) and %DIFF (Gabrielatos & Marchi 2011)."""
    a, b, n1, n2 = float(a), float(b), float(n1), float(n2)
    e1 = n1 * (a + b) / (n1 + n2); e2 = n2 * (a + b) / (n1 + n2)
    ll = 2 * ((a * math.log(a / e1) if a > 0 else 0) + (b * math.log(b / e2) if b > 0 else 0))
    r1, r2 = (a + 0.5) / n1, (b + 0.5) / n2
    log_ratio = math.log2(r1 / r2)
    pdiff = ((a / n1 - b / n2) / (b / n2) * 100) if b > 0 else np.inf
    p = 1 - stats.chi2.cdf(ll, 1)
    return dict(LL=round(ll, 2), p=p, log_ratio=round(log_ratio, 3), pct_diff=(round(pdiff, 1) if np.isfinite(pdiff) else np.inf),
                sign=("+" if a / n1 > b / n2 else "-"))


def bh(p):
    p = np.asarray(p, float); q = np.full_like(p, np.nan); ok = ~np.isnan(p)
    if ok.sum(): q[ok] = multipletests(p[ok], method="fdr_bh")[1]
    return q


def corr_pair(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); ok = ~(np.isnan(x) | np.isnan(y)); x, y = x[ok], y[ok]
    if len(x) < 8 or x.std() == 0 or y.std() == 0:
        return dict(n=int(len(x)), r=np.nan, p_r=np.nan, rho=np.nan, p_rho=np.nan)
    r, pr = stats.pearsonr(x, y); rho, prho = stats.spearmanr(x, y)
    return dict(n=int(len(x)), r=float(r), p_r=float(pr), rho=float(rho), p_rho=float(prho))


def hac_ols(y, X: pd.DataFrame, lags=4):
    """OLS with Newey-West HAC SE. Returns dict(coef, se, p, t, n, r2, adj_r2) or None."""
    Xc = sm.add_constant(X.astype(float), has_constant="add"); y = np.asarray(y, float)
    ok = ~np.isnan(Xc.values).any(axis=1) & ~np.isnan(y)
    if ok.sum() < max(12, Xc.shape[1] + 5): return None
    m = sm.OLS(y[ok], Xc[ok]).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return dict(coef=m.params.to_dict(), se=m.bse.to_dict(), p=m.pvalues.to_dict(), t=m.tvalues.to_dict(), n=int(ok.sum()), r2=float(m.rsquared), adj_r2=float(m.rsquared_adj))


def stars(p):
    return "" if p is None or np.isnan(p) else ("***" if p < .01 else "**" if p < .05 else "*" if p < .10 else "")


def mk_trend(x):
    import pymannkendall as mk
    x = np.asarray(x, float)
    if len(x) < 8 or np.nanstd(x) == 0: return None
    r = mk.original_test(x)
    return dict(trend=r.trend, p=float(r.p), tau=float(r.Tau), sen_slope=float(r.slope), n=int(len(x)))


def pelt_breaks(y, min_size=4, pen_scale=2.0):
    import ruptures as rpt
    y = np.asarray(y, float)
    if len(y) < 2 * min_size or y.std() == 0: return []
    z = (y - y.mean()) / y.std()
    bk = rpt.Pelt(model="l2", min_size=min_size, jump=1).fit(z.reshape(-1, 1)).predict(pen=pen_scale * math.log(len(y)))
    return [b for b in bk if b < len(y)]


def norm_sentence(s: str) -> str:
    s = str(s).lower(); s = re.sub(r"\d+([./-]\d+)*", "#", s); s = re.sub(r"[^a-z# ]+", " ", s); return re.sub(r"\s+", " ", s).strip()


def kwic(sentence: str, modal: str, width=70) -> str:
    s = re.sub(r"\s+", " ", str(sentence))
    m = re.search(r"\b" + re.escape(modal) + r"\b", s, flags=re.I)
    if not m: return s[:2 * width]
    a, b = m.start(), m.end()
    left = s[max(0, a - width):a]; right = s[b:b + width]
    return f"…{left}[{s[a:b]}]{right}…"


def modal_of_unit(u: str) -> str:
    return re.split(r"[+/]", str(u), 1)[0]


# ----------------------------------------------------------------------------------------------
# per-document series
# ----------------------------------------------------------------------------------------------
def doc_key_index(dl: pd.DataFrame, key_col: str) -> pd.DataFrame:
    g = dl.groupby(["doc_id", key_col]).agg(date=("date", "first"), tokens=("n_tokens", "sum")).reset_index()
    return g.rename(columns={key_col: "key"})


def unit_series(tk: pd.DataFrame, dl: pd.DataFrame, level: str, unit_col: str, min_tokens=MIN_TOKENS, extra_units=(), keep_all=True) -> pd.DataFrame:
    """Long table: doc_id, date, level, key, unit, count, tokens, six_total, per1k, pmw, share."""
    key_col = "layer" if level == "layer" else "genre"
    idx = doc_key_index(dl, key_col); out = []
    for key, sub in tk.groupby(key_col):
        docs_k = idx[idx.key == key].set_index("doc_id")
        cnt = sub.groupby(["doc_id", unit_col]).size().unstack(fill_value=0).reindex(docs_k.index, fill_value=0)
        total = cnt.sum(axis=1)
        keep = [u for u in cnt.columns if cnt[u].sum() >= min_tokens or u in extra_units]
        cnt = cnt[keep]
        if keep_all: cnt["ALL"] = total
        long = cnt.reset_index().melt(id_vars="doc_id", var_name="unit", value_name="count")
        long["date"] = long.doc_id.map(docs_k.date); long["tokens"] = long.doc_id.map(docs_k.tokens); long["six_total"] = long.doc_id.map(total)
        long["level"] = level; long["key"] = key; out.append(long)
    if not out:
        return pd.DataFrame(columns=["doc_id", "date", "level", "key", "unit", "count", "tokens", "six_total", "per1k", "pmw", "share"])
    df = pd.concat(out, ignore_index=True)
    df["per1k"] = df["count"] / df["tokens"].replace(0, np.nan) * 1000; df["pmw"] = df["per1k"] * 1000
    df["share"] = df["count"] / df["six_total"].replace(0, np.nan)
    return df


def save(df: pd.DataFrame, out: Path, name: str):
    (out / "tables").mkdir(parents=True, exist_ok=True); df.to_csv(out / "tables" / f"{name}.csv", index=False)


def jsonable(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, float) and np.isnan(o): return None
    return str(o)
