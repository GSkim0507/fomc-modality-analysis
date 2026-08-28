"""Shared constants/helpers for the modal-verb experiments."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "results" / "tables"
FIG = ROOT / "results" / "figures"
TAB.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)

SIX = ["will", "would", "could", "can", "should", "may"]
NINE = SIX + ["might", "must", "shall"]
GENRES = ["statement", "minutes", "press_conf", "speech"]
GENRE_LABEL = {"statement": "Statement", "minutes": "Minutes",
               "press_conf": "Press conference", "speech": "Chair speech"}
START, END = "2014-01-01", "2026-12-31"

# Policy / framework events used to annotate time-series figures
EVENTS = [
    ("2014-10-29", "QE3 ends"),
    ("2015-12-16", "First hike (liftoff)"),
    ("2017-06-14", "Normalization addendum"),
    ("2017-10-01", "Balance-sheet runoff"),
    ("2018-02-05", "Powell chair"),
    ("2019-07-31", "Mid-cycle cut"),
    ("2020-03-15", "Pandemic ZLB"),
    ("2020-08-27", "New framework"),
    ("2022-03-16", "Hiking cycle begins"),
    ("2023-07-26", "Last hike"),
    ("2024-09-18", "Cutting cycle begins"),
    ("2025-08-22", "Framework review 2025"),
]

# Coarse policy phases (statement dates)
PHASES = [
    ("2014-01-01", "2015-12-15", "ZLB/taper"),
    ("2015-12-16", "2019-06-30", "Hiking I / normalization"),
    ("2019-07-01", "2020-02-29", "Mid-cycle cuts"),
    ("2020-03-01", "2022-03-15", "Pandemic ZLB"),
    ("2022-03-16", "2023-07-31", "Hiking II"),
    ("2023-08-01", "2024-09-17", "Hold at peak"),
    ("2024-09-18", "2026-12-31", "Cuts / post-peak"),
]

def phase_of(date: str) -> str:
    for a, b, name in PHASES:
        if a <= date <= b:
            return name
    return "pre-2014"

def load_modals(window=True, six=True) -> pd.DataFrame:
    df = pd.read_csv(TAB / "modal_tokens.csv", low_memory=False)
    if window:
        df = df[(df["date"] >= START) & (df["date"] <= END)]
    if six:
        df = df[df["modal"].isin(SIX)]
    df = df.assign(year=df["date"].str[:4].astype(int))
    return df

def load_docs(window=True) -> pd.DataFrame:
    d = pd.read_csv(TAB / "corpus_docs.csv")
    if window:
        d = d[(d["date"] >= START) & (d["date"] <= END)]
    return d.assign(year=d["date"].str[:4].astype(int))

# Verb semantic classes (Biber et al. 1999, ch. 5.2; extended with a policy-action class)
VERB_CLASS = {}
def _add(cls, words):
    for w in words.split():
        VERB_CLASS[w] = cls
_add("policy_action", "raise lower cut reduce increase decrease tighten ease adjust hike lift normalize "
     "purchase buy sell reinvest roll taper slow pause hold keep maintain continue begin start initiate end "
     "conclude implement conduct set target reach achieve restore return move modify change revise "
     "recalibrate remove provide supply lend accommodate support stabilize expand shrink unwind "
     "reinvesting reducing")
_add("mental", "think believe judge expect anticipate assess evaluate consider view see regard know "
     "understand recognize feel want prefer decide determine hope worry doubt assume guess suppose "
     "remember forget learn interpret weigh monitor watch look review examine analyze estimate project "
     "forecast foresee imagine wonder appreciate care mind intend plan mean")
_add("communication", "say tell speak talk note indicate state emphasize stress suggest argue mention "
     "announce report describe explain discuss communicate signal comment ask answer call refer "
     "point add remark reiterate highlight underscore acknowledge affirm reaffirm advise warn "
     "characterize cite express respond reply write publish release show demonstrate")
_add("activity", "do make take give go come get use work act help serve try put bring run play "
     "carry deal handle manage operate meet allow enable let leave bear pay spend save invest hire "
     "produce build create develop apply pursue address respond react step wait proceed prepare "
     "act pursue undertake adopt engage participate)")
_add("causative", "cause lead result affect impact influence impede hamper restrain boost push drive "
     "force generate induce prompt trigger contribute weigh damp dampen weaken strengthen "
     "undermine promote foster facilitate encourage discourage prevent limit constrain pose "
     "threaten warrant justify require necessitate call")
_add("occurrence", "happen occur emerge arise develop rise fall decline grow increase improve worsen "
     "deteriorate accelerate decelerate moderate pick slow ease firm soften stabilize recover "
     "rebound persist remain stay become turn prove evolve unfold change vary fluctuate widen narrow "
     "converge drift edge climb drop surge spike jump")
_add("existence", "be exist have seem appear tend stand lie represent constitute involve include "
     "contain reflect depend rely relate correspond mean matter differ resemble")
_add("aspectual", "begin start continue keep stop cease finish complete end resume proceed")
# NOTE: 'continue/keep/maintain/hold' are in policy_action deliberately for FOMC usage; adjust in analysis if needed.

def verb_class(v: str) -> str:
    return VERB_CLASS.get(v, "other")

SUBJ_ORDER = ["committee", "fed", "we_I", "person", "it_there_rel", "econ", "risks", "other", "none"]
