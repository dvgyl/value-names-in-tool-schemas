"""Decision rules of the release test (the paper, Section 7 step 5 and Appendix H). Pure functions, no data.

The simulation (sim.py) and the fidelity check (stored.py) use these functions. test_sim.py shows that they give the
same set classes and model decisions as the frozen functions:
- original rule: release_analyze.decide and release_analyze.release (amendment R10-6), as-run index;
- revised rule: release_test.decide and release_test.release (R10-20), as-run index, exact sign condition;
- final rule: rtest_final9.set_class and rtest_final9.model_dec with index "symmetric", alpha = 1 - level and the
  zero-width guard (post hoc rule of the paper).
Two baselines of amendment R10-26 are also here:
- strat_nosign: the final rule without the sign condition (symmetric index, zero-width guard);
- pooled: one interval over the requests of both sets together, symmetric index, at level 1 - 0.05/(C/2),
  no sign condition and no zero-width guard.

Index rules for B sorted resampled means (rtest_final9 docstring):
- as run (stats.percentile): low = value at index round(a B) - 1, high = value at index round((1 - a) B) - 1,
  a = (1 - level) / 2. At 98.75% and B = 2,000: the 12th lowest and the 13th highest.
- symmetric: the k-th lowest and the k-th highest, k = floor(a B), at least 1. At 98.75%: k = 12; at 99.5%: k = 5.
"""
import math

L = 5.0
FLAG, WITHIN, UNRESOLVED = "flag", "within", "unresolved"
RULES = {
    # name: (index rule, sign condition, zero-width guard)
    "original": ("as_run", False, False),
    "revised": ("as_run", True, False),
    "final": ("symmetric", True, True),
    "strat_nosign": ("symmetric", False, True),
}
POOLED_INDEX = "symmetric"
ALL_RULES = tuple(RULES) + ("pooled",)


def level(c):
    """Interval level 1 - 0.05/C (C = models x sets x looks)."""
    return 1 - 0.05 / c


def idx_as_run(q, draws):
    """stats.percentile index rule: round(q B) - 1, inside [0, B - 1]."""
    return min(draws - 1, max(0, int(round(q * draws)) - 1))


def k_sym(lev, draws):
    """rtest_final9.k_sym: floor((1 - level) / 2 x B), at least 1."""
    return max(1, math.floor((1 - lev) / 2 * draws + 1e-9))


def end_index(lev, draws, index):
    """(low index, high index) into the sorted list of B resampled values."""
    if index == "as_run":
        a = (1 - lev) / 2
        return idx_as_run(a, draws), idx_as_run(1 - a, draws)
    k = k_sym(lev, draws)
    return k - 1, draws - k


def endpoints(sorted_vals, lev, index):
    lo, hi = end_index(lev, len(sorted_vals), index)
    return sorted_vals[lo], sorted_vals[hi]


def sign_p(up, down):
    """Two-sided exact sign test (ties dropped), as stats.sign_test and release_test.sign_p."""
    n, k = up + down, min(up, down)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def set_class(change, lo, hi, sign_ok=True, zero_width_guard=False, lim=L):
    """One set: "flag" (meets the flag rule), "within" (within limits) or "unresolved".
    sign_ok: the sign condition holds (pass True for a rule without it)."""
    if abs(change) >= lim and (lo > 0 or hi < 0) and sign_ok:
        return FLAG
    if -lim <= lo and hi <= lim and not (zero_width_guard and lo == hi):
        return WITHIN
    return UNRESOLVED


def model_decision(classes):
    """One model, one look with all requests (n = n_max): flag, pass or hold."""
    if FLAG in classes:
        return "flag"
    if len(classes) == 2 and all(c == WITHIN for c in classes):
        return "pass"
    return "hold"


def pooled_decision(change, lo, hi, lim=L):
    """The pooled baseline: one interval over all requests."""
    if abs(change) >= lim and (lo > 0 or hi < 0):
        return "flag"
    if -lim <= lo and hi <= lim:
        return "pass"
    return "hold"


def decide_sets(sets, lev, rule):
    """sets: list of dicts with change, up, down and the sorted resampled means "vals" (in points).
    Returns (model decision, [set classes], [(lo, hi)])."""
    index, use_sign, guard = RULES[rule]
    alpha = 1 - lev
    classes, ivs = [], []
    for s in sets:
        lo, hi = endpoints(s["vals"], lev, index)
        ok = (sign_p(s["up"], s["down"]) <= alpha) if use_sign else True
        classes.append(set_class(s["change"], lo, hi, ok, guard))
        ivs.append((lo, hi))
    return model_decision(classes), classes, ivs
