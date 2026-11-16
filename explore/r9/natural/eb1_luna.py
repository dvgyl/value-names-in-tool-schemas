"""eb1_luna on openai_r9. B1: `gpt-6-luna`, forms F2, F3, F5, F6 on S1 and S2, 3 reads (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/eb1_luna.py estimate | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
