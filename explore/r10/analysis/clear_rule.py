"""The clear-request rule: do the traveller's own words state the venue type? Post hoc. Words only.

Why. Reviewers ask for a measure of the "guess" reading: the renamed value acts mainly when the dialogue leaves the
type open. Their test marks the requests whose words state the type, and reports the correct-side effect separately
for clear and unclear requests. This module is that mark. clear_split.py applies it.

What the rule reads. Only the traveller turns (even log indexes) of the MultiWOZ text that the model saw: the full
dialogue, or the prefix up to and including the first traveller turn that says "hotel". It reads no brief, no gold
state, no model answer, and no sealed file. It was written and fixed before any split by it was computed:
out/clear_rule.md records the SHA-256 of this file, and clear_split.py stops when the file differs.

Labels of a dialogue or a prefix:
- "hotel_only": a traveller sentence requires a hotel or excludes the guesthouse kinds, and no sentence does the
  mirror.
- "guesthouse_only": a traveller sentence requires a guesthouse kind or excludes hotels, and no sentence does the
  mirror.
- "mixed": sentences of both kinds (for example, the traveller changes the type).
- "unclear": no sentence matches.
The guesthouse kinds are guesthouse, guest house, B&B, bed and breakfast, and hostel.

How. A traveller turn is split into sentences. Each pattern runs on one sentence. The four pattern families:
- E, exclusion: the sentence rejects the other kind. Examples: "a hotel, not a guesthouse", "I don't want a
  guesthouse", "rather than a guesthouse", "No guesthouses.", "I hate guesthouses".
- R, restriction: "only hotels", "hotels only", "an actual hotel", "a proper hotel", "a regular hotel".
- P, predicate: the sentence says what the venue must be. Examples: "it has to be a hotel", "it should be a hotel",
  "I'd like it to be a hotel", "make sure it's a hotel", "as long as it is a hotel", "a place that is a hotel".
- T, type word: the sentence names the kind as a type. Examples: "a hotel type", "in the type of hotel", "my
  preferred type is a hotel".
The plain head noun never matches. Examples: "I need a hotel", "a cheap hotel in the north", "I prefer a hotel".
MultiWOZ travellers use that form also when they book a guesthouse, so it does not state the type.

Guards. A match does not count when:
- the sentence is a yes/no question about a venue: it ends with "?" and starts with "is", "isn't", "was", "am", or
  "are they / those / these / any of" ("Is that an actual hotel?");
- (P) a negation comes just before it ("it doesn't have to be a hotel", "it does not need to be a guesthouse");
- (P1) its subject is a person ("I need to be in a hotel" is a plain request);
- (R, P, T) the kind word is followed by "or <other kind>", "that is <other kind>", or "if" ("it should be a hotel
  or a guesthouse", "a hotel type that is a guesthouse", "I only want a guesthouse if ...");
- (R1) it follows "the" ("the only hotel in the area");
- (E1) it follows "there is" or "there are" ("if there is not a guesthouse ..." is about the results);
- (E) the sentence names another domain (restaurant, attraction, train, taxi, ...) and no venue kind before the match
  ("I'm looking for a restaurant, not a hotel").

Known limit. The rule reads traveller words only. A short answer to an assistant's type question ("A hotel, please."
after "A hotel or a guesthouse?") stays "unclear".

The pre-declared secondary rule `strict` uses the E and R families only (P and T leave). It shows whether the split
depends on the predicate and type-word patterns.

Usage (from explore/): .venv/bin/python -I r10/analysis/clear_rule.py   (writes out/clear_rule.md; no model call)
"""
import collections
import datetime
import hashlib
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
DOC = OUT / "clear_rule.md"
SEED = 20261112
LABELS = ("hotel_only", "guesthouse_only", "mixed", "unclear")

KIND = {
    "hotel": r"hotels?",
    "guesthouse": r"(?:guest ?houses?|b ?& ?bs?|b and bs?|bed and breakfasts?|hostels?)",
}
SIDE = {"hotel": "hotel_only", "guesthouse": "guesthouse_only"}
OTHER = {"hotel": "guesthouse", "guesthouse": "hotel"}
STRICT_FAMILIES = ("E", "R")

ART = r"(?:an?\s+|in\s+an?\s+|at\s+an?\s+)?"
ADJ = r"(?:actual\s+|proper\s+|real\s+)?"
END = r"(?=\s*(?:[.,;:!?)]|please\b|thanks?\b|$))"

# (name, family, template). {want} is the kind that the sentence requires; {other} is the kind that it excludes.
PATTERNS = (
    ("E1_not_other", "E", r"(?:\bnot|\b(?:is|was|are|were)n't)\s+" + ART + r"{other}\b"),
    ("E2_dont_want_other", "E", r"(?:\bnot|n't|\bnever)\s+(?:really\s+|even\s+|particularly\s+)?"
                                r"(?:want|like|care\s+for|wish)\w*\s+(?:to\s+(?:stay|be|sleep)\s+(?:in|at)\s+)?"
                                r"(?:an?\s+|any\s+)?{other}\b"),
    ("E3_dislike_other", "E", r"(?:\b(?:hates?|dislikes?|detest|avoid)\s+(?:\w+\s+){{0,2}}?"
                              r"|\bnot\s+(?:too\s+|very\s+|really\s+|a\s+big\s+|much\s+of\s+)?"
                              r"(?:fond\s+of|a\s+fan\s+of|interested\s+in|keen\s+on)\s+(?:\w+\s+){{0,3}}?){other}\b"),
    ("E4_rather_than_other", "E", r"\b(?:rather\s+than|instead\s+of|as\s+opposed\s+to)\s+"
                                  r"(?:(?:stay(?:ing)?|be(?:ing)?)\s+(?:in|at)\s+)?" + ART + r"{other}\b"),
    ("E5_no_other", "E", r"(?:^|[.,;:!(]\s*|\b(?:and|but|please,?)\s+)no\s+{other}" + END),
    ("R1_only_want", "R", r"\b(?:only|strictly|exclusively)\s+(?:(?:want|consider|book|stay|look|search|check)\w*\s+"
                          r"(?:to\s+(?:stay|book)\s+)?(?:in\s+|at\s+|for\s+)?|for\s+|in\s+)?(?:an?\s+)?{want}\b"),
    ("R2_want_only", "R", r"\b{want}\s+only" + END),
    ("R3_actual_want", "R", r"\b(?:actual|proper|real|regular|true|traditional|normal|full[- ]service)\s+{want}\b"),
    ("P1_must_be_want", "P", r"\b(?:has\s+to|have\s+to|needs?\s+to|must|should|will\s+need\s+to|would\s+need\s+to|"
                             r"(?:has\s+|have\s+)?got\s+to|ought\s+to)\s+(?:also\s+|definitely\s+|really\s+|"
                             r"absolutely\s+)?be\s+" + ART + ADJ + r"{want}\b"),
    ("P2_want_it_to_be_want", "P", r"\b(?:want|like|need|prefer|require|wish)\w*\s+(?:for\s+)?"
                                   r"(?:it|the\s+(?:hotel|place|lodging|accommodations?|room))\s+to\s+"
                                   r"(?:also\s+|definitely\s+)?be\s+" + ART + ADJ + r"{want}\b"),
    ("P3_make_sure_it_is_want", "P", r"\b(?:make\s+sure|making\s+sure|as\s+long\s+as|so\s+long\s+as|provided)\s+"
                                     r"(?:that\s+)?(?:it|this|that|the\s+place|the\s+hotel)\s*"
                                     r"(?:'s|s|\s+is|\s+will\s+be|\s+would\s+be)\s+" + ART + ADJ + r"{want}\b"),
    ("P4_that_is_want", "P", r"\b(?:that|which|and)\s+(?:is|'s)\s+(?:also\s+)?(?:an?\s+)?(?:actual\s+)?{want}\b"),
    ("T1_kind_type", "T", r"\ban?\s+(?:(?!(?:the|of|their|its|this|that)\b)[\w-]+\s+){{0,3}}?{want}[- ]type\b"),
    ("T2_in_the_type_of", "T", r"\b(?:in|of)\s+the\s+type\s+of\s+(?:an?\s+)?{want}\b"),
    ("T3_type_is", "T", r"\btype\s+(?:should|must|needs\s+to|has\s+to|would\s+need\s+to|is)\s+(?:be\s+)?"
                        r"(?:an?\s+)?{want}\b"),
)
FAMILY = {name: fam for name, fam, _ in PATTERNS}
COMPILED = {(want, name): re.compile(tpl.format(want=KIND[want], other=KIND[OTHER[want]]), re.I)
            for want in KIND for name, _, tpl in PATTERNS}

SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
VENUE_QUESTION = re.compile(r"^\W*(?:so\s+|and\s+|also,?\s+)?(?:is|isn't|was|am|are\s+(?:they|those|these|any\s+of))\b",
                            re.I)
NEGATED = re.compile(r"(?:n't|\bnot|\bnever)\s+(?:\w+\s+)?$", re.I)
PERSON = re.compile(r"\b(?:i|we|you|they|he|she)(?:'d|'ll)?\s+(?:\w+\s+)?$", re.I)
THERE = re.compile(r"\bthere\s*(?:is|are|was|were|'s)?\s*$", re.I)
THE = re.compile(r"\bthe\s+$", re.I)
ANY_KIND = re.compile(r"\b(?:" + KIND["hotel"] + "|" + KIND["guesthouse"] + r")\b", re.I)
DOMAIN = re.compile(r"\b(?:restaurant|attraction|train|taxi|museum|college|food|place\s+to\s+eat)s?\b", re.I)


# ------------------------------------------------------------------------------------------------------- the rule
def sentences(text):
    """The sentences of one turn, with curly quotes made plain."""
    text = text.replace("’", "'").replace("‘", "'")
    return [s.strip() for s in SENTENCE.split(text) if s and s.strip()]


def _guarded(name, want, sentence, m):
    """True when a guard of the module docstring removes the match `m` of pattern `name`."""
    before, after = sentence[:m.start()], sentence[m.end():]
    fam = FAMILY[name]
    if fam == "E":
        return bool(DOMAIN.search(before) and not ANY_KIND.search(before)) or (
            name == "E1_not_other" and bool(THERE.search(before)))
    other = re.compile(r"^\s+(?:or|(?:that|which)\s+is)\s+(?:an?\s+)?" + KIND[OTHER[want]] + r"\b", re.I)
    if other.search(after) or re.match(r"^\s+if\b", after, re.I):
        return True
    if fam == "P" and NEGATED.search(before):
        return True
    if name == "P1_must_be_want" and PERSON.search(before):
        return True
    if name == "R1_only_want" and THE.search(before):
        return True
    return False


def sentence_matches(sentence):
    """[(want, pattern name)] for one sentence; empty for a guarded yes/no venue question."""
    if sentence.rstrip().endswith("?") and VENUE_QUESTION.search(sentence):
        return []
    out = []
    for (want, name), rx in COMPILED.items():
        if any(not _guarded(name, want, sentence, m) for m in rx.finditer(sentence)):
            out.append((want, name))
    return out


def traveller_turns(d, prefix_end=None):
    """The traveller turns (even log indexes) up to and including log index `prefix_end` (None: the full log)."""
    log = d["log"] if prefix_end is None else d["log"][:prefix_end + 1]
    return [(i, t["text"]) for i, t in enumerate(log) if i % 2 == 0]


def matches(d, prefix_end=None):
    """[(turn index, sentence, want, pattern name)] over the traveller turns of the text."""
    out = []
    for i, text in traveller_turns(d, prefix_end):
        for s in sentences(text):
            out += [(i, s, want, name) for want, name in sentence_matches(s)]
    return out


def label_of(found, families=None):
    """The label of a list of matches, using only the named pattern families (None: all)."""
    sides = {SIDE[want] for _, _, want, name in found if families is None or FAMILY[name] in families}
    if len(sides) == 2:
        return "mixed"
    return sides.pop() if sides else "unclear"


def label(d, prefix_end=None):
    """The main label of a dialogue (prefix_end None) or of a prefix."""
    return label_of(matches(d, prefix_end))


def label_strict(d, prefix_end=None):
    """The pre-declared secondary label: families E and R only."""
    return label_of(matches(d, prefix_end), STRICT_FAMILIES)


def file_sha256():
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------------- the sets
SET_TEXT = {
    "a_hotel": "Source 1, tool calls at the first request: prefixes whose brief sets `type` = hotel",
    "a_no_type": "Source 1, tool calls at the first request: prefixes whose brief sets no type",
    "b_hotel": "Source 2, round-9 form runs: S2 full dialogues whose brief sets `type` = hotel",
    "b_no_type": "Source 2, round-9 form runs: S1t full dialogues whose brief sets no type",
    "c_hotel": "Source 3, held-out test stage 1: goal-hotel sample, full dialogues",
    "c_no_type": "Source 3, held-out test stage 1: natural sample (the goal sets no type), full dialogues",
}


def sets():
    """(data, {set name: [(dialogue id with .json, prefix_end or None)]}). Corpus text and briefs only. Source 3 takes
    the stage-1 dialogues of main/exp0/analysis.stage1_units, so no Track P sample (second look) dialogue enters."""
    explore = HERE.parents[1]
    for sub in ("lib", "forms", "pmain", "trackc", "r9", "r9/natural", "r9/additions", "r9/free", "main", "r10"):
        sys.path.insert(0, str(explore / sub))
    sys.path.insert(0, str(explore / "main" / "exp0"))
    sys.path.insert(0, str(HERE))
    import analysis  # noqa: E402  (main/exp0/analysis.py; only stage1_units)
    import briefsearch as bs  # noqa: E402
    import gold  # noqa: E402
    import natural  # noqa: E402
    import runs  # noqa: E402
    import wave1  # noqa: E402
    import zforms  # noqa: E402
    data, g = runs.context()
    booked = list(g["booked"])
    no_type = set(bs.brief_subsets(data, booked, gold.hotel_db())["no_type"])
    nat = natural.ids()
    units, _ = analysis.stage1_units(wave1.ids())
    none = lambda d: gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None
    out = {
        "a_hotel": [(d, zforms.prefix_end(data[d])) for d in booked if gold.brief_type(data[d]) == "hotel"],
        "a_no_type": [(d, zforms.prefix_end(data[d])) for d in booked if d in no_type],
        "b_hotel": [(d, None) for d in nat["S2"] if gold.brief_type(data[d]) == "hotel"],
        "b_no_type": [(d, None) for d in nat["S1t"] if none(d)],
        "c_hotel": [(d + ".json", None) for d in units["goal_hotel"]],
        "c_no_type": [(d + ".json", None) for d in units["natural"]],
    }
    sizes = {k: len(v) for k, v in out.items()}
    assert sizes == {"a_hotel": 59, "a_no_type": 448, "b_hotel": 233, "b_no_type": 807, "c_hotel": 77,
                     "c_no_type": 213}, sizes
    return data, out


# ---------------------------------------------------------------------------------------------------- the record
def describe(data, units):
    """Label counts, dialogues per pattern, and the matched and unmatched sentences of one set."""
    labels, strict, per = collections.Counter(), collections.Counter(), collections.Counter()
    hit, miss = [], []
    for d, end in units:
        found = matches(data[d], end)
        labels[label_of(found)] += 1
        strict[label_of(found, STRICT_FAMILIES)] += 1
        for key in {(want, name) for _, _, want, name in found}:
            per[key] += 1
        names = collections.defaultdict(set)
        for i, s, want, name in found:
            names[(i, s)].add(f"{SIDE[want]}: {name}")
        for i, text in traveller_turns(data[d], end):
            for s in sentences(text):
                if (i, s) in names:
                    hit.append((d, i, s, sorted(names[(i, s)])))
                elif ANY_KIND.search(s):
                    miss.append((d, i, s))
    rng = random.Random(SEED)
    return {"labels": labels, "strict": strict, "per_pattern": per,
            "hit": rng.sample(hit, min(10, len(hit))), "miss": rng.sample(miss, min(10, len(miss))),
            "n_hit": len(hit), "n_miss": len(miss)}


def write_doc():
    data, all_sets = sets()
    info = {k: describe(data, v) for k, v in all_sets.items()}
    sha = file_sha256()
    L = ["# The clear-request rule (post hoc)", "",
         f"- SHA-256 of `r10/analysis/clear_rule.py`: `{sha}`",
         f"- Written: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}", "",
         "This rule was written and fixed before any split by it was computed. `clear_split.py` computes the splits. "
         "It stops when the SHA-256 of `clear_rule.py` is not the value above. The rule reads traveller words only: "
         "no brief, no gold state, no model answer, and no sealed file. No sealed second-look answer was read.", "",
         "## The rule", "",
         "A traveller turn is split into sentences. Each pattern runs on one sentence. A dialogue (or a prefix) gets "
         "one label from its traveller turns:", "",
         "- `hotel_only`: a sentence requires a hotel or excludes the guesthouse kinds, and no sentence does the "
         "mirror.",
         "- `guesthouse_only`: the mirror case.",
         "- `mixed`: sentences of both kinds.",
         "- `unclear`: no sentence matches. The plain head noun (\"I need a hotel\", \"a cheap hotel in the north\", "
         "\"I prefer a hotel\") never matches.", "",
         "For prefixes (source 1), only the traveller turns up to and including the first traveller turn that says "
         "\"hotel\" count. For the other sources, all traveller turns count.", "",
         "In the effect tables, **clear** is `hotel_only` and **unclear** is `unclear`. `guesthouse_only` and "
         "`mixed` are counted and shown separately. The secondary rule `strict` keeps the E and R families only.", "",
         "### Kind words", "", "| Kind | Regular expression |", "|---|---|"]
    L += [f"| {k} | `{v.replace('|', chr(92) + '|')}` |" for k, v in KIND.items()]
    L += ["", "### Patterns", "",
          "`{want}` is the kind that the sentence requires. `{other}` is the kind that it excludes. For "
          "`hotel_only`, `{want}` is hotel and `{other}` is the guesthouse kinds. The mirror swaps them. All patterns "
          "ignore case.", "", "| Pattern | Family | Template |", "|---|---|---|"]
    L += [f"| {name} | {fam} | `{tpl.replace('|', chr(92) + '|').replace('{{', '{').replace('}}', '}')}` |"
          for name, fam, tpl in PATTERNS]
    L += ["", "Families: E exclusion, R restriction, P predicate, T type word.", "", "### Guards", "",
          "A match does not count when:", "",
          "- the sentence is a yes/no question about a venue: it ends with \"?\" and starts with \"is\", \"isn't\", "
          "\"was\", \"am\", or \"are they / those / these / any of\";",
          "- (P) a negation comes just before it (\"it doesn't have to be a hotel\");",
          "- (P1) its subject is a person (\"I need to be in a hotel\");",
          "- (R, P, T) the kind word is followed by \"or <other kind>\", \"that is <other kind>\", or \"if\";",
          "- (R1) it follows \"the\" (\"the only hotel in the area\");",
          "- (E1) it follows \"there is\" or \"there are\" (\"if there is not a guesthouse ...\");",
          "- (E) the sentence names another domain (restaurant, attraction, train, taxi, museum, college, food) and "
          "no venue kind before the match.", "",
          "Known limit: a short answer to an assistant's type question (\"A hotel, please.\") stays `unclear`.", "",
          "## Labels per set", "",
          "| Set | Dialogues | hotel_only | guesthouse_only | mixed | unclear | strict: hotel_only | strict: unclear |",
          "|---|---|---|---|---|---|---|---|"]
    for k, v in info.items():
        n = len(all_sets[k])
        L.append(f"| {k} | {n} | " + " | ".join(str(v["labels"][x]) for x in LABELS)
                 + f" | {v['strict']['hotel_only']} | {v['strict']['unclear']} |")
    L += ["", "Sets:", ""] + [f"- `{k}`: {t}." for k, t in SET_TEXT.items()]
    L += ["", "## Dialogues per pattern", "",
          "A dialogue counts once per pattern. One dialogue can match more than one pattern.", "",
          "| Side | Pattern | " + " | ".join(info) + " |", "|---|---|" + "---|" * len(info)]
    for want in KIND:
        for name, _, _ in PATTERNS:
            L.append(f"| {SIDE[want]} | {name} | " + " | ".join(str(v["per_pattern"][(want, name)]) for v in
                                                                 info.values()) + " |")
    L += ["", "## Example sentences (corpus text only)", "",
          f"Each set: 10 matched sentences and 10 unmatched sentences, drawn at random (seed {SEED}). An unmatched "
          "sentence names a venue kind (hotel, guesthouse, guest house, B&B, bed and breakfast, hostel) but matches "
          "no pattern. These are the sentences where a missed type statement would show."]
    for k, v in info.items():
        L += ["", f"### {k}", "", f"{SET_TEXT[k]}. Matched sentences: {v['n_hit']}. Unmatched sentences that name a "
              f"kind: {v['n_miss']}.", "", "Matched:", ""]
        L += [f"{j}. `{d.removesuffix('.json')}` turn {i}: \"{s}\" ({'; '.join(p)})" for j, (d, i, s, p) in
              enumerate(v["hit"], 1)] or ["None."]
        L += ["", "Unmatched:", ""]
        L += [f"{j}. `{d.removesuffix('.json')}` turn {i}: \"{s}\"" for j, (d, i, s) in enumerate(v["miss"], 1)] \
            or ["None."]
    OUT.mkdir(exist_ok=True)
    DOC.write_text("\n".join(L) + "\n")
    print(f"wrote {DOC}")
    print(f"clear_rule.py SHA-256 {sha}")


if __name__ == "__main__":
    write_doc()
