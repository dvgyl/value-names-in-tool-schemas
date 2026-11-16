"""Review fix (2026-11-15): can a tool call whose arguments do not fit the schema enter the returned-flag experiment?

Usage (from explore/): python3 -I posthoc/checks/repair-counts/strict_check.py
Post hoc; no model call. It reads the stored first-request answers era1_<model> (arm t0) through the code of the
experiment (tools.parse_call, briefsearch.search and .relaxation, gold.hides_guesthouse, flag.sample, flag2.sample_b)
and the full-schema validator of r10/analysis/tool_validity.py (problems, value_kinds). It opens no folder whose name
starts with "em", no sealed file and no key file.

For every t0 search call it records: whether the arguments after tools.clean_nulls fit the schema of tools.SEARCH_T0;
the kinds of the problems; whether the parsed call has a hotel-only filter; whether the relaxation check flags it (the
search finds no venue and the same search without its type finds 1 or more); and whether the call is in the sample of
the returned-flag experiment. Output: out/strict_check.json.
"""
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]  # explore/ of the repository
EXPLORE = ROOT
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import briefsearch as bs  # noqa: E402
import flag  # noqa: E402
import flag2  # noqa: E402
import gold  # noqa: E402
import stage2  # noqa: E402
import tool_validity as tv  # noqa: E402
import tools  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent / "out/strict_check.json"
SCHEMA = tools.SEARCH_T0["input_schema"]


def main():
    db = gold.hotel_db()
    samples = {m: {r["custom_id"] for r, *_ in flag.sample(m, db)} for m in flag.MODELS}
    samples.update({m: {r["custom_id"] for r, *_ in flag2.sample_b(m, db)} for m in flag2.MODELS_B})
    out = {"post_hoc": True, "models": {}}
    for m in ("sonnet", "haiku", "opus", "sol", "astra"):
        c = collections.Counter()
        kinds = collections.Counter()
        invalid_flagged = []
        for row in stage2.rows_of(EXPLORE / f"era1_{m}", "raw"):
            if row.get("type", "succeeded") != "succeeded" or "-t0-" not in row["custom_id"]:
                continue
            kind, fields = tools.parse_call(row, "t0")
            if kind != "search":
                continue
            c["search calls"] += 1
            args = tools.clean_nulls(row["tool_calls"][0]["input"])
            bad = bool(tv.problems(args, SCHEMA))
            ho = gold.hides_guesthouse(fields.get("type"))
            rel = bs.relaxation(fields, db)
            insample = row["custom_id"] in samples[m]
            c["in flag sample"] += insample
            if not bad:
                continue
            c["invalid after normalization"] += 1
            for k in tv.value_kinds(args, SCHEMA):
                kinds[k] += 1
            c["invalid, hotel-only"] += ho
            c["invalid, search finds a venue"] += rel["count"] > 0
            c["invalid, search without type finds a venue"] += rel["count_without_type"] > 0
            c["invalid, flagged by the relaxation check"] += rel["flag"]
            c["invalid, hotel-only and flagged"] += ho and rel["flag"]
            c["invalid, in flag sample"] += insample
            if rel["flag"]:
                invalid_flagged.append({"custom_id": row["custom_id"], "kinds": sorted(tv.value_kinds(args, SCHEMA)),
                                        "problems": tv.problems(args, SCHEMA), "hotel_only": ho, "in_sample": insample})
        out["models"][m] = {"counts": dict(c), "kinds": dict(kinds), "invalid_flagged": invalid_flagged,
                            "sample_size": len(samples[m])}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps({m: (v["counts"], v["kinds"], v["sample_size"]) for m, v in out["models"].items()}, indent=1))
    for m, v in out["models"].items():
        for x in v["invalid_flagged"]:
            print(m, x)


if __name__ == "__main__":
    main()
