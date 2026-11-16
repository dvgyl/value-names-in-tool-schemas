"""Amendment R10-23 (PROTOCOL.md): the steering runs when the agent can search again. Exploratory, fixed in the
protocol before the run. For the paper. No real person is involved: the traveller turns are corpus text.

Question: the service rewrites H1 and G1 (R10-14) raised the exclusion of the first search, and each answer of those
runs allowed one search call. Does the steering stay when the agent can search again and sees each result?

Design. The first requests and the tools of the steering runs: the 554 prefixes of experiment A (zforms.prefix_text),
cells t0 (the original tool), h1 (steer/edit_h.json) and g1 (steer/edit_g.json), the cell names of R10-15. Two changes:
1. The system text is flag.multi_system("t0"): the two one-search sentences of the tool text are replaced, as in R10-7
   (experiment W) and R10-8 (later turns).
2. The agent may call search_hotels up to MAX_CALLS times (turns.MAX_CALLS). Each search call gets one tool result:
   json.dumps(briefsearch.result_rows(search)) (the first 5 venues and the total), in the names of the cell's tool
   (`display`). A call that does not parse gets ERROR_RESULT (the text of turns.py). The conversation ends at an answer
   without a call, or after the 4th answer (a call in the 4th answer gets no result). No traveller turn follows.
The conversation runs in rounds: round k sends the k-th call of every conversation that is still open. Each round is
one batch run (erq<k>_<model>), so the main run has batch prices. A round-k request is built from the stored answers of
rounds 1 to k-1 (`requests`). The pilot runs whole conversations synchronously with the same request code (`pilot`).

Models (PLAN): Haiku (anthropic_r9b; the open set), Sol and Luna (openai_r9; the three sets; Luna 2 answers).
Usage (from explore/): .venv/bin/python -I r10/steer3.py check | show | project | next <model> | status
       .venv/bin/python -I r10/erq1_<model>.py estimate | pilot [--approve X]     (the conversation pilot)
       .venv/bin/python -I r10/erq<k>_<model>.py estimate | submit --approve X | fetch
"""
import collections
import concurrent.futures as cf
import hashlib
import json
import math
import pathlib
import sys
import threading
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import briefsearch as bs  # noqa: E402
import flag  # noqa: E402
import release  # noqa: E402
import steer2  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

AMENDMENT = "### R10-23 "
CELLS = ("t0", "h1", "g1")
CONTROL = "t0"
MAX_CALLS = 4  # turns.MAX_CALLS (R10-8); tests/test_steer3_harmless3.py checks that the two agree
ROUNDS = tuple(range(1, MAX_CALLS + 1))
ERROR_RESULT = "The arguments are not valid for search_hotels."  # the text of turns.py (R10-8)
NEW_TEXTS = (ERROR_RESULT,)
MAX_BOUND = 4.00  # USD per step of R10-23
RESERVE = 0.00  # the caps of newmoney.py (group R23) hold the margin, as in R10-19 to R10-22
MARGIN = 1.25


class Plan(NamedTuple):
    account: str
    sets: tuple  # request sets of control.set_of
    reads: int  # answers per prefix and cell


# The cut order of R10-23, if the projected OpenAI bounds pass the cap: first Sol's specific and guesthouse sets, then
# Luna's second answer. A cut is a change of PLAN with a dated note in R10-23 before the first submit of the model.
PLAN = {
    "haiku": Plan("anthropic_r9b", ("open",), 1),
    "sol": Plan("openai_r9", ("open", "specific", "guesthouse"), 1),
    "luna": Plan("openai_r9", ("open", "specific", "guesthouse"), 2),
}
MODELS = tuple(PLAN)
PILOT_PREFIXES = 3  # per model: the same 3 prefixes in each cell, 1 answer (9 conversations)
PILOT_CAP = {"haiku": 0.05, "sol": 0.40, "luna": 0.05}  # hard caps of the conversation pilots, USD at list prices
PILOT_WORKERS = 3


def run_name(model, k):
    return f"erq{k}_{model}"


RUNS = tuple(run_name(m, k) for m in MODELS for k in ROUNDS)


def parse_run(name):
    """(model, round) of a run name erq<k>_<model>."""
    head, model = name.split("_", 1)
    assert head.startswith("erq") and model in PLAN, name
    return model, int(head[3:])


SYSTEM = flag.multi_system("t0")


def tool_of(cell):
    return tools.TOOLS["t0"] if cell == CONTROL else [steer2.cell_tool(cell)]


def unquote(v):
    """The quote rule of R10-23 (a note after the first Haiku pilot, before any batch): a string value that starts and
    ends with a double quote is read without the two quotes; a list is read item by item. Haiku wrote the option "any"
    as the string "\"any\"" in 2 of 9 pilot conversations, and the search then found no venue."""
    if isinstance(v, str) and len(v) >= 2 and v[0] == v[-1] == '"':
        return v[1:-1]
    if isinstance(v, list):
        return [unquote(x) for x in v]
    return v


def clean_row(row):
    """The row with the quote rule applied to the input of each tool call (the row itself does not change)."""
    calls = row.get("tool_calls") or []
    if not any(isinstance(c.get("input"), dict) for c in calls):
        return row
    return {**row, "tool_calls": [{**c, "input": {k: unquote(x) for k, x in c["input"].items()}}
                                  if isinstance(c.get("input"), dict) else c for c in calls]}


def parse(row, cell):
    """("search", F0 fields), ("none", text) or ("invalid", reason) of one answer, after the quote rule (`unquote`):
    tools.parse_call for t0, and steer2.parse_call (the rewrite maps back to the F0 names and values) for h1 and g1."""
    row = clean_row(row)
    return tools.parse_call(row, "t0") if cell == CONTROL else steer2.parse_call(row, cell)


def display(rows, cell):
    """The result rows in the names of the cell's tool: each field that is a parameter gets the rewrite's parameter name,
    and each option value gets the rewrite's value (steer2.edit: params and values). t0 keeps its rows."""
    if cell == CONTROL:
        return rows
    e = steer2.edit(cell)
    out = []
    for r in rows["results"]:
        x = {}
        for k, v in r.items():
            vals = e["values"].get(k, {})
            x[e["params"].get(k, k)] = vals.get(release.key(v), v)
        out.append(x)
    return {"results": out, "total": rows["total"]}


def provider(model):
    import models
    return models.PROVIDER[model]


def first_request(name, model, d, cell, read, user):
    import models
    import runs
    return models.request(model, runs.cid(name, d, cell, read), user, SYSTEM, None, tools=tool_of(cell), cell=cell)


def history_request(name, model, d, cell, read, history):
    import models
    import runs
    if provider(model) == "anthropic":
        return models.request(model, runs.cid(name, d, cell, read), None, SYSTEM, None, tools=tool_of(cell),
                              messages=history, cell=cell)
    return models.request(model, runs.cid(name, d, cell, read), None, None, None, tools=tool_of(cell),
                          input_items=history, cell=cell)


def initial_history(model, user):
    """The first request as a history: Claude messages, or OpenAI input items (the system item, then the user item)."""
    if provider(model) == "anthropic":
        return [{"role": "user", "content": user}]
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


CUT = flag.CUT


class Conv:
    """One conversation: the history that the next request sends, the answer rows, the searches and the status.
    Status: "open" (a next call is due), "complete" (an answer without a call), "calls" (the 4th answer held a call),
    "failed" (a row did not succeed), "cut" (a row stopped at the output cap), "multi" (an answer with more than one
    call), "absent" (no row for a request that was sent)."""

    def __init__(self, model, d, cell, read, user):
        self.model, self.d, self.cell, self.read = model, d, cell, read
        self.history = initial_history(model, user)
        self.rows, self.searches, self.texts, self.status = [], [], [], "open"

    def add(self, row, db):
        k = len(self.rows) + 1
        assert self.status == "open" and k <= MAX_CALLS, (self.d, self.cell, self.status, k)
        self.rows.append(row)
        if row.get("type", "succeeded") != "succeeded":
            self.status = "failed"
            return
        if row.get("stop") in CUT:
            self.status = "cut"
            return
        if (row.get("text") or "").strip():
            self.texts.append(row["text"].strip())
        calls = row.get("tool_calls") or []
        if not calls:
            self.status = "complete"
            return
        if len(calls) > 1:
            self.status = "multi"
            return
        kind, fields = parse(row, self.cell)
        s = {"call": k, "kind": kind}
        if kind == "search":
            found = bs.search(db, fields)
            s.update(fields=fields, total=len(found), shown=[v["name"] for v in found[:5]])
            result, error = json.dumps(display(bs.result_rows(found), self.cell)), False
        else:
            s["reason"] = fields
            result, error = ERROR_RESULT, True
        self.searches.append(s)
        if k == MAX_CALLS:
            self.status = "calls"
            return
        call = calls[0]
        if "id" not in call:  # repository copy: the answer rows hold no call ids and content blocks (README.md, section 9)
            self.history = None  # the next request cannot be built; the outcomes of the analysis do not need it
            return
        if provider(self.model) == "anthropic":
            tr = {"type": "tool_result", "tool_use_id": call["id"], "content": result}
            if error:
                tr["is_error"] = True
            self.history = self.history + [{"role": "assistant", "content": row["content"]},
                                           {"role": "user", "content": [tr]}]
        else:
            self.history = self.history + list(row["output_items"]) + [
                {"type": "function_call_output", "call_id": call["id"], "output": result}]

    def reply(self):
        """The text that the traveller sees: the text blocks of all answers, joined (as turns.py)."""
        return "\n\n".join(self.texts)

    def record(self):
        """The conversation for the analysis (no request text)."""
        first = None
        if self.rows and self.rows[0].get("type", "succeeded") == "succeeded" and self.rows[0].get("stop") not in CUT:
            first = parse(self.rows[0], self.cell)
        return {"dialogue": self.d, "cell": self.cell, "read": self.read, "status": self.status, "calls": len(self.rows),
                "first": None if first is None else [first[0], ser(first[1]) if first[0] == "search" else None],
                "searches": [{k: (ser(v) if k == "fields" else v) for k, v in s.items()} for s in self.searches],
                "reply": self.reply()}


def ser(fields):
    """Parsed fields with lists for tuples (JSON)."""
    return {f: (list(x) if isinstance(x, tuple) else x) for f, x in fields.items()}


def keys(model, data, g):
    """[(dialogue id, cell, read)] of the plan of `model`, in request order: per prefix and read, the cells follow each
    other, control first."""
    import control
    p = PLAN[model]
    sets = control.set_of(data, g)
    return [(d, cell, read) for d in g["booked"] if sets[d] in p.sets for read in range(1, p.reads + 1) for cell in CELLS]


def rows_of(model, k, source):
    """{(dialogue id, cell, read): row} of round k ("raw": the fetched batch; "pilot": the conversation pilot). None when
    the file does not exist."""
    folder = EXPLORE / run_name(model, k)
    assert not folder.name.startswith("em"), folder
    path = folder / ("raw.jsonl" if source == "raw" else "pilot_raw.jsonl")
    if not path.exists():
        return None
    out = {}
    for line in path.read_text().splitlines():
        r = json.loads(line)
        _, did, cell, read = r["custom_id"].split("-")
        out[(did + ".json", cell, int(read))] = r
    return out


def replay(model, upto, data, g, source="raw", conv_keys=None, db=None, strict=True):
    """The conversations after rounds 1 .. `upto` of the stored rows. A round without its file stops the replay with
    RuntimeError, unless no conversation is open (strict), or leaves the open conversations open (not strict)."""
    import gold
    db = db or gold.hotel_db()
    convs = [Conv(model, d, cell, read, zforms.prefix_text(data[d])) for d, cell, read in (conv_keys or keys(model, data, g))]
    for k in range(1, upto + 1):
        todo = [c for c in convs if c.status == "open"]
        if not todo:
            break
        rows = rows_of(model, k, source)
        if rows is None and not strict:
            break
        if rows is None:
            raise RuntimeError(f"{run_name(model, k)}: no {'raw' if source == 'raw' else 'pilot_raw'}.jsonl; round {k} "
                               f"is not fetched")
        for c in todo:
            row = rows.get((c.d, c.cell, c.read))
            if row is None:
                c.status = "absent"
            else:
                c.add(row, db)
    return convs


def requests(name, model, data, g):
    """The requests of round k: the first requests (k = 1), or the k-th call of each open conversation."""
    _, k = parse_run(name)
    if k == 1:
        return [first_request(name, model, d, cell, read, zforms.prefix_text(data[d])) for d, cell, read in
                keys(model, data, g)]
    convs = replay(model, k - 1, data, g)
    return [history_request(name, model, c.d, c.cell, c.read, c.history) for c in convs
            if c.status == "open" and len(c.rows) == k - 1]


def build(k):
    """The build function of round k for runs.RUNS."""
    def built(name, model, reads, data, g):
        assert parse_run(name) == (model, k) and reads == PLAN[model].reads, (name, model, reads)
        return requests(name, model, data, g)
    built.round = k
    return built


# ---------------------------------------------------------------- the conversation pilot (synchronous)

def pilot_prefixes(data, g, db=None):
    """The pilot prefixes (fixed in R10-23): open-set prefixes in the order of the SHA-256 of the id without ".json".
    The first 2 whose stored ers_haiku th read is a hotel-only search with an empty result, then the first 1 whose
    stored ers_haiku tg read is a guesthouse-only search with an empty result. Such a first search often leads to a
    second search, so the pilot runs the multi-call path."""
    import control
    import gold
    import steer
    db = db or gold.hotel_db()
    sets = control.set_of(data, g)
    stored = {}
    for line in (EXPLORE / "ers_haiku" / "raw.jsonl").read_text().splitlines():
        r = json.loads(line)
        _, did, cell, _ = r["custom_id"].split("-")
        stored[(did + ".json", cell)] = r
    order = sorted((d for d in g["booked"] if sets[d] == "open"),
                   key=lambda d: hashlib.sha256(d.removesuffix(".json").encode()).hexdigest())

    def empty_one_type(d, cell, keep, drop):
        r = stored.get((d, cell))
        if not r or r.get("type") != "succeeded":
            return False
        kind, f = steer.parse_call(r, cell)
        t = f.get("type") if kind == "search" else None
        return (isinstance(t, tuple) and keep in t and drop not in t and not bs.search(db, f))

    hot = [d for d in order if empty_one_type(d, "th", "hotel", "guesthouse")][:2]
    guest = [d for d in order if d not in hot and empty_one_type(d, "tg", "guesthouse", "hotel")][:1]
    assert len(hot) + len(guest) == PILOT_PREFIXES, (hot, guest)
    return hot + guest


def pilot_keys(data, g):
    return [(d, cell, 1) for d in pilot_prefixes(data, g) for cell in CELLS]


def worst(model, req):
    import anth
    import openai_compat as oc
    if provider(model) == "anthropic":
        p = req["params"]
        return anth.cost(p["model"], anth.est_in(req) * 1.5, p["max_tokens"], batch=False)
    return oc.worst(oc.APIS["openai"], req)


class Caller:
    """One synchronous call per request, under the hard cap of turns.Budget. Returns (row, cost at list prices)."""

    def __init__(self, model, a, budget):
        self.model, self.a, self.budget = model, a, budget
        if provider(model) == "anthropic":
            import anth
            self.client = anth.client(a)
        else:
            import accounts
            self.key = accounts.api_key(a)

    def __call__(self, req):
        x = worst(self.model, req)
        self.budget.reserve(x)
        actual = 0.0
        try:
            row, actual = (self.anthropic if provider(self.model) == "anthropic" else self.openai)(req)
        finally:
            self.budget.settle(x, actual)
        return row

    def anthropic(self, req):
        import anth
        msg = self.client.messages.create(**req["params"])
        row = anth.message_row(req["custom_id"], msg)
        row["content"] = [anth.block_dict(b) for b in msg.content]
        return row, anth.cost(msg.model, msg.usage.input_tokens, msg.usage.output_tokens, batch=False)

    def openai(self, req):
        import random
        import time
        import openai_compat as oc
        api = oc.APIS["openai"]
        for attempt in range(oc.ATTEMPTS):
            if attempt:
                time.sleep(2 ** attempt + random.random())
            try:
                status, body = api.post(self.key, req["body"])
            except oc.NoAnswer:
                continue
            if status == 200:
                row = oc.row(api, req["custom_id"], {"status": 200, "body": body.decode("utf-8", "replace")})
                cost = (oc.cost(api, req["body"]["model"], row["input_tokens"], row["output_tokens"], batch=False)
                        if row["type"] == "succeeded" else worst(self.model, req))
                return row, cost
            if status >= 500 or status in (408, 429):
                continue
            raise RuntimeError(f"HTTP {status} from openai: {body[:300]!r}")
        raise RuntimeError("no answer after the retries")


def drive(conv, model, caller, db, log):
    """Run one pilot conversation to its end. `log` collects (round, request, row)."""
    while conv.status == "open":
        k = len(conv.rows) + 1
        name = run_name(model, k)
        req = (first_request(name, model, conv.d, conv.cell, conv.read, conv.history[-1]["content"]) if k == 1 else
               history_request(name, model, conv.d, conv.cell, conv.read, conv.history))
        row = caller(req)
        log.append((k, req, row))
        conv.add(row, db)


def cell_key(model, req):
    import anth
    import openai_compat as oc
    return "|".join(anth.cell(req) if provider(model) == "anthropic" else oc.cell(req))


def est_in(model, req):
    import anth
    import openai_compat as oc
    return anth.est_in(req) if provider(model) == "anthropic" else oc.est_in(req)


def size_summary(model, entries):
    """pilot.json entries in the format of the clients: per cell, in_ratio and out_mean (pilot sizes of the round). A
    cell without a pilot row in a round gets the pooled sizes of the round ("pooled": true)."""
    by = collections.defaultdict(list)
    for req, row in entries:
        if row.get("type", "succeeded") == "succeeded":
            by[cell_key(model, req)].append((row["input_tokens"], est_in(model, req), row["output_tokens"],
                                            row.get("stop"), row.get("reasoning_tokens", 0) or 0))

    def summ(v):
        return {"in_ratio": sum(x[0] for x in v) / sum(x[1] for x in v), "out_mean": sum(x[2] for x in v) / len(v),
                "out_max": max(x[2] for x in v), "reasoning_mean": sum(x[4] for x in v) / len(v),
                "stops": sorted({str(x[3]) for x in v}), "n": len(v)}
    out = {k: summ(v) for k, v in by.items()}
    pooled = [x for v in by.values() for x in v]
    return out, (summ(pooled) if pooled else None)


def write_pilot(model, log, convs):
    """Per round: erq<k>_<model>/pilot_raw.jsonl and pilot.json. The pilot.json of a round without a row gets the pooled
    sizes of the last round with rows. erq1_<model>/pilot_conversations.jsonl holds the records."""
    import accounts
    import anth
    import openai_compat as oc
    first = accounts.folder(run_name(model, 1))
    first.mkdir(parents=True, exist_ok=True)
    with open(first / "pilot_log.jsonl", "w") as fh:  # every call of the pilot, before the files per round
        fh.writelines(json.dumps({"round": k, "row": row}) + "\n" for k, _, row in log)
    prev = None
    for k in ROUNDS:
        entries = [(req, row) for kk, req, row in log if kk == k]
        folder = accounts.folder(run_name(model, k))
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / "pilot_raw.jsonl", "w") as fh:
            fh.writelines(json.dumps(row) + "\n" for _, row in entries)
        out, pooled = size_summary(model, entries)
        pooled = pooled or prev
        base = anth.cell if provider(model) == "anthropic" else oc.cell
        probe = first_request(run_name(model, k), model, "X.json", CONTROL, 1, "x")
        for cell in CELLS:
            key = "|".join(base({**probe, "cell": cell}))
            if key not in out and pooled is not None:
                out[key] = {**pooled, "pooled": True}
        (folder / "pilot.json").write_text(json.dumps(out, indent=1))
        prev = pooled
    with open(EXPLORE / run_name(model, 1) / "pilot_conversations.jsonl", "w") as fh:
        fh.writelines(json.dumps(c.record()) + "\n" for c in convs)


def pilot(model, approve):
    """The conversation pilot of R10-23: PILOT_PREFIXES prefixes x 3 cells x 1 answer, synchronous, list prices, under
    the hard cap PILOT_CAP[model]. The run name of the ledger row is erq1_<model>, step "pilot"."""
    import accounts
    import budget_gate
    import gold
    import newmoney
    import runs
    import turns
    data, g = runs.context()
    db = gold.hotel_db()
    a = accounts.account(PLAN[model].account, ("anthropic", "openai"))
    name = run_name(model, 1)
    bound = PILOT_CAP[model]
    convs = [Conv(model, d, cell, read, zforms.prefix_text(data[d])) for d, cell, read in pilot_keys(data, g)]
    print(f"{name} pilot: {len(convs)} conversations of up to {MAX_CALLS} calls, synchronous, hard cap {bound:.2f} USD "
          f"at list prices (enforced before each call)")
    newmoney.check(a.name, bound, newmoney.R23)
    if approve is not None and not budget_gate.fits(a.name, bound, RESERVE):
        sys.exit(f"Not run. {name}: {bound:.2f} USD does not fit the free money of {a.name}.")
    accounts.check_approval(a, approve, bound)
    budget = turns.Budget(bound)
    held = accounts.hold(a, name, "pilot", bound)
    log, lock, errors = [], threading.Lock(), []
    try:
        caller = Caller(model, a, budget)

        def one(c):
            own = []
            try:
                drive(c, model, caller, db, own)
            except turns.CapReached as e:
                c.status = "cap"
                errors.append(f"{c.d} {c.cell}: cap ({e})")
            except Exception as e:  # an API error after the retries: the conversation ends
                c.status = "error"
                errors.append(f"{c.d} {c.cell}: {type(e).__name__}: {str(e)[:200]}")
            with lock:
                log.extend(own)
        with cf.ThreadPoolExecutor(PILOT_WORKERS) as ex:
            list(ex.map(one, convs))
    finally:
        accounts.ledger(a, name, "pilot", bound, budget.spent)
        held.unlink()
    order = {(c.d, c.cell): i for i, c in enumerate(convs)}
    log.sort(key=lambda x: (x[0], order[(x[1]["custom_id"].split("-")[1] + ".json", x[1]["cell"])]))
    write_pilot(model, log, convs)
    for e in errors:
        print("  stopped:", e)
    print(f"{name} pilot: {len(log)} calls, spent {budget.spent:.4f} USD at list prices (cap {bound:.2f})")
    print(pilot_report(model))


def pilot_report(model, records=None):
    """The pilot rule of R10-23, printed: every conversation ends with status complete or calls; at least one
    conversation has 2 or more searches and ends with an answer without a call (the multi-call path ran)."""
    if records is None:
        path = EXPLORE / run_name(model, 1) / "pilot_conversations.jsonl"
        records = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    st = collections.Counter(r["status"] for r in records)
    multi = [r for r in records if len(r["searches"]) >= 2 and r["status"] == "complete"]
    ok = bool(records) and set(st) <= {"complete", "calls"} and bool(multi)
    lines = [f"{run_name(model, 1)} conversation pilot: {len(records)} conversations, status {dict(st)}; "
             f"{len(multi)} with 2 or more searches and a final answer: {'PASS' if ok else 'FAIL'}"]
    for r in records:
        s = "; ".join(f"call {x['call']} {x['kind']} type={x.get('fields', {}).get('type')} total={x.get('total')}"
                      for x in r["searches"])
        lines.append(f"  {r['dialogue']} {r['cell']}: {r['status']}, {r['calls']} calls [{s}]; reply "
                     f"{len(r['reply'])} chars")
    return "\n".join(lines)


def pilot_parses(row, cell, k):
    """pilot_check for erq runs: an answer parses when it is a valid search call of the cell's tool or a text answer
    without a call (round 1: also counted as a tool cell)."""
    if row.get("tool_calls"):
        return parse(row, cell)[0] == "search"
    return bool((row.get("text") or "").strip())


# ---------------------------------------------------------------- money

def call_cost(model, row, batch=True):
    """The price of one answer row at list prices (batch: half)."""
    import anth
    import models
    import openai_compat as oc
    mid = models.MODELS[model].id
    if provider(model) == "anthropic":
        return anth.cost(mid, row["input_tokens"], row["output_tokens"], batch=batch)
    return oc.cost(oc.APIS["openai"], mid, row["input_tokens"], row["output_tokens"], batch=batch)


def project(model, data, g):
    """The projection of all rounds of `model`, from the conversation pilot: per round k, (conversations of the plan) x
    (the share of pilot conversations with a k-th call) x (the mean batch price of a pilot call of round k). A round
    without a pilot call takes the price of the round before it. The pilot prefixes lead to more second searches than a
    random prefix, so the projection is high. None before the pilot."""
    path = EXPLORE / run_name(model, 1) / "pilot_conversations.jsonl"
    if not path.exists():
        return None
    recs = [json.loads(x) for x in path.read_text().splitlines()]
    n_conv = len(keys(model, data, g))
    out, last_c = {"conversations": n_conv, "rounds": {}}, 0.0
    for k in ROUNDS:
        rows = [r for r in (rows_of(model, k, "pilot") or {}).values() if r.get("type", "succeeded") == "succeeded"]
        c_k = sum(call_cost(model, r) for r in rows) / len(rows) if rows else last_c
        p_k = sum(r["calls"] >= k for r in recs) / len(recs)
        out["rounds"][k] = {"share": p_k, "cost_per_call": c_k, "expected": n_conv * p_k * c_k}
        last_c = c_k
    out["expected"] = sum(x["expected"] for x in out["rounds"].values())
    out["bound"] = cents_up(out["expected"] * MARGIN)
    return out


def cents_up(x):
    return math.ceil(round(x * 100, 6)) / 100


def submitted(model):
    """The rounds of `model` with a batch.json."""
    return [k for k in ROUNDS if (EXPLORE / run_name(model, k) / "batch.json").exists()]


def future(model, data, g, after=None):
    """The projected bound of the rounds of `model` after round `after` (default: after the last submitted round)."""
    pr = project(model, data, g)
    if pr is None:
        return None
    after = max(submitted(model), default=0) if after is None else after
    return cents_up(sum(x["expected"] for k, x in pr["rounds"].items() if k > after) * MARGIN)


def check_projection(name, bound):
    """Round 1 of a model goes only when the cap of group R23 holds: the money used, the printed bound of this round,
    the projected rounds 2 to 4 of this model, the projected rounds not yet submitted of the other R10-23 models of the
    account, and the estimated bounds of the R10-24 runs of the account that have no batch and no run step yet."""
    import harmless3
    import newmoney
    import runs
    model, k = parse_run(name)
    if k != 1:
        return
    data, g = runs.context()
    acc = PLAN[model].account
    own = future(model, data, g, after=1)
    if own is None:
        sys.exit(f"Not run. {name}: no conversation pilot.")
    others = 0.0
    for m in MODELS:
        if m != model and PLAN[m].account == acc:
            x = future(m, data, g)
            if x is None:
                sys.exit(f"Not run. {name}: {m} has no conversation pilot, so its money cannot be projected.")
            others += x
    r24 = harmless3.pending_bounds(acc)
    used = newmoney.used(acc, newmoney.R23)
    cap = newmoney.CAPS_R23[acc]
    total = used + bound + own + others + r24
    print(f"R10-23 projection on {acc}: used {used:.2f} + this round {bound:.2f} + rounds 2-4 of {model} {own:.2f} + "
          f"other R10-23 models {others:.2f} + R10-24 not run {r24:.2f} = {total:.2f} USD (cap {cap:.2f})")
    if total > cap + 1e-9:
        sys.exit(f"Not run. {name}: the projected R10-23 and R10-24 money ({total:.2f} USD) passes the cap of "
                 f"{cap:.2f} USD on {acc}. Apply the cut order of R10-23 first.")


def next_round(model):
    """After the fetch of round k: write the manifest entry of round k + 1 (runs.amend_manifest under R10-23) and print
    its requests and the submit command. Offline."""
    import runs
    data, g = runs.context()
    done = [k for k in ROUNDS if (EXPLORE / run_name(model, k) / "raw.jsonl").exists()]
    if not done:
        sys.exit(f"Not run. {run_name(model, 1)} is not fetched.")
    k = max(done) + 1
    if k > MAX_CALLS:
        print(f"{model}: all {MAX_CALLS} rounds are fetched.")
        return
    if (EXPLORE / run_name(model, k) / "batch.json").exists():
        sys.exit(f"{run_name(model, k)} already has a batch.")
    name = run_name(model, k)
    reqs = runs.requests(name)
    if not reqs:
        print(f"{model}: no conversation is open after round {k - 1}; the run of {model} is complete.")
        return
    man = json.loads(runs.MANIFEST.read_text())
    if name not in man:
        runs.amend_manifest("R10-23", [name])
    elif man[name] != {"requests": len(reqs), "sha256": runs.digest(reqs)}:
        sys.exit(f"Not run. {name}: the manifest entry differs from the requests built now.")
    print(f"{name}: {len(reqs)} requests (open conversations after round {k - 1}). Next:")
    print(f"  .venv/bin/python -I r10/{name}.py submit            (prints the bound)")
    print(f"  .venv/bin/python -I r10/{name}.py submit --approve <the printed bound>")


def status():
    import runs
    data, g = runs.context()
    for m in MODELS:
        fetched = [k for k in ROUNDS if (EXPLORE / run_name(m, k) / "raw.jsonl").exists()]
        if not fetched:
            print(f"{m}: no round fetched; {len(keys(m, data, g))} conversations planned")
            continue
        convs = replay(m, max(fetched), data, g)
        print(f"{m}: rounds fetched {fetched}; status {dict(collections.Counter(c.status for c in convs))}")


# ---------------------------------------------------------------- the amendment

def amendment_text():
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-23 is in PROTOCOL.md under the round-10 amendments and holds the new sentences, the result texts, the call
    limit, the plan and the run names."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    need = [flag.MULTI_ASK, flag.MULTI_END, tools.ASK_NEW, tools.END_NEW, ERROR_RESULT,
            f"at most {MAX_CALLS} calls", "Status: exploratory, fixed in the protocol before the run.",
            "steer/edit_h.json", "steer/edit_g.json", *(run_name(m, 1) for m in MODELS),
            "a string value that starts and ends with a double quote is read without the two quotes"]
    for m, p in PLAN.items():
        need.append(f"{m}: {p.account}, sets {', '.join(p.sets)}, {p.reads} answer{'s' if p.reads > 1 else ''} per "
                    f"prefix and cell")
    for words in need:
        if words not in flat:
            sys.exit(f"Not run. R10-23 does not hold {words!r}.")


def show():
    print("system text:\n" + SYSTEM)
    for c in CELLS[1:]:
        e = steer2.edit(c)
        print(f"{c}: {steer2.edit_path(c).relative_to(EXPLORE)}; params renamed "
              f"{ {p: q for p, q in e['params'].items() if p != q} }")
    for m, p in PLAN.items():
        print(f"{m}: {p.account}, sets {', '.join(p.sets)}, {p.reads} answer{'s' if p.reads > 1 else ''} per prefix and cell")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-23 holds the texts, the call limit, the plan and the run names")
    elif cmd == "show":
        show()
    elif cmd == "project":
        import runs
        data, g = runs.context()
        for m in MODELS:
            pr = project(m, data, g)
            print(m, "no pilot" if pr is None else json.dumps(pr, indent=1))
    elif cmd == "next" and len(sys.argv) > 2 and sys.argv[2] in PLAN:
        next_round(sys.argv[2])
    elif cmd == "status":
        status()
    elif cmd == "pilot-report":
        for m in MODELS:
            print(pilot_report(m))
    else:
        sys.exit(__doc__)
