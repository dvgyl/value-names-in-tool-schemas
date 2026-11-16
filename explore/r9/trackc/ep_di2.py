"""P2 (ep_di2), the second DeepInfra token pilot, with the settings of r9/deepinfra_settings.py.

P2 reads the units of P (ep.units()): 20 natural, 20 Track C, and 20 on-site calls each for DeepSeek and Qwen, and 20
natural calls for the alternative option of each model (deepinfra_settings.ALTERNATIVES). Gemma keeps its P settings, so
P2 does not read it. A custom_id is the P custom_id with the prefix ep2, so the rows of P and P2 join by unit.
r9_counts.py does not count P2. The bound of `estimate` uses the full output cap of each call.
Usage: python3 -I r9/trackc/ep_di2.py estimate | run --approve <bound> | summary
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ep  # noqa: E402
import ep_summary  # noqa: E402
import panel  # noqa: E402
import tasks  # noqa: E402
from panel import accounts, ds, oc  # noqa: E402

NAME, ACCOUNT = "ep_di2", "deepinfra"
TASKS = {"dsv4": ("nat", "tc", "os"), "qwen": ("nat", "tc", "os"), "dsv4alt": ("nat",), "qwenalt": ("nat",)}
SETTINGS = {"dsv4": ds.DEEPSEEK, "qwen": ds.QWEN, "dsv4alt": ds.ALTERNATIVES[ds.DEEPSEEK.id],
            "qwenalt": ds.ALTERNATIVES[ds.QWEN.id]}
EXPECTED = (3 + 3 + 1 + 1) * ep.PER_TASK


def cells():
    """Every P2 request as (custom_id, task, model, prompt), the cell format of ep_summary.summarize."""
    by_task, ids = ep.units()
    panel.guard(ids)
    out = [(f"ep2-{task}-{tag}-{p.key}", task, panel.Model(tag, SETTINGS[tag].id, "deepinfra", {}), p)
           for tag, task_list in TASKS.items() for task in task_list for p in by_task[task]]
    assert len(out) == EXPECTED, len(out)
    return out


def build():
    tasks.check_trackc_items()
    return [ds.request(SETTINGS[m.short], cid, p.user, p.system, p.schema) for cid, _, m, p in cells()]


def main():
    a = accounts.account(ACCOUNT, ("deepinfra",))
    api = oc.APIS[a.provider]
    accounts.folder(NAME)
    ap = argparse.ArgumentParser(description=f"{NAME}: second DeepInfra token pilot on {a.name}")
    ap.add_argument("step", choices=["estimate", "run", "summary"])
    ap.add_argument("--approve", help="the bound that the operator approved in writing")
    args = ap.parse_args()
    if args.step == "summary":
        got = panel.rows(NAME)
        if not got:
            sys.exit(f"{NAME} has no raw.jsonl. Run the step run first.")
        out = ep_summary.summarize(a.provider, cells(), got)
        (panel.EXPLORE / NAME / "summary.json").write_text(json.dumps({"experiment": NAME, "cells": out}, indent=1))
        print(json.dumps(out, indent=1))
        return
    reqs = build()
    oc.check_requests(reqs, api)
    if args.step == "estimate":
        in_flight = oc.WORKERS * max(oc.worst(api, r) for r in reqs)  # the reserve that `run` adds, so both print one bound
        oc.print_estimate(NAME, reqs, ds.MAX_TOKENS, a, api, in_flight)
    else:
        oc.run(NAME, reqs, ds.MAX_TOKENS, args.approve, a, api)


if __name__ == "__main__":
    main()
