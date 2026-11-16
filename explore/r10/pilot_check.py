"""Gate G3 shape check of a round-10 pilot (review/plan15/ACTION-PLAN.md section 1.3). Offline; reads pilot_raw.jsonl.

Per cell: the count of rows, the rows that succeeded, the answers that parse, and for a tool cell the answers that hold
a tool call. Pass: in each cell, 9 or more of 10 answers parse; in each tool cell, 8 or more of 10 hold a tool call;
no row with an HTTP error. Cells plain and flag (R10-7): an answer parses when it is a valid search call or a text
answer. Runs erq<k>_<model> (R10-23, the rounds of the conversation pilot): an answer parses when it is a valid search
call of the cell's tool or a text answer; only round 1 needs the tool-call share. It prints counts, stop reasons and
sizes only.
Usage (from explore/): .venv/bin/python -I r10/pilot_check.py <run name> [...]
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EXPLORE / "r9" / "natural"))
import forms10  # noqa: E402
import natural  # noqa: E402
import tools  # noqa: E402

TOOL_CELLS = {"t0", "t1", "t0ask", "s2_empty", "s2_nonempty", "tedit", "th", "tg"}  # tedit R10-6; th, tg R10-14
REWRITE_CELLS = {f"{g}{i}" for g in "hgn" for i in (1, 2, 3)}  # R10-15: the rewrites h1 .. n3
CONTROL_CELLS = {"trep", "tord"}  # R10-16: the original tool again, and the tool with its fields in another order
CONTROL_CELLS |= {"tpar"}  # R10-20: the original tool with a paraphrased description (the names and values of t0)
CONTROL_CELLS |= {"tpar2"}  # R10-22: the second paraphrase of the description (the names and values of t0)
LABEL_TOOL_CELLS = {"tl_hotel", "tl_code", "tl_neutral"}  # R10-21: the label arms map back to the F0 value hotel
TOOL_CELLS |= LABEL_TOOL_CELLS
TOOL_CELLS |= REWRITE_CELLS | CONTROL_CELLS
STEP_CELLS = {"plain", "flag", "xplain", "xflag"}  # R10-7 and R10-13: a valid answer is a search call or a text answer
FORM_OF = {"p0": "f0", "f0": "f0", "f1": "f1", "orig_f0": "f0", "orig_f1": "f1", "ins_f0": "f0", "ins_f1": "f1"}
FORM_OF |= {"prep": "f0", "ppar": "f0", "p1": "f1"}  # R10-20, form channel: repeat, paraphrase, rename


def cell_of(cid):
    return cid.split("-")[2]


def parses(row, cell):
    text = row.get("text", "")
    try:
        if cell == "tedit":  # the edited tool maps back to the F0 names and values first
            import release
            return release.parse_call(row, "tedit")[0] in ("search", "ask")
        if cell in ("th", "tg"):  # the steered tools of R10-14 map back to the F0 names and values first
            import steer
            return steer.parse_call(row, cell)[0] == "search"
        if cell in REWRITE_CELLS:  # the rewrites of R10-15 map back to the F0 names and values first
            import steer2
            return steer2.parse_call(row, cell)[0] == "search"
        if cell in LABEL_TOOL_CELLS:  # R10-21: a valid search call whose type values are the arm's values
            import labeltest3
            return labeltest3.parse_call(row, cell)[0] == "search"
        if cell in CONTROL_CELLS:  # R10-16: the names and values of t0
            return tools.parse_call(row, "t0")[0] == "search"
        if cell in STEP_CELLS:
            import flag
            return flag.classify(row)[0] not in ("invalid", "neither")
        if cell in TOOL_CELLS:
            return tools.parse_call(row, "t0" if cell.startswith("s2") else cell)[0] in ("search", "ask")
        if cell in FORM_OF:
            natural.parse(text, natural.FORMS[FORM_OF[cell]])
            return True
        if cell in ("g0", "g4", "cal_g0", "cal_g4"):
            obj = json.loads(text[text.rfind("{"):text.rfind("}") + 1])
            return isinstance(obj, dict)
        if cell == "b_evidence":
            return isinstance(json.loads(text[text.find("{"):text.rfind("}") + 1]), dict)
        if cell in ("l_hotel", "l_code"):  # R10-18: the label maps back to the F0 value hotel
            import labeltest
            labeltest.parse(cell, text)
            return True
        if cell == "l_neutral":  # R10-19: the label serviced_property maps back to the F0 value hotel
            import labeltest2
            labeltest2.parse(cell, text)
            return True
        forms10.parse(cell, text)
        return True
    except (ValueError, KeyError, TypeError, IndexError, RuntimeError):
        return False


def check(name):
    path = EXPLORE / name / "pilot_raw.jsonl"
    if not path.exists():
        print(f"{name}: no pilot_raw.jsonl")
        return False
    rows = [json.loads(x) for x in path.read_text().splitlines()]
    conv_round = None
    if name.startswith("erq"):  # R10-23: a round of the conversation pilot
        import steer3
        conv_round = steer3.parse_run(name)[1]
        if not rows:
            print(f"{name}: no pilot call reached this round")
            return True
    by = collections.defaultdict(list)
    for r in rows:
        by[cell_of(r["custom_id"])].append(r)
    ok = True
    for cell, rs in sorted(by.items()):
        good = [r for r in rs if r.get("type", "succeeded") == "succeeded"]
        if conv_round is None:
            parsed = sum(parses(r, cell) for r in good)
            tool = sum(bool(r.get("tool_calls")) for r in good) if cell in TOOL_CELLS else None
        else:
            parsed = sum(steer3.pilot_parses(r, cell, conv_round) for r in good)
            tool = sum(bool(r.get("tool_calls")) for r in good) if conv_round == 1 else None
        errors = len(rs) - len(good)
        stops = collections.Counter(r.get("stop") for r in good)
        out = [r.get("output_tokens", 0) for r in good]
        need = max(1, round(0.9 * len(rs)))
        cell_ok = errors == 0 and parsed >= need and (tool is None or tool >= round(0.8 * len(rs)))
        ok &= cell_ok
        print(f"{name} {cell:12s} rows {len(rs):2d} errors {errors} parse {parsed:2d}"
              + (f" tool {tool:2d}" if tool is not None else "") + f" stops {dict(stops)} out mean "
              f"{sum(out) / max(len(out), 1):.0f} max {max(out, default=0)}  {'PASS' if cell_ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    results = [check(n) for n in sys.argv[1:]]
    sys.exit(0 if all(results) else 1)
