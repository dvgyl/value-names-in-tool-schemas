"""Forms and dialogue texts of the round-9 additions Z1 to Z3 and the balance runs B2 to B4 (ROUND9-ADDITIONS.md).

F0 is the E13 form `p_main` and F1 is `p_main_renamed`, each with the E13 closed schema (pmain/e13.py). Every other
form adds one part to F0. `parse` maps each form back to the fields and values of F0, so all forms are scored on the
same fields. `test_forms.py` checks that each form and each text edit changes only its intended text.
"""
import json
import pathlib
import re
import sys
from typing import NamedTuple

EXPLORE = pathlib.Path(__file__).resolve().parents[2]
for _sub in ("lib", "forms", "pmain", "trackc"):
    sys.path.insert(0, str(EXPLORE / _sub))
import anth  # noqa: E402
import common  # noqa: E402
import e13  # noqa: E402
import templates  # noqa: E402

F0 = common.FORMS["p_main"].system
F1 = common.FORMS["p_main_renamed"].system
ALLOWED_END = "internet: yes, no."  # the last allowed value list; p_define and p_split add their sentence after it
DEFINE = "`hotel` means the database category hotel, not the traveller's general word for a place to stay."
SPLIT_FIELDS = (", stars, type, parking,", ", stars, type_required, type_preferred, parking,")
SPLIT_VALUES = ("type: guesthouse, hotel.", "type_required: guesthouse, hotel. type_preferred: guesthouse, hotel.")
SPLIT_RULE = ("type_required filters the search, so give it only the types that the traveller requires. type_preferred "
              "only changes the order of the results, so give it the types that the traveller prefers but does not "
              "require.")
# The E14 way (trackc/templates.py): the ambiguity sentence goes after the "changed their mind" sentence.
UNCLEAR_SENTENCE = templates.AMBIGUITY
NULL_SENTENCE = templates.AMBIGUITY.replace('write "unclear"', "write null")
FRAME = ("hotel booking assistant", "accommodation booking assistant")
PROBE_QUESTION = ("Does the traveller's wording fix the venue type to hotel? Answer fixes, does not fix, or cannot "
                  "tell.")
PROBE_VALUES = ("fixes", "does not fix", "cannot tell")


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


def schema(words=("any",), type_keys=("type",), type_values=tuple(e13.VALUES["type"])):
    """The E13 schema: each field is null, one of `words`, or a list of allowed values. `type_keys` take the place of
    the `type` key, with `type_values` as their allowed values."""
    props = {"name": {"anyOf": [{"type": "null"}, {"type": "string"}]}}
    for field, values in e13.VALUES.items():
        keys, vals = (type_keys, type_values) if field == "type" else ((field,), values)
        for key in keys:
            props[key] = {"anyOf": [{"type": "null"}, {"type": "string", "enum": list(words)},
                                    {"type": "array", "items": {"type": "string", "enum": list(vals)}}]}
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


class Form(NamedTuple):
    system: str
    schema: dict  # the closed JSON schema of the answer, without a provider wrapper


FORMS = {
    "f0": Form(F0, schema()),
    "f1": Form(F1, schema(type_keys=("property_kind",), type_values=("guesthouse", "large_property"))),
    "p_define": Form(once(F0, ALLOWED_END, f"{ALLOWED_END} {DEFINE}"), schema()),
    "p_split": Form(once(once(once(F0, *SPLIT_FIELDS), *SPLIT_VALUES), ALLOWED_END, f"{ALLOWED_END} {SPLIT_RULE}"),
                    schema(type_keys=("type_required", "type_preferred"))),
    "p_null_nat": Form(once(F0, templates.CHANGED, templates.CHANGED + NULL_SENTENCE), schema()),
    "p_unclear_nat": Form(once(F0, templates.CHANGED, templates.CHANGED + UNCLEAR_SENTENCE),
                          schema(words=("any", "unclear"))),
    "probe": Form(F0.split(". ")[0] + ". " + PROBE_QUESTION,
                  {"type": "object", "properties": {"answer": {"type": "string", "enum": list(PROBE_VALUES)}},
                   "required": ["answer"], "additionalProperties": False}),
}


def framed(system):
    """The Z1 frame edit: the system prompt calls the assistant an accommodation booking assistant."""
    return once(system, *FRAME)


def parse(form, text):
    """The last JSON object of a reply, mapped to the F0 fields by common.parse. p_split maps `type_required` to
    `type`, the field that filters, and keeps `type_preferred`. The probe gives {"answer": one of PROBE_VALUES}."""
    s, e = text.rfind("{"), text.rfind("}")
    obj = json.loads(text[s:e + 1])
    if form == "probe":
        if obj.get("answer") not in PROBE_VALUES:
            raise ValueError(f"probe answer {obj.get('answer')!r}")
        return {"answer": obj["answer"]}
    preferred = None
    if form == "p_split":
        preferred = obj.pop("type_preferred", None)
        if "type_required" in obj:
            obj["type"] = obj.pop("type_required")
    out = common.parse(json.dumps(obj))
    if form == "p_split":
        out["type_preferred"] = common.parse(json.dumps({"type": preferred}))["type"]
    return out


# Text variants. A traveller turn has an even index in the log, as in common.dialogue_text.
WORD = re.compile(r"\bhotels?\b", re.I)
HOTELS = json.loads((anth.DATA / "hotel_db.json").read_text())
# The word before "hotel" in each venue name that holds "hotel" (arms, ashley, gonville, lensfield, marriott), and
# "marriot", the one misspelt name in the traveller turns of the 994 dialogues (MUL0601). The rule also keeps short
# forms such as "the Marriott hotel" and "Lensfield Hotel".
NAME_WORDS = sorted({n.split()[n.split().index("hotel") - 1] for n in (h["name"].lower() for h in HOTELS)
                     if "hotel" in n.split()} | {"marriot"})
IN_NAME = re.compile(r"\b(?:" + "|".join(map(re.escape, NAME_WORDS)) + r")\s+hotels?\b", re.I)


def _place_to_stay(word):
    new = "places to stay" if word.lower() == "hotels" else "place to stay"
    return new.upper() if word.isupper() else new[0].upper() + new[1:] if word[0].isupper() else new


def edit_turn(text):
    """Z1: "hotel" becomes "place to stay" and "hotels" becomes "places to stay", except inside a venue name."""
    kept = [m.span() for m in IN_NAME.finditer(text)]
    return WORD.sub(lambda m: m.group(0) if any(a <= m.start() < b for a, b in kept) else _place_to_stay(m.group(0)),
                    text)


def edited_text(d):
    """The dialogue text with every traveller turn edited by edit_turn. Assistant turns stay as they are."""
    return common.dialogue_text({"log": [{"text": edit_turn(t["text"]) if i % 2 == 0 else t["text"]}
                                         for i, t in enumerate(d["log"])]})


def prefix_end(d):
    """The index of the first traveller turn that says "hotel" (the rule of the 994 traveller-turns dialogues)."""
    return next(i for i, t in enumerate(d["log"]) if i % 2 == 0 and WORD.search(t["text"]))


def prefix_text(d):
    """Z2: all turns up to and including the first traveller turn that says "hotel"."""
    return common.dialogue_text({"log": d["log"][:prefix_end(d) + 1]})


TEXTS = {"orig": common.dialogue_text, "edit": edited_text, "prefix": prefix_text}
