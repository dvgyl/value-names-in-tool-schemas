"""Spending guard and client test, with a fake transport. It makes no network call.

1. Recorded usage blocks give the expected cost, and the stop values match those of anth.py.
2. A paid step on each account refuses a wrong --approve value and a bound that passes the limit, before it reads a key.
3. Each account has its own ledger, batches, and open steps.
4. The old Anthropic account keeps its key, ledger, limit, committed money, refusal text, and ledger row format.
5. A synchronous rerun skips the requests with a stored answer, also after a crash that cut a line.
6. Retries keep the worst case of each call that can have run, the bound stops a run, and HTTP 401 stops a step.
7. An OpenAI batch goes through submit and fetch. A second fetch makes no call and writes no second ledger row.
8. No key is in a file or in the output.

Usage: python3 -I test_clients.py
"""
import contextlib
import csv
import inspect
import io
import json
import pathlib
import shutil
import sys
import tempfile
import types
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import accounts  # noqa: E402
import anth  # noqa: E402
import openai_compat as oc  # noqa: E402

REAL = accounts.EXPLORE
KEY = "test-key-7f3a9c"  # each account gets KEY-<account name>, a fake value


def no_network(*args, **kw):
    raise AssertionError("a step tried to reach the network")


class FakeAnthropic:
    """The part of anthropic.Anthropic that anth.pilot uses. `expect` is the key of the account under test."""
    expect = None

    def __init__(self, api_key, max_retries):
        assert FakeAnthropic.expect and api_key == FakeAnthropic.expect, "the step used the key of another account"
        self.messages = types.SimpleNamespace(create=self.create)

    def create(self, **params):
        usage = types.SimpleNamespace(input_tokens=1000, output_tokens=500)
        return types.SimpleNamespace(model=params["model"], stop_reason="end_turn", usage=usage)


urllib.request.urlopen = no_network
sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=FakeAnthropic, APIStatusError=type("APIStatusError", (Exception,), {}))

# The usage block of the OpenAI reasoning guide: output_tokens includes the 1,024 reasoning tokens.
RESPONSE = {"id": "resp_1", "object": "response", "status": "completed", "model": "gpt-6.1-sol-2026-09-30",
            "output": [{"type": "reasoning", "id": "rs_1", "summary": []},
                       {"type": "message", "role": "assistant",
                        "content": [{"type": "output_text", "text": "{\"a\": 1}", "annotations": []}]}],
            "usage": {"input_tokens": 75, "input_tokens_details": {"cached_tokens": 0}, "output_tokens": 1186,
                      "output_tokens_details": {"reasoning_tokens": 1024}, "total_tokens": 1261}}
CHAT = {"id": "chatcmpl-1", "object": "chat.completion", "model": "Qwen/Qwen3.8-27B",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\"a\": 1}"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1000, "completion_tokens": 500, "total_tokens": 1500}}
CHAT_COST = 0.00145  # (1000 x 0.20 + 500 x 2.50) / 1e6
SCHEMA = {"type": "object", "properties": {"a": {"type": "integer"}}, "required": ["a"], "additionalProperties": False}
D, O = accounts.ACCOUNTS["deepinfra"], accounts.ACCOUNTS["openai_r9"]
DI, OA = oc.APIS["deepinfra"], oc.APIS["openai"]


def chat_reqs(n):
    return [oc.deepinfra_request(f"d{i}", "Qwen/Qwen3.8-27B", 1000, f"question {i} " * 20, schema=SCHEMA)
            for i in range(n)]


def resp_reqs(n):
    return [oc.openai_request(f"o{i}", "gpt-6.1-sol", "low", 2000, f"question {i} " * 20, "Answer in JSON.", SCHEMA)
            for i in range(n)]


def claude_reqs(n):
    return [anth.request(f"c{i}", "claude-haiku-5-5", "low", 20000, "hi " * 50) for i in range(n)]


class Fake:
    """A recorded transport. `answer(method, url, body)` returns (status, bytes) or raises."""

    def __init__(self, answer, account):
        self.answer, self.key, self.calls = answer, f"{KEY}-{account.name}", []

    def __call__(self, method, url, key, data=None, content_type="application/json"):
        assert key == self.key, "the step sent the key of another account"
        self.calls.append((method, url, data))
        return self.answer(method, url, data)


def always(status, body):
    return lambda method, url, data: (status, json.dumps(body).encode())


@contextlib.contextmanager
def sandbox(env=True):
    """A temporary explore folder. Without `env` there is no key file, so a key read stops with "empty or missing", not
    with a refusal."""
    with tempfile.TemporaryDirectory() as tmp:
        root, env_path = pathlib.Path(tmp) / "explore", pathlib.Path(tmp) / ".env"
        root.mkdir()
        if env:
            env_path.write_text("".join(f"{a.key}={KEY}-{a.name}\n" for a in accounts.ACCOUNTS.values()))
        saved = accounts.EXPLORE, anth.EXPLORE, accounts.ENV_FILES, oc.send, oc.sleep, oc.WORKERS
        accounts.EXPLORE = anth.EXPLORE = root
        accounts.ENV_FILES, oc.send, oc.sleep, oc.WORKERS = (env_path,), no_network, lambda s: None, 1
        try:
            yield root
            leaked = [p for p in pathlib.Path(tmp).rglob("*") if p.is_file() and p != env_path
                      and KEY.encode() in p.read_bytes()]
            assert not leaked, f"a key is in {leaked}"
        finally:
            accounts.EXPLORE, anth.EXPLORE, accounts.ENV_FILES, oc.send, oc.sleep, oc.WORKERS = saved


def refused(step, *args):
    """Run a step that must refuse, and return the refusal text."""
    try:
        step(*args)
    except SystemExit as e:
        return str(e.code)
    raise AssertionError(f"{step.__name__} did not refuse")


def operator(step):
    """Run a paid step as the operator does: read the bound from the refusal, then approve exactly that bound."""
    text = refused(step, None)
    assert "Rerun with --approve" in text, text
    return step(text.split("--approve ")[1].split()[0])


def rows(path):
    return list(csv.DictReader(open(path))) if path.exists() else []


def spent(root, account, step):
    return [float(r["list_price_usd"]) for r in rows(root / account.ledger) if r["step"] == step]


def ids_of(calls, reqs):
    by_body = {json.dumps(r["body"]).encode(): r["custom_id"] for r in reqs}
    return sorted(by_body[data] for _, _, data in calls)


def test_cost_from_recorded_usage():
    r = OA.decode(RESPONSE)
    assert (r["input_tokens"], r["output_tokens"], r["reasoning_tokens"], r["stop"], r["text"]) == (
        75, 1186, 1024, "end_turn", '{"a": 1}'), r
    assert abs(oc.cost(OA, "gpt-6.1-sol", 75, 1186, batch=False) - 0.01201) < 1e-12  # (75 x 2 + 1186 x 10) / 1e6
    assert abs(oc.cost(OA, "gpt-6.1-sol", 75, 1186, batch=True) - 0.006005) < 1e-12
    c = DI.decode(CHAT)
    assert (c["input_tokens"], c["output_tokens"], c["stop"], c["text"]) == (1000, 500, "end_turn", '{"a": 1}'), c
    assert abs(oc.cost(DI, "Qwen/Qwen3.8-27B", 1000, 500, batch=False) - CHAT_COST) < 1e-12
    cut = dict(RESPONSE, status="incomplete", incomplete_details={"reason": "max_output_tokens"})
    refusal = dict(RESPONSE, output=[{"type": "message", "content": [{"type": "refusal", "refusal": "no"}]}])
    length = dict(CHAT, choices=[dict(CHAT["choices"][0], finish_reason="length")])
    assert (OA.decode(cut)["stop"], OA.decode(refusal)["stop"], DI.decode(length)["stop"]) == (
        "max_tokens", "refusal", "max_tokens"), "the analysis scripts count only these stop values"


def test_approval_mismatch_refused():
    with sandbox(env=False) as root:
        r9 = accounts.ACCOUNTS["anthropic_r9a"]
        for step, args in ((oc.pilot, ("e90", chat_reqs(3), "9.99", D, DI)),
                           (oc.run, ("e90", chat_reqs(3), 100, "9.99", D, DI)),
                           (oc.pilot, ("e91", resp_reqs(3), None, O, OA)),
                           (oc.submit, ("e91", resp_reqs(3), 100, "9.99", O, OA)),
                           (anth.pilot, ("e92", claude_reqs(3), "9.99", r9)),
                           (anth.submit, ("e92", claude_reqs(3), 100, None, r9))):
            text = refused(step, *args)
            assert text.startswith("Not run. Rerun with --approve "), (step.__name__, text)
        assert not list(root.rglob("*")), "a refused step wrote a file"


def test_limit_refused():
    with sandbox(env=False) as root:
        accounts.ledger(D, "e80", "run", 21.18, 21.18)  # 21.18 x 1.18 = 24.99 committed of 25.00
        for step in (lambda approve: oc.pilot("e81", chat_reqs(3), approve, D, DI),
                     lambda approve: oc.run("e81", chat_reqs(3), 100, approve, D, DI)):
            text = refused(step, None)
            assert text.startswith("Not run. 24.99 USD is committed, and "), text
            assert text.endswith(" more would pass the 25.00 USD limit."), text
        (root / "e82").mkdir()
        (root / "e82" / "pilot.open.json").write_text(json.dumps({"account": "openai_r9", "step": "pilot", "bound": 149.99}))
        assert "149.99 USD is committed" in refused(oc.pilot, "e83", resp_reqs(2), None, O, OA)
        (root / "e84").mkdir()
        (root / "e84" / "batch.json").write_text(json.dumps({"id": "msgbatch_x", "bound": 199.99, "account": "anthropic_r9b"}))
        assert "199.99 USD is committed" in refused(anth.pilot, "e85", claude_reqs(2), None, accounts.ACCOUNTS["anthropic_r9b"])
        assert sorted(p.name for p in root.iterdir()) == ["e82", "e84", D.ledger], "a refused step wrote a file"


def test_ledgers_apart():
    with sandbox() as root:
        oc.send = Fake(always(200, CHAT), D)
        operator(lambda approve: oc.pilot("e50", chat_reqs(3), approve, D, DI))
        assert [abs(x - 3 * CHAT_COST) < 1e-4 for x in spent(root, D, "pilot")] == [True]
        assert sorted(p.name for p in root.glob("ledger*")) == [D.ledger], "a row went to another ledger"
        assert abs(accounts.committed(D) - 3 * CHAT_COST * accounts.TAX) < 2e-4
        others = [a for a in accounts.ACCOUNTS.values() if a is not D]
        assert [accounts.committed(a) for a in others] == [0] * len(others)
        for folder, info in (("e51", {"id": "batch_1", "bound": 5.0, "account": "openai_r9"}),
                             ("e52", {"id": "msgbatch_1", "bound": 7.0})):
            (root / folder).mkdir()
            (root / folder / "batch.json").write_text(json.dumps(info))
        assert (accounts.committed(O), accounts.committed(accounts.ACCOUNTS["anthropic_old"]),
                accounts.committed(accounts.ACCOUNTS["anthropic_r9a"])) == (5.0, 7.0, 0)


def old_rule(root):
    """The committed money of lib/anth.py before the accounts table, copied unchanged except for the folder and for the
    batches of the new accounts, which the old rule never saw."""
    ledger = root / "ledger.csv"
    rows = list(csv.DictReader(open(ledger))) if ledger.exists() else []
    actual = {r["experiment"]: float(r["list_price_usd"]) for r in rows if r["step"] == "batch"}
    pilots = sum(float(r["list_price_usd"]) for r in rows if r["step"] == "pilot")
    old = [(p, json.loads(p.read_text())) for p in root.glob("e*/batch.json")]
    batches = sum(actual.get(p.parent.name, info["bound"]) for p, info in old if info.get("account", accounts.OLD) == accounts.OLD)
    return batches + pilots


def test_old_account_unchanged():
    old = accounts.ACCOUNTS["anthropic_old"]
    assert (old.provider, old.key, old.ledger, old.limit, old.paid_from, old.cash) == (
        "anthropic", "ANTHROPIC_API_KEY", "ledger.csv", 208.51, "anthropic promo credits", False)
    assert accounts.committed(old) == old_rule(REAL), "the live old account changed"
    with sandbox(env=False) as root:
        shutil.copy(REAL / "ledger.csv", root / "ledger.csv")
        for p in REAL.glob("e*/batch.json"):
            (root / p.parent.name).mkdir()
            shutil.copy(p, root / p.parent.name / "batch.json")
        before = old_rule(root)
        (root / "e70").mkdir()
        (root / "e70" / "batch.json").write_text(json.dumps({"id": "msgbatch_y", "bound": 50.0, "account": "anthropic_r9a"}))
        (root / "e70" / "submit.open.json").write_text(json.dumps({"account": "openai_r9", "step": "submit", "bound": 3.0}))
        accounts.ledger(accounts.ACCOUNTS["anthropic_r9b"], "e70", "pilot", 1.0, 0.5)
        assert abs(accounts.committed(old) - before) < 1e-9, "money of a new account counted for the old account"
        assert refused(accounts.check_approval, old, "0.44", 0.44) == (
            f"Not run. {before:.2f} USD is committed, and 0.44 more would pass the 208.51 USD limit.")
        assert refused(accounts.check_approval, old, "0.01", 0.0) == (
            "Not run. Rerun with --approve 0.00 after the operator approves this bound in writing.")
        accounts.ledger(old, "e99", "pilot", 0.0, 0.0123)
        lines = (root / "ledger.csv").read_text().splitlines()
        assert lines[0] == "utc,experiment,step,bound_usd,list_price_usd,paid_from,cash_usd"
        assert lines[-1].split(",")[1:] == ["e99", "pilot", "0.00", "0.0123", "anthropic promo credits", "0.00"]
        assert "submitted on anthropic_old" in refused(anth.batch_info, root / "e14", accounts.ACCOUNTS["anthropic_r9a"])
        assert anth.batch_info(root / "e14", old)["id"].startswith("msgbatch_")


def test_anthropic_accounts_apart():
    a, b = accounts.ACCOUNTS["anthropic_r9a"], accounts.ACCOUNTS["anthropic_r9b"]
    assert (a.key, a.ledger, a.limit, b.key, b.ledger, b.limit) == (
        "ANTHROPIC_API_KEY_R9A", "ledger_anthropic_r9a.csv", 200.0, "ANTHROPIC_API_KEY_R9B", "ledger_anthropic_r9b.csv", 200.0)
    with sandbox() as root:
        try:
            FakeAnthropic.expect = f"{KEY}-anthropic_r9a"
            operator(lambda approve: anth.pilot("e60", claude_reqs(3), approve, a))
            haiku = 0.00035  # (1000 x 0.10 + 500 x 0.50) / 1e6, standard price
            assert [abs(x - 3 * haiku) < 1e-4 for x in spent(root, a, "pilot")] == [True]
            assert not (root / b.ledger).exists() and accounts.committed(b) == 0
            (root / "e61").mkdir()
            (root / "e61" / "batch.json").write_text(json.dumps({"id": "msgbatch_z", "bound": 199.99, "account": a.name}))
            assert refused(anth.pilot, "e62", claude_reqs(2), None, a).endswith("pass the 200.00 USD limit.")
            assert refused(anth.pilot, "e62", claude_reqs(2), None, b).startswith("Not run. Rerun with --approve")
            FakeAnthropic.expect = f"{KEY}-anthropic_r9b"
            operator(lambda approve: anth.pilot("e62", claude_reqs(2), approve, b))
            assert (len(spent(root, a, "pilot")), len(spent(root, b, "pilot"))) == (1, 1)
            assert abs(accounts.committed(b) - 2 * haiku) < 1e-4, "money of r9a counted for r9b"
            assert "submitted on anthropic_r9a" in refused(anth.batch_info, root / "e61", b), "a batch spans two accounts"
        finally:
            FakeAnthropic.expect = None


class Crash(Exception):
    pass


def test_resume_skips_answered():
    with sandbox() as root:
        reqs = chat_reqs(6)

        def crash_on_fourth(method, url, data):
            if len(first.calls) == 4:
                raise Crash
            return 200, json.dumps(CHAT).encode()

        first = oc.send = Fake(crash_on_fourth, D)
        try:
            operator(lambda approve: oc.run("e40", reqs, 2000, approve, D, DI))
        except Crash:
            pass
        else:
            raise AssertionError("the crash did not stop the run")
        store = root / "e40" / "responses.jsonl"
        assert [json.loads(x)["custom_id"] for x in store.read_text().splitlines()] == ["d0", "d1", "d2"]
        assert not (root / "e40" / "run.open.json").exists(), "an ordinary crash left the open step"
        assert abs(spent(root, D, "run")[0] - (3 * CHAT_COST + oc.worst(DI, reqs[3]))) < 1e-4, \
            "the call that crashed can have run, so its worst case stays in the ledger"
        with open(store, "a") as fh:
            fh.write('{"custom_id": "d3", "sta')  # a line that a hard stop cut
        oc.WORKERS = 4
        second = oc.send = Fake(always(200, CHAT), D)
        operator(lambda approve: oc.run("e40", reqs, 2000, approve, D, DI))
        assert ids_of(second.calls, reqs) == ["d3", "d4", "d5"]
        raw = [json.loads(x) for x in (root / "e40" / "raw.jsonl").read_text().splitlines()]
        assert [(x["custom_id"], x["type"]) for x in raw] == [(f"d{i}", "succeeded") for i in range(6)]
        assert abs(spent(root, D, "run")[1] - 3 * CHAT_COST) < 1e-4
        oc.send = no_network
        oc.run("e40", reqs, 2000, None, D, DI)
        assert len(spent(root, D, "run")) == 2, "a run with nothing to send wrote a ledger row"


def test_retries_keep_possible_cost():
    with sandbox() as root:
        reqs = chat_reqs(3)
        plan = {"d0": [429, 200], "d1": [503, 200], "d2": ["timeout", 200]}
        by_body = {json.dumps(r["body"]).encode(): r["custom_id"] for r in reqs}

        def answer(method, url, data):
            status = plan[by_body[data]].pop(0)
            if status == "timeout":
                raise oc.NoAnswer("TimeoutError")
            return status, json.dumps(CHAT if status == 200 else {"error": "busy"}).encode()

        fake = oc.send = Fake(answer, D)
        operator(lambda approve: oc.run("e41", reqs, 2000, approve, D, DI))
        assert len(fake.calls) == 6
        stored = [json.loads(x) for x in (root / "e41" / "responses.jsonl").read_text().splitlines()]
        assert sorted((x["custom_id"], x["status"]) for x in stored) == [("d0", 200), ("d1", 200), ("d2", 200)]
        expected = 3 * CHAT_COST + oc.worst(DI, reqs[1]) + oc.worst(DI, reqs[2])  # HTTP 503 and the timeout
        assert abs(spent(root, D, "run")[0] - expected) < 1e-4, (spent(root, D, "run"), expected)


def test_bound_stops_run():
    with sandbox() as root:
        reqs = chat_reqs(3)
        fake = oc.send = Fake(always(503, {"error": "down"}), D)
        operator(lambda approve: oc.run("e44", reqs, 100, approve, D, DI))
        bound = float(rows(root / D.ledger)[0]["bound_usd"])
        assert spent(root, D, "run")[0] <= bound / accounts.TAX + 1e-4
        assert len(fake.calls) < len(reqs) * oc.ATTEMPTS, "the run did not stop at its bound"
        assert not (root / "e44" / "responses.jsonl").exists(), "an HTTP 5xx answer was stored as final"


def test_fatal_status_stops():
    with sandbox() as root:
        fake = oc.send = Fake(always(401, {"error": "bad key"}), D)
        try:
            operator(lambda approve: oc.pilot("e42", chat_reqs(4), approve, D, DI))
        except RuntimeError as e:
            assert "HTTP 401" in str(e) and KEY not in str(e), e
        else:
            raise AssertionError("HTTP 401 did not stop the pilot")
        assert len(fake.calls) == 1
        assert not (root / "e42" / "pilot_responses.jsonl").exists()
        assert spent(root, D, "pilot") == [0.0] and not (root / "e42" / "pilot.open.json").exists()


def test_openai_batch_submit_and_fetch():
    with sandbox() as root:
        reqs = resp_reqs(3)

        def create(method, url, data):
            body = {"id": "file-in", "object": "file"} if url.endswith("/files") else {"id": "batch_1", "status": "validating"}
            return 200, json.dumps(body).encode()

        fake = oc.send = Fake(create, O)
        operator(lambda approve: oc.submit("e43", reqs, 100, approve, O, OA))
        assert [(m, u) for m, u, _ in fake.calls] == [("POST", f"{oc.OPENAI}/files"), ("POST", f"{oc.OPENAI}/batches")]
        assert b'name="purpose"\r\n\r\nbatch\r\n' in fake.calls[0][2]
        assert json.loads(fake.calls[1][2]) == {"input_file_id": "file-in", "endpoint": "/v1/responses",
                                                "completion_window": "24h", "metadata": {"experiment": "e43"}}
        lines = [json.loads(x) for x in (root / "e43" / "requests.jsonl").read_text().splitlines()]
        assert [(x["custom_id"], x["method"], x["url"]) for x in lines] == [(f"o{i}", "POST", "/v1/responses") for i in range(3)]
        info = json.loads((root / "e43" / "batch.json").read_text())
        assert (info["id"], info["account"]) == ("batch_1", "openai_r9") and not (root / "e43" / "submit.open.json").exists()
        assert accounts.committed(O) == info["bound"] and accounts.committed(accounts.ACCOUNTS["anthropic_old"]) == 0

        oc.send = Fake(always(200, {"id": "batch_1", "status": "in_progress"}), O)
        assert refused(oc.fetch, "e43", O, OA).startswith("e43: in_progress")
        assert not (root / "e43" / "raw.jsonl").exists() and not accounts.has_row(O, "e43", "batch")

        cut = dict(RESPONSE, status="incomplete", incomplete_details={"reason": "max_output_tokens"})
        out = "".join(json.dumps({"id": f"batch_req_{i}", "custom_id": f"o{i}", "error": None,
                                  "response": {"status_code": 200, "request_id": f"req_{i}", "body": body}}) + "\n"
                      for i, body in ((1, cut), (0, RESPONSE))).encode()
        err = (json.dumps({"id": "batch_req_2", "custom_id": "o2", "response": None,
                           "error": {"code": "batch_expired", "message": "expired"}}) + "\n").encode()
        files = {f"{oc.OPENAI}/batches/batch_1": json.dumps({"id": "batch_1", "status": "completed",
                                                             "output_file_id": "file-out", "error_file_id": "file-err"}).encode(),
                 f"{oc.OPENAI}/files/file-out/content": out, f"{oc.OPENAI}/files/file-err/content": err}
        oc.send = Fake(lambda method, url, data: (200, files[url]), O)
        oc.fetch("e43", O, OA)
        assert (root / "e43" / "batch_output.jsonl").read_bytes() == out, "the output file is not stored verbatim"
        raw = [json.loads(x) for x in (root / "e43" / "raw.jsonl").read_text().splitlines()]
        assert [(x["custom_id"], x["type"], x.get("stop")) for x in raw] == [
            ("o0", "succeeded", "end_turn"), ("o1", "succeeded", "max_tokens"), ("o2", "errored", None)]
        assert abs(spent(root, O, "batch")[0] - 2 * 0.006005) < 1e-4, "cost at batch prices of the requested model"
        assert abs(accounts.committed(O) - 2 * 0.006005) < 1e-4, "the fetched cost did not replace the bound"
        oc.send = no_network
        oc.fetch("e43", O, OA)
        assert len(spent(root, O, "batch")) == 1, "a second fetch wrote a second ledger row"


def test_account_is_explicit():
    for main in (anth.main, oc.main):
        p = inspect.signature(main).parameters["account"]
        assert p.kind is p.KEYWORD_ONLY and p.default is p.empty, main.__module__
    for name, providers in ((None, ("anthropic",)), ("openai_r9", ("anthropic",)), ("anthropic_old", tuple(oc.APIS))):
        assert refused(accounts.account, name, providers).startswith("Not run. Name the account explicitly")
    try:
        oc.check_requests(resp_reqs(1), DI)
    except AssertionError as e:
        assert "not served" in str(e)
    else:
        raise AssertionError("OpenAI requests passed the check of the DeepInfra account")


def test_openai_batch_one_model():
    with sandbox(env=False) as root:
        reqs = resp_reqs(2) + [oc.openai_request("o9", "gpt-6-luna", "none", 2000, "question 9 " * 20, "Answer in JSON.", SCHEMA)]
        text = refused(oc.submit, "e93", reqs, 100, "9.99", O, OA)
        assert text.startswith("Not run. An OpenAI batch takes one model"), text
        assert not list(root.rglob("*")), "a refused batch wrote a file"


def test_macos_metadata_files_ignored():
    with sandbox(env=False) as root:
        (root / "e60").mkdir()
        (root / "e60" / "pilot.open.json").write_text(json.dumps({"account": "openai_r9", "step": "pilot", "bound": 2.5}))
        (root / "e60" / "._pilot.open.json").write_bytes(b"\x00\x05\x16\x07\x00\x02\x00\x00Mac OS X        \xb0\xff")
        assert accounts.committed(O) == 2.5, "a ._ metadata file changed or broke the committed money"


TESTS = [test_openai_batch_one_model, test_macos_metadata_files_ignored, test_cost_from_recorded_usage, test_approval_mismatch_refused, test_limit_refused, test_ledgers_apart,
         test_old_account_unchanged, test_anthropic_accounts_apart, test_resume_skips_answered, test_retries_keep_possible_cost, test_bound_stops_run,
         test_fatal_status_stops, test_openai_batch_submit_and_fetch, test_account_is_explicit]


def main():
    out = io.StringIO()
    for test in TESTS:
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                test()
        except BaseException:
            print(out.getvalue())
            raise
        print(f"ok  {test.__name__}")
    assert KEY not in out.getvalue(), "a key reached the output"
    print("client test passed: guard, separate ledgers, old account, resume, retries, batch flow; no network call")


if __name__ == "__main__":
    main()
