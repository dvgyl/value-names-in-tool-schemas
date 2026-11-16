"""ex7_claude on anthropic_r9a. X7: Haiku 3 reads, Sonnet 2 reads, forms A0 and A1, with a pilot of 10 calls per cell (PROTOCOL.md X7).
Usage: python3 -I r9/x7/ex7_claude.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x7  # noqa: E402

if __name__ == "__main__":
    x7.main(pathlib.Path(__file__).stem)
