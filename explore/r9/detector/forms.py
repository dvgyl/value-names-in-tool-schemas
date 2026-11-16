"""The X3 and Z4 extraction forms: one form per selected pair, built like the E13 `p_main` form (PROTOCOL.md E13).

A domain form has the `p_main` sentences with the frame and the fields of its domain, and the closed schema of
`pmain/e13.py`. The allowed values of a field are the values of the domain database. If the pair value is not one of
them, it is added at the end of its field, because the test needs the value in the schema. The neutral form changes
only that one value, in the prompt and in the schema. `parse` maps the neutral value back to the original value.
"""
import json
from typing import NamedTuple

AREA = ["centre", "north", "south", "east", "west"]
STATIONS = ["birmingham new street", "bishops stortford", "broxbourne", "cambridge", "ely", "kings lynn", "leicester",
            "london kings cross", "london liverpool street", "norwich", "peterborough", "stansted airport", "stevenage"]
TIME = None  # a field with free values, given as hh:mm


class Domain(NamedTuple):
    frame: str  # the assistant in the first sentence
    thing: str  # the noun of the requirements sentence and of the name sentence
    name: bool  # the form has the name field of `p_main`
    fields: dict  # field -> allowed values in database order, or TIME


DOMAINS = {
    # restaurant_db.json, attraction_db.json, and train_db.json; attraction types written as words
    "restaurant": Domain("a restaurant booking assistant", "restaurant", True, {
        "food": ["african", "asian oriental", "british", "chinese", "european", "french", "gastropub", "indian",
                 "international", "italian", "japanese", "korean", "lebanese", "mediterranean", "mexican",
                 "modern european", "north american", "portuguese", "seafood", "spanish", "thai", "turkish",
                 "vietnamese"],
        "pricerange": ["cheap", "moderate", "expensive"], "area": AREA}),
    "attraction": Domain("a tourist information assistant", "attraction", True, {
        "type": ["architecture", "boat", "cinema", "college", "concert hall", "entertainment", "museum",
                 "multiple sports", "nightclub", "park", "swimming pool", "theatre"], "area": AREA}),
    "train": Domain("a train booking assistant", "train", False, {
        "departure": STATIONS, "destination": STATIONS,
        "day": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        "leaveat": TIME, "arriveby": TIME}),
}


class Form(NamedTuple):
    system: str
    schema: dict  # the JSON schema; Anthropic gets {"type": "json_schema", "schema": schema}
    slot: str
    value: str  # the original pair value
    token: str  # the value as the form writes it: the original value or the neutral value


def system_text(dom, fields):
    allowed = " ".join(f"{f}: {', '.join(v) if v is not TIME else 'times as hh:mm'}." for f, v in fields.items())
    return (f"You read a conversation between a traveller and {dom.frame} in Cambridge. Write down the traveller's "
            f"requirements for the {dom.thing} as one JSON object. Use only what the traveller said or agreed to. "
            f"Fields: {', '.join((['name'] if dom.name else []) + list(fields))}. "
            + (f"Give name as the {dom.thing} name if the traveller asked for one {dom.thing} by name, else null. "
               if dom.name else "")
            + "For each field give null if the traveller never stated a requirement, \"any\" if the traveller said it "
            "does not matter, or a list of acceptable values in the traveller's order of preference (first is most "
            f"preferred). Allowed values: {allowed} If the traveller changed their mind, give the final requirement. "
            "An option that the traveller only accepted from the assistant's offers is not a requirement. Output only "
            "the JSON object.")


def schema(dom, fields):
    """The closed schema of pmain/e13.py: each field is null, "any", or a list of allowed values."""
    props = {"name": {"anyOf": [{"type": "null"}, {"type": "string"}]}} if dom.name else {}
    for f, v in fields.items():
        items = {"type": "string"} if v is TIME else {"type": "string", "enum": list(v)}
        props[f] = {"anyOf": [{"type": "null"}, {"type": "string", "enum": ["any"]}, {"type": "array", "items": items}]}
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def form(domain, slot, value, neutral=None):
    """The form of one pair. With `neutral`, the pair value is replaced by the neutral value."""
    dom = DOMAINS[domain]
    fields = {f: (v if v is TIME else list(v)) for f, v in dom.fields.items()}
    assert fields[slot] is not TIME, slot
    if value not in fields[slot]:
        fields[slot].append(value)
    token = neutral or value
    fields[slot][fields[slot].index(value)] = token
    return Form(system_text(dom, fields), schema(dom, fields), slot, value, token)


def parse(text, f):
    """The final JSON object to {field: None, "any", or a tuple of values}. The neutral value maps back to the
    original value, so both forms are scored on the same field and value names."""
    s, e = text.rfind("{"), text.rfind("}")
    obj = json.loads(text[s:e + 1])
    out = {}
    for field in f.schema["properties"]:
        v = obj.get(field)
        if field == "name" or v is None:
            out[field] = v or None
        elif isinstance(v, str) and v.strip().lower() in ("any", "dontcare"):
            out[field] = "any"
        else:
            vals = [str(x).strip().lower() for x in (v if isinstance(v, list) else [v])]
            if field == f.slot and f.token != f.value:  # an original value that the neutral form does not offer
                vals = [f.value if x == f.token else f"{x} (not offered)" if x == f.value else x for x in vals]
            out[field] = tuple(dict.fromkeys(vals)) or None
    return out


def holds(parsed, f):
    """The read writes the pair value (or its neutral value) as an acceptable value of the pair slot."""
    v = parsed[f.slot]
    return isinstance(v, tuple) and f.value in v
