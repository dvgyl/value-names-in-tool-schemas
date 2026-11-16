"""Tests of the detector rule (pairs.py) on synthetic dialogues. No data file, no API call.
Usage: python3 -I r9/detector/test_pairs.py"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pairs  # noqa: E402
from pairs import Pair  # noqa: E402


def dialogue(goal, *turns):
    return {"goal": goal, "log": [{"text": t} for t in turns]}


def test_values_and_candidates():
    assert pairs.values(["centre", "centre|west", "east>north", "dontcare", "none"]) == ["centre", "east", "north", "west"]
    onto = {"train-day": ["monday"] * 30, "train-departure": [f"v{k}" for k in range(31)],
            "restaurant-book day": ["monday"], "hotel-area": ["north"]}
    got = {(p.slot, p.value): out for p, _, out in pairs.candidates(onto)}
    assert got[("day", "monday")] == "", "a slot with 30 values is a candidate"
    assert got[("departure", "v0")].startswith("slot has 31"), "a slot with 31 values is not a candidate"
    assert got[("book day", "monday")].startswith("booking slot"), "a booking slot is not a candidate"
    assert not any(s == "area" for s, _ in got), "the hotel domain is out"


def test_word():
    rx = pairs.word("london kings cross")
    assert rx.search("From London  Kings\nCross please") and not rx.search("london kings crossing")
    assert pairs.word("centre").search("near the centres") and not pairs.word("centre").search("centrepiece")
    assert not pairs.word("london").search("a Londoner")


def test_brief_and_rule_l():
    goal = {"train": {"info": {"leaveAt": "10:00", "departure": "ely"}},
            "restaurant": {"fail_info": {"area": "north"}, "info": {"area": "south"}, "book": {"day": "monday"}}}
    assert pairs.brief_sets(goal, Pair("train", "departure", "ely"))
    assert pairs.brief_sets(goal, Pair("train", "leaveat", "10:00")), "slot keys match without case"
    assert pairs.brief_sets(goal, Pair("restaurant", "area", "north")), "fail_info counts"
    assert not pairs.brief_sets(goal, Pair("restaurant", "area", "north"), ("info",))
    assert not pairs.brief_sets(goal, Pair("restaurant", "day", "monday")), "the book section does not count"
    sib = ["london", "east london", "london kings cross", "park", "theme park"]
    assert pairs.rule_l(Pair("train", "departure", "london"), sib) == "head word of 'east london'"
    assert pairs.rule_l(Pair("attraction", "type", "park"), sib) == "head word of 'theme park'"
    assert pairs.rule_l(Pair("attraction", "type", "theme park"), sib) == ""
    assert pairs.rule_l(Pair("train", "type", "train"), sib) == "the domain noun"
    assert pairs.rule_l(Pair("train", "departure", "london"), ["london kings cross"]) == "", "a modifier is not a head"


def test_table_counts_traveller_turns_of_domain_dialogues():
    onto = {"train-departure": ["ely", "london"]}
    data = {
        "a": dialogue({"train": {"info": {"departure": "ely"}}}, "a train from Ely", "ok"),
        "b": dialogue({"train": {"info": {"departure": "london"}}}, "a train from Ely please", "ok"),
        "c": dialogue({"train": {"info": {"departure": "london"}}}, "a train", "Ely is fine"),  # assistant turn only
        "d": dialogue({"hotel": {"info": {"area": "east"}}, "train": {}}, "near Ely", "ok"),  # not a train dialogue
    }
    data["e"] = dialogue({"train": {"info": {"departure": "ely"}, "fail_info": {"departure": "ely"}}}, "hi", "ok")
    rows = {r.pair.value: r for r in pairs.table(data, onto, sorted(data))}
    assert rows["ely"].words == ("a", "b") and rows["ely"].mismatch == 1 and rows["ely"].rule_b == 0.5
    assert rows["london"].words == () and rows["london"].rule_b is None
    assert (rows["ely"].briefs, rows["london"].briefs) == (2, 2), "a brief counts once, also without the word"
    assert rows["ely"].out == "2 briefs set the value, fewer than 25"
    saved, pairs.MIN_BRIEFS = pairs.MIN_BRIEFS, 2
    try:
        assert pairs.table(data, onto, sorted(data))[0].out == "", "2 briefs pass a threshold of 2"
    finally:
        pairs.MIN_BRIEFS = saved


def row(value, n, b, rule_l="", out=""):
    return pairs.Row(Pair("train", "departure", value), 9, out, tuple(range(n)), round(b * n), 30, rule_l)


def test_ranking_and_selection():
    rows = [row("a", 100, 0.9), row("b", 100, 1.0), row("c", 200, 1.0), row("d", 100, 1.0, "head word of 'x d'"),
            row("e", 49, 1.0), row("f", 100, 0.1), row("g", 100, 0.2), row("h", 300, 0.5, out="booking slot"),
            row("i", 100, 0.3)]
    order = [r.pair.value for r in pairs.ranked(rows, 50)]
    assert order == ["d", "c", "b", "a", "i", "g", "f"], order
    high, control = pairs.select_x3(rows)
    assert [r.pair.value for r in high] == ["d", "c", "b", "a"] and [r.pair.value for r in control] == ["g", "f"]
    many = [row(f"v{k:02d}", 120, k / 100) for k in range(31)]
    z4 = pairs.select_z4(many + [row("small", 119, 0.99)])
    assert len(z4) == 16 and z4[0].pair.value == "v30" and z4[-1].pair.value == "v00", "highest and lowest included"
    assert [r.pair.value for r in z4][:3] == ["v30", "v28", "v26"], "evenly spaced ranks"
    assert pairs.select_z4(many[:15]) is None
    many = [row(f"v{k:02d}", 120, k / 100) for k in range(33)]
    ranks = [32 - int(r.pair.value[1:]) for r in pairs.select_z4(many)]
    assert ranks == [0, 2, 4, 6, 9, 11, 13, 15, 17, 19, 21, 23, 26, 28, 30, 32], ranks


def test_neutral():
    p = Pair("restaurant", "pricerange", "expensive")
    assert pairs.neutral(p, "a cheap place") == "dax"
    assert pairs.neutral(p, "my dog is named Dax") == "wug", "a word of a traveller turn is not neutral"
    assert not pairs.neutral_ok("pens", p, ""), "3 letters in a row shared with the value"
    assert not pairs.neutral_ok("large", Pair("train", "day", "monday"), ""), "a size word"
    assert not pairs.neutral_ok("cross", Pair("train", "departure", "london kings cross"), ""), "a word of the value"


def test_allocate_and_order():
    assert pairs.allocate([500, 500, 60, 500, 500, 500], 1200) == [228, 228, 60, 228, 228, 228]
    assert pairs.allocate([200] * 6, 600) == [100] * 6
    assert pairs.allocate([10, 20], 100) == [10, 20], "never more than the pool"
    assert sum(pairs.allocate([120] * 13, 720)) == 720
    p = Pair("train", "day", "monday")
    a = pairs.order(tuple(range(300)), p)
    assert a == pairs.order(tuple(range(300)), p) and sorted(a) == list(range(300)) and a != list(range(300))
    assert a[:120] == pairs.order(tuple(range(300)), p)[:120], "a smaller sample is a prefix of a larger one"


if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_")]
    for t in tests:
        t()
    print(f"test_pairs: all {len(tests)} tests pass")
