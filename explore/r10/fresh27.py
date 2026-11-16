"""Amendment R10-27 (PROTOCOL.md): a fresh evaluation of the final release-test rule of the paper on
new first requests. Exploratory, fixed in the protocol before the run.

New file; it edits no frozen script. It adds its two runs to runs.RUNS at run time (register) and then uses the
existing runner (runs.main, lib/openai_compat.py) without change.

- Requests: first-request prefixes (zforms.prefix_text) of MultiWOZ 2.4 training dialogues that are not among the 554
  prefixes of experiment A, were never sent in a release-test run, and are in no protected list (select).
  Open set: the brief sets no type (info and fail_info); specific set: the brief sets hotel. SIZES and SEED below.
- Cells (the texts of R10-16, R10-20 and R10-22, unchanged): t0 the control, trep the repeat, tord the field order,
  tpar paraphrase 1, tpar2 paraphrase 2, t1 the full rename. PLAN: Luna all six cells; Sol t0, trep and t1.
- Money: CAP (4.00 USD at list price in total, pilots included) over the runs of PLAN, as newmoney.used counts it.
- Account limit: patch_accounts sets the limit of openai_r9 to LIMIT for these steps only (see LIMIT).
- No em* folder: the money guard of lib/accounts.py globs every e*/batch.json. While a step of this module runs,
  accounts.committed is replaced by committed_no_em, which opens no folder whose name starts with "em" and counts the
  fetched em* batches by their ledger rows (the same value when every em* batch has a ledger row).
Usage (from explore/): .venv/bin/python -I r10/fresh27.py check | select | show | status | prove | manifest
                       .venv/bin/python -I r10/erk4_luna.py estimate | pilot | submit | fetch [--approve X]
"""
import csv
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import control  # noqa: E402
import harmless  # noqa: E402
import harmless2  # noqa: E402
import tools  # noqa: E402

AMENDMENT = "### R10-27 "
SEED = 20261115
SIZES = {"open": 448, "specific": 59}  # the sizes of the paper's release tests
READS = {"open": 1, "specific": 10}  # answers per cell and prefix (control.READS without the guesthouse set)
CAP = 4.00  # USD at list price, pilots included, over the runs of PLAN
# The run-time limit of openai_r9 for the steps of this module: the committed money at 15:07 UTC on 2026-11-15
# (committed_no_em) plus the console balance of the account (withheld in this repository; README.md, section 8),
# rounded down to the cent, so that the cap (CAP) and this limit agree. lib/accounts.py does not change (its
# limit stays for every other run).
LIMIT = 175.97
ACCOUNT = "openai_r9"
RELEASE_EXPS = ("R", "S", "M", "C", "K", "K2", "K3")  # the release-test runs of R10-6, R10-14 to R10-16, R10-20 to R10-24

# cell: (system text, tools, the parse arm of the scored names and values)
CELLS = {
    "t0": (tools.tool_system("t0"), tools.TOOLS["t0"], "t0"),
    "trep": (tools.tool_system("t0"), tools.TOOLS["t0"], "t0"),
    "tord": (tools.tool_system("t0"), [control.ordered_tool()], "t0"),
    "tpar": (tools.tool_system("t0"), [harmless.paraphrased_tool()], "t0"),
    "tpar2": (tools.tool_system("t0"), [harmless2.paraphrased_tool2()], "t0"),
    "t1": (tools.tool_system("t1"), tools.TOOLS["t1"], "t1"),
}
CONTROL = "t0"
UPDATES = {"repeat": "trep", "field-order edit": "tord", "paraphrase 1": "tpar", "paraphrase 2": "tpar2",
           "full rename": "t1"}
PLAN = {"erk4_luna": ("t0", "trep", "tord", "tpar", "tpar2", "t1"), "erk4_sol": ("t0", "trep", "t1")}
RUNS = tuple(PLAN)
MODEL_OF = {"erk4_luna": "luna", "erk4_sol": "sol"}
# The stored requests that each cell must equal, byte for byte in the body except the user text (prove_same).
EARLIER = {"t0": "erk_{m}", "trep": "erk_{m}", "tpar": "erk_{m}", "t1": "erk_{m}", "tord": "erk2_{m}",
           "tpar2": "erk2_{m}"}
NEW_TEXTS = harmless.NEW_TEXTS + harmless2.NEW_TEXTS

_cache = {}


# ---------------------------------------------------------------------------------------------------- selection

def release_test_ids():
    """The dialogue ids of every request of the earlier release-test runs (rebuilt offline from runs.RUNS)."""
    if "sent" not in _cache:
        import runs
        _cache["sent"] = {r["custom_id"].split("-")[1] + ".json" for n, run in runs.RUNS.items()
                          if run.exp in RELEASE_EXPS for r in runs.requests(n)}
    return _cache["sent"]


def select(data, g):
    """{"pool": counts, "open": sorted ids, "specific": sorted ids}. MultiWOZ texts and briefs only.

    Pool: the 2,874 training dialogues whose goal has hotel and at least one other domain (common.e7_ids), minus the
    554 prefixes of experiment A, minus the dialogues of every release-test request, minus the protected lists
    (groups.protected: Track P pool, validation, test, wave-1 gate and pool), with a traveller turn that says "hotel"
    or "hotels" (zforms.WORD; the cut point of zforms.prefix_text). Open: gold.brief_type of info and of fail_info
    both None. Specific: gold.brief_type(d) == "hotel". Draw: random.Random(SEED).sample(sorted open, 448) and
    random.Random(SEED + 1).sample(sorted specific, 59); fewer when fewer exist."""
    if "sel" in _cache:
        return _cache["sel"]
    import common
    import gold
    import groups as grp
    import zforms
    booked = set(g["booked"])
    sent = release_test_ids()
    protected = set().union(*grp.protected(data).values())
    e7 = common.e7_ids(data)
    pool = [d for d in e7 if d not in booked and d not in sent and d not in protected]
    says = [d for d in pool if any(zforms.WORD.search(t) for t in gold.traveller(data[d]))]
    elig = {"open": [d for d in says if gold.brief_type(data[d]) is None
                     and gold.brief_type(data[d], "fail_info") is None],
            "specific": [d for d in says if gold.brief_type(data[d]) == "hotel"]}
    out = {"pool": {"e7": len(e7), "after_exclusions": len(pool), "traveller_says_hotel": len(says),
                    "eligible_open": len(elig["open"]), "eligible_specific": len(elig["specific"]),
                    "release_test_dialogues": len(sent), "release_test_outside_554": len(sent - booked)}}
    for k, (s, n) in {"open": (SEED, SIZES["open"]), "specific": (SEED + 1, SIZES["specific"])}.items():
        ids = sorted(elig[k])
        out[k] = sorted(random.Random(s).sample(ids, min(n, len(ids))))
    _cache["sel"] = out
    return out


def set_of(data, g):
    sel = select(data, g)
    return {d: k for k in ("open", "specific") for d in sel[k]}


# ---------------------------------------------------------------------------------------------------- requests

def cell_request(model, cid, user, cell):
    import models
    system, tl, _ = CELLS[cell]
    return models.request(model, cid, user, system, None, tools=tl, cell=cell)


def build(name, model, reads, data, g):
    """The cells of PLAN[name] on the fresh prefixes in dialogue-id order, READS answers per cell and prefix. Per
    prefix and read, the cells follow each other, control first. `reads` must be 1."""
    import groups as grp
    import runs
    import zforms
    assert reads == 1 and MODEL_OF[name] == model, (name, model, reads)
    if "new_text" not in _cache:  # the constructed texts copy no sentence of a main-study item
        grp.assert_new_text(tools.NEW_TEXTS + NEW_TEXTS)
        _cache["new_text"] = True
    sets = set_of(data, g)
    out = []
    for d in sorted(sets):
        user = zforms.prefix_text(data[d])
        for read in range(1, READS[sets[d]] + 1):
            for cell in PLAN[name]:
                out.append(cell_request(model, runs.cid(name, d, cell, read), user, cell))
    return out


def parse_row(row, cell):
    """("search", F0 fields), ("none", text) or ("invalid", reason): tools.parse_call with the cell's names."""
    return tools.parse_call(row, CELLS[cell][2])


def register():
    import runs
    for n in PLAN:
        runs.RUNS.setdefault(n, runs.Run("K4", MODEL_OF[n], ACCOUNT, 1, build, pilot=2))


# ---------------------------------------------------------------------------------------------------- checks

def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    order = "(" + ", ".join(control.ordered_tool()["input_schema"]["properties"]) + ")"
    for words in (harmless.TOOL_PARAPHRASE, harmless2.TOOL_PARAPHRASE2, tools.SEARCH_DESCRIPTION, order,
                  "Status: exploratory, fixed in the protocol before the run.", f"seed {SEED}",
                  f"{SIZES['open']} open", f"{SIZES['specific']} specific", f"{CAP:.2f} USD", *RUNS):
        if words not in flat:
            sys.exit(f"Not run. R10-27 does not hold {words!r}.")


def prove_same(model):
    """Each cell equals the stored request of the earlier release test of the same model, prefix and cell, except the
    custom_id: build the cell on a 554 prefix and compare with requests.jsonl of erk_<m> or erk2_<m> (requests only)."""
    import zforms
    import runs
    data, g = runs.context()
    out = {}
    for cell, folder in EARLIER.items():
        folder = folder.format(m=model)
        assert not folder.startswith("em")
        stored = {}
        for line in (EXPLORE / folder / "requests.jsonl").read_text().splitlines():
            r = json.loads(line)
            _, d, c, read = r["custom_id"].split("-")
            if c == cell and read == "1" and len(stored) < 5:
                stored[d + ".json"] = r["body"]
        same = all(cell_request(model, "x", zforms.prefix_text(data[d]), cell)["body"] == body
                   for d, body in stored.items())
        out[cell] = (folder, len(stored), same)
    return out


# ---------------------------------------------------------------------------------------------------- money

def committed_no_em(a):
    """accounts.committed without opening a folder whose name starts with "em": the batches of e*/mp* folders as
    accounts.committed counts them, the fetched em* batches by their ledger rows, and the open steps of e*/mp* folders."""
    import accounts
    path = EXPLORE / a.ledger
    rows = list(csv.DictReader(open(path))) if path.exists() else []
    actual = {r["experiment"]: float(r["list_price_usd"]) for r in rows if r["step"] == "batch"}
    steps = sum(float(r["list_price_usd"]) for r in rows if r["step"] != "batch")
    batches = held = 0.0
    seen = set()
    for p in sorted(EXPLORE.iterdir()):
        n = p.name
        if n.startswith(("em", "._")) or not n.startswith(accounts.PREFIXES) or not p.is_dir():
            continue
        b = p / "batch.json"
        if b.exists():
            info = json.loads(b.read_text())
            if info.get("account", accounts.OLD) == a.name:
                batches += actual[n] * accounts.factor(a) if n in actual else info["bound"]
                seen.add(n)
        for h in p.glob("*.open.json"):
            if not h.name.startswith("._"):
                info = json.loads(h.read_text())
                if info.get("account", accounts.OLD) == a.name:
                    held += info["bound"]
    batches += sum(v * accounts.factor(a) for k, v in actual.items() if k.startswith("em") and k not in seen)
    return batches + steps * accounts.factor(a) + held


def patch_accounts():
    """For the steps of this module only: accounts.committed opens no em* folder, and the limit of ACCOUNT is LIMIT."""
    import accounts
    accounts.committed = committed_no_em
    a = accounts.ACCOUNTS[ACCOUNT]
    if a.limit < LIMIT:
        accounts.ACCOUNTS[ACCOUNT] = a._replace(limit=LIMIT)


def used():
    """The money of the runs of PLAN, as newmoney.used counts it: ledger list prices, the bound of every batch without
    a ledger row, and the bound of every open step."""
    import accounts
    a = accounts.ACCOUNTS[ACCOUNT]
    path = EXPLORE / a.ledger
    rows = [r for r in csv.DictReader(open(path)) if r["experiment"] in PLAN] if path.exists() else []
    total = sum(float(r["list_price_usd"]) for r in rows)
    fetched = {r["experiment"] for r in rows if r["step"] == "batch"}
    for n in PLAN:
        folder = EXPLORE / n
        if not folder.exists():
            continue
        b = folder / "batch.json"
        if b.exists() and n not in fetched:
            total += json.loads(b.read_text())["bound"]
        for h in folder.glob("*.open.json"):
            if not h.name.startswith("._"):
                total += json.loads(h.read_text())["bound"]
    return round(total, 4)


def check_cap(bound):
    u = used()
    if u + bound > CAP + 1e-9:
        sys.exit(f"Not run. R10-27 has used {u:.4f} USD; {bound:.2f} more would pass the cap of {CAP:.2f} USD.")
    print(f"R10-27 on {ACCOUNT}: {u:.4f} USD used, {u + bound:.4f} USD with this step (cap {CAP:.2f})")


def status():
    import accounts
    import budget_gate
    patch_accounts()
    a = accounts.ACCOUNTS[ACCOUNT]
    a = accounts.ACCOUNTS[ACCOUNT]
    print(f"{ACCOUNT}: limit {a.limit:.2f}, committed (no em* folder opened) {accounts.committed(a):.4f}, free after "
          f"the 2.00 USD reserve {budget_gate.free(ACCOUNT):.4f}; R10-27 used {used():.4f} of {CAP:.2f}")


# ---------------------------------------------------------------------------------------------------- entry

def main(name):
    """The paid steps of one run: the R10-27 checks, then runs.main unchanged."""
    import runs
    register()
    patch_accounts()
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step in ("pilot", "submit"):
        check_amendment()
        if "--approve" in sys.argv:
            check_cap(float(sys.argv[sys.argv.index("--approve") + 1]))
    return runs.main(name)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-27 holds the texts, the seed, the sizes, the cap and the run names")
    elif cmd == "select":
        import runs
        data, g = runs.context()
        sel = select(data, g)
        print(json.dumps({"pool": sel["pool"], "open": len(sel["open"]), "specific": len(sel["specific"])}, indent=1))
    elif cmd == "ids":
        import runs
        data, g = runs.context()
        sel = select(data, g)
        print(json.dumps({k: sel[k] for k in ("open", "specific")}))
    elif cmd == "show":
        for c, (system, tl, arm) in CELLS.items():
            print(c, arm, tl[0]["description"], list(tl[0]["input_schema"]["properties"]))
    elif cmd == "status":
        status()
    elif cmd == "prove":
        register()
        for m in ("luna", "sol"):
            print(m, prove_same(m))
    elif cmd == "manifest":
        import runs
        register()
        runs.write_manifest(list(RUNS))
    else:
        sys.exit(__doc__)
