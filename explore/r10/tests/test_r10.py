"""Offline tests of the round-10 modules that Opus wrote (review/plan15/ACTION-PLAN.md section 2.8): tools.py,
stage2.py, runs.py, budget_gate.py and the protocol lock. No network call, no key, no sealed file.

Usage (from explore/): .venv/bin/python -I r10/tests/test_r10.py
"""
import json
import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
sys.path.insert(0, str(R10))
sys.path.insert(0, str(R10.parent / "lib"))
import accounts  # noqa: E402
import briefsearch  # noqa: E402
import budget_gate  # noqa: E402
import groups as grp  # noqa: E402
import models  # noqa: E402
import runs  # noqa: E402
import stage2  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402


def raises(fn, *args):
    try:
        fn(*args)
    except (SystemExit, AssertionError, ValueError):
        return True
    raise AssertionError(f"{fn.__name__} did not refuse")


def sentences(text):
    return [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]


def test_tool_texts():
    for arm, form in (("t0", "f0"), ("t1", "f1"), ("t0ask", "f0")):
        old, new = sentences(zforms.FORMS[form].system), sentences(tools.tool_system(arm))
        changed = [s for s in new if s not in old]
        assert len(old) == len(new), arm
        assert all(any(t in s for t in (tools.ASK_NEW.rstrip("."), tools.END_NEW.rstrip("."), tools.END_NEW_ASK.rstrip(".")))
                   for s in changed), (arm, changed)
        assert len(changed) == 2, (arm, changed)
    t0, t1 = json.dumps(tools.SEARCH_T0["input_schema"]), json.dumps(tools.SEARCH_T1["input_schema"])
    p0, p1 = set(tools.SEARCH_T0["input_schema"]["properties"]), set(tools.SEARCH_T1["input_schema"]["properties"])
    assert p1 == (p0 - {"type"}) | {"property_kind"}, (p0, p1)
    assert "large_property" in t1 and "large_property" not in t0 and t0 != t1
    assert all(t["strict"] is True for t in (tools.SEARCH_T0, tools.SEARCH_T1, tools.ASK))
    grp.assert_new_text(tools.NEW_TEXTS)
    print("ok test_tool_texts")


def test_parse_call():
    call = {"name": None, "area": ["north"], "pricerange": None, "stars": None, "type": ["hotel"], "parking": None,
            "internet": None}
    assert tools.parse_call({"tool_calls": [{"id": "a", "name": "search_hotels", "input": call}]}, "t0")[1]["type"] == ("hotel",)
    assert tools.parse_call({"tool_calls": [], "text": "hello"}, "t0") == ("none", "hello")
    assert tools.parse_call({"tool_calls": [{"id": "a", "name": "ask_traveller", "input": {"question": "Q?"}}]}, "t0ask") == ("ask", "Q?")
    assert tools.parse_call({"tool_calls": [{"id": "a", "name": "ask_traveller", "input": {"question": "Q?"}}]}, "t0")[0] == "invalid"
    assert tools.parse_call({"tool_calls": [{"id": "a", "name": "search_hotels", "input": None}]}, "t0")[0] == "invalid"
    nulls = dict(call, name="null", stars="null", parking=["null"])  # amendment R10-3: the Claude form of null
    got = tools.parse_call({"tool_calls": [{"id": "a", "name": "search_hotels", "input": nulls}]}, "t0")[1]
    assert got["name"] is None and got["stars"] is None and got["parking"] is None and got["type"] == ("hotel",)
    two = {"tool_calls": [{"id": "a", "name": "search_hotels", "input": call}] * 2}
    assert tools.parse_call(two, "t0")[0] == "invalid"
    print("ok test_parse_call")


def test_tool_requests_per_provider():
    sys_text = tools.tool_system("t0")
    a = models.request("sonnet", "x-1", "hi", sys_text, None, tools=tools.TOOLS["t0ask"], cell="t0ask")
    assert a["params"]["tool_choice"] == {"type": "auto", "disable_parallel_tool_use": True}
    assert a["params"]["tools"][0]["input_schema"] == tools.SEARCH_T0["input_schema"] and a["cell"] == "t0ask"
    assert "format" not in a["params"]["output_config"]
    assert runs.anth.wire(a) == {"custom_id": "x-1", "params": a["params"]}
    o = models.request("sol", "x-1", "hi", sys_text, None, tools=tools.TOOLS["t0"], cell="t0")
    assert o["body"]["tools"] == [{"type": "function", "name": "search_hotels", "description": tools.SEARCH_DESCRIPTION,
                                   "parameters": tools.SEARCH_T0["input_schema"], "strict": True}]
    assert o["body"]["tool_choice"] == "auto" and o["body"]["parallel_tool_calls"] is False and "text" not in o["body"]
    assert runs.oc.cell(o) == ("gpt-6.1-sol", "low", "t0")
    # a request without the new arguments is byte-identical to the old form
    plain = models.request("sonnet", "x-2", "hi", "sys", zforms.FORMS["f0"].schema)
    assert "cell" not in plain and "tools" not in plain["params"] and list(plain) == ["custom_id", "params"]
    print("ok test_tool_requests_per_provider")


def fake_rows(short):
    """Two stage-1 pilot rows: one t0 call that keeps hotel (gets a step-2 request), one that keeps guesthouse."""
    reqs = [r for r in runs.requests(f"era1_{short}") if r.get("cell") == "t0"][:2]
    call_h = {"name": None, "area": ["north"], "pricerange": None, "stars": None, "type": ["hotel"], "parking": None,
              "internet": None}
    call_g = dict(call_h, type=["guesthouse"])
    rows = []
    for r, call in zip(reqs, (call_h, call_g)):
        row = {"custom_id": r["custom_id"], "type": "succeeded", "text": "",
               "tool_calls": [{"id": "call_1", "name": "search_hotels", "input": call}]}
        if models.PROVIDER[short] == "anthropic":
            row["content"] = [{"type": "thinking", "thinking": "", "signature": "sig"},
                              {"type": "tool_use", "id": "call_1", "name": "search_hotels", "input": call}]
        else:
            row["output_items"] = [{"type": "reasoning", "id": "rs_1", "summary": [], "encrypted_content": "enc"},
                                   {"type": "function_call", "id": "fc_1", "call_id": "call_1", "name": "search_hotels",
                                    "arguments": json.dumps(call)}]
        rows.append(row)
    return reqs, rows


def test_stage2():
    db = briefsearch.gold.hotel_db()
    for short in ("sonnet", "sol"):
        reqs, rows = fake_rows(short)
        with tempfile.TemporaryDirectory() as tmp:
            saved = stage2.EXPLORE
            stage2.EXPLORE = pathlib.Path(tmp)
            (stage2.EXPLORE / f"era1_{short}").mkdir()
            (stage2.EXPLORE / f"era1_{short}" / "pilot_raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
            try:
                out = stage2.requests(short, "pilot", db)
            finally:
                stage2.EXPLORE = saved
        assert len(out) == 1, (short, len(out))
        want = json.dumps(briefsearch.result_rows(briefsearch.search(db, tools.parse_call(rows[0], "t0")[1])))
        s2 = out[0]
        assert s2["custom_id"].startswith(f"era2_{short}-") and "-s2-" in s2["custom_id"]
        if short == "sonnet":
            msgs = s2["params"]["messages"]
            assert msgs[0] == reqs[0]["params"]["messages"][0] and msgs[1]["content"] == rows[0]["content"]
            assert msgs[2]["content"][0] == {"type": "tool_result", "tool_use_id": "call_1", "content": want}
            assert msgs[3] == {"role": "system", "content": stage2.STEP2_TEXT} and len(msgs) == 4  # amendment R10-2
            assert s2["params"]["system"] == reqs[0]["params"]["system"]
        else:
            items = s2["body"]["input"]
            assert items[:2] == reqs[0]["body"]["input"] and items[2:4] == rows[0]["output_items"]
            assert items[4] == {"type": "function_call_output", "call_id": "call_1", "output": want}
            assert items[5] == {"role": "system", "content": stage2.STEP2_TEXT} and len(items) == 6  # amendment R10-2
        assert s2["cell"] in ("s2_empty", "s2_nonempty")
    print("ok test_stage2")


def test_runs():
    for name, run in runs.RUNS.items():
        if run.exp in ("A2", "H") or (run.exp == "Q" and getattr(run.build, "round", 1) > 1):
            continue  # A2 needs stage-1 answers; H needs pairs.py (its own test); R10-23 rounds 2 to 4 need the
            # answers of the round before (test_steer3_harmless3.py tests them)
        reqs = runs.requests(name)
        assert len({r["custom_id"] for r in reqs}) == len(reqs)
        model_ids = {(r.get("params") or r.get("body"))["model"] for r in reqs}
        assert len(model_ids) == 1, (name, model_ids)
        assert all(r.get("cell") for r in reqs), name
    planted = runs.RUNS["ere_opus"]
    data, g = runs.context()
    pool_id = sorted(runs.anth.trackp_pool(data))[0]
    bad = dict(g, s1t=[pool_id] + g["s1t"][:2], s3=[], s2=[])
    reqs = planted.build("ere_opus", "opus", 1, data, bad)
    assert raises(grp.assert_unprotected, {r["custom_id"].split("-")[1] + ".json" for r in reqs}, data)
    print("ok test_runs")


def test_budget():
    free = budget_gate.free("anthropic_r9a")
    assert budget_gate.fits("anthropic_r9a", round(free, 2) - 0.01)
    assert not budget_gate.fits("anthropic_r9a", free + 0.01)
    with tempfile.TemporaryDirectory() as tmp:
        saved = budget_gate.CONSOLE
        budget_gate.CONSOLE = pathlib.Path(tmp) / "console.json"
        acc = accounts.ACCOUNTS["openai_r9"]
        committed = accounts.committed(acc)
        # A console balance below the free money of the ledger, so that the console balance sets the limit. (The
        # balance was 10.0 USD; on 2026-11-14 the free money of openai_r9 fell below 10 USD and the test failed.)
        balance = max(0.0, (acc.limit - committed) / 2)
        budget_gate.CONSOLE.write_text(json.dumps({"openai_r9": {"balance": balance, "committed_then": 0.0}}))
        try:
            assert abs(budget_gate.free("openai_r9") - (balance - budget_gate.RESERVE)) < 1e-9
        finally:
            budget_gate.CONSOLE = saved
    print("ok test_budget")


def test_lock():
    text = "# P\n\n## Round 10 runs\n\nA1 holds.\n\n## Round 10 amendments\n\nnone\n"
    h = runs.section_hash(text)
    assert h == runs.section_hash(text.replace("none", "an amendment")), "an amendment changed the locked hash"
    assert h != runs.section_hash(text.replace("A1 holds", "A1 fails")), "a prediction change kept the hash"
    assert runs.section_hash("# P\n") is None
    with tempfile.TemporaryDirectory() as tmp:
        saved = runs.PROTOCOL, runs.LOCK
        runs.PROTOCOL, runs.LOCK = pathlib.Path(tmp) / "PROTOCOL.md", pathlib.Path(tmp) / "lock.json"
        try:
            runs.PROTOCOL.write_text("# P\n")
            assert raises(runs.check_lock)
            runs.PROTOCOL.write_text(text)
            assert raises(runs.check_lock)  # no lock file
            runs.LOCK.write_text(json.dumps({"sha256": runs.section_hash(text)}))
            runs.check_lock()
            runs.PROTOCOL.write_text(text.replace("A1 holds", "A1 fails"))
            assert raises(runs.check_lock)
        finally:
            runs.PROTOCOL, runs.LOCK = saved
    print("ok test_lock")


def main():
    test_tool_texts()
    test_parse_call()
    test_tool_requests_per_provider()
    test_stage2()
    test_runs()
    test_budget()
    test_lock()
    print("r10 test passed")


if __name__ == "__main__":
    main()
