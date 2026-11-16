"""Exact (Clopper-Pearson) two-sided 95% upper bounds for the second-step removal rates.
Haiku: 0 removals in 39 non-empty trials (Table D2), from 23 first requests.
Luna: 15 removals in 179 non-empty trials (Table D2).
Usage (from explore/): python3 -I r10/analysis/loyal_cp_bounds.py. It prints the bounds.
This file is a copy of the project script cp_bounds.py with the paths of the study folder; the results are the same.
"""
from math import comb

def cdf(k, n, p):
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k + 1))

def upper(k, n, alpha=0.05):
    # largest p with P(X <= k | p) >= alpha/2, by bisection
    lo, hi = k / n, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if cdf(k, n, mid) > alpha / 2:
            lo = mid
        else:
            hi = mid
    return lo

for name, k, n in (("haiku trials", 0, 39), ("haiku requests", 0, 23), ("luna trials", 15, 179)):
    print(f"{name}: {k}/{n} upper 95% = {100*upper(k, n):.1f}%")
