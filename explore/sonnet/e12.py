"""E12: the registered Sonnet setting (DECISIONS-R7 item 12, 2026-10-25).

`claude-sonnet-5-5` with thinking `between_tools` (no thinking), effort `high` (the highest effort that `between_tools`
accepts), 3 reads, on two sets:
  natural: the 1,136 E11 dialogues x forms `p4` and `p4_renamed` = 6,816 requests;
  trackc:  the 320 E4 items x the forms base, null-instruction, and unclear = 2,880 requests.
Usage: python3 -I e12.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "forms"))
sys.path.insert(0, str(HERE.parent / "trackc"))
import common  # noqa: E402
import templates  # noqa: E402
from common import anth  # noqa: E402

MODEL = "claude-sonnet-5-5"
THINKING = {"type": "between_tools"}
EFFORT = "high"
MAX_TOKENS = 4096
READS = 3
NATURAL_FORMS = ("p4", "p4_renamed")
EXPECTED = 6816 + 2880


def natural_cells(data):
    ids = common.dialogue_ids("e11", data)
    return [(f"e12n-{d.removesuffix('.json')}-{form}-{read}", d, form, read)
            for d in ids for form in NATURAL_FORMS for read in range(1, READS + 1)]


def trackc_cells():
    return [(f"e12c-{item.id}-{form}-r{read}", item, form, read)
            for item in templates.items() for form in templates.FORMS for read in range(1, READS + 1)]


def build():
    data = anth.multiwoz()
    nat = natural_cells(data)
    anth.assert_outside_trackp({d for _, d, _, _ in nat}, data)
    reqs = [anth.request(cid, MODEL, EFFORT, MAX_TOKENS, common.dialogue_text(data[d]), common.FORMS[form].system, THINKING)
            for cid, d, form, _ in nat]
    reqs += [anth.request(cid, MODEL, EFFORT, MAX_TOKENS, item.text, templates.FORMS[form], THINKING)
             for cid, item, form, _ in trackc_cells()]
    assert len(reqs) == EXPECTED, len(reqs)
    return reqs


if __name__ == "__main__":
    anth.main("e12", build, planning_out=100, account="anthropic_old")
