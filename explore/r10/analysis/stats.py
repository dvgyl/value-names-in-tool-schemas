"""Shared statistics of round 10 and of the experiment-0 analysis (review/plan15/ACTION-PLAN.md sections 2.10, 3.3, 3.4).
Pure standard library; no data access. Every function is deterministic for a given seed.

- sign_test: the two-sided exact sign test over units (ties dropped).
- permutation_test: the two-sided sign-flip permutation test of the mean of per-unit paired differences.
- holm: Holm's step-down adjustment.
- cluster_bootstrap: a percentile interval, units resampled with replacement inside each group.
- trade / trade_interval: the paired trade estimator of review/plan14/harm_by_model.py (difference 5 of the action
  plan): wrong values removed = sum over the wrong groups of (F0 share - form share) x group size; correct values
  lost = the same on the correct group; ratio = lost / removed. The point values equal those of harm_by_model.py.
  One difference: harm_by_model.py uses one random generator for all its cells in sequence, and trade_interval starts
  a new generator (seed 20261112) for each call. So only the interval of its first cell (Sonnet, F1) is identical;
  the other intervals differ by resampling noise. Round-10 papers take every trade interval from this module.
"""
import math
import random


def sign_test(pos, neg):
    """Two-sided exact binomial p of `pos` units higher against `neg` units lower (ties dropped), p = 0.5."""
    n, k = pos + neg, min(pos, neg)
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def permutation_test(diffs, draws=10_000, seed=0):
    """Two-sided sign-flip permutation p of the mean of `diffs` (one paired difference per unit). The observed
    statistic counts as one draw, so p is never 0."""
    diffs = [d for d in diffs if d is not None]
    if not diffs:
        return 1.0
    obs = abs(sum(diffs) / len(diffs))
    rng = random.Random(seed)
    hits = 1
    for _ in range(draws):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs) / len(diffs)
        hits += abs(s) >= obs - 1e-12
    return hits / (draws + 1)


def holm(pvals):
    """Holm-adjusted p values, in the order of `pvals`."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj, run = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * pvals[i]))
        adj[i] = run
    return adj


def percentile(sorted_vals, q):
    """The value at quantile q of a sorted list, by the index rule of harm_by_model.py (2,000 draws: index 49 and 1949)."""
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(round(q * len(sorted_vals))) - 1))]


def cluster_bootstrap(groups, statistic, draws=2000, seed=20261112, level=0.95):
    """`groups` maps a group name to a list of unit rows; `statistic(sample)` takes the same shape. Units are
    resampled with replacement inside each group. Returns (point, low, high)."""
    rng = random.Random(seed)
    point = statistic(groups)
    vals = sorted(statistic({g: rng.choices(rows, k=len(rows)) for g, rows in groups.items()}) for _ in range(draws))
    a = (1 - level) / 2
    return point, percentile(vals, a), percentile(vals, 1 - a)


def trade(cells, sizes, wrong=("S1t", "S3"), correct="S2"):
    """`cells` maps a group to rows (k0, n0, k1, n1): per paired unit, the F0 hits and reads, the form hits and reads.
    Returns (wrong removed, correct lost, ratio)."""
    sh = {g: (sum(r[0] for r in rows) / sum(r[1] for r in rows), sum(r[2] for r in rows) / sum(r[3] for r in rows))
          for g, rows in cells.items()}
    removed = sum((sh[g][0] - sh[g][1]) * sizes[g] for g in wrong)
    lost = (sh[correct][0] - sh[correct][1]) * sizes[correct]
    return removed, lost, lost / removed if removed > 0 else float("inf")


def trade_interval(cells, sizes, draws=2000, seed=20261112, wrong=("S1t", "S3"), correct="S2"):
    """The point trade and a 95% percentile interval of the ratio, as harm_by_model.py computes them (same rng use)."""
    rng = random.Random(seed)
    point = trade(cells, sizes, wrong, correct)
    ratios = sorted(trade({g: rng.choices(rows, k=len(rows)) for g, rows in cells.items()}, sizes, wrong, correct)[2]
                    for _ in range(draws))
    return point, ratios[int(0.025 * draws) - 1], ratios[int(0.975 * draws) - 1]


def share(k, n):
    return k / n if n else None
