"""ex1_f6 on anthropic_r9a. X1 form F6 (`category_A`): S1 3 reads; S2 to S5 Haiku 3 reads, Sonnet 2 (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/ex1_f6.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
