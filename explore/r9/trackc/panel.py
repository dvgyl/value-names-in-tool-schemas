"""Round-9 builder B: the panel settings, the request builder, the data guard, and the step wrapper (BUILD_BRIEF.md).

The settings of the GPT models come from ../../PLAN.md SI-02 and SI-09, which use
../../research/out/SYN-S5-models-infra.md section 3.2, and from ../../budget_v11.py. UNVERIFIED marks a setting that
no document or run confirms. The settings of the open models are in r9/deepinfra_settings.py.

Every experiment script of this folder gives its sizes and calls `main()`. `main()` has no `pilot` step, because the
token pilot P (and E14 and E3 for the Claude runs) measured the sizes, and r9_counts.py counts no other pilot call.
"""
import functools
import json
import pathlib
import statistics
import sys
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parents[1]
sys.path.insert(0, str(EXPLORE / "lib"))
sys.path.insert(0, str(HERE.parent))
import accounts  # noqa: E402
import anth  # noqa: E402
import deepinfra_settings as ds  # noqa: E402
import openai_compat as oc  # noqa: E402

MAX_TOKENS = 4000  # PLAN.md SI-02 and SYN-S5 3.2: the output cap of every GPT extraction call, reasoning included


class Model(NamedTuple):
    short: str  # the model tag in a custom_id; no "_", because the E2 custom_id splits on "_"
    id: str  # the model id that the provider takes
    provider: str  # a key of oc.APIS
    options: dict  # openai: {"effort": value or None (the provider default)}; deepinfra: {} (deepinfra_settings)


MODELS = {m.short: m for m in (
    Model("sol", "gpt-6.1-sol", "openai", {"effort": "low"}),  # SYN-S5 3.2
    Model("soldef", "gpt-6.1-sol", "openai", {"effort": None}),  # PLAN.md SI-09: Sol at its default effort (N7)
    Model("luna", "gpt-6-luna", "openai", {"effort": "none"}),  # SYN-S5 3.2
    # SYN-S5 3.2 gives Astra effort low for gating. UNVERIFIED: that the annotation calls (SI-17) use the same effort.
    Model("astra", "gpt-6-astra", "openai", {"effort": "low"}),
    Model("dsv4", ds.DEEPSEEK.id, "deepinfra", {}),
    Model("qwen", ds.QWEN.id, "deepinfra", {}),
    Model("gemma", ds.GEMMA.id, "deepinfra", {}),
)}


class Prompt(NamedTuple):
    key: str  # the unit part of a custom_id
    user: str
    system: str
    schema: dict | None  # the JSON schema for strict structured output, or None for a free-text reply
    max_tokens: int  # the GPT output cap; a DeepInfra request takes the cap of deepinfra_settings


def request(model, custom_id, p):
    if model.provider == "openai":
        r = oc.openai_request(custom_id, model.id, model.options["effort"] or "low", p.max_tokens, p.user, p.system,
                              p.schema)
        if model.options["effort"] is None:
            del r["body"]["reasoning"]  # no reasoning field, so the model runs at its default effort
        return r
    return ds.request(ds.MODELS[model.id], custom_id, p.user, p.system, p.schema)


@functools.cache
def multiwoz():
    """MultiWOZ data.json, read once per process (about 13 s from the external drive)."""
    return anth.multiwoz()


def guard(dialogue_ids):
    """BUILD_BRIEF.md rule 3: no Track P, gate-set, validation, or test dialogue goes into a request."""
    anth.assert_outside_trackp(dialogue_ids, multiwoz())
    val, test = anth.splits()
    hit = set(dialogue_ids) & (val | test)
    assert not hit, f"{len(hit)} validation or test dialogues in a request set, for example {sorted(hit)[:3]}"


def write_sizes(name, measured, source):
    """Write <name>/pilot.json in the format of anth.pilot from measured rows. `measured` holds (cell key, estimated
    input, raw.jsonl row) triples. A DeepInfra row counts as deepinfra_settings.projected gives it. Return the cells
    that have at least one answer."""
    groups = {}
    for key, est, row in measured:
        model = ds.MODELS.get(key.split("|")[0])
        if row.get("type") == "succeeded" and model:
            row = ds.projected(row, model)
        if row and row.get("type") == "succeeded":
            groups.setdefault(key, []).append((est, row))
    sizes = {key: {"in_ratio": sum(r["input_tokens"] for _, r in v) / sum(e for e, _ in v),
                   "out_mean": statistics.fmean(r["output_tokens"] for _, r in v),
                   "out_max": max(r["output_tokens"] for _, r in v),
                   "reasoning_mean": statistics.fmean(r.get("reasoning_tokens", 0) for _, r in v),
                   "stops": sorted({r["stop"] for _, r in v}), "n": len(v), "source": source}
             for key, v in sorted(groups.items())}
    if sizes:
        anth.pilot_path(name).parent.mkdir(parents=True, exist_ok=True)
        anth.pilot_path(name).write_text(json.dumps(sizes, indent=1))
    return set(sizes)


def rows(name, file="raw.jsonl"):
    path = EXPLORE / name / file
    return {r["custom_id"]: r for r in map(json.loads, path.read_text().splitlines())} if path.exists() else {}


def claude_sizes(name, source, select):
    """Sizes from the stored requests and rows of an earlier Claude run (E14, E3): `select(custom_id)` picks the rows."""
    reqs = [json.loads(line) for line in (EXPLORE / source / "requests.jsonl").read_text().splitlines()]
    got = rows(source)
    return write_sizes(name, [("|".join(anth.cell(r)), anth.est_in(r), got[r["custom_id"]])
                              for r in reqs if select(r["custom_id"]) and r["custom_id"] in got],
                       f"{source} raw.jsonl")


def main(name, build, planning_out, *, account, sizes):
    """Run one step. `sizes()` writes <name>/pilot.json from measured rows and returns the measured cells. A paid step
    runs only when every cell of the run has a measured size, so no bound rests on a planning guess."""
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step == "pilot":
        sys.exit(f"Not run. {name} has no pilot of its own: P, E14, or E3 measured its sizes (r9_counts.py).")
    if step in ("estimate", "submit", "run"):
        reqs = build()
        measured = sizes()
        cell = anth.cell if accounts.ACCOUNTS[account].provider == "anthropic" else oc.cell
        missing = sorted({"|".join(cell(r)) for r in reqs} - measured)
        if missing:
            print(f"{name}: no measured size for {', '.join(missing)}; the estimate uses planning sizes")
            if step != "estimate":
                sys.exit("Not run. Run P first (r9/trackc/ep_oa.py and ep_di.py), then estimate again.")
        build = lambda: reqs  # noqa: E731
    if accounts.ACCOUNTS[account].provider == "anthropic":
        anth.main(name, build, planning_out, account=account)
    else:
        oc.main(name, build, planning_out, account=account)
