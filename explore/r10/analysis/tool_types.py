"""Tool calls at the first request: the type outputs per model and tool, and the hotel-only outcome on the 59 prefixes
whose brief sets hotel. Post hoc; no model call; it reads stored answers only.

It uses the reads of a_analyze.load (era1 and the fill runs; the definitions of a_analyze without change: a read is
valid when the row succeeded, did not stop at the output limit and tools.parse_call does not give "invalid").
- Type outputs: for each model, arm (t0 original tool, t1 renamed tool, mapped back) and brief group (brief sets hotel
  59, no type 448, guesthouse 47), the valid reads by the parsed `type`: hotel only, both types, guesthouse only, null
  (an empty list also parses to null), "any", other; and the valid reads without a search call (non-call).
- Hotel-only outcome on the 59: the share of valid reads whose type holds hotel and not guesthouse
  (gold.hides_guesthouse), per tool; the change t1 minus t0 as a_analyze.paired computes it (mean over paired prefixes,
  95% percentile cluster bootstrap, 2,000 draws, seed 20261112; exact sign test over prefixes, not adjusted).
Outputs: r10/analysis/out/tool_types.md and tool_types.json.
Usage (from explore/): .venv/bin/python -I r10/analysis/tool_types.py
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a_analyze as aa  # noqa: E402  (its imports set the paths; its main() does not run)

import gold  # noqa: E402

OUT = HERE / "out"
KINDS = ("hotel only", "both types", "guesthouse only", "null", "any", "other", "non-call")


def kind_of(kind, fields):
    if kind == "none":
        return "non-call"
    t = fields.get("type")
    if t is None:
        return "null"
    if t == "any":
        return "any"
    if isinstance(t, tuple):
        h, gh = "hotel" in t, "guesthouse" in t
        return "both types" if h and gh else "hotel only" if h else "guesthouse only" if gh else "other"
    return "other"


def main():
    data, g = aa.runs.context()
    ids = list(g["booked"])
    groups = {"brief hotel": [i for i in ids if gold.brief_type(data[i]) == "hotel"],
              "brief no type": [i for i in ids if gold.brief_type(data[i]) is None
                                and gold.brief_type(data[i], "fail_info") is None],
              "brief guesthouse": [i for i in ids if gold.brief_type(data[i]) == "guesthouse"]}
    assert {k: len(v) for k, v in groups.items()} == {"brief hotel": 59, "brief no type": 448, "brief guesthouse": 47}
    out = {"post_hoc": True, "no_model_call": True, "groups": {k: len(v) for k, v in groups.items()}, "models": {}}
    for m in aa.MODELS:
        reads, _ = aa.load(m)
        res = {"types": {}}
        for arm in ("t0", "t1"):
            for gname, gi in groups.items():
                c = collections.Counter(kind_of(k, f) for d in gi for _, k, f, _ in reads.get((d, arm), [])
                                        if k != "invalid")
                res["types"][f"{arm} {gname}"] = {k: c.get(k, 0) for k in KINDS}
        spec = groups["brief hotel"]
        res["hotel_only_rate"] = {arm: aa.rate(aa.cell_counts(reads, spec, arm, aa.hides)) for arm in ("t0", "t1")}
        res["hotel_only_change"] = aa.paired(reads, spec, "t0", "t1", aa.hides)
        out["models"][m] = res
    OUT.mkdir(exist_ok=True)
    (OUT / "tool_types.json").write_text(json.dumps(out, indent=1))
    L = ["## Tool calls at the first request: type outputs and the hotel-only outcome (post hoc)", "",
         "No model call. Valid reads of a_analyze.load. t0: original tool; t1: renamed tool (values mapped back).", "",
         "### Hotel-only outcome on the 59 prefixes whose brief sets hotel", "",
         "| Model | t0 | t1 | Change, points [95%] | Lower / higher | Sign p |", "|---|---|---|---|---|---|"]
    for m, r in out["models"].items():
        a, b, ch = r["hotel_only_rate"]["t0"], r["hotel_only_rate"]["t1"], r["hotel_only_change"]
        L.append(f"| {m} | {100 * a['share']:.1f}% ({a['k']}/{a['n']}) | {100 * b['share']:.1f}% ({b['k']}/{b['n']}) | "
                 f"{100 * ch['mean']:+.1f} [{100 * ch['ci'][0]:+.1f}, {100 * ch['ci'][1]:+.1f}] | "
                 f"{ch['lower']} / {ch['higher']} | {ch['sign_p']:.2g} |")
    L += ["", "### Type outputs (valid reads)", "", "| Model | Tool and group | " + " | ".join(KINDS) + " |",
          "|---|---|" + "---|" * len(KINDS)]
    for m, r in out["models"].items():
        for key, c in r["types"].items():
            L.append(f"| {m} | {key} | " + " | ".join(str(c[k]) for k in KINDS) + " |")
    (OUT / "tool_types.md").write_text("\n".join(L) + "\n")
    print((OUT / "tool_types.md").read_text())


if __name__ == "__main__":
    main()
