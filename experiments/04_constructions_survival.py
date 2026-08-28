"""
04_constructions_survival.py — Experiment B/half-life: formulaic sentences, construction cohorts, survival.

Statements only (2014–2026, meeting-ordered).
1. Sentence reuse: for each modal-bearing sentence, normalised key; recurrence across statements;
   "formulaic" = appears (near-)verbatim in >= 3 statements.
2. Boilerplate table: modal sentences recurring in >= 5 statements, with first/last date, run length, modals inside.
3. Construction cohorts: (modal, head_verb) pairs; first appearance meeting; survival = number of consecutive
   later meetings in which the pair still appears (death = first meeting absent; right-censored at end).
   Kaplan–Meier per modal → median survival (half-life in meetings).
4. Decomposition: share of each modal's tokens that sit in formulaic sentences, by year.
5. Edit events: for each consecutive pair of statements, sentences added / removed and the modals they carry.
Outputs: C1_statement_sentence_reuse.csv, C2_boilerplate_modal_sentences.csv, C3_construction_cohorts.csv,
         C4_km_survival_by_modal.csv, C5_formulaic_share_by_year.csv, C6_edit_events.csv
Figures: C_fig1_km_survival.png, C_fig2_formulaic_vs_novel.png, C_fig3_edit_events.png
"""
from __future__ import annotations
import re, difflib, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\d+(\.\d+)?", "#", s)            # numbers → #
    s = re.sub(r"[^a-z# ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def km(durations, events):
    """Kaplan–Meier estimator. durations: array of meetings survived; events: 1=died, 0=censored."""
    d = np.asarray(durations); e = np.asarray(events)
    times = np.sort(np.unique(d[e == 1]))
    S = 1.0; out = [(0, 1.0)]
    for t in times:
        at_risk = np.sum(d >= t); died = np.sum((d == t) & (e == 1))
        if at_risk == 0: continue
        S *= (1 - died / at_risk); out.append((t, S))
    return pd.DataFrame(out, columns=["t", "S"])

def median_survival(kmdf):
    below = kmdf[kmdf.S <= 0.5]
    return float(below["t"].iloc[0]) if len(below) else np.inf

def main():
    df = load_modals(); df = df[df.doc_type == "statement"]
    docs = load_docs(); docs = docs[docs.doc_type == "statement"].sort_values("date").reset_index(drop=True)
    order = {d: i for i, d in enumerate(docs["doc_id"])}
    dates = dict(zip(docs["doc_id"], docs["date"]))
    df = df.assign(midx=df["doc_id"].map(order)).sort_values(["midx", "sent_id"])
    df["key"] = df["sentence"].map(norm)

    # ---- 1. sentence reuse (modal-bearing sentences, unique per doc)
    sent = df.drop_duplicates(["doc_id", "sent_id"])[["doc_id", "midx", "date", "sent_id", "sentence", "key"]]
    # fuzzy-merge keys: map each key to a canonical key if similarity >= 0.85 with an earlier canonical key
    canon = {}; canon_list = []
    for k in sent.sort_values("midx")["key"]:
        if k in canon: continue
        match = None
        for c in canon_list:
            if abs(len(c) - len(k)) / max(len(c), 1) < 0.3 and difflib.SequenceMatcher(None, c, k).ratio() >= 0.85:
                match = c; break
        canon[k] = match or k
        if match is None: canon_list.append(k)
    sent["canon"] = sent["key"].map(canon)
    rec = sent.groupby("canon").agg(n_statements=("doc_id", "nunique"), first=("date", "min"), last=("date", "max"),
                                    example=("sentence", "first")).reset_index()
    sent = sent.merge(rec[["canon", "n_statements"]], on="canon")
    sent["formulaic"] = sent["n_statements"] >= 3
    sent.to_csv(TAB / "C1_statement_sentence_reuse.csv", index=False)

    # modals within each canonical sentence
    mods = df.merge(sent[["doc_id", "sent_id", "canon"]], on=["doc_id", "sent_id"])
    mod_by_canon = mods.groupby("canon")["modal"].agg(lambda s: ",".join(sorted(set(s))))
    rec["modals"] = rec["canon"].map(mod_by_canon)
    # run structure: consecutive-meeting runs
    runs = []
    for c, sub in sent.groupby("canon"):
        idx = sorted(sub["midx"].unique())
        n_runs = 1 + sum(1 for a, b in zip(idx, idx[1:]) if b - a > 1)
        runs.append((c, n_runs, len(idx)))
    runs = pd.DataFrame(runs, columns=["canon", "n_runs", "n_meetings"])
    rec = rec.merge(runs, on="canon")
    boiler = rec[rec.n_statements >= 5].sort_values("n_statements", ascending=False)
    boiler.to_csv(TAB / "C2_boilerplate_modal_sentences.csv", index=False)

    # ---- 3. construction cohorts (modal, head_verb) with survival
    pairs = df.groupby(["midx", "modal", "head_verb"]).size().reset_index(name="n")
    present = pairs.groupby(["modal", "head_verb"])["midx"].agg(set)
    last_m = docs.index.max()
    rows = []
    for (m, v), ms in present.items():
        ms = sorted(ms)
        # cohorts: each entry (first meeting of a run) is a cohort; survival = run length
        runs_ = []; start = ms[0]; prev = ms[0]
        for x in ms[1:]:
            if x == prev + 1: prev = x
            else: runs_.append((start, prev)); start = x; prev = x
        runs_.append((start, prev))
        for s, e in runs_:
            dur = e - s + 1            # meetings survived incl. first
            censored = (e == last_m)
            rows.append(dict(modal=m, head_verb=v, start_midx=s, start_date=dates[docs.loc[s, "doc_id"]],
                             end_midx=e, end_date=dates[docs.loc[e, "doc_id"]], duration=dur, event=int(not censored)))
    coh = pd.DataFrame(rows); coh.to_csv(TAB / "C3_construction_cohorts.csv", index=False)

    kmrows = []; kmcurves = {}
    for m in SIX:
        sub = coh[coh.modal == m]
        if len(sub) < 3: continue
        k = km(sub["duration"], sub["event"]); kmcurves[m] = k
        kmrows.append(dict(modal=m, n_cohorts=len(sub), n_events=int(sub.event.sum()),
                           median_survival_meetings=median_survival(k),
                           mean_duration=round(sub.duration.mean(), 2), max_duration=int(sub.duration.max()),
                           share_one_off=round((sub.duration == 1).mean(), 3)))
    # also all constructions pooled
    k_all = km(coh["duration"], coh["event"]); kmcurves["all"] = k_all
    kmrows.append(dict(modal="ALL", n_cohorts=len(coh), n_events=int(coh.event.sum()), median_survival_meetings=median_survival(k_all),
                       mean_duration=round(coh.duration.mean(), 2), max_duration=int(coh.duration.max()), share_one_off=round((coh.duration == 1).mean(), 3)))
    kmdf = pd.DataFrame(kmrows); kmdf.to_csv(TAB / "C4_km_survival_by_modal.csv", index=False)

    # ---- 4. formulaic share by year and modal
    mods = mods.merge(sent[["doc_id", "sent_id", "formulaic"]], on=["doc_id", "sent_id"])
    fs = mods.groupby(["year", "modal"]).agg(n=("modal", "size"), formulaic=("formulaic", "sum")).reset_index()
    fs["formulaic_share"] = fs["formulaic"] / fs["n"]
    fs.to_csv(TAB / "C5_formulaic_share_by_year.csv", index=False)

    # ---- 5. edit events between consecutive statements
    ev = []
    by_doc = {d: set(sub["canon"]) for d, sub in sent.groupby("doc_id")}
    canon_mod = mod_by_canon.to_dict()
    for i in range(1, len(docs)):
        a, b = docs.loc[i-1, "doc_id"], docs.loc[i, "doc_id"]
        added = by_doc.get(b, set()) - by_doc.get(a, set()); removed = by_doc.get(a, set()) - by_doc.get(b, set())
        for c in added:
            ev.append(dict(date=dates[b], kind="added", modals=canon_mod.get(c, ""), sentence=rec.set_index("canon").loc[c, "example"][:300]))
        for c in removed:
            ev.append(dict(date=dates[b], kind="removed", modals=canon_mod.get(c, ""), sentence=rec.set_index("canon").loc[c, "example"][:300]))
    evdf = pd.DataFrame(ev); evdf.to_csv(TAB / "C6_edit_events.csv", index=False)

    # ---- figures
    fig, ax = plt.subplots(figsize=(8, 5))
    for m, k in kmcurves.items():
        ax.step(k["t"], k["S"], where="post", label=f"{m} (median={median_survival(k):.0f})", lw=2 if m == "all" else 1.2, color="black" if m == "all" else None)
    ax.axhline(0.5, color="grey", ls=":"); ax.set_xlabel("consecutive meetings survived"); ax.set_ylabel("S(t)")
    ax.set_title("Kaplan–Meier survival of modal + verb constructions in FOMC statements (2014–2026)"); ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(FIG / "C_fig1_km_survival.png", dpi=160); plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(14, 7), sharex=True)
    for ax, m in zip(axes.flat, SIX):
        sub = fs[fs.modal == m].set_index("year").reindex(range(2014, 2027)).fillna(0)
        ax.bar(sub.index, sub["formulaic"], label="in formulaic sentences (≥3 statements)", color="#4c72b0")
        ax.bar(sub.index, sub["n"] - sub["formulaic"], bottom=sub["formulaic"], label="in novel sentences", color="#dd8452")
        ax.set_title(m); ax.grid(alpha=.3, axis="y")
    axes[0, 0].legend(fontsize=7); fig.suptitle("Modal tokens in FOMC statements: formulaic vs novel sentences, by year")
    fig.tight_layout(); fig.savefig(FIG / "C_fig2_formulaic_vs_novel.png", dpi=160); plt.close(fig)

    if len(evdf):
        e2 = evdf.assign(year=evdf["date"].str[:4].astype(int)).groupby(["year", "kind"]).size().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(10, 4)); e2.plot(kind="bar", ax=ax); ax.set_title("Modal-bearing sentences added / removed between consecutive statements")
        ax.grid(alpha=.3, axis="y"); fig.tight_layout(); fig.savefig(FIG / "C_fig3_edit_events.png", dpi=160); plt.close(fig)

    print("KM survival by modal:"); print(kmdf.to_string(index=False))
    print("\nTop boilerplate modal sentences:"); print(boiler[["n_statements", "first", "last", "n_runs", "modals", "example"]].head(25).to_string(index=False, max_colwidth=110))
    print("\nFormulaic share by year (statements):"); print(fs.pivot(index="year", columns="modal", values="formulaic_share").round(2).to_string())

if __name__ == "__main__":
    main()
