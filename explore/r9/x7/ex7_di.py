"""ex7_di on deepinfra. X7: the three DeepInfra models, 1 read, forms A0 and A1, synchronous (PROTOCOL.md X7).
Usage: python3 -I r9/x7/ex7_di.py estimate | run --approve <bound>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x7  # noqa: E402

if __name__ == "__main__":
    x7.main(pathlib.Path(__file__).stem)
