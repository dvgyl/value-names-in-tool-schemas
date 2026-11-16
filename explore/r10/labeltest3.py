"""Amendment R10-21 (PROTOCOL.md): the label test of R10-18 and R10-19 in the tool channel. Exploratory, fixed in the
protocol before the run.

The search tool search_hotels of the round-10 original t0 (tools.TOOLS["t0"], system text tools.tool_system("t0")),
with three arms that differ only in the value label of the `type` parameter. Each arm has the written definition of
R10-18 and R10-19 after its label, in the allowed-values line of the system text:
- tl_hotel:   "type: guesthouse, hotel (any venue type that is not a guesthouse)."
- tl_code:    "type: guesthouse, category_A (any venue type that is not a guesthouse)."
- tl_neutral: "type: guesthouse, serviced_property (any venue type that is not a guesthouse)."
The tool schema has the arm's label in place of hotel in the `type` enum. The tool name, the description, the other
parameters, the other system sentences, the user text (the prefix) and the model settings stay those of t0.

Prefixes: the 554 first requests of experiment A (open 448, specific 59, guesthouse 47; control.set_of).
Runs (r10/runs.py, experiment code "L3"): erl3_sol (3 answers per prefix and arm), erl3_luna (4 answers).
Usage (from explore/): .venv/bin/python -I r10/labeltest3.py check | texts
"""
import copy
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import labeltest2 as l2  # noqa: E402
import natural  # noqa: E402
import tools  # noqa: E402

AMENDMENT = "### R10-21 "
ARM_OF = {"tl_hotel": "l_hotel", "tl_code": "l_code", "tl_neutral": "l_neutral"}  # the labeltest2 arm of each cell
CELLS = tuple(ARM_OF)
LABELS = {c: l2.LABELS[a] for c, a in ARM_OF.items()}
TYPE_LINE = {c: l2.TYPE_LINE[a] for c, a in ARM_OF.items()}
READS = {"erl3_sol": 3, "erl3_luna": 4}  # answers per prefix and arm, on all 554 prefixes
RUNS = tuple(READS)
# Money of R10-21 and R10-22: the cap newmoney.CAPS_R21 holds the margin (newmoney.py is not in this repository;
# README.md, section 8).
RESERVE = 0.00  # the budget-gate reserve of R10-21 and R10-22
MAX_BOUND = 8.00  # USD per step


def system(cell):
    """tools.tool_system("t0") with the arm's type line (natural.system changes only the allowed-values lines)."""
    return natural.system(tools.tool_system("t0"), l2.NATURAL[ARM_OF[cell]])


def tool(cell):
    """tools.SEARCH_T0 with the arm's label in place of hotel in the `type` enum; nothing else changes."""
    t = copy.deepcopy(tools.SEARCH_T0)
    t["input_schema"] = natural.schema({"schema": t["input_schema"]}, l2.NATURAL[ARM_OF[cell]])["schema"]
    return t


def build(name, model, reads, data, g):
    """The three cells on the 554 prefixes, READS[name] answers per prefix and arm. Per prefix and read, the three cells
    follow each other in the order of CELLS, so all arms of one prefix are in the same batch. `reads` must be 1."""
    import control
    import models
    import runs
    import zforms
    assert reads == 1, reads
    sets = control.set_of(data, g)
    out = []
    for d in g["booked"]:
        if sets[d] is None:
            continue
        user = zforms.prefix_text(data[d])
        for read in range(1, READS[name] + 1):
            for cell in CELLS:
                out.append(models.request(model, runs.cid(name, d, cell, read), user, system(cell), None,
                                          tools=[tool(cell)], cell=cell))
    return out


def parse_call(row, cell):
    """As tools.parse_call, with labeltest2.parse for the arm: ("search", F0 fields), ("none", text) or ("invalid",
    reason). A `type` value outside the arm's two values is not valid."""
    if cell not in ARM_OF:
        raise RuntimeError(f"unknown cell {cell!r}")
    calls = row.get("tool_calls") or []
    if not calls:
        return ("none", row.get("text", ""))
    if len(calls) > 1:
        return ("invalid", f"{len(calls)} tool calls")
    c = calls[0]
    if c["name"] != "search_hotels" or not isinstance(c.get("input"), dict):
        return ("invalid", f"tool {c.get('name')!r} with input {type(c.get('input')).__name__}")
    try:
        return ("search", l2.parse(ARM_OF[cell], json.dumps(tools.clean_nulls(c["input"]))))
    except (ValueError, KeyError, TypeError, IndexError) as e:
        return ("invalid", f"{type(e).__name__}: {e}")


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-21 is in PROTOCOL.md under the round-10 amendments and holds the type lines, the read counts and the runs."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    for words in (*TYPE_LINE.values(), "554 first requests", "Sol 3 answers per prefix and arm",
                  "Luna 4 answers per prefix and arm", "Status: exploratory, fixed in the protocol before the run.",
                  *RUNS):
        if words not in flat:
            sys.exit(f"Not run. R10-21 does not hold {words!r}.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-21 holds the type lines, the read counts and the run names")
    elif cmd == "texts":
        for c in CELLS:
            print(c, TYPE_LINE[c], tool(c)["input_schema"]["properties"]["type"]["anyOf"][2]["items"]["enum"])
    else:
        sys.exit(__doc__)
