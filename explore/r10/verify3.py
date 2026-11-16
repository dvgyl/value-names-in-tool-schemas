"""Amendment R10-17 (PROTOCOL.md): the planned verifier of experiment B on three open models (DeepSeek, Qwen, gemma on
DeepInfra), as a test fixed in advance of the search trade measure of the paper. Exploratory.

The dialogues are not new: the 807 no-type-brief dialogues of S1t and the 233 hotel-brief dialogues of S2, the sets of
r10/analysis/search_sym.py. Cells f0 and verify (forms10.FORMS), reads 1 and 2, the round-9 DeepInfra settings.
Runs ery_deepseek, ery_qwen, ery_gemma (r10/runs.py), account deepinfra_main, synchronous step run.
Usage (from explore/): .venv/bin/python -I r10/verify3.py check | shared | sets
"""
import csv
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import forms10  # noqa: E402

AMENDMENT = "### R10-17 "
ACCOUNT = "deepinfra_main"
CELLS = ("f0", "verify")
READS = 2
MAX_BOUND = 4.00  # USD per step
SHARED_LIMIT = 8.00  # USD of bounds for R10-17, pilots included
RUNS = ("ery_deepseek", "ery_qwen", "ery_gemma")
SIZES = {"no_type": 807, "hotel": 233}


def sets(data, g):
    """The two sets of search_sym.py: S1t dialogues whose brief sets no type (info and fail_info), and S2 dialogues
    whose brief sets hotel."""
    import gold
    out = {"no_type": [d for d in g["s1t"] if gold.brief_type(data[d]) is None
                       and gold.brief_type(data[d], "fail_info") is None],
           "hotel": [d for d in g["s2"] if gold.brief_type(data[d]) == "hotel"]}
    assert {k: len(v) for k, v in out.items()} == SIZES, {k: len(v) for k, v in out.items()}
    return out


def build(name, model, reads, data, g):
    """Cells f0 and verify, reads 1..reads, on the 807 + 233 dialogues; the user text is the full dialogue."""
    import models
    import runs
    assert reads == READS, reads
    s = sets(data, g)
    out = []
    for d in s["no_type"] + s["hotel"]:
        user = runs.text_full(data, d)
        for read in range(1, reads + 1):
            for arm in CELLS:
                form = forms10.FORMS[arm]
                out.append(models.request(model, runs.cid(name, d, arm, read), user, form.system, form.schema,
                                          cell=arm))
    return out


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-17 is in PROTOCOL.md under the round-10 amendments and holds the verifier question and the fixed values."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    for words in (forms10.VERIFY_QUESTION, "W_hotel = 233, W_notype = 807", "W_hotel = 545, W_notype = 994",
                  "The limit is 0.30", "The dialogues are not new."):
        if words not in flat:
            sys.exit(f"Not run. R10-17 does not hold {words!r}.")


def shared_bounds():
    """The bounds of R10-17 so far: every ledger row of RUNS on ACCOUNT, and every open step of RUNS."""
    import accounts
    a = accounts.ACCOUNTS[ACCOUNT]
    path = EXPLORE / a.ledger
    rows = [r for r in csv.DictReader(open(path)) if r["experiment"] in RUNS] if path.exists() else []
    total = sum(float(r["bound_usd"]) for r in rows)
    for n in RUNS:
        folder = EXPLORE / n
        for h in folder.glob("*.open.json") if folder.exists() else ():
            if not h.name.startswith("._"):
                total += json.loads(h.read_text())["bound"]
    return round(total, 2)


def check_shared(bound):
    used = shared_bounds()
    if used + bound > SHARED_LIMIT + 1e-9:
        sys.exit(f"Not run. R10-17 has used {used:.2f} USD of bounds; {bound:.2f} more would pass its limit of "
                 f"{SHARED_LIMIT:.2f} USD.")
    print(f"bounds of R10-17: {used:.2f} USD used, {used + bound:.2f} USD with this step (limit {SHARED_LIMIT:.2f})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-17 holds the verifier question and the fixed values")
    elif cmd == "shared":
        print(f"{shared_bounds():.2f} USD of bounds used by R10-17 (limit {SHARED_LIMIT:.2f})")
    elif cmd == "sets":
        import runs
        data, g = runs.context()
        print({k: len(v) for k, v in sets(data, g).items()})
    else:
        sys.exit(__doc__)
