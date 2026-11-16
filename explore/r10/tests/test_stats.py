"""Test of r10/analysis/stats.py. No data access.

Usage (from explore/): .venv/bin/python -I r10/tests/test_stats.py
"""
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import stats  # noqa: E402


def test_sign_test():
    assert stats.sign_test(0, 0) == 1.0
    assert abs(stats.sign_test(10, 0) - 2 / 2 ** 10) < 1e-15
    assert abs(stats.sign_test(5, 5) - 1.0) < 1e-12
    assert stats.sign_test(150, 1) < 1e-40  # E13 Sonnet, 150 to 1 (RESULTS.md reports 1.1e-43)
    print("ok test_sign_test")


def test_permutation_test():
    assert stats.permutation_test([], 100) == 1.0
    p_null = stats.permutation_test([1, -1] * 50, draws=2000, seed=1)
    assert p_null > 0.5, p_null
    p_eff = stats.permutation_test([1] * 40 + [0] * 60, draws=2000, seed=1)
    assert p_eff < 0.001, p_eff
    assert stats.permutation_test([1] * 40, draws=500, seed=3) == stats.permutation_test([1] * 40, draws=500, seed=3)
    # the rate of rejection at 0.025 under the null stays near 0.025
    rng = random.Random(7)
    rej = sum(stats.permutation_test([rng.choice((-1, 0, 1)) for _ in range(60)], draws=400, seed=k) <= 0.025
              for k in range(200))
    assert rej <= 15, rej
    print("ok test_permutation_test")


def test_holm():
    assert stats.holm([0.01, 0.04]) == [0.02, 0.04]
    assert stats.holm([0.04, 0.01]) == [0.04, 0.02]
    assert stats.holm([0.5, 0.6, 0.001]) == [1.0, 1.0, 0.003]
    print("ok test_holm")


def test_trade():
    sizes = {"S1t": 994, "S3": 490, "S2": 545}
    cells = {"S1t": [(1, 2, 0, 2)] * 10, "S3": [(0, 2, 0, 2)] * 10, "S2": [(2, 2, 1, 2)] * 10}
    removed, lost, ratio = stats.trade(cells, sizes)
    assert abs(removed - 0.5 * 994) < 1e-9 and abs(lost - 0.5 * 545) < 1e-9 and abs(ratio - 545 / 994) < 1e-12
    point, lo, hi = stats.trade_interval(cells, sizes, draws=200, seed=1)
    assert lo == hi == ratio  # identical rows: every draw gives the same ratio
    # the index rule of harm_by_model.py for 2,000 draws: index 49 and 1949
    vals = list(range(2000))
    assert stats.percentile(vals, 0.025) == 49 and stats.percentile(vals, 0.975) == 1949
    print("ok test_trade")


def main():
    test_sign_test()
    test_permutation_test()
    test_holm()
    test_trade()
    print("stats test passed")


if __name__ == "__main__":
    main()
