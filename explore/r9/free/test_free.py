"""Synthetic tests of the `gold.py` helpers. Each test must pass on the helper and fail on a broken copy of it.

Usage: python3 -I test_free.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gold  # noqa: E402

DB = [
    {"name": "acorn guest house", "type": "guesthouse", "area": "north", "pricerange": "cheap", "stars": "4",
     "parking": "yes", "internet": "yes"},
    {"name": "bridge guest house", "type": "guesthouse", "area": "south", "pricerange": "moderate", "stars": "3",
     "parking": "no", "internet": "yes"},
    {"name": "the lensfield hotel", "type": "hotel", "area": "north", "pricerange": "expensive", "stars": "3",
     "parking": "yes", "internet": "yes"},
    {"name": "gonville hotel", "type": "hotel", "area": "south", "pricerange": "cheap", "stars": "2",
     "parking": "yes", "internet": "no"},
]
TYPES = gold.db_types(DB)
NO = dict.fromkeys(gold.common.FIELDS)


def dialogue(turns, booked=(), info=None, fail=None):
    """Booked names grow on the assistant turns, as in MultiWOZ metadata."""
    log = []
    for k, text in enumerate(turns):
        md = {} if k % 2 == 0 else {"hotel": {"book": {"booked": [{"name": n} for n in booked[:(k + 1) // 2]]}}}
        log.append({"text": text, "metadata": md})
    goal = {"info": {} if info is None else {"type": info}, "fail_info": {} if fail is None else {"type": fail}}
    return {"goal": {"hotel": goal}, "log": log}


def test_booked(booked_type):
    two = dialogue(["a", "b", "c", "d"], booked=["Acorn Guest-House", "The Lensfield Hotel"])
    assert booked_type(two, TYPES) == "hotel"
    assert booked_type(dialogue(["a", "b"], booked=["Acorn Guest House"]), TYPES) == "guesthouse"
    assert booked_type(dialogue(["a", "b"], booked=["nowhere inn"]), TYPES) == "unmatched"
    assert booked_type(dialogue(["a", "b"]), TYPES) == "none"


def test_brief(brief_type):
    d = dialogue(["a"], info="hotel", fail="guesthouse")
    assert brief_type(d) == "hotel"
    assert brief_type(d, "fail_info") == "guesthouse"
    assert brief_type(dialogue(["a"])) is None


def test_outcomes(holds, hides):
    assert [holds(v) for v in (("hotel",), ("guesthouse", "hotel"), ("guesthouse",), "any", None, "unclear")] == [
        True, True, False, False, False, False]
    assert [hides(v) for v in (("hotel",), ("guesthouse", "hotel"), ("hotel", "guesthouse"), ("guesthouse",), None)] == [
        True, False, False, False, False]


def test_outcome_from_text(holds):
    """A renamed reply maps back to `type`, so its outcome equals the original form's outcome."""
    read = gold.common.parse('Here: {"property_kind": ["large_property"], "area": null}')
    assert holds(read["type"]) and not holds(gold.common.parse('{"type": ["guesthouse"]}')["type"])


def test_hotel_words(hotel_words):
    d = dialogue(["Hotels near a hotel, not hotelier.", "The hotel is here.", "A hotel please."])
    assert hotel_words(d) == 3


def test_sign(sign_test):
    a = {"d1": [True, True, False], "d2": [True], "d3": [False], "d4": [True]}
    b = {"d1": [False, False, False], "d2": [False], "d3": [False], "d4": [False]}
    assert sign_test(a, b, {"d1", "d2", "d3"}) == (2, 0, 0.5)
    five = {f"d{i}": [True] for i in range(5)}
    assert sign_test(five, {d: [False] for d in five}, set(five)) == (5, 0, 0.0625)
    four = {"d1": [True], "d2": [True], "d3": [True], "d4": [False]}
    assert sign_test(four, {"d1": [False], "d2": [False], "d3": [False], "d4": [True]}, set(four)) == (3, 1, 0.625)


def test_availability(availability):
    assert availability({**NO, "area": ("north",)}, DB) == "both"
    assert availability({**NO, "area": ("north",), "type": ("guesthouse",)}, DB) == "both"
    assert availability({**NO, "area": ("north",), "pricerange": ("cheap",)}, DB) == "only guesthouse"
    assert availability({**NO, "pricerange": ("expensive",)}, DB) == "only hotel"
    assert availability({**NO, "area": ("east",)}, DB) == "neither"


def test_matches(matches):
    assert sorted(matches({**NO, "area": "unclear", "type": ("hotel",)}, DB)) == ["gonville hotel", "the lensfield hotel"]
    assert matches({**NO, "pricerange": ("moderate",), "type": ("hotel",)}, DB) == []


def test_wizard(wizard_first):
    acts = {"1": "No Annotation", "2": {"Restaurant-Inform": [["Name", "golden wok"]]},
            "3": {"Hotel-Request": [["Name", "?"]]}, "4": {"Booking-Inform": [["Name", "the lensfield hotel"]]},
            "10": {"Hotel-Inform": [["Name", "acorn guest house"]]}}
    plain = lambda v: TYPES.get(gold.norm(v), "unmatched")
    assert wizard_first(acts, plain) == "unmatched"
    assert wizard_first(acts, plain, skip=("?", "none")) == "hotel"
    assert wizard_first(acts, plain, domains=("Hotel",), skip=("?", "none")) == "guesthouse"
    assert wizard_first({"1": {"Restaurant-Inform": [["Name", "x"]]}}, plain) == "none"


def test_loose(loose_type):
    assert [loose_type(n, TYPES) for n in ("the acorn guest house", "gonville", "lensfield hotel", "guest", "")] == [
        "guesthouse", "hotel", "hotel", "unmatched", "unmatched"]


def test_split_id(split_id):
    assert split_id("e12n-PMUL1-p4_renamed-3") == ("e12", "PMUL1.json", "p4_renamed", 3, "sonnet")
    assert split_id("e12c-x-g01-a-b-r1") is None
    assert split_id("e13-MUL1-p_main-2-haiku") == ("e13", "MUL1.json", "p_main", 2, "haiku")


def test_load(load_reads):
    """Only succeeded, finished, parsed rows of kept dialogues count; the other rows of a cell count as invalid."""
    rows = {"e7": [("e7-A-p4-1-haiku", "succeeded", "end_turn", '{"type": ["hotel"]}'),
                   ("e7-A-p4-2-haiku", "succeeded", "max_tokens", '{"type": ["hotel"]}'),
                   ("e7-A-p4-3-haiku", "errored", None, ""),
                   ("e7-B-p4-1-haiku", "succeeded", "end_turn", '{"type": ["hotel"]}')],
            "e11": [("e11-A-p4_renamed-1-haiku", "succeeded", "end_turn", "no json")],
            "e12": [("e12n-A-p4-1", "succeeded", "end_turn", '{"type": "guesthouse"}'),
                    ("e12c-x-g01-a-b-r1", "succeeded", "end_turn", "{}")],
            "e13": [("e13-A-p_main-1-sonnet", "succeeded", "end_turn", '{"property_kind": ["large_property"]}')]}
    model = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5"}
    with tempfile.TemporaryDirectory() as tmp:
        for exp, rs in rows.items():
            (Path(tmp) / exp).mkdir()
            with open(Path(tmp) / exp / "raw.jsonl", "w") as f:
                for cid, typ, stop, text in rs:
                    m = "sonnet" if cid.startswith("e12") else cid.rsplit("-", 1)[1]
                    f.write(json.dumps({"custom_id": cid, "type": typ, "stop": stop, "text": text, "model": model[m]}) + "\n")
        reads, bad = load_reads({"A.json"}, root=Path(tmp))
    assert {k: {d: [r["type"] for r in v] for d, v in c.items()} for k, c in reads.items()} == {
        ("E7/E11", "haiku", "p4"): {"A.json": [("hotel",)]}, ("E12", "sonnet", "p4"): {"A.json": [("guesthouse",)]},
        ("E13", "sonnet", "p_main"): {"A.json": [("hotel",)]}}
    assert dict(bad) == {("E7/E11", "haiku", "p4"): 2, ("E7/E11", "haiku", "p4_renamed"): 1}


def test_like(like):
    assert [like("13.2%", 13.249), like("6.8e-13", 6.81e-13), like("0.125", 0.125), like("355", 355.0)] == [
        "13.2", "6.8e-13", "0.125", "355"]


def broken_booked(d, types):
    names = [b["name"] for t in d["log"] for b in ((t.get("metadata") or {}).get("hotel", {}).get("book", {}).get("booked")
                                                   or [])]
    return types.get(gold.norm(names[0]), "unmatched") if names else "none"


def broken_availability(g, db):
    ok = set(gold.common.acceptable_rank(g, db, {h["name"]: 0 for h in db}))
    found = {h["type"] for h in db if h["name"] in ok}
    return gold.AVAIL[("guesthouse" in found, "hotel" in found)]


def broken_wizard(acts, match, domains=("Hotel", "Booking"), skip=()):
    return gold.wizard_first({str(n): acts[k] for n, k in enumerate(sorted(acts), 1)}, match, domains, skip)


def broken_load(keep, root):
    reads, bad = gold.load_reads(keep, root)
    bad.clear()
    return reads, bad


CASES = [
    ("booked type", test_booked, (gold.booked_type,), (broken_booked,)),
    ("brief type", test_brief, (gold.brief_type,), (lambda d, key="info": gold.brief_type(d, "fail_info") or gold.brief_type(d),)),
    ("read outcomes", test_outcomes, (gold.holds_hotel, gold.hides_guesthouse), (gold.holds_hotel, gold.holds_hotel)),
    ("outcome from reply text", test_outcome_from_text, (gold.holds_hotel,), (lambda v: v == "hotel",)),
    ("hotel words", test_hotel_words, (gold.hotel_words,), (lambda d: sum(len(gold.WORD.findall(t["text"])) for t in d["log"]),)),
    ("sign test", test_sign, (gold.sign_test,), (lambda a, b, keep: gold.e8_measure.sign_test(a, b),)),
    ("availability class", test_availability, (gold.availability,), (broken_availability,)),
    ("venue matches", test_matches, (gold.matches,), (lambda r, db: gold.common.acceptable_rank(r, db, {h["name"]: 0 for h in db}),)),
    ("wizard first venue", test_wizard, (gold.wizard_first,), (broken_wizard,)),
    ("loose venue name", test_loose, (gold.loose_type,), (lambda n, types: types.get(gold.norm(n), "unmatched"),)),
    ("custom id", test_split_id, (gold.split_id,), (lambda cid: gold.common.split_custom_id(cid) if cid.count("-") == 4 else None,)),
    ("read loader", test_load, (gold.load_reads,), (broken_load,)),
    ("planner number style", test_like, (gold.like,), (lambda p, m: f"{m:.1f}" if not isinstance(m, str) else m,)),
]


def main():
    for name, test, good, bad in CASES:
        test(*good)
        try:
            test(*bad)
        except AssertionError:
            print(f"ok   {name}: passes, and its broken copy fails")
            continue
        raise SystemExit(f"FAIL {name}: the broken copy passes")
    print(f"all {len(CASES)} tests pass")


if __name__ == "__main__":
    main()
