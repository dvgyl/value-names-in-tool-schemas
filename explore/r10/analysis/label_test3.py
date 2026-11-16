"""Analysis of amendment R10-21 (prototypes/explore/PROTOCOL.md): the label test in the tool channel. Exploratory.

Arms (one written definition; the tool search_hotels of t0): tl_hotel (label hotel), tl_code (label category_A),
tl_neutral (label serviced_property). Runs: erl3_sol (3 answers per prefix and arm), erl3_luna (4 answers). Prefixes:
the 554 first requests of experiment A: no-type 448, hotel-brief 59, guesthouse-brief 47 (description).

Definitions (fixed in R10-21 before any call):
- A valid read: the row succeeded, it did not stop at the output cap, and labeltest3.parse_call gives "search" or
  "none". A "none" read (no tool call) scores 0 on each outcome.
- Hotel value (primary): the type list of the search call holds hotel. Hotel-only filter: hotel and not guesthouse.
  Search failure: briefsearch.search_failure (the hotel-only filter, and no hotel among the venues that fit the brief).
- Per prefix, model and arm: the share is the mean over the valid reads. A contrast X - Y is share(X) - share(Y) in
  points, over the prefixes with a valid read of both arms. D_c = tl_code - tl_hotel, D_n = tl_neutral - tl_hotel,
  D_nc = tl_neutral - tl_code.
- Panel: per prefix, the mean of the contrast over the models with a valid pair; then the mean over prefixes. 95%
  percentile cluster bootstrap over prefixes (2,000 draws, seed 20261112); two-sided sign-flip permutation test
  (10,000 draws, seed 20261114) for the primary outcome.

Usage (from explore/):
    python3 -I r10/analysis/label_test3.py            # the fetched raw.jsonl files
    python3 -I r10/analysis/label_test3.py --selftest # fake answers
Outputs: r10/analysis/out/label_test3.json and label_test3.md.
This file is a copy of the project analysis (workshops/label-test/analyze3.py) with the paths of the study folder; the results are the same.
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
sys.path.insert(0, str(HERE))
import label_test as a18  # noqa: E402  (R10-18 analysis: rows_of, effect; its main does not run)
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import labeltest3 as l3  # noqa: E402
import release_analyze as ra  # noqa: E402  (trade; its main does not run)
import stats  # noqa: E402
import tools  # noqa: E402

OUT = HERE / "out"
CUT = a18.CUT
FOLDERS = {"sol": "erl3_sol", "luna": "erl3_luna"}
MODELS = tuple(FOLDERS)
STORED_T0 = {"sol": ("era1_sol", "erx_a3_sol"), "luna": ("era1_luna",)}  # the stored t0 tool calls (references)
SETS = ("no_type", "hotel_brief", "guesthouse")
SET_OF_RA = {"no_type": "open", "hotel_brief": "specific", "guesthouse": "guesthouse"}
OUTCOMES = ("hotel", "hotel_only", "search_failure")
CONTRASTS = {"D_c": ("tl_code", "tl_hotel"), "D_n": ("tl_neutral", "tl_hotel"), "D_nc": ("tl_neutral", "tl_code")}


def outcomes(kind, fields, d, data, db):
    """{outcome: 0 or 1} of one valid read. A read without a search call scores 0 on each outcome."""
    if kind != "search":
        return {o: 0 for o in OUTCOMES}
    t = fields.get("type")
    return {"hotel": int(isinstance(t, tuple) and "hotel" in t), "hotel_only": int(bool(gold.hides_guesthouse(t))),
            "search_failure": int(bool(bs.search_failure(fields, data[d], db)))}


def read_of(row, parse):
    """(prefix id, cell, kind, fields or reason). kind is "search", "none" or "invalid"."""
    _, d, cell, _ = row["custom_id"].split("-")
    if row.get("type", "succeeded") != "succeeded":
        return d + ".json", cell, "invalid", "failed"
    if row.get("stop") in CUT:
        return d + ".json", cell, "invalid", "cut"
    kind, val = parse(row, cell)
    if kind not in ("search", "none"):
        return d + ".json", cell, "invalid", val if kind == "invalid" else f"kind {kind}"
    return d + ".json", cell, kind, val


def load(pilot, data, db):
    """{model: {(d, cell): [outcomes, ...]}}, {model: {cell: Counter(kind)}}, missing folders."""
    reads = {m: collections.defaultdict(list) for m in MODELS}
    counts = {m: collections.defaultdict(collections.Counter) for m in MODELS}
    missing = []
    for m, f in FOLDERS.items():
        rr = a18.rows_of(f, pilot)
        if rr is None:
            missing.append(f)
            continue
        for row in rr:
            d, cell, kind, val = read_of(row, l3.parse_call)
            counts[m][cell][kind if kind != "invalid" else f"invalid: {str(val)[:50]}"] += 1
            if kind != "invalid":
                reads[m][(d, cell)].append(outcomes(kind, val, d, data, db))
    return reads, {m: {k: dict(v) for k, v in c.items()} for m, c in counts.items()}, missing


def load_stored_t0(data, db):
    """{model: {(d, "t0"): [outcomes, ...]}} of the stored t0 tool calls (other batches and days; references)."""
    out = {m: collections.defaultdict(list) for m in MODELS}
    for m, folders in STORED_T0.items():
        for f in folders:
            for row in a18.rows_of(f, False) or []:
                if row["custom_id"].split("-")[2] != "t0":
                    continue
                d, cell, kind, val = read_of(row, tools.parse_call)
                if kind != "invalid":
                    out[m][(d, cell)].append(outcomes(kind, val, d, data, db))
    return out


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def arm_share(got, d, cell, outcome):
    v = [x[outcome] for x in got.get((d, cell), [])]
    return mean(v) if v else None


def arm_pct(got, ids, cell, outcome):
    vals = [s for d in ids if (s := arm_share(got, d, cell, outcome)) is not None]
    return (None if not vals else 100 * mean(vals), len(vals))


def effect(diffs, perm):
    """a18.effect (mean, 95% cluster bootstrap, sign counts and sign p), with the permutation p only when `perm`."""
    if perm:
        return a18.effect(diffs)
    saved = a18.stats.permutation_test
    a18.stats.permutation_test = lambda *args, **kw: None
    try:
        return a18.effect(diffs)
    finally:
        a18.stats.permutation_test = saved


def contrast(reads, x, y, ids, outcome, perm, models=MODELS):
    """Per model and panel: the arm shares and the paired effect of x - y (cells), paired by prefix."""
    per, by_d = {}, collections.defaultdict(list)
    for m in models:
        got = reads.get(m, {})
        pairs = {}
        for d in ids:
            sx, sy = arm_share(got, d, x, outcome), arm_share(got, d, y, outcome)
            if sx is not None and sy is not None:
                pairs[d] = 100 * (sx - sy)
                by_d[d].append(pairs[d])
        per[m] = {"x": arm_pct(got, ids, x, outcome), "y": arm_pct(got, ids, y, outcome),
                  **effect(list(pairs.values()), perm)}
    panel = {"models_per_prefix": mean(len(v) for v in by_d.values()), **effect([mean(v) for v in by_d.values()], perm)}
    return {"models": per, "panel": panel}


def trade_rows(got, ids, control, update):
    """(sum, n, sum, n) of the hotel value per prefix, control then update, for release_analyze.trade."""
    rows = []
    for d in ids:
        a = [x["hotel"] for x in got.get((d, control), [])]
        b = [x["hotel"] for x in got.get((d, update), [])]
        if a and b:
            rows.append((sum(a), len(a), sum(b), len(b)))
    return rows


def analyse(reads, ids):
    res = {}
    for outcome in OUTCOMES:
        res[outcome] = {c: {s: contrast(reads, x, y, ids[s], outcome, outcome == "hotel") for s in SETS}
                        for c, (x, y) in CONTRASTS.items()}
    res["trade"] = {m: {cell: ra.trade(trade_rows(reads.get(m, {}), ids["no_type"], "tl_hotel", cell),
                                       trade_rows(reads.get(m, {}), ids["hotel_brief"], "tl_hotel", cell))
                        for cell in ("tl_code", "tl_neutral")} for m in MODELS}
    return res


def definition_effect(reads, stored, ids):
    """tl_hotel (R10-21) against the stored t0 reads of the same model (other batches and days; description)."""
    both = {m: {**stored.get(m, {}), **reads.get(m, {})} for m in MODELS}
    return {o: {s: contrast(both, "tl_hotel", "t0", ids[s], o, False) for s in SETS} for o in OUTCOMES}


def references(stored, ids):
    """Stored t0 rates per model, set and outcome: percent of valid reads (the table of R10-21)."""
    out = {}
    for m in MODELS:
        for s in SETS:
            vals = [x for d in ids[s] for x in stored.get(m, {}).get((d, "t0"), [])]
            out[f"{m}|{s}"] = {o: (None if not vals else round(100 * mean(x[o] for x in vals), 1)) for o in OUTCOMES}
            out[f"{m}|{s}"]["reads"] = len(vals)
    return out


def below(e, lim):
    return None if e["D"] is None else bool(e["D"] <= lim and e["high"] < 0)


def inside(e, lo, hi):
    return None if e["D"] is None else bool(lo <= e["low"] and e["high"] <= hi)


def category_t12(e, holds):
    """The categories of R10-21 for T1 and T2."""
    if e["D"] is None:
        return "no data"
    if holds:
        return "shared word acts"
    if inside(e, -3.0, 3.0):
        return "against (a): the whole interval is inside -3 to +3 points"
    if e["low"] > 0:
        return "against (b): reversed (the interval is above 0)"
    return "unresolved"


def category_t3(e, holds):
    if e["D"] is None:
        return "no data"
    if holds:
        return "the neutral label acts as the code"
    if (e["D"] <= -3.0 and e["high"] < 0) or (e["D"] >= 3.0 and e["low"] > 0):
        return "against: the neutral label and the code differ by 3 points or more"
    return "unresolved"


def predictions(res):
    r = res["hotel"]
    t1, t2, t3 = (r[c]["no_type"]["panel"] for c in ("D_c", "D_n", "D_nc"))
    out = {"T1": below(t1, -3.0), "T2": below(t2, -3.0), "T3": inside(t3, -3.0, 3.0)}
    out["T1_category"] = category_t12(t1, out["T1"])
    out["T2_category"] = category_t12(t2, out["T2"])
    out["T3_category"] = category_t3(t3, out["T3"])
    pv = [t1["perm_p"], t2["perm_p"]]
    out["holm_T1_T2"] = stats.holm(pv) if None not in pv else None
    return out


def fmt(x, nd=1):
    return "n/a" if x is None else f"{x:.{nd}f}"


def status(v):
    return "n/a" if v is None else ("holds" if v else "fails")


def table(lines, block, label_x, label_y, sets=SETS):
    lines += [f"| Model | Set | {label_x} % (n) | {label_y} % (n) | pairs | D | 95% interval | perm p | up/down |",
              "|---|---|---:|---:|---:|---:|---|---:|---:|"]
    for s in sets:
        e = block[s]
        for m, x in list(e["models"].items()) + [("panel", e["panel"])]:
            xs = "" if m == "panel" else f"{fmt(x['x'][0])} ({x['x'][1]})"
            ys = "" if m == "panel" else f"{fmt(x['y'][0])} ({x['y'][1]})"
            lines.append(f"| {m} | {s} | {xs} | {ys} | {x['dialogues']} | {fmt(x['D'])} | "
                         f"[{fmt(x['low'])}, {fmt(x['high'])}] | {fmt(x['perm_p'], 4)} | {x['up']}/{x['down']} |")
    lines.append("")


def markdown(blob):
    res, preds = blob["results"], blob["predictions"]
    lines = [f"# Label test in the tool channel (R10-21){' — PILOT ANSWERS (dry run; no result)' if blob['pilot'] else ''}",
             "", "Exploratory, fixed in the protocol before the run. Contrasts in points, paired by prefix: D_c = tl_code − "
             "tl_hotel, D_n = tl_neutral − tl_hotel, D_nc = tl_neutral − tl_code. Sets: no-type 448, hotel-brief 59, "
             "guesthouse-brief 47 (description). On the hotel-brief set the search failure is 0 by construction.", ""]
    if blob["missing"]:
        lines += [f"Missing folders: {', '.join(blob['missing'])}.", ""]
    lines += ["## Predictions (primary outcome, no-type prefixes)", "",
              f"- T1 (panel D_c ≤ −3 with the interval below 0): {status(preds['T1'])}; {preds['T1_category']}",
              f"- T2 (panel D_n ≤ −3 with the interval below 0): {status(preds['T2'])}; {preds['T2_category']}",
              f"- T3 (the whole interval of the panel D_nc inside ±3): {status(preds['T3'])}; {preds['T3_category']}"]
    if preds["holm_T1_T2"]:
        lines.append("- Holm-adjusted p of T1 and T2 (description): " + ", ".join(fmt(x, 4) for x in preds["holm_T1_T2"]))
    lines.append("")
    for outcome in OUTCOMES:
        lines += [f"## Outcome: {outcome}", ""]
        for cname, (cx, cy) in CONTRASTS.items():
            lines += [f"### {cname} = {cx} − {cy}", ""]
            table(lines, res[outcome][cname], cx, cy)
    lines += ["## Descriptions", "", "### Value trade against tl_hotel (wrong values removed on no-type, correct values "
              "lost on hotel-brief)", "", "| Model | Arm | Wrong removed | Correct lost | Ratio |", "|---|---|---:|---:|---|"]
    for m, per in res["trade"].items():
        for cell, t in per.items():
            if t is None:
                lines.append(f"| {m} | {cell} | - | - | not computed |")
            else:
                lines.append(f"| {m} | {cell} | {t['wrong_removed']:.1f} | {t['correct_lost']:.1f} | "
                             f"{'not defined' if not t['defined'] else fmt(t['ratio'], 2)} |")
    lines += ["", "### tl_hotel against the stored t0 (the definition on the label hotel; other batches and days)", ""]
    for outcome in OUTCOMES:
        lines += [f"Outcome {outcome}:", ""]
        table(lines, blob["definition_effect"][outcome], "tl_hotel", "t0 (stored)")
    lines += ["### Stored t0 references (percent of valid reads)", "", "| Model and set | Reads | " +
              " | ".join(OUTCOMES) + " |", "|---|---:|" + "---:|" * len(OUTCOMES)]
    for k, v in blob["stored_references"].items():
        lines.append(f"| {k} | {v['reads']} | " + " | ".join(fmt(v[o]) for o in OUTCOMES) + " |")
    lines += ["", "### Read kinds per arm", ""]
    for m, c in blob["counts"].items():
        lines.append(f"- {m}: " + "; ".join(f"{cell} {json.dumps(k)}" for cell, k in sorted(c.items())))
    return "\n".join(lines) + "\n"


def set_ids(data, g):
    s = ra.request_sets(data, g)
    return {k: s[v] for k, v in SET_OF_RA.items()}


def run(pilot):
    import runs
    l3.check_amendment()
    data, g = runs.context()
    db = gold.hotel_db()
    ids = set_ids(data, g)
    assert {k: len(v) for k, v in ids.items()} == {"no_type": 448, "hotel_brief": 59, "guesthouse": 47}
    reads, counts, missing = load(pilot, data, db)
    stored = load_stored_t0(data, db)
    res = analyse(reads, ids)
    blob = {"amendment": "R10-21", "exploratory": True, "pilot": pilot, "missing": missing, "counts": counts,
            "results": res, "predictions": predictions(res), "definition_effect": definition_effect(reads, stored, ids),
            "stored_references": references(stored, ids)}
    OUT.mkdir(exist_ok=True)
    stem = "label_test3_pilot" if pilot else "label_test3"
    (OUT / f"{stem}.json").write_text(json.dumps(blob, indent=1, default=str))
    (OUT / f"{stem}.md").write_text(markdown(blob))
    print((OUT / f"{stem}.md").read_text())


def selftest():
    """Fake reads with known effects: the shared-word world (tl_code and tl_neutral low and equal) and the meaning world
    (all arms equal). Checks the pairing, the contrasts, the verdicts, the outcomes and the parse path."""
    rng = random.Random(21)
    a18.DRAWS, a18.PERM_DRAWS = 400, 400  # fewer draws, so that the selftest is fast; the run keeps 2,000 and 10,000
    ids = {"no_type": [f"N{i}.json" for i in range(448)], "hotel_brief": [f"H{i}.json" for i in range(59)],
           "guesthouse": [f"G{i}.json" for i in range(47)]}
    n_reads = {"sol": 3, "luna": 4}

    def world(p_hotel, p_code):
        reads = {m: collections.defaultdict(list) for m in MODELS}
        for m in MODELS:
            for s, lst in ids.items():
                for d in lst:
                    for cell, p in (("tl_hotel", p_hotel), ("tl_code", p_code)):
                        for _ in range(n_reads[m]):
                            h = rng.random() < (p if s != "hotel_brief" else 0.9)
                            reads[m][(d, cell)].append({"hotel": int(h), "hotel_only": int(h),
                                                        "search_failure": int(h and s != "hotel_brief")})
                    reads[m][(d, "tl_neutral")] = list(reads[m][(d, "tl_code")])  # the neutral label acts as the code
        return reads

    shared = world(0.30, 0.05)
    res = analyse(shared, ids)
    p = predictions(res)
    t1 = res["hotel"]["D_c"]["no_type"]["panel"]
    assert t1["dialogues"] == 448 and t1["models_per_prefix"] == 2 and -30 < t1["D"] < -20 and t1["high"] < 0, t1
    assert p["T1"] and p["T2"] and p["T3"], p
    assert p["T1_category"] == "shared word acts" and p["T3_category"].startswith("the neutral label"), p
    assert res["hotel"]["D_nc"]["no_type"]["panel"]["D"] == 0.0
    assert res["search_failure"]["D_c"]["hotel_brief"]["panel"]["D"] == 0.0  # 0 by construction on hotel briefs
    assert res["trade"]["sol"]["tl_code"]["defined"], res["trade"]["sol"]
    meaning = world(0.30, 0.30)
    for m in MODELS:  # all arms answer the same: every contrast is 0
        for k in [k for k in meaning[m] if k[1] != "tl_hotel"]:
            meaning[m][k] = list(meaning[m][(k[0], "tl_hotel")])
    res2 = analyse(meaning, ids)
    p2 = predictions(res2)
    assert not p2["T1"] and not p2["T2"] and p2["T3"], p2
    assert p2["T1_category"].startswith("against (a)") and p2["T2_category"].startswith("against (a)"), p2
    # a neutral label that differs from the code counts against T3
    far = world(0.30, 0.05)
    for m in MODELS:
        for k in [k for k in far[m] if k[1] == "tl_neutral"]:
            far[m][k] = list(far[m][(k[0], "tl_hotel")])
    p3 = predictions(analyse(far, ids))
    assert not p3["T3"] and p3["T3_category"].startswith("against"), p3
    # a missing model: the panel uses the other model only
    one = world(0.30, 0.05)
    one["luna"] = collections.defaultdict(list)
    r1 = analyse(one, ids)
    assert r1["hotel"]["D_c"]["no_type"]["models"]["luna"]["dialogues"] == 0
    assert r1["hotel"]["D_c"]["no_type"]["panel"]["models_per_prefix"] == 1
    blob = {"pilot": False, "missing": [], "counts": {}, "results": res, "predictions": p,
            "definition_effect": definition_effect(shared, {m: {(d, "t0"): v for (d, c), v in shared[m].items()
                                                                if c == "tl_hotel"} for m in MODELS}, ids),
            "stored_references": {}}
    assert blob["definition_effect"]["hotel"]["no_type"]["panel"]["D"] == 0.0
    md = markdown(blob)
    assert "### D_c = tl_code − tl_hotel" in md and "T3 (the whole interval" in md
    # the outcomes of one read: a hotel-only call on a brief that only a guesthouse fits is a search failure
    data = {"X.json": {"goal": {"hotel": {"info": {"area": "north", "pricerange": "cheap"}}}}}
    db = [{"name": "a", "type": "guesthouse", "area": "north", "pricerange": "cheap"},
          {"name": "b", "type": "hotel", "area": "south", "pricerange": "cheap"}]
    assert outcomes("search", {"type": ("hotel",)}, "X.json", data, db) == {"hotel": 1, "hotel_only": 1,
                                                                             "search_failure": 1}
    assert outcomes("search", {"type": ("guesthouse", "hotel")}, "X.json", data, db) == {"hotel": 1, "hotel_only": 0,
                                                                                          "search_failure": 0}
    assert outcomes("none", "text", "X.json", data, db) == {"hotel": 0, "hotel_only": 0, "search_failure": 0}
    # the parse path: the label maps back; a raw hotel under tl_code is not valid; a cut row is not valid
    row = {"custom_id": "erl3_sol-SNG1-tl_code-2", "type": "succeeded", "stop": "end_turn", "tool_calls": [
        {"name": "search_hotels", "input": {"name": None, "area": None, "pricerange": None, "stars": None,
                                            "type": ["category_A"], "parking": None, "internet": None}}]}
    assert read_of(row, l3.parse_call)[2:] == ("search", read_of(row, l3.parse_call)[3])
    assert read_of(row, l3.parse_call)[3]["type"] == ("hotel",)
    row["tool_calls"][0]["input"]["type"] = ["hotel"]
    assert read_of(row, l3.parse_call)[2] == "invalid"
    assert read_of({**row, "stop": "max_output_tokens"}, l3.parse_call)[3] == "cut"
    assert read_of({"custom_id": "erl3_luna-SNG1-tl_hotel-4", "type": "errored"}, l3.parse_call)[3] == "failed"
    assert read_of({"custom_id": "erl3_luna-SNG1-tl_hotel-4", "type": "succeeded", "stop": "end_turn", "text": "Hi"},
                   l3.parse_call)[2] == "none"
    print("selftest passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        run("--pilot" in sys.argv)
