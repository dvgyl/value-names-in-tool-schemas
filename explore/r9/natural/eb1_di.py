"""eb1_di on deepinfra. B1: the three DeepInfra models, forms F2 to F6 on S1 and F0, F1, F4 on S2, 1 read (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/eb1_di.py estimate | run --approve <bound>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
