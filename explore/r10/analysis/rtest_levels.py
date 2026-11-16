"""Final-5 analysis of the release test (post hoc, exploratory). Stored answers and stored result files only.

This file is a copy of the project analysis (an internal file) with the paths of the study folder and neutral names;
the results are the same. Usage (from explore/): python3 -I r10/analysis/rtest_levels.py
Output: r10/analysis/out/rtest_levels.json and rtest_levels.md.

Parts:
A. Interval levels. The paper states the level 1 - 0.05/C for each interval, with C = the number of intervals in one
   release decision (models x sets x looks). This part recomputes, at that level, the stored decisions of Table 4 and
   Table 15 whose answers are stored outside the held-out folders:
   A1 tool calls of Table 4 (one answer per prefix; the control updates keep 10 answers per specific prefix);
   A2 the exploratory rows of Table 15 (round-9 forms; tool calls with all stored answers);
   A3 the held-out rows of Table 15, as an approximation only: a normal approximation from the stored 95% intervals
      (the per-dialogue held-out answers are not read).
B. Zero-width intervals. A sensitivity analysis with an interval that keeps a width when no request changes: for a set
   with one answer per request, each paired difference is -100, 0 or +100 points. The interval is
   [100 (Lu - Ud), 100 (Uu - Ld)], where Lu, Uu are exact (Clopper-Pearson) one-sided bounds for the share of requests
   that rise and Ld, Ud for the share that fall, each at error (1 - level) / 4. By the union bound, the interval
   misses the true mean change with probability at most 1 - level. The rule itself does not change; this part reports
   the decisions that such an interval would give, next to the original decisions.
C. Error rates of the percentile interval near the limits, one answer per request on 59 requests (the specific set):
   exact enumeration over the counts of rises and falls, the rule's percentile bootstrap (2,000 draws) for each count.
   C1 wrong "within limits" when the true change is just above L; C2 wrong "meets flag rule" when the true change is 0.
D. Order of the two arms. The percentile index rule of stats.percentile takes, at 98.75% and 2,000 draws, the 12th
   lowest and the 13th highest resampled mean. This part recomputes the pairs whose decision depended on the order,
   with the original index rule and with a symmetric rule (12th lowest, 12th highest), with the same draws in both
   orders.

Safety: no model call, no network call. The loaders of verify.py refuse a folder whose name starts with "em". The
script opens no sealed file, no key file and no .env file.
"""
import collections
import itertools
import json
import math
import pathlib
import random
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
OUTDIR = HERE / "out"

sys.path.insert(0, str(HERE))
import rtest_v as V  # noqa: E402  (extract of the independent check: loaders and parsers)

L = 5.0
SEED, DRAWS = 20261112, 2000
MY_SEED = 20261117


def level(c):
    return 1 - 0.05 / c


def rnd(x, nd=4):
    return None if x is None else round(x, nd)


# ------------------------------------------------------------------------------------------------ intervals

def boot(diffs, lev, seed=SEED, sym=False):
    """The rule's percentile bootstrap over requests (same draws as stats.cluster_bootstrap for the same seed).
    sym=True: the k-th lowest and the k-th highest resampled mean, k = round(a x draws)."""
    n = len(diffs)
    rng = random.Random(seed)
    point = sum(diffs) / n
    vals = sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(DRAWS))
    a = (1 - lev) / 2
    if sym:
        k = max(1, int(round(a * DRAWS)))
        lo, hi = vals[k - 1], vals[DRAWS - k]
    else:
        lo, hi = V.stats.percentile(vals, a), V.stats.percentile(vals, 1 - a)
    up, down = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    return {"pairs": n, "change": point, "low": lo, "high": hi, "up": up, "down": down,
            "sign_p": V.sign_p(up, down), "three_point": all(x in (-100.0, 0.0, 100.0) for x in diffs)}


def binom_cdf(k, n, p):
    if p <= 0:
        return 1.0
    if p >= 1:
        return 1.0 if k >= n else 0.0
    lp, lq = math.log(p), math.log1p(-p)
    return min(1.0, sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp
                                 + (n - i) * lq) for i in range(k + 1)))


def cp_upper(k, n, a):
    """One-sided exact upper bound: the p with P(X <= k | n, p) = a."""
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if binom_cdf(k, n, mid) > a else (lo, mid)
    return hi


def cp_lower(k, n, a):
    """One-sided exact lower bound: the p with P(X >= k | n, p) = a."""
    if k <= 0:
        return 0.0
    return 1 - cp_upper(n - k, n, a)


def exact_interval(n, up, down, lev):
    a = (1 - lev) / 4
    lu, uu = cp_lower(up, n, a), cp_upper(up, n, a)
    ld, ud = cp_lower(down, n, a), cp_upper(down, n, a)
    return 100 * (lu - ud), 100 * (uu - ld)


def with_exact(s, lev):
    """The same set with the exact interval (only for one answer per request)."""
    assert s["three_point"], "exact interval needs one answer per request"
    lo, hi = exact_interval(s["pairs"], s["up"], s["down"], lev)
    return {**s, "low": lo, "high": hi}


# ------------------------------------------------------------------------------------------------ rule

def set_class(s, alpha=None, lim=L):
    """First rule (alpha None) or revised rule (sign p <= alpha)."""
    if abs(s["change"]) >= lim and (s["low"] > 0 or s["high"] < 0) and (alpha is None or s["sign_p"] <= alpha):
        return "meets flag rule"
    if -lim <= s["low"] and s["high"] <= lim:
        return "within limits"
    return "unresolved"


def model_dec(sets, alpha=None, lim=L):
    d = [set_class(s, alpha, lim) for s in sets if s is not None]
    if "meets flag rule" in d:
        return "flag"
    if len(d) == 2 and all(x == "within limits" for x in d):
        return "pass"
    return "hold"


def both_rules(o, s, lev, lim=L):
    return {"first": model_dec([o, s], None, lim), "revised": model_dec([o, s], 1 - lev, lim)}


def show(s):
    return {k: rnd(s[k]) for k in ("pairs", "change", "low", "high", "up", "down", "sign_p")}


def diffs_of(ctrl, upd, ids):
    return [100 * (V.mean(upd[d]) - V.mean(ctrl[d])) for d in ids if ctrl.get(d) and upd.get(d)]


# ------------------------------------------------------------------------------------------------ part A1

def part_a1(sets):
    out = {"definition": "C = models x 2 sets x 1 look for the models of the row; level 1 - 0.05/C. One-model "
                         "rows: C = 2 (97.5%). The prospective rows keep the level fixed in their protocols."}
    # unchanged tool, one answer per prefix: the 29 pairs of verify.py item 1
    ver = json.loads((HERE / "out" / "rtest_check_values.json").read_text())
    stored = {(e["model"], e["a"], e["b"]): e for e in ver["item1"]["aa"]["one_answer"]}
    rows, tally = [], collections.Counter()
    for m, srcs in V.AA.items():
        src = [(s_[0], V.tool_reads(s_[1], s_[2], s_[3])) for s_ in srcs]
        for (la, a), (lb, b) in itertools.combinations(src, 2):
            e = {"model": m, "a": la, "b": lb}
            for lev_name, lev in (("98.75", 0.9875), ("99.5", level(10)), ("97.5", level(2))):
                o = boot(diffs_of(a, b, sets["open"]), lev)
                s = boot(diffs_of(a, b, sets["specific"]), lev)
                dec = both_rules(o, s, lev)
                ex = both_rules(with_exact(o, lev), with_exact(s, lev), lev)
                e[lev_name] = {"open": show(o), "specific": show(s), **dec,
                               "exact_first": ex["first"], "exact_revised": ex["revised"],
                               "specific_zero_width": s["low"] == s["high"],
                               "exact_specific": [rnd(x, 2) for x in exact_interval(s["pairs"], s["up"], s["down"], lev)]}
                for k in ("first", "revised", "exact_first", "exact_revised"):
                    tally[(lev_name, k, e[lev_name][k])] += 1
            st = stored[(m, la, lb)]
            assert e["98.75"]["first"] == st["decision"], (m, la, lb)
            assert abs(e["98.75"]["specific"]["low"] - st["specific"]["low"]) < 1e-3
            rows.append(e)
    out["unchanged_pairs"] = rows
    out["unchanged_tally"] = {f"{a} {b}: {c}": v for (a, b, c), v in sorted(tally.items())}
    # edits with one answer per prefix (Table 4) and the control updates (10 answers per specific prefix)
    edits = {}
    for m in ("sonnet", "haiku", "opus", "sol", "astra", "luna"):
        edits[f"full rename, {m}"] = ("post hoc, 6 models", 12,
                                      V.tool_reads((f"era1_{m}",), "t0", 1), V.tool_reads((f"era1_{m}",), "t1", 1))
    for m in ("sonnet", "sol"):
        edits[f"broad rewrite, {m}"] = ("prospective, 2 models", 4,
                                        V.tool_reads((f"erp_{m}",), "t0", 1), V.tool_reads((f"erp_{m}",), "tedit", 1))
    sc, hc = V.tool_reads(("erp_sonnet",), "t0", 1), V.tool_reads(("ers_haiku",), "t0", 1)
    for c in ("th", "tg"):
        edits[f"steered {c}, sonnet"] = ("prospective, 2 models", 4, sc, V.tool_reads(("ers_sonnet",), c, 1))
        edits[f"steered {c}, haiku"] = ("prospective, 2 models", 4, hc, V.tool_reads(("ers_haiku",), c, 1))
    mc = V.tool_reads(("erm_haiku",), "t0", 1)
    for c in [f"{g}{i}" for g in "hgn" for i in (1, 2, 3)]:
        edits[f"rewrite {c}, haiku"] = ("post hoc, 1 model", 2, mc, V.tool_reads(("erm_haiku",), c, 1))
    cc = V.tool_reads(("erc_haiku",), "t0", None)
    edits["field order (10 answers), haiku"] = ("prospective, 1 model, 2 updates", 4, cc,
                                                V.tool_reads(("erc_haiku",), "tord", None))
    edits["repeat (10 answers), haiku"] = ("prospective, 1 model, 2 updates", 4, cc,
                                           V.tool_reads(("erc2_haiku",), "trep", None))
    res = {}
    for name, (status, c, a, b) in edits.items():
        e = {"status": status, "C": c, "stated_level": rnd(level(c), 6)}
        for lev_name, lev in (("98.75", 0.9875), ("stated", level(c)), ("97.5", 0.975)):
            o = boot(diffs_of(a, b, sets["open"]), lev)
            s = boot(diffs_of(a, b, sets["specific"]), lev)
            dec = both_rules(o, s, lev)
            ex_o = with_exact(o, lev)
            ex_s = with_exact(s, lev) if s["three_point"] else s
            ex = both_rules(ex_o, ex_s, lev)
            e[lev_name] = {"open": show(o), "specific": show(s), **dec, "exact_first": ex["first"],
                           "exact_revised": ex["revised"], "specific_exact_used": s["three_point"],
                           "exact_open": [rnd(ex_o["low"], 2), rnd(ex_o["high"], 2)],
                           "exact_specific": [rnd(ex_s["low"], 2), rnd(ex_s["high"], 2)]}
        res[name] = e
    out["edits"] = res
    return out


# ------------------------------------------------------------------------------------------------ part A2

def part_a2(sets):
    out = {}
    # round-9 forms: value-only rename (f2) and opaque code (f6); open set S1t (807, 7 models), specific S2 (233,
    # Sonnet, Haiku, Luna). C = 7 + 3 = 10 intervals in one release, level 99.5%.
    reads, _ = V.na.load()
    data, g = V.runs.context()
    s2 = {d.removesuffix(".json") for d in g["s2"] if V.gold.brief_type(data[d]) == "hotel"}
    s1t = {d.removesuffix(".json") for d in g["s1t"] if V.gold.brief_type(data[d]) is None
           and V.gold.brief_type(data[d], "fail_info") is None}
    forms = {}
    for label, form in (("value-only rename", "f2"), ("opaque code", "f6")):
        per = {}
        for m in ("sonnet", "haiku", "sol", "luna", "deepseek", "qwen", "gemma"):
            base, oth = reads.get((m, "f0"), {}), reads.get((m, form), {})
            e = {}
            for lev_name, lev in (("95", 0.95), ("99.5", level(10))):
                ss = []
                for units in (s1t, s2):
                    both = sorted(u for u in units if base.get(u) and oth.get(u))
                    diffs = [100 * (V.mean(V.na.hotel(v) for v in oth[u]) - V.mean(V.na.hotel(v) for v in base[u]))
                             for u in both]
                    ss.append(boot(diffs, lev) if diffs else None)
                o, s = ss
                e[lev_name] = {"open": show(o), "specific": show(s) if s else None,
                               **{f"L{lim:g}": {"first": model_dec([o, s], None, lim),
                                                "revised": model_dec([o, s], 1 - lev, lim)} for lim in (3.0, 5.0, 10.0)}}
            per[m] = e
        forms[label] = per
    out["forms"] = forms
    # tool calls, full rename, all stored answers per prefix (Table 15 row; Table 3 and Table 7 averages); C = 12
    tc = {}
    for m in ("sonnet", "haiku", "opus", "sol", "astra", "luna"):
        a = V.tool_reads((f"era1_{m}",), "t0", None)
        b = V.tool_reads((f"era1_{m}",), "t1", None)
        e = {}
        for lev_name, lev in (("95", 0.95), ("99.58", level(12))):
            o = boot(diffs_of(a, b, sets["open"]), lev)
            s = boot(diffs_of(a, b, sets["specific"]), lev)
            e[lev_name] = {"open": show(o), "specific": show(s),
                           **{f"L{lim:g}": {"first": model_dec([o, s], None, lim),
                                            "revised": model_dec([o, s], 1 - lev, lim)} for lim in (3.0, 5.0, 10.0)}}
        tc[m] = e
    out["tool_call_full_rename_all_answers"] = tc
    return out


# ------------------------------------------------------------------------------------------------ part A3

def part_a3():
    """Held-out rows: normal approximation from the stored 95% percentile intervals (approximate only)."""
    st = json.loads((EXPLORE / "main/exp0/stage1.json").read_text())["results"]
    z95 = statistics.NormalDist().inv_cdf(0.975)

    def approx(mean, ci, lev):
        se = (ci[1] - ci[0]) / (2 * z95)
        z = statistics.NormalDist().inv_cdf(1 - (1 - lev) / 2)
        return {"change": 100 * mean, "low": 100 * (mean - z * se), "high": 100 * (mean + z * se), "sign_p": 0.0}

    def dec(sets_, lev):
        d = [set_class(s) for s in sets_]
        if "meets flag rule" in d:
            return "flag"
        if len(d) == 2 and all(x == "within limits" for x in d):
            return "pass"
        return "more data"

    out = {"note": "approximate: normal approximation from the stored 95% intervals; the sign condition is not "
                   "applied (no stored sign counts for most rows)"}
    t = st["part1_family"]["tests"]
    p3 = st["part3_models"]["read1"]
    rows = {"full rename": ({"panel": [(t[0]["mean"], t[0]["ci95"]), (t[1]["mean"], t[1]["ci95"])]} |
                            {m: [(p3["wrong_values"][m]["mean"], p3["wrong_values"][m]["ci95"]),
                                 (p3["correct_values_kept"][m]["mean"], p3["correct_values_kept"][m]["ci95"])]
                             for m in p3["wrong_values"]}, 14)}
    for key, label in (("f4", "neutral value"), ("t_described", "description edit")):
        a, b = st["part4_secondary"][key]
        rows[label] = ({"panel": [(a["panel"]["mean"], a["panel"]["ci95"]), (b["panel"]["mean"], b["panel"]["ci95"])]} |
                       {m: [(a["models"][m]["mean"], a["models"][m]["ci95"]),
                            (b["models"][m]["mean"], b["models"][m]["ci95"])] for m in a["models"]}, 14)
    plc = st["part4_secondary"]["placebo"]["placebo_effect"]
    rows["unrelated rename"] = ({"panel": [(plc["panel"]["mean"], plc["panel"]["ci95"])]} |
                                {m: [(plc["models"][m]["mean"], plc["models"][m]["ci95"])] for m in plc["models"]}, 2)
    for label, (cells, c) in rows.items():
        e = {"C": c, "level": rnd(level(c), 6)}
        for lev_name, lev in (("95", 0.95), ("stated", level(c))):
            r = {}
            for unit, sets_ in cells.items():
                ss = [approx(mu, ci, lev) for mu, ci in sets_]
                r[unit] = {"decision": dec(ss, lev), "sets": [[rnd(s["change"], 2), rnd(s["low"], 2), rnd(s["high"], 2)]
                                                              for s in ss]}
            models = [u for u in r if u != "panel"]
            r["tally_models"] = dict(collections.Counter(r[u]["decision"] for u in models))
            e[lev_name] = r
        out[label] = e
    return out


# ------------------------------------------------------------------------------------------------ part C

def part_c():
    """One answer per request, n = 59 (the specific set), level 98.75%."""
    n, lev = 59, 0.9875
    rng = random.Random(MY_SEED)
    cache = {}

    def boot_counts(u, d):
        if (u, d) not in cache:
            lo, hi = V.boot_three_point(n, u, d, DRAWS, random.Random(MY_SEED + 1000 * u + d), lev)
            cache[(u, d)] = (lo, hi)
        return cache[(u, d)]

    def multinom(u, d, pu, pd):
        if u + d > n:
            return 0.0
        lg = math.lgamma(n + 1) - math.lgamma(u + 1) - math.lgamma(d + 1) - math.lgamma(n - u - d + 1)
        t = 0.0
        for k, p in ((u, pu), (d, pd), (n - u - d, 1 - pu - pd)):
            if k:
                if p <= 0:
                    return 0.0
                t += k * math.log(p)
        return math.exp(lg + t)

    def rates(pu, pd):
        within_b = within_e = flag_b = flag_r = flag_e = zero = 0.0
        for u in range(n + 1):
            for d in range(n + 1 - u):
                p = multinom(u, d, pu, pd)
                if p < 1e-10:
                    continue
                ch = 100 * (u - d) / n
                lo, hi = boot_counts(u, d)
                s = {"change": ch, "low": lo, "high": hi, "sign_p": V.sign_p(u, d)}
                elo, ehi = exact_interval(n, u, d, lev)
                se = {**s, "low": elo, "high": ehi}
                within_b += p * (set_class(s) == "within limits")
                within_e += p * (set_class(se) == "within limits")
                flag_b += p * (set_class(s) == "meets flag rule")
                flag_r += p * (set_class(s, 1 - lev) == "meets flag rule")
                flag_e += p * (set_class(se) == "meets flag rule")
                zero += p * (u == 0 and d == 0)
        return {"p_up": pu, "p_down": pd, "true_change": rnd(100 * (pu - pd), 2), "no_request_changes": rnd(zero, 5),
                "within_limits_percentile": rnd(within_b, 5), "within_limits_exact": rnd(within_e, 5),
                "meets_flag_first_percentile": rnd(flag_b, 5), "meets_flag_revised_percentile": rnd(flag_r, 5),
                "meets_flag_exact": rnd(flag_e, 5)}

    within_any = [(u, d) for u in range(n + 1) for d in range(n + 1 - u)
                  if set_class({"change": 100 * (u - d) / n, "sign_p": 1.0,
                                **dict(zip(("low", "high"), exact_interval(n, u, d, lev)))}) == "within limits"]
    zero = exact_interval(n, 0, 0, lev)
    near_l = [rates(pu, pd) for pu, pd in ((0.051, 0.0), (0.06, 0.0), (0.08, 0.0), (0.07, 0.01), (0.08, 0.02),
                                            (0.10, 0.04))]
    at_zero = [rates(p, p) for p in (0.01, 0.02, 0.04, 0.06, 0.10)]
    del rng
    return {"n": n, "level": lev, "nominal_error_one_tail": rnd((1 - lev) / 2, 5),
            "exact_interval_no_change": [rnd(x, 3) for x in zero],
            "exact_within_limits_counts": within_any,
            "true_change_above_L": near_l, "true_change_zero": at_zero,
            "note": "within limits with a true change above L is a wrong pass of this set; meets flag rule with a true "
                    "change of 0 is a wrong flag of this set. The percentile bootstrap for each count uses 2,000 "
                    "binomial draws (the same distribution as resampling requests)."}


# ------------------------------------------------------------------------------------------------ part D

def part_d(sets):
    ver = json.loads((HERE / "out" / "rtest_check_values.json").read_text())
    out = []
    for case in ver["item1"]["arm_order_changes"]:
        m = case["model"]
        srcs = {s_[0]: s_ for s_ in V.AA[m]}
        idx = 4 if case["variant"] == "all_answers" else 3
        a = V.tool_reads(srcs[case["a"]][1], srcs[case["a"]][2], srcs[case["a"]][idx])
        b = V.tool_reads(srcs[case["b"]][1], srcs[case["b"]][2], srcs[case["b"]][idx])
        e = {"case": f"{m}: {case['a']} against {case['b']} ({case['variant']})"}
        for name, sym in (("original index rule", False), ("symmetric index rule", True)):
            fw = [boot(diffs_of(a, b, sets[k]), 0.9875, sym=sym) for k in ("open", "specific")]
            rv = [boot(diffs_of(b, a, sets[k]), 0.9875, sym=sym) for k in ("open", "specific")]
            e[name] = {"forward": model_dec(fw), "reverse": model_dec(rv),
                       "forward_specific": [rnd(fw[1][k], 3) for k in ("change", "low", "high")],
                       "reverse_specific": [rnd(rv[1][k], 3) for k in ("change", "low", "high")]}
        out.append(e)
    return out


# ------------------------------------------------------------------------------------------------ report

def md(out):
    a1 = out["A1"]
    lines = ["## Final-5 analysis: interval levels, zero-width intervals, error rates near the limits, arm order",
             "", "Status: post hoc, exploratory. L = 5 points.", "", "### A1. Table 4 rows at the stated level", "",
             "Unchanged tool, 29 pairs, one answer per prefix. Tally (level, rule, decision):", "", "```"]
    lines += [f"{k}: {v}" for k, v in a1["unchanged_tally"].items()]
    lines += ["```", "", "| Edit | Status | C | Level | First | Revised | Exact first | Exact revised | Open | Specific |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for name, e in a1["edits"].items():
        for lev_name in ("98.75", "stated", "97.5"):
            x = e[lev_name]
            o, s = x["open"], x["specific"]
            lines.append(f"| {name} | {e['status']} | {e['C']} | {lev_name} ({e['stated_level']}) | {x['first']} | "
                         f"{x['revised']} | {x['exact_first']} | {x['exact_revised']} | "
                         f"{o['change']:+.1f} [{o['low']:+.1f}, {o['high']:+.1f}] {o['up']}/{o['down']} | "
                         f"{s['change']:+.1f} [{s['low']:+.1f}, {s['high']:+.1f}] {s['up']}/{s['down']} p={s['sign_p']:.3g} |")
    lines += ["", "Unchanged pairs whose decision is not a hold at some level:", "",
              "| Pair | Level | First | Revised | Exact first | Specific | Exact specific |", "|---|---|---|---|---|---|---|"]
    for e in a1["unchanged_pairs"]:
        for lev_name in ("98.75", "99.5", "97.5"):
            x = e[lev_name]
            if x["first"] != "hold" or x["revised"] != "hold" or x["exact_first"] != "hold":
                s = x["specific"]
                lines.append(f"| {e['model']} {e['a']} v {e['b']} | {lev_name} | {x['first']} | {x['revised']} | "
                             f"{x['exact_first']} | {s['change']:+.1f} [{s['low']:+.1f}, {s['high']:+.1f}] "
                             f"{s['up']}/{s['down']} | {x['exact_specific']} |")
    lines += ["", "### A2. Table 15 exploratory rows", ""]
    for label, per in out["A2"]["forms"].items():
        for m, e in per.items():
            for lev_name in ("95", "99.5"):
                x = e[lev_name]
                o, s = x["open"], x["specific"]
                st = f"{s['change']:+.1f} [{s['low']:+.1f}, {s['high']:+.1f}] {s['up']}/{s['down']} p={s['sign_p']:.3g}" if s else "-"
                lines.append(f"- {label}, {m}, {lev_name}%: open {o['change']:+.2f} [{o['low']:+.2f}, {o['high']:+.2f}] "
                             f"{o['up']}/{o['down']}; specific {st}; L3 {x['L3']}; L5 {x['L5']}; L10 {x['L10']}")
    for m, e in out["A2"]["tool_call_full_rename_all_answers"].items():
        for lev_name in ("95", "99.58"):
            x = e[lev_name]
            o, s = x["open"], x["specific"]
            lines.append(f"- tool-call full rename (all answers), {m}, {lev_name}%: open {o['change']:+.1f} "
                         f"[{o['low']:+.1f}, {o['high']:+.1f}] {o['up']}/{o['down']}; specific {s['change']:+.1f} "
                         f"[{s['low']:+.1f}, {s['high']:+.1f}] {s['up']}/{s['down']}; L3 {x['L3']}; L5 {x['L5']}; L10 {x['L10']}")
    lines += ["", "### A3. Held-out rows (approximate)", "", "```", json.dumps(out["A3"], indent=1), "```", "",
              "### C. Error rates of one set with one answer per request (n = 59, 98.75%)", "", "```",
              json.dumps(out["C"], indent=1), "```", "", "### D. Order of the two arms", "", "```",
              json.dumps(out["D"], indent=1), "```"]
    return "\n".join(lines) + "\n"


def main():
    data, g = V.runs.context()
    sets = V.ra.request_sets(data, g)
    out = {"post_hoc": True, "exploratory": True, "L": L, "seed": SEED, "draws": DRAWS}
    out["A1"] = part_a1(sets)
    print("A1 done", flush=True)
    out["A2"] = part_a2(sets)
    print("A2 done", flush=True)
    out["A3"] = part_a3()
    out["C"] = part_c()
    print("C done", flush=True)
    out["D"] = part_d(sets)
    OUTDIR.mkdir(exist_ok=True)
    (OUTDIR / "rtest_levels.json").write_text(json.dumps(out, indent=1))
    (OUTDIR / "rtest_levels.md").write_text(md(out))
    print("wrote", OUTDIR / "rtest_levels.json")


if __name__ == "__main__":
    main()
