"""X5, the independent check of the item readings (ROUND9-EXPERIMENT-PLAN.md section 3).

`claude-opus-5-5` (E3 settings: effort medium, max_tokens 16,000) and `gpt-6-astra` (panel.py) each read the same
seeded units with the E3 prompt (annot/codebook.md) and no model answer: 80 E4 items (both items of 10 seeded goals per
condition) and 40 seeded E7 training dialogues (read 1), and a seeded 20 of these 120 again (read 2). 140 calls each.
Scripts: ex5_an.py (Anthropic batch), ex5_oa.py (OpenAI batch). Analysis: ex5_analyze.py.
"""
import functools
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ep  # noqa: E402
import panel  # noqa: E402
import tasks  # noqa: E402
from panel import anth  # noqa: E402

GOALS_PER_CONDITION, DIALOGUES, REPEATS = 10, 40, 20
EXPECTED = 2 * GOALS_PER_CONDITION * 4 + DIALOGUES + REPEATS
SHORT = {"anthropic": "opus", "openai": "astra"}
PLANNING_OUT = {"anthropic": 900, "openai": 4000}  # E3 output mean 881.7 (e3/pilot.json); budget_v11.py Astra size


@functools.cache
def units():
    """The 120 seeded units of read 1, the 20 repeated units, and the MultiWOZ dialogues among them."""
    data = panel.multiwoz()
    system = tasks.codebook()
    goals = {g for c in tasks.templates.CONDITIONS for g in tasks.sample(
        sorted({i.goal.id for i in tasks.templates.items() if i.condition == c}), GOALS_PER_CONDITION, f"x5-goals-{c}")}
    ids = sorted(tasks.sample(tasks.common.e7_ids(data), DIALOGUES, "x5-dialogues"))
    first = ([tasks.item_annotation(i, system) for i in tasks.templates.items() if i.goal.id in goals]
             + [tasks.dialogue_annotation(d, data, system) for d in ids])
    return first, tasks.sample(first, REPEATS, "x5-repeats"), ids


def cells(provider):
    """Every request of one annotator as (custom_id, unit key, read, prompt)."""
    first, repeats, ids = units()
    panel.guard(ids)
    return [(f"ex5-{p.key}-r{read}-{SHORT[provider]}", p.key, read, p)
            for read, group in ((1, first), (2, repeats)) for p in group]


def build(provider):
    if provider == "anthropic":
        reqs = [anth.request(cid, tasks.e3.MODEL, tasks.e3.EFFORT, tasks.e3.MAX_TOKENS, user=p.user, system=p.system)
                for cid, _, _, p in cells(provider)]
    else:
        reqs = [panel.request(panel.MODELS["astra"], cid, p) for cid, _, _, p in cells(provider)]
    assert len(reqs) == EXPECTED, len(reqs)
    return reqs


def sizes(name, provider):
    if provider == "anthropic":  # E3: the same model, settings, and system prompt
        return panel.claude_sizes(name, "e3", lambda cid: True)
    return ep.sizes(name, "an")


def main(name, provider, account):
    panel.main(name, lambda: build(provider), PLANNING_OUT[provider], account=account,
               sizes=lambda: sizes(name, provider))
