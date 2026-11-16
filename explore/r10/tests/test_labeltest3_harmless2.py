"""Offline tests of r10/labeltest3.py (amendment R10-21), r10/harmless2.py (amendment R10-22) and the R10-21 cap of
r10/newmoney.py. No network call, no key, no sealed file, no em* folder.

Usage (from explore/): .venv/bin/python -I r10/tests/test_labeltest3_harmless2.py [test name ...]
"""
import copy
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
import harmless2 as h2  # noqa: E402
import labeltest2 as l2  # noqa: E402
import labeltest3 as l3  # noqa: E402
import newmoney  # noqa: E402
import pilot_check  # noqa: E402
import runs  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

T0_LINE = "type: guesthouse, hotel."
ENUM = ("tools", 0, "parameters", "properties", "type", "anyOf", 2, "items", "enum")


def raises(fn, *args, kinds=(ValueError,)):
    try:
        fn(*args)
    except kinds:
        return True
    raise AssertionError(f"{fn.__name__} did not refuse {args!r}")


def body(r):
    return r.get("params") or r["body"]


def at(obj, path):
    for k in path:
        obj = obj[k]
    return obj


def put(obj, path, value):
    at(obj, path[:-1])[path[-1]] = value


def stored_t0(model):
    """{prefix id: body of the stored era1_<model> t0 request, read 1}."""
    out = {}
    with open(EXPLORE / f"era1_{model}" / "requests.jsonl") as fh:
        for line in fh:
            r = json.loads(line)
            _, d, cell, read = r["custom_id"].split("-")
            if cell == "t0" and read == "1":
                out[d] = body(r)
    assert len(out) == 554, (model, len(out))
    return out


def test_arms_r21():
    """Each arm changes only the type line of the t0 system text and the type enum of the t0 tool; the texts and the
    schemas equal the R10-19 form arms with the two tool sentences."""
    base = tools.tool_system("t0")
    assert base.count(T0_LINE) == 1
    assert l3.TYPE_LINE == {"tl_hotel": "type: guesthouse, hotel (any venue type that is not a guesthouse).",
                            "tl_code": "type: guesthouse, category_A (any venue type that is not a guesthouse).",
                            "tl_neutral": "type: guesthouse, serviced_property (any venue type that is not a guesthouse)."}
    for cell in l3.CELLS:
        s = l3.system(cell)
        assert s == base.replace(T0_LINE, l3.TYPE_LINE[cell]), cell
        form = l2.FORMS[l3.ARM_OF[cell]]
        assert s == zforms.once(zforms.once(form.system, tools.ASK_OLD, tools.ASK_NEW), tools.END_OLD, tools.END_NEW)
        t, t0 = l3.tool(cell), copy.deepcopy(tools.SEARCH_T0)
        assert t["input_schema"] == form.schema, cell
        assert list(t["input_schema"]["properties"]) == list(t0["input_schema"]["properties"])
        enum = t["input_schema"]["properties"]["type"]["anyOf"][2]["items"]["enum"]
        assert enum == ["guesthouse", l3.LABELS[cell]], (cell, enum)
        t["input_schema"]["properties"]["type"]["anyOf"][2]["items"]["enum"] = ["guesthouse", "hotel"]
        assert t == t0, cell
    assert l3.tool("tl_hotel") == tools.SEARCH_T0
    print("  R21 arms: the type line and the enum only; equal to the R10-19 form arms")


def test_requests_r21():
    """Counts, order, and each request against the stored era1 t0 request of the same prefix (read 1)."""
    assert {n for n, r in runs.RUNS.items() if r.exp == "L3"} == set(l3.RUNS)
    for name, want in (("erl3_sol", 554 * 3 * 3), ("erl3_luna", 554 * 3 * 4)):
        model = runs.RUNS[name].model
        assert runs.RUNS[name].account == "openai_r9"
        reqs = runs.requests(name)
        assert len(reqs) == want, (name, len(reqs))
        for i in range(0, len(reqs), 3):  # the three arms of one prefix and read follow each other
            assert [r["cell"] for r in reqs[i:i + 3]] == list(l3.CELLS)
            assert len({r["custom_id"].rsplit("-", 2)[0] + r["custom_id"].rsplit("-", 1)[1] for r in reqs[i:i + 3]}) == 1
        prev = stored_t0(model)
        reads = {}
        for r in reqs:
            _, d, cell, read = r["custom_id"].split("-")
            reads.setdefault(d, set()).add(int(read))
            x, c = copy.deepcopy(body(r)), copy.deepcopy(prev[d])
            assert x["input"][0]["role"] == "system"
            assert x["input"][0]["content"] == c["input"][0]["content"].replace(T0_LINE, l3.TYPE_LINE[cell])
            x["input"][0]["content"] = c["input"][0]["content"]
            assert at(x, ENUM) == ["guesthouse", l3.LABELS[cell]]
            put(x, ENUM, ["guesthouse", "hotel"])
            assert x == c, (name, d, cell)
        assert len(reads) == 554 and all(v == set(range(1, l3.READS[name] + 1)) for v in reads.values())
    print("  R21 requests: counts, order, against the stored era1 t0 requests")


def test_parse_r21():
    """The label maps back to hotel; a value outside the arm is not valid; the other kinds of tools.parse_call."""
    def call(t, **kw):
        args = {"name": "null", "area": None, "pricerange": None, "stars": None, "type": t, "parking": None,
                "internet": None, **kw}
        return {"tool_calls": [{"name": "search_hotels", "input": args}]}
    for cell in l3.CELLS:
        k, f = l3.parse_call(call(["guesthouse", l3.LABELS[cell]]), cell)
        assert k == "search" and f["type"] == ("guesthouse", "hotel") and f["name"] is None, (cell, k, f)
        assert l3.parse_call(call("any"), cell)[0] == "search"
        assert l3.parse_call(call(None), cell)[1]["type"] is None
        assert l3.parse_call({"text": "I need more detail."}, cell) == ("none", "I need more detail.")
        two = {"tool_calls": call(["guesthouse"])["tool_calls"] * 2}
        assert l3.parse_call(two, cell)[0] == "invalid"
        other = {"tool_calls": [{"name": "ask_traveller", "input": {"question": "Which area?"}}]}
        assert l3.parse_call(other, cell)[0] == "invalid"
    for cell, wrong in (("tl_code", "hotel"), ("tl_neutral", "hotel"), ("tl_hotel", "category_A"),
                        ("tl_code", "serviced_property")):
        assert l3.parse_call(call([wrong]), cell)[0] == "invalid", (cell, wrong)
    assert raises(l3.parse_call, call(["hotel"]), "t0", kinds=(RuntimeError,))
    for cell in l3.CELLS:
        assert pilot_check.parses(call([l3.LABELS[cell]]), cell) and cell in pilot_check.TOOL_CELLS
        assert not pilot_check.parses({"text": "no call"}, cell)  # the pilot check wants a search call
    print("  R21 parse: labels, values outside the arm, none, two calls, another tool")


def test_requests_r22():
    """Counts, order; t0 equals the stored era1 t0; tord differs only in the order; tpar2 only in the description."""
    assert {n for n, r in runs.RUNS.items() if r.exp == "K2"} == set(h2.RUNS)
    order = ["area", "internet", "name", "parking", "pricerange", "stars", "type"]
    for name in h2.RUNS:
        model = runs.RUNS[name].model
        assert model == h2.MODEL_OF[name] and runs.RUNS[name].account == "openai_r9"
        reqs = runs.requests(name)
        assert len(reqs) == 3 * 1085, (name, len(reqs))
        for i in range(0, len(reqs), 3):
            assert [r["cell"] for r in reqs[i:i + 3]] == ["t0", "tord", "tpar2"]
        by = {tuple(r["custom_id"].split("-")[1:]): r for r in reqs}
        prev = stored_t0(model)
        for (d, cell, read), r in by.items():
            x, c = copy.deepcopy(body(r)), copy.deepcopy(body(by[(d, "t0", read)]))
            if cell == "t0":
                assert x == prev[d], (name, d, read)  # byte for byte in the body (the dicts and their key order)
                assert json.dumps(x) == json.dumps(prev[d])
            elif cell == "tord":
                p, q = x["tools"][0]["parameters"], c["tools"][0]["parameters"]
                assert list(p["properties"]) == order and p["required"] == order
                assert list(q["properties"]) == list(tools.SEARCH_T0["input_schema"]["properties"])
                assert json.dumps(x, sort_keys=True) != json.dumps(c, sort_keys=True)  # the required list differs
                p["required"] = sorted(p["required"])
                q["required"] = sorted(q["required"])
                assert json.dumps(x, sort_keys=True) == json.dumps(c, sort_keys=True), (name, d)
            else:
                assert x["tools"][0]["description"] == h2.TOOL_PARAPHRASE2
                assert c["tools"][0]["description"] == tools.SEARCH_DESCRIPTION
                x["tools"][0]["description"] = c["tools"][0]["description"]
                assert json.dumps(x) == json.dumps(c), (name, d)
        set_of = control.set_of(*runs.context())
        n = {s: sum(1 for (d, cell, _) in by if cell == "t0" and set_of[d + ".json"] == s)
             for s in ("open", "specific", "guesthouse")}
        assert n == {"open": 448, "specific": 590, "guesthouse": 47}, n
    for cell in ("tord", "tpar2"):
        assert pilot_check.parses({"tool_calls": [{"name": "search_hotels", "input": {"type": ["hotel"]}}]}, cell)
        assert h2.parse_row({"tool_calls": [{"name": "search_hotels", "input": {"type": ["hotel"]}}]}, cell)[0] == "search"
    assert raises(h2.parse_row, {}, "t1", kinds=(RuntimeError,))
    print("  R22 requests: counts, order, t0 against era1, tord and tpar2 against t0")


def test_paraphrase2():
    """The second paraphrase keeps the word hotel once, is a new text, and differs from the R10-20 paraphrase."""
    import groups as grp
    p = h2.TOOL_PARAPHRASE2
    assert tools.SEARCH_DESCRIPTION.count("hotel") == p.count("hotel") == 1
    assert p not in (tools.SEARCH_DESCRIPTION, hm.TOOL_PARAPHRASE)
    grp.assert_new_text(tools.NEW_TEXTS + h2.NEW_TEXTS)
    t = h2.paraphrased_tool2()
    assert t["input_schema"] == tools.SEARCH_T0["input_schema"] and t["name"] == "search_hotels"
    assert {k: v for k, v in t.items() if k != "description"} == \
        {k: v for k, v in tools.SEARCH_T0.items() if k != "description"}
    assert h2.TOOL_OF["tord"] == [control.ordered_tool()]
    print("  R22 paraphrase: hotel once, new text, not the R10-20 text")


def test_money_r21():
    assert l3.RESERVE == 0.0 and l3.MAX_BOUND == 8.00 and budget_gate.RESERVE == 2.00
    assert newmoney.CAPS_R21 == {"openai_r9": 13.50}
    assert newmoney.CAPS == {"openai_r9": 24.00, "anthropic_r9a": 1.50, "anthropic_r9b": 1.50, "deepinfra_main": 12.00}
    assert set(newmoney.runs_of("openai_r9", newmoney.R21)) == {"erl3_sol", "erl3_luna", "erk2_sol", "erk2_luna"}
    assert set(newmoney.runs_of("openai_r9")) == {"erl2_sol", "erl2_luna", "erk_sol", "erk_luna"}  # R19 unchanged
    assert newmoney.used("openai_r9", newmoney.R21) >= 0
    assert raises(newmoney.check, "openai_r9", 13.51 - newmoney.used("openai_r9", newmoney.R21), newmoney.R21,
                  kinds=(SystemExit,))
    for acc in ("anthropic_r9a", "anthropic_r9b", "deepinfra_main"):
        assert raises(newmoney.check, acc, 0.01, newmoney.R21, kinds=(SystemExit,))
    print("  R21 money: the cap, the runs, the refusals")


def test_main_guards():
    """runs.main stops a step above the step limit and a step above the cap, before the client starts."""
    import openai_compat as oc
    saved_main, saved_argv, saved_used = oc.main, sys.argv, newmoney.used

    def reached(*a, **kw):
        raise AssertionError("the client was reached")
    try:
        oc.main = reached
        for name in (*l3.RUNS, *h2.RUNS):
            sys.argv = ["x", "submit", "--approve", "8.01"]
            try:
                runs.main(name)
                raise AssertionError("no stop")
            except SystemExit as x:
                assert "allow at most 8.00 USD per step" in str(x), x
            newmoney.used = lambda account, group=newmoney.R19: 13.00 if group == newmoney.R21 else 0.0
            sys.argv = ["x", "submit", "--approve", "0.60"]
            try:
                runs.main(name)
                raise AssertionError("no stop")
            except SystemExit as x:
                assert "would pass the cap of 13.50 USD" in str(x), x
            newmoney.used = saved_used
    finally:
        oc.main, sys.argv, newmoney.used = saved_main, saved_argv, saved_used
    print("  main: step limit and cap stop before the client")


if __name__ == "__main__":
    only = sys.argv[1:]
    for fname, fn in list(globals().items()):
        if fname.startswith("test_") and callable(fn) and (not only or fname in only):
            fn()
            print("ok", fname)
    print("PASS")
