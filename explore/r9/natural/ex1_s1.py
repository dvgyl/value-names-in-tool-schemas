"""ex1_s1 on anthropic_r9a. X1 on S1: forms F2 to F5, 3 reads, and the F0 drift check on the 228 drift dialogues; Haiku and Sonnet (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/ex1_s1.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
