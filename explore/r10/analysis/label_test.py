"""Analysis of amendment R10-18 (prototypes/explore/PROTOCOL.md): the label test with one fixed definition. Exploratory.

Arms: l_hotel ("type: guesthouse, hotel (any venue type that is not a guesthouse).") and l_code (the same line with
category_A). Runs: erl_sonnet and erl_sonnet_hb (Sonnet), erl_haiku, erl_sol, erl_luna. Sets: 807 no-type briefs,
233 hotel briefs, and the word-rule split of the 233 (89 stated, 140 not stated).

Definitions (fixed in R10-18 before any call):
- A valid read: the row succeeded, it did not stop at the output cap, and labeltest.parse accepts it.
- Hotel value (primary): the scored type list holds hotel. Hotel-only value (secondary): it holds hotel, not guesthouse.
- Per dialogue and model: the share of each arm is the mean over its valid reads; D = share(l_code) - share(l_hotel)
  in points, over the dialogues with a valid read in both arms.
- Panel: per dialogue, the mean of D over the models with a valid pair; the panel D of a set is the mean over its
  dialogues. 95% percentile cluster bootstrap over dialogues (2,000 draws, seed 20261112); two-sided sign-flip
  permutation test (10,000 draws, seed 20261114).

Usage (from explore/):
    python3 -I r10/analysis/label_test.py            # the fetched raw.jsonl files
    python3 -I r10/analysis/label_test.py --pilot    # the pilot_raw.jsonl files
    python3 -I r10/analysis/label_test.py --selftest # fake answers, known effect
Outputs: r10/analysis/out/label_test.json and label_test.md (--pilot: label_test_pilot.*; --selftest: nothing).
This file is a copy of the project analysis of the label test with the paths of the study folder; the results are the same.
No model call, no network call. It opens no folder whose name starts with "em", no *.sealed file and no key file.
"""
import collections
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import clear_rule as cr  # noqa: E402
import labeltest as lt  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"  # explore/r10/analysis/out
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}  # b_analyze.CUT
FOLDERS = {"sonnet": ("erl_sonnet", "erl_sonnet_hb"), "haiku": ("erl_haiku",), "sol": ("erl_sol",),
           "luna": ("erl_luna",)}
MODELS = tuple(FOLDERS)
SETS = ("no_type", "hotel", "stated", "not_stated")
BOOT_SEED, PERM_SEED, DRAWS, PERM_DRAWS = 20261112, 20261114, 2000, 10_000
F6_STORED = {"sonnet": 2.4, "haiku": 2.3, "sol": 27.5, "luna": 2.7}  # R10-18 table, no-type set, percent


def rows_of(folder, pilot):
    assert not folder.startswith("em"), f"refused: {folder}"
    path = EXPLORE / folder / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None


def read_of(row):
    """(dialogue id, cell, read, parsed fields or None, reason)."""
    _, d, cell, read = row["custom_id"].split("-")
    if row.get("type", "succeeded") != "succeeded":
        return d + ".json", cell, int(read), None, "failed"
    if row.get("stop") in CUT:
        return d + ".json", cell, int(read), None, "cut"
    try:
        return d + ".json", cell, int(read), lt.parse(cell, row.get("text", "")), "valid"
    except (ValueError, KeyError, TypeError, IndexError):
        return d + ".json", cell, int(read), None, "no parse"


def hit(fields, outcome):
    t = fields["type"]
    has = isinstance(t, tuple) and "hotel" in t
    return has and not (outcome == "hotel_only" and "guesthouse" in t)


def load(pilot):
    """{model: {(d, cell): [parsed, ...]}}, {model: {cell: Counter(reason)}}, missing folders."""
    reads, counts, missing = {}, {}, []
    for m, folders in FOLDERS.items():
        got, c = collections.defaultdict(list), collections.defaultdict(collections.Counter)
        for f in folders:
            rr = rows_of(f, pilot)
            if rr is None:
                missing.append(f)
                continue
            for row in rr:
                d, cell, _, parsed, why = read_of(row)
                c[cell][why] += 1
                if parsed is not None:
                    got[(d, cell)].append(parsed)
        reads[m], counts[m] = got, {k: dict(v) for k, v in c.items()}
    return reads, counts, missing


def set_ids(data, g):
    s = lt.sets(data, g)
    rule = {d: cr.label(data[d]) for d in s["hotel"]}
    return {"no_type": s["no_type"], "hotel": s["hotel"],
            "stated": [d for d in s["hotel"] if rule[d] == "hotel_only"],
            "not_stated": [d for d in s["hotel"] if rule[d] == "unclear"]}, collections.Counter(rule.values())


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def shares(got, ids, outcome):
    """{d: (l_hotel share, l_code share)} over the dialogues with a valid read in both arms; and the arm shares over
    every dialogue with a valid read of that arm."""
    pairs, arm = {}, {c: [] for c in lt.CELLS}
    for d in ids:
        v = {c: [hit(x, outcome) for x in got.get((d, c), [])] for c in lt.CELLS}
        for c in lt.CELLS:
            if v[c]:
                arm[c].append(mean(v[c]))
        if v["l_hotel"] and v["l_code"]:
            pairs[d] = (mean(v["l_hotel"]), mean(v["l_code"]))
    return pairs, {c: (None if not x else 100 * mean(x), len(x)) for c, x in arm.items()}


def effect(diffs):
    """Mean D in points, 95% cluster bootstrap, permutation p, sign counts and sign p."""
    if not diffs:
        return {"dialogues": 0, "D": None, "low": None, "high": None, "perm_p": None, "up": 0, "down": 0,
                "sign_p": None}
    point, lo, hi = stats.cluster_bootstrap({"all": [(x,) for x in diffs]},
                                            lambda g: sum(t[0] for t in g["all"]) / len(g["all"]),
                                            draws=DRAWS, seed=BOOT_SEED)
    up, down = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    return {"dialogues": len(diffs), "D": point, "low": lo, "high": hi,
            "perm_p": stats.permutation_test(diffs, draws=PERM_DRAWS, seed=PERM_SEED), "up": up, "down": down,
            "sign_p": stats.sign_test(up, down)}


def trade(nt, st, ns):
    """The value trade of l_code against l_hotel, as verify.py item 3 (in dialogues): removed = sum over the no-type
    set of (l_hotel - l_code); lost on the stated and not-stated sets the same. Ratios brief, T1, T2 with intervals."""
    g = {"nt": list(nt.values()), "st": list(st.values()), "ns": list(ns.values())}
    if not all(g.values()):
        return {"dialogues": {k: len(v) for k, v in g.items()}, "note": "a set has no pair"}
    inf = float("inf")

    def ratios(x):
        dm = lambda rows: sum(a - b for a, b in rows)  # noqa: E731
        removed, lost_st, lost_ns = dm(x["nt"]), dm(x["st"]), dm(x["ns"])
        return {"brief": (lost_st + lost_ns) / removed if removed > 0 else inf,
                "T1": lost_st / removed if removed > 0 else inf,
                "T2": lost_st / (removed + lost_ns) if removed + lost_ns > 0 else inf,
                "removed": removed, "lost_stated": lost_st, "lost_not_stated": lost_ns}
    out = {"dialogues": {k: len(v) for k, v in g.items()}, **ratios(g)}
    for key in ("brief", "T1", "T2"):
        _, lo, hi = stats.cluster_bootstrap(g, lambda x, key=key: ratios(x)[key], draws=DRAWS, seed=BOOT_SEED)
        out[f"{key}_ci95"] = [lo, hi]
    return out


def analyse(reads, ids):
    """Per outcome: per model and panel, per set: arm shares and the paired effect; and the value trade."""
    res = {}
    for outcome in ("hotel", "hotel_only"):
        per, pair_all = {}, {}
        for m in MODELS:
            per[m] = {}
            for s in SETS:
                pairs, arm = shares(reads.get(m, {}), ids[s], outcome)
                pair_all[(m, s)] = pairs
                per[m][s] = {"l_hotel": arm["l_hotel"], "l_code": arm["l_code"],
                             **effect([100 * (b - a) for a, b in pairs.values()])}
            per[m]["trade"] = trade(pair_all[(m, "no_type")], pair_all[(m, "stated")], pair_all[(m, "not_stated")])
        panel, pooled = {}, {}
        for s in SETS:
            by_d = collections.defaultdict(list)
            for m in MODELS:
                for d, p in pair_all[(m, s)].items():
                    by_d[d].append(p)
            pooled[s] = {d: (mean(a for a, _ in v), mean(b for _, b in v)) for d, v in by_d.items()}
            panel[s] = {"models_per_dialogue": mean(len(v) for v in by_d.values()),
                        "l_hotel": None if not pooled[s] else 100 * mean(a for a, _ in pooled[s].values()),
                        "l_code": None if not pooled[s] else 100 * mean(b for _, b in pooled[s].values()),
                        **effect([100 * mean(b - a for a, b in v) for v in by_d.values()])}
        panel["trade"] = trade(pooled["no_type"], pooled["stated"], pooled["not_stated"])
        res[outcome] = {"models": per, "panel": panel}
    return res


def predictions(res):
    """L1 to L5 and the categories against the shared-word reading (R10-18), on the primary outcome."""
    p, sonnet = res["hotel"]["panel"], res["hotel"]["models"]["sonnet"]
    nt, st, ns = p["no_type"], p["stated"], p["not_stated"]

    def below(e, lim):
        return None if e["D"] is None else bool(e["D"] <= lim and e["high"] < 0)

    def inside(e, a, b):
        return None if e["D"] is None else bool(a <= e["low"] and e["high"] <= b)
    out = {"L1": below(nt, -3.0), "L2": below(sonnet["no_type"], -5.0), "L3": below(ns, -10.0),
           "L4": None if st["D"] is None or ns["D"] is None else bool(abs(st["D"]) < abs(ns["D"]) and st["D"] >= -8.0)}
    l5 = {}
    for m in MODELS:
        x = res["hotel"]["models"][m]["no_type"]["l_code"][0]
        l5[m] = None if x is None else bool(abs(x - F6_STORED[m]) <= 3.0)
    out["L5"] = l5
    against = {"a_inside_3": inside(nt, -3.0, 3.0), "b_reversed": None if nt["D"] is None else bool(nt["low"] > 0),
               "c_sonnet_inside_3": inside(sonnet["no_type"], -3.0, 3.0)}
    out["against"] = against
    if out["L1"]:
        verdict = "shared word acts (L1 holds)"
    elif against["a_inside_3"] or against["b_reversed"]:
        verdict = "meaning reading (against the shared-word reading)"
    elif against["c_sonnet_inside_3"]:  # R10-18 (c): the meaning reading for Sonnet only
        verdict = "meaning reading for Sonnet (category c); otherwise unresolved"
    elif nt["D"] is None:
        verdict = "no data"
    else:
        verdict = "unresolved"
    out["verdict"] = verdict
    pv = [nt["perm_p"], ns["perm_p"]]
    out["holm_L1_L3"] = stats.holm(pv) if None not in pv else None
    return out


def stored_references(data, ids):
    """Stored development reads on the same sets (descriptions): F0 of erb_<model> (round 10, experiment B) and the
    round-9 F6 (the l_code requests) and F1 reads. Percent, mean over dialogues of the per-dialogue share."""
    import b_analyze as B
    import natural_analyze as na
    out = {}
    for m in MODELS:
        per = collections.defaultdict(list)
        for row in rows_of(f"erb_{m}", False) or []:
            d, arm, _ = B.split(row["custom_id"])
            if arm == "f0":
                v = B.parse_row(row, arm, None)
                if v is not None:
                    per[d].append(na.hotel(v["type"]))
        out[(m, "f0_round10")] = {s: share_of(per, ids[s]) for s in SETS}
    r9, _ = na.load()
    for m in MODELS:
        for f in ("f6", "f1"):
            rr = r9.get((m, f), {})
            per = {d + ".json": list(map(na.hotel, v)) for d, v in rr.items()}
            out[(m, f"{f}_round9")] = {s: share_of(per, ids[s]) for s in SETS}
    return {f"{m}|{k}": v for (m, k), v in out.items()}


def share_of(per, ids):
    vals = [mean(per[d]) for d in ids if per.get(d)]
    return [None if not vals else round(100 * mean(vals), 1), len(vals)]


def fmt(x, nd=1):
    return "n/a" if x is None else f"{x:.{nd}f}"


def markdown(res, preds, counts, missing, refs, rule_counts, pilot):
    lines = [f"# Label test with one fixed definition (R10-18){' — PILOT ANSWERS' if pilot else ''}", "",
             "Exploratory, fixed in the protocol before the run. D = share(l_code) − share(l_hotel), in points.", ""]
    if missing:
        lines += [f"Missing folders: {', '.join(missing)}.", ""]
    lines += [f"Word rule on the 233 hotel briefs: {dict(rule_counts)}.", ""]
    for outcome in ("hotel", "hotel_only"):
        lines += [f"## Outcome: {outcome} value", "",
                  "| Model | Set | l_hotel % (n) | l_code % (n) | pairs | D | 95% interval | perm p | up/down |",
                  "|---|---|---:|---:|---:|---:|---|---:|---:|"]
        rows = [(m, res[outcome]["models"][m]) for m in MODELS] + [("panel", res[outcome]["panel"])]
        for m, e in rows:
            for s in SETS:
                x = e[s]
                lh = x["l_hotel"] if m == "panel" else x["l_hotel"][0]
                lc = x["l_code"] if m == "panel" else x["l_code"][0]
                nh = "" if m == "panel" else f" ({x['l_hotel'][1]})"
                nc = "" if m == "panel" else f" ({x['l_code'][1]})"
                lines.append(f"| {m} | {s} | {fmt(lh)}{nh} | {fmt(lc)}{nc} | {x['dialogues']} | {fmt(x['D'])} | "
                             f"[{fmt(x['low'])}, {fmt(x['high'])}] | {fmt(x['perm_p'], 4)} | {x['up']}/{x['down']} |")
        t = res[outcome]["panel"]["trade"]
        if "brief" in t:
            lines += ["", f"Panel value trade (l_code against l_hotel, in dialogues): removed {t['removed']:.1f}, lost "
                          f"stated {t['lost_stated']:.1f}, lost not stated {t['lost_not_stated']:.1f}; brief "
                          f"{t['brief']:.2f} {fmt_ci(t['brief_ci95'])}, T1 {t['T1']:.2f} {fmt_ci(t['T1_ci95'])}, "
                          f"T2 {t['T2']:.2f} {fmt_ci(t['T2_ci95'])}."]
        lines.append("")
    lines += ["## Predictions (primary outcome)", ""]
    for k in ("L1", "L2", "L3", "L4"):
        lines.append(f"- {k}: {status(preds[k])}")
    lines.append("- L5 (l_code within 3 points of the stored round-9 F6 on the no-type set): "
                 + ", ".join(f"{m} {status(v)}" for m, v in preds["L5"].items()))
    lines.append("- Against the shared-word reading: " + ", ".join(f"{k} {status(v)}" for k, v in preds["against"].items()))
    lines.append(f"- Category: {preds['verdict']}.")
    if preds["holm_L1_L3"]:
        lines.append(f"- Holm-adjusted p of L1 and L3 (description): {fmt(preds['holm_L1_L3'][0], 4)}, "
                     f"{fmt(preds['holm_L1_L3'][1], 4)}.")
    lines += ["", "## Reads per arm", ""]
    for m in MODELS:
        lines.append(f"- {m}: " + "; ".join(f"{c} {counts[m].get(c, {})}" for c in lt.CELLS))
    if refs:
        lines += ["", "## Stored references (other runs, other days; descriptions)", "",
                  "| Model and form | " + " | ".join(SETS) + " |", "|---|" + "---:|" * len(SETS)]
        for k, v in refs.items():
            lines.append(f"| {k} | " + " | ".join(f"{fmt(v[s][0])} ({v[s][1]})" for s in SETS) + " |")
    return "\n".join(lines) + "\n"


def fmt_ci(ci):
    return f"[{fmt(ci[0], 2)}, {fmt(ci[1], 2)}]"


def status(v):
    return "n/a" if v is None else ("holds" if v else "fails")


def run(pilot):
    import runs
    data, g = runs.context()
    ids, rule_counts = set_ids(data, g)
    assert {k: len(v) for k, v in ids.items()} == {"no_type": 807, "hotel": 233, "stated": 89, "not_stated": 140}
    reads, counts, missing = load(pilot)
    res = analyse(reads, ids)
    preds = predictions(res)
    refs = stored_references(data, ids)
    OUT.mkdir(exist_ok=True)
    stem = "label_test_pilot" if pilot else "label_test"
    blob = {"pilot": pilot, "missing": missing, "word_rule_233": dict(rule_counts), "counts": counts,
            "results": res, "predictions": preds, "stored_references": refs}
    (OUT / f"{stem}.json").write_text(json.dumps(blob, indent=1, default=str))
    (OUT / f"{stem}.md").write_text(markdown(res, preds, counts, missing, refs, rule_counts, pilot))
    print((OUT / f"{stem}.md").read_text())


def selftest():
    """Fake parsed reads with a known effect: l_hotel 40% hotel values, l_code 10% on the no-type set (D = -30),
    and the same share in both arms on the stated set (D = 0). Checks the pairing, D, the interval and the verdict."""
    rng = random.Random(7)
    ids = {"no_type": [f"N{i}.json" for i in range(300)], "hotel": [f"H{i}.json" for i in range(120)]}
    ids["stated"], ids["not_stated"] = ids["hotel"][:60], ids["hotel"][60:]
    hotel, none = {"type": ("hotel",)}, {"type": None}
    reads = {}
    for m in MODELS:
        got = collections.defaultdict(list)
        for d in ids["no_type"]:
            got[(d, "l_hotel")] = [hotel if rng.random() < 0.4 else none]
            got[(d, "l_code")] = [hotel if rng.random() < 0.1 else none]
        for d in ids["stated"]:
            got[(d, "l_hotel")] = got[(d, "l_code")] = [hotel]
        for d in ids["not_stated"]:
            got[(d, "l_hotel")] = [hotel]
            got[(d, "l_code")] = [none]
        del got[(ids["no_type"][0], "l_code")]  # a missing arm: the dialogue has no pair
        reads[m] = got
    res = analyse(reads, ids)
    p = res["hotel"]["panel"]
    assert p["no_type"]["dialogues"] == 299, p["no_type"]["dialogues"]
    assert -36 < p["no_type"]["D"] < -24 and p["no_type"]["high"] < 0 and p["no_type"]["perm_p"] < 0.001, p["no_type"]
    assert p["stated"]["D"] == 0 and p["not_stated"]["D"] == -100
    assert res["hotel"]["models"]["sonnet"]["stated"]["l_hotel"] == (100.0, 60)
    t = p["trade"]
    assert abs(t["T1"]) < 1e-9 and t["brief"] > 0 and t["removed"] > 0
    preds = predictions(res)
    assert preds["L1"] and preds["L3"] and preds["verdict"].startswith("shared word"), preds
    # no effect: the verdict must not say that the shared word acts
    for m in MODELS:
        for d in ids["no_type"]:
            reads[m][(d, "l_code")] = list(reads[m][(d, "l_hotel")])
    preds = predictions(analyse(reads, ids))
    assert not preds["L1"] and preds["against"]["a_inside_3"] and preds["verdict"].startswith("meaning"), preds
    # the parser path: a raw hotel under l_code is not a valid read
    row = {"custom_id": "erl_haiku-SNG1-l_code-1", "type": "succeeded", "stop": "end_turn",
           "text": json.dumps({"name": None, "area": None, "pricerange": None, "stars": None, "type": ["hotel"],
                               "parking": None, "internet": None})}
    assert read_of(row)[4] == "no parse"
    row["text"] = row["text"].replace('["hotel"]', '["category_A"]')
    assert read_of(row)[3]["type"] == ("hotel",)
    row["stop"] = "max_tokens"
    assert read_of(row)[4] == "cut"
    print("selftest passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        run("--pilot" in sys.argv)
