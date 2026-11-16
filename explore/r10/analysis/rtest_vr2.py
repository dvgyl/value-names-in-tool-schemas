"""Verbatim extract of the independent check script workshops/release-test/verify_release2.py: the names that the post hoc scripts
rtest_c1.py, rtest_levels.py and rtest_symmetric.py use (EXPLORE, MODELS, R20_CONTROL, jsonl, load, load_sets, mean, safe, valid_scores), with every module-level name that they need,
and the paths of the study folder. The checks of that script are not here. No model call, no network call.
"""
import collections
import datetime
import difflib
import hashlib
import json
import math
import pathlib
import random
import re
HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
MODELS = {"sol": "erk2_sol", "luna": "erk2_luna"}
R20_CONTROL = {"sol": "erk_sol", "luna": "erk_luna"}
SIZES = {"open": 448, "specific": 59, "guesthouse": 47}
FIELDS = ("area", "pricerange", "stars", "type", "parking", "internet")


def safe(path):
    p = pathlib.Path(path)
    for part in p.parts:
        assert part not in ("seal_keys", "seal-key", "private folder"), f"refused: {p}"
    try:
        inner = p.relative_to(EXPLORE).parts
    except ValueError:
        inner = ()
    assert not any(part.startswith("em") for part in inner[:-1]), f"refused: {p}"
    assert not p.name.endswith((".sealed", ".env")) and "key" not in p.name.lower(), f"refused: {p}"
    assert not p.name.startswith("._"), f"refused: {p}"
    return p


def jsonl(path):
    p = safe(path)
    if not p.exists():
        return None
    with open(p) as fh:
        return [json.loads(x) for x in fh if x.strip()]


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def brief_type(d, key="info"):
    return d["goal"]["hotel"].get(key, {}).get("type")


def load_sets(data, order):
    sets = {"open": [d for d in order if brief_type(data[d]) is None and brief_type(data[d], "fail_info") is None],
            "specific": [d for d in order if brief_type(data[d]) == "hotel"],
            "guesthouse": [d for d in order if brief_type(data[d]) == "guesthouse"]}
    assert {k: len(v) for k, v in sets.items()} == SIZES, {k: len(v) for k, v in sets.items()}
    assert sum(SIZES.values()) == len(order) == 554
    return sets


def norm_value(field, v):
    v = v.strip().lower()
    if field == "type":
        v = {"guest house": "guesthouse", "bed and breakfast": "guesthouse"}.get(v, v)
    if field in ("parking", "internet") and v == "free":
        v = "yes"
    return v


def clean_nulls(args):
    out = {}
    for k, v in args.items():
        if v == "null":
            v = None
        elif isinstance(v, list):
            v = [x for x in v if x != "null"] or None
        out[k] = v
    return out


def parse_f0(text):
    """natural.parse with F0 (the label hotel maps to itself) and common.parse."""
    s, e = text.rfind("{"), text.rfind("}")
    obj = json.loads(text[s:e + 1])
    if "property_kind" in obj:
        kind = obj.pop("property_kind")
        swap = {"large_property": "hotel", "large property": "hotel"}
        obj["type"] = [swap.get(str(x).lower(), x) for x in kind] if isinstance(kind, list) else swap.get(str(kind).lower(), kind)
    out = {"name": (obj.get("name") or None)}
    for f in FIELDS:
        v = obj.get(f)
        if isinstance(v, str) and v.lower() == "unclear":
            out[f] = "unclear"
        elif v is None:
            out[f] = None
        elif isinstance(v, str) and v.lower() in ("any", "dontcare"):
            out[f] = "any"
        else:
            vals = v if isinstance(v, list) else [v]
            out[f] = tuple(dict.fromkeys(norm_value(f, str(x)) for x in vals)) or None
    return out


def read_row(row):
    """(kind, fields or reason): harmless2.parse_row = tools.parse_call with the t0 names and values."""
    if row.get("type", "succeeded") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in CUT:
        return "invalid", "cut"
    calls = row.get("tool_calls") or []
    if not calls:
        return "none", row.get("text", "")
    if len(calls) > 1:
        return "invalid", f"{len(calls)} tool calls"
    c = calls[0]
    if c["name"] != "search_hotels" or not isinstance(c.get("input"), dict):
        return "invalid", f"tool {c.get('name')!r} with input {type(c.get('input')).__name__}"
    try:
        return "search", parse_f0(json.dumps(clean_nulls(c["input"])))
    except (ValueError, KeyError, TypeError) as x:
        return "invalid", f"{type(x).__name__}: {x}"


def score(kind, fields):
    return int(kind == "search" and isinstance(fields.get("type"), tuple) and "hotel" in fields["type"])


def load(run, cells=None, rename=None):
    rows = jsonl(EXPLORE / run / "raw.jsonl")
    if rows is None:
        return None, None
    reads, detail = collections.defaultdict(list), []
    for r in rows:
        _, d, cell, _ = r["custom_id"].split("-")
        if cells is not None and cell not in cells:
            continue
        k, f = read_row(r)
        reads[(d + ".json", (rename or {}).get(cell, cell))].append((k, f))
        if k != "search":
            detail.append({"custom_id": r["custom_id"], "kind": k, "stop": r.get("stop"),
                           "text": (r.get("text") or "")[:80], "text_type_null": '"type":null' in (r.get("text") or "")})
    return reads, detail


def valid_scores(reads, d, cell):
    return [score(k, f) for k, f in reads.get((d, cell), []) if k != "invalid"]
