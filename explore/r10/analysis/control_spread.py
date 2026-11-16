"""Post hoc description of the two control updates of amendment R10-16: the spread of the per-prefix changes.

No model call. Reads the stored answers of erc_haiku and erc2_haiku with the readers of control_analyze.py and
release_analyze.py, without change. For each update and set: the per-prefix change (update minus control, mean of the
valid reads of each arm, in points), its standard deviation over prefixes, the number of prefixes that rise, fall or
stay, and the largest rises and falls. No decision and no prediction.
Usage (from explore/): .venv/bin/python -I r10/analysis/control_spread.py
Outputs: r10/analysis/out/control_spread.md and control_spread.json.
"""
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import control_analyze as ca  # noqa: E402  (it adds the other paths)
import release_analyze as ra  # noqa: E402
import runs  # noqa: E402

OUT = ca.OUT


def per_prefix(reads, ids):
    """{prefix: (change in points, (control hits, control valid reads), (update hits, update valid reads))}."""
    out = {}
    for d in ids:
        a, b = ra.valid_scores(reads, d, "t0"), ra.valid_scores(reads, d, "tedit")
        if a and b:
            out[d] = (100 * (ra.mean(b) - ra.mean(a)), (sum(a), len(a)), (sum(b), len(b)))
    return out


def describe(rows):
    xs = [r[0] for r in rows.values()]
    order = sorted(rows.items(), key=lambda kv: kv[1][0])
    return {"pairs": len(xs), "mean": ra.mean(xs), "sd_sample": statistics.stdev(xs), "sd_population": statistics.pstdev(xs),
            "rise": sum(x > 0 for x in xs), "fall": sum(x < 0 for x in xs), "same": sum(x == 0 for x in xs),
            "abs_30_or_more": sum(abs(x) >= 30 for x in xs),
            "largest_rises": [round(r[0], 1) for _, r in order[::-1][:5]],
            "largest_falls": [round(r[0], 1) for _, r in order[:5]],
            "abs_30_or_more_counts": [{"change": round(r[0], 1), "control": f"{r[1][0]}/{r[1][1]}",
                                       "update": f"{r[2][0]}/{r[2][1]}"} for _, r in order if abs(r[0]) >= 30]}


def main():
    data, g = runs.context()
    sets = ra.request_sets(data, g)
    out = {"amendment": "R10-16", "post_hoc": True, "updates": {}}
    for u, (_, (cf, cc), (uf, uc)) in ca.UPDATES.items():
        reads = ca.reads_of(ca.load_cell(cf, cc, False), ca.load_cell(uf, uc, False))
        out["updates"][u] = {s: describe(per_prefix(reads, sets[s])) for s in ("open", "specific")}
    lines = ["## Control updates: spread of the per-prefix changes (post hoc, amendment R10-16)", "",
             "No model call. Per prefix: update minus control, mean of the valid reads of each arm, in points "
             "(specific set: 10 reads per arm; open set: 1 read per arm). SD: standard deviation over prefixes.", "",
             "| Update | Set | Pairs | Mean | SD (sample) | SD (population) | Rise | Fall | Same | abs >= 30 | "
             "Largest rises | Largest falls |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for u, e in out["updates"].items():
        for s, x in e.items():
            lines.append(f"| {u} | {s} | {x['pairs']} | {x['mean']:+.1f} | {x['sd_sample']:.1f} | "
                         f"{x['sd_population']:.1f} | {x['rise']} | {x['fall']} | {x['same']} | {x['abs_30_or_more']} | "
                         f"{', '.join(f'{v:+.0f}' for v in x['largest_rises'])} | "
                         f"{', '.join(f'{v:+.0f}' for v in x['largest_falls'])} |")
    lines += ["", "Specific set, prefixes whose change is 30 points or more in size (hotel values in the valid reads, "
              "control and update):", ""]
    for u, e in out["updates"].items():
        lines.append(f"- {u}: " + "; ".join(f"{c['change']:+.0f} ({c['control']} to {c['update']})"
                                           for c in e["specific"]["abs_30_or_more_counts"]))
    OUT.mkdir(exist_ok=True)
    (OUT / "control_spread.json").write_text(json.dumps(out, indent=1))
    (OUT / "control_spread.md").write_text("\n".join(lines) + "\n")
    print((OUT / "control_spread.md").read_text())


if __name__ == "__main__":
    main()
