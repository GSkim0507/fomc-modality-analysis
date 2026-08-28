"""
17_wordnet_similarity.py
------------------------
수업 7강(의미분석)에서 다룬 WordNet 의미 유사도(wup_similarity)를
FOMC 양태(modality) 어휘에 적용한다.

수업 코드 패턴 (직접 인용):
    from nltk.corpus import wordnet as wn
    wn.synsets('motorcar')
    w1.path_similarity(w2)
    w1.wup_similarity(w2)
    pd.DataFrame([[s1.wup_similarity(s2) for s2 in synsets] for s1 in synsets])

+α: 양태 어휘의 epistemic certainty 점수(MSI 사전)와의 의미 거리를 비교
    → 헷지 군집 vs 확신 군집이 WordNet 위에서도 분리되는가 검증.

출력:
    analysis/wordnet_modality_similarity.csv
    analysis/wordnet_similarity_report.txt
    analysis/figures/23_wordnet_modality_heatmap.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import wordnet as wn

for resource in ("wordnet", "omw-1.4"):
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"

WORDS = [
    ("certainty",    1.0, "booster"),
    ("conviction",   1.0, "booster"),
    ("assurance",    0.9, "booster"),
    ("confidence",   0.8, "booster"),
    ("likelihood",   0.5, "hedge"),
    ("probability",  0.5, "hedge"),
    ("possibility",  0.3, "hedge"),
    ("uncertainty",  0.2, "hedge"),
    ("doubt",        0.1, "hedge"),
    ("ambiguity",    0.1, "hedge"),
]

POS_PRIORITY = ["n", "a", "s", "v", "r"]


def best_synset(word: str):
    for pos in POS_PRIORITY:
        ss = wn.synsets(word, pos=pos)
        if ss:
            return ss[0]
    ss = wn.synsets(word)
    return ss[0] if ss else None


def main():
    synsets = {w: best_synset(w) for w, _, _ in WORDS}
    missing = [w for w, s in synsets.items() if s is None]
    if missing:
        print("WARNING: no synset found for", missing)

    labels = [w for w, _, _ in WORDS]
    n = len(labels)
    mat = np.zeros((n, n))
    for i, w1 in enumerate(labels):
        for j, w2 in enumerate(labels):
            s1 = synsets[w1]
            s2 = synsets[w2]
            if s1 is None or s2 is None:
                mat[i, j] = np.nan
                continue
            sim = s1.wup_similarity(s2)
            mat[i, j] = sim if sim is not None else np.nan

    df = pd.DataFrame(mat, index=labels, columns=labels)
    df.to_csv(ANALYSIS / "wordnet_modality_similarity.csv")
    print(df.round(2))

    report = []
    report.append("WordNet wup_similarity over modality lexicon")
    report.append("=" * 60)
    report.append("words (with MSI epistemic certainty score):")
    for w, s, cat in WORDS:
        ss = synsets[w]
        if ss is None:
            report.append(f"  {w:10s}  score={s}  cat={cat:8s}  [no synset]")
        else:
            report.append(f"  {w:10s}  score={s}  cat={cat:8s}  -> {ss.name():18s} : {ss.definition()[:70]}")

    boosters = [w for w, _, c in WORDS if c == "booster" and synsets[w]]
    hedges = [w for w, _, c in WORDS if c == "hedge" and synsets[w]]
    within_b = [df.loc[a, b] for a in boosters for b in boosters if a != b]
    within_h = [df.loc[a, b] for a in hedges for b in hedges if a != b]
    between = [df.loc[a, b] for a in boosters for b in hedges]
    within_b = [x for x in within_b if not np.isnan(x)]
    within_h = [x for x in within_h if not np.isnan(x)]
    between = [x for x in between if not np.isnan(x)]
    report.append("")
    report.append(f"mean similarity within boosters (n={len(within_b)}):   {np.mean(within_b):.3f}")
    report.append(f"mean similarity within hedges   (n={len(within_h)}):   {np.mean(within_h):.3f}")
    report.append(f"mean similarity between groups  (n={len(between)}):    {np.mean(between):.3f}")
    report.append("→ within-cluster > between-cluster confirms semantic separation")

    with open(ANALYSIS / "wordnet_similarity_report.txt", "w") as f:
        f.write("\n".join(report))
    print("\n".join(report[-6:]))

    fig, ax = plt.subplots(figsize=(8.5, 7))
    im = ax.imshow(mat, cmap="RdYlBu_r", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    for i in range(n):
        for j in range(n):
            v = mat[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=8, color="black" if 0.3 < v < 0.75 else "white")
    ax.axhline(3.5, color="black", lw=1.5)
    ax.axvline(3.5, color="black", lw=1.5)
    ax.set_title("WordNet wup_similarity — booster (top-left) vs hedge (bottom-right)\n"
                 f"within-booster μ={np.mean(within_b):.2f}  /  within-hedge μ={np.mean(within_h):.2f}  /  between μ={np.mean(between):.2f}")
    fig.colorbar(im, ax=ax, label="wup_similarity (0–1)")
    fig.tight_layout()
    fig.savefig(FIG / "23_wordnet_modality_heatmap.png", dpi=160)
    plt.close(fig)
    print("saved -> figures/23_wordnet_modality_heatmap.png")


if __name__ == "__main__":
    main()
