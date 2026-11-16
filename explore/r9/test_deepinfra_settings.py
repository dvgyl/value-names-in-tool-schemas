"""Offline test of r9/deepinfra_settings.py. No API call. Usage: python3 -I r9/test_deepinfra_settings.py

1. Thinking off: DeepSeek and Qwen take reasoning_effort "none", Gemma takes no option, and each alternative is the
   other documented option. The three models share one output cap.
2. The cap is at least 5 times the largest valid answer of P with a schema and 3 times the largest without one
   (ep_di/raw.jsonl, reasoning tokens left out), and below the old cap of 4,000.
3. A request holds the prompt and the schema unchanged, the sampling settings, and the seed of its custom_id, and no
   other field.
4. projected() drops a row with reasoning tokens and stops a cut-off answer at the cap.
"""
import json
import pathlib
import sys
import zlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import deepinfra_settings as ds  # noqa: E402

P_ROWS = HERE.parent / "ep_di" / "raw.jsonl"


def test_options():
    assert ds.DEEPSEEK.options == ds.QWEN.options == {"reasoning_effort": "none"} and ds.GEMMA.options == {}
    assert ds.ALTERNATIVES[ds.DEEPSEEK.id].options == {"reasoning": {"enabled": False}}
    assert ds.ALTERNATIVES[ds.QWEN.id].options == {"chat_template_kwargs": {"enable_thinking": False}}
    caps = {m.max_tokens for m in [*ds.MODELS.values(), *ds.ALTERNATIVES.values()]}
    assert caps == {ds.MAX_TOKENS}, caps
    print(f"1. thinking off on DeepSeek and Qwen, no option on Gemma, one cap of {ds.MAX_TOKENS} tokens")


def test_cap():
    rows = [json.loads(line) for line in P_ROWS.read_text().splitlines()]
    valid = [r for r in rows if r["type"] == "succeeded" and r["stop"] == "end_turn"]
    assert len(valid) == 175, len(valid)
    largest = {kind: max(r["output_tokens"] - r.get("reasoning_tokens", 0) for r in valid
                         if (r["custom_id"].split("-")[1] == "os") == (kind == "free")) for kind in ("schema", "free")}
    assert 5 * largest["schema"] <= ds.MAX_TOKENS and 3 * largest["free"] <= ds.MAX_TOKENS < 4000, largest
    print(f"2. cap {ds.MAX_TOKENS} >= 5 x the largest valid schema answer of P and 3 x the largest free answer {largest}")


def test_request():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"],
              "additionalProperties": False}
    got = ds.request(ds.QWEN, "ex-unit-1", "the dialogue", "the form", schema)
    want = {"custom_id": "ex-unit-1", "body": {
        "model": "Qwen/Qwen3.8-27B",
        "messages": [{"role": "system", "content": "the form"}, {"role": "user", "content": "the dialogue"}],
        "max_tokens": 650, "temperature": 1.0, "top_p": 1.0, "seed": zlib.crc32(b"ex-unit-1"),
        "reasoning_effort": "none",
        "response_format": {"type": "json_schema", "json_schema": {"name": "answer", "strict": True, "schema": schema}}}}
    assert got == want, got
    free = ds.request(ds.GEMMA, "ex-unit-2", "the case", "the prompt")["body"]
    assert "response_format" not in free and "reasoning_effort" not in free and free["seed"] == zlib.crc32(b"ex-unit-2")
    print("3. a request holds the prompt and schema unchanged, the settings, and the custom_id seed, and nothing more")


def test_projected():
    row = {"type": "succeeded", "stop": "end_turn", "output_tokens": 300, "reasoning_tokens": 0}
    assert ds.projected(row, ds.QWEN) == row
    assert ds.projected({**row, "reasoning_tokens": 250}, ds.DEEPSEEK) is None
    assert ds.projected({**row, "stop": "max_tokens", "output_tokens": 4000}, ds.QWEN)["output_tokens"] == 650
    print("4. projected() drops a thinking row and stops a cut-off answer at the cap")


if __name__ == "__main__":
    for test in (test_options, test_cap, test_request, test_projected):
        test()
    print("test_deepinfra_settings.py: PASS")
