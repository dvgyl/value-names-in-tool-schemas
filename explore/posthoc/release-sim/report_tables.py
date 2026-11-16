"""Compact tables for REPORT.md, from out/sim.json (amendment R10-26). No new computation; selection only.
Usage: python3 -I report_tables.py  -> out/report_tables.md
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
SIM = json.loads((OUT / "sim.json").read_text())
S = {s["id"]: s for s in SIM["summaries"]}
T = {t["id"]: t for t in SIM["tails"]}
PROFILES = ("haiku", "deepseek", "sol")
RULES = ("original", "revised", "final", "strat_nosign", "pooled")
NAMES = {"original": "Orig.", "revised": "Rev.", "final": "Final", "strat_nosign": "Final w/o sign", "pooled": "Pooled"}


def pc(x):
    return f"{100 * x:.1f}"


def fph(s, C, rule):
    d = s["levels"][str(C)]["decisions"][rule]
    return f"{pc(d['flag']['share'])} / {pc(d['pass']['share'])} / {pc(d['hold']['share'])}"


def ci(sh):
    return f"{pc(sh['share'])} [{pc(sh['ci95'][0])}, {pc(sh['ci95'][1])}]"


def cid(group, prof, label, n=59, m=10):
    return f"{group}|{prof}|{label}|n{n}m{m}"


lines = ["# Compact tables for the report (from out/sim.json)", "",
         "Cells: flag / pass / hold, percent of 2,000 trials. C = 4 (98.75%; pooled 97.5%) unless stated.", ""]

# 1. null configurations
lines += ["## 1. True change 0 in both sets", "", "| Profile | Case | " + " | ".join(NAMES[r] for r in RULES) +
          " | Final, C = 10 |", "|---|---|" + "---|" * (len(RULES) + 1)]
null_cases = [("A-both", "no change"), ("X-cancel", "cancel 2 down 2 up specific"),
              ("X-cancel", "cancel 12 down 12 up specific"), ("X-cancel", "cancel 10 down 10 up open"),
              ("Z-drift", "no effect, drift +2"), ("Z-drift", "no effect, drift +3"), ("Z-drift", "no effect, drift +5")]
for prof in PROFILES:
    for g, lab in null_cases:
        s = S[cid(g, prof, lab)]
        lines.append(f"| {prof} | {lab} | " + " | ".join(fph(s, 4, r) for r in RULES) + f" | {fph(s, 10, 'final')} |")
lines.append("")

# 2. effect curves, paper design
for g, title, deltas in (("A-both", "The same shift in both sets", [-6, -5, 2, 4, 5, 6, 8, 15]),
                         ("B-spec", "Shift in the specific set only", [2, 4, 5, 6, 8, 15]),
                         ("S-sparse", "Sparse change in the specific set only", [4, 6, 8, 15, -4, -6, -8, -15])):
    lines += [f"## 2. {title} (paper design)", "", "| Profile | True change | " + " | ".join(NAMES[r] for r in RULES) +
              " | Final, C = 10 |", "|---|---|" + "---|" * (len(RULES) + 1)]
    for prof in PROFILES:
        for D in deltas:
            lab = {"A-both": f"shift {D:+g} both", "B-spec": f"shift {D:+g} specific",
                   "S-sparse": f"sparse {D:+g} specific"}[g]
            s = S.get(cid(g, prof, lab))
            if s is None:
                continue
            lines.append(f"| {prof} | {D:+g} | " + " | ".join(fph(s, 4, r) for r in RULES) + f" | {fph(s, 10, 'final')} |")
    lines.append("")

# 3. sample size
lines += ["## 3. Sample size and answers per specific request (shift in the specific set only)", "",
          "| Profile | Specific design | True change | Original | Final | Final, C = 10 | Pooled | Final: specific set flag / within / unresolved |",
          "|---|---|---|---|---|---|---|---|"]
for prof in ("haiku", "deepseek"):
    for n, m in ((59, 1), (59, 10), (120, 1), (120, 10), (240, 1), (240, 10)):
        for D in (0, 2, 5, 6, 8):
            lab = "no change" if D == 0 else f"shift {D:+g} specific"
            g = "N-size"
            if (n, m) == (59, 10):
                g = "A-both" if D == 0 else "B-spec"
            s = S[cid(g, prof, lab, n, m)]
            sc = s["levels"]["4"]["set_classes"]["final"]["specific"]
            lines.append(f"| {prof} | {n} x {m} | {D:+g} | {fph(s, 4, 'original')} | {fph(s, 4, 'final')} | "
                         f"{fph(s, 10, 'final')} | {fph(s, 4, 'pooled')} | {pc(sc['flag']['share'])} / "
                         f"{pc(sc['within']['share'])} / {pc(sc['unresolved']['share'])} |")
lines.append("")

# 4. coverage
lines += ["## 4. Coverage of the intervals (smallest over configurations, and in the null configurations)", ""]
for C in (4, 10):
    lines += [f"### C = {C}", "", "| Index | Set | Smallest coverage (configuration) | Smallest in configurations without drift | Mean over configurations without drift |",
              "|---|---|---|---|---|"]
    for index in ("as_run", "symmetric"):
        for st in ("open", "specific", "both"):
            allv = [(s["levels"][str(C)]["coverage"][index][st], s) for s in SIM["summaries"]]
            nod = [(v, s) for v, s in allv if s["drift"] == 0]
            v0, s0 = min(allv, key=lambda z: z[0]["share"])
            v1, s1 = min(nod, key=lambda z: z[0]["share"])
            mean = sum(v["share"] for v, _ in nod) / len(nod)
            lines.append(f"| {index} | {st} | {ci(v0)} ({s0['id']}) | {ci(v1)} ({s1['id']}) | {pc(mean)} |")
    v = [(s["levels"][str(C)]["coverage"]["pooled"], s) for s in SIM["summaries"] if s["drift"] == 0]
    v1, s1 = min(v, key=lambda z: z[0]["share"])
    lines += [f"| pooled | pooled | - | {ci(v1)} ({s1['id']}) | {pc(sum(x['share'] for x, _ in v) / len(v))} |", ""]

# 5. error summary (paper design and all designs)
lines += ["## 5. Error summary over the configurations without drift", "",
          "| C | Rule | Largest false flag | Largest wrong pass | Smallest detection (true change at least L) | Largest set-level false flag |",
          "|---|---|---|---|---|---|"]
for C in (4, 10):
    for r in RULES:
        rows = [s for s in SIM["summaries"] if s["drift"] == 0]

        def ext(kind, key, fn):
            v = [(s["levels"][str(C)]["errors"][r][key], s) for s in rows if s["truth_kind"] in kind
                 and key in s["levels"][str(C)]["errors"][r]]
            if not v:
                return "-"
            x, s = fn(v, key=lambda z: z[0]["share"])
            return f"{ci(x)} ({s['profile']}, {s['label']}, {s['design']['n_spec']} x {s['design']['m_spec']})"
        sff = [(v, s) for s in rows for k, v in s["levels"][str(C)]["errors"][r].items() if k.startswith("set_false")]
        if sff:
            x, s0 = max(sff, key=lambda z: z[0]["share"])
            sffs = f"{ci(x)} ({s0['profile']}, {s0['label']})"
        else:
            sffs = "-"
        lines.append(f"| {C} | {NAMES[r]} | {ext(('null',), 'false_flag', max)} | {ext(('outside',), 'wrong_pass', max)} | "
                     f"{ext(('at', 'outside'), 'detection', min)} | {sffs} |")
lines.append("")

# 6. tails
lines += ["## 6. Tails of the 2,000-draw interval (paper design, 1,000 trials)", "",
          "| C | Profile | Case | Final F/P/H 2,000 | Final F/P/H 20,000 | Changed by seed (final) | Changed by 20,000 draws (final) | Changed by seed (original) | Changed by index (original, 2,000) | Mean end change by seed, open / spec. |",
          "|---|---|---|---|---|---|---|---|---|---|"]
for C in (10, 4):
    for t in SIM["tails"]:
        e = t["levels"][str(C)]
        a, c = e["decisions_2000"]["final"], e["decisions_20000"]["final"]
        em = e["endpoint_mean_abs_change"]
        lines.append(f"| {C} | {t['profile']} | {t['label']} | {pc(a['flag'])} / {pc(a['pass'])} / {pc(a['hold'])} | "
                     f"{pc(c['flag'])} / {pc(c['pass'])} / {pc(c['hold'])} | {ci(e['changed_by_seed']['final'])} | "
                     f"{ci(e['changed_by_draws']['final'])} | {ci(e['changed_by_seed']['original'])} | "
                     f"{ci(e['changed_by_index']['original, 2,000 draws'])} | "
                     f"{em['open symmetric']['other_seed_2000']:.2f} / {em['specific symmetric']['other_seed_2000']:.2f} |")
lines.append("")


# 7. candidate appendix table: ranges over the profiles, C = 4
APPX = [
    ("No change", [("A-both", p, "no change", 59, 10) for p in PROFILES], "0 / 0"),
    ("Shift +2 in both sets", [("A-both", p, "shift +2 both", 59, 10) for p in PROFILES], "+2 / +2"),
    ("Shift +4 in both sets", [("A-both", p, "shift +4 both", 59, 10) for p in PROFILES], "+4 / +4"),
    ("Shift +5 in both sets", [("A-both", p, "shift +5 both", 59, 10) for p in PROFILES], "+5 / +5"),
    ("Shift +6 in both sets", [("A-both", p, "shift +6 both", 59, 10) for p in PROFILES], "+6 / +6"),
    ("Shift +6 in the specific set only", [("B-spec", p, "shift +6 specific", 59, 10) for p in PROFILES], "0 / +6"),
    ("Sparse: 6 specific requests move by about 80 points", [("S-sparse", p, f"sparse {s}8 specific", 59, 10)
                                                         for p, s in (("haiku", "+"), ("deepseek", "+"), ("sol", "-"))], "0 / ±8"),
    ("Cancel: up to 12 specific requests fall, 12 rise", [("X-cancel", p, "cancel 12 down 12 up specific", 59, 10) for p in PROFILES], "0 / 0"),
    ("Cancel: 10 open requests fall, 10 rise", [("X-cancel", p, "cancel 10 down 10 up open", 59, 10) for p in PROFILES], "0 / 0"),
    ("No change, batch drift +3 on the new arm", [("Z-drift", p, "no effect, drift +3", 59, 10) for p in PROFILES], "0 / 0"),
    ("No change, 1 answer per specific request", [("N-size", p, "no change", 59, 1) for p in ("haiku", "deepseek")], "0 / 0"),
    ("Shift +6 in the specific set, 240 requests x 1 answer", [("N-size", p, "shift +6 specific", 240, 1) for p in ("haiku", "deepseek")], "0 / +6"),
]


def rng_(vals):
    lo, hi = min(vals), max(vals)
    return pc(lo) if abs(lo - hi) < 5e-4 else f"{pc(lo)}-{pc(hi)}"


lines += ["## 7. Candidate appendix table (C = 4, level 98.75%; pooled 97.5%; ranges over the profiles)", "",
          "| Case | True change open / specific | Flag, original | Flag, final | Pass, final | Hold, final | Pass, pooled |",
          "|---|---|---|---|---|---|---|"]
for name, keys, tr in APPX:
    ss = [S[cid(g, p, lab, n, m)] for g, p, lab, n, m in keys]
    dd = lambda s, r, x: s["levels"]["4"]["decisions"][r][x]["share"]  # noqa: E731
    lines.append(f"| {name} | {tr} | {rng_([dd(s, 'original', 'flag') for s in ss])} | {rng_([dd(s, 'final', 'flag') for s in ss])} | "
                 f"{rng_([dd(s, 'final', 'pass') for s in ss])} | {rng_([dd(s, 'final', 'hold') for s in ss])} | "
                 f"{rng_([dd(s, 'pooled', 'pass') for s in ss])} |")
lines.append("")
lines += ["Profiles in each row: " + "; ".join(f"{name}: {', '.join(k[1] for k in keys)}" for name, keys, _ in APPX), ""]

(OUT / "report_tables.md").write_text("\n".join(lines) + "\n")
print((OUT / "report_tables.md").read_text())
