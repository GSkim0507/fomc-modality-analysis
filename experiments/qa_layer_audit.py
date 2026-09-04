"""
qa_layer_audit.py — Data-integrity audit behind the 2026-09-04 replan (docs/08).

Two questions the meeting raised about the v2 corpus:
  (1) Press conferences: how many "Fed" modal tokens are actually journalist / moderator speech?
  (2) Minutes: which discourse layer (staff / participants / committee / vote / boilerplate) does each
      modal token come from, and where does the be+appropriate idiom sit by modal?

Runs on the *existing* v2 tables (results/tables/modal_tokens.csv) by re-cleaning the raw JSON with the
same clean() as 00_build_corpus.py and locating each modal sentence in the cleaned text.  It does not
change any v2 output; Phase 10 replaces this with a proper layer-aware corpus build.

Outputs (2014-01-01 onward):
  results/tables/QA1_pressconf_modal_by_role.csv      modal x {chair, journalist, moderator, pre, UNMATCHED}
  results/tables/QA2_minutes_modal_by_section.csv     modal x section
  results/tables/QA3_minutes_be_appropriate_by_section.csv
  results/tables/QA4_minutes_reported_share.csv       reported-speech share, will/would x section
"""
from __future__ import annotations
import json, re, glob, sys
from collections import Counter
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
from importlib import import_module
bc = import_module("00_build_corpus")
TAB = ROOT / "results" / "tables"
START = "2014-01-01"

SPEAKER_RE = re.compile(r"(?m)^\s*([A-Z][A-Z .'’\-]{3,40})\.\s")
MODERATORS = ("MICHELLE SMITH",)
SECTIONS = [("Developments in Financial Markets", "staff_desk"),
            ("Staff Review of the Economic Situation", "staff"),
            ("Staff Review of the Financial Situation", "staff"),
            ("Staff Economic Outlook", "staff"),
            ("Participants' Views", "participants"),
            ("Committee Policy Action", "committee"),
            ("Voting for", "vote")]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def norm_index_map(t: str) -> list[int]:
    """Map raw-text char index -> index in whitespace-normalised text."""
    out, prev_space, ni = [], False, 0
    for ch in t:
        if ch.isspace():
            if not prev_space and ni > 0:
                ni += 1
            prev_space = True
        else:
            prev_space = False
            ni += 1
        out.append(ni)
    return out


def role_of(name: str) -> str:
    if name.startswith("CHAIR"):
        return "chair"
    if any(m in name for m in MODERATORS):
        return "moderator"
    return "journalist"


def locate(tn: str, sentence: str, marks: list[tuple[int, str]], default: str) -> str:
    key = norm(str(sentence))[:70]
    j = tn.find(key)
    if j < 0:
        return "UNMATCHED"
    label = default
    for pos, lab in marks:
        if pos <= j:
            label = lab
        else:
            break
    return label


def main():
    m = pd.read_csv(TAB / "modal_tokens.csv", low_memory=False)
    m = m[m.date >= START]

    # ---- press conferences ----
    rows, turns = [], Counter()
    for p in sorted(glob.glob(str(ROOT / "FOMC_corpus" / "transcripts" / "*.json"))):
        r = json.loads(Path(p).read_text())
        if r["date"] < START:
            continue
        t = bc.clean(r["text"]); tn = norm(t); imap = norm_index_map(t)
        marks = [(imap[mm.start()], role_of(mm.group(1).strip())) for mm in SPEAKER_RE.finditer(t)]
        for _, rl in marks:
            turns[rl] += 1
        sub = m[(m.doc_type == "press_conf") & (m.doc_id == r["doc_id"])]
        for _, row in sub.iterrows():
            rows.append(dict(doc_id=r["doc_id"], modal=row.modal, predicate=row.predicate,
                             role=locate(tn, row.sentence, marks, "pre")))
    pc = pd.DataFrame(rows)
    ct = pd.crosstab(pc.modal, pc.role)
    ct["journalist_share"] = (ct.get("journalist", 0) / ct.sum(axis=1)).round(3)
    ct.to_csv(TAB / "QA1_pressconf_modal_by_role.csv")
    print("press_conf turns:", dict(turns)); print(ct)

    # ---- minutes ----
    rows = []
    for p in sorted(glob.glob(str(ROOT / "FOMC_corpus" / "minutes" / "*.json"))):
        r = json.loads(Path(p).read_text())
        if r["date"] < START:
            continue
        tn = norm(bc.clean(r["text"]))
        marks = sorted((mm.start(), lab) for kw, lab in SECTIONS for mm in re.finditer(re.escape(kw), tn))
        sub = m[(m.doc_type == "minutes") & (m.doc_id == r["doc_id"])]
        for _, row in sub.iterrows():
            rows.append(dict(doc_id=r["doc_id"], modal=row.modal, predicate=row.predicate,
                             reported=row.reported, section=locate(tn, row.sentence, marks, "front_matter")))
    mn = pd.DataFrame(rows)
    pd.crosstab(mn.modal, mn.section).to_csv(TAB / "QA2_minutes_modal_by_section.csv")
    ba = mn[mn.predicate == "be+appropriate"]
    pd.crosstab(ba.modal, ba.section).to_csv(TAB / "QA3_minutes_be_appropriate_by_section.csv")
    rep = mn[mn.modal.isin(["will", "would"])].groupby(["modal", "section"]).reported.mean().round(3).unstack()
    rep.to_csv(TAB / "QA4_minutes_reported_share.csv")
    print(pd.crosstab(mn.modal, mn.section)); print(pd.crosstab(ba.modal, ba.section)); print(rep)


if __name__ == "__main__":
    main()
