"""P on deepinfra (ep.py). Usage: python3 -I r9/trackc/ep_di.py estimate | run --approve <bound>"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ep  # noqa: E402

if __name__ == "__main__":
    ep.main("ep_di", "deepinfra")
