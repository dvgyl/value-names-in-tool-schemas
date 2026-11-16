"""Offline tests of r10/flag.py (amendment R10-7) and r10/turns.py (amendment R10-8). No network call, no key.

Usage (from explore/): .venv/bin/python -I r10/tests/test_flag_turns.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
sys.path.insert(0, str(R10))
import flag  # noqa: E402
import tools  # noqa: E402
import turns  # noqa: E402


def test_texts():
    old, new = tools.tool_system("t0"), flag.multi_system("t0")
    assert tools.ASK_NEW in old and tools.END_NEW in old
    assert tools.ASK_NEW not in new and tools.END_NEW not in new and "one call" not in new
    assert new == old.replace(tools.ASK_NEW, flag.MULTI_ASK).replace(tools.END_NEW, flag.MULTI_END)
    assert flag.multi_system("t1").count("property_kind") == 2 and "type:" not in flag.multi_system("t1")
    assert flag.flag_line(1).startswith("No hotel matches. 1 guesthouse matches ")
    assert flag.flag_line(4) == ("No hotel matches. 4 guesthouses match the other filters; the type filter alone "
                                 "removed them.")


def row(text="", calls=None, stop="end_turn"):
    r = {"custom_id": "x", "type": "succeeded", "stop": stop, "text": text}
    if calls is not None:
        r["tool_calls"] = calls
    return r


def search(type_value):
    args = {"name": None, "area": ["north"], "pricerange": None, "stars": None, "type": type_value, "parking": None,
            "internet": None}
    return [{"id": "t", "name": "search_hotels", "input": args}]


def test_classify():
    assert flag.classify(row(calls=search(["guesthouse"])))[0] == "widen"
    assert flag.classify(row(calls=search(None)))[0] == "widen"
    assert flag.classify(row(calls=search(["hotel"])))[0] == "kept"
    assert flag.classify(row("No hotels. Would a guest house suit you?"))[0] == "tell"
    assert flag.classify(row("I searched hotels only."))[0] == "tell"
    assert flag.classify(row("Would another kind of accommodation work for you?"))[0] == "tell"
    assert flag.classify(row("Another kind of accommodation is possible."))[0] == "other"
    assert flag.classify(row("No match. Would a different area suit you?"))[0] == "other"
    assert flag.classify(row(""))[0] == "neither"
    assert flag.classify(row("x", stop="max_tokens"))[0] == "invalid"
    assert flag.classify({"custom_id": "x", "type": "errored"})[0] == "invalid"


def test_build():
    import runs
    for m in flag.MODELS:
        reqs = runs.requests(f"erw_{m}")
        s = flag.sample(m)
        assert len(reqs) == 2 * len(s) > 0
        by = {r["custom_id"]: r for r in reqs}
        for r0, _, n in s:
            _, did, _, read = r0["custom_id"].split("-")
            p = by[f"erw_{m}-{did}-plain-{read}"]["params"]["messages"][2]["content"][0]["content"]
            f = by[f"erw_{m}-{did}-flag-{read}"]["params"]["messages"][2]["content"][0]["content"]
            assert json.loads(p) == {"results": [], "total": 0} and f == p + "\n" + flag.flag_line(n)


def test_brief_and_display():
    d = {"goal": {"message": [
        "You are looking for information in Cambridge",
        "You are looking for a <span class='emphasis'>train</span>. The train should leave on monday",
        "You are also looking for a <span class='emphasis'>place to stay</span>. The hotel should be cheap",
        "Once you find the hotel you want to book it for 2 people", "Make sure you get the reference number",
        "You also want to book a taxi to commute between the two places", "You want to leave the hotel by 10:00"]}}
    assert turns.hotel_brief(d) == "You are also looking for a place to stay. The hotel should be cheap."
    rows = {"results": [{"name": "a", "type": "hotel", "area": "north", "pricerange": "cheap", "stars": "2"},
                        {"name": "b", "type": "guesthouse", "area": "north", "pricerange": "cheap", "stars": "4"}],
            "total": 2}
    t1 = turns.display(rows, "t1")
    assert [r["property_kind"] for r in t1["results"]] == ["large_property", "guesthouse"]
    assert all("type" not in r for r in t1["results"]) and turns.display(rows, "t0") is rows


def test_budget():
    b = turns.Budget(1.0)
    b.reserve(0.6)
    try:
        b.reserve(0.5)
        raise AssertionError("the cap did not stop the call")
    except turns.CapReached:
        pass
    b.settle(0.6, 0.1)
    b.reserve(0.85)
    assert abs(b.spent - 0.1) < 1e-12


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
