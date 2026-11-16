"""Post hoc analyses of the repairs, final-8 round (2026-11-15). No model call, no network, no paid call.

This file is a copy of the project analysis (an internal file) with the paths of the study folder and neutral
names; the results are the same. Usage (from explore/): .venv/bin/python -I r10/analysis/repair_limits.py
Output: r10/analysis/out/repair_limits.json.

Data: the same stored training-set answers as repair_rule.py (whose functions this script imports, so every
display outcome is computed by the same code), and the stored result files of the paper's Tables D1, D10, D12, D13
and D16. The script opens no folder whose name starts with "em", no sealed file, no key file and no .env file.

Part 1. Counts of models that meet a limit, at the point estimate and with the whole 95% interval.
  (a) The planned verifier and the clear-no gate against the word rule, the reader majority and the brief (Table D13;
      stored repair_refs.json part_a), with both traveller mixes: the evaluated mix (233 hotel to 807 no-type
      dialogues, "set") and the label-group mix (545 to 994, "group"). "Meets" = share removed >= 50% and ratio <= 0.30.
      "Whole interval meets" = the low end of the share-removed interval >= 50% and the high end of the ratio interval
      <= 0.30. The share-removed interval is new here: the same cluster bootstrap as repair_refs.py (groups nt, st, ns;
      2,000 draws, seed 20261112). The group-mix interval of the brief ratio is the set-mix interval times the constant
      (545 / 233) / (994 / 807).
  (b) The display loss ratio of the planned verifier and the clear-no gate (Table D12: search_sym.json; Table D10:
      trade_prospective.json), both mixes: point below 0.30, and whole interval below 0.30 (no 50% condition).
  (c) The trade rule against the label (Table D1: b_hotel_only.json): the clear-no gate on Sol and Astra.
  (d) The word rule as a repair against the reader majority, and the full reassignment (Table D16; repair_rule.json),
      with new share-removed intervals (cluster bootstrap inside each brief set, seed 20261112).
Part 3. The label-group-mix values of the main text that are derived from stored outputs (no new resampling): the
  rename ratios (the stored values of the independent check, out/repair_rename_check.json: verify_out.json item3 dev_pooled, "word rule, all 233" and "reader majority (5 of 9, read 1)"; each
  ratio and interval times the constant above, because the bootstrap keeps the set sizes fixed); the planned verifier
  against the brief, the word rule and the reader majority (repair_refs.json part_a); the word rule as a repair against
  the brief (repair_rule.json part2); the display loss ratios of the planned verifier (Tables D10 and D12 files) and of
  the word rule and always removing (repair_rule.json part4); and their evaluated-mix ranges.
Part 2. Table 3: paired differences of net visible failures avoided on the no-type briefs, relaxation policy minus
  verifier and soft type filter minus verifier, in dialogue counts (models with two answers: the mean of the two).
  95% interval: cluster bootstrap of dialogues (2,000 draws, seed 20261112), each dialogue keeps its answers.
  Self-check: the avoided counts equal repair_rule.json part4_display.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
sys.path.insert(0, str(HERE))
import repair_rule as F5  # noqa: E402  (imports repair_loaders.py, which sets the project paths)

V, B, bs, cr, gold, runs, stats = F5.V, F5.B, F5.bs, F5.cr, F5.gold, F5.runs, F5.stats
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "out" / "repair_limits.json"
F4 = json.loads((HERE / "out" / "repair_refs.json").read_text())
F5J = json.loads((HERE / "out" / "repair_rule.json").read_text())
R10 = HERE / "out"
FACTOR = (545 / 233) / (994 / 807)
MODELS9 = ("sonnet", "haiku", "sol", "luna", "opus", "astra", "deepseek", "qwen", "gemma")
GATES = {"verifier, planned gate": "verify", "verifier, clear-no gate": B.POSTHOC}
INF = float("inf")


def num(x):
    return INF if x == "inf" else float(x)


def value_cells(got, ids, arm):
    """As repair_refs.value_cells: per dialogue, mean hotel-only of original and gate over reads valid in both."""
    out = {}
    for d in ids:
        a, b = [], []
        for rd in B.reads_of(got, d, "verify"):
            f0, x = got.get((d, "f0", rd)), B.scored(got, d, arm, rd)
            if f0 is not None and x is not None:
                a.append(F5.ho(f0["type"]))
                b.append(F5.ho(x["type"]))
        if a:
            out[d] = (F5.mean(a), F5.mean(b))
    return out


def share_removed_ci(groups):
    def stat(g):
        orig = sum(a for a, _ in g["nt"])
        return sum(a - b for a, b in g["nt"]) / orig if orig > 0 else -INF
    return list(stats.cluster_bootstrap(groups, stat))


def part1a(G, data, nt, h):
    rule = {d: cr.label(data[d]) == "hotel_only" for d in h}
    out = {}
    for m in MODELS9:
        got = G[m]
        row = {}
        for gname, arm in GATES.items():
            st = F4["part_a"][m][gname]
            c_nt, c_h = value_cells(got, nt, arm), value_cells(got, h, arm)
            removed = sum(a - b for a, b in c_nt.values())
            assert abs(removed - st["removed"]) < 1e-9, (m, gname)
            g = {"nt": list(c_nt.values()), "st": [p for d, p in c_h.items() if rule[d]],
                 "ns": [p for d, p in c_h.items() if not rule[d]]}
            rem_ci = share_removed_ci(g)
            assert abs(rem_ci[0] - st["share_removed"]) < 1e-9
            e = {"share_removed_ci": rem_ci}
            for ref in ("word rule", "reader majority (5 of the other 8)", "brief"):
                if ref == "brief":
                    w = st["word rule"]
                    s_ci = w["brief_ci"]
                    g_ci = [x * FACTOR for x in s_ci]
                    s, gp = w["brief"], w["brief_group"]
                else:
                    w = st[ref]
                    s, s_ci, gp, g_ci = w["T1"], w["T1_ci"], w["T1_group"], w["T1_group_ci"]
                assert abs(gp - s * FACTOR) < 1e-9, (m, gname, ref)
                cell = {}
                for mix, (pt, ci) in (("set", (s, s_ci)), ("group", (gp, g_ci))):
                    cell[mix] = {"ratio": pt, "ci": [ci[1], ci[2]] if len(ci) == 3 else ci[:2],
                                 "meets_point": bool(rem_ci[0] >= 0.5 and pt <= 0.30),
                                 "meets_whole": bool(rem_ci[1] >= 0.5 and (ci[2] if len(ci) == 3 else ci[1]) <= 0.30)}
                e[ref] = cell
            row[gname] = e
        out[m] = row
    counts = {}
    for gname in GATES:
        for ref in ("word rule", "reader majority (5 of the other 8)", "brief"):
            for mix in ("set", "group"):
                pts = [m for m in MODELS9 if out[m][gname][ref][mix]["meets_point"]]
                whole = [m for m in MODELS9 if out[m][gname][ref][mix]["meets_whole"]]
                counts[f"{gname} | {ref} | {mix}"] = {"point": len(pts), "point_models": pts,
                                                      "whole": len(whole), "whole_models": whole}
    return {"models": out, "counts": counts}


def part1b():
    six = json.loads((R10 / "search_sym.json").read_text())["models"]
    three = json.loads((R10 / "trade_prospective.json").read_text())["models"]
    rows = {}
    for m in MODELS9[:6]:
        for arm in ("verify", "verify_no_only (post hoc)"):
            c = six[m][arm]
            rows[(m, arm)] = {"set": (c["subset"]["ratio"], c["subset"]["ci"]),
                              "group": (c["groups"]["ratio"], c["groups"]["ci"])}
    for m in MODELS9[6:]:
        for arm in ("verify", "verify_no_only (post hoc)"):
            c = three[m]["gates"][arm]
            rows[(m, arm)] = {"set": (c["subset"]["ratio"], c["subset"]["ci"]),
                              "group": (c["groups"]["ratio"], c["groups"]["ci"])}

    def below(v):
        return v is not None and num(v) <= 0.30

    out = {}
    for arm in ("verify", "verify_no_only (post hoc)"):
        for part, members in (("six models (post hoc)", MODELS9[:6]), ("three open models (fixed)", MODELS9[6:])):
            for mix in ("set", "group"):
                pts, whole = [], []
                for m in members:
                    r, ci = rows[(m, arm)][mix]
                    if r is None or num(r) == INF:  # "avoids none"
                        continue
                    if below(r):
                        pts.append(m)
                    if ci is not None and below(ci[1]):
                        whole.append(m)
                out[f"{arm} | {part} | {mix}"] = {"point": len(pts), "point_models": pts, "whole": len(whole),
                                                  "whole_models": whole}
    detail = {f"{m} | {a}": {k: [v[0], v[1]] for k, v in d.items()} for (m, a), d in rows.items()}
    return {"counts": out, "values": detail}


def part1c():
    b = json.loads((R10 / "b_hotel_only.json").read_text())
    out = {}
    for m in ("sol", "astra"):
        t = b["models"][m]["trade"][B.POSTHOC] if "models" in b else b[m]["trade"][B.POSTHOC]
        out[m] = t
    return out


def part1d(G, data, nt, h):
    every = sorted(set(nt) | set(h))
    stated = {d: cr.label(data[d]) == "hotel_only" for d in every}
    p2, p3 = F5J["part2_word_rule_repair"], F5J["part3_full_text_reassignment"]
    out = {}
    for m in MODELS9:
        got = G[m]
        ntp = F5.value_pairs(got, nt, "word_rule", stated)
        hp = F5.value_pairs(got, h, "word_rule", stated)
        g = {"nt": list(ntp.values()), "h": list(hp.values())}
        wr_rem_ci = share_removed_ci(g)
        maj = p2[m]["word_rule"]["majority"]
        e = {"word_rule_repair": {"share_removed_ci": wr_rem_ci,
                                  "majority_set": [maj["set"], *maj["set_ci"][1:]],
                                  "majority_group": [maj["group"], *maj["group_ci"][1:]]}}
        # full reassignment, planned verifier: share removed on the not-stated units, with its interval
        vnt = F5.value_pairs(got, nt, "verify", stated)
        vh = F5.value_pairs(got, h, "verify", stated)
        groups = {"nt": [(a, b, stated[d]) for d, (a, b) in vnt.items()],
                  "h": [(a, b, stated[d]) for d, (a, b) in vh.items()]}

        def rem_stat(gr):
            u = gr["nt"] + gr["h"]
            orig = sum(a for a, b, s in u if not s)
            return sum(a - b for a, b, s in u if not s) / orig if orig > 0 else -INF
        rr = list(stats.cluster_bootstrap(groups, rem_stat))
        full = p3[m]["verify"]
        assert abs(rr[0] - full["share_removed"]) < 1e-9
        e["full_reassignment_verify"] = {"share_removed_ci": rr, "ratio_ci": [num(x) for x in full["ratio_ci"]]}
        out[m] = e

    def cnt(f):
        ms = [m for m in MODELS9 if f(out[m])]
        return {"n": len(ms), "models": ms}
    counts = {
        "word rule as a repair vs majority, set: point": cnt(lambda e: e["word_rule_repair"]["share_removed_ci"][0] >= .5 and num(e["word_rule_repair"]["majority_set"][0]) <= .30),
        "word rule as a repair vs majority, set: whole": cnt(lambda e: e["word_rule_repair"]["share_removed_ci"][1] >= .5 and num(e["word_rule_repair"]["majority_set"][2]) <= .30),
        "word rule as a repair vs majority, group: point": cnt(lambda e: e["word_rule_repair"]["share_removed_ci"][0] >= .5 and num(e["word_rule_repair"]["majority_group"][0]) <= .30),
        "word rule as a repair vs majority, group: whole": cnt(lambda e: e["word_rule_repair"]["share_removed_ci"][1] >= .5 and num(e["word_rule_repair"]["majority_group"][2]) <= .30),
        "full reassignment, planned verifier: point": cnt(lambda e: e["full_reassignment_verify"]["share_removed_ci"][0] >= .5 and e["full_reassignment_verify"]["ratio_ci"][0] <= .30),
        "full reassignment, planned verifier: whole": cnt(lambda e: e["full_reassignment_verify"]["share_removed_ci"][1] >= .5 and e["full_reassignment_verify"]["ratio_ci"][2] <= .30),
    }
    return {"models": out, "counts": counts}


def part2(G, data, db, nt, h):
    every = sorted(set(nt) | set(h))
    stated = {d: cr.label(data[d]) == "hotel_only" for d in every}
    stored = F5J["part4_display"]
    out = {}
    for m in MODELS9:
        got = G[m]
        per = {p: {} for p in ("original", "verify", "relax_any", "soft")}
        for d in nt:
            brief = bs.brief_of(data[d])
            acc = {p: [] for p in per}
            for rd in F5.base_reads(got, d):
                for p in per:
                    f = F5.policy_answer(got, d, rd, p, stated[d])
                    shown, _n = F5.show(db, f, p)
                    acc[p].append(0.0 if F5.sees(shown, brief, False) else 1.0)
            if acc["original"]:
                for p in per:
                    per[p][d] = F5.mean(acc[p])
        ids = list(per["original"])
        avoided = {p: sum(per["original"][d] - per[p][d] for d in ids) for p in ("verify", "relax_any", "soft")}
        for p in avoided:
            assert abs(avoided[p] - stored[m][p]["net_avoided"]) < 1e-9, (m, p, avoided[p], stored[m][p]["net_avoided"])
        units = [(per["verify"][d], per["relax_any"][d], per["soft"][d]) for d in ids]
        e = {"dialogues": len(ids), "avoided": avoided}
        for name, k in (("relax_minus_verify", 1), ("soft_minus_verify", 2)):
            def stat(g, k=k):
                return sum(u[0] - u[k] for u in g["nt"])  # fewer failures under the policy = more avoided
            pt, lo, hi = stats.cluster_bootstrap({"nt": units}, stat)
            assert abs(pt - (avoided["relax_any" if k == 1 else "soft"] - avoided["verify"])) < 1e-9
            e[name] = [pt, lo, hi]
        out[m] = e
    return out


def part3():
    V3 = json.loads((R10 / "repair_rename_check.json").read_text())["item3"]["dev_pooled"]
    out = {"rename": {}}
    for key, name in (("word rule, all 233", "word rule"), ("reader majority (5 of 9, read 1)", "reader majority")):
        e = V3[key]
        out["rename"][name] = {"dialogues": e["dialogues"],
                               "brief_evaluated": e["brief"], "brief_label_group": [x * FACTOR for x in e["brief"]],
                               "text_evaluated": e["T1"], "text_label_group": [x * FACTOR for x in e["T1"]]}
    pa = F4["part_a"]
    out["verifier_planned"] = {m: {"brief_group": pa[m]["verifier, planned gate"]["word rule"]["brief_group"],
                                   "word_rule_group": pa[m]["verifier, planned gate"]["word rule"]["T1_group"],
                                   "word_rule_group_ci": pa[m]["verifier, planned gate"]["word rule"]["T1_group_ci"],
                                   "majority_group": pa[m]["verifier, planned gate"]["reader majority (5 of the other 8)"]["T1_group"]}
                               for m in MODELS9}
    p2, p4 = F5J["part2_word_rule_repair"], F5J["part4_display"]
    wr = {m: p2[m]["word_rule"]["brief"] for m in MODELS9}
    out["word_rule_repair_brief"] = {"group": [min(v["group"] for v in wr.values()), max(v["group"] for v in wr.values())],
                                     "evaluated": [min(v["set"] for v in wr.values()), max(v["set"] for v in wr.values())]}
    for pol in ("word_rule", "always"):
        g = {m: num(p4[m][pol]["group_ratio"][0]) for m in MODELS9}
        st = {m: num(p4[m][pol]["set_ratio"][0]) for m in MODELS9}
        out["display_" + pol] = {"group": [min(g.values()), max(g.values())], "evaluated": [min(st.values()), max(st.values())],
                                 "group_by_model": g}
    sixr = json.loads((R10 / "search_sym.json").read_text())["models"]
    thr = json.loads((R10 / "trade_prospective.json").read_text())["models"]
    out["display_verifier_group"] = {**{m: [sixr[m]["verify"]["groups"]["ratio"], *sixr[m]["verify"]["groups"]["ci"]] for m in MODELS9[:6]},
                                     **{m: [thr[m]["gates"]["verify"]["groups"]["ratio"], *thr[m]["gates"]["verify"]["groups"]["ci"]] for m in MODELS9[6:]}}
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
    out = {"post_hoc": True, "note": "final-8 analyses of the repairs; see the docstring", "factor": FACTOR}
    out["part1a_text_reference"] = part1a(G, data, nt, h)
    print("part 1a done", flush=True)
    out["part1b_display"] = part1b()
    out["part1c_label_clear_no"] = part1c()
    out["part1d_word_rule_repair_and_full"] = part1d(G, data, nt, h)
    print("part 1d done", flush=True)
    out["part3_main_text_values"] = part3()
    out["part2_table3_paired"] = part2(G, data, db, nt, h)
    print("part 2 done", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, default=lambda x: "inf" if x == INF else str(x)))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
