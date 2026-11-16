"""B2 on the three DeepInfra models: the Z1 traveller-text edit under F0 and F1 (deepinfra).

The design and the request counts are in zruns.RUNS (ROUND9-ADDITIONS.md sections 3 and 9).
Usage, from explore/: python3 -I r9/additions/eb2_open.py estimate | run --approve <bound>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zruns  # noqa: E402

if __name__ == "__main__":
    zruns.main("eb2_open")
