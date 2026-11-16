"""Forms and parsers of experiment B of round 10 (ROUND10-EXPERIMENT-PLAN.md section 4 B, review/plan15/ACTION-PLAN.md
section 2.6).

FORMS holds one zforms.Form(system, schema) for each cell tag. F0 is the E13 form `p_main` (zforms.FORMS["f0"]). Each
B arm changes one named part of F0 and no other text:
- `b_list`: the `type` key becomes `accepted_types`, and one sentence after zforms.ALLOWED_END tells what the list is.
- `b_shot`: two worked examples after zforms.ALLOWED_END. The schema is the F0 schema.
- `b_evidence`: each field becomes an object {"value", "quote", "status"}, and the sentences after zforms.ALLOWED_END
  tell how to fill the object.
- `verify`: a separate call with its own system text and the schema {"answer": "yes" | "no" | "unclear"}.
- `b_define`: the round-9 form `p_define` (zforms.FORMS["p_define"]).

`parse(arm, text, turns)` maps each answer back to the F0 fields (name, area, pricerange, stars, type, parking,
internet), so all arms are scored on the same fields. `b_verify` makes the B-verify answer from an F0 answer and the
verifier's answer. NEW_TEXTS holds every new sentence and example text, for groups.assert_new_text.
`tests/test_forms10.py` checks that each arm changes only its named part.
"""
import json
import pathlib
import sys

EXPLORE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPLORE / "r9" / "additions"))
import zforms  # noqa: E402
from zforms import common  # noqa: E402

F0 = zforms.F0
ALLOWED_END = zforms.ALLOWED_END
FIELDS = ("name", *common.FIELDS)  # the keys of an F0 answer, in schema order

# b_list: the `type` key and its sentence.
LIST_KEY = "accepted_types"
LIST_FIELDS = (", stars, type, parking,", ", stars, accepted_types, parking,")
LIST_VALUES = ("type: guesthouse, hotel.", "accepted_types: guesthouse, hotel.")
LIST_RULE = "Give accepted_types as a list of every type that the traveller accepts, or null."

# b_shot: two worked examples, new constructed text. Example 1 uses "hotel" as the general word for a place to stay,
# so its answer has `type` null. In Example 2 the traveller excludes guesthouses, so its answer has `type` ["hotel"].
# The examples go between ALLOWED_END and the next F0 sentence, with blank lines in place of the one space there.
EXAMPLE_1 = (
    "Example 1:\n"
    "Traveller: I have a job interview in Cambridge on Thursday morning, so I need a hotel for Wednesday night.\n"
    "Assistant: Good luck with the interview. Which area of Cambridge would be best for you?\n"
    "Traveller: Somewhere in the north, and it has to be cheap. I am driving there, so I also need parking.\n"
    'Answer: {"name": null, "area": ["north"], "pricerange": ["cheap"], "stars": null, "type": null, '
    '"parking": ["yes"], "internet": null}')
EXAMPLE_2 = (
    "Example 2:\n"
    "Traveller: My parents are coming to Cambridge for their anniversary, and they want a hotel for two nights. "
    "They will only stay in the west, because their friends live there.\n"
    "Assistant: What a nice plan. What else matters to them?\n"
    "Traveller: Please do not offer them a guesthouse, because they did not enjoy the last one. It must also have "
    "four stars.\n"
    'Answer: {"name": null, "area": ["west"], "pricerange": null, "stars": ["4"], "type": ["hotel"], '
    '"parking": null, "internet": null}')
SHOT = (ALLOWED_END + " ", ALLOWED_END + "\n\n" + EXAMPLE_1 + "\n\n" + EXAMPLE_2 + "\n\n")

# b_evidence: the object of each field and its sentences.
STATUS_VALUES = ("stated requirement", "mention only")
EVIDENCE_SENTENCES = (
    'Give each field as an object with the keys "value", "quote" and "status".',
    'In "value", give the field value as described above.',
    'In "quote", copy the exact words of one traveller turn that support the value.',
    'In "status", give "stated requirement" if the traveller requires the value, or "mention only" if the traveller '
    'only mentions the value.',
    'If the value is null, give "" for "quote" and "no value" for "status".',
)
# Amendment R10-1 (2026-11-12, before any batch result): the Claude API refused the first schema ("too many parameters
# with union types": 21, limit 16), so "quote" is a string ("" when there is no value) and "status" has a third value.
NO_VALUE = "no value"
EVIDENCE_RULE = " ".join(EVIDENCE_SENTENCES)

# verify: a separate call. The first F0 sentence frames the conversation, as in the round-9 probe.
VERIFY_QUESTION = "Does the traveller exclude guesthouses? Answer yes, no, or unclear."
VERIFY_VALUES = ("yes", "no", "unclear")
VERIFY_SYSTEM = F0.split(". ")[0] + ". " + VERIFY_QUESTION
VERIFY_SCHEMA = {"type": "object", "properties": {"answer": {"type": "string", "enum": list(VERIFY_VALUES)}},
                 "required": ["answer"], "additionalProperties": False}

# Every new text of the round-10 arms. b_define uses the round-9 sentence zforms.DEFINE, which is not new.
NEW_TEXTS = (LIST_RULE, EXAMPLE_1, EXAMPLE_2, *EVIDENCE_SENTENCES, VERIFY_QUESTION)


def _nullable(option):
    return {"anyOf": [{"type": "null"}, option]}


def evidence_schema():
    """The F0 schema with each field property P put in an object {"value": P, "quote": string, "status": one of
    STATUS_VALUES or NO_VALUE}. Only the 7 value properties are unions (amendment R10-1)."""
    base = zforms.schema()
    props = {key: {"type": "object",
                   "properties": {"value": prop, "quote": {"type": "string"},
                                  "status": {"type": "string", "enum": [*STATUS_VALUES, NO_VALUE]}},
                   "required": ["value", "quote", "status"], "additionalProperties": False}
             for key, prop in base["properties"].items()}
    return {**base, "properties": props}


once = zforms.once
FORMS = {
    "f0": zforms.FORMS["f0"],
    "b_list": zforms.Form(once(once(once(F0, *LIST_FIELDS), *LIST_VALUES), ALLOWED_END, f"{ALLOWED_END} {LIST_RULE}"),
                          zforms.schema(type_keys=(LIST_KEY,))),
    "b_shot": zforms.Form(once(F0, *SHOT), zforms.schema()),
    "b_evidence": zforms.Form(once(F0, ALLOWED_END, f"{ALLOWED_END} {EVIDENCE_RULE}"), evidence_schema()),
    "verify": zforms.Form(VERIFY_SYSTEM, VERIFY_SCHEMA),
    "b_define": zforms.FORMS["p_define"],
}
AS_F0 = ("f0", "b_shot", "b_define")  # the arms whose answer has the F0 schema


def traveller_turns(d):
    """The texts of the traveller turns of a MultiWOZ dialogue (even indices, as in common.dialogue_text)."""
    return [t["text"] for i, t in enumerate(d["log"]) if i % 2 == 0]


def _squash(text):
    return " ".join(text.split())


def verbatim(quote, turns):
    """True when the quote occurs in one traveller turn, letter for letter and with the same case. Only the runs of
    white space are made equal. An empty quote is not verbatim."""
    q = _squash(quote)
    return bool(q) and any(q in _squash(t) for t in turns)


def _flat_object(text):
    """The last JSON object of a reply, as zforms.parse finds it. Use it only for a flat object."""
    s, e = text.rfind("{"), text.rfind("}")
    return json.loads(text[s:e + 1])


def _top_object(text):
    """The last JSON object of a reply that is not inside another object."""
    decoder, found, i = json.JSONDecoder(), None, text.find("{")
    while i != -1:
        try:
            found, end = decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            end = i + 1
        i = text.find("{", end)
    if not isinstance(found, dict):
        raise ValueError("the reply holds no JSON object")
    return found


def _parse_list(text):
    obj = _flat_object(text)
    obj["type"] = obj.pop(LIST_KEY, None)  # only accepted_types gives the type
    out = common.parse(json.dumps(obj))
    accepted = out["type"]
    both = isinstance(accepted, tuple) and {"hotel", "guesthouse"} <= set(accepted)
    out["type"] = None if both else accepted
    out[LIST_KEY] = accepted
    return out


def _parse_evidence(text, turns):
    if turns is None or isinstance(turns, str):
        raise RuntimeError("b_evidence needs the list of traveller turns: parse(arm, text, traveller_turns(d))")
    obj = _top_object(text)
    if obj and not set(obj) & set(FIELDS):
        raise ValueError("the reply holds no b_evidence answer object")
    values, quotes, status = {}, {}, {}
    for field in FIELDS:
        entry = obj.get(field)
        entry = {} if entry is None else entry
        if not isinstance(entry, dict):
            raise ValueError(f"b_evidence field {field!r} is not an object")
        values[field], quotes[field], status[field] = entry.get("value"), entry.get("quote"), entry.get("status")
        quotes[field] = None if quotes[field] == "" else quotes[field]  # amendment R10-1: "" means no quote
        status[field] = None if status[field] == NO_VALUE else status[field]  # and "no value" means no status
        if values[field] is not None and not isinstance(values[field], (str, list)):
            raise ValueError(f"b_evidence value of {field!r} is {values[field]!r}")
        if quotes[field] is not None and not isinstance(quotes[field], str):
            raise ValueError(f"b_evidence quote of {field!r} is {quotes[field]!r}")
        if status[field] not in (None, *STATUS_VALUES):
            raise ValueError(f"b_evidence status of {field!r} is {status[field]!r}")
    raw = common.parse(json.dumps(values))
    out = {field: raw[field] if status[field] == "stated requirement" else None for field in FIELDS}
    out["raw"] = raw
    out["status"] = status
    out["verbatim"] = {field: None if quotes[field] is None else verbatim(quotes[field], turns) for field in FIELDS}
    return out


def _parse_verify(text):
    answer = _flat_object(text).get("answer")
    if answer not in VERIFY_VALUES:
        raise ValueError(f"verify answer {answer!r}")
    return {"answer": answer}


def parse(arm, text, turns=None):
    """Map the reply of one arm to the F0 fields, as common.parse gives them. ValueError: the answer is not valid.
    RuntimeError: the call is wrong (an unknown arm, or b_evidence without the traveller turns).

    - f0, b_shot, b_define: zforms.parse("f0", text), the round-9 parser.
    - b_list: `type` is the accepted_types list, except that a list with both `hotel` and `guesthouse` gives null,
      because it excludes no type. So `hotel` stays only when the list holds `hotel` and not `guesthouse`. The key
      `accepted_types` holds the list as the model gave it, after common.parse.
    - b_evidence: `turns` is the list of traveller turn texts (traveller_turns(d)). A field keeps its value only when
      its status is "stated requirement"; else the field is null. The key `raw` holds every value before this rule,
      `status` the status of each field, and `verbatim` for each field True or False (does the quote occur in a
      traveller turn?), or None when the quote is null. A missing field is null.
    - verify: {"answer": one of VERIFY_VALUES}.
    """
    if arm in AS_F0:
        return zforms.parse("f0", text)
    if arm == "b_list":
        return _parse_list(text)
    if arm == "b_evidence":
        return _parse_evidence(text, turns)
    if arm == "verify":
        return _parse_verify(text)
    raise RuntimeError(f"unknown arm {arm!r}")


def b_verify(f0_answer, verify_answer):
    """The B-verify answer: the parsed F0 answer of one dialogue and read number, where a `type` list that holds
    `hotel` and not `guesthouse` becomes null unless the verifier says "yes". The verifier asks whether the traveller
    excludes guesthouses, so it gates only a value that excludes guesthouses. A list that holds both types does not
    change (Opus, 2026-11-12: making it null would count a lost correct value on S2 with no change of the search).
    Other fields do not change. f0_answer is not changed."""
    if verify_answer not in VERIFY_VALUES:
        raise ValueError(f"verify answer {verify_answer!r}")
    out = dict(f0_answer)
    t = out["type"]
    if verify_answer != "yes" and isinstance(t, tuple) and "hotel" in t and "guesthouse" not in t:
        out["type"] = None
    return out
