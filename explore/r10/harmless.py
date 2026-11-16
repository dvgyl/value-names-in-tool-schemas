"""Amendment R10-20 (PROTOCOL.md): release tests of harmless updates and of an unchanged tool, with the rename as a
known-change comparison. Exploratory, fixed in the protocol before the run. For the paper.

Three updates, each against the original as the control, all in one batch (or one synchronous run) per model:
- (a) the original again (an A/A test): cell trep (tool channel) or prep (form channel), byte-identical to the control
  request except the custom_id (and, on DeepInfra, the seed that comes from the custom_id);
- (b) a meaning-preserving paraphrase: cell tpar (the tool description TOOL_PARAPHRASE) or ppar (the two form sentences
  of FORM_PARAPHRASE);
- (c) the registered rename property_kind / large_property: cell t1 (tools.TOOLS["t1"]) or p1 (zforms.FORMS["f1"]).
Tool channel (Sol, Luna; OpenAI batch): control t0, the request of runs.build_a. Form channel (DeepSeek, Qwen, Gemma;
DeepInfra, synchronous; round 10 sends no tool request to DeepInfra): control p0, the p0 request of runs.build_a.
Prefixes: the 554 first requests of experiment A; answers per arm: control.READS (open 1, specific 10, guesthouse 1).
Usage (from explore/): .venv/bin/python -I r10/harmless.py check | show
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
import control  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

AMENDMENT = "### R10-20 "
TOOL_PARAPHRASE = ("Use the traveller's requirements to search the Cambridge hotel database. Give each argument as one "
                   "requirement, in the form that the instructions describe.")
FORM_PARAPHRASE = {  # old sentence of the F0 form text: new sentence
    tools.ASK_OLD: "Record the requirements of the traveller for the hotel in one JSON object.",
    tools.END_OLD: "Write nothing except the JSON object.",
}
NEW_TEXTS = (TOOL_PARAPHRASE, *FORM_PARAPHRASE.values())


def paraphrased_tool():
    """tools.SEARCH_T0 with the description TOOL_PARAPHRASE; nothing else changes."""
    t = copy.deepcopy(tools.SEARCH_T0)
    t["description"] = TOOL_PARAPHRASE
    return t


def paraphrased_form():
    """zforms.FORMS["f0"] with the two sentences of FORM_PARAPHRASE replaced; the schema does not change."""
    f0 = zforms.FORMS["f0"]
    text = f0.system
    for old, new in FORM_PARAPHRASE.items():
        text = zforms.once(text, old, new)
    return zforms.Form(text, f0.schema)


# cell: (system text, tools or None, form schema or None, the parse arm of the scored names and values)
TOOL_CELLS = {
    "t0": (tools.tool_system("t0"), tools.TOOLS["t0"], None, "t0"),
    "trep": (tools.tool_system("t0"), tools.TOOLS["t0"], None, "t0"),
    "tpar": (tools.tool_system("t0"), [paraphrased_tool()], None, "t0"),
    "t1": (tools.tool_system("t1"), tools.TOOLS["t1"], None, "t1"),
}
FORM_CELLS = {
    "p0": (zforms.FORMS["f0"].system, None, zforms.FORMS["f0"].schema, "f0"),
    "prep": (zforms.FORMS["f0"].system, None, zforms.FORMS["f0"].schema, "f0"),
    "ppar": (paraphrased_form().system, None, paraphrased_form().schema, "f0"),
    "p1": (zforms.FORMS["f1"].system, None, zforms.FORMS["f1"].schema, "f1"),
}
CHANNEL = {"sol": "tool", "luna": "tool", "deepseek": "form", "qwen": "form", "gemma": "form"}
CELLS_OF = {"tool": TOOL_CELLS, "form": FORM_CELLS}
CONTROL_CELL = {"tool": "t0", "form": "p0"}
UPDATES = {"a": {"tool": "trep", "form": "prep"}, "b": {"tool": "tpar", "form": "ppar"},
           "c": {"tool": "t1", "form": "p1"}}
RUNS = ("erk_sol", "erk_luna", "erk_deepseek", "erk_qwen", "erk_gemma")
PARSE_ARM = {c: v[3] for cells in CELLS_OF.values() for c, v in cells.items()}


def build(name, model, reads, data, g):
    """The four cells of the model's channel on the 554 prefixes, control.READS answers per arm and prefix. Per prefix
    and read, the four cells follow each other (control first). `reads` must be 1."""
    import models
    import runs
    assert reads == 1, reads
    cells = CELLS_OF[CHANNEL[model]]
    sets = control.set_of(data, g)
    out = []
    for d in g["booked"]:
        if sets[d] is None:
            continue
        user = zforms.prefix_text(data[d])
        for read in range(1, control.READS[sets[d]] + 1):
            for cell, (system, tl, schema, _) in cells.items():
                out.append(models.request(model, runs.cid(name, d, cell, read), user, system, schema, tools=tl,
                                          cell=cell))
    return out


def parse_row(row, cell):
    """("search", fields), ("none", text) or ("invalid", reason) of one answer row, with the F0 names and values.
    Tool cells: tools.parse_call with the cell's parse arm. Form cells: natural.parse with the cell's form (a form
    answer that parses is a "search")."""
    import natural
    arm = PARSE_ARM[cell]
    if cell in TOOL_CELLS:
        return tools.parse_call(row, arm)
    try:
        return ("search", natural.parse(row.get("text") or "", natural.FORMS[arm]))
    except (ValueError, KeyError, TypeError, IndexError) as x:
        return ("invalid", f"{type(x).__name__}: {x}")


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-20 is in PROTOCOL.md under the round-10 amendments and holds the paraphrase texts verbatim, the read counts and
    the run names."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    for words in (TOOL_PARAPHRASE, tools.SEARCH_DESCRIPTION, *FORM_PARAPHRASE, *FORM_PARAPHRASE.values(),
                  "10 answers per arm on the specific set, 1 per arm on the open set and on the guesthouse set",
                  "Status: exploratory, fixed in the protocol before the run.", *RUNS):
        if words not in flat:
            sys.exit(f"Not run. R10-20 does not hold {words!r}.")
    assert control.READS == {"open": 1, "specific": 10, "guesthouse": 1}, control.READS


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-20 holds the paraphrase texts, the read counts and the run names")
    elif cmd == "show":
        print("tool description, old:", tools.SEARCH_DESCRIPTION)
        print("tool description, new:", TOOL_PARAPHRASE)
        for old, new in FORM_PARAPHRASE.items():
            print("form sentence, old:", old)
            print("form sentence, new:", new)
    else:
        sys.exit(__doc__)
