"""Forms, parser, gold, and market for E1, E5, and E6 (PROTOCOL.md).

The prompt text, the gold mapping, the parser, and the market are copies of
`p4_multiwoz/run.py` and `p5_unclear/run.py`. `test_prompts.py` and `test_analyze.py` check the copies
against those scripts and their saved results.
"""
import json
import random
import sys
from pathlib import Path
from typing import NamedTuple

FORMS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FORMS_DIR.parent / "lib"))
import anth  # noqa: E402

P4_DIR = FORMS_DIR.parents[1] / "p4_multiwoz"
FIELDS = ["area", "pricerange", "stars", "type", "parking", "internet"]
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}

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
NAME = (
    "Fields: area, pricerange, stars, type, parking, internet.",
    "Fields: name, area, pricerange, stars, type, parking, internet. Give name as the hotel name if the traveller "
    "asked for one hotel by name, else null.",
)
UNCLEAR = (
    "If the traveller changed their mind, give the final requirement.",
    "If the traveller changed their mind, give the final requirement. If the traveller's words allow more than one "
    "reasonable reading for a field, write \"unclear\" for that field instead of choosing a reading.",
)

OFFER = (  # the draft p_main of PLAN SI-05 and SI-02, as annot/e3.py builds it
    "If the traveller changed their mind, give the final requirement.",
    "If the traveller changed their mind, give the final requirement. An option that the traveller only accepted from "
    "the assistant's offers is not a requirement.",
)


class Form(NamedTuple):
    system: str
    name: bool
    unclear: bool
    renamed: bool = False


def renamed(system: str) -> str:
    """The natural Claim 1 test of PLAN SI-16: `type` becomes `property_kind`, and `hotel` becomes `large_property`."""
    out = system.replace(", stars, type, parking,", ", stars, property_kind, parking,").replace(
        "type: guesthouse, hotel.", "property_kind: guesthouse, large_property.")
    assert out.count("property_kind") == 2 and " type" not in out, out
    return out


FORMS = {
    "p4": Form(P4_SYSTEM, False, False),
    "p4_name": Form(P4_SYSTEM.replace(*NAME), True, False),
    "p4_unclear": Form(P4_SYSTEM.replace(*UNCLEAR), False, True),
    "p5": Form(P4_SYSTEM.replace(*NAME).replace(*UNCLEAR), True, True),
    "p4_renamed": Form(renamed(P4_SYSTEM), False, False, True),
    "p5_renamed": Form(renamed(P4_SYSTEM.replace(*NAME).replace(*UNCLEAR)), True, True, True),
    "p_main": Form(P4_SYSTEM.replace(*NAME).replace(*OFFER), True, False),
    "p_main_renamed": Form(renamed(P4_SYSTEM.replace(*NAME).replace(*OFFER)), True, False, True),
}


class Spec(NamedTuple):
    dialogues: str
    forms: tuple
    reads: int
    models: tuple
    effort: str
    max_tokens: int


EXPERIMENTS = {
    "e1": Spec("p4", tuple(FORMS), 5, ("haiku", "sonnet", "opus"), "low", 4096),
    "e5": Spec("e5", ("p4", "p5"), 3, ("haiku", "sonnet", "opus"), "low", 4096),
    "e6": Spec("p4", ("p4", "p5"), 3, ("sonnet", "opus"), "high", 16000),
    "e7": Spec("e7", ("p4", "p5"), 3, ("haiku", "sonnet", "opus"), "low", 4096),
    "e8": Spec("e5", ("p4_renamed", "p5_renamed"), 3, ("haiku", "sonnet", "opus"), "low", 4096),
    "e11": Spec("e11", ("p4_renamed", "p5_renamed"), 3, ("haiku", "sonnet", "opus"), "low", 4096),
}
GOLD = {"p4": "MultiWOZ 2.4 (validation and test)", "e5": "MultiWOZ 2.1 (training split, not corrected in 2.4)",
        "e7": "MultiWOZ 2.1 (training split, multi-domain, not corrected in 2.4)",
        "e11": "MultiWOZ 2.1 (training split, multi-domain, not corrected in 2.4)"}


def p4_ids(data):
    val, test = anth.splits()
    return sorted(k for k in val | test if k in data and anth.domains(data[k]["goal"]) == ["hotel"])


def e5_ids(data):
    val, test = anth.splits()
    pool = sorted(k for k in data if k not in val | test and anth.domains(data[k]["goal"]) == ["hotel"])
    assert len(pool) == 513, len(pool)
    return sorted(random.Random(20261024).sample(pool, 500))


def e7_ids(data):
    val, test = anth.splits()
    pool = sorted(k for k in data if k not in val | test and "hotel" in anth.domains(data[k]["goal"])
                  and len(anth.domains(data[k]["goal"])) > 1)
    assert len(pool) == 2874, len(pool)
    return pool


def e11_ids(data):
    """The E7 dialogues that the E8 measure uses: gold sets no type, and some turn says "hotel" (the all-turns rule)."""
    import re
    word = re.compile(r"\bhotels?\b", re.I)
    return [i for i in e7_ids(data) if gold_form(data[i])["type"] is None and any(word.search(t["text"]) for t in data[i]["log"])]


def dialogue_ids(name, data):
    return {"p4": p4_ids, "e5": e5_ids, "e7": e7_ids, "e11": e11_ids}[EXPERIMENTS[name].dialogues](data)


def custom_id(name, dialogue, form, read, model):
    return f"{name}-{dialogue.removesuffix('.json')}-{form}-{read}-{model}"


def split_custom_id(cid):
    name, dialogue, form, read, model = cid.split("-")
    return name, dialogue + ".json", form, int(read), model


def requests(name, data, ids):
    spec = EXPERIMENTS[name]
    return [anth.request(custom_id(name, i, form, read, model), MODELS[model], spec.effort, spec.max_tokens,
                         dialogue_text(data[i]), FORMS[form].system)
            for model in spec.models for form in spec.forms for i in ids for read in range(1, spec.reads + 1)]


def p4_field_sets(ids):
    """The 53 P4-ambiguous fields and the 635 fields that no P4 adjudication row disputes."""
    adj = json.loads((P4_DIR / "adjudication.json").read_text())
    ambiguous = {(a["id"], a["field"]) for a in adj if a["label"] == "AMBIGUOUS"}
    undisputed = {(i, f) for i in ids for f in FIELDS} - {(a["id"], a["field"]) for a in adj}
    assert (len(ambiguous), len(undisputed)) == (53, 635), (len(ambiguous), len(undisputed))
    return ambiguous, undisputed


def norm_value(field: str, v: str) -> str:
    v = v.strip().lower()
    if field == "type":
        v = {"guest house": "guesthouse", "bed and breakfast": "guesthouse"}.get(v, v)
    if field in ("parking", "internet") and v == "free":
        v = "yes"
    return v


def parse_gold(raw: str, field: str):
    """MultiWOZ label to None (not stated), 'any', or a tuple of values in preference order."""
    if raw in ("not mentioned", "none", ""):
        return None
    if raw == "dontcare":
        return "any"
    parts = raw.replace("<", ">").split(">") if ">" in raw or "<" in raw else raw.split("|")
    if "<" in raw:
        parts = parts[::-1]
    return tuple(dict.fromkeys(norm_value(field, p) for p in parts))


def gold_form(d: dict) -> dict:
    semi = [t for t in d["log"] if t.get("metadata")][-1]["metadata"]["hotel"]["semi"]
    return {f: parse_gold(semi.get(f, "not mentioned"), f) for f in FIELDS}


def dialogue_text(d: dict) -> str:
    return "\n".join(("Traveller: " if i % 2 == 0 else "Assistant: ") + t["text"].strip() for i, t in enumerate(d["log"]))


def parse(text: str):
    """The P5 parser for every form, so a contrast between forms measures the prompt and not the parser."""
    s, e = text.rfind("{"), text.rfind("}")  # the last object is the final answer
    obj = json.loads(text[s:e + 1])
    if "property_kind" in obj:  # the renamed forms map back, so every form is scored on the same fields
        kind = obj.pop("property_kind")
        swap = {"large_property": "hotel", "large property": "hotel"}
        obj["type"] = [swap.get(str(x).lower(), x) for x in kind] if isinstance(kind, list) else swap.get(str(kind).lower(), kind)
    out = {"name": (obj.get("name") or None)}
    for f in FIELDS:
        v = obj.get(f)
        if isinstance(v, str) and v.lower() == "unclear":
            out[f] = "unclear"
        elif v is None:
            out[f] = None
        elif isinstance(v, str) and v.lower() in ("any", "dontcare"):
            out[f] = "any"
        else:
            vals = v if isinstance(v, list) else [v]
            out[f] = tuple(dict.fromkeys(norm_value(f, str(x)) for x in vals)) or None
    return out


def acceptable_rank(form: dict, hotels: list, tiebreak: dict) -> list:
    """Hotels the form accepts, best first: fewer fallback steps first, then a fixed per-person order."""
    ranked = []
    for h in hotels:
        cost = 0
        ok = True
        for f in FIELDS:
            want = form[f]
            if want in (None, "any"):
                continue
            hv = norm_value(f, h[f])
            if hv not in want:
                ok = False
                break
            cost += want.index(hv)
        if ok:
            ranked.append((cost, tiebreak[h["name"]], h["name"]))
    return [n for _, _, n in sorted(ranked)]


def rsd(prefs: dict, order: list) -> dict:
    taken, out = set(), {}
    for p in order:
        out[p] = next((h for h in prefs[p] if h not in taken), None)
        if out[p]:
            taken.add(out[p])
    return out


MARKETS, OTHERS = 20, 23


class Market:
    """The P4 market with its seeds: per dialogue, 20 serial dictatorships with 23 other travellers from `ids`."""

    def __init__(self, data, ids):
        self.hotels = json.loads((anth.DATA / "hotel_db.json").read_text())
        rng = random.Random(11)
        self.tieb = {i: {h["name"]: rng.random() for h in self.hotels} for i in ids}
        gold_pref = {i: acceptable_rank(gold_form(data[i]), self.hotels, self.tieb[i]) for i in ids}
        self.draws = {}
        for i in ids:
            mr = random.Random(int("".join(ch for ch in i if ch.isdigit())))
            rounds = []
            for _ in range(MARKETS):
                others = mr.sample([j for j in ids if j != i], OTHERS)
                order = mr.sample(others + [i], OTHERS + 1)
                prefs = {j: gold_pref[j] for j in others}
                rounds.append((prefs, order, rsd({**prefs, i: gold_pref[i]}, order)))
            self.draws[i] = rounds

    def flips(self, i, ext):
        """Markets whose allocation changes. "unclear" counts as no constraint; the name field is not used."""
        pref = acceptable_rank({f: (None if ext[f] == "unclear" else ext[f]) for f in FIELDS}, self.hotels, self.tieb[i])
        return sum(rsd({**prefs, i: pref}, order) != gold for prefs, order, gold in self.draws[i])
