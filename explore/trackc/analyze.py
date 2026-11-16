"""Score E4 (PROTOCOL.md) with the PLAN.md SI-08 definitions. Reads raw.jsonl and writes summary.json.

Usage: python3 -I analyze.py [folder]   (default: explore/e4)
"""
import collections
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import importlib  # noqa: E402
import os  # noqa: E402

EXP = importlib.import_module(os.environ.get("TRACKC_EXP", "e4"))  # e4, or e9 for the effort-high rerun
import templates as tp  # noqa: E402
from templates import anth  # noqa: E402

MAIN, OTHERS = "p_main", ("p_unclear", "p_null")
BOOT = 2000
STATUSES = ("ok", "absent", "error", "refusal", "truncated", "parse_fail")
DEFINITIONS = {
    "commitment": "ambiguous items: the target value commits when its acceptable set does not contain the acceptable "
                  "set of every reading; null, any, and unclear never commit; in condition d a commitment is a gap-fill",
    "commit_error": "a commitment whose value equals no reading",
    "retention": "clear controls: the target value equals the clear reading",
    "unclear_on_clear": "clear controls: unclear on the target field, and unclear over all 7 fields",
    "exchange_rate": "(commit rate p_main - other) / (retention p_main - other), cluster bootstrap over objects "
                     "(goals with the same target field and form values are one object); "
                     "the two drops are always given, and the rate is null when the retention drop is 0",
    "missing_cell": "absent row, API error, refusal, max_tokens stop (even if the text parses), or parse failure",
}


def parse(text):
    """The P5 parser for every form (protocol note 1). "unclear" in a form without the option is kept as "unclear"."""
    s, e = text.rfind("{"), text.rfind("}")  # the last object is the final answer
    obj = json.loads(text[s:e + 1])
    out = {"name": (obj.get("name") or None)}
    for f in tp.FIELDS[1:]:
        v = obj.get(f)
        if isinstance(v, str) and v.lower() == "unclear":
            out[f] = "unclear"
        elif v is None:
            out[f] = None
        elif isinstance(v, str) and v.lower() in ("any", "dontcare"):
            out[f] = "any"
        else:
            vals = v if isinstance(v, list) else [v]
            out[f] = tuple(dict.fromkeys(tp.norm(f, str(x)) for x in vals)) or None
    return out


def score(item, form):
    v = form[item.target]
    if item.kind == "ambiguous":
        readings = [i[item.target] for i in item.interpretations]
        union = frozenset().union(*(tp.accepts(item.target, r) for r in readings))
        commit = not tp.accepts(item.target, v) >= union
        return {"commit": commit, "commit_error": commit and v not in readings}
    return {"retained": v == item.interpretations[0][item.target], "unclear_target": v == "unclear",
            "unclear_fields": sum(form[f] == "unclear" for f in tp.FIELDS)}


def status(row):
    if row is None:
        return "absent", None
    if row["type"] != "succeeded":
        return "error", None
    if row.get("stop") == "refusal":
        return "refusal", None
    if row.get("stop") == "max_tokens":
        return "truncated", None
    try:
        return "ok", parse(row.get("text") or "")
    except (ValueError, AttributeError):
        return "parse_fail", None


def ratio(n, d):
    return n / d if d else None


def rates(sums):
    return {"commit": ratio(sums["commit"], sums["amb_valid"]), "retention": ratio(sums["retained"], sums["clr_valid"])}


def exchange(per_goal, label):
    """Exchange rate of p_main against each other form, with a cluster bootstrap over the formal objects."""
    goals = sorted(set().union(*per_goal.values()))

    def drops(sample):
        total = {form: collections.Counter() for form in per_goal}
        for g in sample:
            for form in per_goal:
                total[form].update(per_goal[form][g])
        main = rates(total[MAIN])
        out = {}
        for other in OTHERS:
            o = rates(total[other])
            out[other] = tuple(None if main[k] is None or o[k] is None else main[k] - o[k] for k in ("commit", "retention"))
        return out

    point = drops(goals)
    rng = random.Random(f"{tp.SEED}-{label}")
    boots = [drops([rng.choice(goals) for _ in goals]) for _ in range(BOOT)]
    result = {}
    for other in OTHERS:
        commit, retention = point[other]
        entry = {"clusters": len(goals), "commit_drop": commit, "retention_drop": retention,
                 "rate": commit / retention if commit is not None and retention else None}
        for i, key in enumerate(("commit_drop", "retention_drop")):
            vals = sorted(b[other][i] for b in boots if b[other][i] is not None)
            entry[f"{key}_ci95"] = [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]] if vals else None
        ci = entry["retention_drop_ci95"]
        entry["retention_drop_ci_holds_0"] = None if ci is None else ci[0] <= 0 <= ci[1]
        result[other] = entry
    return result


def summarize(rows):
    by_id = {r["custom_id"]: r for r in rows}
    cells = EXP.cells()
    known = {cid for cid, *_ in cells}
    groups = collections.defaultdict(lambda: {"status": collections.Counter(), "sums": collections.Counter(),
                                              "in": [], "out": []})
    per_goal = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(collections.Counter)))
    served = collections.defaultdict(set)
    for cid, item, form, _, model in cells:
        row = by_id.get(cid)
        g = groups[(item.condition, form, model)]
        st, parsed = status(row)
        g["status"][st] += 1
        if row is not None and row["type"] == "succeeded":
            g["in"].append(row["input_tokens"])
            g["out"].append(row["output_tokens"])
            served[model].add(row["model"])
        if st != "ok":
            continue
        s = score(item, parsed)
        kind = "amb" if item.kind == "ambiguous" else "clr"
        sums = collections.Counter({f"{kind}_valid": 1, **{k: int(v) for k, v in s.items()}})
        g["sums"].update(sums)
        per_goal[(item.condition, model)][form][(item.target, item.goal.others, item.goal.clear)].update(sums)

    out = {}
    for (c, form, model), g in sorted(groups.items()):
        s = g["sums"]
        out.setdefault(c, {}).setdefault(form, {})[model] = {
            "requests": sum(g["status"].values()), **{k: g["status"][k] for k in STATUSES},
            "commitment": {"valid": s["amb_valid"], "commit": s["commit"], "commit_error": s["commit_error"],
                           "rate": ratio(s["commit"], s["amb_valid"])},
            "retention": {"valid": s["clr_valid"], "retained": s["retained"], "rate": ratio(s["retained"], s["clr_valid"])},
            "unclear_on_clear": {"target": s["unclear_target"], "target_rate": ratio(s["unclear_target"], s["clr_valid"]),
                                 "fields": s["unclear_fields"],
                                 "field_rate": ratio(s["unclear_fields"], s["clr_valid"] * len(tp.FIELDS))},
            "tokens": {"input_mean": ratio(sum(g["in"]), len(g["in"])), "output_mean": ratio(sum(g["out"]), len(g["out"]))},
        }
    rates_x = {}
    for (c, model), pg in sorted(per_goal.items()):
        if MAIN in pg and all(o in pg for o in OTHERS):
            rates_x.setdefault(c, {})[model] = exchange(pg, f"{c}-{model}")
    return {"experiment": EXP.__name__, "conditions": tp.CONDITIONS, "definitions": DEFINITIONS, "requests": len(cells),
            "rows": len(rows), "unknown_rows": sum(r["custom_id"] not in known for r in rows),
            "absent": sum(st["absent"] for c in out.values() for f in c.values() for st in f.values()),
            "served_models": {m: sorted(v) for m, v in served.items()}, "cells": out, "exchange_rate": rates_x}


def main(folder):
    rows = [json.loads(line) for line in (folder / "raw.jsonl").read_text().splitlines() if line.strip()]
    summary = summarize(rows)
    (folder / "summary.json").write_text(json.dumps(summary, indent=1))
    print(f"{EXP.__name__}: {summary['rows']} rows, {summary['absent']} of {summary['requests']} requests absent")
    fmt = lambda x: "  -  " if x is None else f"{x:5.2f}"  # noqa: E731
    for c, forms in summary["cells"].items():
        for form, models in forms.items():
            for model, cell in models.items():
                print(f"  {c} {form:9} {model:17} commit {fmt(cell['commitment']['rate'])}  retention "
                      f"{fmt(cell['retention']['rate'])}  unclear on clear {fmt(cell['unclear_on_clear']['target_rate'])}")
    for c, models in summary["exchange_rate"].items():
        for model, pairs in models.items():
            for other, x in pairs.items():
                print(f"  {c} {model:17} p_main vs {other:9} rate {fmt(x['rate'])}  commit drop "
                      f"{fmt(x['commit_drop'])}  retention drop {fmt(x['retention_drop'])}")
    print(f"wrote {folder / 'summary.json'}")


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else anth.EXPLORE / EXP.__name__)
