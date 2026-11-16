"""The round-10 panel and its settings (review/plan15/ACTION-PLAN.md section 2.3).

The round-9 settings come from r9/natural/natural.py MODELS (Sonnet: thinking between_tools, effort high; Haiku: thinking
disabled, effort medium; Sol: effort low; Luna: effort none; the open models: r9/deepinfra_settings.py). Round 10 adds
Opus at effort low (its thinking cannot be turned off; claude-api skill, cached 2026-11-03), gpt-6-astra at effort
low, and the high settings of experiment F and of the fill.

`request(short, cid, ...)` builds one provider request. `schema` is the closed answer schema without a provider
wrapper (zforms.Form.schema), or None for a tool arm. `cell` is the arm tag.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions"):
    sys.path.insert(0, str(EXPLORE / sub))
import anth  # noqa: E402
import deepinfra_settings as ds  # noqa: E402
import natural  # noqa: E402
import openai_compat as oc  # noqa: E402

Model = natural.Model
MODELS = dict(natural.MODELS)
MODELS.update({
    "opus": Model("claude-opus-5-5", "anthropic", 4096, "low", None),
    "astra": Model("gpt-6-astra", "openai", 4000, "low"),
    "sonnet_high": Model("claude-sonnet-5-5", "anthropic", 16000, "high", {"type": "adaptive"}),
    "haiku_high": Model("claude-haiku-5-5", "anthropic", 16000, "high", {"type": "adaptive"}),
    "opus_high": Model("claude-opus-5-5", "anthropic", 16000, "high", None),
    "sol_high": Model("gpt-6.1-sol", "openai", 16000, "high"),
    "luna_high": Model("gpt-6-luna", "openai", 16000, "high"),
})
del MODELS["gemini"]  # no Google money in round 10
PROVIDER = {k: m.provider for k, m in MODELS.items()}


def request(short, cid, user, system_text, schema, *, tools=None, messages=None, input_items=None, cell=None):
    m = MODELS[short]
    if m.provider == "anthropic":
        fmt = {"type": "json_schema", "schema": schema} if schema else None
        return anth.request(cid, m.id, m.effort, m.max_tokens, user if messages is None else None, system_text,
                            m.thinking, fmt, tools=tools, messages=messages, cell=cell)
    if m.provider == "openai":
        return oc.openai_request(cid, m.id, m.effort, m.max_tokens, user if input_items is None else None,
                                 system_text if input_items is None else None, schema, tools=tools,
                                 input_items=input_items, cell=cell)
    assert not tools and messages is None and input_items is None, "round 10 sends no tool request to DeepInfra"
    req = ds.request(ds.MODELS[m.id], cid, user, system_text, schema)
    if cell is not None:
        req["cell"] = cell
    return req
