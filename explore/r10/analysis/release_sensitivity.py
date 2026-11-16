"""Sensitivity of the forward release test (amendment R10-6) to the bootstrap. Post hoc; no model call.

release_analyze.py fixed the interval before the run: a percentile cluster bootstrap over prefixes, 2,000 draws, seed
20261112, level 98.75%. At this level each tail holds only about 12 of the 2,000 draws. This script recomputes the
intervals of the two decision sets with 20,000 draws (the same seed, then ten other seeds), applies the decision rule
of Appendix I unchanged, and says whether a decision changes. release_analyze.py and its outputs do not change.

It also gives an approximate number of requests that would resolve each unresolved set. Assumption: the estimate stays
the same, and the distance from the estimate to the interval end that crosses L falls with the square root of the
number of requests. Then the set becomes "absent" at about n x (distance / (L - |estimate|))^2 requests.

Inputs: the reads of release_analyze.load (erp_<model>/raw.jsonl, models whose file exists). Outputs:
out/release_sensitivity.md and out/release_sensitivity.json.
Usage (from explore/): .venv/bin/python -I r10/analysis/release_sensitivity.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import release_analyze as ra  # noqa: E402  (its imports set the paths; its main() does not run)
import stats  # noqa: E402

DRAWS = 20_000
SEEDS = [ra.SEED] + [ra.SEED + k for k in range(1, 11)]
DECISION_SETS = ("open", "specific")


def diffs(reads, ids):
    out = []
    for d in ids:
        a, b = ra.valid_scores(reads, d, "t0"), ra.valid_scores(reads, d, "tedit")
        if a and b:
            out.append(100 * (ra.mean(b) - ra.mean(a)))
    return out


def interval(xs, draws, seed):
    return stats.cluster_bootstrap({"all": [(x,) for x in xs]}, lambda g: ra.mean([r[0] for r in g["all"]]),
                                   draws=draws, seed=seed, level=ra.LEVEL)


def needed(change, low, high, n, L):
    """Approximate requests for an unresolved set to become absent (see the module docstring), or None."""
    if abs(change) >= L:
        return None
    side = max(high - change if high > L else 0.0, change - low if low < -L else 0.0)
    if side == 0.0:
        return None
    return n * (side / (L - abs(change))) ** 2


def main():
    data, g = ra.runs.context()
    sets = ra.request_sets(data, g)
    out = {"post_hoc": True, "no_model_call": True, "level": ra.LEVEL, "L": ra.L, "draws": DRAWS,
           "registered_draws": ra.DRAWS, "seeds": SEEDS, "models": {}, "missing": []}
    for m, folder in ra.MODELS.items():
        reads = ra.load(folder, False)
        if reads is None:
            out["missing"].append(folder)
            continue
        res, per_seed = {}, {}
        for s in DECISION_SETS:
            xs = diffs(reads, sets[s])
            base = interval(xs, ra.DRAWS, ra.SEED)
            main_ = interval(xs, DRAWS, ra.SEED)
            per_seed[s] = [interval(xs, DRAWS, sd) for sd in SEEDS]
            res[s] = {"pairs": len(xs),
                      "registered": {"change": base[0], "interval": [base[1], base[2]],
                                     "decision": ra.decide(*base, ra.L)},
                      "draws_20000": {"change": main_[0], "interval": [main_[1], main_[2]],
                                      "decision": ra.decide(*main_, ra.L)},
                      "seeds_20000": {"low_range": [min(r[1] for r in per_seed[s]), max(r[1] for r in per_seed[s])],
                                      "high_range": [min(r[2] for r in per_seed[s]), max(r[2] for r in per_seed[s])],
                                      "decisions": sorted({ra.decide(*r, ra.L) for r in per_seed[s]})},
                      "approx_requests_to_resolve": {
                          "from_registered": needed(*base, len(xs), ra.L),
                          "from_20000": needed(*main_, len(xs), ra.L)}}
        tup = lambda e: (e["change"], *e["interval"])  # noqa: E731
        res["release"] = {k: ra.release(tup(res["open"][k]), tup(res["specific"][k]), ra.L, ra.N_MAX, ra.N_MAX)
                          for k in ("registered", "draws_20000")}
        res["release"]["seeds_20000"] = sorted({ra.release(o, sp, ra.L, ra.N_MAX, ra.N_MAX)
                                                for o, sp in zip(per_seed["open"], per_seed["specific"])})
        out["models"][m] = res
    (ra.OUT / "release_sensitivity.json").write_text(json.dumps(out, indent=1))
    lines = ["## Forward release test: sensitivity to the bootstrap (post hoc)", "",
             f"No model call. Level {100 * ra.LEVEL:.2f}%, L = {ra.L}. Registered: {ra.DRAWS} draws, seed {ra.SEED}. "
             f"Check: {DRAWS} draws, seed {ra.SEED}, then {len(SEEDS)} seeds ({SEEDS[0]} to {SEEDS[-1]}). "
             "The rule of Appendix I decides, unchanged.", ""]
    if out["missing"]:
        lines += [f"Not fetched at this run: {', '.join(out['missing'])}.", ""]
    lines += ["| Model | Set | Pairs | Change | Registered interval | Decision | 20,000 draws | Decision | "
              "Ends over seeds (low; high) | Decisions over seeds | Approx. requests to resolve |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda x: f"{x:+.2f}"  # noqa: E731
    for m, res in out["models"].items():
        for s in DECISION_SETS:
            e = res[s]
            r, t, sd, ap = e["registered"], e["draws_20000"], e["seeds_20000"], e["approx_requests_to_resolve"]
            lines.append(
                f"| {m} | {s} | {e['pairs']} | {f(r['change'])} | [{f(r['interval'][0])}, {f(r['interval'][1])}] | "
                f"{r['decision']} | [{f(t['interval'][0])}, {f(t['interval'][1])}] | {t['decision']} | "
                f"{f(sd['low_range'][0])} to {f(sd['low_range'][1])}; {f(sd['high_range'][0])} to "
                f"{f(sd['high_range'][1])} | {', '.join(sd['decisions'])} | "
                f"{'-' if ap['from_registered'] is None else round(ap['from_registered'])} (registered); "
                f"{'-' if ap['from_20000'] is None else round(ap['from_20000'])} (20,000) |")
        rel = res["release"]
        lines += ["", f"{m}: model decision {rel['registered']} (registered), {rel['draws_20000']} (20,000 draws), "
                      f"{', '.join(rel['seeds_20000'])} (each of the seeds)."]
    (ra.OUT / "release_sensitivity.md").write_text("\n".join(lines) + "\n")
    print((ra.OUT / "release_sensitivity.md").read_text())


if __name__ == "__main__":
    main()
