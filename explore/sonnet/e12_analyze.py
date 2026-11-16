"""E12 analysis (PROTOCOL.md). Usage: python3 -I e12_analyze.py [folder]   (default: explore/e12)

Natural part: the E8 measure (`type = hotel` reads on dialogues that say "hotel" and whose gold sets no type), for
`p4` against `p4_renamed` under `between_tools`, beside the same Sonnet cells of E7 (`p4`) and E11 (`p4_renamed`),
which ran with thinking at effort `low`. Track C part: commitment on the ambiguous items and retention on the clear
controls per condition and form, beside E4 Sonnet.
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "forms"))
sys.path.insert(0, str(HERE.parent / "trackc"))
import analyze as tc  # noqa: E402
import common  # noqa: E402
import e8_measure  # noqa: E402
import templates  # noqa: E402
from common import anth  # noqa: E402


def natural(folder, data):
    ids = common.dialogue_ids("e11", data)
    out = {}
    for label, traveller_only in (("traveller_turns", True), ("all_turns", False)):
        chosen = e8_measure.subset(data, ids, traveller_only)
        cur = collections.defaultdict(lambda: collections.defaultdict(list))
        for line in open(folder / "raw.jsonl"):
            r = json.loads(line)
            if not r["custom_id"].startswith("e12n-"):
                continue
            _, d, form, _ = r["custom_id"].split("-")
            d += ".json"
            if d not in chosen or r["type"] != "succeeded" or r.get("stop") != "end_turn":
                continue
            try:
                v = common.parse(r["text"])["type"]
            except (ValueError, KeyError):
                continue
            cur[form][d].append(isinstance(v, tuple) and "hotel" in v)
        before = e8_measure.hits(("e7", "e11"), chosen)

        def rate(cell):
            n = sum(map(len, cell.values()))
            return round(sum(map(sum, cell.values())) / n, 4) if n else None
        more, less, p = e8_measure.sign_test(cur["p4"], cur["p4_renamed"])
        out[label] = {"dialogues": len(chosen),
                      "between_tools": {"p4": rate(cur["p4"]), "p4_renamed": rate(cur["p4_renamed"]),
                                        "sign_test": {"original_more": more, "renamed_more": less, "p_exact": p}},
                      "thinking_low": {"p4": rate(before[("sonnet", "p4")]),
                                       "p4_renamed": rate(before[("sonnet", "p4_renamed")])}}
    return out


def trackc(folder):
    items = {item.id: item for item in templates.items()}
    cells = collections.defaultdict(lambda: collections.Counter())
    for line in open(folder / "raw.jsonl"):
        r = json.loads(line)
        if not r["custom_id"].startswith("e12c-"):
            continue
        body = r["custom_id"].removeprefix("e12c-")
        item_id, form = None, None
        for f in templates.FORMS:
            if f"-{f}-r" in body:
                item_id, form = body.split(f"-{f}-r")[0], f
        item = items[item_id]
        key = (item.condition, form)
        state, parsed = tc.status(r)
        if state != "ok":
            cells[key][state] += 1
            continue
        s = tc.score(item, parsed)
        if item.kind == "ambiguous":
            cells[key]["amb"] += 1
            cells[key]["commit"] += s["commit"]
        else:
            cells[key]["clr"] += 1
            cells[key]["retained"] += s["retained"]
    out = {}
    for (cond, form), c in sorted(cells.items()):
        out[f"{cond}|{form}"] = {"commit_rate": round(c["commit"] / c["amb"], 4) if c["amb"] else None,
                                 "retention": round(c["retained"] / c["clr"], 4) if c["clr"] else None,
                                 "missing": {k: v for k, v in c.items() if k not in ("amb", "clr", "commit", "retained")}}
    e4 = json.loads((anth.EXPLORE / "e4" / "summary.json").read_text())["cells"] if (anth.EXPLORE / "e4" / "summary.json").exists() else {}
    for key in out:
        cond, form = key.split("|")
        c = e4.get(cond, {}).get(form, {}).get("claude-sonnet-5-5")
        out[key]["e4_thinking_low"] = {"commit_rate": c["commitment"]["rate"], "retention": c["retention"]["rate"]} if c else None
    return out


def main(folder):
    data = anth.multiwoz()
    summary = {"experiment": "e12", "model": "claude-sonnet-5-5", "thinking": "between_tools", "effort": "high",
               "natural": natural(folder, data), "trackc": trackc(folder)}
    (folder / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else anth.EXPLORE / "e12")
