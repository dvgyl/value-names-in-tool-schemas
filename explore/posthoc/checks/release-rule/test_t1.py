"""Tests of t1_compare.py (SPEC-T1). Usage: python3 -I test_t1.py"""
import importlib.util
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t1", HERE / "t1_compare.py")
t1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t1)


def test_wilson():
    lo, hi = t1.wilson(0, 2000)
    assert abs(lo) < 1e-12 and abs(hi - 0.0019170) < 1e-6, hi  # z^2 / (n + z^2) = 3.8415 / 2003.84
    # k = 80, n = 2000 by hand: p = 0.04, centre = (0.04 + 3.8415/4000) / (1 + 3.8415/2000)
    z2 = 1.959964 ** 2
    c = (0.04 + z2 / 4000) / (1 + z2 / 2000)
    h = 1.959964 * math.sqrt(0.04 * 0.96 / 2000 + z2 / (4 * 2000 ** 2)) / (1 + z2 / 2000)
    lo, hi = t1.wilson(80, 2000)
    assert abs(lo - (c - h)) < 1e-12 and abs(hi - (c + h)) < 1e-12
    assert abs(lo - 0.03228) < 1e-4 and abs(hi - 0.04950) < 1e-4, (lo, hi)


def test_cells_and_tallies():
    sim, by_id = t1.load()
    s = by_id["A-both|haiku|no change|n59m10"]
    e = t1.cell(s, 4, "final")
    assert (e["flag"]["k"], e["pass"]["k"], e["hold"]["k"]) == (0, 1920, 80), e
    raw = sim["raw_tallies"]["A-both|haiku|no change|n59m10"]
    for rule in t1.RULES:
        for x in ("flag", "pass", "hold"):
            assert t1.cell(s, 4, rule)[x]["k"] == raw.get(f"dec|4|{rule}|{x}", 0), (rule, x)


def test_every_row_sums():
    out = t1.build()
    for c, lv in out["levels"].items():
        for sc in lv["scenarios"]:
            for p, row in sc["profiles"].items():
                for r, e in row["rules"].items():
                    assert e["flag"]["k"] + e["pass"]["k"] + e["hold"]["k"] == e["flag"]["n"] == 2000, (c, sc["key"], p, r)
        assert len(lv["beyond_margin"]["configurations"]) > 0


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            print("ok", name)
