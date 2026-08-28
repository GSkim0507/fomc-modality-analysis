"""
01_extract_modals.py — Dependency-based modal-verb extraction (all genres, 2010–2026).

For each token tagged MD (or contracted 'll/'d):
  modal        normalised lemma (will, would, could, can, should, may, might, must, shall, ought)
  contracted   True if surface is 'll / 'd
  head_verb    the lexical verb the modal scopes over (skip aux chain: have/be/been/being/get)
  head_verb_surface
  neg          True if 'not'/'n't' attached to the modal or the head verb
  passive      True if head verb has auxpass / nsubjpass
  perfect      True if 'have' aux between modal and verb (would have been)
  progressive  True if 'be ... -ing'
  subj_text    subject head text of the clause (nsubj/nsubjpass/expl)
  subj_lemma   subject lemma
  subj_type    committee | fed | we/I | it/there | econ (inflation, economy, conditions...) | risks | other
  cond         True if the clause is inside/adjacent to an if/should/unless/as long as clause
  reported     True if the modal clause is a ccomp/xcomp of a reporting verb (said, noted, indicated, judged...)
  question     True if sentence ends with '?'
  sentence     full sentence text
Outputs: results/tables/modal_tokens.csv
"""
from __future__ import annotations
import csv, sys, time, re
from pathlib import Path
import pandas as pd
import spacy

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "results" / "tables"

MODAL_NORM = {"will": "will", "'ll": "will", "’ll": "will", "wo": "will",
              "would": "would", "'d": "would", "’d": "would",
              "could": "could", "can": "can", "ca": "can",
              "should": "should", "may": "may", "might": "might",
              "must": "must", "shall": "shall", "ought": "ought"}
AUX = {"have", "be", "been", "being", "get", "got", "gotten", "having", "has", "had"}
REPORT_VERBS = {"say", "note", "indicate", "judge", "state", "emphasize", "stress", "suggest",
                "observe", "remark", "comment", "argue", "believe", "think", "expect", "anticipate",
                "agree", "view", "see", "point", "mention", "add", "conclude", "maintain", "recognize",
                "acknowledge", "report", "highlight", "underscore", "explain", "worry", "concern",
                "feel", "hold", "contend", "assess", "affirm", "reaffirm", "reiterate", "signal"}
COND_MARKERS = {"if", "unless", "provided", "should", "as long as", "in the event", "were", "whether"}

ECON_SUBJ = re.compile(r"\b(inflation|economy|econom|growth|activity|condition|price|rate|market|employment|"
                       r"unemployment|labor|spending|invest|demand|supply|output|wage|risk|uncertaint|"
                       r"outlook|expectation|pressure|shock|policy|purchase|holding|balance|tariff|"
                       r"financial|credit|dollar|yield|asset|securit|program|facility|indicator|data|"
                       r"gdp|pce|cpi|payroll|sector|business|household|consumer|bank|firm)", re.I)

def subj_type(lemma: str, text: str) -> str:
    l = lemma.lower(); t = text.lower()
    if "committee" in t or "fomc" in t: return "committee"
    if l in {"we", "i", "us", "our"} : return "we_I"
    if "fed" in t or "reserve" in t or "board" in t or "system" in t or "desk" in t: return "fed"
    if l in {"you", "they", "he", "she", "people", "participant", "member", "official", "president", "governor", "chair"}: return "person"
    if l in {"it", "there", "this", "that", "these", "those", "which", "who", "what"}: return "it_there_rel"
    if "risk" in t: return "risks"
    if ECON_SUBJ.search(t): return "econ"
    return "other"

def find_subject(tok):
    """Walk up from modal to the clause head verb, return subject token."""
    head = tok.head
    for c in head.children:
        if c.dep_ in {"nsubj", "nsubjpass", "expl", "csubj"}:
            return c
    # try conj / relative constructions
    h = head
    for _ in range(3):
        if h.dep_ in {"conj", "xcomp", "advcl", "relcl", "ccomp"} and h.head != h:
            h = h.head
            for c in h.children:
                if c.dep_ in {"nsubj", "nsubjpass", "expl", "csubj"}:
                    return c
        else:
            break
    return None

def lexical_head(tok):
    """Return the lexical verb governed by the modal (skip aux chain)."""
    h = tok.head
    perfect = progressive = passive = False
    hops = 0
    while hops < 4:
        hops += 1
        # if head is itself an auxiliary with its own head verb, move
        if h.pos_ in {"AUX"} and h.lemma_ in AUX and h.head != h and h.dep_ in {"aux", "auxpass"}:
            if h.lemma_ == "have": perfect = True
            h = h.head
            continue
        break
    # inspect aux children of the head
    for c in h.children:
        if c.dep_ == "aux" and c.lemma_ == "have" and c.i > tok.i: perfect = True
        if c.dep_ == "auxpass": passive = True
        if c.dep_ == "aux" and c.lemma_ == "be" and c.i > tok.i and h.tag_ == "VBG": progressive = True
    if h.tag_ == "VBN" and any(c.dep_ == "auxpass" for c in h.children): passive = True
    if any(c.dep_ == "nsubjpass" for c in h.children): passive = True
    return h, perfect, progressive, passive

def is_reported(tok):
    h = tok.head
    for _ in range(4):
        if h.dep_ in {"ccomp", "xcomp", "advcl"} and h.head.lemma_.lower() in REPORT_VERBS:
            return True
        if h.head == h: break
        h = h.head
    return False

def is_conditional(tok, sent):
    # a marker 'if/unless' appears in the sentence and the modal clause is the main or governs an advcl
    text = sent.text.lower()
    if any(m in text for m in COND_MARKERS if m not in {"should", "were", "whether"}):
        return True
    # inverted conditional: "should economic developments ..." handled by 'should' with subj after
    return False

def main():
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    sents = pd.read_csv(TAB / "corpus_sentences.csv")
    print(f"sentences: {len(sents)}", file=sys.stderr)
    rows = []
    t0 = time.time()
    texts = sents["text"].tolist()
    meta = sents[["doc_id", "doc_type", "date", "chair", "sent_id"]].to_dict("records")
    for k, (doc, m) in enumerate(zip(nlp.pipe(texts, batch_size=256), meta)):
        sent = doc
        for tok in doc:
            surf = tok.text.lower()
            if tok.tag_ != "MD" and surf not in {"'ll", "’ll", "'d", "’d"}:
                continue
            if surf in {"'d", "’d"}:
                # 'd could be had; treat as would only if next token is base verb (VB) or 'be'
                nxt = doc[tok.i + 1] if tok.i + 1 < len(doc) else None
                if nxt is None or nxt.tag_ not in {"VB", "RB"} : continue
            modal = MODAL_NORM.get(surf, tok.lemma_.lower())
            if modal not in MODAL_NORM.values(): continue
            head, perfect, progressive, passive = lexical_head(tok)
            neg = any(c.dep_ == "neg" for c in head.children) or any(
                c.dep_ == "neg" for c in tok.children)
            # neg attached to modal's head chain
            for c in tok.head.children:
                if c.dep_ == "neg": neg = True
            subj = find_subject(tok)
            rows.append(dict(
                doc_id=m["doc_id"], doc_type=m["doc_type"], date=m["date"], chair=m["chair"],
                sent_id=m["sent_id"], modal=modal, surface=surf,
                contracted=surf.startswith(("'", "’")),
                head_verb=head.lemma_.lower(), head_verb_surface=head.text.lower(),
                head_pos=head.pos_, head_tag=head.tag_,
                neg=neg, passive=passive, perfect=perfect, progressive=progressive,
                subj_text=(subj.text if subj is not None else ""),
                subj_lemma=(subj.lemma_.lower() if subj is not None else ""),
                subj_type=(subj_type(subj.lemma_, " ".join(t.text for t in subj.subtree)) if subj is not None else "none"),
                cond=is_conditional(tok, sent), reported=is_reported(tok),
                question=sent.text.strip().endswith("?"),
                modal_idx=tok.i, sentence=sent.text))
        if (k + 1) % 20000 == 0:
            print(f"[{k+1}/{len(texts)}] {time.time()-t0:.0f}s modals={len(rows)}", file=sys.stderr)
    out = TAB / "modal_tokens.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out} rows={len(rows)} in {time.time()-t0:.0f}s", file=sys.stderr)

if __name__ == "__main__":
    main()
