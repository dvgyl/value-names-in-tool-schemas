"""P, the token and format pilot of round 9 (ROUND9-EXPERIMENT-PLAN.md section 3, part of X2).

On each non-Claude panel model, 20 calls per task: natural dialogue (E13 `p_main` and its schema on seeded E11
dialogues), Track C (seeded E14 items and forms), and on-site (seeded E2 cases and arms). `gpt-6.1-sol` also reads the
same 60 units at its default effort. `gpt-6-astra` makes 24 annotation calls with the E3 prompt: 16 seeded E4 items and
8 seeded E7 dialogues, the 2:1 mix of X5. P runs synchronously at standard prices, because every X2 bound waits for it.
The scripts ep_oa.py and ep_di.py run it; ep_summary.py prints the result.
"""
import argparse
import functools
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import panel  # noqa: E402
import tasks  # noqa: E402
from panel import accounts, oc  # noqa: E402

PER_TASK = 20
TASK_MODELS = {"openai": ("sol", "soldef", "luna"), "deepinfra": ("dsv4", "qwen", "gemma")}
ANNOT_ITEMS, ANNOT_DIALOGUES = 16, 8
PLANNING_OUT = 4000  # the output cap of the extraction calls and the budget_v11.py size of an Astra annotation call
APIS = {"openai": oc.APIS["openai"]._replace(batch=False), "deepinfra": oc.APIS["deepinfra"]}
EXPECTED = {"openai": 3 * 3 * PER_TASK + ANNOT_ITEMS + ANNOT_DIALOGUES, "deepinfra": 3 * 3 * PER_TASK}
FOLDERS = {"openai": "ep_oa", "deepinfra": "ep_di"}


@functools.cache
def units():
    """The seeded units of each task, the same for every model, and the MultiWOZ dialogues that they hold."""
    data = panel.multiwoz()
    nat_ids = sorted(tasks.sample(tasks.common.e11_ids(data), PER_TASK, "p-natural"))
    table = tasks.onsite_table()
    system = tasks.codebook()
    annot_ids = sorted(tasks.sample(tasks.common.e7_ids(data), ANNOT_DIALOGUES, "p-annotation-dialogues"))
    out = {
        "nat": tasks.natural(nat_ids, data),
        "tc": [tasks.trackc(i, f) for i, f in tasks.sample(
            [(i, f) for i in tasks.templates.items() for f in tasks.templates.FORMS], PER_TASK, "p-trackc")],
        "os": [tasks.onsite(table, c, a) for c, a in tasks.sample(
            [(c, a) for c in table for a in tasks.e2.ARMS], PER_TASK, "p-onsite")],
        "an": [tasks.item_annotation(i, system) for i in tasks.sample(tasks.templates.items(), ANNOT_ITEMS,
                                                                       "p-annotation-items")]
              + [tasks.dialogue_annotation(d, data, system) for d in annot_ids],
    }
    return out, nat_ids + annot_ids


def cells(provider):
    """Every P request of one provider as (custom_id, task, model, prompt)."""
    by_task, ids = units()
    panel.guard(ids)
    out = [(f"ep-{task}-{s}-{p.key}", task, panel.MODELS[s], p)
           for s in TASK_MODELS[provider] for task in ("nat", "tc", "os") for p in by_task[task]]
    if provider == "openai":
        out += [(f"ep-an-astra-{p.key}", "an", panel.MODELS["astra"], p) for p in by_task["an"]]
    assert len(out) == EXPECTED[provider], len(out)
    return out


def build(provider):
    tasks.check_trackc_items()
    return [panel.request(m, cid, p) for cid, _, m, p in cells(provider)]


def sizes(name, task):
    """Write <name>/pilot.json from the P and P2 answers of one task and return the measured cells (panel.main)."""
    import ep_di2  # here, because ep_di2 imports this module
    measured = []
    for provider, folder in FOLDERS.items():
        got = panel.rows(folder)
        for cid, t, m, p in cells(provider) if got else ():
            if t == task and cid in got:
                req = panel.request(m, cid, p)
                measured.append(("|".join(oc.cell(req)), oc.est_in(req), got[cid]))
    got = panel.rows(ep_di2.NAME)
    for cid, t, m, p in ep_di2.cells() if got else ():  # P2 measured DeepSeek and Qwen with the settings of today's runs
        if t == task and cid in got:
            req = panel.ds.request(ep_di2.SETTINGS[m.short], cid, p.user, p.system, p.schema)
            measured.append(("|".join(oc.cell(req)), oc.est_in(req), got[cid]))
    return panel.write_sizes(name, measured, f"P and P2 raw.jsonl, task {task}")


def main(name, account):
    """estimate (offline) or run --approve <bound> (every request, synchronously, at standard prices)."""
    a = accounts.account(account, tuple(APIS))
    api = APIS[a.provider]
    accounts.folder(name)
    ap = argparse.ArgumentParser(description=f"{name}: token pilot P on {a.name}")
    ap.add_argument("step", choices=["estimate", "run"])
    ap.add_argument("--approve", help="the bound that the operator approved in writing")
    args = ap.parse_args()
    reqs = build(a.provider)
    oc.check_requests(reqs, api)
    if args.step == "estimate":
        in_flight = oc.WORKERS * max(oc.worst(api, r) for r in reqs)  # the reserve that `run` adds, so both print one bound
        oc.print_estimate(name, reqs, PLANNING_OUT, a, api, in_flight)
    else:
        oc.run(name, reqs, PLANNING_OUT, args.approve, a, api)
