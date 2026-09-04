"""
common_v3.py — Shared definitions for the v3 (layer-aware) scenario experiments.

Layers (corpus_sentences_v3.layer):
  statement, statement_vote,
  min_front_matter, min_staff_desk, min_staff, min_participants, min_committee, min_statement_quote,
  min_directive_quote, min_vote, min_special, min_sep, min_boilerplate,
  pc_chair, pc_journalist, pc_moderator, pc_pre,
  speech_chair

Scenario axes (docs/08 §3.3):
  S  corpus definition   S1..S6 (see SCENARIOS)
  U  analysis unit       U1 modal | U2 modal+predicate | U3 modal+verb class
  T  period              T1 2014-2026 | T2 excl. 2020 | T3 2010-2026     (variant columns inside each block)
  N  normalisation       N1 per 1k tokens | N2 share of six modals | N3 count per document

Normalisation policy (docs/08 §3.2 step 10.5): N1 is the default for layer comparison and macro correlation;
N2 for compositional change (the staircase); N3 only for statements, where document length is itself an editing outcome.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "results" / "tables"
SCEN = ROOT / "results" / "scenarios"; SCEN.mkdir(parents=True, exist_ok=True)

_spec = importlib.util.spec_from_file_location("common_v2", ROOT / "experiments" / "common.py")
common_v2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(common_v2)
SIX = common_v2.SIX; EVENTS = common_v2.EVENTS; PHASES = common_v2.PHASES; EXCLUDE_DOCS = common_v2.EXCLUDE_DOCS
verb_class = common_v2.verb_class; refine_subj_type = common_v2.refine_subj_type

MINUTES_SUBSTANTIVE = ["min_staff_desk", "min_staff", "min_participants", "min_committee", "min_special"]
MINUTES_ALL = MINUTES_SUBSTANTIVE + ["min_front_matter", "min_statement_quote", "min_directive_quote", "min_vote",
                                     "min_sep", "min_boilerplate"]
PC_ALL = ["pc_chair", "pc_journalist", "pc_moderator", "pc_pre"]

SCENARIOS = {
    "S1": dict(name="statement only", layers=["statement"],
               note="세미나 원안. 의사록 제외."),
    "S2": dict(name="statement + minutes committee layer", layers=["statement", "min_committee"],
               note="성명서의 '확장판': 의사록 중 위원회 정책조치 서술만(인용된 성명서·지침 제외)."),
    "S3": dict(name="statement + minutes (all substantive layers)", layers=["statement"] + MINUTES_SUBSTANTIVE,
               note="의사록 스태프·참가자·위원회·특별 섹션을 귀속 라벨과 함께 포함."),
    "S4": dict(name="4 genres, journalists removed, attribution labels", layers=["statement"] + MINUTES_SUBSTANTIVE + ["pc_chair", "speech_chair"],
               note="권장안. 기자·진행자 발화 제거, 의사록 규정문·인용문 제거."),
    "S5": dict(name="minutes only (substantive layers)", layers=MINUTES_SUBSTANTIVE,
               note="진단용: 의사록만으로 무엇이 보이는가."),
    "S6": dict(name="unfiltered 4 genres (v2-like)", layers=["statement", "statement_vote"] + MINUTES_ALL + PC_ALL + ["speech_chair"],
               note="비교용: 기자 발화·규정문·인용 성명서를 제거하지 않은 v2 방식."),
}
UNITS = {"U1": "modal", "U2": "modal + predicate", "U3": "modal + verb class"}
PERIODS = {"T1": ("2014-01-01", "2026-12-31", False), "T2": ("2014-01-01", "2026-12-31", True), "T3": ("2010-01-01", "2026-12-31", False),
           "H1": ("2014-01-01", "2019-12-31", False), "H2": ("2021-01-01", "2026-12-31", False)}   # halves: sign-consistency check
MAIN_PERIODS = ("T1", "T2", "T3")
NORMS = {"N1": "per 1,000 tokens", "N2": "share of six modals", "N3": "count per document"}

# genre of a layer (for pooled per-document series)
def genre_of(layer: str) -> str:
    if layer.startswith("statement"): return "statement"
    if layer.startswith("min_"): return "minutes"
    if layer.startswith("pc_"): return "press_conf"
    return "speech"

LAYER_LABEL = {
    "statement": "Statement", "statement_vote": "Statement (vote line)",
    "min_front_matter": "Minutes: front matter", "min_staff_desk": "Minutes: Desk/markets (staff)",
    "min_staff": "Minutes: staff review & outlook", "min_participants": "Minutes: participants' views",
    "min_committee": "Minutes: Committee policy action", "min_statement_quote": "Minutes: quoted statement",
    "min_directive_quote": "Minutes: quoted directive", "min_vote": "Minutes: vote & post-vote",
    "min_special": "Minutes: special topics", "min_sep": "Minutes: SEP addendum", "min_boilerplate": "Minutes: authorizations/boilerplate",
    "pc_chair": "Press conf.: Chair", "pc_journalist": "Press conf.: journalists", "pc_moderator": "Press conf.: moderator",
    "pc_pre": "Press conf.: pre-marker", "speech_chair": "Chair speech",
}


def load_tokens_v3() -> pd.DataFrame:
    df = pd.read_csv(TAB / "modal_tokens_v3.csv", low_memory=False)
    df["subj_type"] = [refine_subj_type(a, b) for a, b in zip(df["subj_lemma"], df["subj_text"])]
    df = df[~df["doc_id"].isin(EXCLUDE_DOCS)]
    df = df.assign(year=df["date"].str[:4].astype(int), genre=df["layer"].map(genre_of))
    df["vclass"] = df["predicate"].map(lambda p: ("copular_" + p.split("+", 1)[0]) if False else None)
    df["vclass"] = [("copular_adj" if (str(bt) == "adjectival") else "copular_nom" if str(bt) == "nominal"
                     else "copular_prep" if str(bt) == "prepositional" else "copular_adv" if str(bt) == "adverbial"
                     else verb_class(str(hv))) for bt, hv in zip(df["be_comp_type"], df["head_verb"])]
    return df


def load_docs_v3() -> pd.DataFrame:
    d = pd.read_csv(TAB / "corpus_docs_v3.csv")
    d = d[~d["doc_id"].isin(EXCLUDE_DOCS)]
    return d.assign(year=d["date"].str[:4].astype(int), genre=d["layer"].map(genre_of))


def load_macro() -> pd.DataFrame:
    m = pd.read_csv(TAB / "macro_by_doc.csv")
    return m.drop(columns=[c for c in ("doc_type", "date") if c in m.columns])


def unit_key(df: pd.DataFrame, U: str) -> pd.Series:
    if U == "U1": return df["modal"]
    if U == "U2": return df["modal"] + "+" + df["predicate"].astype(str)
    return df["modal"] + "/" + df["vclass"].astype(str)


def period_mask(dates: pd.Series, T: str) -> pd.Series:
    a, b, ex2020 = PERIODS[T]
    m = (dates >= a) & (dates <= b)
    if ex2020:
        m &= ~dates.str.startswith("2020")
    return m
