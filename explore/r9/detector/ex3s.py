"""ex3s: X3 on gpt-6.1-sol (1 read), account openai_r9; the Sol cut rule of ROUND9-EXPERIMENT-PLAN.md P can drop it
(PROTOCOL.md section "X3 and Z4"). The requests are in runs.py.
Usage: python3 -I r9/detector/ex3s.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import runs  # noqa: E402

if __name__ == "__main__":
    runs.main("ex3s")
