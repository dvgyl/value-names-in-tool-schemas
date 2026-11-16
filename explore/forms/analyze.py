"""Measures of PROTOCOL.md for E1, E5, and E6, from <root>/<name>/raw.jsonl to <root>/<name>/summary.json.

Usage: python3 -I analyze.py e1|e5|e6 [--root <folder with the experiment folders>]
"""
import argparse
import collections
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common  # noqa: E402
from common import anth  # noqa: E402

CONTRASTS = {
    "name_effect": {"p4_name": 1, "p4": -1},
    "unclear_effect": {"p4_unclear": 1, "p4": -1},
    "interaction": {"p5": 1, "p4_unclear": -1, "p4_name": -1, "p4": 1},
    "p5_minus_p4": {"p5": 1, "p4": -1},
}
E6_VS_E1 = ["output_tokens_mean", "flip_rate", "ambiguous_list_rate", "ambiguous_multi_list_rate",
            "ambiguous_unclear_rate", "undisputed_unclear_rate", "unclear_rate"]


def rate(n, d):
    return n / d if d else None


def kind(v):
    return "unclear" if v == "unclear" else "null" if v is None else "any" if v == "any" else "list"


def agreement_key(field, v):
    return str(v).strip().lower() if field == "name" and v is not None else v


def load(root, name):
    rows = [json.loads(line) for line in (root / name / "raw.jsonl").read_text().splitlines() if line.strip()]
    ids = [r["custom_id"] for r in rows]
    assert len(ids) == len(set(ids)), f"{name}: duplicate custom_id in raw.jsonl"
    return rows


def summarize_cell(entries, form, reads, market, p4_sets):
    """entries: (dialogue, read, raw row) for one model and form."""
    c, stops, tin, tout = collections.Counter(), collections.Counter(), [], []
    valid = collections.defaultdict(dict)
    for dialogue, read, row in entries:
        if row["type"] != "succeeded":
            c["errors"] += 1
            stops[row["type"]] += 1
            continue
        tin.append(row["input_tokens"])
        tout.append(row["output_tokens"])
        stops[row["stop"]] += 1
        if row["stop"] == "refusal":
            c["refusals"] += 1
        elif row["stop"] == "max_tokens":
            c["truncations"] += 1
        else:
            try:
                valid[dialogue][read] = common.parse(row.get("text") or "")
            except (ValueError, AttributeError):
                c["parse_failures"] += 1
    groups = {"all_fields": None}
    if p4_sets:
        groups.update(ambiguous=p4_sets[0], undisputed=p4_sets[1])
    values = {g: collections.Counter() for g in groups}
    flips = names = n_valid = 0
    for dialogue, by_read in valid.items():
        for ext in by_read.values():
            n_valid += 1
            flips += market.flips(dialogue, ext)
            names += bool(ext["name"])
            for g, members in groups.items():
                for f in common.FIELDS:
                    if members is None or (dialogue, f) in members:
                        k = kind(ext[f])
                        values[g]["fields"] += 1
                        values[g][k] += 1
                        values[g]["multi_list"] += k == "list" and len(ext[f]) > 1
    complete = [list(r.values()) for r in valid.values() if len(r) == reads]
    fields = common.FIELDS + (["name"] if common.FORMS[form].name else [])
    same = {f: sum(len({agreement_key(f, p[f]) for p in r}) == 1 for r in complete) for f in fields}
    identical = sum(all(len({agreement_key(f, p[f]) for p in r}) == 1 for f in fields) for r in complete)
    cell = {
        "requests": len(entries), "valid_reads": n_valid, "errors": c["errors"], "refusals": c["refusals"],
        "truncations": c["truncations"], "parse_failures": c["parse_failures"], "stop_reasons": dict(stops),
        "input_tokens_mean": statistics.mean(tin) if tin else None,
        "output_tokens_mean": statistics.mean(tout) if tout else None,
        "flip_markets": flips, "markets": common.MARKETS * n_valid, "name_filled": names,
        "values": {g: {k: v[k] for k in ("fields", "list", "multi_list", "unclear", "any", "null")}
                   for g, v in values.items()},
        "agreement": {"dialogues_with_all_reads": len(complete), "identical": identical,
                      "per_field": {f: rate(same[f], len(complete)) for f in fields}},
    }
    v = values
    cell["measures"] = {
        "input_tokens_mean": cell["input_tokens_mean"], "output_tokens_mean": cell["output_tokens_mean"],
        "flip_rate": rate(flips, cell["markets"]), "name_rate": rate(names, n_valid),
        "unclear_rate": rate(v["all_fields"]["unclear"], v["all_fields"]["fields"]),
        "identical_share": rate(identical, len(complete)),
        "field_agreement": rate(sum(same[f] for f in common.FIELDS), len(complete) * len(common.FIELDS)),
    }
    if p4_sets:
        cell["measures"].update(
            ambiguous_list_rate=rate(v["ambiguous"]["list"], v["ambiguous"]["fields"]),
            ambiguous_multi_list_rate=rate(v["ambiguous"]["multi_list"], v["ambiguous"]["fields"]),
            ambiguous_unclear_rate=rate(v["ambiguous"]["unclear"], v["ambiguous"]["fields"]),
            undisputed_unclear_rate=rate(v["undisputed"]["unclear"], v["undisputed"]["fields"]))
    return cell


def contrast(weights, by_form):
    out = {}
    for m in next(iter(by_form.values()))["measures"]:
        xs = [(w, by_form[f]["measures"][m]) for f, w in weights.items()]
        out[m] = None if any(x is None for _, x in xs) else sum(w * x for w, x in xs)
    return out


def experiment(root, name, data):
    spec = common.EXPERIMENTS[name]
    ids = common.dialogue_ids(name, data)
    market = common.Market(data, ids)
    p4_sets = common.p4_field_sets(ids) if spec.dialogues == "p4" else None
    rows = load(root, name)
    entries = collections.defaultdict(list)
    for row in rows:
        exp, dialogue, form, read, model = common.split_custom_id(row["custom_id"])
        assert exp == name and form in spec.forms and model in spec.models and 1 <= read <= spec.reads, row["custom_id"]
        assert dialogue in market.draws, f"{dialogue} is not in the {name} dialogue set"
        entries[(model, form)].append((dialogue, read, row))
    cells, missing = {}, []
    for model in spec.models:
        for form in spec.forms:
            if (model, form) not in entries:
                missing.append(f"{model}|{form}")
                continue
            cell = summarize_cell(entries[(model, form)], form, spec.reads, market, p4_sets)
            cell["missing_rows"] = len(ids) * spec.reads - cell["requests"]
            cells.setdefault(common.MODELS[model], {})[form] = cell
    contrasts = {model: {k: contrast(w, by_form) for k, w in CONTRASTS.items() if set(w) <= set(by_form)}
                 for model, by_form in cells.items()}
    return {"experiment": name, "status": "exploratory", "raw": str(root / name / "raw.jsonl"), "rows": len(rows),
            "spec": spec._asdict(), "dialogues": len(ids), "gold": common.GOLD[spec.dialogues],
            "missing_cells": missing, "cells": cells, "contrasts": contrasts}


def e6_vs_e1(e6, e1):
    out = {}
    for model, by_form in e6["cells"].items():
        for form, high in by_form.items():
            low = (e1 or {}).get("cells", {}).get(model, {}).get(form)
            out.setdefault(model, {})[form] = {}
            for m in E6_VS_E1:
                lo, hi = (low["measures"].get(m) if low else None), high["measures"].get(m)
                out[model][form][m] = {"low": lo, "high": hi, "high_minus_low": None if lo is None or hi is None else hi - lo}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("name", choices=sorted(common.EXPERIMENTS))
    ap.add_argument("--root", type=pathlib.Path, default=anth.EXPLORE)
    args = ap.parse_args()
    data = anth.multiwoz()
    summary = experiment(args.root, args.name, data)
    if args.name == "e6":
        e1 = experiment(args.root, "e1", data) if (args.root / "e1" / "raw.jsonl").exists() else None
        summary["e1_reads"] = e1["raw"] if e1 else None
        summary["e6_vs_e1"] = e6_vs_e1(summary, e1)
    (args.root / args.name / "summary.json").write_text(json.dumps(summary, indent=1))
    for model, by_form in summary["cells"].items():
        for form, cell in by_form.items():
            print(f"{args.name} {model} {form}: {cell['valid_reads']}/{cell['requests']} valid reads, "
                  f"flip markets {cell['flip_markets']}/{cell['markets']}, errors {cell['errors']}, "
                  f"refusals {cell['refusals']}, truncations {cell['truncations']}, parse failures {cell['parse_failures']}")
    print(f"wrote {args.root / args.name / 'summary.json'}")


if __name__ == "__main__":
    main()
