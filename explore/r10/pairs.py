"""Experiment H: constructed word and schema pairs (ROUND10-EXPERIMENT-PLAN.md H, ACTION-PLAN.md 2.7).

A pair is a service with a `type` slot of 3 values. One value, the collision value, is also the everyday noun for the
whole service, as "hotel" is for a place to stay. `CANDIDATES` holds the 20 candidates in the fixed order of the plan.
`HOTEL` is the calibration pair. `check_pair` applies the two mechanical checks. `RULE_D_EXCLUDED` holds the
candidates that the template review of 2026-11-12 found outside the pair rule. `chosen` takes, in plan order, the
candidates that pass both checks and are not excluded, at most 16, and writes `pairs.json` one time. No model output
can change the list. Version 1 of the list (16 pairs, no exclusion) is in `pairs.v1.json`.

Each pair has 20 scenarios. A seeded draw (seed `SEED`) sets the place, the price, the size and the day of each
scenario from fixed lists. A pair can change a list (for example the language in place of the area, or Monday to
Friday only). Each scenario has 4 item kinds:
- `unclear_word`: the traveller uses the collision word in the general sense ("I need a table for two on Friday").
- `unclear_para`: the same text with a paraphrase that holds no value word ("somewhere to sit").
- `clear_specific`: `unclear_word` plus a sentence that excludes the two other values.
- `clear_general`: `unclear_word` plus a sentence that accepts every value.

`form(pair, neutral)` gives G0 (the original values) or G4 (a neutral token in place of the collision value). The
system text is `zforms.F0` with these parts changed: the assistant phrase ("a hotel booking assistant"), the role
word ("traveller"), the service noun in "requirements for the hotel", the field list (the name field and its sentence
are removed), and the allowed values. The schema is closed, as `zforms.schema`.

`requests_spec()` gives every request of one read in a form that has no provider wrapper. `NEW_TEXTS` holds every
constructed text (the system texts and the user texts of all 21 pairs) for `groups.assert_new_text`.

Usage: python3 -I r10/pairs.py choose   (writes pairs.json one time; a rerun checks that it is unchanged)
       python3 -I r10/pairs.py review   (prints the review text of pairs_review.md)
"""
import functools
import hashlib
import itertools
import json
import pathlib
import random
import re
import sys
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for _sub in ("lib", "forms", "pmain", "trackc", "r9/additions"):
    sys.path.insert(0, str(EXPLORE / _sub))
import anth  # noqa: E402
import common  # noqa: E402
import e13  # noqa: E402
import zforms  # noqa: E402

PAIRS_JSON = HERE / "pairs.json"
SEED = 20261112
N_PAIRS, MIN_PAIRS, N_SCENARIOS = 16, 12, 20
KINDS = ("unclear_word", "unclear_para", "clear_specific", "clear_general")
FORMS = ("g0", "g4")
RULE = ("the candidates in the order of ROUND10-EXPERIMENT-PLAN.md H that pass checks 1 and 2 and are not in "
        "RULE_D_EXCLUDED, at most 16; if fewer than 12 remain, H does not run")
# Check 3 (judgement, from the template review of 2026-11-12): the collision word is not the everyday word for all
# three values, so the pair breaks the pair rule. The operator approves this list before any call.
RULE_D_EXCLUDED = {
    "gym": "a pool or a yoga studio is not \"a gym\"",
    "apartment": "\"an apartment\" excludes \"a house\", and a studio is a kind of apartment",
    "office": "\"office\" is not the everyday word for a job; the frame and the days are also unnatural",
    "movie": "a movie does not include a series",
    "truck": "in a British setting \"van\" is the general word, and a trailer is not a vehicle",
    "call": "a call does not include a message",
    "box": "weak by the same rule: \"a box\" does not include an envelope or a tube",
    "flowers": "weak by the same rule: \"flowers\" does not include a plant or a wreath",
}
# Changes to a value of the plan's candidate list, from the template reviews. The operator approves them with the list.
VALUE_CHANGES = {"boat": ("ferry", "punt", "a ferry is not hired by the hour and cannot be taken out; review of 2026-11-12")}
# The size and quality words of the round-9 F4 token rule (a copy of test_natural.SIZE_OR_QUALITY; the test checks it).
SIZE_OR_QUALITY = {"large", "small", "big", "little", "tiny", "huge", "grand", "mini", "major", "minor", "luxury",
                   "luxurious", "premium", "budget", "cheap", "expensive", "deluxe", "superior", "basic", "fancy", "posh",
                   "upscale", "boutique", "quality", "standard", "economy", "elite", "best", "top", "fine", "high", "low"}


class Dim(NamedTuple):
    field: str  # the schema field
    values: tuple  # its allowed values
    phrases: tuple  # the traveller's words for each value


class Pair(NamedTuple):
    collision: str  # the value that is also the everyday noun for the service; also the pair key
    others: tuple  # the two other values
    service: str  # the noun of "requirements for the {service}" ("hotel" in F0)
    neutral: str  # the G4 token for the collision value
    nouns: tuple  # noun phrases of (collision, *others) for the clear sentences
    word: str  # the thing that the traveller asks for, with the collision word
    para: str  # the same thing with no value word
    request: str  # first sentence: {thing}, {size}, {day}
    constraint: str  # second sentence: {price}, {place}
    size: Dim
    price: Dim = None  # None: PRICES
    place: Dim = None  # None: AREAS
    days: Dim = None  # None: DAYS
    assistant: str = None  # the assistant phrase without its article; None: "<service> booking assistant"
    role: str = "traveller"  # the role word of the frame


# The fixed lists of the scenarios.
AREAS = Dim("area", ("centre", "north", "south", "east", "west"), ("centre", "north", "south", "east", "west"))
PRICES = Dim("pricerange", ("cheap", "moderate", "expensive"), ("cheap", "moderately priced", "expensive"))
# One wording per price level; a constraint starts with it: "{price}, and ...".
LEVELS = Dim("price", ("low", "moderate", "high"), ("It should be cheap", "A moderate price is fine",
                                                    "I am happy to pay a lot"))
DAYS = Dim("day", ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"),
           ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))
WEEKDAYS = Dim("day", DAYS.values[:5], DAYS.phrases[:5])
NUMBERS = ("one", "two", "three", "four", "five", "six")


def people(lo, hi, bare=False):
    """The `people` field from lo to hi: "four" (bare) or "four people"."""
    nums = range(lo, hi + 1)
    phrase = lambda k: NUMBERS[k - 1] if bare else "one person" if k == 1 else f"{NUMBERS[k - 1]} people"
    return Dim("people", tuple(map(str, nums)), tuple(map(phrase, nums)))


def counted(field, lo, hi, one, many):
    """A count field: "one day", "two days"."""
    nums = range(lo, hi + 1)
    return Dim(field, tuple(map(str, nums)), tuple(f"{NUMBERS[k - 1]} {one if k == 1 else many}" for k in nums))


PLACE = "The place should be {price} and in the {place}."
HIRE = "The hire should be {price}, with pick-up in the {place}."  # excluded candidates only
PICKUP = "{price}, and the pick-up should be in the {place}."
CANDIDATES = (
    Pair("table", ("booth", "bar seat"), "table", "open_floor", ("a table", "a booth", "a bar seat"),
         "a table", "somewhere to sit", "I need {thing} for {size} on {day}.",
         "The restaurant should be {price} and in the {place}.", people(1, 2, bare=True)),
    Pair("room", ("suite", "apartment"), "room", "lodging_unit", ("a room", "a suite", "an apartment"),
         "a room", "somewhere to sleep", "I need {thing} for {size} from {day}.", PLACE, people(1, 3)),
    Pair("restaurant", ("cafe", "pub"), "restaurant", "dining_venue", ("a restaurant", "a cafe", "a pub"),
         "a restaurant", "somewhere to eat", "I am looking for {thing} for {size} on {day}.", PLACE,
         people(2, 6, bare=True)),
    Pair("car", ("van", "minibus"), "car", "private_vehicle", ("a car", "a van", "a minibus"),
         "a car", "something to drive", "I need {thing} for {size} from {day}.", PICKUP,
         counted("days", 1, 4, "day", "days"), LEVELS),
    Pair("taxi", ("minibus", "limousine"), "taxi", "metered_vehicle", ("a taxi", "a minibus", "a limousine"),
         "a taxi", "a ride", "I need {thing} for {size} on {day}.",
         "{price}, and the pick-up is in the {place}.", people(2, 4), LEVELS),
    Pair("doctor", ("nurse practitioner", "pharmacist"), "doctor", "licensed_physician",
         ("a doctor", "a nurse practitioner", "a pharmacist"), "a doctor", "someone",
         "I need to see {thing} about a sore throat on {day}, {size}.",
         "I would like to go in the {price}, somewhere in the {place}.",
         Dim("people", ("1", "2", "3"), ("just for me", "for me and my son", "for me and my two sons")),
         Dim("time", ("morning", "afternoon", "evening"), ("morning", "afternoon", "evening")),
         days=WEEKDAYS, assistant="doctor appointment assistant"),
    Pair("gym", ("pool", "yoga studio"), "gym", "fitness_floor", ("a gym", "a pool", "a yoga studio"),
         "a gym", "somewhere to exercise", "I am looking for {thing} for {size} on {day}.", PLACE, people(1, 3)),
    Pair("school", ("college", "academy"), "school", "education_provider", ("a school", "a college", "an academy"),
         "a school that teaches English", "somewhere that teaches English",
         "I am looking for {thing} for {size}, starting on {day}.",
         "{price}, and the lessons should be in the {place}.", people(1, 3),
         LEVELS._replace(field="fees"), days=WEEKDAYS, assistant="school enrolment assistant"),
    Pair("bike", ("e-bike", "scooter"), "bike", "pedal_cycle", ("a bike", "an e-bike", "a scooter"),
         "a bike", "something to ride", "I need {thing} for {size} from {day}.", PICKUP,
         counted("days", 1, 4, "day", "days"), LEVELS),
    Pair("apartment", ("house", "studio"), "apartment", "building_unit", ("an apartment", "a house", "a studio"),
         "an apartment", "somewhere to live", "I need {thing} for {size} from {day}.",
         "The rent should be {price}, and the place should be in the {place}.", people(1, 2)),
    Pair("office", ("remote", "hybrid"), "job", "premises_based", ("an office job", "a remote job", "a hybrid job"),
         "an office job", "a desk job", "I am looking for {thing} in accounting, {size}, starting on {day}.",
         "The salary should be {price}, and the company should be in the {place}.",
         Dim("hours", ("20", "30", "40"), ("20 hours a week", "30 hours a week", "40 hours a week")),
         Dim("salary", ("low", "moderate", "high"),
             ("around 25,000 pounds a year", "around 35,000 pounds a year", "around 45,000 pounds a year"))),
    Pair("movie", ("documentary", "series"), "movie", "feature_length", ("a movie", "a documentary", "a series"),
         "a movie", "something", "I want {thing} to watch with {size} on {day}.",
         "The screening room should be {price} and in the {place}.",
         Dim("people", ("2", "3", "4", "5"), ("one friend", "two friends", "three friends", "four friends"))),
    Pair("boat", ("punt", "kayak"), "boat", "private_vessel", ("a boat", "a punt", "a kayak"),
         "a boat", "something to take out on the water", "I need {thing} for {size} on {day}.",
         "{price}, and I want to leave from the {place}.",
         counted("hours", 1, 4, "hour", "hours"), LEVELS),
    Pair("truck", ("van", "trailer"), "truck", "cargo_vehicle", ("a truck", "a van", "a trailer"),
         "a truck", "something", "I need {thing} on {day} to move the furniture from my {size} flat.", HIRE,
         Dim("bedrooms", ("1", "2", "3"), ("one-bedroom", "two-bedroom", "three-bedroom"))),
    Pair("letter", ("email", "fax"), "letter", "postal_item", ("a letter", "an email", "a fax"),
         "a letter", "something in writing", "I need to send {thing} to {size} by {day}.",
         "{price}, and the language should be {place}.",
         counted("recipients", 1, 3, "person", "people"), LEVELS,
         Dim("language", ("english", "french", "german", "spanish", "italian"),
             ("English", "French", "German", "Spanish", "Italian")),
         WEEKDAYS, "letter sending assistant", "customer"),
    Pair("call", ("video call", "message"), "call", "voice_session", ("a call", "a video call", "a message"),
         "a call", "some contact", "I need {thing} with a local guide on {day}, for {size}.",
         "The guide should be {price} and based in the {place}.", people(1, 3)),
    Pair("coffee", ("tea", "hot chocolate"), "coffee", "bean_brew", ("coffee", "tea", "hot chocolate"),
         "coffee", "something warm to drink", "I want to arrange {thing} for a meeting of {size} on {day} morning.",
         "{price}, and the meeting is in the {place}.", people(2, 6), LEVELS,
         assistant="coffee ordering assistant"),
    Pair("camera", ("camcorder", "webcam"), "camera", "photo_device", ("a camera", "a camcorder", "a webcam"),
         "a camera", "something to take pictures or video with", "I want to hire {thing} for {size} from {day}.",
         PICKUP, counted("days", 1, 4, "day", "days"), LEVELS, assistant="camera hire assistant"),
    Pair("box", ("envelope", "tube"), "box", "rigid_container", ("a box", "an envelope", "a tube"),
         "a box", "some packaging", "I need {thing} to post {size} on {day}.",
         "The postage should be {price}, and I will drop the parcel off in the {place}.",
         counted("items", 1, 4, "print", "prints")),
    Pair("flowers", ("plant", "wreath"), "flowers", "cut_stems", ("flowers", "a plant", "a wreath"),
         "flowers", "something from the florist", "I want to send {thing} to {size} on {day}.",
         "The order should be {price}, from a shop in the {place}.", counted("recipients", 1, 3, "friend", "friends")),
)
# The calibration pair: the round-9 word, the F4 token, and the Z1 paraphrase ("place to stay"). Unchanged from v1.
HOTEL = Pair("hotel", ("guesthouse", "hostel"), "hotel", "serviced_property", ("a hotel", "a guesthouse", "a hostel"),
             "a hotel", "a place to stay", "I need {thing} for {size} from {day}.", PLACE, people(1, 3))
SPECIFIC = "It has to be {0}, not {1} or {2}."
GENERAL = "{0}, {1} or {2} would all be fine."

# The system text frame: zforms.F0 with the assistant phrase, the role word, the service noun, the field list and the
# allowed values changed.
F0_ASSISTANT = "a hotel booking assistant"
F0_FIELDS = "Fields: name, " + ", ".join(common.FIELDS) + "."
F0_NAME = "Give name as the hotel name if the traveller asked for one hotel by name, else null."
F0_ALLOWED = "Allowed values: " + " ".join(f"{f}: {', '.join(v)}." for f, v in e13.VALUES.items())
F0_ROLE_COUNT = 8  # "traveller" in F0 after the name sentence is removed
_frame = zforms.once(zforms.once(zforms.once(zforms.once(
    zforms.F0, f"and {F0_ASSISTANT} in", "and {a_assistant} in"),
    "requirements for the hotel as", "requirements for the {service} as"),
    f"{F0_FIELDS} {F0_NAME}", "Fields: {fields}."),
    F0_ALLOWED, "Allowed values: {allowed}")
assert _frame.count("traveller") == F0_ROLE_COUNT, _frame.count("traveller")
FRAME = _frame.replace("traveller", "{role}")


def _pair(pair):
    return pair if isinstance(pair, Pair) else {p.collision: p for p in CANDIDATES + (HOTEL,)}[pair]


def dims(pair):
    """The scenario fields of the pair in the order of the field list: place, price, size, then `type`, then day."""
    pair = _pair(pair)
    return pair.place or AREAS, pair.price or PRICES, pair.size, pair.days or DAYS


def type_values(pair, neutral=False):
    pair = _pair(pair)
    return pair.others + (pair.neutral if neutral else pair.collision,)


def article(noun):
    return ("an " if noun[0] in "aeiou" else "a ") + noun


def fields(pair, neutral=False):
    place, price, size, day = dims(pair)
    return [(place.field, place.values), (price.field, price.values), (size.field, size.values),
            ("type", type_values(pair, neutral)), (day.field, day.values)]


def system(pair, neutral=False):
    pair = _pair(pair)
    shown = fields(pair, neutral)
    return FRAME.format(a_assistant=article(pair.assistant or f"{pair.service} booking assistant"), role=pair.role,
                        service=pair.service, fields=", ".join(f for f, _ in shown),
                        allowed=" ".join(f"{f}: {', '.join(v)}." for f, v in shown))


def schema(pair, neutral=False):
    """The closed schema of zforms.schema: each field is null, "any", or a list of its allowed values."""
    props = {f: {"anyOf": [{"type": "null"}, {"type": "string", "enum": ["any"]},
                           {"type": "array", "items": {"type": "string", "enum": list(v)}}]}
             for f, v in fields(_pair(pair), neutral)}
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def form(pair, neutral: bool):
    """G0 (neutral False) or G4 (neutral True) as a zforms.Form(system, schema)."""
    return zforms.Form(system(pair, neutral), schema(pair, neutral))


class Item(NamedTuple):
    unit: str  # <pair>_<scenario>_<kind>; it has no "-", so a custom_id keeps its "-" separated parts
    pair: str
    scenario: int
    kind: str
    text: str  # the traveller turn
    user: str  # the user message: the turn as a one-turn conversation (common.dialogue_text, with the role word)
    values: dict  # scenario field -> value


def scenarios(pair, seed=None):
    """N_SCENARIOS distinct (place, price, size, day) index tuples, drawn with a seed from SEED and the pair key."""
    pair = _pair(pair)
    seed = SEED if seed is None else seed
    rng = random.Random(int(hashlib.sha256(f"{seed}:{pair.collision}".encode()).hexdigest()[:16], 16))
    return rng.sample(list(itertools.product(*(range(len(d.values)) for d in dims(pair)))), N_SCENARIOS)


def items(pair, seed=None):
    """N_SCENARIOS x 4 items, in scenario order and then in the order of KINDS."""
    pair = _pair(pair)
    place, price, size, day = dims(pair)
    general = GENERAL.format(*pair.nouns)
    out = []
    for s, (a, p, z, d) in enumerate(scenarios(pair, seed)):
        def base(thing):
            first = pair.request.format(thing=thing, size=size.phrases[z], day=day.phrases[d])
            return first + " " + pair.constraint.format(price=price.phrases[p], place=place.phrases[a])
        word = base(pair.word)
        texts = {"unclear_word": word, "unclear_para": base(pair.para),
                 "clear_specific": word + " " + SPECIFIC.format(*pair.nouns),
                 "clear_general": word + " " + general[0].upper() + general[1:]}
        values = {place.field: place.values[a], price.field: price.values[p], size.field: size.values[z],
                  day.field: day.values[d]}
        for kind in KINDS:
            user = common.dialogue_text({"log": [{"text": texts[kind]}]})
            user = zforms.once(user, "Traveller: ", pair.role.capitalize() + ": ")  # the role word of the frame
            out.append(Item(f"{pair.collision}_{s:02d}_{kind}", pair.collision, s, kind, texts[kind], user, values))
    return out


# The two mechanical checks.
def value_words(pair):
    """Every word of every value of the pair: "bar seat" gives "bar" and "seat"."""
    pair = _pair(pair)
    return sorted({w for v in (pair.collision,) + pair.others for w in v.split()})


def word_pattern(word):
    """The word with an optional plural; for a word that ends in "s", also the form without it."""
    forms = [re.escape(word) + "(?:s|es)?"] + ([re.escape(word[:-1])] if word.endswith("s") else [])
    return re.compile(r"\b(?:" + "|".join(forms) + r")\b", re.I)


@functools.lru_cache(maxsize=1)
def training_turns():
    """The traveller turns of the MultiWOZ training split (no validation or test dialogue), as in test_natural."""
    data, (val, test) = anth.multiwoz(), anth.splits()
    return tuple(t["text"] for k, d in data.items() if k not in val | test for i, t in enumerate(d["log"]) if i % 2 == 0)


def token_failures(pair):
    """Check 1, the round-9 F4 token rule: the token is in no traveller turn of the training split, it holds no value
    word of the pair (round 9: no "hotel"), and no part of it is a size or quality word."""
    pair = _pair(pair)
    tok, out = pair.neutral, []
    phrase = re.compile(r"\b" + tok.replace("_", "[ _-]?") + r"s?\b", re.I)
    n = sum(1 for t in training_turns() if phrase.search(t))
    if n:
        out.append(f"check 1: the neutral token {tok!r} is in {n} traveller turns of the MultiWOZ training split")
    held = [w for w in value_words(pair) if w.lower() in tok.lower()]
    if held:
        out.append(f"check 1: the neutral token {tok!r} holds the value word(s) {held}")
    quality = sorted(set(tok.lower().split("_")) & SIZE_OR_QUALITY)
    if quality:
        out.append(f"check 1: the neutral token {tok!r} holds the size or quality word(s) {quality}")
    return out


def para_failures(pair):
    """Check 2: no part of the paraphrase template and no unclear_para item holds a value word of the pair."""
    pair = _pair(pair)
    parts = [pair.para, re.sub(r"\{\w+\}", " ", pair.request), re.sub(r"\{\w+\}", " ", pair.constraint)]
    parts += [ph for d in dims(pair) for ph in d.phrases]
    parts += [it.text for it in items(pair) if it.kind == "unclear_para"]
    out = []
    for w in value_words(pair):
        hits = [t for t in parts if word_pattern(w).search(t)]
        if hits:
            out.append(f"check 2: the paraphrase text holds the value word {w!r} ({len(hits)} texts, first {hits[0]!r})")
    return out


def check_pair(pair) -> list:
    """The failed mechanical checks of the pair (an empty list if both checks pass)."""
    return token_failures(pair) + para_failures(pair)


# The choice, the requests, and the constructed texts.
def pair_json(pair):
    d = pair._asdict()
    d.update(price=d["price"] or PRICES, place=d["place"] or AREAS, days=d["days"] or DAYS,
             assistant=d["assistant"] or f"{pair.service} booking assistant")
    return json.loads(json.dumps({k: (v._asdict() if isinstance(v, Dim) else v) for k, v in d.items()}))


def spec(pairs):
    """The requests of one read: each pair, item and form; HOTEL gets the cell tags cal_g0 and cal_g4."""
    out = []
    for pair in pairs:
        cal = pair.collision == HOTEL.collision
        forms = {tag: form(pair, tag == "g4") for tag in FORMS}
        for it in items(pair):
            for tag in FORMS:
                out.append({"stem": f"{it.unit}-{tag}", "unit": it.unit, "form": tag, "cell": ("cal_" if cal else "") + tag,
                            "pair": pair.collision, "kind": it.kind, "scenario": it.scenario,
                            "system": forms[tag].system, "user": it.user, "schema": forms[tag].schema})
    return out


def sha256(requests):
    return hashlib.sha256(json.dumps(requests, sort_keys=True).encode()).hexdigest()


def choice():
    """The content of pairs.json. It raises RuntimeError under the stop rule (fewer than MIN_PAIRS remain)."""
    checked = [(p, check_pair(p)) for p in CANDIDATES]
    picked = [p for p, failed in checked if not failed and p.collision not in RULE_D_EXCLUDED][:N_PAIRS]
    if len(picked) < MIN_PAIRS:
        raise RuntimeError(f"stop rule: only {len(picked)} of the 20 candidates remain; H does not run")
    reqs = spec(picked)
    cal = spec([HOTEL])
    return json.loads(json.dumps({
        "seed": SEED, "rule": RULE,
        "checked": [{"pair": p.collision, "failed": failed, "excluded": RULE_D_EXCLUDED.get(p.collision)}
                    for p, failed in checked],
        "chosen": [p.collision for p in picked],
        "value_changes": {k: v for k, v in VALUE_CHANGES.items() if k in {p.collision for p in picked}},
        "calibration": {"pair": HOTEL.collision, "failed": check_pair(HOTEL)},
        "pairs": {p.collision: pair_json(p) for p in picked + [HOTEL]},
        "requests_per_read": len(reqs), "calibration_requests_per_read": len(cal),
        "requests_sha256": sha256(reqs + cal)}))


def chosen(path=PAIRS_JSON):
    """The chosen pairs. The first call writes pairs.json; each later call checks that the rule gives the same file."""
    content = choice()
    if path.exists():
        if json.loads(path.read_text()) != content:
            raise ValueError(f"{path} differs from the rule; the list is fixed before any call")
    else:
        path.write_text(json.dumps(content, indent=1) + "\n")
    return [_pair(k) for k in content["chosen"]]


def requests_spec(path=PAIRS_JSON):
    """Every request of one read: n pairs x 20 scenarios x 4 kinds x 2 forms (1,920 for 12 pairs), then the 160 of
    HOTEL."""
    return spec(chosen(path) + [HOTEL])


NEW_TEXTS = tuple(dict.fromkeys([system(p, n) for p in CANDIDATES + (HOTEL,) for n in (False, True)]
                                + [t for p in CANDIDATES + (HOTEL,) for it in items(p) for t in (it.user, it.text)]))


def review_markdown(path=PAIRS_JSON):
    """The text of pairs_review.md: pairs.json, the checks, the frame, and 2 example items per pair and kind."""
    content = json.loads(path.read_text())
    n = len(content["chosen"])
    lines = ["# Experiment H: the word and schema pairs for review (version 3)", "",
             "Status: **a proposal for the operator's approval. No call has run.** "
             "`python3 -I r10/pairs.py review` writes this text from `r10/pairs.py` and `r10/pairs.json`. Version 1 "
             "(16 pairs, before the template review) is in `pairs.v1.json` and `pairs_review.v1.md`. Version 2 (before "
             "the second review) is in `pairs.v2.json` and `pairs_review.v2.md`.", "",
             "## 1. The steps for the reviewers", "",
             f"1. Operator: read sections 2 and 3. Approve the change from 16 to {n} pairs (check 3), or reject it, "
             "before any H call.",
             "2. Template reviewer: read section 5. For each item, write down if the stated reading (unclear, "
             "specific, general) is not the only reasonable reading.",
             "3. Correct a template, not a single item. A template change changes `requests_sha256`, so "
             "`pairs.chosen()` then stops. Rename `pairs.json` and write it again only before the approval.", "",
             "## 2. The chosen pairs", "",
             "Value changes against the plan's candidate list (the operator approves them with the list): "
             + "; ".join(f"`{k}`: `{a}` becomes `{b}` ({why})" for k, (a, b, why) in content["value_changes"].items())
             + ".", "",
             f"Rule: {content['rule']}. Seed of the scenario draw: {content['seed']}.", "",
             "| # | Collision value | Other values | Assistant phrase | Role | G4 token |", "|---|---|---|---|---|---|"]
    for i, key in enumerate(content["chosen"] + [content["calibration"]["pair"]], 1):
        p = content["pairs"][key]
        label = "calibration" if key == content["calibration"]["pair"] else str(i)
        lines.append(f"| {label} | `{key}` | `{p['others'][0]}`, `{p['others'][1]}` | {p['assistant']} | {p['role']} | "
                     f"`{p['neutral']}` |")
    lines += ["", f"Requests per read: {content['requests_per_read']:,} for the chosen pairs, plus "
              f"{content['calibration_requests_per_read']} for the calibration pair (cell tags `cal_g0`, `cal_g4`). "
              f"SHA-256 of all requests: `{content['requests_sha256']}`.", "",
              "## 3. The checks of each candidate", "",
              "Check 1: the G4 token is in no traveller turn of the MultiWOZ training split, it holds no value word of "
              "the pair, and no part of it is a size or quality word (the round-9 F4 rule). Check 2: no "
              "`unclear_para` item and no part of its template holds a value word of the pair. Check 3 "
              "(`RULE_D_EXCLUDED`, a judgement of the template review): the collision word is the everyday word for "
              "all three values.", "",
              "| Order | Candidate | Failed checks 1 and 2 | Check 3 | Result |", "|---|---|---|---|---|"]
    for i, row in enumerate(content["checked"], 1):
        result = ("chosen" if row["pair"] in content["chosen"] else "excluded" if row["excluded"] else
                  "failed" if row["failed"] else "not needed: 16 earlier candidates remain")
        lines.append(f"| {i} | `{row['pair']}` | {'; '.join(row['failed']) or 'none'} | "
                     f"{row['excluded'] or 'passes'} | {result} |")
    cal = content["calibration"]
    lines += [f"| calibration | `{cal['pair']}` | {'; '.join(cal['failed']) or 'none'} | passes | reported apart |",
              "", "## 4. The system text", "",
              "One frame for all pairs. It is `zforms.F0` with these changes only: the assistant phrase, the role word "
              "(\"traveller\" in F0), the service noun of \"requirements for the hotel\", the field list (the `name` "
              "field and its sentence are removed), and the allowed values. G4 changes only the collision value of "
              "`type` to the G4 token, in the text and in the schema.", "",
              "```text", FRAME, "```", "", "Example: G0 of `table`.", "", "```text", system("table"), "```", "",
              "Decisions for the reviewers to check:",
              "- The service noun is the collision value, as `hotel` is in F0.",
              "- The assistant phrase is \"<service> booking assistant\", as in F0, except where \"booking\" is not "
              "natural: doctor (appointment), school (enrolment), letter (sending), coffee (ordering), camera "
              "(hire).",
              "- One wording per price level where the price field is `price` or `fees`: \"It should be cheap\", "
              "\"A moderate price is fine\", \"I am happy to pay a lot\". `table`, `room` and `restaurant` keep the "
              "wording of the calibration pair (\"should be cheap / moderately priced / expensive\").",
              "- The role word is \"traveller\", as in F0, except for `letter` (\"customer\"). The user text starts "
              "with the same role word (\"Customer: ...\").",
              "- The fields are place, price, size, `type` and day. Some pairs change a list: `letter` has the "
              "language in place of the area; `doctor` has the time of day in place of the price; `doctor`, "
              "`school` and `letter` have Monday to Friday only. The calibration pair also has these fields, so its "
              "text differs from F0 in the field list and the allowed values.",
              "- The user text is one traveller turn, in the form of `common.dialogue_text` (\"Traveller: ...\").",
              "- Check 1 is the round-9 rule with \"hotel\" replaced by every word of every value of the pair. This "
              "is stricter than the round-9 rule.",
              "- The size lists fit all three values (for example, a table for one or two, a car or a boat by days "
              "or hours, not by people).",
              "- The two clear sentences are the same in all scenarios of a pair.", "",
              "## 5. Example items (scenarios 0 and 1 of each pair)", ""]
    for key in content["chosen"] + [cal["pair"]]:
        lines += [f"### `{key}`", "", "| Scenario | Kind | Traveller text |", "|---|---|---|"]
        for it in items(key):
            if it.scenario < 2:
                lines.append(f"| {it.scenario} | `{it.kind}` | {it.text} |")
        lines.append("")
    lines += ["## 6. pairs.json", "", "```json", path.read_text().rstrip(), "```", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.argv[1:] == ["choose"]:
        pairs = chosen()
        print(f"{PAIRS_JSON}: {len(pairs)} pairs: " + ", ".join(p.collision for p in pairs))
    elif sys.argv[1:] == ["review"]:
        print(review_markdown(), end="")
    else:
        sys.exit("Usage: python3 -I r10/pairs.py choose | review")
