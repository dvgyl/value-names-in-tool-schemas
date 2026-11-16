"""Gemini client test (openai_compat.py, provider "google"), with a fake transport. It makes no network call.

1. gemini_request() and natural.request("gemini") give the generateContent body; the batch line has no `model`.
2. A response with the fields of the generateContent reference decodes to the shared row fields, at list prices.
3. With the limit 0.00 USD every paid step refuses; a wrong --approve value refuses; neither writes a file.
4. A paid step stops 2 days before the 2026 Gemini prices end.
5. A batch goes through upload, create, and fetch. A second fetch makes no call and writes no second ledger row.
6. An upload URL outside the Gemini API host gets no key and no bytes.
7. A sealed batch and a sealed pilot leave no planted marker on disk or in the output; a pilot rerun sends only the
   requests without a stored answer.

The token counts are test values. The field names come from the generateContent and Batch API pages (read 2026-11-04).
Usage: python3 -I test_gemini.py
"""
import contextlib
import datetime
import io
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "r9" / "natural"))
import test_seal as ts  # noqa: E402  (it imports test_clients, which installs the fake transports)
import test_clients as tc  # noqa: E402
import accounts  # noqa: E402
import openai_compat as oc  # noqa: E402

G = accounts.ACCOUNTS["google"]
G50 = G._replace(limit=50.00)  # a paid test needs a limit above 0.00 USD
GA = oc.APIS["google"]
MODEL = "gemini-3.8-flash"
SCHEMA = tc.SCHEMA
RESPONSE = {"candidates": [{"content": {"role": "model", "parts": [{"text": "a thought", "thought": True},
                                                                   {"text": "{\"a\": 1}"}]},
                            "finishReason": "STOP", "index": 0}],
            "usageMetadata": {"promptTokenCount": 1000, "candidatesTokenCount": 200, "thoughtsTokenCount": 300,
                              "totalTokenCount": 1500},
            "modelVersion": MODEL, "responseId": "resp-1"}
COST = 0.002625  # (1000 x 0.75 + (200 + 300) x 3.75) / 1e6, standard price
UPLOAD_URL = f"{oc.GEMINI_UPLOAD}?upload_id=u1&upload_protocol=resumable"
OUT = io.StringIO()


def gem_reqs(n):
    return [oc.gemini_request(f"g{i}", MODEL, 4000, f"question {i} " * 20, "Answer in JSON.", SCHEMA) for i in range(n)]


class GFake:
    """A recorded Gemini transport. `answer(method, url, data, headers)` returns (status, headers, bytes) or raises."""

    def __init__(self, answer, account=G):
        self.answer, self.key, self.calls = answer, f"{tc.KEY}-{account.name}", []

    def __call__(self, method, url, key, data=None, headers=None):
        assert key == self.key, "the step sent the key of another account"
        self.calls.append((method, url, data, headers or {}))
        return self.answer(method, url, data, headers or {})


def sent_ids(calls):
    """The custom_id of each generateContent call, from the question number in its user text."""
    return [f"g{json.loads(data)['contents'][0]['parts'][0]['text'].split()[1]}" for _, _, data, _ in calls]


@contextlib.contextmanager
def gemini_transport():
    saved = oc.google_send
    oc.google_send = tc.no_network
    try:
        yield
    finally:
        oc.google_send = saved


def batch_server(output, state="BATCH_STATE_SUCCEEDED"):
    """A fake Gemini batch API: the resumable upload, the batch create, the batch get, and the file download."""
    def answer(method, url, data, headers):
        if url == oc.GEMINI_UPLOAD:
            return 200, {"x-goog-upload-url": UPLOAD_URL}, b""
        if url == UPLOAD_URL:
            return 200, {}, json.dumps({"file": {"name": "files/in1", "uri": "https://x/files/in1"}}).encode()
        if url.endswith(":batchGenerateContent"):
            return 200, {}, json.dumps({"name": "batches/b1", "metadata": {"state": "BATCH_STATE_PENDING"}}).encode()
        if url == f"{oc.GEMINI}/batches/b1":
            return 200, {}, json.dumps({"name": "batches/b1", "metadata": {"state": state, "batchStats": {"requestCount": "3"}},
                                        "response": {"responsesFile": "files/out1"}}).encode()
        if url == f"{oc.GEMINI_DOWNLOAD}/files/out1:download?alt=media":
            return 200, {}, output
        raise AssertionError(f"unexpected {method} {url}")
    return answer


def output_lines(response):
    """g1 first: the output order need not be the input order. g2 is an error line."""
    cut = dict(response, candidates=[dict(response["candidates"][0], finishReason="MAX_TOKENS")])
    return "".join(json.dumps(x) + "\n" for x in (
        {"key": "g1", "response": cut}, {"key": "g0", "response": response},
        {"key": "g2", "error": {"code": 500, "message": "internal", "status": "INTERNAL"}})).encode()


def test_request_shape():
    import natural
    r = oc.gemini_request("g0", MODEL, 4000, "the dialogue", "the prompt", SCHEMA)
    assert r == {"custom_id": "g0", "body": {
        "model": MODEL, "contents": [{"role": "user", "parts": [{"text": "the dialogue"}]}],
        "generationConfig": {"maxOutputTokens": 4000, "thinkingConfig": {"thinkingLevel": "LOW"},
                             "responseMimeType": "application/json", "responseJsonSchema": SCHEMA},
        "systemInstruction": {"parts": [{"text": "the prompt"}]}}}, r
    assert oc.wire(r["body"]) == {k: v for k, v in r["body"].items() if k != "model"} and "model" in r["body"]
    plain = oc.gemini_request("g1", MODEL, 100, "u")["body"]
    assert "systemInstruction" not in plain and "responseJsonSchema" not in plain["generationConfig"]
    fmt = {"type": "json_schema", "schema": SCHEMA}
    assert natural.request("gemini", "g0", "the dialogue", "the prompt", fmt) == r
    assert natural.MODELS["gemini"].provider == G.provider and natural.MODELS["gemini"].id in GA.prices
    assert oc.cell(r) == (MODEL, "LOW") and GA.cap(r["body"]) == 4000
    assert oc.est_in(r) == oc.est_in(oc.deepinfra_request("d0", "Qwen/Qwen3.8-27B", 1, "the dialogue", "the prompt"))
    oc.check_requests(gem_reqs(2), GA)
    try:
        oc.check_requests(gem_reqs(1), tc.DI)
    except AssertionError as e:
        assert "not served" in str(e)
    else:
        raise AssertionError("Gemini requests passed the check of the DeepInfra account")


def test_decode_and_cost():
    r = GA.decode(RESPONSE)
    assert r == {"model": MODEL, "stop": "end_turn", "provider_stop": "STOP", "input_tokens": 1000,
                 "output_tokens": 500, "reasoning_tokens": 300, "text": '{"a": 1}'}, r
    assert abs(oc.cost(GA, MODEL, 1000, 500, batch=False) - COST) < 1e-12
    assert abs(oc.cost(GA, MODEL, 1000, 500, batch=True) - COST / 2) < 1e-12
    finish = lambda reason: dict(RESPONSE, candidates=[dict(RESPONSE["candidates"][0], finishReason=reason)])
    blocked = {"promptFeedback": {"blockReason": "SAFETY"}, "usageMetadata": {"promptTokenCount": 9, "totalTokenCount": 9}}
    stops = [GA.decode(x)["stop"] for x in (finish("MAX_TOKENS"), finish("SAFETY"), blocked, finish("RECITATION"))]
    assert stops == ["max_tokens", "refusal", "refusal", "finish:RECITATION"], stops
    assert GA.decode(blocked)["output_tokens"] == 0 and GA.decode(blocked)["text"] == ""


def test_approval_refused():
    with tc.sandbox(env=False) as root, gemini_transport():
        assert G.limit == 0.0 and G.cash and G.key == "GEMINI_API_KEY" and G.ledger == "ledger_google.csv"
        for step, args in ((oc.pilot, ("e30", gem_reqs(3), "0.01", G, GA)),
                           (oc.google_submit, ("e30", gem_reqs(3), 100, "0.01", G, GA))):
            assert tc.refused(step, *args).endswith("would pass the 0.00 USD limit."), step.__name__
        for step, args in ((oc.pilot, ("e31", gem_reqs(3), "9.99", G50, GA)),
                           (oc.google_submit, ("e31", gem_reqs(3), 100, None, G50, GA))):
            assert tc.refused(step, *args).startswith("Not run. Rerun with --approve "), step.__name__
        assert not list(root.rglob("*")), "a refused step wrote a file"


def test_prices_end():
    oc.check_prices(GA, datetime.date(2026, 12, 29))
    oc.check_prices(tc.DI, datetime.date(2030, 1, 1))
    for day in (datetime.date(2026, 12, 30), datetime.date(2027, 1, 2)):
        assert tc.refused(oc.check_prices, GA, day).startswith("Not run. The prices in APIS end on 2026-12-31.")


def test_batch_submit_and_fetch():
    with tc.sandbox() as root, gemini_transport():
        reqs = gem_reqs(3)
        fake = oc.google_send = GFake(batch_server(output_lines(RESPONSE), "BATCH_STATE_RUNNING"))
        tc.operator(lambda approve: oc.google_submit("e32", reqs, 500, approve, G50, GA))
        assert [u for _, u, _, _ in fake.calls] == [oc.GEMINI_UPLOAD, UPLOAD_URL,
                                                    f"{oc.GEMINI}/models/{MODEL}:batchGenerateContent"]
        assert fake.calls[0][3]["X-Goog-Upload-Command"] == "start" and fake.calls[1][3]["X-Goog-Upload-Command"] == "upload, finalize"
        lines = [json.loads(x) for x in (root / "e32" / "requests.jsonl").read_text().splitlines()]
        assert lines == [{"key": r["custom_id"], "request": oc.wire(r["body"])} for r in reqs]
        assert fake.calls[1][2] == (root / "e32" / "requests.jsonl").read_bytes(), "the uploaded bytes differ from the file"
        assert json.loads(fake.calls[2][2]) == {"batch": {"display_name": "e32", "input_config": {"file_name": "files/in1"}}}
        info = json.loads((root / "e32" / "batch.json").read_text())
        assert (info["id"], info["account"], info["model"]) == ("batches/b1", "google", MODEL)
        assert accounts.committed(G50) == info["bound"] and not (root / "e32" / "submit.open.json").exists()
        assert tc.refused(oc.google_submit, "e32", reqs, 500, str(info["bound"]), G50, GA).startswith("e32 already has a batch")

        assert tc.refused(oc.google_fetch, "e32", G50, GA).startswith("e32: BATCH_STATE_RUNNING")
        assert not (root / "e32" / "raw.jsonl").exists() and not accounts.has_row(G50, "e32", "batch")
        oc.google_send = GFake(batch_server(output_lines(RESPONSE)))
        oc.google_fetch("e32", G50, GA)
        raw = [json.loads(x) for x in (root / "e32" / "raw.jsonl").read_text().splitlines()]
        assert [(x["custom_id"], x["type"], x.get("stop")) for x in raw] == [
            ("g0", "succeeded", "end_turn"), ("g1", "succeeded", "max_tokens"), ("g2", "errored", None)], raw
        assert abs(tc.spent(root, G50, "batch")[0] - COST) < 1e-4, "2 answers at half the standard price"
        assert abs(accounts.committed(G50) - COST * accounts.TAX) < 1e-4, "the fetched cost did not replace the bound"
        oc.google_send = tc.no_network
        oc.google_fetch("e32", G50, GA)
        assert len(tc.spent(root, G50, "batch")) == 1, "a second fetch wrote a second ledger row"


def test_foreign_upload_url_refused():
    with tc.sandbox() as root, gemini_transport():
        def answer(method, url, data, headers):
            if url == oc.GEMINI_UPLOAD:
                return 200, {"x-goog-upload-url": "https://upload.example.com/u1"}, b""
            raise AssertionError(f"the step called {url}")
        fake = oc.google_send = GFake(answer)
        text = tc.refused(lambda: tc.operator(lambda approve: oc.google_submit("e33", gem_reqs(2), 500, approve, G50, GA)))
        assert text.startswith("e33: upload not started") and len(fake.calls) == 1, text
        assert not (root / "e33" / "batch.json").exists() and not (root / "e33" / "submit.open.json").exists()


def marked():
    resp = json.loads(json.dumps(RESPONSE))
    resp["candidates"][0]["content"]["parts"][1]["text"] = ts.ANSWER
    return resp


def test_sealed_batch_leaves_no_marker():
    with ts.keyed_sandbox() as (root, private), gemini_transport():
        reqs = gem_reqs(3)
        oc.google_send = GFake(batch_server(output_lines(marked())))
        tc.operator(lambda approve: oc.google_submit("em11", reqs, 500, approve, G50, GA))
        oc.google_fetch("em11", G50, GA)
        folder = root / "em11"
        assert not (folder / "batch_output.jsonl").exists(), "a plain batch output file exists"
        raw = [json.loads(x) for x in (folder / "raw.jsonl").read_text().splitlines()]
        assert [(x["custom_id"], x.get("json_ok")) for x in raw] == [("g0", True), ("g1", True), ("g2", None)]
        assert all("text" not in x for x in raw) and raw[0]["output_tokens"] == 500
        oc.google_send = tc.no_network
        assert tc.refused(oc.google_fetch, "em11", G50, GA).startswith("em11: already fetched and sealed")
        plain = ts.opened(root, "em11", private)
        assert json.loads((plain / "raw.jsonl").read_text().splitlines()[0])["text"] == ts.ANSWER
        assert ts.MARKER.encode() in (plain / "batch_output.jsonl").read_bytes()
        (plain / "raw.jsonl").unlink(), (plain / "batch_output.jsonl").unlink()


def test_sealed_pilot_resume():
    with ts.keyed_sandbox() as (root, private), gemini_transport():
        reqs, ok = gem_reqs(5), (200, {}, json.dumps(marked()).encode())

        def crash_on_third(method, url, data, headers):
            assert url == f"{oc.GEMINI}/models/{MODEL}:generateContent" and "model" not in json.loads(data)
            if len(first.calls) == 3:
                raise tc.Crash
            return ok

        first = oc.google_send = GFake(crash_on_third)
        try:
            tc.operator(lambda approve: oc.pilot("em12", reqs, approve, G50, GA))
        except tc.Crash:
            pass
        else:
            raise AssertionError("the crash did not stop the pilot")
        stored = {json.loads(x)["custom_id"] for x in (root / "em12" / "pilot_responses.jsonl").read_text().splitlines()}
        assert stored == set(sent_ids(first.calls[:2])), stored
        second = oc.google_send = GFake(lambda method, url, data, headers: ok)
        tc.operator(lambda approve: oc.pilot("em12", reqs, approve, G50, GA))
        assert sorted(sent_ids(second.calls)) == sorted({r["custom_id"] for r in reqs} - stored), "a stored answer was sent again"
        lines = [json.loads(x) for x in (root / "em12" / "pilot_responses.jsonl").read_text().splitlines()]
        assert len(lines) == 5 and all(set(x) == {"custom_id", "public", "sealed"} for x in lines)
        plain = ts.opened(root, "em12", private)
        assert ts.MARKER in (plain / "pilot_responses.jsonl").read_text()
        (plain / "pilot_responses.jsonl").unlink()


TESTS = [test_request_shape, test_decode_and_cost, test_approval_refused, test_prices_end, test_batch_submit_and_fetch,
         test_foreign_upload_url_refused, test_sealed_batch_leaves_no_marker, test_sealed_pilot_resume]


def main():
    for test in TESTS:
        try:
            with contextlib.redirect_stdout(OUT), contextlib.redirect_stderr(OUT):
                test()
        except BaseException:
            print(OUT.getvalue())
            raise
        print(f"ok  {test.__name__}")
    assert tc.KEY not in OUT.getvalue(), "a key reached the output"
    assert ts.MARKER not in OUT.getvalue(), "the marker reached the printed output"
    print("gemini test passed: request shape, decode, cost, guard, batch flow, sealing, resume; no network call")


if __name__ == "__main__":
    main()
