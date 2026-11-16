"""Amendment R10-19 (PROTOCOL.md): the label test with one fixed definition, third arm. Exploratory, fixed in the
protocol before the run.

The R10-18 arms stay as they are (labeltest.FORMS; their requests do not change). This module adds one arm:
- l_neutral: "type: guesthouse, serviced_property (any venue type that is not a guesthouse)."
The label is the registered neutral value (natural.NEUTRAL, the F4 token). The definition is the R10-18 note. So the
three arms differ only in the value label: hotel (the shared word), category_A (a code), serviced_property (a familiar
word that is not the shared word).

Runs (r10/runs.py, experiment code "L2"; the cells of each run are in PLAN):
- erl2_sol, erl2_luna (openai_r9): l_neutral reads 1 and 2; new reads of l_hotel and l_code in the same batch
  (Sol read 2, Luna reads 3 and 4; R10-18 holds Sol read 1 and Luna reads 1 and 2).
- erl2_sonnet_a (anthropic_r9b), erl2_sonnet_b (anthropic_r9a): l_neutral read 1 on the 807 no-type dialogues, split
  by SONNET_SPLIT.
- erl2_haiku (anthropic_r9a): l_neutral reads 1 and 2 on the 1,040 dialogues.
- erl2_deepseek, erl2_qwen, erl2_gemma (deepinfra_main, synchronous): the three arms, reads 1 and 2.
Usage (from explore/): .venv/bin/python -I r10/labeltest2.py check | texts | split | pilot-copy
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import e13  # noqa: E402
import labeltest as lt  # noqa: E402
import natural  # noqa: E402
import zforms  # noqa: E402

AMENDMENT = "### R10-19 "
NEW = "l_neutral"
LABELS = {**lt.LABELS, NEW: natural.NEUTRAL}  # serviced_property
CELLS = (*lt.CELLS, NEW)
NATURAL = {**lt.NATURAL, NEW: natural.Form({}, natural.NEUTRAL, lt.NOTE)}
FORMS = {**lt.FORMS, NEW: zforms.Form(natural.system(zforms.F0, NATURAL[NEW]),
                                      natural.schema(e13.schema(False), NATURAL[NEW])["schema"])}
TYPE_LINE = {cell: f"type: guesthouse, {label}{lt.NOTE}." for cell, label in LABELS.items()}
# (sets, {cell: read numbers}) per run. Every set name is a key of labeltest.sets, or "no_type_a" / "no_type_b".
BOTH = ("no_type", "hotel")
PLAN = {
    "erl2_sol": (BOTH, {NEW: (1, 2), "l_hotel": (2,), "l_code": (2,)}),
    "erl2_luna": (BOTH, {NEW: (1, 2), "l_hotel": (3, 4), "l_code": (3, 4)}),
    "erl2_sonnet_a": (("no_type_a",), {NEW: (1,)}),
    "erl2_sonnet_b": (("no_type_b",), {NEW: (1,)}),
    "erl2_haiku": (BOTH, {NEW: (1, 2)}),
    "erl2_deepseek": (BOTH, {c: (1, 2) for c in CELLS}),
    "erl2_qwen": (BOTH, {c: (1, 2) for c in CELLS}),
    "erl2_gemma": (BOTH, {c: (1, 2) for c in CELLS}),
}
RUNS = tuple(PLAN)
SONNET_A = 440  # the first 440 no-type dialogues in the split order go to erl2_sonnet_a, the other 367 to erl2_sonnet_b
RESERVE = 0.00  # the budget-gate reserve of R10-19 and R10-20; the caps of newmoney.CAPS hold the margin
NO_PILOT = ("erl2_sonnet_b",)  # its pilot.json is a copy of the erl2_sonnet_a pilot (pilot_copy)
MAX_BOUND = 8.00  # USD per step


def parse(cell, text):
    """As labeltest.parse, with the third arm. ValueError: the answer is not valid; a `type` value outside the arm's two
    values is not valid. RuntimeError: an unknown cell."""
    if cell in lt.NATURAL:
        return lt.parse(cell, text)
    if cell != NEW:
        raise RuntimeError(f"unknown cell {cell!r}")
    s, e = text.rfind("{"), text.rfind("}")
    raw = json.loads(text[s:e + 1])
    t = raw.get("type")
    allowed = {"guesthouse", LABELS[NEW].lower()}
    for v in t if isinstance(t, list) else ([] if t is None or str(t).lower() in ("any", "dontcare") else [t]):
        if str(v).strip().lower() not in allowed:
            raise ValueError(f"{cell}: type value {v!r} is not one of the arm's values")
    return natural.parse(text, NATURAL[NEW])


def split_key(d):
    """The split order of the no-type dialogues: the SHA-256 hex digest of the dialogue id without ".json"."""
    return hashlib.sha256(d.removesuffix(".json").encode()).hexdigest()


def sets(data, g):
    """The R10-18 sets (labeltest.sets) and the fixed Sonnet split of the no-type set."""
    s = dict(lt.sets(data, g))
    order = sorted(s["no_type"], key=split_key)
    s["no_type_a"], s["no_type_b"] = order[:SONNET_A], order[SONNET_A:]
    return s


def build(name, model, reads, data, g):
    """The cells and reads of PLAN[name]. Per dialogue and read, the cells follow each other in the order of CELLS, so
    all arms of one dialogue and read are in the same batch. `reads` must be 1 (PLAN holds the read numbers)."""
    import models
    import runs
    assert reads == 1, reads
    sets_used, cells = PLAN[name]
    s = sets(data, g)
    out = []
    for set_name in sets_used:
        for d in s[set_name]:
            user = runs.text_full(data, d)
            for read in sorted({r for rr in cells.values() for r in rr}):
                for cell in CELLS:
                    if read in cells.get(cell, ()):
                        form = FORMS[cell]
                        out.append(models.request(model, runs.cid(name, d, cell, read), user, form.system,
                                                  form.schema, cell=cell))
    return out


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-19 is in PROTOCOL.md under the round-10 amendments and holds the type line, the split and the fixed values."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    for words in (*TYPE_LINE.values(), "807 no-type dialogues", "233 hotel-brief dialogues", "Status: exploratory, "
                  "fixed in the protocol before the run.", f"the first {SONNET_A} dialogues", *RUNS):
        if words not in flat:
            sys.exit(f"Not run. R10-19 does not hold {words!r}.")


def pilot_copy():
    """erl2_sonnet_b gets the pilot.json of erl2_sonnet_a (the same cell; other dialogues of the same set)."""
    src = EXPLORE / "erl2_sonnet_a" / "pilot.json"
    if not src.exists():
        sys.exit(f"Not written. {src} does not exist; run the pilot of erl2_sonnet_a first.")
    (EXPLORE / "erl2_sonnet_b").mkdir(exist_ok=True)
    (EXPLORE / "erl2_sonnet_b" / "pilot.json").write_text(src.read_text())
    print("erl2_sonnet_b/pilot.json written from erl2_sonnet_a/pilot.json:", list(json.loads(src.read_text())))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-19 holds the type lines, the split and the fixed values")
    elif cmd == "texts":
        for c in CELLS:
            print(c, TYPE_LINE[c])
    elif cmd == "split":
        import runs
        data, g = runs.context()
        s = sets(data, g)
        a = s["no_type_a"]
        print(len(a), len(s["no_type_b"]), "first:", a[0], "last of a:", a[-1],
              "SHA-256 of the part-a list:", hashlib.sha256("\n".join(a).encode()).hexdigest())
    elif cmd == "pilot-copy":
        pilot_copy()
    else:
        sys.exit(__doc__)
