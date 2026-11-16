"""ex1_grp on anthropic_r9a. X1 on S2 to S5: forms F0, F1, F2, F4; Haiku 3 reads, Sonnet 2 (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/ex1_grp.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
