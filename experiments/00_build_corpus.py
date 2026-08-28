"""
00_build_corpus.py — Build a clean sentence-level corpus for 2010–2026 (analysis window 2014–2026).

- Fix mojibake (UTF-8 bytes mis-decoded as latin-1).
- Strip boilerplate headers (release lines, "Share", page markers, "For release at ...").
- Sentence-split with spaCy; keep doc metadata.
Outputs:
  results/tables/corpus_docs.csv       one row per document (doc_id, doc_type, date, chair, n_tokens, n_sents)
  results/tables/corpus_sentences.csv  one row per sentence (doc_id, doc_type, date, chair, sent_id, text)
"""
from __future__ import annotations
import json, re, csv, sys, time
from pathlib import Path
import spacy
import ftfy

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "FOMC_corpus"
OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

GENRES = {"statements": "statement", "minutes": "minutes",
          "transcripts": "press_conf", "speeches": "speech"}

def fix_mojibake(t: str) -> str:
    """Repair UTF-8 text that was mis-decoded as latin-1/cp1252 (ftfy handles mixed cases)."""
    return ftfy.fix_text(t)

HEADER_PATTERNS = [
    r"^\s*For release at .*$", r"^\s*Share\s*$", r"^\s*Page \d+ of \d+\s*$",
    r"^\s*FINAL\s*$", r"^\s*Federal Reserve issues FOMC statement\s*$",
    r"^\s*(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\s*$",
    r"^\s*Transcript of Chair .* Press Conference\s*$",
    r"^\s*Chair .*’s Press Conference\s*$",
    r"^\s*Last Update:.*$", r"^\s*Implementation Note issued .*$",
]
HEADER_RE = [re.compile(p, re.I | re.M) for p in HEADER_PATTERNS]

def clean(t: str) -> str:
    t = fix_mojibake(t)
    t = t.replace("\r", "")
    for rx in HEADER_RE:
        t = rx.sub("", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def main():
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    nlp.max_length = 2_000_000
    docs_rows, sent_rows = [], []
    t0 = time.time()
    paths = []
    for sub, genre in GENRES.items():
        for p in sorted((CORPUS / sub).glob("*.json")):
            paths.append((p, genre))
    for i, (p, genre) in enumerate(paths, 1):
        rec = json.loads(p.read_text())
        text = clean(rec["text"])
        doc = nlp(text)
        n_tok = sum(1 for t in doc if not t.is_space and not t.is_punct)
        sents = [s.text.strip().replace("\n", " ") for s in doc.sents]
        sents = [re.sub(r"\s+", " ", s) for s in sents if len(s.split()) >= 3]
        docs_rows.append(dict(doc_id=rec["doc_id"], doc_type=genre, date=rec["date"],
                              chair=rec.get("chair"), speaker=rec.get("speaker", rec.get("chair")),
                              n_tokens=n_tok, n_sents=len(sents)))
        for j, s in enumerate(sents):
            sent_rows.append(dict(doc_id=rec["doc_id"], doc_type=genre, date=rec["date"],
                                  chair=rec.get("chair"), sent_id=j, text=s))
        if i % 50 == 0 or i == len(paths):
            print(f"[{i}/{len(paths)}] {time.time()-t0:.0f}s {p.name}", file=sys.stderr)
    with (OUT / "corpus_docs.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(docs_rows[0].keys())); w.writeheader(); w.writerows(docs_rows)
    with (OUT / "corpus_sentences.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sent_rows[0].keys())); w.writeheader(); w.writerows(sent_rows)
    print(f"docs={len(docs_rows)} sentences={len(sent_rows)}", file=sys.stderr)

if __name__ == "__main__":
    main()
