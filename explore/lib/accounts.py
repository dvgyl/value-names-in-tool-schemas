"""The spending guard for every paid account (PROTOCOL.md).

Each account has its own key, ledger, and limit. A paid step runs only when the --approve value equals the bound that
the same step prints, and only when the committed money of that account plus the bound stays within its limit.
Committed money is the ledger cost of every finished step, the bound of every batch that is not fetched, and the bound
of every open step. An open step is a file `<experiment>/<step>.open.json` that a client writes before its first paid
call and deletes after the ledger row. A crash can leave the file, and then its bound stays committed.
"""
import csv
import datetime
import json
import pathlib
import sys
from typing import NamedTuple

EXPLORE = pathlib.Path(__file__).resolve().parents[1]
ENV = EXPLORE.parents[2] / "harness" / ".env"
KEYS = ENV.with_name("keys-r9.env")
ENV_FILES = (KEYS, ENV)  # api_key() takes the key from the first file that sets it
TAX = 1.18  # a tax margin on cash payments
OLD = "anthropic_old"  # a batch.json without an "account" field is from this account (E1 to E15)


class Account(NamedTuple):
    name: str
    provider: str  # the client that can use the account: "anthropic", "openai", "deepinfra", or "google"
    key: str  # the key name in harness/.env
    ledger: str  # the ledger file in explore/
    limit: float  # USD
    paid_from: str  # the money source, as the ledger writes it
    cash: bool  # bounds and committed money of a cash account include the TAX margin


ACCOUNTS = {a.name: a for a in (
    Account(OLD, "anthropic", "ANTHROPIC_API_KEY", "ledger.csv", 208.51, "anthropic promo credits", False),
    Account("anthropic_r9a", "anthropic", "ANTHROPIC_API_KEY_R9A", "ledger_anthropic_r9a.csv", 200.02,
            "anthropic r9a promo credits", False),
    Account("anthropic_r9b", "anthropic", "ANTHROPIC_API_KEY_R9B", "ledger_anthropic_r9b.csv", 199.61,
            "anthropic r9b promo credits", False),
    Account("openai_r9", "openai", "OPENAI_API_KEY", "ledger_openai_r9.csv", 172.94, "openai credits", False),
    Account("deepinfra", "deepinfra", "DEEPINFRA_API_KEY", "ledger_deepinfra.csv", 25.00, "deepinfra cash", True),
    Account("deepinfra_main", "deepinfra", "DEEPINFRA_API_KEY", "ledger_deepinfra_main.csv", 50.41, "deepinfra cash", True),
    Account("google", "google", "GEMINI_API_KEY", "ledger_google.csv", 0.00, "google cash", True),
)}


def account(name, providers):
    """The account that an experiment names. There is no default, so a run cannot go to an account by accident."""
    a = ACCOUNTS.get(name)
    if a is None or a.provider not in providers:
        names = ", ".join(n for n, x in ACCOUNTS.items() if x.provider in providers)
        sys.exit(f"Not run. Name the account explicitly, one of: {names}. {name!r} is not one of them.")
    return a


def factor(a):
    return TAX if a.cash else 1.0


# The prefixes of the experiment folders. "e" holds every experiment run, "mp" holds the main-study paraphrase inputs
# (main/paraphrase.py), which are not sealed. committed() finds batches and open steps only in these folders.
PREFIXES = ("e", "mp")


def folder(name):
    """The experiment folder. Its name starts with one of PREFIXES."""
    assert name.startswith(PREFIXES) and "/" not in name, f"experiment names start with one of {PREFIXES}: {name}"
    return EXPLORE / name


def _owned(a, pattern):
    for p in EXPLORE.glob(pattern):
        if p.name.startswith("._"):  # the binary metadata file that macOS writes beside each file on the exFAT drive
            continue
        info = json.loads(p.read_text())
        if info.get("account", OLD) == a.name:
            yield p, info


def committed(a):
    """The ledger cost of every finished step, plus the bound of every batch that is not fetched and of every open step."""
    path = EXPLORE / a.ledger
    rows = list(csv.DictReader(open(path))) if path.exists() else []
    actual = {r["experiment"]: float(r["list_price_usd"]) for r in rows if r["step"] == "batch"}
    steps = sum(float(r["list_price_usd"]) for r in rows if r["step"] != "batch")
    batches = sum(actual[p.parent.name] * factor(a) if p.parent.name in actual else info["bound"]
                  for x in PREFIXES for p, info in _owned(a, f"{x}*/batch.json"))
    held = sum(info["bound"] for x in PREFIXES for _, info in _owned(a, f"{x}*/*.open.json"))
    return batches + steps * factor(a) + held


def check_approval(a, given, bound):
    if committed(a) + bound > a.limit:
        sys.exit(f"Not run. {committed(a):.2f} USD is committed, and {bound:.2f} more would pass the {a.limit:.2f} USD limit.")
    if given is None or round(float(given), 2) != bound:
        sys.exit(f"Not run. Rerun with --approve {bound:.2f} after the operator approves this bound in writing.")


def hold(a, name, step, bound):
    """Write the open-step file before the first paid call of a step. Its bound counts as committed until it is deleted."""
    path = folder(name) / f"{step}.open.json"
    if path.exists():
        sys.exit(f"Not run. {path} is left from a {step} that did not end, and its bound stays committed. Compare the "
                 f"stored responses with the usage page of the provider, add a ledger row if money was used, then "
                 f"delete the file.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"account": a.name, "step": step, "bound": bound, "started": now()}))
    return path


def has_row(a, name, step):
    path = EXPLORE / a.ledger
    return path.exists() and any(r["experiment"] == name and r["step"] == step for r in csv.DictReader(open(path)))


def ledger(a, name, step, bound, spent):
    """One row at list prices. A cash account also writes the list price as cash; the TAX margin is not a measured cost."""
    path = EXPLORE / a.ledger
    new = not path.exists()
    with open(path, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["utc", "experiment", "step", "bound_usd", "list_price_usd", "paid_from", "cash_usd"])
        w.writerow([now(timespec="seconds"), name, step, f"{bound:.2f}", f"{spent:.4f}", a.paid_from,
                    f"{spent:.4f}" if a.cash else "0.00"])


def now(**kw):
    return datetime.datetime.now(datetime.timezone.utc).isoformat(**kw)


def api_key(a):
    """The key of the account. Only a paid step calls this, after its approval check. The key is never printed or stored."""
    for path in ENV_FILES:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.strip().startswith(f"{a.key}="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    sys.exit(f"{a.key} is empty or missing in {' and '.join(str(p) for p in ENV_FILES)}")
