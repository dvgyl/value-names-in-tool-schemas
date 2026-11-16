"""T3 (SPEC-T3-bootstrap-precision.md), step 2: every actual release decision with 100,000 bootstrap draws and the
five seeds fixed in the spec. Post hoc numerical sensitivity; the 2,000-draw decisions stay primary.

Input: out/t3_diffs.json (t3_collect.py). Also reads the stored 20,000-draw decisions (posthoc/release-sim/out/
tails_stored.json, posthoc/release-fresh/out/sensitivity.json); computes no new 20,000-draw value.
Usage: python3 -I t3_boot.py [--workers 8]      -> out/t3_bootstrap.json, out/t3_bootstrap.md
"""
import concurrent.futures as cf
import json
import os
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parents[1]
sys.path.insert(0, str(W / "release-sim"))
import rules  # noqa: E402

OUT = HERE / "out"
SEEDS = (20271101, 20271102, 20271103, 20271104, 20271105)
B = 100_000
PRIMARY = (20261112, 2000)
SETS = ("open", "specific")
L = rules.L


def boot_sorted(diffs, seed, draws):
    """The frozen bootstrap: random.Random(seed), `draws` means of rng.choices over the requests, sorted."""
    n = len(diffs)
    rng = random.Random(seed)
    return sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(draws))


def needed_ends(comp):
    """(rule, level) pairs of a comparison -> the (index, level) endpoints to read."""
    return sorted({(rules.RULES[r][0], v["level"]) for r, v in comp["rules"].items()})


def task(args):
    key, s, diffs, seed, draws, ends = args
    vals = boot_sorted(diffs, seed, draws)
    return key, s, seed, draws, {f"{ix}|{lev!r}": list(rules.endpoints(vals, lev, ix)) for ix, lev in ends}


def classes_and_decision(comp, rule, ends_by_set):
    """rules.decide_sets with given interval ends (the same logic)."""
    index, use_sign, guard = rules.RULES[rule]
    lev = comp["rules"][rule]["level"]
    alpha = 1 - lev
    cls = []
    for s in SETS:
        d = comp["sets"][s]
        change, up, down = sum(d) / len(d), sum(x > 0 for x in d), sum(x < 0 for x in d)
        ok = (rules.sign_p(up, down) <= alpha) if use_sign else True
        lo, hi = ends_by_set[s]
        cls.append(rules.set_class(change, lo, hi, ok, guard))
    return rules.model_decision(cls), cls


def set_facts(comp, rule):
    index, use_sign, guard = rules.RULES[rule]
    alpha = 1 - comp["rules"][rule]["level"]
    out = {}
    for s in SETS:
        d = comp["sets"][s]
        change, up, down = sum(d) / len(d), sum(x > 0 for x in d), sum(x < 0 for x in d)
        p = rules.sign_p(up, down)
        out[s] = {"change": change, "up": up, "down": down, "sign_p": p,
                  "eligible": abs(change) >= L and ((p <= alpha) if use_sign else True), "guard": guard}
    return out


def boundary(comp, rule, runs):
    """runs: list of {"ends": {set: (lo, hi)}, "decision", "classes"} over the six computations (primary first).
    Returns (boundary label, set, distance in points, changed?)."""
    facts = set_facts(comp, rule)
    decs = [r["decision"] for r in runs]
    if len(set(decs)) > 1:  # which crossing changes the decision
        labels = []
        for i, s in enumerate(SETS):
            cl = {r["classes"][i] for r in runs}
            if len(cl) == 1:
                continue
            los = [r["ends"][s][0] for r in runs]
            his = [r["ends"][s][1] for r in runs]
            if rules.FLAG in cl:
                labels.append(("0", s))
            if min(los) < -L <= max(los):
                labels.append(("-L", s))
            if min(his) <= L < max(his):
                labels.append(("+L", s))
            if facts[s]["guard"] and any(r["ends"][s][0] == r["ends"][s][1] for r in runs):
                labels.append(("zero width", s))
        return {"changed": True, "crossings": labels}
    dec = decs[0]
    if dec == "pass":
        best = None
        for s in SETS:
            for r in runs:
                lo, hi = r["ends"][s]
                for lab, dist in (("-L", lo + L), ("+L", L - hi)):
                    if best is None or dist < best[2]:
                        best = (lab, s, dist)
        return {"changed": False, "boundary": best[0], "set": best[1], "distance": best[2]}
    if dec == "flag":
        best = None  # the most robust flagging set: the flag survives while any set keeps it
        for s in SETS:
            if not facts[s]["eligible"]:
                continue
            ch = facts[s]["change"]
            d = min((r["ends"][s][0] if ch > 0 else -r["ends"][s][1]) for r in runs)
            if d > 0 and (best is None or d > best[2]):
                best = ("0", s, d)
        return {"changed": False, "boundary": best[0], "set": best[1], "distance": best[2]}
    # hold: nearest change to a flag (an eligible set's interval excludes 0) or to a pass (every set within limits)
    cands = []
    for s in SETS:
        if facts[s]["eligible"]:
            ch = facts[s]["change"]
            d = min(-(r["ends"][s][0] if ch > 0 else -r["ends"][s][1]) for r in runs)
            cands.append(("0", s, d))
    to_pass = []
    for r in runs:
        worst = None
        for s in SETS:
            lo, hi = r["ends"][s]
            if facts[s]["guard"] and lo == hi:
                worst = ("zero width", s, float("inf"))
                break
            for lab, ex in (("-L", -L - lo), ("+L", hi - L)):
                if worst is None or ex > worst[2]:
                    worst = (lab, s, ex)
        to_pass.append(worst)
    tp = min(to_pass, key=lambda x: x[2])
    cands.append(tp)
    best = min(cands, key=lambda x: x[2])
    return {"changed": False, "boundary": best[0], "set": best[1], "distance": best[2]}


def twenty_thousand():
    out = {}
    tails = json.loads((W / "release-sim" / "out" / "tails_stored.json").read_text())["rows"]
    for r in tails:
        out[("stored", r["name"])] = r["base"]
    sens = json.loads((W / "release-fresh" / "out" / "sensitivity.json").read_text())["rows"]
    for r in sens:
        out[("fresh", f"R10-27 {r['update']} {r['model']}")] = {"final": r["draws_20000"]}
    return out


def d20000(comp, rule, table):
    name = comp["source_name"]
    if comp["group"] == "fresh test":
        e = table.get(("fresh", name))
        return None if e is None or rule != "final" else e["final"]
    e = table.get(("stored", name))
    if e is None:
        return None
    lv = "final" if rule == "final" else "run"
    return e.get(f"{lv}|{rule}|20000")


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else (os.cpu_count() or 4)
    comps = json.loads((OUT / "t3_diffs.json").read_text())["comparisons"]
    tasks = []
    for c in comps:
        ends = needed_ends(c)
        for s in SETS:
            for seed, draws in [PRIMARY] + [(sd, B) for sd in SEEDS]:
                tasks.append((c["key"], s, c["sets"][s], seed, draws, ends))
    tasks.sort(key=lambda t: -len(t[2]) * t[4])
    t0 = time.time()
    got = {}
    with cf.ProcessPoolExecutor(max_workers=workers) as ex:
        for i, (key, s, seed, draws, ends) in enumerate(ex.map(task, tasks, chunksize=1)):
            got[(key, s, seed, draws)] = ends
            if i % 50 == 0:
                print(f"{i}/{len(tasks)} tasks, {time.time() - t0:.0f} s", flush=True)
    t20 = twenty_thousand()
    rows = []
    for c in comps:
        for rule, rv in c["rules"].items():
            lev = rv["level"]
            ix = rules.RULES[rule][0]
            runs = []
            for seed, draws in [PRIMARY] + [(sd, B) for sd in SEEDS]:
                ends = {s: tuple(got[(c["key"], s, seed, draws)][f"{ix}|{lev!r}"]) for s in SETS}
                dec, cls = classes_and_decision(c, rule, ends)
                runs.append({"seed": seed, "draws": draws, "ends": ends, "decision": dec, "classes": cls})
            facts = set_facts(c, rule)
            rows.append({
                "key": c["key"], "group": c["group"], "table": c["table"], "label": c["label"], "rule": rule,
                "level": lev, "index": ix, "pairs": c["pairs"],
                "change": {s: facts[s]["change"] for s in SETS},
                "up_down": {s: [facts[s]["up"], facts[s]["down"]] for s in SETS},
                "sign_p": {s: facts[s]["sign_p"] for s in SETS},
                "decision_2000": runs[0]["decision"], "intervals_2000": runs[0]["ends"],
                "decision_20000_stored": d20000(c, rule, t20),
                "decisions_100000": [r["decision"] for r in runs[1:]],
                "ends_100000": [r["ends"] for r in runs[1:]],
                "end_range_100000": {s: {"low": [min(r["ends"][s][0] for r in runs[1:]), max(r["ends"][s][0] for r in runs[1:])],
                                         "high": [min(r["ends"][s][1] for r in runs[1:]), max(r["ends"][s][1] for r in runs[1:])]}
                                     for s in SETS},
                "boundary": boundary(c, rule, runs),
                "changed_vs_2000": any(r["decision"] != runs[0]["decision"] for r in runs[1:]),
                "seeds_disagree": len({r["decision"] for r in runs[1:]}) > 1})
    out = {"what": "T3: every actual release decision with 100,000 draws and five fixed seeds (post hoc)",
           "seeds": SEEDS, "draws": B, "primary": {"seed": PRIMARY[0], "draws": PRIMARY[1]},
           "seconds": time.time() - t0, "workers": workers, "rows": rows}
    OUT.mkdir(exist_ok=True)
    (OUT / "t3_bootstrap.json").write_text(json.dumps(out, indent=1))
    (OUT / "t3_bootstrap.md").write_text(markdown(out))
    print(markdown(out)[:6000])


def f2(x):
    return f"{x:+.2f}".replace("-", "−")


def markdown(out):
    rows = out["rows"]
    ch = [r for r in rows if r["changed_vs_2000"] or r["seeds_disagree"]]
    stable = [r for r in rows if not (r["changed_vs_2000"] or r["seeds_disagree"])]
    lines = ["# T3: every actual release decision with 100,000 draws (post hoc numerical sensitivity)", "",
             f"Seeds {', '.join(map(str, out['seeds']))}; {out['draws']:,} draws each. Primary: 2,000 draws, seed "
             f"{out['primary']['seed']} (the paper). Same answers, pairing, averaging, validity rule, L, C, index "
             "convention and decision order. Rule-decisions: "
             f"{len(rows)} in {len({r['key'] for r in rows})} comparisons. Run time {out['seconds']:.0f} s with "
             f"{out['workers']} workers.", "",
             f"- Rule-decisions whose 100,000-draw decision differs from the 2,000-draw decision for at least one seed, "
             f"or whose five seeds disagree: **{len(ch)}**.",
             f"- Rule-decisions with the same decision under the 2,000-draw primary and all five seeds: **{len(stable)}**.", ""]
    if stable:
        m = min(stable, key=lambda r: r["boundary"]["distance"])
        lines.append(f"- Smallest distance to a responsible boundary among the stable ones: {m['boundary']['distance']:.3f} "
                     f"points ({m['label']}, {m['rule']} rule, {m['boundary']['boundary']} on the {m['boundary']['set']} set).")
    lines += ["", "## Decisions that change or whose seeds disagree", "",
              "| Comparison | Rule (level) | 2,000 draws | 20,000 (stored) | 100,000: five seeds | Deciding set: 2,000-draw interval; 100,000-draw end range | Boundary |",
              "|---|---|---|---|---|---|---|"]
    for r in ch:
        b = r["boundary"]
        sets_x = sorted({s for _, s in b.get("crossings", [])}) or ["open", "specific"]
        cells = []
        for s in sets_x:
            lo, hi = r["intervals_2000"][s]
            er = r["end_range_100000"][s]
            cells.append(f"{s}: [{f2(lo)}, {f2(hi)}]; low {f2(er['low'][0])} to {f2(er['low'][1])}, high {f2(er['high'][0])} to {f2(er['high'][1])}")
        lines.append(f"| {r['label']} | {r['rule']} ({100 * r['level']:.2f}%) | {r['decision_2000']} | "
                     f"{r['decision_20000_stored'] or '-'} | {', '.join(r['decisions_100000'])} | {'; '.join(cells)} | "
                     f"{', '.join(f'{a} ({s})' for a, s in b.get('crossings', [])) or '-'} |")
    lines += ["", "## Every rule-decision", "",
              "| Group | Comparison | Rule (level) | Change open / specific | 2,000 | 20,000 (stored) | 100,000 (5 seeds) | Boundary (set): smallest distance |",
              "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        b = r["boundary"]
        bd = (", ".join(f"{a} ({s})" for a, s in b["crossings"]) + " (changes)") if b["changed"] else \
            f"{b['boundary']} ({b['set']}): {b['distance']:.2f}"
        lines.append(f"| {r['group']} | {r['label']} | {r['rule']} ({100 * r['level']:.2f}%) | "
                     f"{f2(r['change']['open'])} / {f2(r['change']['specific'])} | {r['decision_2000']} | "
                     f"{r['decision_20000_stored'] or '-'} | {', '.join(r['decisions_100000'])} | {bd} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
