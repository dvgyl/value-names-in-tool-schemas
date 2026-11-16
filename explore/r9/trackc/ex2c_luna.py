"""X2 Track C, gpt-6-luna only, on openai_r9 (x2c.py). Usage: python3 -I r9/trackc/ex2c_luna.py estimate | submit --approve <bound> | fetch"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x2c  # noqa: E402

if __name__ == "__main__":
    x2c.main("ex2c_luna", "openai", "openai_r9", only="luna")
