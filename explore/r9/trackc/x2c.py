"""X2, Claim 2 (Track C) part (ROUND9-EXPERIMENT-PLAN.md section 3).

The 320 E4 items under `p_main`, `p_null`, `p_unclear`, and `p_option` with the E14 schemas (`p_option` has the
`p_unclear` schema). Reads: `gpt-6.1-sol` 2 and `gpt-6-luna` 3 (OpenAI batch); each DeepInfra model 1 (synchronous).
The Claude models run only `p_option` with the E14 settings: Haiku 7 reads, Sonnet 4 reads (Anthropic batch).
Scripts: ex2c_sol.py and ex2c_luna.py (one model per OpenAI batch; ex2c_oa failed on mixed models), ex2c_di.py, ex2c_an.py. Analysis: ex2c_analyze.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ep  # noqa: E402
import panel  # noqa: E402
import tasks  # noqa: E402
from panel import anth  # noqa: E402

FORMS = ("p_main", "p_null", "p_unclear", "p_option")
READS = {"sol": 2, "luna": 3, "dsv4": 1, "qwen": 1, "gemma": 1}
CLAUDE_READS = {"haiku": 7, "sonnet": 4}
PROVIDER_MODELS = {"openai": ("sol", "luna"), "deepinfra": ("dsv4", "qwen", "gemma")}
EXPECTED = {"openai": 320 * 4 * (2 + 3), "deepinfra": 320 * 4 * 3, "anthropic": 320 * (7 + 4)}
BY_ID = {m.id: m for m in panel.MODELS.values() if m.short != "soldef"}
PLANNING_OUT = {"openai": 550, "deepinfra": 350, "anthropic": 100}  # budget_v11.py: 50 visible plus the reasoning guess


def cells(provider, only=None):
    """Every request of one run as (custom_id, item, form, read, model id), the cell format of trackc/analyze.py."""
    items = tasks.templates.items()
    if provider == "anthropic":
        return [(f"ex2c-{item.id}-p_option-r{read}-{short}", item, "p_option", read, tasks.e14.SETTINGS[short][0])
                for short, reads in CLAUDE_READS.items() for item in items for read in range(1, reads + 1)]
    return [(f"ex2c-{item.id}-{form}-r{read}-{short}", item, form, read, panel.MODELS[short].id)
            for short in PROVIDER_MODELS[provider] if only in (None, short) for item in items for form in FORMS
            for read in range(1, READS[short] + 1)]


def build(provider, only=None):
    tasks.check_trackc_items()
    panel.guard(())  # the E4 items are built text and hold no MultiWOZ dialogue
    if provider == "anthropic":
        settings = {model: (thinking, effort) for model, thinking, effort in tasks.e14.SETTINGS.values()}
        reqs = [anth.request(cid, model, settings[model][1], tasks.e14.MAX_TOKENS, item.text, tasks.TRACKC_FORMS[form],
                             settings[model][0], tasks.trackc_schema(form))
                for cid, item, form, _, model in cells(provider)]
    else:
        reqs = [panel.request(BY_ID[model], cid, tasks.trackc(item, form)) for cid, item, form, _, model in cells(provider, only)]
    assert len(reqs) == (EXPECTED[provider] if only is None else 320 * len(FORMS) * READS[only]), len(reqs)
    return reqs


def sizes(name, provider):
    if provider == "anthropic":  # the E14 p_unclear rows: the same items, model, settings, and schema
        return panel.claude_sizes(name, "e14", lambda cid: "-p_unclear-" in cid)
    return ep.sizes(name, "tc")


def main(name, provider, account, only=None):
    panel.main(name, lambda: build(provider, only), PLANNING_OUT[provider], account=account,
               sizes=lambda: sizes(name, provider))
