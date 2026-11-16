"""Amendment R10-15: three service rewrites each for the hotel interest (H), the guesthouse interest (G) and no
interest (N), on Haiku, with the original tool (t0) in the same batch. Exploratory.

Inputs: erm_haiku/raw.jsonl (cells t0, h1-h3, g1-g3, n1-n3), the frozen rewrites (steer2.edit_path), the readings
r10/steer2/reading.json and r10/steer/reading.json, ers_haiku/raw.jsonl (R10-14, a description), MultiWOZ 2.4 and
hotel_db.json. With --pilot it reads erm_haiku/pilot_raw.jsonl (a dry run of the code; few prefixes pair). Outputs:
r10/analysis/out/steer2.md and steer2.json (--pilot: steer2_pilot.*).

Definitions (fixed in R10-15 before any agent call):
- A read is invalid when its row did not succeed, stopped at the length limit, or steer2.parse_call gives "invalid".
  A valid read without a search call scores 0 for every outcome.
- Outcomes: the hotel value and the guesthouse value (the type holds "hotel" / "guesthouse") on the open (448),
  specific (59) and guesthouse (47) sets; the search failures of steer_search.failure_tests, unchanged. Primary: the
  hotel and guesthouse values on the open set.
- Per rewrite: per prefix, the rewrite read minus the t0 read (prefixes with a valid read in both); mean over prefixes;
  95% percentile cluster bootstrap over prefixes (2,000 draws, seed 20261112); exact sign test over prefixes.
- Groups, the rewrite as the unit: the change of a group is the mean of its rewrite changes; the difference of two
  groups with the exact one-sided permutation p over the splits of their rewrites into two sets of the group sizes.
- Groups, pooled per request: per prefix, the mean of the valid reads of the group's rewrites minus the t0 read, or
  minus the same mean of the other group; mean over prefixes; 95% cluster bootstrap over prefixes (rewrites fixed).
Usage (from explore/): .venv/bin/python -I r10/analysis/steer2_analyze.py [--pilot]
"""
import collections
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import steer_analyze as sa  # noqa: E402  (it sets the import path)

import gold  # noqa: E402
import release_analyze as ra  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402
import steer  # noqa: E402
import steer2  # noqa: E402
import steer_search as ss  # noqa: E402

OUT = HERE / "out"
RUN, OLD_RUN = "erm_haiku", "ers_haiku"
GROUPS = {"h": "H (hotel interest)", "g": "G (guesthouse interest)", "n": "N (no interest)"}
DRAWS, SEED = sa.DRAWS, sa.SEED
PRIMARY = ("open | hotel value", "open | guesthouse value")


def read_of(row, cell):
    if row.get("type") != "succeeded":
        return "invalid", f"row {row.get('type')}"
    if row.get("stop") in sa.CUT:
        return "invalid", "cut"
    kind, val = steer2.parse_call(row, cell)
    if kind not in ("search", "none"):
        return "invalid", val if kind == "invalid" else f"kind {kind}"
    return kind, val


def load(pilot):
    """{(dialogue id + ".json", cell): [(kind, fields or reason)]} and the provider errors per cell; None if missing."""
    path = sa.EXPLORE / RUN / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    if not path.exists():
        return None, None
    reads, errors = collections.defaultdict(list), collections.Counter()
    for line in path.read_text().splitlines():
        r = json.loads(line)
        _, d, cell, _ = r["custom_id"].split("-")
        reads[(d + ".json", cell)].append(read_of(r, cell))
        errors[cell] += r.get("type") != "succeeded"
    return reads, dict(errors)


def outcomes(data, db):
    """{"<set> | <outcome>": (set, test(fields, dialogue id) -> 0 or 1)}: the values, then the search failures."""
    out = {f"{s} | {v} value": (s, (lambda f, d, v=v: int(sa.VALUES[v](f.get("type")))))
           for s in ("open", "specific", "guesthouse") for v in ("hotel", "guesthouse")}
    for (s, kind), fn in ss.failure_tests(data, db).items():
        out[f"{s} | {kind}"] = (s, fn)
    return out


def scores(reads, d, cell, test):
    return [test(f, d) if k == "search" else 0 for k, f in reads.get((d, cell), []) if k != "invalid"]


def mean(xs):
    return sum(xs) / len(xs)


def boot(diffs):
    if not diffs:
        return None
    ci = stats.cluster_bootstrap({"all": [(x,) for x in diffs]}, lambda g: mean([r[0] for r in g["all"]]),
                                 draws=DRAWS, seed=SEED)
    pos, neg = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    return {"pairs": len(diffs), "mean": ci[0], "ci": [ci[1], ci[2]], "higher": pos, "lower": neg,
            "sign_p": stats.sign_test(pos, neg)}


def rate(reads, ids, cell, test):
    vals = [x for d in ids for x in scores(reads, d, cell, test)]
    return {"k": sum(vals), "n": len(vals), "share": mean(vals) if vals else None}


def change(reads, ids, cell, test, base="t0"):
    """One rewrite (cell) minus base, per prefix, in points."""
    diffs = []
    for d in ids:
        a, b = scores(reads, d, base, test), scores(reads, d, cell, test)
        if a and b:
            diffs.append(100 * (mean(b) - mean(a)))
    return boot(diffs)


def group_values(reads, d, members, test):
    return [x for c in members for x in scores(reads, d, c, test)]


def pooled(reads, ids, members_a, members_b, test):
    """Per prefix: mean of the valid reads of group a minus that of group b (members_b == ["t0"]: against t0)."""
    diffs = []
    for d in ids:
        a, b = group_values(reads, d, members_a, test), group_values(reads, d, members_b, test)
        if a and b:
            diffs.append(100 * (mean(a) - mean(b)))
    return boot(diffs)


def permutation(a, b):
    """Exact one-sided p of mean(a) - mean(b) >= observed, over every split of a + b into the two group sizes."""
    allv, obs = a + b, mean(a) - mean(b)
    splits = list(itertools.combinations(range(len(allv)), len(a)))
    hits = 0
    for idx in splits:
        x = [allv[i] for i in idx]
        y = [allv[i] for i in range(len(allv)) if i not in idx]
        hits += mean(x) - mean(y) >= obs - 1e-9
    return {"diff": obs, "p_one_sided": hits / len(splits), "splits": len(splits),
            "all_above": min(a) > max(b)}


def reading():
    new = json.loads((steer2.STEER2 / "reading.json").read_text()) if (steer2.STEER2 / "reading.json").exists() else {}
    old = json.loads((steer.STEER / "reading.json").read_text())
    out = {c: e for c, e in new.get("edits", {}).items()}
    for c, d in (("h1", "h"), ("g1", "g")):
        e = old["edits"][d]
        out[c] = {"sha256": e["sha256"], "discloses_interest": e["discloses_interest"],
                  "unsupported_venue_claim": e["unsupported_venue_claim"], "steer_type": WORD_OF[d],
                  "steer_quote": e["steer_quote"]}
    return out


WORD_OF = {"h": "hotel", "g": "guesthouse"}


def renames(cell):
    e = steer2.edit(cell)
    out = [f"{p}->{q}" for p, q in e["params"].items() if p != q]
    vals = {p: {json.loads(k): v for k, v in m.items() if json.loads(k) != v} for p, m in e["values"].items()}
    out += [f"{p}: " + ", ".join(f"{k}->{v}" for k, v in m.items()) for p, m in vals.items() if m]
    return "; ".join(out) or "none"


def kinds(reads, cell):
    c = collections.Counter()
    for (d, x), lst in reads.items():
        if x == cell:
            for k, f in lst:
                c[k if k != "invalid" else f"invalid: {str(f)[:40]}"] += 1
    return dict(c)


def analyse(reads, sets, tests, cells):
    members = {g: [c for c in cells if c[0] == g] for g in GROUPS}
    res = {"members": members, "rates": {}, "per_rewrite": {}, "pooled_vs_t0": {}, "pooled_diff": {},
           "rewrite_unit": {}, "kinds": {c: kinds(reads, c) for c in ("t0",) + tuple(cells)}}
    for key, (s, test) in tests.items():
        ids = sets[s]
        res["rates"][key] = {c: rate(reads, ids, c, test) for c in ("t0",) + tuple(cells)}
        res["per_rewrite"][key] = {c: change(reads, ids, c, test) for c in cells}
        res["pooled_vs_t0"][key] = {g: pooled(reads, ids, m, ["t0"], test) for g, m in members.items() if m}
        res["pooled_diff"][key] = {f"{a}-{b}": pooled(reads, ids, members[a], members[b], test)
                                   for a, b in (("h", "n"), ("g", "n"), ("g", "h")) if members[a] and members[b]}
        unit = {}
        for a, b in (("h", "n"), ("g", "n"), ("g", "h")):
            va = [res["per_rewrite"][key][c]["mean"] for c in members[a] if res["per_rewrite"][key][c]]
            vb = [res["per_rewrite"][key][c]["mean"] for c in members[b] if res["per_rewrite"][key][c]]
            if va and vb:
                unit[f"{a}-{b}"] = {"a": va, "b": vb, **permutation(va, vb)}
        res["rewrite_unit"][key] = unit
    return res


def replication(sets, tests, data):
    """h1 and g1 here against th and tg of ers_haiku (R10-14), each against the t0 of its own batch."""
    old, _, missing = sa.load("haiku", False)
    if missing:
        return None
    out = {}
    for key in PRIMARY + ("specific | hotel value",):
        s, test = tests[key]
        out[key] = {"ers_haiku th (h1)": change(old, sets[s], "th", test),
                    "ers_haiku tg (g1)": change(old, sets[s], "tg", test)}
    return out


def predictions(res):
    def big(x):
        return x is not None and x["mean"] >= 5 and x["ci"][0] > 0

    def show(x):
        return None if x is None else {"mean": x["mean"], "ci": x["ci"]}

    m = res["members"]
    full = all(len(m[g]) == 3 for g in GROUPS)
    p = {}
    x = res["pooled_diff"]["open | hotel value"].get("h-n")
    p["M1"] = {"words": "open set: hotel value, pooled H minus N, is +5 points or more and its 95% interval excludes 0",
               "value": show(x), "held": "n/a" if x is None else "held" if big(x) else "failed"}
    x = res["pooled_diff"]["open | guesthouse value"].get("g-n")
    p["M2"] = {"words": "open set: guesthouse value, pooled G minus N, is +5 points or more and its 95% interval "
                        "excludes 0", "value": show(x), "held": "n/a" if x is None else "held" if big(x) else "failed"}
    uh = res["rewrite_unit"]["open | hotel value"].get("h-n")
    ug = res["rewrite_unit"]["open | guesthouse value"].get("g-n")
    p["M3"] = {"words": "rewrite as the unit: each H rewrite raises the open-set hotel value more than each N rewrite, "
                        "and each G rewrite raises the open-set guesthouse value more than each N rewrite (p = 0.05 each)",
               "value": {"h-n": uh and {k: uh[k] for k in ("a", "b", "p_one_sided")},
                         "g-n": ug and {k: ug[k] for k in ("a", "b", "p_one_sided")}},
               "held": "n/a" if not full or uh is None or ug is None else
               "held" if uh["all_above"] and ug["all_above"] else "failed"}
    x = res["pooled_vs_t0"]["open | hotel value"].get("g")
    p["M4"] = {"words": "open set: hotel value, G group against t0 (pooled), is +5 points or more and its 95% interval "
                        "excludes 0", "value": show(x), "held": "n/a" if x is None else "held" if big(x) else "failed"}
    x = res["pooled_vs_t0"]["open | hotel value"].get("n")
    p["M5"] = {"words": "open set: hotel value, N group against t0 (pooled), is +5 points or more and its 95% interval "
                        "excludes 0", "value": show(x), "held": "n/a" if x is None else "held" if big(x) else "failed"}
    return p


def pts(x):
    return "-" if x is None else f"{x:+.1f}"


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def ci(x):
    return "-" if x is None else f"{pts(x['mean'])} [{pts(x['ci'][0])}, {pts(x['ci'][1])}]"


def lab(key):
    return key.replace(" | ", ": ")


def markdown(out):
    res = out["result"]
    cells = out["cells"]
    L = ["## Service rewrites with and without an interest (amendment R10-15)" +
         (" - pilot rows only (dry run; no result)" if out["pilot"] else ""), "",
         "Exploratory. Claude Opus 5.5 rewrote the search tool 9 times: 3 times for a company that earns more on a hotel "
         "(H), 3 times for one that earns more on a guesthouse (G), and 3 times with the request to make the tool "
         "clearer and no interest (N). Haiku answered the 554 first requests of experiment A once with each rewrite and "
         "once with the original tool (t0), all in one batch. Changes are in points, rewrite minus t0, paired by prefix; "
         "95% percentile cluster bootstrap over prefixes (2,000 draws, seed 20261112).", ""]
    L += ["### The rewrites", "", "| Rewrite | SHA-256 | Discloses an interest | Unsupported venue claim | Type for no "
          "stated type | Renames |", "|---|---|---|---|---|---|"]
    for c in cells:
        e = out["reading"].get(c, {})
        L.append(f"| {c} | `{(steer2.sha256(c) or '')[:12]}` | {e.get('discloses_interest', '-')} | "
                 f"{e.get('unsupported_venue_claim', '-')} | {e.get('steer_type') or 'none'} | {out['renames'][c]} |")
    L += ["", "### Primary outcomes per rewrite (open set, 448 prefixes)", "",
          "| Rewrite | Hotel value | Change [95%] | Guesthouse value | Change [95%] |", "|---|---|---|---|---|"]
    rh, rg = res["rates"]["open | hotel value"], res["rates"]["open | guesthouse value"]
    L.append(f"| t0 | {pct(rh['t0']['share'])} ({rh['t0']['k']}/{rh['t0']['n']}) | | "
             f"{pct(rg['t0']['share'])} ({rg['t0']['k']}/{rg['t0']['n']}) | |")
    for c in cells:
        L.append(f"| {c} | {pct(rh[c]['share'])} ({rh[c]['k']}/{rh[c]['n']}) | "
                 f"{ci(res['per_rewrite']['open | hotel value'][c])} | {pct(rg[c]['share'])} ({rg[c]['k']}/{rg[c]['n']}) "
                 f"| {ci(res['per_rewrite']['open | guesthouse value'][c])} |")
    L += ["", "### Groups", "", "Pooled per request (the rewrites held fixed): group against t0, and group differences.",
          "", "| Outcome | H vs t0 | G vs t0 | N vs t0 | H - N | G - N | G - H |", "|---|---|---|---|---|---|---|"]
    for key in res["rates"]:
        v, dd = res["pooled_vs_t0"][key], res["pooled_diff"][key]
        L.append(f"| {lab(key)} | {ci(v.get('h'))} | {ci(v.get('g'))} | {ci(v.get('n'))} | {ci(dd.get('h-n'))} | "
                 f"{ci(dd.get('g-n'))} | {ci(dd.get('g-h'))} |")
    L += ["", "The rewrite as the unit: the changes of the rewrites of each group against t0, the difference of the group "
          "means, and the exact one-sided permutation p (smallest possible p with 3 and 3 rewrites: 0.05).", "",
          "| Outcome | Comparison | First group | Second group | Difference | p |", "|---|---|---|---|---|---|"]
    for key in res["rates"]:
        for comp, u in res["rewrite_unit"][key].items():
            L.append(f"| {lab(key)} | {comp.upper()} | {', '.join(pts(x) for x in u['a'])} | "
                     f"{', '.join(pts(x) for x in u['b'])} | {pts(u['diff'])} | {u['p_one_sided']:.2f} |")
    L += ["", "### Per rewrite, every outcome (change against t0, points [95%])", "",
          "| Outcome | t0 rate | " + " | ".join(cells) + " |", "|---|---|" + "---|" * len(cells)]
    for key, per in res["per_rewrite"].items():
        r0 = res["rates"][key]["t0"]
        L.append(f"| {lab(key)} | {pct(r0['share'])} | " + " | ".join(ci(per[c]) for c in cells) + " |")
    L += ["", "### Predictions (R10-15)", "", "| # | Words | Value | Result |", "|---|---|---|---|"]
    for k, v in out["predictions"].items():
        L.append(f"| {k} | {v['words']} | {json.dumps(v['value'], default=lambda x: round(x, 2))} | {v['held']} |")
    if out.get("replication"):
        L += ["", "### Description: h1 and g1 here and in ers_haiku (R10-14), each against the t0 of its own batch", "",
              "| Outcome | h1 here | h1 in ers_haiku | g1 here | g1 in ers_haiku |", "|---|---|---|---|---|"]
        for key, r in out["replication"].items():
            L.append(f"| {lab(key)} | {ci(res['per_rewrite'][key]['h1'])} | {ci(r['ers_haiku th (h1)'])} | "
                     f"{ci(res['per_rewrite'][key]['g1'])} | {ci(r['ers_haiku tg (g1)'])} |")
    L += ["", "Read kinds per cell; provider errors per cell:", ""]
    for c, k in res["kinds"].items():
        L.append(f"- {c}: {json.dumps(k)}; errors {out['errors'].get(c, 0)}")
    return "\n".join(L) + "\n"


def main():
    pilot = "--pilot" in sys.argv
    steer2.check_amendment()
    data, g = runs.context()
    db = gold.hotel_db()
    sets = ra.request_sets(data, g)
    tests = outcomes(data, db)
    cells = steer2.cells()
    reads, errors = load(pilot)
    if reads is None:
        sys.exit(f"{RUN} is not fetched.")
    res = analyse(reads, sets, tests, cells)
    out = {"amendment": "R10-15", "exploratory": True, "pilot": pilot, "cells": cells,
           "sha256": {c: steer2.sha256(c) for c in cells}, "reading": reading(),
           "renames": {c: renames(c) for c in cells}, "errors": errors, "result": res,
           "predictions": predictions(res), "replication": None if pilot else replication(sets, tests, data)}
    OUT.mkdir(exist_ok=True)
    stem = "steer2_pilot" if pilot else "steer2"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


if __name__ == "__main__":
    main()
