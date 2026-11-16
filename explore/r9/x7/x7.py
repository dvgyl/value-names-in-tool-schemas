"""Round 9, X7: the second collision words "entertainment" and "sport(s)" in attraction dialogues (PROTOCOL.md X7).

Form A0 is the E13 form `p_main` for the attraction domain: the same sentences, the fields name, area, and type, and
the closed schema of `pmain/e13.py`. The type values are the types of `attraction_db.json` in sorted order. Form A1 is
A0 with the values `entertainment` and `multiple sports` replaced by the neutral words. The parser maps each neutral
word back, so both forms are scored on the same fields and values. The five groups come from the brief and the
traveller turns. A dialogue in more than one group is read once per form, and the analysis counts it in each group.
`ids.json` holds the groups and the revealed type of each dialogue, fixed before any call
(`python3 -I r9/x7/x7.py ids` writes and checks it). Each experiment is one folder at the explore root, one account,
and one model per OpenAI batch. Its script is `r9/x7/<experiment>.py`.
"""
import json
import pathlib
import re
import sys
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent
R9 = HERE.parent
sys.path.insert(0, str(R9 / "natural"))
sys.path.insert(0, str(R9 / "trackc"))
import natural  # noqa: E402
from natural import accounts, anth, common, e13, oc  # noqa: E402
import ep  # noqa: E402
import panel  # noqa: E402

EXPLORE = natural.EXPLORE
IDS = HERE / "ids.json"
DB_SPELLING = {"mutliple sports": "multiple sports"}  # attraction_db.json and the briefs write this type with a typo
AREA = list(e13.VALUES["area"])
TYPES = sorted({DB_SPELLING.get(a["type"], a["type"]) for a in json.loads((anth.DATA / "attraction_db.json").read_text())})
# The first candidate of each pair that passes the F4 rule (test_x7.py check_neutral; PREDICTIONS.md).
NEUTRAL = {"entertainment": "amusement_venue", "multiple sports": "athletics_venue"}
CANDIDATES = {"entertainment": ("amusement_venue", "leisure_venue"),
              "multiple sports": ("athletics_venue", "activity_centre")}


class Form(NamedTuple):
    tokens: dict  # type value -> the token that the form shows; a value that is not named keeps its name


FORMS = {"a0": Form({}), "a1": Form(dict(NEUTRAL))}

# The edits that turn `p_main` into A0. Each old text occurs once in `p_main`.
P_MAIN = common.FORMS["p_main"].system
HOTEL_VALUES = " ".join(f"{f}: {', '.join(v)}." for f, v in e13.VALUES.items())
A0_EDITS = (("a hotel booking assistant", "a tourist information assistant"),
            ("requirements for the hotel", "requirements for the attraction"),
            ("Fields: name, area, pricerange, stars, type, parking, internet.", "Fields: name, area, type."),
            ("as the hotel name if the traveller asked for one hotel by name",
             "as the attraction name if the traveller asked for one attraction by name"))


def shown(form):
    """The allowed values of each field as the form writes them."""
    return {"area": AREA, "type": [form.tokens.get(v, v) for v in TYPES]}


def system(form):
    out = P_MAIN
    for old, new in A0_EDITS + ((HOTEL_VALUES, " ".join(f"{f}: {', '.join(v)}." for f, v in shown(form).items())),):
        assert out.count(old) == 1, f"{old!r} occurs {out.count(old)} times"
        out = out.replace(old, new)
    assert "hotel" not in out, out
    return out


def schema(form):
    """The closed schema of e13.schema: name is null or a string; area and type are null, "any", or a list of values."""
    props = {"name": {"anyOf": [{"type": "null"}, {"type": "string"}]}}
    for field, values in shown(form).items():
        props[field] = {"anyOf": [{"type": "null"}, {"type": "string", "enum": ["any"]},
                                  {"type": "array", "items": {"type": "string", "enum": values}}]}
    return {"type": "json_schema",
            "schema": {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}}


def _token(value):
    return str(value).strip().lower().replace(" ", "_")


def parse(text, form):
    """The last JSON object as {"name": str or None, "area" and "type": None, "any", or a tuple of values}. Each type
    value goes to its database name: a neutral token of the form maps back, and the A0 form maps no neutral token."""
    s, e = text.rfind("{"), text.rfind("}")
    obj = json.loads(text[s:e + 1])
    names = {_token(v): v for v in TYPES} | {_token(k): v for k, v in DB_SPELLING.items()}
    names |= {_token(t): v for v, t in form.tokens.items()}
    out = {"name": obj.get("name") or None}
    for field in ("area", "type"):
        v = obj.get(field)
        if v is None:
            out[field] = None
        elif isinstance(v, str) and v.strip().lower() in ("any", "dontcare"):
            out[field] = "any"
        else:
            vals = [str(x).strip().lower() for x in (v if isinstance(v, list) else [v])]
            if field == "type":
                vals = [names.get(_token(x), x) for x in vals]
            out[field] = tuple(dict.fromkeys(vals)) or None
    return out


# Groups (PROTOCOL.md X7). A word is matched at word boundaries in the traveller turns, plural allowed, as in the E8
# and E11 rule `\bhotels?\b` and the X3 rule.
class Group(NamedTuple):
    word: re.Pattern
    value: str  # the target type value
    brief: bool  # True: the brief sets type = value (info or fail_info); False: it does not


ENT, SPORT, MUSEUM = (re.compile(rf"\b{w}s?\b", re.I) for w in ("entertainment", "sport", "museum"))
GROUPS = {"G_ent": Group(ENT, "entertainment", False), "C_ent": Group(ENT, "entertainment", True),
          "G_sport": Group(SPORT, "multiple sports", False), "C_sport": Group(SPORT, "multiple sports", True),
          "M": Group(MUSEUM, "museum", True)}
COUNTS = {"G_ent": 15, "C_ent": 205, "G_sport": 2, "C_sport": 126, "M": 437}
UNION = 734


def says(d, word):
    return any(word.search(t["text"]) for k, t in enumerate(d["log"]) if k % 2 == 0)


def brief_types(d):
    a = d["goal"]["attraction"]
    return {DB_SPELLING.get(t, t) for t in ((a.get("info") or {}).get("type"), (a.get("fail_info") or {}).get("type")) if t}


def _keys(name):
    """The match keys of a name. The metadata often drops "the" and the apostrophe or the whole possessive "'s" of a
    database name: "cherry hinton village centre", "kettles yard", "christ college"."""
    s = re.sub(r"^the ", "", name.strip().lower().replace("&", "and"))
    return {re.sub(r"[^a-z0-9]", "", s), re.sub(r"[^a-z0-9]", "", s.replace("'s", ""))}


def db_types():
    out = {}
    for a in json.loads((anth.DATA / "attraction_db.json").read_text()):
        for k in _keys(a["name"]):
            assert out.setdefault(k, DB_SPELLING.get(a["type"], a["type"])) == DB_SPELLING.get(a["type"], a["type"]), k
    return out


EMPTY = ("", "not mentioned", "none", "dontcare")


def revealed(d, db_type):
    """The database type of the last attraction name in the per-turn metadata, "unmatched", or "none"."""
    names = [((t.get("metadata") or {}).get("attraction") or {}).get("semi", {}).get("name", "") for t in d["log"]]
    names = [n for n in names if n.strip().lower() not in EMPTY]
    if not names:
        return "none"
    return next((db_type[k] for k in sorted(_keys(names[-1])) if k in db_type), "unmatched")


def compute_ids(data):
    """The groups and the revealed types, by rule, with each count asserted."""
    val, test = anth.splits()
    pool = sorted(k for k in data if k not in val | test and "attraction" in anth.domains(data[k]["goal"]))
    assert len(pool) == 2718, len(pool)
    groups = {g: [k for k in pool if says(data[k], x.word) and (x.value in brief_types(data[k])) == x.brief]
              for g, x in GROUPS.items()}
    assert {g: len(v) for g, v in groups.items()} == COUNTS, {g: len(v) for g, v in groups.items()}
    union = sorted({k for v in groups.values() for k in v})
    assert len(union) == UNION, len(union)
    db_type = db_types()
    return {"groups": groups, "revealed": {k.removesuffix(".json"): revealed(data[k], db_type) for k in union}}


def ids():
    return json.loads(IDS.read_text())


def write_ids():
    """Write ids.json once. A rerun checks that the rule still gives the same content and changes nothing."""
    got = compute_ids(panel.multiwoz())
    if IDS.exists():
        assert ids() == got, f"{IDS} differs from the rule; the ids are fixed before any call"
        print(f"{IDS} matches the rule")
        return
    IDS.write_text(json.dumps(got, indent=0) + "\n")
    print(f"wrote {IDS}: " + ", ".join(f"{g} {len(v)}" for g, v in got["groups"].items()) + f", union {UNION}")


# The experiments. The models and their settings are natural.MODELS: Claude with the E13 settings, GPT with
# r9/trackc/panel.py (Sol effort low, Luna effort none), DeepInfra with r9/deepinfra_settings.py.
class Experiment(NamedTuple):
    account: str
    reads: dict  # model -> read numbers
    planning_out: int  # output tokens per call for a cell without a measured size
    pilot: bool  # the folder has its own pilot of anth.PILOT_PER_CELL calls per (model, effort) cell


EXPERIMENTS = {
    "ex7_claude": Experiment("anthropic_r9a", {"haiku": natural.reads(3), "sonnet": natural.reads(2)}, 56, True),
    "ex7_luna": Experiment("openai_r9", {"luna": natural.reads(3)}, 56, False),
    "ex7_sol": Experiment("openai_r9", {"sol": natural.ONE}, natural.SOL_OUT, False),
    "ex7_di": Experiment("deepinfra", natural.DI1, natural.DI_OUT, False),
}


def dialogues(groups):
    return sorted({d for v in groups.values() for d in v})


def requests(name, data=None, stored=None):
    exp = EXPERIMENTS[name]
    data = data or panel.multiwoz()
    stored = stored or ids()
    units = dialogues(stored["groups"])
    anth.assert_outside_trackp(units, data)
    val, test = anth.splits()
    assert not set(units) & (val | test), "a validation or test dialogue in an X7 request"
    provider = accounts.ACCOUNTS[exp.account].provider
    out = []
    for short, nums in exp.reads.items():
        assert natural.MODELS[short].provider == provider, f"{short} is not served by {exp.account}"
        for form_name, form in FORMS.items():
            text, fmt = system(form), schema(form)
            for d in units:
                user = common.dialogue_text(data[d])
                out += [natural.request(short, f"{name}-{d.removesuffix('.json')}-{form_name}-{r}-{short}", user, text,
                                        fmt) for r in nums]
    if provider == "openai":
        assert len({r["body"]["model"] for r in out}) == 1, f"{name}: an OpenAI batch takes one model"
    if provider in natural.BATCH_LIMITS:
        most, size = natural.BATCH_LIMITS[provider]
        body = sum(len(json.dumps(r)) for r in out)
        assert len(out) <= most and body < 0.9 * size, f"{name}: {len(out)} requests, {body / 1e6:.0f} MB in one batch"
    return out


def main(name):
    """The Claude folder has the steps of anth.main, its pilot included. The other folders take the per-call sizes of
    the natural-task answers of P (ep_oa, ep_di) and P2 (ep_di2) through ep.sizes, and have no pilot step."""
    exp = EXPERIMENTS[name]
    build = lambda: requests(name)  # noqa: E731
    if accounts.ACCOUNTS[exp.account].provider == "anthropic":
        anth.main(name, build, exp.planning_out, account=exp.account)
    else:
        panel.main(name, build, exp.planning_out, account=exp.account, sizes=lambda: ep.sizes(name, "nat"))


if __name__ == "__main__":
    assert sys.argv[1:] == ["ids"], "Usage: python3 -I r9/x7/x7.py ids"
    write_ids()
