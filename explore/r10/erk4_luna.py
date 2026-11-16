"""Round 10 run erk4_luna (amendment R10-27; r10/fresh27.py adds it to runs.RUNS)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fresh27  # noqa: E402

fresh27.main("erk4_luna")
