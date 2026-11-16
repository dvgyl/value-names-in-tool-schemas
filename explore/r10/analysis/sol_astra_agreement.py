"""How often two models gave the same answer on the 2,029 repair dialogues of experiment B. Post hoc; no model call; it
reads stored round-10 answers only.

Pairs and inputs (one read per dialogue, read 1; the same folders as b_analyze.SOURCES):
- Sol and Astra, original form f0: erb_sol (cell f0) and erg_astra (cell f0).
- Sonnet and Opus, original form f0: erb_sonnet (cell f0) and ere_opus (cell f0). This pair is the reference.
- Sol and Astra, the verifier ("Does the traveller exclude guesthouses?"): erb_sol (cell verify) and erx_b1_astra,
  erx_b2_astra, erx_b3_astra (cell verify).
Dialogues: the 2,029 dialogues of the groups S1t (994), S3 (490) and S2 (545) of runs.context().

Definitions:
- Same text: the two stored answer texts (`text` of the answer row) are equal, character for character. A dialogue
  counts when both rows exist.
- Same value: both answers parse (forms10.parse; the row succeeded and did not stop at the length limit) and give the
  same parsed value: the `type` field for f0 (null is a value), the `answer` field for the verifier. A dialogue where
  either answer does not parse counts as not the same.
Outputs: r10/analysis/out/sol_astra_agreement.json and sol_astra_agreement.md.
Usage (from explore/): .venv/bin/python -I r10/analysis/sol_astra_agreement.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
import forms10  # noqa: E402
import runs  # noqa: E402

OUT = HERE / "out"
GROUPS = {"S1t": "s1t", "S3": "s3", "S2": "s2"}
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
PAIRS = [  # (key, label, cell, field, folders of the first model, folders of the second model)
    ("sol_astra_f0", "Sol and Astra, original form", "f0", "type", ("erb_sol",), ("erg_astra",)),
    ("sonnet_opus_f0", "Sonnet and Opus, original form (reference)", "f0", "type", ("erb_sonnet",), ("ere_opus",)),
    ("sol_astra_verify", "Sol and Astra, verifier", "verify", "answer", ("erb_sol",),
     ("erx_b1_astra", "erx_b2_astra", "erx_b3_astra")),
]


def rows(folders, cell):
    """{dialogue file: answer row} of read 1 of one cell."""
    out = {}
    for folder in folders:
        for line in (EXPLORE / folder / "raw.jsonl").read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            _, did, c, read = r["custom_id"].split("-")
            if c == cell and read == "1":
                out[did + ".json"] = r
    return out


INVALID = object()  # an answer that does not parse; a parsed value can itself be None (null)


def value(row, cell, field):
    """The parsed value (None when the answer gives null), or INVALID when the answer does not parse."""
    if row.get("type") != "succeeded" or row.get("stop") in CUT:
        return INVALID
    try:
        return forms10.parse(cell, row.get("text", ""))[field]
    except (ValueError, KeyError, TypeError):
        return INVALID


def share(k, n):
    return {"k": k, "n": n, "share": k / n if n else None}


def compare(cell, field, first, second, ids):
    a, b = rows(first, cell), rows(second, cell)
    n = same_text = same_value = 0
    for d in ids:
        if d not in a or d not in b:
            continue
        n += 1
        same_text += a[d].get("text") == b[d].get("text")
        va, vb = value(a[d], cell, field), value(b[d], cell, field)
        same_value += va is not INVALID and vb is not INVALID and va == vb
    return {"same_text": share(same_text, n), "same_value": share(same_value, n)}


def pct(x):
    return "-" if x["share"] is None else f"{x['k']:,} of {x['n']:,} ({100 * x['share']:.1f}%)"


def main():
    _, g = runs.context()
    ids_by_group = {G: sorted(g[key]) for G, key in GROUPS.items()}
    every = [d for ids in ids_by_group.values() for d in ids]
    assert {G: len(v) for G, v in ids_by_group.items()} == {"S1t": 994, "S3": 490, "S2": 545}
    out = {"post_hoc": True, "no_model_call": True, "dialogues": len(every),
           "groups": {G: len(v) for G, v in ids_by_group.items()}, "pairs": {}}
    for key, label, cell, field, first, second in PAIRS:
        res = {"label": label, "cell": cell, "field": field, "first": list(first), "second": list(second),
               "all": compare(cell, field, first, second, every),
               "by_group": {G: compare(cell, field, first, second, ids) for G, ids in ids_by_group.items()}}
        out["pairs"][key] = res
    OUT.mkdir(exist_ok=True)
    (OUT / "sol_astra_agreement.json").write_text(json.dumps(out, indent=1) + "\n")
    L = ["## Same answers of two models on the repair dialogues (post hoc)", "",
         "No model call. Read 1 of each dialogue, on the 2,029 dialogues of experiment B (groups S1t 994, S3 490, "
         "S2 545). Same text: the two answer texts are equal, character for character. Same value: both answers "
         "parse and give the same `type` (original form; null is a value) or the same `answer` (verifier).", "",
         "| Pair | Same text | Same value |", "|---|---|---|"]
    for r in out["pairs"].values():
        L.append(f"| {r['label']} | {pct(r['all']['same_text'])} | {pct(r['all']['same_value'])} |")
    L += ["", "### By group", "", "| Pair | Group | Same text | Same value |", "|---|---|---|---|"]
    for r in out["pairs"].values():
        for G, x in r["by_group"].items():
            L.append(f"| {r['label']} | {G} | {pct(x['same_text'])} | {pct(x['same_value'])} |")
    L += ["", "Inputs: " + "; ".join(f"{r['label']}: {', '.join(r['first'])} against {', '.join(r['second'])}, "
                                     f"cell {r['cell']}" for r in out["pairs"].values()) + "."]
    (OUT / "sol_astra_agreement.md").write_text("\n".join(L) + "\n")
    print((OUT / "sol_astra_agreement.md").read_text())


if __name__ == "__main__":
    main()
