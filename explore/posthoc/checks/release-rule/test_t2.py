"""Tests of t2_signfloor.py (SPEC-T2). Usage: python3 -I test_t2.py"""
import importlib.util
import pathlib
import sys
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t2", HERE / "t2_signfloor.py")
t2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t2)
sys.path.insert(0, str(HERE.parents[1] / "release-sim"))
import rules  # noqa: E402  (the rule code of the simulation; unchanged)


def test_hand_cases():
    assert t2.sign_p(5, 0) == Fraction(1, 16)            # 0.0625 (Table 10 example)
    assert t2.sign_p(7, 0) == Fraction(1, 64)            # 0.015625
    assert t2.sign_p(8, 0) == Fraction(1, 128)           # 0.0078125
    assert t2.sign_p(0, 0) == 1
    assert round(float(t2.sign_p(21, 5)), 4) == 0.0025   # DeepSeek paraphrase 1, Table 13
    assert round(float(t2.sign_p(4, 12)), 4) == 0.0768   # Luna paraphrase 2, Table 13
    assert round(float(t2.sign_p(7, 0)), 4) == 0.0156    # Sonnet hotel rewrite, Table 14


def test_against_rules_py():
    for r in range(0, 40):
        for f in range(0, 40):
            assert abs(float(t2.sign_p(r, f)) - rules.sign_p(r, f)) < 1e-12, (r, f)


def test_floors():
    out = t2.build()
    fl = out["floors"]
    assert {c: v["d_min"] for c, v in fl.items()} == {2: 7, 4: 8, 6: 8, 10: 9, 12: 9}
    assert round(fl[4]["change_floor_points_59x1"], 1) == 13.6
    assert round(fl[10]["change_floor_points_59x1"], 1) == 15.3


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            print("ok", name)
