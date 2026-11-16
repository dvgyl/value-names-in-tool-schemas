"""Round 10 run erk_deepseek (r10/runs.py)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import runs  # noqa: E402

runs.main("erk_deepseek")
