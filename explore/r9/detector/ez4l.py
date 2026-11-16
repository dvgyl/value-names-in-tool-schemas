"""ez4l: Z4 on gpt-6-luna (3 reads), the new Z4 instances, account openai_r9 (PROTOCOL.md section "X3 and Z4"). The
requests are in runs.py.
Usage: python3 -I r9/detector/ez4l.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import runs  # noqa: E402

if __name__ == "__main__":
    runs.main("ez4l")
