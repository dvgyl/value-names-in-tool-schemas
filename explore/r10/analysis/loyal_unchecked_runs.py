"""Full-schema sensitivity of the tool-call runs that the first check (r10/analysis/tool_validity.py) did not cover.
Post hoc; no model call; stored rows only. Paper: Appendix B ("Scorable and valid tool calls").

The checker is tool_validity.problems (imported, not edited). A search call is *not valid* when its arguments, after
the normalization that the run itself declared, do not fit the input schema of the call's own condition:
- every run: tools.clean_nulls (the text "null" is read as null; amendment R10-3);
- the search-again run (R10-23) also declared steer3.unquote (a value in extra quotation marks is read without them),
  so its check applies unquote first, as its parser does.
Rule of the sensitivity (fixed here, before any output of this script):
- one-call answers (first and second service runs, release-test pairs, label test): an answer whose search call is not
  valid is missing (as tool_validity.py does); the frozen analysis functions then run unchanged on the remaining reads;
- conversations (search-again run, later turns): a conversation with any search call that is not valid is missing,
  because the agent saw the result of that call; the frozen analysis functions then run on the other conversations.
Runs and frozen analyses (imported, not edited; none of their output files is written):
- first service run: r10/analysis/steer_search.py (rate, change, failure_tests) on steer_analyze.load;
- second service run: r10/analysis/steer2_analyze.py (load, analyse);
- release test on the nine rewrites and the 29 stored pairs: workshops/proposals-verified/verify.py (item1);
- search-again run: workshops/steer-search/analyze.py (outcome, analyse_model, panel, predictions) on steer3.replay;
- later turns: r10/analysis/turns_analyze.py (analyse) on ert_sonnet and ert1_sonnet conversations.jsonl;
- label-test tool calls: workshops/label-test/analyze3.py (load, analyse, predictions).
Each part also recomputes the primary result without the change and asserts that it equals the stored output.
Usage (from explore/): python3 -I r10/analysis/loyal_unchecked_runs.py
Outputs: r10/analysis/out/loyal_unchecked_runs.json and loyal_unchecked_runs.md.
This file is a copy of the project script unchecked_runs.py with the paths of the study folder and the names of its output files changed; the code is otherwise the same. It reads project files outside the study folder (the independent check of the release test and its stored output; the project analyses of the search-again run and of the label-test tool calls), so it cannot run in the supplementary package. The stored outputs are the outputs of the project script.
"""
import collections
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
ROOT = EXPLORE.parents[1]  # the project folder (outside the study folder)
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import tool_validity as tv  # noqa: E402  (the checker; its main() does not run)

import control  # noqa: E402
import gold  # noqa: E402
import labeltest3 as l3  # noqa: E402
import release  # noqa: E402
import release_analyze as ra  # noqa: E402
import runs  # noqa: E402
import steer  # noqa: E402
import steer2  # noqa: E402
import steer3  # noqa: E402
import steer2_analyze as S2  # noqa: E402
import steer_analyze as SA  # noqa: E402
import steer_search as SS  # noqa: E402
import tools  # noqa: E402
import turns_analyze as TA  # noqa: E402

OUT = HERE / "out"
STORE = EXPLORE / "r10" / "analysis" / "out"


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


T0, T1 = tools.SEARCH_T0["input_schema"], tools.SEARCH_T1["input_schema"]
STEER_CELL = {steer.CELL[d]: d for d in steer.directions()}


def schema_of(cell):
    if cell in ("t0", "trep"):
        return T0
    if cell == "t1":
        return T1
    if cell == "tedit":
        return release.edit()["obj"]["tool"]["input_schema"]
    if cell == "tord":
        return control.ordered_tool()["input_schema"]
    if cell in STEER_CELL:
        return steer.edit(STEER_CELL[cell])["obj"]["tool"]["input_schema"]
    if cell in steer2.CELLS:
        return steer2.edit(cell)["obj"]["tool"]["input_schema"]
    if cell in l3.CELLS:
        return l3.tool(cell)["input_schema"]
    raise KeyError(cell)


def row_bad(row, schema, unquote=False):
    """True when the row holds one search_hotels call whose normalized arguments do not fit the schema."""
    calls = row.get("tool_calls") or []
    if len(calls) != 1 or calls[0].get("name") != "search_hotels" or not isinstance(calls[0].get("input"), dict):
        return False
    args = calls[0]["input"]
    if unquote:
        args = {k: steer3.unquote(x) for k, x in args.items()}
    return bool(tv.problems(tools.clean_nulls(args), schema))


def close(a, b, tol=1e-9):
    if isinstance(a, dict):
        return all(close(a[k], b[k], tol) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and abs(a - b) <= tol
    return a == b


COUNTS = collections.Counter()


# ---------------------------------------------------------------- one-call runs (first and second service runs)
def patched_read_of(orig, counter_key):
    def read_of(row, cell):
        kind, val = orig(row, cell)
        if kind == "search" and row_bad(row, schema_of(cell)):
            COUNTS[(counter_key, cell)] += 1
            return "invalid", "full schema"
        return kind, val
    return read_of


def first_service(data, sets):
    db = gold.hotel_db()
    tests = SS.failure_tests(data, db)
    stored = json.loads((STORE / "steer_search.json").read_text())["agents"]
    out = {}
    orig = SA.read_of
    for variant in ("primary", "sensitivity"):
        SA.read_of = orig if variant == "primary" else patched_read_of(orig, "first service run")
        res = {}
        for agent in SA.SOURCES:
            reads, _, missing = SA.load(agent, False)
            assert not missing
            a = {"rates": {}, "changes": {}}
            for (s, kind), test in tests.items():
                if s != "open":
                    continue
                key = f"{s} | {kind}"
                a["rates"][key] = {c: SS.rate(reads, sets[s], c, test) for c in SA.CELLS}
                a["changes"][key] = {c: SS.change(reads, sets[s], c, test) for c in ("th", "tg")}
            res[agent] = a
        out[variant] = res
    SA.read_of = orig
    for agent, a in out["primary"].items():
        for key in a["rates"]:
            assert close(a["rates"][key], stored[agent]["rates"][key]), (agent, key)
            assert close(a["changes"][key], stored[agent]["changes"][key]), (agent, key)
    return out


def second_service(data, sets):
    db = gold.hotel_db()
    tests = S2.outcomes(data, db)
    cells = steer2.cells()
    stored = json.loads((STORE / "steer2.json").read_text())["result"]
    out = {}
    orig = S2.read_of
    for variant in ("primary", "sensitivity"):
        S2.read_of = orig if variant == "primary" else patched_read_of(orig, "second service run")
        reads, _ = S2.load(False)
        out[variant] = S2.analyse(reads, sets, {k: v for k, v in tests.items() if k.startswith("open")}, cells)
    S2.read_of = orig
    p = out["primary"]
    for part in ("rates", "per_rewrite", "pooled_vs_t0", "pooled_diff"):
        for key in p[part]:
            assert close(p[part][key], stored[part][key]), (part, key)
    return out


# ---------------------------------------------------------------- release test: the nine rewrites and the 29 pairs
def release_pairs(sets):
    V = load_mod("lv_verify", ROOT / "workshops" / "proposals-verified" / "verify.py")
    orig = V.score_tool

    def score_tool(row, cell):
        s = orig(row, cell)
        if s is not None and row_bad(row, schema_of(cell)):
            COUNTS[("release test", cell)] += 1
            return None
        return s
    V.score_tool = score_tool
    # item1 also estimates sample sizes from the per-prefix rates; that part is no reported value of the paper and
    # needs a read for every prefix, which the sensitivity can remove. It is left out here (verify.py unchanged).
    V.sample_size = lambda sets: None
    res = V.item1(sets)
    V.score_tool = orig
    stored = json.loads((ROOT / "workshops" / "proposals-verified" / "verify_out.json").read_text())["item1"]
    pairs = []
    for e_new, e_old in zip(res["aa"]["one_answer"], stored["aa"]["one_answer"]):
        assert (e_new["model"], e_new["a"], e_new["b"]) == (e_old["model"], e_old["a"], e_old["b"])
        pairs.append({"model": e_new["model"], "a": e_new["a"], "b": e_new["b"],
                      "first rule": [e_old["decision"], e_new["decision"]],
                      "revised rule": [e_old["exact_0.0125"], e_new["exact_0.0125"]],
                      "specific": [[e_old["specific"][k] for k in ("change", "low", "high")],
                                   [e_new["specific"][k] for k in ("change", "low", "high")]]})
    edits = {}
    for name in [f"rewrite {g}{i}, haiku" for g in "hgn" for i in (1, 2, 3)] + ["repeat (10 answers), haiku",
                                                                                "field order (10 answers), haiku"]:
        o, n = stored["edits"][name]["0.9875"], res["edits"][name]["0.9875"]
        edits[name] = {"first rule": [o["bootstrap"], n["bootstrap"]], "revised rule": [o["exact_0.0125"], n["exact_0.0125"]],
                       "open": [[o["open"][k] for k in ("change", "low", "high")], [n["open"][k] for k in ("change", "low", "high")]],
                       "specific": [[o["specific"][k] for k in ("change", "low", "high")],
                                    [n["specific"][k] for k in ("change", "low", "high")]]}
    return {"tally_one_answer": [stored["tally"]["one_answer"], res["tally"]["one_answer"]], "pairs": pairs,
            "edits": edits}


# ---------------------------------------------------------------- search-again run (R10-23)
def search_again(data, g):
    A = load_mod("ss_analyze", ROOT / "workshops" / "steer-search" / "analyze.py")
    db = gold.hotel_db()
    sets = control.set_of(data, g)
    tests = A.failure_tests(data, db)
    stored = json.loads((ROOT / "workshops" / "steer-search" / "out" / "result.json").read_text())
    out = {"primary": {}, "sensitivity": {}, "dropped": {}, "quote_rule_fixes": {}}
    outs_v = {"primary": {}, "sensitivity": {}}
    for m in steer3.MODELS:
        convs = steer3.replay(m, steer3.MAX_CALLS, data, g, "raw", steer3.keys(m, data, g), db, strict=False)
        drop, fixes = collections.Counter(), collections.Counter()
        kept = []
        for c in convs:
            sch = T0 if c.cell == steer3.CONTROL else schema_of(c.cell)
            bad = any(row_bad(r, sch, unquote=True) for r in c.rows)
            fixes[c.cell] += sum(row_bad(r, sch) and not row_bad(r, sch, unquote=True) for r in c.rows)
            if bad and c.status in A.VALID:
                drop[c.cell] += 1
            if not bad:
                kept.append(c)
        out["dropped"][m], out["quote_rule_fixes"][m] = dict(drop), dict(fixes)
        for variant, cs in (("primary", convs), ("sensitivity", kept)):
            outs = [o for c in cs if (o := A.outcome(c, sets[c.d], tests)) is not None]
            status = collections.Counter("unfinished" if c.status == "open" else c.status for c in cs)
            outs_v[variant][m] = outs
            out[variant][m] = A.analyse_model(outs, status)
    for variant in ("primary", "sensitivity"):
        out[f"{variant}_panel"] = A.panel(outs_v[variant])
        out[f"{variant}_predictions"] = A.predictions(out[variant])
    for m in steer3.MODELS:
        for key, e in out["primary"][m]["sets"].items():
            assert close(e["first_change"], stored["models"][m]["sets"][key]["first_change"]), (m, key)
            assert close(e["last_change"], stored["models"][m]["sets"][key]["last_change"]), (m, key)
        assert out["primary"][m]["behaviour"]["h1"]["searched_again"] == stored["models"][m]["behaviour"]["h1"]["searched_again"]
    assert close(out["primary_panel"], stored["panel"])
    return out


# ---------------------------------------------------------------- later turns (R10-8)
def later_turns(data):
    db = gold.hotel_db()
    stored = json.loads((STORE / "turns.json").read_text())["arms"]
    out = {"primary": {}, "sensitivity": {}, "dropped": {}}
    for arm, name in TA.RUNS.items():
        recs = [json.loads(x) for x in (EXPLORE / name / "conversations.jsonl").read_text().splitlines()]
        sch = T0 if arm == "t0" else T1
        kept = [r for r in recs if not any(row_bad(c, sch) for c in r["calls"])]
        out["dropped"][arm] = {"complete conversations": sum(r["status"] == "complete" for r in recs)
                               - sum(r["status"] == "complete" for r in kept)}
        for variant, rs in (("primary", recs), ("sensitivity", kept)):
            res = TA.analyse(rs, data, db)
            res.pop("_rows", None)
            out[variant][arm] = res
        for key in ("F", "R", "F_initial_failure", "F_no_initial_failure", "never_fit_failure_minus_no_failure"):
            assert close(out["primary"][arm][key], stored[arm][key]), (arm, key)
    return out


# ---------------------------------------------------------------- label-test tool calls (R10-21)
def label_test(data, g):
    LT = load_mod("lt_analyze3", ROOT / "workshops" / "label-test" / "analyze3.py")
    db = gold.hotel_db()
    ids = LT.set_ids(data, g)
    bad = collections.Counter()
    for m, f in LT.FOLDERS.items():
        for row in LT.a18.rows_of(f, False):
            cell = row["custom_id"].split("-")[2]
            bad[(m, cell)] += row_bad(row, schema_of(cell))
    out = {"not_valid_calls": {f"{m} {c}": n for (m, c), n in sorted(bad.items())}}
    stored = json.loads((ROOT / "workshops" / "label-test" / "out" / "result3.json").read_text())
    orig = LT.read_of

    def read_of(row, parse):
        d, cell, kind, val = orig(row, parse)
        if kind == "search" and row_bad(row, schema_of(cell)):
            return d, cell, "invalid", "full schema"
        return d, cell, kind, val
    for variant in ("primary", "sensitivity"):
        LT.read_of = orig if variant == "primary" else read_of
        reads, _, missing = LT.load(False, data, db)
        assert not missing
        res = LT.analyse(reads, ids)
        out[variant] = {"results": {o: res[o] for o in ("hotel", "search_failure")}, "predictions": LT.predictions(res)}
    LT.read_of = orig
    for o in ("hotel", "search_failure"):
        for c in out["primary"]["results"][o]:
            for s in out["primary"]["results"][o][c]:
                assert close(out["primary"]["results"][o][c][s]["panel"], stored["results"][o][c][s]["panel"]), (o, c, s)
    return out


# ---------------------------------------------------------------- comparison at the paper's rounding
def pt(x):
    return round(x, 1)


def compare_rows(R):
    """(run, quantity, stored value, sensitivity value) for every value that the paper reports from these runs."""
    rows = []

    def add(run, what, a, b, unit="points"):
        rows.append({"run": run, "quantity": what, "reported": a, "sensitivity": b, "unit": unit})
    fs = R["first service run"]
    for agent in ("sonnet", "haiku"):
        for key, lab in (("open | hotel-only failure", "hotel only"), ("open | guesthouse-only failure", "guesthouse only"),
                         ("open | any failure", "either")):
            for c, nm in (("t0", "original"), ("th", "H1"), ("tg", "G1")):
                add("first service run (Table E3)", f"{agent} {lab} rate {nm}",
                    100 * fs["primary"][agent]["rates"][key][c]["share"], 100 * fs["sensitivity"][agent]["rates"][key][c]["share"], "%")
            for c, nm in (("th", "H1"), ("tg", "G1")):
                p, s = fs["primary"][agent]["changes"][key][c], fs["sensitivity"][agent]["changes"][key][c]
                add("first service run (Table E3)", f"{agent} {lab} change {nm}", p["mean"], s["mean"])
                add("first service run (Table E3)", f"{agent} {lab} change {nm} low", p["ci"][0], s["ci"][0])
                add("first service run (Table E3)", f"{agent} {lab} change {nm} high", p["ci"][1], s["ci"][1])
    ss = R["second service run"]
    for key, lab in (("open | hotel value", "hotel filter"), ("open | guesthouse value", "guesthouse filter"),
                     ("open | any failure", "exclusion (either)")):
        for c in ["t0"] + steer2.cells():
            add("second service run (Table E1, Figure 2)", f"{lab} rate {c}", 100 * ss["primary"]["rates"][key][c]["share"],
                100 * ss["sensitivity"]["rates"][key][c]["share"], "%")
        for c in steer2.cells():
            p, s = ss["primary"]["per_rewrite"][key][c], ss["sensitivity"]["per_rewrite"][key][c]
            for i, part in ((None, "change"), (0, "low"), (1, "high")):
                add("second service run (Table E1, Figure 2)", f"{lab} {c} {part}",
                    p["mean"] if i is None else p["ci"][i], s["mean"] if i is None else s["ci"][i])
        for grp in ("h", "g", "n"):
            p, s = ss["primary"]["pooled_vs_t0"][key][grp], ss["sensitivity"]["pooled_vs_t0"][key][grp]
            for i, part in ((None, "change"), (0, "low"), (1, "high")):
                add("second service run (Table E1, Figure 2)", f"{lab} group {grp.upper()} {part}",
                    p["mean"] if i is None else p["ci"][i], s["mean"] if i is None else s["ci"][i])
        for dk in ("h-n", "g-n", "g-h"):
            p, s = ss["primary"]["pooled_diff"][key][dk], ss["sensitivity"]["pooled_diff"][key][dk]
            for i, part in ((None, "change"), (0, "low"), (1, "high")):
                add("second service run (Table E1)", f"{lab} {dk.upper()} {part}",
                    p["mean"] if i is None else p["ci"][i], s["mean"] if i is None else s["ci"][i])
    rp = R["release test"]
    for name in ("rewrite n1, haiku",):
        e = rp["edits"][name]
        for setn, lab in (("specific", "hotel-brief set"), ("open", "no-type set")):
            for i, part in ((0, "change"), (1, "low"), (2, "high")):
                add("release test (Appendix E.3)", f"N1 {lab} {part}", e[setn][0][i], e[setn][1][i])
    sa = R["search-again run"]
    for m in steer3.MODELS:
        for key, lab in (("open | hotel-only", "H1 hotel only"), ("open | either", "G1 either")):
            cell = "h1" if lab.startswith("H1") else "g1"
            pe, se = sa["primary"][m]["sets"][key], sa["sensitivity"][m]["sets"][key]
            for part in ("first_change", "last_change"):
                for i, nm in ((None, "change"), (0, "low"), (1, "high")):
                    a = pe[part][cell]["change"] if i is None else pe[part][cell]["interval"][i]
                    b = se[part][cell]["change"] if i is None else se[part][cell]["interval"][i]
                    add("search-again run (Table E2)", f"{m} {lab} {part.split('_')[0]} search {nm}", a, b)
            for part in ("first", "last"):
                add("search-again run (Table E2)", f"{m} {lab} original-tool {part} rate",
                    100 * pe["rates"]["t0"][part]["share"], 100 * se["rates"]["t0"][part]["share"], "%")
        for cell in ("t0", "h1", "g1"):
            p, s = sa["primary"][m]["behaviour"][cell]["searched_again"], sa["sensitivity"][m]["behaviour"][cell]["searched_again"]
            add("search-again run (Table E2)", f"{m} searched again {cell}", 100 * p["k"] / p["n"], 100 * s["k"] / s["n"], "%")
    p, s = sa["primary"]["haiku"]["sets"]["open | hotel-only"]["drop_change"]["h1"], sa["sensitivity"]["haiku"]["sets"]["open | hotel-only"]["drop_change"]["h1"]
    for i, nm in ((None, "change"), (0, "low"), (1, "high")):
        add("search-again run (Section 5)", f"haiku H1 later searches removed part {nm}",
            p["change"] if i is None else p["interval"][i], s["change"] if i is None else s["interval"][i])
    for key in sa["primary_panel"]:
        if key.startswith(("hotel-only | h1", "either | g1")):
            p, s = sa["primary_panel"][key], sa["sensitivity_panel"][key]
            for i, nm in ((None, "change"), (0, "low"), (1, "high")):
                add("search-again run (Table E2, panel)", f"panel {key} {nm}",
                    p["change"] if i is None else p["interval"][i], s["change"] if i is None else s["interval"][i])
    lt = R["later turns"]
    for arm in ("t0", "t1"):
        pa, sa_ = lt["primary"][arm], lt["sensitivity"][arm]
        for grp, lab in (("F", "only guesthouses fit"), ("F_initial_failure", "after an initial exclusion"),
                         ("F_no_initial_failure", "without one"), ("R", "a hotel fits")):
            for key in ("initial_failure", "fit_shown", "never_fit", "hotel_only_end", "relapse"):
                a, b = pa[grp][key], sa_[grp][key]
                if a is None or b is None:
                    continue
                add("later turns (Table D1)", f"{arm} {lab} {key} ({a['k']}/{a['n']} -> {b['k']}/{b['n']})",
                    100 * a["share"], 100 * b["share"], "%")
            add("later turns (Table D1)", f"{arm} {lab} mean searches", pa[grp]["mean_searches"], sa_[grp]["mean_searches"], "searches")
    a, b = lt["primary"]["t0"]["never_fit_failure_minus_no_failure"], lt["sensitivity"]["t0"]["never_fit_failure_minus_no_failure"]
    for i, nm in ((None, "difference"), (0, "low"), (1, "high")):
        add("later turns (Section 6)", f"t0 never fit: initial exclusion minus none, {nm}",
            100 * (a["diff"] if i is None else a["ci"][i]), 100 * (b["diff"] if i is None else b["ci"][i]))
    la = R["label test"]
    for o, lab in (("search_failure", "exclusion"), ("hotel", "hotel filter")):
        for c in ("D_c", "D_n", "D_nc"):
            for s in ("no_type", "hotel_brief"):
                p, q = la["primary"]["results"][o][c][s]["panel"], la["sensitivity"]["results"][o][c][s]["panel"]
                for k, nm in (("D", "change"), ("low", "low"), ("high", "high")):
                    add("label-test tool calls (Section 7, Appendix G)", f"{lab} {c} {s} {nm}", p[k], q[k])
    for r in rows:
        a, b = r["reported"], r["sensitivity"]
        r["difference"] = None if a is None or b is None else b - a
        r["rounded_equal"] = a is not None and b is not None and round(a, 1) == round(b, 1)
    return rows


def decisions(R):
    out = []
    fsr = R["release test"]
    for e in fsr["pairs"]:
        for rule in ("first rule", "revised rule"):
            if e[rule][0] != e[rule][1]:
                out.append(f"29 pairs: {e['model']} {e['a']} vs {e['b']}, {rule}: {e[rule][0]} -> {e[rule][1]}")
    for name, e in fsr["edits"].items():
        for rule in ("first rule", "revised rule"):
            if e[rule][0] != e[rule][1]:
                out.append(f"release test {name}, {rule}: {e[rule][0]} -> {e[rule][1]}")
    sa = R["search-again run"]
    for m in steer3.MODELS:
        for key, e in sa["primary"][m]["sets"].items():
            for c, cat in e["category"].items():
                new = sa["sensitivity"][m]["sets"][key]["category"][c]
                if new != cat:
                    out.append(f"search-again {m} {key} {c}: category {cat} -> {new}")
    for q, v in sa["primary_predictions"].items():
        if json.dumps(v, sort_keys=True, default=str) != json.dumps(sa["sensitivity_predictions"][q], sort_keys=True, default=str):
            out.append(f"search-again prediction {q}: {v} -> {sa['sensitivity_predictions'][q]}")
    la = R["label test"]
    if json.dumps(la["primary"]["predictions"], sort_keys=True, default=str) != json.dumps(la["sensitivity"]["predictions"], sort_keys=True, default=str):
        out.append("label test: predictions changed")
    return out


def main():
    data, g = runs.context()
    sets = ra.request_sets(data, g)
    R = {}
    R["release test"] = release_pairs(sets)
    print("release test done", flush=True)
    R["first service run"] = first_service(data, sets)
    print("first service run done", flush=True)
    R["second service run"] = second_service(data, sets)
    print("second service run done", flush=True)
    R["search-again run"] = search_again(data, g)
    print("search-again run done", flush=True)
    R["later turns"] = later_turns(data)
    print("later turns done", flush=True)
    R["label test"] = label_test(data, g)
    print("label test done", flush=True)
    rows = compare_rows(R)
    dec = decisions(R)
    counts = {f"{k[0]} | {k[1]}": v for k, v in sorted(COUNTS.items())}
    blob = {"post_hoc": True, "no_model_call": True, "not_valid_answers_missing": counts,
            "search_again_dropped_conversations": R["search-again run"]["dropped"],
            "search_again_quote_rule_fixes": R["search-again run"]["quote_rule_fixes"],
            "later_turns_dropped": R["later turns"]["dropped"], "label_test_not_valid": R["label test"]["not_valid_calls"],
            "release_tally_one_answer": R["release test"]["tally_one_answer"], "comparison": rows,
            "decision_changes": dec}
    OUT.mkdir(exist_ok=True)
    (OUT / "loyal_unchecked_runs.json").write_text(json.dumps(blob, indent=1, default=str))
    big = [r for r in rows if r["difference"] is not None and abs(r["difference"]) >= 0.5 and r["unit"] != "searches"]
    L = ["## Full-schema sensitivity of the tool-call runs not covered by tool_validity.py (post hoc; no model call)", "",
         "Answers (or, for conversations, conversations) with a search call that is not valid after the run's declared "
         "normalization are missing; the frozen analysis functions then run unchanged.", "",
         "Answers counted as missing: " + json.dumps(counts), "",
         "Search-again run, conversations dropped (valid status, any call not valid after unquote and clean_nulls): "
         + json.dumps(R["search-again run"]["dropped"]),
         "Search-again run, calls that the declared quote rule makes valid: " + json.dumps(R["search-again run"]["quote_rule_fixes"]),
         "Later turns, complete conversations dropped: " + json.dumps(R["later turns"]["dropped"]),
         "Label-test tool calls not valid: " + json.dumps(R["label test"]["not_valid_calls"]), "",
         "29 stored pairs, one answer, tally (stored, sensitivity): " + json.dumps(R["release test"]["tally_one_answer"]), "",
         f"Reported values compared: {len(rows)}; rounded value changed: {sum(not r['rounded_equal'] for r in rows)}; "
         f"largest absolute difference: {max(abs(r['difference']) for r in rows if r['difference'] is not None):.3f}; "
         f"differences of 0.5 or more (points or %): {len(big)}", "",
         "Decision changes: " + (json.dumps(dec) if dec else "none"), "",
         "| Run | Quantity | Reported | Sensitivity | Difference |", "|---|---|---|---|---|"]
    for r in rows:
        if not r["rounded_equal"]:
            L.append(f"| {r['run']} | {r['quantity']} | {r['reported']:.2f} | {r['sensitivity']:.2f} | {r['difference']:+.2f} |")
    (OUT / "loyal_unchecked_runs.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
