"""Post hoc analyses of the repairs, final-4 round (2026-11-14). No model call, no network, no paid call.

This file is a copy of the project analysis (an internal file) with the paths of the study folder and neutral
names; the results are the same. Usage (from explore/): .venv/bin/python -I r10/analysis/repair_refs.py
Output: r10/analysis/out/repair_refs.json.

Data: stored development answers only (the repair folders that b_analyze.SOURCES names, and ery_deepseek, ery_qwen,
ery_gemma), loaded with the loaders of the independent check (repair_loaders.py), which use the
project's own parsers. The script refuses any folder whose name starts with "em". It opens no sealed file, no key file
and no .env file. It imports no script of workshops/proposal-*.

Sets: the 807 development dialogues where the brief and the label set no type ("nt") and the 233 where both set
`hotel` ("h"). A hotel-only value is a `type` list that holds `hotel` and not `guesthouse` (the paper's main count).

Part A. The repairs under the brief and under two text references (value level, raw counts on the 807 and 233).
  Per model, arm and dialogue: the mean over the reads where the original answer and the arm answer are both valid.
  removed = net hotel-only values removed on nt; share removed = removed / original hotel-only values on nt;
  brief ratio = net values lost on all 233 / removed; T1 = net values lost on the "stated" h dialogues / removed;
  each as a raw ratio and in the two weightings of the paper's search measure (rates per paired dialogue times 233 and
  807, "subset", or 545 and 994, "group"); the subset form is the main one and equals the raw one when every
  dialogue has a valid pair;
  loss not stated = share of the net brief losses outside the "stated" dialogues.
  References for "stated": word rule (clear_rule.label == "hotel_only"); reader majority, leave one out (at least 5
  of the other 8 models' read-1 verifier answers say "yes"). Text rule (post hoc): share removed >= 50% and T1 <= 0.30.
  95% cluster bootstrap inside each set (stats.cluster_bootstrap, 2,000 draws, seed 20261112).
Part B. Display policies on the same original answers (search measure of the paper, five venues in file order):
  original, verifier (planned gate), clear-no gate, relaxation policy (any type filter; the search with the type is
  empty and the search without it is not), always remove (every hotel-only filter becomes null).
Part C. The same policies under other displays: 10 venues, file order; 5 venues by stars (high to low) or by price
  (cheap first), ties in file order; 5 venues in random order (mean over 200 seeded orders of the venue file). Also the
  visibility cost of a search from the brief without a type on the 233 hotel briefs.
Part D. Worst-case bound for the cut original answers of Qwen and gemma (three-model evaluation): each cut original
  answer is scored as a pair whose gate causes the error (a visible failure on nt, a visible loss on h).
"""
import collections
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
sys.path.insert(0, str(HERE))
import repair_loaders as V  # noqa: E402  (sets the project import paths)

B, bs, cr, gold, runs, stats = V.B, V.bs, V.cr, V.gold, V.runs, V.stats
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "out" / "repair_refs.json"
ARMS = ("b_list", "b_shot", "b_evidence", "verify", B.POSTHOC)
NAME = {"b_list": "list", "b_shot": "examples", "b_evidence": "quote", "verify": "verifier, planned gate",
        B.POSTHOC: "verifier, clear-no gate"}
DEV = {"sonnet": "a", "haiku": "a", "opus": "a", "sol": "o", "luna": "o", "astra": "o", "deepseek": "d", "qwen": "q",
       "gemma": "g"}
INF = float("inf")


def ho(t):
    return isinstance(t, tuple) and "hotel" in t and "guesthouse" not in t


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


# ------------------------------------------------------------------------------------------------ part A
def value_cells(got, ids, arm):
    out = {}
    src = "verify" if arm in ("verify", B.POSTHOC) else arm
    for d in ids:
        a, b = [], []
        for rd in B.reads_of(got, d, src):
            f0, x = got.get((d, "f0", rd)), B.scored(got, d, arm, rd)
            if f0 is not None and x is not None:
                a.append(ho(f0["type"]))
                b.append(ho(x["type"]))
        if a:
            out[d] = (mean(a), mean(b))
    return out


def ratios(g):
    """Raw ratios (net counts), and the subset-weight and group-weight forms of the paper's search measure: rates per
    paired dialogue times 233 and 807 (subset) or 545 and 994 (group)."""
    removed = sum(a - b for a, b in g["nt"])
    lost_st = sum(a - b for a, b in g["st"])
    lost_ns = sum(a - b for a, b in g["ns"])
    n_nt, n_h = len(g["nt"]), len(g["st"]) + len(g["ns"])
    out = {"brief_raw": (lost_st + lost_ns) / removed if removed > 0 else INF,
           "T1_raw": lost_st / removed if removed > 0 else INF}
    for w, (wh, wnt) in {"subset": (233, 807), "group": (545, 994)}.items():
        ben = removed / n_nt * wnt
        out["brief_" + w] = (lost_st + lost_ns) / n_h * wh / ben if removed > 0 else INF
        out["T1_" + w] = lost_st / n_h * wh / ben if removed > 0 else INF
    out["brief"], out["T1"] = out["brief_subset"], out["T1_subset"]
    return out


def part_a(G, data, nt, h):
    rule = {d: cr.label(data[d]) for d in h}
    votes = collections.defaultdict(dict)
    for m, got in G.items():
        for d in h:
            v = got.get((d, "verify", 1))
            if v is not None:
                votes[d][m] = v["answer"]
    res = {"counts": {"word_rule": dict(collections.Counter(rule.values()))}}
    for m, got in G.items():
        maj = {d: sum(a == "yes" for mm, a in votes[d].items() if mm != m) >= 5 for d in h}
        n_votes = collections.Counter(sum(1 for mm in votes[d] if mm != m) for d in h)
        refs = {"word rule": lambda d: rule[d] == "hotel_only", "reader majority (5 of the other 8)": lambda d: maj[d]}
        row = {"other_votes_per_dialogue": dict(n_votes), "reader_majority_stated": sum(maj.values())}
        for arm in ARMS:
            src = "verify" if arm in ("verify", B.POSTHOC) else arm
            if not any(k[1] == src for k in got):
                continue
            c_nt, c_h = value_cells(got, nt, arm), value_cells(got, h, arm)
            f0_nt = sum(a for a, _ in c_nt.values())
            removed = sum(a - b for a, b in c_nt.values())
            e = {"dialogues": [len(c_nt), len(c_h)], "f0_values_nt": f0_nt, "removed": removed,
                 "share_removed": removed / f0_nt if f0_nt else None,
                 "lost_brief": sum(a - b for a, b in c_h.values())}
            for rname, f in refs.items():
                g = {"nt": list(c_nt.values()), "st": [p for d, p in c_h.items() if f(d)],
                     "ns": [p for d, p in c_h.items() if not f(d)]}
                rr = ratios(g)
                lost_all = sum(a - b for a, b in g["st"] + g["ns"])
                lost_st = sum(a - b for a, b in g["st"])
                x = {"stated": len(g["st"]), "lost_stated": lost_st, **rr,
                     "loss_not_stated_share": (lost_all - lost_st) / lost_all if lost_all > 0 else None,
                     "meets_text_rule": bool(e["share_removed"] is not None and e["share_removed"] >= 0.5
                                             and rr["T1"] <= 0.30),
                     "meets_text_rule_group": bool(e["share_removed"] is not None and e["share_removed"] >= 0.5
                                                   and rr["T1_group"] <= 0.30)}
                if arm in ("verify", B.POSTHOC):
                    for key in ("brief", "T1", "T1_group"):
                        x[key + "_ci"] = list(stats.cluster_bootstrap(g, lambda s, key=key: ratios(s)[key]))
                e[rname] = x
            row[NAME[arm]] = e
        res[m] = row
    return res


# ------------------------------------------------------------------------------------------------ parts B, C, D
PRICE = {"cheap": 0, "moderate": 1, "expensive": 2}


def policy_fields(got, d, rd, policy, db):
    """The fields whose search the display shows, or None when the pair is not valid. `relax` is handled in show()."""
    f0 = got.get((d, "f0", rd))
    if f0 is None or B.scored(got, d, "verify", rd) is None:
        return None
    if policy in ("original", "relax"):
        return f0
    if policy == "always":
        out = dict(f0)
        if ho(out["type"]):
            out["type"] = None
        return out
    return B.scored(got, d, policy, rd)


def rows_for(fields, policy, db):
    rows = bs.search(db, fields)
    if policy == "relax" and not rows:
        wide = bs.search(db, {**fields, "type": None})
        if wide:
            return wide
    return rows


def order(rows, how, rank=None):
    if how == "file":
        return rows
    if how == "stars":
        return sorted(rows, key=lambda v: -int(v.get("stars") or 0))
    if how == "price":
        return sorted(rows, key=lambda v: PRICE.get(v.get("pricerange"), 3))
    return sorted(rows, key=lambda v: rank[v["name"]])


def miss(shown, brief, want_hotel):
    return 0.0 if any(bs.fits(v, brief) and (v["type"] == "hotel" or not want_hotel) for v in shown) else 1.0


POLICIES = ("original", "verify", B.POSTHOC, "relax", "always")
DISPLAYS = {"file 5": ("file", 5), "file 10": ("file", 10), "stars 5": ("stars", 5), "price 5": ("price", 5),
            "random 5": ("random", 5)}


def display_parts(G, data, db, nt, h, n_random=200):
    rng = random.Random(20261114)
    ranks = []
    for _ in range(n_random):
        names = [v["name"] for v in db]
        rng.shuffle(names)
        ranks.append({n: i for i, n in enumerate(names)})
    out = {}
    for m, got in G.items():
        per = collections.defaultdict(dict)  # (display, side, policy) -> {d: mean miss}
        for side, ids, want in (("nt", nt, False), ("h", h, True)):
            for d in ids:
                brief = bs.brief_of(data[d])
                acc = collections.defaultdict(list)
                for rd in B.reads_of(got, d, "f0"):
                    for p in POLICIES:
                        f = policy_fields(got, d, rd, p, db)
                        if f is None:
                            continue
                        rows = rows_for(f, p, db)
                        for dname, (how, k) in DISPLAYS.items():
                            if how == "random":
                                v = mean(miss(order(rows, how, rk)[:k], brief, want) for rk in ranks)
                            else:
                                v = miss(order(rows, how)[:k], brief, want)
                            acc[(dname, p)].append(v)
                for (dname, p), vals in acc.items():
                    per[(dname, side, p)][d] = mean(vals)
        res = {}
        for dname in DISPLAYS:
            f_nt, f_h = per[(dname, "nt", "original")], per[(dname, "h", "original")]
            row = {"original": {"visible_failure": mean(f_nt.values()), "visible_loss": mean(f_h.values()),
                                "dialogues": [len(f_nt), len(f_h)]}}
            for p in POLICIES[1:]:
                a_nt, a_h = per[(dname, "nt", p)], per[(dname, "h", p)]
                pnt = [(f_nt[d], a_nt[d]) for d in f_nt if d in a_nt]
                ph = [(f_h[d], a_h[d]) for d in f_h if d in a_h]
                e = {"visible_failure": mean(a_nt.values()), "visible_loss": mean(a_h.values()),
                     "net_avoided": sum(x - y for x, y in pnt), "net_added": sum(y - x for x, y in ph),
                     "failures_caused": sum(max(y - x, 0) for x, y in pnt), "losses_caused": sum(max(y - x, 0) for x, y in ph)}
                if dname == "file 5":
                    def stat(gr):
                        ben = sum(x - y for x, y in gr["nt"]) / len(gr["nt"])
                        cost = sum(y - x for x, y in gr["h"]) / len(gr["h"])
                        return cost * 233 / (ben * 807) if ben > 0 else INF
                    e["subset_ratio"] = list(stats.cluster_bootstrap({"nt": pnt, "h": ph}, stat))
                row[NAME.get(p, p)] = e
            res[dname] = row
        out[m] = res
    # visibility cost of a search from the brief without a type (233 hotel briefs)
    vis = {}
    for dname, (how, k) in DISPLAYS.items():
        vals = []
        for d in h:
            brief = {kk: vv for kk, vv in bs.brief_of(data[d]).items() if kk != "type"}
            rows = [v for v in db if bs.fits(v, brief)]
            if how == "random":
                vals.append(mean(miss(order(rows, how, rk)[:k], bs.brief_of(data[d]), True) for rk in ranks))
            else:
                vals.append(miss(order(rows, how)[:k], bs.brief_of(data[d]), True))
        vis[dname] = {"briefs": len(vals), "no_fitting_hotel_shown": sum(vals), "share": mean(vals)}
    return out, vis


def worst_case(G, data, db, nt, h):
    """Part D: the cut original answers of Qwen and gemma scored against the gate (worst case for the ratio)."""
    out = {}
    for m in ("qwen", "gemma"):
        got = G[m]
        res = {}
        for gate in ("verify", B.POSTHOC):
            sides = {}
            n_cut = collections.Counter()
            for side, ids, want in (("nt", nt, False), ("h", h, True)):
                pairs = []
                for d in ids:
                    brief = bs.brief_of(data[d])
                    vals = []
                    for rd in B.reads_of(got, d, "verify"):
                        f0 = got.get((d, "f0", rd))
                        v = got.get((d, "verify", rd))
                        if v is None:
                            continue
                        if f0 is None:
                            n_cut[side] += 1
                            vals.append((0.0, 1.0))
                            continue
                        x = B.scored(got, d, gate, rd)
                        vals.append((miss(bs.search(db, f0)[:5], brief, want), miss(bs.search(db, x)[:5], brief, want)))
                    if vals:
                        pairs.append((mean(a for a, _ in vals), mean(b for _, b in vals)))
                sides[side] = pairs

            def stat(gr):
                ben = sum(x - y for x, y in gr["nt"]) / len(gr["nt"])
                cost = sum(y - x for x, y in gr["h"]) / len(gr["h"])
                return cost * 233 / (ben * 807) if ben > 0 else INF
            res[NAME[gate]] = {"cut_answers": dict(n_cut), "dialogues": [len(sides["nt"]), len(sides["h"])],
                               "net_avoided": sum(x - y for x, y in sides["nt"]),
                               "net_added": sum(y - x for x, y in sides["h"]),
                               "subset_ratio": list(stats.cluster_bootstrap(sides, stat))}
        out[m] = res
    return out


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    ids = {k: list(g[B.GROUP_KEY[k]]) for k in B.SIZES}
    group_of = {d: k for k, lst in ids.items() for d in lst}
    nt = [d for d in ids["S1t"] if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    h = [d for d in ids["S2"] if gold.brief_type(data[d]) == "hotel"]
    assert (len(nt), len(h)) == (807, 233)
    G = V.gots(data, group_of)
    out = {"post_hoc": True, "note": "final-4 analyses of the repairs; see the docstring"}
    out["part_a"] = part_a(G, data, nt, h)
    print("part A done", flush=True)
    out["display"], out["visibility_cost"] = display_parts(G, data, db, nt, h)
    print("parts B and C done", flush=True)
    out["worst_case_cut"] = worst_case(G, data, db, nt, h)
    print("part D done", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, default=lambda x: "inf" if x == INF else str(x)))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
