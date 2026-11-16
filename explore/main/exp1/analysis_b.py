"""Registration B, Track I: the frozen analysis of the H4 synthetic family (registration B, sections 5 and 5b).

Inputs: the output folder of main/exp1/unseal_track_i.py (one em2i_<model>/raw.jsonl per panel model, and
unseal_manifest.json), the frozen Track I files in main/track_i/, and main/wave2_track_i_manifest.json.
Outputs: RESULT-TRACK-I.md and track_i.json, in main/exp1/ or in the folder that --out names. The script never
overwrites a file, so it runs one time. The content:
1. The H4 synthetic family: 5 contrasts of the silent error, Holm, alpha 0.05; Claim 1 and the anchoring reading.
2. The missing cells and the worst-case sensitivity analysis.
3. Each model's paired effect.
4. Each collision word (description, no test).
5. The secondary outcomes all errors and unsupported commitment (description, no test).
6. The rates per model, schema variant and wording, and the field kinds of the silent errors (description).

The script stops before any write when the input holds a row that is not a Track I answer of the panel: an id of
another form or track, of another model, an id that no Track I request has, or an id that occurs twice. It also stops
when a frozen Track I file differs from its registered SHA-256, or when its own scorer does not score the gold as
correct. It never prints or writes answer text. CHOICES lists each point where the registration was not specific
enough to code, with its reason. CHOICES is part of registration B.

Usage (from explore/): python3 -I main/exp1/analysis_b.py <unseal output folder> [--out <folder>]
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
TRACK = EXPLORE / "main" / "track_i"
MANIFEST = EXPLORE / "main" / "wave2_track_i_manifest.json"
sys.path.insert(0, str(EXPLORE / "r10" / "analysis"))
import stats  # noqa: E402  (r10/analysis/stats.py, the statistics module of registration A, amendment A1)

PANEL = ("sonnet", "haiku", "sol", "luna", "deepseek", "qwen", "gemma")  # the 7 models that ran Track I
FAMILIES = ("onsite", "north", "retail", "large")
WORDINGS = ("collision", "reword_1", "reword_2")
VARIANTS = ("a_legacy", "c_described", "b_renamed", "e_value_renamed")
COLLISION, REWORDS = ("collision",), ("reword_1", "reword_2")
ID = re.compile(r"^em2i_([a-z]+)-(ti-(onsite|north|retail|large)-([0-9]{2})-(collision|reword_1|reword_2)-"
                r"(a_legacy|c_described|b_renamed|e_value_renamed))$")
EXPECTED = {"objects": 100, "objects_per_word": 25, "requests_per_model": 1200}
ALPHA = 0.05  # registration B section 5: one look, alpha 0.05, Holm inside the family
PERMUTATION_DRAWS = 10_000
PERMUTATION_SEED = 2026111301
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20261113
OUTPUTS = ("RESULT-TRACK-I.md", "track_i.json")
PRIMARY = "silent_error"
SECONDARY = ("all_errors", "unsupported_commitment")
SCHEMA_KEYWORDS = {"type", "properties", "required", "additionalProperties", "items", "anyOf", "enum"}

CHOICES = (
    ("family", "The 5 contrasts are registration B section 5, H4 synthetic family, items 1 to 5, in that order, with "
               "Holm over the 5 p values. Each is a paired difference per base object and model."),
    ("panel", "The panel is the 7 models that ran Track I (PANEL). gemini-3.8-flash has no Track I answer at the "
              "filing; if it runs later, its answers do not enter these tests (registration B section 5b)."),
    ("reply", "The reply is the last top-level JSON object in the answer text: the scan starts at each `{` from the "
              "left, and an object that parses moves the scan to its end. No object is a parse failure."),
    ("V0", "V0 is the closed JSON schema of the request's family and variant in main/track_i/schema_snapshot.json "
           "(keys, types, enums, no extra key). A boolean is never a string, and a string is never a boolean."),
    ("V1", "V1 is the typed validator of PLAN SI-05 for the Track I report, on a reply that passes V0. It rejects: an "
           "organization name that is not one of the 6 names of the object (after whitespace and case folding); an "
           "organization twice in `ranking`, twice in `unacceptable`, or in both; two conditions with the same "
           "organization and attribute; a report with all three lists empty; and a label without a canonical "
           "value in the variant's attribute table. Reason: PLAN SI-05 lists unknown values, duplicate or "
           "overlapping organizations and an all-empty report; the SI-05 validator itself does not exist yet."),
    ("canonical", "A V1-valid reply is mapped to the canonical labels by the attribute table of its variant "
                  "(schema_snapshot.json, `attributes`: name to canonical name, label to canonical value), and it "
                  "is compared with `gold_canonical` of main/track_i/gold.jsonl."),
    ("fields", "The fields are those of the repository rule (semantic-integrity si_eval/extraction_task.py, "
               "_erroneous_fields), without valuations: `acceptability:<org>` for each of the 6 organizations "
               "(acceptable = in `ranking`, unacceptable = in `unacceptable`, else unspecified); "
               "`conditions:<org>.<attribute>` for each pair in the gold or the reply; `ranking:full` when the "
               "ranked set differs or two organizations of both rankings change order."),
    ("silent error", "A read scores 1 when it passes V0 and V1 and at least one field differs from the gold, and 0 "
                     "when it passes V0 and V1 and no field differs. Reason: PLAN SI-08, a field value that passes "
                     "V1 and differs from the constructive gold; one read is the unit of a cell."),
    ("missing", "A read is a missing cell for the silent error when it has no row, its row did not succeed, it did "
                "not stop at end_turn, or it fails the parse, V0 or V1. Reason: registration A section 7 (a V0 "
                "failure or a cut reply is a missing cell); a V1 failure is loud, so it is not silent."),
    ("gold check", "Before any answer is scored, the gold of each of the 1,200 requests, in the labels of its "
                   "variant, must pass V0 and V1 and score 0. Else the script stops."),
    ("contrast value", "Per base object and model, a contrast is the sum of its terms, coefficient times the value. "
                       "A term on one wording is the read of that cell. A term on the two rewordings is the mean of "
                       "their valid reads (one or two). A contrast with a term without a value has no value."),
    ("panel mean", "Per base object, the mean of the contrast over the panel models that have a value. A base "
                   "object without any value leaves the test. Each base object has equal weight."),
    ("test", "Two-sided sign-flip permutation test of the mean over base objects (stats.permutation_test), 10,000 "
             "draws, seed PERMUTATION_SEED, the same seed for each contrast. Holm (stats.holm) over the 5 contrasts. "
             "A contrast rejects when its Holm p is 0.05 or less."),
    ("predicted signs", "Contrast 1 (renaming) negative, 2 (descriptions) negative, 3 (wording) positive, 4 "
                        "(interaction) positive, 5 (value label) negative. The tests are two-sided. The signs are "
                        "used by the claim rules (contrasts 1, 3 and 5) and to break a zero mean in the worst case."),
    ("claims", "Claim 1 holds on constructed items when contrasts 3 and 1 reject with the predicted signs. The "
               "anchoring reading holds when Claim 1 holds and contrast 5 rejects with the predicted sign. Reason: "
               "registration B section 5, Claim 1 (decision D1)."),
    ("worst case", "Each missing cell is scored in the direction that shrinks the contrast: against the sign of the "
                   "primary panel mean of that contrast (the predicted sign when the mean is 0). A cell whose term "
                   "has a coefficient of the same sign scores 0, else 1. Then the same test and Holm run again."),
    ("intervals", "Every interval is the 95% percentile interval of stats.cluster_bootstrap, 2,000 draws, "
                  "BOOTSTRAP_SEED. The cluster is the base object."),
    ("per model", "Each model's paired effect is the mean of its contrast values over the base objects, with its "
                  "interval. The exact sign test of each model is a description, not a registered test."),
    ("per word", "Part 4 gives each contrast on the 25 base objects of each collision word, with its interval and no "
                 "test. Reason: PLAN SI-11, the results per collision word as description."),
    ("all errors", "Secondary, no test: a read scores 1 when it fails the parse, V0 or V1, or has a silent error, and "
                   "0 when it passes V1 with no wrong field. A read with no row, a row that did not succeed or a cut "
                   "reply is missing. Reason: PLAN SI-08, all errors add the V0 and V1 failures."),
    ("unsupported commitment", "Secondary, no test: a V1-valid read scores 1 when it states a condition (organization "
                               "and attribute) that the gold does not state, else 0. Reason: PLAN SI-08, a value for "
                               "a field that the text leaves not stated; every Track I text states one condition."),
    ("one read", "Track I has one read per cell (PLAN SI-10). There is no repeat analysis."),
    ("frozen inputs", "Every file of main/track_i/SHA256SUMS must have its hash, the SHA-256 of SHA256SUMS must equal "
                      "track_i_sha256sums of main/wave2_track_i_manifest.json, and the manifest must give 1,200 "
                      "requests for each panel model."),
    ("input check", "The input folder must hold em2i_<model> folders of the panel only, and unseal_manifest.json with "
                    "the same panel. Each raw.jsonl must match the SHA-256 and row count of the manifest. `._*` files "
                    "are ignored."),
)


class Refused(Exception):
    """An input that the frozen analysis does not accept. The script stops before any write."""


class Term(NamedTuple):
    coef: int
    variant: str
    wordings: tuple


class Contrast(NamedTuple):
    number: int
    name: str
    text: str
    terms: tuple
    predicted_sign: int


FAMILY = (
    Contrast(1, "renaming", "b_renamed minus c_described, collision wording",
             (Term(1, "b_renamed", COLLISION), Term(-1, "c_described", COLLISION)), -1),
    Contrast(2, "descriptions", "c_described minus a_legacy, collision wording",
             (Term(1, "c_described", COLLISION), Term(-1, "a_legacy", COLLISION)), -1),
    Contrast(3, "wording", "collision wording minus the mean of the two rewordings, under a_legacy",
             (Term(1, "a_legacy", COLLISION), Term(-1, "a_legacy", REWORDS)), 1),
    Contrast(4, "interaction", "wording effect under a_legacy minus wording effect under b_renamed",
             (Term(1, "a_legacy", COLLISION), Term(-1, "a_legacy", REWORDS), Term(-1, "b_renamed", COLLISION),
              Term(1, "b_renamed", REWORDS)), 1),
    Contrast(5, "value_label", "e_value_renamed minus b_renamed, collision wording",
             (Term(1, "e_value_renamed", COLLISION), Term(-1, "b_renamed", COLLISION)), -1),
)


class Item(NamedTuple):
    request_id: str
    object_id: str
    family: str
    wording: str
    variant: str
    options: tuple  # the 6 organization names of the base object
    schema: dict  # the closed JSON schema of the family and variant
    attributes: dict  # attribute name of the variant -> (canonical name, ((label, canonical value), ...))
    gold: dict  # the gold in the labels of the variant
    gold_canonical: dict


class Report(NamedTuple):
    ranking: tuple
    unacceptable: frozenset
    conditions: dict  # (organization, canonical attribute) -> canonical value


class Read(NamedTuple):
    silent_error: object  # 0, 1 or None (missing)
    all_errors: object
    unsupported_commitment: object
    reason: object  # why the silent error is missing, or None
    kinds: tuple  # the field kinds of the wrong fields


# ---------------------------------------------------------------------------- copied unchanged from main/exp0/analysis.py
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def mean(vals):
    return sum(vals) / len(vals) if vals else None


def interval(vals):
    if not vals:
        return {"n": 0, "mean": None, "ci95": [None, None]}
    point, lo, hi = stats.cluster_bootstrap({"dialogues": vals}, lambda g: mean(g["dialogues"]), BOOTSTRAP_DRAWS,
                                            BOOTSTRAP_SEED)
    return {"n": len(vals), "mean": point, "ci95": [lo, hi]}


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


def pval(p):
    return f"{p:.4f}" if p >= 0.00005 else f"{p:.1e}"


def yes(b):
    return "yes" if b else "no"


# ------------------------------------------------------------------------------------------------- frozen inputs
def check_frozen():
    """Every Track I file has its frozen hash, and the hash list is the one of the wave-2 manifest."""
    for line in (TRACK / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        if sha256(TRACK / name) != digest:
            raise Refused(f"main/track_i/{name} differs from main/track_i/SHA256SUMS")
    man = json.loads(MANIFEST.read_text())
    if sha256(TRACK / "SHA256SUMS") != man.get("track_i_sha256sums"):
        raise Refused("main/track_i/SHA256SUMS differs from track_i_sha256sums of main/wave2_track_i_manifest.json")
    for m in PANEL:
        if man.get("folders", {}).get(f"em2i_{m}", {}).get("requests") != EXPECTED["requests_per_model"]:
            raise Refused(f"main/wave2_track_i_manifest.json gives no {EXPECTED['requests_per_model']} requests "
                          f"for em2i_{m}")


def check_keywords(schema):
    if isinstance(schema, dict):
        extra = set(schema) - SCHEMA_KEYWORDS
        if extra:
            raise Refused(f"a schema keyword that V0 does not know: {sorted(extra)}")
        for key in ("items",):
            if key in schema:
                check_keywords(schema[key])
        for option in schema.get("anyOf", ()):
            check_keywords(option)
        for sub in schema.get("properties", {}).values():
            check_keywords(sub)


def load_items():
    """The 1,200 Track I requests in request order, as Items, with the gold check."""
    check_frozen()
    snapshot = json.loads((TRACK / "schema_snapshot.json").read_text())
    objects = {o["object_id"]: o for o in json.loads((TRACK / "objects.json").read_text())}
    golds = {g["request_id"]: g for g in map(json.loads, (TRACK / "gold.jsonl").read_text().splitlines())}
    items = {}
    for p in map(json.loads, (TRACK / "prompts.jsonl").read_text().splitlines()):
        variant = snapshot["families"][p["family"]]["variants"][p["variant"]]
        check_keywords(variant["json_schema"])
        attributes = {a["name"]: (a["canonical"], tuple((label, canon) for label, canon in a["values"]))
                      for a in variant["attributes"]}
        g = golds[p["request_id"]]
        obj = objects[p["object_id"]]
        if g["gold_canonical"] != obj["gold_canonical"] or g["variant"] != p["variant"]:
            raise Refused(f"the gold of {p['request_id']} differs from objects.json")
        items[p["request_id"]] = Item(p["request_id"], p["object_id"], p["family"], p["wording"], p["variant"],
                                      tuple(obj["entity_names"].values()), variant["json_schema"], attributes,
                                      g["gold"], g["gold_canonical"])
    objs = collections.Counter(it.object_id for it in items.values())
    words = collections.Counter(it.family for it in items.values() if it.wording == "collision"
                                and it.variant == "a_legacy")
    if (len(items) != EXPECTED["requests_per_model"] or len(objs) != EXPECTED["objects"]
            or set(objs.values()) != {len(WORDINGS) * len(VARIANTS)}
            or words != dict.fromkeys(FAMILIES, EXPECTED["objects_per_word"])):
        raise Refused("the Track I requests do not have the registered counts")
    for it in items.values():
        if ID.match(f"em2i_sonnet-{it.request_id}") is None:
            raise Refused(f"the request id {it.request_id} does not have the Track I form")
        if not fits(it.gold, it.schema):
            raise Refused(f"the gold of {it.request_id} does not fit its schema")
        report, why = canonical_report(it.gold, it)
        if why or wrong_fields(gold_report(it), report, it.options):
            raise Refused(f"the scorer does not score the gold of {it.request_id} as correct ({why})")
    return items


def objects_of(items):
    out = collections.defaultdict(list)
    for it in items.values():
        if it.object_id not in out[it.family]:
            out[it.family].append(it.object_id)
    return {f: sorted(out[f]) for f in FAMILIES}


# --------------------------------------------------------------------------------------------------- the scorer
def last_object(text):
    dec, i, last = json.JSONDecoder(), 0, None
    while True:
        i = text.find("{", i)
        if i < 0:
            return last
        try:
            obj, end = dec.raw_decode(text, i)
        except ValueError:
            i += 1
            continue
        if isinstance(obj, dict):
            last = obj
        i = end


def fits(value, schema):
    """V0 for the keywords of SCHEMA_KEYWORDS."""
    if "anyOf" in schema:
        return any(fits(value, option) for option in schema["anyOf"])
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(value, dict):
            return False
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(props):
            return False
        if set(schema.get("required", ())) - set(value):
            return False
        return all(fits(value[k], props[k]) for k in value if k in props)
    if kind == "array":
        return isinstance(value, list) and all(fits(x, schema["items"]) for x in value)
    if kind == "string":
        ok = isinstance(value, str)
    elif kind == "boolean":
        ok = isinstance(value, bool)
    else:
        raise Refused(f"a schema type that V0 does not know: {kind}")
    return ok and ("enum" not in schema or any(type(e) is type(value) and e == value for e in schema["enum"]))


def norm(name):
    return " ".join(name.split()).casefold()


_NONE = object()


def canonical_report(obj, item):
    """V1 on an object that passes V0: (Report in canonical labels, None), or (None, reason)."""
    lookup = {norm(n): n for n in item.options}
    org = lambda s: lookup.get(norm(s))
    ranking = [org(x) for x in obj["ranking"]]
    unacceptable = [org(x) for x in obj["unacceptable"]]
    conds = obj["conditions"]
    if None in ranking or None in unacceptable or any(org(c["organization"]) is None for c in conds):
        return None, "V1 unknown organization"
    if len(set(ranking)) < len(ranking) or len(set(unacceptable)) < len(unacceptable) or set(ranking) & set(unacceptable):
        return None, "V1 duplicate or overlapping organization"
    if not ranking and not unacceptable and not conds:
        return None, "V1 empty report"
    out = {}
    for c in conds:
        attr = item.attributes.get(c["attribute"])
        value = _NONE if attr is None else next(
            (canon for label, canon in attr[1] if type(label) is type(c["required_value"])
             and label == c["required_value"]), _NONE)
        if value is _NONE:
            return None, "V1 value outside the domain"
        key = (org(c["organization"]), attr[0])
        if key in out:
            return None, "V1 duplicate condition"
        out[key] = value
    return Report(tuple(ranking), frozenset(unacceptable), out), None


def gold_report(item):
    g = item.gold_canonical
    return Report(tuple(g["ranking"]), frozenset(g["unacceptable"]),
                  {(c["organization"], c["attribute"]): c["required_value"] for c in g["conditions"]})


def acceptability(report, option):
    if option in report.ranking:
        return "acceptable"
    if option in report.unacceptable:
        return "unacceptable"
    return "unspecified"


def wrong_fields(truth, got, options):
    """The field ids where `got` differs from `truth` (the repository rule, without valuations)."""
    errors = [f"acceptability:{o}" for o in options if acceptability(truth, o) != acceptability(got, o)]
    for o, a in sorted(set(truth.conditions) | set(got.conditions), key=lambda k: (k[0], k[1])):
        if (o, a) not in truth.conditions or (o, a) not in got.conditions \
                or type(truth.conditions[(o, a)]) is not type(got.conditions[(o, a)]) \
                or truth.conditions[(o, a)] != got.conditions[(o, a)]:
            errors.append(f"conditions:{o}.{a}")
    common = [x for x in truth.ranking if x in set(got.ranking)]
    pos_t, pos_g = {x: i for i, x in enumerate(truth.ranking)}, {x: i for i, x in enumerate(got.ranking)}
    changed = set(truth.ranking) != set(got.ranking) or any(
        (pos_t[a] < pos_t[b]) != (pos_g[a] < pos_g[b]) for i, a in enumerate(common) for b in common[i + 1:])
    if changed:
        errors.append("ranking:full")
    return errors


def judge(row, item):
    """One Read per request: the three outcomes, the reason of a missing silent error, and the wrong field kinds."""
    if row is None:
        return Read(None, None, None, "no row", ())
    if row.get("type") != "succeeded":
        return Read(None, None, None, f"row {row.get('type')}", ())
    if row.get("stop") != "end_turn":
        return Read(None, None, None, f"stop {row.get('stop')}", ())
    text = row.get("text")
    obj = last_object(text) if isinstance(text, str) else None
    if obj is None:
        return Read(None, 1, None, "parse", ())
    if not fits(obj, item.schema):
        return Read(None, 1, None, "schema (V0)", ())
    report, why = canonical_report(obj, item)
    if why:
        return Read(None, 1, None, why, ())
    truth = gold_report(item)
    wrong = wrong_fields(truth, report, item.options)
    unsupported = int(any(k not in truth.conditions for k in report.conditions))
    kinds = tuple(sorted({w.split(":")[0] for w in wrong}))
    return Read(int(bool(wrong)), int(bool(wrong)), unsupported, None, kinds)


def score(rows, items, panel):
    """cells[(model, variant, wording)][object] = Read; one read per cell."""
    cells = collections.defaultdict(dict)
    for m in panel:
        got = rows.get(m, {})
        for it in items.values():
            cells[(m, it.variant, it.wording)][it.object_id] = judge(got.get(f"em2i_{m}-{it.request_id}"), it)
    return cells


# ------------------------------------------------------------------------------------------------------ contrasts
def fill_of(coef, sign):
    """The worst-case score of a missing cell: it moves the contrast against `sign`."""
    return 0 if coef * sign > 0 else 1


def term_value(cells, model, term, obj, measure, fill=None):
    vals = []
    for w in term.wordings:
        r = cells.get((model, term.variant, w), {}).get(obj)
        v = None if r is None else getattr(r, measure)
        if v is None:
            v = fill
        if v is not None:
            vals.append(v)
    return mean(vals)


def model_value(cells, model, c, obj, measure=PRIMARY, sign=None):
    total = 0.0
    for t in c.terms:
        v = term_value(cells, model, t, obj, measure, None if sign is None else fill_of(t.coef, sign))
        if v is None:
            return None
        total += t.coef * v
    return total


def panel_values(cells, c, objs, panel, measure=PRIMARY, sign=None):
    out = []
    for o in objs:
        vals = [x for m in panel if (x := model_value(cells, m, c, o, measure, sign)) is not None]
        if vals:
            out.append(sum(vals) / len(vals))
    return out


def sign_of(x, predicted):
    return predicted if not x else (1 if x > 0 else -1)


def direction(x, predicted):
    return "none" if not x else ("as predicted" if x * predicted > 0 else "against the prediction")


def family(cells, objs, panel, signs=None, draws=PERMUTATION_DRAWS, with_interval=True):
    """The 5 tests of the H4 synthetic family: the panel mean of the per-object contrast, the two-sided sign-flip
    permutation p, and Holm over the 5 contrasts."""
    out = []
    for i, c in enumerate(FAMILY):
        vals = panel_values(cells, c, objs, panel, PRIMARY, signs[i] if signs else None)
        row = {"number": c.number, "contrast": c.name, "text": c.text, "objects": len(vals), "mean": mean(vals),
               "p": stats.permutation_test(vals, draws, PERMUTATION_SEED)}
        if with_interval:
            row["ci95"] = interval(vals)["ci95"]
        out.append(row)
    for row, c, adj in zip(out, FAMILY, stats.holm([r["p"] for r in out])):
        row["p_holm"] = adj
        row["reject"] = adj <= ALPHA
        row["predicted_sign"] = c.predicted_sign
        row["direction"] = direction(row["mean"], c.predicted_sign)
    return out


def claims(tests):
    ok = lambda n: tests[n - 1]["reject"] and (tests[n - 1]["mean"] or 0) * FAMILY[n - 1].predicted_sign > 0
    claim1 = ok(3) and ok(1)
    return {"claim1_holds": claim1, "anchoring_reading": claim1 and ok(5)}


def per_model(cells, c, objs, panel, measure=PRIMARY):
    out = {}
    for m in panel:
        vals = [x for o in objs if (x := model_value(cells, m, c, o, measure)) is not None]
        row = interval(vals)
        higher, lower = sum(x > 0 for x in vals), sum(x < 0 for x in vals)
        row.update(positive=higher, negative=lower, sign_p=stats.sign_test(higher, lower))
        out[m] = row
    return out


# ---------------------------------------------------------------------------------------------------- the analysis
def missing_table(cells, panel):
    out = {}
    for m in panel:
        for v in VARIANTS:
            for w in WORDINGS:
                reasons = collections.Counter(r.reason for r in cells.get((m, v, w), {}).values() if r.reason)
                if reasons:
                    out[f"{m} {v} {w}"] = {"missing": sum(reasons.values()), "reasons": dict(sorted(reasons.items()))}
    return out


def rate(reads, measure):
    vals = [getattr(r, measure) for r in reads if getattr(r, measure) is not None]
    return {"k": sum(vals), "n": len(vals)}


def analyse(cells, items, panel):
    by_word = objects_of(items)
    objs = sorted(o for f in FAMILIES for o in by_word[f])
    r = {}
    primary = family(cells, objs, panel)
    r["part1_family"] = {"tests": primary, **claims(primary)}

    signs = [sign_of(t["mean"], c.predicted_sign) for t, c in zip(primary, FAMILY)]
    worst = family(cells, objs, panel, signs=signs)
    reads = [x for (m, _, _), v in cells.items() if m in panel for x in v.values()]
    r["part2_missing"] = {
        "rule": "A read with no row, a row that did not succeed, a cut reply, or a parse, V0 or V1 failure is a "
                "missing cell for the silent error. The primary test leaves it out. The worst case scores it in the "
                "direction that shrinks the contrast.",
        "reads": len(reads), "missing": sum(x.silent_error is None for x in reads),
        "cells": missing_table(cells, panel),
        "worst_case": [{**t, "sign_used": s} for t, s in zip(worst, signs)],
        "same_decisions": [a["reject"] for a in primary] == [b["reject"] for b in worst],
        "same_claims": claims(primary) == claims(worst)}

    r["part3_models"] = {c.name: per_model(cells, c, objs, panel) for c in FAMILY}

    r["part4_words"] = {f: {c.name: interval(panel_values(cells, c, by_word[f], panel)) for c in FAMILY}
                        for f in FAMILIES}

    r["part5_secondary"] = {meas: [{"number": c.number, "contrast": c.name,
                                    **interval(panel_values(cells, c, objs, panel, meas))} for c in FAMILY]
                            for meas in SECONDARY}

    fam_of = {it.object_id: it.family for it in items.values()}
    r["part6_rates"] = {
        "models": {m: {f"{v} {w}": {meas: rate(cells[(m, v, w)].values(), meas) for meas in (PRIMARY, *SECONDARY)}
                       for v in VARIANTS for w in WORDINGS} for m in panel},
        "words": {f: {f"{v} {w}": {meas: rate([x for m in panel for o, x in cells[(m, v, w)].items()
                                               if fam_of[o] == f], meas) for meas in (PRIMARY, *SECONDARY)}
                      for v in VARIANTS for w in WORDINGS} for f in FAMILIES},
        "field_kinds": {m: dict(sorted(collections.Counter(k for v in VARIANTS for w in WORDINGS
                                                           for x in cells[(m, v, w)].values() if x.silent_error
                                                           for k in x.kinds).items())) for m in panel}}
    return r


# ------------------------------------------------------------------------------------------------------- the report
def family_table(tests):
    out = ["| # | Contrast | Objects | Panel mean, points | 95% interval | p | Holm p | Rejects at 0.05 | Direction |",
           "|---|---|---|---|---|---|---|---|---|"]
    for t in tests:
        out.append(f"| {t['number']} | {t['contrast']}: {t['text']} | {t['objects']} | {pts(t['mean'])} | "
                   f"{ci_pts(t['ci95'])} | {pval(t['p'])} | {pval(t['p_holm'])} | {yes(t['reject'])} | "
                   f"{t['direction']} |")
    return out


def model_table(rows):
    out = ["| Model | Objects | Mean paired difference, points | 95% interval | Positive | Negative | "
           "Sign p (description) |", "|---|---|---|---|---|---|---|"]
    for m, x in rows.items():
        out.append(f"| {m} | {x['n']} | {pts(x['mean'])} | {ci_pts(x['ci95'])} | {x['positive']} | {x['negative']} | "
                   f"{pval(x['sign_p'])} |")
    return out


def share(x):
    return f"{x['k']}/{x['n']} ({pct(x['k'] / x['n'] if x['n'] else None)})"


def rate_table(rows, label):
    out = ["| " + label + " | Variant and wording | Silent error | All errors | Unsupported commitment |",
           "|---|---|---|---|---|"]
    for key, cellrows in rows.items():
        out += [f"| {key} | {vw} | {share(x[PRIMARY])} | {share(x['all_errors'])} | "
                f"{share(x['unsupported_commitment'])} |" for vw, x in cellrows.items()]
    return out


def render(r, meta):
    p1, p2, p3, p4, p5, p6 = (r[k] for k in ("part1_family", "part2_missing", "part3_models", "part4_words",
                                             "part5_secondary", "part6_rates"))
    L = ["# Registration B, Track I: the H4 synthetic family", "",
         "Status: confirmatory. The frozen analysis ran one time on the unsealed Track I answers.", "",
         f"- Panel: {', '.join(meta['panel'])}.",
         f"- Base objects: {meta['counts']['objects']} ({meta['counts']['objects_per_word']} per collision word). "
         f"Requests per model: {meta['counts']['requests_per_model']}. One read per request.",
         f"- Alpha {ALPHA}, Holm over the 5 contrasts. Permutation test: {PERMUTATION_DRAWS:,} draws, seed "
         f"{PERMUTATION_SEED}. Bootstrap: {BOOTSTRAP_DRAWS:,} draws, seed {BOOTSTRAP_SEED}.",
         f"- Rows read per model: {', '.join(f'{m} {n}' for m, n in meta['rows'].items())}.", "",
         "## Frozen files (SHA-256)", "", "| File | SHA-256 |", "|---|---|"]
    L += [f"| `{k}` | `{v}` |" for k, v in meta["frozen_sha256"].items()]
    L += ["", "Other inputs:", "", "| File | SHA-256 |", "|---|---|"]
    L += [f"| `{k}` | `{v}` |" for k, v in meta["input_sha256"].items()]

    L += ["", "## 1. The H4 synthetic family", "",
          "Outcome: the silent error of read 1 (a reply that passes V0 and V1 and has a field that differs from the "
          "constructive gold). Per base object: the contrast, averaged over the panel models. Test of the mean: "
          "two-sided sign-flip permutation test. A negative value means fewer silent errors under the first form "
          "of the contrast.", ""]
    L += family_table(p1["tests"])
    L += ["", f"- Claim 1 holds on constructed items (contrasts 3 and 1 reject, with the predicted signs): "
              f"{yes(p1['claim1_holds'])}.",
          f"- The anchoring reading (Claim 1, and contrast 5 rejects with the predicted sign): "
          f"{yes(p1['anchoring_reading'])}."]

    L += ["", "## 2. Missing cells and the worst case", "", p2["rule"], "",
          f"Reads: {p2['reads']}. Missing for the silent error: {p2['missing']}.", ""]
    if p2["cells"]:
        L += ["| Model, variant, wording | Missing | Reasons |", "|---|---|---|"]
        L += [f"| {k} | {v['missing']} | {', '.join(f'{a} {b}' for a, b in v['reasons'].items())} |"
              for k, v in p2["cells"].items()]
    else:
        L += ["No read is missing."]
    L += ["", "Worst case:", ""] + family_table(p2["worst_case"])
    L += ["", f"- The decisions are the same as in section 1: {yes(p2['same_decisions'])}.",
          f"- The claim results are the same as in section 1: {yes(p2['same_claims'])}."]

    L += ["", "## 3. Each model's paired effect", "", "The sign test is a description, not a registered test.", ""]
    for c in FAMILY:
        L += [f"**{c.number}. {c.name}** ({c.text})", ""] + model_table(p3[c.name]) + [""]

    L += ["## 4. Each collision word (description, no test)", "",
          "| Word | Contrast | Objects | Panel mean, points | 95% interval |", "|---|---|---|---|---|"]
    for f, rows in p4.items():
        L += [f"| {f} | {c.number}. {c.name} | {rows[c.name]['n']} | {pts(rows[c.name]['mean'])} | "
              f"{ci_pts(rows[c.name]['ci95'])} |" for c in FAMILY]

    L += ["", "## 5. Secondary outcomes (description, no test)", ""]
    for meas, rows in p5.items():
        L += [f"**{meas}**", "", "| Contrast | Objects | Panel mean, points | 95% interval |", "|---|---|---|---|"]
        L += [f"| {x['number']}. {x['contrast']} | {x['n']} | {pts(x['mean'])} | {ci_pts(x['ci95'])} |" for x in rows]
        L += [""]

    L += ["## 6. Rates (description)", "", "Count of reads with the outcome / reads with a value.", ""]
    L += rate_table(p6["models"], "Model") + [""] + rate_table(p6["words"], "Word")
    L += ["", "Field kinds of the silent errors (reads with at least one wrong field of the kind):", "",
          "| Model | Field kinds |", "|---|---|"]
    L += [f"| {m} | {', '.join(f'{k} {n}' for k, n in v.items()) or '-'} |" for m, v in p6["field_kinds"].items()]

    L += ["", "## Choices (CHOICES)", "", "Where the registration was not specific enough to code a step, the script "
          "uses the plainest reading:", ""]
    L += [f"- **{k}**: {v}" for k, v in CHOICES]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------------------------------------- the run
def check_id(cid, short, expected, where):
    m = ID.match(cid) if isinstance(cid, str) else None
    if not m:
        raise Refused(f"{where}: an id that does not have the Track I form")
    if m.group(1) != short:
        raise Refused(f"{where}: the id {cid} is of another model")
    if cid not in expected:
        raise Refused(f"{where}: no Track I request has the id {cid}")


def read_rows(folder, short, expected):
    path = folder / f"em2i_{short}" / "raw.jsonl"
    if not path.is_file():
        raise Refused(f"em2i_{short}/raw.jsonl does not exist")
    rows = {}
    for n, line in enumerate(path.read_text().splitlines(), 1):
        where = f"em2i_{short}/raw.jsonl line {n}"
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            raise Refused(f"{where} is not JSON") from None
        check_id(row.get("custom_id") if isinstance(row, dict) else None, short, expected, where)
        if row["custom_id"] in rows:
            raise Refused(f"{where}: the id {row['custom_id']} occurs twice")
        rows[row["custom_id"]] = row
    return rows


def check_manifest(folder, panel):
    names = {f"em2i_{m}" for m in panel}
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


def load(folder, panel, items=None):
    """Read and check the unseal output. Returns (cells, items, rows per model)."""
    folder = pathlib.Path(folder)
    items = items or load_items()
    rows = {}
    for m in panel:
        expected = {f"em2i_{m}-{rid}" for rid in items}
        rows[m] = read_rows(folder, m, expected)
    check_manifest(folder, panel)
    return score(rows, items, panel), items, {m: len(v) for m, v in rows.items()}


def run(folder, panel, out):
    folder, out = pathlib.Path(folder), pathlib.Path(out)
    for name in OUTPUTS:
        if (out / name).exists():
            raise Refused(f"{out / name} exists. Nothing is overwritten.")
    if pathlib.Path(stats.__file__).resolve() != (EXPLORE / "r10" / "analysis" / "stats.py").resolve():
        raise Refused("the module r10/analysis/stats.py was imported from another file")
    cells, items, nrows = load(folder, panel)
    results = analyse(cells, items, panel)
    meta = {
        "status": "confirmatory", "panel": list(panel), "alpha": ALPHA,
        "permutation": {"draws": PERMUTATION_DRAWS, "seed": PERMUTATION_SEED},
        "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED},
        "counts": dict(EXPECTED), "rows": nrows,
        "frozen_sha256": {"main/exp1/analysis_b.py": sha256(__file__), "r10/analysis/stats.py": sha256(stats.__file__)},
        "input_sha256": {
            **{f"main/track_i/{name}": sha256(TRACK / name) for name in ("SHA256SUMS", "gold.jsonl", "objects.json",
                                                                       "prompts.jsonl", "schema_snapshot.json")},
            "main/wave2_track_i_manifest.json": sha256(MANIFEST),
            "unseal_manifest.json": sha256(folder / "unseal_manifest.json"),
            **{f"em2i_{m}/raw.jsonl": sha256(folder / f"em2i_{m}" / "raw.jsonl") for m in panel}},
        "choices": dict(CHOICES)}
    report = render(results, meta)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "track_i.json", "x") as fh:
        json.dump(clean({"meta": meta, "results": results}), fh, indent=1)
    with open(out / "RESULT-TRACK-I.md", "x") as fh:
        fh.write(report)
    return results, meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("unsealed", help="the output folder of unseal_track_i.py")
    ap.add_argument("--panel", default=",".join(PANEL), help="comma-separated model short names (default: PANEL)")
    ap.add_argument("--out", default=str(HERE), help="the folder for RESULT-TRACK-I.md and track_i.json")
    args = ap.parse_args(argv)
    panel = [m.strip() for m in args.panel.split(",") if m.strip()]
    try:
        if sorted(panel) != sorted(PANEL):
            raise Refused(f"the panel must be the Track I panel of registration B: {','.join(PANEL)}")
        results, _ = run(args.unsealed, list(PANEL), args.out)
    except Refused as e:
        sys.exit(f"Stopped before any write: {e}")
    for t in results["part1_family"]["tests"]:
        print(f"{t['number']}. {t['contrast']}: {t['objects']} objects, panel mean {pts(t['mean'])} points, "
              f"p {pval(t['p'])}, Holm p {pval(t['p_holm'])}, rejects at {ALPHA}: {yes(t['reject'])}")
    print(f"Claim 1 holds: {yes(results['part1_family']['claim1_holds'])}; anchoring reading: "
          f"{yes(results['part1_family']['anchoring_reading'])}")
    print(f"wrote {pathlib.Path(args.out) / OUTPUTS[0]} and {pathlib.Path(args.out) / OUTPUTS[1]}")


if __name__ == "__main__":
    main()
