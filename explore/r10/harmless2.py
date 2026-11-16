"""Amendment R10-22 (PROTOCOL.md): two more release tests of harmless updates on the tool channel, with the rule of
R10-20. Exploratory, fixed in the protocol before the run. For the paper.

Cells, all in one batch per model, control first:
- t0: the original tool, a fresh control (the t0 request of runs.build_a, byte for byte in the body);
- tord: update (d), a field-order change. The tool of R10-16 (control.ordered_tool): the parameters of search_hotels
  and the required list in alphabetical order. Every name, value and text stays the same;
- tpar2: update (e), a second meaning-preserving paraphrase of the tool description (TOOL_PARAPHRASE2), written as a
  new text, not from the R10-20 paraphrase. Every value, field and instruction stays the same.
Models: Sol and Luna (openai_r9, batch). Prefixes: the 554 first requests of experiment A; answers per arm:
control.READS (open 1, specific 10, guesthouse 1).
Usage (from explore/): .venv/bin/python -I r10/harmless2.py check | show
"""
import copy
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import control  # noqa: E402
import tools  # noqa: E402

AMENDMENT = "### R10-22 "
TOOL_PARAPHRASE2 = ("Query the hotel database for Cambridge, using the requirements of the traveller. Every argument "
                    "holds a requirement, in the format that the instructions explain.")
NEW_TEXTS = (TOOL_PARAPHRASE2,)


def paraphrased_tool2():
    """tools.SEARCH_T0 with the description TOOL_PARAPHRASE2; nothing else changes."""
    t = copy.deepcopy(tools.SEARCH_T0)
    t["description"] = TOOL_PARAPHRASE2
    return t


TOOL_OF = {"t0": tools.TOOLS["t0"], "tord": [control.ordered_tool()], "tpar2": [paraphrased_tool2()]}
CONTROL = "t0"
UPDATES = {"d": "tord", "e": "tpar2"}
UPDATE_NAMES = {"d": "field order", "e": "second paraphrase"}
# The cells of each run (control first). A cut of the R10-22 cut order (update (d) on Sol) removes "tord" from
# PLAN["erk2_sol"], with a note in R10-22 before the submit.
PLAN = {"erk2_sol": ("t0", "tord", "tpar2"), "erk2_luna": ("t0", "tord", "tpar2")}
RUNS = tuple(PLAN)
MODEL_OF = {"erk2_sol": "sol", "erk2_luna": "luna"}


def build(name, model, reads, data, g):
    """The cells of PLAN[name] on the 554 prefixes, control.READS answers per arm and prefix. Per prefix and read, the
    cells follow each other, control first. `reads` must be 1."""
    import models
    import runs
    import zforms
    assert reads == 1, reads
    system = tools.tool_system("t0")
    sets = control.set_of(data, g)
    out = []
    for d in g["booked"]:
        if sets[d] is None:
            continue
        user = zforms.prefix_text(data[d])
        for read in range(1, control.READS[sets[d]] + 1):
            for cell in PLAN[name]:
                out.append(models.request(model, runs.cid(name, d, cell, read), user, system, None,
                                          tools=TOOL_OF[cell], cell=cell))
    return out


def parse_row(row, cell):
    """("search", F0 fields), ("none", text) or ("invalid", reason): tools.parse_call with the t0 names and values (every
    cell of R10-22 has them)."""
    if cell not in TOOL_OF:
        raise RuntimeError(f"unknown cell {cell!r}")
    return tools.parse_call(row, "t0")


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-22 is in PROTOCOL.md under the round-10 amendments and holds the paraphrase text, the field order, the read
    counts and the run names."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    order = "(" + ", ".join(control.ordered_tool()["input_schema"]["properties"]) + ")"
    for words in (TOOL_PARAPHRASE2, tools.SEARCH_DESCRIPTION, order,
                  "10 answers per arm on the specific set, 1 per arm on the open set and on the guesthouse set",
                  "Status: exploratory, fixed in the protocol before the run.", *RUNS):
        if words not in flat:
            sys.exit(f"Not run. R10-22 does not hold {words!r}.")
    assert control.READS == {"open": 1, "specific": 10, "guesthouse": 1}, control.READS


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-22 holds the paraphrase text, the field order, the read counts and the run names")
    elif cmd == "show":
        print("tool description, old:", tools.SEARCH_DESCRIPTION)
        print("tool description, new:", TOOL_PARAPHRASE2)
        print("field order, old:", list(tools.SEARCH_T0["input_schema"]["properties"]))
        print("field order, new:", list(control.ordered_tool()["input_schema"]["properties"]))
    else:
        sys.exit(__doc__)
