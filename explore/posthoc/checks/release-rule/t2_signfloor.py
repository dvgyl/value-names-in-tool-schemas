"""T2 (SPEC-T2-sign-floor.md): the floor of the sign condition of the release rule, checked with exact arithmetic.

Analytical consequence of the stated rule (two-sided exact sign test, ties dropped, flag only if p <= 0.05/C). The
descriptive means come from the existing simulation output (posthoc/release-sim/out/sim.json); nothing is simulated.
Usage: python3 -I t2_signfloor.py      -> out/t2_signfloor.json, out/t2_signfloor.md
"""
import json
import math
import pathlib
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
SIM = HERE.parents[1] / "release-sim" / "out" / "sim.json"
OUT = HERE / "out"
ALPHA = Fraction(5, 100)
C_USED = {2: "97.5% (fresh test, Luna-only updates)", 4: "98.75% (tool calls, two-model test, fresh test)",
          6: "99.17% (forms in the five-model test; final rule for Haiku's field-order edit)",
          10: "99.5% (final rule, five-model test and stored comparisons)", 12: "99.58% (final rule, Haiku's repeat)"}


def sign_p(r, f):
    """Exact two-sided sign test as a Fraction (rules.sign_p): min(1, 2 P(X <= min(r, f))), X ~ Bin(r + f, 1/2)."""
    d, k = r + f, min(r, f)
    if d == 0:
        return Fraction(1)
    return min(Fraction(1), Fraction(2 * sum(math.comb(d, i) for i in range(k + 1)), 2 ** d))


def p_min(d):
    return min(sign_p(r, d - r) for r in range(d + 1))


def d_min_enum(c):
    level = ALPHA / c
    return next(d for d in range(1, 200) if p_min(d) <= level)


def d_min_closed(c):
    return math.ceil(1 + math.log2(c / 0.05))


def sim_means():
    sim = json.loads(SIM.read_text())
    out = {}
    for s in sim["summaries"]:
        d = s["design"]
        if (d["n_spec"], d["m_spec"]) != (59, 10):
            continue
        if s["group"] == "S-sparse" and abs(s["truth"]["specific"]) == 8:
            out[s["id"]] = {"truly_changed_specific": s["effect_info_mean"]["specific:changed"],
                            "observed_nonzero_specific": s["mean_changed_requests"]["specific"]}
        if s["group"] == "A-both" and s["label"] == "no change":
            out[s["id"]] = {"truly_changed_specific": 0, "observed_nonzero_specific": s["mean_changed_requests"]["specific"]}
    return out


def build():
    pmin = {d: p_min(d) for d in range(1, 31)}
    assert all(pmin[d] == Fraction(2, 2 ** d) for d in pmin), "p_min(d) = 2^(1-d)"
    floors = {}
    for c, where in C_USED.items():
        de, dc = d_min_enum(c), d_min_closed(c)
        assert de == dc, (c, de, dc)
        floors[c] = {"level": float(1 - ALPHA / c), "alpha_over_C": float(ALPHA / c), "used": where, "d_min": de,
                     "p_at_d_min": float(pmin[de]), "p_at_d_min_minus_1": float(pmin[de - 1]),
                     "change_floor_points_59x1": 100 * de / 59, "change_floor_points_448x1": 100 * de / 448,
                     "change_floor_points_59x10": 100 * de / (59 * 10)}
    return {"what": "T2: floor of the sign condition (exact arithmetic) and observed nonzero differences in the "
                    "existing simulation", "p_min": {d: {"fraction": str(pmin[d]), "decimal": float(pmin[d])}
                                                    for d in range(1, 13)},
            "floors": floors, "sim_means": sim_means()}


def markdown(out):
    lines = ["# T2: floor of the sign condition", "",
             "p_min(d) = 2^(1−d): the smallest two-sided exact sign-test p with d nonzero differences (ties dropped). "
             "Checked by enumeration for d = 1 to 30.", "", "| d | p_min (fraction) | p_min |", "|---:|---|---:|"]
    for d, v in out["p_min"].items():
        lines.append(f"| {d} | {v['fraction']} | {v['decimal']:.7g} |")
    lines += ["", "| C | Level | 0.05/C | d_min (enumeration = closed form) | p at d_min | p at d_min − 1 | "
              "Change floor, 59 × 1 (points) | 448 × 1 | 59 × 10 | Used in the paper |", "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for c, v in out["floors"].items():
        lines.append(f"| {c} | {100 * v['level']:.2f}% | {v['alpha_over_C']:.6g} | {v['d_min']} | {v['p_at_d_min']:.7g} | "
                     f"{v['p_at_d_min_minus_1']:.7g} | {v['change_floor_points_59x1']:.2f} | "
                     f"{v['change_floor_points_448x1']:.2f} | {v['change_floor_points_59x10']:.2f} | {v['used']} |")
    lines += ["", "## Truly changed against observed nonzero specific differences (sim.json, means per trial)", "",
              "| Configuration | Truly changed specific requests | Specific requests with an observed nonzero difference |",
              "|---|---:|---:|"]
    for k, v in out["sim_means"].items():
        lines.append(f"| `{k}` | {v['truly_changed_specific']:g} | {v['observed_nonzero_specific']:.2f} |")
    return "\n".join(lines) + "\n"


def main():
    out = build()
    OUT.mkdir(exist_ok=True)
    (OUT / "t2_signfloor.json").write_text(json.dumps(out, indent=1))
    (OUT / "t2_signfloor.md").write_text(markdown(out))
    print(markdown(out))


if __name__ == "__main__":
    main()
