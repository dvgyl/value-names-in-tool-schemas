"""Z3 on gpt-6-luna: the four fix forms on the X1 groups (openai_r9).

The design and the request counts are in zruns.RUNS (ROUND9-ADDITIONS.md sections 3 and 9).
Usage, from explore/: python3 -I r9/additions/ez3_luna.py estimate | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zruns  # noqa: E402

if __name__ == "__main__":
    zruns.main("ez3_luna")
