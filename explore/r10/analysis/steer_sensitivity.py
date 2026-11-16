"""Sensitivity of the steering decisions (amendment R10-14) to the bootstrap. Post hoc; no model call.

steer_analyze.py applies the release rule of R10-6 to the hotel value: a percentile cluster bootstrap over prefixes,
2,000 draws, seed 20261112, level 98.75%. At this level each tail holds only about 12 of the 2,000 draws. This script
recomputes the intervals of the two decision sets with 20,000 draws (the same seed, then ten other seeds), as
release_sensitivity.py does for the forward release test, applies the decision rule of Appendix I unchanged, and says
whether a decision changes. steer_analyze.py and its outputs do not change.

Inputs: the reads of steer_analyze.load (stored answers only). Outputs: out/steer_sensitivity.md and .json.
Usage (from explore/): .venv/bin/python -I r10/analysis/steer_sensitivity.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import release_analyze as ra  # noqa: E402  (its imports set the paths; its main() does not run)
import stats  # noqa: E402
import steer  # noqa: E402
import steer_analyze as sa  # noqa: E402

DRAWS = 20_000
SEEDS = [sa.SEED] + [sa.SEED + k for k in range(1, 11)]
DECISION_SETS = ("open", "specific")


def diffs(reads, ids, cell):
    out = []
    for d in ids:
        a, b = sa.scores(reads, d, "t0", "hotel"), sa.scores(reads, d, cell, "hotel")
        if a and b:
            out.append(100 * (sa.mean(b) - sa.mean(a)))
    return out


def interval(xs, draws, seed):
    return stats.cluster_bootstrap({"all": [(x,) for x in xs]}, lambda g: sa.mean([r[0] for r in g["all"]]),
                                   draws=draws, seed=seed, level=sa.LEVEL)


def main():
    data, g = ra.runs.context()
    sets = ra.request_sets(data, g)
    cells = tuple(steer.CELL[d] for d in steer.directions())
    out = {"post_hoc": True, "no_model_call": True, "level": sa.LEVEL, "L": ra.L, "draws": DRAWS,
           "registered_draws": sa.DRAWS, "seeds": SEEDS, "agents": {}}
    for agent in sa.SOURCES:
        reads, _, missing = sa.load(agent, False)
        if missing:
            continue
        per_cell = {}
        for cell in cells:
            res, per_seed = {}, {}
            for s in DECISION_SETS:
                xs = diffs(reads, sets[s], cell)
                base, wide = interval(xs, sa.DRAWS, sa.SEED), interval(xs, DRAWS, sa.SEED)
                per_seed[s] = [interval(xs, DRAWS, sd) for sd in SEEDS]
                res[s] = {"pairs": len(xs),
                          "registered": {"change": base[0], "interval": [base[1], base[2]],
                                         "decision": ra.decide(*base, ra.L)},
                          "draws_20000": {"change": wide[0], "interval": [wide[1], wide[2]],
                                          "decision": ra.decide(*wide, ra.L)},
                          "seeds_20000": {"low_range": [min(r[1] for r in per_seed[s]), max(r[1] for r in per_seed[s])],
                                          "high_range": [min(r[2] for r in per_seed[s]),
                                                         max(r[2] for r in per_seed[s])],
                                          "decisions": sorted({ra.decide(*r, ra.L) for r in per_seed[s]})}}
            tup = lambda e: (e["change"], *e["interval"])  # noqa: E731
            res["release"] = {k: ra.release(tup(res["open"][k]), tup(res["specific"][k]), ra.L, ra.N_MAX, ra.N_MAX)
                              for k in ("registered", "draws_20000")}
            res["release"]["seeds_20000"] = sorted({ra.release(o, sp, ra.L, ra.N_MAX, ra.N_MAX)
                                                    for o, sp in zip(per_seed["open"], per_seed["specific"])})
            per_cell[cell] = res
        out["agents"][agent] = per_cell
    (ra.OUT / "steer_sensitivity.json").write_text(json.dumps(out, indent=1))
    f = lambda x: f"{x:+.2f}"  # noqa: E731
    lines = ["## Steering decisions: sensitivity to the bootstrap (post hoc)", "",
             f"No model call. Level {100 * sa.LEVEL:.2f}%, L = {ra.L}, hotel value. Registered: {sa.DRAWS} draws, seed "
             f"{sa.SEED}. Check: {DRAWS} draws, seed {sa.SEED}, then {len(SEEDS)} seeds ({SEEDS[0]} to {SEEDS[-1]}). "
             "The rule of Appendix I decides, unchanged.", "",
             "| Agent | Cell | Set | Pairs | Change | 2,000 draws | Decision | 20,000 draws | Decision | "
             "Ends over seeds (low; high) | Decisions over seeds |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for agent, per_cell in out["agents"].items():
        for cell, res in per_cell.items():
            for s in DECISION_SETS:
                e = res[s]
                r, t, sd = e["registered"], e["draws_20000"], e["seeds_20000"]
                lines.append(f"| {agent} | {cell} | {s} | {e['pairs']} | {f(r['change'])} | [{f(r['interval'][0])}, "
                             f"{f(r['interval'][1])}] | {r['decision']} | [{f(t['interval'][0])}, {f(t['interval'][1])}] "
                             f"| {t['decision']} | {f(sd['low_range'][0])} to {f(sd['low_range'][1])}; "
                             f"{f(sd['high_range'][0])} to {f(sd['high_range'][1])} | {', '.join(sd['decisions'])} |")
    lines.append("")
    for agent, per_cell in out["agents"].items():
        for cell, res in per_cell.items():
            rel = res["release"]
            lines.append(f"- {agent} {cell}: model decision {rel['registered']} (2,000 draws), {rel['draws_20000']} "
                         f"(20,000 draws), {', '.join(rel['seeds_20000'])} (each of the seeds).")
    (ra.OUT / "steer_sensitivity.md").write_text("\n".join(lines) + "\n")
    print((ra.OUT / "steer_sensitivity.md").read_text())


if __name__ == "__main__":
    main()
