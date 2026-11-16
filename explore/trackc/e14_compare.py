"""E14 comparison and prediction check (PROTOCOL.md). Run after `TRACKC_EXP=e14 python3 -I analyze.py`.

Usage: python3 -I e14_compare.py
Puts each E14 cell beside E4 Haiku (free text, thinking at effort low) and E12 Sonnet (free text, `between_tools`),
and checks the six predictions that PROTOCOL.md wrote before the run. Writes e14/compare.json.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from templates import anth  # noqa: E402

FORMS = ("p_main", "p_null", "p_unclear")
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5"}


def load(name):
    return json.loads((anth.EXPLORE / name / "summary.json").read_text())


def before(e4, e12, short, cond, form):
    """The free-text cell of the same model: E4 for Haiku, E12 for Sonnet."""
    if short == "haiku":
        c = e4["cells"][cond][form][MODELS["haiku"]]
        return {"source": "e4", "commit": c["commitment"]["rate"], "retention": c["retention"]["rate"]}
    c = e12["trackc"][f"{cond}|{form}"]
    return {"source": "e12", "commit": c["commit_rate"], "retention": c["retention"]}


def main():
    e14, e4, e12 = load("e14"), load("e4"), load("e12")
    rows, checks = [], {k: [] for k in ("d_zero", "b_both_lower", "c_high", "option_small", "unclear_on_clear", "retention")}
    for cond in ("a", "b", "c", "d"):
        for short, model in MODELS.items():
            cell = {f: e14["cells"][cond][f][model] for f in FORMS}
            commit = {f: cell[f]["commitment"]["rate"] for f in FORMS}
            keep = {f: cell[f]["retention"]["rate"] for f in FORMS}
            row = {"condition": cond, "model": short,
                   "commit": commit, "retention": keep,
                   "unclear_on_clear": cell["p_unclear"]["unclear_on_clear"]["target_rate"],
                   "missing": {f: cell[f]["requests"] - cell[f]["ok"] for f in FORMS},
                   "option_effect_pp": round(100 * (commit["p_null"] - commit["p_unclear"]), 1),
                   "instruction_effect_pp": round(100 * (commit["p_main"] - commit["p_null"]), 1),
                   "exchange": e14["exchange_rate"].get(cond, {}).get(model),
                   "free_text": {f: before(e4, e12, short, cond, f) for f in FORMS}}
            rows.append(row)
            if cond == "d":
                checks["d_zero"].append(all(commit[f] == 0 for f in FORMS))
            if cond == "b":
                checks["b_both_lower"].append(commit["p_null"] < commit["p_main"] and commit["p_unclear"] < commit["p_main"])
            if cond == "c":
                checks["c_high"].append(all(commit[f] >= 0.80 for f in FORMS))
            if cond != "d":
                checks["option_small"].append(abs(row["option_effect_pp"]) <= 5)
                checks["retention"].append(cond == "c" or all(keep[f] >= 0.95 for f in FORMS))
            checks["unclear_on_clear"].append(row["unclear_on_clear"] <= 0.02)
    verdict = {"d_zero": all(checks["d_zero"]), "b_both_lower": all(checks["b_both_lower"]),
               "c_high": all(checks["c_high"]),
               "option_small_in_most": sum(checks["option_small"]) > len(checks["option_small"]) / 2,
               "option_small_cells": f"{sum(checks['option_small'])} of {len(checks['option_small'])}",
               "unclear_on_clear": all(checks["unclear_on_clear"]), "retention": all(checks["retention"])}
    out = {"experiment": "e14", "requests": e14["requests"], "absent": e14["absent"], "rows": rows,
           "predictions": verdict}
    (anth.EXPLORE / "e14" / "compare.json").write_text(json.dumps(out, indent=1))
    pct = lambda x: "  -  " if x is None else f"{100 * x:5.1f}"  # noqa: E731
    print("cond model   commit main/null/unclear   (free text)           retention main/null/unclear   option  instr  unclear-on-clear")
    for r in rows:
        ft = r["free_text"]
        print(f"  {r['condition']}  {r['model']:6} " + " ".join(pct(r["commit"][f]) for f in FORMS)
              + "   (" + " ".join(pct(ft[f]["commit"]) for f in FORMS) + ")  "
              + " ".join(pct(r["retention"][f]) for f in FORMS)
              + f"   {r['option_effect_pp']:5.1f}  {r['instruction_effect_pp']:5.1f}  {pct(r['unclear_on_clear'])}")
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
