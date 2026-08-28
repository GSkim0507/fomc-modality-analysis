"""
Rule-based Modality Strength Index (MSI).

Each modal/epistemic lemma is assigned an epistemic-certainty score in [0, 1]:
  1.0 = full speaker commitment to the proposition
  0.0 = explicit non-commitment / negation of likelihood

Modal verb anchors (drawn from Coates 1983; Palmer 1990; Biber et al. 1999):
  Strong commitment  (will, would, must)        = 1.0
  Mid commitment     (should, shall, ought)     = 0.7
  Possibility        (can, could)               = 0.4
  Weak possibility   (may, might)               = 0.3
  Hortative          (let, need)                = 0.5
Epistemic adverbs/adjectives (Hyland 1998 hedging scale):
  booster_high (certainly/clearly/definitely)   = 1.0
  booster_mid  (evidently)                      = 0.7
  hedge_mid    (likely/probably/apparently)     = 0.5
  hedge_low    (possibly/perhaps/potentially)   = 0.3
  hedge_neg    (unlikely)                       = 0.1
  anticipation (expect/anticipate/project)      = 0.7
  judgment     (judge/assess/believe)           = 0.5

Per document we report:
  msi_modal_density      = sum(modal scores) / tokens * 1000
  msi_epistemic_density  = sum(epistemic scores) / tokens * 1000
  msi_avg_modal_strength = mean(modal scores)        # intensity (per-modal certainty)
  msi_total_density      = (modal + epistemic densities)
  msi_signed             = (boosters + strong-modal) - (hedges + weak-modal) per 1000 tokens
                           — positive = hawkish/committed, negative = dovish/hedged

Outputs:
  analysis/modality_index.csv     per-doc scores joined with date/chair/doc_type
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"

MODAL_STRENGTH = {
    "will": 1.0, "would": 1.0, "must": 1.0,
    "should": 0.7, "shall": 0.7, "ought": 0.7,
    "can": 0.4, "could": 0.4,
    "may": 0.3, "might": 0.3,
    "need": 0.5,
}
EPISTEMIC_STRENGTH = {
    # cat -> score
    "booster_high": 1.0,
    "booster_mid":  0.7,
    "hedge_mid":    0.5,
    "hedge_low":    0.3,
    "hedge_neg":    0.1,
    "anticipation": 0.7,
    "judgment":     0.5,
}
# Categorize modals for the signed index (+ / -)
MODAL_POLARITY = {
    "will": +1, "would": +1, "must": +1, "shall": +1, "ought": +1, "should": +1,
    "can": 0, "could": 0, "need": 0,
    "may": -1, "might": -1,
}
EPI_POLARITY = {
    "booster_high": +1, "booster_mid": +1,
    "anticipation": +1, "judgment": 0,
    "hedge_mid": -1, "hedge_low": -1, "hedge_neg": -1,
}

POS_DIR = ANALYSIS / "pos_features"

def score_doc(rec: dict) -> dict:
    n_tokens = max(1, rec["n_tokens"])
    modal_scores, modal_polar = [], []
    for inst in rec["modal_instances"]:
        s = MODAL_STRENGTH.get(inst["lemma"])
        if s is None:
            continue
        modal_scores.append(s)
        modal_polar.append(MODAL_POLARITY.get(inst["lemma"], 0))

    epi_scores, epi_polar = [], []
    for inst in rec["epistemic_instances"]:
        cat = inst["category"]
        s = EPISTEMIC_STRENGTH.get(cat)
        if s is None:
            continue
        epi_scores.append(s)
        epi_polar.append(EPI_POLARITY.get(cat, 0))

    modal_sum = sum(modal_scores)
    epi_sum = sum(epi_scores)
    signed_sum = sum(modal_polar) + sum(epi_polar)

    return {
        "doc_id": rec["doc_id"],
        "doc_type": rec["doc_type"],
        "date": rec["date"],
        "chair": rec["chair"],
        "n_tokens": rec["n_tokens"],
        "modal_count": len(modal_scores),
        "epistemic_count": len(epi_scores),
        "msi_modal_density": round(1000 * modal_sum / n_tokens, 3),
        "msi_epistemic_density": round(1000 * epi_sum / n_tokens, 3),
        "msi_total_density": round(1000 * (modal_sum + epi_sum) / n_tokens, 3),
        "msi_avg_modal_strength": round(modal_sum / len(modal_scores), 3) if modal_scores else 0.0,
        "msi_avg_epistemic_strength": round(epi_sum / len(epi_scores), 3) if epi_scores else 0.0,
        "msi_signed_per_1000": round(1000 * signed_sum / n_tokens, 3),
    }

def main():
    rows = []
    files = sorted(POS_DIR.glob("*.json"))
    print(f"Scoring {len(files)} docs...")
    for p in files:
        rec = json.loads(p.read_text())
        rows.append(score_doc(rec))

    out_csv = ANALYSIS / "modality_index.csv"
    cols = list(rows[0].keys())
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {out_csv} ({len(rows)} rows)")

    # Quick sanity: mean per doc_type
    from collections import defaultdict
    bucket = defaultdict(list)
    for r in rows:
        bucket[r["doc_type"]].append(r["msi_avg_modal_strength"])
    print("\nmsi_avg_modal_strength by doc_type:")
    for k, vs in sorted(bucket.items()):
        print(f"  {k:<25} n={len(vs):>4}  mean={sum(vs)/len(vs):.3f}  min={min(vs):.3f}  max={max(vs):.3f}")

if __name__ == "__main__":
    main()
