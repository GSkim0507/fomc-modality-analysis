"""
POS tagging pipeline for the FOMC corpus.

For every document:
  - Run spaCy en_core_web_sm
  - Extract modal verbs (MD tag) with surface, lemma, head verb, sentence context
  - Extract epistemic adverbs/adjectives (closed list, lemma match)
  - Record token/sentence counts and a full POS distribution
  - Optionally extract N-gram modal phrases (1-4-gram around each modal)

Outputs:
  analysis/pos_features/<doc_id>.json   per-document feature record
  analysis/pos_summary.csv              flat aggregate (one row per doc)
  analysis/modal_instances.csv          one row per modal occurrence (for downstream stats)
"""
from __future__ import annotations
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

import spacy

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
POS_DIR = ANALYSIS / "pos_features"
POS_DIR.mkdir(parents=True, exist_ok=True)

# Epistemic adverbs/adjectives — closed list grounded in:
#   Biber et al. (1999) Longman Grammar; Hyland (1998) Hedging in Scientific Discourse.
# Stored as (lemma, category). Surface match falls back to lemma.
EPISTEMIC_LEX = {
    # Hedges (lower the certainty of the proposition)
    "likely":     ("hedge_mid", "adj/adv"),
    "possibly":   ("hedge_low", "adv"),
    "possible":   ("hedge_low", "adj"),
    "perhaps":    ("hedge_low", "adv"),
    "probably":   ("hedge_mid", "adv"),
    "probable":   ("hedge_mid", "adj"),
    "apparently": ("hedge_mid", "adv"),
    "presumably": ("hedge_mid", "adv"),
    "seemingly":  ("hedge_low", "adv"),
    "potentially":("hedge_low", "adv"),
    "potential":  ("hedge_low", "adj"),
    "uncertain":  ("hedge_low", "adj"),
    "unlikely":   ("hedge_neg", "adj/adv"),
    # Boosters (raise the certainty)
    "certainly":  ("booster_high", "adv"),
    "certain":    ("booster_high", "adj"),
    "clearly":    ("booster_high", "adv"),
    "definitely": ("booster_high", "adv"),
    "evidently":  ("booster_mid", "adv"),
    "obvious":    ("booster_high", "adj"),
    "obviously":  ("booster_high", "adv"),
    "undoubtedly":("booster_high", "adv"),
    # Anticipation verbs (mid certainty epistemic stance)
    "expect":     ("anticipation", "verb"),
    "anticipate": ("anticipation", "verb"),
    "project":    ("anticipation", "verb"),
    "forecast":   ("anticipation", "verb"),
    "foresee":    ("anticipation", "verb"),
    # Communication of judgment (commitment level)
    "judge":      ("judgment", "verb"),
    "assess":     ("judgment", "verb"),
    "believe":    ("judgment", "verb"),
}

DOC_TYPES_DIRS = ["statements", "minutes", "transcripts", "speeches"]

def iter_docs():
    for sub in DOC_TYPES_DIRS:
        for p in sorted((ROOT / sub).glob("*.json")):
            yield p

def process_doc(nlp, doc_path: Path) -> dict:
    rec = json.loads(doc_path.read_text())
    text = rec["text"]
    # spaCy default max_length is 1_000_000 chars; longest minutes ~120k so fine
    doc = nlp(text)

    pos_counts = Counter(t.tag_ for t in doc if not t.is_space)
    n_tokens = sum(1 for t in doc if not t.is_space and not t.is_punct)
    n_sents = sum(1 for _ in doc.sents)

    modals = []
    epistemics = []
    for sent in doc.sents:
        sent_text = sent.text.strip().replace("\n", " ")
        for t in sent:
            if t.tag_ == "MD":
                # head verb (the verb the modal supports)
                head = t.head
                # find the lexical verb if head is also an aux
                lex = head
                while lex.tag_ in {"MD"} and lex != lex.head:
                    lex = lex.head
                modals.append({
                    "surface": t.text.lower(),
                    "lemma": t.lemma_.lower(),
                    "sent_idx": sent.start,
                    "head_verb_surface": lex.text.lower(),
                    "head_verb_lemma": lex.lemma_.lower(),
                    "left_3": " ".join(x.text for x in doc[max(0, t.i - 3): t.i]),
                    "right_3": " ".join(x.text for x in doc[t.i + 1: t.i + 4]),
                    "sentence": sent_text[:400],
                })
            lem = t.lemma_.lower()
            if lem in EPISTEMIC_LEX and t.pos_ in {"ADV", "ADJ", "VERB"}:
                cat, kind = EPISTEMIC_LEX[lem]
                epistemics.append({
                    "surface": t.text.lower(),
                    "lemma": lem,
                    "pos": t.pos_,
                    "category": cat,
                    "kind": kind,
                    "sentence": sent_text[:400],
                })

    modal_lemma_counts = Counter(m["lemma"] for m in modals)
    epistemic_lemma_counts = Counter(e["lemma"] for e in epistemics)

    out = {
        "doc_id": rec["doc_id"],
        "doc_type": rec["doc_type"],
        "date": rec["date"],
        "chair": rec.get("chair"),
        "n_tokens": n_tokens,
        "n_sents": n_sents,
        "pos_counts": dict(pos_counts),
        "modal_count": len(modals),
        "modal_lemma_counts": dict(modal_lemma_counts),
        "modals_per_1000": round(1000 * len(modals) / max(1, n_tokens), 3),
        "epistemic_count": len(epistemics),
        "epistemic_lemma_counts": dict(epistemic_lemma_counts),
        "epistemics_per_1000": round(1000 * len(epistemics) / max(1, n_tokens), 3),
        "modal_instances": modals,
        "epistemic_instances": epistemics,
    }
    return out

def main():
    print("Loading spaCy...", file=sys.stderr)
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    paths = list(iter_docs())
    print(f"Documents to process: {len(paths)}", file=sys.stderr)

    summary_rows = []
    modal_rows = []

    t0 = time.time()
    for i, p in enumerate(paths, 1):
        try:
            rec = process_doc(nlp, p)
        except Exception as e:
            print(f"  ERROR {p.name}: {e}", file=sys.stderr)
            continue
        (POS_DIR / f"{rec['doc_id']}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))

        summary_rows.append({
            "doc_id": rec["doc_id"],
            "doc_type": rec["doc_type"],
            "date": rec["date"],
            "chair": rec["chair"],
            "n_tokens": rec["n_tokens"],
            "n_sents": rec["n_sents"],
            "modal_count": rec["modal_count"],
            "modals_per_1000": rec["modals_per_1000"],
            "epistemic_count": rec["epistemic_count"],
            "epistemics_per_1000": rec["epistemics_per_1000"],
            **{f"mod_{k}": v for k, v in rec["modal_lemma_counts"].items()},
        })
        for m in rec["modal_instances"]:
            modal_rows.append({
                "doc_id": rec["doc_id"],
                "doc_type": rec["doc_type"],
                "date": rec["date"],
                "chair": rec["chair"],
                "lemma": m["lemma"],
                "surface": m["surface"],
                "head_verb_lemma": m["head_verb_lemma"],
                "left_3": m["left_3"],
                "right_3": m["right_3"],
                "sentence": m["sentence"],
            })

        if i % 25 == 0 or i == len(paths):
            elapsed = time.time() - t0
            print(f"  [{i}/{len(paths)}] {elapsed:5.1f}s  {p.name}", file=sys.stderr)

    # Write summary CSV (union of modal columns)
    all_modal_cols = sorted({k for row in summary_rows for k in row if k.startswith("mod_")})
    base_cols = ["doc_id","doc_type","date","chair","n_tokens","n_sents",
                 "modal_count","modals_per_1000","epistemic_count","epistemics_per_1000"]
    cols = base_cols + all_modal_cols
    with (ANALYSIS / "pos_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in summary_rows:
            w.writerow({c: row.get(c, 0) for c in cols})

    with (ANALYSIS / "modal_instances.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(modal_rows[0].keys()))
        w.writeheader()
        w.writerows(modal_rows)

    print(f"\nDONE in {time.time()-t0:.1f}s", file=sys.stderr)
    print(f"  pos_summary.csv     ({len(summary_rows)} rows)", file=sys.stderr)
    print(f"  modal_instances.csv ({len(modal_rows)} rows)", file=sys.stderr)
    print(f"  pos_features/*.json ({len(summary_rows)} files)", file=sys.stderr)

if __name__ == "__main__":
    main()
