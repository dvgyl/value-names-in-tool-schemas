"""ex2n_di on deepinfra. X2 natural: the three DeepInfra models, forms F0 and F1 on S1, 1 read (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/ex2n_di.py estimate | run --approve <bound>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
