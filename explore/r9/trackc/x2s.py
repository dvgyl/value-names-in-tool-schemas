"""X2, on-site part (ROUND9-EXPERIMENT-PLAN.md section 3).

The 38 E2 cases x 3 arms (orig, office, renamed) x 5 reads on the 5 non-Claude models, with the frozen E2 prompts
(onsite/prompts.json) and no schema, as E2. OpenAI batch for `gpt-6.1-sol` and `gpt-6-luna`; synchronous on DeepInfra.
The custom_id has the E2 format, so onsite/analyze.py scores the rows (ex2s_analyze.py).
Scripts: ex2s_sol.py and ex2s_luna.py (one model per OpenAI batch; ex2s_oa failed on mixed models), ex2s_di.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ep  # noqa: E402
import panel  # noqa: E402
import tasks  # noqa: E402

PROVIDER_MODELS = {"openai": ("sol", "luna"), "deepinfra": ("dsv4", "qwen", "gemma")}
EXPECTED = {"openai": 38 * 3 * 5 * 2, "deepinfra": 38 * 3 * 5 * 3}
PLANNING_OUT = {"openai": 800, "deepinfra": 600}  # budget_v11.py and r9_costs.py: 300 visible plus the reasoning guess


def cells(provider, table, only=None):
    """Every request of one run as (custom_id, case_id, arm, read, model short)."""
    return [(tasks.e2.custom_id(short, arm, read, case), case, arm, read, short)
            for short in PROVIDER_MODELS[provider] if only in (None, short) for case in table for arm in tasks.e2.ARMS for read in tasks.e2.READS]


def build(provider, only=None):
    panel.guard(())  # the E2 cases are SIB cases and hold no MultiWOZ dialogue
    table = tasks.onsite_table()
    reqs = [panel.request(panel.MODELS[short], cid, tasks.onsite(table, case, arm))
            for cid, case, arm, _, short in cells(provider, table, only)]
    assert len(reqs) == (EXPECTED[provider] if only is None else 38 * 3 * 5), len(reqs)
    return reqs


def main(name, provider, account, only=None):
    panel.main(name, lambda: build(provider, only), PLANNING_OUT[provider], account=account,
               sizes=lambda: ep.sizes(name, "os"))
