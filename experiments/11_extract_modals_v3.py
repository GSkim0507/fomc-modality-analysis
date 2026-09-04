"""
11_extract_modals_v3.py — Modal-construction extraction on the layer-aware corpus (Phase 10.6).

Re-uses the dependency logic of 01_extract_modals.py (lexical head, copular-be resolution, subject typing,
negation / passive / perfect / progressive, conditional and reported-speech flags) unchanged, so that v2 and v3
differ only in the corpus (cleaning + layers), not in the extraction rules.

Input : results/tables/corpus_sentences_v3.csv
Output: results/tables/modal_tokens_v3.csv  (v2 columns + layer, section, speaker, n_tok)
"""
from __future__ import annotations
import sys, time, importlib.util
from pathlib import Path
import pandas as pd
import spacy

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "results" / "tables"
spec = importlib.util.spec_from_file_location("x01", ROOT / "experiments" / "01_extract_modals.py")
x01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(x01)


def main():
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    sents = pd.read_csv(TAB / "corpus_sentences_v3.csv")
    print(f"sentences: {len(sents)}", file=sys.stderr)
    texts = sents["text"].astype(str).tolist()
    meta = sents[["doc_id", "doc_type", "date", "chair", "layer", "section", "speaker", "sent_id", "n_tok"]].to_dict("records")
    rows = []; t0 = time.time()
    for k, (doc, m) in enumerate(zip(nlp.pipe(texts, batch_size=256), meta)):
        for tok in doc:
            surf = tok.text.lower()
            if tok.tag_ != "MD" and surf not in {"'ll", "’ll", "'d", "’d"}:
                continue
            if surf in {"'d", "’d"}:
                nxt = doc[tok.i + 1] if tok.i + 1 < len(doc) else None
                if nxt is None or nxt.tag_ not in {"VB", "RB"}:
                    continue
            modal = x01.MODAL_NORM.get(surf, tok.lemma_.lower())
            if modal not in x01.MODAL_NORM.values():
                continue
            head, perfect, progressive, passive = x01.lexical_head(tok)
            neg = any(c.dep_ == "neg" for c in head.children) or any(c.dep_ == "neg" for c in tok.children)
            for c in tok.head.children:
                if c.dep_ == "neg":
                    neg = True
            subj = x01.find_subject(tok)
            hv = head.lemma_.lower()
            b_comp = b_type = b_x = ""
            if hv == "be":
                b_comp, b_type, b_x = x01.be_complement(head)
            predicate = f"be+{b_comp}" if (hv == "be" and b_comp) else hv
            rows.append(dict(
                doc_id=m["doc_id"], doc_type=m["doc_type"], date=m["date"], chair=m["chair"],
                layer=m["layer"], section=m["section"], speaker=m["speaker"], sent_id=m["sent_id"], n_tok=m["n_tok"],
                modal=modal, surface=surf, contracted=surf.startswith(("'", "’")),
                head_verb=hv, head_verb_surface=head.text.lower(), head_pos=head.pos_, head_tag=head.tag_,
                be_comp=b_comp, be_comp_type=b_type, be_xcomp=b_x, predicate=predicate,
                neg=neg, passive=passive, perfect=perfect, progressive=progressive,
                subj_text=(subj.text if subj is not None else ""),
                subj_lemma=(subj.lemma_.lower() if subj is not None else ""),
                subj_type=(x01.subj_type(subj.lemma_, " ".join(t.text for t in subj.subtree)) if subj is not None else "none"),
                cond=x01.is_conditional(tok, doc), reported=x01.is_reported(tok),
                question=doc.text.strip().endswith("?"), modal_idx=tok.i, sentence=doc.text))
        if (k + 1) % 20000 == 0:
            print(f"[{k+1}/{len(texts)}] {time.time()-t0:.0f}s modals={len(rows)}", file=sys.stderr)
    out = TAB / "modal_tokens_v3.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out} rows={len(rows)} in {time.time()-t0:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
