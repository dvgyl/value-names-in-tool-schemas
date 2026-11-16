"""Second step of the tool calls: the number of distinct first requests behind the trials. Post hoc, no model call.

It joins each stored second-step answer (era2_<model>) to its first tool call (era1_<model>, arm t0) exactly as
a_analyze.step2 does, and counts trials and distinct first requests (dialogues) by result (empty or not empty). It also
gives the exact 95% upper bound (Clopper-Pearson, two-sided) of Haiku's new-search rate after a non-empty result, with
the distinct first requests as the units (0 events). Outputs: r10/analysis/out/step2_links.json and step2_links.md.
Usage (from explore/): .venv/bin/python -I r10/analysis/step2_links.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a_analyze as aa  # noqa: E402  (it sets the import path)

import briefsearch as bs  # noqa: E402
import gold  # noqa: E402

OUT = HERE / "out"
MODELS = ("sonnet", "haiku", "opus", "sol", "astra", "luna")


def main():
    db = gold.hotel_db()
    res = {"post_hoc": True, "models": {}}
    for m in MODELS:
        reads, _ = aa.load(m)
        rr = aa.rows(f"era2_{m}")
        first = {(d, read): f for (d, arm), lst in reads.items() if arm == "t0"
                 for read, k, f, folder in lst if folder == f"era1_{m}" and k == "search"}
        out = {"empty": {"trials": 0, "dialogues": set()}, "nonempty": {"trials": 0, "dialogues": set()}, "unmatched": 0}
        for r in rr:
            d, _, read = aa.split(r["custom_id"])
            f1 = first.get((d, read))
            if f1 is None:
                out["unmatched"] += 1
                continue
            part = "empty" if not bs.search(db, f1) else "nonempty"
            out[part]["trials"] += 1
            out[part]["dialogues"].add(d)
        res["models"][m] = {p: {"trials": v["trials"], "first_requests": len(v["dialogues"])} if isinstance(v, dict) else v
                            for p, v in out.items()}
    n = res["models"]["haiku"]["nonempty"]["first_requests"]
    res["haiku_nonempty_upper_95"] = 1 - 0.025 ** (1 / n)  # Clopper-Pearson upper limit for 0 of n
    OUT.mkdir(exist_ok=True)
    (OUT / "step2_links.json").write_text(json.dumps(res, indent=1))
    L = ["## Second step: trials and distinct first requests (post hoc)", "",
         "| Model | Result | Trials | Distinct first requests |", "|---|---|---|---|"]
    for m, o in res["models"].items():
        for p in ("nonempty", "empty"):
            L.append(f"| {m} | {p} | {o[p]['trials']} | {o[p]['first_requests']} |")
    L += ["", f"Unmatched rows: {', '.join(f'{m} {o['unmatched']}' for m, o in res['models'].items())}.",
          f"Haiku, new search after a non-empty result: 0 events; exact 95% upper bound (Clopper-Pearson) with {n} first requests "
          f"as units: {100 * res['haiku_nonempty_upper_95']:.1f}%."]
    (OUT / "step2_links.md").write_text("\n".join(L) + "\n")
    print((OUT / "step2_links.md").read_text())


if __name__ == "__main__":
    main()
