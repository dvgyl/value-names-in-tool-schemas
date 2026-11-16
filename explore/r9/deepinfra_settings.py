"""The DeepInfra settings of every round-9 run: one entry per open model. All builders use `request()`.

Sources, read 2026-11-03:
- https://docs.deepinfra.com/chat/reasoning.md: `reasoning_effort: "none"` turns chain-of-thought off, and
  `reasoning: {"enabled": false}` is the same. The examples use deepseek-ai/DeepSeek-V4-Flash-0731.
- https://docs.deepinfra.com/api-reference/chat-completions/openai-chat-completions.md: `reasoning_effort` takes none,
  minimal, low, medium, high, xhigh, or max, and none turns reasoning off "if the model supports". `chat_template_kwargs`
  is an object with free keys. The `json_schema` format has `name` and `schema`, but no `strict` field.
- https://deepinfra.com/Qwen/Qwen3.8-27B: thinking is on by default and a request can turn it off. No option name.
- https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash: the reasoning effort is an integer from 1 to 100. No off option.
P (ep_di) measured: DeepSeek with `reasoning_effort: "low"` thinks (about 1,169 reasoning tokens per natural call), and
Qwen with `reasoning_effort: "none"` gives 0 reasoning tokens. UNVERIFIED: that "none" turns DeepSeek-V4.1-Flash
thinking off, and that DeepInfra reads `chat_template_kwargs.enable_thinking`. The pilot ep_di2 measures both.
"""
import pathlib
import sys
import zlib
from typing import NamedTuple

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
import openai_compat as oc  # noqa: E402

# P: the largest valid answer has 121 output tokens with a schema (Qwen, Track C) and 189 without one (Qwen, on-site);
# 650 is more than 5 and 3 times these. A blank-space loop inside a JSON list (3 of 60 Qwen answers in P) runs to the
# cap, so a lost answer costs 650 output tokens.
MAX_TOKENS = 650
SAMPLING = {"temperature": 1.0, "top_p": 1.0}  # research/out/SYN-S5-models-infra.md section 3.2


class OpenModel(NamedTuple):
    id: str  # the DeepInfra model id
    options: dict  # the body fields that turn thinking off
    max_tokens: int  # the output cap, reasoning included


DEEPSEEK = OpenModel("deepseek-ai/DeepSeek-V4.1-Flash", {"reasoning_effort": "none"}, MAX_TOKENS)
QWEN = OpenModel("Qwen/Qwen3.8-27B", {"reasoning_effort": "none"}, MAX_TOKENS)
GEMMA = OpenModel("google/gemma-4-31B-it", {}, MAX_TOKENS)  # no thinking mode: 0 reasoning tokens in P
MODELS = {m.id: m for m in (DEEPSEEK, QWEN, GEMMA)}
# The other documented option of each thinking model. Only the pilot ep_di2 sends these, to compare the two options.
ALTERNATIVES = {DEEPSEEK.id: DEEPSEEK._replace(options={"reasoning": {"enabled": False}}),
                QWEN.id: QWEN._replace(options={"chat_template_kwargs": {"enable_thinking": False}})}


def seed(custom_id):
    """The recorded seed of one request. It differs per read, and a rebuild gives the same value. The API reference
    says that determinism is not guaranteed."""
    return zlib.crc32(custom_id.encode())


def request(model, custom_id, user, system=None, schema=None):
    """One chat completions request of `model`, an entry of MODELS or ALTERNATIVES. The prompt and the schema are the
    ones that the other panel models get, so the form stays the same."""
    return oc.deepinfra_request(custom_id, model.id, model.max_tokens, user, system, schema, **SAMPLING,
                                seed=seed(custom_id), **model.options)


def projected(row, model):
    """A raw.jsonl row of an earlier pilot as the size of one call of `model`, or None. A row with reasoning tokens
    comes from thinking on, so it gives no size for a call with thinking off. An answer that ran to a higher cap stops
    at `model.max_tokens` now."""
    if row.get("reasoning_tokens", 0):
        return None
    return {**row, "output_tokens": min(row["output_tokens"], model.max_tokens)}
