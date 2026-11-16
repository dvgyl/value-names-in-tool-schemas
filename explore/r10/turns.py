"""Amendment R10-8 (PROTOCOL.md): later turns. Exploratory, for the paper.

Question: after a search failure at the first request, does the harm stay when the traveller keeps talking?

The agent (Claude Sonnet 5.5, models.MODELS["sonnet"]) gets the system text `flag.multi_system(arm)` (the tool text of
experiment A without the limit to one call), the tool of the arm (tools.TOOLS["t0"] or ["t1"]), and the first-request
prefix of experiment A (zforms.prefix_text) as the first user message. It may search more than once per turn and then
answers the traveller. Each search gets the real result: json.dumps(briefsearch.result_rows(search)) (the first 5 rows
and the total), in the names of the arm (`display`). The simulated traveller (Claude Haiku 5.5, models.MODELS["haiku"],
one call per traveller turn) gets SIM_SYSTEM and SIM_USER: the traveller's written brief (`hotel_brief`: the hotel part
of the corpus goal message) and the conversation so far. After the agent's first reply, the traveller speaks 3 times;
the agent answers each time. An agent turn has at most MAX_CALLS calls; a search call in the last of them gets its
result at the start of the next user message.

Synchronous calls, account anthropic_r9a, top-level automatic prompt caching (cache_control ephemeral) on the agent
calls. The history is append-only. A hard cap (`Budget`) stops the run before a call that could pass the approved bound.
Files: <run>/pilot_conversations.jsonl (pilot) and <run>/conversations.jsonl (run), one conversation per line.
Usage (from explore/): .venv/bin/python -I r10/<run>.py estimate | pilot | run | continue [--approve X]
(continue: amendment R10-11, the conversations of the run that are not complete, priced at the run's own mean cost.)
"""
import argparse
import concurrent.futures as cf
import json
import math
import pathlib
import random
import re
import sys
import threading

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import briefsearch as bs  # noqa: E402
import flag  # noqa: E402
import gold  # noqa: E402
import models  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

AMENDMENT = "### R10-8 "
AMENDMENT_9 = "### R10-9 "
AMENDMENT_11 = "### R10-11 "
CONTINUE_WORKERS = 1  # R10-11: with a small bound, the reserved worst cost of parallel calls would block calls
AGENT, TRAVELLER = "sonnet", "haiku"
ACCOUNT = "anthropic_r9a"
SEED = 20261112
N_PER_GROUP = 130  # R10-10 (R10-8: 90)
PILOT_PER_GROUP = 3
TRAVELLER_TURNS = 3
MAX_CALLS = 4
MAX_BOUND = 8.00
PILOT_CAP = 1.00
MARGIN = 1.25
MAX_ERRORS = 3  # the run stops after this many conversations end with an API error
WORKERS = 6
CACHE_WRITE = 1.25
CACHE_READ = {"claude-sonnet-5-5": 0.05, "claude-haiku-5-5": 0.10}  # of the input price (claude-api skill, 2026-11-03)

SIM_SYSTEM_R10_8 = (
    "You play a traveller who talks with a booking assistant in Cambridge about a place to stay. You get your brief "
    "and the conversation so far. Write only the traveller's next message, in one to three short sentences. Use only "
    "the requirements in your brief, and give them when the conversation needs them. Do not add a requirement that the "
    "brief does not give. Your brief calls every place to stay a hotel; a type of place is a requirement only when the "
    "brief says \"should be in the type of\". Do not name a type of place unless your brief or the conversation names "
    "it. If the assistant asks about something that your brief does not mention, say that it does not matter to you. "
    "The assistant can only search. Do not ask for a booking, and do not give booking details.")
# Amendment R10-9 (after the R10-8 pilot, before the run): in the pilot the traveller asked for bookings, addresses and
# phone numbers and went on with other parts of the trip. The traveller text gets two sentences, and the brief loses its
# booking sentences (BRIEF_DROP).
SIM_SYSTEM = (
    "You play a traveller who talks with a booking assistant in Cambridge about a place to stay. You get your brief "
    "and the conversation so far. Write only the traveller's next message, in one to three short sentences. Talk only "
    "about the place to stay. Use only the requirements in your brief, and give them when the conversation needs them. "
    "Do not add a requirement that the brief does not give. Your brief calls every place to stay a hotel; a type of "
    "place is a requirement only when the brief says \"should be in the type of\". Do not name a type of place unless "
    "your brief or the conversation names it. If the assistant asks about something that your brief does not mention, "
    "say that it does not matter to you. When the assistant has shown a place that meets every requirement of your "
    "brief, say that it suits you, and do not ask for anything new. The assistant can only search. Do not ask for a "
    "booking, an address, a phone number or a reference number.")
BRIEF_DROP = re.compile(r"^(Once you find|If the booking fails|Make sure you get)", re.I)
SIM_USER = "Your brief:\n{brief}\n\nThe conversation so far:\n{dialogue}\n\nWrite the traveller's next message."
NEW_TEXTS = (SIM_SYSTEM, SIM_USER.split("\n")[-1])

STARTS = re.compile(r"^You (are )?(also )?(looking for|want to book|planning|traveling|travelling)", re.I)
HOTEL_PART = re.compile(r"place to stay|particular hotel|looking for a hotel\b", re.I)
GUEST_WORD = re.compile(r"guest ?houses?", re.I)


def hotel_brief(d):
    """The hotel part of the goal message: the sentences from the one that starts the hotel part (it names "a place to
    stay", "a particular hotel" or "looking for a hotel") up to the next part (a sentence that matches STARTS), without
    HTML and without the booking sentences (BRIEF_DROP, amendment R10-9), joined with ". "."""
    parts, cur = [], []
    for s in d["goal"]["message"]:
        s = re.sub(r"<[^>]+>", "", s).strip()
        if STARTS.match(s) and cur:
            parts.append(cur)
            cur = []
        cur.append(s)
    parts.append(cur)
    hotel = [p for p in parts if HOTEL_PART.search(p[0])]
    assert len(hotel) == 1, (d["goal"]["message"], len(hotel))
    keep = [x for x in hotel[0] if not BRIEF_DROP.match(x)]  # R10-9: no booking sentences
    return ". ".join(x.rstrip(".") for x in keep) + "."


def groups(data, ids, db):
    """F: no-type prefixes whose fitting venues are all guesthouses (a hotel-only filter cannot show one); R: the other
    no-type prefixes (a hotel fits). Both sorted."""
    no_type = bs.brief_subsets(data, ids, db)["no_type"]
    fit = {d: bs.brief_fitting(data[d], db) for d in no_type}
    f = sorted(d for d in no_type if fit[d] and not any(v["type"] == "hotel" for v in fit[d]))
    r = sorted(d for d in no_type if any(v["type"] == "hotel" for v in fit[d]))
    return {"F": f, "R": r}


def orders(data, ids, db):
    """The two seeded random orders. The run takes the first N_PER_GROUP of each, the pilot the first PILOT_PER_GROUP."""
    g = groups(data, ids, db)
    return {"F": random.Random(SEED).sample(g["F"], len(g["F"])),
            "R": random.Random(SEED + 1).sample(g["R"], len(g["R"]))}


def sample(data, ids, db, per_group):
    """The first `per_group` of each order, interleaved (F1, R1, F2, R2, ...), so that a stop at the cap leaves a
    balanced random part of the sample."""
    o = orders(data, ids, db)
    return [(o[grp][i], grp) for i in range(per_group) for grp in ("F", "R")]


def did(d):
    return d.removesuffix(".json")


def agent_request(name, d, arm, turn, call, messages):
    req = models.request(AGENT, f"{name}-{did(d)}-{arm}-t{turn}c{call}", None, flag.multi_system(arm), None,
                         tools=tools.TOOLS[arm], messages=messages, cell=arm)
    req["params"]["cache_control"] = {"type": "ephemeral"}
    return req


def traveller_request(name, d, turn, brief, dialogue):
    user = SIM_USER.format(brief=brief, dialogue=dialogue)
    return models.request(TRAVELLER, f"{name}-{did(d)}-sim-t{turn}", user, SIM_SYSTEM, None, cell="sim")


def first_requests(name, arm, data, ids, db, per_group=N_PER_GROUP):
    """The first agent request of each sampled conversation (deterministic; r10/manifest.json holds their digest)."""
    return [agent_request(name, d, arm, 1, 1, [{"role": "user", "content": zforms.prefix_text(data[d])}])
            for d, _ in sample(data, ids, db, per_group)]


def display(rows, arm):
    """The result rows in the names of the arm (T1: property_kind, large_property)."""
    if arm != "t1":
        return rows
    out = []
    for r in rows["results"]:
        r = dict(r)
        kind = r.pop("type")
        r = {"name": r.pop("name"), "property_kind": "large_property" if kind == "hotel" else kind, **r}
        out.append(r)
    return {"results": out, "total": rows["total"]}


def cost(model, usage):
    p_in, p_out = __import__("anth").PRICES[model]
    return (usage.get("input_tokens", 0) * p_in + usage.get("cache_creation_input_tokens", 0) * p_in * CACHE_WRITE
            + usage.get("cache_read_input_tokens", 0) * p_in * CACHE_READ[model]
            + usage.get("output_tokens", 0) * p_out) / 1e6


def worst_cost(req):
    """The most that one call can cost: all input written to the cache at 1.5 times the estimate, and max_tokens out."""
    import anth
    p = req["params"]
    p_in, p_out = anth.PRICES[p["model"]]
    return (anth.est_in(req) * 1.5 * p_in * CACHE_WRITE + p["max_tokens"] * p_out) / 1e6


class CapReached(Exception):
    pass


class Budget:
    """A hard cap: a call goes only when the spent money, the reserved money and its worst cost stay within the cap."""

    def __init__(self, cap):
        self.cap, self.spent, self.reserved, self.lock = cap, 0.0, 0.0, threading.Lock()

    def reserve(self, x):
        with self.lock:
            if self.spent + self.reserved + x > self.cap:
                raise CapReached(f"{self.spent:.4f} spent, {self.reserved:.4f} reserved, {x:.4f} more > {self.cap:.2f}")
            self.reserved += x

    def settle(self, x, actual):
        with self.lock:
            self.reserved -= x
            self.spent += actual


def usage_dict(u):
    return {k: getattr(u, k, 0) or 0 for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                                                "cache_read_input_tokens")}


def call(client, req, budget):
    import anth
    x = worst_cost(req)
    budget.reserve(x)
    actual = 0.0
    try:
        msg = client.messages.create(**req["params"])
        u = usage_dict(msg.usage)
        actual = cost(msg.model, u)
    finally:
        budget.settle(x, actual)
    row = anth.message_row(req["custom_id"], msg)
    row["content"] = [anth.block_dict(b) for b in msg.content]
    row["usage"] = u
    row["cost"] = actual
    return row


def clean_traveller(text):
    text = (text or "").strip()
    text = re.sub(r"^\**traveller\**\s*:\s*", "", text, flags=re.I).strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1].strip()
    return text


def converse(client, name, d, grp, arm, data, db, budget):
    """One conversation. Returns its record; status "complete", or "cap" when the hard cap stopped it."""
    dialogue_d = data[d]
    brief = hotel_brief(dialogue_d)
    prefix = zforms.prefix_text(dialogue_d)
    messages = [{"role": "user", "content": prefix}]
    transcript = prefix
    rec = {"dialogue": d, "group": grp, "arm": arm, "brief": brief, "calls": [], "searches": [], "replies": [],
           "traveller": [], "status": "complete"}
    pending = None
    try:
        for turn in range(1, TRAVELLER_TURNS + 2):
            texts = []
            for k in range(1, MAX_CALLS + 1):
                row = call(client, agent_request(name, d, arm, turn, k, messages), budget)
                row["turn"], row["call"] = turn, k
                rec["calls"].append(row)
                if not row["content"]:
                    rec["status"] = f"empty answer (stop {row.get('stop')})"
                    return finish(rec)
                messages.append({"role": "assistant", "content": row["content"]})
                if row.get("text"):
                    texts.append(row["text"].strip())
                tc = row.get("tool_calls") or []
                if not tc:
                    break
                kind, fields = tools.parse_call(row, arm)
                s = {"turn": turn, "call": k, "kind": kind}
                if kind == "search":
                    found = bs.search(db, fields)
                    rows = bs.result_rows(found)
                    s.update(fields={f: (list(v) if isinstance(v, tuple) else v) for f, v in fields.items()},
                             shown=[v["name"] for v in found[:5]], total=len(found))
                    result = {"type": "tool_result", "tool_use_id": tc[0]["id"],
                              "content": json.dumps(display(rows, arm))}
                else:
                    result = {"type": "tool_result", "tool_use_id": tc[0]["id"], "is_error": True,
                              "content": "The arguments are not valid for search_hotels."}
                rec["searches"].append(s)
                if k < MAX_CALLS:
                    messages.append({"role": "user", "content": [result]})
                else:
                    pending = result
            reply = "\n\n".join(t for t in texts if t)
            rec["replies"].append(reply)
            transcript += "\nAssistant: " + reply
            if turn > TRAVELLER_TURNS:
                break
            row = call(client, traveller_request(name, d, turn, brief, transcript), budget)
            said = clean_traveller(row.get("text"))
            row["turn"] = turn
            rec["traveller"].append({"text": said, "row": row})
            transcript += "\nTraveller: " + said
            content = [pending] if pending else []
            pending = None
            content.append({"type": "text", "text": "Traveller: " + said})
            messages.append({"role": "user", "content": content})
    except CapReached as e:
        rec["status"], rec["cap"] = "cap", str(e)
    except Exception as e:  # an API error after the client's retries: the conversation ends, the run goes on
        rec["status"], rec["error"] = "error", f"{type(e).__name__}: {e}"[:500]
    return finish(rec)


def finish(rec):
    rec["cost"] = sum(r["cost"] for r in rec["calls"]) + sum(t["row"]["cost"] for t in rec["traveller"])
    return rec


def done_ids(path):
    if not path.exists():
        return set()
    return {json.loads(x)["dialogue"] for x in path.read_text().splitlines() if json.loads(x)["status"] == "complete"}


def drive(name, arm, convs, path, budget, client, workers=WORKERS):
    """Run the conversations not yet complete in `path` with WORKERS threads, under the hard cap of `budget`. A
    conversation that the cap or an API error ends is written with its status; after the first cap stop or MAX_ERRORS
    errors, no new conversation starts."""
    import gold as gd
    from runs import context
    data, _ = context()
    db = gd.hotel_db()
    todo = [(d, grp) for d, grp in convs if d not in done_ids(path)]
    lock = threading.Lock()
    ended = {"cap": 0, "error": 0}

    def one(item):
        if ended["cap"] or ended["error"] >= MAX_ERRORS:
            return
        rec = converse(client, name, item[0], item[1], arm, data, db, budget)
        with lock:
            with open(path, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            if rec["status"] in ended:
                ended[rec["status"]] += 1
            print(f"{len(rec['calls']):2d} agent calls  {rec['cost']:.4f} USD  {item[1]} {item[0]}  {rec['status']}  "
                  f"spent {budget.spent:.4f}", flush=True)

    with cf.ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, todo))
    if ended["cap"] or ended["error"]:
        print(f"Stopped early: {ended['cap']} conversation(s) at the cap, {ended['error']} with an API error.")


def amendment_text(head=AMENDMENT):
    import runs
    text = runs.PROTOCOL.read_text().split(runs.AMEND, 1)[-1]
    if head not in text:
        return None
    body = text.split(head, 1)[1]
    ends = [i for i in (body.find("\n## "), body.find("\n### ")) if i >= 0]
    return head + (body[:min(ends)] if ends else body)


def check_amendment(pilot_v1=False):
    """R10-8 holds the agent texts and the first traveller text; R10-9 (not needed for the first pilot) holds the
    traveller text in use and the brief rule."""
    need = {AMENDMENT: (flag.MULTI_ASK, flag.MULTI_END, SIM_SYSTEM_R10_8, NEW_TEXTS[1])}
    if not pilot_v1:
        need[AMENDMENT_9] = (SIM_SYSTEM, "Once you find", "If the booking fails", "Make sure you get")
    for head, texts in need.items():
        text = amendment_text(head)
        if text is None:
            sys.exit(f"Not run. PROTOCOL.md has no amendment {head.strip()!r}.")
        flat = " ".join(text.split())
        for t in texts:
            if " ".join(t.split()) not in flat:
                sys.exit(f"Not run. {head.strip()} does not hold the text {t[:60]!r}... verbatim.")


def pilot_cost(name):
    path = EXPLORE / name / "pilot_conversations.jsonl"
    recs = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    recs = [r for r in recs if r["status"] == "complete"]
    return (sum(r["cost"] for r in recs) / len(recs), max(r["cost"] for r in recs), len(recs)) if recs else None


def run_bound(name, n):
    pc = pilot_cost(name)
    if pc is None:
        return None
    return math.ceil(pc[0] * n * MARGIN * 100) / 100


def main(name, arm):
    import accounts
    import budget_gate
    import runs
    ap = argparse.ArgumentParser(description=f"{name}: amendment R10-8 on {ACCOUNT}")
    ap.add_argument("step", choices=["estimate", "pilot", "run", "continue"])
    ap.add_argument("--approve")
    args = ap.parse_args()
    data, g = runs.context()
    db = gold.hotel_db()
    ids = list(g["booked"])
    a = accounts.account(ACCOUNT, ("anthropic",))
    folder = accounts.folder(name)
    if args.step == "estimate":
        pc = pilot_cost(name)
        print(f"{name}: {2 * N_PER_GROUP} conversations; pilot {pc}; run bound {run_bound(name, 2 * N_PER_GROUP)}")
        return
    runs.check_lock()
    import protocol_h
    protocol_h.check()
    check_amendment()
    workers = WORKERS
    if args.step == "continue":  # amendment R10-11: the conversations of the run that are not complete
        if amendment_text(AMENDMENT_11) is None:
            sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT_11.strip()!r}.")
        man = json.loads(runs.MANIFEST.read_text())
        if man.get(name, {}).get("sha256") != runs.digest(runs.requests(name)):
            sys.exit(f"Not run. {name}: the first requests differ from {runs.MANIFEST.name} or have no entry.")
        path = folder / "conversations.jsonl"
        recs = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
        done = [r for r in recs if r["status"] == "complete"]
        convs = [c for c in sample(data, ids, db, N_PER_GROUP) if c[0] not in done_ids(path)]
        if not done or not convs:
            sys.exit(f"Not run. {name}: no run to continue, or every conversation is complete.")
        bound = math.ceil(sum(r["cost"] for r in done) / len(done) * len(convs) * MARGIN * 100) / 100
        workers = CONTINUE_WORKERS
        print(f"{name} continue: {len(convs)} conversations left, bound {bound:.2f} USD (run mean x {MARGIN}; a hard "
              f"cap; {workers} worker)")
    elif args.step == "pilot":
        convs, path, bound = sample(data, ids, db, PILOT_PER_GROUP), folder / "pilot_conversations.jsonl", PILOT_CAP
        print(f"{name} pilot: {len(convs)} conversations, hard cap {bound:.2f} USD (enforced before each call)")
    else:
        man = json.loads(runs.MANIFEST.read_text())
        if man.get(name, {}).get("sha256") != runs.digest(runs.requests(name)):
            sys.exit(f"Not run. {name}: the first requests differ from {runs.MANIFEST.name} or have no entry.")
        convs, path = sample(data, ids, db, N_PER_GROUP), folder / "conversations.jsonl"
        left = [c for c in convs if c[0] not in done_ids(path)]  # a continuation prices only the conversations left
        if not left:
            sys.exit(f"Not run. {name}: every conversation is complete.")
        bound = run_bound(name, len(left))
        if bound is None:
            sys.exit(f"Not run. {name} has no pilot.")
        print(f"{name} run: {len(left)} of {len(convs)} conversations left, bound {bound:.2f} USD (pilot mean x "
              f"{MARGIN}; a hard cap)")
    if bound > MAX_BOUND:
        sys.exit(f"Not run. {name}: {bound:.2f} USD is above the R10-8 maximum of {MAX_BOUND:.2f} USD per run.")
    if args.approve is not None and not budget_gate.fits(ACCOUNT, bound):
        sys.exit(f"Not run. {name}: {bound:.2f} USD does not fit the free money of {ACCOUNT} minus the reserve.")
    accounts.check_approval(a, args.approve, bound)
    import anth
    held = accounts.hold(a, name, args.step, bound)
    budget = Budget(bound)
    try:
        drive(name, arm, convs, path, budget, anth.client(a), workers)
    finally:
        accounts.ledger(a, name, args.step, bound, budget.spent)
        held.unlink()
    print(f"{name} {args.step}: spent {budget.spent:.4f} USD at list prices (bound {bound:.2f})")


if __name__ == "__main__":
    import runs
    data, g = runs.context()
    db = gold.hotel_db()
    gr = groups(data, list(g["booked"]), db)
    print({k: len(v) for k, v in gr.items()})
    for d, grp in sample(data, list(g["booked"]), db, 2):
        print(grp, d, "|", hotel_brief(data[d]))
