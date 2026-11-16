"""Request builders of the X3 and Z4 runs (PROTOCOL.md section "X3 and Z4" and amendment 1; r9_counts.py).

Each request reads one instance (a selected pair and one of its dialogues) under the original or the neutral form of
the pair. The instances come from `selection.json`, which `table.py` fixed before any call.
Claude settings are those of pmain/e13.py. The GPT settings are those of PLAN.md SI-09 and
research/out/SYN-S5-models-infra.md section 3.2: no temperature, `gpt-6.1-sol` effort low, `gpt-6-luna` effort none,
output cap 4,000. The open-model settings are those of r9/deepinfra_settings.py.
"""
import json
import pathlib
import sys
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parents[1]
sys.path.insert(0, str(EXPLORE / "forms"))
sys.path.insert(0, str(EXPLORE / "lib"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402
import deepinfra_settings as ds  # noqa: E402
import openai_compat as oc  # noqa: E402
from common import anth  # noqa: E402
import forms  # noqa: E402

SELECTION = HERE / "selection.json"
CLAUDE_MAX, GPT_MAX = 4096, 4000
VARIANTS = ("orig", "neut")


class Model(NamedTuple):
    provider: str  # "anthropic", "openai", or "deepinfra"
    model: str
    effort: str  # Anthropic and OpenAI effort; "" for DeepInfra
    options: dict  # Anthropic: thinking; DeepInfra: {} (deepinfra_settings)


MODELS = {
    "haiku": Model("anthropic", "claude-haiku-5-5", "medium", {"type": "disabled"}),
    "sonnet": Model("anthropic", "claude-sonnet-5-5", "high", {"type": "between_tools"}),
    "luna": Model("openai", "gpt-6-luna", "none", {}),
    "sol": Model("openai", "gpt-6.1-sol", "low", {}),
    "deepseek": Model("deepinfra", ds.DEEPSEEK.id, "", {}),
    "qwen": Model("deepinfra", ds.QWEN.id, "", {}),
    "gemma": Model("deepinfra", ds.GEMMA.id, "", {}),
}


class Run(NamedTuple):
    instances: str  # the instance list of selection.json: "x3", "x3_deepinfra", or "z4"
    reads: dict  # model short name -> reads
    account: str
    planning_out: int  # output tokens per call before a pilot; reasoning tokens included (budget_v11.py guesses)


RUNS = {
    "ex3c": Run("x3", {"haiku": 3, "sonnet": 2}, "anthropic_r9a", 100),
    "ex3l": Run("x3", {"luna": 3}, "openai_r9", 100),
    "ex3s": Run("x3", {"sol": 1}, "openai_r9", 556),
    "ex3d": Run("x3_deepinfra", {"deepseek": 1, "qwen": 1, "gemma": 1}, "deepinfra", 356),
    "ez4c": Run("z4", {"haiku": 3, "sonnet": 2}, "anthropic_r9b", 100),
    "ez4l": Run("z4", {"luna": 3}, "openai_r9", 100),
}
# X3: review/plan13/r9_counts.py --balance, column X3 (test_runs.py checks it against that script). Z4: PROTOCOL.md
# amendment 1 replaces the 720 instances of r9_counts.py with 120 for each of the 13 Z4 pairs that X3 does not read.
EXPECTED = {"ex3c": {"haiku": 7200, "sonnet": 4800}, "ex3l": {"luna": 7200}, "ex3s": {"sol": 2400},
            "ex3d": {"deepseek": 1200, "qwen": 1200, "gemma": 1200}, "ez4c": {"haiku": 9360, "sonnet": 6240},
            "ez4l": {"luna": 9360}}


def selection():
    return json.loads(SELECTION.read_text())


def pair_form(p, variant):
    return forms.form(p["domain"], p["slot"], p["value"], p["neutral"] if variant == "neut" else None)


def instances(sel, key):
    return [(p, d) for p in sel["pairs"] for d in p.get(key, [])]


def custom_id(exp, dialogue, pair_id, variant, read, short):
    return f"{exp}-{dialogue.removesuffix('.json')}-{pair_id}-{variant}-{read}-{short}"


def split_custom_id(cid):
    exp, dialogue, pair_id, variant, read, short = cid.split("-")
    return exp, dialogue + ".json", pair_id, variant, int(read), short


def request(cid, m, f, user):
    if m.provider == "anthropic":
        return anth.request(cid, m.model, m.effort, CLAUDE_MAX, user, f.system, m.options,
                            {"type": "json_schema", "schema": f.schema})
    if m.provider == "openai":
        return oc.openai_request(cid, m.model, m.effort, GPT_MAX, user, f.system, f.schema)
    return ds.request(ds.MODELS[m.model], cid, user, f.system, f.schema)


def build(exp, data=None, sel=None):
    run, sel = RUNS[exp], sel or selection()
    data = data or anth.multiwoz()
    todo = instances(sel, run.instances)
    ids = sorted({d for _, d in todo})
    val, test = anth.splits()
    assert not set(ids) & (val | test), "a validation or test dialogue in a request set"
    anth.assert_outside_trackp(ids, data)
    providers = {MODELS[s].provider for s in run.reads}
    assert len(providers) == 1, f"one experiment folder holds one account: {providers}"
    reqs = []
    for short, reads in run.reads.items():
        for variant in VARIANTS:
            fs = {p["id"]: pair_form(p, variant) for p in sel["pairs"]}
            for p, d in todo:
                for read in range(1, reads + 1):
                    cid = custom_id(exp, d, p["id"], variant, read, short)
                    reqs.append(request(cid, MODELS[short], fs[p["id"]], common.dialogue_text(data[d])))
    counts = {s: sum(r["custom_id"].endswith(f"-{s}") for r in reqs) for s in run.reads}
    assert counts == EXPECTED[exp], (exp, counts, EXPECTED[exp])
    return reqs


def main(exp):
    run = RUNS[exp]
    builder = lambda: build(exp)
    if MODELS[next(iter(run.reads))].provider == "anthropic":
        anth.main(exp, builder, planning_out=run.planning_out, account=run.account)
    else:
        oc.main(exp, builder, planning_out=run.planning_out, account=run.account)
