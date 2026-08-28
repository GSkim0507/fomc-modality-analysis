"""
18_nb_classifier.py
-------------------
수업 9강(문서분류·감성분석)에서 다룬 NLTK NaiveBayesClassifier +
show_most_informative_features() 패턴을 FOMC hawkish/dovish 분류에
그대로 응용한다.

수업 코드 패턴 (직접 인용):
    from nltk.corpus import movie_reviews
    A = {w for w,_ in nltk.FreqDist(...).most_common(1000)}
    B = {w for w,_ in nltk.FreqDist(...).most_common(1000)}
    Symmetric_Difference = A ^ B
    def document_features(document):
        document_words = set(document)
        features = {}
        for word in Symmetric_Difference:
            features[f'contains({word})'] = word in document_words
        return features
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    classifier.show_most_informative_features(15)

+α: 영화리뷰 pos/neg 대신 FOMC Statement의 hawkish/dovish 라벨을 사용.
출력:
    analysis/nb_classifier_features.txt
"""

import json
import os
import random
from collections import Counter
from pathlib import Path

import nltk
import pandas as pd

for resource in ("punkt", "punkt_tab"):
    try:
        nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
STMT = ROOT / "statements"

random.seed(7)


def load_labeled_statements():
    labels = pd.read_csv(ANALYSIS / "dotplot_labels.csv")
    labels = labels[labels["label"].isin(["hawkish", "dovish"])].copy()
    docs = []
    for fn in sorted(os.listdir(STMT)):
        if not fn.endswith(".json"):
            continue
        with open(STMT / fn, encoding="utf-8") as f:
            d = json.load(f)
        date = d.get("meeting_date") or d.get("date")
        row = labels[labels["meeting_date"] == date]
        if row.empty:
            continue
        label = row.iloc[0]["label"]
        tokens = [w.lower() for w in nltk.word_tokenize(d.get("text", ""))
                  if w.isalpha()]
        docs.append((tokens, label))
    return docs


def main():
    docs = load_labeled_statements()
    print(f"Labeled Statement docs: {len(docs)}")
    print("Class balance:", Counter(label for _, label in docs))

    hawk_words = [w for toks, lab in docs if lab == "hawkish" for w in toks]
    dove_words = [w for toks, lab in docs if lab == "dovish" for w in toks]

    A = {w for w, _ in nltk.FreqDist(hawk_words).most_common(500)}
    B = {w for w, _ in nltk.FreqDist(dove_words).most_common(500)}
    symmetric_diff = A ^ B
    print(f"|A∩B| common  = {len(A & B)}")
    print(f"|A△B| diff    = {len(symmetric_diff)}  ← features")

    def document_features(document):
        words = set(document)
        return {f"contains({w})": (w in words) for w in symmetric_diff}

    feature_sets = [(document_features(d), c) for d, c in docs]
    random.shuffle(feature_sets)
    split = int(len(feature_sets) * 0.8)
    train_set, test_set = feature_sets[:split], feature_sets[split:]
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    acc = nltk.classify.accuracy(classifier, test_set)
    train_acc = nltk.classify.accuracy(classifier, train_set)

    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        classifier.show_most_informative_features(20)
    most_informative = buf.getvalue()

    lines = []
    lines.append("NLTK NaiveBayesClassifier — FOMC Statement hawkish vs dovish")
    lines.append("=" * 64)
    lines.append(f"corpus: {len(docs)} labeled FOMC Statements")
    lines.append(f"  hawkish = {sum(1 for _, c in docs if c == 'hawkish')}")
    lines.append(f"  dovish  = {sum(1 for _, c in docs if c == 'dovish')}")
    lines.append(f"feature set (symmetric difference of top-500 FreqDist): {len(symmetric_diff)}")
    lines.append(f"train/test split: {len(train_set)}/{len(test_set)}")
    lines.append(f"train accuracy = {train_acc:.3f}")
    lines.append(f"test  accuracy = {acc:.3f}")
    lines.append("")
    lines.append("Most informative features (수업 9강 패턴):")
    lines.append(most_informative)

    out = ANALYSIS / "nb_classifier_features.txt"
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
