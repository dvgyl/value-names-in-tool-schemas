"""Form and parser test of r10/forms10.py (no API call, no MultiWOZ dialogue). Usage: .venv/bin/python -I
r10/tests/test_forms10.py (from explore/)

Each arm must equal F0 after its intended change is undone. The intended changes and the verify texts are written here
as literals, so a change to forms10 that is not in this list fails.
"""
import copy
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import forms10  # noqa: E402
from forms10 import common, zforms  # noqa: E402

EXAMPLE_1 = (
    "Example 1:\n"
    "Traveller: I have a job interview in Cambridge on Thursday morning, so I need a hotel for Wednesday night.\n"
    "Assistant: Good luck with the interview. Which area of Cambridge would be best for you?\n"
    "Traveller: Somewhere in the north, and it has to be cheap. I am driving there, so I also need parking.\n"
    'Answer: {"name": null, "area": ["north"], "pricerange": ["cheap"], "stars": null, "type": null, '
    '"parking": ["yes"], "internet": null}')
EXAMPLE_2 = (
    "Example 2:\n"
    "Traveller: My parents are coming to Cambridge for their anniversary, and they want a hotel for two nights. They "
    "will only stay in the west, because their friends live there.\n"
    "Assistant: What a nice plan. What else matters to them?\n"
    "Traveller: Please do not offer them a guesthouse, because they did not enjoy the last one. It must also have four "
    "stars.\n"
    'Answer: {"name": null, "area": ["west"], "pricerange": null, "stars": ["4"], "type": ["hotel"], '
    '"parking": null, "internet": null}')
LIST_RULE = "Give accepted_types as a list of every type that the traveller accepts, or null."
EVIDENCE = ('Give each field as an object with the keys "value", "quote" and "status".',
            'In "value", give the field value as described above.',
            'In "quote", copy the exact words of one traveller turn that support the value.',
            'In "status", give "stated requirement" if the traveller requires the value, or "mention only" if the '
            'traveller only mentions the value.',
            'If the value is null, give "" for "quote" and "no value" for "status".')  # amendment R10-1
DEFINE = " `hotel` means the database category hotel, not the traveller's general word for a place to stay."
INTENDED = {  # (text in F0, text in the arm)
    "b_list": [(", stars, type, parking,", ", stars, accepted_types, parking,"),
               ("type: guesthouse, hotel.", "accepted_types: guesthouse, hotel."),
               ("", " " + LIST_RULE)],
    "b_shot": [("internet: yes, no. ", "internet: yes, no.\n\n" + EXAMPLE_1 + "\n\n" + EXAMPLE_2 + "\n\n")],
    "b_evidence": [("", " " + " ".join(EVIDENCE))],
    "b_define": [("", DEFINE)],
}
VERIFY_SYSTEM = ("You read a conversation between a traveller and a hotel booking assistant in Cambridge. Does the "
                 "traveller exclude guesthouses? Answer yes, no, or unclear.")
VERIFY_SCHEMA = {"type": "object", "properties": {"answer": {"type": "string", "enum": ["yes", "no", "unclear"]}},
                 "required": ["answer"], "additionalProperties": False}
F0_KEYS = ["name", "area", "pricerange", "stars", "type", "parking", "internet"]
BLANK = dict.fromkeys(F0_KEYS)


def undo(text, changes):
    for old, new in changes:
        assert text.count(new) == 1, (new, text.count(new))
        text = text.replace(new, old)
    return text


def reply(**fields):
    """A reply with a short text before the JSON object, as a reply with thinking text can have."""
    return "Here is the answer.\n" + json.dumps({**BLANK, **fields})


def raises(error, fn, *args):
    try:
        fn(*args)
    except error:
        return
    raise AssertionError(f"{fn.__name__}{args!r} must raise {error.__name__}")


def test_arms_and_base_forms():
    assert list(forms10.FORMS) == ["f0", "b_list", "b_shot", "b_evidence", "verify", "b_define"]
    assert forms10.FORMS["f0"] == zforms.FORMS["f0"] == (common.FORMS["p_main"].system, zforms.schema())
    assert forms10.FORMS["b_define"] == zforms.FORMS["p_define"], "b_define is the round-9 p_define form"


def test_each_arm_changes_only_its_text():
    f0 = forms10.FORMS["f0"].system
    for arm, changes in INTENDED.items():
        system = forms10.FORMS[arm].system
        assert system != f0 and undo(system, changes) == f0, f"{arm}: not F0 plus only its intended text"
    for arm, first in (("b_list", LIST_RULE), ("b_shot", "\n\nExample 1:\n"), ("b_evidence", EVIDENCE[0]),
                       ("b_define", DEFINE.strip())):  # each new text starts right after zforms.ALLOWED_END
        assert "internet: yes, no." + ("" if first.startswith("\n") else " ") + first in forms10.FORMS[arm].system, arm
    shot = forms10.FORMS["b_shot"].system
    assert shot.endswith('"internet": null}\n\nIf the traveller changed their mind, give the final requirement. An '
                         "option that the traveller only accepted from the assistant's offers is not a requirement. "
                         "Output only the JSON object."), "the F0 sentences after the examples must stay"


def test_schemas():
    f0 = zforms.schema()
    assert forms10.FORMS["b_shot"].schema == f0 and forms10.FORMS["b_define"].schema == f0
    b_list = forms10.FORMS["b_list"].schema
    keys = ["name", "area", "pricerange", "stars", "accepted_types", "parking", "internet"]
    assert list(b_list["properties"]) == keys and b_list["required"] == keys and not b_list["additionalProperties"]
    assert b_list["properties"]["accepted_types"] == f0["properties"]["type"], "only the key of `type` changes"
    assert {k: v for k, v in b_list["properties"].items() if k != "accepted_types"} == {
        k: v for k, v in f0["properties"].items() if k != "type"}
    ev = forms10.FORMS["b_evidence"].schema
    assert list(ev["properties"]) == F0_KEYS and ev["required"] == F0_KEYS and not ev["additionalProperties"]
    for key, prop in ev["properties"].items():
        assert prop == {"type": "object",
                        "properties": {"value": f0["properties"][key],
                                       "quote": {"type": "string"},
                                       "status": {"type": "string", "enum": [
                                           "stated requirement", "mention only", "no value"]}},
                        "required": ["value", "quote", "status"], "additionalProperties": False}, key
    assert forms10.FORMS["f0"].schema == f0, "building the arms must not change the F0 schema"


def test_verify_texts_are_fixed():
    assert forms10.FORMS["verify"] == (VERIFY_SYSTEM, VERIFY_SCHEMA)
    assert forms10.VERIFY_SYSTEM == VERIFY_SYSTEM and forms10.VERIFY_VALUES == ("yes", "no", "unclear")


def test_new_texts():
    assert forms10.NEW_TEXTS == (LIST_RULE, EXAMPLE_1, EXAMPLE_2, *EVIDENCE,
                                 "Does the traveller exclude guesthouses? Answer yes, no, or unclear.")
    for text in forms10.NEW_TEXTS:
        assert any(text in form.system for form in forms10.FORMS.values()), text
        assert text not in zforms.F0, text


def _check_f0_answer(answer):
    """The answer satisfies the F0 schema: name null or a string; each other field null, "any", or allowed values."""
    assert list(answer) == F0_KEYS
    assert answer["name"] is None or isinstance(answer["name"], str)
    for field, values in zforms.e13.VALUES.items():
        v = answer[field]
        assert v is None or v == "any" or (isinstance(v, list) and v and set(v) <= set(values)), (field, v)


def test_worked_examples():
    for n, text, expected in ((1, EXAMPLE_1, None), (2, EXAMPLE_2, ("hotel",))):
        lines = text.split("\n")
        assert lines[0] == f"Example {n}:", lines[0]
        assert [line.split(": ")[0] for line in lines[1:]] == ["Traveller", "Assistant", "Traveller", "Answer"]
        answer = json.loads(lines[-1].removeprefix("Answer: "))
        _check_f0_answer(answer)
        assert common.parse(lines[-1])["type"] == expected
        traveller = " ".join(line for line in lines if line.startswith("Traveller: "))
        assert zforms.WORD.search(traveller), "both travellers say hotel"
        for name in (h["name"] for h in zforms.HOTELS):
            assert name.lower() not in text.lower(), f"the example uses the venue name {name!r}"
    assert not re.search(r"guest ?house", EXAMPLE_1, re.I), "Example 1 says nothing about guesthouses"
    assert "do not offer them a guesthouse" in EXAMPLE_2, "Example 2 excludes guesthouses"


def test_parse_as_f0():
    for arm in ("f0", "b_shot", "b_define"):
        assert forms10.parse(arm, reply(type=["hotel"], area=["north"])) == {**BLANK, "type": ("hotel",),
                                                                              "area": ("north",)}
        assert forms10.parse(arm, reply(type=["hotel", "guesthouse"]))["type"] == ("hotel", "guesthouse")
        assert forms10.parse(arm, reply(type=None))["type"] is None
        assert forms10.parse(arm, reply(type="any"))["type"] == "any"
        assert forms10.parse(arm, '{"name": null}')["type"] is None, "a missing field is null"


def test_parse_b_list():
    blank = {k: None for k in F0_KEYS if k != "type"}
    p = lambda **kw: forms10.parse("b_list", "Here is the answer.\n" + json.dumps({**blank, **kw}))
    assert p(accepted_types=["hotel"])["type"] == ("hotel",)
    assert p(accepted_types=["guesthouse"])["type"] == ("guesthouse",)
    for both in (["hotel", "guesthouse"], ["guesthouse", "hotel"], ["hotel", "Guest House"]):
        out = p(accepted_types=both)
        assert out["type"] is None, (both, out)  # a list of both types excludes no type
        assert set(out["accepted_types"]) == {"hotel", "guesthouse"}
    assert p(accepted_types=["hotel", "hotel"])["accepted_types"] == ("hotel",)
    assert p(accepted_types=None)["type"] is None and p(accepted_types=[])["type"] is None
    assert p(accepted_types="any")["type"] == "any"
    assert p()["type"] is None and p()["accepted_types"] is None, "a missing accepted_types is null"
    assert p(type=["hotel"], accepted_types=None)["type"] is None, "only accepted_types gives the type"
    out = p(accepted_types=["hotel"], area=["west", "north"], parking="any")
    assert (out["area"], out["parking"], out["accepted_types"]) == (("west", "north"), "any", ("hotel",))
    assert set(out) == set(F0_KEYS) | {"accepted_types"}


TURNS = ["Hi, I need a hotel in the  north for two nights.", "Yes, it must have free parking.", "That is all."]


def ev(**fields):
    """A b_evidence reply. Each keyword is (value, quote, status) or None."""
    obj = {k: None if v is None else {"value": v[0], "quote": v[1], "status": v[2]} for k, v in fields.items()}
    return json.dumps(obj)


def test_parse_b_evidence():
    p = lambda text: forms10.parse("b_evidence", text, TURNS)
    out = p(ev(type=(["hotel"], "I need a hotel", "mention only"), area=(["north"], "in the north", "stated requirement"),
               parking=(["yes"], "it must have free parking", "stated requirement")))
    assert out["type"] is None and out["raw"]["type"] == ("hotel",) and out["status"]["type"] == "mention only"
    assert out["area"] == ("north",) and out["parking"] == ("yes",)
    assert out["verbatim"]["type"] and out["verbatim"]["area"] and out["verbatim"]["parking"]
    assert out["name"] is None and out["stars"] is None and out["verbatim"]["stars"] is None, "missing fields are null"
    assert set(out) == set(F0_KEYS) | {"raw", "status", "verbatim"}
    out = p(ev(type=(["hotel"], "I need a hotel", "stated requirement")))
    assert out["type"] == ("hotel",) and out["raw"]["type"] == ("hotel",)
    not_verbatim = ("I need a hotel room", "i need a hotel", "a hotel please", "Yes, I need a hotel", "   ",
                    "That is all. Yes")  # changed words, case, a mix of two turns, and a blank quote
    for quote in not_verbatim:
        assert p(ev(type=(["hotel"], quote, "stated requirement")))["verbatim"]["type"] is False, quote
    # amendment R10-1: the empty string is the form of "no quote", so its verbatim flag is None, not False
    assert p(ev(type=(["hotel"], "", "stated requirement")))["verbatim"]["type"] is None
    assert p(ev(area=(["north"], "hotel in the north", "stated requirement")))["verbatim"]["area"], "white space runs"
    assert p(ev(area=(["north"], "  in the north ", "stated requirement")))["verbatim"]["area"]
    d = {"log": [{"text": "I need a room."}, {"text": "The hotel in the north has rooms."}]}
    out = forms10.parse("b_evidence", ev(type=(["hotel"], "The hotel in the north", "stated requirement")),
                        forms10.traveller_turns(d))
    assert out["verbatim"]["type"] is False, "a quote of an assistant turn is not verbatim"
    out = p(ev(type=(None, None, None), area=None, stars=("any", "any star rating", "stated requirement"),
               pricerange=(["cheap", "moderate"], "cheap", "stated requirement")))
    assert out["type"] is None and out["raw"]["type"] is None and out["verbatim"]["type"] is None
    assert out["area"] is None and out["status"]["area"] is None
    # amendment R10-1: "" and "no value" are the new forms of no quote and no status
    amended = p(ev(type=(None, "", "no value"), area=(["north"], "", "stated requirement")))
    assert amended["type"] is None and amended["status"]["type"] is None and amended["verbatim"]["type"] is None
    assert amended["area"] == ("north",) and amended["verbatim"]["area"] is None
    assert out["stars"] == "any" and out["verbatim"]["stars"] is False
    assert out["pricerange"] == ("cheap", "moderate")
    out = p(ev(name=("Example House", "Example House", "stated requirement"), type=(["Guest House"], None, None)))
    assert out["name"] == "Example House" and out["type"] is None and out["raw"]["type"] == ("guesthouse",)
    assert p("Thinking first {not json}. " + ev(type=(["hotel"], "I need a hotel", "stated requirement")) + "\n")[
        "type"] == ("hotel",), "the last top-level object, not an inner object"
    assert p("{}")["type"] is None
    for bad in (ev(type=(["hotel"], "I need a hotel", "required")), json.dumps({"type": ["hotel"]}),
                json.dumps({"type": {"value": {"x": 1}, "quote": None, "status": None}}),
                json.dumps({"type": {"value": ["hotel"], "quote": 3, "status": None}}),
                '{"name": {"value": null, "quote": null, "status": null}, "area": {"value": ["no',  # cut off
                "no object"):
        raises(ValueError, p, bad)
    raises(RuntimeError, forms10.parse, "b_evidence", ev(type=(["hotel"], "I need a hotel", "mention only")))
    raises(RuntimeError, forms10.parse, "b_evidence", ev(), "I need a hotel")


def test_traveller_turns():
    d = {"log": [{"text": "a hotel please"}, {"text": "this hotel is fine"}, {"text": "book it"}]}
    assert forms10.traveller_turns(d) == ["a hotel please", "book it"]


def test_parse_verify_and_b_verify():
    for answer in ("yes", "no", "unclear"):
        assert forms10.parse("verify", json.dumps({"answer": answer})) == {"answer": answer}
    for bad in ('{"answer": "maybe"}', '{"answer": "Yes"}', '{"reply": "yes"}', '{"answer": null}'):
        raises(ValueError, forms10.parse, "verify", bad)
    raises(RuntimeError, forms10.parse, "b_verify", '{"answer": "yes"}')
    f0 = forms10.parse("f0", reply(type=["hotel"], area=["north"]))
    before = copy.deepcopy(f0)
    assert forms10.b_verify(f0, "yes") == f0
    for answer in ("no", "unclear"):
        assert forms10.b_verify(f0, answer) == {**f0, "type": None}
    assert f0 == before, "b_verify must not change its input"
    both = forms10.parse("f0", reply(type=["hotel", "guesthouse"]))
    assert forms10.b_verify(both, "no")["type"] == ("hotel", "guesthouse") and forms10.b_verify(both, "yes")["type"] == (
        "hotel", "guesthouse")  # a list that holds both types excludes no guesthouse, so the verifier does not gate it
    for kept in (["guesthouse"], None, "any"):
        out = forms10.parse("f0", reply(type=kept))
        assert forms10.b_verify(out, "no") == out, kept
    raises(ValueError, forms10.b_verify, f0, "maybe")


def main():
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    print("forms10 test passed")


if __name__ == "__main__":
    main()
