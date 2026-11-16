"""ex1_tc on anthropic_r9a. X1 on the 80 E4 condition-a items: forms F1, F2, F4 (Haiku 7 reads, Sonnet 6) and Sonnet F0 reads 3 to 6 (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/ex1_tc.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
