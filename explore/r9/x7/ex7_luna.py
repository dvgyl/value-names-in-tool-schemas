"""ex7_luna on openai_r9. X7: `gpt-6-luna` 3 reads, forms A0 and A1 (PROTOCOL.md X7).
Usage: python3 -I r9/x7/ex7_luna.py estimate | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x7  # noqa: E402

if __name__ == "__main__":
    x7.main(pathlib.Path(__file__).stem)
