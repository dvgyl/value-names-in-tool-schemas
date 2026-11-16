"""ex3d: X3 on DeepSeek-V4.1-Flash, Qwen3.8-27B, and gemma-4-31B-it (1 read each, 600 instances), account deepinfra
(PROTOCOL.md section "X3 and Z4"). The requests are in runs.py.
Usage: python3 -I r9/detector/ex3d.py estimate | pilot --approve <bound> | run --approve <bound>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import runs  # noqa: E402

if __name__ == "__main__":
    runs.main("ex3d")
