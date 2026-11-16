"""Clients for the OpenAI Responses and Batch APIs, the DeepInfra chat completions API, and the Gemini generateContent
and Batch APIs (PROTOCOL.md).

The clients use only the Python standard library. An experiment script builds its requests with `openai_request()`,
`deepinfra_request()`, or `gemini_request()` and hands them to `main()` with an account from `accounts.ACCOUNTS`. The
account selects the provider. The steps are `estimate` (offline) and `pilot --approve <bound>` (a few synchronous calls
per cell), then `submit --approve <bound>` and `fetch` on OpenAI and Google, or `run --approve <bound>` (every request,
synchronous) on DeepInfra.
A paid step runs only when the --approve value equals the bound that the same step prints (accounts.py).

Each response is written to disk before it is parsed, and a rerun skips each request that has a stored response.
`raw.jsonl` and `pilot.json` have the format of anth.py, so the analysis scripts read the rows of every provider.
The request and response shapes come from the provider docs (read 2026-11-03). UNVERIFIED marks a shape that the docs
do not show.
"""
import argparse
import concurrent.futures
import datetime
import http.client
import json
import math
import os
import pathlib
import random
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from typing import Callable, NamedTuple

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import accounts  # noqa: E402
import anth  # noqa: E402
import seal  # noqa: E402

OPENAI = "https://api.openai.com/v1"
DEEPINFRA = "https://api.deepinfra.com/v1/openai"
# Gemini, read 2026-11-04. Each ai.google.dev page below answered with HTTP 301 to the aistudio.google.com page beside it.
# - https://ai.google.dev/gemini-api/docs/batch-api (-> https://aistudio.google.com/docs/batch-api): the batch costs
#   50% of the standard price, targets 24 hours, and expires after 48 hours. Input is a JSONL file of
#   {"key", "request"} lines (at most 2 GB), sent by the resumable upload with the x-goog-api-key header. Each output
#   line has "the same key" and a "response" or an "error". Structured output is supported in a batch.
# - https://ai.google.dev/api/batch-mode (-> https://aistudio.google.com/api-reference/batch-api): BATCH_STATE_PENDING,
#   _RUNNING, _SUCCEEDED, _FAILED, _CANCELLED, _EXPIRED; the guide writes JOB_STATE_ for the same states.
# - https://ai.google.dev/api/generate-content (-> https://aistudio.google.com/api-reference/generate-content):
#   generationConfig.responseMimeType, responseJsonSchema, maxOutputTokens, thinkingConfig.thinkingLevel (MINIMAL,
#   LOW, MEDIUM, HIGH); temperature and topP are ignored on Gemini 3.6 Flash and newer. totalTokenCount is the sum
#   of the prompt, tool-use prompt, thought, and candidate tokens, so candidatesTokenCount has no thought tokens.
# - https://ai.google.dev/gemini-api/docs/structured-output (-> https://aistudio.google.com/docs/structured-output):
#   the schema keywords anyOf, enum, the type null, required, and additionalProperties are supported.
# - https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash (-> aistudio.google.com/docs/models/gemini-3.8-flash):
#   Batch API and structured outputs supported; thinking levels low, medium, high; minimal returns an error.
# - https://ai.google.dev/gemini-api/docs/pricing (-> https://aistudio.google.com/docs/pricing): the output price
#   includes the thinking tokens.
GEMINI = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_UPLOAD = "https://generativelanguage.googleapis.com/upload/v1beta/files"
GEMINI_DOWNLOAD = "https://generativelanguage.googleapis.com/download/v1beta"
GEMINI_THINKING = "LOW"  # research/out/SYN-S5-models-infra.md section 3.2; the model default is medium
GEMINI_DONE = {"SUCCEEDED", "FAILED", "CANCELLED", "EXPIRED"}
GEMINI_REFUSAL = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII"}
WORKERS = 4
TIMEOUT = 300  # seconds for one HTTP request, because a reasoning model can think for minutes
ATTEMPTS = 4
FATAL = {401, 402, 403, 404}  # a bad key, no money, or a wrong model or path: all other requests fail the same way
TERMINAL = {"completed", "failed", "expired", "cancelled"}
sleep = time.sleep


def decode_response(body):
    """The row fields of a Responses API body. output_tokens includes the reasoning tokens, which bill as output."""
    parts = [c for item in body["output"] if item["type"] == "message" for c in item["content"]]
    reason = (body.get("incomplete_details") or {}).get("reason")
    if any(c["type"] == "refusal" for c in parts):
        stop = "refusal"
    elif body["status"] == "completed":
        stop = "end_turn"
    else:
        stop = "max_tokens" if reason == "max_output_tokens" else f"{body['status']}:{reason}"
    u = body["usage"]
    row = {"model": body["model"], "stop": stop, "provider_stop": reason or body["status"],
           "input_tokens": u["input_tokens"], "output_tokens": u["output_tokens"],
           "reasoning_tokens": (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0),
           "text": "".join(c["text"] for c in parts if c["type"] == "output_text")}
    calls = [item for item in body["output"] if item["type"] == "function_call"]
    if calls:  # round 10: a step-2 request sends `output_items` again, reasoning items included
        row["tool_calls"] = [{"id": c["call_id"], "name": c["name"], "input": parse_arguments(c["arguments"])}
                             for c in calls]
        row["output_items"] = body["output"]
    return row


def parse_arguments(text):
    """The JSON-encoded arguments of a function call; None when they do not parse (the analysis counts it invalid)."""
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return None


def decode_chat(body):
    """The row fields of a chat completions body. The DeepInfra docs show only prompt_tokens and completion_tokens.
    UNVERIFIED: completion_tokens_details.reasoning_tokens, usage.estimated_cost, and whether completion_tokens
    includes the thinking tokens."""
    choice = body["choices"][0]
    msg, finish = choice["message"], choice.get("finish_reason")
    stop = "refusal" if msg.get("refusal") else {"stop": "end_turn", "length": "max_tokens"}.get(finish, f"finish:{finish}")
    u = body["usage"]
    row = {"model": body.get("model"), "stop": stop, "provider_stop": finish,
           "input_tokens": u["prompt_tokens"], "output_tokens": u["completion_tokens"],
           "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0),
           "provider_cost": u.get("estimated_cost"), "text": msg.get("content") or ""}
    if msg.get("tool_calls"):  # round 10, experiment D only
        row["tool_calls"] = [{"id": c.get("id"), "name": c["function"]["name"],
                              "input": parse_arguments(c["function"].get("arguments"))} for c in msg["tool_calls"]]
    return row


def decode_gemini(body):
    """The row fields of a GenerateContentResponse. output_tokens adds thoughtsTokenCount to candidatesTokenCount,
    because the output price includes the thinking tokens. A thought part is not answer text. A blocked prompt has no
    candidate and a promptFeedback.blockReason."""
    cand = (body.get("candidates") or [{}])[0]
    finish, block = cand.get("finishReason"), (body.get("promptFeedback") or {}).get("blockReason")
    if finish in GEMINI_REFUSAL or (block and not finish):
        stop = "refusal"
    else:
        stop = {"STOP": "end_turn", "MAX_TOKENS": "max_tokens"}.get(finish, f"finish:{finish}")
    u = body["usageMetadata"]
    thoughts = u.get("thoughtsTokenCount", 0)
    return {"model": body.get("modelVersion"), "stop": stop, "provider_stop": finish or block,
            "input_tokens": u["promptTokenCount"], "output_tokens": u.get("candidatesTokenCount", 0) + thoughts,
            "reasoning_tokens": thoughts,
            "text": "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts") or [] if not p.get("thought"))}


def bearer(url):
    """One synchronous call with the key as a bearer token. The body goes as JSON, unchanged."""
    return lambda key, body: send("POST", url, key, json.dumps(body).encode())


def gemini_post(key, body):
    status, _, data = google_send("POST", f"{GEMINI}/models/{body['model']}:generateContent", key,
                                  json.dumps(wire(body)).encode())
    return status, data


class Api(NamedTuple):
    post: Callable[[str, dict], tuple]  # one synchronous call: (key, request body) -> (HTTP status, response bytes)
    cap: Callable[[dict], int]  # the output token cap of a request body, reasoning included; None when it is missing
    decode: Callable[[dict], dict]  # a response body to the fields of a raw.jsonl row
    batch: bool  # True: the steps submit and fetch at batch prices; False: the step run at standard prices
    prices: dict  # USD per million tokens at list price
    until: datetime.date = None  # the last day of the prices; a paid step stops 2 days before it


APIS = {
    # budget_v11.py PRICES, from the OpenAI pricing page (research/out/SYN-S5-models-infra.md section 1.1)
    "openai": Api(bearer(f"{OPENAI}/responses"), lambda b: b.get("max_output_tokens"), decode_response, True,
                  {"gpt-6.1-sol": (2.00, 10.00), "gpt-6-luna": (0.10, 0.50), "gpt-6-astra": (10.00, 50.00)}),
    # list prices of the DeepInfra model pages (read 2026-11-03); the current promotions bill less
    "deepinfra": Api(bearer(f"{DEEPINFRA}/chat/completions"), lambda b: b.get("max_tokens"), decode_chat, False,
                     {"deepseek-ai/DeepSeek-V4.1-Flash": (0.20, 0.60), "Qwen/Qwen3.8-27B": (0.20, 2.50),
                      "google/gemma-4-31B-it": (0.20, 0.40)}),
    # budget_v11.py PANEL and the Gemini pricing page: 0.75 and 3.75 until 2026-12-31, then 1.50 and 7.50
    "google": Api(gemini_post, lambda b: (b.get("generationConfig") or {}).get("maxOutputTokens"), decode_gemini, True,
                  {"gemini-3.8-flash": (0.75, 3.75)}, datetime.date(2026, 12, 31)),
}


def messages(user, system):
    return ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]


def openai_request(custom_id, model, effort, max_tokens, user, system=None, schema=None, *, tools=None,
                   input_items=None, cell=None):
    """One Responses API request. `max_tokens` also limits the reasoning tokens. `schema` is a JSON schema for strict
    structured output: each object needs `additionalProperties: false` and all its properties in `required`.

    Round 10 (OpenAI function-calling, reasoning and batch guides at developers.openai.com, read 2026-11-12; the
    Responses API reference answered HTTP 403): `tools` is the neutral list of anth.request ({"name", "description",
    "input_schema", "strict"}). It becomes function tools {"type": "function", "name", "description", "parameters",
    "strict": true}, with tool_choice "auto" and parallel_tool_calls false ("exactly zero or one tool is called").
    `input_items` replaces messages(user, system); a step-2 request holds the stage-1 input, the stored output items
    (the guide: reasoning items "must also be passed back with tool call outputs"), and one function_call_output item.
    UNVERIFIED: the store default of a batch request; the step-2 replay test of the pilot checks the replay.
    Without the keyword arguments, the request is byte-identical to the request of the code before round 10."""
    assert model in APIS["openai"].prices, model
    assert (user is None) == (input_items is not None), "give user or input_items, not both"
    body = {"model": model, "input": input_items if input_items is not None else messages(user, system),
            "max_output_tokens": max_tokens, "reasoning": {"effort": effort}}
    if schema:
        body["text"] = {"format": {"type": "json_schema", "name": "answer", "schema": schema, "strict": True}}
    if tools:
        body["tools"] = [{"type": "function", "name": t["name"], "description": t["description"],
                          "parameters": t["input_schema"], "strict": True} for t in tools]
        body["tool_choice"] = "auto"
        body["parallel_tool_calls"] = False
    req = {"custom_id": custom_id, "body": body}
    if cell is not None:
        req["cell"] = cell
    return req


def deepinfra_request(custom_id, model, max_tokens, user, system=None, schema=None, *, tools=None, cell=None,
                      **options):
    """One chat completions request. `options` go into the body unchanged, for example `reasoning_effort` or
    `temperature`. UNVERIFIED: the option that turns off Qwen thinking, and `seed`. The docs do not name them.
    Round 10 (experiment D only): `tools` become chat-completions function tools, tool_choice "auto"; UNVERIFIED on
    DeepInfra until the pilot of D."""
    assert model in APIS["deepinfra"].prices, model
    body = {"model": model, "messages": messages(user, system), "max_tokens": max_tokens, **options}
    if schema:
        body["response_format"] = {"type": "json_schema",
                                   "json_schema": {"name": "answer", "strict": True, "schema": schema}}
    if tools:
        body["tools"] = [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                                           "parameters": t["input_schema"], "strict": True}}
                         for t in tools]
        body["tool_choice"] = "auto"
        body["parallel_tool_calls"] = False
    req = {"custom_id": custom_id, "body": body}
    if cell is not None:
        req["cell"] = cell
    return req


def gemini_request(custom_id, model, max_tokens, user, system=None, schema=None):
    """One generateContent request. `max_tokens` also limits the thinking tokens. `schema` is a JSON schema for
    responseJsonSchema. The body keeps `model` for the shared steps; wire() removes it, because the URL names the model.
    No temperature: Gemini 3.6 Flash and newer ignore it."""
    assert model in APIS["google"].prices, model
    config = {"maxOutputTokens": max_tokens, "thinkingConfig": {"thinkingLevel": GEMINI_THINKING}}
    if schema:
        config.update(responseMimeType="application/json", responseJsonSchema=schema)
    body = {"model": model, "contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": config}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    return {"custom_id": custom_id, "body": body}


def wire(body):
    """The GenerateContentRequest that Google gets: the body without `model`."""
    return {k: v for k, v in body.items() if k != "model"}


def cell(req):
    b = req["body"]
    thinking = ((b.get("generationConfig") or {}).get("thinkingConfig") or {}).get("thinkingLevel")
    base = (b["model"], (b.get("reasoning") or {}).get("effort") or thinking or str(b.get("reasoning_effort", "default")))
    return base + (req["cell"],) if "cell" in req else base


def prompt_texts(b):
    if "contents" in b:  # Gemini
        return [p["text"] for c in [b.get("systemInstruction") or {"parts": []}, *b["contents"]] for p in c["parts"]]
    items = b.get("input") or b["messages"]
    # A string content counts as its text; a list content or an item without content (a stored output item, a tool
    # result) counts as its JSON text. The tools count as their JSON text.
    texts = [m["content"] if isinstance(m.get("content"), str) else json.dumps(m) for m in items]
    return texts + ([json.dumps(b["tools"])] if "tools" in b else [])


def est_in(req):
    """Estimated input tokens, with the Claude tokenizer factor of anth.py as a margin until a pilot measures them."""
    chars = sum(map(len, prompt_texts(req["body"])))
    return math.ceil(chars / anth.CHARS_PER_TOKEN) * anth.TOKENIZER


def cost(api, model, tokens_in, tokens_out, batch):
    """List price. Cached input tokens get the normal input price, so the cost is an upper value."""
    p_in, p_out = api.prices[model]
    return (tokens_in * p_in + tokens_out * p_out) / 1e6 * (anth.BATCH if batch else 1.0)


def worst(api, req):
    """The most that one synchronous call can cost: 1.5 times the estimated input and the full output cap."""
    return cost(api, req["body"]["model"], est_in(req) * 1.5, api.cap(req["body"]), batch=False)


def cents_up(usd):
    return math.ceil(round(usd * 100, 6)) / 100


def estimate(name, reqs, planning_out, api):
    """Expected cost: input from the pilot ratio of real to estimated tokens, output from the pilot mean per cell."""
    path = anth.pilot_path(name)
    pilot = json.loads(path.read_text()) if path.exists() else {}
    total, rows = 0.0, {}
    for r in reqs:
        key = "|".join(cell(r))
        m = pilot.get(key)
        tin = est_in(r) * (m["in_ratio"] if m else 1.0)
        tout = m["out_mean"] if m else planning_out
        c = cost(api, cell(r)[0], tin, tout, api.batch)
        rows.setdefault(key, [0, 0.0, "pilot" if m else "planning"])
        rows[key][0] += 1
        rows[key][1] += c
        total += c
    return total, rows


def print_estimate(name, reqs, planning_out, a, api, in_flight=0.0):
    """Print the expected cost and return the bound. `in_flight` is the worst case of the calls that a synchronous run
    has open at one time, so that the run can reserve it and still stay within the bound."""
    total, rows = estimate(name, reqs, planning_out, api)
    print(f"{name} on {a.name}: {len(reqs)} requests")
    for key, (n, c, src) in sorted(rows.items()):
        print(f"  {key}: {n} requests, expected {c:.2f} USD ({src} output size)")
    bound = cents_up((total * anth.MARGIN + in_flight) * accounts.factor(a))
    parts = ["batch prices" if api.batch else "standard prices", "25% margin"]
    parts += ["18% TAX margin"] if a.cash else []
    parts += [f"{in_flight:.4f} USD for the calls in flight"] if in_flight else []
    print(f"  expected {total:.2f} USD, bound {bound:.2f} USD ({', '.join(parts)})")
    return bound


class NoAnswer(Exception):
    """A timeout or a network error. The provider can have run the request, so its worst-case cost stays counted."""


def http_request(method, url, headers, data):
    """One HTTP request; the return value is (status, response headers with lower-case names, body bytes)."""
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in (e.headers or {}).items()}, e.read()
    except (urllib.error.URLError, http.client.HTTPException, OSError) as e:
        raise NoAnswer(f"{type(e).__name__}: {e}") from None


def send(method, url, key, data=None, content_type="application/json"):
    """One HTTP request with a bearer key; the return value is (status, body bytes). The tests replace this function."""
    headers = {"Authorization": f"Bearer {key}"}
    if data is not None:
        headers["Content-Type"] = content_type
    status, _, body = http_request(method, url, headers, data)
    return status, body


def google_send(method, url, key, data=None, headers=None):
    """One HTTP request with the x-goog-api-key header; the return value is (status, response headers, body bytes).
    The tests replace this function."""
    sent = {"x-goog-api-key": key, **({"Content-Type": "application/json"} if data is not None else {}), **(headers or {})}
    return http_request(method, url, sent, data)


class Store:
    """The verbatim responses of one step: one JSON line per request with a final answer (custom_id, HTTP status, body
    text). Each line is on disk before the body is parsed. A request without a line is sent again on a rerun.

    With an api, the step is sealed (seal.py): a line holds the public row fields and the sealed status and body."""

    def __init__(self, path, api=None):
        self.path, self.lock, self.done = path, threading.Lock(), {}
        self.api = api
        self.sealer = seal.Sealer(path.parent) if api else None
        if path.exists():
            data = path.read_bytes()
            if not data.endswith(b"\n"):  # a crash cut the last line
                path.write_bytes(data[:data.rfind(b"\n") + 1])
            for line in path.read_text().splitlines():
                rec = json.loads(line)
                self.done[rec["custom_id"]] = rec

    def add(self, custom_id, status, data):
        rec = {"custom_id": custom_id, "status": status, "body": data.decode("utf-8", "replace")}
        if self.sealer:
            rec = {"custom_id": custom_id, "public": seal.public(row(self.api, custom_id, rec)),
                   "sealed": self.sealer.seal(json.dumps(rec).encode())}
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            self.done[custom_id] = rec


class Budget:
    """The money that a synchronous step can have used, at list prices. Each call reserves its worst case before it is
    sent, so the step stays within its approved bound, also with retries."""

    def __init__(self, cap):
        self.cap, self.used, self.lock = cap, 0.0, threading.Lock()

    def reserve(self, usd):
        with self.lock:
            if self.used + usd > self.cap:
                return False
            self.used += usd
            return True

    def settle(self, reserved, actual):
        with self.lock:
            self.used += actual - reserved


def call_all(name, step, todo, bound, a, api, store):
    """Send each request synchronously and store each final answer. The ledger row records the money that the calls
    can have used: the cost of each answer, plus the worst case of each call that got no answer or an HTTP 5xx."""
    key = accounts.api_key(a)
    held = accounts.hold(a, name, step, bound)
    budget, stop, sent = Budget(bound / accounts.factor(a)), threading.Event(), []

    def one(r):
        try:
            attempts(r)
        except BaseException:
            stop.set()  # the other workers send nothing more
            raise

    def attempts(r):
        limit = worst(api, r)
        for attempt in range(ATTEMPTS):
            if attempt:
                sleep(2 ** attempt + random.random())
            if stop.is_set() or not budget.reserve(limit):
                stop.set()
                return
            sent.append(r["custom_id"])
            try:
                status, body = api.post(key, r["body"])
            except NoAnswer:
                continue
            if status == 200:
                store.add(r["custom_id"], status, body)
                try:
                    u = api.decode(json.loads(body))
                    actual = cost(api, r["body"]["model"], u["input_tokens"], u["output_tokens"], batch=False)
                except (ValueError, KeyError, TypeError, IndexError):
                    actual = limit
                budget.settle(limit, actual)
                return
            if status >= 500:
                continue
            budget.settle(limit, 0.0)  # an HTTP 4xx answer runs no model, so it costs nothing
            if status in (408, 429):
                continue
            if status in FATAL:
                raise RuntimeError(f"{name}: HTTP {status} from {a.provider}: {body[:300]!r}")
            store.add(r["custom_id"], status, body)  # the same request gets the same error again
            return

    pool = concurrent.futures.ThreadPoolExecutor(WORKERS)
    try:
        for f in [pool.submit(one, r) for r in todo]:
            f.result()
    finally:
        stop.set()
        pool.shutdown(cancel_futures=True)
        accounts.ledger(a, name, step, bound, budget.used)
        held.unlink()
        missing = sum(r["custom_id"] not in store.done for r in todo)
        print(f"{name} {step}: {len(sent)} calls, {len(todo) - missing} answers stored, {missing} without an answer "
              f"(a rerun sends them), {budget.used:.4f} USD used at list prices")
    return budget.used


def row(api, custom_id, rec):
    """One raw.jsonl row, in the format of anth.fetch, from a stored answer: an HTTP status and a body."""
    if rec is None:
        return {"custom_id": custom_id, "type": "absent"}
    if "public" in rec:  # a sealed Store line
        return rec["public"]
    body = rec["body"]
    if rec["status"] != 200:
        return {"custom_id": custom_id, "type": "errored", "status": rec["status"],
                "error": (body if isinstance(body, str) else json.dumps(body))[:1000]}
    try:
        return {"custom_id": custom_id, "type": "succeeded",
                **api.decode(json.loads(body) if isinstance(body, str) else body)}
    except (ValueError, KeyError, TypeError, IndexError):
        return {"custom_id": custom_id, "type": "unparsed", "error": str(body)[:1000]}


def write_rows(path, api, models, recs, batch, sealer=None):
    """Write one row per request, in request order. `models` maps each custom_id to its model. Return the cost.
    With a sealer, the full rows go into raw.sealed and raw.jsonl keeps the public fields (anth.write_raw)."""
    spent, counts, out = 0.0, {}, []
    path.parent.mkdir(parents=True, exist_ok=True)
    for cid, model in models.items():
        x = row(api, cid, recs.get(cid))
        if x["type"] == "succeeded":
            spent += cost(api, model, x["input_tokens"], x["output_tokens"], batch)
        counts[x["type"]] = counts.get(x["type"], 0) + 1
        out.append(x)
    if sealer or any("public" in r for r in recs.values() if r):
        if sealer:
            seal.write_blob(path.with_name(path.stem + ".sealed"), "".join(json.dumps(x) + "\n" for x in out).encode(), sealer)
        out = [seal.public(x) for x in out]
    tmp = path.with_name(path.name + ".part")
    with open(tmp, "w") as fh:
        for x in out:
            fh.write(json.dumps(x) + "\n")
    os.replace(tmp, path)
    print(f"{path.parent.name}: {path.name} rows {counts}, cost at {'batch' if batch else 'standard'} list prices "
          f"{spent:.4f} USD")
    return spent


def pilot(name, reqs, approve, a, api):
    """A few synchronous calls per (model, effort) cell. The bound uses the output cap, so it is a hard upper limit."""
    sample = anth.pilot_sample(reqs, cell)
    store = Store(accounts.folder(name) / "pilot_responses.jsonl", api if seal.sealed(name) else None)
    todo = [r for r in sample if r["custom_id"] not in store.done]
    bound = cents_up(sum(worst(api, r) for r in todo) * accounts.factor(a))
    print(f"{name} pilot on {a.name}: {len(todo)} synchronous calls ({len(sample) - len(todo)} stored), "
          f"hard bound {bound:.2f} USD at the output cap and list prices")
    if todo:
        accounts.check_approval(a, approve, bound)
        call_all(name, "pilot", todo, bound, a, api, store)
    write_rows(accounts.folder(name) / "pilot_raw.jsonl", api, {r["custom_id"]: cell(r)[0] for r in sample},
               store.done, batch=False)
    out = {}
    for r in sample:
        x = row(api, r["custom_id"], store.done.get(r["custom_id"]))
        if x["type"] == "succeeded":
            out.setdefault("|".join(cell(r)), []).append(dict(x, est_in=est_in(r)))
    summary = {k: {"in_ratio": sum(x["input_tokens"] for x in v) / sum(x["est_in"] for x in v),
                   "out_mean": sum(x["output_tokens"] for x in v) / len(v),
                   "out_max": max(x["output_tokens"] for x in v),
                   "reasoning_mean": sum(x["reasoning_tokens"] for x in v) / len(v),
                   "stops": sorted({x["stop"] for x in v}), "n": len(v)} for k, v in out.items()}
    anth.pilot_path(name).write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def run(name, reqs, planning_out, approve, a, api):
    """Every request, synchronously, at standard prices. A rerun sends only the requests without a stored answer."""
    store = Store(accounts.folder(name) / "responses.jsonl", api if seal.sealed(name) else None)
    todo = [r for r in reqs if r["custom_id"] not in store.done]
    print(f"{name}: {len(reqs) - len(todo)} of {len(reqs)} requests have a stored answer")
    if todo:
        in_flight = WORKERS * max(worst(api, r) for r in todo)
        bound = print_estimate(name, todo, planning_out, a, api, in_flight)
        accounts.check_approval(a, approve, bound)
        call_all(name, "run", todo, bound, a, api, store)
    write_rows(accounts.folder(name) / "raw.jsonl", api, {r["custom_id"]: cell(r)[0] for r in reqs}, store.done,
               batch=False)


def multipart(filename, content):
    """A multipart form with the field purpose=batch and the file. UNVERIFIED: the content type of the file part."""
    boundary = uuid.uuid4().hex
    head = (f'--{boundary}\r\nContent-Disposition: form-data; name="purpose"\r\n\r\nbatch\r\n'
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f'Content-Type: application/octet-stream\r\n\r\n')
    return head.encode() + content + f"\r\n--{boundary}--\r\n".encode(), f"multipart/form-data; boundary={boundary}"


def get(url, key):
    """A free GET of the batch API. A failure stops the step; a rerun continues from the files on disk."""
    try:
        status, data = send("GET", url, key)
    except NoAnswer as e:
        sys.exit(f"No answer from {url} ({e}). Rerun the step.")
    if status != 200:
        sys.exit(f"HTTP {status} from {url}: {data[:300]!r}")
    return data


def write_once(path, data):
    tmp = path.with_name(path.name + ".part")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def submit(name, reqs, planning_out, approve, a, api):
    """One OpenAI batch: upload the JSONL input file, then create the batch with the endpoint /v1/responses."""
    folder = accounts.folder(name)
    if (folder / "batch.json").exists():
        sys.exit(f"{name} already has a batch: {(folder / 'batch.json').read_text()}")
    models = sorted({r["body"]["model"] for r in reqs})
    if len(models) > 1:  # OpenAI fails a batch file with more than one model (ex2c_oa and ex2s_oa, 2026-11-03)
        sys.exit(f"Not run. An OpenAI batch takes one model, and {name} has {models}. Put each model in its own folder.")
    bound = print_estimate(name, reqs, planning_out, a, api)
    accounts.check_approval(a, approve, bound)
    key = accounts.api_key(a)
    lines ="".join(json.dumps({"custom_id": r["custom_id"], "method": "POST", "url": "/v1/responses",
                                "body": r["body"]}) + "\n" for r in reqs).encode()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "requests.jsonl").write_bytes(lines)
    form, content_type = multipart(f"{name}_requests.jsonl", lines)
    try:
        status, data = send("POST", f"{OPENAI}/files", key, form, content_type)
    except NoAnswer as e:
        sys.exit(f"{name}: no answer to the file upload ({e}). No batch exists. Rerun the step.")
    if status != 200:
        sys.exit(f"{name}: file upload failed, HTTP {status}: {data[:300]!r}")
    file_id = json.loads(data)["id"]
    held = accounts.hold(a, name, "submit", bound)
    create = {"input_file_id": file_id, "endpoint": "/v1/responses", "completion_window": "24h",
              "metadata": {"experiment": name}}
    try:
        status, data = send("POST", f"{OPENAI}/batches", key, json.dumps(create).encode())
    except NoAnswer as e:
        sys.exit(f"{name}: no answer to the batch request ({e}), so a batch can exist. {held} stays, and its bound "
                 f"stays committed. Find metadata experiment={name} in the OpenAI batch list. If the batch exists, "
                 f"write its id into batch.json. Then delete {held.name}.")
    if status != 200:
        held.unlink()
        sys.exit(f"{name}: batch not created, HTTP {status}: {data[:300]!r}")
    batch = json.loads(data)
    (folder / "batch.json").write_text(json.dumps({"id": batch["id"], "bound": bound, "requests": len(reqs),
                                                   "created": accounts.now(), "account": a.name,
                                                   "script": anth.script(), "input_file_id": file_id}))
    held.unlink()
    print(f"{name}: batch {batch['id']} submitted, {len(reqs)} requests, status {batch.get('status')}")


def fetch(name, a, api):
    """Download the output and error files of an ended batch once, then write raw.jsonl and one ledger row."""
    folder = accounts.folder(name)
    info = anth.batch_info(folder, a)
    final = folder / "batch_final.json"
    sealer, files = None, {}
    if seal.sealed(name) and (folder / "raw.jsonl").exists():
        sys.exit(f"{name}: already fetched and sealed. The answers are in the sealed files only.")
    if seal.sealed(name) or not final.exists():  # a sealed run keeps no plain copy, so it downloads in one pass
        key = accounts.api_key(a)
        batch = json.loads(get(f"{OPENAI}/batches/{info['id']}", key))
        if batch["status"] not in TERMINAL:
            sys.exit(f"{name}: {batch['status']}, counts {batch.get('request_counts')}")
        sealer = seal.Sealer(folder) if seal.sealed(name) else None
        for field, file in (("output_file_id", "batch_output.jsonl"), ("error_file_id", "batch_errors.jsonl")):
            if not batch.get(field):
                continue
            if sealer:
                files[file] = get(f"{OPENAI}/files/{batch[field]}/content", key)
                seal.write_blob(folder / f"{file}.sealed", files[file], sealer)
            elif not (folder / file).exists():
                write_once(folder / file, get(f"{OPENAI}/files/{batch[field]}/content", key))
        if not sealer:
            write_once(final, json.dumps(batch).encode())
    else:
        batch = json.loads(final.read_text())
    if not sealer:
        files = {f: (folder / f).read_bytes() for f in ("batch_output.jsonl", "batch_errors.jsonl") if (folder / f).exists()}
    recs = {}
    for file in ("batch_output.jsonl", "batch_errors.jsonl"):
        for line in files.get(file, b"").decode().splitlines():
            x = json.loads(line)
            resp = x.get("response")
            recs[x["custom_id"]] = ({"status": resp.get("status_code"), "body": resp.get("body")} if resp
                                    else {"status": None, "body": x.get("error")})
    models = {r["custom_id"]: r["body"]["model"] for r in map(json.loads, open(folder / "requests.jsonl"))}
    spent = write_rows(folder / "raw.jsonl", api, models, recs, batch=True, sealer=sealer)
    if sealer:
        write_once(final, json.dumps(batch).encode())
    if not accounts.has_row(a, name, "batch"):
        accounts.ledger(a, name, "batch", info["bound"], spent)
    print(f"{name}: batch {batch['status']}, counts {batch.get('request_counts')}, errors {batch.get('errors')}, "
          f"cost at batch list prices {spent:.2f} USD (bound {info['bound']:.2f})")


def google_get(url, key):
    """A free GET of the Gemini batch API. A failure stops the step; a rerun continues from the files on disk."""
    try:
        status, _, data = google_send("GET", url, key)
    except NoAnswer as e:
        sys.exit(f"No answer from {url} ({e}). Rerun the step.")
    if status != 200:
        sys.exit(f"HTTP {status} from {url}: {data[:300]!r}")
    return data


def google_upload(name, content, key):
    """The resumable upload of the batch input file: a start request, then the bytes to the URL in the
    x-goog-upload-url header. Return the file name ("files/..."). UNVERIFIED: that the batch takes `file.name`."""
    start = {"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
             "X-Goog-Upload-Header-Content-Length": str(len(content)),
             "X-Goog-Upload-Header-Content-Type": "application/jsonl", "Content-Type": "application/jsonl"}
    try:
        status, headers, data = google_send("POST", GEMINI_UPLOAD, key,
                                            json.dumps({"file": {"display_name": f"{name}_requests.jsonl"}}).encode(), start)
        url = headers.get("x-goog-upload-url", "")
        if status != 200 or not url.startswith(GEMINI_UPLOAD):
            sys.exit(f"{name}: upload not started, HTTP {status}: {data[:300]!r}. No batch exists. Rerun the step.")
        status, _, data = google_send("POST", url, key, content, {"X-Goog-Upload-Offset": "0",
                                                                  "X-Goog-Upload-Command": "upload, finalize"})
    except NoAnswer as e:
        sys.exit(f"{name}: no answer to the file upload ({e}). No batch exists. Rerun the step.")
    if status != 200:
        sys.exit(f"{name}: file upload failed, HTTP {status}: {data[:300]!r}. No batch exists. Rerun the step.")
    return json.loads(data)["file"]["name"]


def google_submit(name, reqs, planning_out, approve, a, api):
    """One Gemini batch: upload the JSONL input file, then create the batch with models/<model>:batchGenerateContent."""
    folder = accounts.folder(name)
    if (folder / "batch.json").exists():
        sys.exit(f"{name} already has a batch: {(folder / 'batch.json').read_text()}")
    models = sorted({r["body"]["model"] for r in reqs})
    if len(models) > 1:
        sys.exit(f"Not run. A Gemini batch takes one model, because the URL names it, and {name} has {models}.")
    bound = print_estimate(name, reqs, planning_out, a, api)
    accounts.check_approval(a, approve, bound)
    key = accounts.api_key(a)
    lines = "".join(json.dumps({"key": r["custom_id"], "request": wire(r["body"])}) + "\n" for r in reqs).encode()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "requests.jsonl").write_bytes(lines)
    file_name = google_upload(name, lines, key)
    held = accounts.hold(a, name, "submit", bound)
    create = {"batch": {"display_name": name, "input_config": {"file_name": file_name}}}
    try:
        status, _, data = google_send("POST", f"{GEMINI}/models/{models[0]}:batchGenerateContent", key,
                                      json.dumps(create).encode())
    except NoAnswer as e:
        sys.exit(f"{name}: no answer to the batch request ({e}), so a batch can exist. {held} stays, and its bound "
                 f"stays committed. Find display name {name} in the Gemini batch list. If the batch exists, write its "
                 f"name into batch.json. Then delete {held.name}.")
    if status != 200:
        held.unlink()
        sys.exit(f"{name}: batch not created, HTTP {status}: {data[:300]!r}")
    batch = json.loads(data)
    (folder / "batch.json").write_text(json.dumps({"id": batch["name"], "bound": bound, "requests": len(reqs),
                                                   "created": accounts.now(), "account": a.name, "model": models[0],
                                                   "script": anth.script(), "input_file": file_name}))
    held.unlink()
    print(f"{name}: batch {batch['name']} submitted, {len(reqs)} requests")


def google_status(op):
    """The state, the statistics, and the output file of a batch. The batch guide reads `.metadata.state` and
    `.response.responsesFile` in one example and `.state` and `.dest.fileName` in another; the reference names
    `output.responsesFile`. This function reads every one of these paths."""
    b = op.get("metadata") or op
    file = ((op.get("response") or {}).get("responsesFile") or (b.get("output") or {}).get("responsesFile")
            or (op.get("dest") or {}).get("fileName"))
    return {"name": op.get("name"), "state": str(b.get("state")), "batchStats": b.get("batchStats"), "responsesFile": file}


def google_fetch(name, a, api):
    """Download the output file of an ended batch once, then write raw.jsonl and one ledger row. batch_final.json keeps
    only the state, the statistics, and the file name, so that no answer text gets into it."""
    folder = accounts.folder(name)
    info = anth.batch_info(folder, a)
    final = folder / "batch_final.json"
    sealer, out = None, b""
    if seal.sealed(name) and (folder / "raw.jsonl").exists():
        sys.exit(f"{name}: already fetched and sealed. The answers are in the sealed files only.")
    if seal.sealed(name) or not final.exists():  # a sealed run keeps no plain copy, so it downloads in one pass
        key = accounts.api_key(a)
        status = google_status(json.loads(google_get(f"{GEMINI}/{info['id']}", key)))
        if status["state"].rsplit("_", 1)[-1] not in GEMINI_DONE:
            sys.exit(f"{name}: {status['state']}, stats {status['batchStats']}")
        sealer = seal.Sealer(folder) if seal.sealed(name) else None
        if status["responsesFile"]:
            url = f"{GEMINI_DOWNLOAD}/{status['responsesFile']}:download?alt=media"
            if sealer:
                out = google_get(url, key)
                seal.write_blob(folder / "batch_output.jsonl.sealed", out, sealer)
            elif not (folder / "batch_output.jsonl").exists():
                write_once(folder / "batch_output.jsonl", google_get(url, key))
        if not sealer:
            write_once(final, json.dumps(status).encode())
    else:
        status = json.loads(final.read_text())
    if not sealer and (folder / "batch_output.jsonl").exists():
        out = (folder / "batch_output.jsonl").read_bytes()
    recs = {}
    for line in out.decode().splitlines():
        x = json.loads(line)
        if "key" not in x:
            sys.exit(f"{name}: an output line has no key, so it cannot be matched to its request. Nothing is written.")
        recs[x["key"]] = ({"status": 200, "body": x["response"]} if x.get("response")
                          else {"status": None, "body": x.get("error") or x.get("status")})
    models = {json.loads(line)["key"]: info["model"] for line in open(folder / "requests.jsonl")}
    spent = write_rows(folder / "raw.jsonl", api, models, recs, batch=True, sealer=sealer)
    if sealer:
        write_once(final, json.dumps(status).encode())
    if not accounts.has_row(a, name, "batch"):
        accounts.ledger(a, name, "batch", info["bound"], spent)
    print(f"{name}: batch {status['state']}, stats {status['batchStats']}, cost at batch list prices {spent:.2f} USD "
          f"(bound {info['bound']:.2f})")


def check_requests(reqs, api):
    ids = [r["custom_id"] for r in reqs]
    assert len(ids) == len(set(ids)), "duplicate custom_id"
    assert all(len(i) <= 64 and all(c.isalnum() or c in "_-" for c in i) for i in ids), "custom_id format"
    wrong = sorted({r["body"]["model"] for r in reqs} - set(api.prices))
    assert not wrong, f"models {wrong} are not served by this account's provider"
    assert all(api.cap(r["body"]) for r in reqs), "every request needs an output token cap"


def check_prices(api, today=None):
    """A paid step stops 2 days before the last day of the prices, so that no call can bill at newer prices."""
    today = today or datetime.date.today()
    if api.until and today > api.until - datetime.timedelta(days=2):
        sys.exit(f"Not run. The prices in APIS end on {api.until}. Put the new list prices into APIS first.")


BATCH_STEPS = {"openai": (submit, fetch), "google": (google_submit, google_fetch)}


def main(name, build, planning_out, *, account):
    """`account` names an OpenAI, DeepInfra, or Google account of accounts.ACCOUNTS and so selects the provider. It has
    no default."""
    a = accounts.account(account, tuple(APIS))
    api = APIS[a.provider]
    accounts.folder(name)
    ap = argparse.ArgumentParser(description=f"{name}: exploratory requests on {a.name} (PROTOCOL.md)")
    ap.add_argument("step", choices=["estimate", "pilot", "submit", "fetch"] if api.batch else ["estimate", "pilot", "run"])
    ap.add_argument("--approve", help="the bound that the operator approved in writing")
    args = ap.parse_args()
    if args.step == "fetch":
        return BATCH_STEPS[a.provider][1](name, a, api)
    reqs = build()
    check_requests(reqs, api)
    if args.step != "estimate":
        check_prices(api)
    if args.step == "estimate":
        print_estimate(name, reqs, planning_out, a, api)
    elif args.step == "pilot":
        pilot(name, reqs, args.approve, a, api)
    elif args.step == "submit":
        BATCH_STEPS[a.provider][0](name, reqs, planning_out, args.approve, a, api)
    else:
        run(name, reqs, planning_out, args.approve, a, api)
