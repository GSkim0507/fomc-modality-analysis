"""
N-gram analysis of modal-bearing phrases.

Input:  analysis/modal_instances.csv  (one row per modal occurrence)
Idea:   For each modal token we already saved `left_3` and `right_3` context.
        Build the 7-token window  left_3 + [modal] + right_3  and extract:
          - bigrams containing the modal
          - trigrams containing the modal
          - 4-grams containing the modal

Outputs:
  analysis/ngrams_top.csv         top phrases per n, overall
  analysis/ngrams_by_year.csv     top phrases per year (for time trend)
  figures/08_ngram_top_phrases.png  bar charts of top 3-grams overall
  figures/09_ngram_phrase_trend.png  selected phrases over time
"""
from __future__ import annotations
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"

TOKEN_RE = re.compile(r"[A-Za-z']+")

STOPISH = set()  # keep all tokens — modal phrases ARE semi-stopwordy by design

def tok(s: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(s or "")]

def window(left: str, modal: str, right: str) -> list[str]:
    return tok(left) + [modal.lower()] + tok(right)

def ngrams_containing_modal(words: list[str], modal_idx: int, n: int) -> list[tuple[str, ...]]:
    """All n-grams that span the modal position."""
    out = []
    L = len(words)
    for start in range(max(0, modal_idx - n + 1), min(L - n, modal_idx) + 1):
        if start <= modal_idx < start + n:
            out.append(tuple(words[start:start + n]))
    return out

def load_instances():
    with (ANALYSIS / "modal_instances.csv").open() as f:
        return list(csv.DictReader(f))

def main():
    rows = load_instances()
    print(f"Loaded {len(rows)} modal instances")

    # Overall counters
    cnt = {2: Counter(), 3: Counter(), 4: Counter()}
    # Per-year: only collect 3-grams for time-trend analysis (keeps file size sane)
    per_year_3 = defaultdict(Counter)
    # Per-doc_type, 3-grams
    per_type_3 = defaultdict(Counter)

    for r in rows:
        words = window(r["left_3"], r["surface"], r["right_3"])
        # modal position = len(left tokens). left_3 may have <3 tokens after tokenisation,
        # so re-locate by surface match.
        try:
            modal_idx = next(i for i, w in enumerate(words) if w == r["surface"].lower())
        except StopIteration:
            continue
        year = r["date"][:4]
        dtype = r["doc_type"]
        for n in (2, 3, 4):
            for g in ngrams_containing_modal(words, modal_idx, n):
                cnt[n][g] += 1
                if n == 3:
                    per_year_3[year][g] += 1
                    per_type_3[dtype][g] += 1

    # Write top overall
    with (ANALYSIS / "ngrams_top.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "phrase", "count"])
        for n in (2, 3, 4):
            for g, c in cnt[n].most_common(150):
                w.writerow([n, " ".join(g), c])
    print("  ngrams_top.csv written")

    # Per-year top-50 3-grams
    with (ANALYSIS / "ngrams_by_year.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "phrase", "count"])
        for y in sorted(per_year_3):
            for g, c in per_year_3[y].most_common(50):
                w.writerow([y, " ".join(g), c])
    print("  ngrams_by_year.csv written")

    # ---- Figure 08: top 15 3-grams overall ----
    top3 = cnt[3].most_common(15)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh([" ".join(g) for g, _ in top3[::-1]], [c for _, c in top3[::-1]], color="#4c72b0")
    ax.set_title("Top-15 Modal Trigrams (corpus-wide)")
    ax.set_xlabel("count")
    fig.tight_layout(); fig.savefig(FIG / "08_ngram_top_phrases.png", dpi=150); plt.close(fig)
    print("  fig 08 written")

    # ---- Figure 09: trend of selected committed-vs-hedged trigrams ----
    # Pick a few semantically-loaded phrases that actually appear
    candidate_phrases = [
        # committed / strong
        ("we", "will", "continue"),
        ("will", "be", "appropriate"),
        ("committee", "will", "continue"),
        # hedged / uncertain
        ("is", "likely", "to"),
        ("may", "become", "appropriate"),
        ("could", "be", "appropriate"),
        ("might", "be", "appropriate"),
    ]
    # Keep only phrases that actually appear with reasonable freq
    candidate_phrases = [p for p in candidate_phrases if cnt[3][p] >= 5]
    years = sorted(per_year_3)
    fig, ax = plt.subplots(figsize=(11, 6))
    for p in candidate_phrases:
        vals = [per_year_3[y].get(p, 0) for y in years]
        ax.plot([int(y) for y in years], vals, marker="o", label=" ".join(p))
    ax.set_title("Selected Modal Trigrams Over Time")
    ax.set_xlabel("Year"); ax.set_ylabel("count (raw)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / "09_ngram_phrase_trend.png", dpi=150); plt.close(fig)
    print("  fig 09 written")

    # Console summary
    print("\nTop-10 trigrams overall:")
    for g, c in cnt[3].most_common(10):
        print(f"  {c:>5}  {' '.join(g)}")

if __name__ == "__main__":
    main()
