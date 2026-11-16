"""X3 and Z4 analysis (PROTOCOL.md section "X3 and Z4"). Local files only, no API call.

For each pair and model: the share of reads whose pair slot holds the pair value, under the original form and under
the neutral form (the neutral value maps back), the drop in percentage points, and the dialogue-level exact sign test
of `forms/e8_measure.py`. Then the Spearman correlation between Rule B and the drop over the pairs of each set.
X3 uses the `x3` instances. Z4 uses the 16 Z4 pairs: the new `z4` instances, and for a pair that X3 also reads, the
first 120 `x3` instances. A read that did not end, or that does not parse, is left out and counted.
Exploratory split: the drop among instances whose brief sets the value and among the others.
Usage: python3 -I r9/detector/analyze.py
"""
import collections
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runs  # noqa: E402
import forms  # noqa: E402
import e8_measure  # noqa: E402  (runs.py puts forms/ on the path)

Z4_FROM_X3 = 120


def load(rows, sel):
    """{(model, pair id, variant): {dialogue: [read holds the value, ...]}} and the counts of the left-out reads."""
    fs = {(p["id"], v): runs.pair_form(p, v) for p in sel["pairs"] for v in runs.VARIANTS}
    h, out = collections.defaultdict(lambda: collections.defaultdict(list)), collections.Counter()
    for r in rows:
        _, d, pid, variant, _, short = runs.split_custom_id(r["custom_id"])
        if r["type"] != "succeeded" or r.get("stop") != "end_turn":
            out[(short, variant, r.get("stop") or r["type"])] += 1
            continue
        try:
            parsed = forms.parse(r["text"], fs[pid, variant])
        except (ValueError, KeyError, TypeError, AttributeError):
            out[(short, variant, "unparsed")] += 1
            continue
        h[(short, pid, variant)][d].append(forms.holds(parsed, fs[pid, variant]))
    return h, out


def rate(cell, keep):
    hits = [x for d in keep for x in cell.get(d, [])]
    return (sum(hits) / len(hits), len(hits)) if hits else (None, 0)


def stats(h, short, pid, keep):
    a, b = h.get((short, pid, "orig"), {}), h.get((short, pid, "neut"), {})
    (ra, na), (rb, nb) = rate(a, keep), rate(b, keep)
    more, less, p = e8_measure.sign_test({d: a[d] for d in keep if d in a}, {d: b[d] for d in keep if d in b})
    drop = None if ra is None or rb is None else 100 * (ra - rb)
    return {"orig": ra, "neut": rb, "reads": (na, nb), "drop": drop, "more": more, "less": less, "p": p}


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda k: xs[k])
    out, k = [0.0] * len(xs), 0
    while k < len(xs):
        j = k
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[k]]:
            j += 1
        for m in range(k, j + 1):
            out[order[m]] = (k + j) / 2 + 1
        k = j + 1
    return out


def spearman(x, y):
    """Pearson correlation of the ranks (ties get the mean rank). None with fewer than 3 points or no spread."""
    if len(x) < 3:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx, syy = sum((a - mx) ** 2 for a in rx), sum((b - my) ** 2 for b in ry)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else None


def members(sel, name):
    """(pair, instances) of the X3 set or the Z4 set."""
    if name == "X3":
        return [(p, p["x3"]) for p in sel["pairs"] if "x3" in p]
    return [(p, p["z4"] if "z4" in p else p["x3"][:Z4_FROM_X3]) for p in sel["pairs"] if "z4" in p["roles"]]


def pct(x):
    return "  -  " if x is None else f"{100 * x:5.1f}"


def signed(x, digits=1):
    return "-" if x is None else f"{x:+.{digits}f}"


def report(h, sel, name, models, out=print):
    rho = {}
    for short in models:
        out(f"== {name}, {short}: share of reads that write the pair value, original -> neutral form")
        b, d = [], []
        for p, keep in members(sel, name):
            s = stats(h, short, p["id"], keep)
            role = "high risk" if "x3_high" in p["roles"] else "control" if "x3_control" in p["roles"] else ""
            match = set(p["brief_match"])
            split = [stats(h, short, p["id"], [i for i in keep if (i in match) == m])["drop"] for m in (True, False)]
            out(f"{p['id']} {p['domain']}-{p['slot']}={p['value']!r:26} B {p['rule_b']:.3f} {role:9} "
                f"{pct(s['orig'])}% -> {pct(s['neut'])}% (reads {s['reads'][0]}, {s['reads'][1]}) drop "
                f"{signed(s['drop'])} pp; dialogues {s['more']} to {s['less']}, p = {s['p']:.2g}; exploratory drop, "
                f"brief sets value ({len(match & set(keep))}) {signed(split[0])}, other {signed(split[1])}")
            if s["drop"] is not None:
                b.append(p["rule_b"])
                d.append(s["drop"])
            if name == "X3" and short == "sonnet" and s["drop"] is not None:
                ok = s["drop"] >= 3 if role == "high risk" else abs(s["drop"]) <= 2
                out(f"   prediction ({'drop of 3 points or more' if role == 'high risk' else 'move of 2 points or less'}"
                    f"): {'holds' if ok else 'fails'}")
        rho[short] = spearman(b, d)
        out(f"   Spearman(Rule B, drop) over {len(d)} pairs: {signed(rho[short], 3)}"
            + ("  (Z4 prediction: above 0)" if name == "Z4" else ""))
    return rho


def main():
    sel = runs.selection()
    rows = []
    for exp in runs.RUNS:
        path = runs.EXPLORE / exp / "raw.jsonl"
        if path.exists():
            rows += [json.loads(line) for line in open(path)]
        print(f"{exp}: {'raw.jsonl found' if path.exists() else 'no raw.jsonl yet'}")
    h, left = load(rows, sel)
    for key, n in sorted(left.items()):
        print(f"left out: {key} {n}")
    report(h, sel, "X3", ("haiku", "sonnet", "luna", "sol", "deepseek", "qwen", "gemma"))
    if sel["z4_selected"]:
        report(h, sel, "Z4", ("haiku", "sonnet", "luna"))


if __name__ == "__main__":
    main()
