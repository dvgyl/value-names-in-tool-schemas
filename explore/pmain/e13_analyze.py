"""E13 analysis (PROTOCOL.md). Usage: python3 -I e13_analyze.py

The E8 measure (`type = hotel` reads on dialogues that say "hotel" and whose gold sets no type) for `p_main` against
`p_main_renamed`, per model, with the dialogue-level sign test; beside the same models' `p4` and `p4_renamed` cells of
E7 and E11 (free text, thinking at effort low), and Sonnet's E12 cells (free text, `between_tools`).
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "forms"))
import common  # noqa: E402
import e8_measure  # noqa: E402
from common import anth  # noqa: E402


def rate(cell):
    n = sum(map(len, cell.values()))
    return round(sum(map(sum, cell.values())) / n, 4) if n else None


def missing():
    out = collections.Counter()
    for line in open(anth.EXPLORE / "e13" / "raw.jsonl"):
        r = json.loads(line)
        if r["type"] != "succeeded":
            out["error"] += 1
        elif r.get("stop") != "end_turn":
            out[str(r.get("stop"))] += 1
        else:
            try:
                common.parse(r["text"])
            except (ValueError, KeyError):
                out["parse_fail"] += 1
    return dict(out)


def main():
    data = anth.multiwoz()
    ids = common.dialogue_ids("e11", data)
    summary = {"experiment": "e13", "missing": missing(), "rules": {}}
    for label, traveller_only in (("traveller_turns", True), ("all_turns", False)):
        chosen = e8_measure.subset(data, ids, traveller_only)
        h = e8_measure.hits(("e13",), chosen)
        before = e8_measure.hits(("e7", "e11"), chosen)
        rows = {}
        for model in ("haiku", "sonnet"):
            more, less, p = e8_measure.sign_test(h[(model, "p_main")], h[(model, "p_main_renamed")])
            rows[model] = {"p_main": rate(h[(model, "p_main")]), "p_main_renamed": rate(h[(model, "p_main_renamed")]),
                           "sign_test": {"original_more": more, "renamed_more": less, "p_exact": p},
                           "free_text_thinking_low": {"p4": rate(before[(model, "p4")]),
                                                      "p4_renamed": rate(before[(model, "p4_renamed")])}}
        e12 = json.loads((anth.EXPLORE / "e12" / "summary.json").read_text())["natural"][label]["between_tools"]
        rows["sonnet"]["free_text_between_tools_e12"] = {"p4": e12["p4"], "p4_renamed": e12["p4_renamed"]}
        summary["rules"][label] = {"dialogues": len(chosen), "models": rows}
    (anth.EXPLORE / "e13" / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
