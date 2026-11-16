"""Amendment R10-14, post hoc (the paper, round 8): the text that the agents wrote next to a hotel value of
the guesthouse-steered tool (cell tg). Reads stored outputs only; makes no model call.

For each agent: the prefixes of the open set (brief sets no type) whose tg read holds the hotel value and whose t0 read
does not (the switchers of the paired change). For each, the text that the agent wrote before its call (empty for many
reads) and the last traveller turn of the prefix. A word check (no person checked it) counts the texts that give the
traveller's word as the reason: the text holds "hotel" and one of "said", "asked", "asks", "wants", "requested",
"explicitly", "stated".
Inputs: ers_sonnet/raw.jsonl, ers_haiku/raw.jsonl (tg), erp_sonnet/raw.jsonl and ers_haiku/raw.jsonl (t0), MultiWOZ 2.4.
Output: r10/analysis/out/steer_quote.md and steer_quote.json.
Usage (from explore/): .venv/bin/python -I r10/analysis/steer_quote.py
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import release_analyze as ra  # noqa: E402
import runs  # noqa: E402
import steer_analyze as sa  # noqa: E402
import zforms  # noqa: E402

OUT = HERE / "out"
REASON = re.compile(r"\b(said|asked|asks|wants|requested|explicitly|stated)\b", re.I)


def rows(folder, cell):
    out = {}
    for line in (EXPLORE / folder / "raw.jsonl").read_text().splitlines():
        r = json.loads(line)
        _, d, c, _ = r["custom_id"].split("-")
        if c == cell:
            out[d + ".json"] = r
    return out


def hotel(row, cell):
    kind, val = sa.read_of(row, cell)
    return kind == "search" and sa.VALUES["hotel"](val.get("type") if isinstance(val, dict) else None)


def last_traveller(text):
    lines = [x for x in text.splitlines() if x.startswith("Traveller: ")]
    return lines[-1][len("Traveller: "):] if lines else ""


def main():
    data, g = runs.context()
    sets = ra.request_sets(data, g)
    res = {"note": "post hoc; word check not checked by a person", "agents": {}}
    md = ["## Text next to the hotel value of the guesthouse-steered tool (R10-14, post hoc)", "",
          "Open set (brief sets no type). Switchers: tg read holds hotel, t0 read does not. "
          "Reason check: the text holds 'hotel' and a word of " + REASON.pattern + ". No person checked it.", ""]
    for agent in ("sonnet", "haiku"):
        t0 = rows(sa.SOURCES[agent]["t0"], "t0")
        tg = rows(sa.SOURCES[agent]["tg"], "tg")
        sw = []
        for d in sets["open"]:
            if d in t0 and d in tg and hotel(tg[d], "tg") and not hotel(t0[d], "t0"):
                text = (tg[d].get("text") or "").strip()
                sw.append({"dialogue": d, "text": text, "reason_word": bool(text and "hotel" in text.lower()
                                                                             and REASON.search(text)),
                           "traveller": last_traveller(zforms.prefix_text(data[d]))})
        with_text = [s for s in sw if s["text"]]
        n_reason = sum(s["reason_word"] for s in sw)
        res["agents"][agent] = {"switchers": len(sw), "with_text": len(with_text), "reason_word": n_reason,
                                "rows": sw}
        md += [f"### {agent}", "", f"Switchers {len(sw)}; with text {len(with_text)}; reason check {n_reason}.", ""]
        for s in with_text:
            md.append(f"- {s['dialogue']} | agent: {s['text'][:300]} | traveller: {s['traveller'][:200]}")
        md.append("")
    OUT.mkdir(exist_ok=True)
    (OUT / "steer_quote.json").write_text(json.dumps(res, indent=1))
    (OUT / "steer_quote.md").write_text("\n".join(md))
    print("\n".join(md[:6]))
    for agent, v in res["agents"].items():
        print(agent, v["switchers"], v["with_text"], v["reason_word"])


if __name__ == "__main__":
    main()
