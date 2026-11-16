"""Requests of the round-9 additions Z1 to Z3 and the balance runs B2 to B4 (ROUND9-ADDITIONS.md sections 3 and 9).

A run is one experiment folder at the explore root on one account. RUNS describes each run as blocks of (dialogue
group, cells, reads per model). A thin script per run, for example `ez1_claude.py`, calls `main()`, so `lib/watch.py`
can run its fetch step. The request count per model plus the pilot equals `review/plan13/r9_counts.py --balance`.
"""
import collections
import random
import re
import sys
from typing import NamedTuple

import zforms
from zforms import anth, common, e13

sys.path.insert(0, str(zforms.EXPLORE / "lib"))
sys.path.insert(0, str(zforms.EXPLORE / "r9"))
import accounts  # noqa: E402
import deepinfra_settings as ds  # noqa: E402
import openai_compat as oc  # noqa: E402

FRAME_SEED = 20261103  # draws the 500 frame dialogues; fixed before any pilot
OTHER_MAX_TOKENS = 4000  # SYN-S5 section 3.2 and PLAN SI-02: 4,000 GPT output tokens, reasoning included


class Groups(NamedTuple):
    t994: list  # the E11 dialogues by the traveller-turns rule
    frame500: list  # a seeded 500 of t994 (Z1 frame part)
    booked: list  # the 554 dialogues of t994 whose booked venue is in hotel_db.json (Z2)
    s1: list  # the 1,136 E11 dialogues by the all-turns rule (X1 group S1)
    rest: list  # the other 1,738 E7 dialogues (X1 groups S2 to S5)
    s2: list  # the 545 E7 dialogues whose gold type is hotel (X1 group S2)
    venue: dict  # E7 dialogue -> the hotel_db.json entry of its last booked venue (only matched bookings)
    brief: dict  # E7 dialogue -> the brief type, goal.hotel.info.type: "hotel", "guesthouse", or None


def _key(name):
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("&", "and"))


def booked_venue(d, by_key):
    """The last booked hotel name of the dialogue state, matched to hotel_db.json as in review/plan13/revealed_r9b.py."""
    names = [b["name"] for t in d["log"] for b in ((t.get("metadata") or {}).get("hotel", {}).get("book", {})
                                                   .get("booked") or []) if b.get("name")]
    return by_key.get(_key(names[-1])) if names else None


def brief_type(d):
    value = d["goal"].get("hotel", {}).get("info", {}).get("type")
    return common.norm_value("type", value) if value else None


def groups(data):
    e7 = common.e7_ids(data)
    s1 = common.e11_ids(data)
    t994 = [i for i in s1 if any(zforms.WORD.search(t["text"]) for k, t in enumerate(data[i]["log"]) if k % 2 == 0)]
    by_key = {_key(h["name"]): h for h in zforms.HOTELS}
    venue = {i: v for i in e7 if (v := booked_venue(data[i], by_key))}
    rest = sorted(set(e7) - set(s1))
    g = Groups(t994, sorted(random.Random(FRAME_SEED).sample(t994, 500)), [i for i in t994 if i in venue], s1, rest,
               [i for i in e7 if common.gold_form(data[i])["type"] == ("hotel",)], venue,
               {i: brief_type(data[i]) for i in e7})
    sizes = {"t994": 994, "frame500": 500, "booked": 554, "s1": 1136, "rest": 1738, "s2": 545}
    assert {k: len(getattr(g, k)) for k in sizes} == sizes, {k: len(getattr(g, k)) for k in sizes}
    return g


# Model settings. Claude takes the E13 settings. GPT takes PLAN SI-02 and SYN-S5 section 3.2 (budget_v11.py has no
# decoding settings). The open models take r9/deepinfra_settings.py.
def claude(short):
    thinking, effort = e13.SETTINGS[short]
    return lambda cid, system, user, schema: anth.request(cid, common.MODELS[short], effort, e13.MAX_TOKENS, user,
                                                          system, thinking, {"type": "json_schema", "schema": schema})


def gpt(model, effort):
    return lambda cid, system, user, schema: oc.openai_request(cid, model, effort, OTHER_MAX_TOKENS, user, system,
                                                               schema)


def open_model(model):
    return lambda cid, system, user, schema: ds.request(model, cid, user, system, schema)


MODELS = {
    "haiku": claude("haiku"),  # thinking disabled, effort medium
    "sonnet": claude("sonnet"),  # thinking between_tools, effort high
    "luna": gpt("gpt-6-luna", "none"),
    "sol": gpt("gpt-6.1-sol", "low"),
    "deepseek": open_model(ds.DEEPSEEK),
    "qwen": open_model(ds.QWEN),
    "gemma": open_model(ds.GEMMA),
}


class Cell(NamedTuple):
    text: str  # a key of zforms.TEXTS
    frame: str  # "hotel" (as written) or "accommodation" (zforms.framed)
    form: str  # a key of zforms.FORMS


CELLS = {
    "orig_f0": Cell("orig", "hotel", "f0"), "orig_f1": Cell("orig", "hotel", "f1"),  # read in E13, X1, and X2
    "edit_f0": Cell("edit", "hotel", "f0"), "edit_f1": Cell("edit", "hotel", "f1"),
    "acc_orig_f0": Cell("orig", "accommodation", "f0"), "acc_orig_f1": Cell("orig", "accommodation", "f1"),
    "acc_edit_f0": Cell("edit", "accommodation", "f0"), "acc_edit_f1": Cell("edit", "accommodation", "f1"),
    "pre_f0": Cell("prefix", "hotel", "f0"), "pre_f1": Cell("prefix", "hotel", "f1"),
    "pre_unclear": Cell("prefix", "hotel", "p_unclear_nat"), "pre_probe": Cell("prefix", "hotel", "probe"),
    **{f: Cell("orig", "hotel", f) for f in ("p_define", "p_split", "p_null_nat", "p_unclear_nat")},
}
EDIT = ("edit_f0", "edit_f1")
FRAMED = ("acc_orig_f0", "acc_orig_f1", "acc_edit_f0", "acc_edit_f1")
PREFIX = ("pre_f0", "pre_f1", "pre_unclear")
FIXES = ("p_define", "p_split", "p_null_nat", "p_unclear_nat")
OPEN = {"deepseek": 1, "qwen": 1, "gemma": 1}


class Block(NamedTuple):
    group: str  # a field of Groups
    cells: tuple  # keys of CELLS
    reads: dict  # model short name -> reads


class Run(NamedTuple):
    account: str
    blocks: tuple
    counts: dict  # batch requests per model; plus `pilot`, this equals r9_counts.py --balance
    pilot: int  # synchronous pilot calls per model (Claude only; r9_counts.py counts no other pilot)
    planning_out: int  # output tokens per call until a pilot measures them (budget_v11.py guesses, E13 for Claude)


RUNS = {
    "ez1_claude": Run("anthropic_r9b", (Block("t994", EDIT, {"haiku": 3, "sonnet": 3}),
                                        Block("frame500", FRAMED, {"haiku": 3, "sonnet": 3})),
                      {"haiku": 11964, "sonnet": 11964}, 40, 100),
    "ez1_luna": Run("openai_r9", (Block("t994", EDIT, {"luna": 3}), Block("frame500", FRAMED, {"luna": 3})),
                    {"luna": 11964}, 0, 56),
    "ez2_claude": Run("anthropic_r9b", (Block("booked", PREFIX + ("pre_probe",), {"haiku": 3, "sonnet": 3}),),
                      {"haiku": 6648, "sonnet": 6648}, 40, 100),
    "ez2_luna": Run("openai_r9", (Block("booked", PREFIX, {"luna": 3}),), {"luna": 4986}, 0, 56),
    # Z3 on Claude is one folder per model: one batch of both would hold 252 MB, against the 256 MB batch limit.
    "ez3_haiku": Run("anthropic_r9b", (Block("s1", FIXES, {"haiku": 3}), Block("rest", FIXES, {"haiku": 3})),
                     {"haiku": 34488}, 80, 100),
    "ez3_sonnet": Run("anthropic_r9b", (Block("s1", FIXES, {"sonnet": 3}), Block("rest", FIXES, {"sonnet": 2})),
                      {"sonnet": 27536}, 80, 100),
    "ez3_luna": Run("openai_r9", (Block("s1", FIXES, {"luna": 3}), Block("rest", FIXES, {"luna": 3})),
                    {"luna": 34488}, 0, 56),
    # Sol parts are separate folders, so they can run in the order B2, B1, B3, B4 while the OpenAI money lasts.
    # planning_out: 56 visible tokens plus the budget_v11.py reasoning guess (Sol 500; DeepSeek 300, the largest of the
    # three open models).
    "eb2_sol": Run("openai_r9", (Block("t994", EDIT, {"sol": 1}),), {"sol": 1988}, 0, 556),
    "eb2_open": Run("deepinfra", (Block("t994", EDIT, OPEN),), dict.fromkeys(OPEN, 1988), 0, 356),
    "eb3_sol": Run("openai_r9", (Block("booked", PREFIX, {"sol": 1}),), {"sol": 1662}, 0, 556),
    "eb3_open": Run("deepinfra", (Block("booked", PREFIX, OPEN),), dict.fromkeys(OPEN, 1662), 0, 356),
    "eb4_sol": Run("openai_r9", (Block("s1", ("p_split", "p_define"), {"sol": 1}),), {"sol": 2272}, 0, 556),
    "eb4_open": Run("deepinfra", (Block("s1", FIXES, OPEN), Block("s2", FIXES, OPEN)), dict.fromkeys(OPEN, 6724), 0,
                    356),
}


def custom_id(name, dialogue, cell, read, model):
    return f"{name}-{dialogue.removesuffix('.json')}-{cell}-{read}-{model}"


def request(name, data, dialogue, cell, read, model):
    c = CELLS[cell]
    form = zforms.FORMS[c.form]
    system = zforms.framed(form.system) if c.frame == "accommodation" else form.system
    return MODELS[model](custom_id(name, dialogue, cell, read, model), system, zforms.TEXTS[c.text](data[dialogue]),
                         form.schema)


def requests(name, data=None, g=None):
    """Every batch request of the run, with the guard of the round-9 build brief."""
    run = RUNS[name]
    data = data or anth.multiwoz()
    g = g or groups(data)
    ids = sorted({i for b in run.blocks for i in getattr(g, b.group)})
    anth.assert_outside_trackp(ids, data)
    val, test = anth.splits()
    assert not set(ids) & (val | test), "a validation or test dialogue in a round-9 request set"
    reqs = [request(name, data, i, cell, read, model) for b in run.blocks for model, reads in b.reads.items()
            for cell in b.cells for i in getattr(g, b.group) for read in range(1, reads + 1)]
    counts = collections.Counter(common.split_custom_id(r["custom_id"])[4] for r in reqs)
    assert counts == run.counts, (name, dict(counts), run.counts)
    return reqs


def main(name):
    """The steps of lib/anth.py (Claude) or lib/openai_compat.py (OpenAI, DeepInfra) for one run."""
    run = RUNS[name]
    provider = accounts.ACCOUNTS[run.account].provider
    if provider == "anthropic":
        anth.PILOT_PER_CELL = run.pilot  # one (model, effort) cell per Claude model, so this is the pilot per model
        return anth.main(name, lambda: requests(name), run.planning_out, account=run.account)
    if sys.argv[1:2] == ["pilot"]:
        sys.exit(f"Not run. r9_counts.py counts no pilot for {name}. To use measured sizes, run "
                 f"r9/trackc/di_sizes.py before the estimate.")
    return oc.main(name, lambda: requests(name), run.planning_out, account=run.account)

