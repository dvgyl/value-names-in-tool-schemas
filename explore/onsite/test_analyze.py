"""Offline test of onsite/analyze.py on a synthetic raw.jsonl. No API call.

Read 1 of claude-sonnet-5-5 replays the P3 replies (arm orig is the P1 Sonnet reply, as in P3), so the expected counts
come from the P1 and P3 summaries, which other code computed. Read 2 holds one row of each missing kind.
Run:  harness/.venv/bin/python onsite/test_analyze.py
"""
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PROTOTYPES = HERE.parents[1]
SONNET, HAIKU = "claude-sonnet-5-5", "claude-haiku-5-5"


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def synthetic_rows():
    p1 = {r["case_id"]: r["text"] for r in jsonl(PROTOTYPES / "p1_saturation" / "raw.jsonl") if r["model"] == "sonnet"}
    p3 = {(r["case_id"], r["arm"]): r["text"] for r in jsonl(PROTOTYPES / "p3_schema" / "raw.jsonl")}
    cases = sorted({c for c, _ in p3})
    ok = {"type": "succeeded", "model": SONNET, "stop": "end_turn", "input_tokens": 1000, "output_tokens": 200}
    rows = []
    for c in cases:
        for arm, text in (("orig", p1[c]), ("office", p3[(c, "B")]), ("renamed", p3[(c, "C")])):
            rows.append({"custom_id": f"sonnet_{arm}_r1_{c}", **ok, "text": text})
    late = {"type": "succeeded", "model": SONNET, "input_tokens": 2000, "output_tokens": 4096}
    rows += [{"custom_id": f"sonnet_orig_r2_{cases[0]}", "type": "errored"},
             {"custom_id": f"sonnet_orig_r2_{cases[1]}", **late, "stop": "refusal", "text": ""},
             {"custom_id": f"sonnet_orig_r2_{cases[2]}", **late, "stop": "max_tokens", "text": '{"ranking": ['},
             {"custom_id": f"sonnet_orig_r2_{cases[3]}", **late, "stop": "end_turn", "text": "no JSON here"}]
    return rows


def main():
    with tempfile.TemporaryDirectory() as tmp:
        raw, out = pathlib.Path(tmp) / "raw.jsonl", pathlib.Path(tmp) / "summary.json"
        raw.write_text("".join(json.dumps(r) + "\n" for r in synthetic_rows()))
        subprocess.run([sys.executable, str(HERE / "analyze.py"), "--raw", str(raw), "--out", str(out)], check=True)
        s = json.loads(out.read_text())

    p3 = json.loads((PROTOTYPES / "p3_schema" / "summary.json").read_text())
    sonnet = s["models"][SONNET]
    for arm, p3_arm in (("orig", "A"), ("office", "B"), ("renamed", "C")):
        r1 = sonnet[arm]["per_read"]["1"]
        assert (r1["wrong"], r1["flip"]) == (p3[p3_arm]["wrong"], p3[p3_arm]["flip"]), (arm, r1)
        assert r1["parse_fail"] == 0 and r1["crash"] == 0 and r1["absent"] == 0, (arm, r1)
    assert sonnet["orig"]["per_read"]["1"]["flip_p1"] == 8, "P1 summary: 8 of the 12 on-site wrong items are sdfr hits"

    r2 = sonnet["orig"]["per_read"]["2"]
    assert (r2["error"], r2["refusal"], r2["truncated"], r2["parse_fail"], r2["absent"]) == (1, 1, 1, 1, 34), r2
    assert sonnet["orig"]["pooled"]["wrong"] == 12 and sonnet["orig"]["pooled"]["absent"] == 34 + 3 * 38
    assert sonnet["orig"]["tokens"]["n"] == 41
    assert abs(sonnet["orig"]["tokens"]["input_mean"] - (38 * 1000 + 3 * 2000) / 41) < 1e-9

    m = s["mcnemar_read1"][SONNET]["orig_vs_office"]
    assert m["wrong"] == {"pairs": 38, "orig_only": 12, "other_only": 0, "p_exact": 2 / 2 ** 12}, m
    assert m["flip"] == {"pairs": 38, "orig_only": 8, "other_only": 0, "p_exact": 2 / 2 ** 8}, m
    assert s["mcnemar_read1"][HAIKU]["orig_vs_renamed"]["wrong"] == {"pairs": 0, "orig_only": 0, "other_only": 0, "p_exact": 1.0}
    assert s["models"][HAIKU]["orig"]["pooled"]["absent"] == 5 * 38
    assert s["rows"] == 118 and s["expected_rows"] == 1710
    print("onsite/test_analyze.py: PASS (P3 counts reproduced, missing kinds counted, McNemar p-values exact)")


if __name__ == "__main__":
    main()
