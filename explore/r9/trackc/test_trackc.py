"""Offline tests of builder B (r9/trackc). No API call, no key read, and no write into the explore folder.

1. The request count per model equals r9_counts.py --balance for P, X2 Track C, X2 on-site, and X5.
2. p_option differs from p_unclear only by the ambiguity sentence, in the form and in the built requests, and it keeps
   the p_unclear schema. Its Claude requests equal the E14 p_unclear requests except the system text.
3. Each request carries the panel settings (DeepInfra: deepinfra_settings.request); the X5 Opus requests equal the E3
   requests except the user turn.
4. No request holds a Track P, validation, or test dialogue, and the guard rejects one.
5. Samples are seeded and shared: P across models, X5 across annotators.
6. P rows give the pilot.json that the library estimate reads; a paid step stops without measured sizes; no pilot step.
   A DeepInfra row sizes a cell only as deepinfra_settings.projected gives it.
7. The P summary counts errors, cut-off answers, and valid JSON, and applies the Sol cut rule at batch prices.
8. The Track C wrapper scores synthetic rows of every form, joins the E14 rows for Claude, and checks Q3 and Q4.
9. The X5 analysis counts disagreement, construction agreement, and repeat changes on synthetic replies.
10. P2 reads the P units with the P prompts and schemas: 60 calls each for DeepSeek and Qwen, and 20 natural calls for
    each alternative option.
Usage: python3 -I r9/trackc/test_trackc.py
"""
import collections
import contextlib
import difflib
import io
import json
import pathlib
import runpy
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ep  # noqa: E402
import ep_di2  # noqa: E402
import ep_summary  # noqa: E402
import ex2c_analyze  # noqa: E402
import ex5_analyze  # noqa: E402
import panel  # noqa: E402
import tasks  # noqa: E402
import x2c  # noqa: E402
import x2s  # noqa: E402
import x5  # noqa: E402
from panel import anth, ds, oc  # noqa: E402

DATA = panel.multiwoz()
COUNTS = panel.EXPLORE.parents[1] / "review" / "plan13" / "r9_counts.py"
TP = tasks.templates


def by_id(reqs):
    return {r["custom_id"]: r for r in reqs}


def model_counts(reqs):
    return collections.Counter((r["body"] if "body" in r else r["params"])["model"].split("/")[-1] for r in reqs)


def test_counts():
    saved, sys.argv = sys.argv, [str(COUNTS), "--balance"]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            g = runpy.run_path(str(COUNTS))
    finally:
        sys.argv = saved
    n, mine = g["n"], collections.Counter()
    for provider in ("openai", "deepinfra"):
        mine += model_counts(ep.build(provider)) + model_counts(x2c.build(provider)) + model_counts(x2s.build(provider))
    mine += model_counts(x2c.build("anthropic"))
    natural = {g["SOL"]: g["S1"] * 3 + g["SPEC"] * 3, g["LUNA"]: (g["S1"] + g["REST"]) * 3 * 3,
               **{m: g["S1"] * 2 for m in g["DI"]}}  # the natural part of X2 is builder A's (ex2n)
    plan = {m: n[m]["X2"] - natural.get(m, 0) for m in n if n[m]["X2"]}
    assert dict(mine) == plan, (dict(mine), plan)
    x5_counts = model_counts(x5.build("anthropic")) + model_counts(x5.build("openai"))
    assert dict(x5_counts) == {m: n[m]["X5"] for m in n if n[m]["X5"]}, x5_counts
    print(f"1. counts equal r9_counts.py --balance: X2 (builder B part) {dict(mine)}, X5 {dict(x5_counts)}")


def test_p_option():
    unclear, option = TP.FORMS["p_unclear"], tasks.TRACKC_FORMS["p_option"]
    ops = [(tag, unclear[i1:i2], option[j1:j2])
           for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, unclear, option, autojunk=False).get_opcodes()
           if tag != "equal"]
    assert len(ops) == 1 and ops[0][0] == "delete" and ops[0][1].strip() == TP.AMBIGUITY.strip(), ops
    assert option == TP.FORMS["p_main"], "p_option and p_main must differ only by the schema"
    s_opt, s_unc, s_main = (tasks.trackc_schema(f)["schema"] for f in ("p_option", "p_unclear", "p_main"))
    assert s_opt == s_unc
    for field in TP.ALLOWED:
        assert s_opt["properties"][field]["anyOf"][1]["enum"] == ["any", "unclear"]
        assert s_main["properties"][field]["anyOf"][1]["enum"] == ["any"]
    assert json.dumps(s_opt).replace('["any", "unclear"]', '["any"]') == json.dumps(s_main)

    for provider, short, system in (("openai", "sol", lambda b: b["input"][0]),
                                    ("deepinfra", "qwen", lambda b: b["messages"][0])):
        reqs = by_id(x2c.build(provider))
        a, b = (reqs[f"ex2c-xb-g03-amb-{f}-r1-{short}"]["body"] for f in ("p_option", "p_unclear"))
        assert system(a)["content"] == option and system(b)["content"] == unclear
        system(a)["content"] = unclear
        a.pop("seed", None), b.pop("seed", None)
        assert a == b, f"{provider}: p_option and p_unclear requests differ outside the system text"
    e14 = {r["custom_id"]: r for r in map(json.loads, open(panel.EXPLORE / "e14" / "requests.jsonl"))}
    mine = by_id(x2c.build("anthropic"))
    for short in ("haiku", "sonnet"):
        a = mine[f"ex2c-xb-g03-amb-p_option-r1-{short}"]["params"]
        b = e14[f"e14-xb-g03-amb-p_unclear-r1-{short}"]["params"]
        assert a["system"] == option and b["system"] == unclear
        assert {**a, "system": unclear} == b, f"{short}: p_option request differs from E14 outside the system text"
    reply = {"name": None, "area": None, "pricerange": None, "stars": None, "type": "unclear", "parking": None,
             "internet": None}
    item = next(i for i in TP.items() if i.id == "xa-g00-amb")
    parsed = ex2c_analyze.TC.parse(json.dumps(reply))
    assert parsed["type"] == "unclear" and not ex2c_analyze.TC.score(item, parsed)["commit"]
    print("2. p_option = p_unclear without the ambiguity sentence = p_main text with the p_unclear schema; "
          "requests differ only in the system text; E14 settings kept; 'unclear' parses and does not commit")


def test_settings():
    effort = {"sol": "low", "luna": "none", "astra": "low"}
    for cid, r in by_id(ep.build("openai")).items():
        b, task, short = r["body"], cid.split("-")[1], cid.split("-")[2]
        assert not {"temperature", "top_p", "seed"} & set(b), cid
        assert ("reasoning" not in b) if short == "soldef" else b["reasoning"] == {"effort": effort[short]}, cid
        assert b["max_output_tokens"] == (16000 if task == "an" else 4000), cid
        assert (b["text"]["format"]["strict"] is True) if task in ("nat", "tc") else "text" not in b, cid
    reqs = by_id(ep.build("deepinfra"))
    for cid, task, m, p in ep.cells("deepinfra"):
        b = reqs[cid]["body"]
        assert b == ds.request(ds.MODELS[m.id], cid, p.user, p.system, p.schema)["body"], cid
        assert (b["response_format"]["json_schema"]["strict"] is True) if task in ("nat", "tc") else "response_format" not in b
    seeds = collections.defaultdict(set)
    for cid, r in by_id(x2s.build("deepinfra")).items():
        short, arm, _, case = cid.split("_", 3)
        seeds[(short, arm, case)].add(r["body"]["seed"])
    assert all(len(s) == 5 for s in seeds.values()), "the 5 reads of one unit need 5 seeds"
    e3 = json.loads((panel.EXPLORE / "e3" / "requests.jsonl").open().readline())["params"]
    for r in x5.build("anthropic"):
        assert {**r["params"], "messages": e3["messages"]} == e3, r["custom_id"]
    for r in x5.build("openai"):
        b = r["body"]
        assert b["input"][0]["content"] == e3["system"] and b["reasoning"] == {"effort": "low"}
        assert b["max_output_tokens"] == 16000 and "text" not in b
    for r in x2s.build("openai"):
        assert r["body"]["max_output_tokens"] == 4000 and "text" not in r["body"]
    print("3. panel settings on every request; DeepInfra seeds differ per read; X5 Opus = E3 settings and prompt")


def test_guard():
    val, test = anth.splits()
    forbidden = val | test | anth.trackp_pool(DATA)
    used = set(ep.units()[1]) | set(x5.units()[2])
    assert used and not used & forbidden
    try:
        panel.guard([sorted(val)[0]])
    except AssertionError:
        pass
    else:
        raise AssertionError("the guard accepted a validation dialogue")
    print(f"4. {len(used)} MultiWOZ dialogues in P and X5, none in Track P, validation, or test; the guard rejects one")


def test_samples():
    a, b = ep.units()[0], ep.units()[0]
    assert {t: [p.key for p in v] for t, v in a.items()} == {t: [p.key for p in v] for t, v in b.items()}
    for provider in ("openai", "deepinfra"):
        keys = collections.defaultdict(set)
        for cid, task, m, p in ep.cells(provider):
            keys[task].add((m.short, p.key))
        for task, pairs in keys.items():
            per_model = collections.defaultdict(set)
            for short, key in pairs:
                per_model[short].add(key)
            assert len({frozenset(v) for v in per_model.values()}) == 1, f"P {task}: models read different units"
    opus = [(k, r) for _, k, r, _ in x5.cells("anthropic")]
    assert opus == [(k, r) for _, k, r, _ in x5.cells("openai")], "the X5 annotators read different units"
    first = {k for k, r in opus if r == 1}
    assert {k for k, r in opus if r == 2} <= first and len(first) == 120
    items = [i for i in TP.items() if i.id in first]
    assert collections.Counter((i.condition, i.kind) for i in items) == {(c, k): 10 for c in "abcd" for k in ("ambiguous", "clear")}
    assert all(sum(i.goal.id == g for i in items) == 2 for g in {i.goal.id for i in items})
    print("5. seeded samples repeat; P units shared across models; X5 units shared; 10 goals per condition, both items")


def p_rows(provider, task, output, scale=3):
    rows = {}
    for cid, t, m, p in ep.cells(provider):
        if t == task:
            est = oc.est_in(panel.request(m, cid, p))
            rows[cid] = {"custom_id": cid, "type": "succeeded", "model": m.id, "stop": "end_turn",
                         "input_tokens": int(scale * est), "output_tokens": output, "reasoning_tokens": 7, "text": "{}"}
    return rows


def test_sizes():
    got = {**p_rows("openai", "tc", 100), **p_rows("openai", "nat", 999)}
    saved_rows, saved_explore = panel.rows, anth.EXPLORE
    with tempfile.TemporaryDirectory() as tmp:
        panel.rows = lambda name, file="raw.jsonl": got if name == "ep_oa" else {}
        anth.EXPLORE = pathlib.Path(tmp)
        try:
            measured = ep.sizes("ex2c_oa", "tc")
            sizes = json.loads((pathlib.Path(tmp) / "ex2c_oa" / "pilot.json").read_text())
            reqs = x2c.build("openai")
            total, cells = oc.estimate("ex2c_oa", reqs, 550, oc.APIS["openai"])
        finally:
            panel.rows, anth.EXPLORE = saved_rows, saved_explore
    assert measured == {"gpt-6.1-sol|low", "gpt-6.1-sol|default", "gpt-6-luna|none"}, measured
    sol = [r for cid, r in got.items() if cid.startswith("ep-tc-sol-")]
    est = [oc.est_in(panel.request(panel.MODELS["sol"], cid, p)) for cid, t, m, p in ep.cells("openai")
           if t == "tc" and m.short == "sol"]
    assert abs(sizes["gpt-6.1-sol|low"]["in_ratio"] - sum(r["input_tokens"] for r in sol) / sum(est)) < 1e-12
    assert sizes["gpt-6.1-sol|low"]["out_mean"] == 100, "the natural rows must not enter the Track C sizes"
    expect = sum(oc.cost(oc.APIS["openai"], r["body"]["model"],
                         oc.est_in(r) * sizes["|".join(oc.cell(r))]["in_ratio"], 100, True) for r in reqs)
    assert abs(total - expect) < 1e-9 and all(src == "pilot" for _, _, src in cells.values())

    calls, saved_main, saved_argv = [], oc.main, sys.argv
    oc.main = lambda *a, **k: calls.append(a)
    try:
        for argv, sized, stops in ((["x", "submit", "--approve", "1.00"], set(), True),
                                   (["x", "pilot", "--approve", "1.00"], measured, True),
                                   (["x", "submit", "--approve", "1.00"], measured, False)):
            sys.argv = argv
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    panel.main("ex2c_oa", lambda: reqs, 550, account="openai_r9", sizes=lambda: sized)
                stopped = False
            except SystemExit:
                stopped = True
            assert stopped == stops, (argv, sized)
    finally:
        oc.main, sys.argv = saved_main, saved_argv
    assert len(calls) == 1, "only the measured submit may reach the provider client"
    print("6. P rows -> pilot.json -> library estimate; paid steps stop without measured sizes; no pilot step")


def test_deepinfra_sizes():
    got = p_rows("deepinfra", "tc", 80)
    for cid in got:
        got[cid]["reasoning_tokens"] = 700 if "-dsv4-" in cid else 0
    cut = sorted(cid for cid in got if "-qwen-" in cid)[0]
    got[cut] |= {"stop": "max_tokens", "output_tokens": 4000}
    saved_rows, saved_explore = panel.rows, anth.EXPLORE
    with tempfile.TemporaryDirectory() as tmp:
        panel.rows = lambda name, file="raw.jsonl": got if name == "ep_di" else {}
        anth.EXPLORE = pathlib.Path(tmp)
        try:
            measured = ep.sizes("ex2c_di", "tc")
            sizes = json.loads((pathlib.Path(tmp) / "ex2c_di" / "pilot.json").read_text())
        finally:
            panel.rows, anth.EXPLORE = saved_rows, saved_explore
    assert measured == {"Qwen/Qwen3.8-27B|none", "google/gemma-4-31B-it|default"}, measured
    qwen = sizes["Qwen/Qwen3.8-27B|none"]
    assert (qwen["n"], qwen["out_max"], qwen["out_mean"]) == (20, ds.MAX_TOKENS, (19 * 80 + ds.MAX_TOKENS) / 20), qwen
    print("6b. a DeepInfra row with reasoning tokens sizes no thinking-off cell; a cut-off answer counts at the new cap")


def test_p_summary():
    cells = ep.cells("openai")
    reply = json.dumps({f: None for f in ("name",) + tuple(tasks.common.FIELDS)})
    got = p_rows("openai", "nat", 556)
    sol = sorted(cid for cid in got if cid.startswith("ep-nat-sol-"))
    for cid in got:
        got[cid] |= {"input_tokens": 1846, "text": reply}
    got[sol[0]] = {"custom_id": sol[0], "type": "errored", "status": 500}
    got[sol[1]] |= {"stop": "max_tokens", "text": reply[:20]}
    got[sol[2]] |= {"text": "no JSON here"}
    c = ep_summary.summarize("openai", cells, got)["sol|nat"]
    assert (c["requests"], c["answers"], c["errors"], c["cut_off"], c["valid_json"]) == (20, 19, 1, 1, 17), c
    assert abs(c["usd_per_call_batch"] - (1846 * 1.0 + 556 * 5.0) / 1e6) < 1e-12
    assert ep_summary.cut_rule({"sol|nat": c})["cut"] is False
    for cid in sol[3:]:
        got[cid]["output_tokens"] = 2056
    assert ep_summary.cut_rule(ep_summary.summarize("openai", cells, got))["cut"] is True
    assert ep_summary.cut_rule({})["cut"] is None
    print("7. P summary: 19 answers, 1 error, 1 cut off, 17 valid JSON; cut rule NO at 556 output tokens, YES at 2,056")


QUIET = {"Qwen/Qwen3.8-27B", "google/gemma-4-31B-it"}  # p_null always null, so their option effect is 0


def target(item, form, model, sonnet_unclear_commits=False):
    g = int(item.goal.id[-2:])
    narrow = (item.goal.clear[1],) if item.condition == "c" else item.goal.clear
    if item.kind == "clear":
        return "unclear" if form == "p_option" and g < 4 else item.goal.clear
    if item.condition == "d":
        return None
    if form == "p_unclear":
        return narrow if sonnet_unclear_commits and model == ex2c_analyze.SONNET else "unclear"
    return {"p_main": narrow, "p_null": None if g < 20 or model in QUIET else narrow,
            "p_option": "unclear" if g < 30 else narrow}[form]


def track_c_rows(cells, **kw):
    rows = []
    for cid, item, form, _, model in cells:
        obj = {f: (list(v) if isinstance(v, tuple) else v) for f, v in item.interpretations[0].items()}
        t = target(item, form, model, **kw)
        obj[item.target] = list(t) if isinstance(t, tuple) else t
        rows.append({"custom_id": cid, "type": "succeeded", "model": model, "stop": "end_turn",
                     "input_tokens": 1500, "output_tokens": 50, "text": json.dumps(obj)})
    return rows


def test_track_c_wrapper():
    ex2c_analyze.TC.BOOT = 50  # the test checks point values; fewer bootstrap draws keep it fast
    effects = []
    for provider in ("openai", "deepinfra", "anthropic"):
        cells = ex2c_analyze.run_cells(provider)
        rows = track_c_rows(cells)
        if provider == "deepinfra":
            d = [r for r, (cid, item, form, _, model) in zip(rows, cells)
                 if model == "google/gemma-4-31B-it" and form == "p_main" and item.condition == "d" and item.kind == "ambiguous"]
            d[0] |= {"type": "errored", "text": None}
            d[1] |= {"stop": "max_tokens"}
        s = ex2c_analyze.summarize(rows, cells)
        assert s["requests"] == len(cells) and s["absent"] == 0 and s["unknown_rows"] == 0
        effects += ex2c_analyze.effects(s)
        model = {"openai": "gpt-6.1-sol", "deepinfra": "google/gemma-4-31B-it", "anthropic": ex2c_analyze.SONNET}[provider]
        a = s["cells"]["a"]
        assert [a[f][model]["commitment"]["rate"] for f in x2c.FORMS] == [1.0, 0.0 if model in QUIET else 0.5, 0.0, 0.25]
        assert a["p_option"][model]["retention"]["rate"] == 36 / 40 and a["p_main"][model]["retention"]["rate"] == 1.0
        x = s["exchange_rate"]["a"][model]["p_option"]
        assert abs(x["commit_drop"] - 0.75) < 1e-12 and abs(x["retention_drop"] - 0.1) < 1e-12
        if provider == "deepinfra":
            gd = s["cells"]["d"]["p_main"][model]
            assert (gd["error"], gd["truncated"], gd["commitment"]["valid"]) == (1, 1, 38), gd
    v = ex2c_analyze.verdict(effects)
    assert v == {"q3_option_small_cells": "6 of 15", "q3_option_small_in_most": False, "q3_d_zero": True,
                 "q4_sonnet_b_option_at_least_unclear": True}, v
    sol_a = next(r for r in effects if r["model"] == "gpt-6.1-sol" and r["condition"] == "a")
    assert (sol_a["option_effect_pp"], sol_a["schema_option_pp"], sol_a["sentence_pp"]) == (50.0, 75.0, 25.0), sol_a
    cells = ex2c_analyze.run_cells("anthropic")
    s = ex2c_analyze.summarize(track_c_rows(cells, sonnet_unclear_commits=True), cells)
    assert ex2c_analyze.verdict(ex2c_analyze.effects(s))["q4_sonnet_b_option_at_least_unclear"] is False
    print("8. Track C wrapper: rates, exchange with p_option, missing kinds, E14 join, Q3 '6 of 15', Q4 both ways")


def test_x5_analysis():
    reader = ex5_analyze.ANNOT.Reader(tasks.e3.load_p5().p4)
    first, repeats, _ = x5.units()
    repeated = {p.key for p in repeats}
    items = ex5_analyze.ITEMS

    def reply(key, who, read):
        fields = {f: {"class": "clear", "subtag": None, "readings": [None], "note": None} for f in tasks.e3.FIELDS}
        item = items.get(key)
        if item:
            readings = [list(r) if isinstance(r, tuple) else r for r in (i[item.target] for i in item.interpretations)]
            split = who == "astra" and int(item.goal.id[-2:]) % 2 == 0
            if len(readings) > 1 and not split:
                fields[item.target] = {"class": "ambiguous", "subtag": "relaxation", "readings": readings}
            else:
                fields[item.target] = {"class": "clear", "subtag": None, "readings": [readings[-1]]}
        elif read == 2 and who == "opus":
            fields["area"] = {"class": "ambiguous", "subtag": "vague_word", "readings": [None, ["north"]]}
        return {"type": "succeeded", "stop": "end_turn",
                "text": json.dumps({"name_request": False, "fields": fields, "links": []})}

    codes = {who: {(p.key, read): reader.code(reply(p.key, who, read))
                   for read, group in ((1, first), (2, repeats)) for p in group} for who in ("opus", "astra")}
    s = ex5_analyze.summarize(codes, [p.key for p in first])
    amb = [k for k in items if k in {p.key for p in first} and len(items[k].interpretations) > 1]
    split = sum(int(items[k].goal.id[-2:]) % 2 == 0 for k in amb)
    assert s["disagreement"]["ambiguous_target"] == {"fields": len(amb), "disagree": split, "rate": split / len(amb)}
    assert s["disagreement"]["clear_target"]["disagree"] == 0 and s["disagreement"]["dialogue_all_fields"]["rate"] == 0
    assert s["construction"]["opus"]["disagree"] == 0 and s["construction"]["astra"]["disagree"] == split
    dialogues = sum(k not in items for k in repeated)
    assert s["repeat_change"]["opus"] == {"fields": 7 * 20, "disagree": dialogues, "rate": dialogues / 140}
    assert s["repeat_change"]["astra"]["disagree"] == 0 and s["missing"] == {"opus": 0, "astra": 0}
    assert s["prediction_more_disagreement_on_ambiguous"] is True
    print(f"9. X5 analysis: {split} of {len(amb)} ambiguous targets split, construction and repeat counts exact")


def test_p2():
    reqs = ep_di2.build()
    assert len({r["custom_id"] for r in reqs}) == len(reqs) == 160
    p = by_id(ep.build("deepinfra"))
    tags = collections.Counter()
    for r in reqs:
        _, task, tag, unit = r["custom_id"].split("-", 3)
        tags[tag, task] += 1
        b, old = r["body"], p[f"ep-{task}-{tag.removesuffix('alt')}-{unit}"]["body"]
        assert (b["model"], b["messages"], b.get("response_format")) == (old["model"], old["messages"],
                                                                        old.get("response_format")), r["custom_id"]
        assert {k: b[k] for k in b.keys() - old.keys()} == ({} if tag in ("dsv4", "qwen") else
                                                            ds.ALTERNATIVES[b["model"]].options), r["custom_id"]
        assert b["max_tokens"] == ds.MAX_TOKENS and ("reasoning_effort" in b) == (tag in ("dsv4", "qwen"))
    assert tags == {**{(t, task): 20 for t in ("dsv4", "qwen") for task in ("nat", "tc", "os")},
                    ("dsv4alt", "nat"): 20, ("qwenalt", "nat"): 20}, tags
    print("10. P2: 160 requests on the P units with the P prompts and schemas; each alternative only changes the option")


if __name__ == "__main__":
    for test in (test_counts, test_p_option, test_settings, test_guard, test_samples, test_sizes, test_deepinfra_sizes,
                 test_p_summary, test_track_c_wrapper, test_x5_analysis, test_p2):
        test()
    print("test_trackc.py: PASS")
