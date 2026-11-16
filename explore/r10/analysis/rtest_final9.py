"""Final-9 analysis of the release test (post hoc, exploratory): the final-8 analysis (every release decision
again, with a symmetric percentile index, next to the decisions of the rule as run), with one correction from the
independent check (VERIFIED-TRUST8.md section 2.3): under the final rule, C counts every model that received the same
update in our tests. Broad rewrite: Sonnet, Sol and Haiku (C = 6); field-order edit: Haiku, Sol and Luna (C = 6);
repeat of the unchanged tool: Haiku and the five models of R10-20 (C = 12); the steered rewrites (Haiku rewrites h1 and
g1 are the same two rewrites again): Sonnet and Haiku (C = 4); Haiku's further rewrites: Haiku only (C = 2). Stored
answers and stored result files only.

This file is a copy of the project analysis (an internal file) with the paths of the study folder and neutral names;
the results are the same. Usage (from explore/): python3 -I r10/analysis/rtest_final9.py
Output: r10/analysis/out/rtest_final9.json and rtest_final9.md.
Changes for the study folder: the loaders of the independent check come from rtest_v.py, rtest_vr.py and rtest_vr2.py;
the stored results come from out/release_test.json, release_test2.json and rtest_check_values.json; the request
order comes from runs.requests (the requests rebuilt from the code; verify_requests.py checks them), not from
the request files.

The index rule as run (stats.percentile) takes, of the 2,000 sorted resampled means, the value at index
round(q x 2,000) - 1 for q = a and q = 1 - a, a = (1 - level) / 2. So the low end is the k-th lowest mean and the
high end is the (k + 1)-th highest mean (98.75%: the 12th lowest and the 13th highest; 99.17%: the 8th lowest and
the 9th highest). The symmetric index of this script takes the k-th lowest and the k-th highest mean, with
k = floor(a x 2,000), at least 1 (98.75%: k = 12; 99.17%: 8; 99.5%: 5; 99.58%: 4; 97.5%: 25; 95%: 50). The draws
are the draws of the rule as run (same seed, same random calls). The low end does not change; the high end moves
out by one sorted mean. With the symmetric index, a reversed comparison gives exactly the negated interval.

Rules (L = 5 points unless stated):
- first: a set meets the flag rule if |change| >= L and the interval excludes 0; it is within limits if the whole
  interval is inside [-L, +L]; else unresolved. Model: flag if a set meets the flag rule; pass if both sets are within
  limits; else hold (one look with all requests, so n = n_max).
- revised: the first rule, and a flag also needs the exact two-sided sign test p <= 1 - level.
- final (the operational rule of the paper, Section 7 step 5, chosen post hoc): the revised rule with the symmetric
  index, at the level of one release (C = the intervals of one update on every model that received it), and a set
  whose interval has zero width is not within limits (it is unresolved).

Parts:
A. The prospective tests of updates that preserve meaning (R10-20: repeat, first paraphrase, full rename on Sol, Luna,
   DeepSeek, Qwen, Gemma; R10-22: field order, second paraphrase on Sol and Luna). Paper Tables 4 and 19.
B. The stored tool calls of Table 16 and the prospective rows of Table 15 (Appendices I, L, M, N).
C. The exploratory form rows and the all-answer tool-call row of Table 15 (L = 3, 5, 10).
D. The error-rate model of one set with one answer per request (59 requests, 98.75%), bootstrap randomness averaged
   out exactly, for both index rules and for the final rule.
E. The floor of the sign condition: with one answer per request and no change in the other direction, the smallest
   number of changed requests whose exact two-sided sign test p is at most 1 - level, and the change in points that
   this number gives on 59 and on 448 requests.
F. A summary for the paper: the decisions that the symmetric index changes at the levels as run (first and revised
   rules), the largest outward move of a high end, and the decisions of the final rule.
The held-out rows of Table 15 are not recomputed: their per-dialogue answers are in folders that this script does
not open.

Safety: no model call, no network call. The loaders refuse folders whose names start with "em", sealed files, key
files and .env files.
"""
import collections
import functools
import importlib.util
import itertools
import json
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
OUTDIR = HERE / "out"
sys.path.insert(0, str(HERE))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # main() does not run on import
    return m


VR = module("f8_vr1", HERE / "rtest_vr.py")      # R10-20 loader and parser (independent check)
VR2 = module("f8_vr2", HERE / "rtest_vr2.py")    # R10-22 loader and parser (independent check)
V = module("f8_v", HERE / "rtest_v.py")  # stored tool calls and round-9 forms

L = 5.0
SEED, DRAWS = 20261112, 2000


def level(c):
    return 1 - 0.05 / c


def rnd(x, nd=4):
    return None if x is None else round(x, nd)


# ------------------------------------------------------------------------------------------------ intervals

def idx_as_run(q):
    return min(DRAWS - 1, max(0, int(round(q * DRAWS)) - 1))


def k_sym(lev):
    return max(1, math.floor((1 - lev) / 2 * DRAWS + 1e-9))


def boot(diffs, lev, seed=SEED):
    """The percentile bootstrap over requests with the draws of stats.cluster_bootstrap; both index rules."""
    n = len(diffs)
    rng = random.Random(seed)
    vals = sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(DRAWS))
    a = (1 - lev) / 2
    k = k_sym(lev)
    up, down = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    return {"pairs": n, "change": sum(diffs) / n, "up": up, "down": down, "sign_p": V.sign_p(up, down),
            "as_run": [vals[idx_as_run(a)], vals[idx_as_run(1 - a)]], "symmetric": [vals[k - 1], vals[DRAWS - k]],
            "level": lev}


# ------------------------------------------------------------------------------------------------ rules

def set_class(s, index, alpha=None, zero_width_guard=False, lim=L):
    lo, hi = s[index]
    if abs(s["change"]) >= lim and (lo > 0 or hi < 0) and (alpha is None or s["sign_p"] <= alpha):
        return "meets flag rule"
    if -lim <= lo and hi <= lim and not (zero_width_guard and lo == hi):
        return "within limits"
    return "unresolved"


def model_dec(sets, index, alpha=None, zero_width_guard=False, lim=L):
    d = [set_class(s, index, alpha, zero_width_guard, lim) for s in sets if s is not None]
    if "meets flag rule" in d:
        return "flag"
    if len(d) == 2 and all(x == "within limits" for x in d):
        return "pass"
    return "hold"


def decisions(o, s, lev):
    """o, s: the two sets at level lev. Returns the decisions of the first and revised rules with both indices."""
    a = 1 - lev
    return {"first_as_run": model_dec([o, s], "as_run"), "revised_as_run": model_dec([o, s], "as_run", a),
            "first_symmetric": model_dec([o, s], "symmetric"), "revised_symmetric": model_dec([o, s], "symmetric", a),
            "final": model_dec([o, s], "symmetric", a, True)}


def show(s):
    return {"pairs": s["pairs"], "change": rnd(s["change"]), "up": s["up"], "down": s["down"], "sign_p": rnd(s["sign_p"], 6),
            "as_run": [rnd(x) for x in s["as_run"]], "symmetric": [rnd(x) for x in s["symmetric"]]}


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


# ------------------------------------------------------------------------------------------------ part A

R20 = {"sol": ("tool", "erk_sol"), "luna": ("tool", "erk_luna"), "deepseek": ("form", "erk_deepseek"),
       "qwen": ("form", "erk_qwen"), "gemma": ("form", "erk_gemma")}
R20_UPD = {"a": "repeat", "b": "first paraphrase", "c": "full rename"}
R22_UPD = {"d": ("tord", "field-order edit"), "e": ("tpar2", "second paraphrase")}


def diffs_vr(mod, reads, ids, control, update):
    out = []
    for d in ids:
        a, b = mod.valid_scores(reads, d, control), mod.valid_scores(reads, d, update)
        if a and b:
            out.append(100 * (mod.mean(b) - mod.mean(a)))
    return out


def part_a():
    data = json.loads(VR.safe(VR.MW / "data.json").read_text())
    res = {"R10-20": {}, "R10-22": {}, "checks": [], "levels": {}}
    # R10-20
    order = []
    for r in V.runs.requests("erk_luna"):
        d = r["custom_id"].split("-")[1] + ".json"
        if not order or order[-1] != d:
            order.append(d)
    sets = VR.load_sets(data, order)
    stored = json.loads(VR.safe(OUTDIR / "release_test.json").read_text())["models"]
    final_lev20 = level(5 * 2 * 1)  # one release = one update on the five models that received it
    res["levels"]["R10-20"] = {"as_run": {"tool": VR.LEVEL["tool"], "form": VR.LEVEL["form"]},
                               "final": final_lev20, "final_C": 10}
    for m, (ch, run) in R20.items():
        reads, _ = VR.load(m)
        lev_run = VR.LEVEL[ch]
        per = {}
        for u, name in R20_UPD.items():
            ctrl, upd = VR.CONTROL[ch], VR.UPDATES[u][ch]
            sets_run = {k: boot(diffs_vr(VR, reads, sets[k], ctrl, upd), lev_run) for k in ("open", "specific")}
            sets_fin = {k: boot(diffs_vr(VR, reads, sets[k], ctrl, upd), final_lev20) for k in ("open", "specific")}
            for k in ("open", "specific"):  # the as-run interval must equal the stored (independently checked) value
                st = stored[m]["updates"][u]["sets"][k]
                ok = (close(sets_run[k]["change"], st["change"]) and close(sets_run[k]["as_run"][0], st["interval"][0])
                      and close(sets_run[k]["as_run"][1], st["interval"][1]) and sets_run[k]["up"] == st["up"]
                      and sets_run[k]["down"] == st["down"])
                res["checks"].append({"test": "R10-20", "model": m, "update": u, "set": k, "equal_to_result_json": ok})
            dr = decisions(sets_run["open"], sets_run["specific"], lev_run)
            dfin = decisions(sets_fin["open"], sets_fin["specific"], final_lev20)
            st_dec = (stored[m]["updates"][u]["first"]["release"], stored[m]["updates"][u]["revised"]["release"])
            res["checks"].append({"test": "R10-20", "model": m, "update": u, "decisions_equal_to_result_json":
                                  (dr["first_as_run"], dr["revised_as_run"]) == st_dec})
            per[u] = {"update": name, "channel": ch, "level_as_run": rnd(lev_run, 6),
                      "sets_as_run_level": {k: show(v) for k, v in sets_run.items()},
                      "decisions_as_run_level": dr,
                      "sets_final_level": {k: show(v) for k, v in sets_fin.items()},
                      "final_rule": dfin["final"],
                      "revised_symmetric_final_level": dfin["revised_symmetric"],
                      "first_symmetric_final_level": dfin["first_symmetric"]}
        # post hoc description: the first paraphrase against the repeat (as in VERIFIED-RELEASE 6.3)
        ctrl, upd = VR.UPDATES["a"][ch], VR.UPDATES["b"][ch]
        pr = {k: boot(diffs_vr(VR, reads, sets[k], ctrl, upd), lev_run) for k in ("open", "specific")}
        per["b_against_a"] = {"sets": {k: show(v) for k, v in pr.items()}, **decisions(pr["open"], pr["specific"], lev_run)}
        res["R10-20"][m] = per
    # R10-22
    order2 = []
    for r in V.runs.requests("erk2_luna"):
        d = r["custom_id"].split("-")[1] + ".json"
        if not order2 or order2[-1] != d:
            order2.append(d)
    sets2 = VR2.load_sets(data, order2)
    stored2 = json.loads(VR2.safe(OUTDIR / "release_test2.json").read_text())
    lev22 = level(2 * 2 * 1)
    res["levels"]["R10-22"] = {"as_run": lev22, "final": lev22, "final_C": 4}
    for m, run in VR2.MODELS.items():
        reads, _ = VR2.load(run)
        per = {}
        for u, (cell, name) in R22_UPD.items():
            ss = {k: boot(diffs_vr(VR2, reads, sets2[k], "t0", cell), lev22) for k in ("open", "specific")}
            for k in ("open", "specific"):
                st = stored2["models"][m]["updates"][u]["sets"][k]
                ok = (close(ss[k]["change"], st["change"]) and close(ss[k]["as_run"][0], st["interval"][0])
                      and close(ss[k]["as_run"][1], st["interval"][1]) and ss[k]["up"] == st["up"]
                      and ss[k]["down"] == st["down"])
                res["checks"].append({"test": "R10-22", "model": m, "update": u, "set": k, "equal_to_result2_json": ok})
            dr = decisions(ss["open"], ss["specific"], lev22)
            st_dec = (stored2["models"][m]["updates"][u]["first"]["release"],
                      stored2["models"][m]["updates"][u]["revised"]["release"])
            res["checks"].append({"test": "R10-22", "model": m, "update": u, "decisions_equal_to_result2_json":
                                  (dr["first_as_run"], dr["revised_as_run"]) == st_dec})
            per[u] = {"update": name, "level_as_run": rnd(lev22, 6), "sets_as_run_level": {k: show(v) for k, v in ss.items()},
                      "decisions_as_run_level": dr, "final_rule": dr["final"]}
        # description: the fresh control against the R10-20 control (98.75%)
        old, _ = VR2.load(VR2.R20_CONTROL[m], cells={"t0"}, rename={"t0": "t0_r20"})
        both = {**old, **reads}
        per["control_drift"] = {k: show(boot(diffs_vr(VR2, both, sets2[k], "t0_r20", "t0"), lev22)) for k in ("open", "specific")}
        res["R10-22"][m] = per
    return res


# ------------------------------------------------------------------------------------------------ part B

def diffs_of(ctrl, upd, ids):
    return [100 * (V.mean(upd[d]) - V.mean(ctrl[d])) for d in ids if ctrl.get(d) and upd.get(d)]


def part_b(sets):
    out = {"unchanged_one_answer": [], "unchanged_all_answers": []}
    ver = json.loads((OUTDIR / "rtest_check_values.json").read_text())
    stored = {(e["model"], e["a"], e["b"]): e for e in ver["item1"]["aa"]["one_answer"]}
    tallies = collections.Counter()
    for variant, idx in (("one_answer", 3), ("all_answers", 4)):
        for m, srcs in V.AA.items():
            src = [(s_[0], V.tool_reads(s_[1], s_[2], s_[idx])) for s_ in srcs]
            for (la, a), (lb, b) in itertools.combinations(src, 2):
                e = {"model": m, "a": la, "b": lb}
                for lev_name, lev in (("98.75", 0.9875), ("99.5", level(10))):
                    o = boot(diffs_of(a, b, sets["open"]), lev)
                    s = boot(diffs_of(a, b, sets["specific"]), lev)
                    orv = boot(diffs_of(b, a, sets["open"]), lev)
                    srv = boot(diffs_of(b, a, sets["specific"]), lev)
                    dec = decisions(o, s, lev)
                    rev = decisions(orv, srv, lev)
                    e[lev_name] = {"open": show(o), "specific": show(s), **dec,
                                   "reverse_order": {k: rev[k] for k in ("first_as_run", "first_symmetric", "final")},
                                   "symmetric_negates_exactly": all(
                                       close(x["symmetric"][0], -y["symmetric"][1], 1e-9) and
                                       close(x["symmetric"][1], -y["symmetric"][0], 1e-9)
                                       for x, y in ((o, orv), (s, srv)))}
                    for rule in ("first_as_run", "revised_as_run", "first_symmetric", "revised_symmetric", "final"):
                        tallies[(variant, lev_name, rule, dec[rule])] += 1
                    for rule in ("first_as_run", "first_symmetric"):
                        tallies[(variant, lev_name, rule + " reversed", rev[rule])] += 1
                if variant == "one_answer":
                    st = stored[(m, la, lb)]
                    e["equal_to_verify_out"] = (e["98.75"]["first_as_run"] == st["decision"]
                                                and close(e["98.75"]["specific"]["as_run"][0], rnd(st["specific"]["low"]), 1e-3))
                out["unchanged_" + variant].append(e)
    out["tally"] = {" | ".join(k): v for k, v in sorted(tallies.items())}
    # edits: (status, C of one release under the final rule, C as run, control reads, update reads)
    edits = {}
    for m in ("sonnet", "haiku", "opus", "sol", "astra", "luna"):
        edits[f"full rename, {m}"] = ("post hoc", 12, 4, V.tool_reads((f"era1_{m}",), "t0", 1),
                                      V.tool_reads((f"era1_{m}",), "t1", 1))
    for m in ("sonnet", "sol"):
        edits[f"broad rewrite, {m}"] = ("prospective", 6, 4, V.tool_reads((f"erp_{m}",), "t0", 1),
                                        V.tool_reads((f"erp_{m}",), "tedit", 1))
    sc, hc = V.tool_reads(("erp_sonnet",), "t0", 1), V.tool_reads(("ers_haiku",), "t0", 1)
    for c in ("th", "tg"):
        edits[f"steered {c}, sonnet"] = ("prospective", 4, 4, sc, V.tool_reads(("ers_sonnet",), c, 1))
        edits[f"steered {c}, haiku"] = ("prospective", 4, 4, hc, V.tool_reads(("ers_haiku",), c, 1))
    mc = V.tool_reads(("erm_haiku",), "t0", 1)
    for c in [f"{g}{i}" for g in "hgn" for i in (1, 2, 3)]:
        c_fin = 6 if c == "n1" else (4 if c in ("h1", "g1") else 2)  # n1: the broad rewrite; h1, g1: the steered rewrites
        edits[f"rewrite {c}, haiku"] = ("post hoc", c_fin, 4, mc, V.tool_reads(("erm_haiku",), c, 1))
    cc = V.tool_reads(("erc_haiku",), "t0", None)
    edits["field order (10 answers), haiku"] = ("prospective", 6, 4, cc, V.tool_reads(("erc_haiku",), "tord", None))
    edits["repeat (10 answers), haiku"] = ("prospective", 12, 4, cc, V.tool_reads(("erc2_haiku",), "trep", None))
    res = {}
    for name, (status, c_final, c_run, a, b) in edits.items():
        e = {"status": status, "C_final": c_final, "final_level": rnd(level(c_final), 6)}
        for lev_name, lev in (("98.75", 0.9875), ("final", level(c_final))):
            o = boot(diffs_of(a, b, sets["open"]), lev)
            s = boot(diffs_of(a, b, sets["specific"]), lev)
            e[lev_name] = {"open": show(o), "specific": show(s), **decisions(o, s, lev),
                           **{f"first L={lim:g} {ix}": model_dec([o, s], ix, None, False, lim)
                              for lim in (3.0, 10.0) for ix in ("as_run", "symmetric")}}
        res[name] = e
    out["edits"] = res
    return out


# ------------------------------------------------------------------------------------------------ part C

def part_c():
    out = {}
    reads, _ = V.na.load()
    data, g = V.runs.context()
    s2 = {d.removesuffix(".json") for d in g["s2"] if V.gold.brief_type(data[d]) == "hotel"}
    s1t = {d.removesuffix(".json") for d in g["s1t"] if V.gold.brief_type(data[d]) is None
           and V.gold.brief_type(data[d], "fail_info") is None}
    lev = level(10)
    forms = {}
    for label, form in (("value-only rename", "f2"), ("opaque code", "f6")):
        per = {}
        for m in ("sonnet", "haiku", "sol", "luna", "deepseek", "qwen", "gemma"):
            base, oth = reads.get((m, "f0"), {}), reads.get((m, form), {})
            ss = []
            for units in (s1t, s2):
                both = sorted(u for u in units if base.get(u) and oth.get(u))
                diffs = [100 * (V.mean(V.na.hotel(v) for v in oth[u]) - V.mean(V.na.hotel(v) for v in base[u])) for u in both]
                ss.append(boot(diffs, lev) if diffs else None)
            o, s = ss
            if o is None:
                continue
            per[m] = {"open": show(o), "specific": show(s) if s else None,
                      **{f"L={lim:g} {rule} {ix}": model_dec([o, s], ix, (1 - lev) if rule == "revised" else None, False, lim)
                         for lim in (3.0, 5.0, 10.0) for rule in ("first", "revised") for ix in ("as_run", "symmetric")}}
        forms[label] = per
    out["forms_99.5"] = forms
    data2, g2 = V.runs.context()
    sets = V.ra.request_sets(data2, g2)
    lev12 = level(12)
    tc = {}
    for m in ("sonnet", "haiku", "opus", "sol", "astra", "luna"):
        a = V.tool_reads((f"era1_{m}",), "t0", None)
        b = V.tool_reads((f"era1_{m}",), "t1", None)
        o = boot(diffs_of(a, b, sets["open"]), lev12)
        s = boot(diffs_of(a, b, sets["specific"]), lev12)
        tc[m] = {"open": show(o), "specific": show(s),
                 **{f"L={lim:g} {rule} {ix}": model_dec([o, s], ix, (1 - lev12) if rule == "revised" else None, False, lim)
                    for lim in (3.0, 5.0, 10.0) for rule in ("first", "revised") for ix in ("as_run", "symmetric")}}
    out["tool_call_full_rename_all_answers_99.58"] = tc
    return out


# ------------------------------------------------------------------------------------------------ part D

def _lpmf(i, n, p):
    return math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p) + (n - i) * math.log1p(-p)


def _pmf(i, n, p):
    if p <= 0:
        return 1.0 if i == 0 else 0.0
    if p >= 1:
        return 1.0 if i == n else 0.0
    return math.exp(_lpmf(i, n, p))


def _cdf(k, n, p):
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return min(1.0, sum(_pmf(i, n, p) for i in range(k + 1)))


def part_d(n=59, lev=0.9875):
    """One set, n requests, one answer each; each request rises with probability pu and falls with pd. For counts
    (u, d), a resampled mean is 100 (U - D) / n with (U, D) multinomial (u/n, d/n). The k-th lowest of 2,000 means is
    above x when at most k - 1 draws are <= x; the j-th highest is below x when at most j - 1 draws are >= x."""
    k_low = idx_as_run((1 - lev) / 2) + 1                    # 12: the low end is the 12th lowest (both rules)
    j_run = DRAWS - idx_as_run(1 - (1 - lev) / 2)            # 13: the high end as run is the 13th highest
    j_sym = k_sym(lev)                                       # 12: the symmetric high end

    @functools.lru_cache(maxsize=None)
    def tails(u, d):
        """P(mean <= 0), P(mean >= 0), P(mean > L) for one resampled mean."""
        pu, pd = u / n, d / n
        le = ge = gt = 0.0
        for U in range(n + 1):
            pU = _pmf(U, n, pu)
            if pU < 1e-15:
                continue
            rest = n - U
            q = pd / (1 - pu) if pu < 1 else 0.0
            for D in range(rest + 1):
                pD = _pmf(D, rest, q)
                if pD < 1e-15:
                    continue
                w = pU * pD
                m = 100 * (U - D) / n
                le += w * (m <= 0)
                ge += w * (m >= 0)
                gt += w * (m > L + 1e-12)
        return le, ge, gt

    @functools.lru_cache(maxsize=None)
    def p_flag(u, d, j):
        ch = 100 * (u - d) / n
        if abs(ch) < L:
            return 0.0
        le, ge, _ = tails(u, d)
        if ch > 0:
            return _cdf(k_low - 1, DRAWS, le)   # low end > 0
        return _cdf(j - 1, DRAWS, ge)           # high end < 0

    def multinom(u, d, pu, pd):
        z = n - u - d
        if (u and pu <= 0) or (d and pd <= 0) or (z and pu + pd >= 1):
            return 0.0
        lp = math.lgamma(n + 1) - math.lgamma(u + 1) - math.lgamma(d + 1) - math.lgamma(z + 1)
        lp += (u * math.log(pu) if u else 0) + (d * math.log(pd) if d else 0) + (z * math.log(1 - pu - pd) if z else 0)
        return math.exp(lp)

    def flag_rates(pu, pd):
        r = {"first_as_run": 0.0, "first_symmetric": 0.0, "revised_as_run": 0.0, "revised_symmetric": 0.0}
        for u in range(n + 1):
            for d in range(n + 1 - u):
                pr = multinom(u, d, pu, pd)
                if pr < 1e-12:
                    continue
                sp = V.sign_p(u, d) <= 1 - lev
                fa, fs = p_flag(u, d, j_run), p_flag(u, d, j_sym)
                r["first_as_run"] += pr * fa
                r["first_symmetric"] += pr * fs
                r["revised_as_run"] += pr * fa * sp
                r["revised_symmetric"] += pr * fs * sp
        return {"p_up": pu, "p_down": pd, "true_change": rnd(100 * (pu - pd), 2), **{k: rnd(v, 6) for k, v in r.items()}}

    def within_rates(pu):
        """Rises only (pd = 0): every resampled mean is >= 0, so the set is within limits when the high end is <= L."""
        r = {"as_run": 0.0, "symmetric": 0.0, "final": 0.0, "no_request_changes": 0.0}
        for u in range(n + 1):
            pr = multinom(u, 0, pu, 0.0)
            if pr < 1e-12:
                continue
            _, _, gt = tails(u, 0)
            wa, ws = _cdf(j_run - 1, DRAWS, gt), _cdf(j_sym - 1, DRAWS, gt)
            r["as_run"] += pr * wa
            r["symmetric"] += pr * ws
            r["final"] += pr * ws * (u > 0)  # zero width when no request changes: not within limits
            r["no_request_changes"] += pr * (u == 0)
        return {"p_up": pu, "true_change": rnd(100 * pu, 2), **{k: rnd(v, 6) for k, v in r.items()}}

    return {"n": n, "level": lev, "low_end": f"{k_low}th lowest (both rules)", "high_end_as_run": f"{j_run}th highest",
            "high_end_symmetric": f"{j_sym}th highest",
            "true_change_zero": [flag_rates(p, p) for p in (0.01, 0.02, 0.04, 0.06, 0.10)],
            "true_change_above_L": [within_rates(p) for p in (0.051, 0.06)]}


# ------------------------------------------------------------------------------------------------ part E

def part_e():
    out = {}
    for name, lev in (("97.50%", level(2)), ("98.75%", level(4)), ("99.17%", level(6)), ("99.50%", level(10))):
        alpha = 1 - lev
        n = 1
        while V.sign_p(n, 0) > alpha:
            n += 1
        out[name] = {"alpha": rnd(alpha, 6), "min_changes_one_direction": n, "sign_p_at_min": rnd(V.sign_p(n, 0), 6),
                     "sign_p_one_fewer": rnd(V.sign_p(n - 1, 0), 6), "points_on_59": rnd(100 * n / 59, 2),
                     "points_on_448": rnd(100 * n / 448, 2)}
    return out


# ------------------------------------------------------------------------------------------------ part F

def part_f(out):
    changed, shifts = [], []

    def note(where, s):
        shifts.append((round(s["symmetric"][1] - s["as_run"][1], 4), where))
        assert s["symmetric"][0] == s["as_run"][0], where  # the low end never moves

    for test in ("R10-20", "R10-22"):
        for m, per in out["A"][test].items():
            for u, e in per.items():
                if u in ("b_against_a", "control_drift"):
                    continue
                d = e["decisions_as_run_level"]
                for rule in ("first", "revised"):
                    if d[rule + "_as_run"] != d[rule + "_symmetric"]:
                        changed.append((test, m, u, rule, d[rule + "_as_run"], d[rule + "_symmetric"]))
                for k, s in e["sets_as_run_level"].items():
                    note(f"{test} {m} {u} {k}", s)
    for name, e in out["B"]["edits"].items():
        x = e["98.75"]
        for rule in ("first", "revised"):
            if x[rule + "_as_run"] != x[rule + "_symmetric"]:
                changed.append(("Table 18 edit", name, "98.75", rule, x[rule + "_as_run"], x[rule + "_symmetric"]))
        for lim in ("3", "10"):
            if x[f"first L={lim} as_run"] != x[f"first L={lim} symmetric"]:
                changed.append(("Table 17 edit", name, f"L={lim}", "first", x[f"first L={lim} as_run"],
                                x[f"first L={lim} symmetric"]))
        for k in ("open", "specific"):
            note(f"edit {name} {k}", x[k])
    for e in out["B"]["unchanged_one_answer"]:
        x = e["98.75"]
        for rule in ("first", "revised"):
            if x[rule + "_as_run"] != x[rule + "_symmetric"]:
                changed.append(("unchanged pair", f"{e['model']} {e['a']} v {e['b']}", "98.75", rule,
                                x[rule + "_as_run"], x[rule + "_symmetric"]))
        for k in ("open", "specific"):
            note(f"pair {e['model']} {e['a']} v {e['b']} {k}", x[k])
    for label, per in out["C"]["forms_99.5"].items():
        for m, e in per.items():
            for k in e:
                if k.startswith("L=") and k.endswith("as_run") and e[k] != e[k.replace("as_run", "symmetric")]:
                    changed.append(("Table 17 form row", label, m, k, e[k], e[k.replace("as_run", "symmetric")]))
    for m, e in out["C"]["tool_call_full_rename_all_answers_99.58"].items():
        for k in e:
            if k.startswith("L=") and k.endswith("as_run") and e[k] != e[k.replace("as_run", "symmetric")]:
                changed.append(("Table 17 tool row", m, k, e[k], e[k.replace("as_run", "symmetric")]))
    t = out["B"]["tally"]
    final = {"R10-20 at 99.5%": {m: {u: per[u]["final_rule"] for u in ("a", "b", "c")} for m, per in out["A"]["R10-20"].items()},
             "R10-22 at 98.75%": {m: {u: per[u]["final_rule"] for u in ("d", "e")} for m, per in out["A"]["R10-22"].items()},
             "Table 18 rows": {name: e["final"]["final"] for name, e in out["B"]["edits"].items()},
             "unchanged one answer at 99.5%": {k.split(" | ")[3]: v for k, v in t.items()
                                               if k.startswith("one_answer | 99.5 | final")},
             "unchanged all answers at 99.5%": {k.split(" | ")[3]: v for k, v in t.items()
                                                if k.startswith("all_answers | 99.5 | final")},
             "all answers, first rule at 98.75%, as run / reversed / symmetric": [
                 {k.split(" | ")[3]: v for k, v in t.items() if k.startswith("all_answers | 98.75 | first_as_run |")},
                 {k.split(" | ")[3]: v for k, v in t.items() if k.startswith("all_answers | 98.75 | first_as_run reversed")},
                 {k.split(" | ")[3]: v for k, v in t.items() if k.startswith("all_answers | 98.75 | first_symmetric |")}]}
    shifts.sort(reverse=True)
    return {"decisions_changed_by_the_index_at_levels_as_run": changed, "largest_high_end_moves": shifts[:5],
            "final_rule": final}


# ------------------------------------------------------------------------------------------------ report

def fmt_set(s, ix):
    lo, hi = s[ix]
    return f"{s['change']:+.1f} [{lo:+.2f}, {hi:+.2f}] {s['up']}/{s['down']} p={s['sign_p']:.4g}"


def md(out):
    A, B = out["A"], out["B"]
    lines = ["## Final-9: release decisions with a symmetric percentile index (post hoc)", "",
             "As run: the low end is the k-th lowest and the high end the (k + 1)-th highest of 2,000 resampled means.",
             "Symmetric: the k-th lowest and the k-th highest, k = floor(2,000 x (1 - level) / 2).",
             "Final rule: revised rule, symmetric index, level of one release (one update on every model that "
             "received it), zero-width interval not within limits.", "",
             f"Checks against result.json, result2.json and verify_out.json: "
             f"{sum(all(v for k, v in c.items() if k.startswith(('equal', 'decisions'))) for c in A['checks'])} of "
             f"{len(A['checks'])} part-A checks pass; part B one-answer pairs equal: "
             f"{sum(e['equal_to_verify_out'] for e in B['unchanged_one_answer'])} of {len(B['unchanged_one_answer'])}.", "",
             "### A. Prospective tests (Tables 4 and 19)", "",
             "| Test | Model | Update | Level as run | Open (as run; symmetric high end) | Specific (as run; symmetric high end) | "
             "First as run | Revised as run | First sym. | Revised sym. | Final rule (level) |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for test in ("R10-20", "R10-22"):
        fin = A["levels"][test]["final"]
        for m, per in A[test].items():
            for u, e in per.items():
                if u in ("b_against_a", "control_drift"):
                    continue
                o, s = e["sets_as_run_level"]["open"], e["sets_as_run_level"]["specific"]
                d = e["decisions_as_run_level"]
                lines.append(f"| {test} | {m} | {e['update']} | {100 * e['level_as_run']:.2f}% | {fmt_set(o, 'as_run')}; "
                             f"{o['symmetric'][1]:+.2f} | {fmt_set(s, 'as_run')}; {s['symmetric'][1]:+.2f} | "
                             f"{d['first_as_run']} | {d['revised_as_run']} | {d['first_symmetric']} | {d['revised_symmetric']} | "
                             f"{e['final_rule']} ({100 * fin:.2f}%) |")
    lines += ["", "Final level of R10-20 (C = 10, 99.5%), sets:", ""]
    for m, per in A["R10-20"].items():
        for u in ("a", "b", "c"):
            e = per[u]
            o, s = e["sets_final_level"]["open"], e["sets_final_level"]["specific"]
            lines.append(f"- {m}, {e['update']}: open {fmt_set(o, 'symmetric')}; specific {fmt_set(s, 'symmetric')}; "
                         f"first {e['first_symmetric_final_level']}; revised {e['revised_symmetric_final_level']}; "
                         f"final {e['final_rule']}")
    lines += ["", "Post hoc descriptions (as-run level, both indices):", ""]
    for m, per in A["R10-20"].items():
        x = per["b_against_a"]
        lines.append(f"- R10-20 {m}, first paraphrase against the repeat: open {fmt_set(x['sets']['open'], 'as_run')}, "
                     f"symmetric {x['sets']['open']['symmetric']}; specific {fmt_set(x['sets']['specific'], 'as_run')}, "
                     f"symmetric {x['sets']['specific']['symmetric']}; first {x['first_as_run']} / {x['first_symmetric']}; "
                     f"revised {x['revised_as_run']} / {x['revised_symmetric']}")
    for m, per in A["R10-22"].items():
        for k, s in per["control_drift"].items():
            lines.append(f"- R10-22 {m}, fresh control against the R10-20 control, {k}: {fmt_set(s, 'as_run')}; "
                         f"symmetric {s['symmetric']}")
    lines += ["", "### B. Stored tool calls (Table 16; prospective rows of Table 15)", "", "Tally (variant | level | rule | decision):", "", "```"]
    lines += [f"{k}: {v}" for k, v in B["tally"].items()]
    lines += ["```", "", "Unchanged pairs whose decision is not a hold under some rule:", "",
              "| Variant | Pair | Level | Open | Specific (as run; symmetric) | First as run | Revised as run | First sym. | Revised sym. | Final | Reversed (first as run; first sym.) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for variant in ("one_answer", "all_answers"):
        for e in B["unchanged_" + variant]:
            for lev_name in ("98.75", "99.5"):
                x = e[lev_name]
                rules = [x[k] for k in ("first_as_run", "revised_as_run", "first_symmetric", "revised_symmetric", "final")]
                rv = x["reverse_order"]
                if any(r != "hold" for r in rules) or rv["first_as_run"] != "hold" or rv["first_symmetric"] != "hold":
                    s = x["specific"]
                    lines.append(f"| {variant} | {e['model']} {e['a']} v {e['b']} | {lev_name} | {fmt_set(x['open'], 'as_run')} | "
                                 f"{fmt_set(s, 'as_run')}; {s['symmetric']} | " + " | ".join(rules) +
                                 f" | {rv['first_as_run']}; {rv['first_symmetric']} |")
    lines += ["", "| Edit | Status | Level | Open (as run; sym.) | Specific (as run; sym.) | First as run | Revised as run | "
              "First sym. | Revised sym. | Final | L=3 (as run; sym.) | L=10 (as run; sym.) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, e in B["edits"].items():
        for lev_name in ("98.75", "final"):
            x = e[lev_name]
            o, s = x["open"], x["specific"]
            lv = "98.75" if lev_name == "98.75" else f"{100 * e['final_level']:.2f} (C = {e['C_final']})"
            lines.append(f"| {name} | {e['status']} | {lv} | {fmt_set(o, 'as_run')}; {o['symmetric']} | {fmt_set(s, 'as_run')}; "
                         f"{s['symmetric']} | {x['first_as_run']} | {x['revised_as_run']} | {x['first_symmetric']} | "
                         f"{x['revised_symmetric']} | {x['final']} | {x['first L=3 as_run']}; {x['first L=3 symmetric']} | "
                         f"{x['first L=10 as_run']}; {x['first L=10 symmetric']} |")
    lines += ["", "### C. Table 15 exploratory rows", ""]
    for label, per in out["C"]["forms_99.5"].items():
        for m, e in per.items():
            sp = fmt_set(e["specific"], "as_run") + f"; sym {e['specific']['symmetric']}" if e["specific"] else "-"
            keys = [k for k in e if k.startswith("L=")]
            diff = [k for k in keys if k.endswith("as_run") and e[k] != e[k.replace("as_run", "symmetric")]]
            lines.append(f"- {label}, {m}, 99.5%: open {fmt_set(e['open'], 'as_run')}; sym {e['open']['symmetric']}; specific {sp}; "
                         f"L=5 first {e['L=5 first as_run']}/{e['L=5 first symmetric']}; L=3 {e['L=3 first as_run']}/"
                         f"{e['L=3 first symmetric']}; L=10 {e['L=10 first as_run']}/{e['L=10 first symmetric']}; "
                         f"changed by the index: {diff or 'none'}")
    for m, e in out["C"]["tool_call_full_rename_all_answers_99.58"].items():
        keys = [k for k in e if k.startswith("L=")]
        diff = [k for k in keys if k.endswith("as_run") and e[k] != e[k.replace("as_run", "symmetric")]]
        lines.append(f"- tool-call full rename, all answers, {m}, 99.58%: open {fmt_set(e['open'], 'as_run')}; sym "
                     f"{e['open']['symmetric']}; specific {fmt_set(e['specific'], 'as_run')}; sym {e['specific']['symmetric']}; "
                     f"L=5 {e['L=5 first as_run']}/{e['L=5 first symmetric']}; L=3 {e['L=3 first as_run']}/{e['L=3 first symmetric']}; "
                     f"L=10 {e['L=10 first as_run']}/{e['L=10 first symmetric']}; changed by the index: {diff or 'none'}")
    lines += ["", "### D. Error-rate model (59 requests, one answer each, 98.75%)", "", "```", json.dumps(out["D"], indent=1), "```",
              "", "### E. Floor of the sign condition (one answer per request, no change in the other direction)", "",
              "```", json.dumps(out["E"], indent=1), "```",
              "", "### F. Summary for the paper", "", "```", json.dumps(out["F"], indent=1), "```"]
    return "\n".join(lines) + "\n"


def main():
    out = {"post_hoc": True, "exploratory": True, "L": L, "seed": SEED, "draws": DRAWS,
           "symmetric_k": {f"{100 * lv:.2f}%": k_sym(lv) for lv in (0.95, 0.975, 0.9875, level(6), level(10), level(12))}}
    out["A"] = part_a()
    print("A done", flush=True)
    data, g = V.runs.context()
    sets = V.ra.request_sets(data, g)
    out["B"] = part_b(sets)
    print("B done", flush=True)
    out["C"] = part_c()
    print("C done", flush=True)
    out["D"] = part_d()
    print("D done", flush=True)
    out["E"] = part_e()
    out["F"] = part_f(out)
    OUTDIR.mkdir(exist_ok=True)
    (OUTDIR / "rtest_final9.json").write_text(json.dumps(out, indent=1))
    (OUTDIR / "rtest_final9.md").write_text(md(out))
    print("wrote", OUTDIR / "rtest_final9.md")


if __name__ == "__main__":
    main()
