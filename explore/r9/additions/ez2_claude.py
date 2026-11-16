"""Z2 on Claude: the prefix reads under three forms and the recognition probe (anthropic_r9b).

The design and the request counts are in zruns.RUNS (ROUND9-ADDITIONS.md sections 3 and 9).
Usage, from explore/: python3 -I r9/additions/ez2_claude.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zruns  # noqa: E402

if __name__ == "__main__":
    zruns.main("ez2_claude")
