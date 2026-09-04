"""
10_build_corpus_v3.py — Layer-aware sentence corpus (Phase 10; replaces 00_build_corpus.py for v3).

What is new relative to v2 (docs/08 §3.2):
  * cleaning     : site navigation, page headers/footers, lone footnote digits, footnotes ("Return to text"),
                   speech reference lists and title blocks are removed; mojibake fixed with ftfy.
  * press_conf   : speaker-turn segmentation -> speaker_role in {chair, journalist, moderator, pre}.
  * minutes      : section attribution -> {front_matter, staff_desk, staff, participants, committee,
                   statement_quote, directive_quote, vote, special, sep, boilerplate}.
                   The verbatim statement quoted inside "Committee Policy Action" is separated so that it is
                   never double-counted against the statement genre.
  * statement    : "Voting for/against ..." paragraphs -> statement_vote (excluded from analysis).
  * speech       : chair_personal.
  * every sentence carries `layer` (genre x attribution key used by the scenario runner) and `n_tok`.

Outputs:
  results/tables/corpus_docs_v3.csv        one row per document x layer  (doc_id, doc_type, date, chair, layer, n_tokens, n_sents)
  results/tables/corpus_sentences_v3.csv   one row per sentence (doc_id, doc_type, date, chair, layer, section, speaker, para_id, sent_id, n_tok, text)
  results/qa/build_v3_log.json             per-document diagnostics (unknown headings, long pre-marker text, cuts applied)
"""
from __future__ import annotations
import json, re, csv, sys, time
from pathlib import Path
from collections import Counter, defaultdict
import spacy, ftfy

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "FOMC_corpus"
OUT = ROOT / "results" / "tables"; OUT.mkdir(parents=True, exist_ok=True)
QA = ROOT / "results" / "qa"; QA.mkdir(parents=True, exist_ok=True)
GENRES = {"statements": "statement", "minutes": "minutes", "transcripts": "press_conf", "speeches": "speech"}

# ----------------------------------------------------------------------------------------------
# generic cleaning
# ----------------------------------------------------------------------------------------------
HEADER_PATTERNS = [
    r"^\s*For release at .*$", r"^\s*Page \d+ of \d+\s*$", r"^\s*FINAL\s*$",
    r"^\s*Federal Reserve issues FOMC statement\s*$",
    r"^\s*(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(-\d{1,2})?, \d{4}\s*$",
    r"^\s*Transcript of Chair(man)? .* Press Conference\s*$",
    r"^\s*Chair(man)? .*’s Press Conference\s*$", r"^\s*Chair(man)? .*'s Press Conference\s*$",
    r"^\s*Last [Uu]pdate:.*$", r"^\s*Implementation Note issued .*$",
    r"^\s*\d{1,2}\s*$",                      # lone footnote-reference digits
]
HEADER_RE = [re.compile(p, re.I | re.M) for p in HEADER_PATTERNS]
NAV_LINES = {"share", "watch live", "print", "home", "search", "publications", "return to top", "return to text",
             "accessibility", "disclaimer", "foia", "contact us", "rss", "pdf reader", "linking policy",
             "website policies", "current faqs", "fomc minutes", "advanced search", "skip to content",
             "skip to main navigation", "skip to secondary navigation", "what's new", "what's next", "site map",
             "a-z index", "careers", "all videos", "faqs", "monetary policy", "federal open market committee",
             "about", "the fed", "news", "& events", "monetary", "policy", "banking", "information",
             "& regulation", "payment", "systems", "economic", "research", "& data", "consumer", "community",
             "development", "reporting", "forms", "·", ">", "|"}


def strip_footnotes(t: str) -> str:
    """Remove numbered footnotes that end in a 'Return to text' back-link."""
    lines = t.split("\n"); keep = [True] * len(lines)
    for i, l in enumerate(lines):
        if l.strip().lower() == "return to text":
            j = i
            while j >= 0 and i - j <= 40 and not re.match(r"^\s*\d{1,3}\.(\s|$)", lines[j]):
                j -= 1
            start = j if (j >= 0 and i - j <= 40) else i
            for k in range(start, i + 1):
                keep[k] = False
    return "\n".join(l for l, k in zip(lines, keep) if k)


def base_clean(t: str) -> str:
    t = ftfy.fix_text(t).replace("\r", "")
    t = strip_footnotes(t)
    for rx in HEADER_RE:
        t = rx.sub("", t)
    out = []
    for line in t.split("\n"):
        s = line.strip()
        if s.lower() in NAV_LINES:
            continue
        if re.fullmatch(r"_{5,}", s):
            continue
        out.append(line)
    t = "\n".join(out)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def paragraphs(t: str) -> list[str]:
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


# ----------------------------------------------------------------------------------------------
# minutes: section attribution
# ----------------------------------------------------------------------------------------------
PRIMARY = [
    (re.compile(r"^(Developments in Financial Markets|Discussion of Financial Markets|Financial Developments and Open Market)", re.I), "staff_desk"),
    (re.compile(r"^Staff Review of", re.I), "staff"),
    (re.compile(r"^Staff Economic Outlook", re.I), "staff"),
    (re.compile(r"^Participants['’] Views?", re.I), "participants"),
    (re.compile(r"^Committee Policy Actions?$", re.I), "committee"),
    (re.compile(r"^(Voting|Votes?) (for|against)", re.I), "vote"),
    (re.compile(r"^Notation Votes?", re.I), "boilerplate"),
    (re.compile(r"^Summary of Economic Projections$", re.I), "sep"),
    (re.compile(r"^(Annual Organizational Matters|Selection of Committee Officers?|AUTHORIZATION FOR|"
                r"FOREIGN CURRENCY DIRECTIVE|STATEMENT ON LONGER-RUN|PROCEDURAL INSTRUCTIONS|ADDITIONAL MATTERS|"
                r"Program for Security|Rules|Guidelines|Domestic Policy Directive|RESOLUTION|Resolution)", re.I), "boilerplate"),
]
SPECIAL = re.compile(r"^(Discussion|Review|Update|Special Topic|Consideration|Briefing|Monetary Policy|Long-Run|"
                     r"Longer-Run|Balance Sheet|System Open Market Account|Consensus Forecast|Potential Enhancements|"
                     r"Policy Normalization|Options|Assessment|Framework|Principles|Plans|Reinvestment|Overview|"
                     r"Report|Presentation|Approaches|Implications|Economic Projections|Communications|Strategy|"
                     r"Statement on|Federal Reserve['’]s Balance Sheet|Liftoff|Enhanced|Alternative|Summary of)", re.I)
PERSON_RE = re.compile(r"^[A-Z][a-z]+(?: [A-Z]\.)?(?: [A-Z][a-zA-Z'’\-]+){1,2}(?:,? (Jr\.|II|III))?$")


def minutes_layers(t: str, log: dict) -> list[tuple[str, str, str]]:
    """Return [(layer, section_heading, paragraph)] for a minutes document."""
    m = re.search(r"A (joint )?meeting of the Federal Open Market Committee", t)
    if m:
        t = t[m.start():]; log["cut_head"] = True
    # tail cut: signature / site footer
    for pat in (r"\n\s*Return to top\s*\n", r"\n\s*_{5,}\s*\n"):
        mm = re.search(pat, t)
        if mm and mm.start() > 0.5 * len(t):
            t = t[:mm.start()]; log["cut_tail"] = pat
    paras = paragraphs(t)
    layer, section = "front_matter", "front_matter"
    out = []; in_quote = False; embedded = False; quote_label = None; prev = ""
    VOTE_RE = re.compile(r"^(Voting|Votes?) (for|against)", re.I)
    for p in paras:
        head = None
        words = p.split()
        if VOTE_RE.match(p):
            head = "vote"                      # hard reset, regardless of length or open quotes
        elif not in_quote and len(words) <= 15 and not p.endswith((".", ";", ",", ")")):
            for rx, lab in PRIMARY:
                if rx.search(p):
                    head = lab; break
            if head is None and layer != "committee" and SPECIAL.search(p) and len(words) >= 2 and not PERSON_RE.match(p):
                head = "special"
        if head is not None:
            layer, section = head, p[:80]
            in_quote = False
            out.append((layer, section, p))  # keep the heading line (rarely contains a modal; filtered by length later)
            prev = p
            continue
        lab = layer
        if layer == "committee":
            starts_q = p.startswith(("\"", "“"))
            # embedded adopted documents (ALL-CAPS title, e.g. PLANS FOR REDUCING THE SIZE OF ... BALANCE SHEET)
            if not in_quote and not embedded and p.isupper() and len(words) >= 3:
                embedded = True
            if embedded and (starts_q or p.startswith(("After adopting", "The vote", "Following", "In their", "Members"))):
                embedded = False
            if embedded:
                out.append(("directive_quote", section, p)); prev = p
                continue
            if not in_quote and starts_q:
                in_quote = True
                pl = prev.lower()
                quote_label = "statement_quote" if ("statement" in pl and "directive" not in pl) else "directive_quote"
            if in_quote:
                lab = quote_label
                if p.endswith(("\"", "”", "\".", "”.")):
                    in_quote = False
        else:
            # unknown heading candidates are logged for review (do not switch layer)
            if len(words) <= 10 and not p.endswith((".", ":", ";", ",")) and p[:1].isupper() and not PERSON_RE.match(p) \
                    and not re.search(r"\d", p) and "," not in p and len(words) >= 2:
                log.setdefault("unknown_headings", []).append(p)
        out.append((lab, section, p))
        prev = p
    return out


# ----------------------------------------------------------------------------------------------
# press conference: speaker turns
# ----------------------------------------------------------------------------------------------
MODERATORS = ("MICHELLE SMITH", "MICHELE SMITH")


def speaker_of(line: str):
    """Return (name, rest) if the line starts with a speaker marker like 'CHAIR POWELL. ...' else None."""
    m = re.match(r"^\s*([^.:]{4,50}?)[.:]\s+(\S.*)$", line)
    if not m:
        return None
    name = m.group(1).strip()
    letters = [c for c in name if c.isalpha()]
    if len(letters) < 4 or len(name.split()) > 5:
        return None
    if sum(c.isupper() for c in letters) / len(letters) < 0.7:
        return None
    return name, m.group(2)


def role_of(name: str) -> str:
    u = name.upper()
    if u.startswith(("CHAIR", "VICE CHAIR")):
        return "chair"
    if any(mod in u for mod in MODERATORS):
        return "moderator"
    return "journalist"


def transcript_turns(t: str, log: dict) -> list[tuple[str, str, str]]:
    """Return [(role, speaker_name, turn_text)]; transcripts are hard-wrapped, so lines are joined with spaces."""
    turns = []; cur_role, cur_name, buf = "pre", "", []
    for line in t.split("\n"):
        if not line.strip():
            continue
        sp = speaker_of(line)
        if sp:
            if buf:
                turns.append((cur_role, cur_name, " ".join(buf)))
            cur_name, rest = sp; cur_role = role_of(cur_name); buf = [rest]
        else:
            buf.append(line.strip())
    if buf:
        turns.append((cur_role, cur_name, " ".join(buf)))
    pre_words = sum(len(x[2].split()) for x in turns if x[0] == "pre")
    if pre_words > 60:
        log["long_pre_marker_text"] = pre_words
    log["n_turns"] = Counter(r for r, _, _ in turns)
    log["speakers"] = sorted(set(n for r, n, _ in turns if r == "journalist"))[:50]
    return turns


# ----------------------------------------------------------------------------------------------
# speeches
# ----------------------------------------------------------------------------------------------
def speech_body(t: str, log: dict) -> list[str]:
    mm = re.search(r"(?m)^\s*(References|REFERENCES|Bibliography)\s*$", t)
    if mm and mm.start() > 0.4 * len(t):
        t = t[:mm.start()]; log["cut_references"] = True
    paras = paragraphs(t)
    # drop the title block: leading paragraphs that do not end like a sentence
    i = 0
    while i < len(paras) and not re.search(r"[.?!][\"”’')]*$", paras[i]):
        i += 1
    log["title_paras_dropped"] = i
    return paras[i:]


# ----------------------------------------------------------------------------------------------
def main():
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    nlp.max_length = 2_000_000
    docs_rows, sent_rows, logs = [], [], {}
    t0 = time.time()
    paths = [(p, g) for sub, g in GENRES.items() for p in sorted((CORPUS / sub).glob("*.json"))]
    for i, (p, genre) in enumerate(paths, 1):
        rec = json.loads(p.read_text())
        log = {}
        text = base_clean(rec["text"])
        units = []  # (layer, section, speaker, paragraph)
        if genre == "statement":
            for para in paragraphs(text):
                lab = "statement_vote" if re.match(r"^Voting (for|against)", para) else "statement"
                units.append((lab, "", "", para))
        elif genre == "minutes":
            for lab, sec, para in minutes_layers(text, log):
                units.append((f"min_{lab}", sec, "", para))
        elif genre == "press_conf":
            for role, name, turn in transcript_turns(text, log):
                units.append((f"pc_{role}", "", name, turn))
        else:
            for para in speech_body(text, log):
                units.append(("speech_chair", "", rec.get("speaker", rec.get("chair")) or "", para))
        # sentence split per unit
        per_layer_tok, per_layer_sent = Counter(), Counter()
        sid = 0
        for pid, (doc, (lab, sec, spk, para)) in enumerate(zip(nlp.pipe([u[3] for u in units], batch_size=64), units)):
            for s in doc.sents:
                txt = re.sub(r"\s+", " ", s.text).strip()
                if len(txt.split()) < 3:
                    continue
                ntok = sum(1 for tk in s if not tk.is_space and not tk.is_punct)
                sent_rows.append(dict(doc_id=rec["doc_id"], doc_type=genre, date=rec["date"], chair=rec.get("chair"),
                                      layer=lab, section=sec, speaker=spk, para_id=pid, sent_id=sid, n_tok=ntok, text=txt))
                per_layer_tok[lab] += ntok; per_layer_sent[lab] += 1; sid += 1
        for lab in per_layer_tok:
            docs_rows.append(dict(doc_id=rec["doc_id"], doc_type=genre, date=rec["date"], chair=rec.get("chair"),
                                  layer=lab, n_tokens=per_layer_tok[lab], n_sents=per_layer_sent[lab]))
        if log:
            log = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in log.items()}
            logs[rec["doc_id"]] = log
        if i % 50 == 0 or i == len(paths):
            print(f"[{i}/{len(paths)}] {time.time()-t0:.0f}s {p.name}", file=sys.stderr)
    with (OUT / "corpus_docs_v3.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(docs_rows[0].keys())); w.writeheader(); w.writerows(docs_rows)
    with (OUT / "corpus_sentences_v3.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sent_rows[0].keys())); w.writeheader(); w.writerows(sent_rows)
    (QA / "build_v3_log.json").write_text(json.dumps(logs, indent=1, ensure_ascii=False))
    print(f"docs x layers={len(docs_rows)} sentences={len(sent_rows)} in {time.time()-t0:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
