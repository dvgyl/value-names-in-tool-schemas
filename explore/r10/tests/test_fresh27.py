"""Offline tests of r10/fresh27.py (amendment R10-27). No network call, no key, no sealed file, no em* folder.
Usage (from explore/): .venv/bin/python -I r10/tests/test_fresh27.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
import common  # noqa: E402
import control  # noqa: E402
import fresh27 as f  # noqa: E402
import gold  # noqa: E402
import groups as grp  # noqa: E402
import runs  # noqa: E402
import zforms  # noqa: E402


def test_selection(data, g):
    sel = f.select(data, g)
    o, s = sel["open"], sel["specific"]
    assert (len(o), len(s)) == (448, 59), (len(o), len(s))
    assert not set(o) & set(s)
    both = set(o) | set(s)
    assert not both & set(g["booked"]), "a fresh prefix is one of the 554"
    assert not both & f.release_test_ids(), "a fresh prefix was sent in a release-test run"
    prot = grp.protected(data)
    assert not both & set().union(*prot.values()), "a fresh prefix is protected"
    val, test = prot["validation"], prot["test"]
    assert not both & (val | test)
    assert both <= set(common.e7_ids(data))
    for d in o:
        assert gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None
    for d in s:
        assert gold.brief_type(data[d]) == "hotel"
    for d in both:
        assert zforms.WORD.search(data[d]["log"][zforms.prefix_end(data[d])]["text"])
    f._cache.pop("sel")
    assert f.select(data, g)["open"] == o, "the draw is not deterministic"
    grp.assert_unprotected(both, data)
    print("selection:", sel["pool"])


def test_requests(data, g):
    f.register()
    sets = f.set_of(data, g)
    for name, cells in f.PLAN.items():
        reqs = runs.requests(name)
        assert len(reqs) == len(cells) * (448 + 10 * 59), (name, len(reqs))
        ids = [r["custom_id"] for r in reqs]
        assert len(set(ids)) == len(ids) and all(len(i) <= 64 for i in ids)
        assert {i.split("-")[2] for i in ids} == set(cells)
        first = reqs[0]
        d = first["custom_id"].split("-")[1] + ".json"
        assert first["cell"] == "t0" and sets[d] in ("open", "specific")
        assert first["body"]["input"][-1]["content"] == zforms.prefix_text(data[d])
        model = f.MODEL_OF[name]
        for cell, (folder, n, same) in f.prove_same(model).items():
            assert n == 5 and same, (model, cell, folder, n, same)
    t0, tord = f.CELLS["t0"][1][0], f.CELLS["tord"][1][0]
    assert {k: v for k, v in t0.items() if k != "input_schema"} == {k: v for k, v in tord.items() if k != "input_schema"}
    assert list(tord["input_schema"]["properties"]) == sorted(t0["input_schema"]["properties"])
    assert control.ordered_tool() == tord
    print("requests: both runs build; every cell equals the earlier release-test request")


def test_parse():
    row = {"tool_calls": [{"name": "search_hotels", "input": {"property_kind": ["large_property"]}}]}
    kind, fields = f.parse_row(row, "t1")
    assert kind == "search" and fields["type"] == ("hotel",), (kind, fields)
    row0 = {"tool_calls": [{"name": "search_hotels", "input": {"type": ["hotel"]}}]}
    assert f.parse_row(row0, "tord") == f.parse_row(row0, "t0")
    assert f.parse_row({"tool_calls": []}, "t0")[0] == "none"
    two = {"tool_calls": [row0["tool_calls"][0]] * 2}
    assert f.parse_row(two, "tpar2")[0] == "invalid"
    print("parse: ok")


def test_money_no_em():
    import accounts
    opened = []
    orig = {n: getattr(pathlib.Path, n) for n in ("is_dir", "exists", "glob", "read_text")}

    def guard(name):
        def wrapped(self, *a, **k):
            rel = self.relative_to(EXPLORE).parts if self.is_relative_to(EXPLORE) else ()
            if rel and rel[0].startswith("em"):
                opened.append(str(self))
            return orig[name](self, *a, **k)
        return wrapped
    for n in orig:
        setattr(pathlib.Path, n, guard(n))
    try:
        c = f.committed_no_em(accounts.ACCOUNTS["openai_r9"])
    finally:
        for n, fn in orig.items():
            setattr(pathlib.Path, n, fn)
    assert not opened, opened[:3]
    assert c > 0
    assert f.used() >= 0
    try:
        f.check_cap(f.CAP + 0.01)
    except SystemExit:
        pass
    else:
        raise AssertionError("check_cap let a bound above the cap pass")
    print(f"money: committed without em* folders {c:.4f} USD; cap check refuses {f.CAP + 0.01:.2f} USD")


if __name__ == "__main__":
    data, g = runs.context()
    test_selection(data, g)
    test_requests(data, g)
    test_parse()
    test_money_no_em()
    print("all R10-27 tests pass")
