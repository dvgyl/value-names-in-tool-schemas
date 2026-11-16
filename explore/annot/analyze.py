"""Summarize the E3 annotations and write explore/e3/summary.json.

Measures (PROTOCOL.md E3): input and output tokens per call, agreement of the field class with the P4 labels on the
139 disputed rows, read-to-read stability, and a repricing line for the annotation call of budget_v10.py.
Run:  python3 -I annot/analyze.py [--raw PATH] [--out PATH]
"""
import argparse
import collections
import importlib.util
import json
import math
import pathlib
import re
import statistics
import sys
from typing import NamedTuple

sys.dont_write_bytecode = True

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import e3  # noqa: E402

ADJUDICATION = e3.PROTOTYPES / "p4_multiwoz" / "adjudication.json"
BUDGET = e3.PROTOTYPES.parent / "budget_v10.py"
ANNOT_DIALOGUES = 136  # PLAN.md SI-17: the 64 gate-set dialogues and the 72 dialogues of the registered half
CLASS_MAP = {
    "MODEL_ERROR": "clear",
    "GOLD_ERROR": "clear",
    "SCHEMA_GAP": "clear",
    "AMBIGUOUS/SELECTION": "clear",
    "AMBIGUOUS/WORD_COLLISION": "ambiguous",
    "AMBIGUOUS": "ambiguous",
}
CLASS_MAP_REASON = {
    "MODEL_ERROR": "One defensible reading, the gold.",
    "GOLD_ERROR": "One defensible reading, the model value.",
    "SCHEMA_GAP": "Rule 1 under p_main: the name field holds the request, and the other field is clear with the reading null.",
    "AMBIGUOUS/SELECTION": "The p_main offer sentence makes an accepted offer no requirement, so the field is clear (SI-10).",
    "AMBIGUOUS/WORD_COLLISION": "Two defensible readings.",
    "AMBIGUOUS": "Two defensible readings (feature question, relaxation, or vague word).",
}


class Field(NamedTuple):
    cls: str
    subtag: object
    readings: frozenset


def last_object(text):
    """The last top-level JSON object in the reply. P4 lost two replies that held a corrected second object."""
    decoder, found, i = json.JSONDecoder(), None, text.find("{")
    while i != -1:
        try:
            obj, end = decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            i = text.find("{", i + 1)
            continue
        if isinstance(obj, dict):
            found = obj
        i = text.find("{", end)
    return found


class Reader:
    """Parses a reply into a code: one Field per form field, or the reason why that field is invalid."""

    def __init__(self, p4):
        self.norm_value = p4.norm_value
        self.domain = {f: set(v) for f, v in e3.allowed(p4).items()}
        self.names = {self.name_key(n): n for n in self.domain["name"]}

    @staticmethod
    def name_key(name):
        return re.sub(r"[^a-z0-9]", "", name.lower()).removeprefix("the")

    def value(self, field, x):
        if field == "name":
            return self.names.get(self.name_key(str(x)), str(x))
        return self.norm_value(field, str(x))

    def reading(self, field, raw):
        if raw is None:
            return None
        if isinstance(raw, str) and raw.strip().lower() == "any":
            return "any"
        values = tuple(self.value(field, x) for x in (raw if isinstance(raw, list) else [raw]))
        if not values or len(set(values)) != len(values) or not set(values) <= self.domain[field]:
            raise ValueError("a reading holds a value outside the form, a repeated value, or no value")
        return values

    def field(self, field, entry):
        if not isinstance(entry, dict):
            return "field missing"
        cls = entry.get("class")
        if cls not in e3.SUBTAGS:
            return "unknown class"
        if not isinstance(entry.get("readings"), list):
            return "readings is not a list"
        try:
            readings = [self.reading(field, r) for r in entry["readings"]]
        except ValueError as exc:
            return str(exc)
        distinct = set(readings)
        if len(distinct) != len(readings):
            return "repeated reading"
        if cls == "clear" and len(distinct) != 1:
            return "clear field without exactly one reading"
        if cls == "ambiguous" and len(distinct) < 2:
            return "ambiguous field with fewer than two readings"
        if cls == "outside_form" and readings != [None]:
            return "outside_form field whose reading set is not [null]"
        return Field(cls, entry.get("subtag"), frozenset(distinct))

    def code(self, row):
        """A dict for a parsed reply, else the kind of missing cell."""
        if row["type"] != "succeeded":
            return "error"
        if row["stop"] in ("refusal", "max_tokens"):
            return "refusal" if row["stop"] == "refusal" else "truncated"
        obj = last_object(row.get("text") or "")
        if obj is None or not isinstance(obj.get("fields"), dict):
            return "parse_fail"
        flag = obj.get("name_request")
        links = obj.get("links")
        return {"name_request": flag if isinstance(flag, bool) else None,
                "fields": {f: self.field(f, obj["fields"].get(f)) for f in e3.FIELDS},
                "links": len(links) if isinstance(links, list) else 0}


def p95(xs):
    return sorted(xs)[math.ceil(0.95 * len(xs)) - 1]


def describe(xs):
    return {"mean": statistics.fmean(xs), "p95": p95(xs), "max": max(xs)} if xs else None


def p4_label(row):
    return row["label"] + (f"/{row['subtag']}" if row["subtag"] else "")


def field_of(codes, dialogue, read, field):
    code = codes.get((dialogue, read))
    return code["fields"][field] if isinstance(code, dict) else None


def agreement(codes, adj):
    per_read, confusion = {}, {}
    for k in e3.READS:
        table = collections.defaultdict(collections.Counter)
        coded = agree = 0
        for a in adj:
            f = field_of(codes, a["id"], k, a["field"])
            got = f.cls if isinstance(f, Field) else "missing"
            table[p4_label(a)][got] += 1
            if got != "missing":
                coded += 1
                agree += got == CLASS_MAP[p4_label(a)]
        per_read[str(k)] = {"rows": len(adj), "coded": coded, "agree": agree, "share": agree / coded if coded else None}
        confusion[str(k)] = {label: dict(c) for label, c in sorted(table.items())}
    by_pair = collections.defaultdict(set)
    for a in adj:
        by_pair[(a["id"], a["field"])].add(CLASS_MAP[p4_label(a)])
    def flag(dialogue):
        code = codes.get((dialogue, 1))
        return str(code["name_request"]) if isinstance(code, dict) else "missing"

    flags = collections.Counter(flag(a["id"]) for a in adj if a["label"] == "SCHEMA_GAP")
    return {"class_map": CLASS_MAP, "class_map_reason": CLASS_MAP_REASON, "unique_pairs": len(by_pair),
            "pairs_with_two_p4_classes": sum(len(v) > 1 for v in by_pair.values()),
            "per_read": per_read, "confusion_per_read": confusion,
            "schema_gap_rows_name_request_read1": dict(flags)}


def stability(codes, ids, pairs):
    complete = [i for i in ids if all(isinstance(codes.get((i, k)), dict) for k in e3.READS)]

    def tally(cells):
        n = same_class = same_readings = 0
        for i, f in cells:
            fs = [field_of(codes, i, k, f) for k in e3.READS]
            if all(isinstance(x, Field) for x in fs):
                n += 1
                same_class += len({x.cls for x in fs}) == 1
                same_readings += len({x.readings for x in fs}) == 1
        return {"fields": n, "same_class": same_class, "same_readings": same_readings,
                "share_same_class": same_class / n if n else None, "share_same_readings": same_readings / n if n else None}

    whole = [i for i in complete if all(isinstance(field_of(codes, i, k, f), Field) for k in e3.READS for f in e3.FIELDS)]
    signature = lambda i, k: (codes[(i, k)]["name_request"],  # noqa: E731
                              tuple((field_of(codes, i, k, f).cls, field_of(codes, i, k, f).readings) for f in e3.FIELDS))
    return {"dialogues_with_all_reads_parsed": len(complete),
            "per_field": {f: tally([(i, f) for i in complete]) for f in e3.FIELDS},
            "all_fields": tally([(i, f) for i in complete for f in e3.FIELDS]),
            "p4_disputed_pairs": tally([p for p in sorted(pairs) if p[0] in complete]),
            "name_request_same": sum(len({codes[(i, k)]["name_request"] for k in e3.READS}) == 1 for i in complete),
            "dialogues_with_all_fields_valid": len(whole),
            "whole_code_same": sum(len({signature(i, k) for k in e3.READS}) == 1 for i in whole)}


def load_budget():
    spec = importlib.util.spec_from_file_location("budget_v10", BUDGET)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def repricing(tokens_in, tokens_out):
    b = load_budget()
    planned = b.annot_cost(e3.MODEL)
    mean = e3.anth.cost(e3.MODEL, statistics.fmean(tokens_in), statistics.fmean(tokens_out))
    high = e3.anth.cost(e3.MODEL, p95(tokens_in), p95(tokens_out))
    line = (f"Annotation call, {e3.MODEL}, batch: budget_v10 prices {b.ANNOT_IN:,} in and {b.ANNOT_OUT:,} out "
            f"(x1.3 tokenizer factor) at {planned:.6f} USD. E3 measures {statistics.fmean(tokens_in):,.0f} in and "
            f"{statistics.fmean(tokens_out):,.0f} out (mean) at {mean:.6f} USD, and {p95(tokens_in):,} in and "
            f"{p95(tokens_out):,} out (95th percentile) at {high:.6f} USD. The SI-17 share of {e3.MODEL} at "
            f"{ANNOT_DIALOGUES} calls is {ANNOT_DIALOGUES * planned:.2f} USD planned, {ANNOT_DIALOGUES * mean:.2f} USD at "
            f"the measured mean, and {ANNOT_DIALOGUES * high:.2f} USD at the 95th percentile, before the 25% margin.")
    return {"planned_per_call": planned, "measured_mean_per_call": mean, "measured_p95_per_call": high,
            "calls": ANNOT_DIALOGUES, "line": line}


def summarize(rows, reader, ids, adj):
    keys = [r["custom_id"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate custom_id in raw.jsonl"
    codes, outcomes = {}, {str(k): collections.Counter() for k in e3.READS}
    tokens_in, tokens_out = [], []
    for row in rows:
        dialogue, k = e3.parse_id(row["custom_id"])
        code = reader.code(row)
        codes[(dialogue, k)] = code
        outcomes[str(k)]["parsed" if isinstance(code, dict) else code] += 1
        if row["type"] == "succeeded":
            tokens_in.append(row["input_tokens"])
            tokens_out.append(row["output_tokens"])
    for k, c in outcomes.items():
        c["absent"] = len(ids) - sum(c.values())
    parsed = [c for c in codes.values() if isinstance(c, dict)]
    fields = [(f, c["fields"][f]) for c in parsed for f in e3.FIELDS]
    classes = collections.defaultdict(collections.Counter)
    subtags = collections.defaultdict(collections.Counter)
    for f, x in fields:
        if isinstance(x, Field):
            classes[f][x.cls] += 1
            subtags[x.cls][str(x.subtag)] += 1
    return {
        "experiment": "e3", "rows": len(rows), "expected_rows": len(ids) * len(e3.READS),
        "outcomes_per_read": {k: dict(c) for k, c in outcomes.items()},
        "tokens": {"calls": len(tokens_in), "input": describe(tokens_in), "output": describe(tokens_out)},
        "invalid_fields": dict(collections.Counter(x for _, x in fields if isinstance(x, str))),
        "valid_fields": sum(isinstance(x, Field) for _, x in fields),
        "classes_per_field": {f: dict(c) for f, c in classes.items()},
        "subtags_per_class": {c: dict(s) for c, s in subtags.items()},
        "codes_with_links": sum(c["links"] > 0 for c in parsed),
        "p4_agreement": agreement(codes, adj),
        "stability": stability(codes, ids, {(a["id"], a["field"]) for a in adj}),
        "repricing": repricing(tokens_in, tokens_out) if tokens_in else None,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", type=pathlib.Path, default=e3.EXPLORE / "e3" / "raw.jsonl")
    ap.add_argument("--out", type=pathlib.Path, default=e3.EXPLORE / "e3" / "summary.json")
    args = ap.parse_args()
    rows = [json.loads(line) for line in args.raw.read_text().splitlines() if line.strip()]
    adj = json.loads(ADJUDICATION.read_text())
    assert len(adj) == 139, len(adj)
    s = summarize(rows, Reader(e3.load_p5().p4), e3.p4_ids(), adj)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(s, indent=1))
    t = s["tokens"]
    if t["calls"]:
        print(f"tokens over {t['calls']} calls: input mean {t['input']['mean']:,.0f}, p95 {t['input']['p95']:,}; "
              f"output mean {t['output']['mean']:,.0f}, p95 {t['output']['p95']:,}")
    for k, r in s["p4_agreement"]["per_read"].items():
        print(f"read {k}: class agrees with the mapped P4 label on {r['agree']} of {r['coded']} coded rows ({r['rows']} rows)")
    a = s["stability"]["all_fields"]
    print(f"stability: same class in all reads {a['same_class']} of {a['fields']} fields, same readings {a['same_readings']}")
    if s["repricing"]:
        print(s["repricing"]["line"])
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
