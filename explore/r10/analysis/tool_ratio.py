"""Tool calls at the first request: the renamed-to-original filter-rate ratio, by brief. Post hoc, no model call.

It reads only the stored tool-call answers through a_analyze.load (era1 and the fill runs) and uses the a_analyze
definitions without change. For each model and each brief group (brief sets hotel: correct filters; brief sets no type:
extra filters), the hotel-filter rate is hits / valid answers, pooled over the answers of the group, under the original
tool (t0) and the renamed tool (t1). The ratio is rate(t1) / rate(t0). Random deletion of filters gives the same ratio
for both groups. Intervals: 95% percentile cluster bootstrap over first requests (stats.cluster_bootstrap, 2,000 draws,
seed 20261112), each brief group resampled apart; for the difference of the two ratios, both groups in one draw.
Outputs: r10/analysis/out/tool_ratio.json and tool_ratio.md.
Usage (from explore/): .venv/bin/python -I r10/analysis/tool_ratio.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a_analyze as aa  # noqa: E402  (it sets the import path)

import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"


def ratio(rows):
    """rows: per first request (k0, n0, k1, n1). Pooled rate under t1 divided by the pooled rate under t0."""
    k0, n0 = sum(r[0] for r in rows), sum(r[1] for r in rows)
    k1, n1 = sum(r[2] for r in rows), sum(r[3] for r in rows)
    return (k1 / n1) / (k0 / n0) if k0 and n0 and n1 else float("nan")


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    ids = list(g["booked"])
    groups = {"hotel": [i for i in ids if gold.brief_type(data[i]) == "hotel"],
              "no type": bs.brief_subsets(data, ids, db)["no_type"]}
    res = {"post_hoc": True, "first_requests": {k: len(v) for k, v in groups.items()}, "models": {}}
    for m in aa.MODELS:
        reads, _ = aa.load(m)
        cells = {}
        for name, gi in groups.items():
            c0 = aa.cell_counts(reads, gi, "t0", aa.is_hotel)
            c1 = aa.cell_counts(reads, gi, "t1", aa.is_hotel)
            cells[name] = [(a[0], a[1], b[0], b[1]) for a, b in zip(c0, c1) if a[1] or b[1]]
        out = {}
        for name, rows in cells.items():
            pt, lo, hi = stats.cluster_bootstrap({"x": rows}, lambda s: ratio(s["x"]))
            out[name] = {"t0": [sum(r[0] for r in rows), sum(r[1] for r in rows)],
                         "t1": [sum(r[2] for r in rows), sum(r[3] for r in rows)], "ratio": pt, "ci": [lo, hi]}
        pt, lo, hi = stats.cluster_bootstrap({"h": cells["hotel"], "x": cells["no type"]},
                                             lambda s: ratio(s["h"]) - ratio(s["x"]))
        out["hotel_minus_no_type"] = {"diff": pt, "ci": [lo, hi]}
        res["models"][m] = out
    OUT.mkdir(exist_ok=True)
    (OUT / "tool_ratio.json").write_text(json.dumps(res, indent=1, default=float))
    L = ["## Tool calls at the first request: renamed-to-original filter-rate ratio, by brief (post hoc)", "",
         f"First requests: brief sets hotel {res['first_requests']['hotel']}, brief sets no type "
         f"{res['first_requests']['no type']}. Rates pool the valid answers; intervals resample first requests.", "",
         "| Model | Hotel: t0 | Hotel: t1 | Hotel: ratio [95% CI] | No type: t0 | No type: t1 | No type: ratio [95% CI] | "
         "Hotel minus no type [95% CI] |", "|---|---|---|---|---|---|---|---|"]

    def rt(k, n):
        return f"{k}/{n} = {100 * k / n:.1f}%"
    for m, o in res["models"].items():
        h, x, d = o["hotel"], o["no type"], o["hotel_minus_no_type"]
        L.append(f"| {m} | {rt(*h['t0'])} | {rt(*h['t1'])} | {h['ratio']:.3f} [{h['ci'][0]:.3f}, {h['ci'][1]:.3f}] | "
                 f"{rt(*x['t0'])} | {rt(*x['t1'])} | {x['ratio']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}] | "
                 f"{d['diff']:+.3f} [{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}] |")
    (OUT / "tool_ratio.md").write_text("\n".join(L) + "\n")
    print((OUT / "tool_ratio.md").read_text())


if __name__ == "__main__":
    main()
