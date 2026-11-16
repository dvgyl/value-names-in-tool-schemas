"""B4 on gpt-6.1-sol: p_split and p_define on S1 (openai_r9).

The design and the request counts are in zruns.RUNS (ROUND9-ADDITIONS.md sections 3 and 9).
Usage, from explore/: python3 -I r9/additions/eb4_sol.py estimate | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zruns  # noqa: E402

if __name__ == "__main__":
    zruns.main("eb4_sol")
