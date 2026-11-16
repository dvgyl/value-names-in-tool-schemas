"""Analysis of amendment R10-19 (prototypes/explore/PROTOCOL.md): the label test, third arm l_neutral. Exploratory.

Arms (one written definition): l_hotel (label hotel), l_code (label category_A), l_neutral (label serviced_property).
Stored arms: the R10-18 runs erl_sonnet, erl_sonnet_hb, erl_haiku, erl_sol, erl_luna (source "r18"). New runs: erl2_*
(source "r19"; a different batch on the same day). Sets: 807 no-type briefs, 233 hotel briefs, and the word-rule split of the 233 (89 stated,
140 not stated).

Definitions (fixed in R10-19 before any call):
- A valid read: the row succeeded, it did not stop at the output cap, and labeltest2.parse accepts it.
- Hotel value (primary): the scored type list holds hotel. Hotel-only value (secondary): hotel and not guesthouse.
- Per dialogue, model and arm: the share is the mean over the valid reads of the named source. A contrast X - Y is
  share(X) - share(Y) in points, over the dialogues with a valid read of both.
- Contrasts: D_n = l_neutral - l_hotel, D_nc = l_neutral - l_code, D_c = l_code - l_hotel.
- Comparisons: "days" (l_neutral of r19 against the stored r18 arms; Sonnet, Haiku, Sol, Luna); "batch" (every arm of
  r19, the same batch or run; Sol, Luna, DeepSeek, Qwen, Gemma); "repeat" (an r19 arm against the same r18 arm; Sol,
  Luna).
- Panel: per dialogue, the mean of the contrast over the panel models with a valid pair; then the mean over dialogues.
  95% percentile cluster bootstrap over dialogues (2,000 draws, seed 20261112); two-sided sign-flip permutation test
  (10,000 draws, seed 20261114).

Usage (from explore/):
    python3 -I r10/analysis/label_test2.py            # the fetched raw.jsonl files
    python3 -I r10/analysis/label_test2.py --selftest # fake answers
Outputs: r10/analysis/out/label_test2.json and label_test2.md.
This file is a copy of the project analysis (workshops/label-test/analyze2.py) with the paths of the study folder; the results are the same.
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
import label_test as a18  # noqa: E402  (R10-18 analysis: sets, hit, effect; its main does not run)
import labeltest2 as l2  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
CUT = a18.CUT
STORED = {"sonnet": ("erl_sonnet", "erl_sonnet_hb"), "haiku": ("erl_haiku",), "sol": ("erl_sol",),
          "luna": ("erl_luna",)}
NEW = {"sonnet": ("erl2_sonnet_a", "erl2_sonnet_b"), "haiku": ("erl2_haiku",), "sol": ("erl2_sol",),
       "luna": ("erl2_luna",), "deepseek": ("erl2_deepseek",), "qwen": ("erl2_qwen",), "gemma": ("erl2_gemma",)}
MODELS = tuple(NEW)
SETS = a18.SETS
CONTRASTS = {"D_n": ("l_neutral", "l_hotel"), "D_nc": ("l_neutral", "l_code"), "D_c": ("l_code", "l_hotel")}
# comparison: (panel models, {arm: source}); an arm with source "r18" uses the stored R10-18 reads only
COMPARISONS = {
    "days": (("sonnet", "haiku", "sol", "luna"), {"l_neutral": "r19", "l_hotel": "r18", "l_code": "r18"}),
    "batch_gpt": (("sol", "luna"), {"l_neutral": "r19", "l_hotel": "r19", "l_code": "r19"}),
    "batch_open": (("deepseek", "qwen", "gemma"), {"l_neutral": "r19", "l_hotel": "r19", "l_code": "r19"}),
}
REPEAT = ("sol", "luna")


def read_of(row):
    """(dialogue id, cell, read, parsed fields or None, reason)."""
    _, d, cell, read = row["custom_id"].split("-")
    if row.get("type", "succeeded") != "succeeded":
        return d + ".json", cell, int(read), None, "failed"
    if row.get("stop") in CUT:
        return d + ".json", cell, int(read), None, "cut"
    try:
        return d + ".json", cell, int(read), l2.parse(cell, row.get("text", "")), "valid"
    except (ValueError, KeyError, TypeError, IndexError):
        return d + ".json", cell, int(read), None, "no parse"


def load(pilot):
    """{model: {(d, cell, source): [parsed, ...]}}, {model: {source|cell: Counter(reason)}}, missing folders.
    --pilot: the new folders give their pilot_raw.jsonl; the stored R10-18 folders give their raw.jsonl."""
    reads = {m: collections.defaultdict(list) for m in MODELS}
    counts = {m: collections.defaultdict(collections.Counter) for m in MODELS}
    missing = []
    for source, folders in (("r18", STORED), ("r19", NEW)):
        for m, names in folders.items():
            for f in names:
                rr = a18.rows_of(f, pilot and source == "r19")
                if rr is None:
                    missing.append(f)
                    continue
                for row in rr:
                    d, cell, _, parsed, why = read_of(row)
                    counts[m][f"{source}|{cell}"][why] += 1
                    if parsed is not None:
                        reads[m][(d, cell, source)].append(parsed)
    return reads, {m: {k: dict(v) for k, v in c.items()} for m, c in counts.items()}, missing


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def arm_share(got, d, cell, source, outcome):
    v = [a18.hit(x, outcome) for x in got.get((d, cell, source), [])]
    return mean(v) if v else None


def pairs_of(got, ids, x, y, outcome):
    """{d: (share of y, share of x)} over the dialogues with a valid read of both arms; x and y are (cell, source)."""
    out = {}
    for d in ids:
        sx, sy = arm_share(got, d, *x, outcome), arm_share(got, d, *y, outcome)
        if sx is not None and sy is not None:
            out[d] = (sy, sx)
    return out


def arm_pct(got, ids, cell, source, outcome):
    vals = [s for d in ids if (s := arm_share(got, d, cell, source, outcome)) is not None]
    return (None if not vals else 100 * mean(vals), len(vals))


def effect(diffs, perm):
    """a18.effect (mean D, 95% cluster bootstrap, sign counts and sign p), with the permutation p only when `perm`."""
    if perm:
        return a18.effect(diffs)
    saved = a18.stats.permutation_test
    a18.stats.permutation_test = lambda *args, **kw: None
    try:
        return a18.effect(diffs)
    finally:
        a18.stats.permutation_test = saved


def contrast(reads, models, x, y, ids, outcome, perm=True):
    """Per model and panel: the arm shares and the paired effect of x - y (x, y: (cell, source)). The permutation test
    runs for the primary outcome only (`perm`); the other rows give the bootstrap interval and the sign counts."""
    per, by_d = {}, collections.defaultdict(list)
    for m in models:
        got = reads.get(m, {})
        p = pairs_of(got, ids, x, y, outcome)
        per[m] = {"x": arm_pct(got, ids, *x, outcome), "y": arm_pct(got, ids, *y, outcome),
                  **effect([100 * (b - a) for a, b in p.values()], perm)}
        for d, v in p.items():
            by_d[d].append(v)
    panel = {"models_per_dialogue": mean(len(v) for v in by_d.values()),
             **effect([100 * mean(b - a for a, b in v) for v in by_d.values()], perm)}
    return {"models": per, "panel": panel}


def analyse(reads, ids):
    res = {}
    for outcome in ("hotel", "hotel_only"):
        res[outcome] = {}
        for comp, (models, src) in COMPARISONS.items():
            res[outcome][comp] = {}
            for cname, (cx, cy) in CONTRASTS.items():
                if comp == "days" and cname == "D_c":
                    continue  # D_c on the stored arms is the R10-18 result
                res[outcome][comp][cname] = {s: contrast(reads, models, (cx, src[cx]), (cy, src[cy]), ids[s], outcome,
                                                      outcome == "hotel") for s in SETS}
        res[outcome]["repeat"] = {cell: {s: contrast(reads, REPEAT, (cell, "r19"), (cell, "r18"), ids[s], outcome,
                                                     False) for s in SETS} for cell in ("l_hotel", "l_code")}
    return res


def below(e, lim):
    return None if e["D"] is None else bool(e["D"] <= lim and e["high"] < 0)


def inside(e, lo, hi):
    return None if e["D"] is None else bool(lo <= e["low"] and e["high"] <= hi)


def category(e, prediction):
    """The categories of R10-19 for a shared-word prediction on the no-type set."""
    if e["D"] is None:
        return "no data"
    if prediction:
        return "shared word acts"
    if inside(e, -3.0, 3.0):
        return "code avoidance (l_neutral stays within 3 points of l_hotel)"
    if e["low"] > 0:
        return "reversed (l_neutral above l_hotel)"
    return "unresolved"


def predictions(res):
    r = res["hotel"]
    days = r["days"]["D_n"]["no_type"]["panel"]
    opn = r["batch_open"]
    out = {"N1": below(days, -3.0)}
    out["N1_category"] = category(days, out["N1"])
    out["N1_against"] = {"a_inside_3": inside(days, -3.0, 3.0), "b_reversed": None if days["D"] is None
                         else bool(days["low"] > 0)}
    n2 = {}
    for m in REPEAT:
        for cell in ("l_hotel", "l_code"):
            e = r["repeat"][cell]["no_type"]["models"][m]
            new, old = e["x"][0], e["y"][0]
            n2[f"{m}|{cell}"] = None if new is None or old is None else bool(abs(new - old) <= 3.0)
    out["N2"] = n2
    out["N3"] = below(opn["D_c"]["no_type"]["panel"], -3.0)
    out["N3_against_inside_3"] = inside(opn["D_c"]["no_type"]["panel"], -3.0, 3.0)
    n4 = opn["D_n"]["no_type"]["panel"]
    out["N4"] = below(n4, -3.0)
    out["N4_category"] = category(n4, out["N4"])
    ns = contrast_panel_days_not_stated(res)
    out["N5"] = below(ns, -10.0)
    pv = [days["perm_p"], opn["D_c"]["no_type"]["panel"]["perm_p"], n4["perm_p"]]
    out["holm_N1_N3_N4"] = stats.holm(pv) if None not in pv else None
    return out


def contrast_panel_days_not_stated(res):
    """N5 uses the days comparison without Sonnet (Sonnet has no hotel-brief l_neutral arm): Haiku, Sol, Luna."""
    return res["hotel"]["days_hb"]["panel"]


def add_days_hb(reads, ids, res):
    src = COMPARISONS["days"][1]
    for outcome in ("hotel", "hotel_only"):
        res[outcome]["days_hb"] = contrast(reads, ("haiku", "sol", "luna"), ("l_neutral", src["l_neutral"]),
                                           ("l_hotel", src["l_hotel"]), ids["not_stated"], outcome, outcome == "hotel")


def fmt(x, nd=1):
    return "n/a" if x is None else f"{x:.{nd}f}"


def status(v):
    return "n/a" if v is None else ("holds" if v else "fails")


def table(lines, block, label_x, label_y):
    lines += [f"| Model | Set | {label_x} % (n) | {label_y} % (n) | pairs | D | 95% interval | perm p | up/down |",
              "|---|---|---:|---:|---:|---:|---|---:|---:|"]
    for s in [s for s in SETS if s in block]:
        e = block[s]
        for m, x in list(e["models"].items()) + [("panel", e["panel"])]:
            xs = "" if m == "panel" else f"{fmt(x['x'][0])} ({x['x'][1]})"
            ys = "" if m == "panel" else f"{fmt(x['y'][0])} ({x['y'][1]})"
            lines.append(f"| {m} | {s} | {xs} | {ys} | {x['dialogues']} | {fmt(x['D'])} | "
                         f"[{fmt(x['low'])}, {fmt(x['high'])}] | {fmt(x['perm_p'], 4)} | {x['up']}/{x['down']} |")
    lines.append("")


def markdown(res, preds, counts, missing, refs, rule_counts, pilot):
    lines = [f"# Label test, third arm l_neutral (R10-19){' — PILOT ANSWERS' if pilot else ''}", "",
             "Exploratory, fixed in the protocol before the run. Contrasts in points: D_n = l_neutral − l_hotel, "
             "D_nc = l_neutral − l_code, D_c = l_code − l_hotel.", "",
             "The comparison \"days\" pairs the new l_neutral answers with the stored R10-18 answers, which ran in "
             "a different batch on the same day (R10-18 batches fetched 2026-11-14 06:25 to 10:52 UTC; R10-19 batches submitted 12:34 to 12:40 UTC). The comparisons \"batch\" pair arms of the same new batch "
             "or run.", ""]
    if missing:
        lines += [f"Missing folders: {', '.join(missing)}.", ""]
    lines += [f"Word rule on the 233 hotel briefs: {dict(rule_counts)}.", ""]
    for outcome in ("hotel", "hotel_only"):
        r = res[outcome]
        lines += [f"## Outcome: {outcome} value", ""]
        for comp in COMPARISONS:
            for cname, block in r[comp].items():
                cx, cy = CONTRASTS[cname]
                src = COMPARISONS[comp][1]
                lines += [f"### {comp}: {cname} = {cx} ({src[cx]}) − {cy} ({src[cy]})", ""]
                table(lines, block, cx, cy)
        lines += ["### days, without Sonnet: D_n on the 140 not-stated hotel briefs (N5)", ""]
        table(lines, {"not_stated": r["days_hb"]}, "l_neutral", "l_hotel")
        for cell in ("l_hotel", "l_code"):
            lines += [f"### repeat: {cell} (r19) − {cell} (r18), Sol and Luna", ""]
            table(lines, r["repeat"][cell], f"{cell} r19", f"{cell} r18")
    lines += ["## Predictions (primary outcome)", "",
              f"- N1 (panel of Sonnet, Haiku, Sol, Luna, days, D_n on no-type ≤ −3 with the interval below 0): "
              f"{status(preds['N1'])}",
              f"- N1 category: {preds['N1_category']}. Against N1: "
              + ", ".join(f"{k} {status(v)}" for k, v in preds["N1_against"].items()),
              "- N2 (day check: the new share within 3 points of the stored share on no-type): "
              + ", ".join(f"{k} {status(v)}" for k, v in preds["N2"].items()),
              f"- N3 (open models, batch, D_c on no-type ≤ −3 with the interval below 0): {status(preds['N3'])}; "
              f"interval inside ±3: {status(preds['N3_against_inside_3'])}",
              f"- N4 (open models, batch, D_n on no-type ≤ −3 with the interval below 0): {status(preds['N4'])}; "
              f"category: {preds['N4_category']}",
              f"- N5 (Haiku, Sol, Luna, days, D_n on not-stated ≤ −10 with the interval below 0): {status(preds['N5'])}"]
    if preds["holm_N1_N3_N4"]:
        lines.append("- Holm-adjusted p of N1, N3, N4 (description): "
                     + ", ".join(fmt(x, 4) for x in preds["holm_N1_N3_N4"]))
    lines += ["", "## Reads per source and arm", ""]
    for m in MODELS:
        lines.append(f"- {m}: " + "; ".join(f"{k} {v}" for k, v in sorted(counts[m].items())))
    if refs:
        lines += ["", "## Stored round-9 references (no definition; other runs and days; descriptions)", "",
                  "| Model and form | " + " | ".join(SETS) + " |", "|---|" + "---:|" * len(SETS)]
        for k, v in refs.items():
            lines.append(f"| {k} | " + " | ".join(f"{fmt(v[s][0])} ({v[s][1]})" for s in SETS) + " |")
    return "\n".join(lines) + "\n"


def stored_references(ids):
    """Round-9 F0, F4 (serviced_property without the definition) and F6 shares on the same sets (descriptions)."""
    import natural_analyze as na
    r9, _ = na.load()
    out = {}
    for m in MODELS:
        for f in ("f0", "f4", "f6"):
            per = {d + ".json": list(map(na.hotel, v)) for d, v in r9.get((m, f), {}).items()}
            out[f"{m}|{f}_round9"] = {s: a18.share_of(per, ids[s]) for s in SETS}
    return out


def run(pilot, refs_on):
    import runs
    data, g = runs.context()
    ids, rule_counts = a18.set_ids(data, g)
    assert {k: len(v) for k, v in ids.items()} == {"no_type": 807, "hotel": 233, "stated": 89, "not_stated": 140}
    reads, counts, missing = load(pilot)
    res = analyse(reads, ids)
    add_days_hb(reads, ids, res)
    preds = predictions(res)
    refs = stored_references(ids) if refs_on else {}
    OUT.mkdir(exist_ok=True)
    stem = "label_test2_pilot" if pilot else "label_test2"
    blob = {"amendment": "R10-19", "pilot": pilot, "missing": missing, "word_rule_233": dict(rule_counts),
            "counts": counts, "results": res, "predictions": preds, "stored_references": refs}
    (OUT / f"{stem}.json").write_text(json.dumps(blob, indent=1, default=str))
    (OUT / f"{stem}.md").write_text(markdown(res, preds, counts, missing, refs, rule_counts, pilot))
    print((OUT / f"{stem}.md").read_text())


def fake(rates, ids, rng, reads_n=2):
    """Fake parsed reads: rates[(model, cell, source)] = share of hotel values on the no-type and not-stated sets."""
    hotel, none = {"type": ("hotel",)}, {"type": None}
    reads = {m: collections.defaultdict(list) for m in MODELS}
    for (m, cell, source), p in rates.items():
        for s in ("no_type", "not_stated"):
            for d in ids[s]:
                for _ in range(reads_n):
                    reads[m][(d, cell, source)].append(hotel if rng.random() < p else none)
        for d in ids["stated"]:
            reads[m][(d, cell, source)].append(hotel)
    return reads


def selftest():
    """Fake parsed reads with known effects: the shared-word world (l_neutral as low as l_code) and the code-avoidance
    world (l_neutral as high as l_hotel). Checks the pairing by source, the contrasts and the verdicts."""
    rng = random.Random(11)
    a18.DRAWS, a18.PERM_DRAWS = 400, 400  # fewer draws, so that the selftest is fast; the run keeps 2,000 and 10,000
    ids = {"no_type": [f"N{i}.json" for i in range(300)], "hotel": [f"H{i}.json" for i in range(120)]}
    ids["stated"], ids["not_stated"] = ids["hotel"][:60], ids["hotel"][60:]

    def world(neutral):
        rates = {}
        for m in MODELS:
            for source in ("r18", "r19"):
                if source == "r18" and m not in STORED:
                    continue
                rates[(m, "l_hotel", source)] = 0.40
                rates[(m, "l_code", source)] = 0.10
            rates[(m, "l_neutral", "r19")] = neutral
        reads = fake(rates, ids, rng)
        for m in REPEAT:  # the new l_hotel and l_code reads of Sol and Luna repeat the stored ones exactly (N2)
            for (d, cell, source) in [k for k in reads[m] if k[2] == "r18"]:
                reads[m][(d, cell, "r19")] = list(reads[m][(d, cell, "r18")])
        if neutral == 0.40:  # the code-avoidance world: l_neutral answers exactly as l_hotel (so D_n is 0)
            for m in MODELS:
                for (d, cell, source) in [k for k in reads[m] if k[1] == "l_neutral"]:
                    reads[m][(d, cell, source)] = list(reads[m][(d, "l_hotel", "r18" if m in STORED else "r19")])
        return reads

    for neutral, want in ((0.10, "shared word"), (0.40, "code avoidance")):
        reads = world(neutral)
        res = analyse(reads, ids)
        add_days_hb(reads, ids, res)
        p = predictions(res)
        days = res["hotel"]["days"]["D_n"]["no_type"]["panel"]
        assert days["dialogues"] == 300, days
        if neutral == 0.10:
            assert -36 < days["D"] < -24 and days["high"] < 0, days
            assert p["N1"] and p["N4"] and p["N3"] and p["N5"], p
        else:
            assert abs(days["D"]) < 3 and not p["N1"] and p["N1_against"]["a_inside_3"], (days, p)
            assert not p["N4"] and p["N3"], p
        assert p["N1_category"].startswith(want) and p["N4_category"].startswith(want), p
        md = markdown(res, p, {m: {} for m in MODELS}, [], {}, {}, False)  # the report builds from these results
        assert "### days: D_n = l_neutral (r19) − l_hotel (r18)" in md and "N1 category" in md
        assert all(p["N2"].values()), p["N2"]  # the new and the stored l_hotel and l_code have the same rates
        # the days comparison of Sonnet uses only the stored l_hotel reads, the batch comparison only the new ones
        assert set(res["hotel"]["days"]["D_n"]["no_type"]["models"]) == {"sonnet", "haiku", "sol", "luna"}
        assert set(res["hotel"]["batch_open"]["D_n"]["no_type"]["models"]) == {"deepseek", "qwen", "gemma"}
    # a source that is missing gives no pair: Sonnet without r19 reads drops out of the days panel
    reads = world(0.10)
    for k in [k for k in reads["sonnet"] if k[2] == "r19"]:
        del reads["sonnet"][k]
    res = analyse(reads, ids)
    assert res["hotel"]["days"]["D_n"]["no_type"]["models"]["sonnet"]["dialogues"] == 0
    assert res["hotel"]["days"]["D_n"]["no_type"]["panel"]["models_per_dialogue"] == 3
    # the parser path: a raw hotel under l_neutral is not a valid read; serviced_property maps back to hotel
    row = {"custom_id": "erl2_haiku-SNG1-l_neutral-1", "type": "succeeded", "stop": "end_turn",
           "text": json.dumps({"name": None, "area": None, "pricerange": None, "stars": None, "type": ["hotel"],
                               "parking": None, "internet": None})}
    assert read_of(row)[4] == "no parse"
    row["text"] = row["text"].replace('["hotel"]', '["guesthouse", "serviced_property"]')
    assert read_of(row)[3]["type"] == ("guesthouse", "hotel")
    assert not a18.hit(read_of(row)[3], "hotel_only") and a18.hit(read_of(row)[3], "hotel")
    row["stop"] = "max_tokens"
    assert read_of(row)[4] == "cut"
    row = {"custom_id": "erl2_qwen-SNG1-l_code-2", "type": "errored"}
    assert read_of(row)[4] == "failed"
    print("selftest passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        run("--pilot" in sys.argv, "--no-refs" not in sys.argv)
