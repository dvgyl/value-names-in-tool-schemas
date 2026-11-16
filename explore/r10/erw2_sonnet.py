"""Round 10 run erw2_sonnet (r10/runs.py)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import runs  # noqa: E402

runs.main("erw2_sonnet")
