"""X2 Track C p_option on anthropic_r9a (x2c.py). Usage: python3 -I r9/trackc/ex2c_an.py estimate | submit --approve <bound> | fetch"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x2c  # noqa: E402

if __name__ == "__main__":
    x2c.main("ex2c_an", "anthropic", "anthropic_r9a")
