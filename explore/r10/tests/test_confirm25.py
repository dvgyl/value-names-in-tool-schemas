"""Offline tests of r10/confirm25.py (amendment R10-25), its run entries in r10/runs.py and the cap group R25 of
r10/newmoney.py. No network call, no key, no sealed file. The held-out answers come only through confirm25 (the frozen
loader); the tests compute no outcome on them (they check which answers get a request).

Usage (from explore/): .venv/bin/python -I r10/tests/test_confirm25.py [test name ...]
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
import confirm25 as c25  # noqa: E402
import forms10  # noqa: E402
import newmoney  # noqa: E402
import pilot_check  # noqa: E402
import runs  # noqa: E402


def raises(fn, *args, kinds=(ValueError,)):
    try:
        fn(*args)
    except kinds:
        return True
    raise AssertionError(f"{fn.__name__} did not refuse {args!r}")


def test_texts():
    """The verifier text is the development text; the held-out original form t_legacy is the development F0 form; the
    user text of a verifier request is the user text of the held-out request of the same dialogue."""
    A = c25.frozen()
    system, fmt, parser = A.wave1.FORMS[c25.FORM]
    f0 = forms10.FORMS["f0"]
    assert system == f0.system and fmt == {"type": "json_schema", "schema": f0.schema} and parser == "f0"
    assert forms10.FORMS["verify"].system == forms10.VERIFY_SYSTEM
    assert forms10.VERIFY_SYSTEM == ("You read a conversation between a traveller and a hotel booking assistant in "
                                     "Cambridge. Does the traveller exclude guesthouses? Answer yes, no, or unclear.")
    assert c25.PARTS == ("nat", "hot") and A.wave1.PARTS["nat"][2] == A.wave1.PARTS["hot"][2] == "orig"
    data, _g = runs.context()
    held = {r["custom_id"]: r for r in A.wave1.requests("sol", data, A.wave1.ids())}
    units, _ = c25.stage1()
    for d in units["natural"][:2] + units["goal_hotel"][:2]:
        part = "nat" if d in units["natural"] else "hot"
        old = held[f"em1_sol-{part}-{d}-t_legacy-1"]["body"]["input"][1]
        new = c25.request("ern_sol", "sol", d + ".json", 1, data)["body"]["input"][1]
        assert old == new and old["role"] == "user", d
    c25.check_amendment()
    print("  texts: the development verifier, t_legacy = F0, the same user text as the held-out request")


def test_requests_equal_dev():
    """On a development dialogue, the request of confirm25.request equals the request of the development verifier run
    (the rebuilt request, which r10/manifest.json checks, and the stored requests.jsonl line) except the custom_id
    (and on DeepInfra the seed, which comes from the custom_id)."""
    data, _g = runs.context()
    for model, dev in (("sol", "erb_sol"), ("luna", "erb_luna"), ("haiku", "erb_haiku"), ("sonnet", "erb_sonnet"),
                       ("deepseek", "ery_deepseek"), ("qwen", "ery_qwen"), ("gemma", "ery_gemma")):
        old = [r for r in runs.requests(dev) if r["cell"] == "verify"][:3]
        stored = {}
        path = EXPLORE / dev / "requests.jsonl"
        if path.exists():
            for line in path.read_text().splitlines():
                x = json.loads(line)
                stored[x["custom_id"]] = x
        for o in old:
            _, did, cell, read = o["custom_id"].split("-")
            n = c25.request(c25.RUN_OF[model], model, did + ".json", int(read), data)
            assert n["custom_id"] == f"{c25.RUN_OF[model]}-{did}-verify-{read}" and n["cell"] == "verify"
            key = "params" if "params" in o else "body"
            a, b = copy.deepcopy(n[key]), copy.deepcopy(o[key])
            if key == "body" and "seed" in a:
                assert a.pop("seed") != b.pop("seed")
            assert a == b, (model, o["custom_id"])
            if o["custom_id"] in stored:
                s = stored[o["custom_id"]]
                assert (s.get("params") or s.get("body")) == o[key], (model, o["custom_id"])
    print("  requests: equal to the development verifier requests except the custom_id (and the DeepInfra seed)")


def allowed_ids(s):
    return set(s["NT"] + s["H"] + s["G"])


def test_sets_and_guard():
    data, _g = runs.context()
    s, rep = c25.sets(data)
    assert {k: len(v) for k, v in s.items()} == c25.SIZES and {k: len(v) for k, v in rep.items()} == c25.REPEAT_SIZES
    assert not set(s["NT"]) & set(s["H"]) and not set(s["H"]) & set(s["G"])
    lists = c25.frozen().wave1.ids()
    c25.assert_stage1(set(s["NT"] + s["H"] + s["G"]))
    assert raises(c25.assert_stage1, {lists["gate"][0]})
    stage2 = [d for d in lists["sample"] if d in set(lists["natural"]) | set(lists["goal_hotel"])]
    assert stage2 and raises(c25.assert_stage1, {stage2[0]})
    g = runs.context()[1]
    assert raises(c25.assert_stage1, {g["s1t"][0]})  # a development dialogue
    other = [d for d in lists["pool"] if d not in allowed_ids(s) and d not in set(lists["sample"])]
    assert other and raises(c25.assert_stage1, {other[0]})  # a pool dialogue that is neither natural nor goal-hotel
    print("  sets: NT 213, H 66, G 11, LN 187, LG 19, LH 74; the guard refuses gate, stage-2 and other dialogues")


def test_build():
    """Each model: one request per valid t_legacy answer with a hotel-only filter (parts nat and hot, every read), in
    order; the ids are stage-1 ids; the runs equal confirm25.PLAN."""
    data, _g = runs.context()
    s, _ = c25.sets(data)
    allowed = set(s["NT"] + s["H"] + s["G"])
    for name, (model, account, pilot) in c25.PLAN.items():
        run = runs.RUNS[name]
        assert (run.exp, run.model, run.account, run.reads, run.pilot) == ("V", model, account, 1, pilot)
        reqs = runs.requests(name)
        keys = c25.call_keys(model, data)
        assert len(reqs) == len(keys) and len({r["custom_id"] for r in reqs}) == len(reqs)
        orig = c25.original_reads(model, data)
        for r, (d, read) in zip(reqs, keys):
            assert r["custom_id"] == f"{name}-{d.removesuffix('.json')}-verify-{read}" and r["cell"] == "verify"
            assert d in allowed and orig[(d, read)] is not None and c25.hotel_only(orig[(d, read)]["type"])
        n_ho = sum(1 for f in orig.values() if f is not None and c25.hotel_only(f["type"]))
        assert n_ho == len(keys)
        both = sum(1 for f in orig.values() if f is not None and isinstance(f["type"], tuple)
                   and {"hotel", "guesthouse"} <= set(f["type"]))
        print(f"  {name}: {len(reqs)} requests ({both} answers with both types get none)")
    assert tuple(n for n in runs.RUNS if runs.RUNS[n].exp == "V") == c25.RUNS


def test_money():
    assert c25.MAX_BOUND == 1.50 and c25.RESERVE == 0.0 and budget_gate.RESERVE == 2.00
    assert newmoney.CAPS_R25 == {"deepinfra_main": 2.00, "openai_r9": 1.60, "anthropic_r9a": 0.45}
    assert newmoney.CAPS_R23 == {"anthropic_r9b": 0.55, "openai_r9": 6.80, "deepinfra_main": 1.00}
    assert newmoney.CAPS == {"openai_r9": 24.00, "anthropic_r9a": 1.50, "anthropic_r9b": 1.50, "deepinfra_main": 12.00}
    assert newmoney.CAPS_R21 == {"openai_r9": 13.50}
    assert set(newmoney.runs_of("deepinfra_main", newmoney.R25)) == {"ern_deepseek", "ern_qwen", "ern_gemma"}
    assert set(newmoney.runs_of("openai_r9", newmoney.R25)) == {"ern_luna", "ern_sol"}
    assert set(newmoney.runs_of("anthropic_r9a", newmoney.R25)) == {"ern_haiku", "ern_sonnet"}
    assert "ern_sol" not in newmoney.runs_of("openai_r9", newmoney.R23)
    for acc, cap in newmoney.CAPS_R25.items():
        assert newmoney.used(acc, newmoney.R25) >= 0
        assert raises(newmoney.check, acc, cap + 0.01, newmoney.R25, kinds=(SystemExit,))
    assert raises(newmoney.check, "anthropic_r9b", 0.01, newmoney.R25, kinds=(SystemExit,))
    print("  R25 money: the caps, the runs, the refusals; the older groups unchanged")


def test_projection():
    """confirm25.check_projection keeps the money of the later R10-23 rounds and of R10-24 free."""
    import steer3
    import harmless3
    saved = steer3.future, harmless3.pending_bounds, budget_gate.free
    try:
        budget_gate.free = lambda name, reserve=2.0: 3.00
        steer3.future = lambda m, data, g, after=None: 1.00  # Sol and Luna: 2.00 USD on openai_r9
        harmless3.pending_bounds = lambda acc: 0.50
        c25.check_projection("ern_sol", 0.50)  # 0.50 + 2.00 + 0.50 = 3.00: holds
        assert raises(c25.check_projection, "ern_sol", 0.51, kinds=(SystemExit,))
        c25.check_projection("ern_deepseek", 2.50)  # no R10-23 model on deepinfra_main: 2.50 + 0.50 = 3.00
        steer3.future = lambda m, data, g, after=None: None
        assert raises(c25.check_projection, "ern_luna", 0.01, kinds=(SystemExit,))
    finally:
        steer3.future, harmless3.pending_bounds, budget_gate.free = saved
    print("  projection: the R10-23 later rounds and the R10-24 runs keep their money")


def test_main_guards():
    """runs.main stops a V step above the step limit, above the cap, or above the projection, before the client."""
    import anth
    import openai_compat as oc
    saved = anth.main, oc.main, sys.argv, newmoney.used, c25.check_projection

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
        for name in ("ern_deepseek", "ern_sol", "ern_haiku"):
            step = "run" if name == "ern_deepseek" else "submit"
            sys.argv = ["x", step, "--approve", "1.51"]
            stop(name, "allows at most 1.50 USD per step")
            acc = runs.RUNS[name].account
            newmoney.used = lambda account, group=newmoney.R19: (newmoney.CAPS_R25[account] - 0.05
                                                                  if group == newmoney.R25 else 0.0)
            sys.argv = ["x", step, "--approve", "0.10"]
            stop(name, f"would pass the cap of {newmoney.CAPS_R25[acc]:.2f} USD")
            newmoney.used = saved[3]
            c25.check_projection = lambda n, b: sys.exit("Not run. projection")
            stop(name, "projection")
            c25.check_projection = saved[4]
    finally:
        anth.main, oc.main, sys.argv, newmoney.used, c25.check_projection = saved
    print("  main: the step limit, the cap and the projection stop before the client")


def test_pilot_check():
    assert pilot_check.cell_of("ern_sol-PMUL0001-verify-2") == "verify"
    row = {"custom_id": "ern_sol-PMUL0001-verify-2", "type": "succeeded", "stop": "end_turn", "text": '{"answer": "no"}'}
    assert pilot_check.parses(row, "verify") and not pilot_check.parses({**row, "text": '{"answer": "maybe"}'}, "verify")
    print("  pilot_check: a verify row")


if __name__ == "__main__":
    only = sys.argv[1:]
    for fname, fn in list(globals().items()):
        if fname.startswith("test_") and callable(fn) and (not only or fname in only):
            print(fname)
            fn()
    print("confirm25 tests passed")
