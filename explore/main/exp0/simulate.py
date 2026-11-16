"""Simulated unseal output for the test of main/exp0/analysis.py (review/plan15/ACTION-PLAN.md section 2.10).

No model call, no sealed file, no real answer. The script takes the real request ids of wave1.requests(short) and keeps
the stage-1 ids: the parts nat, plc, hot and pre, on the natural and goal-hotel dialogues that are not in the Track P
sample. It writes one simulated answer per id, in the row format of lib/anth.py message_row, and an
unseal_manifest.json in the format of main/exp0/subset_unseal.py. Each answer is a JSON object with the key names and
the hotel token of its form. Its `name` holds MARKER, so a test can check that no answer text leaves the analysis.

The answers come from a known model. Per model and dialogue, the chance of `type = hotel` under t_legacy is
sigmoid(sample base + dialogue effect + model effect). Under another form, the chance is that value minus the form's
entry in the effect table (0 in NULL). Every read is one independent draw.

Usage (from explore/): python3 -I main/exp0/simulate.py <new folder> [--null] [--seed N] [--panel m1,m2,...]
"""
import argparse
import datetime
import hashlib
import json
import math
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import wave1  # noqa: E402

MARKER = "SIMULATED-ANSWER-MARKER"
PANEL = ("sonnet", "haiku", "sol", "luna", "deepseek", "qwen", "gemma")
PARTS = ("nat", "plc", "hot", "pre")
SAMPLE_OF_PART = {"nat": "natural", "plc": "natural", "pre": "natural", "hot": "goal_hotel"}
ID = re.compile(r"^em1_([a-z]+)-(nat|plc|hot|pre|tp)-([A-Z]+[0-9]+)-([a-z0-9_]+)-([0-9])$")
BASE = {("natural", "orig"): -0.5, ("natural", "prefix"): -0.8, ("goal_hotel", "orig"): 1.5}  # logit of t_legacy
EFFECT = {"t_legacy": 0.0, "t_renamed": 0.15, "f4": 0.10, "t_described": 0.03, "f5": 0.0}  # fall of the chance
NULL = dict.fromkeys(EFFECT, 0.0)
MISSING_KINDS = ("errored", "absent", "cut", "schema", "not_json")


def stage1_units(lists):
    sample = set(lists["sample"])
    return {k: {d.removesuffix(".json") for d in lists[k] if d not in sample} for k in ("natural", "goal_hotel")}


def stage1_ids(short, data=None, lists=None):
    """The real stage-1 request ids of one model, in request order (read requests only)."""
    lists = lists or wave1.ids()
    units = stage1_units(lists)
    out = []
    for r in wave1.requests(short, data, lists):
        _, part, d, _, _ = ID.match(r["custom_id"]).groups()
        if part in PARTS and d in units[SAMPLE_OF_PART[part]]:
            out.append(r["custom_id"])
    return out


def answer(form, type_value):
    """The answer text of a form: its keys, its hotel token, and the closed schema's key order."""
    parser = wave1.natural.FORMS[wave1.FORMS[form][2]]
    token = lambda v: parser.hotel if v == "hotel" else v
    value = [token(v) for v in type_value] if isinstance(type_value, list) else type_value
    obj = {"name": MARKER, "area": None, "pricerange": None, "stars": None, "type": value, "parking": None,
           "internet": None}
    return json.dumps({parser.keys.get(k, k): v for k, v in obj.items()})


def _gauss(*key, sd=1.0):
    return random.Random("|".join(map(str, key))).gauss(0.0, sd)


def chance(seed, short, part, d, form, effect):
    sample = SAMPLE_OF_PART[part]
    text = wave1.PARTS[part][2]
    logit = BASE[(sample, text)] + _gauss(seed, sample, d) + _gauss(seed, short, sd=0.5) + _gauss(seed, short, sample, d, sd=0.5)
    return max(0.0, 1 / (1 + math.exp(-logit)) - effect[form])


def type_value(rng, hit):
    if hit:
        return ["hotel"] if rng.random() < 0.85 else ["hotel", "guesthouse"]
    x = rng.random()
    return None if x < 0.5 else ["guesthouse"] if x < 0.8 else "any"


def row(short, cid, text, stop="end_turn"):
    return {"custom_id": cid, "type": "succeeded", "model": wave1.natural.MODELS[short].id, "stop": stop,
            "input_tokens": 900, "output_tokens": 40, "text": text}


def missing_row(short, cid, kind):
    """One request that gives no valid read, of a named kind."""
    _, _, _, form, _ = ID.match(cid).groups()
    if kind == "errored":
        return {"custom_id": cid, "type": "errored", "status": 500, "error": MARKER}
    if kind == "absent":
        return {"custom_id": cid, "type": "absent"}
    if kind == "cut":
        return row(short, cid, answer(form, ["hotel"])[:30], stop="max_tokens")
    if kind == "schema":  # parses, but `type` holds a value that the closed schema does not allow (a V0 failure)
        return row(short, cid, answer(form, ["motel"]))
    if kind == "not_json":
        return row(short, cid, MARKER + " no object here")
    raise ValueError(kind)


def rows(short, ids, effect=EFFECT, seed=1, missing=None):
    """One simulated row per id. `missing` maps an id to a kind of MISSING_KINDS."""
    missing = missing or {}
    out = []
    for cid in ids:
        if cid in missing:
            out.append(missing_row(short, cid, missing[cid]))
            continue
        _, part, d, form, _ = ID.match(cid).groups()
        rng = random.Random(f"{seed}|{cid}")
        hit = rng.random() < chance(seed, short, part, d, form, effect)
        out.append(row(short, cid, answer(form, type_value(rng, hit))))
    return out


def write_rows(out, short, folder_rows):
    target = pathlib.Path(out) / f"em1_{short}" / "raw.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes("".join(json.dumps(r) + "\n" for r in folder_rows).encode())


def write_manifest(out, panel):
    """unseal_manifest.json in the format of subset_unseal.py, from the raw.jsonl files that are in `out` now."""
    out = pathlib.Path(out)
    manifest = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(), "panel": list(panel), "folders": {}}
    for short in panel:
        data = (out / f"em1_{short}" / "raw.jsonl").read_bytes()
        manifest["folders"][f"em1_{short}"] = {"rows": data.count(b"\n"), "sha256": hashlib.sha256(data).hexdigest()}
    (out / "unseal_manifest.json").write_text(json.dumps(manifest, indent=1))


def write(out, effect=EFFECT, seed=1, panel=PANEL, missing=None, data=None, lists=None):
    """A complete fake unseal folder. The folder must be new or empty."""
    out = pathlib.Path(out)
    if out.exists() and any(p for p in out.iterdir() if not p.name.startswith("._")):
        sys.exit(f"Stopped: {out} is not empty.")
    data, lists = data or wave1.anth.multiwoz(), lists or wave1.ids()
    for short in panel:
        write_rows(out, short, rows(short, stage1_ids(short, data, lists), effect, seed, missing))
    write_manifest(out, panel)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("--null", action="store_true", help="no effect of any form")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--panel", default=",".join(PANEL))
    args = ap.parse_args(argv)
    panel = [m.strip() for m in args.panel.split(",") if m.strip()]
    write(args.out, NULL if args.null else EFFECT, args.seed, panel)
    print(f"wrote a simulated unseal folder ({'no effect' if args.null else 'known effect'}, seed {args.seed}) "
          f"into {args.out}")


if __name__ == "__main__":
    main()
