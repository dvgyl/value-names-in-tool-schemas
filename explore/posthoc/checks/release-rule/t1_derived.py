"""T1b (SPEC-T1b-derived-checks.md): derived summaries of the existing simulation behind the T1 sentences.

Post hoc. Reads only posthoc/release-sim/out/sim.json. Usage: python3 -I t1_derived.py -> out/t1_derived.json, .md
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SIM = HERE.parents[1] / "release-sim" / "out" / "sim.json"
OUT = HERE / "out"


def k(s, c, rule, dec):
    return s["levels"][str(c)]["decisions"][rule][dec]["k"]


def paper(s):
    return (s["design"]["n_spec"], s["design"]["m_spec"]) == (59, 10)


def pass_equal(summaries):
    out = {}
    for c in (4, 10):
        out[str(c)] = {
            "final_vs_nosign_differ": [s["id"] for s in summaries if k(s, c, "final", "pass") != k(s, c, "strat_nosign", "pass")],
            "original_vs_revised_differ": [s["id"] for s in summaries if k(s, c, "original", "pass") != k(s, c, "revised", "pass")],
            "configurations": len(summaries)}
    return out


def flag_diff(summaries, groups, c, want_paper=True):
    best = None
    for s in summaries:
        if s["group"] not in groups or paper(s) != want_paper or (want_paper and s["drift"] != 0 and "Z-drift" not in groups):
            continue
        n = s["levels"][str(c)]["decisions"]["final"]["flag"]["n"]
        d = 100 * (k(s, c, "strat_nosign", "flag") - k(s, c, "final", "flag")) / n
        if best is None or d > best[0]:
            best = (d, s["id"])
    return {"largest_points": best[0], "id": best[1]} if best else None


def build(sim):
    S = sim["summaries"]
    by = {s["id"]: s for s in S}
    out = {"pass_equal": pass_equal(S), "flag_diff": {}}
    for c in (4, 10):
        out["flag_diff"][f"shifts A-both and B-spec, paper design, C={c}"] = flag_diff(S, ("A-both", "B-spec"), c)
    for g in ("S-sparse", "X-cancel", "Z-drift"):
        out["flag_diff"][f"{g}, paper design, C=4"] = flag_diff(S, (g,), 4)
    out["flag_diff"]["N-size, other designs, C=4"] = flag_diff(S, ("N-size",), 4, want_paper=False)
    zero = [by[f"A-both|{p}|no change|n59m10"] for p in ("haiku", "deepseek", "sol")]
    out["zero_change_flags_C4"] = {r: sum(k(s, 4, r, "flag") for s in zero) for r in ("final", "strat_nosign", "original")}
    out["zero_change_trials"] = sum(s["trials"] for s in zero)
    m1 = [by[f"N-size|{p}|no change|n59m1"] for p in ("haiku", "deepseek")]
    out["zero_59x1_flag_range_C4"] = {r: [min(k(s, 4, r, "flag") for s in m1) / 2000, max(k(s, 4, r, "flag") for s in m1) / 2000]
                                      for r in ("original", "final", "strat_nosign")}
    d3 = [by[f"Z-drift|{p}|no effect, drift +3|n59m10"] for p in ("haiku", "deepseek", "sol")]
    vals = [k(s, 4, r, "flag") / 2000 for s in d3 for r in ("original", "revised", "final", "strat_nosign")]
    out["drift3_flag_range_C4_four_rules"] = [min(vals), max(vals)]
    return out


def markdown(o):
    lines = ["# T1b: derived checks (post hoc; sim.json only)", ""]
    for c, v in o["pass_equal"].items():
        lines.append(f"- C = {c}: configurations {v['configurations']}; final vs without sign, pass counts differ in "
                     f"{len(v['final_vs_nosign_differ'])}; original vs revised differ in {len(v['original_vs_revised_differ'])}.")
    for key, v in o["flag_diff"].items():
        lines.append(f"- Largest flag-share difference (without sign minus final), {key}: {v['largest_points']:.2f} points (`{v['id']}`).")
    z = o["zero_change_flags_C4"]
    lines.append(f"- Zero change, paper design, C = 4: flags final {z['final']}, without sign {z['strat_nosign']}, original "
                 f"{z['original']}, of {o['zero_change_trials']} trials.")
    for r, v in o["zero_59x1_flag_range_C4"].items():
        lines.append(f"- Zero change, 59 x 1, C = 4, {r}: flag share {100 * v[0]:.2f}% to {100 * v[1]:.2f}%.")
    d = o["drift3_flag_range_C4_four_rules"]
    lines.append(f"- Drift +3, no effect, C = 4, four stratified rules: flag share {100 * d[0]:.2f}% to {100 * d[1]:.2f}%.")
    return "\n".join(lines) + "\n"


def main():
    o = build(json.loads(SIM.read_text()))
    OUT.mkdir(exist_ok=True)
    (OUT / "t1_derived.json").write_text(json.dumps(o, indent=1))
    (OUT / "t1_derived.md").write_text(markdown(o))
    print(markdown(o))


if __name__ == "__main__":
    main()
