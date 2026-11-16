"""E14: the Claim 2 Track C contrast under the confirmatory settings (PROTOCOL.md, 2026-10-25).

The 320 E4 items x the forms `p_main`, `p_unclear`, and `p_null`, structured output with a closed JSON schema (only
`p_unclear` offers "unclear"), `claude-haiku-5-5` with thinking disabled (effort medium) and `claude-sonnet-5-5` with
thinking `between_tools` (effort high), READS reads per model.
Usage: python3 -I e14.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
Analysis: TRACKC_EXP=e14 python3 -I analyze.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_items  # noqa: E402
import templates  # noqa: E402
from templates import anth  # noqa: E402

SETTINGS = {"haiku": ("claude-haiku-5-5", {"type": "disabled"}, "medium"),
            "sonnet": ("claude-sonnet-5-5", {"type": "between_tools"}, "high")}
READS = {"haiku": 7, "sonnet": 2}  # sized after the pilot to the largest bound under the limit (PROTOCOL.md)
MAX_TOKENS = 4096
EXPECTED = 320 * len(templates.FORMS) * sum(READS.values())


def schema(form):
    """The three field states of the plan (null, "any", or a list of allowed values); `p_unclear` adds "unclear"."""
    words = ["any", "unclear"] if form == "p_unclear" else ["any"]
    props = {"name": {"anyOf": [{"type": "null"}, {"type": "string"}]}}
    for field, values in templates.ALLOWED.items():
        props[field] = {"anyOf": [{"type": "null"}, {"type": "string", "enum": words},
                                  {"type": "array", "items": {"type": "string", "enum": list(values)}}]}
    return {"type": "json_schema",
            "schema": {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}}


def cells():
    """Every E14 request as (custom_id, item, form, read, model)."""
    return [(f"e14-{item.id}-{form}-r{read}-{short}", item, form, read, SETTINGS[short][0])
            for short in SETTINGS for item in templates.items() for form in templates.FORMS
            for read in range(1, READS[short] + 1)]


def build():
    failed = [(name, bad) for name, _, bad in check_items.check() if bad]
    assert not failed, f"item checks fail, run check_items.py: {failed[0][0]}"
    by_model = {model: (thinking, effort) for model, thinking, effort in SETTINGS.values()}
    reqs = [anth.request(cid, model, by_model[model][1], MAX_TOKENS, item.text, templates.FORMS[form],
                         by_model[model][0], schema(form))
            for cid, item, form, _, model in cells()]
    assert len(reqs) == EXPECTED, len(reqs)
    return reqs


if __name__ == "__main__":
    anth.main("e14", build, planning_out=100, account="anthropic_old")
