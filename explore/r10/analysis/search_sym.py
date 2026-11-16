"""Symmetric search-harm measure for the repairs (exploratory, post hoc; review round 4, 2026-11-12).

Both sides replay the answer's own search (briefsearch.search with the answer's fields) and look at the first 5 rows,
the rows the tool shows the agent:
- benefit side, dialogues whose brief sets no type (807 of S1t): a "visible failure" is a read whose first 5 rows hold
  no venue that fits the brief;
- cost side, dialogues whose brief sets hotel (233 of S2): a "visible loss" is a read whose first 5 rows hold no hotel
  that fits the brief.
Per dialogue, the mean over valid reads; a dialogue counts when F0 and the arm both have a valid read (paired).
Ratio = (mean visible loss, arm - F0) x W_hotel / ((mean visible failure, F0 - arm) x W_notype). Two weightings:
"subset" (W = 233 and 807) and "groups" (W = 545 and 994, the sizes of the label groups of the trade rule).
95% interval: cluster bootstrap (stats.cluster_bootstrap, 2,000 draws, seed 20261112), dialogues resampled inside
each side. A ratio with no benefit (the arm does not lower visible failures) is reported as "no benefit".
Outputs: r10/analysis/out/search_sym.md and .json. Usage (from explore/): .venv/bin/python -I r10/analysis/search_sym.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import b_analyze as B  # noqa: E402
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
WEIGHTS = {"subset": (233, 807), "groups": (545, 994)}


def first5_has(fields, brief, db, want_hotel):
    rows = bs.search(db, fields)[:5]
    return any(bs.fits(v, brief) and (v["type"] == "hotel" or not want_hotel) for v in rows)


def per_dialogue(got, ids, arm, data, db, want_hotel):
    src = "verify" if arm in ("verify", B.POSTHOC) else arm
    out = {}
    for d in ids:
        brief = bs.brief_of(data[d])
        vals = []
        for r in B.reads_of(got, d, src):
            x = B.scored(got, d, arm, r)
            if x is not None:
                vals.append(0.0 if first5_has(x, brief, db, want_hotel) else 1.0)
        if vals:
            out[d] = sum(vals) / len(vals)
    return out


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    ids = {G: list(g[B.GROUP_KEY[G]]) for G in B.SIZES}
    group_of = {d: G for G, l in ids.items() for d in l}
    no_type = [d for d in ids["S1t"] if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    hotel = [d for d in ids["S2"] if gold.brief_type(data[d]) == "hotel"]
    res = {}
    for m in B.SOURCES:
        got, _ = B.load(m, data, group_of)
        if not got:
            continue
        f_nt = per_dialogue(got, no_type, "f0", data, db, False)
        f_h = per_dialogue(got, hotel, "f0", data, db, True)
        arms = [a for a in B.ARMS if any(k[1] == a for k in got) and a != "b_define"] + [B.POSTHOC]
        row = {"f0": {"visible_failure": sum(f_nt.values()) / len(f_nt), "visible_loss": sum(f_h.values()) / len(f_h)}}
        for arm in arms:
            a_nt = per_dialogue(got, no_type, arm, data, db, False)
            a_h = per_dialogue(got, hotel, arm, data, db, True)
            nt = [(f_nt[d], a_nt[d]) for d in f_nt if d in a_nt]
            h = [(f_h[d], a_h[d]) for d in f_h if d in a_h]
            entry = {"visible_failure": sum(a_nt.values()) / len(a_nt), "visible_loss": sum(a_h.values()) / len(a_h),
                     "paired": [len(nt), len(h)]}
            for wname, (wh, wnt) in WEIGHTS.items():
                def stat(gr, wh=wh, wnt=wnt):
                    ben = sum(r[0] - r[1] for r in gr["nt"]) / len(gr["nt"])
                    cost = sum(r[1] - r[0] for r in gr["h"]) / len(gr["h"])
                    return cost * wh / (ben * wnt) if ben > 0 else float("inf")
                point, lo, hi = stats.cluster_bootstrap({"nt": nt, "h": h}, stat)
                entry[wname] = {"ratio": point, "ci": [lo, hi]}
            row[arm] = entry
        res[m] = row
    OUT.mkdir(exist_ok=True)
    (OUT / "search_sym.json").write_text(json.dumps({"post_hoc": True, "sizes": {"no_type": len(no_type), "hotel": len(hotel)},
                                                     "models": res}, indent=1, default=float))
    fmt = lambda x: "no benefit" if x == float("inf") else f"{x:.2f}"
    L = ["## Symmetric search-harm measure (exploratory, post hoc)", "",
         "Both sides replay the answer's own search and look at the first 5 rows. Visible failure: no venue that fits a "
         "no-type brief (807 dialogues). Visible loss: no hotel that fits a hotel brief (233 dialogues). Ratio: extra "
         "visible losses per visible failure avoided, against F0; 95% cluster bootstrap interval.", "",
         "| Model | Arm | Visible failure (F0 -> arm) | Visible loss (F0 -> arm) | Ratio, subset weights | Ratio, group weights |",
         "|---|---|---|---|---|---|"]
    for m, row in res.items():
        f0 = row["f0"]
        for arm, e in row.items():
            if arm == "f0":
                continue
            s, gw = e["subset"], e["groups"]
            L.append(f"| {m} | {arm} | {100 * f0['visible_failure']:.1f}% -> {100 * e['visible_failure']:.1f}% | "
                     f"{100 * f0['visible_loss']:.1f}% -> {100 * e['visible_loss']:.1f}% | {fmt(s['ratio'])} "
                     f"[{fmt(s['ci'][0])}, {fmt(s['ci'][1])}] | {fmt(gw['ratio'])} [{fmt(gw['ci'][0])}, {fmt(gw['ci'][1])}] |")
    (OUT / "search_sym.md").write_text("\n".join(L) + "\n")
    print((OUT / "search_sym.md").read_text())


if __name__ == "__main__":
    main()
