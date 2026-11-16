"""Calibration simulation of the release-test decision rules (amendment R10-26 of PROTOCOL.md).

Status: exploratory, post hoc with respect to the rules (the rules were chosen before this simulation); the design
below was fixed in R10-26 before any simulation output existed. No model call, no paid call, no network call, no
data access: the only input is out/fit.json (stored.py fit). Pure standard library.

Usage (from this folder):
    python3 -I sim.py run            # every configuration and the tails check -> out/sim.json, out/sim.md
    python3 -I sim.py run --workers 8
    python3 -I sim.py time           # times data generation and bootstrap only (no decision is computed)

Data-generating model (one simulated release decision for one model = one trial):
- Two request sets: open (n_open requests, m_open answers per request and arm) and specific (n_spec, m_spec).
  Paper design: 448 x 1 and 59 x 10.
- Per request i, a base hotel probability p_i ~ Beta(a, b) of the profile and set (fit.json), drawn fresh in each
  trial. The old arm gives Binomial(m, p_i) hotel values; the new arm gives Binomial(m, q_i), independent given
  p_i and q_i. The m answers of one request share p_i (within-request dependence).
- q_i comes from the effect of the set (exact per trial: the mean over the set's requests of q_i - p_i equals the
  true change, up to rounding of about 1e-12 points):
  none: q = p.
  shift(D): q_i = clip(p_i + c, 0, 1), c solved exactly (every request moves by about the same amount).
  sparse(D): k = ceil(|D| n / 80) requests chosen at random among those with p <= 0.2 (D > 0) or p >= 0.8 (D < 0)
    move by c = D n / (100 k) (about 80 points each).
  cancel(kd, ku): kd requests chosen at random among those with p >= 0.5 fall, and ku requests chosen at random
    among those with p < 0.5 rise (fewer when fewer exist). Both groups move the same total T = min(sum of p over
    the falling group, sum of 1 - p over the rising group): falling q = p (1 - T / sum p), rising
    q = p + (1 - p) T / sum (1 - p). The mean change is exactly 0; the group that binds moves fully (q = 0 or 1).
- Batch drift d (new arm only): after the effect, the new-arm probabilities move by shift(d). The true change of
  the update stays the effect alone; the drift is not part of it.
- Per request, the observed change is 100 (new hotel values - old hotel values) / m points. Up and down: the
  requests whose observed change is above or below 0.

Estimand: for each set, the mean over the requests of the set of the true change q_i - p_i, in points (the
fixed-set mean of the update effect, without drift). Because the effects are calibrated per trial, it equals the
configured value in every trial.

Rules (rules.py), each at C = 4 (level 98.75%) and C = 10 (99.5%), L = 5 points, one look with all requests,
percentile bootstrap over requests with 2,000 draws; all rules of one trial use the same bootstrap draws:
original, revised, final, strat_nosign (final without the sign condition) and pooled (one interval over the
requests of both sets, request-weighted mean, level 1 - 0.05/(C/2), the same draws of each set combined).

Tails check (separate trials, C = 10 and C = 4): the same data with 2,000 draws (stream A), 2,000 draws (stream B)
and 20,000 draws (stream C); decisions of the original and final rules, and of the original rule with the
symmetric index.
"""
import bisect
import collections
import concurrent.futures as cf
import json
import math
import os
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rules  # noqa: E402

OUT = HERE / "out"
MASTER = "release-sim-R10-26"
DRAWS = 2000
TAIL_DRAWS = 20000
LEVEL_C = (4, 10)
TRIALS = 2000
TAIL_TRIALS = 1000
PAPER = {"n_open": 448, "m_open": 1, "n_spec": 59, "m_spec": 10}
SETS = ("open", "specific")


# ------------------------------------------------------------------------------------------------ configurations

def configurations():
    """Every configuration of R10-26, in a fixed order. Each: id, group, profile, design, effects, drift."""
    cfgs = []

    def add(group, prof, eff_open, eff_spec, drift=0.0, design=None, label=""):
        d = dict(PAPER if design is None else design)
        cid = f"{group}|{prof}|{label}|n{d['n_spec']}m{d['m_spec']}"
        cfgs.append({"id": cid, "group": group, "profile": prof, "design": d,
                     "effects": {"open": eff_open, "specific": eff_spec}, "drift": drift, "label": label})

    none = ("none",)
    for prof in ("haiku", "deepseek", "sol"):
        deltas = [0, 2, 4, 5, 6, 8, 15] + ([] if prof == "haiku" else [-5, -6])
        for D in deltas:  # A: the same shift in both sets
            add("A-both", prof, ("shift", D) if D else none, ("shift", D) if D else none,
                label=f"shift {D:+g} both" if D else "no change")
    for prof in ("haiku", "deepseek", "sol"):
        for D in (2, 4, 5, 6, 8, 15):  # B: shift in the specific set only
            add("B-spec", prof, none, ("shift", D), label=f"shift {D:+g} specific")
    for prof in ("haiku", "deepseek", "sol"):
        sign = -1 if prof == "sol" else 1
        for D in (4, 6, 8, 15):  # S: sparse change in the specific set only
            add("S-sparse", prof, none, ("sparse", sign * D), label=f"sparse {sign * D:+g} specific")
    for prof in ("haiku", "deepseek", "sol"):  # X: cancelling changes, mean exactly 0
        add("X-cancel", prof, none, ("cancel", 2, 2), label="cancel 2 down 2 up specific")
        add("X-cancel", prof, none, ("cancel", 12, 12), label="cancel 12 down 12 up specific")
        add("X-cancel", prof, ("cancel", 10, 10), none, label="cancel 10 down 10 up open")
    for prof in ("haiku", "deepseek", "sol"):  # Z: batch drift on the new arm only
        for d in (2, 3, 5):
            add("Z-drift", prof, none, none, drift=d, label=f"no effect, drift {d:+g}")
        add("Z-drift", prof, ("shift", 6), ("shift", 6), drift=-3, label="shift +6 both, drift -3")
    for prof in ("haiku", "deepseek"):  # N: sample size and answers per request (TR-03); 59 x 10 is in A and B
        for n_spec, m_spec in ((59, 1), (120, 1), (120, 10), (240, 1), (240, 10)):
            design = dict(PAPER, n_spec=n_spec, m_spec=m_spec)
            for D in (0, 2, 5, 6, 8):
                add("N-size", prof, none, ("shift", D) if D else none, design=design,
                    label=f"shift {D:+g} specific" if D else "no change")
    return cfgs


def tail_configurations():
    cfgs = []
    for prof in ("haiku", "deepseek", "sol"):
        for label, eo, es in (("no change", ("none",), ("none",)), ("shift +5 both", ("shift", 5), ("shift", 5)),
                              ("shift +6 specific", ("none",), ("shift", 6))):
            cfgs.append({"id": f"T-tails|{prof}|{label}|n59m10", "group": "T-tails", "profile": prof,
                         "design": dict(PAPER), "effects": {"open": eo, "specific": es}, "drift": 0.0, "label": label})
    return cfgs


def truth(effect):
    """The true change of a set (points), fixed by the design."""
    if effect[0] in ("shift", "sparse"):
        return float(effect[1])
    return 0.0


# ------------------------------------------------------------------------------------------------ effects

def shift_exact(p, delta_pts):
    """q_i = clip(p_i + c, 0, 1) with sum(q - p) / n = delta exactly (piecewise-linear solve)."""
    n = len(p)
    target = delta_pts / 100 * n
    if target == 0:
        return list(p), 0.0
    room = sorted((1 - x) if target > 0 else x for x in p)  # the largest move of each request in this direction
    need = abs(target)
    if need > sum(room) * (1 - 1e-12):
        raise ValueError("infeasible shift")
    # f(c) = sum(min(room_i, c)); find c with f(c) = need
    acc = 0.0
    for j, r in enumerate(room):
        k = n - j  # requests with room >= r (still moving at full c)
        if acc + r * k >= need:
            c = (need - acc) / k
            break
        acc += r
    else:  # pragma: no cover
        raise ValueError("infeasible shift")
    if target > 0:
        return [min(1.0, x + c) for x in p], c
    return [max(0.0, x - c) for x in p], -c


def sparse_exact(rng, p, delta_pts):
    n = len(p)
    k = math.ceil(abs(delta_pts) * n / 80)
    up = delta_pts > 0
    cand = [i for i, x in enumerate(p) if (x <= 0.2 if up else x >= 0.8)]
    fallback = False
    if len(cand) >= k:
        chosen = rng.sample(cand, k)
        c = delta_pts * n / (100 * k)
        q = list(p)
        for i in chosen:  # min/max: floating-point rounding only
            q[i] = min(1.0, max(0.0, p[i] + c))
        return q, {"changed": k, "fallback": False}
    # fallback (fixed in R10-26): the k requests with the most room, moved with clipping, solved exactly
    fallback = True
    order = sorted(range(n), key=lambda i: p[i] if up else -p[i])
    for kk in range(k, n + 1):
        idx = order[:kk]
        sub = [p[i] for i in idx]
        try:
            qs, _ = shift_exact(sub, delta_pts * n / kk)
        except ValueError:
            continue
        q = list(p)
        for i, v in zip(idx, qs):
            q[i] = v
        return q, {"changed": kk, "fallback": fallback}
    raise ValueError("infeasible sparse change")


def cancel_exact(rng, p, k_down, k_up):
    """Down group: k_down requests at random among p >= 0.5; up group: k_up at random among p < 0.5 (fewer when
    fewer exist). T = min(sum of p over the down group, sum of 1 - p over the up group). Down: q = p (1 - T / sum p);
    up: q = p + (1 - p) T / sum(1 - p). The mean change is exactly 0; the binding group moves fully (q = 0 or 1)."""
    n = len(p)
    down_c = [i for i, x in enumerate(p) if x >= 0.5]
    up_c = [i for i, x in enumerate(p) if x < 0.5]
    rng.shuffle(down_c)
    rng.shuffle(up_c)
    down, ups = down_c[:k_down], up_c[:k_up]
    q = list(p)
    loss_cap = sum(p[i] for i in down)
    gain_cap = sum(1 - p[i] for i in ups)
    T = min(loss_cap, gain_cap)
    if T > 0:
        for i in down:  # max/min: floating-point rounding only
            q[i] = max(0.0, p[i] * (1 - T / loss_cap))
        for i in ups:
            q[i] = min(1.0, p[i] + (1 - p[i]) * T / gain_cap)
    harm = sum(1 for i in range(n) if p[i] - q[i] >= 0.3)
    gain = sum(1 for i in range(n) if q[i] - p[i] >= 0.3)
    return q, {"down": len(down) if T > 0 else 0, "up": len(ups) if T > 0 else 0, "harm30": harm, "gain30": gain,
               "moved_points_down": 100 * T / n}


def apply_effect(rng, p, effect):
    kind = effect[0]
    if kind == "none":
        return list(p), {}
    if kind == "shift":
        q, c = shift_exact(p, effect[1])
        return q, {"c": c}
    if kind == "sparse":
        return sparse_exact(rng, p, effect[1])
    if kind == "cancel":
        return cancel_exact(rng, p, effect[1], effect[2])
    raise ValueError(kind)


# ------------------------------------------------------------------------------------------------ data

def binom(rng, m, x):
    if m == 1:
        return 1 if rng.random() < x else 0
    return rng.binomialvariate(m, x)


def gen_set(rng, ab, n, m, effect, drift):
    """One request set. A set that cannot carry the configured shift or drift is drawn again (note of
    2026-11-15 15:23 UTC under R10-26); "redraws" counts these draws."""
    a, b = ab
    for redraws in range(1001):
        p = [rng.betavariate(a, b) for _ in range(n)]
        try:
            q, info = apply_effect(rng, p, effect)
            qn = shift_exact(q, drift)[0] if drift else q
        except ValueError as x:
            if "infeasible" not in str(x):
                raise
            continue
        break
    else:
        raise ValueError("no feasible request set in 1,001 draws")
    true_mean = 100 * (sum(q) - sum(p)) / n
    D = [binom(rng, m, y) - binom(rng, m, x) for x, y in zip(p, qn)]
    return {"D": D, "n": n, "m": m, "true_realized": true_mean, "info": info, "redraws": redraws}


# ------------------------------------------------------------------------------------------------ bootstrap

def boot_sums(rng, D, draws):
    """Unsorted bootstrap sums of D (integers): each is the sum of n requests drawn with replacement. Same
    distribution as stats.cluster_bootstrap (multinomial counts drawn by sequential binomials when few distinct
    non-zero values exist; otherwise random.choices)."""
    n = len(D)
    hist = collections.Counter(D)
    nonzero = sorted((v, c) for v, c in hist.items() if v != 0)
    if not nonzero:
        return [0] * draws
    if len(nonzero) < 0.058 * n:
        bv = rng.binomialvariate
        out = []
        for _ in range(draws):
            rem, rem_c, s = n, n, 0
            for v, c in nonzero:
                if rem == 0:
                    break
                N = rem if c >= rem_c else bv(rem, c / rem_c)
                s += v * N
                rem -= N
                rem_c -= c
            out.append(s)
        return out
    ch = rng.choices
    return [sum(ch(D, k=n)) for _ in range(draws)]


def pts(s, n, m):
    return 100 * s / (n * m)


def set_view(st, sorted_sums):
    """A set for rules.decide_sets: change, up, down and the sorted resampled means in points."""
    n, m = st["n"], st["m"]
    D = st["D"]
    return {"change": pts(sum(D), n, m), "up": sum(1 for x in D if x > 0), "down": sum(1 for x in D if x < 0),
            "vals": [pts(s, n, m) for s in sorted_sums]}


# ------------------------------------------------------------------------------------------------ one configuration

def new_tally():
    return collections.Counter()


def run_config(cfg, prof_params, trials=TRIALS):
    t0 = time.time()
    d = cfg["design"]
    rng_data = random.Random(f"{MASTER}|{cfg['id']}|data")
    rng_boot = random.Random(f"{MASTER}|{cfg['id']}|boot")
    tr = {s: truth(cfg["effects"][s]) for s in SETS}
    n_all = d["n_open"] + d["n_spec"]
    tr_pooled = (d["n_open"] * tr["open"] + d["n_spec"] * tr["specific"]) / n_all
    tal = new_tally()
    info_sum = collections.Counter()
    max_dev = 0.0
    for _t in range(trials):
        sts = {}
        for s, n, m in (("open", d["n_open"], d["m_open"]), ("specific", d["n_spec"], d["m_spec"])):
            sts[s] = gen_set(rng_data, prof_params[s], n, m, cfg["effects"][s], cfg["drift"])
            max_dev = max(max_dev, abs(sts[s]["true_realized"] - tr[s]))
            tal[f"redraw|{s}"] += sts[s]["redraws"]
            for k, v in sts[s]["info"].items():
                if k != "c":
                    info_sum[f"{s}:{k}"] += v
        raw = {s: boot_sums(rng_boot, sts[s]["D"], DRAWS) for s in SETS}
        mo, ms = d["m_open"], d["m_spec"]
        pooled_raw = sorted(a * ms + b * mo for a, b in zip(raw["open"], raw["specific"]))
        pden = mo * ms * n_all
        views = [set_view(sts[s], sorted(raw[s])) for s in SETS]
        for s, v in zip(SETS, views):
            tal[f"changed|{s}"] += v["up"] + v["down"]
        pooled_change = 100 * (sum(sts["open"]["D"]) * ms + sum(sts["specific"]["D"]) * mo) / pden
        pooled_vals = [100 * x / pden for x in pooled_raw]
        for C in LEVEL_C:
            lev = rules.level(C)
            for rule in rules.RULES:
                dec, classes, ivs = rules.decide_sets(views, lev, rule)
                tal[f"dec|{C}|{rule}|{dec}"] += 1
                for s, c in zip(SETS, classes):
                    tal[f"set|{C}|{rule}|{s}|{c}"] += 1
            for index in ("as_run", "symmetric"):
                cov_all = True
                for s, v in zip(SETS, views):
                    lo, hi = rules.endpoints(v["vals"], lev, index)
                    ok = lo <= tr[s] + 1e-9 and tr[s] - 1e-9 <= hi
                    cov_all &= ok
                    tal[f"cov|{C}|{index}|{s}"] += ok
                    tal[f"zero|{C}|{index}|{s}"] += lo == hi
                    tal[f"halfw|{C}|{index}|{s}"] += (hi - lo) / 2
                tal[f"cov|{C}|{index}|both"] += cov_all
            plev = rules.level(C / 2)
            lo, hi = rules.endpoints(pooled_vals, plev, rules.POOLED_INDEX)
            tal[f"dec|{C}|pooled|{rules.pooled_decision(pooled_change, lo, hi)}"] += 1
            tal[f"cov|{C}|pooled|pooled"] += lo <= tr_pooled + 1e-9 and tr_pooled - 1e-9 <= hi
    return {"cfg": cfg, "truth": tr, "truth_pooled": tr_pooled, "trials": trials, "tally": dict(tal),
            "info_sum": dict(info_sum), "max_truth_deviation": max_dev, "seconds": time.time() - t0}


def run_tails(cfg, prof_params, trials=TAIL_TRIALS):
    t0 = time.time()
    d = cfg["design"]
    rng_data = random.Random(f"{MASTER}|{cfg['id']}|data")
    rngs = {k: random.Random(f"{MASTER}|{cfg['id']}|boot-{k}") for k in "ABC"}
    tal = new_tally()
    for _t in range(trials):
        sts = {s: gen_set(rng_data, prof_params[s], n, m, cfg["effects"][s], 0.0)
               for s, n, m in (("open", d["n_open"], d["m_open"]), ("specific", d["n_spec"], d["m_spec"]))}
        for s in SETS:
            tal[f"redraw|{s}"] += sts[s]["redraws"]
        views = {}
        for k, draws in (("A", DRAWS), ("B", DRAWS), ("C", TAIL_DRAWS)):
            views[k] = [set_view(sts[s], sorted(boot_sums(rngs[k], sts[s]["D"], draws))) for s in SETS]
        for C in LEVEL_C:
            lev = rules.level(C)
            dec = {}
            for k in "ABC":
                for rule in ("original", "final"):
                    dec[(k, rule)] = rules.decide_sets(views[k], lev, rule)[0]
                dec[(k, "original_sym")] = rules.model_decision(
                    [rules.set_class(v["change"], *rules.endpoints(v["vals"], lev, "symmetric")) for v in views[k]])
            for rule in ("original", "final", "original_sym"):
                tal[f"dec|{C}|{rule}|A|{dec[('A', rule)]}"] += 1
                tal[f"dec|{C}|{rule}|C|{dec[('C', rule)]}"] += 1
                tal[f"seed|{C}|{rule}"] += dec[("A", rule)] != dec[("B", rule)]
                tal[f"draws|{C}|{rule}"] += dec[("A", rule)] != dec[("C", rule)]
            tal[f"index|{C}|original"] += dec[("A", "original")] != dec[("A", "original_sym")]
            tal[f"index|{C}|original|C"] += dec[("C", "original")] != dec[("C", "original_sym")]
            for si, s in enumerate(SETS):
                for index in ("as_run", "symmetric"):
                    la, ha = rules.endpoints(views["A"][si]["vals"], lev, index)
                    lb, hb = rules.endpoints(views["B"][si]["vals"], lev, index)
                    lc, hc = rules.endpoints(views["C"][si]["vals"], lev, index)
                    tal[f"endseed|{C}|{index}|{s}"] += (abs(la - lb) + abs(ha - hb)) / 2
                    tal[f"enddraws|{C}|{index}|{s}"] += (abs(la - lc) + abs(ha - hc)) / 2
                    tal[f"endseed_sq|{C}|{index}|{s}"] += ((la - lb) ** 2 + (ha - hb) ** 2) / 2
    return {"cfg": cfg, "trials": trials, "tally": dict(tal), "seconds": time.time() - t0}


# ------------------------------------------------------------------------------------------------ summaries

def wilson(k, n, z=1.959964):
    if n == 0:
        return [None, None]
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def share(k, n):
    return {"k": k, "n": n, "share": k / n, "ci95": wilson(k, n)}


def summarise(res):
    cfg, n, t = res["cfg"], res["trials"], res["tally"]
    tr = res["truth"]
    big = max(abs(tr["open"]), abs(tr["specific"]))
    kind = "null" if big == 0 else ("inside" if big < rules.L else ("at" if big == rules.L else "outside"))
    out = {"id": cfg["id"], "group": cfg["group"], "profile": cfg["profile"], "label": cfg["label"],
           "design": cfg["design"], "effects": cfg["effects"], "drift": cfg["drift"], "truth": tr,
           "truth_pooled": res["truth_pooled"], "truth_kind": kind, "trials": n, "seconds": res["seconds"],
           "max_truth_deviation": res["max_truth_deviation"],
           "mean_changed_requests": {s: t.get(f"changed|{s}", 0) / n for s in SETS},
           "redraws": {s: t.get(f"redraw|{s}", 0) for s in SETS},
           "effect_info_mean": {k: v / n for k, v in res["info_sum"].items()}, "levels": {}}
    for C in LEVEL_C:
        e = {"level": rules.level(C), "pooled_level": rules.level(C / 2), "decisions": {}, "set_classes": {},
             "coverage": {}, "zero_width": {}, "mean_half_width": {}}
        for rule in rules.ALL_RULES:
            e["decisions"][rule] = {dcs: share(t.get(f"dec|{C}|{rule}|{dcs}", 0), n) for dcs in ("flag", "pass", "hold")}
        for rule in rules.RULES:
            e["set_classes"][rule] = {s: {c: share(t.get(f"set|{C}|{rule}|{s}|{c}", 0), n)
                                          for c in (rules.FLAG, rules.WITHIN, rules.UNRESOLVED)} for s in SETS}
        for index in ("as_run", "symmetric"):
            e["coverage"][index] = {s: share(t.get(f"cov|{C}|{index}|{s}", 0), n) for s in SETS + ("both",)}
            e["zero_width"][index] = {s: share(t.get(f"zero|{C}|{index}|{s}", 0), n) for s in SETS}
            e["mean_half_width"][index] = {s: t.get(f"halfw|{C}|{index}|{s}", 0) / n for s in SETS}
        e["coverage"]["pooled"] = share(t.get(f"cov|{C}|pooled|pooled", 0), n)
        err = {}
        for rule in rules.ALL_RULES:
            dd = e["decisions"][rule]
            if kind == "null":
                err[rule] = {"false_flag": dd["flag"]}
            elif kind == "outside":
                err[rule] = {"wrong_pass": dd["pass"], "detection": dd["flag"]}
            elif kind == "at":
                err[rule] = {"detection": dd["flag"]}
            else:
                err[rule] = {"flag_below_L": dd["flag"]}
            if rule in rules.RULES:
                for s in SETS:
                    if tr[s] == 0:
                        err[rule][f"set_false_flag_{s}"] = e["set_classes"][rule][s][rules.FLAG]
        e["errors"] = err
        out["levels"][str(C)] = e
    return out


def summarise_tails(res):
    cfg, n, t = res["cfg"], res["trials"], res["tally"]
    out = {"id": cfg["id"], "profile": cfg["profile"], "label": cfg["label"], "trials": n, "seconds": res["seconds"],
           "redraws": {s: t.get(f"redraw|{s}", 0) for s in SETS}, "levels": {}}
    for C in LEVEL_C:
        e = {"level": rules.level(C), "decisions_2000": {}, "decisions_20000": {}, "changed_by_seed": {},
             "changed_by_draws": {}, "changed_by_index": {}, "endpoint_mean_abs_change": {}}
        for rule in ("original", "final", "original_sym"):
            e["decisions_2000"][rule] = {x: t.get(f"dec|{C}|{rule}|A|{x}", 0) / n for x in ("flag", "pass", "hold")}
            e["decisions_20000"][rule] = {x: t.get(f"dec|{C}|{rule}|C|{x}", 0) / n for x in ("flag", "pass", "hold")}
            e["changed_by_seed"][rule] = share(t.get(f"seed|{C}|{rule}", 0), n)
            e["changed_by_draws"][rule] = share(t.get(f"draws|{C}|{rule}", 0), n)
        e["changed_by_index"]["original, 2,000 draws"] = share(t.get(f"index|{C}|original", 0), n)
        e["changed_by_index"]["original, 20,000 draws"] = share(t.get(f"index|{C}|original|C", 0), n)
        for s in SETS:
            for index in ("as_run", "symmetric"):
                e["endpoint_mean_abs_change"][f"{s} {index}"] = {
                    "other_seed_2000": t.get(f"endseed|{C}|{index}|{s}", 0) / n,
                    "rms_other_seed_2000": math.sqrt(t.get(f"endseed_sq|{C}|{index}|{s}", 0) / n),
                    "draws_20000": t.get(f"enddraws|{C}|{index}|{s}", 0) / n}
        out["levels"][str(C)] = e
    return out


# ------------------------------------------------------------------------------------------------ report

def pc(x, nd=1):
    return "-" if x is None else f"{100 * x:.{nd}f}"


def ci(sh, nd=1):
    lo, hi = sh["ci95"]
    return f"{pc(sh['share'], nd)} [{pc(lo, nd)}, {pc(hi, nd)}]"


def fph(dd):
    return f"{pc(dd['flag']['share'])} / {pc(dd['pass']['share'])} / {pc(dd['hold']['share'])}"


RULE_NAMES = {"original": "Original", "revised": "Revised", "final": "Final", "strat_nosign": "Final without sign",
              "pooled": "Pooled"}


def markdown(out):
    S = out["summaries"]
    lines = ["# Release-test calibration simulation (amendment R10-26)", "",
             "Exploratory; post hoc with respect to the rules; design fixed before any output. "
             f"Trials per configuration: {out['trials']}; bootstrap draws: {DRAWS}; L = {rules.L:g} points. "
             "Each cell gives the share of trials, in percent. F / P / H: flag / pass / hold. "
             "Brackets: 95% Wilson interval of the simulation (Monte Carlo) uncertainty.", "",
             f"Run time: {out['run_seconds']:.0f} s wall clock with {out['workers']} worker processes "
             f"({out['cpu_seconds']:.0f} s summed over configurations).", ""]

    def table(group_filter, C, title, note=""):
        rows = [s for s in S if group_filter(s)]
        lines.extend([f"## {title} (C = {C}, level {100 * rules.level(C):.2f}%; pooled {100 * rules.level(C / 2):.2f}%)", ""])
        if note:
            lines.extend([note, ""])
        lines.append("| Profile | Configuration | Design (spec.) | True open / spec. | " +
                     " | ".join(f"{RULE_NAMES[r]} F / P / H" for r in rules.ALL_RULES) + " |")
        lines.append("|---|---|---|---|" + "---|" * len(rules.ALL_RULES))
        for s in rows:
            e = s["levels"][str(C)]["decisions"]
            d = s["design"]
            lines.append(f"| {s['profile']} | {s['label']} | {d['n_spec']} x {d['m_spec']} | "
                         f"{s['truth']['open']:+g} / {s['truth']['specific']:+g} | " +
                         " | ".join(fph(e[r]) for r in rules.ALL_RULES) + " |")
        lines.append("")

    for C in LEVEL_C:
        table(lambda s: s["group"] == "A-both", C, "A. The same shift in both sets")
        table(lambda s: s["group"] == "B-spec", C, "B. Shift in the specific set only")
        table(lambda s: s["group"] == "S-sparse", C, "S. Sparse change in the specific set (about 80 points on a few requests)")
        table(lambda s: s["group"] == "X-cancel", C, "X. Cancelling changes (true mean change exactly 0)")
        table(lambda s: s["group"] == "Z-drift", C, "Z. Batch drift on the new arm only (true change of the update: as stated)")
        table(lambda s: s["group"] == "N-size", C, "N. Sample size and answers per specific request (open set 448 x 1)")

    lines += ["## Error summary", "",
              "False flag: flag when the true change is 0 in both sets. Wrong pass: pass when the true change exceeds "
              "L in size in at least one set. Detection: flag when the true change is at least L in size in at "
              "least one set. Largest value over the configurations of each kind (with its configuration).", ""]
    for C in LEVEL_C:
        lines += [f"### C = {C}", "", "| Rule | Largest false flag | Largest wrong pass | Smallest detection at |true| >= L | "
                  "Largest set-level false flag (a set with true change 0) |", "|---|---|---|---|---|"]
        for rule in rules.ALL_RULES:
            ff = [(x["levels"][str(C)]["errors"][rule]["false_flag"], x) for x in S if x["truth_kind"] == "null"]
            wp = [(x["levels"][str(C)]["errors"][rule]["wrong_pass"], x) for x in S if x["truth_kind"] == "outside"]
            dt = [(x["levels"][str(C)]["errors"][rule]["detection"], x) for x in S if x["truth_kind"] in ("at", "outside")]
            sf = [(v, x) for x in S for k, v in x["levels"][str(C)]["errors"][rule].items() if k.startswith("set_false_flag")]

            def best(lst, fn):
                if not lst:
                    return "-"
                v, x = fn(lst, key=lambda z: z[0]["share"])
                return f"{ci(v)} ({x['profile']}, {x['label']}, {x['design']['n_spec']} x {x['design']['m_spec']})"
            lines.append(f"| {RULE_NAMES[rule]} | {best(ff, max)} | {best(wp, max)} | {best(dt, min)} | "
                         f"{best(sf, max) if rule != 'pooled' else '-'} |")
        lines.append("")

    lines += ["## Coverage of the intervals", "",
              "Share of trials whose interval contains the true change of the set (nominal: the level for one set; "
              "at least 95% for both sets together under the Bonferroni argument). Zero width: share of trials whose "
              "interval has zero width.", ""]
    for C in LEVEL_C:
        lines += [f"### C = {C} (nominal {100 * rules.level(C):.2f}% per set)", "",
                  "| Profile | Configuration | Design | Open, as run | Specific, as run | Both, as run | Open, sym. | "
                  "Specific, sym. | Both, sym. | Zero width spec. (sym.) | Pooled |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for s in S:
            c = s["levels"][str(C)]["coverage"]
            z = s["levels"][str(C)]["zero_width"]["symmetric"]["specific"]
            d = s["design"]
            lines.append(f"| {s['profile']} | {s['label']} | {d['n_spec']} x {d['m_spec']} | "
                         f"{pc(c['as_run']['open']['share'])} | {pc(c['as_run']['specific']['share'])} | "
                         f"{pc(c['as_run']['both']['share'])} | {pc(c['symmetric']['open']['share'])} | "
                         f"{pc(c['symmetric']['specific']['share'])} | {pc(c['symmetric']['both']['share'])} | "
                         f"{pc(z['share'])} | {pc(c['pooled']['share'])} |")
        lines.append("")

    lines += ["## Effect details", "", "Redraws: request sets drawn again because they could not carry the configured "
              "shift or drift (note of 2026-11-15 15:23 UTC under R10-26), summed over the trials.", "",
              "| Configuration | Mean changed requests open / spec. (observed) | Effect details (mean per trial) | "
              "Redraws open / spec. | Largest truth deviation (points) |", "|---|---|---|---|---|"]
    for s in S:
        mc = s["mean_changed_requests"]
        info = ", ".join(f"{k} {v:.2f}" for k, v in sorted(s["effect_info_mean"].items()))
        rd = s["redraws"]
        lines.append(f"| {s['id']} | {mc['open']:.1f} / {mc['specific']:.1f} | {info or '-'} | {rd['open']} / "
                     f"{rd['specific']} | {s['max_truth_deviation']:.1e} |")
    lines.append("")

    lines += ["## Tails of the percentile interval", "",
              f"{TAIL_TRIALS} trials per configuration (paper design). Each trial: the same data with 2,000 draws "
              "(stream A), 2,000 draws (stream B, another seed) and 20,000 draws (stream C). Shares of trials whose "
              "model decision changes; mean absolute change of an interval end, in points.", ""]
    for C in LEVEL_C:
        lines += [f"### C = {C} ({100 * rules.level(C):.2f}%)", "",
                  "| Profile | Configuration | Final F/P/H (2,000) | Final F/P/H (20,000) | Changed by seed: original / final | "
                  "Changed by 20,000 draws: original / final | Changed by index (original; 2,000 / 20,000) | "
                  "End change by seed, open / spec. (as run) | End change by 20,000 draws, open / spec. (as run) |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for x in out["tails"]:
            e = x["levels"][str(C)]
            f2, f20 = e["decisions_2000"]["final"], e["decisions_20000"]["final"]
            em = e["endpoint_mean_abs_change"]
            lines.append(
                f"| {x['profile']} | {x['label']} | {pc(f2['flag'])} / {pc(f2['pass'])} / {pc(f2['hold'])} | "
                f"{pc(f20['flag'])} / {pc(f20['pass'])} / {pc(f20['hold'])} | "
                f"{ci(e['changed_by_seed']['original'])} / {ci(e['changed_by_seed']['final'])} | "
                f"{ci(e['changed_by_draws']['original'])} / {ci(e['changed_by_draws']['final'])} | "
                f"{ci(e['changed_by_index']['original, 2,000 draws'])} / {ci(e['changed_by_index']['original, 20,000 draws'])} | "
                f"{em['open as_run']['other_seed_2000']:.2f} / {em['specific as_run']['other_seed_2000']:.2f} | "
                f"{em['open as_run']['draws_20000']:.2f} / {em['specific as_run']['draws_20000']:.2f} |")
        lines.append("")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------------------------------------ main

def profiles():
    fit = json.loads((OUT / "fit.json").read_text())
    return {p: {s: (e["sets"][s]["a"], e["sets"][s]["b"]) for s in SETS} for p, e in fit["profiles"].items()}


def _main_task(args):
    kind, cfg, prof = args
    return kind, (run_config(cfg, prof) if kind == "main" else run_tails(cfg, prof))


def main_run(workers):
    profs = profiles()
    cfgs, tails = configurations(), tail_configurations()
    tasks = [("tails", c, profs[c["profile"]]) for c in tails] + [("main", c, profs[c["profile"]]) for c in cfgs]
    # longest tasks first
    tasks.sort(key=lambda t: -(10 if t[0] == "tails" else 1) * t[1]["design"]["n_spec"] * t[1]["design"]["m_spec"])
    t0 = time.time()
    res_main, res_tails = {}, {}
    with cf.ProcessPoolExecutor(max_workers=workers) as ex:
        for kind, r in ex.map(_main_task, tasks):
            (res_main if kind == "main" else res_tails)[r["cfg"]["id"]] = r
            print(f"{kind} {r['cfg']['id']}: {r['seconds']:.1f} s", flush=True)
    wall = time.time() - t0
    out = {"amendment": "R10-26", "exploratory": True, "post_hoc_wrt_rules": True, "master_seed": MASTER,
           "trials": TRIALS, "tail_trials": TAIL_TRIALS, "draws": DRAWS, "tail_draws": TAIL_DRAWS, "L": rules.L,
           "levels_C": list(LEVEL_C), "profiles": {p: {s: list(v) for s, v in x.items()} for p, x in profs.items()},
           "workers": workers, "run_seconds": wall,
           "cpu_seconds": sum(r["seconds"] for r in list(res_main.values()) + list(res_tails.values())),
           "summaries": [summarise(res_main[c["id"]]) for c in cfgs],
           "tails": [summarise_tails(res_tails[c["id"]]) for c in tails],
           "raw_tallies": {cid: r["tally"] for cid, r in res_main.items()}}
    OUT.mkdir(exist_ok=True)
    (OUT / "sim.json").write_text(json.dumps(out, indent=1))
    (OUT / "sim.md").write_text(markdown(out))
    print(f"wrote {OUT / 'sim.md'} and sim.json; wall {wall:.0f} s")


def time_only():
    """Times data generation and bootstrap of the heaviest designs. No decision is computed or printed."""
    profs = profiles()
    for design in (PAPER, dict(PAPER, n_spec=240, m_spec=10)):
        rng = random.Random("timing")
        t0 = time.time()
        for _ in range(50):
            for s, n, m in (("open", design["n_open"], design["m_open"]), ("specific", design["n_spec"], design["m_spec"])):
                st = gen_set(rng, profs["deepseek"][s], n, m, ("shift", 5), 0.0)
                sorted(boot_sums(rng, st["D"], DRAWS))
        print(f"design {design}: {(time.time() - t0) / 50 * 1000:.1f} ms per trial (generation and bootstrap only)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else (os.cpu_count() or 4)
        main_run(w)
    elif cmd == "time":
        time_only()
    else:
        sys.exit("Usage: python3 -I sim.py run [--workers N] | time")
