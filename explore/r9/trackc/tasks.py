"""The four tasks of builder B as Prompt units: natural dialogue (E13), Track C (E14 and p_option), on-site (E2), and
annotation (E3). Every prompt and schema is the one of the earlier run; only p_option is new.
"""
import functools
import importlib.util
import json
import random
import sys

import panel

for sub in ("forms", "trackc", "pmain", "onsite", "annot"):
    sys.path.insert(0, str(panel.EXPLORE / sub))
import check_items  # noqa: E402
import common  # noqa: E402
import e2  # noqa: E402
import e3  # noqa: E402
import e13  # noqa: E402
import e14  # noqa: E402
import templates  # noqa: E402

ANNOT_MAX_TOKENS = e3.MAX_TOKENS  # 16,000, as E3; PLAN.md SI-17 asks for at least 8,000

# p_option: the "unclear" value in the schema, and no sentence about ambiguity. It is p_unclear without that sentence.
P_OPTION = templates.FORMS["p_unclear"].replace(templates.AMBIGUITY, "")
TRACKC_FORMS = {**templates.FORMS, "p_option": P_OPTION}


def load(path, name):
    """A module from a file path under its own name. trackc, forms, onsite, and annot all hold an analyze.py."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def trackc_schema(form):
    """The E14 schema in the format of anth.request. p_option takes the p_unclear schema, which offers "unclear"."""
    return e14.schema("p_unclear" if form == "p_option" else form)


@functools.cache  # about 40 s; the items are fixed while a process runs
def check_trackc_items():
    failed = [(name, bad) for name, _, bad in check_items.check() if bad]
    assert not failed, f"item checks fail, run trackc/check_items.py: {failed[0][0]}"


def natural(ids, data):
    """E13 `p_main` and its schema on MultiWOZ dialogues."""
    form = common.FORMS["p_main"]
    schema = e13.schema(form.renamed)["schema"]
    return [panel.Prompt(d.removesuffix(".json"), common.dialogue_text(data[d]), form.system, schema, panel.MAX_TOKENS)
            for d in ids]


def trackc(item, form):
    return panel.Prompt(f"{item.id}-{form}", item.text, TRACKC_FORMS[form], trackc_schema(form)["schema"],
                        panel.MAX_TOKENS)


def onsite_table():
    """The frozen E2 prompts: {case_id: {arm: {"system", "user"}}}. E2 sent no schema, so no schema goes here."""
    table = json.loads(e2.PROMPTS.read_text())
    assert len(table) == 38 and all(tuple(arms) == e2.ARMS for arms in table.values()), "prompts.json is not the E2 table"
    return table


def onsite(table, case_id, arm):
    p = table[case_id][arm]
    return panel.Prompt(f"{case_id}-{arm}", p["user"], p["system"], None, panel.MAX_TOKENS)


def codebook():
    """The E3 annotator prompt. It must equal the system prompt that E3 sent, byte for byte."""
    text = e3.CODEBOOK.read_text()
    sent = json.loads((panel.EXPLORE / "e3" / "requests.jsonl").open().readline())["params"]["system"]
    assert text == sent, "annot/codebook.md changed after E3"
    return text


def annotation(key, text, system):
    return panel.Prompt(key, text, system, None, ANNOT_MAX_TOKENS)


def item_annotation(item, system):
    return annotation(item.id, item.text, system)


def dialogue_annotation(dialogue_id, data, system):
    return annotation(dialogue_id.removesuffix(".json"), common.dialogue_text(data[dialogue_id]), system)


def sample(population, k, label):
    """A seeded sample. Each sample has its own seed, so a change to one sample leaves the others the same."""
    return random.Random(f"20261103-{label}").sample(list(population), k)
