"""ex2n_sol_f4 on openai_r9. X2 natural: `gpt-6.1-sol`, form F4 on S1, 1 read. The X2 Sol cut rule drops it (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/ex2n_sol_f4.py estimate | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
