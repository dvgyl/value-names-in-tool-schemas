"""E15: replication of the E14 Sonnet condition b result with new reads (PROTOCOL.md, 2026-10-25).

The 40 ambiguous condition b items x `p_main`, `p_null`, and `p_unclear`, with the E14 request settings (structured
output, `claude-sonnet-5-5`, thinking `between_tools`, effort high), reads 3 to 2 + READS (E14 used reads 1 and 2).
The size estimate comes from the real E14 rows of the same items (`size`), so no pilot runs.
Usage: python3 -I e15.py size | estimate | submit --approve <bound> | fetch | analyze
"""
import collections
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import analyze as tc  # noqa: E402
import e14  # noqa: E402
import templates  # noqa: E402
from templates import anth  # noqa: E402

MODEL, THINKING, EFFORT = e14.SETTINGS["sonnet"]
READS = 4
FIRST_READ = 3
EXPECTED = 40 * len(templates.FORMS) * READS


def chosen():
    return [item for item in templates.items() if item.condition == "b" and item.kind == "ambiguous"]


def cells():
    return [(f"e15-{item.id}-{form}-r{read}", item, form, read, MODEL)
            for item in chosen() for form in templates.FORMS for read in range(FIRST_READ, FIRST_READ + READS)]


def build():
    reqs = [anth.request(cid, MODEL, EFFORT, e14.MAX_TOKENS, item.text, templates.FORMS[form], THINKING, e14.schema(form))
            for cid, item, form, _, _ in cells()]
    assert len(reqs) == EXPECTED, len(reqs)
    return reqs


def size():
    """Write e15/pilot.json from the E14 rows of the same items and model: real input over estimated input, mean output."""
    ids = {f"e14-{item.id}-{form}-r{read}-sonnet" for item in chosen() for form in templates.FORMS for read in (1, 2)}
    est = {r["custom_id"]: anth.est_in(r) for r in map(json.loads, open(anth.EXPLORE / "e14" / "requests.jsonl"))
           if r["custom_id"] in ids}
    rows = [r for r in map(json.loads, open(anth.EXPLORE / "e14" / "raw.jsonl")) if r["custom_id"] in ids]
    assert len(rows) == len(est) == len(ids), (len(rows), len(est), len(ids))
    out = {f"{MODEL}|{EFFORT}": {"in_ratio": sum(r["input_tokens"] for r in rows) / sum(est[r["custom_id"]] for r in rows),
                                 "out_mean": sum(r["output_tokens"] for r in rows) / len(rows),
                                 "out_max": max(r["output_tokens"] for r in rows), "n": len(rows),
                                 "source": "e14 raw.jsonl, the same items, forms, and model, reads 1 and 2"}}
    anth.pilot_path("e15").parent.mkdir(parents=True, exist_ok=True)
    anth.pilot_path("e15").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def sign_test(a, b, items):
    """Exact two-sided sign test over items: commitment counts of form a against form b, ties dropped."""
    more = sum(a[i] > b[i] for i in items)
    less = sum(a[i] < b[i] for i in items)
    n, k = more + less, min(more, less)
    p = min(1.0, 2 * sum(math.comb(n, j) for j in range(k + 1)) / 2 ** n) if n else 1.0
    return {"first_more": more, "second_more": less, "ties": len(items) - n, "p_exact": p}


def analyze():
    """Commitment per form for E15 alone, for E14 reads 1 and 2, and for both pooled."""
    sums = collections.defaultdict(collections.Counter)
    per_item = collections.defaultdict(collections.Counter)
    items = {item.id: item for item in chosen()}
    for exp, suffix in (("e14", "-sonnet"), ("e15", "")):
        for r in map(json.loads, open(anth.EXPLORE / exp / "raw.jsonl")):
            cid = r["custom_id"]
            if not cid.endswith(suffix):
                continue
            body = cid.removeprefix(f"{exp}-").removesuffix(suffix)
            form = next((f for f in templates.FORMS if f"-{f}-r" in body), None)
            item = items.get(body.split(f"-{form}-r")[0]) if form else None
            if item is None:
                continue
            state, parsed = tc.status(r)
            sums[(exp, form)]["requests"] += 1
            if state == "ok":
                sums[(exp, form)]["valid"] += 1
                sums[(exp, form)]["commit"] += tc.score(item, parsed)["commit"]
                per_item[(exp, form)][item.id] += tc.score(item, parsed)["commit"]
    out = {}
    for label, exps in (("e15", ("e15",)), ("e14_reads_1_2", ("e14",)), ("pooled", ("e14", "e15"))):
        out[label] = {}
        for form in templates.FORMS:
            n = sum(sums[(e, form)]["valid"] for e in exps)
            k = sum(sums[(e, form)]["commit"] for e in exps)
            out[label][form] = {"valid": n, "commit": k, "rate": round(k / n, 4) if n else None,
                                "missing": sum(sums[(e, form)]["requests"] for e in exps) - n}
    out["sign_test_e15"] = {f"{x}_vs_{y}": sign_test(per_item[("e15", x)], per_item[("e15", y)], items)
                            for x, y in (("p_unclear", "p_null"), ("p_main", "p_unclear"))}
    (anth.EXPLORE / "e15" / "summary.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1:] == ["size"]:
        size()
    elif sys.argv[1:] == ["analyze"]:
        analyze()
    else:
        anth.main("e15", build, planning_out=100, account="anthropic_old")
