"""Tests of n3_d3_check.py with a case computed by hand (SPEC-N3-D3.md). Run: python3 -I test_n3_d3_check.py"""
import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("n3", HERE / "n3_d3_check.py")
n3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n3)

# Sonnet, planned gate, one answer per dialogue: no-type 188 values, 16 kept ("yes"); guesthouse 15, 0 kept;
# hotel 369, 126 kept. By hand: R = 172 + 15 = 187, L = 243, ratio 243 / 187 = 1.2995, share 187 / 203 = 92.12%.
counts = {"S1t": (188, 16), "S3": (15, 0), "S2": (369, 126)}
base = {"S1t": 994, "S3": 490, "S2": 545}
R, L, share, ratio = n3.trade(counts, base, base)
assert abs(R - 187) < 1e-9 and abs(L - 243) < 1e-9, (R, L)
assert round(ratio, 2) == 1.30 and round(100 * share, 1) == 92.1
# Without the guesthouse group (the printed D3): 243 / 172 = 1.41.
R, L, share, ratio = n3.trade(counts, base, base, ("S1t",))
assert R == 172 and round(ratio, 2) == 1.41
# Decreases for a two-answer model halve the counts: Haiku planned no-type 25 + guesthouse 11 removed -> 18.
assert n3.decreases({"S1t": (89, 64), "S3": (21, 10), "S2": (441, 361)}, 2) == (18.0, 40.0)
# Exact bases matter: Luna clear-no with n0 = 1988, 980 and n1 = 1987, 978 gives 48.0%; simple bases give 48.1%.
c = {"S1t": (427, 240), "S3": (39, 2), "S2": (709, 443)}
_, _, s_exact, _ = n3.trade(c, {"S1t": 1988, "S3": 980, "S2": 1090}, {"S1t": 1987, "S3": 978, "S2": 1090})
_, _, s_simple, _ = n3.trade(c, {"S1t": 1988, "S3": 980, "S2": 1090}, {"S1t": 1988, "S3": 980, "S2": 1090})
assert round(100 * s_exact, 1) == 48.0 and round(100 * s_simple, 1) == 48.1, (s_exact, s_simple)
print("test_n3_d3_check: all tests passed")
