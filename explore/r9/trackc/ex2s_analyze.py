"""Score X2 on-site with the E2 scorer (onsite/analyze.py) and check prediction Q5 of PREDICTIONS.md. Offline.

The scorer runs unchanged. Only its model table changes: the X2 custom_id has the E2 format with the model tags of
panel.py. Writes summary.json into ex2s_sol, ex2s_luna, and ex2s_di.
Run with the repository venv:  harness/.venv/bin/python r9/trackc/ex2s_analyze.py
"""
import contextlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import panel  # noqa: E402
import tasks  # noqa: E402
import x2s  # noqa: E402

OA = tasks.load(panel.EXPLORE / "onsite" / "analyze.py", "onsite_analyze")
RUNS = {"ex2s_sol": "openai", "ex2s_luna": "openai", "ex2s_di": "deepinfra"}


@contextlib.contextmanager
def models(provider):
    """The E2 scorer reads the model of a custom_id from e2.MODELS; the X2 tags replace the Claude tags while it runs."""
    saved = OA.e2.MODELS
    OA.e2.MODELS = {s: panel.MODELS[s].id for s in x2s.PROVIDER_MODELS[provider]}
    try:
        yield
    finally:
        OA.e2.MODELS = saved


def summarize(rows, provider, cases, map_back):
    with models(provider):
        return OA.summarize(rows, cases, map_back)


def wrong_rate(pooled):
    """Wrong replies over scored replies. The scorer scores a parse failure as not wrong (P1, P3)."""
    scored = pooled["right"] + pooled["wrong"] + pooled["parse_fail"]
    return pooled["wrong"] / scored if scored else None


def q5(summaries):
    """Q5: the renamed arm gives fewer wrong extractions than the original arm for 3 or more of the 5 models."""
    per_model = {}
    for s in summaries:  # a split run (ex2s_sol, ex2s_luna) also lists its other model, with no rows
        for m, arms in s["models"].items():
            rates = {arm: wrong_rate(c["pooled"]) for arm, c in arms.items()}
            if m not in per_model or any(r is not None for r in rates.values()):
                per_model[m] = rates
    lower = {m: None if r["orig"] is None or r["renamed"] is None else r["renamed"] < r["orig"] for m, r in per_model.items()}
    known = [v for v in lower.values() if v is not None]
    return {"wrong_rate": per_model, "renamed_lower": lower,
            "q5_holds": sum(known) >= 3 if len(known) == len(lower) else None}


def main():
    cases, map_back, summaries = tasks.e2.onsite_cases(), tasks.e2.load_p3().map_back, []
    for name, provider in RUNS.items():
        got = list(panel.rows(name).values())
        summary = summarize(got, provider, cases, map_back)
        summary["experiment"] = name
        summaries.append(summary)
        if got:
            (panel.EXPLORE / name / "summary.json").write_text(json.dumps(summary, indent=1))
        print(f"{name}: {summary['rows']} of {summary['expected_rows']} rows")
    print(json.dumps(q5(summaries), indent=1))


if __name__ == "__main__":
    main()
