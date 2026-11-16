"""Search-side outcomes asked for in review round 2 (exploratory, post hoc, 2026-11-12). No model call.

1. The relaxation check on every T0 search of the 554 prefixes, split by what the brief sets for `type` (no type,
   hotel, guesthouse). A flag is an empty search whose repeat without the type filter finds venues. For a brief that
   sets hotel, a flag widens the search beyond the brief.
2. For each repair arm and model: the share of answers whose `type` hides every venue that fits the brief
   (briefsearch.search_failure), on the S1t dialogues whose brief sets no type (807), against the baseline F0; and the
   share of answers that keep a hotel-only filter on the S2 dialogues whose brief sets hotel (233).
Outputs: r10/analysis/out/search_side.json and search_side.md.
Usage (from explore/): .venv/bin/python -I r10/analysis/search_side.py
"""
import collections
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
import a_analyze as A  # noqa: E402
import b_analyze as B  # noqa: E402
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402

OUT = HERE / "out"


def brief_kind(d):
    t1, t2 = gold.brief_type(d), gold.brief_type(d, "fail_info")
    return t1 or t2 or "no type"


def relaxation_by_brief(data, g, db):
    res = {}
    for m in A.MODELS:
        reads, _ = A.load(m)
        if reads is None:
            continue
        c = collections.defaultdict(collections.Counter)
        for d in g["booked"]:
            kind = brief_kind(data[d])
            for _, k, f, _ in reads.get((d, "t0"), []):
                if k != "search":
                    continue
                rel = bs.relaxation(f, db)
                c[kind]["searches"] += 1
                c[kind]["flags"] += rel["flag"]
                c[kind]["flags_failure"] += rel["flag"] and bs.search_failure(f, data[d], db)
        res[m] = {k: dict(v) for k, v in c.items()}
    return res


def repair_search(data, g, db):
    ids = {G: list(g[B.GROUP_KEY[G]]) for G in B.SIZES}
    group_of = {d: G for G, l in ids.items() for d in l}
    no_type = [d for d in ids["S1t"] if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    hotel = [d for d in ids["S2"] if gold.brief_type(data[d]) == "hotel"]
    res = {}
    for m in B.SOURCES:
        got, _ = B.load(m, data, group_of)
        if not got:
            continue
        arms = ["f0"] + [a for a in B.ARMS if any(k[1] == a for k in got)] + [B.POSTHOC]
        row = {}
        for arm in arms:
            src = "verify" if arm in ("verify", B.POSTHOC) else arm
            fail = n1 = keep = n2 = 0
            for d in no_type:
                for r in B.reads_of(got, d, src):
                    x = B.scored(got, d, arm, r)
                    if x is not None:
                        n1 += 1
                        fail += bs.search_failure(x, data[d], db)
            for d in hotel:
                for r in B.reads_of(got, d, src):
                    x = B.scored(got, d, arm, r)
                    if x is not None:
                        n2 += 1
                        keep += gold.hides_guesthouse(x["type"])
            vis = 0  # visible loss: a brief-hotel answer whose own search shows no fitting hotel in the first 5 rows
            for d in hotel:
                brief = bs.brief_of(data[d])
                for r in B.reads_of(got, d, src):
                    x = B.scored(got, d, arm, r)
                    if x is not None and not gold.hides_guesthouse(x["type"]):
                        top = bs.search(db, x)[:5]
                        vis += not any(v["type"] == "hotel" and bs.fits(v, brief) for v in top)
            row[arm] = {"search_failure": [fail, n1], "hotel_only_kept_brief_hotel": [keep, n2],
                        "visible_loss_brief_hotel": [vis, n2]}
        res[m] = row
    return res


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    rel = relaxation_by_brief(data, g, db)
    rep = repair_search(data, g, db)
    OUT.mkdir(exist_ok=True)
    (OUT / "search_side.json").write_text(json.dumps({"exploratory": True, "post_hoc": True, "relaxation_by_brief": rel,
                                                       "repairs": rep}, indent=1))
    pct = lambda k, n: f"{k}/{n} ({100 * k / n:.1f}%)" if n else "-"
    L = ["## Search-side outcomes (exploratory, post hoc)", "", "### The relaxation check by what the brief sets (T0 searches, 554 prefixes)", "",
         "| Model | Brief | Searches | Flags | Flags on a search failure |", "|---|---|---|---|---|"]
    for m, r in rel.items():
        for kind in ("no type", "hotel", "guesthouse"):
            x = r.get(kind, {})
            L.append(f"| {m} | {kind} | {x.get('searches', 0)} | {x.get('flags', 0)} | {x.get('flags_failure', 0)} |")
    L += ["", "### Repairs: search failure (brief sets no type, 807) and hotel-only filter kept (brief sets hotel, 233)", "",
          "| Model | Arm | Search failure | Hotel-only filter kept where the brief sets hotel |", "|---|---|---|---|"]
    for m, r in rep.items():
        for arm, x in r.items():
            L.append(f"| {m} | {arm} | {pct(*x['search_failure'])} | {pct(*x['hotel_only_kept_brief_hotel'])} |")
    L += ["", "### Repairs: extra visible losses per search failure avoided (post hoc; review round 3, N1)", "",
          "A visible loss: on a dialogue whose brief sets hotel, the answer keeps no hotel-only filter and the first 5 rows "
          "of its own search hold no hotel that fits the brief. Rates are per answer; the ratio uses the subset sizes "
          "(807 no-type briefs, 233 hotel briefs): (visible-loss rate of the arm - of F0) x 233 / ((search-failure rate of "
          "F0 - of the arm) x 807).", "",
          "| Model | Arm | Search failure | Visible loss | Extra visible losses per search failure avoided |", "|---|---|---|---|---|"]
    for m, r in rep.items():
        f0 = r["f0"]
        sf0 = f0["search_failure"][0] / f0["search_failure"][1]
        vl0 = f0["visible_loss_brief_hotel"][0] / f0["visible_loss_brief_hotel"][1]
        for arm, x in r.items():
            sf = x["search_failure"][0] / x["search_failure"][1] if x["search_failure"][1] else None
            vl = x["visible_loss_brief_hotel"][0] / x["visible_loss_brief_hotel"][1] if x["visible_loss_brief_hotel"][1] else None
            ratio = "-"
            if arm != "f0" and sf is not None and vl is not None and sf0 - sf > 0:
                ratio = f"{(vl - vl0) * 233 / ((sf0 - sf) * 807):.2f}"
            elif arm != "f0":
                ratio = "- (no search failure avoided)"
            L.append(f"| {m} | {arm} | {pct(*x['search_failure'])} | {pct(*x['visible_loss_brief_hotel'])} | {ratio} |")
    (OUT / "search_side.md").write_text("\n".join(L) + "\n")
    print((OUT / "search_side.md").read_text())


if __name__ == "__main__":
    main()
