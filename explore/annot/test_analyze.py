"""Offline test of annot/analyze.py on a synthetic raw.jsonl. No API call.

Read 1 codes every P4-disputed field with the class that the stated P4 map gives its first P4 row. Read 2 changes one
class and one reading set. Read 3 holds one row of each missing kind, one invalid field, and one reply with a draft
object before the final object.
Run:  python3 -I annot/test_analyze.py
"""
import json
import math
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PROTOTYPES = HERE.parents[1]
FIELDS = ("name", "area", "pricerange", "stars", "type", "parking", "internet")
STATED_MAP = {"MODEL_ERROR": "clear", "GOLD_ERROR": "clear", "SCHEMA_GAP": "clear", "AMBIGUOUS/SELECTION": "clear",
              "AMBIGUOUS/WORD_COLLISION": "ambiguous", "AMBIGUOUS": "ambiguous"}
SECOND_VALUE = {"area": "centre", "pricerange": "cheap", "stars": "0", "type": "guesthouse", "parking": "yes", "internet": "yes"}


def label(a):
    return a["label"] + (f"/{a['subtag']}" if a["subtag"] else "")


def entry(cls, readings, subtag=None):
    return {"class": cls, "subtag": subtag, "readings": readings, "note": None}


def main():
    adj = json.loads((PROTOTYPES / "p4_multiwoz" / "adjudication.json").read_text())
    ids = sorted({json.loads(line)["id"] for line in (PROTOTYPES / "p4_multiwoz" / "raw.jsonl").read_text().splitlines()})
    first = {}
    for a in adj:
        first.setdefault((a["id"], a["field"]), STATED_MAP[label(a)])
    named = {a["id"] for a in adj if a["label"] == "SCHEMA_GAP"}

    def code(i):
        fields = {f: entry("clear", [None]) for f in FIELDS}
        for (d, f), cls in first.items():
            if d == i and cls == "ambiguous":
                fields[f] = entry("ambiguous", [None, [SECOND_VALUE[f]]], "vague_word")
        return {"name_request": i in named, "fields": fields, "links": []}

    quiet = [i for i in ids if i not in {a["id"] for a in adj}]
    a_, b_, d1, d2, d3, d4, d5, d6 = quiet[:8]
    rows = []
    for k in (1, 2, 3):
        for n, i in enumerate(ids):
            c = code(i)
            if k == 2 and i == a_:
                c["fields"]["area"] = entry("ambiguous", [None, ["centre"]], "vague_word")
            if k == 2 and i == b_:
                c["fields"]["area"] = entry("clear", [["north"]])
            if k == 3 and i == d5:
                c["fields"]["stars"] = entry("ambiguous", [None], "vague_word")
            text = json.dumps(c)
            if k == 3 and i == d6:
                draft = {**c, "fields": {f: entry("ambiguous", [None, "any"], "vague_word") for f in FIELDS}}
                text = f"Draft: {json.dumps(draft)}\nFinal answer: {text}"
            row = {"custom_id": f"{i.removesuffix('.json')}_r{k}", "type": "succeeded", "model": "claude-opus-5-5",
                   "stop": "end_turn", "input_tokens": 3000 + n, "output_tokens": 1000 + 10 * n + k, "text": text}
            if k == 3 and i == d1:
                row = {"custom_id": row["custom_id"], "type": "errored"}
            if k == 3 and i == d2:
                row.update(stop="refusal", text="")
            if k == 3 and i == d3:
                row.update(stop="max_tokens", text=text[:200])
            if k == 3 and i == d4:
                row.update(text="no JSON here")
            rows.append(row)

    with tempfile.TemporaryDirectory() as tmp:
        raw, out = pathlib.Path(tmp) / "raw.jsonl", pathlib.Path(tmp) / "summary.json"
        raw.write_text("".join(json.dumps(r) + "\n" for r in rows))
        subprocess.run([sys.executable, "-I", str(HERE / "analyze.py"), "--raw", str(raw), "--out", str(out)], check=True)
        s = json.loads(out.read_text())

    assert s["rows"] == 369 and s["expected_rows"] == 369
    assert s["outcomes_per_read"]["3"] == {"parsed": 119, "error": 1, "refusal": 1, "truncated": 1, "parse_fail": 1,
                                           "absent": 0}, s["outcomes_per_read"]["3"]
    assert s["invalid_fields"] == {"ambiguous field with fewer than two readings": 1}, s["invalid_fields"]

    ok = [r for r in rows if r["type"] == "succeeded"]
    tin, tout = sorted(r["input_tokens"] for r in ok), sorted(r["output_tokens"] for r in ok)
    assert s["tokens"]["calls"] == 368
    assert abs(s["tokens"]["input"]["mean"] - sum(tin) / 368) < 1e-9
    assert s["tokens"]["output"]["p95"] == tout[math.ceil(0.95 * 368) - 1] and s["tokens"]["output"]["max"] == tout[-1]

    agree = sum(STATED_MAP[label(a)] == first[(a["id"], a["field"])] for a in adj)
    for k in ("1", "2", "3"):
        assert s["p4_agreement"]["per_read"][k] == {"rows": 139, "coded": 139, "agree": agree, "share": agree / 139}, k
    assert s["p4_agreement"]["class_map"] == STATED_MAP
    confusion = s["p4_agreement"]["confusion_per_read"]["1"]
    assert sum(sum(c.values()) for c in confusion.values()) == 139
    assert confusion["AMBIGUOUS/SELECTION"].get("clear") == sum(label(a) == "AMBIGUOUS/SELECTION" for a in adj)
    assert s["p4_agreement"]["schema_gap_rows_name_request_read1"] == {"True": 49}

    st = s["stability"]
    assert st["dialogues_with_all_reads_parsed"] == 119
    assert (st["all_fields"]["fields"], st["all_fields"]["same_class"], st["all_fields"]["same_readings"]) == (832, 831, 830)
    assert st["per_field"]["stars"]["fields"] == 118 and st["per_field"]["area"]["same_readings"] == 117
    assert (st["dialogues_with_all_fields_valid"], st["whole_code_same"], st["name_request_same"]) == (118, 116, 119)

    rp = s["repricing"]
    assert abs(rp["planned_per_call"] - (8000 * 1.3 * 4 + 4000 * 1.3 * 20) / 1e6 * 0.5) < 1e-12
    assert abs(rp["measured_mean_per_call"] - (sum(tin) / 368 * 4 + sum(tout) / 368 * 20) / 1e6 * 0.5) < 1e-12
    assert rp["calls"] == 136
    print("annot/test_analyze.py: PASS (missing kinds, last-object parse, P4 agreement, stability, repricing)")


if __name__ == "__main__":
    main()
