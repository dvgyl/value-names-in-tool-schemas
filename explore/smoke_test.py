"""Offline smoke test: from the stored answer rows of one run to values that the stored result files report.

It makes no model call and no network call, and it needs no key. It needs the public corpus (README section 3).
It reads era1_haiku/raw.jsonl (experiment A, Haiku, cell t0: the original tool), scores the answers with the code of
the analysis (a_analyze.read_of, briefsearch.search_failure, tool_validity.problems), and compares the results with
the expected values in smoke_test_expected.json. That file is a fixed input: no script writes it, and the analysis
scripts do not read it. This script writes no file.
Values:
- the hotel-filter share of the original tool on the 554 first requests (r10/analysis/out/a.md);
- the exclusion share of the original tool on the 448 first requests whose brief sets no type (r10/analysis/out/a.md);
- the original-tool search calls that do not fit the full input schema after the declared normalization, and how
  many of them are scorable (valid = 1); tool_validity.md;
- the exclusion share again, with these schema-invalid calls counted as missing (tool_validity.md).
Usage (from explore/): python3 -I smoke_test.py
Exit code 0 when every value is as expected.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.dont_write_bytecode = True
import anth  # noqa: E402

if not (anth.DATA / "data.json").exists():
    sys.exit(f"The public corpus is not in {anth.DATA}. Get it as README section 3 tells, then run this test again.")

import a_analyze as aa  # noqa: E402
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import tool_validity  # noqa: E402
import tools  # noqa: E402

RUN, CELL = "era1_haiku", "t0"


def share(k, n):
    return f"{100 * k / n:.1f}%"


def compute():
    data, g = runs.context()
    db = gold.hotel_db()
    ids = list(g["booked"])
    no_type = bs.brief_subsets(data, ids, db)["no_type"]
    schema = tools.SEARCH_T0["input_schema"]
    answers = {}  # dialogue -> [(kind, fields, schema problems or None)]
    for line in (EXPLORE / RUN / "raw.jsonl").read_text().splitlines():
        r = json.loads(line)
        d, cell, _ = aa.split(r["custom_id"])
        if cell != CELL:
            continue
        kind, val = aa.read_of(r, cell)
        found = None
        calls = r.get("tool_calls") or []
        if (r.get("type") == "succeeded" and r.get("stop") not in aa.CUT and len(calls) == 1
                and calls[0].get("name") == "search_hotels" and isinstance(calls[0].get("input"), dict)):
            found = tool_validity.problems(tools.clean_nulls(calls[0]["input"]), schema)
        answers.setdefault(d, []).append((kind, val if isinstance(val, dict) else None, found))
    scored = [(d, k, f, p) for d in ids for k, f, p in answers.get(d, []) if k != "invalid"]
    hotel = [aa.is_hotel(k, f) for _, k, f, _ in scored]
    blank = set(no_type)
    excl = [k in ("search", "form") and bs.search_failure(f, data[d], db) for d, k, f, _ in scored if d in blank]
    excl_sv = [k in ("search", "form") and bs.search_failure(f, data[d], db)
               for d, k, f, p in scored if d in blank and not p]
    every = [x for d in ids for x in answers.get(d, [])]
    return {
        "hotel_share_original_tool": {"k": sum(hotel), "n": len(hotel)},
        "exclusion_original_tool": {"k": sum(excl), "n": len(excl)},
        "schema_invalid_calls_original_tool": {"count": sum(bool(p) for _, _, p in every)},
        "schema_invalid_calls_scorable": {"count": sum(bool(p) for k, _, p in every if k != "invalid")},
        "exclusion_original_tool_schema_valid": {"k": sum(excl_sv), "n": len(excl_sv)},
    }


def main():
    expected = json.loads((HERE / "smoke_test_expected.json").read_text())
    got = compute()
    bad = 0
    print(f"Smoke test: {RUN}, cell {CELL}")
    for e in expected["values"]:
        x = got[e["key"]]
        ok = all(x[f] == e[f] for f in x) and ("printed" not in e or share(x["k"], x["n"]) == e["printed"])
        bad += not ok
        value = f"{x['k']}/{x['n']} = {share(x['k'], x['n'])}" if "k" in x else str(x["count"])
        want = f"{e['k']}/{e['n']} = {e['printed']}" if "k" in e else str(e["count"])
        print(f"- {e['label']}: {value}; expected {want} ({e['source']}): {'as expected' if ok else 'NOT AS EXPECTED'}")
    n = len(expected["values"])
    print(f"smoke test: {n - bad} of {n} values as expected")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
