"""E4: draft Track C items under the base, "unclear", and null-instruction forms (PROTOCOL.md).

4 conditions x 40 goals x (ambiguous, clear) x 3 forms x 3 reads x 3 models = 8,640 requests.
Usage: python3 -I e4.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_items  # noqa: E402
import templates  # noqa: E402
from templates import anth  # noqa: E402

MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
READS = 3
EFFORT = "low"
MAX_TOKENS = 4096
EXPECTED = 8640


def cells():
    """Every E4 request as (custom_id, item, form, read, model)."""
    return [(f"{item.id}-{form}-r{read}-{short}", item, form, read, model)
            for item in templates.items() for form in templates.FORMS for read in range(1, READS + 1)
            for short, model in MODELS.items()]


def build():
    failed = [(name, bad) for name, _, bad in check_items.check() if bad]
    assert not failed, f"item checks fail, run check_items.py: {failed[0][0]}"
    reqs = [anth.request(cid, model, EFFORT, MAX_TOKENS, item.text, templates.FORMS[form])
            for cid, item, form, _, model in cells()]
    assert len(reqs) == EXPECTED, len(reqs)
    return reqs


if __name__ == "__main__":
    anth.main("e4", build, planning_out=400, account="anthropic_old")
