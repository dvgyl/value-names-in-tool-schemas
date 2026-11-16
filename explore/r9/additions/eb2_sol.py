"""B2 on gpt-6.1-sol: the Z1 traveller-text edit under F0 and F1 (openai_r9).

The design and the request counts are in zruns.RUNS (ROUND9-ADDITIONS.md sections 3 and 9).
Usage, from explore/: python3 -I r9/additions/eb2_sol.py estimate | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zruns  # noqa: E402

if __name__ == "__main__":
    zruns.main("eb2_sol")
