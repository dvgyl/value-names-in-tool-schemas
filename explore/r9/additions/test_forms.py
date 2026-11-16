"""Form and text-edit test of zforms (no API call, no MultiWOZ dialogue). Usage: python3 -I r9/additions/test_forms.py

Each form must equal F0 after its intended change is undone. The intended changes are written here as literals, so a
change to zforms that is not in this list fails.
"""
import copy
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zforms  # noqa: E402
from zforms import common, e13, templates  # noqa: E402

sys.path.insert(0, str(zforms.EXPLORE / "trackc"))
import e14  # noqa: E402

UNCLEAR = (" If the traveller's words allow more than one reasonable reading for a field, write \"unclear\" for that "
           "field instead of choosing a reading.")
NULL = UNCLEAR.replace('write "unclear"', "write null")
INTENDED = {  # (text in F0, text in the form)
    "p_define": [("", " `hotel` means the database category hotel, not the traveller's general word for a place to "
                      "stay.")],
    "p_null_nat": [("", NULL)],
    "p_unclear_nat": [("", UNCLEAR)],
    "p_split": [(", stars, type, parking,", ", stars, type_required, type_preferred, parking,"),
                ("type: guesthouse, hotel.", "type_required: guesthouse, hotel. type_preferred: guesthouse, hotel."),
                ("", " type_required filters the search, so give it only the types that the traveller requires. "
                     "type_preferred only changes the order of the results, so give it the types that the traveller "
                     "prefers but does not require.")],
}


def undo(text, changes):
    for old, new in changes:
        assert text.count(new) == 1, (new, text.count(new))
        text = text.replace(new, old)
    return text


def test_base_forms():
    assert zforms.FORMS["f0"] == (common.FORMS["p_main"].system, e13.schema(False)["schema"]), "F0 is not E13 p_main"
    assert zforms.FORMS["f1"] == (common.FORMS["p_main_renamed"].system, e13.schema(True)["schema"]), "F1 is not E13"


def test_each_form_changes_only_its_text():
    f0 = zforms.FORMS["f0"].system
    for name, changes in INTENDED.items():
        system = zforms.FORMS[name].system
        assert system != f0 and undo(system, changes) == f0, f"{name}: not F0 plus only its intended text"
    for name in ("p_null_nat", "p_unclear_nat"):  # the E14 place: right after the "changed their mind" sentence
        assert "give the final requirement. If the traveller's words allow" in zforms.FORMS[name].system, name
    assert templates.FORMS["p_unclear"] == templates.P_MAIN.replace(templates.CHANGED, templates.CHANGED + UNCLEAR)
    assert templates.FORMS["p_null"] == templates.P_MAIN.replace(templates.CHANGED, templates.CHANGED + NULL)


def test_schemas():
    f0 = zforms.FORMS["f0"].schema
    assert zforms.FORMS["p_define"].schema == f0 and zforms.FORMS["p_null_nat"].schema == f0
    assert zforms.FORMS["p_unclear_nat"].schema == e14.schema("p_unclear")["schema"], "not the E14 unclear schema"
    unclear = copy.deepcopy(f0)
    for key, prop in unclear["properties"].items():
        if key != "name":
            prop["anyOf"][1]["enum"].append("unclear")
    assert zforms.FORMS["p_unclear_nat"].schema == unclear, "p_unclear_nat differs from F0 by more than the option"
    split = zforms.FORMS["p_split"].schema
    keys = ["name", "area", "pricerange", "stars", "type_required", "type_preferred", "parking", "internet"]
    assert list(split["properties"]) == keys and split["required"] == keys and not split["additionalProperties"]
    assert split["properties"]["type_required"] == split["properties"]["type_preferred"] == f0["properties"]["type"]
    assert {k: v for k, v in split["properties"].items() if not k.startswith("type")} == {
        k: v for k, v in f0["properties"].items() if k != "type"}


def test_frame_and_probe():
    for name in ("f0", "f1"):
        system = zforms.FORMS[name].system
        framed = zforms.framed(system)
        assert framed.replace("accommodation booking assistant", "hotel booking assistant") == system != framed
        assert "requirements for the hotel" in framed, "the frame edit changes only the assistant noun phrase"
    assert zforms.FORMS["probe"].system == (
        "You read a conversation between a traveller and a hotel booking assistant in Cambridge. Does the traveller's "
        "wording fix the venue type to hotel? Answer fixes, does not fix, or cannot tell.")
    assert zforms.FORMS["probe"].schema["properties"]["answer"]["enum"] == ["fixes", "does not fix", "cannot tell"]


def test_parse_maps_back_to_f0_fields():
    blank = {"name": None, "area": None, "pricerange": None, "stars": None, "parking": None, "internet": None}
    reply = lambda **kw: str({**blank, **kw}).replace("None", "null").replace("'", '"')
    assert zforms.parse("f1", reply(property_kind=["large_property"]))["type"] == ("hotel",)
    out = zforms.parse("p_split", reply(type_required=None, type_preferred=["hotel"]))
    assert out["type"] is None and out["type_preferred"] == ("hotel",), "only type_required may filter"
    out = zforms.parse("p_split", reply(type_required=["guesthouse"], type_preferred=["hotel", "guesthouse"]))
    assert out["type"] == ("guesthouse",) and out["type_preferred"] == ("hotel", "guesthouse")
    assert zforms.parse("p_unclear_nat", reply(type="unclear"))["type"] == "unclear"
    assert zforms.parse("probe", '{"answer": "does not fix"}') == {"answer": "does not fix"}
    try:
        zforms.parse("probe", '{"answer": "maybe"}')
        raise AssertionError("a probe answer outside the three values must fail")
    except ValueError:
        pass


def test_edit_keeps_all_33_venue_names():
    assert len(zforms.HOTELS) == 33
    for name in (h["name"] for h in zforms.HOTELS):
        for shown in (name, name.title(), name.upper()):
            assert zforms.edit_turn(f"I want to book {shown} please.") == f"I want to book {shown} please.", shown
            assert zforms.edit_turn(f"Is {shown} a hotel?") == f"Is {shown} a place to stay?", shown
    for kept in ("the Marriott hotel", "Lensfield Hotel", "the ashley hotel", "University Arms hotels",
                 "the Huntington Marriot Hotel"):
        assert zforms.edit_turn(kept) == kept, kept


def test_edit_changes_only_the_word():
    cases = {"I need a hotel.": "I need a place to stay.", "Hotels in the north?": "Places to stay in the north?",
             "A HOTEL, please": "A PLACE TO STAY, please", "the hotel's address": "the place to stay's address",
             "a hotelier and hotel-type": "a hotelier and place to stay-type",
             "the Autumn House hotel": "the Autumn House place to stay", "no change here": "no change here"}
    for before, after in cases.items():
        assert zforms.edit_turn(before) == after, (before, zforms.edit_turn(before))
    d = {"log": [{"text": "a hotel please"}, {"text": "this hotel is fine"}, {"text": "book the Gonville hotel"}]}
    assert zforms.edited_text(d) == ("Traveller: a place to stay please\nAssistant: this hotel is fine\n"
                                     "Traveller: book the Gonville hotel"), "assistant turns must stay as they are"


def test_prefix():
    d = {"log": [{"text": "a room please"}, {"text": "which hotel?"}, {"text": "any hotel"}, {"text": "ok"},
                 {"text": "a hotel"}]}
    assert zforms.prefix_text(d) == "Traveller: a room please\nAssistant: which hotel?\nTraveller: any hotel"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    print("zforms test passed")
