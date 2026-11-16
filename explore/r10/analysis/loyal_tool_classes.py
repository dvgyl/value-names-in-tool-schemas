"""Answer classes of the first-request tool calls, per model and tool condition (post hoc; no model call).

Paper: Table B2 and Appendix B ("Scoring"). Stored answers only: the raw.jsonl files of era1_<model> and
the fill runs of a_analyze.FILL (the same files as a_analyze.py and tool_validity.py). No folder whose name starts
with "em", no sealed file and no key is opened.

For each answer of the arms t0 (original tool), t1 (renamed tool) and t0ask (original tool with the ask tool):
- not completed: the row failed or stopped at the output limit (a_analyze.read_of: "invalid");
- non-call: no tool call;
- ask call: one ask_traveller call (arm t0ask only);
- other: more than one call, a call of another tool, or a call that the parser cannot read;
- search call: one search_hotels call that tools.parse_call reads after tools.clean_nulls (a *scorable* search call);
  it is *schema-valid* when its arguments after clean_nulls fit the closed input schema
  (tool_validity.problems, the full-schema check).
Exclusion (a_analyze "search failure"): on the 448 first requests whose brief sets no type in either stage, a search
call whose type keeps hotel and not guesthouse while only guesthouses fit the brief. Primary denominator: every
scorable answer (search, ask or non-call), as in a_analyze.py. Sensitivity: the same with every search call that is
not schema-valid counted as missing (as in tool_validity.py).
The script asserts that its counts equal the stored outputs a.json and tool_validity.json.
Usage (from explore/): python3 -I r10/analysis/loyal_tool_classes.py
Outputs: r10/analysis/out/loyal_tool_classes.md and loyal_tool_classes.json.
This file is a copy of the project script tool_classes.py with the paths of the study folder and the names of its output files changed; the results are the same.
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
sys.path.insert(0, str(EXPLORE / "r10" / "analysis"))
import a_analyze as aa  # noqa: E402  (its imports set the paths; its main() does not run)
import tool_validity as tv  # noqa: E402

import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import tools  # noqa: E402

OUT = HERE / "out"
ARMS = ("t0", "t1", "t0ask")
SCHEMA = {"t0": tools.SEARCH_T0["input_schema"], "t1": tools.SEARCH_T1["input_schema"],
          "t0ask": tools.SEARCH_T0["input_schema"]}


def classify(row, arm):
    kind, val = aa.read_of(row, arm)
    if kind == "invalid" and val in ("failed", "cut"):
        return "not completed", None
    if kind == "none":
        return "non-call", None
    if kind == "ask":
        return "ask call", None
    if kind == "invalid":
        return "other", None
    args = tools.clean_nulls(row["tool_calls"][0]["input"])
    ok = not tv.problems(args, SCHEMA[arm])
    return ("search, schema-valid" if ok else "search, not schema-valid"), val


def main():
    data, g = aa.runs.context()
    db = gold.hotel_db()
    open_ = {i for i in g["booked"] if gold.brief_type(data[i]) is None and gold.brief_type(data[i], "fail_info") is None}
    assert len(open_) == 448
    stored_a = json.loads((EXPLORE / "r10" / "analysis" / "out" / "a.json").read_text())["models"]
    stored_tv = json.loads((EXPLORE / "r10" / "analysis" / "out" / "tool_validity.json").read_text())
    res = {}
    for m in aa.MODELS:
        folders = [f"era1_{m}", *aa.FILL.get(m, ())]
        c = {a: collections.Counter() for a in ARMS}
        excl = {a: collections.Counter() for a in ARMS}
        for folder in folders:
            rr = aa.rows(folder)
            if rr is None:
                continue
            for r in rr:
                d, arm, _ = aa.split(r["custom_id"])
                if arm not in ARMS:
                    continue
                cls, fields = classify(r, arm)
                c[arm]["answers"] += 1
                c[arm][cls] += 1
                if d not in open_ or cls in ("not completed", "other"):
                    continue
                fail = bool(fields) and bs.search_failure(fields, data[d], db)
                excl[arm]["non-calls among scorable"] += cls == "non-call"
                excl[arm]["n scorable"] += 1
                excl[arm]["k scorable"] += fail
                if cls != "search, not schema-valid":
                    excl[arm]["n schema-valid"] += 1
                    excl[arm]["k schema-valid"] += fail
                else:
                    excl[arm]["k removed"] += fail
        res[m] = {"counts": {a: dict(c[a]) for a in ARMS}, "exclusion_448": {a: dict(excl[a]) for a in ARMS}}
        # Step 2 (a_analyze.step2): the era2 trials and whether their era1 original-tool search call is schema-valid.
        first, r_first = {}, {}
        for r in aa.rows(f"era1_{m}") or []:
            d, arm, read = aa.split(r["custom_id"])
            if arm == "t0":
                cls, fields = classify(r, arm)
                if fields:
                    first[(d, read)] = (cls, fields)
                    r_first[(d, read)] = r
        s2 = collections.Counter()
        for r in aa.rows(f"era2_{m}") or []:
            d, _, read = aa.split(r["custom_id"])
            if (d, read) not in first:
                continue
            cls, f1 = first[(d, read)]
            part = "empty" if not bs.search(db, f1) else "nonempty"
            bad = cls == "search, not schema-valid"
            s2[f"{part} trials"] += 1
            s2[f"{part} trials after a call that is not schema-valid"] += bad
            if bad and part == "empty":
                # Is the result empty only because of the fields that do not fit the schema? Clear those fields
                # (set them to None, no filter) and search again.
                raw = tools.clean_nulls(r_first[(d, read)]["tool_calls"][0]["input"])
                sch = SCHEMA["t0"]["properties"]
                badkeys = {k for k in sch if k in raw and tv.problems(raw[k], sch[k])}
                cleared = {k: (None if k in badkeys else v) for k, v in f1.items()}
                s2["empty, not valid: a search without the invalid fields finds a venue"] += bool(bs.search(db, cleared))
                s2["empty, not valid: kinds " + "+".join(sorted(tv.value_kinds(raw, SCHEMA["t0"])))] += 1
            if d in open_ and bs.search_failure(f1, data[d], db):
                s2["trials after an exclusion"] += 1
                s2["trials after an exclusion, call not schema-valid"] += bad
        res[m]["step2"] = dict(s2)
        st = stored_a[m].get("step2") or {}
        for part in ("empty", "nonempty"):
            assert s2[f"{part} trials"] == sum(st.get(part, {}).values()), (m, part, "step2")
        assert s2["trials after an exclusion"] == sum((st.get("after_search_failure") or {}).values()), (m, "step2 fail")
        # checks against the stored outputs
        for a in ("t0", "t1"):
            row = next(x for x in stored_tv["audit"] if x["run"] == "first request" and x["model"] == m
                       and x["condition"].endswith(f"({a})"))
            sc = row["counts"]
            assert c[a]["answers"] == sc["answers"], (m, a, "answers")
            assert c[a]["non-call"] == sc.get("non-call", 0), (m, a, "non-call")
            assert c[a]["search, schema-valid"] == sc.get("valid after normalization", 0), (m, a, "schema-valid")
            blk = stored_tv["variant"]["first request"]["_blocking"][m][a]
            assert (excl[a]["k schema-valid"], excl[a]["n schema-valid"]) == (blk["k"], blk["n"]), (m, a, "sensitivity")
            sf = stored_a[m]["search_failure"][a]
            share = excl[a]["k scorable"] / excl[a]["n scorable"]
            assert abs(share - sf["share"]) < 1e-9, (m, a, "primary", share, sf)
        ask = stored_a[m]["share_ask"]
        assert (c["t0ask"]["ask call"], sum(v for k, v in c["t0ask"].items()
                                            if k not in ("answers", "not completed", "other"))) == (ask["k"], ask["n"]), (m, "ask")
    OUT.mkdir(exist_ok=True)
    (OUT / "loyal_tool_classes.json").write_text(json.dumps(res, indent=1))
    cols = ("answers", "not completed", "non-call", "ask call", "other", "search, schema-valid",
            "search, not schema-valid")
    L = ["## Answer classes of the first-request tool calls (post hoc; no model call)", "",
         "Scorable = parsed after the declared normalization (tools.parse_call after tools.clean_nulls). Schema-valid ="
         " the arguments after this normalization fit the closed input schema (tool_validity.problems).", "",
         "| Model | Tool | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
    for m, r in res.items():
        for a in ARMS:
            L.append(f"| {m} | {a} | " + " | ".join(str(r["counts"][a].get(k, 0)) for k in cols) + " |")
    L += ["", "Exclusion on the 448 first requests whose brief sets no type (k / n):", "",
          "| Model | Tool | Scorable answers (primary) | Schema-invalid calls missing (sensitivity) | Exclusions in removed calls |",
          "|---|---|---|---|---|"]
    for m, r in res.items():
        for a in ARMS:
            e = r["exclusion_448"][a]
            p = f"{e['k scorable']}/{e['n scorable']} = {100 * e['k scorable'] / e['n scorable']:.2f}%"
            s = f"{e['k schema-valid']}/{e['n schema-valid']} = {100 * e['k schema-valid'] / e['n schema-valid']:.2f}%"
            L.append(f"| {m} | {a} | {p} | {s} | {e.get('k removed', 0)} |")
    tot = {a: (sum(res[m]["exclusion_448"][a]["k scorable"] for m in res),
               sum(res[m]["exclusion_448"][a].get("k removed", 0) for m in res)) for a in ARMS}
    L += ["", "All six models, exclusions among scorable answers / of these in calls that are not schema-valid: "
          + "; ".join(f"{a} {k} / {x}" for a, (k, x) in tot.items()), "",
          "Step 2 (era2 trials joined to their era1 original-tool search, as in a_analyze.step2):", ""]
    for m, r in res.items():
        L.append(f"- {m}: {json.dumps(r['step2'])}")
    L += ["", "Renamed minus original tool, hotel filter, paired per first request (points): stored a.json against the "
          "sensitivity of tool_validity.json (calls that are not schema-valid missing):", ""]
    for m in res:
        for key_a, key_v in (("t1_minus_t0", "all 554"), ("t1_minus_t0_no_type", "brief no type 448")):
            a = 100 * stored_a[m][key_a]["mean"]
            v = 100 * stored_tv["variant"]["first request"][m][key_v]["mean"]
            res[m].setdefault("paired", {})[key_v] = {"stored": a, "sensitivity": v, "difference": v - a}
            L.append(f"- {m} {key_v}: {a:+.2f} against {v:+.2f} (difference {v - a:+.2f})")
    L += ["", "Ask share of the ask option (t0ask; a_analyze share_ask: ask calls / scorable answers), stored and with the "
          "search calls that are not schema-valid counted as missing:", ""]
    for m, r in res.items():
        c = r["counts"]["t0ask"]
        n_all = c["answers"] - c.get("not completed", 0) - c.get("other", 0)
        n_sens = n_all - c.get("search, not schema-valid", 0)
        k = c.get("ask call", 0)
        assert (k, n_all) == (stored_a[m]["share_ask"]["k"], stored_a[m]["share_ask"]["n"]), m
        r["ask_share"] = {"stored": [k, n_all, 100 * k / n_all], "sensitivity": [k, n_sens, 100 * k / n_sens]}
        L.append(f"- {m}: {k}/{n_all} = {100 * k / n_all:.2f}% -> {k}/{n_sens} = {100 * k / n_sens:.2f}% "
                 f"({100 * k / n_sens - 100 * k / n_all:+.2f} points)")
    (OUT / "loyal_tool_classes.json").write_text(json.dumps(res, indent=1))
    L += ["",
          "Checks: answers, non-calls and schema-valid calls equal tool_validity.json; the sensitivity counts equal "
          "tool_validity.json (_blocking); the primary shares equal a.json (search_failure); the ask counts equal "
          "a.json (share_ask)."]
    (OUT / "loyal_tool_classes.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
