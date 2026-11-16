"""ex2n_luna on openai_r9. X2 natural: `gpt-6-luna`, forms F0, F1, F4 on all 2,874 dialogues, 3 reads (r9/natural/PREDICTIONS.md).
Usage: python3 -I r9/natural/ex2n_luna.py estimate | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402

if __name__ == "__main__":
    natural.main(pathlib.Path(__file__).stem)
