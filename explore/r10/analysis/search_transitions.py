"""Post hoc details of the repair results (review round 6, 2026-11-12). No model call; reads only the stored
answers that b_analyze.py and search_sym.py read.

1. Transitions of the two verifier gates on the search (search_sym.py measure). The gate changes only the `type` of
   the original-form answer of the same read, so each read gives one pair (original, gate). On the 807 no-type briefs:
   "fixed" = a visible failure under the original form and none under the gate; "broken" = the reverse. On the 233
   hotel briefs: "lost" = no visible loss under the original form and a visible loss under the gate; "regained" = the
   reverse. Counts are in dialogues: a read counts 1 / (valid paired reads of its dialogue), so Haiku and Luna give
   halves. Net avoided = fixed - broken; net added = lost - regained.
2. 95% intervals of the share removed (Table 2, main count: hotel-only values, all 2,029 dialogues). Share removed =
   net unsupported values removed / unsupported values of the original form, with the trade weights 994 and 490.
   Percentile cluster bootstrap (stats.cluster_bootstrap, 2,000 draws, seed 20261112), dialogues resampled inside each
   group, as for the ratio.
Outputs: r10/analysis/out/search_transitions.json and .md.
Usage (from explore/): .venv/bin/python -I r10/analysis/search_transitions.py
"""
import collections
import json
import pathlib
import sys

sys.argv.append("--hotel-only")  # b_analyze reads its main count from argv at import (Table 2 uses hotel-only values)
HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import b_analyze as B  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import search_sym as S  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
GATES = ("verify", B.POSTHOC)


def transitions(got, ids, arm, data, db, want_hotel):
    """{"bad_to_good", "good_to_bad", "bad_to_bad", "good_to_good"} in dialogue units; bad = no fitting venue (no-type
    side) or no fitting hotel (hotel side) among the first five."""
    out = collections.Counter()
    for d in ids:
        brief = S.bs.brief_of(data[d])
        pairs = []
        for r in B.reads_of(got, d, "verify"):
            x0, x1 = B.scored(got, d, "f0", r), B.scored(got, d, arm, r)
            if x0 is None or x1 is None:
                continue
            pairs.append((not S.first5_has(x0, brief, db, want_hotel), not S.first5_has(x1, brief, db, want_hotel)))
        for b0, b1 in pairs:
            key = ("bad" if b0 else "good") + "_to_" + ("bad" if b1 else "good")
            out[key] += 1 / len(pairs)
    return dict(out)


def share_interval(c):
    def share(gr):
        p = {g: (sum(r[0] for r in gr[g]) / sum(r[1] for r in gr[g]), sum(r[2] for r in gr[g]) / sum(r[3] for r in gr[g]))
             for g in ("S1t", "S3")}
        wrong = sum(p[g][0] * B.SIZES[g] for g in p)
        return sum((p[g][0] - p[g][1]) * B.SIZES[g] for g in p) / wrong
    return stats.cluster_bootstrap({g: c[g] for g in ("S1t", "S3")}, share)


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    ids_by_group = {G: list(g[B.GROUP_KEY[G]]) for G in B.SIZES}
    group_of = {d: G for G, ids in ids_by_group.items() for d in ids}
    no_type = [d for d in ids_by_group["S1t"]
               if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    hotel = [d for d in ids_by_group["S2"] if gold.brief_type(data[d]) == "hotel"]
    res = {}
    for m in B.SOURCES:
        got, _ = B.load(m, data, group_of)
        arms = [a for a in B.ARMS if any(k[1] == a for k in got) and a != "b_define"]
        row = {"transitions": {}, "removed_share": {}}
        for gate in GATES:
            row["transitions"][gate] = {"no_type": transitions(got, no_type, gate, data, db, False),
                                        "hotel": transitions(got, hotel, gate, data, db, True)}
        for arm in arms + [B.POSTHOC]:
            point, lo, hi = share_interval(B.cells(got, ids_by_group, arm))
            row["removed_share"][arm] = [point, lo, hi]
        res[m] = row
    OUT.mkdir(exist_ok=True)
    (OUT / "search_transitions.json").write_text(json.dumps({"post_hoc": True, "sizes": {"no_type": len(no_type),
                                                             "hotel": len(hotel)}, "models": res}, indent=1))
    f = lambda x: f"{x:.1f}".rstrip("0").rstrip(".") if x % 1 else f"{x:.0f}"
    L = ["## Repair details (post hoc)", "", "### Transitions of the verifier gates (dialogues; Haiku and Luna: halves)",
         "", "| Model | Gate | No-type: fixed | broken | still failing | still fine | Net avoided | Hotel: lost | regained | "
         "still lost | still fine | Net added |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, row in res.items():
        for gate, t in row["transitions"].items():
            nt, h = t["no_type"], t["hotel"]
            fx, br = nt.get("bad_to_good", 0), nt.get("good_to_bad", 0)
            lo_, rg = h.get("good_to_bad", 0), h.get("bad_to_good", 0)
            L.append(f"| {m} | {gate} | {f(fx)} | {f(br)} | {f(nt.get('bad_to_bad', 0))} | {f(nt.get('good_to_good', 0))} | "
                     f"{f(fx - br)} | {f(lo_)} | {f(rg)} | {f(h.get('bad_to_bad', 0))} | {f(h.get('good_to_good', 0))} | "
                     f"{f(lo_ - rg)} |")
    L += ["", "### Share removed with 95% intervals (main count, all dialogues)", "", "| Model | Repair | Share removed |",
          "|---|---|---|"]
    for m, row in res.items():
        for arm, (p, lo, hi) in row["removed_share"].items():
            L.append(f"| {m} | {arm} | {100 * p:.1f}% [{100 * lo:.1f}, {100 * hi:.1f}] |")
    (OUT / "search_transitions.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
