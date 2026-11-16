"""Amendment R10-16 (PROTOCOL.md): two control updates that are harmless by construction, under the release rule of
R10-6. Exploratory, for the paper.

- trep: the original tool (tools.TOOLS["t0"]) sent again in a new batch (run erc2_haiku). Its params equal the t0
  request of runs.build_a byte for byte.
- tord: the original tool with the keys of input_schema.properties in alphabetical order and the required list in the
  same order (`ordered_tool`). Every name, option value and text stays the same.
- Run erc_haiku: cells t0 (the control) and tord. Run erc2_haiku: cell trep. READS answers per arm and prefix: 10 on
  the specific set (brief sets hotel), 1 on the open and guesthouse sets.
Usage (from explore/): .venv/bin/python -I r10/control.py check | show | pilot-copy
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
import tools  # noqa: E402
import zforms  # noqa: E402

AMENDMENT = "### R10-16 "
READS = {"open": 1, "specific": 10, "guesthouse": 1}  # answers per arm and prefix (fixed in R10-16)
CELLS = {"control": ("t0", "tord"), "repeat": ("trep",)}


def ordered_tool():
    """tools.SEARCH_T0 with the properties and the required list in alphabetical order; nothing else changes."""
    t = copy.deepcopy(tools.SEARCH_T0)
    s = t["input_schema"]
    names = sorted(s["properties"])
    t["input_schema"] = {k: ({n: s["properties"][n] for n in names} if k == "properties" else
                             names if k == "required" else v) for k, v in s.items()}
    return t


TOOL_OF = {"t0": tools.TOOLS["t0"], "trep": tools.TOOLS["t0"], "tord": [ordered_tool()]}


def set_of(data, g):
    """{dialogue id: "open" | "specific" | "guesthouse" | None} for the 554 prefixes (the sets of R10-6)."""
    import gold
    out = {}
    for d in g["booked"]:
        t = gold.brief_type(data[d])
        out[d] = ("open" if t is None and gold.brief_type(data[d], "fail_info") is None else
                  "specific" if t == "hotel" else "guesthouse" if t == "guesthouse" else None)
    return out


def build(name, model, reads, data, g, part):
    """The cells of `part` on the 554 prefixes, READS answers per arm and prefix (reads must be 1)."""
    import models
    import runs
    assert reads == 1, reads
    system = tools.tool_system("t0")
    sets = set_of(data, g)
    out = []
    for d in g["booked"]:
        if sets[d] is None:  # a prefix outside the three sets (none in the 554; the sets of R10-6 cover all of them)
            continue
        user = zforms.prefix_text(data[d])
        for read in range(1, READS[sets[d]] + 1):
            for cell in CELLS[part]:
                out.append(models.request(model, runs.cid(name, d, cell, read), user, system, None,
                                          tools=TOOL_OF[cell], cell=cell))
    return out


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-16 is in PROTOCOL.md under the round-10 amendments and names the read counts of READS."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    if "10 per arm on the specific set, 1 per arm on the open set and on the guesthouse set" not in flat:
        sys.exit("Not run. R10-16 does not hold the read counts of control.READS.")
    if "(area, internet, name, parking, pricerange, stars, type)" not in flat:
        sys.exit("Not run. R10-16 does not hold the field order of control.ordered_tool.")
    assert list(ordered_tool()["input_schema"]["properties"]) == ["area", "internet", "name", "parking", "pricerange",
                                                                  "stars", "type"]


def pilot_copy():
    """erc2_haiku gets the pilot.json of erc_haiku, with the t0 entry also under trep (the same requests)."""
    src = json.loads((EXPLORE / "erc_haiku" / "pilot.json").read_text())
    key = next(k for k in src if k.endswith("|t0"))
    out = {key: src[key], key.rsplit("|", 1)[0] + "|trep": src[key]}
    (EXPLORE / "erc2_haiku").mkdir(exist_ok=True)
    (EXPLORE / "erc2_haiku" / "pilot.json").write_text(json.dumps(out, indent=1))
    print("erc2_haiku/pilot.json written from erc_haiku/pilot.json:", list(out))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-16 holds the read counts and the field order")
    elif cmd == "show":
        print(json.dumps(ordered_tool(), indent=1)[:1500])
    elif cmd == "pilot-copy":
        pilot_copy()
    else:
        sys.exit(__doc__)
