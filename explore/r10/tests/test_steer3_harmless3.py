"""Offline tests of r10/steer3.py (amendment R10-23), r10/harmless3.py (amendment R10-24) and the R23 cap group of
r10/newmoney.py. No network call, no key, no sealed file, no em* folder.

Usage (from explore/): .venv/bin/python -I r10/tests/test_steer3_harmless3.py [test name ...]
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
import flag  # noqa: E402
import harmless as hm  # noqa: E402
import harmless3 as h3  # noqa: E402
import newmoney  # noqa: E402
import pilot_check  # noqa: E402
import runs  # noqa: E402
import steer2  # noqa: E402
import steer3 as s3  # noqa: E402
import tools  # noqa: E402
import turns  # noqa: E402

OLD_SYSTEM = tools.tool_system("t0")


def raises(fn, *args, kinds=(ValueError,)):
    try:
        fn(*args)
    except kinds:
        return True
    raise AssertionError(f"{fn.__name__} did not refuse {args!r}")


def stored(folder):
    """{custom_id: request} of a stored requests.jsonl (Anthropic: the request; OpenAI: the batch line)."""
    assert not folder.startswith("em")
    out = {}
    for line in (EXPLORE / folder / "requests.jsonl").read_text().splitlines():
        r = json.loads(line)
        out[r["custom_id"]] = r
    return out


def test_texts():
    """The system text is the R10-7 text; the call limit and the error text are those of R10-8 (turns.py)."""
    assert s3.MAX_CALLS == turns.MAX_CALLS == 4
    assert s3.SYSTEM == flag.multi_system("t0")
    assert s3.SYSTEM == OLD_SYSTEM.replace(tools.ASK_NEW, flag.MULTI_ASK).replace(tools.END_NEW, flag.MULTI_END)
    assert s3.SYSTEM.count(flag.MULTI_ASK) == 1 and s3.SYSTEM.count(flag.MULTI_END) == 1
    assert f'"content": "{s3.ERROR_RESULT}"' in (R10 / "turns.py").read_text()
    assert s3.tool_of("t0") == tools.TOOLS["t0"]
    assert s3.tool_of("h1") == [steer2.cell_tool("h1")] and s3.tool_of("g1") == [steer2.cell_tool("g1")]
    import steer
    assert s3.tool_of("h1") == [steer.steered_tool("h")] and s3.tool_of("g1") == [steer.steered_tool("g")]
    s3.check_amendment()
    h3.check_amendment()
    print("  texts: R10-7 system text, R10-8 call limit and error text, R10-14 tools")


def test_round1_haiku():
    """Each erq1_haiku request equals the stored ers_haiku request of the same prefix and cell, except the system text
    (the two sentences) and the custom_id. Counts and order."""
    reqs = runs.requests("erq1_haiku")
    old = stored("ers_haiku")
    cmap = {"t0": "t0", "h1": "th", "g1": "tg"}
    assert len(reqs) == 1344
    for i, r in enumerate(reqs):
        _, did, cell, read = r["custom_id"].split("-")
        assert cell == s3.CELLS[i % 3] and read == "1", r["custom_id"]
        o = old[f"ers_haiku-{did}-{cmap[cell]}-1"]
        p, q = copy.deepcopy(r["params"]), copy.deepcopy(o["params"])
        assert p.pop("system") == s3.SYSTEM and q.pop("system") == OLD_SYSTEM
        assert p == q, r["custom_id"]
    data, g = runs.context()
    import control
    sets = control.set_of(data, g)
    assert {r["custom_id"].split("-")[1] + ".json" for r in reqs} == {d for d in g["booked"] if sets[d] == "open"}
    print("  round 1, Haiku: 1,344 requests equal ers_haiku except the system text")


def test_round1_openai():
    """Sol and Luna: each t0 request equals the stored era1 t0 request (read 1) of the same prefix except the system
    item and the custom_id; h1 and g1 differ from t0 only in the tools; Luna's read 2 equals read 1."""
    for model, n in (("sol", 1662), ("luna", 3324)):
        reqs = runs.requests(f"erq1_{model}")
        assert len(reqs) == n, (model, len(reqs))
        old = stored(f"era1_{model}")
        by = {}
        for r in reqs:
            _, did, cell, read = r["custom_id"].split("-")
            by[(did, cell, read)] = r
            if cell == "t0":
                o = old[f"era1_{model}-{did}-t0-1"]["body"]
                b, ob = copy.deepcopy(r["body"]), copy.deepcopy(o)
                assert b["input"][0] == {"role": "system", "content": s3.SYSTEM}
                assert ob["input"][0] == {"role": "system", "content": OLD_SYSTEM}
                b["input"][0], ob["input"][0] = None, None
                assert b == ob, r["custom_id"]
        for (did, cell, read), r in by.items():
            if cell != "t0":
                t0 = by[(did, "t0", read)]["body"]
                assert {k: v for k, v in r["body"].items() if k != "tools"} == \
                    {k: v for k, v in t0.items() if k != "tools"}
                assert r["body"]["tools"][0]["description"] == steer2.cell_tool(cell)["description"]
            if read == "2":
                assert r["body"] == by[(did, cell, "1")]["body"]
        assert {k[2] for k in by} == ({"1", "2"} if model == "luna" else {"1"})
    print("  round 1, Sol and Luna: t0 equals era1 t0 except the system item; h1 and g1 change only the tool")


def fake_call(i, inp, text="", openai=False):
    row = {"type": "succeeded", "stop": "tool_use" if not openai else "end_turn", "text": text, "input_tokens": 10,
           "output_tokens": 5, "tool_calls": [{"id": f"call{i}", "name": "search_hotels", "input": inp}]}
    if openai:
        row["output_items"] = [{"type": "function_call", "call_id": f"call{i}", "name": "search_hotels",
                                "arguments": json.dumps(inp)}]
    else:
        row["content"] = ([{"type": "text", "text": text}] if text else []) + [
            {"type": "tool_use", "id": f"call{i}", "name": "search_hotels", "input": inp}]
    return row


FINAL = {"type": "succeeded", "stop": "end_turn", "text": "Here is what I found.", "input_tokens": 10, "output_tokens": 5}
BASE = {"name": None, "area": ["north"], "pricerange": ["cheap"], "stars": None, "parking": None, "internet": None}


def test_conversation():
    """The history of both providers, the results in the names of the tool, the error result, the call limit and the
    statuses."""
    import gold
    db = gold.hotel_db()
    c = s3.Conv("haiku", "X.json", "h1", 1, "Traveller: I need a cheap hotel in the north.")
    c.add(fake_call(1, {**BASE, "accommodation_type": ["hotel"]}), db)
    c.add(fake_call(2, {**BASE, "accommodation_type": None}), db)
    assert c.status == "open" and len(c.history) == 5
    first = json.loads(c.history[2]["content"][0]["content"])
    second = json.loads(c.history[4]["content"][0]["content"])
    assert first["total"] == 0 and first["results"] == [], first  # no cheap hotel in the north (the paper's example)
    assert second["total"] >= 2 and all("accommodation_type" in x and "type" not in x for x in second["results"])
    assert all(x["accommodation_type"] == "guesthouse" for x in second["results"]), second
    c.add(FINAL, db)
    assert c.status == "complete" and c.reply() == "Here is what I found." and len(c.searches) == 2
    assert c.searches[0]["fields"]["type"] == ("hotel",) and c.searches[1]["fields"]["type"] is None
    # an invalid call gets the error result; the 4th call gets no result
    c2 = s3.Conv("haiku", "X.json", "t0", 1, "x")
    c2.add(fake_call(1, None), db)  # arguments that do not parse as JSON give input None
    tr = c2.history[-1]["content"][0]
    assert tr["content"] == s3.ERROR_RESULT and tr["is_error"] is True and c2.searches[0]["kind"] == "invalid"
    for i in range(2, 5):
        c2.add(fake_call(i, {**BASE, "type": ["hotel"]}), db)
    assert c2.status == "calls" and len(c2.rows) == 4 and len(c2.history) == 7
    raises(c2.add, FINAL, db, kinds=(AssertionError,))
    # OpenAI: output items back, then a function_call_output item; t0 rows keep the field name "type"
    co = s3.Conv("sol", "X.json", "t0", 1, "x")
    co.add(fake_call(1, {**BASE, "type": None}, openai=True), db)
    assert co.history[0] == {"role": "system", "content": s3.SYSTEM} and co.history[1]["role"] == "user"
    assert co.history[2]["type"] == "function_call" and co.history[3]["type"] == "function_call_output"
    assert co.history[3]["call_id"] == "call1" and "type" in json.loads(co.history[3]["output"])["results"][0]
    # statuses: failed, cut, two calls
    for row, st in (({"type": "errored"}, "failed"), ({**FINAL, "stop": "max_tokens"}, "cut"),
                    ({**fake_call(1, BASE), "tool_calls": fake_call(1, BASE)["tool_calls"] * 2}, "multi")):
        x = s3.Conv("haiku", "X.json", "t0", 1, "x")
        x.add(row, db)
        assert x.status == st, (st, x.status)
    # display: g1 keeps the names; h1 renames only type
    rows = {"results": [{"name": "a", "type": "hotel", "area": "north", "pricerange": "cheap", "stars": "4"}], "total": 1}
    assert s3.display(rows, "g1") == rows and s3.display(rows, "t0") is rows
    assert s3.display(rows, "h1")["results"][0] == {"name": "a", "accommodation_type": "hotel", "area": "north",
                                                     "pricerange": "cheap", "stars": "4"}
    print("  conversation: history, display, error result, call limit, statuses")


def test_rounds():
    """Round k requests come from the stored rows of rounds 1 to k - 1: only open conversations, the right history."""
    data, g = runs.context()
    some = [k for k in s3.keys("haiku", data, g)][:6]  # 2 prefixes x 3 cells
    saved_keys, saved_rows = s3.keys, s3.rows_of
    fake = {}
    for d, cell, read in some:
        p = "accommodation_type" if cell == "h1" else "type"
        fake.setdefault(1, {})[(d, cell, read)] = fake_call(1, {**BASE, p: ["hotel"]})
    d0 = some[0][0]
    fake.setdefault(2, {})[(d0, "t0", 1)] = FINAL  # this conversation ends in round 2
    for d, cell, read in some[1:]:
        p = "accommodation_type" if cell == "h1" else "type"
        fake[2][(d, cell, read)] = fake_call(2, {**BASE, p: None})
    try:
        s3.keys = lambda model, data, g: some
        s3.rows_of = lambda model, k, source: fake.get(k)
        r2 = s3.requests("erq2_haiku", "haiku", data, g)
        assert len(r2) == 6 and all(r["custom_id"].startswith("erq2_haiku-") for r in r2)
        m = r2[0]["params"]["messages"]
        assert [x["role"] for x in m] == ["user", "assistant", "user"] and m[2]["content"][0]["type"] == "tool_result"
        assert r2[0]["params"]["system"] == s3.SYSTEM and r2[0]["params"]["tools"] == tools.TOOLS["t0"]
        r3 = s3.requests("erq3_haiku", "haiku", data, g)
        assert len(r3) == 5 and not any(r["custom_id"].split("-")[1] + ".json" == d0 and
                                        r["custom_id"].split("-")[2] == "t0" for r in r3)
        assert all(len(r["params"]["messages"]) == 5 for r in r3)
        raises(s3.requests, "erq4_haiku", "haiku", data, g, kinds=(RuntimeError,))  # round 3 is not "fetched"
        convs = s3.replay("haiku", 4, data, g, strict=False)
        assert sum(c.status == "complete" for c in convs) == 1 and sum(c.status == "open" for c in convs) == 5
    finally:
        s3.keys, s3.rows_of = saved_keys, saved_rows
    assert raises(runs.requests, "erq2_sol", kinds=(RuntimeError,))  # no round 1 of Sol is fetched
    print("  rounds: open conversations only, append-only history, a missing round stops the build")


def test_pilot_prefixes():
    data, g = runs.context()
    assert s3.pilot_prefixes(data, g) == ["PMUL3592.json", "PMUL0388.json", "MUL1016.json"]
    assert len(s3.pilot_keys(data, g)) == 9
    t = s3.amendment_text()
    assert "(PMUL3592, PMUL0388, MUL1016)" in " ".join(t.split())
    print("  pilot prefixes: the fixed rule gives PMUL3592, PMUL0388, MUL1016")


def test_requests_r24():
    """erk3_deepseek equals the R10-20 requests of erk_deepseek (cells p0 and ppar) except the custom_id and the seed;
    erk3_luna equals the R10-22 requests of erk2_luna (cells t0 and tpar2) except the custom_id."""
    for name, orig in h3.ORIGINAL.items():
        new = runs.requests(name)
        assert len(new) == 2170, (name, len(new))
        old = {r["custom_id"]: r for r in runs.requests(orig)}
        cells = h3.PLAN[name]
        new_seeds = 0
        for i, r in enumerate(new):
            _, did, cell, read = r["custom_id"].split("-")
            assert cell == cells[i % 2]
            o = old[f"{orig}-{did}-{cell}-{read}"]
            b, ob = copy.deepcopy(r["body"]), copy.deepcopy(o["body"])
            if name == "erk3_deepseek":  # the seed comes from the custom_id, so the answers are new
                new_seeds += b.pop("seed") != ob.pop("seed")
            assert b == ob, r["custom_id"]
        assert name != "erk3_deepseek" or new_seeds == len(new), new_seeds
        man = json.loads(runs.MANIFEST.read_text())
        assert man[orig] == {"requests": len(old), "sha256": runs.digest(list(old.values()))}
    assert h3.LEVEL == {"erk3_deepseek": 1 - 0.05 / 6, "erk3_luna": 1 - 0.05 / 4}
    assert hm.FORM_PARAPHRASE[tools.ASK_OLD] in " ".join(h3.amendment_text().split())
    print("  R10-24 requests: equal to the flagged runs except the custom_id (and the DeepSeek seed)")


def test_money_r23():
    assert s3.RESERVE == 0.0 and s3.MAX_BOUND == 4.00 and h3.MAX_BOUND == 1.00 and budget_gate.RESERVE == 2.00
    assert newmoney.CAPS_R23 == {"anthropic_r9b": 0.55, "openai_r9": 6.80, "deepinfra_main": 1.00}
    assert newmoney.CAPS == {"openai_r9": 24.00, "anthropic_r9a": 1.50, "anthropic_r9b": 1.50, "deepinfra_main": 12.00}
    assert newmoney.CAPS_R21 == {"openai_r9": 13.50}
    assert set(newmoney.runs_of("anthropic_r9b", newmoney.R23)) == {f"erq{k}_haiku" for k in (1, 2, 3, 4)}
    assert set(newmoney.runs_of("openai_r9", newmoney.R23)) == \
        {f"erq{k}_{m}" for k in (1, 2, 3, 4) for m in ("sol", "luna")} | {"erk3_luna"}
    assert set(newmoney.runs_of("deepinfra_main", newmoney.R23)) == {"erk3_deepseek"}
    assert set(newmoney.runs_of("openai_r9", newmoney.R21)) == {"erl3_sol", "erl3_luna", "erk2_sol", "erk2_luna"}
    for acc, cap in newmoney.CAPS_R23.items():
        assert newmoney.used(acc, newmoney.R23) >= 0
        assert raises(newmoney.check, acc, cap + 0.01, newmoney.R23, kinds=(SystemExit,))
    assert raises(newmoney.check, "anthropic_r9a", 0.01, newmoney.R23, kinds=(SystemExit,))
    print("  R23 money: the caps, the runs, the refusals; the older groups unchanged")


def test_main_guards():
    """runs.main stops a Q or K3 step above the step limit or above the cap before the client starts, and a pilot of a
    later round."""
    import anth
    import openai_compat as oc
    saved = (anth.main, oc.main, sys.argv, newmoney.used)

    def reached(*a, **kw):
        raise AssertionError("the client was reached")

    def stop(name, words):
        try:
            runs.main(name)
            raise AssertionError("no stop")
        except SystemExit as x:
            assert words in str(x), x
    try:
        anth.main = oc.main = reached
        for name, limit in (("erq1_haiku", 4.00), ("erq2_sol", 4.00), ("erk3_luna", 1.00), ("erk3_deepseek", 1.00)):
            step = "run" if name == "erk3_deepseek" else "submit"
            sys.argv = ["x", step, "--approve", f"{limit + 0.01:.2f}"]
            stop(name, f"allows at most {limit:.2f} USD per step")
            acc = runs.RUNS[name].account
            newmoney.used = lambda account, group=newmoney.R19: (newmoney.CAPS_R23[account] - 0.05
                                                                  if group == newmoney.R23 else 0.0)
            sys.argv = ["x", step, "--approve", "0.10"]
            stop(name, f"would pass the cap of {newmoney.CAPS_R23[acc]:.2f} USD")
            newmoney.used = saved[3]
        sys.argv = ["x", "pilot"]
        stop("erq2_haiku", "covers every round")
    finally:
        anth.main, oc.main, sys.argv, newmoney.used = saved
    print("  main: step limit, cap and later-round pilot stop before the client")


def test_pilot_check_rounds():
    """pilot_check: a round-2 text answer parses; a round-1 cell needs tool calls."""
    row_text = {"custom_id": "erq2_haiku-X-h1-1", "type": "succeeded", "stop": "end_turn", "text": "Found two."}
    assert s3.pilot_parses(row_text, "h1", 2)
    assert not s3.pilot_parses({**row_text, "text": ""}, "h1", 2)
    call = fake_call(1, {**BASE, "accommodation_type": ["hotel"]})
    assert s3.pilot_parses(call, "h1", 1) and not s3.pilot_parses(fake_call(1, None), "h1", 1)
    assert s3.parse(call, "h1")[1]["type"] == ("hotel",)
    assert pilot_check.cell_of("erq3_luna-PMUL0388-g1-1") == "g1"
    print("  pilot_check: the round rule")


def test_old_manifest():
    """The manifest entries of the steering runs and of the flagged runs still rebuild (their requests unchanged)."""
    man = json.loads(runs.MANIFEST.read_text())
    for n in ("ers_haiku", "ers_sonnet", "erm_haiku", "erk_deepseek", "erk2_luna", "era1_sol", "era1_luna"):
        if n in man:
            r = runs.requests(n)
            assert man[n] == {"requests": len(r), "sha256": runs.digest(r)}, n
    print("  old manifest entries of the source runs rebuild unchanged")


if __name__ == "__main__":
    only = sys.argv[1:]
    for fname, fn in list(globals().items()):
        if fname.startswith("test_") and callable(fn) and (not only or fname in only):
            fn()
            print("ok", fname)
    print("PASS")
