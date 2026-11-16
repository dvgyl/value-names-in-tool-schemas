"""The detector table and the pair selection of X3 and Z4 (PROTOCOL.md section "X3 and Z4", fixed 2026-11-03, with
its amendment 1 of the same day: a candidate needs 25 or more training briefs that set the value; ties go to Rule L,
then to more word dialogues).

The functions use only the dialogue text, the brief (`goal`), and `ontology.json`. No function reads a model output.
Readings of the rule that its text does not fix:
- A slot is a key of `ontology.json`. Its size is the number of entries of that key, as the file writes them.
- A value is one entry, split at "|" and ">" (two values in one label). "dontcare" and "none" are not values.
- A booking slot (`<domain>-book <x>`) is not a candidate. The brief sets it in `goal.<domain>.book`, which Rule B
  does not read, so its Rule B is 1.0 for every value. An extraction form like `p_main` also has no booking field.
- The head word of a value of more than one word is its last word ("park" in "theme park").
- The brief count reads the same brief sections as Rule B, over the training dialogues of the domain.
- Ties that Rule L and the word dialogues do not break go to the alphabetical order.
"""
import collections
import random
import re
from typing import NamedTuple

DOMAINS = ("restaurant", "attraction", "train")
MAX_VALUES = 30
X3_MIN, Z4_MIN, MIN_BRIEFS = 50, 120, 25
X3_HIGH, X3_CONTROL, Z4_PAIRS = 4, 2, 16
NOT_VALUES = {"dontcare", "none"}
# The neutral values, written before the table existed. Each pair gets the first word that passes `neutral_ok`. The
# words are nonce words of child-language studies, so they carry no meaning, no size, and no quality.
NEUTRAL = ("dax", "wug", "fep", "zav", "blicket")
SIZE_QUALITY = {"large", "small", "big", "little", "tiny", "huge", "great", "good", "bad", "best", "worst", "top",
                "high", "low", "cheap", "expensive", "luxury", "premium", "basic", "standard", "fine", "poor", "major",
                "minor", "grand", "mini", "max", "super"}
SEED = 20261103


class Pair(NamedTuple):
    domain: str
    slot: str  # the key of `goal.<domain>.info`, for example "departure"
    value: str


class Row(NamedTuple):
    pair: Pair
    slot_size: int  # entries of the slot in ontology.json
    out: str  # why the pair is not a candidate; "" for a candidate
    words: tuple  # training dialogues of the domain whose traveller turns hold the value word, sorted
    mismatch: int  # of `words`, the dialogues whose brief does not set the slot to the value
    briefs: int  # training dialogues of the domain whose brief sets the slot to the value
    rule_l: str  # why Rule L marks the value high risk; "" if it does not

    @property
    def rule_b(self):
        return self.mismatch / len(self.words) if self.words else None


def values(entries):
    return sorted({v.strip() for e in entries for v in re.split(r"[|>]", e)} - NOT_VALUES - {""})


def word(value):
    """The value word: word boundary, case ignored, plural allowed, any white space between the words of the value."""
    return re.compile(r"\b" + r"\s+".join(map(re.escape, value.split())) + r"(?:s|es)?\b", re.I)


def traveller(d):
    return [t["text"] for i, t in enumerate(d["log"]) if i % 2 == 0]


def brief_sets(goal, pair, sections=("info", "fail_info")):
    part = goal.get(pair.domain) or {}
    for section in sections:
        info = {k.lower(): v for k, v in (part.get(section) or {}).items()}
        if str(info.get(pair.slot, "")).strip().lower() == pair.value:
            return True
    return False


def rule_l(pair, siblings):
    if pair.value == pair.domain:
        return "the domain noun"
    heads = [v for v in siblings if v != pair.value and len(v.split()) > 1 and v.split()[-1] == pair.value]
    return f"head word of '{heads[0]}'" if heads else ""


def candidates(ontology):
    """(pair, slot size, reason out) for every value of every slot of the three domains, in ontology order."""
    for key, entries in ontology.items():
        domain, slot = key.split("-", 1)
        if domain not in DOMAINS:
            continue
        out = ""
        if slot.startswith("book "):
            out = "booking slot: the brief sets it in goal.<domain>.book, which Rule B does not read"
        elif len(entries) > MAX_VALUES:
            out = f"slot has {len(entries)} values in ontology.json"
        for v in values(entries):
            yield Pair(domain, slot.lower(), v), len(entries), out


def table(data, ontology, train_ids, sections=("info", "fail_info")):
    """One Row per (slot, value) of the three domains. `train_ids` must hold only training dialogues. `sections` is
    the part of the brief that Rule B reads; only a sensitivity check changes it."""
    cands = list(candidates(ontology))
    siblings = {}
    for p, _, _ in cands:
        siblings.setdefault((p.domain, p.slot), []).append(p.value)
    domain_ids = {d: [i for i in train_ids if data[i]["goal"].get(d)] for d in DOMAINS}
    briefs = collections.Counter()
    for d, ids in domain_ids.items():
        for i in ids:
            part = data[i]["goal"][d]
            briefs.update({(d, k.lower(), str(v).strip().lower())
                           for sec in sections for k, v in (part.get(sec) or {}).items()})
    text = {i: "\n".join(traveller(data[i])) for i in train_ids}
    rows = []
    for pair, size, out in cands:
        rx = word(pair.value)
        words = tuple(sorted(i for i in domain_ids[pair.domain] if rx.search(text[i])))
        mismatch = sum(not brief_sets(data[i]["goal"], pair, sections) for i in words)
        n = briefs[tuple(pair)]
        if not out and n < MIN_BRIEFS:
            out = f"{n} briefs set the value, fewer than {MIN_BRIEFS}"
        rows.append(Row(pair, size, out, words, mismatch, n, rule_l(pair, siblings[pair.domain, pair.slot])))
    return rows


def ranked(rows, minimum):
    """Candidates with `minimum` or more word dialogues, highest Rule B first. Rule L breaks a tie (high risk first)."""
    keep = [r for r in rows if not r.out and len(r.words) >= minimum]
    return sorted(keep, key=lambda r: (-r.rule_b, not r.rule_l, -len(r.words), r.pair))


def select_x3(rows):
    order = ranked(rows, X3_MIN)
    assert len(order) >= X3_HIGH + X3_CONTROL, f"only {len(order)} candidates have {X3_MIN} or more word dialogues"
    return order[:X3_HIGH], order[-X3_CONTROL:]


def select_z4(rows):
    """16 pairs at evenly spaced ranks, the highest and the lowest included. None if fewer than 16 candidates."""
    order = ranked(rows, Z4_MIN)
    if len(order) < Z4_PAIRS:
        return None
    ranks = sorted({int(k * (len(order) - 1) / (Z4_PAIRS - 1) + 0.5) for k in range(Z4_PAIRS)})  # half rounds up
    assert len(ranks) == Z4_PAIRS, ranks
    return [order[k] for k in ranks]


def neutral_ok(token, pair, traveller_text):
    """The three conditions of the rule: no part of the original value, no size or quality word, and in no traveller
    turn of the training split. A part is a word of the value or 3 or more letters in a row that both share."""
    v = re.sub(r"[^a-z]", "", pair.value)
    shares = any(token[i:i + 3] in v for i in range(len(token) - 2))
    return not (token in pair.value.split() or shares or token in SIZE_QUALITY or word(token).search(traveller_text))


def neutral(pair, traveller_text):
    return next(t for t in NEUTRAL if neutral_ok(t, pair, traveller_text))


def allocate(pools, total):
    """Instance counts per pair that sum to `total` (or to all instances, if fewer): equal shares, and the share that a
    small pool cannot use goes in equal parts to the larger pools. Earlier pairs get the remainder."""
    n = [0] * len(pools)
    left = min(total, sum(pools))
    while left:
        open_ = [k for k in range(len(pools)) if n[k] < pools[k]]
        share = max(1, left // len(open_))
        for k in open_:
            add = min(share, pools[k] - n[k], left)
            n[k] += add
            left -= add
            if not left:
                break
    return n


def order(words, pair):
    """A fixed random order of the word dialogues of a pair. A smaller sample is a prefix of a larger one."""
    out = list(words)
    random.Random(f"{SEED}-{pair.domain}-{pair.slot}-{pair.value}").shuffle(out)
    return out
