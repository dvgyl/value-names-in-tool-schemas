"""Round 10 run erx_f0h_opus (r10/runs.py)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import runs  # noqa: E402

runs.main("erx_f0h_opus")
