"""
Extract concrete misannotation cases from the corpus to support the
Limitations section with observed evidence (not just claims).

We document five failure modes:

  L1.  Contraction tokens ('ll, 'd, 's) tagged as MD
  L2.  Em-dash-joined compound tokens (e.g., 'constraints—would') as a single MD
  L3.  Deontic / future-tense 'will' counted as epistemic commitment
  L4.  Conditional 'would' in reported speech counted as proposition modality
  L5.  Modal-like uses outside an MD tag spaCy missed entirely

For each failure mode we collect 3-5 attested examples from the corpus along
with their source doc and surrounding context. The evidence is written to
analysis/limitations_examples.json and visualized in figures/20_mistagging.png.
"""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"
POS_DIR = ANALYSIS / "pos_features"

# Lemmas commonly mistagged
CONTRACTION_LEMMAS = {"'ll", "'d", "'s", "’ll", "’d", "’s"}
EM_DASH = "—"   # — (U+2014)

def iter_pos_records():
    for p in sorted(POS_DIR.glob("*.json")):
        yield json.loads(p.read_text())

def collect_cases():
    """
    Walk every modal instance recorded by the POS pipeline.
    Bin into the five failure-mode buckets defined above.
    """
    cases = {
        "L1_contractions": [],
        "L2_em_dash_compounds": [],
        "L3_future_will": [],
        "L4_reported_would": [],
        "L5_modal_lemma_counts": Counter(),
    }
    legitimate_modals = {"will","would","could","can","may","might","should","must",
                         "shall","ought","need"}

    for rec in iter_pos_records():
        for inst in rec["modal_instances"]:
            lemma = inst["lemma"]
            surface = inst["surface"]
            sent = inst["sentence"]
            # L1: contraction tokens
            if lemma in CONTRACTION_LEMMAS or surface in CONTRACTION_LEMMAS:
                if len(cases["L1_contractions"]) < 12:
                    cases["L1_contractions"].append({
                        "doc_id": rec["doc_id"], "doc_type": rec["doc_type"],
                        "surface": surface, "lemma": lemma,
                        "sentence": sent[:280],
                    })
                continue
            # L2: em-dash compound tokens — lemma contains the em-dash literal
            if EM_DASH in lemma or "â\x80\x94" in lemma:
                if len(cases["L2_em_dash_compounds"]) < 12:
                    cases["L2_em_dash_compounds"].append({
                        "doc_id": rec["doc_id"], "doc_type": rec["doc_type"],
                        "surface": surface, "lemma": lemma,
                        "sentence": sent[:280],
                    })
                continue
            # L3: "will" with a clearly *temporal* head (release, publish, hold)
            #     — these are future-tense uses, not strong commitment.
            #     We use a small heuristic: head_verb in a "schedule" verb set.
            FUTURE_HEAD_VERBS = {"release","publish","hold","convene","meet","update",
                                  "announce","report","reconvene","occur","start","begin"}
            if lemma == "will" and inst.get("head_verb_lemma") in FUTURE_HEAD_VERBS:
                if len(cases["L3_future_will"]) < 12:
                    cases["L3_future_will"].append({
                        "doc_id": rec["doc_id"], "doc_type": rec["doc_type"],
                        "head_verb": inst["head_verb_lemma"],
                        "left_3": inst["left_3"], "surface": surface,
                        "sentence": sent[:280],
                    })
                continue
            # L4: 'would' in clearly reported-speech contexts
            #     — heuristic: 'said', 'noted', 'reported', 'argued' to the left
            REPORTED_VERBS = {"said","noted","reported","argued","added","observed",
                              "suggested","expected","emphasized","commented","remarked"}
            if lemma == "would":
                left_words = (inst.get("left_3") or "").lower().split()
                if any(w in REPORTED_VERBS for w in left_words):
                    if len(cases["L4_reported_would"]) < 12:
                        cases["L4_reported_would"].append({
                            "doc_id": rec["doc_id"], "doc_type": rec["doc_type"],
                            "left_3": inst["left_3"], "surface": surface,
                            "sentence": sent[:280],
                        })
                    continue
            # L5: tally counts
            if lemma in legitimate_modals:
                cases["L5_modal_lemma_counts"][lemma] += 1
            else:
                cases["L5_modal_lemma_counts"]["__other__"] += 1

    return cases

def write_json(cases, out_path: Path):
    serializable = {
        k: (dict(v) if isinstance(v, Counter) else v)
        for k, v in cases.items()
    }
    out_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False))

def render_figure(cases, out_path: Path):
    """One-page evidence figure with example sentences and counts."""
    fig = plt.figure(figsize=(13.5, 9.5))
    fig.suptitle("Observed mis-annotation cases in spaCy MD tagging of the FOMC corpus",
                 fontsize=14, fontweight="bold")

    # Layout: 5 row panels, 2 columns (counts left, example right)
    panels = [
        ("L1.  Contractions tagged as MD",
         "spaCy's tokenizer splits *I'll be*, *we'd like* into [I, 'll, be].\n"
         "The clitic 'll inherits the MD tag of its parent will/would, so it is\n"
         "counted twice in modal frequency tables.",
         cases["L1_contractions"]),
        ("L2.  Em-dash-joined compounds taken as a single token",
         "When source PDFs use em-dash without surrounding whitespace\n"
         "(e.g., 'constraints—would'), the entire compound is tagged MD\n"
         "and emerges in our pos_summary.csv as a spurious column.",
         cases["L2_em_dash_compounds"]),
        ("L3.  Future-tense 'will' counted as epistemic commitment",
         "'will' in temporal scheduling (will release, will hold, will publish)\n"
         "is future-time grammatical marking, not the commissive epistemic\n"
         "modality our MSI scale assumes. Frequency-based methods cannot\n"
         "disambiguate.",
         cases["L3_future_will"]),
        ("L4.  Reported-speech 'would' counted toward proposition modality",
         "'would' inside reported speech (participants said ... would) belongs\n"
         "to the speech-act layer of the speaker being reported, not to the\n"
         "Committee's own stance — but our MSI treats it identically.",
         cases["L4_reported_would"]),
    ]

    n = len(panels)
    for i, (title, explainer, examples) in enumerate(panels):
        ax = fig.add_axes([0.04, 0.92 - (i+1)*0.21, 0.92, 0.18])
        ax.axis("off")
        # Title bar
        ax.add_patch(FancyBboxPatch((0, 0.78), 1.0, 0.22,
                     boxstyle="round,pad=0.01",
                     linewidth=0.6, edgecolor="#222",
                     facecolor="#e8eef5"))
        ax.text(0.01, 0.89, title, fontsize=12, fontweight="bold",
                color="#1f3a5f", va="center")
        # Explainer
        ax.text(0.01, 0.62, explainer, fontsize=9.5, color="#333", va="top")
        # Examples
        ex_text = ""
        for j, ex in enumerate(examples[:3], 1):
            snippet = ex.get("sentence", "").replace("\n", " ")
            ex_text += f"   • [{ex.get('doc_id','?')}]  {snippet[:170]}…\n"
        if not ex_text:
            ex_text = "   (no instances detected — heuristic too narrow)"
        ax.text(0.41, 0.62, ex_text, fontsize=8.5, color="#222",
                va="top", family="monospace")

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  figure saved -> {out_path}")

def main():
    print("Walking POS feature files ...")
    cases = collect_cases()
    print(f"  L1 contractions: {len(cases['L1_contractions'])}")
    print(f"  L2 em-dash compounds: {len(cases['L2_em_dash_compounds'])}")
    print(f"  L3 future-tense 'will' cases: {len(cases['L3_future_will'])}")
    print(f"  L4 reported 'would' cases: {len(cases['L4_reported_would'])}")
    write_json(cases, ANALYSIS / "limitations_examples.json")
    render_figure(cases, FIG / "20_mistagging_evidence.png")

    # ---- Summary stats: how prevalent are these errors? ----
    print("\nPrevalence summary (raw counts across the entire pos_features corpus):")
    total_modals = sum(cases["L5_modal_lemma_counts"].values())
    print(f"  total modal-tagged instances: {total_modals:,}")
    other = cases['L5_modal_lemma_counts']['__other__']
    print(f"  non-canonical lemmas (incl. contractions, em-dash compounds): {other:,}  "
          f"({100*other/total_modals:.2f}% of all MD)")

if __name__ == "__main__":
    main()
