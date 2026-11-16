"""ez4c: Z4 on claude-haiku-5-5 (3 reads) and claude-sonnet-5-5 (2 reads), the new Z4 instances, account anthropic_r9b
(PROTOCOL.md section "X3 and Z4"). The requests are in runs.py.
Usage: python3 -I r9/detector/ez4c.py estimate | pilot --approve <bound> | submit --approve <bound> | fetch
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import runs  # noqa: E402

if __name__ == "__main__":
    runs.main("ez4c")
