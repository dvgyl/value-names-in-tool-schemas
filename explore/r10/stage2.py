"""Step 2 of experiment A (review/plan15/ACTION-PLAN.md section 2.4): the agent sees the real search result of its own
stage-1 call.

For each stage-1 `t0` row whose call keeps `hotel` and not `guesthouse`, the step-2 request is the same system text and
tools, the stage-1 user message, the stored assistant output unchanged, and one tool result with
json.dumps(briefsearch.result_rows(briefsearch.search(db, fields))). The cell tag is `s2_empty` (the search found no
venue) or `s2_nonempty`. The harness sends no other text.
- Claude: messages = [user, {"role": "assistant", "content": stored content blocks}, {"role": "user", "content":
  [{"type": "tool_result", "tool_use_id": ..., "content": ...}]}].
- OpenAI: input = the stage-1 input items, then the stored output items (reasoning items included), then one
  {"type": "function_call_output", "call_id": ..., "output": ...} item.
requests(short, source) reads `era1_<short>/raw.jsonl` (source "raw") or `pilot_raw.jsonl` (source "pilot", the
step-2 replay test of the pilot phase).
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import briefsearch  # noqa: E402
import gold  # noqa: E402
import models  # noqa: E402
import tools  # noqa: E402

# Amendment R10-2 (2026-11-12, before any batch result): the stage-1 text says "Call search_hotels one time, and write
# no other text", so in the replay pilot Sol, Luna and Opus wrote nothing in step 2. Step 2 therefore adds one operator
# message after the tool result (a mid-conversation system message on Claude 5.5 models; a system input item on
# OpenAI). Nothing earlier in the conversation changes.
STEP2_TEXT = "Now either call search_hotels again or answer the traveller."


def stage1_requests(folder):
    """custom_id -> the stage-1 request as stored by the client (Anthropic: the request; OpenAI: the batch line)."""
    out = {}
    path = folder / "requests.jsonl"
    if path.exists():
        for line in path.read_text().splitlines():
            r = json.loads(line)
            out[r["custom_id"]] = r
    return out


def rows_of(folder, source):
    path = folder / ("raw.jsonl" if source == "raw" else "pilot_raw.jsonl")
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []


def build_stage1(short, name):
    """The stage-1 requests rebuilt offline (the pilot keeps no requests.jsonl)."""
    import runs
    return {r["custom_id"]: r for r in runs.requests(name)}


def requests(short, source="raw", db=None):
    name = f"era1_{short}"
    folder = EXPLORE / name
    db = db or gold.hotel_db()
    stage1 = build_stage1(short, name)
    provider = models.PROVIDER[short]
    out = []
    for row in rows_of(folder, source):
        if row.get("type", "succeeded") != "succeeded" or "-t0-" not in row["custom_id"]:
            continue
        kind, fields = tools.parse_call(row, "t0")
        if kind != "search" or not gold.hides_guesthouse(fields.get("type")):
            continue
        result = json.dumps(briefsearch.result_rows(briefsearch.search(db, fields)))
        cell = "s2_empty" if json.loads(result)["total"] == 0 else "s2_nonempty"
        first = stage1[row["custom_id"]]
        call = row["tool_calls"][0]
        new_id = row["custom_id"].replace(f"{name}-", f"era2_{short}-", 1).replace("-t0-", "-s2-")
        if provider == "anthropic":
            p = first["params"]
            messages = [p["messages"][0], {"role": "assistant", "content": row["content"]},
                        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": call["id"],
                                                      "content": result}]},
                        {"role": "system", "content": STEP2_TEXT}]
            out.append(models.request(short, new_id, None, p.get("system"), None, tools=tools.TOOLS["t0"],
                                      messages=messages, cell=cell))
        else:
            b = first["body"]
            items = list(b["input"]) + list(row["output_items"]) + [
                {"type": "function_call_output", "call_id": call["id"], "output": result},
                {"role": "system", "content": STEP2_TEXT}]
            out.append(models.request(short, new_id, None, None, None, tools=tools.TOOLS["t0"], input_items=items,
                                      cell=cell))
    return out
