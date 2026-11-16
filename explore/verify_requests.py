"""Rebuild the requests of each round-10 run from the code and the corpus, and compare them with r10/manifest.json
(the number of requests and the SHA-256 that were recorded before the runs). Written for the supplementary packages and this repository;
it makes no model call. This is r10/runs.py verify, run by run.

Some runs build their requests from the stored answers of an earlier step, with the full content blocks and the
provider identifiers (the second step, the returned flag). This repository does not hold those blocks, so these runs
show "not rebuilt" with the reason.
Usage (from explore/): .venv/bin/python -I verify_requests.py
"""
import json
import pathlib
import sys

EXPLORE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXPLORE / "r10"))
import runs  # noqa: E402


def main():
    man = json.loads(runs.MANIFEST.read_text())
    counts = {"same": 0, "different": 0, "not rebuilt": 0}
    for name in sorted(k for k in man if k != "amendments"):
        if name not in runs.RUNS:
            print(f"{name}: not in runs.RUNS")
            counts["not rebuilt"] += 1
            continue
        try:
            reqs = runs.requests(name)
        except Exception as e:  # stored answers, held-out answers or code that this repository does not hold (README, section 5)
            print(f"{name}: not rebuilt ({type(e).__name__}: {e})")
            counts["not rebuilt"] += 1
            continue
        same = {"requests": len(reqs), "sha256": runs.digest(reqs)} == man[name]
        counts["same" if same else "different"] += 1
        print(f"{name}: {len(reqs)} requests, {'same as the manifest' if same else 'DIFFERENT from the manifest'}")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
