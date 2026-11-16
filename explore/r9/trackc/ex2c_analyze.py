"""Score X2 Track C with the E4 scorer (trackc/analyze.py) and check the predictions of PREDICTIONS.md. Offline.

The scorer runs unchanged on the cells of each run, with `p_option` added to the forms that it compares with `p_main`.
The Claude run holds only `p_option`, so its cells and rows join the E14 cells and rows of the same models and settings.
Writes summary.json into ex2c_sol, ex2c_luna, ex2c_di, and ex2c_an.
Usage: python3 -I r9/trackc/ex2c_analyze.py
"""
import json
import pathlib
import sys
import types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import panel  # noqa: E402
import tasks  # noqa: E402
import x2c  # noqa: E402

TC = tasks.load(panel.EXPLORE / "trackc" / "analyze.py", "trackc_analyze")
TC.OTHERS = ("p_unclear", "p_null", "p_option")
RUNS = {"ex2c_sol": "openai", "ex2c_luna": "openai", "ex2c_di": "deepinfra", "ex2c_an": "anthropic"}
CLAUDE = {model for model, _, _ in tasks.e14.SETTINGS.values()}
SONNET = tasks.e14.SETTINGS["sonnet"][0]


def run_cells(provider):
    return x2c.cells(provider) + (tasks.e14.cells() if provider == "anthropic" else [])


def summarize(rows, cells):
    """The E4 scorer on any set of cells in the format (custom_id, item, form, read, model)."""
    TC.EXP = types.SimpleNamespace(__name__="x2c", cells=lambda: cells)
    return TC.summarize(rows)


def effects(summary):
    """Per condition and model: commitment and retention per form, and three contrasts in percentage points."""
    out = []
    for cond, forms in summary["cells"].items():
        for model in sorted({m for f in forms.values() for m in f}):
            cell = {f: forms.get(f, {}).get(model) for f in x2c.FORMS}
            commit = {f: c and c["commitment"]["rate"] for f, c in cell.items()}
            pp = lambda a, b: None if commit[a] is None or commit[b] is None else round(100 * (commit[a] - commit[b]), 1)  # noqa: E731
            out.append({"condition": cond, "model": model, "commit": commit,
                        "retention": {f: c and c["retention"]["rate"] for f, c in cell.items()},
                        "option_effect_pp": pp("p_null", "p_unclear"),  # the E14 contrast: option against null
                        "schema_option_pp": pp("p_main", "p_option"),  # "unclear" in the schema only
                        "sentence_pp": pp("p_option", "p_unclear")})  # the ambiguity sentence added to the option
    return out


def verdict(rows):
    """Q3 on the five non-Claude models and Q4 on Sonnet. None when the cells have no valid reads yet."""
    new = [r for r in rows if r["model"] not in CLAUDE]
    amb = [r["option_effect_pp"] for r in new if r["condition"] != "d" and r["option_effect_pp"] is not None]
    d = [v for r in new if r["condition"] == "d" for v in r["commit"].values() if v is not None]
    b = next((r["commit"] for r in rows if r["model"] == SONNET and r["condition"] == "b"), {})
    q4 = None if b.get("p_option") is None or b.get("p_unclear") is None else b["p_option"] >= b["p_unclear"]
    return {"q3_option_small_cells": f"{sum(abs(x) <= 5 for x in amb)} of {len(amb)}",
            "q3_option_small_in_most": sum(abs(x) <= 5 for x in amb) > len(amb) / 2 if amb else None,
            "q3_d_zero": all(v == 0 for v in d) if d else None,
            "q4_sonnet_b_option_at_least_unclear": q4}


def main():
    rows = []
    for name, provider in RUNS.items():
        got = list(panel.rows(name).values()) + (list(panel.rows("e14").values()) if provider == "anthropic" else [])
        summary = summarize(got, run_cells(provider))
        summary["effects"] = effects(summary)
        rows += summary["effects"]
        if panel.rows(name):
            (panel.EXPLORE / name / "summary.json").write_text(json.dumps(summary, indent=1))
        print(f"{name}: {summary['rows']} rows, {summary['absent']} of {summary['requests']} requests absent")
    pct = lambda x: "  -  " if x is None else f"{100 * x:5.1f}"  # noqa: E731
    print("cond model                              commit main/null/unclear/option   option  schema  sentence (pp)")
    for r in rows:
        print(f"  {r['condition']}  {r['model']:33} " + " ".join(pct(r["commit"][f]) for f in x2c.FORMS)
              + f"   {r['option_effect_pp']}  {r['schema_option_pp']}  {r['sentence_pp']}")
    print(json.dumps(verdict(rows), indent=1))


if __name__ == "__main__":
    main()
