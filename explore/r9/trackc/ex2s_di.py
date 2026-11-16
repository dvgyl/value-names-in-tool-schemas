"""X2 on-site on deepinfra, synchronous (x2s.py). Usage: python3 -I r9/trackc/ex2s_di.py estimate | run --approve <bound>"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x2s  # noqa: E402

if __name__ == "__main__":
    x2s.main("ex2s_di", "deepinfra", "deepinfra")
