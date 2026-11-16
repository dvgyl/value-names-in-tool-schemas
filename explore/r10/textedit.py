"""Experiment I: the reverse text edit (ROUND10-EXPERIMENT-PLAN.md, experiment I; ACTION-PLAN.md section 2.5).

`insert_turn` is the reverse of `zforms.edit_turn`. It changes a lodging phrase in a traveller turn to "hotel". The rule:

1. "place to stay" with an article: "a place to stay" becomes "a hotel", "the place to stay" becomes "the hotel".
   "any" and "some" become "a". A word of a small list before the noun ("cheap", "4 star", "moderately priced") stays.
   Without an article, a or an is put before the phrase.
2. "places to stay" becomes "hotels".
3. "somewhere to stay" becomes "a hotel".
4. "accommodation", "lodging" and "lodging place" follow rule 1. After "type of", "kind of" or "sort of" they become "hotel".
5. "accommodations", "lodgings" and "lodging accommodations" become "hotels". The word before them stays.
6. "in" or "at" after "place to stay" or "somewhere to stay" is dropped when no noun follows it (before a comma, a
   full stop, a question mark, the end of the turn, or "with").
7. Case follows `zforms._place_to_stay`: an upper-case phrase stays upper case, a phrase that starts with a capital letter
   starts with a capital letter.
Assistant turns do not change.
"""
import pathlib
import re
import sys

EXPLORE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPLORE / "r9" / "additions"))
import zforms  # noqa: E402
from zforms import common  # noqa: E402

# A word that can stand between the article and the noun. The list holds each such word of the 256 dialogues.
ADJ = r"(?:\d+(?:\s|-)star|cheap|expensive|good|great|nice|moderate(?:ly)?(?:[ -]priced?)?)"
KEEP = r"(?:the|my|your|our|his|her|their|this|that)"
CHANGE = r"(?:an?|any|some)"
# "in" or "at" with no noun after it ("a place to stay in, preferably ..."): the edit drops it, because "a hotel in," is
# not grammatical.
STRANDED = r"(?:\s+(?:in|at)(?=\s*(?:[,.?!;]|$)|\s+with\b))?"
PATTERN = re.compile(
    rf"\b(?P<plural>places to stay|(?:lodging\s+)?accommodations|lodgings)\b"
    rf"|\b(?P<somewhere>somewhere to stay){STRANDED}"
    rf"|\b(?:(?P<keep>{KEEP})\s+|(?P<change>{CHANGE})\s+)?(?P<adj>(?:{ADJ}\s+)*)"
    rf"(?:place to stay{STRANDED}|(?:lodging\s+)?accommodation\b|lodging\s+place\b|lodging\b(?!\s+accommodations?\b))", re.I)
KIND_OF = re.compile(r"\b(?:type|kind|sort)s?\s+of\s+$", re.I)
VOWEL = re.compile(r"[aeiou]", re.I)  # matches at the start of the text only


def _case(source, new):
    """The case rule of zforms._place_to_stay, applied to the whole phrase."""
    if source.isupper():
        return new.upper()
    return new[0].upper() + new[1:] if source[0].isupper() else new


def _replace(m):
    if m.group("plural"):
        return _case(m.group(0), "hotels")
    if m.group("somewhere"):
        return _case(m.group(0), "a hotel")
    adj = m.group("adj") or ""
    if m.group("keep"):
        new = f"{m.group('keep').lower()} {adj}hotel"
    elif KIND_OF.search(m.string[:m.start()]) and not m.group("change"):
        new = f"{adj}hotel"
    else:
        new = f"{'an' if VOWEL.match(adj or 'hotel') else 'a'} {adj}hotel"
    return _case(m.group(0), new)


def insert_turn(text):
    """The traveller turn with each lodging phrase changed to "hotel" or "hotels"."""
    return PATTERN.sub(_replace, text)


def has_phrase(text):
    return PATTERN.search(text) is not None


def inserted_text(d):
    """The dialogue text with every traveller turn edited by insert_turn. Assistant turns stay as they are."""
    return common.dialogue_text({"log": [{"text": insert_turn(t["text"]) if i % 2 == 0 else t["text"]}
                                         for i, t in enumerate(d["log"])]})
