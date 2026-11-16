"""Offline tests of r10/steer2.py (amendment R10-15) and r10/control.py (amendment R10-16). No network call, no key.

Usage (from explore/): .venv/bin/python -I r10/tests/test_steer2_control.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import release  # noqa: E402
import runs  # noqa: E402
import steer  # noqa: E402
import steer2  # noqa: E402
import tools  # noqa: E402
from test_flag_turns import row  # noqa: E402


def test_service_requests():
    """The new rewrites use the params of the first rewrite of their group (R10-14 and R10-6), unchanged."""
    for g, path in (("h", R10 / "steer" / "request_h.json"), ("g", R10 / "steer" / "request_g.json"),
                    ("n", R10 / "release" / "request.json")):
        assert steer2.rewrite_request(g)["params"] == json.loads(path.read_text())["params"], g
    assert "system" not in steer2.rewrite_request("n")["params"]
    assert steer2.rewrite_request("h")["params"]["system"] == steer.BRIEF["h"]


def test_rewrites_accepted():
    """Every frozen rewrite passes the R10-6 rule, and the first rewrite of each group is the earlier frozen edit."""
    assert steer2.edit_path("h1") == steer.edit_path("h") and steer2.edit_path("n1") == release.EDIT
    for c in steer2.cells():
        release.accept_obj(json.loads(steer2.edit_path(c).read_text()))
    log = [x for x in steer2.answers() if x["accepted"]]
    assert {x["cell"] for x in log} == {c for c in steer2.cells() if c[1] != "1"}


def test_parse_maps_back():
    """A call of each rewrite with every option of type maps back to the F0 values."""
    for c in steer2.cells():
        e = steer2.edit(c)
        q = e["params"]["type"]
        for old in ("hotel", "guesthouse"):
            new = e["values"]["type"][release.key(old)]
            args = {e["params"][p]: None for p in e["params"]}
            args[q] = [new]
            kind, f = steer2.parse_call(row(calls=[{"id": "t", "name": "search_hotels", "input": args}]), c)
            assert kind == "search" and f["type"] == (old,), (c, old, f)
        assert steer2.parse_call(row("text only"), c)[0] == "none"


def test_erm_requests():
    """Each erm_haiku request equals the t0 request of build_a except the tools; 10 cells x 554 prefixes."""
    data, g = runs.context()
    t0 = {r["custom_id"].split("-")[1]: r["params"] for r in runs.build_a("x", "haiku", 1, data, g) if r["cell"] == "t0"}
    reqs = runs.requests("erm_haiku")
    assert len(reqs) == 554 * (1 + len(steer2.cells()))
    for r in reqs:
        d, cell = r["custom_id"].split("-")[1:3]
        p = r["params"]
        if cell == "t0":
            assert p == t0[d]
        else:
            assert {k: v for k, v in p.items() if k != "tools"} == {k: v for k, v in t0[d].items() if k != "tools"}
            assert p["tools"] == [steer2.cell_tool(cell)] and p["tools"][0]["strict"] is True


def test_control_requests():
    """R10-16: t0 and trep are the t0 request of build_a (params byte for byte); tord differs only in the order of the
    schema fields; the read counts follow control.READS."""
    import control
    data, g = runs.context()
    t0 = {r["custom_id"].split("-")[1]: r["params"] for r in runs.build_a("x", "haiku", 1, data, g) if r["cell"] == "t0"}
    sets = control.set_of(data, g)
    for name in ("erc_haiku", "erc2_haiku"):
        reqs = runs.requests(name)
        count = {}
        for r in reqs:
            d, cell = r["custom_id"].split("-")[1:3]
            count[(d, cell)] = count.get((d, cell), 0) + 1
            p = r["params"]
            if cell in ("t0", "trep"):
                assert json.dumps(p) == json.dumps(t0[d]), r["custom_id"]
            else:
                assert cell == "tord"
                assert {k: v for k, v in p.items() if k != "tools"} == {k: v for k, v in t0[d].items() if k != "tools"}
                new, old = p["tools"][0], t0[d]["tools"][0]
                same = lambda t: {**t, "input_schema": {**t["input_schema"], "required": sorted(t["input_schema"]["required"])}}  # noqa: E731
                assert same(new) == same(old) and json.dumps(new) != json.dumps(old)  # the same objects, other order
                assert list(new["input_schema"]["properties"]) == sorted(old["input_schema"]["properties"])
                assert new["input_schema"]["required"] == sorted(old["input_schema"]["required"])
        for (d, cell), n in count.items():
            assert n == control.READS[sets[d + ".json"]], (d, cell, n)
    assert len(runs.requests("erc2_haiku")) * 2 == len(runs.requests("erc_haiku"))


def test_verify3_requests():
    """R10-17: the f0 and verify requests carry the system texts, schemas and user texts of the earlier verifier runs
    (erb_sonnet), with the round-9 DeepInfra settings; 1,040 dialogues x 2 reads x 2 cells; no protected dialogue."""
    import verify3
    old = {}
    for line in (EXPLORE / "erb_sonnet" / "requests.jsonl").read_text().splitlines():
        r = json.loads(line)
        _, d, cell, _ = r["custom_id"].split("-")
        if cell in ("f0", "verify"):
            p = r["params"]
            old[(d, cell)] = (p["system"], p["output_config"]["format"]["schema"], p["messages"][0]["content"])
    for name in verify3.RUNS:
        reqs = runs.requests(name)
        assert len(reqs) == 1040 * 2 * 2
        for r in reqs:
            _, d, cell, read = r["custom_id"].split("-")
            b = r["body"]
            assert b["messages"][0]["content"] == old[(d, cell)][0] and b["messages"][1]["content"] == old[(d, cell)][2]
            assert b["response_format"]["json_schema"]["schema"] == old[(d, cell)][1]
            assert b["temperature"] == 1.0 and b["top_p"] == 1.0 and b["max_tokens"] == 650
            assert (b.get("reasoning_effort") == "none") == (name != "ery_gemma")


if __name__ == "__main__":
    only = sys.argv[1:]
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn) and (not only or name in only):
            fn()
            print("ok", name)
    print("PASS")
