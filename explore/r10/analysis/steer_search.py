"""The service run (amendment R10-14): search failures under the original tool and the two steered rewrites. Post hoc,
exploratory, no model call (the paper review round 6: Opus R2, Sol 3).

Inputs: the stored first calls of the steering run, read with steer_analyze.load (Sonnet: t0 from erp_sonnet, th and tg
from ers_sonnet; Haiku: t0, th and tg from ers_haiku), MultiWOZ 2.4 and hotel_db.json. The fit rule is the frozen
briefsearch.fits (the corpus goal record goal.hotel.info), unchanged. Outputs: r10/analysis/out/steer_search.md and
steer_search.json.

Definitions (chosen after the run; post hoc):
- A read is as in steer_analyze.read_of (invalid reads are left out; a read without a search scores 0).
- Open set (448 first requests, brief sets no type): the venues that fit the brief are briefsearch.brief_fitting.
  * hotel-only failure: briefsearch.search_failure (the call keeps hotel and not guesthouse, at least one venue fits,
    and no fitting venue is a hotel). This is the paper's "search failure".
  * guesthouse-only failure: the call keeps guesthouse and not hotel, at least one venue fits, and no fitting venue is
    a guesthouse (the mirror case).
  * any failure: either of the two, so the type filter excludes every venue that fits the brief.
- Guesthouse set (47, brief sets guesthouse): the fitting venues are the guesthouses that meet briefsearch.fits. A
  failure is a call that keeps hotel and not guesthouse while at least one such guesthouse exists.
- Hotel set (59, brief sets hotel): the fitting venues are the hotels that meet briefsearch.fits. A failure is a call
  that keeps guesthouse and not hotel while at least one such hotel exists.
- Rates: share of valid reads (one read per request and tool). Change: steered minus original per request, mean over
  requests, 95% percentile cluster bootstrap over requests (stats.cluster_bootstrap, 2,000 draws, seed 20261112).
- A word check, no person checked it: a th read with text before or instead of the call that mentions a later or a
  second search ("first search", "search ... first", "start with", "again", "then search", "fall back", "if that
  returns", "if nothing"). Two or more
  calls in one answer make the read invalid in steer.parse_call; the count of such reads is also given.
Usage (from explore/): .venv/bin/python -I r10/analysis/steer_search.py
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import steer_analyze as sa  # noqa: E402  (it sets the import path)

import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import release_analyze as ra  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
CELLS = ("t0", "th", "tg")
LATER = re.compile(r"first search|search(es|ing)? [^.]{0,40}\bfirst\b|start with|\bagain\b|then search|fall ?back|if that returns|if nothing", re.I)


def holds_guest_only(t):
    return isinstance(t, tuple) and "guesthouse" in t and "hotel" not in t


def failure_tests(data, db):
    """{set: function(fields, dialogue id) -> 0 or 1} for each kind of failure."""
    def fit(d):
        return bs.brief_fitting(data[d], db)

    def open_hotel(f, d):
        return int(bs.search_failure(f, data[d], db))

    def open_guest(f, d):
        v = fit(d)
        return int(holds_guest_only(f.get("type")) and bool(v) and not any(x["type"] == "guesthouse" for x in v))

    def open_any(f, d):
        return max(open_hotel(f, d), open_guest(f, d))

    def guest_set(f, d):
        return int(gold.hides_guesthouse(f.get("type")) and any(x["type"] == "guesthouse" for x in fit(d)))

    def hotel_set(f, d):
        return int(holds_guest_only(f.get("type")) and any(x["type"] == "hotel" for x in fit(d)))
    return {("open", "hotel-only failure"): open_hotel, ("open", "guesthouse-only failure"): open_guest,
            ("open", "any failure"): open_any, ("guesthouse", "hotel-only failure"): guest_set,
            ("specific", "guesthouse-only failure"): hotel_set}


def scores(reads, d, cell, test):
    return [test(f, d) if k == "search" else 0 for k, f in reads.get((d, cell), []) if k != "invalid"]


def mean(xs):
    return sum(xs) / len(xs)


def rate(reads, ids, cell, test):
    vals = [x for d in ids for x in scores(reads, d, cell, test)]
    return {"k": sum(vals), "n": len(vals), "share": mean(vals) if vals else None}


def change(reads, ids, cell, test):
    diffs = []
    for d in ids:
        a, b = scores(reads, d, "t0", test), scores(reads, d, cell, test)
        if a and b:
            diffs.append(100 * (mean(b) - mean(a)))
    ci = stats.cluster_bootstrap({"all": [(x,) for x in diffs]}, lambda g: mean([r[0] for r in g["all"]]),
                                 draws=sa.DRAWS, seed=sa.SEED)
    return {"pairs": len(diffs), "mean": ci[0], "ci": [ci[1], ci[2]], "higher": sum(x > 0 for x in diffs),
            "lower": sum(x < 0 for x in diffs)}


def later_search_text(agent):
    """th reads: texts that mention a later search (word check), and reads with two or more calls."""
    rows = [json.loads(x) for x in (sa.EXPLORE / sa.SOURCES[agent]["th"] / "raw.jsonl").read_text().splitlines()]
    th = [r for r in rows if r["custom_id"].split("-")[2] == "th"]
    texts = [r for r in th if (r.get("text") or "").strip()]
    hits = [r for r in texts if LATER.search(r.get("text") or "")]
    multi = [r for r in th if sa.read_of(r, "th")[0] == "invalid"]
    return {"reads": len(th), "with_text": len(texts), "mentions_later_search": len(hits),
            "examples": [{"id": r["custom_id"], "text": (r.get("text") or "")[:300]} for r in hits[:8]],
            "invalid_reads": len(multi)}


def group_sizes(data, db, sets):
    out = {}
    fit = {d: bs.brief_fitting(data[d], db) for s in sets.values() for d in s}
    o = sets["open"]
    out["open"] = {"n": len(o), "only_guesthouses_fit": sum(bool(fit[d]) and all(v["type"] == "guesthouse" for v in fit[d]) for d in o),
                   "only_hotels_fit": sum(bool(fit[d]) and all(v["type"] == "hotel" for v in fit[d]) for d in o),
                   "both_fit": sum(any(v["type"] == "hotel" for v in fit[d]) and any(v["type"] == "guesthouse" for v in fit[d]) for d in o),
                   "none_fits": sum(not fit[d] for d in o)}
    out["guesthouse"] = {"n": len(sets["guesthouse"]),
                         "a_guesthouse_fits": sum(any(v["type"] == "guesthouse" for v in fit[d]) for d in sets["guesthouse"])}
    out["specific"] = {"n": len(sets["specific"]),
                       "a_hotel_fits": sum(any(v["type"] == "hotel" for v in fit[d]) for d in sets["specific"])}
    return out


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    sets = ra.request_sets(data, g)
    tests = failure_tests(data, db)
    out = {"post_hoc": True, "exploratory": True, "groups": group_sizes(data, db, sets), "agents": {}}
    for agent in sa.SOURCES:
        reads, errors, missing = sa.load(agent, False)
        assert not missing, missing
        a = {"rates": {}, "changes": {}, "later_search_text": later_search_text(agent)}
        for (s, kind), test in tests.items():
            key = f"{s} | {kind}"
            a["rates"][key] = {c: rate(reads, sets[s], c, test) for c in CELLS}
            a["changes"][key] = {c: change(reads, sets[s], c, test) for c in ("th", "tg")}
        out["agents"][agent] = a
    L = ["## The service run: search failures under the original tool and the two rewrites (post hoc)", "",
         "No model call. Stored first calls of the steering run (one per request and tool). Fit rule: the frozen "
         "briefsearch.fits on the corpus goal record. Rates: share of valid reads. Change: steered minus original, "
         "points, 95% cluster bootstrap over requests (2,000 draws, seed 20261112).", "",
         "Groups: " + json.dumps(out["groups"]), "",
         "| Agent | Set | Failure | Original | Rewrite H | Change H [95%] | Rewrite G | Change G [95%] |",
         "|---|---|---|---|---|---|---|---|"]
    for agent, a in out["agents"].items():
        for key, r in a["rates"].items():
            s, kind = key.split(" | ")
            ch = a["changes"][key]
            cols = []
            for c in ("th", "tg"):
                x = ch[c]
                cols += [f"{pct(r[c]['share'])} ({r[c]['k']}/{r[c]['n']})",
                         f"{x['mean']:+.1f} [{x['ci'][0]:+.1f}, {x['ci'][1]:+.1f}]"]
            L.append(f"| {agent} | {s} ({r['t0']['n']}) | {kind} | {pct(r['t0']['share'])} ({r['t0']['k']}/{r['t0']['n']}) | "
                     + " | ".join(cols) + " |")
    L += ["", "### Rewrite H: texts that mention a later search (word check; no person checked it)", ""]
    for agent, a in out["agents"].items():
        x = a["later_search_text"]
        L.append(f"- {agent}: {x['reads']} reads; {x['with_text']} with text; {x['mentions_later_search']} mention a "
                 f"later search; {x['invalid_reads']} invalid reads (two or more calls make a read invalid)")
        for e in x["examples"]:
            L.append(f"  - {e['id']}: {e['text']!r}")
    OUT.mkdir(exist_ok=True)
    (OUT / "steer_search.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / "steer_search.md").write_text("\n".join(L) + "\n")
    print((OUT / "steer_search.md").read_text())


if __name__ == "__main__":
    main()
