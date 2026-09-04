"""
12_qa_integrity.py — Data-integrity report for corpus v3 (Phase 10.7).

Checks
  1. document inventory by genre x year; meeting-date alignment statement <-> minutes (FOMC_corpus/_meta/meeting_dates.json)
  2. duplicate documents (text hash), duplicate ids, date parse/order
  3. token outliers per genre x layer (|z| > 3)
  4. residue: encoding artefacts, navigation / footnote / page-header strings surviving in sentences
  5. layer coverage: minutes missing key sections, press conferences with long unlabeled text, journalist share
  6. quoted statement inside minutes vs the statement document of the same meeting (sentence-set Jaccard)
  7. v2 vs v3 comparison (tokens, modal tokens) when modal_tokens_v3.csv exists
  8. human-validation samples: speaker roles (10 docs x 20 turns), minutes layers (2 sentences per layer per doc, 10 docs)
Outputs: results/qa/QA_report.md (+ CSVs in results/qa/)
"""
from __future__ import annotations
import json, re, hashlib, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "results" / "tables"; QA = ROOT / "results" / "qa"; QA.mkdir(exist_ok=True, parents=True)
sys.path.insert(0, str(ROOT / "experiments"))
from common_v3 import EXCLUDE_DOCS, LAYER_LABEL

L = ["# QA report — corpus v3", ""]


def h(title): L.extend(["", f"## {title}", ""])


def table(df: pd.DataFrame, max_rows=40):
    if df is None or len(df) == 0:
        L.append("(none)"); return
    df = df.head(max_rows)
    L.append("| " + " | ".join(map(str, df.columns)) + " |"); L.append("|" + "---|" * len(df.columns))
    for _, r in df.iterrows():
        L.append("| " + " | ".join(str(v) for v in r.values) + " |")


def norm_sent(s):
    s = str(s).lower(); s = re.sub(r"\d+([./-]\d+)*", "#", s); s = re.sub(r"[^a-z# ]+", " ", s); return re.sub(r"\s+", " ", s).strip()


def main():
    docs = pd.read_csv(TAB / "corpus_docs_v3.csv"); sents = pd.read_csv(TAB / "corpus_sentences_v3.csv")
    docs["year"] = docs.date.str[:4].astype(int)
    # 1 inventory
    h("1. Inventory (documents by genre × year, all layers pooled)")
    inv = docs.drop_duplicates("doc_id").pivot_table(index="year", columns="doc_type", values="doc_id", aggfunc="count").fillna(0).astype(int)
    table(inv.reset_index())
    meeting_dates = json.loads((ROOT / "FOMC_corpus" / "_meta" / "meeting_dates.json").read_text())
    md = set()
    for m in meeting_dates:
        d = str(m.get("meeting_date", "")) if isinstance(m, dict) else str(m)
        if len(d) == 8: md.add(f"{d[:4]}-{d[4:6]}-{d[6:]}")
    st = docs[(docs.doc_type == "statement") & ~docs.doc_id.isin(EXCLUDE_DOCS)].drop_duplicates("doc_id")
    mn = docs[docs.doc_type == "minutes"].drop_duplicates("doc_id")
    st_dates, mn_dates = set(st.date), set(mn.date)
    L.append(""); L.append(f"- statements (post-meeting, after EXCLUDE_DOCS): {len(st)}; minutes: {len(mn)}; meeting dates in _meta: {len(md)}")
    only_st = sorted(st_dates - mn_dates); only_mn = sorted(mn_dates - st_dates)
    L.append(f"- statement dates without minutes ({len(only_st)}): {', '.join(only_st)}")
    L.append(f"- minutes dates without statement ({len(only_mn)}): {', '.join(only_mn)}")
    L.append("- (expected: unscheduled/emergency meetings such as 2020-03-03 and 2020-03-15 issue statements whose minutes are combined; minutes dated by the last meeting day may differ by one day from the statement date)")
    # 2 duplicates
    h("2. Duplicates and dates")
    hashes = {}
    for sub in ("statements", "minutes", "transcripts", "speeches"):
        for p in sorted((ROOT / "FOMC_corpus" / sub).glob("*.json")):
            r = json.loads(p.read_text()); hh = hashlib.md5(r["text"].encode()).hexdigest(); hashes.setdefault(hh, []).append(r["doc_id"])
    dups = [v for v in hashes.values() if len(v) > 1]
    L.append(f"- identical-text document groups: {len(dups)} {dups[:5]}")
    L.append(f"- duplicate doc_ids in corpus_docs_v3: {int(docs.drop_duplicates(['doc_id','layer']).duplicated(['doc_id','layer']).sum())}")
    bad = docs[~docs.date.str.match(r"^\d{4}-\d{2}-\d{2}$")]
    L.append(f"- unparseable dates: {len(bad)}")
    # 3 token outliers
    h("3. Token outliers per genre × layer (|z| > 3)")
    rows = []
    for (g, lay), s in docs.groupby(["doc_type", "layer"]):
        if len(s) < 10: continue
        z = (s.n_tokens - s.n_tokens.mean()) / s.n_tokens.std()
        for _, r in s[z.abs() > 3].iterrows():
            rows.append(dict(doc_type=g, layer=lay, doc_id=r.doc_id, n_tokens=r.n_tokens, z=round(float(z[_]), 2)))
    table(pd.DataFrame(rows))
    # 4 residue
    h("4. Residue in sentences")
    pats = {"encoding (â/Ã/�/Â)": r"â|Ã|�|Â", "Return to text": r"Return to text", "Watch Live / Share": r"^(Watch Live|Share)$",
            "page header": r"Page \d+ of \d+", "URL": r"https?://", "footnote digit glued": r"[a-z]\.\d{1,2}\s"}
    for name, pat in pats.items():
        hit = sents[sents.text.str.contains(pat, regex=True, na=False)]
        L.append(f"- {name}: {len(hit)} sentences" + (f" — e.g. {hit.text.iloc[0][:120]!r}" if len(hit) else ""))
    # 5 layer coverage
    h("5. Layer coverage")
    piv = docs[docs.doc_type == "minutes"].pivot_table(index="doc_id", columns="layer", values="n_tokens", aggfunc="sum").fillna(0)
    for lay in ["min_staff_desk", "min_staff", "min_participants", "min_committee", "min_statement_quote", "min_directive_quote", "min_vote"]:
        miss = piv.index[piv.get(lay, pd.Series(0, index=piv.index)) == 0].tolist()
        L.append(f"- minutes missing `{lay}`: {len(miss)} {miss[:8]}")
    log = json.loads((QA / "build_v3_log.json").read_text())
    unk = {}
    for k, v in log.items():
        for x in v.get("unknown_headings", []): unk[x] = unk.get(x, 0) + 1
    L.append(f"- unknown heading candidates in minutes (not used to switch layers; review): {sorted(unk.items(), key=lambda x: -x[1])[:20]}")
    pc = docs[docs.doc_type == "press_conf"].pivot_table(index="doc_id", columns="layer", values="n_tokens", aggfunc="sum").fillna(0)
    pc["journalist_share"] = pc.get("pc_journalist", 0) / pc.sum(axis=1)
    L.append(f"- press conferences: {len(pc)}; journalist token share mean {pc.journalist_share.mean():.3f} (min {pc.journalist_share.min():.3f}, max {pc.journalist_share.max():.3f}); docs with pc_pre > 60 tokens: {int((pc.get('pc_pre', 0) > 60).sum())}")
    spk = sorted({n for v in log.values() for n in v.get("speakers", [])})
    L.append(f"- distinct journalist/other speaker names: {len(spk)}; sample: {spk[:15]}")
    # 6 statement quote vs statement doc
    h("6. Quoted statement in minutes vs statement document (sentence-set Jaccard, same meeting)")
    sq = sents[sents.layer == "min_statement_quote"].groupby("date").text.apply(lambda s: set(map(norm_sent, s)))
    sd = sents[sents.layer == "statement"].groupby("date").text.apply(lambda s: set(map(norm_sent, s)))
    jac = []
    for d, a in sq.items():
        # statement may be dated the same day or the day before the minutes' meeting end date
        cands = [x for x in sd.index if abs((pd.Timestamp(x) - pd.Timestamp(d)).days) <= 1]
        if not cands: continue
        b = sd[cands[0]]; jac.append(dict(minutes_date=d, statement_date=cands[0], jaccard=round(len(a & b) / max(len(a | b), 1), 3), n_quote=len(a), n_stmt=len(b)))
    jd = pd.DataFrame(jac)
    if len(jd):
        L.append(f"- meetings compared: {len(jd)}; median Jaccard {jd.jaccard.median():.2f}; < 0.5: {int((jd.jaccard < .5).sum())}")
        table(jd.sort_values("jaccard").head(8)); jd.to_csv(QA / "QA_statement_quote_jaccard.csv", index=False)
    # 7 v2 vs v3
    h("7. v2 vs v3")
    if (TAB / "corpus_docs.csv").exists():
        v2 = pd.read_csv(TAB / "corpus_docs.csv"); v2 = v2[v2.date >= "2014-01-01"]; v3 = docs[docs.date >= "2014-01-01"]
        cmp = pd.DataFrame({"v2_tokens": v2.groupby("doc_type").n_tokens.sum(), "v3_tokens_all_layers": v3.groupby("doc_type").n_tokens.sum()})
        keep = v3[~v3.layer.isin(["statement_vote", "min_front_matter", "min_statement_quote", "min_directive_quote", "min_vote", "min_sep", "min_boilerplate", "pc_journalist", "pc_moderator", "pc_pre"])]
        cmp["v3_tokens_analysis_layers"] = keep.groupby("doc_type").n_tokens.sum(); cmp["retained_share"] = (cmp.v3_tokens_analysis_layers / cmp.v2_tokens).round(3)
        table(cmp.reset_index())
        if (TAB / "modal_tokens_v3.csv").exists() and (TAB / "modal_tokens.csv").exists():
            m2 = pd.read_csv(TAB / "modal_tokens.csv", low_memory=False, usecols=["doc_type", "date", "modal"]); m2 = m2[m2.date >= "2014-01-01"]
            m3 = pd.read_csv(TAB / "modal_tokens_v3.csv", low_memory=False, usecols=["doc_type", "date", "modal", "layer"]); m3 = m3[m3.date >= "2014-01-01"]
            six = ["will", "would", "could", "can", "should", "may"]
            c2 = m2[m2.modal.isin(six)].groupby("doc_type").size(); c3 = m3[m3.modal.isin(six)].groupby("doc_type").size()
            c3k = m3[m3.modal.isin(six) & ~m3.layer.isin(["statement_vote", "min_front_matter", "min_statement_quote", "min_directive_quote", "min_vote", "min_sep", "min_boilerplate", "pc_journalist", "pc_moderator", "pc_pre"])].groupby("doc_type").size()
            L.append(""); table(pd.DataFrame({"v2_six_modal": c2, "v3_all_layers": c3, "v3_analysis_layers": c3k}).reset_index())
            L.append(""); L.append("six-modal tokens by layer (v3, 2014–2026):")
            table(m3[m3.modal.isin(six)].groupby("layer").size().rename("n").reset_index().assign(label=lambda d: d.layer.map(LAYER_LABEL)))
    # 8 samples
    h("8. Human-validation samples")
    rng = np.random.RandomState(7)
    pcs = sents[sents.doc_type == "press_conf"]
    sample_docs = rng.choice(pcs.doc_id.unique(), 10, replace=False)
    rows = []
    for d in sample_docs:
        turns = pcs[pcs.doc_id == d].drop_duplicates("para_id")
        for _, r in turns.sample(min(20, len(turns)), random_state=7).sort_values("para_id").iterrows():
            rows.append(dict(doc_id=d, para_id=r.para_id, layer=r.layer, speaker=r.speaker, text=r.text[:140], human_ok=""))
    pd.DataFrame(rows).to_csv(QA / "sample_speaker_roles.csv", index=False)
    mns = sents[sents.doc_type == "minutes"]
    rows = []
    for d in rng.choice(mns.doc_id.unique(), 10, replace=False):
        for lay, s in mns[mns.doc_id == d].groupby("layer"):
            for _, r in s.sample(min(2, len(s)), random_state=7).iterrows():
                rows.append(dict(doc_id=d, layer=lay, section=r.section, text=r.text[:160], human_ok=""))
    pd.DataFrame(rows).to_csv(QA / "sample_minutes_layers.csv", index=False)
    L.append("- `results/qa/sample_speaker_roles.csv` (10 docs × 20 turns) and `results/qa/sample_minutes_layers.csv` (10 docs × 2 sentences per layer) — fill `human_ok` (1/0).")
    (QA / "QA_report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
