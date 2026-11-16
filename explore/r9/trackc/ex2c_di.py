"""X2 Track C on deepinfra, synchronous (x2c.py). Usage: python3 -I r9/trackc/ex2c_di.py estimate | run --approve <bound>"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x2c  # noqa: E402

if __name__ == "__main__":
    x2c.main("ex2c_di", "deepinfra", "deepinfra")
