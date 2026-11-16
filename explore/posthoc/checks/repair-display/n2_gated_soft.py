"""SPEC-N2-gated-soft.md: one verifier-gated soft type filter on the development dialogues of Table 3.

Exploratory: a new policy, defined in the spec before this script ran, on reused development dialogues.
No model call, no network call, no paid call. Data loaders: verify.py of the independent check (not in this repository) (refuses em* folders);
display code: r10/analysis/repair_rule.py (imported without change).

Usage (from explore/):
    python3 -I posthoc/checks/repair-display/n2_gated_soft.py
Output: posthoc/checks/repair-display/out/n2_gated_soft.json
"""
import collections
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]  # explore/ of the repository
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out" / "n2_gated_soft.json"
MODELS9 = ("sonnet", "haiku", "sol", "luna", "opus", "astra", "deepseek", "qwen", "gemma")
COMPARATORS = ("verify", "relax_any", "soft")


def ho(t):
    return isinstance(t, tuple) and "hotel" in t and "guesthouse" not in t


def gated_display(search, f0, answer):
    """(shown, searches, triggered, widened) for the frozen policy G of the spec. `search(fields)` returns venues in
    venue-data order. The brief, label and word rule never enter."""
    d0 = search(f0)[:5]
    if not ho(f0.get("type")) or len(d0) >= 5:
        return d0, 1, False, False
    if answer != "no":  # "yes", "unclear", and (operationally) invalid or missing answers keep the display
        return d0, 1, True, False
    shown, names = list(d0), {v["name"] for v in d0}
    for v in search({**f0, "type": None}):
        if len(shown) >= 5:
            break
        if v["name"] not in names:
            shown.append(v)
            names.add(v["name"])
    return shown, 2, True, True


def is_prefix(d0, d):
    return [v["name"] for v in d][:len(d0)] == [v["name"] for v in d0]


def has_gh(shown):
    return any(v["type"] == "guesthouse" for v in shown)


def load_f5():
    saved = sys.argv
    sys.argv = sys.argv[:1]  # repair_rule reads sys.argv at import
    spec = importlib.util.spec_from_file_location("nf5", ROOT / "r10/analysis/repair_rule.py")
    f5 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f5)
    sys.argv = saved
    return f5


def evaluate(F5, got, data, db, nt, h, stated):
    bs, B, mean = F5.bs, F5.B, F5.mean
    search = lambda f: bs.search(db, f)  # noqa: E731
    per = collections.defaultdict(dict)  # (side, policy) -> {d: mean miss}
    gh_new = collections.defaultdict(lambda: {"stated": 0.0, "not_stated": 0.0})
    cnt = collections.Counter()
    for side, ids, want in (("nt", nt, False), ("h", h, True)):
        for d in ids:
            f0_reads = B.reads_of(got, d, "f0")
            reads = F5.base_reads(got, d)
            for rd in f0_reads:
                if rd in reads:
                    continue
                cnt["left_out_original_invalid" if got.get((d, "f0", rd)) is None else "left_out_verifier_invalid"] += 1
            if not reads:
                cnt[f"dialogues_without_base_answer_{side}"] += 1
                continue
            brief = bs.brief_of(data[d])
            acc, acc_gh = collections.defaultdict(list), collections.defaultdict(list)
            for rd in reads:
                f0 = got[(d, "f0", rd)]
                ans = got[(d, "verify", rd)]["answer"]
                assert ans in ("yes", "no", "unclear"), ans
                d0, _ = F5.show(db, f0, "original")
                g, n_search, trig, wid = gated_display(search, f0, ans)
                soft, _ = F5.show(db, f0, "soft")
                cnt["answers"] += 1
                cnt["triggered"] += trig
                cnt["second_search"] += wid
                cnt["prefix_violation_G"] += not is_prefix(d0, g)
                cnt["prefix_violation_soft"] += not is_prefix(d0, soft)
                names_g = [v["name"] for v in g]
                if names_g == [v["name"] for v in d0]:
                    cnt["G_equals_original"] += 1
                elif names_g == [v["name"] for v in soft]:
                    cnt["G_equals_soft"] += 1
                else:
                    cnt["G_other"] += 1
                if wid and not ho(f0["type"]):
                    cnt["widened_without_hotel_only"] += 1
                acc["original"].append(0.0 if F5.sees(d0, brief, want) else 1.0)
                acc["G"].append(0.0 if F5.sees(g, brief, want) else 1.0)
                if side == "h":
                    acc_gh["G"].append(float(has_gh(g) and not has_gh(d0)))
                for p in COMPARATORS:
                    f = F5.policy_answer(got, d, rd, p, stated[d])
                    shown, _ = F5.show(db, f, p)
                    acc[p].append(0.0 if F5.sees(shown, brief, want) else 1.0)
                    if side == "h":
                        acc_gh[p].append(float(has_gh(shown) and not has_gh(d0)))
            for p, vals in acc.items():
                per[(side, p)][d] = mean(vals)
            if side == "h":
                key = "stated" if stated[d] else "not_stated"
                for p, vals in acc_gh.items():
                    gh_new[p][key] += mean(vals)
    o_nt, o_h = per[("nt", "original")], per[("h", "original")]
    res = {"dialogues": {"nt": len(o_nt), "h": len(o_h), "h_stated": sum(1 for d in o_h if stated[d])},
           "original": {"failures": sum(o_nt.values()), "losses": sum(o_h.values())},
           "counts": dict(cnt), "policies": {}}
    for p in ("G",) + COMPARATORS:
        a_nt, a_h = per[("nt", p)], per[("h", p)]
        pnt = [(o_nt[d], a_nt[d]) for d in o_nt]
        ph = [(o_h[d], a_h[d]) for d in o_h]
        res["policies"][p] = {
            "net_avoided": sum(x - y for x, y in pnt), "failures_ended": sum(max(x - y, 0) for x, y in pnt),
            "failures_caused": sum(max(y - x, 0) for x, y in pnt), "gross_losses": sum(max(y - x, 0) for x, y in ph),
            "gross_gains": sum(max(x - y, 0) for x, y in ph), "net_added": sum(y - x for x, y in ph),
            "guesthouse_newly_shown": dict(gh_new[p])}
    units = [(per[("nt", "verify")][d], per[("nt", "soft")][d], per[("nt", "G")][d]) for d in o_nt]
    for name, k in (("G_minus_verify", 0), ("G_minus_soft", 1)):
        def stat(gr, k=k):
            return sum(u[k] - u[2] for u in gr["nt"])  # fewer failures under G = more avoided by G
        res[name] = list(F5.stats.cluster_bootstrap({"nt": units}, stat))
    a = res["answers"] = cnt["answers"]
    res["conditional_calls_share"] = cnt["triggered"] / a
    res["second_search_share"] = cnt["second_search"] / a
    res["historical_calls_per_answer"] = 1.0
    return res


def main():
    F5 = load_f5()
    data, g = F5.runs.context()
    db = F5.gold.hotel_db()
    ids = {k: list(g[F5.B.GROUP_KEY[k]]) for k in F5.B.SIZES}
    group_of = {d: k for k, lst in ids.items() for d in lst}
    nt = [d for d in ids["S1t"] if F5.gold.brief_type(data[d]) is None and F5.gold.brief_type(data[d], "fail_info") is None]
    h = [d for d in ids["S2"] if F5.gold.brief_type(data[d]) == "hotel"]
    assert (len(nt), len(h)) == (807, 233)
    every = sorted(set(d for lst in ids.values() for d in lst))
    stated = {d: F5.cr.label(data[d]) == "hotel_only" for d in every}
    assert sum(stated[d] for d in h) == 89
    G = F5.V.gots(data, group_of)
    f5j = json.loads((ROOT / "r10/analysis/out/repair_rule.json").read_text())["part4_display"]
    pa = json.loads((ROOT / "posthoc/checks/repair-counts/out/plan_counts.json").read_text())[
        "part_a_explicit_constraint_displays"]
    out = {"spec": "SPEC-N2-gated-soft.md", "status": "exploratory; new policy on reused development dialogues",
           "models": {}, "self_check": {}}
    for m in MODELS9:
        r = evaluate(F5, G[m], data, db, nt, h, stated)
        checks = {}
        for p in COMPARATORS:
            s = f5j[m][p]
            checks[p] = (abs(r["policies"][p]["net_avoided"] - s["net_avoided"]) < 1e-9
                         and abs(r["policies"][p]["net_added"] - s["net_added"]) < 1e-9
                         and abs(r["policies"][p]["gross_losses"] - s["losses_caused"]) < 1e-9
                         and abs(r["policies"][p]["gross_gains"] - s["losses_ended"]) < 1e-9
                         and abs(r["policies"][p]["guesthouse_newly_shown"]["stated"]
                                 - pa[m]["newly_shows_guesthouse"][p]["stated"]) < 1e-9)
        checks["original"] = (abs(r["original"]["failures"] - f5j[m]["original"]["failures"]) < 1e-9
                              and abs(r["original"]["losses"] - f5j[m]["original"]["losses"]) < 1e-9)
        out["self_check"][m] = checks
        if not all(checks.values()):
            OUT.parent.mkdir(exist_ok=True)
            OUT.write_text(json.dumps(out, indent=1))
            sys.exit(f"Stopped: the self-check failed for {m}: {checks}")
        out["models"][m] = r
        P = r["policies"]
        print(f"{m:8} nt {r['dialogues']['nt']} h {r['dialogues']['h']} st {r['dialogues']['h_stated']} | avoided G "
              f"{P['G']['net_avoided']:g} V {P['verify']['net_avoided']:g} S {P['soft']['net_avoided']:g} | G-V "
              f"{[round(x, 2) for x in r['G_minus_verify']]} G-S {[round(x, 2) for x in r['G_minus_soft']]} | H lost/gained "
              f"{P['G']['gross_losses']:g}/{P['G']['gross_gains']:g} | gh stated G {P['G']['guesthouse_newly_shown']['stated']:g}"
              f" S {P['soft']['guesthouse_newly_shown']['stated']:g} V {P['verify']['guesthouse_newly_shown']['stated']:g}"
              f" | calls {100 * r['conditional_calls_share']:.1f}% 2nd {100 * r['second_search_share']:.1f}% | "
              f"{ {k: v for k, v in r['counts'].items() if k != 'answers'} }", flush=True)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
