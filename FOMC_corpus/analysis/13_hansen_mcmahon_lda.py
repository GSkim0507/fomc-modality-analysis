"""
Paper A — Hansen & McMahon (2016)-style LDA topic analysis.

H&M identified topics in FOMC discourse (forward guidance, financial markets,
economic outlook) and showed that the sentiment of forward-guidance language
has measurable macro effects.

We adapt the approach to ask: does the MSI / hedging concentrate in specific
topics? If forward-guidance topics carry the bulk of hedged modals, that
strengthens the 'Hedging as Policy' thesis — the Fed hedges exactly where it
talks about future policy.

Pipeline:
  1. Sentence-segment minutes (richest discourse). Filter to substantive sents.
  2. Train LDA (gensim) with k=6 topics on the lemmatized, stopword-removed corpus.
  3. Label topics by inspecting top words.
  4. For each topic, compute MSI per sentence assigned to that topic.
  5. Test: does modality strength differ by topic? (ANOVA)

Output:
  analysis/lda_topics.txt
  analysis/sentence_topic_modality.csv
  figures/19_paperA_topic_modality.png
"""
from __future__ import annotations
from pathlib import Path
import re, json
from collections import Counter, defaultdict

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from gensim import corpora, models
from gensim.parsing.preprocessing import STOPWORDS
import spacy

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"

EXTRA_STOP = {
    "committee","members","participant","participants","meeting","staff","said",
    "noted","also","would","could","may","might","will","should","one","two","also",
    "many","most","several","like","made","make","make","page","federal","reserve",
    "fomc","mr","ms","secretary","chair","chairman","percent","point","percentage",
}
ALL_STOP = set(STOPWORDS) | EXTRA_STOP

MODAL_LEMMAS = {"will","would","could","can","may","might","should","must","shall",
                "ought","need"}
MODAL_STRENGTH = {"will":1.0,"would":1.0,"must":1.0,"should":0.7,"shall":0.7,
                  "ought":0.7,"can":0.4,"could":0.4,"may":0.3,"might":0.3,"need":0.5}

def lemmatize_sentences(nlp, text: str):
    """Yield (sentence_text, lemma_tokens, modal_strength, n_tokens) per sentence."""
    doc = nlp(text)
    for sent in doc.sents:
        toks = []
        modal_scores = []
        n_content = 0
        for t in sent:
            if t.is_space or t.is_punct: continue
            lem = t.lemma_.lower()
            if t.tag_ == "MD" and lem in MODAL_STRENGTH:
                modal_scores.append(MODAL_STRENGTH[lem])
            if lem in ALL_STOP or t.is_stop or not t.is_alpha:
                continue
            if len(lem) < 3: continue
            toks.append(lem)
            n_content += 1
        if n_content < 5:
            continue
        avg_mod = sum(modal_scores) / len(modal_scores) if modal_scores else None
        yield sent.text.strip()[:300], toks, avg_mod, n_content

def main():
    print("Loading spaCy ...")
    nlp = spacy.load("en_core_web_sm", disable=["ner","parser"])
    nlp.enable_pipe("senter") if "senter" in nlp.pipe_names else nlp.add_pipe("sentencizer")

    print("Streaming Minutes corpus into sentences ...")
    sentences = []      # list of (doc_id, date, sent_text, tokens, avg_modal, n_tokens)
    paths = sorted((ROOT / "minutes").glob("*.json"))
    for i, p in enumerate(paths, 1):
        rec = json.loads(p.read_text())
        for sent_text, toks, mod, n in lemmatize_sentences(nlp, rec["text"]):
            sentences.append({
                "doc_id": rec["doc_id"], "date": rec["date"],
                "sent": sent_text, "tokens": toks,
                "avg_modal": mod, "n_tokens": n,
            })
        if i % 20 == 0:
            print(f"  [{i}/{len(paths)}]  sentences so far: {len(sentences)}")
    print(f"Total content sentences: {len(sentences):,}")

    # ---- Build dictionary, corpus, LDA ----
    texts = [s["tokens"] for s in sentences]
    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=10, no_above=0.5)
    bow = [dictionary.doc2bow(t) for t in texts]
    print(f"Vocabulary after filtering: {len(dictionary)}")

    K = 6
    print(f"Training LDA  k={K} ...")
    lda = models.LdaModel(bow, num_topics=K, id2word=dictionary,
                          passes=8, iterations=200, random_state=0, alpha="auto")

    # ---- Top words per topic ----
    lines = ["=== Paper A — H&M-style LDA topic analysis ==="]
    lines.append(f"\nSentences: {len(sentences):,}    vocab: {len(dictionary)}    K={K}")
    lines.append("\nTop words per topic:")
    topic_words = {}
    for k in range(K):
        words = [w for w, _ in lda.show_topic(k, topn=12)]
        topic_words[k] = words
        lines.append(f"  T{k}: {', '.join(words)}")

    # ---- Assign top topic per sentence and modality ----
    print("Inferring topic for each sentence ...")
    rows = []
    for s, b in zip(sentences, bow):
        if not b: continue
        topic_dist = lda.get_document_topics(b, minimum_probability=0.0)
        topic_dist.sort(key=lambda x: -x[1])
        top_topic, prob = topic_dist[0]
        rows.append({
            "doc_id": s["doc_id"], "date": s["date"],
            "n_tokens": s["n_tokens"],
            "avg_modal": s["avg_modal"],
            "topic": int(top_topic), "topic_prob": float(prob),
            "sentence": s["sent"],
        })
    df = pd.DataFrame(rows)
    df.to_csv(ANALYSIS / "sentence_topic_modality.csv", index=False)
    print(f"  wrote sentence_topic_modality.csv ({len(df):,} rows)")

    # ---- Modality by topic (sentences with at least one modal) ----
    df_m = df[df["avg_modal"].notna()].copy()
    lines.append(f"\nModal-bearing sentences: {len(df_m):,}  ({100*len(df_m)/len(df):.1f}%)")
    lines.append("\nMean modal strength by topic (modal-bearing sentences only):")
    g = df_m.groupby("topic")["avg_modal"].agg(["count","mean","std"]).round(3)
    g["top_words"] = [", ".join(topic_words[k][:6]) for k in g.index]
    lines.append(g.to_string())

    # ANOVA across topics
    groups = [df_m[df_m["topic"] == k]["avg_modal"].values for k in range(K)
              if len(df_m[df_m["topic"] == k]) >= 5]
    if len(groups) >= 2:
        F, p = stats.f_oneway(*groups)
        lines.append(f"\nOne-way ANOVA  modal_strength ~ topic   F={F:.2f}, p={p:.3e}")

    # ---- Figure ----
    fig, ax = plt.subplots(figsize=(11, 6))
    box_data = [df_m[df_m["topic"] == k]["avg_modal"].values for k in range(K)]
    labels = [f"T{k}\n{', '.join(topic_words[k][:3])}" for k in range(K)]
    bp = ax.boxplot(box_data, tick_labels=labels, patch_artist=True, showmeans=True)
    cmap = plt.get_cmap("tab10")
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(cmap(i)); patch.set_alpha(0.7)
    ax.set_ylabel("Avg modal strength (per sentence)  [0–1]")
    ax.set_title("Modal certainty distribution by LDA topic (Minutes corpus)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / "19_paperA_topic_modality.png", dpi=150); plt.close(fig)

    (ANALYSIS / "lda_topics.txt").write_text("\n".join(lines))
    print("\n".join(lines))

if __name__ == "__main__":
    main()
