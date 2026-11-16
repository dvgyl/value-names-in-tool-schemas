"""Planted-marker audit of the sealed collection (REVISION-12.md section 3). Fake transports, no network call.

Every fake answer holds a marker string. After each collection path (Anthropic batch fetch, OpenAI batch fetch,
OpenAI pilot, DeepInfra synchronous run with a crash and a resume), no file and no printed line may hold the marker.
The operator's private key must open every sealed file and give back the marker. A run that is not sealed keeps its
plain files, and a sealed run without the public key does not start.

Usage: python3 -I test_seal.py
"""
import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import types

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_clients as tc  # noqa: E402  (it installs the fake transports)
import accounts  # noqa: E402
import anth  # noqa: E402
import openai_compat as oc  # noqa: E402
import seal  # noqa: E402
import unseal  # noqa: E402

MARKER = "MARKER-Q7Z2-planted"
ANSWER = json.dumps({"a": 1, "m": MARKER})
RESPONSE = json.loads(json.dumps(tc.RESPONSE))
RESPONSE["output"][1]["content"][0]["text"] = ANSWER
CHAT = json.loads(json.dumps(tc.CHAT))
CHAT["choices"][0]["message"]["content"] = ANSWER
OUT = io.StringIO()


@contextlib.contextmanager
def keyed_sandbox():
    """tc.sandbox with an operator key pair: the public key inside, the private key in another folder."""
    with tc.sandbox() as root, tempfile.TemporaryDirectory() as keydir:
        private = pathlib.Path(keydir) / "private.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out",
                        str(private)], check=True, capture_output=True)
        (root / "main").mkdir()
        subprocess.run(["openssl", "pkey", "-in", str(private), "-pubout", "-out", str(root / "main" / "seal_public.pem")],
                       check=True, capture_output=True)
        yield root, private
        hits = [p for p in root.parent.rglob("*") if p.is_file() and MARKER.encode() in p.read_bytes()]
        assert not hits, f"the marker is in plain text in {hits}"


def opened(root, name, private):
    out = root.parent / "opened" / name
    unseal.main(private, root / name, out)
    return out


def test_openai_batch_sealed():
    with keyed_sandbox() as (root, private):
        reqs = tc.resp_reqs(3)
        tc.operator(lambda approve: (setattr(oc, "send", tc.Fake(tc.always(200, {"id": "x", "status": "validating"}), tc.O)),
                                     oc.submit("em01", reqs, 100, approve, tc.O, tc.OA)))
        out = "".join(json.dumps({"custom_id": f"o{i}", "response": {"status_code": 200, "body": RESPONSE}}) + "\n"
                      for i in range(2)).encode()
        err = (json.dumps({"custom_id": "o2", "response": None, "error": {"code": "batch_expired"}}) + "\n").encode()
        files = {f"{oc.OPENAI}/batches/x": json.dumps({"id": "x", "status": "completed", "output_file_id": "fo",
                                                       "error_file_id": "fe"}).encode(),
                 f"{oc.OPENAI}/files/fo/content": out, f"{oc.OPENAI}/files/fe/content": err}
        oc.send = tc.Fake(lambda method, url, data: (200, files[url]), tc.O)
        oc.fetch("em01", tc.O, tc.OA)
        folder = root / "em01"
        assert not (folder / "batch_output.jsonl").exists(), "a plain batch output file exists"
        raw = [json.loads(x) for x in (folder / "raw.jsonl").read_text().splitlines()]
        assert [(x["custom_id"], x["type"], x.get("json_ok")) for x in raw] == [
            ("o0", "succeeded", True), ("o1", "succeeded", True), ("o2", "errored", None)]
        assert all("text" not in x for x in raw) and raw[0]["output_tokens"] == 1186
        assert tc.spent(root, tc.O, "batch"), "no ledger row"
        oc.send = tc.no_network
        assert tc.refused(oc.fetch, "em01", tc.O, tc.OA).startswith("em01: already fetched and sealed")
        plain = opened(root, "em01", private)
        assert (plain / "batch_output.jsonl").read_bytes() == out, "the sealed output file is not verbatim"
        full = [json.loads(x) for x in (plain / "raw.jsonl").read_text().splitlines()]
        assert full[0]["text"] == ANSWER
        (plain / "raw.jsonl").unlink(), (plain / "batch_output.jsonl").unlink()


def test_deepinfra_run_sealed_with_resume():
    with keyed_sandbox() as (root, private):
        reqs = tc.chat_reqs(5)
        first = []

        def crash_on_third(method, url, data):
            if len(first[0].calls) == 3:
                raise tc.Crash
            return 200, json.dumps(CHAT).encode()

        first.append(tc.Fake(crash_on_third, tc.D))
        oc.send = first[0]
        try:
            tc.operator(lambda approve: oc.run("em02", reqs, 2000, approve, tc.D, tc.DI))
        except tc.Crash:
            pass
        second = oc.send = tc.Fake(tc.always(200, CHAT), tc.D)
        tc.operator(lambda approve: oc.run("em02", reqs, 2000, approve, tc.D, tc.DI))
        assert tc.ids_of(second.calls, reqs) == ["d2", "d3", "d4"], "the resume sent stored requests again"
        raw = [json.loads(x) for x in (root / "em02" / "raw.jsonl").read_text().splitlines()]
        assert [(x["custom_id"], x["json_ok"]) for x in raw] == [(f"d{i}", True) for i in range(5)]
        lines = [json.loads(x) for x in (root / "em02" / "responses.jsonl").read_text().splitlines()]
        assert all(set(x) == {"custom_id", "public", "sealed"} for x in lines)
        plain = opened(root, "em02", private)
        recs = [json.loads(x) for x in (plain / "responses.jsonl").read_text().splitlines()]
        assert all(MARKER in r["body"] and r["status"] == 200 for r in recs) and len(recs) == 5
        (plain / "responses.jsonl").unlink()


def test_openai_pilot_sealed():
    with keyed_sandbox() as (root, private):
        oc.send = tc.Fake(tc.always(200, RESPONSE), tc.O)
        tc.operator(lambda approve: oc.pilot("em03", tc.resp_reqs(4), approve, tc.O, tc.OA))
        pilot = json.loads(anth.pilot_path("em03").read_text())
        assert next(iter(pilot.values()))["n"] == 4, "the pilot summary lost its usage rows"
        plain = opened(root, "em03", private)
        assert MARKER in (plain / "pilot_responses.jsonl").read_text()
        (plain / "pilot_responses.jsonl").unlink()


class FakeBatches:
    def retrieve(self, batch_id):
        return types.SimpleNamespace(processing_status="ended", request_counts={})

    def results(self, batch_id):
        msg = types.SimpleNamespace(model="claude-haiku-5-5", stop_reason="end_turn",
                                    usage=types.SimpleNamespace(input_tokens=100, output_tokens=20),
                                    content=[types.SimpleNamespace(type="text", text=ANSWER)])
        yield types.SimpleNamespace(custom_id="c0", result=types.SimpleNamespace(type="succeeded", message=msg))
        yield types.SimpleNamespace(custom_id="c1", result=types.SimpleNamespace(type="errored"))


def test_anthropic_fetch_sealed():
    a = accounts.ACCOUNTS["anthropic_r9a"]
    fake = sys.modules["anthropic"]
    saved = fake.Anthropic
    fake.Anthropic = lambda api_key, max_retries: types.SimpleNamespace(messages=types.SimpleNamespace(batches=FakeBatches()))
    try:
        with keyed_sandbox() as (root, private):
            (root / "em04").mkdir()
            (root / "em04" / "batch.json").write_text(json.dumps({"id": "b1", "bound": 1.0, "account": a.name}))
            anth.fetch("em04", a)
            raw = [json.loads(x) for x in (root / "em04" / "raw.jsonl").read_text().splitlines()]
            assert [(x["custom_id"], x["type"], x.get("json_ok")) for x in raw] == [("c0", "succeeded", True), ("c1", "errored", None)]
            plain = opened(root, "em04", private)
            assert json.loads((plain / "raw.jsonl").read_text().splitlines()[0])["text"] == ANSWER
            (plain / "raw.jsonl").unlink()
    finally:
        fake.Anthropic = saved


def test_unsealed_run_unchanged_and_no_key_refused():
    with tc.sandbox() as root:
        oc.send = tc.Fake(tc.always(200, CHAT), tc.D)
        tc.operator(lambda approve: oc.run("e70", tc.chat_reqs(2), 2000, approve, tc.D, tc.DI))
        assert MARKER in (root / "e70" / "raw.jsonl").read_text(), "an exploratory run lost its plain answers"
        (root / "e70" / "raw.jsonl").unlink(), (root / "e70" / "responses.jsonl").unlink()
        assert "seal_public.pem is missing" in tc.refused(oc.run, "em05", tc.chat_reqs(2), 2000, None, tc.D, tc.DI)


TESTS = [test_openai_batch_sealed, test_deepinfra_run_sealed_with_resume, test_openai_pilot_sealed,
         test_anthropic_fetch_sealed, test_unsealed_run_unchanged_and_no_key_refused]


def main():
    for test in TESTS:
        try:
            with contextlib.redirect_stdout(OUT), contextlib.redirect_stderr(OUT):
                test()
        except BaseException:
            print(OUT.getvalue())
            raise
        print(f"ok  {test.__name__}")
    assert MARKER not in OUT.getvalue(), "the marker reached the printed output"
    print("seal test passed: no plain answer on disk or in the output on any path; the private key opens every file")


if __name__ == "__main__":
    main()
