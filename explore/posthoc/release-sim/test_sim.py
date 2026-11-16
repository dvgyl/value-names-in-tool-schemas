"""Unit tests for the release-test simulation (amendment R10-26). No model call, no network call.

1. rules.py gives the same set classes and model decisions as the frozen functions (release_analyze.decide and
   release; release_test.decide and release; rtest_final9.set_class and model_dec) on many random inputs, including
   exact boundary values and zero-width intervals.
2. The endpoint indices equal those of stats.percentile and rtest_final9 (idx_as_run, k_sym).
3. The bootstrap of sim.py (both paths) has the distribution of the frozen bootstrap (random.choices over
   requests): the same mean and variance as theory, and quantiles close to those of the frozen bootstrap.
4. The effects are exact: shift, sparse and cancel give the configured mean change.
Usage: python3 -I test_sim.py
"""
import importlib.util
import math
import pathlib
import random
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
AN = HERE.parents[1] / "r10" / "analysis"
sys.path.insert(0, str(HERE))
import rules  # noqa: E402
import sim  # noqa: E402


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V = module("t_v", AN / "rtest_v.py")
RA = V.ra  # release_analyze (frozen, R10-6)
RT = module("t_rt", AN / "release_test.py")  # frozen R10-20 analysis (revised rule)
F9 = module("t_f9", AN / "rtest_final9.py")  # final rule (post hoc)
ST = V.stats

MAP_ORIG = {"flag-worthy": rules.FLAG, "absent": rules.WITHIN, "unresolved": rules.UNRESOLVED}
MAP_REV = {"meets flag rule": rules.FLAG, "within limits": rules.WITHIN, "unresolved": rules.UNRESOLVED}
MAP_F9 = MAP_REV


def rand_set(rng):
    grid = [x / 2 for x in range(-24, 25)]  # -12 to +12 in steps of 0.5: hits 0 and +-5 exactly
    lo, hi = sorted(rng.choice(grid) for _ in range(2))
    if rng.random() < 0.1:
        hi = lo
    change = rng.choice(grid + [lo, hi, (lo + hi) / 2])
    up, down = rng.randrange(0, 15), rng.randrange(0, 15)
    return change, lo, hi, up, down


def test_rules(trials=200_000):
    rng = random.Random(1)
    for _ in range(trials):
        C = rng.choice([2, 4, 6, 10, 12])
        lev = rules.level(C)
        alpha = 1 - lev
        sets = [rand_set(rng) for _ in range(2)]
        # original
        mine = [rules.set_class(c, lo, hi) for c, lo, hi, _u, _d in sets]
        frz = [MAP_ORIG[RA.decide(c, lo, hi, rules.L)] for c, lo, hi, _u, _d in sets]
        assert mine == frz, (sets, mine, frz)
        assert rules.model_decision(mine) == RA.release(*[s[:3] for s in sets], rules.L, 1, 1)
        # revised
        mine = [rules.set_class(c, lo, hi, rules.sign_p(u, d) <= alpha) for c, lo, hi, u, d in sets]
        frz = [MAP_REV[RT.decide(c, lo, hi, rules.L, u, d, alpha)] for c, lo, hi, u, d in sets]
        assert mine == frz, (sets, mine, frz)
        assert rules.model_decision(mine) == RT.release(*sets, rules.L, alpha, 1, 1)
        # final
        mine = [rules.set_class(c, lo, hi, rules.sign_p(u, d) <= alpha, True) for c, lo, hi, u, d in sets]
        f9 = [{"change": c, "symmetric": [lo, hi], "sign_p": F9.V.sign_p(u, d)} for c, lo, hi, u, d in sets]
        frz = [MAP_F9[F9.set_class(s, "symmetric", alpha, True)] for s in f9]
        assert mine == frz, (sets, mine, frz)
        assert rules.model_decision(mine) == F9.model_dec(f9, "symmetric", alpha, True)
        # final without sign = rtest_final9 with alpha None and the guard
        mine = [rules.set_class(c, lo, hi, True, True) for c, lo, hi, _u, _d in sets]
        frz = [MAP_F9[F9.set_class(s, "symmetric", None, True)] for s in f9]
        assert mine == frz
    for u in range(0, 30):
        for d in range(0, 30):
            assert rules.sign_p(u, d) == ST.sign_test(u, d) == F9.V.sign_p(u, d)
    print(f"rules: {trials} random cases equal to the frozen functions (original, revised, final, final without sign)")


def test_indices():
    for C in (2, 4, 6, 10, 12, 20):
        lev = rules.level(C)
        for B in (2000, 20000):
            vals = list(range(B))
            a = (1 - lev) / 2
            lo, hi = rules.endpoints(vals, lev, "as_run")
            assert (lo, hi) == (ST.percentile(vals, a), ST.percentile(vals, 1 - a))
            if B == 2000:
                assert rules.end_index(lev, B, "as_run") == (F9.idx_as_run(a), F9.idx_as_run(1 - a))
                k = F9.k_sym(lev)
                assert rules.end_index(lev, B, "symmetric") == (k - 1, B - k)
    assert rules.end_index(0.9875, 2000, "as_run") == (11, 1987)  # 12th lowest, 13th highest
    assert rules.end_index(0.9875, 2000, "symmetric") == (11, 1988)
    assert rules.end_index(0.995, 2000, "symmetric") == (4, 1995)  # 5th lowest, 5th highest
    print("indices: equal to stats.percentile and rtest_final9 (as run and symmetric)")


def frozen_sums(rng, D, draws):
    return [sum(rng.choices(D, k=len(D))) for _ in range(draws)]


def test_bootstrap(draws=200_000):
    rng = random.Random(7)
    cases = {
        "open-like (448, 3 values)": [1] * 20 + [-1] * 11 + [0] * 417,
        "specific-like (59, 10 answers)": [rng.choice([0, 0, 0, 0, 1, -1, 2, -2, 5, -3, 9]) for _ in range(59)],
        "two values (59)": [1] * 5 + [0] * 54,
    }
    for name, D in cases.items():
        n = len(D)
        mu = n * statistics.fmean(D)
        var = n * statistics.pvariance(D)
        nz = len({x for x in D if x != 0})
        r_new = sim.boot_sums(random.Random(11), D, draws)
        r_frz = frozen_sums(random.Random(12), D, draws)
        for lab, r in (("sim", r_new), ("frozen", r_frz)):
            m, v = statistics.fmean(r), statistics.pvariance(r)
            se = math.sqrt(var / draws)
            assert abs(m - mu) < 5 * se + 1e-9, (name, lab, m, mu)
            assert abs(v - var) < 0.03 * var + 1e-9, (name, lab, v, var)
        q_new = sorted(r_new)
        q_frz = sorted(r_frz)
        for q in (0.0025, 0.00625, 0.5, 0.99375, 0.9975):
            i = int(q * draws)
            assert abs(q_new[i] - q_frz[i]) <= max(1, 0.02 * math.sqrt(var) * 3), (name, q, q_new[i], q_frz[i])
        path = "binomial counts" if nz < 0.058 * n else "random.choices"
        print(f"bootstrap {name}: path {path}; mean and variance match theory; quantiles match the frozen bootstrap")


def test_effects():
    rng = random.Random(3)
    for prof, (a, b) in (("haiku", (0.0260, 0.1760)), ("sol", (0.2918, 0.0612)), ("deepseek", (0.1342, 0.2512))):
        for _ in range(300):
            p = [rng.betavariate(a, b) for _ in range(59)]
            for D in (2, 5, 8, 15, -5):
                if D < 0 and -D / 100 >= statistics.fmean(p):
                    continue
                if D > 0 and D / 100 >= 1 - statistics.fmean(p):
                    continue
                q, _ = sim.shift_exact(p, D)
                assert abs(100 * (sum(q) - sum(p)) / 59 - D) < 1e-9
                assert all(0 <= x <= 1 for x in q)
            for D in ((4, 8, 15) if prof != "sol" else (-4, -8, -15)):
                q, info = sim.sparse_exact(rng, p, D)
                assert abs(100 * (sum(q) - sum(p)) / 59 - D) < 1e-9, (prof, D)
                assert all(0 <= x <= 1 for x in q)
            for kd, ku in ((2, 2), (12, 12)):
                q, info = sim.cancel_exact(rng, p, kd, ku)
                assert abs(sum(q) - sum(p)) < 1e-9
                assert all(0 <= x <= 1 for x in q)
    print("effects: shift, sparse and cancel give the exact mean change; probabilities stay in [0, 1]")


def test_configurations():
    cfgs = sim.configurations()
    assert len(cfgs) == 126, len(cfgs)
    assert len({c["id"] for c in cfgs}) == 126
    assert len(sim.tail_configurations()) == 9
    print("configurations: 126 main configurations with unique ids; 9 tails configurations")


if __name__ == "__main__":
    test_indices()
    test_rules()
    test_bootstrap()
    test_effects()
    test_configurations()
    print("all tests pass")
