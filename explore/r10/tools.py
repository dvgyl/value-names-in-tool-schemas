"""Experiment A: the tool definitions, the tool system texts, and the parse of a tool call (ROUND10-EXPERIMENT-PLAN.md
experiment A; review/plan15/ACTION-PLAN.md section 2.4).

The search tool takes the same closed schema as the form (zforms.FORMS["f0"].schema for T0, ["f1"] for T1), so a tool
call and a form answer have the same value space and natural.parse scores both. The tool system text is the form text
with two sentences replaced: the sentence that asks for one JSON object, and the last sentence. The arm t0ask adds the
tool ask_traveller and one clause about it. Every request sends tool_choice auto (the forced-call rule of anth.request).
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions"):
    sys.path.insert(0, str(EXPLORE / sub))
import natural  # noqa: E402
import zforms  # noqa: E402

SEARCH_DESCRIPTION = ("Search the hotel database of Cambridge with the traveller's requirements. Each argument is a "
                      "requirement in the same form as described in the instructions.")
ASK_DESCRIPTION = "Ask the traveller one question before you search."

ASK_OLD = "Write down the traveller's requirements for the hotel as one JSON object."
ASK_NEW = "Search for hotels that meet the traveller's requirements with one call of the tool search_hotels."
END_OLD = "Output only the JSON object."
END_NEW = "Call search_hotels one time, and write no other text."
END_NEW_ASK = ("Call search_hotels one time, or call ask_traveller one time if you must ask the traveller a question "
               "before you search, and write no other text.")
NEW_TEXTS = (SEARCH_DESCRIPTION, ASK_DESCRIPTION, ASK_NEW, END_NEW, END_NEW_ASK)


def tool(name, description, schema):
    return {"name": name, "description": description, "input_schema": schema, "strict": True}


SEARCH_T0 = tool("search_hotels", SEARCH_DESCRIPTION, zforms.FORMS["f0"].schema)
SEARCH_T1 = tool("search_hotels", SEARCH_DESCRIPTION, zforms.FORMS["f1"].schema)
ASK = tool("ask_traveller", ASK_DESCRIPTION,
           {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"],
            "additionalProperties": False})

FORM_TEXT = {"t0": zforms.FORMS["f0"].system, "t0ask": zforms.FORMS["f0"].system, "t1": zforms.FORMS["f1"].system}
TOOLS = {"t0": [SEARCH_T0], "t1": [SEARCH_T1], "t0ask": [SEARCH_T0, ASK]}
PARSE_FORM = {"p0": "f0", "t0": "f0", "t0ask": "f0", "t1": "f1"}  # natural.FORMS key that maps the answer back


def tool_system(arm):
    text = zforms.once(FORM_TEXT[arm], ASK_OLD, ASK_NEW)
    return zforms.once(text, END_OLD, END_NEW_ASK if arm == "t0ask" else END_NEW)


def clean_nulls(args):
    """Amendment R10-3 (2026-11-12, from the stage-1 pilots, before any batch result): in every Claude tool call the
    empty fields hold the string "null" (Sonnet, Opus and Haiku, 10 to 25 fields of 28 to 30 calls each); the GPT models
    send a JSON null. The string "null" is read as null, and an item "null" of a list is dropped."""
    out = {}
    for k, v in args.items():
        if v == "null":
            v = None
        elif isinstance(v, list):
            v = [x for x in v if x != "null"] or None
        out[k] = v
    return out


def parse_call(row, arm):
    """One of ("search", fields), ("ask", question), ("none", text), ("invalid", reason). `fields` has the F0 field
    names and values (natural.parse with the arm's form), so T0 and T1 calls are scored on the same fields."""
    calls = row.get("tool_calls") or []
    if not calls:
        return ("none", row.get("text", ""))
    if len(calls) > 1:
        return ("invalid", f"{len(calls)} tool calls")
    c = calls[0]
    if c["name"] == "ask_traveller" and arm == "t0ask":
        q = (c.get("input") or {}).get("question")
        return ("ask", q) if isinstance(q, str) else ("invalid", "ask without a question")
    if c["name"] != "search_hotels" or not isinstance(c.get("input"), dict):
        return ("invalid", f"tool {c.get('name')!r} with input {type(c.get('input')).__name__}")
    try:
        return ("search", natural.parse(json.dumps(clean_nulls(c["input"])), natural.FORMS[PARSE_FORM[arm]]))
    except (ValueError, KeyError, TypeError) as e:
        return ("invalid", f"{type(e).__name__}: {e}")
