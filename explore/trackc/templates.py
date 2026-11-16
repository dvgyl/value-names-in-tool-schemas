"""Draft Track C templates, goals, items, and forms for experiment E4 only (PROTOCOL.md).

Never reuse them in a calibration or confirmatory family.

A template family turns one goal into two dialogues. The clear control is the ambiguous item plus the clarifying
sentences, so the two texts differ only in the sentences that make the target field clear.

Usage: python3 -I templates.py   (prints goal 0 of each condition: the ambiguous item and its clear control)
"""
import functools
import itertools
import json
import pathlib
import random
import sys
from dataclasses import dataclass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
import anth  # noqa: E402

SEED = 20261024
GOALS_PER_CONDITION = 40
CONDITIONS = {
    "a": "collision word: the traveller says hotel where any place to stay fits",
    "b": "feature question: the traveller asks about a feature and never states it as a requirement",
    "c": "relaxation: the traveller names a new value after a failed search",
    "d": "unstated fact: the text never states a field that decides the allocation",
}
FIELDS = ("name", "area", "pricerange", "stars", "type", "parking", "internet")
ALLOWED = {"area": ("centre", "north", "south", "east", "west"), "pricerange": ("cheap", "moderate", "expensive"),
           "stars": ("0", "1", "2", "3", "4", "5"), "type": ("guesthouse", "hotel"), "parking": ("yes", "no"),
           "internet": ("yes", "no")}
STATED = {"area": ALLOWED["area"], "pricerange": ALLOWED["pricerange"], "stars": ("2", "3", "4")}
HOTELS = json.loads((anth.DATA / "hotel_db.json").read_text())
ALL = frozenset(h["name"] for h in HOTELS)

# The form prompts. p_unclear is the P5 prompt; check_items.py compares all three with p5_unclear/run.py.
P4_SYSTEM = (
    "You read a conversation between a traveller and a hotel booking assistant in Cambridge. "
    "Write down the traveller's requirements for the hotel as one JSON object. Use only what the traveller "
    "said or agreed to. Fields: area, pricerange, stars, type, parking, internet. For each field give null if "
    "the traveller never stated a requirement, \"any\" if the traveller said it does not matter, or a list of "
    "acceptable values in the traveller's order of preference (first is most preferred). Allowed values: "
    "area: centre, north, south, east, west. pricerange: cheap, moderate, expensive. stars: 0, 1, 2, 3, 4, 5. "
    "type: guesthouse, hotel. parking: yes, no. internet: yes, no. If the traveller changed their mind, give "
    "the final requirement. Output only the JSON object."
)
NAME_FIELD = ("Fields: area, pricerange, stars, type, parking, internet.",
              "Fields: name, area, pricerange, stars, type, parking, internet. Give name as the hotel name if the "
              "traveller asked for one hotel by name, else null.")
CHANGED = "If the traveller changed their mind, give the final requirement."
AMBIGUITY = (" If the traveller's words allow more than one reasonable reading for a field, write \"unclear\" for "
             "that field instead of choosing a reading.")
P_MAIN = P4_SYSTEM.replace(*NAME_FIELD)
FORMS = {
    "p_main": P_MAIN,
    "p_unclear": P_MAIN.replace(CHANGED, CHANGED + AMBIGUITY),
    "p_null": P_MAIN.replace(CHANGED, CHANGED + AMBIGUITY.replace('write "unclear"', "write null")),
}


def norm(field, v):
    """The P4 value normaliser."""
    v = str(v).strip().lower()
    if field == "type":
        v = {"guest house": "guesthouse", "bed and breakfast": "guesthouse"}.get(v, v)
    if field in ("parking", "internet") and v == "free":
        v = "yes"
    return v


def accepts(field, value):
    """The hotels that one field value accepts. A field value is None, "any", "unclear", or a tuple of values."""
    if value in (None, "any", "unclear"):
        return ALL
    return frozenset(h["name"] for h in HOTELS if norm(field, h[field]) in value)


def matches(form):
    return ALL.intersection(*(accepts(f, v) for f, v in form.items()))


def base_form(others):
    return {f: None for f in FIELDS} | {f: (v,) for f, v in others}


CORE, TRIGGER, CLARIFY = "core", "trigger", "clarify"


@dataclass(frozen=True)
class Family:
    id: str
    condition: str
    target: str
    other_fields: tuple
    turns: tuple


@dataclass(frozen=True)
class Goal:
    id: str
    family: Family
    others: tuple
    clear: tuple
    readings: tuple
    nights: int
    people: int
    day: str


@dataclass(frozen=True)
class Item:
    id: str
    goal: Goal
    kind: str
    turns: tuple
    interpretations: tuple

    @property
    def condition(self):
        return self.goal.family.condition

    @property
    def target(self):
        return self.goal.family.target

    @property
    def text(self):
        return "\n".join(("Traveller: " if i % 2 == 0 else "Assistant: ") + " ".join(s for _, s in turn)
                         for i, turn in enumerate(self.turns))


FAMILIES = (
    Family("xa1", "a", "type", ("area", "pricerange", "stars"), (
        ((CORE, "Good evening."), (TRIGGER, "My plan is to book {hotel}."),
         (CLARIFY, "It has to be a real hotel, not a guesthouse.")),
        ((CORE, "Sure, I can do that for you. For which dates, and for how many guests?"),),
        ((CORE, "{Nights} from {day}. The booking is for {people}."),),
        ((CORE, "Noted. Let me see what is free on those dates."),),
    )),
    Family("xa2", "a", "type", ("area", "pricerange", "stars"), (
        ((CORE, "Hi. I am coming to Cambridge on {day} and I still have nowhere to sleep."),),
        ((CORE, "Of course. What sort of place do you have in mind?"),),
        ((CORE, "What matters to me is that {clause}."), (TRIGGER, "Can you find me a hotel like that?"),
         (CLARIFY, "Please do not offer me a guesthouse.")),
        ((CORE, "Sure. How many nights, and for how many guests?"),),
        ((CORE, "{Nights}, for {people}."),),
        ((CORE, "Thanks. I am searching the list for you now."),),
    )),
    Family("xb1", "b", "parking", ("area", "pricerange", "stars"), (
        ((CORE, "Hi. We need {room} for {nights}."),),
        ((CORE, "I can see a few that fit."),),
        ((TRIGGER, "Do those places offer free parking?"),
         (CLARIFY, "I am driving there, so free parking is essential.")),
        ((CORE, "Some of them do, and some do not."),),
        ((CORE, "Thank you. Please book one of them for {people} from {day}."),),
        ((CORE, "Certainly. I will make the booking now."),),
    )),
    Family("xb2", "b", "parking", ("area", "pricerange", "stars"), (
        ((CORE, "Good morning."), (TRIGGER, "Do {rooms} usually come with free parking?")),
        ((CORE, "Some of them have it, and some do not."),),
        ((CORE, "I see. Then please find me {room} for {nights} from {day}."),
         (CLARIFY, "Free parking is a must for me.")),
        ((CORE, "Of course. How many guests will there be?"),),
        ((CORE, "It is for {people}."),),
        ((CORE, "Thanks. I am looking for a room now."),),
    )),
    Family("xc1", "c", "area", ("pricerange", "stars"), (
        ((CORE, "Hello. I would like {room}."), (TRIGGER, "The location I want is the {v0}."),
         (CLARIFY, "If the {v0} has nothing, the {v1} is my second choice.")),
        ((TRIGGER, "I am sorry, I have nothing like that in the {v0}."),),
        ((TRIGGER, "Could you try the {v1}?"),),
        ((CORE, "I can offer you a room in the {v1}. For how many nights?"),),
        ((CORE, "{Nights} from {day}, for {people}."),),
        ((CORE, "Noted. I will check those dates."),),
    )),
    Family("xc2", "c", "pricerange", ("area", "stars"), (
        ((CORE, "Hi. Please find me {room}."), (TRIGGER, "The price level I want is {v0}.")),
        ((TRIGGER, "Sorry, nothing at the {v0} price level fits."),),
        ((CORE, "Okay."), (TRIGGER, "Then could you try the {v1} price level?"),
         (CLARIFY, "The {v0} price level is still my first choice if one becomes free.")),
        ((CORE, "I can find something at the {v1} price level. For how many guests?"),),
        ((CORE, "The booking is for {people}, staying {nights}."),),
        ((CORE, "Thanks. Let me check the dates."),),
    )),
    Family("xd1", "d", "stars", ("area", "pricerange"), (
        ((CORE, "Hello. Please find me {room} from {day}."),),
        ((CORE, "I can help you with that. How many nights will you stay?"),),
        ((CORE, "{Nights}, for {people}."), (CLARIFY, "I would like it to have {v} stars.")),
        ((CORE, "Thanks. I am checking what is free."),),
    )),
    Family("xd2", "d", "parking", ("area", "pricerange", "stars"), (
        ((CORE, "Hi. Could you look for {room}?"),),
        ((CORE, "I can look into that. Are you bringing a car that needs parking?"),),
        ((CLARIFY, "Yes, and the parking must be free."), (CORE, "Could you book one for {nights} from {day}?")),
        ((CORE, "Of course. How many people is it for?"),),
        ((CORE, "It is for {people}."),),
        ((CORE, "Thanks. I am making the booking now."),),
    )),
)


def targets(condition, field, base):
    """(clear reading, ambiguous reading set) pairs that the hotel database makes true for one set of stated fields."""
    if condition == "c":
        return [((v0, v1), ((v1,), (v0, v1))) for v0, v1 in itertools.permutations(ALLOWED[field], 2)
                if not base & accepts(field, (v0,)) and base & accepts(field, (v1,))]
    out = []
    for v in {"type": ("hotel",), "parking": ("yes",), "stars": STATED["stars"]}[field]:
        narrowed = base & accepts(field, (v,))
        if narrowed and narrowed != base:  # the target field decides between the hotels that fit the rest
            out.append(((v,), (None,) if condition == "d" else (None, (v,))))
    return out


def skeletons(family):
    out = []
    for size in (1, 2):
        for fields in itertools.combinations(family.other_fields, size):
            for values in itertools.product(*(STATED[f] for f in fields)):
                others = tuple(zip(fields, values))
                base = matches(base_form(others))
                if base:
                    out += [(others, clear, readings) for clear, readings in targets(family.condition, family.target, base)]
    return out


@functools.cache
def goals():
    rng = random.Random(SEED)
    out = []
    for condition in CONDITIONS:
        families = [f for f in FAMILIES if f.condition == condition]
        pools = {f.id: skeletons(f) for f in families}
        for f in families:
            rng.shuffle(pools[f.id])
        for i in range(GOALS_PER_CONDITION):
            family = families[i % len(families)]
            pool = pools[family.id]
            others, clear, readings = pool[(i // len(families)) % len(pool)]
            out.append(Goal(f"x{condition}-g{i:02d}", family, others, clear, readings,
                            rng.randint(1, 5), rng.randint(1, 4), rng.choice(DAYS)))
    return tuple(out)


DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
NUMBER = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
PRICE = {"cheap": "cheap", "moderate": "moderately priced", "expensive": "expensive"}


def phrase(others, noun):
    o = dict(others)
    words = [PRICE[o["pricerange"]]] if "pricerange" in o else []
    words += [noun] + ([f"in the {o['area']}"] if "area" in o else []) + ([f"with {o['stars']} stars"] if "stars" in o else [])
    return " ".join(words)


def clause(others):
    """The stated fields as one clause, for example "the place is cheap and has 4 stars"."""
    o = dict(others)
    is_ = [p for p in (o.get("pricerange") and PRICE[o["pricerange"]], o.get("area") and f"in the {o['area']}") if p]
    has = f"has {o['stars']} stars" if "stars" in o else ""
    return "the place " + " and ".join(([f"is {' and '.join(is_)}"] if is_ else []) + ([has] if has else []))


def article(s):
    return ("an " if s[0] in "aeiou" else "a ") + s


def slots(goal):
    s = {"room": article(phrase(goal.others, "room")), "rooms": phrase(goal.others, "rooms"),
         "hotel": article(phrase(goal.others, "hotel")), "clause": clause(goal.others),
         "nights": f"{NUMBER[goal.nights]} night{'s' * (goal.nights > 1)}",
         "people": "one person" if goal.people == 1 else f"{NUMBER[goal.people]} people", "day": goal.day}
    s |= {k.capitalize(): v[0].upper() + v[1:] for k, v in s.items()}
    if goal.family.condition == "c":
        s |= {"v0": goal.clear[0], "v1": goal.clear[1]}
    if goal.family.condition == "d":
        s["v"] = goal.clear[0]
    return s


def make(goal, kind):
    s = slots(goal)
    turns = tuple(tuple((role, text.format(**s)) for role, text in turn if kind == "clear" or role != CLARIFY)
                  for turn in goal.family.turns)
    readings = goal.readings if kind == "ambiguous" else (goal.clear,)
    interpretations = tuple(base_form(goal.others) | {goal.family.target: r} for r in readings)
    return Item(f"{goal.id}-{'amb' if kind == 'ambiguous' else 'clr'}", goal, kind, turns, interpretations)


@functools.cache
def items():
    return tuple(make(g, kind) for g in goals() for kind in ("ambiguous", "clear"))


def show(item):
    readings = [i[item.target] for i in item.interpretations]
    return f"{item.id} ({item.kind}, family {item.goal.family.id}, target {item.target}, readings {readings})\n{item.text}"


if __name__ == "__main__":
    for c in CONDITIONS:
        print(f"== condition {c}: {CONDITIONS[c]}")
        for it in items():
            if it.goal.id == f"x{c}-g00":
                print(show(it), end="\n\n")
