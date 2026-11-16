"""X5 claude-opus-5-5 annotator on anthropic_r9a (x5.py). Usage: python3 -I r9/trackc/ex5_an.py estimate | submit --approve <bound> | fetch"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x5  # noqa: E402

if __name__ == "__main__":
    x5.main("ex5_an", "anthropic", "anthropic_r9a")
