"""Representative request and answer pairs of round 10: for each listed run, the first request of each cell, as the
request builder makes it, with the stored answer row of the same custom_id. Written for the supplementary packages and this repository;
it makes no model call.

The request is the body that the run sent to the provider (Anthropic Messages or OpenAI Responses, in batch form).
The user text holds a dialogue of the public corpus MultiWOZ 2.4 (MIT License).
Outputs: ../examples/<run>.json. Usage (from explore/): .venv/bin/python -I export_examples.py [run ...]
"""
import json
import pathlib
import sys

EXPLORE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXPLORE / "r10"))
import runs  # noqa: E402

OUT = EXPLORE.parent / "examples"
RUNS = tuple(sys.argv[1:]) or ("era1_sonnet", "era1_sol", "erb_haiku", "erb_sol", "eri_sonnet", "erh_sonnet")


def cell_of(cid):
    parts = cid.split("-")
    return parts[2]


def main():
    OUT.mkdir(exist_ok=True)
    for name in RUNS:
        if not (EXPLORE / name / "raw.jsonl").exists():
            continue
        answers = {}
        for line in (EXPLORE / name / "raw.jsonl").read_text().splitlines():
            r = json.loads(line)
            answers[r["custom_id"]] = r
        chosen = {}
        try:
            reqs = runs.requests(name)
        except (KeyError, FileNotFoundError, SystemExit) as e:  # a run that needs the full stored answers
            print(name, "not exported:", type(e).__name__)
            continue
        for req in reqs:
            cid = req["custom_id"]
            cell = cell_of(cid)
            if cell not in chosen and cid in answers:
                chosen[cell] = {"custom_id": cid, "request": req, "answer": answers[cid]}
        out = {"run": name, "experiment": runs.RUNS[name].exp, "model": runs.RUNS[name].model,
               "cells": list(chosen), "pairs": list(chosen.values())}
        (OUT / f"{name}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
        print(name, len(chosen), "cells")


if __name__ == "__main__":
    main()
