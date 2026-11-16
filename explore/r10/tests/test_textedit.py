"""Test of r10/textedit.py (no API call). Usage: explore/.venv/bin/python -I r10/tests/test_textedit.py

It checks each rule on literals, that assistant turns do not change, and that each of the 233 dialogues holds the word
"hotel" in a traveller turn after the edit.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import textedit  # noqa: E402
from groups import anth, groups  # noqa: E402

CASES = [  # (text, edited text)
    ("I need a place to stay.", "I need a hotel."),
    ("Is the place to stay cheap?", "Is the hotel cheap?"),
    ("I need any place to stay.", "I need a hotel."),
    ("I need some place to stay.", "I need a hotel."),
    ("I need place to stay.", "I need a hotel."),
    ("a cheap place to stay", "a cheap hotel"),
    ("an expensive place to stay", "an expensive hotel"),
    ("any expensive place to stay", "an expensive hotel"),
    ("moderately priced place to stay", "a moderately priced hotel"),
    ("a 4 star place to stay", "a 4 star hotel"),
    ("Places to stay in the north", "Hotels in the north"),
    ("cheap places to stay", "cheap hotels"),
    ("some places to stay", "some hotels"),
    ("I need somewhere to stay.", "I need a hotel."),
    ("Somewhere to stay, please", "A hotel, please"),
    ("I need accommodation.", "I need a hotel."),
    ("an accommodation", "a hotel"),
    ("the accommodation", "the hotel"),
    ("what type of accommodation is this", "what type of hotel is this"),
    ("I need lodging with parking", "I need a hotel with parking"),
    ("3-star lodging", "a 3-star hotel"),
    ("some lodging", "a hotel"),
    ("booking the lodging", "booking the hotel"),
    ("about a lodging place named X", "about a hotel named X"),
    ("I need accommodations for 6", "I need hotels for 6"),
    ("inquire about lodgings", "inquire about hotels"),
    ("some lodging accommodations first", "some hotels first"),
    ("those two lodging accommodations", "those two hotels"),
    ("A PLACE TO STAY", "A HOTEL"),
    ("PLACES TO STAY", "HOTELS"),
    ("Accommodation please", "A hotel please"),
    ("a place to stay in the north", "a hotel in the north"),
    ("a place to stay in, preferably cheap", "a hotel, preferably cheap"),
    ("find a place to stay at?", "find a hotel?"),
    ("a place to stay at with parking", "a hotel with parking"),
    ("a place to stay and a restaurant", "a hotel and a restaurant"),
    ("I want a guesthouse in the east.", "I want a guesthouse in the east."),  # no phrase: no change
    ("a hotel", "a hotel"),
]


def test_rules():
    for text, want in CASES:
        got = textedit.insert_turn(text)
        assert got == want, (text, got, want)
    for text, _ in CASES:  # applying the edit again changes nothing
        once = textedit.insert_turn(text)
        assert textedit.insert_turn(once) == once, once


def test_reverse_of_zforms():
    """A turn edited by zforms.edit_turn, then by insert_turn, holds the word again."""
    for text in ("I need a hotel in the north.", "Any hotels near the centre?"):
        back = textedit.insert_turn(textedit.zforms.edit_turn(text))
        assert textedit.zforms.WORD.search(back), back


def test_assistant_turns_stay(data, g):
    """With the traveller turns blank, the edited text equals the original text: assistant turns do not change. An
    assistant turn that holds a lodging phrase is kept as it is."""
    for i in g["ins"]:
        d = {"log": [{"text": "" if k % 2 == 0 else t["text"]} for k, t in enumerate(data[i]["log"])]}
        assert textedit.inserted_text(d) == textedit.common.dialogue_text(d), i
    d = {"log": [{"text": "hi"}, {"text": "There is a place to stay and accommodation."}]}
    assert textedit.inserted_text(d) == textedit.common.dialogue_text(d)


def test_only_traveller_turns_change(data, g):
    """Each changed turn is a traveller turn, and a traveller turn without a phrase stays as it is."""
    changed = 0
    for i in g["ins"]:
        for k, t in enumerate(data[i]["log"]):
            new = textedit.insert_turn(t["text"]) if k % 2 == 0 else t["text"]
            if k % 2:
                assert new == t["text"]
            elif not textedit.has_phrase(t["text"]):
                assert new == t["text"]
            else:
                assert new != t["text"]
                changed += 1
    assert changed >= 233, changed


def test_every_dialogue_holds_the_word(data, g):
    for i in g["ins"]:
        assert not any(textedit.zforms.WORD.search(t["text"]) for k, t in enumerate(data[i]["log"]) if k % 2 == 0), i
        edited = [textedit.insert_turn(t["text"]) for k, t in enumerate(data[i]["log"]) if k % 2 == 0]
        assert any(textedit.zforms.WORD.search(t) for t in edited), i
    assert len(g["ins"]) == 233


def main():
    data = anth.multiwoz()
    g = groups(data, verbose=False)
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(*((data, g) if fn.__code__.co_argcount else ()))
            print("ok", name)
    print("textedit test passed")


if __name__ == "__main__":
    main()
