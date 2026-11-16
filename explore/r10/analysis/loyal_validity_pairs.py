"""Two post hoc counts (stored rows only; no model call; no "em" folder).

1. Paired transitions, first-request tool calls (Appendix B, "Scorable and valid tool calls"): on the 448 first requests
   whose brief sets no type, pair each original-tool answer (arm t0) with the renamed-tool answer (arm t1) of the same
   request and the same read number (both from the same run folder of a_analyze.load). Count the original-tool
   exclusions (briefsearch.search_failure of a scorable search) whose paired renamed-tool answer is a no-call answer.
2. The second step with calls that are not valid counted as missing (Appendix C, Table C1): the trials after an
   exclusion (a_analyze.step2, "after_search_failure"), classed as in a_analyze.step2. A trial is missing when its
   first-request search call or its second-step search call does not fit the schema after tools.clean_nulls
   (tool_validity.problems, the checker of r10/analysis/tool_validity.py). Table C1 classes: removes the filter
   (search_unfiltered), mentions the other type (text_mentions), no mention (every other class).
The script asserts that the counts without the change equal the stored a.json values.
Usage (from explore/): python3 -I r10/analysis/loyal_validity_pairs.py
Outputs: r10/analysis/out/loyal_validity_pairs.md and loyal_validity_pairs.json.
This file is a copy of a project script with the paths of the study folder and the names of its output files changed; the results are the same. The title line of the Markdown output is shorter.
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
sys.path.insert(0, str(EXPLORE / "r10" / "analysis"))
import a_analyze as aa  # noqa: E402
import tool_validity as tv  # noqa: E402

import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import tools  # noqa: E402

T0 = tools.SEARCH_T0["input_schema"]


def bad(row):
    calls = row.get("tool_calls") or []
    if len(calls) != 1 or calls[0].get("name") != "search_hotels" or not isinstance(calls[0].get("input"), dict):
        return False
    return bool(tv.problems(tools.clean_nulls(calls[0]["input"]), T0))


def main():
    data, g = aa.runs.context()
    db = gold.hotel_db()
    open_ = {i for i in g["booked"] if gold.brief_type(data[i]) is None and gold.brief_type(data[i], "fail_info") is None}
    stored = json.loads((EXPLORE / "r10" / "analysis" / "out" / "a.json").read_text())["models"]
    out = {"transitions": {}, "step2": {}}
    for m in aa.MODELS:
        # 1. paired transitions t0 -> t1
        by = collections.defaultdict(dict)
        for folder in [f"era1_{m}", *aa.FILL.get(m, ())]:
            for r in aa.rows(folder) or []:
                d, arm, read = aa.split(r["custom_id"])
                if arm in ("t0", "t1") and d in open_:
                    by[(d, read)][arm] = aa.read_of(r, arm)
        c = collections.Counter()
        for key, arms in by.items():
            if "t0" not in arms or "t1" not in arms:
                continue
            k0, f0 = arms["t0"]
            k1, _ = arms["t1"]
            if k0 == "invalid" or k1 == "invalid":
                continue
            c["pairs"] += 1
            excl = k0 == "search" and bs.search_failure(f0, data[key[0]], db)
            c["original exclusions"] += excl
            c["original exclusion -> renamed no-call"] += excl and k1 == "none"
            c["original no-call"] += k0 == "none"
            c["renamed no-call"] += k1 == "none"
        out["transitions"][m] = dict(c)
        # 2. second step with calls that are not valid missing
        first = {}
        for r in aa.rows(f"era1_{m}") or []:
            d, arm, read = aa.split(r["custom_id"])
            if arm == "t0":
                kind, val = aa.read_of(r, arm)
                if kind == "search":
                    first[(d, read)] = (val, bad(r))
        res = {"stored": collections.Counter(), "sensitivity": collections.Counter()}
        for r in aa.rows(f"era2_{m}") or []:
            d, _, read = aa.split(r["custom_id"])
            if (d, read) not in first:
                continue
            f1, bad1 = first[(d, read)]
            if not (d in open_ and bs.search_failure(f1, data[d], db)):
                continue
            if r.get("type") != "succeeded" or r.get("stop") in aa.CUT:
                kind = "invalid"
            elif r.get("tool_calls"):
                k2, f2 = tools.parse_call(r, "t0")
                kind = "invalid" if k2 != "search" else ("search_filtered" if gold.hides_guesthouse(f2.get("type"))
                                                         else "search_unfiltered")
            elif (r.get("text") or "").strip():
                kind = "text_mentions" if aa.GUEST_OR_LIMITED.search(r["text"]) else "text_other"
            else:
                kind = "neither"
            res["stored"][kind] += 1
            if not bad1 and not bad(r):
                res["sensitivity"][kind] += 1
        assert dict(res["stored"]) == stored[m]["step2"]["after_search_failure"], (m, res["stored"])
        e = {}
        for v, cnt in res.items():
            n = sum(cnt.values())
            e[v] = {"trials": n, "removes": cnt["search_unfiltered"], "mentions": cnt["text_mentions"],
                    "no_mention": n - cnt["search_unfiltered"] - cnt["text_mentions"],
                    "shares": [100 * cnt["search_unfiltered"] / n, 100 * cnt["text_mentions"] / n,
                               100 * (n - cnt["search_unfiltered"] - cnt["text_mentions"]) / n]}
        out["step2"][m] = e
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "loyal_validity_pairs.json").write_text(json.dumps(out, indent=1))
    L = ["## Paired transitions and the second step without calls that are not valid (post hoc)", "",
         "### 1. Original-tool exclusions whose paired renamed-tool answer has no call (448 no-type first requests)", "",
         "| Model | Pairs | Original exclusions | of these, renamed answer without a call | Original no-call | Renamed no-call |",
         "|---|---|---|---|---|---|"]
    for m, c in out["transitions"].items():
        L.append(f"| {m} | {c['pairs']} | {c['original exclusions']} | {c['original exclusion -> renamed no-call']} | "
                 f"{c['original no-call']} | {c['renamed no-call']} |")
    L += ["", "### 2. Table C1 classes, stored and with calls that are not valid missing", "",
          "| Model | Trials | Removes the filter | Mentions the other type | No mention |", "|---|---|---|---|---|"]
    for m, e in out["step2"].items():
        for v in ("stored", "sensitivity"):
            x = e[v]
            L.append(f"| {m} ({v}) | {x['trials']} | {x['shares'][0]:.1f}% | {x['shares'][1]:.1f}% | {x['shares'][2]:.1f}% |")
    L += ["", "Check: the stored classes equal a.json models.<m>.step2.after_search_failure for every model."]
    (HERE / "out" / "loyal_validity_pairs.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
