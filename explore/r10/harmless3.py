"""Amendment R10-24 (PROTOCOL.md): a replication of the two paraphrase flags of the release test, each with a fresh
control in the same batch or run. Exploratory, fixed in the protocol before the run. For the paper.

Comparisons (the requests of the flagged runs; only the custom_id differs, and on DeepInfra the seed that comes from it):
- (1) DeepSeek, update (b) of R10-20 in the form channel (erk_deepseek): cells p0 (the control, the F0 form) and ppar
  (the paraphrase of the two form sentences, harmless.FORM_PARAPHRASE). Run erk3_deepseek, deepinfra_main, synchronous.
- (2) Luna, update (e) of R10-22 in the tool channel (erk2_luna): cells t0 (the control, the original tool) and tpar2
  (the second paraphrase of the tool description, harmless2.TOOL_PARAPHRASE2). Run erk3_luna, openai_r9, batch.
Prefixes: the 554 first requests of experiment A; answers per arm: control.READS (open 1, specific 10, guesthouse 1).
Usage (from explore/): .venv/bin/python -I r10/harmless3.py check | show
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import control  # noqa: E402
import harmless  # noqa: E402
import harmless2  # noqa: E402
import tools  # noqa: E402

AMENDMENT = "### R10-24 "
MAX_BOUND = 1.00  # USD per step of R10-24
PLAN = {"erk3_deepseek": ("p0", "ppar"), "erk3_luna": ("t0", "tpar2")}
RUNS = tuple(PLAN)
MODEL_OF = {"erk3_deepseek": "deepseek", "erk3_luna": "luna"}
ORIGINAL = {"erk3_deepseek": "erk_deepseek", "erk3_luna": "erk2_luna"}  # the run whose flag is replicated
UPDATE_OF = {"erk3_deepseek": ("b", "ppar"), "erk3_luna": ("e", "tpar2")}
CONTROL_OF = {"erk3_deepseek": "p0", "erk3_luna": "t0"}
# The release level of the flagged decision: R10-20 form channel 1 - 0.05/6; R10-22 tool channel 1 - 0.05/4.
LEVEL = {"erk3_deepseek": 1 - 0.05 / 6, "erk3_luna": 1 - 0.05 / 4}
NEW_TEXTS = harmless.NEW_TEXTS + harmless2.NEW_TEXTS


def cell_spec(cell):
    """(system text, tools or None, form schema or None) of a cell."""
    if cell in harmless.FORM_CELLS:
        system, tl, schema, _ = harmless.FORM_CELLS[cell]
        return system, tl, schema
    return tools.tool_system("t0"), harmless2.TOOL_OF[cell], None


def build(name, model, reads, data, g):
    """The two cells of PLAN[name] on the 554 prefixes, control.READS answers per arm and prefix. Per prefix and read,
    the control comes first. `reads` must be 1."""
    import models
    import runs
    import zforms
    assert reads == 1 and MODEL_OF[name] == model, (name, model, reads)
    sets = control.set_of(data, g)
    out = []
    for d in g["booked"]:
        if sets[d] is None:
            continue
        user = zforms.prefix_text(data[d])
        for read in range(1, control.READS[sets[d]] + 1):
            for cell in PLAN[name]:
                system, tl, schema = cell_spec(cell)
                out.append(models.request(model, runs.cid(name, d, cell, read), user, system, schema, tools=tl,
                                          cell=cell))
    return out


def parse_row(row, cell):
    """("search", F0 fields), ("none", text) or ("invalid", reason): harmless.parse_row for the form cells,
    harmless2.parse_row for the tool cells."""
    return harmless.parse_row(row, cell) if cell in harmless.FORM_CELLS else harmless2.parse_row(row, cell)


def pending_bounds(account):
    """The estimated bounds of the R10-24 runs of `account` with no batch.json and no ledger row of a run step: the
    client estimate with the pilot sizes (or the planning sizes before the pilot), with the margin. Offline."""
    import accounts
    import anth
    import openai_compat as oc
    import runs
    total = 0.0
    for name in RUNS:
        run = runs.RUNS[name]
        if run.account != account or (EXPLORE / name / "batch.json").exists():
            continue
        a = accounts.ACCOUNTS[account]
        if accounts.has_row(a, name, "run"):
            continue
        reqs = runs.requests(name)
        if a.provider == "anthropic":
            total += round(anth.estimate(name, reqs, runs.PLANNING_OUT[a.provider])[0] * anth.MARGIN, 2)
        else:
            api = oc.APIS[a.provider]
            total += oc.cents_up(oc.estimate(name, reqs, runs.PLANNING_OUT[a.provider], api)[0] * anth.MARGIN
                                 * accounts.factor(a))
    return total


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-24 is in PROTOCOL.md under the round-10 amendments and holds the paraphrase texts, the read counts, the
    levels and the run names."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    for words in (*harmless.FORM_PARAPHRASE, *harmless.FORM_PARAPHRASE.values(), harmless2.TOOL_PARAPHRASE2,
                  tools.SEARCH_DESCRIPTION, "10 answers per arm on the specific set, 1 per arm on the open set and on "
                  "the guesthouse set", "Status: exploratory, fixed in the protocol before the run.", "99.17%",
                  "98.75%", *RUNS, *ORIGINAL.values()):
        if words not in flat:
            sys.exit(f"Not run. R10-24 does not hold {words!r}.")
    assert control.READS == {"open": 1, "specific": 10, "guesthouse": 1}, control.READS


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-24 holds the paraphrase texts, the read counts, the levels and the run names")
    elif cmd == "show":
        for name, cells in PLAN.items():
            print(name, MODEL_OF[name], cells, "replicates", ORIGINAL[name], "level", f"{100 * LEVEL[name]:.2f}%")
        print(json.dumps({"form": harmless.FORM_PARAPHRASE, "tool": harmless2.TOOL_PARAPHRASE2}, indent=1))
    else:
        sys.exit(__doc__)
