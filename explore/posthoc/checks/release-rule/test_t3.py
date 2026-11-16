"""Tests of t3_boot.py (SPEC-T3). Usage: python3 -I test_t3.py"""
import importlib.util
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t3", HERE / "t3_boot.py")
t3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t3)
rules = t3.rules


def test_indices():
    # 98.75%, B = 2,000: as run = 12th lowest (index 11) and 13th highest (index 1987); symmetric k = 12
    assert rules.end_index(0.9875, 2000, "as_run") == (11, 1987)
    assert rules.end_index(0.9875, 2000, "symmetric") == (11, 1988)
    # B = 100,000: as run index 624 and 99374; symmetric k = 625 (index 624 and 99375)
    assert rules.end_index(0.9875, 100_000, "as_run") == (624, 99374)
    assert rules.end_index(0.9875, 100_000, "symmetric") == (624, 99375)
    assert rules.k_sym(0.975, 100_000) == 1250 and rules.k_sym(1 - 0.05 / 6, 100_000) == 416
    assert rules.k_sym(0.995, 100_000) == 250 and rules.k_sym(1 - 0.05 / 12, 100_000) == 208
    assert rules.k_sym(0.995, 2000) == 5 and rules.k_sym(1 - 0.05 / 12, 2000) == 4


def test_bootstrap_equals_frozen():
    st_spec = importlib.util.spec_from_file_location("st", HERE.parents[1] / "release-sim" / "stored.py")
    st = importlib.util.module_from_spec(st_spec)
    st_spec.loader.exec_module(st)  # loads the study loaders; no answer file is read on import
    rng = random.Random(5)
    diffs = [rng.choice([0, 0, 0, 10, -10, 100, -100]) for _ in range(59)]
    assert t3.boot_sorted(diffs, 20261112, 2000) == st.boot_vals(diffs, 20261112, 2000)
    assert t3.boot_sorted(diffs, 7, 3000) == st.boot_vals(diffs, 7, 3000)


def fake(open_d, spec_d, rule, level):
    return {"sets": {"open": open_d, "specific": spec_d}, "rules": {rule: {"level": level}}}


def run(ends):
    return {"ends": ends}


def test_boundary_hand_cases():
    # a pass at [-4.9, +1.0]: responsible -L, distance 0.1
    c = fake([0, 1, -1, 0], [0, 2, -2, 0], "final", 0.9875)
    ends = {"open": (-1.0, 1.0), "specific": (-4.9, 1.0)}
    dec, cls = t3.classes_and_decision(c, "final", ends)
    assert dec == "pass"
    b = t3.boundary(c, "final", [{"ends": ends, "decision": dec, "classes": cls}])
    assert b["boundary"] == "-L" and b["set"] == "specific" and abs(b["distance"] - 0.1) < 1e-9
    # a flag at [+0.3, +9] on the specific set (original rule, no sign condition): responsible 0, distance 0.3
    c = fake([0, 0], [10, 0], "original", 0.9875)
    ends = {"open": (-1.0, 1.0), "specific": (0.3, 9.0)}
    dec, cls = t3.classes_and_decision(c, "original", ends)
    assert dec == "flag"
    b = t3.boundary(c, "original", [{"ends": ends, "decision": dec, "classes": cls}])
    assert b["boundary"] == "0" and b["set"] == "specific" and abs(b["distance"] - 0.3) < 1e-9
    # a hold with [-6, +6] and |change| < L: responsible +-L, distance 1
    c = fake([0, 0], [1, -1], "final", 0.9875)
    ends = {"open": (-1.0, 1.0), "specific": (-6.0, 6.0)}
    dec, cls = t3.classes_and_decision(c, "final", ends)
    assert dec == "hold"
    b = t3.boundary(c, "final", [{"ends": ends, "decision": dec, "classes": cls}])
    assert b["boundary"] in ("-L", "+L") and b["set"] == "specific" and abs(b["distance"] - 1.0) < 1e-9
    # two computations that disagree: pass with high end 4.9, hold with high end 5.1 -> crossing +L
    ends1 = {"open": (-1.0, 1.0), "specific": (-2.0, 4.9)}
    ends2 = {"open": (-1.0, 1.0), "specific": (-2.0, 5.1)}
    runs = []
    for e in (ends1, ends2):
        dec, cls = t3.classes_and_decision(c, "final", e)
        runs.append({"ends": e, "decision": dec, "classes": cls})
    assert [r["decision"] for r in runs] == ["pass", "hold"]
    b = t3.boundary(c, "final", runs)
    assert b["changed"] and ("+L", "specific") in b["crossings"]


def test_decisions_equal_decide_sets():
    rng = random.Random(9)
    for _ in range(300):
        o = [rng.choice([0, 0, 100, -100]) for _ in range(40)]
        s = [rng.choice([0, 0, 10, -10, 20, 50]) for _ in range(20)]
        for rule in ("original", "revised", "final", "strat_nosign"):
            lev = rng.choice([0.975, 0.9875, 0.995])
            views = []
            ends = {}
            for name, d in (("open", o), ("specific", s)):
                vals = t3.boot_sorted(d, rng.randrange(10 ** 6), 400)
                views.append({"change": sum(d) / len(d), "up": sum(x > 0 for x in d), "down": sum(x < 0 for x in d),
                              "vals": vals})
                ends[name] = rules.endpoints(vals, lev, rules.RULES[rule][0])
            ref = rules.decide_sets(views, lev, rule)[0]
            got = t3.classes_and_decision(fake(o, s, rule, lev), rule, ends)[0]
            assert ref == got, (rule, lev)


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            print("ok", name)
