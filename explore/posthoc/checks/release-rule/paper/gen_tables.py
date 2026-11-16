"""Markdown tables for the paper from the T1 and T3 outputs (no number is typed by hand).

Usage: python3 -I gen_tables.py    -> tables.md (three blocks: TABLE6, TABLE17, TABLE18) and numbers.json
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "out"
T1 = json.loads((OUT / "t1_compare.json").read_text())
T3 = json.loads((OUT / "t3_bootstrap.json").read_text())
LV = T1["levels"]["4"]
SC = {s["key"]: s for s in LV["scenarios"]}
PROF = {"haiku": "Haiku", "deepseek": "DeepSeek", "sol": "Sol"}


def pc(x):
    return f"{100 * x:.1f}"


def rng(a):
    lo, hi = pc(a[0]), pc(a[1])
    return lo if lo == hi else f"{lo}–{hi}"


def r(key, rule, outcome):
    return rng(SC[key]["ranges_across_profiles"][rule][outcome])


def table6():
    bm = LV["beyond_margin"]
    rows = [
        ("No change: false flag", "zero", "flag"), ("No change: pass", "zero", "pass"),
        ("No change: hold", "zero", "hold"), ("+6, both sets: flag", "broad6", "flag"),
        ("+6, specific only: flag", "spec6", "flag"), ("Above L: wrong pass", None, None),
        ("Sparse: flag", "sparse8", "flag"), ("Sparse: hold", "sparse8", "hold"),
        ("Cancelling, open: pass", "cancel_open", "pass"), ("Drift +3: false flag", "drift3", "flag"),
        ("Drift +3: hold", "drift3", "hold")]
    lines = ["| Scenario: outcome | Original | Final | Final without sign |", "|---|---|---|---|"]
    for lab, key, out in rows:
        if key is None:
            cells = []
            for rule in ("original", "final", "strat_nosign"):
                e = bm[rule]
                cells.append(f"≤ {100 * e['largest']['share']:.2f}")
        else:
            cells = [r(key, rule, out) for rule in ("original", "final", "strat_nosign")]
        lines.append(f"| {lab} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def fph(e):
    return " / ".join(pc(e[x]["share"]) for x in ("flag", "pass", "hold"))


def table17():
    order = [("zero", "No change"), ("broad6", "+6, both sets"), ("spec6", "+6, specific only"),
             ("sparse8", "Sparse, 6 requests"), ("cancel_open", "Cancelling, open set"),
             ("drift3", "Drift +3"), ("zero_m1", "No change, 59 × 1")]
    lines = ["| Scenario | Profile | Original | Revised | Final | Final without sign | Pooled |",
             "|---|---|---|---|---|---|---|"]
    for key, lab in order:
        for i, (p, row) in enumerate(SC[key]["profiles"].items()):
            cells = [fph(row["rules"][rule]) for rule in ("original", "revised", "final", "strat_nosign", "pooled")]
            lines.append(f"| {lab if i == 0 else ''} | {PROF[p]} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def f2(x):
    s = f"{x:+.2f}"
    return s.replace("-", "−")


def table18():
    want = [("five-model|luna|a", "final", "Luna, repeat; final, 99.5%"),
            ("five-model|gemma|a", "final", "Gemma, repeat; final, 99.5%"),
            ("stored|sonnet|era1 read 1|era1 read 2", "original", "Sonnet pair 1; original, 98.75%"),
            ("stored|sonnet|era1 read 1|erp", "original", "Sonnet pair 2; original, 98.75%"),
            ("fresh|luna|paraphrase 1", "final", "Luna, paraphrase 1, fresh test; final, 97.5%")]
    by = {(x["key"], x["rule"]): x for x in T3["rows"]}
    ends = {"five-model|luna|a": ("open", 0, "−L"), "five-model|gemma|a": ("specific", 1, "+L"),
            "stored|sonnet|era1 read 1|era1 read 2": ("specific", 0, "0"),
            "stored|sonnet|era1 read 1|erp": ("specific", 0, "0"), "fresh|luna|paraphrase 1": ("specific", 0, "−L")}
    lines = ["| Decision | 2,000 draws | 100,000 draws | Deciding end, boundary: 2,000; 100,000 draws |",
             "|---|---|---|---|"]
    rows_out = []
    for key, rule, lab in want:
        x = by[(key, rule)]
        s, j, bnd = ends[key]
        e2 = x["intervals_2000"][s][j]
        er = x["end_range_100000"][s]["low" if j == 0 else "high"]
        rngs = f2(er[0]) if f"{er[0]:.2f}" == f"{er[1]:.2f}" else f"{f2(er[0])} to {f2(er[1])}"
        decs = x["decisions_100000"]
        d100 = f"{decs[0]}" if len(set(decs)) == 1 else ", ".join(decs)
        which = f"{s}, {'low' if j == 0 else 'high'}"
        assert x["decision_20000_stored"] == decs[0]  # the caption says so
        lines.append(f"| {lab} | {x['decision_2000']} | {d100} | {which}, {bnd}: {f2(e2)}; {rngs} |")
        rows_out.append({"key": key, "rule": rule, "d2000": x["decision_2000"], "d20000": x["decision_20000_stored"],
                         "d100000": decs, "end_2000": e2, "end_range_100000": er, "set": s, "boundary": bnd})
    others = [x for x in T3["rows"] if (x["key"], x["rule"]) not in {(k, r_) for k, r_, _ in want}]
    assert all(not (x["changed_vs_2000"] or x["seeds_disagree"]) for x in others)
    dist = sorted(x["boundary"]["distance"] for x in others)
    zero_cases = [(x["label"], x["rule"]) for x in others if x["boundary"]["distance"] < 1e-9]
    pos = [x for x in others if x["boundary"]["distance"] > 1e-9]
    m = min(pos, key=lambda x: x["boundary"]["distance"])
    return "\n".join(lines), {"rows": rows_out, "n_total": len(T3["rows"]), "n_comparisons": len({x["key"] for x in T3["rows"]}),
                              "n_others": len(others), "zero_distance_cases": zero_cases,
                              "smallest_positive_distance": {"label": m["label"], "rule": m["rule"],
                                                             "distance": m["boundary"]["distance"],
                                                             "boundary": m["boundary"]["boundary"], "set": m["boundary"]["set"]},
                              "changed": [(x["label"], x["rule"]) for x in T3["rows"] if x["changed_vs_2000"] or x["seeds_disagree"]]}


def main():
    t18, info = table18()
    text = "\n\n".join(["<!-- TABLE6 -->\n" + table6(), "<!-- TABLE17 -->\n" + table17(), "<!-- TABLE18 -->\n" + t18])
    (HERE / "tables.md").write_text(text + "\n")
    bm = LV["beyond_margin"]
    nums = {"t3": info, "beyond_margin": {r_: {k: bm[r_][k] for k in ("wrong_passes", "trials", "share")} | {"largest": bm[r_]["largest"]}
                                          for r_ in ("original", "revised", "final", "strat_nosign", "pooled")},
            "mean_changed_sparse": {p: SC["sparse8"]["profiles"][p]["mean_changed_requests"]["specific"] for p in PROF}}
    (HERE / "numbers.json").write_text(json.dumps(nums, indent=1))
    print(text)
    print(json.dumps(nums, indent=1)[:3000])


if __name__ == "__main__":
    main()
