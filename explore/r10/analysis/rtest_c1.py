"""Analysis C.1 of the combined plan (post hoc, exploratory).

This file is a copy of the project analysis (an internal file) with the paths of the study folder and neutral names;
the results are the same. Usage (from explore/): python3 -I r10/analysis/rtest_c1.py
Output: r10/analysis/out/rtest_c1.json and rtest_c1.md.

What the script does:
1. The release rule on every stored tool-call comparison (the 29 unchanged-tool pairs with one answer per prefix,
   and the 23 edit comparisons), under the first rule and under the revised flag condition. It reads these
   decisions from out/rtest_check_values.json (stored values of the verified check) and adds the revised condition in
   the form of the plan: |change| >= L, the interval excludes zero, and the two-sided exact sign test over prefixes
   gives p <= 1 - level (0.0125 at the 98.75% level).
2. The same condition on the stored form rows of Table 14 of the paper that keep their sign counts: the held-out
   full rename per model (stage1.json, 95% intervals, alpha 0.05) and the exploratory value-only rename and opaque
   code (r2_posthoc.json, 95% intervals, alpha 0.05).
3. Per-request change: for each comparison, the prefixes whose hotel value rises and falls; and the field-order edit
   against the repeat with the shared control (prefixes that change under one update only).
4. Detection of the full rename against the size of the open set: random subsets of n open prefixes, the open-set
   decision under both conditions (98.75%, 2,000 bootstrap draws, the rule code of release_analyze.decide).

Safety: no model call, no network call. The loaders of the check (rtest_v.py) refuse a folder whose name starts with "em". The
script opens no sealed file, no key file and no .env file.
"""
import collections
import json
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]

sys.path.insert(0, str(HERE))
import rtest_v as V  # noqa: E402  (extract of the independent check: loaders and parsers)
ra, stats, runs = V.ra, V.stats, V.runs

L = 5.0
SEED = 20261112
MY_SEED = 20261116  # seed of this analysis (subsets)


def sign_p(up, down):
    return V.sign_p(up, down)


def revised_set(s, alpha):
    """Plan form: |change| >= L, interval excludes zero, exact sign p <= alpha. Else the first rule's other classes."""
    if abs(s["change"]) >= L and (s["low"] > 0 or s["high"] < 0) and s["sign_p"] <= alpha:
        return "meets flag rule"
    if -L <= s["low"] and s["high"] <= L:
        return "within limits"
    return "unresolved"


def first_set(s):
    d = ra.decide(s["change"], s["low"], s["high"], L)
    return {"flag-worthy": "meets flag rule", "absent": "within limits"}.get(d, d)


def model(o, s):
    d = [x for x in (o, s) if x is not None]
    if "meets flag rule" in d:
        return "flag"
    if len(d) == 2 and all(x == "within limits" for x in d):
        return "pass"
    return "hold"


def rnd(x, nd=4):
    return None if x is None else round(x, nd)


def part1(ver):
    """Tool-call comparisons from the verified check (level 98.75%)."""
    out = {"unchanged_pairs": [], "edits": {}}
    tally = collections.Counter()
    per_model = collections.defaultdict(lambda: collections.Counter())
    for e in ver["item1"]["aa"]["one_answer"]:
        o, s = e["open"], e["specific"]
        first = model(first_set(o), first_set(s))
        assert first == e["decision"], (e["model"], e["a"], e["b"])
        rev = model(revised_set(o, 0.0125), revised_set(s, 0.0125))
        rev25 = model(revised_set(o, 0.025), revised_set(s, 0.025))
        assert rev == e["exact_and_interval_0.0125"]
        out["unchanged_pairs"].append({"model": e["model"], "a": e["a"], "b": e["b"], "first_rule": first,
                                       "revised_0.0125": rev, "revised_0.025": rev25,
                                       "open": {k: rnd(o[k]) for k in ("pairs", "change", "low", "high", "up", "down", "sign_p")},
                                       "specific": {k: rnd(s[k]) for k in ("pairs", "change", "low", "high", "up", "down", "sign_p")}})
        tally[("first rule", first)] += 1
        tally[("revised 0.0125", rev)] += 1
        tally[("revised 0.025", rev25)] += 1
        tally[("open within limits", first_set(o) == "within limits")] += 1
        pm = per_model[e["model"]]
        pm["pairs"] += 1
        pm["first " + first] += 1
        pm["revised " + rev] += 1
        pm["open prefixes"] += o["pairs"]
        pm["open up"] += o["up"]
        pm["open down"] += o["down"]
        pm["specific prefixes"] += s["pairs"]
        pm["specific up"] += s["up"]
        pm["specific down"] += s["down"]
    out["unchanged_tally"] = {f"{a}: {b}": v for (a, b), v in sorted(tally.items(), key=str)}
    out["unchanged_per_model"] = {m: dict(c) for m, c in per_model.items()}
    for name, e in ver["item1"]["edits"].items():
        x = e["0.9875"]
        o, s = x["open"], x["specific"]
        first = model(first_set(o), first_set(s))
        assert first == x["bootstrap"], name
        out["edits"][name] = {
            "first_rule": first,
            "revised_0.0125": model(revised_set(o, 0.0125), revised_set(s, 0.0125)),
            "revised_0.025": model(revised_set(o, 0.025), revised_set(s, 0.025)),
            "open": {k: rnd(o[k]) for k in ("pairs", "change", "low", "high", "up", "down", "sign_p")},
            "specific": {k: rnd(s[k]) for k in ("pairs", "change", "low", "high", "up", "down", "sign_p")}}
    return out


def part2():
    """Form rows of Table 14 with stored sign counts (95% intervals, alpha 0.05)."""
    out = {}
    st = json.loads((EXPLORE / "main/exp0/stage1.json").read_text())["results"]["part3_models"]["read1"]
    for m in st["wrong_values"]:
        sets = []
        for t in ("wrong_values", "correct_values_kept"):
            v = st[t][m]
            sets.append({"pairs": v["n"], "change": 100 * v["mean"], "low": 100 * v["ci95"][0],
                         "high": 100 * v["ci95"][1], "up": v["form_higher"], "down": v["form_lower"],
                         "sign_p": v["sign_p"]})
        o, s = sets
        out[f"held-out full rename, {m}"] = {"first_rule": model(first_set(o), first_set(s)),
                                             "revised_0.05": model(revised_set(o, 0.05), revised_set(s, 0.05)),
                                             "open": {k: rnd(o[k]) for k in o}, "specific": {k: rnd(s[k]) for k in s}}
    a3 = json.loads((EXPLORE / "r10/analysis/out/r2_posthoc.json").read_text())["a3_word_or_meaning"]
    for label, form, m in (("value-only rename", "f2", "haiku"), ("opaque code", "f6", "sonnet"),
                           ("opaque code", "f6", "haiku")):
        sets = []
        for g in ("S1t, brief sets no type", "S2, brief sets hotel"):
            p = a3[g]["models"][m][form]["paired"]
            sets.append({"pairs": p["n"], "change": 100 * p["mean"], "low": 100 * p["ci95"][0],
                         "high": 100 * p["ci95"][1], "up": p["form_higher"], "down": p["form_lower"],
                         "sign_p": p["sign_p"]})
        o, s = sets
        out[f"exploratory {label}, {m}"] = {"first_rule": model(first_set(o), first_set(s)),
                                            "revised_0.05": model(revised_set(o, 0.05), revised_set(s, 0.05)),
                                            "open": {k: rnd(o[k]) for k in o}, "specific": {k: rnd(s[k]) for k in s}}
    out["not checked"] = ("held-out panel rows (full rename, neutral value, description edit, unrelated rename) and "
                          "the held-out neutral value per model: the stored summaries keep no sign counts for them. "
                          "The description edit and the unrelated rename have no flag, so the condition cannot "
                          "change them.")
    return out


def part3(sets):
    """Field order against the repeat, with the shared control (Haiku, the control batch)."""
    ctrl = V.tool_reads(("erc_haiku",), "t0", None)
    tord = V.tool_reads(("erc_haiku",), "tord", None)
    trep = V.tool_reads(("erc2_haiku",), "trep", None)
    out = {}
    for sname in ("open", "specific"):
        ids = [d for d in sets[sname] if ctrl.get(d) and tord.get(d) and trep.get(d)]
        rows = []
        for d in ids:
            c, f, r = V.mean(ctrl[d]), V.mean(tord[d]), V.mean(trep[d])
            rows.append((d, 100 * (f - c), 100 * (r - c)))
        only_f = sum(1 for _, f, r in rows if f != 0 and r == 0)
        only_r = sum(1 for _, f, r in rows if r != 0 and f == 0)
        both = sum(1 for _, f, r in rows if f != 0 and r != 0)
        larger_f = sum(1 for _, f, r in rows if abs(f) > abs(r))
        larger_r = sum(1 for _, f, r in rows if abs(r) > abs(f))
        out[sname] = {"prefixes": len(ids),
                      "field_order_changed": sum(1 for _, f, _ in rows if f != 0),
                      "field_order_up": sum(1 for _, f, _ in rows if f > 0),
                      "field_order_down": sum(1 for _, f, _ in rows if f < 0),
                      "repeat_changed": sum(1 for _, _, r in rows if r != 0),
                      "repeat_up": sum(1 for _, _, r in rows if r > 0),
                      "repeat_down": sum(1 for _, _, r in rows if r < 0),
                      "changed_under_field_order_only": only_f, "changed_under_repeat_only": only_r,
                      "changed_under_both": both, "sign_p_only": sign_p(only_f, only_r),
                      "larger_change_field_order": larger_f, "larger_change_repeat": larger_r,
                      "sign_p_larger": sign_p(larger_f, larger_r)}
    return out


def boot(diffs, level, draws=2000, seed=SEED):
    point, lo, hi = stats.cluster_bootstrap({"all": [(x,) for x in diffs]},
                                            lambda g: sum(t[0] for t in g["all"]) / len(g["all"]),
                                            draws=draws, seed=seed, level=level)
    return {"change": point, "low": lo, "high": hi, "up": sum(x > 0 for x in diffs),
            "down": sum(x < 0 for x in diffs), "sign_p": sign_p(sum(x > 0 for x in diffs), sum(x < 0 for x in diffs))}


def part4(sets, reps=200, sizes=(25, 50, 100, 200)):
    """Share of random open subsets of size n whose open set meets the flag rule (full rename, one answer)."""
    rng = random.Random(MY_SEED)
    out = {}
    for m in ("sonnet", "haiku", "opus", "sol", "astra", "luna"):
        a = V.tool_reads((f"era1_{m}",), "t0", 1)
        b = V.tool_reads((f"era1_{m}",), "t1", 1)
        ids = [d for d in sets["open"] if a.get(d) and b.get(d)]
        diff = {d: 100 * (V.mean(b[d]) - V.mean(a[d])) for d in ids}
        full = boot([diff[d] for d in ids], 0.9875)
        res = {"pairs": len(ids), "full_open_set": {k: rnd(v) for k, v in full.items()}, "by_n": {}}
        for n in sizes:
            c1 = c2 = c3 = 0
            for _ in range(reps):
                sub = rng.sample(ids, n)
                s = boot([diff[d] for d in sub], 0.9875, seed=rng.randrange(10 ** 9))
                c1 += first_set(s) == "meets flag rule"
                c2 += revised_set(s, 0.0125) == "meets flag rule"
                c3 += revised_set(s, 0.025) == "meets flag rule"
            res["by_n"][n] = {"subsets": reps, "first_rule_flag": c1 / reps, "revised_0.0125_flag": c2 / reps,
                              "revised_0.025_flag": c3 / reps}
        out[m] = res
        print("detection", m, res["by_n"], flush=True)
    return out


def md(out):
    L_ = ["## Analysis C.1: the revised flag condition, per-request change, detection (post hoc)",
          "", "Level 98.75% for tool calls (alpha 0.0125); 95% for the form rows (alpha 0.05). L = 5. Revised flag "
          "condition: |change| >= L, the interval excludes zero, and the exact sign test over prefixes gives p <= alpha.",
          "", "### 1. Unchanged tool, one answer per prefix (29 pairs)", ""]
    L_.append("| Model | Pair | Open: change [98.75%], up/down | Specific: change [98.75%], up/down, sign p | First rule | Revised (0.0125) | Revised (0.025) |")
    L_.append("|---|---|---|---|---|---|---|")
    for e in out["part1"]["unchanged_pairs"]:
        o, s = e["open"], e["specific"]
        L_.append(f"| {e['model']} | {e['a']} v {e['b']} | {o['change']:+.1f} [{o['low']:+.1f}, {o['high']:+.1f}], {o['up']}/{o['down']} | "
                  f"{s['change']:+.1f} [{s['low']:+.1f}, {s['high']:+.1f}], {s['up']}/{s['down']}, {s['sign_p']:.4f} | "
                  f"{e['first_rule']} | {e['revised_0.0125']} | {e['revised_0.025']} |")
    L_ += ["", "Tally: " + json.dumps(out["part1"]["unchanged_tally"]), ""]
    L_.append("| Model | Pairs | First rule | Revised (0.0125) | Open prefixes changed (up/down) of pair-prefixes | Specific prefixes changed (up/down) |")
    L_.append("|---|---|---|---|---|---|")
    for m, c in out["part1"]["unchanged_per_model"].items():
        fr = ", ".join(f"{k.split()[1]} {v}" for k, v in sorted(c.items()) if k.startswith("first "))
        rv = ", ".join(f"{k.split()[1]} {v}" for k, v in sorted(c.items()) if k.startswith("revised "))
        L_.append(f"| {m} | {c['pairs']} | {fr} | {rv} | {c['open up'] + c['open down']} of {c['open prefixes']} "
                  f"({c['open up']}/{c['open down']}; {100 * (c['open up'] + c['open down']) / c['open prefixes']:.1f}%) | "
                  f"{c['specific up'] + c['specific down']} of {c['specific prefixes']} ({c['specific up']}/{c['specific down']}) |")
    L_ += ["", "### 2. Edits on the 554 prefixes (tool calls)", ""]
    L_.append("| Edit | Open: change [98.75%], up/down, sign p | Specific: change [98.75%], up/down, sign p | First rule | Revised (0.0125) | Revised (0.025) |")
    L_.append("|---|---|---|---|---|---|")
    for name, e in out["part1"]["edits"].items():
        o, s = e["open"], e["specific"]
        L_.append(f"| {name} | {o['change']:+.1f} [{o['low']:+.1f}, {o['high']:+.1f}], {o['up']}/{o['down']}, {o['sign_p']:.2g} | "
                  f"{s['change']:+.1f} [{s['low']:+.1f}, {s['high']:+.1f}], {s['up']}/{s['down']}, {s['sign_p']:.2g} | "
                  f"{e['first_rule']} | {e['revised_0.0125']} | {e['revised_0.025']} |")
    changed = [n for n, e in out["part1"]["edits"].items() if e["first_rule"] != e["revised_0.0125"]]
    L_ += ["", f"Edit decisions that change at 0.0125: {changed}", "",
           "### 3. Form rows of Table 14 with stored sign counts (95%, alpha 0.05)", ""]
    L_.append("| Row | Open: change [95%], up/down, sign p | Specific: change [95%], up/down, sign p | First rule | Revised (0.05) |")
    L_.append("|---|---|---|---|---|")
    for name, e in out["part2"].items():
        if name == "not checked":
            continue
        o, s = e["open"], e["specific"]
        L_.append(f"| {name} | {o['change']:+.1f} [{o['low']:+.1f}, {o['high']:+.1f}], {o['up']}/{o['down']}, {o['sign_p']:.2g} | "
                  f"{s['change']:+.1f} [{s['low']:+.1f}, {s['high']:+.1f}], {s['up']}/{s['down']}, {s['sign_p']:.2g} | "
                  f"{e['first_rule']} | {e['revised_0.05']} |")
    L_ += ["", "Not checked: " + out["part2"]["not checked"], "",
           "### 4. Field order against the repeat, shared control (Haiku)", "", "```", json.dumps(out["part3"], indent=1),
           "```", "", "### 5. Detection of the full rename against the open-set size (200 random subsets each)", ""]
    L_.append("| Model | Full open set: change [98.75%], up/down | n | First rule: flag | Revised 0.0125: flag | Revised 0.025: flag |")
    L_.append("|---|---|---|---|---|---|")
    for m, res in out["part4"].items():
        f = res["full_open_set"]
        for n, v in res["by_n"].items():
            L_.append(f"| {m} | {f['change']:+.1f} [{f['low']:+.1f}, {f['high']:+.1f}], {f['up']}/{f['down']} ({res['pairs']}) | {n} | "
                      f"{100 * v['first_rule_flag']:.1f}% | {100 * v['revised_0.0125_flag']:.1f}% | {100 * v['revised_0.025_flag']:.1f}% |")
    return "\n".join(L_) + "\n"


def main():
    ver = json.loads((HERE / "out" / "rtest_check_values.json").read_text())
    data, g = runs.context()
    sets = ra.request_sets(data, g)
    out = {"post_hoc": True, "exploratory": True, "level_tool_calls": 0.9875, "L": L,
           "revised_condition": "|change| >= L, interval excludes zero, exact two-sided sign test p <= alpha"}
    out["part1"] = part1(ver)
    out["part2"] = part2()
    out["part3"] = part3(sets)
    out["part4"] = part4(sets)
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "rtest_c1.json").write_text(json.dumps(out, indent=1))
    (HERE / "out" / "rtest_c1.md").write_text(md(out))
    print("wrote", HERE / "out" / "rtest_c1.json")


if __name__ == "__main__":
    main()
