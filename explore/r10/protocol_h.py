"""Write the PROTOCOL.md section of experiment H and its lock (r10/protocol_h.lock.json). Offline.

The design and the predictions are copied verbatim from ROUND10-EXPERIMENT-PLAN.md; the changes that the operator
approved on 2026-11-12 (12 pairs, the excluded candidates, boat ferry -> punt) and the fixed texts come from pairs.py.
The section goes at the end of PROTOCOL.md, followed by its own amendments heading. Refuses to write twice.
Usage (from explore/): .venv/bin/python -I r10/protocol_h.py print | write
"""
import datetime
import inspect
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pairs  # noqa: E402
import protocol_section as ps  # noqa: E402
import runs  # noqa: E402

HSECTION = "## Round 10 experiment H runs"
HAMEND = "## Round 10 experiment H amendments"
HLOCK = HERE / "protocol_h.lock.json"


def section():
    plan = ps.PLAN.read_text()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    chosen = json.loads((HERE / "pairs.json").read_text())
    names = chosen.get("chosen") or chosen.get("pairs")
    parts = [
        HSECTION, "",
        f"Written {now}, before any experiment-H call. Exploratory. The operator approved the pair list and the value "
        "change on 2026-11-12 (\"Approve both\"). Code: `r10/pairs.py`, `r10/runs.py` (runs erh_sonnet, erh_haiku, "
        "erh_opus, erh_sol, erh_luna; reads 2, 2, 1, 2, 2), `r10/models.py` (settings as in the wave-1 section).", "",
        "### The design and the predictions (copied from the round-10 plan)", "",
        ps.block(plan, "### H. Sixteen word and schema pairs", ["### C. "]).replace("### ", "#### ", 1), "",
        "### Changes approved by the operator", "",
        f"- Pairs (12, in plan order): {', '.join(names)}. Calibration pair: hotel (guesthouse, hostel), reported apart.",
        "- A third rule excludes a candidate whose collision value is not the everyday word for all three values "
        "(two independent template reviews, 2026-11-12; `pairs.RULE_D_EXCLUDED`):",
    ]
    parts += [f"  - {k}: {v}" for k, v in pairs.RULE_D_EXCLUDED.items()]
    parts += [f"- Value change: {k}: {a} -> {b} ({why})" for k, (a, b, why) in pairs.VALUE_CHANGES.items()]
    parts += [
        "- The stop rule allows 12 to 15 pairs (action plan, gate G6). Prediction H1 keeps its words, with \"10 of the "
        "16 pairs\" read as \"62.5% of the pairs, rounded up\": 8 of the 12 pairs.",
        "- 1,920 requests per read for the 12 pairs, plus 160 for the calibration pair (cells g0, g4, cal_g0, cal_g4).",
        "- The annotator check of the round-10 plan (two annotator models on the unclear items) does not run in wave 1; "
        "if it runs later, it reads items only, and its result does not change the pair list.", "",
        "### Scoring rule (fixed before any call)", "",
        "- An answer is read with the last JSON object of its text. The `type` field is null, \"any\", or a list. A G4 "
        "answer value equal to the pair's neutral token (case ignored; spaces and underscores equal) counts as the "
        "collision value. The outcome is the share of reads whose `type` list holds the collision value.",
        "- \"writes the collision value alone\" (H4) means a `type` list with the collision value and no other value.",
        "- A read that does not parse is a missing read; the analysis reports the count per cell.", "",
        "### Fixed texts: the code of `r10/pairs.py`", "", "```", inspect.getsource(pairs).strip(), "```", "",
    ]
    return "\n".join(parts)


def section_hash(text):
    if HSECTION not in text:
        return None
    body = text.split(HSECTION, 1)[1]
    end = body.find("\n## ")
    return __import__("hashlib").sha256((HSECTION + (body if end < 0 else body[:end])).encode()).hexdigest()


def check():
    h = section_hash(runs.PROTOCOL.read_text())
    if h is None or not HLOCK.exists() or json.loads(HLOCK.read_text()).get("sha256") != h:
        sys.exit(f"Not run. The section {HSECTION!r} is missing or differs from {HLOCK.name}.")


def write():
    text = runs.PROTOCOL.read_text()
    if HSECTION in text or HLOCK.exists():
        sys.exit("Not written: the H section or its lock exists.")
    new = text.rstrip("\n") + "\n\n" + section() + "\n" + HAMEND + "\n\nNone yet.\n"
    runs.PROTOCOL.write_text(new)
    h = section_hash(new)
    HLOCK.write_text(json.dumps({"sha256": h, "section": HSECTION,
                                 "time": datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=1))
    runs.check_lock()  # the wave-1 lock must still hold
    print(f"H section written and locked: {h}")


if __name__ == "__main__":
    {"print": lambda: print(section()), "write": write}[sys.argv[1] if len(sys.argv) > 1 else "print"]()
