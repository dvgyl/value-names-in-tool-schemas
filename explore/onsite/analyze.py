"""Score the E2 replies with the P1 and P3 scorer and write explore/e2/summary.json.

Run with the repository venv:  harness/.venv/bin/python onsite/analyze.py [--raw PATH] [--out PATH]
"""
import argparse
import collections
import json
import math
import pathlib
import statistics
import sys

sys.dont_write_bytecode = True

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import e2  # noqa: E402

sys.path.insert(0, str(e2.REPO / "src"))
from sib.admission import ReconstructionParseError  # noqa: E402
from si_eval.extraction_task import (  # noqa: E402
    SchemaValidationError,
    parse_extraction_output,
    score_item,
    validate_extraction_payload,
)

OUTCOMES = ("right", "wrong", "parse_fail", "crash", "refusal", "truncated", "error")
MISSING = ("crash", "refusal", "truncated", "error")
DEFINITIONS = {
    "wrong": "The reply passes the schema gate and the repository audit finds a divergence from the case gold (P1, P3).",
    "flip": "A wrong reply that changes the full matching (P3 flip).",
    "flip_p1": "A flip whose reply also passes naive validation (P1 sdfr_hit).",
    "parse_fail": "The reply fails the schema gate or the parse. The scorer scores it as not wrong, as in P1 and P3.",
    "crash": "The parser raised a ValueError (P1 crash_valueerror). A missing cell.",
    "refusal, truncated, error": "Missing cells (PROTOCOL.md). The scorer does not read them.",
    "absent": "A request with no row in raw.jsonl.",
    "renamed": "Each reply is mapped back to remote and site with P3 map_back before the scorer reads it.",
    "mcnemar_read1": "Exact two-sided McNemar test on read 1, arm orig against each other arm, over the cases that have "
                     "no missing cell in either arm. Descriptive only.",
}


def outcome(row, case, map_back=None):
    """One outcome per reply, plus the two flip marks for a wrong reply."""
    if row["type"] != "succeeded":
        return {"outcome": "error"}
    if row["stop"] in ("refusal", "max_tokens"):
        return {"outcome": "refusal" if row["stop"] == "refusal" else "truncated"}
    text = row.get("text") or ""
    if map_back:
        try:
            text = map_back(text)
        except (ReconstructionParseError, ValueError, TypeError, AttributeError):
            text = ""
    try:
        validate_extraction_payload(text)
        extracted, err = parse_extraction_output(text, case), None
    except (SchemaValidationError, ReconstructionParseError) as exc:
        extracted, err = None, str(exc)
    except ValueError:
        return {"outcome": "crash"}
    item = score_item(case, extracted, parse_error=err, model=row.get("model") or "")
    if not item.schema_valid:
        return {"outcome": "parse_fail"}
    wrong = bool(item.semantically_divergent)
    flip = wrong and bool(item.allocation_changed)
    return {"outcome": "wrong" if wrong else "right", "flip": flip, "flip_p1": flip and bool(item.naive_validation_passed)}


def mcnemar(first, second):
    """first and second: per case, whether the event happened. Returns the discordant counts and the exact p-value."""
    b = sum(x and not y for x, y in zip(first, second))
    c = sum(y and not x for x, y in zip(first, second))
    n = b + c
    p = 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)
    return {"pairs": len(first), "orig_only": b, "other_only": c, "p_exact": p}


def summarize(rows, cases, map_back):
    ids = [r["custom_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate custom_id in raw.jsonl"
    counts = collections.defaultdict(lambda: collections.Counter({k: 0 for k in OUTCOMES + ("flip", "flip_p1")}))
    tokens = collections.defaultdict(lambda: ([], []))
    read1 = {}
    for row in rows:
        model, arm, read, cid = e2.parse_id(row["custom_id"])
        o = outcome(row, cases[cid], map_back if arm == "renamed" else None)
        c = counts[(model, arm, read)]
        c[o["outcome"]] += 1
        c["flip"] += o.get("flip", False)
        c["flip_p1"] += o.get("flip_p1", False)
        if row["type"] == "succeeded":
            tokens[(model, arm)][0].append(row["input_tokens"])
            tokens[(model, arm)][1].append(row["output_tokens"])
        if read == 1:
            read1[(model, arm, cid)] = o

    models = {}
    for model in e2.MODELS.values():
        models[model] = {}
        for arm in e2.ARMS:
            per_read = {}
            for k in e2.READS:
                c = dict(counts[(model, arm, k)])
                c["absent"] = len(cases) - sum(c[x] for x in OUTCOMES)
                per_read[str(k)] = c
            pooled = {key: sum(r[key] for r in per_read.values()) for key in per_read["1"]}
            tin, tout = tokens[(model, arm)]
            models[model][arm] = {
                "per_read": per_read, "pooled": pooled,
                "tokens": {"n": len(tin), "input_mean": statistics.fmean(tin) if tin else None,
                           "output_mean": statistics.fmean(tout) if tout else None}}

    tests = {}
    for model in e2.MODELS.values():
        tests[model] = {}
        for other in e2.ARMS[1:]:
            paired = [cid for cid in cases
                      if all(read1.get((model, arm, cid), {"outcome": "error"})["outcome"] not in MISSING
                             for arm in ("orig", other))]
            tests[model][f"orig_vs_{other}"] = {
                event: mcnemar([hit(read1[(model, "orig", c)]) for c in paired],
                               [hit(read1[(model, other, c)]) for c in paired])
                for event, hit in (("wrong", lambda o: o["outcome"] == "wrong"), ("flip", lambda o: o.get("flip", False)))}
    return {"experiment": "e2", "rows": len(rows),
            "expected_rows": len(cases) * len(e2.ARMS) * len(e2.READS) * len(e2.MODELS),
            "cases": len(cases), "definitions": DEFINITIONS, "models": models, "mcnemar_read1": tests}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", type=pathlib.Path, default=e2.EXPLORE / "e2" / "raw.jsonl")
    ap.add_argument("--out", type=pathlib.Path, default=e2.EXPLORE / "e2" / "summary.json")
    args = ap.parse_args()
    rows = [json.loads(line) for line in args.raw.read_text().splitlines() if line.strip()]
    summary = summarize(rows, e2.onsite_cases(), e2.load_p3().map_back)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=1))
    for model, arms in summary["models"].items():
        for arm, cell in arms.items():
            p = cell["pooled"]
            print(f"{model} {arm}: wrong {p['wrong']}, flip {p['flip']}, parse_fail {p['parse_fail']}, "
                  f"missing {sum(p[k] for k in MISSING)}, absent {p['absent']}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
