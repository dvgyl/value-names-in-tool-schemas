"""Round 9, natural-dialogue schema forms: the runs X1, the natural part of X2, and B1 (r9/natural/PREDICTIONS.md).

A form is the E13 form `p_main` with some named tokens changed. Its parser maps each changed token back, so every form
is scored on the original fields and values. The groups S1 to S5 split the 2,874 E7 training dialogues. `ids.json`
holds every id list that a request uses, fixed before any call (`python3 -I natural.py ids` writes and checks it).
Each experiment is one folder at the explore root, one account, and one batch or synchronous run. Its script is
`r9/natural/<experiment>.py`, with the steps of `lib/anth.py` or `lib/openai_compat.py`.
"""
import copy
import json
import math
import pathlib
import random
import re
import sys
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parents[1]
for sub in ("lib", "forms", "pmain", "trackc"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE.parent))
import accounts  # noqa: E402
import anth  # noqa: E402
import common  # noqa: E402
import deepinfra_settings as ds  # noqa: E402
import e13  # noqa: E402
import e14  # noqa: E402
import openai_compat as oc  # noqa: E402
import templates  # noqa: E402

IDS = HERE / "ids.json"
SEED = 20261103
NEUTRAL = "serviced_property"  # the F4 token; test_natural.py checks the token rule on the training split


class Form(NamedTuple):
    keys: dict  # original field -> the key that the form shows; a field that is not named keeps its name
    hotel: str  # the token that the form shows for the `type` value "hotel"
    note: str = ""  # text after the `type` values in the allowed-values list


FORMS = {
    "f0": Form({}, "hotel"),
    "f1": Form({"type": "property_kind"}, "large_property"),
    "f2": Form({}, "large_property"),
    "f3": Form({"type": "property_kind"}, "hotel"),
    "f4": Form({}, NEUTRAL),
    "f5": Form({"area": "district", "pricerange": "price_band"}, "hotel"),
    "f6": Form({}, "category_A", " (any venue type that is not a guesthouse)"),
}
FIELD_LIST = "Fields: name, " + ", ".join(common.FIELDS) + "."


def _once(text, old, new):
    assert text.count(old) == 1, f"{old!r} occurs {text.count(old)} times"
    return text.replace(old, new)


def system(base, form):
    """The base prompt with the field list and the allowed values of the form. No other text changes."""
    key = lambda f: form.keys.get(f, f)
    out = _once(base, FIELD_LIST, "Fields: name, " + ", ".join(map(key, common.FIELDS)) + ".")
    for field, values in e13.VALUES.items():
        shown = [form.hotel if (field, v) == ("type", "hotel") else v for v in values]
        note = form.note if field == "type" else ""
        out = _once(out, f"{field}: {', '.join(values)}.", f"{key(field)}: {', '.join(shown)}{note}.")
    return out


def schema(base, form):
    """The base output format (e13.schema or e14.schema) with the keys and the `type` values of the form."""
    inner = copy.deepcopy(base["schema"])
    hotel = lambda v: form.hotel if v == "hotel" else v
    for option in inner["properties"]["type"]["anyOf"]:
        if option.get("type") == "array":
            option["items"]["enum"] = [hotel(v) for v in option["items"]["enum"]]
    inner["properties"] = {form.keys.get(k, k): v for k, v in inner["properties"].items()}
    inner["required"] = list(inner["properties"])
    return {**base, "schema": inner}


def _token(value):
    return str(value).strip().lower().replace(" ", "_")


def parse(text, form):
    """common.parse after the form's keys and its hotel token are mapped back to the original names."""
    s, e = text.rfind("{"), text.rfind("}")
    obj = json.loads(text[s:e + 1])
    back = {v: k for k, v in form.keys.items()}
    obj = {back.get(k, k): v for k, v in obj.items()}
    undo = lambda v: "hotel" if isinstance(v, str) and _token(v) == _token(form.hotel) else v
    if "type" in obj:
        obj["type"] = [undo(v) for v in obj["type"]] if isinstance(obj["type"], list) else undo(obj["type"])
    return common.parse(json.dumps(obj))


# Groups. WORD is the E8 and E11 rule; `booked` is the rule of review/plan13/revealed_r9b.py.
WORD = re.compile(r"\bhotels?\b", re.I)


def says_hotel(d, traveller_only):
    return any(WORD.search(t["text"]) for k, t in enumerate(d["log"]) if k % 2 == 0 or not traveller_only)


def _norm_name(s):
    return re.sub(r"[^a-z0-9]", "", s.lower().replace("&", "and"))


def booked(d, db_type):
    """The type of the last booked hotel ("hotel" or "guesthouse"), "unmatched" if it is not in hotel_db.json, or "none"."""
    names = [b["name"] for t in d["log"]
             for b in ((t.get("metadata") or {}).get("hotel", {}).get("book", {}).get("booked") or []) if b.get("name")]
    return db_type.get(_norm_name(names[-1]), "unmatched") if names else "none"


def compute_ids(data):
    """Every id list of the round-9 natural runs, by rule, with each count asserted."""
    e7, s1 = common.e7_ids(data), common.e11_ids(data)
    gold = {i: common.gold_form(data[i])["type"] for i in e7}
    guest = [i for i in e7 if gold[i] == ("guesthouse",)]
    g = {"S1": s1, "S1t": [i for i in s1 if says_hotel(data[i], True)],
         "S2": [i for i in e7 if gold[i] == ("hotel",)],
         "S3": [i for i in guest if says_hotel(data[i], True)],
         "S4": [i for i in guest if not says_hotel(data[i], True)]}
    in_s1 = set(s1)
    g["S5"] = [i for i in e7 if i not in in_s1 and gold[i] not in (("hotel",), ("guesthouse",))]
    counts = {k: len(v) for k, v in g.items()}
    assert counts == {"S1": 1136, "S1t": 994, "S2": 545, "S3": 490, "S4": 423, "S5": 280}, counts
    assert sorted(g["S1"] + g["S2"] + g["S3"] + g["S4"] + g["S5"]) == e7, "S1 to S5 do not partition the E7 dialogues"
    g["drift"] = sorted(random.Random(SEED).sample(s1, math.ceil(0.2 * len(s1))))
    g["sub600"] = sorted(random.Random(SEED).sample(sorted(g["S2"] + g["S3"] + g["S4"]), 600))
    db_type = {_norm_name(h["name"]): h["type"] for h in json.loads((anth.DATA / "hotel_db.json").read_text())}
    g["S2_booked_hotel"] = [i for i in g["S2"] if booked(data[i], db_type) == "hotel"]
    g["S2_brief_hotel"] = [i for i in g["S2"] if data[i]["goal"]["hotel"].get("info", {}).get("type") == "hotel"]
    for kind in ("guesthouse", "hotel", "none", "unmatched"):
        g[f"S1t_booked_{kind}"] = [i for i in g["S1t"] if booked(data[i], db_type) == kind]
    counts = {k: len(v) for k, v in g.items() if k not in counts}
    assert counts == {"drift": 228, "sub600": 600, "S2_booked_hotel": 293, "S2_brief_hotel": 233,
                      "S1t_booked_guesthouse": 355, "S1t_booked_hotel": 199, "S1t_booked_none": 440,
                      "S1t_booked_unmatched": 0}, counts
    return g


def ids():
    return json.loads(IDS.read_text())["groups"]


# The panel. Claude: the E13 settings. GPT and Gemini: SYN-S5 section 3.2, which PLAN SI-09 names, and the output cap
# of 4,000 tokens of PLAN SI-02; the Gemini thinking level is oc.GEMINI_THINKING. DeepInfra: r9/deepinfra_settings.py.
class Model(NamedTuple):
    id: str
    provider: str  # the provider of the account that can send the request
    max_tokens: int
    effort: str = None  # Anthropic output_config effort, or OpenAI reasoning effort
    thinking: dict = None  # Anthropic only


MODELS = {
    "haiku": Model(common.MODELS["haiku"], "anthropic", e13.MAX_TOKENS, e13.SETTINGS["haiku"][1], e13.SETTINGS["haiku"][0]),
    "sonnet": Model(common.MODELS["sonnet"], "anthropic", e13.MAX_TOKENS, e13.SETTINGS["sonnet"][1], e13.SETTINGS["sonnet"][0]),
    "sol": Model("gpt-6.1-sol", "openai", 4000, "low"),
    "luna": Model("gpt-6-luna", "openai", 4000, "none"),
    "deepseek": Model(ds.DEEPSEEK.id, "deepinfra", ds.DEEPSEEK.max_tokens),
    "qwen": Model(ds.QWEN.id, "deepinfra", ds.QWEN.max_tokens),
    "gemma": Model(ds.GEMMA.id, "deepinfra", ds.GEMMA.max_tokens),
    "gemini": Model("gemini-3.8-flash", "google", 4000),
}


def request(short, cid, user, system_text, fmt):
    m = MODELS[short]
    if m.provider == "anthropic":
        return anth.request(cid, m.id, m.effort, m.max_tokens, user, system_text, m.thinking, fmt)
    if m.provider == "openai":
        return oc.openai_request(cid, m.id, m.effort, m.max_tokens, user, system_text, fmt["schema"])
    if m.provider == "google":
        return oc.gemini_request(cid, m.id, m.max_tokens, user, system_text, fmt["schema"])
    return ds.request(ds.MODELS[m.id], cid, user, system_text, fmt["schema"])


# The experiments. A block reads each unit of its groups under each form, with the read numbers of each model.
TRACKC = "trackc_a"  # the 80 E4 condition-a items (40 ambiguous, 40 clear controls), base forms of E14
REST = ("S2", "S3", "S4", "S5")


class Block(NamedTuple):
    groups: tuple  # keys of ids.json, or TRACKC
    forms: tuple
    reads: dict  # model -> read numbers


class Experiment(NamedTuple):
    run: str
    account: str
    blocks: tuple
    planning_out: int  # output tokens per call until a pilot measures them (E13 and E14 means, PLAN reasoning guesses)
    pilot: bool  # r9_counts.py counts 10 pilot calls per model in this folder


def reads(n, first=1):
    return tuple(range(first, first + n))


H3S3, H3S2, ONE = {"haiku": reads(3), "sonnet": reads(3)}, {"haiku": reads(3), "sonnet": reads(2)}, (1,)
DI1 = {"deepseek": ONE, "qwen": ONE, "gemma": ONE}
SOL_OUT, DI_OUT = 56 + 500, 56 + 300  # visible output plus the PLAN reasoning guess (Sol 500, DeepSeek 300)
EXPERIMENTS = {
    "ex1_s1": Experiment("X1", "anthropic_r9a", (Block(("S1",), ("f2", "f3", "f4", "f5"), H3S3),
                                                 Block(("drift",), ("f0",), H3S3)), 56, True),
    "ex1_grp": Experiment("X1", "anthropic_r9a", (Block(REST, ("f0", "f1", "f2", "f4"), H3S2),), 56, True),
    "ex1_f6": Experiment("X1", "anthropic_r9a", (Block(("S1",), ("f6",), H3S3), Block(REST, ("f6",), H3S2)), 56, True),
    "ex1_tc": Experiment("X1", "anthropic_r9a", (Block((TRACKC,), ("f1", "f2", "f4"), {"haiku": reads(7), "sonnet": reads(6)}),
                                                 Block((TRACKC,), ("f0",), {"sonnet": reads(4, first=3)})), 51, True),
    "ex2n_sol": Experiment("X2", "openai_r9", (Block(("S1",), ("f0", "f1"), {"sol": ONE}),), SOL_OUT, False),
    "ex2n_sol_f4": Experiment("X2", "openai_r9", (Block(("S1",), ("f4",), {"sol": ONE}),), SOL_OUT, False),
    "ex2n_sol_sub": Experiment("X2", "openai_r9", (Block(("sub600",), ("f0", "f1", "f4"), {"sol": ONE}),), SOL_OUT, False),
    "ex2n_luna": Experiment("X2", "openai_r9", (Block(("S1",) + REST, ("f0", "f1", "f4"), {"luna": reads(3)}),), 56, False),
    "ex2n_di": Experiment("X2", "deepinfra", (Block(("S1",), ("f0", "f1"), DI1),), DI_OUT, False),
    "eb1_luna": Experiment("B1", "openai_r9", (Block(("S1", "S2"), ("f2", "f3", "f5", "f6"), {"luna": reads(3)}),), 56, False),
    "eb1_sol": Experiment("B1", "openai_r9", (Block(("S1",), ("f2", "f6"), {"sol": ONE}),), SOL_OUT, False),
    "eb1_di": Experiment("B1", "deepinfra", (Block(("S1",), ("f2", "f3", "f4", "f5", "f6"), DI1),
                                             Block(("S2",), ("f0", "f1", "f4"), DI1)), DI_OUT, False),
}
# Batch limits of the providers: Anthropic 100,000 requests or 256 MB, OpenAI 50,000 requests or 200 MB.
BATCH_LIMITS = {"anthropic": (100_000, 256e6), "openai": (50_000, 200e6)}


def units(group, data, groups):
    """(unit id, user text) pairs. A unit id has no "-", so a custom_id splits into 5 parts."""
    if group == TRACKC:
        return [(it.id.replace("-", "_"), it.text) for it in templates.items() if it.condition == "a"]
    return [(d.removesuffix(".json"), common.dialogue_text(data[d])) for d in groups[group]]


def base(group):
    """The F0 prompt and output format: E13 `p_main` for dialogues, E14 `p_main` for the Track C items."""
    if group == TRACKC:
        return templates.FORMS["p_main"], e14.schema("p_main")
    return common.FORMS["p_main"].system, e13.schema(False)


def requests(name, data=None, groups=None):
    exp = EXPERIMENTS[name]
    data = data or anth.multiwoz()
    groups = groups or ids()
    provider = accounts.ACCOUNTS[exp.account].provider
    dialogues = sorted({d for b in exp.blocks for g in b.groups if g != TRACKC for d in groups[g]})
    anth.assert_outside_trackp(dialogues, data)
    val, test = anth.splits()
    assert not set(dialogues) & (val | test), "a validation or test dialogue in a round-9 request"
    out = []
    for block in exp.blocks:
        for short, nums in block.reads.items():
            assert MODELS[short].provider == provider, f"{short} is not served by {exp.account}"
            for form in block.forms:
                for group in block.groups:
                    prompt, fmt = base(group)
                    text, form_fmt = system(prompt, FORMS[form]), schema(fmt, FORMS[form])
                    for unit, user in units(group, data, groups):
                        out += [request(short, f"{name}-{unit}-{form}-{r}-{short}", user, text, form_fmt) for r in nums]
    if provider in BATCH_LIMITS:
        most, size = BATCH_LIMITS[provider]
        body = sum(len(json.dumps(r)) for r in out)
        assert len(out) <= most and body < 0.9 * size, f"{name}: {len(out)} requests, {body / 1e6:.0f} MB in one batch"
    return out


def main(name):
    """The steps of the account's client. The pilot step runs only where r9_counts.py counts its calls."""
    exp = EXPERIMENTS[name]
    if sys.argv[1:2] == ["pilot"] and not exp.pilot:
        sys.exit(f"Not run. r9_counts.py counts no pilot calls for {name}; the X2 pilot P measures this task.")
    client = anth if accounts.ACCOUNTS[exp.account].provider == "anthropic" else oc
    client.main(name, lambda: requests(name), exp.planning_out, account=exp.account)


def write_ids():
    """Write ids.json once. A rerun checks that the rule still gives the same lists and changes nothing."""
    groups = compute_ids(anth.multiwoz())
    if IDS.exists():
        assert ids() == groups, f"{IDS} differs from the rule; the ids are fixed before any call"
        print(f"{IDS} matches the rule")
        return
    IDS.write_text(json.dumps({"seed": SEED, "groups": groups}, indent=0) + "\n")
    print(f"wrote {IDS}: " + ", ".join(f"{k} {len(v)}" for k, v in groups.items()))


if __name__ == "__main__":
    assert sys.argv[1:] == ["ids"], "Usage: python3 -I natural.py ids"
    write_ids()
