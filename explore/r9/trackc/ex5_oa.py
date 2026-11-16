"""X5 gpt-6-astra annotator on openai_r9 (x5.py). Usage: python3 -I r9/trackc/ex5_oa.py estimate | submit --approve <bound> | fetch"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x5  # noqa: E402

if __name__ == "__main__":
    x5.main("ex5_oa", "openai", "openai_r9")
