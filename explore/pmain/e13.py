"""E13: the confirmatory H4 natural contrast under the registered settings (PROTOCOL.md, 2026-10-25).

Forms `p_main` against `p_main_renamed` (only `type` and `hotel` renamed), structured output with a closed JSON schema,
`claude-haiku-5-5` with thinking disabled (effort medium, its default) and `claude-sonnet-5-5` with thinking
`between_tools` (effort high, its default), 3 reads, on the 1,136 E11 dialogues: 13,632 requests.
Usage: python3 -I e13.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "forms"))
import common  # noqa: E402
from common import anth  # noqa: E402

VALUES = {"area": ["centre", "north", "south", "east", "west"], "pricerange": ["cheap", "moderate", "expensive"],
          "stars": ["0", "1", "2", "3", "4", "5"], "type": ["guesthouse", "hotel"], "parking": ["yes", "no"],
          "internet": ["yes", "no"]}
SETTINGS = {"haiku": ({"type": "disabled"}, "medium"), "sonnet": ({"type": "between_tools"}, "high")}
FORMS = ("p_main", "p_main_renamed")
READS = 3
MAX_TOKENS = 4096
EXPECTED = 1136 * len(FORMS) * READS * len(SETTINGS)


def schema(renamed):
    """The three field states of the plan: null (not stated), "any", or a list of allowed values in preference order."""
    props = {"name": {"anyOf": [{"type": "null"}, {"type": "string"}]}}
    for field, values in VALUES.items():
        key, vals = field, values
        if renamed and field == "type":
            key, vals = "property_kind", ["guesthouse", "large_property"]
        props[key] = {"anyOf": [{"type": "null"}, {"type": "string", "enum": ["any"]},
                                {"type": "array", "items": {"type": "string", "enum": vals}}]}
    return {"type": "json_schema",
            "schema": {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}}


def build():
    data = anth.multiwoz()
    ids = common.dialogue_ids("e11", data)
    anth.assert_outside_trackp(ids, data)
    reqs = []
    for short, (thinking, effort) in SETTINGS.items():
        for form in FORMS:
            fmt = schema(common.FORMS[form].renamed)
            for d in ids:
                for read in range(1, READS + 1):
                    reqs.append(anth.request(f"e13-{d.removesuffix('.json')}-{form}-{read}-{short}", common.MODELS[short],
                                             effort, MAX_TOKENS, common.dialogue_text(data[d]), common.FORMS[form].system,
                                             thinking, fmt))
    assert len(reqs) == EXPECTED, len(reqs)
    return reqs


if __name__ == "__main__":
    anth.main("e13", build, planning_out=100, account="anthropic_old")
