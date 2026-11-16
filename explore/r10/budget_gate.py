"""Bounds against free money (review/plan15/ACTION-PLAN.md section 2.9).

fits(account, bound, reserve=RESERVE): accounts.committed(account) + bound <= free limit - reserve, where the free limit
is the smaller of the account limit and the console balance that the operator gave (r10/console.json, optional:
{"<account>": usd}).
accounts.check_approval still checks the account limit itself.
Usage: python3 -I r10/budget_gate.py status | wave1 | final
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))  # python -I does not add the script folder
import accounts  # noqa: E402

RESERVE = 2.00
CONSOLE = HERE / "console.json"
ROUND10 = ("anthropic_r9a", "anthropic_r9b", "openai_r9")


def limit(name):
    a = accounts.ACCOUNTS[name]
    console = json.loads(CONSOLE.read_text()) if CONSOLE.exists() else {}
    if name in console:  # the console balance is the money left; the limit is what is committed plus that balance
        return min(a.limit, accounts.committed(a) + float(console[name]["balance"]) - float(console[name].get("committed_then", 0.0)))
    return a.limit


def free(name, reserve=RESERVE):
    return limit(name) - accounts.committed(accounts.ACCOUNTS[name]) - reserve


def fits(name, bound, reserve=RESERVE):
    """`reserve` is RESERVE for every run, except a run whose amendment sets its own (R10-18: labeltest.RESERVE)."""
    return bound <= free(name, reserve) + 1e-9


def status():
    for n in ROUND10:
        a = accounts.ACCOUNTS[n]
        print(f"{n:15s} limit {limit(n):7.2f}  committed {accounts.committed(a):7.2f}  free after the reserve {free(n):7.2f}")


def wave1(bounds):
    """`bounds`: {run name: printed bound}. Prints fits or NO per account."""
    import runs
    per = {}
    for name, b in bounds.items():
        per.setdefault(runs.RUNS[name].account, 0.0)
        per[runs.RUNS[name].account] += b
    ok = True
    for acc, total in sorted(per.items()):
        verdict = "fits" if fits(acc, total) else "NO"
        ok &= verdict == "fits"
        print(f"{acc}: wave-1 bounds {total:.2f} USD, free after the reserve {free(acc):.2f} USD: {verdict}")
    return ok


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd in ("status", "final"):
        status()
    elif cmd == "wave1":
        wave1(json.loads(pathlib.Path(sys.argv[2]).read_text()))
    else:
        sys.exit(__doc__)
