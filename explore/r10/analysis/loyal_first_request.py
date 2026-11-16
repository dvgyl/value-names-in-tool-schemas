"""the paper, post hoc, no model call: three checks on the stored first-request tool calls (combined plan A.1,
items C.4 and C.5, and the "removal of only the type filter" item).

Data: the original-tool answers (arm t0) of the six tool-call models (era1 and the fill runs, read through
r10/analysis/a_analyze.load), on the 554 development first requests: 448 whose brief sets no type ("open") and 59
whose brief sets hotel ("specific"). Venue data: hotel_db.json. Fit: briefsearch.fits against the brief.
This script imports no script of the proposals. It reads no sealed file and no folder whose name starts with "em".

Definitions (all counts are answers, as in Table 3 of the paper; a valid answer is a search call or no call):
1. Exclusion: briefsearch.search_failure of a valid search call on an open request (hotel-only type, a guesthouse
   fits the brief, no hotel fits it).
2. Type-only removal (the call counterfactual), on the exclusions: "type alone" when the same call without its type
   returns at least one venue that fits the brief; "other fields too" when it returns none.
3. Relaxation policy (any type): when the call returns no venue and the same call without its type returns at least
   one venue, show the search without the type. The display is the first five venues in the order of hotel_db.json.
   - Open requests: a visible failure is a display with no fitting venue. Counted on the exclusions and on all valid
     search calls. The policy changes only empty displays, so it cannot add a visible failure (by construction).
   - Specific requests: a visible loss is a display with no fitting hotel. An empty display has no fitting hotel, so the
     policy cannot add a visible loss (by construction). The script counts both, to check the construction.
4. Word rule (clear_rule.label on the first request): the share of open first requests whose words state a type, and
   the share of exclusions on requests with no stated type.
Intervals: 95% cluster bootstrap over first requests (stats.cluster_bootstrap, 2,000 draws, seed 20261112).
Usage (from explore/):
  python3 -I r10/analysis/loyal_first_request.py [out folder]
The default out folder is r10/analysis/out. The run takes about 12 seconds.
This file is a copy of the project script loyal_first_request.py with the paths of the study folder; the results are the same.
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
AN = EXPLORE / "r10" / "analysis"
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(EXPLORE / "r10"))
sys.path.insert(0, str(AN))
import a_analyze as aa  # noqa: E402
import briefsearch as bs  # noqa: E402
import clear_rule  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402
import zforms  # noqa: E402

SHOW = 5


def share_ci(per):
    """per: [(k, n)] per first request -> (k, n, share, low, high)."""
    per = [r for r in per if r[1]]
    k, n = sum(r[0] for r in per), sum(r[1] for r in per)
    if not n:
        return {"k": 0, "n": 0}
    stat = lambda g: sum(r[0] for r in g["all"]) / max(1, sum(r[1] for r in g["all"]))
    p, lo, hi = stats.cluster_bootstrap({"all": per}, stat)
    return {"k": k, "n": n, "share": p, "ci": [lo, hi]}


def main(out_dir):
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data, g = runs.context()
    db = gold.hotel_db()
    booked = list(g["booked"])
    open_ids = [d for d in booked if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    spec_ids = [d for d in booked if gold.brief_type(data[d]) == "hotel"]
    assert (len(booked), len(open_ids), len(spec_ids)) == (554, 448, 59), (len(booked), len(open_ids), len(spec_ids))

    # Word rule on the first requests (the same prefix as the tool calls).
    stated = {d: clear_rule.label(data[d], zforms.prefix_end(data[d])) for d in open_ids + spec_ids}
    res = {"post_hoc": True, "sizes": {"first_requests": 554, "open": 448, "specific": 59},
           "word_rule": {"open": dict(collections.Counter(stated[d] for d in open_ids)),
                         "specific": dict(collections.Counter(stated[d] for d in spec_ids))},
           "models": {}}

    for m in aa.MODELS:
        reads, used = aa.load(m)
        c = collections.Counter()
        per_excl, per_type_alone, per_relax_end = [], [], []
        per_vis_open_before, per_vis_open_after = [], []
        per_loss_before, per_loss_after = [], []
        for d in open_ids:
            brief = bs.brief_of(data[d])
            fits = lambda rows: any(bs.fits(v, brief) for v in rows)
            k_ex = n_val = k_alone = k_end = 0
            vb = va = n_search = 0
            for _, kind, f, _ in reads.get((d, "t0"), []):
                if kind == "invalid":
                    continue
                n_val += 1
                c["valid_open"] += 1
                if kind != "search":
                    continue
                n_search += 1
                c["search_open"] += 1
                with_t = bs.search(db, f)
                without = bs.search(db, {**f, "type": None})
                relaxed = without if (not with_t and without) else with_t
                c["relaxed_open"] += relaxed is not with_t
                before_fail = not fits(with_t[:SHOW])
                after_fail = not fits(relaxed[:SHOW])
                vb += before_fail
                va += after_fail
                c["added_visible_failure_open"] += (not before_fail) and after_fail
                if bs.search_failure(f, data[d], db):
                    k_ex += 1
                    c["exclusions"] += 1
                    alone = fits(without)
                    k_alone += alone
                    c["exclusion_type_alone"] += alone
                    c["exclusion_other_fields_too"] += not alone
                    c["exclusion_empty_call"] += not with_t
                    end = fits(relaxed[:SHOW])
                    k_end += end
                    c["exclusion_ended_by_policy"] += end
                    c["exclusion_no_stated_type"] += stated[d] == "unclear"
            per_excl.append((k_ex, n_val))
            if k_ex:
                per_type_alone.append((k_alone, k_ex))
                per_relax_end.append((k_end, k_ex))
            per_vis_open_before.append((vb, n_search))
            per_vis_open_after.append((va, n_search))
        for d in spec_ids:
            brief = bs.brief_of(data[d])
            fit_hotel = lambda rows: any(bs.fits(v, brief) and v["type"] == "hotel" for v in rows)
            lb = la = n_search = 0
            for _, kind, f, _ in reads.get((d, "t0"), []):
                if kind != "search":
                    continue
                n_search += 1
                c["search_specific"] += 1
                with_t = bs.search(db, f)
                without = bs.search(db, {**f, "type": None})
                relaxed = without if (not with_t and without) else with_t
                c["relaxed_specific"] += relaxed is not with_t
                before = not fit_hotel(with_t[:SHOW])
                after = not fit_hotel(relaxed[:SHOW])
                lb += before
                la += after
                c["added_visible_loss_specific"] += (not before) and after
                c["ended_visible_loss_specific"] += before and not after
            per_loss_before.append((lb, n_search))
            per_loss_after.append((la, n_search))
        res["models"][m] = {
            "folders": used, "counts": dict(c),
            "exclusion": share_ci(per_excl),
            "type_alone_of_exclusions": share_ci(per_type_alone),
            "relaxation_ends_exclusion": share_ci(per_relax_end),
            "visible_failure_open_before": share_ci(per_vis_open_before),
            "visible_failure_open_after": share_ci(per_vis_open_after),
            "visible_loss_specific_before": share_ci(per_loss_before),
            "visible_loss_specific_after": share_ci(per_loss_after),
        }
    (out_dir / "loyal_first_request.json").write_text(json.dumps(res, indent=1))

    pc = lambda x: f"{100 * x['share']:.1f}% [{100 * x['ci'][0]:.1f}, {100 * x['ci'][1]:.1f}]" if x.get("n") else "-"
    L = ["## the paper: first-request checks on the stored original-tool calls (post hoc, no model call)", "",
         f"Word rule on the first requests: open {res['word_rule']['open']}; specific {res['word_rule']['specific']}.", "",
         "| Model | Exclusions / valid answers | Type alone (of exclusions) | Other fields too | Empty call (of exclusions) | "
         "Policy ends the exclusion | Exclusions with no stated type | Visible failure, open: before -> after | "
         "Added visible failures | Visible loss, specific: before -> after | Added visible losses |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, r in res["models"].items():
        c = r["counts"]
        L.append(f"| {m} | {c['exclusions']} / {c['valid_open']} ({pc(r['exclusion'])}) | {c['exclusion_type_alone']} "
                 f"({pc(r['type_alone_of_exclusions'])}) | {c['exclusion_other_fields_too']} | {c['exclusion_empty_call']} | "
                 f"{c['exclusion_ended_by_policy']} ({pc(r['relaxation_ends_exclusion'])}) | {c['exclusion_no_stated_type']} | "
                 f"{pc(r['visible_failure_open_before'])} -> {pc(r['visible_failure_open_after'])} | "
                 f"{c['added_visible_failure_open']} | {pc(r['visible_loss_specific_before'])} -> "
                 f"{pc(r['visible_loss_specific_after'])} | {c['added_visible_loss_specific']} |")
    (out_dir / "loyal_first_request.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "out")
