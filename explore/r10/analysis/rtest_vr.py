"""Verbatim extract of the independent check script workshops/release-test/verify_release.py: the names that the post hoc scripts
rtest_c1.py, rtest_levels.py and rtest_symmetric.py use (CONTROL, EXPLORE, LEVEL, MW, UPDATES, jsonl, load, load_sets, mean, safe, valid_scores), with every module-level name that they need,
and the paths of the study folder. The checks of that script are not here. No model call, no network call.
"""
import collections
import hashlib
import json
import math
import pathlib
import random
import re
import sys
import zlib
HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
MW = pathlib.Path(__file__).resolve().parents[3] / "corpus" / "MULTIWOZ2.4"  # the public corpus (README.md, section 3)
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
MODELS = {"sol": "erk_sol", "luna": "erk_luna", "deepseek": "erk_deepseek", "qwen": "erk_qwen", "gemma": "erk_gemma"}
CONTROL = {"tool": "t0", "form": "p0"}
UPDATES = {"a": {"tool": "trep", "form": "prep"}, "b": {"tool": "tpar", "form": "ppar"}, "c": {"tool": "t1", "form": "p1"}}
RENAMED = {"t1", "p1"}
SIZES = {"open": 448, "specific": 59, "guesthouse": 47}
C = {"tool": 2 * 2 * 1, "form": 3 * 2 * 1}
LEVEL = {ch: 1 - 0.05 / c for ch, c in C.items()}


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


def load_sets(data, order):
    """The sets of R10-6 (control.set_of) on the prefixes, in the request order."""
    def brief(d, key="info"):
        return data[d]["goal"]["hotel"].get(key, {}).get("type")
    sets = {"open": [d for d in order if brief(d) is None and brief(d, "fail_info") is None],
            "specific": [d for d in order if brief(d) == "hotel"],
            "guesthouse": [d for d in order if brief(d) == "guesthouse"]}
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
FIELDS = ("area", "pricerange", "stars", "type", "parking", "internet")


def tok(v):
    return str(v).strip().lower().replace(" ", "_")


def parse_fields(obj, renamed):
    """natural.parse with F0 (renamed False) or F1 (renamed True), then common.parse: the fields with F0 names."""
    keys, label = ({"type": "property_kind"}, "large_property") if renamed else ({}, "hotel")
    back = {v: k for k, v in keys.items()}
    obj = {back.get(k, k): v for k, v in obj.items()}
    undo = lambda v: "hotel" if isinstance(v, str) and tok(v) == tok(label) else v  # noqa: E731
    if "type" in obj:
        obj["type"] = [undo(v) for v in obj["type"]] if isinstance(obj["type"], list) else undo(obj["type"])
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


def last_object(text):
    s, e = text.rfind("{"), text.rfind("}")
    obj = json.loads(text[s:e + 1])
    if not isinstance(obj, dict):
        raise ValueError("not an object")
    return obj


def clean_nulls(args):
    out = {}
    for k, v in args.items():
        if v == "null":
            v = None
        elif isinstance(v, list):
            v = [x for x in v if x != "null"] or None
        out[k] = v
    return out


def read_row(row, cell):
    """(kind, fields or reason): kind is "search", "none" or "invalid" (R10-20, "Outcome and rule")."""
    if row.get("type", "succeeded") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in CUT:
        return "invalid", "cut"
    renamed = cell in RENAMED
    if cell.startswith("t"):
        calls = row.get("tool_calls") or []
        if not calls:
            return "none", row.get("text", "")
        if len(calls) > 1:
            return "invalid", f"{len(calls)} tool calls"
        c = calls[0]
        if c["name"] != "search_hotels" or not isinstance(c.get("input"), dict):
            return "invalid", f"tool {c.get('name')!r} with input {type(c.get('input')).__name__}"
        try:
            return "search", parse_fields(last_object(json.dumps(clean_nulls(c["input"]))), renamed)
        except (ValueError, KeyError, TypeError) as x:
            return "invalid", f"{type(x).__name__}: {x}"
    try:
        return "search", parse_fields(last_object(row.get("text") or ""), renamed)
    except (ValueError, KeyError, TypeError, IndexError) as x:
        return "invalid", f"{type(x).__name__}: {x}"


def arm_check(row, cell):
    """Keys and type values outside the arm's schema (names and values of F0, or of F1 for t1 and p1)."""
    try:
        if cell.startswith("t"):
            calls = row.get("tool_calls") or []
            if len(calls) != 1 or not isinstance(calls[0].get("input"), dict):
                return None
            obj = calls[0]["input"]
        else:
            obj = last_object(row.get("text") or "")
    except ValueError:
        return None
    renamed = cell in RENAMED
    key = "property_kind" if renamed else "type"
    wrong_key = "type" if renamed else "property_kind"
    allowed = {"guesthouse", "large_property" if renamed else "hotel"}
    t = obj.get(key)
    vals = t if isinstance(t, list) else ([] if t is None or t in ("any", "null") else [t])
    problems = []
    if key not in obj:
        problems.append(f"no key {key}")
    if wrong_key in obj:
        problems.append(f"key {wrong_key}")
    problems += [f"value {v!r}" for v in vals if v not in allowed]
    return problems


def score(kind, fields):
    return int(kind == "search" and isinstance(fields.get("type"), tuple) and "hotel" in fields["type"])


def load(model):
    rows = jsonl(EXPLORE / MODELS[model] / "raw.jsonl")
    if rows is None:
        return None, None
    reads = collections.defaultdict(list)
    arm = collections.Counter()
    for r in rows:
        _, d, cell, _ = r["custom_id"].split("-")
        reads[(d + ".json", cell)].append(read_row(r, cell))
        p = arm_check(r, cell)
        if p is None:
            arm[(cell, "no object or no single call")] += 1
        for x in p or []:
            arm[(cell, x)] += 1
    return reads, arm


def valid_scores(reads, d, cell):
    return [score(k, f) for k, f in reads.get((d, cell), []) if k != "invalid"]
