"""Option values in the Sonnet answers of the forward release test (amendment R10-6). Post hoc; no model call.

The edited tool renames the option "any" to dont_care in six fields and requires at least one value in each list.
The system text did not change, so it still names "any". This script reads the stored tool calls of erp_sonnet and
counts, for each arm:
- answers with a field that holds the text "any" (the edited tool does not allow it);
- answers with a field that holds dont_care (also with extra quote marks);
- answers with an empty list (the edited tool requires at least one value);
- answers that the mapping back to the original names changes (release.to_old against tools.clean_nulls), and whether
  a change touches the type field or the hotel score.
Outputs: out/release_values.md and out/release_values.json.
Usage (from explore/): .venv/bin/python -I r10/analysis/release_values.py
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import release_analyze as ra  # noqa: E402  (its imports set the paths; its main() does not run)

FOLDER = "erp_sonnet"
OPTION_FIELDS = ("area", "pricerange", "stars", "type", "parking", "internet")


def items(v):
    return v if isinstance(v, list) else [v]


def quoted_dont_care(args):
    return any(isinstance(x, str) and x != "dont_care" and x.strip('"\'') == "dont_care"
               for f in OPTION_FIELDS for x in items(args.get(f)))


def strict_variant(rows):
    """The decision when the tedit answers with a quoted dont_care (a value that the edited tool does not allow) are
    missing instead of scored. Same sets, statistics and rule as release_analyze.py (2,000 draws, registered seed)."""
    data, g = ra.runs.context()
    sets = ra.request_sets(data, g)
    drop = set()
    for r in rows:
        _, d, arm, _ = r["custom_id"].split("-")
        calls = r.get("tool_calls") or []
        if arm == "tedit" and len(calls) == 1 and isinstance(calls[0].get("input"), dict) \
                and quoted_dont_care(calls[0]["input"]):
            drop.add(d + ".json")
    reads = ra.load(FOLDER, False)
    for d in drop:
        reads[(d, "tedit")] = [("invalid", "quoted dont_care")]
    res = {"answers_missing": len(drop)}
    for s in ("open", "specific"):
        ci, n_pairs, _ = ra.change(reads, sets[s])
        res[s] = {"pairs": n_pairs, "change": ci[0], "interval": [ci[1], ci[2]], "decision": ra.decide(*ci, ra.L)}
    tup = lambda e: (e["change"], *e["interval"])  # noqa: E731
    res["release"] = ra.release(tup(res["open"]), tup(res["specific"]), ra.L, ra.N_MAX, ra.N_MAX)
    return res


def main():
    path = ra.EXPLORE / FOLDER / "raw.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines()]
    out = {"post_hoc": True, "no_model_call": True, "folder": FOLDER, "arms": {}}
    for arm in ra.ARMS:
        c = collections.Counter()
        fields_any, fields_dc = collections.Counter(), collections.Counter()
        for r in rows:
            if r["custom_id"].split("-")[2] != arm:
                continue
            c["answers"] += 1
            calls = r.get("tool_calls") or []
            if len(calls) != 1 or not isinstance(calls[0].get("input"), dict):
                c["no single call"] += 1
                continue
            args = calls[0]["input"]
            has_any = [f for f in OPTION_FIELDS if any(x == "any" for x in items(args.get(f)))]
            has_dc = [f for f in OPTION_FIELDS
                      if any(isinstance(x, str) and x.strip('"\'') == "dont_care" for x in items(args.get(f)))]
            quoted = [f for f in OPTION_FIELDS
                      if any(isinstance(x, str) and x != "dont_care" and x.strip('"\'') == "dont_care"
                             for x in items(args.get(f)))]
            empty = [f for f in OPTION_FIELDS if args.get(f) == []]
            c["answers with any"] += bool(has_any)
            c["answers with dont_care (any spelling)"] += bool(has_dc)
            c["answers with quoted dont_care"] += bool(quoted)
            c["answers with an empty list"] += bool(empty)
            fields_any.update(has_any)
            fields_dc.update(has_dc)
            if arm == "tedit":
                mapped = ra.rel.to_old(args)
                cleaned = {k: v for k, v in ra.rel.tools.clean_nulls(args).items() if k in mapped}
                changed = [f for f in mapped if mapped[f] != cleaned.get(f)]
                c["answers changed by the mapping back"] += bool(changed)
                c["changes in the type field"] += "type" in changed
                before = "hotel" in items(cleaned.get("type") or [])
                after = "hotel" in items(mapped.get("type") or [])
                c["hotel value changed by the mapping back"] += before != after
        out["arms"][arm] = {"counts": dict(c), "fields_with_any": dict(fields_any),
                            "fields_with_dont_care": dict(fields_dc)}
    out["strict_variant"] = strict_variant(rows)
    (ra.OUT / "release_values.json").write_text(json.dumps(out, indent=1))
    lines = ["## Forward release test: option values in the Sonnet answers (post hoc)", "",
             "No model call. Stored tool calls of the forward release test, Sonnet, one answer per prefix and arm. "
             "Arm t0: the original tool; arm tedit: the edited tool (\"any\" renamed dont_care; at least one value "
             "in each list). The system text names \"any\" in both arms.", ""]
    for arm, e in out["arms"].items():
        lines.append(f"- {arm}: " + "; ".join(f"{k} {v}" for k, v in e["counts"].items())
                     + f"; fields with any {json.dumps(e['fields_with_any'])}"
                     + f"; fields with dont_care {json.dumps(e['fields_with_dont_care'])}")
    sv = out["strict_variant"]
    lines += ["", f"Variant: the {sv['answers_missing']} tedit answers with a quoted dont_care count as missing "
                  f"(2,000 draws, registered seed, level {100 * ra.LEVEL:.2f}%):"]
    for s in ("open", "specific"):
        e = sv[s]
        lines.append(f"- {s}: {e['pairs']} pairs, change {e['change']:+.2f} "
                     f"[{e['interval'][0]:+.2f}, {e['interval'][1]:+.2f}], {e['decision']}")
    lines.append(f"- model decision: {sv['release']}")
    (ra.OUT / "release_values.md").write_text("\n".join(lines) + "\n")
    print((ra.OUT / "release_values.md").read_text())


if __name__ == "__main__":
    main()
