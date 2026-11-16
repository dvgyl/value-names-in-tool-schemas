"""e7 request builder (PROTOCOL.md). Usage: python3 -I e7.py estimate|pilot|submit|fetch [--approve <bound>]"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common  # noqa: E402
from common import anth  # noqa: E402


def build():
    data = anth.multiwoz()
    ids = common.dialogue_ids("e7", data)
    anth.assert_outside_trackp(ids, data)
    return common.requests("e7", data, ids)


if __name__ == "__main__":
    anth.main("e7", build, planning_out=400, account="anthropic_old")
