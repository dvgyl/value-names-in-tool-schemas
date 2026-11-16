"""Amendment R10-18 (PROTOCOL.md): the label test with one fixed definition. Exploratory, fixed in the protocol before
the run.

Question: does the hotel effect come from the shared word in the value label when the category definition is the same?
Two arms. They differ only in the value label of the `type` field. Both have the same written definition:
- l_hotel: "type: guesthouse, hotel (any venue type that is not a guesthouse)."
- l_code:  "type: guesthouse, category_A (any venue type that is not a guesthouse)."
The definition is the note of the round-9 form F6 (natural.FORMS["f6"].note). l_code is F6 on the F0 text, byte for
byte. l_hotel is F0 with the same note after the value `hotel`. The system text, the field names, the schema keys, the
user text (the full dialogue) and the model settings are those of the F0 request of experiment B (forms10.FORMS["f0"]).

Dialogues: the development sets of verify3.sets: 807 dialogues of S1t whose brief sets no type, and 233 dialogues of S2
whose brief sets hotel. No held-out, validation, test or sealed dialogue (runs.requests calls groups.assert_unprotected).
Runs: r10/runs.py, experiment code "L" (erl_sonnet, erl_sonnet_hb, erl_haiku, erl_sol, erl_luna).
Usage (from explore/): .venv/bin/python -I r10/labeltest.py check | texts | sets
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import e13  # noqa: E402
import natural  # noqa: E402
import zforms  # noqa: E402

AMENDMENT = "### R10-18 "
NOTE = natural.FORMS["f6"].note  # " (any venue type that is not a guesthouse)", a round-9 text
LABELS = {"l_hotel": "hotel", "l_code": natural.FORMS["f6"].hotel}  # the value label of each arm
CELLS = tuple(LABELS)
NATURAL = {cell: natural.Form({}, label, NOTE) for cell, label in LABELS.items()}
FORMS = {cell: zforms.Form(natural.system(zforms.F0, f), natural.schema(e13.schema(False), f)["schema"])
         for cell, f in NATURAL.items()}
TYPE_LINE = {cell: f"type: guesthouse, {label}{NOTE}." for cell, label in LABELS.items()}
RUNS = ("erl_sonnet", "erl_sonnet_hb", "erl_haiku", "erl_sol", "erl_luna")
SETS = ("no_type", "hotel")
# Money (operator approval of 2026-11-14, relayed by the coordinator): R10-18 may spend the money that is left under
# the ledger limit of anthropic_r9a, anthropic_r9b and openai_r9, so its budget-gate reserve is 0.00 USD.
# accounts.check_approval still refuses a step when the committed money plus the bound passes the account limit.
RESERVE = 0.00
MAX_BOUND = 6.00  # USD per step


def parse(cell, text):
    """The F0 fields of one answer (common.parse), after natural.parse maps the arm's label back to `hotel`.
    ValueError: the answer is not valid. A `type` value outside the arm's two values (guesthouse and its label) is not
    valid, so a raw `hotel` in an l_code answer cannot count as a hotel value. RuntimeError: an unknown cell."""
    if cell not in NATURAL:
        raise RuntimeError(f"unknown cell {cell!r}")
    import json
    s, e = text.rfind("{"), text.rfind("}")
    raw = json.loads(text[s:e + 1])
    t = raw.get("type")
    allowed = {"guesthouse", LABELS[cell].lower()}
    for v in t if isinstance(t, list) else ([] if t is None or str(t).lower() in ("any", "dontcare") else [t]):
        if str(v).strip().lower() not in allowed:
            raise ValueError(f"{cell}: type value {v!r} is not one of the arm's values")
    return natural.parse(text, NATURAL[cell])


def sets(data, g):
    """The two development sets of R10-17 (verify3.sets): {"no_type": 807 ids, "hotel": 233 ids}."""
    import verify3
    return verify3.sets(data, g)


def build(sets_used):
    """A build for runs.Run: cells l_hotel and l_code, reads 1..reads, on the named sets; per dialogue and read the
    two arms follow each other, so both arms of a dialogue are in the same batch."""
    def built(name, model, reads, data, g):
        import models
        import runs
        s = sets(data, g)
        out = []
        for set_name in sets_used:
            for d in s[set_name]:
                user = runs.text_full(data, d)
                for read in range(1, reads + 1):
                    for cell in CELLS:
                        form = FORMS[cell]
                        out.append(models.request(model, runs.cid(name, d, cell, read), user, form.system,
                                                  form.schema, cell=cell))
        return out
    built.sets = tuple(sets_used)
    return built


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-18 is in PROTOCOL.md under the round-10 amendments and holds the two type lines and the fixed values."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    for words in (*TYPE_LINE.values(), "807 dialogues", "233 dialogues", "Status: exploratory, fixed in the protocol "
                  "before the run.", *RUNS):
        if words not in flat:
            sys.exit(f"Not run. R10-18 does not hold {words!r}.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-18 holds the two type lines and the fixed values")
    elif cmd == "texts":
        for c in CELLS:
            print(c, TYPE_LINE[c])
    elif cmd == "sets":
        import runs
        data, g = runs.context()
        print({k: len(v) for k, v in sets(data, g).items()})
    else:
        sys.exit(__doc__)
