"""Offline tests of r10/labeltest.py (amendment R10-18, the label test with one fixed definition). No network call, no
key, no sealed file, no em* folder.

Usage (from explore/): .venv/bin/python -I r10/tests/test_labeltest.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
sys.path.insert(0, str(R10))
sys.path.insert(0, str(EXPLORE / "lib"))
import budget_gate  # noqa: E402
import labeltest as lt  # noqa: E402
import pilot_check  # noqa: E402
import runs  # noqa: E402
import e13  # noqa: E402
import natural  # noqa: E402
import zforms  # noqa: E402

F0_LINE = "type: guesthouse, hotel."


def raises(fn, *args, kinds=(ValueError,)):
    try:
        fn(*args)
    except kinds:
        return True
    raise AssertionError(f"{fn.__name__} did not refuse {args!r}")


def stored(folder, cell, ids, read=1, model=None):
    """{dialogue id: stored request} of one cell and read of an earlier run (only the lines of `ids`)."""
    out = {}
    path = EXPLORE / folder / "requests.jsonl"
    with open(path) as fh:
        for line in fh:
            if f"-{cell}-{read}" not in line[:80]:
                continue
            r = json.loads(line)
            parts = r["custom_id"].split("-")
            if parts[2] == cell and int(parts[3]) == read and (model is None or parts[-1] == model) \
                    and parts[1] + ".json" in ids:
                out[parts[1] + ".json"] = r
    return out


def test_forms():
    """Each arm changes only the type line of F0. The two arms differ only in the label. l_code is round-9 F6."""
    f0 = zforms.FORMS["f0"]
    hotel, code = lt.FORMS["l_hotel"], lt.FORMS["l_code"]
    assert lt.NOTE == " (any venue type that is not a guesthouse)", lt.NOTE
    assert lt.TYPE_LINE == {"l_hotel": "type: guesthouse, hotel (any venue type that is not a guesthouse).",
                            "l_code": "type: guesthouse, category_A (any venue type that is not a guesthouse)."}
    assert f0.system.count(F0_LINE) == 1
    assert hotel.system == f0.system.replace(F0_LINE, lt.TYPE_LINE["l_hotel"])
    assert code.system == f0.system.replace(F0_LINE, lt.TYPE_LINE["l_code"])
    assert code.system == hotel.system.replace("guesthouse, hotel (", "guesthouse, category_A (")
    assert code.system == natural.system(zforms.F0, natural.FORMS["f6"])
    assert hotel.schema == f0.schema
    assert code.schema == natural.schema(e13.schema(False), natural.FORMS["f6"])["schema"]
    swapped = json.loads(json.dumps(f0.schema).replace('"guesthouse", "hotel"', '"guesthouse", "category_A"'))
    assert code.schema == swapped and code.schema != f0.schema
    other = {k: v for k, v in code.schema["properties"].items() if k != "type"}
    assert other == {k: v for k, v in f0.schema["properties"].items() if k != "type"}


def test_parse():
    ans = {"name": None, "area": ["north"], "pricerange": None, "stars": None, "type": None, "parking": None,
           "internet": None}
    txt = lambda t: json.dumps({**ans, "type": t})  # noqa: E731
    assert lt.parse("l_code", txt(["category_A"]))["type"] == ("hotel",)
    assert lt.parse("l_code", txt(["guesthouse", "category_A"]))["type"] == ("guesthouse", "hotel")
    assert lt.parse("l_hotel", txt(["hotel"]))["type"] == ("hotel",)
    assert lt.parse("l_hotel", txt(None))["type"] is None
    assert lt.parse("l_code", txt("any"))["type"] == "any"
    assert lt.parse("l_code", txt(["category_A"]))["area"] == ("north",)
    assert raises(lt.parse, "l_code", txt(["hotel"]))  # a raw hotel under l_code is not valid
    assert raises(lt.parse, "l_hotel", txt(["category_A"]))
    assert raises(lt.parse, "l_hotel", "no object")
    assert raises(lt.parse, "f0", txt(None), kinds=(RuntimeError,))
    assert pilot_check.parses({"text": txt(["category_A"])}, "l_code")
    assert not pilot_check.parses({"text": txt(["hotel"])}, "l_code")
    assert pilot_check.parses({"text": txt(["hotel"])}, "l_hotel")


def test_requests():
    """Counts, sets, and the stored requests: each request equals the stored F0 request of experiment B for the same
    dialogue and model in every part except the custom_id, the cell tag, the system text and (l_code) the schema."""
    data, g = runs.context()
    s = lt.sets(data, g)
    assert {k: len(v) for k, v in s.items()} == {"no_type": 807, "hotel": 233}
    assert not set(s["no_type"]) & set(s["hotel"])
    assert {n for n, r in runs.RUNS.items() if r.exp == "L"} == set(lt.RUNS)
    want = {"erl_sonnet": (("no_type",), 1), "erl_sonnet_hb": (("hotel",), 1), "erl_haiku": (lt.SETS, 2),
            "erl_sol": (lt.SETS, 1), "erl_luna": (lt.SETS, 2)}
    by_model = {}
    for name in lt.RUNS:
        run = runs.RUNS[name]
        sets_used, reads = want[name]
        assert run.build.sets == sets_used and run.reads == reads, name
        reqs = runs.requests(name)
        ids = [d for k in sets_used for d in s[k]]
        assert len(reqs) == len(ids) * reads * 2, (name, len(reqs))
        assert {r["cell"] for r in reqs} == set(lt.CELLS)
        for i in range(0, len(reqs), 2):  # the two arms of one dialogue and read follow each other
            a, b = reqs[i]["custom_id"].split("-"), reqs[i + 1]["custom_id"].split("-")
            assert (a[1], a[3], a[2], b[2]) == (b[1], b[3], "l_hotel", "l_code"), (a, b)
        by_model.setdefault(run.model, []).extend(reqs)
    assert {m: len({r["custom_id"].split("-")[1] for r in v}) for m, v in by_model.items()} == \
        {"sonnet": 1040, "haiku": 1040, "sol": 1040, "luna": 1040}
    for model, reqs in by_model.items():
        ids = {r["custom_id"].split("-")[1] + ".json" for r in reqs}
        old = stored(f"erb_{model}", "f0", ids)
        assert len(old) == 1040, (model, len(old))
        for r in reqs:
            d = r["custom_id"].split("-")[1] + ".json"
            new, base = (r.get("params") or r["body"]), (old[d].get("params") or old[d]["body"])
            form = lt.FORMS[r["cell"]]
            if "params" in r:
                expect = json.loads(json.dumps(base))
                expect["system"] = form.system
                expect["output_config"]["format"]["schema"] = form.schema
            else:
                expect = json.loads(json.dumps(base))
                expect["input"][0]["content"] = form.system
                expect["text"]["format"]["schema"] = form.schema
            assert new == expect, (model, r["custom_id"])
    print("  every request equals the stored F0 request of erb_<model> except the system text and the schema")


def test_l_code_is_round9_f6():
    """l_code requests equal the round-9 F6 requests (ex1_f6 for Claude, eb1_luna and eb1_sol for GPT) of the same
    dialogue, model and read 1, byte for byte in the params or body."""
    data, g = runs.context()
    s = lt.sets(data, g)
    checked = {}
    for name, folder, tag in (("erl_sonnet", "ex1_f6", "sonnet"), ("erl_sonnet_hb", "ex1_f6", "sonnet"),
                              ("erl_haiku", "ex1_f6", "haiku"), ("erl_luna", "eb1_luna", "luna"),
                              ("erl_sol", "eb1_sol", "sol")):
        reqs = [r for r in runs.requests(name) if r["cell"] == "l_code" and r["custom_id"].endswith("-1")]
        ids = {r["custom_id"].split("-")[1] + ".json" for r in reqs}
        old = stored(folder, "f6", ids, model=tag)
        n = 0
        for r in reqs:
            d = r["custom_id"].split("-")[1] + ".json"
            if d in old:
                assert (r.get("params") or r["body"]) == (old[d].get("params") or old[d]["body"]), (name, d)
                n += 1
        checked[name] = (n, len(reqs))
        assert n > 0, name
    assert sum(n for n, _ in checked.values()) > 3000, checked
    print("  l_code equals round-9 F6 (requests compared / requests):", checked)
    assert set(s) == set(lt.SETS)


def test_money_rule():
    """R10-18 uses its own reserve (labeltest.RESERVE); every other run keeps budget_gate.RESERVE."""
    assert lt.RESERVE == 0.0 and budget_gate.RESERVE == 2.00
    for acc in ("anthropic_r9a", "anthropic_r9b", "openai_r9"):
        free0 = budget_gate.free(acc, lt.RESERVE)
        assert abs(free0 - budget_gate.free(acc) - budget_gate.RESERVE) < 1e-9
        assert budget_gate.fits(acc, round(free0, 2) - 0.01, lt.RESERVE)
        assert not budget_gate.fits(acc, free0 + 0.01, lt.RESERVE)
    assert {runs.RUNS[n].account for n in lt.RUNS} == {"anthropic_r9a", "anthropic_r9b", "openai_r9"}


if __name__ == "__main__":
    only = sys.argv[1:]
    for fname, fn in list(globals().items()):
        if fname.startswith("test_") and callable(fn) and (not only or fname in only):
            fn()
            print("ok", fname)
    print("PASS")
