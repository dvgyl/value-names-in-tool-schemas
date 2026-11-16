"""Offline tests of r10/labeltest2.py (amendment R10-19), r10/harmless.py (amendment R10-20) and r10/newmoney.py. No
network call, no key, no sealed file, no em* folder.

Usage (from explore/): .venv/bin/python -I r10/tests/test_labeltest2_harmless.py [test name ...]
"""
import copy
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
sys.path.insert(0, str(R10))
sys.path.insert(0, str(EXPLORE / "lib"))
import budget_gate  # noqa: E402
import control  # noqa: E402
import harmless as hm  # noqa: E402
import labeltest as lt  # noqa: E402
import labeltest2 as l2  # noqa: E402
import newmoney  # noqa: E402
import pilot_check  # noqa: E402
import runs  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402
import e13  # noqa: E402
import natural  # noqa: E402

PART_A_SHA256 = "3f207e3ee760b7140e1acfbdc36d518bbccc7d22dfceb0d88709811b99a1dedb"  # written into R10-19


def raises(fn, *args, kinds=(ValueError,)):
    try:
        fn(*args)
    except kinds:
        return True
    raise AssertionError(f"{fn.__name__} did not refuse {args!r}")


def body(r):
    return r.get("params") or r["body"]


def stored(folder, ids_cells):
    """{(dialogue id, cell, read): stored request} of an earlier run, for the keys in ids_cells."""
    out = {}
    with open(EXPLORE / folder / "requests.jsonl") as fh:
        for line in fh:
            r = json.loads(line)
            _, d, cell, read = r["custom_id"].split("-")
            k = (d + ".json", cell, int(read))
            if k in ids_cells:
                out[k] = r
    return out


def test_forms_r19():
    """l_neutral changes only the label of the R10-18 type line; its schema only the hotel enum value."""
    h, n = lt.FORMS["l_hotel"], l2.FORMS["l_neutral"]
    assert l2.TYPE_LINE["l_neutral"] == "type: guesthouse, serviced_property (any venue type that is not a guesthouse)."
    assert l2.TYPE_LINE["l_hotel"] == lt.TYPE_LINE["l_hotel"] and l2.TYPE_LINE["l_code"] == lt.TYPE_LINE["l_code"]
    assert n.system == h.system.replace(lt.TYPE_LINE["l_hotel"], l2.TYPE_LINE["l_neutral"]) != h.system
    assert n.system == natural.system(zforms.F0, natural.Form({}, "serviced_property", lt.NOTE))
    assert json.dumps(n.schema) == json.dumps(h.schema).replace('"guesthouse", "hotel"', '"guesthouse", "serviced_property"')
    assert natural.NEUTRAL == "serviced_property"
    assert l2.FORMS["l_hotel"] is lt.FORMS["l_hotel"] and l2.FORMS["l_code"] is lt.FORMS["l_code"]
    assert n.schema == natural.schema(e13.schema(False), l2.NATURAL["l_neutral"])["schema"]


def test_parse_r19():
    ans = {"name": None, "area": None, "pricerange": None, "stars": None, "type": None, "parking": None,
           "internet": None}
    txt = lambda t: json.dumps({**ans, "type": t})  # noqa: E731
    assert l2.parse("l_neutral", txt(["serviced_property"]))["type"] == ("hotel",)
    assert l2.parse("l_neutral", txt(["guesthouse"]))["type"] == ("guesthouse",)
    assert l2.parse("l_neutral", txt("any"))["type"] == "any"
    assert raises(l2.parse, "l_neutral", txt(["hotel"]))
    assert raises(l2.parse, "l_neutral", txt(["category_A"]))
    assert l2.parse("l_code", txt(["category_A"]))["type"] == ("hotel",)
    assert raises(l2.parse, "f0", txt(None), kinds=(RuntimeError,))
    assert pilot_check.parses({"text": txt(["serviced_property"])}, "l_neutral")
    assert not pilot_check.parses({"text": txt(["hotel"])}, "l_neutral")


def test_requests_r19():
    """Counts, the Sonnet split, the pairing order, and the stored requests of the R10-18 arms."""
    data, g = runs.context()
    s = l2.sets(data, g)
    a, b = s["no_type_a"], s["no_type_b"]
    assert (len(a), len(b)) == (440, 367) and not set(a) & set(b) and set(a) | set(b) == set(s["no_type"])
    assert hashlib.sha256("\n".join(a).encode()).hexdigest() == PART_A_SHA256
    assert {n for n, r in runs.RUNS.items() if r.exp == "L2"} == set(l2.RUNS)
    want = {"erl2_sol": 4160, "erl2_luna": 6240, "erl2_sonnet_a": 440, "erl2_sonnet_b": 367, "erl2_haiku": 2080,
            "erl2_deepseek": 6240, "erl2_qwen": 6240, "erl2_gemma": 6240}
    built = {}
    for name in l2.RUNS:
        reqs = runs.requests(name)
        built[name] = reqs
        assert len(reqs) == want[name], (name, len(reqs))
        sets_used, cells = l2.PLAN[name]
        got = {}
        for r in reqs:
            _, d, cell, read = r["custom_id"].split("-")
            got.setdefault(cell, set()).add(int(read))
            assert r["cell"] == cell
        assert got == {c: set(v) for c, v in cells.items()}, (name, got)
    # Sol and Luna: the new l_hotel and l_code requests equal the R10-18 requests of the same dialogue and cell
    for name, old, old_read in (("erl2_sol", "erl_sol", 1), ("erl2_luna", "erl_luna", 1)):
        keys = {}
        for r in built[name]:
            _, d, cell, read = r["custom_id"].split("-")
            if cell != "l_neutral":
                keys[(d + ".json", cell, old_read)] = r
        prev = stored(old, set(keys))
        assert len(prev) == len(keys) == 2080, (name, len(prev), len(keys))
        for k, r in keys.items():
            assert body(r) == body(prev[k]), (name, k)
    # every request: l_neutral equals l_hotel of the same run, dialogue and read except the system text and the schema
    for name, reqs in built.items():
        by = {tuple(r["custom_id"].split("-")[1:]): r for r in reqs}
        for (d, cell, read), r in by.items():
            if cell != "l_neutral" or (d, "l_hotel", read) not in by:
                continue
            h = copy.deepcopy(body(by[(d, "l_hotel", read)]))
            n = copy.deepcopy(body(r))
            for x in (h, n):
                if "params" in r:
                    x.pop("system"), x["output_config"]["format"].pop("schema")
                elif "messages" in x:
                    x["messages"][0].pop("content"), x["response_format"]["json_schema"].pop("schema"), x.pop("seed")
                else:
                    x["input"][0].pop("content"), x["text"]["format"].pop("schema")
            assert n == h, (name, d, read)
    # Sonnet and Haiku l_neutral: the R10-18 request of the same dialogue except the system text and the schema
    for name, old in (("erl2_sonnet_a", "erl_sonnet"), ("erl2_sonnet_b", "erl_sonnet"), ("erl2_haiku", "erl_haiku")):
        keys = {(r["custom_id"].split("-")[1] + ".json", "l_hotel", int(r["custom_id"].split("-")[3])): r
                for r in built[name]}
        prev = stored(old, set(keys))
        assert len(prev) == len(keys), (name, len(prev), len(keys))
        for k, r in keys.items():
            p = copy.deepcopy(body(prev[k]))
            p["system"] = l2.FORMS["l_neutral"].system
            p["output_config"]["format"]["schema"] = l2.FORMS["l_neutral"].schema
            assert body(r) == p, (name, k)
    # the open models: the l_hotel request equals the R10-17 f0 request of the same dialogue and read, except the
    # system text, the schema and the seed (the seed comes from the custom_id)
    for m in ("deepseek", "qwen", "gemma"):
        f0 = {tuple(r["custom_id"].split("-")[1::2]): r for r in runs.requests(f"ery_{m}") if r["cell"] == "f0"}
        n = 0
        for r in built[f"erl2_{m}"]:
            _, d, cell, read = r["custom_id"].split("-")
            if cell != "l_hotel":
                continue
            x, y = copy.deepcopy(body(r)), copy.deepcopy(body(f0[(d, read)]))
            assert x["messages"][0]["content"] == lt.FORMS["l_hotel"].system
            assert x["response_format"]["json_schema"]["schema"] == lt.FORMS["l_hotel"].schema
            for z in (x, y):
                z["messages"][0].pop("content"), z["response_format"]["json_schema"].pop("schema"), z.pop("seed")
            assert x == y, (m, d, read)
            n += 1
        assert n == 2080, (m, n)
    print("  R19 requests: counts, split, stored R10-18 arms, l_neutral against l_hotel, open models against R10-17")


def test_requests_r20():
    """Counts; tool cells against the stored era1 requests; the update cells against the control."""
    data, g = runs.context()
    sets = control.set_of(data, g)
    assert {k: sum(v == k for v in sets.values()) for k in ("open", "specific", "guesthouse")} == \
        {"open": 448, "specific": 59, "guesthouse": 47}
    assert {n for n, r in runs.RUNS.items() if r.exp == "K"} == set(hm.RUNS)
    for name in hm.RUNS:
        model = runs.RUNS[name].model
        ch = hm.CHANNEL[model]
        reqs = runs.requests(name)
        assert len(reqs) == 4 * 1085, (name, len(reqs))
        by = {tuple(r["custom_id"].split("-")[1:]): r for r in reqs}
        for i in range(0, len(reqs), 4):  # the four cells of one prefix and read follow each other, control first
            assert [r["cell"] for r in reqs[i:i + 4]] == list(hm.CELLS_OF[ch])
        for (d, cell, read), r in by.items():
            ctrl = body(by[(d, hm.CONTROL_CELL[ch], read)])
            x, c = copy.deepcopy(body(r)), copy.deepcopy(ctrl)
            if cell in ("trep", "prep"):
                if ch == "form":
                    assert x.pop("seed") != c.pop("seed")
                assert x == c, (name, d, cell)
            elif cell == "tpar":
                assert x["tools"][0]["description"] == hm.TOOL_PARAPHRASE
                assert c["tools"][0]["description"] == tools.SEARCH_DESCRIPTION
                x["tools"][0].pop("description"), c["tools"][0].pop("description")
                assert x == c, (name, d)
            elif cell == "ppar":
                xs, cs = x["messages"][0].pop("content"), c["messages"][0].pop("content")
                for old, new in hm.FORM_PARAPHRASE.items():
                    cs = cs.replace(old, new)
                assert xs == cs and xs != zforms.FORMS["f0"].system
                x.pop("seed"), c.pop("seed")
                assert x == c, (name, d)
            elif cell == "p1":
                assert x["messages"][0]["content"] == zforms.FORMS["f1"].system
                assert x["response_format"]["json_schema"]["schema"] == zforms.FORMS["f1"].schema
        if ch == "tool":  # t0 and t1 equal the stored era1 requests of the same prefix (read 1), byte for byte
            keys = {(d, c, 1) for (d, c, read) in by if c in ("t0", "t1")}
            keys = {(d + ".json", c, 1) for d, c, _ in keys}
            prev = stored(f"era1_{model}", keys)
            assert len(prev) == 2 * 554, (name, len(prev))
            for (d, c, read), r in by.items():
                if c in ("t0", "t1"):
                    assert body(r) == body(prev[(d + ".json", c, 1)]), (name, d, c, read)
        else:  # p0 is the p0 request of runs.build_a; prep differs only in the seed
            import models
            f0 = zforms.FORMS["f0"]  # the p0 request of runs.build_a (build_a also builds tool arms, which DeepInfra
            p0 = {runs.did(d): models.request(model, runs.cid(name, d, "p0", 1), zforms.prefix_text(data[d]), f0.system,
                                              f0.schema, cell="p0") for d in g["booked"]}  # does not take)
            for (d, c, read), r in by.items():
                if c == "p0" and read == "1":
                    assert body(r) == body(p0[d]), (name, d)
    assert pilot_check.parses({"tool_calls": [{"name": "search_hotels", "input": {"type": ["hotel"]}}]}, "tpar")
    assert pilot_check.FORM_OF["prep"] == pilot_check.FORM_OF["ppar"] == "f0" and pilot_check.FORM_OF["p1"] == "f1"
    print("  R20 requests: counts, order, update cells against the control, t0 and t1 against era1")


def test_paraphrase():
    """The paraphrases keep the word hotel once and the words JSON object; they are new texts."""
    import groups as grp
    assert tools.SEARCH_DESCRIPTION.count("hotel") == hm.TOOL_PARAPHRASE.count("hotel") == 1
    for old, new in hm.FORM_PARAPHRASE.items():
        assert old.count("hotel") == new.count("hotel") and "JSON object" in new
        assert zforms.FORMS["f0"].system.count(old) == 1
    grp.assert_new_text(tools.NEW_TEXTS + hm.NEW_TEXTS)
    assert hm.paraphrased_tool()["input_schema"] == tools.SEARCH_T0["input_schema"]
    assert hm.paraphrased_form().schema == zforms.FORMS["f0"].schema


def test_money():
    assert l2.RESERVE == 0.0 and budget_gate.RESERVE == 2.00 and l2.MAX_BOUND == 8.00
    assert newmoney.CAPS == {"openai_r9": 24.00, "anthropic_r9a": 1.50, "anthropic_r9b": 1.50, "deepinfra_main": 12.00}
    assert set(newmoney.runs_of("anthropic_r9b")) == {"erl2_sonnet_a"}
    assert set(newmoney.runs_of("anthropic_r9a")) == {"erl2_sonnet_b", "erl2_haiku"}
    assert set(newmoney.runs_of("openai_r9")) == {"erl2_sol", "erl2_luna", "erk_sol", "erk_luna"}
    for acc in newmoney.CAPS:
        assert newmoney.used(acc) >= 0
        assert raises(newmoney.check, acc, newmoney.CAPS[acc] + 0.01, kinds=(SystemExit,))
    assert raises(newmoney.check, "deepinfra", 0.01, kinds=(SystemExit,))


def test_402():
    """A DeepInfra HTTP 402 inside a run of R10-19 or R10-20 ends with a clean stop; other errors still raise."""
    import openai_compat as oc
    saved_main, saved_argv = oc.main, sys.argv
    try:
        def fake(name, build, planning, account):
            raise RuntimeError(f"{name}: HTTP 402 from deepinfra: b'{{\"detail\": \"balance\"}}'")
        oc.main, sys.argv = fake, ["x", "estimate"]
        try:
            runs.main("erk_qwen")
            raise AssertionError("no stop")
        except SystemExit as x:
            assert str(x).startswith("Stopped. erk_qwen: DeepInfra answered HTTP 402"), x
        assert raises(runs.main, "ery_qwen", kinds=(RuntimeError,))  # an older run keeps the old behaviour

        def other(name, build, planning, account):
            raise RuntimeError(f"{name}: HTTP 401 from deepinfra: b'bad key'")
        oc.main = other
        assert raises(runs.main, "erl2_gemma", kinds=(RuntimeError,))
    finally:
        oc.main, sys.argv = saved_main, saved_argv


if __name__ == "__main__":
    only = sys.argv[1:]
    for fname, fn in list(globals().items()):
        if fname.startswith("test_") and callable(fn) and (not only or fname in only):
            fn()
            print("ok", fname)
    print("PASS")
