"""T1 (SPEC-T1-rule-comparison.md): the release rules compared on the same simulated datasets.

Post hoc tabulation of the existing exploratory simulation (posthoc/release-sim, amendment R10-26). Reads only
posthoc/release-sim/out/sim.json; runs no simulation and fits nothing. In sim.json every rule of one trial was
applied to the same simulated data and the same bootstrap draws.

Usage: python3 -I t1_compare.py      -> out/t1_compare.json, out/t1_compare.md
"""
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SIM = HERE.parents[1] / "release-sim" / "out" / "sim.json"
OUT = HERE / "out"
RULES = ("original", "revised", "final", "strat_nosign", "pooled")
NAMES = {"original": "Original", "revised": "Revised", "final": "Final", "strat_nosign": "Final without sign",
         "pooled": "Pooled"}
PROFILES = ("haiku", "deepseek", "sol")
L = 5.0
Z = 1.959964

SCENARIOS = [  # (key, label, {profile: configuration id})
    ("zero", "Zero change", {p: f"A-both|{p}|no change|n59m10" for p in PROFILES}),
    ("broad6", "Shift of +6 in both sets", {p: f"A-both|{p}|shift +6 both|n59m10" for p in PROFILES}),
    ("spec6", "Shift of +6 in the specific set only", {p: f"B-spec|{p}|shift +6 specific|n59m10" for p in PROFILES}),
    ("sparse8", "Sparse change on 6 specific requests (mean 8 points)",
     {"haiku": "S-sparse|haiku|sparse +8 specific|n59m10", "deepseek": "S-sparse|deepseek|sparse +8 specific|n59m10",
      "sol": "S-sparse|sol|sparse -8 specific|n59m10"}),
    ("cancel_spec", "Cancelling changes, specific set (up to 12 down, 12 up)",
     {p: f"X-cancel|{p}|cancel 12 down 12 up specific|n59m10" for p in PROFILES}),
    ("cancel_open", "Cancelling changes, open set (10 down, 10 up)",
     {p: f"X-cancel|{p}|cancel 10 down 10 up open|n59m10" for p in PROFILES}),
    ("drift3", "Drift of +3 on the new answers, no schema effect",
     {p: f"Z-drift|{p}|no effect, drift +3|n59m10" for p in PROFILES}),
    ("drift_m3_shift6", "Drift of -3 on the new answers, true shift of +6 in both sets",
     {p: f"Z-drift|{p}|shift +6 both, drift -3|n59m10" for p in PROFILES}),
    ("zero_m1", "Zero change, 1 answer per specific request",
     {p: f"N-size|{p}|no change|n59m1" for p in ("haiku", "deepseek")}),
]


def wilson(k, n, z=Z):
    if n == 0:
        return [None, None]
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def load():
    sim = json.loads(SIM.read_text())
    return sim, {s["id"]: s for s in sim["summaries"]}


def cell(summary, c, rule):
    """{flag, pass, hold: {k, n, share, ci95}} with a check against the stored Wilson interval and raw tallies."""
    d = summary["levels"][str(c)]["decisions"][rule]
    out = {}
    n = d["flag"]["n"]
    assert sum(d[x]["k"] for x in ("flag", "pass", "hold")) == n, (summary["id"], rule)
    for x in ("flag", "pass", "hold"):
        k = d[x]["k"]
        w = wilson(k, n)
        assert all(abs(a - b) < 1e-12 for a, b in zip(w, d[x]["ci95"])), (summary["id"], rule, x)
        out[x] = {"k": k, "n": n, "share": k / n, "ci95": w}
    return out


def beyond_margin(by_id, c):
    """Wrong passes over the paper-design configurations without drift whose true change exceeds L in a set."""
    rows = [s for s in by_id.values() if s["group"] in ("A-both", "B-spec", "S-sparse") and s["design"]["m_spec"] == 10
            and s["design"]["n_spec"] == 59 and s["drift"] == 0 and max(abs(v) for v in s["truth"].values()) > L]
    out = {"configurations": sorted(s["id"] for s in rows)}
    for rule in RULES:
        k = sum(s["levels"][str(c)]["decisions"][rule]["pass"]["k"] for s in rows)
        n = sum(s["levels"][str(c)]["decisions"][rule]["pass"]["n"] for s in rows)
        top = max(rows, key=lambda s: (s["levels"][str(c)]["decisions"][rule]["pass"]["k"], s["id"]))
        tk = top["levels"][str(c)]["decisions"][rule]["pass"]["k"]
        tn = top["levels"][str(c)]["decisions"][rule]["pass"]["n"]
        out[rule] = {"wrong_passes": k, "trials": n, "share": k / n, "ci95": wilson(k, n),
                     "largest": {"id": top["id"], "k": tk, "n": tn, "share": tk / tn, "ci95": wilson(tk, tn)}}
    return out


def build():
    sim, by_id = load()
    out = {"what": "T1: the release rules on the same simulated datasets (post hoc tabulation of R10-26)",
           "source": str(SIM.relative_to(HERE.parents[2])), "trials": sim["trials"], "draws": sim["draws"],
           "levels": {}}
    for c in (4, 10):
        lv = {"level": 1 - 0.05 / c, "scenarios": [], "beyond_margin": beyond_margin(by_id, c)}
        for key, label, ids in SCENARIOS:
            rows = {}
            for p, cid in ids.items():
                s = by_id[cid]
                rows[p] = {"id": cid, "truth": s["truth"], "mean_changed_requests": s["mean_changed_requests"],
                           "redraws": s["redraws"], "rules": {r: cell(s, c, r) for r in RULES}}
            ranges = {r: {x: [min(rows[p]["rules"][r][x]["share"] for p in rows),
                              max(rows[p]["rules"][r][x]["share"] for p in rows)] for x in ("flag", "pass", "hold")}
                      for r in RULES}
            lv["scenarios"].append({"key": key, "label": label, "profiles": rows, "ranges_across_profiles": ranges})
        out["levels"][str(c)] = lv
    return out


def pc(x):
    return f"{100 * x:.1f}"


def rng(a):
    lo, hi = a
    return pc(lo) if pc(lo) == pc(hi) else f"{pc(lo)}–{pc(hi)}"


def markdown(out):
    lines = ["# T1: the release rules on the same simulated datasets", "",
             "Post hoc tabulation of the existing simulation (R10-26; `posthoc/release-sim/out/sim.json`). "
             f"{out['trials']:,} trials per configuration; every rule of one trial uses the same simulated data and the "
             "same bootstrap draws. Shares in percent; brackets: Wilson 95% interval of the simulation uncertainty. "
             "Paper design: 448 open requests × 1 answer, 59 specific requests × 10 answers, unless stated. L = 5.", ""]
    for c, lv in out["levels"].items():
        lines += [f"## C = {c} (level {100 * lv['level']:.2f}%; pooled {100 * (1 - 0.05 / (int(c) / 2)):.2f}%)", ""]
        lines += ["### Ranges across profiles (not intervals; the ends can come from different profiles)", "",
                  "| Scenario | " + " | ".join(f"{NAMES[r]} F / P / H" for r in RULES) + " |",
                  "|---|" + "---|" * len(RULES)]
        for sc in lv["scenarios"]:
            g = sc["ranges_across_profiles"]
            lines.append(f"| {sc['label']} | " + " | ".join(
                " / ".join(rng(g[r][x]) for x in ("flag", "pass", "hold")) for r in RULES) + " |")
        lines += ["", "### Every scenario and profile", "",
                  "| Scenario | Profile | Rule | Flag % [95%] | Pass % [95%] | Hold % [95%] | k flag / pass / hold of n |",
                  "|---|---|---|---|---|---|---|"]
        for sc in lv["scenarios"]:
            for p, row in sc["profiles"].items():
                for r in RULES:
                    e = row["rules"][r]
                    cells = [f"{pc(e[x]['share'])} [{pc(e[x]['ci95'][0])}, {pc(e[x]['ci95'][1])}]"
                             for x in ("flag", "pass", "hold")]
                    lines.append(f"| {sc['label']} | {p} | {NAMES[r]} | " + " | ".join(cells) +
                                 f" | {e['flag']['k']} / {e['pass']['k']} / {e['hold']['k']} of {e['flag']['n']} |")
        bm = lv["beyond_margin"]
        lines += ["", "### Change beyond the margin: wrong passes", "",
                  f"Configurations ({len(bm['configurations'])}): " + ", ".join(f"`{x}`" for x in bm["configurations"]), "",
                  "| Rule | Wrong passes / trials | Share % [95%] | Largest configuration share % [95%] |",
                  "|---|---|---|---|"]
        for r in RULES:
            e = bm[r]
            t = e["largest"]
            lines.append(f"| {NAMES[r]} | {e['wrong_passes']} / {e['trials']} | {pc(e['share'])} "
                         f"[{pc(e['ci95'][0])}, {pc(e['ci95'][1])}] | {pc(t['share'])} [{pc(t['ci95'][0])}, "
                         f"{pc(t['ci95'][1])}] (`{t['id']}`, {t['k']} of {t['n']}) |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    out = build()
    OUT.mkdir(exist_ok=True)
    (OUT / "t1_compare.json").write_text(json.dumps(out, indent=1))
    (OUT / "t1_compare.md").write_text(markdown(out))
    print(f"wrote {OUT / 't1_compare.md'}")


if __name__ == "__main__":
    main()
