"""Shared helpers for the round-9 free analyses (X0 and Z0). Local files only, no API call.

Brief gold: `goal.hotel.info.type`, the instruction that MultiWOZ gave the traveller. Booked gold: the type of the last
venue in `metadata.hotel.book.booked`, matched to `hotel_db.json` as `review/plan13/revealed_r9b.py` does.
"""
import collections
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

EXPLORE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(EXPLORE / "forms"))
import common  # noqa: E402
import e8_measure  # noqa: E402
from common import anth  # noqa: E402

WORD = e8_measure.WORD
LODGING = re.compile(r"place to stay|somewhere to stay|accommodation|lodging|places to stay|a room\b|where to stay", re.I)
GUEST = re.compile(r"guest ?house", re.I)
EXPLORATORY = "EXPLORATORY: analysis chosen after the runs"
SETTING = {"e7": "E7/E11", "e11": "E7/E11", "e12": "E12", "e13": "E13"}
CELLS = tuple(("E7/E11", m, f, f + "_renamed") for f in ("p4", "p5") for m in ("haiku", "sonnet", "opus")) + (
    ("E12", "sonnet", "p4", "p4_renamed"), ("E13", "haiku", "p_main", "p_main_renamed"),
    ("E13", "sonnet", "p_main", "p_main_renamed"))
AVAIL = {(True, True): "both", (True, False): "only guesthouse", (False, True): "only hotel", (False, False): "neither"}


def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("&", "and"))


def hotel_db():
    return json.loads((anth.DATA / "hotel_db.json").read_text())


def db_types(db):
    return {norm(h["name"]): h["type"] for h in db}


def traveller(d):
    return [t["text"] for k, t in enumerate(d["log"]) if k % 2 == 0]


def brief_type(d, key="info"):
    """'hotel', 'guesthouse', or None. `key="fail_info"` gives the type of the brief's first request, which had no venue."""
    return d["goal"]["hotel"].get(key, {}).get("type")


def booked_type(d, types):
    names = [b["name"] for t in d["log"] for b in ((t.get("metadata") or {}).get("hotel", {}).get("book", {}).get("booked")
                                                   or []) if b.get("name")]
    return types.get(norm(names[-1]), "unmatched") if names else "none"


def hotel_words(d):
    return sum(len(WORD.findall(t)) for t in traveller(d))


def dialogue_sets(data):
    """The E7 pool, the 994 (traveller-turns rule), the 1,136 (all-turns rule), and the 256 of `probe_r9b.py`: gold no
    type, a lodging phrase and no "hotel" in the traveller turns."""
    e7 = common.e7_ids(data)
    no_type = [i for i in e7 if common.gold_form(data[i])["type"] is None]
    says = {i for i in no_type if any(WORD.search(t) for t in traveller(data[i]))}
    sets = {"e7": e7, "994": sorted(says), "1136": common.e11_ids(data),
            "256": [i for i in no_type if i not in says and any(LODGING.search(t) for t in traveller(data[i]))]}
    assert [len(v) for v in sets.values()] == [2874, 994, 1136, 256], {k: len(v) for k, v in sets.items()}
    return sets


def wizard_first(acts, match, domains=("Hotel", "Booking"), skip=()):
    """The match of the first `Name` value in a `domains` act, in turn order, or "none". The defaults rebuild the
    planner's D5 count, where a `Hotel-Request` "?" counts as a name that matches no venue."""
    for k in sorted(acts, key=int):
        if isinstance(acts[k], dict):
            for act, slots in acts[k].items():
                if act.split("-")[0] in domains:
                    for slot, value in slots:
                        if slot == "Name" and value not in skip:
                            return match(value)
    return "none"


def loose_type(name, types):
    """Match without a leading "the", also when the name is the start of exactly one venue name ("gonville")."""
    stem = {k.removeprefix("the"): t for k, t in types.items()}
    n = norm(name).removeprefix("the")
    found = [t for k, t in stem.items() if k == n] or [t for k, t in stem.items() if n and k.startswith(n)]
    return found[0] if len(found) == 1 else "unmatched"


def holds_hotel(v):
    return isinstance(v, tuple) and "hotel" in v


def hides_guesthouse(v):
    """The read keeps hotel and not guesthouse, so a search with it shows no guesthouse."""
    return holds_hotel(v) and "guesthouse" not in v


def is_unclear(v):
    return v == "unclear"


OUTCOMES = {"type holds hotel": holds_hotel, "type hides every guesthouse": hides_guesthouse}


def split_id(cid):
    """(experiment, dialogue, form, read, model), or None for an E12 Track C row."""
    parts = cid.split("-")
    if parts[0] == "e12c":
        return None
    if parts[0] == "e12n":  # E12 ran Sonnet only, so its ids hold no model
        return "e12", parts[1] + ".json", parts[2], int(parts[3]), "sonnet"
    return common.split_custom_id(cid)


def load_reads(keep, root=anth.EXPLORE):
    """{(setting, model, form): {dialogue: [parsed read]}} on `keep`, and the count of rows without a valid read."""
    reads = collections.defaultdict(lambda: collections.defaultdict(list))
    bad = collections.Counter()
    for exp, setting in SETTING.items():
        for line in open(root / exp / "raw.jsonl"):
            r = json.loads(line)
            key = split_id(r["custom_id"])
            if key is None or key[1] not in keep:
                continue
            _, d, form, _, model = key
            assert r["model"] == common.MODELS[model], r["custom_id"]
            if r["type"] != "succeeded" or r.get("stop") != "end_turn":
                bad[(setting, model, form)] += 1
                continue
            try:
                read = common.parse(r["text"])
            except (ValueError, KeyError):
                bad[(setting, model, form)] += 1
                continue
            reads[(setting, model, form)][d].append(read)
    return reads, bad


def hits(cell, outcome, field="type"):
    return {d: [outcome(r[field]) for r in rs] for d, rs in cell.items()}


def count(h, keep):
    """(reads with the outcome, valid reads) on `keep`."""
    return sum(sum(h.get(d, ())) for d in keep), sum(len(h.get(d, ())) for d in keep)


def pct(k, n):
    return 100 * k / n if n else float("nan")


def sign_test(a, b, keep):
    """Dialogue-level exact two-sided sign test on `keep`: (a higher, b higher, p)."""
    return e8_measure.sign_test({d: a[d] for d in keep if d in a}, b)


class Contrast(NamedTuple):
    k0: int
    n0: int
    k1: int
    n1: int
    more: int
    less: int
    p: float
    any0: int

    def text(self):
        return (f"{pct(self.k0, self.n0):5.1f}% -> {pct(self.k1, self.n1):5.1f}% "
                f"({self.more}:{self.less}, p={self.p:.2g})")


def contrast(a, b, keep):
    return Contrast(*count(a, keep), *count(b, keep), *sign_test(a, b, keep), sum(1 for d in keep if any(a.get(d, ()))))


def availability(gold, db):
    """Which venue types match the gold's constraints other than `type`."""
    ok = set(common.acceptable_rank({**gold, "type": None}, db, {h["name"]: 0 for h in db}))
    found = {h["type"] for h in db if h["name"] in ok}
    return AVAIL[("guesthouse" in found, "hotel" in found)]


def matches(read, db):
    """Venues that a read accepts. "unclear" counts as no constraint, as in `common.Market.flips`."""
    form = {f: (None if read[f] == "unclear" else read[f]) for f in common.FIELDS}
    return common.acceptable_rank(form, db, {h["name"]: 0 for h in db})


def like(planner, mine):
    """`mine` written with the precision of the planner's string, so that the two strings compare exactly."""
    s = planner.rstrip("%")
    if isinstance(mine, str):
        return mine
    if "e" in s:
        return f"{mine:.{len(s.split('e')[0].replace('.', '')) - 1}e}"
    if "." in s:
        return f"{mine:.{len(s.split('.')[1])}f}"
    return str(round(mine))


CHECKS = collections.Counter()


def check(source, label, planner, mine):
    m = like(planner, mine)
    verdict = "same" if m == planner.rstrip("%") else "DIFF"
    CHECKS[verdict] += 1
    print(f"  [{source}] {label}: planner {planner} | mine {m} | {verdict}")
    return verdict == "same"


def summary():
    print(f"\nplanner checks: {CHECKS['same']} same, {CHECKS['DIFF']} DIFF")
