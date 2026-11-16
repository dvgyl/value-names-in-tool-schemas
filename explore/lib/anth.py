"""Shared helpers for the exploratory Anthropic batches (PROTOCOL.md).

Every experiment script builds its requests with `request()` and hands them to `main()` with an Anthropic account from
`accounts.ACCOUNTS`. `main()` offers four steps: `estimate` (offline), `pilot --approve <bound>` (a few synchronous
calls that measure token sizes), `submit --approve <bound>` (one Message Batch), and `fetch` (results, usage, cost,
ledger row). A paid step runs only when the --approve value equals the bound that the same step prints, so no call runs
on an unseen number. `accounts.py` holds the limit and the ledger of each account.
"""
import argparse
import datetime
import json
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import accounts  # noqa: E402
import seal  # noqa: E402

EXPLORE = accounts.EXPLORE
HARNESS = EXPLORE.parents[2]
# The public corpus (README.md, section 3): <repository>/corpus/MULTIWOZ2.4.
DATA = pathlib.Path(__file__).resolve().parents[2] / "corpus" / "MULTIWOZ2.4"

# USD per million tokens at list price (claude-api skill table, cached 2026-10-06). The batch API halves them.
PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.00, 10.00), "claude-opus-5-5": (4.00, 20.00)}
BATCH = 0.5
MARGIN = 1.25
CHARS_PER_TOKEN = 4
TOKENIZER = 1.3  # the Claude tokenizer factor of budget_v10.py, used only until a pilot measures real counts
PILOT_PER_CELL = 10


def domains(goal):
    return [d for d in ("hotel", "restaurant", "attraction", "train", "taxi", "police", "hospital") if goal.get(d)]


def splits():
    val = set((DATA / "valListFile.json").read_text().split())
    test = set((DATA / "testListFile.json").read_text().split())
    return val, test


def multiwoz():
    return json.loads((DATA / "data.json").read_text())


def trackp_pool(data=None):
    """The 687 multi-domain hotel dialogues of the validation and test sets, which no exploratory call may touch."""
    data = data or multiwoz()
    val, test = splits()
    pool = {k for k in val | test if k in data and "hotel" in domains(data[k]["goal"]) and len(domains(data[k]["goal"])) > 1}
    assert len(pool) == 687, len(pool)
    return pool


def assert_outside_trackp(dialogue_ids, data=None):
    hit = set(dialogue_ids) & trackp_pool(data)
    assert not hit, f"{len(hit)} Track P dialogues in an exploratory request set, for example {sorted(hit)[:3]}"


def request(custom_id, model, effort, max_tokens, user, system=None, thinking=None, fmt=None, *, tools=None,
            tool_choice=None, messages=None, cell=None):
    """One Messages API request. Without the keyword arguments, the request is byte-identical to the request of the
    code before round 10, so the registered main-study request hashes do not change.

    Round 10 (2026-11-12, claude-api skill cached 2026-11-03): `tools` is a list of {"name", "description",
    "input_schema", "strict": True}. With tools and no `tool_choice`, the request gets
    {"type": "auto", "disable_parallel_tool_use": True}, because Claude Opus 5.5 and Claude Sonnet 5.5 answer a forced
    tool_choice ("any" or "tool") with HTTP 400, also in a batch. `messages` replaces the one user message (then `user`
    is None). `cell` is an arm tag. It is stored as a top-level key of the request, outside `params`, and wire() removes it.
    """
    assert model in PRICES, model
    assert (user is None) == (messages is not None), "give user or messages, not both"
    params = {"model": model, "max_tokens": max_tokens, "output_config": {"effort": effort},
              "messages": messages if messages is not None else [{"role": "user", "content": user}]}
    if system:
        params["system"] = system
    if thinking:
        params["thinking"] = thinking
    if fmt:
        params["output_config"]["format"] = fmt
    if tools:
        params["tools"] = [dict(t) for t in tools]
        params["tool_choice"] = tool_choice or {"type": "auto", "disable_parallel_tool_use": True}
    req = {"custom_id": custom_id, "params": params}
    if cell is not None:
        req["cell"] = cell
    return req


def wire(req):
    """The request that the API gets: the custom_id and the params, without the cell tag."""
    return {"custom_id": req["custom_id"], "params": req["params"]}


def cell(req):
    base = (req["params"]["model"], req["params"]["output_config"]["effort"])
    return base + (req["cell"],) if "cell" in req else base


def content_chars(content):
    return len(content) if isinstance(content, str) else len(json.dumps(content))


def est_in(req):
    p = req["params"]
    chars = len(p.get("system") or "") + sum(content_chars(m["content"]) for m in p["messages"])
    chars += len(json.dumps(p["tools"])) if "tools" in p else 0
    return math.ceil(chars / CHARS_PER_TOKEN) * TOKENIZER


def block_dict(b):
    """One content block as a dict, unchanged, so that a later request can send it again (thinking blocks too)."""
    if hasattr(b, "to_dict"):
        return b.to_dict(mode="json")
    return {k: v for k, v in vars(b).items() if not k.startswith("_")}


def message_row(custom_id, m):
    """One raw.jsonl row of a successful message. A message with a block that is not text also gets `tool_calls`
    ({"id", "name", "input"} per tool_use block) and `content` (every block, in order)."""
    blocks = getattr(m, "content", None) or []
    row = {"custom_id": custom_id, "type": "succeeded", "model": m.model, "stop": m.stop_reason,
           "input_tokens": m.usage.input_tokens, "output_tokens": m.usage.output_tokens,
           "text": "".join(b.text for b in blocks if b.type == "text")}
    if any(b.type != "text" for b in blocks):
        row["tool_calls"] = [{"id": b.id, "name": b.name, "input": b.input} for b in blocks if b.type == "tool_use"]
        row["content"] = [block_dict(b) for b in blocks]
    return row


def cost(model, tokens_in, tokens_out, batch=True):
    p_in, p_out = PRICES[model]
    return (tokens_in * p_in + tokens_out * p_out) / 1e6 * (BATCH if batch else 1.0)


def pilot_path(name):
    return EXPLORE / name / "pilot.json"


def estimate(name, reqs, planning_out):
    """Expected cost: input from the pilot ratio of real to estimated tokens, output from the pilot mean per cell."""
    pilot = json.loads(pilot_path(name).read_text()) if pilot_path(name).exists() else {}
    total, rows = 0.0, {}
    for r in reqs:
        key = "|".join(cell(r))
        m = pilot.get(key)
        tin = est_in(r) * (m["in_ratio"] if m else 1.0)
        tout = m["out_mean"] if m else planning_out
        rows.setdefault(key, [0, 0.0, "pilot" if m else "planning"])
        c = cost(cell(r)[0], tin, tout)
        rows[key][0] += 1
        rows[key][1] += c
        total += c
    return total, rows


def print_estimate(name, reqs, planning_out):
    total, rows = estimate(name, reqs, planning_out)
    print(f"{name}: {len(reqs)} requests")
    for key, (n, c, src) in sorted(rows.items()):
        print(f"  {key}: {n} requests, expected {c:.2f} USD ({src} output size)")
    bound = round(total * MARGIN, 2)
    print(f"  expected {total:.2f} USD, bound {bound:.2f} USD (batch prices, 25% margin)")
    return bound


def client(account):
    import anthropic
    return anthropic.Anthropic(api_key=accounts.api_key(account), max_retries=4)


def pilot_sample(reqs, cell):
    """PILOT_PER_CELL requests of each (model, effort) cell, drawn with a fixed seed."""
    rng = random.Random(20261024)
    by_cell = {}
    for r in reqs:
        by_cell.setdefault(cell(r), []).append(r)
    return [x for c in sorted(by_cell) for x in rng.sample(by_cell[c], min(PILOT_PER_CELL, len(by_cell[c])))]


def pilot(name, reqs, approve, account):
    """A few synchronous calls per (model, effort) cell. Its bound uses max_tokens, so it is a hard upper limit."""
    sample = pilot_sample(reqs, cell)
    bound = round(sum(cost(cell(r)[0], est_in(r) * 1.5, r["params"]["max_tokens"], batch=False) for r in sample), 2)
    print(f"{name} pilot: {len(sample)} synchronous calls, hard bound {bound:.2f} USD at max_tokens and list prices")
    accounts.check_approval(account, approve, bound)
    cl, out, spent, raw = client(account), {}, 0.0, []
    held = accounts.hold(account, name, "pilot", bound)
    try:
        for r in sample:
            msg = cl.messages.create(**r["params"])
            u = msg.usage
            spent += cost(msg.model, u.input_tokens, u.output_tokens, batch=False)
            out.setdefault("|".join(cell(r)), []).append(
                {"in": u.input_tokens, "out": u.output_tokens, "est_in": est_in(r), "stop": msg.stop_reason})
            raw.append(message_row(r["custom_id"], msg))
    finally:
        accounts.ledger(account, name, "pilot", bound, spent)
        held.unlink()
        if raw and not seal.sealed(name):  # round 10: the step-2 replay test builds requests from these rows
            accounts.folder(name)
            with open(EXPLORE / name / "pilot_raw.jsonl", "w") as fh:
                fh.writelines(json.dumps(x) + "\n" for x in raw)
    summary = {k: {"in_ratio": sum(x["in"] for x in v) / sum(x["est_in"] for x in v),
                   "out_mean": sum(x["out"] for x in v) / len(v), "out_max": max(x["out"] for x in v),
                   "stops": sorted({x["stop"] for x in v}), "n": len(v)} for k, v in out.items()}
    pilot_path(name).parent.mkdir(parents=True, exist_ok=True)
    pilot_path(name).write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def submit(name, reqs, planning_out, approve, account):
    folder = EXPLORE / name
    if (folder / "batch.json").exists():
        sys.exit(f"{name} already has a batch: {(folder / 'batch.json').read_text()}")
    bound = print_estimate(name, reqs, planning_out)
    accounts.check_approval(account, approve, bound)
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / "requests.jsonl", "w") as fh:
        for r in reqs:
            fh.write(json.dumps(r) + "\n")
    import anthropic
    cl = client(account)
    held = accounts.hold(account, name, "submit", bound)
    try:
        batch = cl.messages.batches.create(requests=[wire(r) for r in reqs])
    except anthropic.APIStatusError:  # the API answered with an error, so no batch exists
        held.unlink()
        raise
    (folder / "batch.json").write_text(json.dumps({"id": batch.id, "bound": bound, "requests": len(reqs),
                                                   "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                                   "account": account.name, "script": script()}))
    held.unlink()
    print(f"{name}: batch {batch.id} submitted, {len(reqs)} requests, status {batch.processing_status}")


def script():
    """The experiment script, relative to explore/, so that watch.py can run its fetch step."""
    path = pathlib.Path(sys.argv[0]).resolve()
    return str(path.relative_to(EXPLORE) if path.is_relative_to(EXPLORE) else path)


def batch_info(folder, account):
    """batch.json of the experiment. The batch belongs to the account that submitted it, so fetch uses the same key."""
    info = json.loads((folder / "batch.json").read_text())
    if info.get("account", accounts.OLD) != account.name:
        sys.exit(f"Not run. {folder.name} was submitted on {info.get('account', accounts.OLD)}, not on {account.name}.")
    return info


def fetch(name, account):
    folder = EXPLORE / name
    info = batch_info(folder, account)
    cl = client(account)
    batch = cl.messages.batches.retrieve(info["id"])
    if batch.processing_status != "ended":
        sys.exit(f"{name}: {batch.processing_status}, counts {batch.request_counts}")
    spent, counts, rows = 0.0, {}, []
    for res in cl.messages.batches.results(info["id"]):
        row = {"custom_id": res.custom_id, "type": res.result.type}
        if res.result.type == "succeeded":
            m = res.result.message
            row = message_row(res.custom_id, m)
            spent += cost(m.model, m.usage.input_tokens, m.usage.output_tokens)
        counts[row["type"]] = counts.get(row["type"], 0) + 1
        rows.append(row)
    write_raw(folder, rows, seal.Sealer(folder) if seal.sealed(name) else None)
    accounts.ledger(account, name, "batch", info["bound"], spent)
    print(f"{name}: results {counts}, cost at batch list prices {spent:.2f} USD (bound {info['bound']:.2f})")


def write_raw(folder, rows, sealer):
    """raw.jsonl. A sealed run writes the public fields there and every full row into raw.sealed (seal.py)."""
    if sealer:
        seal.write_blob(folder / "raw.sealed", "".join(json.dumps(r) + "\n" for r in rows).encode(), sealer)
    with open(folder / "raw.jsonl.part", "w") as fh:
        for r in rows:
            fh.write(json.dumps(seal.public(r) if sealer else r) + "\n")
    (folder / "raw.jsonl.part").replace(folder / "raw.jsonl")


def main(name, build, planning_out, *, account):
    """`account` names an Anthropic account of accounts.ACCOUNTS. It has no default."""
    account = accounts.account(account, ("anthropic",))
    accounts.folder(name)
    ap = argparse.ArgumentParser(description=f"{name}: exploratory batch on {account.name} (PROTOCOL.md)")
    ap.add_argument("step", choices=["estimate", "pilot", "submit", "fetch"])
    ap.add_argument("--approve", help="the bound that the operator approved in writing")
    args = ap.parse_args()
    if args.step == "fetch":
        return fetch(name, account)
    reqs = build()
    ids = [r["custom_id"] for r in reqs]
    assert len(ids) == len(set(ids)), "duplicate custom_id"
    assert all(len(i) <= 64 and all(c.isalnum() or c in "_-" for c in i) for i in ids), "custom_id format"
    if args.step == "estimate":
        print_estimate(name, reqs, planning_out)
    elif args.step == "pilot":
        pilot(name, reqs, args.approve, account)
    else:
        submit(name, reqs, planning_out, args.approve, account)
