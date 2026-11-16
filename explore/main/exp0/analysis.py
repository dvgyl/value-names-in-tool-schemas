"""Experiment 0, stage 1: the frozen analysis of the held-out H4 natural test (registration A sections 4 to 8,
amendment A1 of review/plan14/fable-review.md section 6.1, review/plan15/ACTION-PLAN.md section 2.10).

Inputs: the output folder of main/exp0/subset_unseal.py (one em1_<model>/raw.jsonl per model of the interim panel, and
unseal_manifest.json), main/wave1_ids.json, the MultiWOZ 2.4 data and hotel_db.json.
Outputs: RESULT-STAGE1.md and stage1.json, in main/exp0/ or in the folder that --out names. The script never
overwrites a file. The content follows the order of ACTION-PLAN section 2.10:
1. The H4 natural family (2 tests, alpha 0.025 for this look, Holm over the 2 tests).
2. The registered missing-cell rule and its worst-case sensitivity analysis.
3. Each model's paired effect, and the repeat reads as a sensitivity analysis.
4. The registered secondary outcomes.
5. The new outcomes of amendment A1: (a) no-venue dialogues, (b) search failure, (c) the trade ratio with its
   interval, (d) the mixed model, removed (MIXED_MODEL is False).

The script stops before any write when a row has an id that stage 1 does not allow: an id of the wrong form, the part
tp, a dialogue of the Track P sample or of the gate set, or an id that no stage-1 request has. It never prints or
writes answer text. CHOICES lists each point where the registration was not specific enough to code, with its reason.

Usage (from explore/): python3 -I main/exp0/analysis.py <unseal output folder> [--panel m1,m2,...] [--out <folder>]
"""
import argparse
import collections
import hashlib
import json
import math
import pathlib
import re
import sys
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parents[1]
sys.path.insert(0, str(EXPLORE / "main"))
import wave1  # noqa: E402  (it puts lib, forms, r9/natural and r9/additions on the path)
sys.path.insert(0, str(EXPLORE / "r10"))
sys.path.insert(0, str(EXPLORE / "r10" / "analysis"))
import briefsearch as bs  # noqa: E402
import stats  # noqa: E402
import zruns  # noqa: E402

PANEL = ("sonnet", "haiku", "sol", "luna", "deepseek", "qwen", "gemma")  # A1: the 7 models that are not Google models
PARTS = ("nat", "plc", "hot", "pre")  # the stage-1 parts; tp is never read
SAMPLE_OF_PART = {"nat": "natural", "plc": "natural", "pre": "natural", "hot": "goal_hotel"}
EXPECTED = {"natural": 213, "goal_hotel": 77, "natural_repeat": 43, "goal_hotel_repeat": 13}
ID = re.compile(r"^em1_([a-z]+)-(nat|plc|hot|pre|tp)-([A-Z]+[0-9]+)-([a-z0-9_]+)-([0-9])$")
ALPHA = 0.025  # A1: alpha for each of the two looks
PREDICTED_SIGN = -1  # registration A section 3: t_renamed lower than t_legacy in both tests
PERMUTATION_DRAWS = 10_000
PERMUTATION_SEED = 2026111201
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20261112  # the default of r10/analysis/stats.py (ACTION-PLAN section 3.1)
TRADE_SIZES = {"nat": 281, "hot": 97}  # registration A section 4: the natural and goal-hotel samples
FIRST, MEAN = "read 1", "mean of reads"
OUTPUTS = ("RESULT-STAGE1.md", "stage1.json")
MIXED_MODEL = False  # A1 outcome (d): removed, because no machine of the project has statsmodels at the freeze
MIXED_MODEL_TEXT = "outcome (d) removed: no package"
if MIXED_MODEL:
    raise SystemExit("MIXED_MODEL is True, but this frozen script has no mixed-model code.")

CHOICES = (
    ("family", "The two tests are registration A section 7 items 1 and 2: t_renamed minus t_legacy on the natural "
               "sample (part nat), and on the goal-hotel sample (part hot), stage-1 dialogues only."),
    ("outcome", "A read scores 1 when its parsed `type` list holds `hotel` after the form's mapping back "
                "(wave1.FORMS parser of r9/natural/natural.py; the E8 measure of natural_analyze.hotel), else 0."),
    ("valid read", "A read is valid when its row succeeded, stopped at end_turn, its last JSON object parses and fits "
                   "the closed schema of its form. Reason: section 7 makes a V0 failure or a cut reply a missing "
                   "cell, and PLAN.md defines V0 as schema validity."),
    ("primary missing", "A model enters the panel mean of a dialogue only when both of its cells are valid. A dialogue "
                        "with no valid pair leaves the test. Reason: section 7 gives no imputation for the primary "
                        "test; the worst case is its sensitivity analysis."),
    ("panel mean", "Each model with a valid pair has equal weight in a dialogue, and each dialogue has equal weight "
                   "in the mean. Reason: section 7, average over the panel models per dialogue."),
    ("worst-case direction", "A missing cell is scored against the sign of the primary panel mean of its test (the "
                             "predicted sign, negative, when the mean is 0). For a negative mean, a missing t_renamed "
                             "cell scores 1 and a missing t_legacy cell scores 0. Reason: section 7, the direction "
                             "that shrinks the paired difference."),
    ("decision", "A test rejects when its Holm-adjusted p is 0.025 or less. Reason: A1 alpha 0.025 for this look."),
    ("repeat means", "The repeat sensitivity analysis replaces read 1 by the mean of the valid reads of each cell (3 "
                     "reads on the repeat dialogues, 1 elsewhere), with the same test and seed. Reason: section 7."),
    ("read 1 elsewhere", "Every secondary and A1 outcome uses read 1 only. Reason: read 1 is the primary read."),
    ("secondary statistics", "A secondary contrast gives each model's mean paired difference and the panel mean, each "
                             "with a 95% interval, and no p value. Reason: section 7, 'no test'."),
    ("sign counts", "Part 3 also shows the exact sign test of each model as a description, not as a registered test. "
                    "Reason: ACTION-PLAN section 3.4 gives each per-model contrast the sign test."),
    ("intervals", "Every interval is the 95% percentile interval of stats.cluster_bootstrap, 2,000 draws, "
                  "BOOTSTRAP_SEED. The cluster is the dialogue."),
    ("placebo net", "The placebo effect is f5 (part plc) minus t_legacy (part nat). The net wrong-value effect is "
                    "t_renamed minus f5 on the dialogues where both cells are valid, per Claude model and for the "
                    "mean of the Claude models of the panel. Reason: decision D4, effect minus placebo effect."),
    ("prefix exclusion", "The booked venue is zruns.booked_venue (the last booked name, matched to hotel_db.json). A "
                         "read excludes it when its `type` is a list without the venue's type (zanalyze "
                         "excludes_type). Dialogues without a matched booking leave this share."),
    ("trade sizes", "The trade weights are the registered sample sizes, natural 281 (wrong values) and goal-hotel 97 "
                    "(correct values). Reason: the interim and the final look then estimate the same ratio."),
    ("trade estimator", "The trade is stats.trade_interval on read 1 of the dialogues with both cells valid. Wrong "
                        "group nat, correct group hot. The panel row adds the read-1 values of all panel models per "
                        "dialogue. Part 4 gives the point values, part 5(c) the interval."),
    ("no venue", "A goal names no venue when goal.hotel.info has no `name` (briefsearch.brief_of). On the natural "
                 "sample this is briefsearch.brief_subsets 'no_name'. On the goal-hotel sample the no-type condition "
                 "of brief_subsets cannot hold, so only the name rule applies."),
    ("search failure", "Search failure is briefsearch.search_failure of read 1. The denominator is every valid read 1 "
                       "on the dialogues whose brief sets no type (all stage-1 natural dialogues). Parts nat, plc "
                       "and pre. Reason: ROUND10-EXPERIMENT-PLAN.md and harm_by_model.py use that denominator."),
    ("search failure fit", "briefsearch.search_failure also requires that some venue fits the brief. On the 213 "
                           "dialogues this changes nothing: each of the 128 with no fitting hotel has a fitting venue."),
    ("commitment", "Any type commitment is a parsed `type` that is a list (not null, 'any' or 'unclear'). An empty "
                   "list parses to None, so it is not a commitment."),
    ("claims", "claim1_transfers and anchoring_reading also require the direction 't_renamed lower'. Reason: "
               "registration A section 3, both contrasts reject in the same direction, the predicted one."),
    ("mixed model", "Outcome (d) is removed: MIXED_MODEL is False, because no machine of the project has "
                    "statsmodels at the freeze (amendment A1). The script has no mixed-model code."),
    ("panel check", "The panel must be PANEL, the interim panel of A1. The panel of the manifest must equal it, and "
                    "each raw.jsonl must match the SHA-256 and row count of the manifest. A directory of the input "
                    "that is not a panel folder stops the script; `._*` files are ignored."),
    ("forms", "The form hashes of wave1.FORMS (prompt and schema) must equal forms_sha256 of main/wave1_manifest.json, "
              "so the scoring schemas are the registered ones."),
)


class Refused(Exception):
    """An input that the frozen analysis does not accept. The script stops before any write."""


class Contrast(NamedTuple):
    name: str
    sample: str  # "natural" or "goal_hotel"
    form: tuple  # (part, form)
    base: tuple  # (part, form)
    claude_only: bool = False


FAMILY = (
    Contrast("wrong_values", "natural", ("nat", "t_renamed"), ("nat", "t_legacy")),
    Contrast("correct_values_kept", "goal_hotel", ("hot", "t_renamed"), ("hot", "t_legacy")),
)
F4 = tuple(Contrast(f"f4_{s}", s, (p, "f4"), (p, "t_legacy")) for s, p in (("natural", "nat"), ("goal_hotel", "hot")))
DESCRIBED = tuple(Contrast(f"t_described_{s}", s, (p, "t_described"), (p, "t_legacy"))
                  for s, p in (("natural", "nat"), ("goal_hotel", "hot")))
PLACEBO = Contrast("placebo", "natural", ("plc", "f5"), ("nat", "t_legacy"), True)
PLACEBO_NET = Contrast("placebo_net", "natural", ("nat", "t_renamed"), ("plc", "f5"), True)
REGISTERED = FAMILY + F4 + DESCRIBED + (PLACEBO,)


# ---------------------------------------------------------------------------------------------------------- inputs
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def form_hashes():
    """The form hashes of wave1.write_manifest: SHA-256 of the system prompt plus the sorted JSON of the format."""
    return {f: hashlib.sha256((s + json.dumps(fmt, sort_keys=True)).encode()).hexdigest()
            for f, (s, fmt, _) in wave1.FORMS.items()}


def stage1_units(lists):
    """The stage-1 dialogues (ids without .json): natural and goal-hotel dialogues outside the Track P sample."""
    sample, gate = set(lists["sample"]), set(lists["gate"])
    units = {k: [d for d in lists[k] if d not in sample] for k in ("natural", "goal_hotel")}
    repeat = {k: [d for d in lists[f"{k}_repeat"] if d in set(units[k])] for k in units}
    counts = {**{k: len(v) for k, v in units.items()}, **{f"{k}_repeat": len(v) for k, v in repeat.items()}}
    if counts != EXPECTED:
        raise Refused(f"the stage-1 counts of wave1_ids.json are {counts}, not {EXPECTED}")
    if any(d in sample or d in gate for v in units.values() for d in v):
        raise Refused("a stage-1 dialogue is in the Track P sample or in the gate set")
    strip = lambda ids: [d.removesuffix(".json") for d in ids]
    return {k: strip(v) for k, v in units.items()}, {k: set(strip(v)) for k, v in repeat.items()}


def allowed_ids(short, units, data, lists):
    """The stage-1 request ids of one model, in request order: wave1.requests filtered to the stage-1 parts and units."""
    keep = {k: set(v) for k, v in units.items()}
    out = []
    for r in wave1.requests(short, data, lists):
        _, part, d, _, _ = ID.match(r["custom_id"]).groups()
        if part in PARTS and d in keep[SAMPLE_OF_PART[part]]:
            out.append(r["custom_id"])
    return out


def check_id(cid, short, allowed, sample, gate, where):
    """Stop on any id that stage 1 does not allow. The message names the id only when it has the wave-1 form."""
    m = ID.match(cid) if isinstance(cid, str) else None
    if not m:
        raise Refused(f"{where}: an id that does not have the wave-1 form")
    model, part, d, _, _ = m.groups()
    if model != short:
        raise Refused(f"{where}: the id {cid} is of another model")
    if part == "tp":
        raise Refused(f"{where}: the id {cid} is of part tp, which stage 1 never reads")
    if d + ".json" in sample:
        raise Refused(f"{where}: the id {cid} is of a Track P sample dialogue")
    if d + ".json" in gate:
        raise Refused(f"{where}: the id {cid} is of a gate-set dialogue")
    if cid not in allowed:
        raise Refused(f"{where}: no stage-1 request has the id {cid}")


def read_rows(folder, short, allowed, lists):
    path = folder / f"em1_{short}" / "raw.jsonl"
    if not path.is_file():
        raise Refused(f"em1_{short}/raw.jsonl does not exist")
    sample, gate, allowed = set(lists["sample"]), set(lists["gate"]), set(allowed)
    rows = {}
    for n, line in enumerate(path.read_text().splitlines(), 1):
        where = f"em1_{short}/raw.jsonl line {n}"
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            raise Refused(f"{where} is not JSON") from None
        check_id(row.get("custom_id") if isinstance(row, dict) else None, short, allowed, sample, gate, where)
        if row["custom_id"] in rows:
            raise Refused(f"{where}: the id {row['custom_id']} occurs twice")
        rows[row["custom_id"]] = row
    return rows


def check_manifest(folder, panel):
    names = {f"em1_{m}" for m in panel}
    extra = sorted(p.name for p in folder.iterdir() if not p.name.startswith("._") and p.is_dir() and p.name not in names)
    if extra:
        raise Refused(f"folders that are not in the panel: {', '.join(extra)}")
    path = folder / "unseal_manifest.json"
    if not path.is_file():
        raise Refused("unseal_manifest.json does not exist")
    man = json.loads(path.read_text())
    if set(man.get("panel", ())) != set(panel) or set(man.get("folders", {})) != names:
        raise Refused("the panel of unseal_manifest.json is not the panel of the analysis")
    for name, info in man["folders"].items():
        raw = (folder / name / "raw.jsonl").read_bytes()
        if hashlib.sha256(raw).hexdigest() != info.get("sha256") or raw.count(b"\n") != info.get("rows"):
            raise Refused(f"{name}/raw.jsonl does not match unseal_manifest.json")
    return man


# --------------------------------------------------------------------------------------------------------- scoring
def _check_shape(option):
    kind = option.get("type")
    if kind == "array":
        _check_shape(option["items"])
    elif kind not in ("null", "string"):
        raise ValueError(f"a schema option of an unknown kind: {option}")


SCHEMAS = {f: wave1.FORMS[f][1]["schema"] for f in wave1.NAT + ("f5",)}
for _s in SCHEMAS.values():
    assert _s.get("additionalProperties") is False and set(_s["required"]) == set(_s["properties"])
    for _p in _s["properties"].values():
        for _o in _p["anyOf"]:
            _check_shape(_o)


def fits_option(v, option):
    kind = option["type"]
    if kind == "null":
        return v is None
    if kind == "string":
        return isinstance(v, str) and ("enum" not in option or v in option["enum"])
    return isinstance(v, list) and all(fits_option(x, option["items"]) for x in v)


def fits_schema(obj, schema):
    """V0: the answer object fits the closed JSON schema of its form."""
    props = schema["properties"]
    return (isinstance(obj, dict) and set(obj) == set(props)
            and all(any(fits_option(obj[k], o) for o in props[k]["anyOf"]) for k in obj))


def judge(row, form):
    """(parsed fields, None) for a valid read; (None, reason) for a missing cell."""
    if row is None:
        return None, "no row"
    if row.get("type") != "succeeded":
        return None, f"row {row.get('type')}"
    if row.get("stop") != "end_turn":
        return None, f"stop {row.get('stop')}"
    text = row.get("text")
    if not isinstance(text, str):
        return None, "parse"
    try:
        obj = json.loads(text[text.rfind("{"):text.rfind("}") + 1])
    except ValueError:
        return None, "parse"
    if not fits_schema(obj, SCHEMAS[form]):
        return None, "schema (V0)"
    try:
        return wave1.natural.parse(text, wave1.natural.FORMS[wave1.FORMS[form][2]]), None
    except (ValueError, KeyError, TypeError, AttributeError):
        return None, "parse"


def score(rows, expected):
    """cells[(model, part, form)][dialogue][read] = parsed fields or None; missing[(model, part, form)] = Counter of
    (read 1 or not, reason)."""
    cells = collections.defaultdict(dict)
    missing = collections.defaultdict(collections.Counter)
    for short, ids in expected.items():
        got = rows.get(short, {})
        for cid in ids:
            _, part, d, form, r = ID.match(cid).groups()
            fields, reason = judge(got.get(cid), form)
            cells[(short, part, form)].setdefault(d, {})[int(r)] = fields
            if reason:
                missing[(short, part, form)][(int(r) == 1, reason)] += 1
    return cells, missing


def hotel(f, d=None):
    t = f["type"]
    return isinstance(t, tuple) and "hotel" in t


def commits(f, d=None):
    return isinstance(f["type"], tuple)


def value(cells, model, cell, d, measure=hotel, reads=FIRST):
    got = cells.get((model, *cell), {}).get(d, {})
    if reads == FIRST:
        f = got.get(1)
        return None if f is None else int(measure(f, d))
    vals = [int(measure(f, d)) for f in got.values() if f is not None]
    return sum(vals) / len(vals) if vals else None


def worst_fill(sign):
    """(score of a missing form cell, score of a missing base cell) that moves the difference against `sign`."""
    return (1, 0) if sign < 0 else (0, 1)


def model_diff(cells, model, c, d, reads=FIRST, fill=None, measure=hotel):
    a, b = value(cells, model, c.form, d, measure, reads), value(cells, model, c.base, d, measure, reads)
    if fill:
        a, b = fill[0] if a is None else a, fill[1] if b is None else b
    return None if a is None or b is None else a - b


def contrast_models(c, panel):
    return [m for m in panel if not c.claude_only or m in wave1.CLAUDE]


def panel_values(cells, c, units, panel, reads=FIRST, fill=None):
    """Per dialogue, the mean paired difference over the models with a value; dialogues without one leave."""
    out = []
    for d in units:
        diffs = [x for m in contrast_models(c, panel) if (x := model_diff(cells, m, c, d, reads, fill)) is not None]
        if diffs:
            out.append(sum(diffs) / len(diffs))
    return out


def mean(vals):
    return sum(vals) / len(vals) if vals else None


def interval(vals):
    if not vals:
        return {"n": 0, "mean": None, "ci95": [None, None]}
    point, lo, hi = stats.cluster_bootstrap({"dialogues": vals}, lambda g: mean(g["dialogues"]), BOOTSTRAP_DRAWS,
                                            BOOTSTRAP_SEED)
    return {"n": len(vals), "mean": point, "ci95": [lo, hi]}


def sign_of(x):
    return PREDICTED_SIGN if not x else (1 if x > 0 else -1)


# ------------------------------------------------------------------------------------------------------ the tests
def family(cells, units, panel, draws=PERMUTATION_DRAWS, reads=FIRST, fills=None, with_interval=True):
    """The two tests of the H4 natural family: the panel mean of the per-dialogue paired differences, the two-sided
    sign-flip permutation p, and Holm over the two tests."""
    out = []
    for i, c in enumerate(FAMILY):
        vals = panel_values(cells, c, units[c.sample], panel, reads, fills[i] if fills else None)
        row = {"test": c.name, "sample": c.sample, "form": "t_renamed", "base": "t_legacy", "dialogues": len(vals),
               "mean": mean(vals), "p": stats.permutation_test(vals, draws, PERMUTATION_SEED)}
        if with_interval:
            row["ci95"] = interval(vals)["ci95"]
        out.append(row)
    for row, adj in zip(out, stats.holm([r["p"] for r in out])):
        row["p_holm"] = adj
        row["reject"] = adj <= ALPHA
        row["direction"] = "none" if not row["mean"] else ("t_renamed lower" if row["mean"] < 0 else "t_renamed higher")
    return out


def per_model(cells, c, units, panel, reads=FIRST, signs=False):
    out = {}
    for m in contrast_models(c, panel):
        diffs = [x for d in units if (x := model_diff(cells, m, c, d, reads)) is not None]
        row = interval(diffs)
        if signs:
            higher, lower = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
            row.update(form_higher=higher, form_lower=lower, sign_p=stats.sign_test(higher, lower))
        out[m] = row
    return out


def contrast_block(cells, c, units, panel, reads=FIRST, signs=False):
    return {"contrast": c.name, "sample": c.sample, "form": list(c.form), "base": list(c.base),
            "panel": interval(panel_values(cells, c, units, panel, reads)),
            "models": per_model(cells, c, units, panel, reads, signs)}


def share_block(cells, model, cell, units, measure):
    vals = [v for d in units if (v := value(cells, model, cell, d, measure)) is not None]
    row = interval(vals)
    return {"k": sum(vals), "n": row["n"], "share": row["mean"], "ci95": row["ci95"]}


def trade_rows(cells, models, form, units):
    """stats.trade cells: per group, one row (k0, n0, k1, n1) per dialogue with both read-1 cells valid; the read-1
    values of the given models are added."""
    out = {}
    for group, sample in (("nat", "natural"), ("hot", "goal_hotel")):
        rows = []
        for d in units[sample]:
            pairs = [(a, b) for m in models if (a := value(cells, m, (group, "t_legacy"), d)) is not None
                     and (b := value(cells, m, (group, form), d)) is not None]
            if pairs:
                rows.append((sum(a for a, _ in pairs), len(pairs), sum(b for _, b in pairs), len(pairs)))
        out[group] = rows
    return out


def trade_block(cells, models, form, units):
    rows = trade_rows(cells, models, form, units)
    paired = {g: len(r) for g, r in rows.items()}
    if not all(rows.values()):
        return {"paired_dialogues": paired, "removed": None, "lost": None, "ratio": None, "ci95": [None, None]}
    (removed, lost, ratio), lo, hi = stats.trade_interval(rows, TRADE_SIZES, BOOTSTRAP_DRAWS, BOOTSTRAP_SEED,
                                                          wrong=("nat",), correct="hot")
    return {"paired_dialogues": paired, "removed": removed, "lost": lost, "ratio": ratio, "ci95": [lo, hi],
            "removed_positive": removed > 0}


# ---------------------------------------------------------------------------------------------------- the analysis
def missing_table(missing, panel):
    out = {}
    for (m, part, form), counter in sorted(missing.items()):
        if m not in panel or not counter:
            continue
        first = {reason: n for (is_first, reason), n in counter.items() if is_first}
        out[f"{m} {part} {form}"] = {"read1": sum(first.values()), "all_reads": sum(counter.values()),
                                     "read1_reasons": first}
    return out


def analyse(cells, missing, units, repeat, data, db, panel):
    nat, hot = units["natural"], units["goal_hotel"]
    r = {}
    primary = family(cells, units, panel)
    r["part1_family"] = {
        "tests": primary,
        "claim1_transfers": primary[0]["reject"] and (primary[0]["mean"] or 0) < 0,
        "anchoring_reading": all(t["reject"] and (t["mean"] or 0) < 0 for t in primary)}

    signs = [sign_of(t["mean"]) for t in primary]
    worst = family(cells, units, panel, fills=[worst_fill(s) for s in signs])
    expected_cells = sum(len(cells.get((m, *c.form), {})) + len(cells.get((m, *c.base), {}))
                         for c in FAMILY for m in panel)
    r["part2_missing"] = {
        "rule": "A V0 failure, a cut reply, or any other request without a valid read is a missing cell. The primary "
                "test leaves it out. The worst case scores it in the direction that shrinks the paired difference.",
        "family_read1_cells": expected_cells,
        "family_read1_missing": sum(n for c in FAMILY for m in panel for cell in (c.form, c.base)
                                    for (first, _), n in missing.get((m, *cell), {}).items() if first),
        "cells": missing_table(missing, panel),
        "worst_case": [{**t, "fill_direction": "missing t_renamed scores 1, missing t_legacy scores 0" if s < 0
                        else "missing t_renamed scores 0, missing t_legacy scores 1"} for t, s in zip(worst, signs)],
        "same_decisions": [a["reject"] for a in primary] == [b["reject"] for b in worst]}

    r["part3_models"] = {
        "read1": {c.name: per_model(cells, c, units[c.sample], panel, FIRST, signs=True) for c in FAMILY},
        "repeat_dialogues": {k: len(v) for k, v in repeat.items()},
        "repeat_means_family": family(cells, units, panel, reads=MEAN),
        "repeat_means_models": {c.name: per_model(cells, c, units[c.sample], panel, MEAN) for c in FAMILY}}

    by_key = {zruns._key(h["name"]): h for h in db}
    venue = {d: v for d in nat if (v := zruns.booked_venue(data[d + ".json"], by_key))}
    excludes = lambda f, d: isinstance(f["type"], tuple) and venue[d]["type"] not in f["type"]
    pre_cells = [("pre", f) for f in wave1.NAT]
    commit_cells = [(p, f) for p in ("nat", "hot", "pre") for f in wave1.NAT] + [("plc", "f5")]
    r["part4_secondary"] = {
        "f4": [contrast_block(cells, c, units[c.sample], panel) for c in F4],
        "t_described": [contrast_block(cells, c, units[c.sample], panel) for c in DESCRIBED],
        "placebo": {"claude_models": contrast_models(PLACEBO, panel),
                    "placebo_effect": contrast_block(cells, PLACEBO, nat, panel),
                    "net_wrong_value_effect": contrast_block(cells, PLACEBO_NET, nat, panel)},
        "prefix": {"booked_venue_dialogues": len(venue),
                   "type_hotel": {m: {c[1]: share_block(cells, m, c, nat, hotel) for c in pre_cells} for m in panel},
                   "excludes_booked_type": {m: {c[1]: share_block(cells, m, c, sorted(venue), excludes)
                                                for c in pre_cells} for m in panel}},
        "commitment": {m: {f"{p} {f}": share_block(cells, m, (p, f), units[SAMPLE_OF_PART[p]], commits)
                           for p, f in commit_cells if (m, p, f) in cells} for m in panel}}

    trades = {f: {**{m: trade_block(cells, [m], f, units) for m in panel}, "panel": trade_block(cells, panel, f, units)}
              for f in ("t_renamed", "f4")}
    r["part4_secondary"]["trade_points"] = {f: {m: {k: t[k] for k in ("paired_dialogues", "removed", "lost", "ratio")}
                                                for m, t in rows.items()} for f, rows in trades.items()}

    no_name = {"natural": [d for d in nat if not bs.brief_of(data[d + ".json"]).get("name")],
               "goal_hotel": [d for d in hot if not bs.brief_of(data[d + ".json"]).get("name")]}
    subsets = bs.brief_subsets(data, [d + ".json" for d in nat], db)
    if [d + ".json" for d in no_name["natural"]] != subsets["no_name"]:
        raise Refused("the no-venue rule differs from briefsearch.brief_subsets")
    no_type = [d.removesuffix(".json") for d in subsets["no_type"]]
    no_hotel_fits = set(subsets["no_hotel_fits"])
    failure = lambda f, d: bs.search_failure(f, data[d + ".json"], db)
    fail_cells = [("nat", f) for f in wave1.NAT] + [("plc", "f5")] + [("pre", f) for f in wave1.NAT]
    r["part5_a1"] = {
        "a_no_venue": {"dialogues": {k: len(v) for k, v in no_name.items()},
                       "contrasts": [contrast_block(cells, c, no_name[c.sample], panel) for c in REGISTERED]},
        "b_search_failure": {"no_type_dialogues": len(no_type), "no_hotel_fits_dialogues": len(subsets["no_hotel_fits"]),
                             "dialogues_that_can_fail": sum(1 for d in no_type if d + ".json" in no_hotel_fits
                                                            and bs.brief_fitting(data[d + ".json"], db)),
                             "models": {m: {f"{p} {f}": share_block(cells, m, (p, f), no_type, failure)
                                            for p, f in fail_cells if (m, p, f) in cells} for m in panel}},
        "c_trade": trades,
        "d_mixed_model": {"status": "removed", "text": MIXED_MODEL_TEXT}}
    return r


# ------------------------------------------------------------------------------------------------------- the report
def clean(x):
    if isinstance(x, float):
        return None if math.isinf(x) or math.isnan(x) else round(x, 6)
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    return x


def pts(x):
    return "-" if x is None else f"{100 * x:+.1f}"


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def ci_pts(ci):
    return "-" if ci[0] is None else f"[{100 * ci[0]:+.1f}, {100 * ci[1]:+.1f}]"


def ci_pct(ci):
    return "-" if ci[0] is None else f"[{100 * ci[0]:.1f}%, {100 * ci[1]:.1f}%]"


def num(x, digits=2):
    return "not defined" if x is None or (isinstance(x, float) and (math.isinf(x) or math.isnan(x))) else f"{x:.{digits}f}"


def pval(p):
    return f"{p:.4f}" if p >= 0.00005 else f"{p:.1e}"


def yes(b):
    return "yes" if b else "no"


def family_table(tests):
    out = ["| Test | Sample | Dialogues | Panel mean, points | 95% interval | p | Holm p | Rejects at 0.025 |",
           "|---|---|---|---|---|---|---|---|"]
    for t in tests:
        out.append(f"| {t['test']} | {t['sample']} | {t['dialogues']} | {pts(t['mean'])} | {ci_pts(t['ci95'])} | "
                   f"{pval(t['p'])} | {pval(t['p_holm'])} | {yes(t['reject'])} |")
    return out


def model_table(rows, signs=False):
    head = "| Model | Dialogues | Mean paired difference, points | 95% interval |"
    out = [head + (" Form higher | Form lower | Sign p (description) |" if signs else ""),
           "|---|---|---|---|" + ("---|---|---|" if signs else "")]
    for m, x in rows.items():
        line = f"| {m} | {x['n']} | {pts(x['mean'])} | {ci_pts(x['ci95'])} |"
        if signs:
            line += f" {x['form_higher']} | {x['form_lower']} | {pval(x['sign_p'])} |"
        out.append(line)
    return out


def contrast_lines(b):
    p = b["panel"]
    out = [f"**{b['contrast']}**: {b['form'][1]} (part {b['form'][0]}) minus {b['base'][1]} (part {b['base'][0]}), "
           f"{b['sample']} sample. Panel mean {pts(p['mean'])} points {ci_pts(p['ci95'])}, {p['n']} dialogues.", ""]
    return out + model_table(b["models"]) + [""]


def share_table(rows, label):
    out = [label, "", "| Model | Cell | Hits/reads | Share | 95% interval |", "|---|---|---|---|---|"]
    for m, v in rows.items():
        out += [f"| {m} | {c} | {x['k']}/{x['n']} | {pct(x['share'])} | {ci_pct(x['ci95'])} |" for c, x in v.items()]
    return out + [""]


def trade_table(rows, with_ci):
    out = ["| Model | Paired dialogues (nat, hot) | Wrong values removed | Correct values lost | Ratio |"
           + (" 95% interval |" if with_ci else ""), "|---|---|---|---|---|" + ("---|" if with_ci else "")]
    for m, t in rows.items():
        pd_ = t["paired_dialogues"]
        line = (f"| {m} | {pd_['nat']}, {pd_['hot']} | {num(t['removed'], 1)} | {num(t['lost'], 1)} | "
                f"{num(t['ratio']) if t['removed'] is None or t['removed'] > 0 else 'not defined (removed <= 0)'} |")
        if with_ci:
            line += f" [{num(t['ci95'][0])}, {num(t['ci95'][1])}] |"
        out.append(line)
    return out


def render(r, meta):
    p1, p2, p3, p4, p5 = (r[k] for k in ("part1_family", "part2_missing", "part3_models", "part4_secondary",
                                         "part5_a1"))
    L = ["# Experiment 0, stage 1: the held-out test of H4 natural (interim look)", "",
         "Status: held-out. The frozen analysis ran once on the stage-1 answers. Section 9 of RESULTS-R10.md copies "
         "this file without a change.", "",
         f"- Panel: {', '.join(meta['panel'])}.",
         f"- Parts: {', '.join(PARTS)}. The part tp is not read.",
         f"- Dialogues: natural {meta['counts']['natural']} ({meta['counts']['natural_repeat']} with repeat reads), "
         f"goal-hotel {meta['counts']['goal_hotel']} ({meta['counts']['goal_hotel_repeat']} with repeat reads).",
         f"- Alpha {ALPHA} for this look, Holm over the 2 tests. Permutation test: {PERMUTATION_DRAWS:,} draws, seed "
         f"{PERMUTATION_SEED}. Bootstrap: {BOOTSTRAP_DRAWS:,} draws, seed {BOOTSTRAP_SEED}.",
         f"- Rows read per model: {', '.join(f'{m} {n}' for m, n in meta['rows'].items())}.", "",
         "## Frozen files (SHA-256)", "", "| File | SHA-256 |", "|---|---|"]
    L += [f"| `{k}` | `{v}` |" for k, v in meta["frozen_sha256"].items()]
    L += ["", "Other inputs:", "", "| File | SHA-256 |", "|---|---|"]
    L += [f"| `{k}` | `{v}` |" for k, v in meta["input_sha256"].items()]

    L += ["", "## 1. The H4 natural family", "",
          "Per dialogue: the paired difference `t_renamed` minus `t_legacy` of read 1, `type = hotel`, averaged over "
          "the panel models. Test of the mean: two-sided sign-flip permutation test. A negative value means fewer "
          "`type = hotel` reads under `t_renamed`. The prediction is negative for both tests.", ""]
    L += family_table(p1["tests"])
    L += ["", f"- Claim 1 transfers to natural dialogue (the wrong-value test rejects, `t_renamed` lower): "
              f"{yes(p1['claim1_transfers'])}.",
          f"- The anchoring reading (both tests reject, both lower): {yes(p1['anchoring_reading'])}."]

    L += ["", "## 2. Missing cells and the worst case", "", p2["rule"], "",
          f"Read-1 cells of the family: {p2['family_read1_cells']}. Missing: {p2['family_read1_missing']}.", ""]
    if p2["cells"]:
        L += ["| Model, part, form | Missing read 1 | Missing, all reads | Reasons (read 1) |", "|---|---|---|---|"]
        L += [f"| {k} | {v['read1']} | {v['all_reads']} | "
              f"{', '.join(f'{a} {b}' for a, b in sorted(v['read1_reasons'].items())) or '-'} |"
              for k, v in p2["cells"].items()]
    else:
        L += ["No cell of the stage-1 parts is missing."]
    L += ["", "Worst case:", ""] + family_table(p2["worst_case"])
    L += [""] + [f"- {t['test']}: {t['fill_direction']}." for t in p2["worst_case"]]
    L += [f"- The decisions are the same as in section 1: {yes(p2['same_decisions'])}."]

    L += ["", "## 3. Each model's paired effect", "",
          "Read 1. The sign test is a description, not a registered test.", ""]
    for name, rows in p3["read1"].items():
        L += [f"**{name}**", ""] + model_table(rows, signs=True) + [""]
    L += ["### 3b. Repeat reads (sensitivity analysis)", "",
          f"Repeat dialogues in stage 1: natural {p3['repeat_dialogues']['natural']}, goal-hotel "
          f"{p3['repeat_dialogues']['goal_hotel']}. Each cell value is the mean of its valid reads.", ""]
    L += family_table(p3["repeat_means_family"]) + [""]
    for name, rows in p3["repeat_means_models"].items():
        L += [f"**{name}**, repeat means", ""] + model_table(rows) + [""]

    L += ["## 4. Registered secondary outcomes", "", "No test. Each value has its 95% interval.", "",
          "### 4.1 `f4` against `t_legacy`", ""]
    for b in p4["f4"]:
        L += contrast_lines(b)
    L += ["### 4.2 `t_described` against `t_legacy`", ""]
    for b in p4["t_described"]:
        L += contrast_lines(b)
    L += ["### 4.3 The placebo (Claude models)", "",
          f"Claude models of the panel: {', '.join(p4['placebo']['claude_models']) or 'none'}.", ""]
    L += contrast_lines(p4["placebo"]["placebo_effect"]) + contrast_lines(p4["placebo"]["net_wrong_value_effect"])
    L += ["### 4.4 The prefix", ""]
    L += share_table(p4["prefix"]["type_hotel"], "Share of read 1 with `type = hotel` on the prefix, per form.")
    L += share_table(p4["prefix"]["excludes_booked_type"],
                     f"Share of read 1 whose `type` excludes the type of the booked venue, on the "
                     f"{p4['prefix']['booked_venue_dialogues']} dialogues with a matched booking.")
    L += ["### 4.5 The trade ratio (point values)", "",
          "Correct values lost per wrong value removed, against `t_legacy`. Weights: natural 281, goal-hotel 97.", ""]
    for f, rows in p4["trade_points"].items():
        L += [f"**{f}**", ""] + trade_table(rows, False) + [""]
    L += ["### 4.6 Any `type` commitment", ""]
    L += share_table(p4["commitment"], "Share of read 1 whose `type` is a list. Cell: part and form.")

    L += ["## 5. New outcomes of amendment A1", "", "### (a) Contrasts on the dialogues whose goal names no venue", "",
          f"Dialogues: natural {p5['a_no_venue']['dialogues']['natural']}, goal-hotel "
          f"{p5['a_no_venue']['dialogues']['goal_hotel']}.", ""]
    for b in p5["a_no_venue"]["contrasts"]:
        L += contrast_lines(b)
    b5 = p5["b_search_failure"]
    L += ["### (b) Search failure per model and form", ""]
    L += share_table(b5["models"], f"Read 1 whose `type` keeps hotel and "
                                   f"not guesthouse, on a dialogue where no hotel fits the brief, as a share of all "
                                   f"valid read 1 on the {b5['no_type_dialogues']} dialogues whose brief sets no type. "
                                   f"No hotel fits the brief on {b5['no_hotel_fits_dialogues']} dialogues; another "
                                   f"venue fits on {b5['dialogues_that_can_fail']} of them.")
    L += ["### (c) The trade ratio with its 95% interval", ""]
    for f, rows in p5["c_trade"].items():
        L += [f"**{f}**", ""] + trade_table(rows, True) + [""]
    L += ["### (d) The mixed model", "", p5["d_mixed_model"]["text"] + "."]

    L += ["", "## Choices (CHOICES)", "", "Where the registration was not specific enough to code a step, the script "
          "uses the plainest reading:", ""]
    L += [f"- **{k}**: {v}" for k, v in CHOICES]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------------------------------------- the run
def load(folder, panel, data=None, lists=None):
    """Read and check the unseal output. Returns (cells, missing, units, repeat, rows per model, manifest)."""
    folder = pathlib.Path(folder)
    lists, data = lists or wave1.ids(), data or wave1.anth.multiwoz()
    units, repeat = stage1_units(lists)
    expected = {m: allowed_ids(m, units, data, lists) for m in panel}
    rows = {m: read_rows(folder, m, expected[m], lists) for m in panel}
    manifest = check_manifest(folder, panel)
    cells, missing = score(rows, expected)
    return cells, missing, units, repeat, {m: len(v) for m, v in rows.items()}, manifest


def run(folder, panel, out):
    folder, out = pathlib.Path(folder), pathlib.Path(out)
    for name in OUTPUTS:
        if (out / name).exists():
            raise Refused(f"{out / name} exists. Nothing is overwritten.")
    for path, rel in ((pathlib.Path(bs.__file__), "r10/briefsearch.py"), (pathlib.Path(stats.__file__),
                                                                          "r10/analysis/stats.py")):
        if path.resolve() != (EXPLORE / rel).resolve():
            raise Refused(f"the module {rel} was imported from another file")
    registered = json.loads(wave1.MANIFEST.read_text())["forms_sha256"]
    if form_hashes() != registered:
        raise Refused("the form hashes of wave1.FORMS differ from forms_sha256 of main/wave1_manifest.json")
    data, lists, db = wave1.anth.multiwoz(), wave1.ids(), bs.gold.hotel_db()
    cells, missing, units, repeat, nrows, _ = load(folder, panel, data, lists)
    results = analyse(cells, missing, units, repeat, data, db, panel)
    meta = {
        "status": "held-out", "panel": list(panel), "parts": list(PARTS), "alpha": ALPHA,
        "permutation": {"draws": PERMUTATION_DRAWS, "seed": PERMUTATION_SEED},
        "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED}, "trade_sizes": TRADE_SIZES,
        "counts": {**{k: len(v) for k, v in units.items()}, **{f"{k}_repeat": len(v) for k, v in repeat.items()}},
        "rows": nrows,
        "frozen_sha256": {"main/exp0/analysis.py": sha256(__file__), "r10/briefsearch.py": sha256(bs.__file__),
                          "r10/analysis/stats.py": sha256(stats.__file__)},
        "input_sha256": {
            "main/wave1.py": sha256(wave1.__file__), "main/wave1_ids.json": sha256(wave1.IDS),
            "main/wave1_manifest.json": sha256(wave1.MANIFEST),
            "r9/natural/natural.py": sha256(wave1.natural.__file__), "forms/common.py": sha256(wave1.common.__file__),
            "pmain/e13.py": sha256(wave1.e13.__file__), "r9/free/gold.py": sha256(bs.gold.__file__),
            "r9/additions/zforms.py": sha256(wave1.zforms.__file__), "lib/anth.py": sha256(wave1.anth.__file__),
            "r9/additions/zruns.py": sha256(zruns.__file__), "hotel_db.json": sha256(wave1.anth.DATA / "hotel_db.json"),
            "data.json (MultiWOZ 2.4)": sha256(wave1.anth.DATA / "data.json"),
            "unseal_manifest.json": sha256(folder / "unseal_manifest.json"),
            **{f"em1_{m}/raw.jsonl": sha256(folder / f"em1_{m}" / "raw.jsonl") for m in panel}},
        "choices": dict(CHOICES)}
    report = render(results, meta)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "stage1.json", "x") as fh:
        json.dump(clean({"meta": meta, "results": results}), fh, indent=1)
    with open(out / "RESULT-STAGE1.md", "x") as fh:
        fh.write(report)
    return results, meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("unsealed", help="the output folder of subset_unseal.py")
    ap.add_argument("--panel", default=",".join(PANEL), help="comma-separated model short names (default: A1 panel)")
    ap.add_argument("--out", default=str(HERE), help="the folder for RESULT-STAGE1.md and stage1.json")
    args = ap.parse_args(argv)
    panel = [m.strip() for m in args.panel.split(",") if m.strip()]
    try:
        if sorted(panel) != sorted(PANEL):
            raise Refused(f"the panel must be the interim panel of A1: {','.join(PANEL)}")
        results, _ = run(args.unsealed, list(PANEL), args.out)
    except Refused as e:
        sys.exit(f"Stopped before any write: {e}")
    for t in results["part1_family"]["tests"]:
        print(f"{t['test']}: {t['dialogues']} dialogues, panel mean {pts(t['mean'])} points, p {pval(t['p'])}, "
              f"Holm p {pval(t['p_holm'])}, rejects at {ALPHA}: {yes(t['reject'])}")
    print(f"wrote {pathlib.Path(args.out) / OUTPUTS[0]} and {pathlib.Path(args.out) / OUTPUTS[1]}")


if __name__ == "__main__":
    main()
