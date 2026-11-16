"""Post hoc sensitivity of the R10-27 final-rule decisions to the bootstrap (added after the R10-27 design, on
request (2026-11-15), before the R10-27 batch answers were analysed; not part of the fixed design or the primary
analysis).

Why: the release-rule simulation (posthoc/release-sim/REPORT.md, section 3.7) found that the 2,000-draw percentile
interval is unstable at high levels. So each final-rule decision of posthoc/release-fresh/analyze.py is recomputed
(1) with 20,000 draws and the primary seed 20261112, and (2) with 2,000 draws and each of 20 other seeds
(20261113 to 20261132). Everything else is the final rule of analyze.py: the same answers, per-request changes, level
1 - 0.05/C, symmetric index k = floor(draws x 0.025 / C), sign condition at 0.05/C, no pass from a zero-width interval.
The bootstrap draws use the random calls of rtest_final9.boot (rng.choices over the per-request changes).

Run after analyze.py, from explore/:
    python3 -I posthoc/release-fresh/sensitivity.py
It reads out/result.json, rebuilds the per-request changes from the fetched raw.jsonl files (analyze.load), writes
out/sensitivity.json and out/sensitivity.md, and appends a labelled post hoc section to out/result.md and a key
"posthoc_bootstrap_sensitivity" to out/result.json. The primary decisions in result.* do not change.
No model call, no network call, no em* folder.
"""
import collections
import importlib.util
import json
import math
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rf_analyze", HERE / "analyze.py")
AN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AN)  # its main does not run on import
T9 = AN.T9
OUT = AN.OUT
PRIMARY_SEED = T9.SEED
OTHER_SEEDS = [PRIMARY_SEED + i for i in range(1, 21)]
MARKER = "## Post hoc: bootstrap sensitivity of the final-rule decisions"


def boot(diffs, lev, draws, seed):
    """rtest_final9.boot with a free number of draws (symmetric index only)."""
    n = len(diffs)
    rng = random.Random(seed)
    vals = sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(draws))
    k = max(1, math.floor((1 - lev) / 2 * draws + 1e-9))
    up, down = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    return {"pairs": n, "change": sum(diffs) / n, "up": up, "down": down, "sign_p": T9.V.sign_p(up, down),
            "symmetric": [vals[k - 1], vals[draws - k]], "k": k}


def final(o, s, lev):
    return T9.model_dec([o, s], "symmetric", 1 - lev, True)


def main():
    import runs
    res = json.loads((OUT / "result.json").read_text())
    data, g = runs.context()
    sel = AN.f27.select(data, g)
    sets = {s: sel[s] for s in AN.SETS}
    run_of = {m: r for r, m in AN.f27.MODEL_OF.items()}
    out = {"status": "post hoc", "primary_seed": PRIMARY_SEED, "other_seeds": OTHER_SEEDS, "rows": []}
    for u, e in res["updates"].items():
        lev, cell = e["level"], e["cell"]
        for m, v in e["models"].items():
            reads = AN.load(run_of[m], False)
            d = {s: AN.diffs(reads, sets[s], AN.f27.CONTROL, cell) for s in AN.SETS}
            prim = {s: boot(d[s], lev, 2000, PRIMARY_SEED) for s in AN.SETS}
            assert final(prim["open"], prim["specific"], lev) == v["decisions"]["final"], (u, m)
            for s in AN.SETS:  # the same interval as the primary analysis
                assert [round(x, 4) for x in prim[s]["symmetric"]] == v["sets"][s]["symmetric"], (u, m, s)
            big = {s: boot(d[s], lev, 20_000, PRIMARY_SEED) for s in AN.SETS}
            per_seed = collections.Counter()
            seed_rows = []
            for sd in OTHER_SEEDS:
                b = {s: boot(d[s], lev, 2000, sd) for s in AN.SETS}
                dec = final(b["open"], b["specific"], lev)
                per_seed[dec] += 1
                seed_rows.append({"seed": sd, "decision": dec,
                                  "intervals": {s: [round(x, 4) for x in b[s]["symmetric"]] for s in AN.SETS}})
            out["rows"].append({
                "update": u, "model": m, "C": e["C"], "level": lev,
                "primary": v["decisions"]["final"],
                "draws_20000": final(big["open"], big["specific"], lev),
                "draws_20000_intervals": {s: [round(x, 4) for x in big[s]["symmetric"]] for s in AN.SETS},
                "other_seeds": {k: per_seed[k] for k in ("flag", "pass", "hold")},
                "other_seed_rows": seed_rows})
    (OUT / "sensitivity.json").write_text(json.dumps(out, indent=1))
    lines = [MARKER, "",
             "Post hoc (added on request after the design was fixed; not part of the primary analysis). "
             "Each final-rule decision recomputed on the same answers with 20,000 draws (seed "
             f"{PRIMARY_SEED}) and with 2,000 draws and each of 20 other seeds ({OTHER_SEEDS[0]} to {OTHER_SEEDS[-1]}). "
             "The primary decision comes first.", "",
             "| Update | Model | Level | Primary (2,000 draws, seed 20261112) | 20,000 draws | 20 other seeds: flag / pass / hold |"
             " 20,000-draw intervals (open; specific) |", "|---|---|---:|---|---|---|---|"]
    for r in out["rows"]:
        o = r["other_seeds"]
        iv = "; ".join(f"[{AN.pts(a)}, {AN.pts(b)}]" for a, b in (r["draws_20000_intervals"][s] for s in AN.SETS))
        lines.append(f"| {r['update']} | {r['model']} | {100 * r['level']:.2f}% | **{r['primary']}** | {r['draws_20000']} | "
                     f"{o['flag']} / {o['pass']} / {o['hold']} | {iv} |")
    text = "\n".join(lines) + "\n"
    (OUT / "sensitivity.md").write_text(text)
    md = (OUT / "result.md").read_text()
    if MARKER in md:
        md = md.split(MARKER)[0].rstrip() + "\n"
    (OUT / "result.md").write_text(md + "\n" + text)
    res["posthoc_bootstrap_sensitivity"] = {k: v for k, v in out.items()}
    (OUT / "result.json").write_text(json.dumps(res, indent=1, default=float))
    print(text)


if __name__ == "__main__":
    main()
