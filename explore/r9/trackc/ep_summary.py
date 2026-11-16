"""Summarize P: per model and task, the tokens, valid JSON, cut-off answers, and the cost of one call. Offline.

It also prints the Sol cut rule of ROUND9-EXPERIMENT-PLAN.md section 3: if one `gpt-6.1-sol` natural call at the
panel effort costs more than 0.0070 USD at batch list prices (the price of the X2 Sol batches, as in r9_costs.py), Sol
keeps only the core parts of X2 and leaves X3. Writes ep_oa/summary.json and ep_di/summary.json.
Usage: python3 -I r9/trackc/ep_summary.py
"""
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ep  # noqa: E402
import panel  # noqa: E402
import tasks  # noqa: E402
from panel import oc  # noqa: E402

CUT_USD = 0.0070
TC = tasks.load(panel.EXPLORE / "trackc" / "analyze.py", "trackc_analyze")
ANNOT = tasks.load(panel.EXPLORE / "annot" / "analyze.py", "annot_analyze")
def json_object(text):
    obj = ANNOT.last_object(text)
    if not isinstance(obj, dict):
        raise ValueError("no JSON object")
    return obj


def annotation(text):
    if not isinstance(json_object(text).get("fields"), dict):
        raise ValueError("no fields object")


VALID = {"nat": tasks.common.parse, "tc": TC.parse, "os": json_object, "an": annotation}  # the parser of each analysis


def valid(task, text):
    try:
        VALID[task](text or "")
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def mean(xs):
    return statistics.fmean(xs) if xs else None


def summarize(provider, cells, got):
    """`cells`: the P cells of one provider; `got`: its raw.jsonl rows by custom_id."""
    api = oc.APIS[provider]
    groups = {}
    for cid, task, model, p in cells:
        groups.setdefault((model.short, task), []).append((cid, model, panel.request(model, cid, p)))
    out = {}
    for (short, task), members in groups.items():
        rs = [(got[cid], req) for cid, _, req in members if cid in got]
        ok = [(r, req) for r, req in rs if r["type"] == "succeeded"]
        model = members[0][1].id
        cost = lambda batch: mean([oc.cost(api, model, r["input_tokens"], r["output_tokens"], batch) for r, _ in ok])  # noqa: E731
        out[f"{short}|{task}"] = {
            "model": model, "requests": len(members), "rows": len(rs), "answers": len(ok),
            "errors": len(rs) - len(ok), "refusals": sum(r["stop"] == "refusal" for r, _ in ok),
            "cut_off": sum(r["stop"] == "max_tokens" for r, _ in ok),
            "valid_json": sum(valid(task, r.get("text")) for r, _ in ok),
            "input_mean": mean([r["input_tokens"] for r, _ in ok]),
            "in_ratio": sum(r["input_tokens"] for r, _ in ok) / sum(oc.est_in(q) for _, q in ok) if ok else None,
            "output_mean": mean([r["output_tokens"] for r, _ in ok]),
            "reasoning_mean": mean([r.get("reasoning_tokens", 0) for r, _ in ok]),
            "output_max": max((r["output_tokens"] for r, _ in ok), default=None),
            "usd_per_call_standard": cost(False), "usd_per_call_batch": cost(True) if api.batch else None,
        }
    return out


def cut_rule(openai_cells):
    sol = openai_cells.get("sol|nat") or {}
    usd = sol.get("usd_per_call_batch")
    return {"usd_per_call_batch": usd, "limit": CUT_USD, "cut": None if usd is None else usd > CUT_USD}


def main():
    result = {}
    for provider, name in ep.FOLDERS.items():
        got = panel.rows(name)
        result[provider] = summarize(provider, ep.cells(provider), got)
        summary = {"experiment": name, "cells": result[provider]}
        if provider == "openai":
            summary["cut_rule"] = cut_rule(result[provider])
        if got:
            (panel.EXPLORE / name / "summary.json").write_text(json.dumps(summary, indent=1))
    f = lambda x, d=0: "-" if x is None else f"{x:.{d}f}"  # noqa: E731
    print("model|task       answers/requests  errors  cut-off  valid JSON  input  output  reasoning  "
          "USD per call (standard / batch)")
    for provider in ep.FOLDERS:
        for key, c in result[provider].items():
            print(f"  {key:15} {c['answers']:3}/{c['requests']:<3}  {c['errors']:6}  {c['cut_off']:7}  "
                  f"{c['valid_json']:10}  {f(c['input_mean']):>5}  {f(c['output_mean']):>6}  "
                  f"{f(c['reasoning_mean']):>9}  {f(c['usd_per_call_standard'], 6)} / {f(c['usd_per_call_batch'], 6)}")
    rule = cut_rule(result["openai"])
    verdict = {None: "not known (no Sol natural answer yet)", True: "YES: Sol keeps only the core parts of X2 and leaves X3",
               False: "NO: Sol keeps every planned part"}[rule["cut"]]
    print(f"Cut rule: one gpt-6.1-sol natural call at effort low costs {f(rule['usd_per_call_batch'], 6)} USD at batch "
          f"list prices. More than {CUT_USD:.4f} USD: {verdict}")
    sol = [result["openai"].get(f"sol|{t}", {}).get("reasoning_mean") for t in ("nat", "tc", "os")]
    astra = result["openai"].get("astra|an", {})
    print(f"Q6: gpt-6.1-sol reasoning tokens per task (natural, Track C, on-site) {[f(x) for x in sol]}, prediction 1,000 "
          f"or fewer; gpt-6-astra input {f(astra.get('input_mean'))} (prediction under 8,000) and output "
          f"{f(astra.get('output_mean'))} (prediction under 4,000)")


if __name__ == "__main__":
    main()
