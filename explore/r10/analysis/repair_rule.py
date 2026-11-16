"""Post hoc analyses of the repairs, final-5 round (2026-11-14). No model call, no network, no paid call.

This file is a copy of the project analysis (an internal file) with the paths of the study folder and neutral
names; the results are the same. Usage (from explore/): .venv/bin/python -I r10/analysis/repair_rule.py
Output: r10/analysis/out/repair_rule.json.

Data: the stored development answers of the final-4 analysis (the repair folders that b_analyze.SOURCES names, and
ery_deepseek, ery_qwen, ery_gemma), loaded with the loaders of the independent check (repair_loaders.py), which use the
project's own parsers, search code and word rule. The script refuses any folder whose name starts with "em". It opens
no sealed file, no key file and no .env file. It imports no script of workshops/proposal-*.

Sets: the 807 development dialogues where the brief and the label set no type ("nt") and the 233 where both set
`hotel` ("h"). A hotel-only value is a `type` list that holds `hotel` and not `guesthouse` (the paper's main count).
Base answers: as in the paper's Table 3, a read counts only when its original-form answer and its verifier answer are
both valid, so every policy uses the same answers.

Part 1. Cross-tabulation of the brief type and the word rule (clear_rule.label) on the evaluated sets and the label
        groups.
Part 2. The word rule as a symbolic repair: a hotel-only filter stays only when the word rule marks the dialogue as
        "stated" (hotel_only); otherwise it becomes null. Value level on the 807 and 233 (share removed, loss ratios
        against the brief, the word rule and the reader majority, set and label-group sizes), and the trade rule
        against the label on the three label groups (994, 490, 545; main count; pooled shares as b_analyze does).
        The planned verifier is computed by the same code as a check against the paper's Tables D1 and D13.
Part 3. A full text reassignment over all 1,040 dialogues: "stated" by the word rule decides support on both brief
        sets. Removals count on the not-stated dialogues; losses count on the stated ones.
Part 4. Display policies on the same original answers (five venues in file order): original, verifier (planned
        gate), relaxation policy (any type; as in Table 3), relaxation policy on hotel-only filters only, soft type
        filter, always remove, word-rule repair. Net visible failures avoided and visible losses added, the errors
        caused and ended, subset-weight ratio with a 95% interval, database searches and model calls per answer, and
        how often the relaxation policy changes the display of a hotel brief.
Part 5. Briefs with no fitting venue at all (807 no-type briefs) and with no fitting hotel (233 hotel briefs).
Part 6. Table D11 check: the share removed by the gates on the three open models, with answers pooled in the
        numerator and the denominator, next to the stored value.
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
sys.path.insert(0, str(HERE))
import repair_loaders as V  # noqa: E402  (sets the project import paths)

B, bs, cr, gold, runs, stats = V.B, V.bs, V.cr, V.gold, V.runs, V.stats
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "out" / "repair_rule.json"
INF = float("inf")
SUB, GRP = (233, 807), (545, 994)


def ho(t):
    return isinstance(t, tuple) and "hotel" in t and "guesthouse" not in t


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def base_reads(got, d):
    """Reads whose original answer and verifier answer are both valid (the base of Table 3)."""
    return [rd for rd in B.reads_of(got, d, "f0")
            if got.get((d, "f0", rd)) is not None and B.scored(got, d, "verify", rd) is not None]


def policy_answer(got, d, rd, policy, stated):
    f0 = got[(d, "f0", rd)]
    if policy in ("original", "relax_any", "relax_hotel_only", "soft"):
        return f0
    if policy == "verify":
        return B.scored(got, d, "verify", rd)
    if policy == "clear_no":
        return B.scored(got, d, B.POSTHOC, rd)
    if policy in ("always", "word_rule"):
        out = dict(f0)
        if ho(out["type"]) and not (policy == "word_rule" and stated):
            out["type"] = None
        return out
    raise ValueError(policy)


# ------------------------------------------------------------------------------------------------ part 1
def part1(data, sets):
    out = {}
    for name, ids in sets.items():
        c = collections.Counter(cr.label(data[d]) for d in ids)
        out[name] = {"dialogues": len(ids), **{k: c.get(k, 0) for k in cr.LABELS}}
    return out


# ------------------------------------------------------------------------------------------------ part 2
def value_pairs(got, ids, policy, stated):
    """{d: (mean original hotel-only, mean policy hotel-only)} over the base reads."""
    out = {}
    for d in ids:
        a, b = [], []
        for rd in base_reads(got, d):
            a.append(ho(got[(d, "f0", rd)]["type"]))
            b.append(ho(policy_answer(got, d, rd, policy, stated[d])["type"]))
        if a:
            out[d] = (mean(a), mean(b))
    return out


def ratio_forms(nt_pairs, h_pairs, supported):
    """Loss per value removed: lost on the hotel dialogues with supported(d) / removed on the 807. Raw, set sizes and
    label-group sizes. supported None = every hotel dialogue (the brief)."""
    removed = sum(a - b for a, b in nt_pairs.values())
    lost = sum(a - b for d, (a, b) in h_pairs.items() if supported is None or supported(d))
    n_nt, n_h = len(nt_pairs), len(h_pairs)
    res = {"removed": removed, "lost": lost, "raw": lost / removed if removed > 0 else INF}
    for w, (wh, wnt) in (("set", SUB), ("group", GRP)):
        res[w] = (lost / n_h * wh) / (removed / n_nt * wnt) if removed > 0 else INF
    return res


def boot(nt_pairs, h_pairs, supported, w):
    wh, wnt = SUB if w == "set" else GRP
    groups = {"nt": list(nt_pairs.values()), "h": [(a, b, supported is None or supported(d)) for d, (a, b) in h_pairs.items()]}

    def stat(g):
        rem = sum(a - b for a, b in g["nt"]) / len(g["nt"])
        lost = sum(a - b for a, b, s in g["h"] if s) / len(g["h"])
        return lost * wh / (rem * wnt) if rem > 0 else INF
    return list(stats.cluster_bootstrap(groups, stat))


def label_trade(got, ids_by_group, policy, stated):
    """The trade rule against the label on the three label groups (main count), pooled shares as stats.trade."""
    cells = {}
    for grp, ids in ids_by_group.items():
        rows_ = []
        for d in ids:
            reads = base_reads(got, d)
            if reads:
                a = [ho(got[(d, "f0", rd)]["type"]) for rd in reads]
                b = [ho(policy_answer(got, d, rd, policy, stated[d])["type"]) for rd in reads]
                rows_.append((sum(a), len(a), sum(b), len(b)))
        cells[grp] = rows_
    (removed, lost, ratio), lo, hi = stats.trade_interval(cells, B.SIZES)
    f0_wrong = sum(sum(r[0] for r in cells[g]) / sum(r[1] for r in cells[g]) * B.SIZES[g] for g in ("S1t", "S3"))
    share = removed / f0_wrong if f0_wrong > 0 else None
    return {"removed_share": share, "ratio": ratio if removed > 0 else None, "ci": [lo, hi] if removed > 0 else None,
            "meets_rule": bool(share is not None and removed > 0 and share >= 0.5 and 0 <= ratio <= 0.30),
            "dialogues": {g: len(cells[g]) for g in cells}}


def reader_majority(G, h):
    votes = collections.defaultdict(dict)
    for m, got in G.items():
        for d in h:
            v = got.get((d, "verify", 1))
            if v is not None:
                votes[d][m] = v["answer"]
    return {m: {d: sum(a == "yes" for mm, a in votes[d].items() if mm != m) >= 5 for d in h} for m in G}


def part2(G, data, nt, h, ids_by_group, stated, maj):
    out = {}
    for m, got in G.items():
        row = {}
        for policy in ("word_rule", "verify", "always"):
            ntp, hp = value_pairs(got, nt, policy, stated), value_pairs(got, h, policy, stated)
            f0_nt = sum(a for a, _ in ntp.values())
            e = {"dialogues": [len(ntp), len(hp)], "share_removed": sum(a - b for a, b in ntp.values()) / f0_nt}
            for rname, sup in (("brief", None), ("word_rule", lambda d: stated[d]), ("majority", lambda d: maj[m][d])):
                r = ratio_forms(ntp, hp, sup)
                r["set_ci"] = boot(ntp, hp, sup, "set")
                r["group_ci"] = boot(ntp, hp, sup, "group")
                r["meets_set"] = bool(e["share_removed"] >= 0.5 and r["set"] <= 0.30)
                r["meets_group"] = bool(e["share_removed"] >= 0.5 and r["group"] <= 0.30)
                e[rname] = r
            if m in B.SOURCES:
                e["label_trade_rule"] = label_trade(got, ids_by_group, policy, stated)
            row[policy] = e
        out[m] = row
    return out


# ------------------------------------------------------------------------------------------------ part 3
def part3(G, data, nt, h, stated):
    """Full text reassignment: every one of the 1,040 dialogues gets support from the word rule."""
    out = {}
    for m, got in G.items():
        row = {}
        for policy in ("verify", "clear_no", "word_rule"):
            ntp, hp = value_pairs(got, nt, policy, stated), value_pairs(got, h, policy, stated)
            units = [(a, b, stated[d]) for d, (a, b) in list(ntp.items()) + list(hp.items())]
            orig_ns = sum(a for a, b, s in units if not s)
            removed = sum(a - b for a, b, s in units if not s)
            lost = sum(a - b for a, b, s in units if s)
            groups = {"nt": [(a, b, stated[d]) for d, (a, b) in ntp.items()],
                      "h": [(a, b, stated[d]) for d, (a, b) in hp.items()]}

            def stat(g):
                u = g["nt"] + g["h"]
                rem = sum(a - b for a, b, s in u if not s)
                return sum(a - b for a, b, s in u if s) / rem if rem > 0 else INF
            row[policy] = {"stated_dialogues": sum(1 for *_, s in units if s),
                           "not_stated_dialogues": sum(1 for *_, s in units if not s),
                           "removed": removed, "lost": lost, "share_removed": removed / orig_ns if orig_ns else None,
                           "ratio_ci": list(stats.cluster_bootstrap(groups, stat)),
                           "meets": bool(orig_ns and removed / orig_ns >= 0.5 and (lost / removed if removed > 0 else INF) <= 0.30)}
        out[m] = row
    return out


# ------------------------------------------------------------------------------------------------ part 4
def show(db, fields, policy):
    """(displayed venues, database searches) for one answer under one display policy."""
    rows = bs.search(db, fields)
    t = fields.get("type")
    if policy in ("relax_any", "relax_hotel_only"):
        acts = not rows and t is not None and (policy == "relax_any" or ho(t))
        if acts:
            wide = bs.search(db, {**fields, "type": None})
            return (wide if wide else rows)[:5], 2
        return rows[:5], 1
    if policy == "soft":
        if len(rows) >= 5 or t is None:
            return rows[:5], 1
        shown = rows[:5]
        names = {v["name"] for v in shown}
        for v in bs.search(db, {**fields, "type": None}):
            if len(shown) >= 5:
                break
            if v["name"] not in names:
                shown.append(v)
                names.add(v["name"])
        return shown, 2
    return rows[:5], 1


def sees(shown, brief, want_hotel):
    return any(bs.fits(v, brief) and (v["type"] == "hotel" or not want_hotel) for v in shown)


POLICIES = ("original", "verify", "relax_any", "relax_hotel_only", "soft", "always", "word_rule")


def part4(G, data, db, nt, h, stated):
    out = {}
    for m, got in G.items():
        per = collections.defaultdict(dict)  # (side, policy) -> {d: mean miss}
        searches = collections.Counter()
        answers = 0
        relax_hotel = {"answers_changed": 0, "dialogues_changed": set(), "stated_dialogues_changed": set(),
                       "answers_changed_show_guesthouse": 0}
        for side, ids, want in (("nt", nt, False), ("h", h, True)):
            for d in ids:
                brief = bs.brief_of(data[d])
                acc = collections.defaultdict(list)
                for rd in base_reads(got, d):
                    answers += 1
                    for p in POLICIES:
                        f = policy_answer(got, d, rd, p, stated[d])
                        shown, n_search = show(db, f, p)
                        searches[p] += n_search
                        acc[p].append(0.0 if sees(shown, brief, want) else 1.0)
                        if side == "h" and p == "relax_any":
                            orig = bs.search(db, f)[:5]
                            if [v["name"] for v in shown] != [v["name"] for v in orig]:
                                relax_hotel["answers_changed"] += 1
                                relax_hotel["dialogues_changed"].add(d)
                                if stated[d]:
                                    relax_hotel["stated_dialogues_changed"].add(d)
                                relax_hotel["answers_changed_show_guesthouse"] += any(v["type"] == "guesthouse" for v in shown)
                for p, vals in acc.items():
                    per[(side, p)][d] = mean(vals)
        f_nt, f_h = per[("nt", "original")], per[("h", "original")]
        row = {"original": {"visible_failure": mean(f_nt.values()), "visible_loss": mean(f_h.values()),
                            "failures": sum(f_nt.values()), "losses": sum(f_h.values()),
                            "dialogues": [len(f_nt), len(f_h)]},
               "answers": answers,
               "searches_per_answer": {p: searches[p] / answers for p in POLICIES},
               "model_calls_per_answer": {p: (1.0 if p == "verify" else 0.0) for p in POLICIES},
               "relax_any_on_hotel_briefs": {"answers_changed": relax_hotel["answers_changed"],
                                             "dialogues_changed": len(relax_hotel["dialogues_changed"]),
                                             "stated_dialogues_changed": len(relax_hotel["stated_dialogues_changed"]),
                                             "answers_changed_show_guesthouse": relax_hotel["answers_changed_show_guesthouse"]}}
        for p in POLICIES[1:]:
            a_nt, a_h = per[("nt", p)], per[("h", p)]
            pnt = [(f_nt[d], a_nt[d]) for d in f_nt]
            ph = [(f_h[d], a_h[d]) for d in f_h]
            e = {"visible_failure": mean(a_nt.values()), "visible_loss": mean(a_h.values()),
                 "failures": sum(a_nt.values()), "losses": sum(a_h.values()),
                 "net_avoided": sum(x - y for x, y in pnt), "net_added": sum(y - x for x, y in ph),
                 "failures_caused": sum(max(y - x, 0) for x, y in pnt), "failures_ended": sum(max(x - y, 0) for x, y in pnt),
                 "losses_caused": sum(max(y - x, 0) for x, y in ph), "losses_ended": sum(max(x - y, 0) for x, y in ph)}
            for w, (wh, wnt) in (("set", SUB), ("group", GRP)):
                def stat(gr, wh=wh, wnt=wnt):
                    ben = sum(x - y for x, y in gr["nt"]) / len(gr["nt"])
                    cost = sum(y - x for x, y in gr["h"]) / len(gr["h"])
                    return cost * wh / (ben * wnt) if ben > 0 else INF
                e[w + "_ratio"] = list(stats.cluster_bootstrap({"nt": pnt, "h": ph}, stat))
            row[p] = e
        out[m] = row
    return out


# ------------------------------------------------------------------------------------------------ parts 5, 6
def part5(data, db, nt, h):
    no_venue = [d for d in nt if not any(bs.fits(v, bs.brief_of(data[d])) for v in db)]
    no_hotel = [d for d in h if not any(bs.fits(v, bs.brief_of(data[d])) and v["type"] == "hotel" for v in db)]
    return {"no_type_briefs_with_no_fitting_venue": len(no_venue), "of": len(nt),
            "hotel_briefs_with_no_fitting_hotel": len(no_hotel), "of_hotel": len(h)}


def part6(G, nt):
    out = {}
    stored = json.loads((HERE / "out" / "trade_prospective.json").read_text())["models"]
    for m in ("deepseek", "qwen", "gemma"):
        got = G[m]
        row = {}
        for gate, key in (("verify", "verify"), ("clear_no", B.POSTHOC)):
            k0 = k1 = n = 0
            for d in nt:
                for rd in B.reads_of(got, d, "verify"):
                    x = B.scored(got, d, key, rd)
                    if x is not None:
                        n += 1
                        k0 += ho(got[(d, "f0", rd)]["type"])
                        k1 += ho(x["type"])
            row[gate] = {"original_values": k0, "gate_values": k1, "answers": n,
                         "share_removed_pooled": (k0 - k1) / k0,
                         "stored_share_removed": stored[m]["descriptions"]["value_count"][key]["share_removed"]}
        out[m] = row
    return out


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    ids = {k: list(g[B.GROUP_KEY[k]]) for k in B.SIZES}
    group_of = {d: k for k, lst in ids.items() for d in lst}
    nt = [d for d in ids["S1t"] if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    h = [d for d in ids["S2"] if gold.brief_type(data[d]) == "hotel"]
    gh = [d for d in ids["S3"] if gold.brief_type(data[d]) == "guesthouse"]
    assert (len(nt), len(h), len(gh)) == (807, 233, 394)
    every = sorted(set(d for lst in ids.values() for d in lst))
    stated = {d: cr.label(data[d]) == "hotel_only" for d in every}
    G = V.gots(data, group_of)
    out = {"post_hoc": True, "note": "final-5 analyses of the repairs; see the docstring"}
    out["part1_cross_tab"] = part1(data, {"no-type briefs (807)": nt, "hotel briefs (233)": h,
                                          "guesthouse briefs (394)": gh, "label group no-type (994)": ids["S1t"],
                                          "label group guesthouse (490)": ids["S3"], "label group hotel (545)": ids["S2"]})
    maj = reader_majority(G, h)
    out["part2_word_rule_repair"] = part2(G, data, nt, h, ids, stated, maj)
    print("part 2 done", flush=True)
    out["part3_full_text_reassignment"] = part3(G, data, nt, h, stated)
    print("part 3 done", flush=True)
    out["part4_display"] = part4(G, data, db, nt, h, stated)
    print("part 4 done", flush=True)
    out["part5_no_fit"] = part5(data, db, nt, h)
    out["part6_table_d11"] = part6(G, nt)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, default=lambda x: "inf" if x == INF else str(x)))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
