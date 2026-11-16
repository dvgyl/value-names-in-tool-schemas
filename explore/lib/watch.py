"""Wait until every submitted batch ends, then fetch each one (free). Usage: python -I lib/watch.py [minutes between checks]

Each check runs the `fetch` step of every batch that has no raw.jsonl. The fetch step reads the account of the batch
from batch.json. A fetch of a batch that has not ended prints its status and changes nothing.
"""
import json
import pathlib
import subprocess
import sys
import time

EXPLORE = pathlib.Path(__file__).resolve().parents[1]
# The scripts of the batches from before batch.json recorded its script.
SCRIPTS = {"e1": "forms/e1.py", "e2": "onsite/e2.py", "e3": "annot/e3.py", "e4": "trackc/e4.py",
           "e5": "forms/e5.py", "e6": "forms/e6.py", "e7": "forms/e7.py",
           "e8": "forms/e8.py", "e9": "trackc/e9.py", "e10": "trackc/e10.py", "e11": "forms/e11.py", "e12": "sonnet/e12.py", "e13": "pmain/e13.py", "e14": "trackc/e14.py", "e15": "trackc/e15.py"}


def pending():
    return {p.parent.name: json.loads(p.read_text()).get("script") or SCRIPTS[p.parent.name]
            for x in ("e", "mp") for p in EXPLORE.glob(f"{x}*/batch.json")  # the prefixes of accounts.PREFIXES
            if not (p.parent / "raw.jsonl").exists()}


def main():
    wait = 60 * float(sys.argv[1]) if len(sys.argv) > 1 else 300
    while todo := pending():
        print(time.strftime("%H:%M"), "pending:", " ".join(sorted(todo)), flush=True)
        for script in todo.values():
            subprocess.run([sys.executable, "-I", script, "fetch"], cwd=EXPLORE, check=False)
        if pending():
            time.sleep(wait)
    print("all submitted batches fetched")


if __name__ == "__main__":
    main()
