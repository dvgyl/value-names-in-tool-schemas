"""Amendment R10-15 (PROTOCOL.md): more service rewrites, with and without a business interest, on one agent.
Exploratory, for the paper. No real person is involved: the traveller turns are corpus text.

1. `rewrite <h|g|n>`: Claude Opus 5.5 (models.MODELS["opus"], account anthropic_r9b) writes new rewrites of the search
   tool. Groups h and g send the R10-14 request of their direction (steer.rewrite_request), group n sends the R10-6
   request (release.rewrite_request); the params are those of the earlier calls. Per group, calls go in order until
   NEW_PER_GROUP answers are accepted (release.accept, the R10-6 rule), with at most MAX_CALLS calls. The accepted
   answers are frozen as steer2/edit_<group>2.json and edit_<group>3.json. Every answer goes into steer2/answers.jsonl.
   Ledger row: experiment "erm_edit", step "rewrite_<group>".
2. `build` (run erm_haiku, r10/runs.py): on the 554 prefixes of experiment A, the cell t0 (the request of
   runs.build_a) and one cell per frozen rewrite: h1 (steer/edit_h.json), h2, h3, g1 (steer/edit_g.json), g2, g3,
   n1 (release/edit.json), n2, n3. Only the tool differs from t0.
3. `parse_call(row, cell)`: as steer.parse_call, with the rewrite of the cell.
The money of R10-15 and R10-16 is shared: `check_shared(bound)` stops a step whose bound would pass SHARED_LIMIT.
Usage (from explore/): .venv/bin/python -I r10/steer2.py rewrite <h|g|n> [--approve <bound>] | show | check | shared
"""
import csv
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import natural  # noqa: E402
import release  # noqa: E402
import steer  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

AMENDMENT = "### R10-15 "
ACCOUNT, MODEL, LEDGER_NAME = "anthropic_r9b", "opus", "erm_edit"
MAX_CALLS, NEW_PER_GROUP = 4, 2  # per group
MAX_BOUND = 2.00  # USD per step of R10-15 or R10-16
SHARED_LIMIT = 4.50  # USD of bounds for R10-15 and R10-16 together, pilots and service calls included
SHARED_RUNS = ("erm_edit", "erm_haiku", "erc_haiku", "erc2_haiku", "erc2_sonnet")  # the experiments of both amendments
STEER2 = HERE / "steer2"
ANSWERS = STEER2 / "answers.jsonl"
GROUPS = ("h", "g", "n")
FIRST = {"h": steer.edit_path("h"), "g": steer.edit_path("g"), "n": release.EDIT}
CELLS = tuple(f"{grp}{i}" for grp in GROUPS for i in (1, 2, 3))


def edit_path(cell):
    return FIRST[cell[0]] if cell[1] == "1" else STEER2 / f"edit_{cell}.json"


def rewrite_request(group):
    """The request of the first rewrite of the group (R10-14 or R10-6), with its params unchanged."""
    return release.rewrite_request() if group == "n" else steer.rewrite_request(group)


_edits = {}


def edit(cell):
    """The frozen rewrite of a cell: {"obj", "params", "values", "rev"} as release.edit(); None when not frozen."""
    if cell not in _edits:
        path = edit_path(cell)
        if not path.exists():
            return None
        obj = json.loads(path.read_text())
        params, values = release.accept_obj(obj)
        rev = {p: {release.key(new): json.loads(k) for k, new in m.items()} for p, m in values.items()}
        _edits[cell] = {"obj": obj, "params": params, "values": values, "rev": rev}
    return _edits[cell]


def cells():
    """The cells whose rewrite is frozen, in the order h1 .. n3."""
    return [c for c in CELLS if edit_path(c).exists()]


def cell_tool(cell):
    t = edit(cell)["obj"]["tool"]
    return tools.tool(t["name"], t["description"], t["input_schema"])


def new_texts():
    return tuple(x for c in cells() for x in (edit(c)["obj"]["tool"]["description"],
                                              *release.texts(edit(c)["obj"]["tool"]["input_schema"])))


def to_old(args, cell):
    """A call's arguments with the F0 names and values (after tools.clean_nulls, amendment R10-3)."""
    e = edit(cell)
    args = tools.clean_nulls(args)
    out = {}
    for p, q in e["params"].items():
        rev = e["rev"][p]
        back = lambda x: rev.get(release.key(x), x)  # noqa: E731
        v = args.get(q)
        out[p] = None if v is None else [back(x) for x in v] if isinstance(v, list) else back(v)
    return out


def parse_call(row, cell):
    """As tools.parse_call. A rewrite cell: one search_hotels call, mapped back by to_old, then natural.parse (f0)."""
    if cell not in CELLS:
        return tools.parse_call(row, cell)
    calls = row.get("tool_calls") or []
    if not calls:
        return ("none", row.get("text", ""))
    if len(calls) > 1:
        return ("invalid", f"{len(calls)} tool calls")
    c = calls[0]
    if c["name"] != release.TOOL_NAME or not isinstance(c.get("input"), dict):
        return ("invalid", f"tool {c.get('name')!r} with input {type(c.get('input')).__name__}")
    try:
        return ("search", natural.parse(json.dumps(to_old(c["input"], cell)), natural.FORMS["f0"]))
    except (ValueError, KeyError, TypeError) as x:
        return ("invalid", f"{type(x).__name__}: {x}")


def build(name, model, reads, data, g):
    """Cell t0 and one cell per frozen rewrite, on the 554 prefixes; 1 read."""
    import models
    import runs
    assert reads == 1, reads
    system = tools.tool_system("t0")
    tool_of = {"t0": tools.TOOLS["t0"], **{c: [cell_tool(c)] for c in cells()}}
    out = []
    for d in g["booked"]:
        user = zforms.prefix_text(data[d])
        for c in tool_of:
            out.append(models.request(model, runs.cid(name, d, c, 1), user, system, None, tools=tool_of[c], cell=c))
    return out


def amendment_text(amendment=AMENDMENT):
    import runs
    text = runs.PROTOCOL.read_text().split(runs.AMEND, 1)[-1]
    if amendment not in text:
        return None
    body = text.split(amendment, 1)[1]
    ends = [i for i in (body.find("\n## "), body.find("\n### ")) if i >= 0]
    return amendment + (body[:min(ends)] if ends else body)


def sha256(cell):
    path = edit_path(cell)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def check_amendment(require_log=True):
    """R10-15 is in PROTOCOL.md under the round-10 amendments; R10-14 and R10-6 still hold the request texts verbatim
    (and the SHA-256 of h1, g1 and n1); (require_log) R10-15 holds the SHA-256 of each new frozen rewrite."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    steer.check_amendment()
    release.check_amendment()
    if require_log and any(sha256(c) not in text for c in cells() if c[1] != "1"):
        sys.exit("Not run. R10-15 does not hold the SHA-256 of each new frozen rewrite.")


# ---- the shared money of R10-15 and R10-16 ----
def shared_bounds():
    """The bounds of R10-15 and R10-16 so far on ACCOUNT: the bound of every ledger row of SHARED_RUNS, the bound of
    every batch of SHARED_RUNS that has no ledger row yet, and the bound of every open step."""
    import accounts
    a = accounts.ACCOUNTS[ACCOUNT]
    path = EXPLORE / a.ledger
    rows = [r for r in csv.DictReader(open(path)) if r["experiment"] in SHARED_RUNS] if path.exists() else []
    total = sum(float(r["bound_usd"]) for r in rows)
    fetched = {r["experiment"] for r in rows if r["step"] == "batch"}
    for n in SHARED_RUNS:
        b = EXPLORE / n / "batch.json"
        if b.exists() and n not in fetched:
            total += json.loads(b.read_text())["bound"]
        for h in (EXPLORE / n).glob("*.open.json") if (EXPLORE / n).exists() else ():
            if not h.name.startswith("._"):
                total += json.loads(h.read_text())["bound"]
    return round(total, 2)


def check_shared(bound):
    used = shared_bounds()
    if used + bound > SHARED_LIMIT + 1e-9:
        sys.exit(f"Not run. R10-15 and R10-16 have used {used:.2f} USD of bounds; {bound:.2f} more would pass the "
                 f"shared limit of {SHARED_LIMIT:.2f} USD.")
    print(f"shared bounds of R10-15 and R10-16: {used:.2f} USD used, {used + bound:.2f} USD with this step "
          f"(limit {SHARED_LIMIT:.2f})")


def answers(group=None):
    rows = [json.loads(x) for x in ANSWERS.read_text().splitlines()] if ANSWERS.exists() else []
    return [x for x in rows if group is None or x["group"] == group]


def rewrite(group, approve):
    import accounts
    import anth
    import budget_gate
    import runs
    runs.check_lock()
    check_amendment(require_log=False)
    a = accounts.account(ACCOUNT, ("anthropic",))
    done = answers(group)
    accepted = sum(x["accepted"] for x in done)
    if accepted >= NEW_PER_GROUP:
        sys.exit(f"Not run. Group {group} has {accepted} accepted new rewrites.")
    if len(done) >= MAX_CALLS:
        sys.exit(f"Not run. Group {group}: {len(done)} calls made; the group runs with the rewrites that it has.")
    req = rewrite_request(group)
    p = req["params"]
    left = MAX_CALLS - len(done)
    bound = round(left * anth.cost(p["model"], anth.est_in(req) * 1.5, p["max_tokens"], batch=False), 2)
    print(f"rewrite {group}: at most {left} synchronous calls (stop at {NEW_PER_GROUP - accepted} more accepted), "
          f"hard bound {bound:.2f} USD at max_tokens and list prices")
    if approve is not None:
        if bound > MAX_BOUND:
            sys.exit(f"Not run. R10-15 allows at most {MAX_BOUND:.2f} USD per step.")
        if not budget_gate.fits(ACCOUNT, bound):
            sys.exit(f"Not run. {bound:.2f} USD does not fit the free money of {ACCOUNT} minus the reserve.")
        check_shared(bound)
    accounts.check_approval(a, approve, bound)
    STEER2.mkdir(exist_ok=True)
    (STEER2 / f"request_{group}.json").write_text(json.dumps(req, indent=1) + "\n")
    cl = anth.client(a)
    step = f"rewrite_{group}"
    held = accounts.hold(a, LEDGER_NAME, step, bound)
    spent = 0.0
    try:
        for i in range(len(done) + 1, MAX_CALLS + 1):
            msg = cl.messages.create(**p)
            spent += anth.cost(msg.model, msg.usage.input_tokens, msg.usage.output_tokens, batch=False)
            row = anth.message_row(f"erm_edit-{step}-{i}", msg)
            try:
                obj, ok, reason = release.accept(row), True, "accepted"
            except release.Invalid as x:
                obj, ok, reason = None, False, str(x)
            cell = None
            if ok:
                accepted += 1
                cell = f"{group}{accepted + 1}"
                edit_path(cell).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
            with open(ANSWERS, "a") as fh:
                fh.write(json.dumps({"group": group, "call": i, "utc": accounts.now(timespec="seconds"),
                                     "accepted": ok, "cell": cell, "reason": reason, "row": row}) + "\n")
            print(f"call {i}: stop {row['stop']}, out {row['output_tokens']} tokens: {reason}"
                  + (f" -> {edit_path(cell).relative_to(EXPLORE)} SHA-256 {sha256(cell)}" if cell else ""))
            if accepted >= NEW_PER_GROUP:
                break
    finally:
        accounts.ledger(a, LEDGER_NAME, step, bound, spent)
        held.unlink()
        try:
            held.parent.rmdir()
        except OSError:
            pass
    print(f"spent {spent:.4f} USD at list prices; group {group}: {accepted} new rewrites accepted")


def show():
    for c in cells():
        e = edit(c)
        print(f"{c}: {edit_path(c).relative_to(EXPLORE)} SHA-256 {sha256(c)}")
        print(f"  tool description: {e['obj']['tool']['description']}")
        for p, q in e["params"].items():
            vals = {json.loads(k): v for k, v in e["values"][p].items() if json.loads(k) != v}
            print(f"  {p} -> {q}" + (f": {json.dumps(vals)}" if vals else ""))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "rewrite" and len(sys.argv) > 2 and sys.argv[2] in GROUPS:
        rewrite(sys.argv[2], sys.argv[sys.argv.index("--approve") + 1] if "--approve" in sys.argv else None)
    elif cmd == "show":
        show()
    elif cmd == "check":
        check_amendment()
        print("R10-15 holds the SHA-256 of each new frozen rewrite; R10-14 and R10-6 hold the request texts")
    elif cmd == "shared":
        print(f"{shared_bounds():.2f} USD of bounds used by R10-15 and R10-16 (limit {SHARED_LIMIT:.2f})")
    else:
        sys.exit(__doc__)
