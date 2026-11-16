"""Revision 12, wave 1: the sealed natural and Track P collection (REVISION-12.md sections 4 and 6).

The split. One seeded order over the 687 multi-domain hotel dialogues of the validation and test sets (PLAN SI-15a).
The seed is the SHA-256 of SEED_TEXT, fixed in registration A before any call. The gate set is the first 64 dialogues
and gets no call. The rest is the pool, in the same order. The Track P sample is the first 144 dialogues of the pool.

The parts, each read once, and a seeded 20% of its units three times, the same 20% for every form (DECISIONS-R7 item 7):
- nat: the H4 natural sample, every natural-list dialogue outside the gate set, forms t_legacy, t_renamed,
  t_described, and f4.
- plc: the same dialogues under the placebo f5, Claude only (D4).
- hot: every pool dialogue whose goal sets `type` = `hotel`, outside the gate set, the same 4 forms (D2).
- pre: the nat dialogues up to and including the first traveller turn with "hotel", the same 4 forms (D5).
- tp: the Track P sample, `p_main` and `p_unclear`.

One folder per model, `em1_<model>`. Its name starts with "em", so lib/seal.py seals every answer.
Usage: python3 -I main/wave1.py ids | manifest      (offline)
       python3 -I main/em1_<model>.py estimate | pilot | submit | run | fetch   (the client steps)
"""
import hashlib
import json
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "trackc", "r9", "r9/natural", "r9/additions"):
    sys.path.insert(0, str(EXPLORE / sub))
import accounts  # noqa: E402
import anth  # noqa: E402
import common  # noqa: E402
import e13  # noqa: E402
import natural  # noqa: E402
import zforms  # noqa: E402

SEED_TEXT = "Semantic Integrity revision 12, Track P split, 2026-11-04"
SEED = int(hashlib.sha256(SEED_TEXT.encode()).hexdigest()[:16], 16)
GATE, SAMPLE, REPEAT, REPEAT_READS = 64, 144, 0.2, 3
IDS = HERE / "wave1_ids.json"
MANIFEST = HERE / "wave1_manifest.json"

DESCRIPTIONS = (  # t_described (PLAN SI-05): one line per field; registration A shows it for the operator's review
    " Field descriptions: name is the hotel that the traveller asks for by name. area is the part of town. pricerange"
    " is the price level. stars is the star rating. type is the kind of venue in the database. parking is whether"
    " the venue must have free parking. internet is whether the venue must have free internet.")


def wrap(inner):
    return {"type": "json_schema", "schema": inner}


F0 = natural.system(common.FORMS["p_main"].system, natural.FORMS["f0"])
FORMS = {  # name -> (system prompt, output format, parser form of natural.py)
    "t_legacy": (F0, e13.schema(False), "f0"),
    "t_renamed": (natural.system(common.FORMS["p_main"].system, natural.FORMS["f1"]),
                  natural.schema(e13.schema(False), natural.FORMS["f1"]), "f1"),
    "t_described": (zforms.once(F0, zforms.ALLOWED_END, zforms.ALLOWED_END + DESCRIPTIONS), e13.schema(False), "f0"),
    "f4": (natural.system(common.FORMS["p_main"].system, natural.FORMS["f4"]),
           natural.schema(e13.schema(False), natural.FORMS["f4"]), "f4"),
    "f5": (natural.system(common.FORMS["p_main"].system, natural.FORMS["f5"]),
           natural.schema(e13.schema(False), natural.FORMS["f5"]), "f5"),
    "p_main": (common.FORMS["p_main"].system, e13.schema(False), "f0"),
    "p_unclear": (common.FORMS["p_main"].system.replace(*common.UNCLEAR), wrap(zforms.schema(words=("any", "unclear"))),
                  "f0"),
}
NAT = ("t_legacy", "t_renamed", "t_described", "f4")
CLAUDE = ("haiku", "sonnet")
PARTS = {  # part -> (id list, forms, text, models or None for all)
    "nat": ("natural", NAT, "orig", None),
    "plc": ("natural", ("f5",), "orig", CLAUDE),
    "hot": ("goal_hotel", NAT, "orig", None),
    "pre": ("natural", NAT, "prefix", None),
    "tp": ("sample", ("p_main", "p_unclear"), "orig", None),
}
ACCOUNT = {"sonnet": "anthropic_r9a", "haiku": "anthropic_r9b", "sol": "openai_r9", "luna": "openai_r9",
           "deepseek": "deepinfra_main", "qwen": "deepinfra_main", "gemma": "deepinfra_main", "gemini": "google"}
# E13 means; round-9 GPT and DeepInfra sizes; Gemini: budget_v11.py VISIBLE_OUT 300 plus its 500-token reasoning guess
PLANNING_OUT = {"anthropic": 60, "openai": 400, "deepinfra": 300, "google": 800}


def goal_types(d):
    g = d["goal"]["hotel"]
    return {g.get(part, {}).get("type") for part in ("info", "fail_info")} - {None}


def traveller_says_hotel(d):
    return bool(natural.WORD.search(" ".join(t["text"] for i, t in enumerate(d["log"]) if i % 2 == 0)))


def compute_ids(data):
    pool = sorted(anth.trackp_pool(data))
    order = pool[:]
    random.Random(SEED).shuffle(order)
    gate, rest = order[:GATE], order[GATE:]
    lists = {
        "gate": gate,
        "pool": rest,
        "sample": rest[:SAMPLE],
        # natural_count.py rule (DECISIONS-R5): goal sets no type, the word in the traveller turns
        "natural": [k for k in rest if not goal_types(data[k]) and traveller_says_hotel(data[k])],
        "goal_hotel": [k for k in rest if "hotel" in goal_types(data[k])],
    }
    rng = random.Random(SEED + 1)
    for name in ("natural", "goal_hotel", "sample"):
        lists[f"{name}_repeat"] = sorted(rng.sample(sorted(lists[name]), math.ceil(REPEAT * len(lists[name]))))
    return lists


def ids():
    return json.loads(IDS.read_text())


def write_ids():
    lists = compute_ids(anth.multiwoz())
    if IDS.exists():
        assert ids() == lists, f"{IDS} differs from the rule; the ids are fixed before any call"
    else:
        IDS.write_text(json.dumps(lists, indent=1))
    print({k: len(v) for k, v in lists.items()})


TEXTS = {"orig": common.dialogue_text, "prefix": zforms.prefix_text}


def requests(short, data=None, lists=None):
    data, lists = data or anth.multiwoz(), lists or ids()
    gate = set(lists["gate"])
    name, out = f"em1_{short}", []
    for part, (key, forms, text, models) in PARTS.items():
        if models and short not in models:
            continue
        units = lists[key]
        assert not gate & set(units), f"{part}: a gate-set dialogue in a request"
        repeat = set(lists[f"{key}_repeat"])
        for form in forms:
            system, fmt, _ = FORMS[form]
            for d in units:
                user = TEXTS[text](data[d])
                for r in range(1, (REPEAT_READS if d in repeat else 1) + 1):
                    out.append(natural.request(short, f"{name}-{part}-{d.removesuffix('.json')}-{form}-{r}",
                                               user, system, fmt))
    return out


def digest(reqs):
    return hashlib.sha256("".join(json.dumps(r, sort_keys=True) + "\n" for r in reqs).encode()).hexdigest()


def write_manifest():
    data, lists = anth.multiwoz(), ids()
    folders = {}
    for short in ACCOUNT:
        reqs = requests(short, data, lists)
        folders[f"em1_{short}"] = {"account": ACCOUNT[short], "model": natural.MODELS[short].id,
                                   "requests": len(reqs), "sha256": digest(reqs)}
    forms = {f: hashlib.sha256((s + json.dumps(fmt, sort_keys=True)).encode()).hexdigest() for f, (s, fmt, _) in FORMS.items()}
    manifest = {"seed_text": SEED_TEXT, "seed": SEED, "counts": {k: len(v) for k, v in lists.items()},
                "ids_sha256": hashlib.sha256(IDS.read_bytes()).hexdigest(), "forms_sha256": forms, "folders": folders}
    MANIFEST.write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest, indent=1))


def main(short):
    a = accounts.ACCOUNTS[ACCOUNT[short]]
    client = anth if a.provider == "anthropic" else natural.oc
    client.main(f"em1_{short}", lambda: requests(short), PLANNING_OUT[a.provider], account=a.name)


if __name__ == "__main__":
    {"ids": write_ids, "manifest": write_manifest}[sys.argv[1]]()
