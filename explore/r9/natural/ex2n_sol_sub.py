"""ex2n_sol_sub on openai_r9. X2 natural: `gpt-6.1-sol`, forms F0, F1, F4 on the seeded 600 of S2 to S4, 1 read. The X2 Sol cut rule drops it (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/ex2n_sol_sub.py estimate | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
