"""Tests of t1_derived.py (SPEC-T1b) on a hand-made two-configuration input. Usage: python3 -I test_t1b.py"""
import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t1b", HERE / "t1_derived.py")
t1b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t1b)


def cfg(cid, group, flags, passes):
    """flags/passes: {rule: k} at both levels; n = 2,000."""
    rules = ("original", "revised", "final", "strat_nosign", "pooled")
    lv = {"decisions": {r: {"flag": {"k": flags[r], "n": 2000}, "pass": {"k": passes[r], "n": 2000},
                            "hold": {"k": 2000 - flags[r] - passes[r], "n": 2000}} for r in rules}}
    return {"id": cid, "group": group, "design": {"n_spec": 59, "m_spec": 10}, "drift": 0.0, "trials": 2000,
            "levels": {"4": lv, "10": lv}}


def test_hand_case():
    f1 = {"original": 10, "revised": 8, "final": 8, "strat_nosign": 10, "pooled": 0}
    p1 = {"original": 100, "revised": 100, "final": 90, "strat_nosign": 90, "pooled": 2000}
    f2 = {"original": 40, "revised": 21, "final": 21, "strat_nosign": 40, "pooled": 0}
    p2 = {"original": 0, "revised": 0, "final": 0, "strat_nosign": 1, "pooled": 0}
    S = [cfg("A-both|x|shift +6 both|n59m10", "A-both", f1, p1), cfg("B-spec|x|shift +6 specific|n59m10", "B-spec", f2, p2)]
    pe = t1b.pass_equal(S)
    assert pe["4"]["final_vs_nosign_differ"] == ["B-spec|x|shift +6 specific|n59m10"]
    assert pe["4"]["original_vs_revised_differ"] == []
    fd = t1b.flag_diff(S, ("A-both", "B-spec"), 4)
    assert abs(fd["largest_points"] - 0.95) < 1e-12 and fd["id"].startswith("B-spec"), fd  # (40 - 21) / 2000


if __name__ == "__main__":
    test_hand_case()
    print("ok test_hand_case")
