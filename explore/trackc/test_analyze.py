"""Test analyze.py on a synthetic raw.jsonl in a temporary folder. It makes no API call.

The synthetic replies follow fixed rules, so the expected counts come from the rules and not from analyze.py.
Usage: python3 -I test_analyze.py
"""
import ast
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze  # noqa: E402
import e4  # noqa: E402
import templates as tp  # noqa: E402

MODEL = "claude-haiku-5-5"


def narrow(item):
    """A target value that commits: the narrow reading in condition c, the clear reading elsewhere."""
    return (item.goal.clear[1],) if item.condition == "c" else item.goal.clear


def reply(item, form):
    g = int(item.goal.id[-2:])
    target = item.goal.clear
    if item.kind == "ambiguous":
        target = {"p_main": narrow(item), "p_unclear": "unclear", "p_null": None if g < 20 else narrow(item)}[form]
    elif form == "p_unclear" and g < 10:
        target = "unclear"
    obj = {f: (list(v) if isinstance(v, tuple) else v) for f, v in item.interpretations[0].items()}
    obj[item.target] = list(target) if isinstance(target, tuple) else target
    return json.dumps(obj)


SPECIAL = {  # (goal, form) of condition a, ambiguous item: the reply text and the stop reason
    "xa-g00": ("errored", None, None),
    "xa-g01": ("succeeded", "", "refusal"),
    "xa-g02": ("succeeded", "PARSEABLE", "max_tokens"),
    "xa-g03": ("succeeded", "I cannot tell.", "end_turn"),
    "xa-g04": ("succeeded", "UNCLEAR", "end_turn"),
    "xa-g05": ("succeeded", "WIDE", "end_turn"),
}


def synthetic_rows():
    rows = []
    for cid, item, form, read, model in e4.cells():
        if read != 1 or model != MODEL:
            continue
        text, stop, kind = reply(item, form), "end_turn", "succeeded"
        if item.kind == "ambiguous" and form == "p_main" and item.goal.id in SPECIAL:
            kind, special, stop = SPECIAL[item.goal.id]
            obj = json.loads(text)
            text = {"PARSEABLE": text, "UNCLEAR": json.dumps(obj | {"type": "unclear"}),
                    "WIDE": json.dumps(obj | {"type": ["guesthouse", "hotel"]})}.get(special, special)
        if item.goal.id == "xb-g00" and form == "p_main":
            text = f"Here is the form.\n```json\n{text}\n```"
        row = {"custom_id": cid, "type": kind}
        if kind == "succeeded":
            row |= {"model": MODEL, "stop": stop, "input_tokens": 300,
                    "output_tokens": 4096 if stop == "max_tokens" else 100, "text": text}
        rows.append(row)
    return rows + [{"custom_id": "zz-unknown", "type": "succeeded", "model": MODEL, "stop": "end_turn",
                    "input_tokens": 1, "output_tokens": 1, "text": "{}"}]


def close(a, b):
    return a is not None and abs(a - b) < 1e-9


def check_summary(s):
    assert (s["requests"], s["rows"], s["unknown_rows"], s["absent"]) == (8640, 961, 1, 8640 - 960), \
        (s["requests"], s["rows"], s["unknown_rows"], s["absent"])
    a_main = s["cells"]["a"]["p_main"][MODEL]
    got = {k: a_main[k] for k in analyze.STATUSES}
    want = {"ok": 76, "absent": 160, "error": 1, "refusal": 1, "truncated": 1, "parse_fail": 1}
    assert got == want, f"condition a, p_main statuses {got}, want {want}"
    assert close(a_main["tokens"]["output_mean"], (78 * 100 + 4096) / 79), a_main["tokens"]
    for c in tp.CONDITIONS:
        cells = s["cells"][c]
        main, unclear, null = (cells[f][MODEL] for f in ("p_main", "p_unclear", "p_null"))
        main_commit = 34 / 36 if c == "a" else 1.0  # a: 4 missing cells, one "unclear", one wide list
        assert close(main["commitment"]["rate"], main_commit), (c, main["commitment"])
        assert main["commitment"]["commit_error"] == (40 if c == "d" else 0), (c, main["commitment"])
        assert (unclear["commitment"]["commit"], null["commitment"]["commit"]) == (0, 20), c
        assert [x["retention"]["rate"] for x in (main, unclear, null)] == [1.0, 0.75, 1.0], c
        assert (unclear["unclear_on_clear"]["target"], unclear["unclear_on_clear"]["fields"]) == (10, 10), c
        assert close(unclear["unclear_on_clear"]["field_rate"], 10 / 280), c
        x = s["exchange_rate"][c][MODEL]
        assert x["p_unclear"]["clusters"] == {"a": 15, "b": 13, "c": 40, "d": 33}[c], (c, x["p_unclear"]["clusters"])
        assert close(x["p_unclear"]["commit_drop"], main_commit) and close(x["p_unclear"]["retention_drop"], 0.25), x
        assert close(x["p_unclear"]["rate"], main_commit / 0.25) and not x["p_unclear"]["retention_drop_ci_holds_0"], x
        assert close(x["p_null"]["commit_drop"], main_commit - 0.5) and x["p_null"]["retention_drop"] == 0, x
        assert x["p_null"]["rate"] is None and x["p_null"]["retention_drop_ci95"] == [0, 0], x
        assert x["p_null"]["retention_drop_ci_holds_0"], x
        for other in ("claude-sonnet-5-5", "claude-opus-5-5"):
            assert cells["p_main"][other]["absent"] == 240 and cells["p_main"][other]["commitment"]["rate"] is None
    assert s["served_models"] == {MODEL: [MODEL]}, s["served_models"]


def check_scoring():
    """The commitment rule on hand-chosen values, against the PLAN.md SI-08 definitions."""
    pick = {c: next(i for i in tp.items() if i.condition == c and i.kind == "ambiguous") for c in tp.CONDITIONS}

    def verdict(item, value):
        s = analyze.score(item, item.interpretations[0] | {item.target: value})
        return "error" if s["commit_error"] else "commit" if s["commit"] else "none"

    a, c, d = pick["a"], pick["c"], pick["d"]
    v0, v1 = c.goal.clear
    cases = [(a, None, "none"), (a, "any", "none"), (a, "unclear", "none"), (a, ("hotel",), "commit"),
             (a, ("guesthouse", "hotel"), "none"), (a, ("guesthouse",), "error"),
             (c, (v1,), "commit"), (c, (v0, v1), "none"), (c, (v1, v0), "none"), (c, (v0,), "error"),
             (d, None, "none"), (d, "unclear", "none"), (d, d.goal.clear, "error")]
    bad = [(i.id, v, verdict(i, v), want) for i, v, want in cases if verdict(i, v) != want]
    assert not bad, bad


def check_parser_matches_p5():
    """analyze.parse gives the same form as the P5 parser on every committed P5 reply."""
    def function(path, name):
        tree = ast.parse(path.read_text())
        return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)

    p4 = HERE.parents[1] / "p4_multiwoz" / "run.py"
    p5 = HERE.parents[1] / "p5_unclear" / "run.py"
    p4_ns = {}
    exec(compile(ast.Module([function(p4, "norm_value")], []), str(p4), "exec"), p4_ns)
    p5_ns = {"json": json, "p4": type("p4", (), {"FIELDS": list(tp.FIELDS[1:]),
                                                 "norm_value": staticmethod(p4_ns["norm_value"])})}
    exec(compile(ast.Module([function(p5, "parse")], []), str(p5), "exec"), p5_ns)
    rows = [json.loads(line) for line in (p5.parent / "raw.jsonl").read_text().splitlines()]
    diffs = [r["id"] for r in rows if p5_ns["parse"](r["text"]) != analyze.parse(r["text"])]
    assert not diffs and len(rows) == 246, (len(rows), diffs[:3])
    return len(rows)


if __name__ == "__main__":
    check_scoring()
    n = check_parser_matches_p5()
    with tempfile.TemporaryDirectory() as tmp:
        folder = pathlib.Path(tmp)
        rows = synthetic_rows()
        (folder / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        run = subprocess.run([sys.executable, "-I", str(HERE / "analyze.py"), tmp], capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        check_summary(json.loads((folder / "summary.json").read_text()))
        print("\n".join(run.stdout.splitlines()[:1] + [x for x in run.stdout.splitlines() if " b " in x or "-5-5 " in x][:6]))
    print(f"PASS: scoring rule, P5 parser match on {n} replies, and the summary of {len(rows)} synthetic rows")
