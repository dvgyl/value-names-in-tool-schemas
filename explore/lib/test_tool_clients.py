"""Round-10 tool cases of the clients (review/plan15/ACTION-PLAN.md section 2.8). No network call, no key.

1. anth.message_row keeps tool_calls and every content block (thinking blocks too) unchanged and in order; a message
   with text blocks only gives the row of the code before round 10.
2. An Anthropic pilot of a run that is not sealed writes pilot_raw.jsonl in the fetch row format.
3. openai_compat.decode_response gives tool_calls and output_items for a function_call item, and the old row for an
   answer without one; arguments that do not parse give input None.
4. A request without the new arguments is byte-identical to the request of the code before round 10.
Usage: python3 -I test_tool_clients.py
"""
import json
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_clients as tc  # noqa: E402  (it installs the fake transports)
import anth  # noqa: E402
import openai_compat as oc  # noqa: E402


def block(**kw):
    return types.SimpleNamespace(**kw)


def message(blocks):
    return types.SimpleNamespace(model="claude-opus-5-5", stop_reason="tool_use", content=blocks,
                                 usage=types.SimpleNamespace(input_tokens=100, output_tokens=40))


def test_message_row():
    blocks = [block(type="thinking", thinking="", signature="sig"),
              block(type="text", text="Searching."),
              block(type="tool_use", id="toolu_1", name="search_hotels", input={"area": ["north"]})]
    row = anth.message_row("c1", message(blocks))
    assert row["text"] == "Searching." and row["stop"] == "tool_use"
    assert row["tool_calls"] == [{"id": "toolu_1", "name": "search_hotels", "input": {"area": ["north"]}}]
    assert [b["type"] for b in row["content"]] == ["thinking", "text", "tool_use"]
    assert row["content"][0] == {"type": "thinking", "thinking": "", "signature": "sig"}
    plain = anth.message_row("c2", message([block(type="text", text="{}")]))
    assert plain == {"custom_id": "c2", "type": "succeeded", "model": "claude-opus-5-5", "stop": "tool_use",
                     "input_tokens": 100, "output_tokens": 40, "text": "{}"}
    print("ok test_message_row")


def test_pilot_raw():
    blocks = [block(type="tool_use", id="toolu_1", name="search_hotels", input={"area": None})]

    def create(self, **params):
        return message(blocks)

    saved = tc.FakeAnthropic.create
    tc.FakeAnthropic.create = create
    try:
        with tc.sandbox() as root:
            a = tc.accounts.ACCOUNTS["anthropic_r9b"]
            tc.FakeAnthropic.expect = f"{tc.KEY}-{a.name}"
            reqs = [anth.request(f"er1-{i}", "claude-opus-5-5", "low", 4096, "hi", tools=[{"name": "search_hotels",
                    "description": "d", "input_schema": {"type": "object"}, "strict": True}], cell="t0") for i in range(3)]
            tc.operator(lambda approve: anth.pilot("ertest", reqs, approve, a))
            rows = [json.loads(x) for x in (root / "ertest" / "pilot_raw.jsonl").read_text().splitlines()]
            assert len(rows) == 3 and all(r["tool_calls"][0]["name"] == "search_hotels" for r in rows)
            pilot = json.loads(anth.pilot_path("ertest").read_text())
            assert list(pilot) == ["claude-opus-5-5|low|t0"], list(pilot)
    finally:
        tc.FakeAnthropic.create = saved
    print("ok test_pilot_raw")


def test_decode_function_call():
    body = json.loads(json.dumps(tc.RESPONSE))
    body["output"] = [{"type": "reasoning", "id": "rs_1", "summary": [], "encrypted_content": "e"},
                      {"type": "function_call", "id": "fc_1", "call_id": "call_1", "name": "search_hotels",
                       "arguments": "{\"area\": [\"north\"]}"}]
    row = oc.decode_response(body)
    assert row["tool_calls"] == [{"id": "call_1", "name": "search_hotels", "input": {"area": ["north"]}}]
    assert row["output_items"] == body["output"] and row["text"] == ""
    body["output"][1]["arguments"] = "{not json"
    assert oc.decode_response(body)["tool_calls"][0]["input"] is None
    old = oc.decode_response(tc.RESPONSE)
    assert "tool_calls" not in old and "output_items" not in old
    print("ok test_decode_function_call")


def test_old_requests_unchanged():
    a = anth.request("c", "claude-haiku-5-5", "low", 100, "hi", "sys", {"type": "disabled"}, {"type": "json_schema"})
    assert a == {"custom_id": "c", "params": {"model": "claude-haiku-5-5", "max_tokens": 100,
                                              "output_config": {"effort": "low", "format": {"type": "json_schema"}},
                                              "messages": [{"role": "user", "content": "hi"}], "system": "sys",
                                              "thinking": {"type": "disabled"}}}
    o = oc.openai_request("c", "gpt-6-luna", "none", 100, "hi", "sys", {"type": "object"})
    assert o == {"custom_id": "c", "body": {"model": "gpt-6-luna", "input": [{"role": "system", "content": "sys"},
                 {"role": "user", "content": "hi"}], "max_output_tokens": 100, "reasoning": {"effort": "none"},
                 "text": {"format": {"type": "json_schema", "name": "answer", "schema": {"type": "object"},
                                     "strict": True}}}}
    assert anth.cell(a) == ("claude-haiku-5-5", "low") and oc.cell(o) == ("gpt-6-luna", "none")
    print("ok test_old_requests_unchanged")


def main():
    test_message_row()
    test_pilot_raw()
    test_decode_function_call()
    test_old_requests_unchanged()
    print("tool client test passed")


if __name__ == "__main__":
    main()
