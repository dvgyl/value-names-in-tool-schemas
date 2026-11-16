"""Test of r10/groups.py on the MultiWOZ files (no API call). Usage: explore/.venv/bin/python -I r10/tests/test_groups.py

It checks the group sizes, the two parts of the 233, the protected-id assert, and the new-text assert.
"""
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import groups  # noqa: E402
from groups import anth  # noqa: E402


def raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def test_sizes(data, g):
    assert {k: len(g[k]) for k in ("s1t", "s3", "s2", "booked", "ins")} == {"s1t": 994, "s3": 490, "s2": 545,
                                                                           "booked": 554, "ins": 233}
    assert all(len(set(g[k])) == len(g[k]) for k in g)
    print(f"  parts of the 233: assistant says hotel {len(g['ins_assistant_hotel'])}, no turn says hotel "
          f"{len(g['ins_clean'])}")


def test_parts(data, g):
    a, c = set(g["ins_assistant_hotel"]), set(g["ins_clean"])
    assert not a & c and a | c == set(g["ins"])
    for i in a:
        assert any(groups.gold.WORD.search(t["text"]) for k, t in enumerate(data[i]["log"]) if k % 2)
    for i in c:
        assert not any(groups.gold.WORD.search(t["text"]) for t in data[i]["log"])


def test_ids_file(data, g):
    """Uses a temporary path, so the test does not write r10/ids.json."""
    real = groups.IDS
    with tempfile.TemporaryDirectory() as tmp:
        groups.IDS = pathlib.Path(tmp) / "ids.json"
        try:
            path = groups.write_ids(data)  # writes once
            assert json.loads(path.read_text()) == g
            assert groups.write_ids(data) == path  # a rerun checks and does not overwrite
            mtime = path.stat().st_mtime_ns
            groups.write_ids(data)
            assert path.stat().st_mtime_ns == mtime
            changed = dict(g, ins=g["ins"][:-1])
            path.write_text(json.dumps(changed))
            try:
                groups.write_ids(data)
            except AssertionError:
                pass
            else:
                raise AssertionError("a changed list must fail")
            assert json.loads(path.read_text()) == changed  # the file stays as it was
        finally:
            groups.IDS = real


def test_unprotected(data, g):
    for name in ("s1t", "s3", "s2", "booked", "ins"):
        groups.assert_unprotected(g[name], data)  # the five groups hold no protected id
    lists = groups.protected(data)
    base = g["ins"]
    for name, planted in (("pool", sorted(lists["pool"])[0]), ("gate", sorted(lists["gate"])[0]),
                          ("test", sorted(lists["test"] - lists["pool"] - lists["gate"])[0]),
                          ("validation", sorted(lists["validation"] - lists["pool"] - lists["gate"])[0]),
                          ("wave1 pool", sorted(lists["wave1_pool"])[0])):
        assert raises(groups.assert_unprotected, base + [planted], data), name


def test_new_text(data, g):
    known = sorted(groups.item_sentences())
    assert len(known) > 1000, len(known)
    first = json.loads((groups.EXPLORE / "main" / "track_c" / "items.jsonl").read_text().splitlines()[0])["text"]
    copied = first.split("\n")[2].removeprefix("Traveller: ")  # one real sentence of the first item
    assert raises(groups.assert_new_text, ["Hello there. " + copied + " Thank you."])
    assert raises(groups.assert_new_text, [copied.upper()])  # case does not matter
    groups.assert_new_text(["Please find me a quiet room near the river for Friday night."])
    groups.assert_new_text(["Hi all"])  # a sentence of fewer than 4 words is not checked


def main():
    data = anth.multiwoz()
    g = groups.groups(data)
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(data, g)
            print("ok", name)
    print("groups test passed")


if __name__ == "__main__":
    main()
