"""Experiment H: twelve word and schema pairs (constructed text). Exploratory.

Design, predictions H1 to H4 and the scoring rule: PROTOCOL.md "## Round 10 experiment H runs" (with "Changes approved
by the operator" and "Scoring rule"). Code of the items: r10/pairs.py and r10/pairs.json (12 pairs; item kinds
unclear_word, unclear_para, clear_specific, clear_general; forms g0 and g4; the calibration pair `hotel`, cells cal_g0
and cal_g4, reported apart). Inputs: the raw.jsonl of erh_<model> (Sonnet, Haiku, Sol, Luna: reads 1 and 2; Opus:
read 1), erx_h1_astra and erx_h2_astra (Astra, read 1, the two halves of the units), erx_h34_haiku and erx_h34_luna
(reads 3 and 4). Outputs: r10/analysis/out/h.json, h.md and fig_pairs.csv.

Definitions (fixed here before the first run of this script; only the row format of the raw files was looked at):
- The scoring rule (locked): an answer is read with the last JSON object of its text (the text from the last "{" to
  the last "}", as pairs.py, zforms.parse and r10/pilot_check.py find it; the H schema is flat). `type` is null, "any"
  or a list. A list value equal to the collision value, or under G4 equal to the pair's neutral token, counts as the
  collision value (case ignored; runs of spaces and underscores are equal). The outcome of a read: its `type` list
  holds the collision value. "Alone" (H4): the list holds the collision value and no other value.
- No parser of H answers exists (pilot_check only tests that a JSON object parses), so this script applies the locked
  rule above and no other parsing.
- A valid read: the row succeeded, did not stop at the length limit, and the rule above reads it. A missing read: a
  row whose text has no JSON object, whose object has no `type` key, or whose `type` is not null, "any" or a list of
  strings; or a request of the design (unit, form, read number of a fetched folder) with no row. Counts per cell.
- Choice 1: under G4 a list value equal to the literal collision word also counts as the collision value. Reason: the
  outcome is "the reads whose type list holds the collision value", and the rule for the neutral token adds to it.
  The closed G4 schema does not allow the word; the count of such values is shown (`out_of_schema`).
- Units: the item is (pair, scenario, kind); a cell is (model, pair, kind, form). Rates are over valid reads. A cell
  rate has a 95% cluster bootstrap interval over the 20 scenarios (stats.cluster_bootstrap, 2,000 draws, seed
  20261112). A rate pooled over the 12 pairs has two intervals (ACTION-PLAN.md section 3.4): (a) scenarios resampled
  inside each pair; (b) pairs resampled. The mixed model is not run: no statsmodels and no R (action plan difference 7).
- Paired contrasts: per item (or per scenario), the mean of the valid reads of one cell minus the mean of the other;
  a unit enters when both cells have a valid read. The point value is the mean of the unit differences; intervals as
  for the rates; the exact sign test (stats.sign_test) over the units. Word against paraphrase pairs the unclear_word
  and unclear_para items of the same scenario; G4 against G0 pairs the same item under the two forms.
- H1 (Sonnet, Sol, Luna): the G0 unclear_word rate pooled over the 12 pairs is at least 30%, and at least 8 of the 12
  pairs have a G0 unclear_word rate of 10% or more ("10 of the 16 pairs" read as 62.5% rounded up; the approved change).
- H2: the paraphrase lowers that rate by at least two thirds: 1 - (G0 unclear_para rate) / (G0 unclear_word rate) is
  at least 2/3, both pooled over the 12 pairs. Held when at least 3 of the 5 models meet it.
- H3: on clear_specific, the G0 rate minus the G4 rate (pooled over the 12 pairs; the collision value is the correct
  value there) is at least 10 points. Held when at least 3 of the 5 models meet it.
- H4: on clear_general, the share of G0 reads that write the collision value alone is 5% or less, for every model.
- Choice 2: "the 5 models" are the five erh models of the locked design (Sonnet, Haiku, Opus, Sol, Luna). Astra is a
  fill model; its values are shown and do not count in the judgement. Reason: the design names the five models and
  Astra as fill.
- A prediction that needs a model that is not fetched shows "incomplete" unless the fetched models already decide it.
Usage (from explore/): .venv/bin/python -I r10/analysis/h_analyze.py
"""
import collections
import csv
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import pairs  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
DESIGN = ("sonnet", "haiku", "opus", "sol", "luna")
MODELS = DESIGN + ("astra",)
KINDS = pairs.KINDS
FORMS = pairs.FORMS
CAL = pairs.HOTEL.collision
SOURCES = {  # model: ((folder, read numbers, half of the units or None), ...); the first folder must be fetched
    "sonnet": (("erh_sonnet", (1, 2), None),),
    "haiku": (("erh_haiku", (1, 2), None), ("erx_h34_haiku", (3, 4), None)),
    "opus": (("erh_opus", (1,), None),),
    "sol": (("erh_sol", (1, 2), None),),
    "luna": (("erh_luna", (1, 2), None), ("erx_h34_luna", (3, 4), None)),
    "astra": (("erx_h1_astra", (1,), 0), ("erx_h2_astra", (1,), 1)),
}
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
WORST_AT = 0.02


def rows(folder):
    path = EXPLORE / folder / "raw.jsonl"
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None


def norm(value):
    return re.sub(r"[\s_]+", "_", str(value).strip().lower())


def score(row, info):
    """(valid, (hit, alone, out_of_schema) or the reason of the missing read), by the locked scoring rule."""
    if row.get("type") != "succeeded":
        return False, "failed"
    if row.get("stop") in CUT:
        return False, "cut"
    text = row.get("text", "") or ""
    try:
        obj = json.loads(text[text.rfind("{"):text.rfind("}") + 1])
    except ValueError:
        return False, "no_json"
    if not isinstance(obj, dict) or "type" not in obj:
        return False, "no_type_key"
    t = obj["type"]
    if t is None or (isinstance(t, str) and norm(t) == "any"):
        values = []
    elif isinstance(t, list) and all(isinstance(x, str) for x in t):
        values = t
    else:
        return False, "type_shape"
    pair = pairs._pair(info["pair"])
    coll = {norm(pair.collision)} | ({norm(pair.neutral)} if info["form"] == "g4" else set())
    allowed = {norm(v) for v in pairs.type_values(pair, info["form"] == "g4")}
    hits = [norm(v) in coll for v in values]
    return True, (any(hits), bool(values) and all(hits), sum(norm(v) not in allowed for v in values))


def spec_index():
    """stem -> {pair, kind, scenario, form, unit} for every request of one read (pairs.requests_spec)."""
    return {s["stem"]: {k: s[k] for k in ("pair", "kind", "scenario", "form", "unit")} for s in pairs.requests_spec()}


def load(model, index):
    """None when the first folder is not fetched; else a dict with the valid reads per (unit, form), the missing
    reads per cell (pair, kind, form) by reason, the used and the missing folders."""
    got = collections.defaultdict(list)
    missing_reads = collections.defaultdict(collections.Counter)
    used, missing, expected, seen = [], [], set(), set()
    out_of_schema = 0
    for i, (folder, reads, half) in enumerate(SOURCES[model]):
        rr = rows(folder)
        if rr is None:
            missing.append(folder)
            if i == 0 and half is None:
                return None
            continue
        used.append(folder)
        expected |= {(stem, r) for stem, info in index.items() for r in reads
                     if half is None or runs.hash_unit(info["unit"]) % 2 == half}
        for row in rr:
            _, unit, form, read = row["custom_id"].split("-")
            stem = f"{unit}-{form}"
            info = index.get(stem)
            if info is None:
                missing_reads[("unknown", "unknown", form)]["unknown_stem"] += 1
                continue
            seen.add((stem, int(read)))
            ok, val = score(row, info)
            cell = (info["pair"], info["kind"], info["form"])
            if ok:
                got[(info["unit"], info["form"])].append(val)
                out_of_schema += val[2]
            else:
                missing_reads[cell][val] += 1
    if not used:
        return None
    for stem, _ in expected - seen:
        info = index[stem]
        missing_reads[(info["pair"], info["kind"], info["form"])]["no_row"] += 1
    return {"got": got, "missing_reads": missing_reads, "used": used, "missing": missing,
            "out_of_schema": out_of_schema}


def unit_of(pair, scenario, kind):
    return f"{pair}_{scenario:02d}_{kind}"


def per_scenario(got, pair, kind, form, measure=0):
    """[(k, n)] over the 20 scenarios; measure 0 is the collision value, 1 is the collision value alone."""
    out = []
    for s in range(pairs.N_SCENARIOS):
        vals = got.get((unit_of(pair, s, kind), form), [])
        out.append((sum(v[measure] for v in vals), len(vals)))
    return out


def ratio(rows_):
    n = sum(r[1] for r in rows_)
    return sum(r[0] for r in rows_) / n if n else 0.0


def cell_rate(got, pair, kind, form, missing_n=0, measure=0):
    per = per_scenario(got, pair, kind, form, measure)
    k, n = sum(r[0] for r in per), sum(r[1] for r in per)
    out = {"k": k, "n": n, "missing": missing_n, "share": k / n if n else None}
    if n:
        _, lo, hi = stats.cluster_bootstrap({"all": [r for r in per if r[1]]}, lambda g: ratio(g["all"]))
        out["ci"] = [lo, hi]
    return out


def pooled_rate(got, pair_list, kind, form, missing_n=0, measure=0):
    """The rate over the pairs, with interval (a) over scenarios inside pairs and (b) over pairs."""
    by_pair = {p: [r for r in per_scenario(got, p, kind, form, measure) if r[1]] for p in pair_list}
    by_pair = {p: v for p, v in by_pair.items() if v}
    k = sum(r[0] for v in by_pair.values() for r in v)
    n = sum(r[1] for v in by_pair.values() for r in v)
    out = {"k": k, "n": n, "missing": missing_n, "share": k / n if n else None,
           "pairs_at_10pct": sum(1 for v in by_pair.values() if ratio(v) >= 0.10)}
    if n:
        flat = lambda g: ratio([r for v in g.values() for r in v])
        out["ci_scenarios"] = list(stats.cluster_bootstrap(by_pair, flat)[1:])
        pair_rows = [(sum(r[0] for r in v), sum(r[1] for r in v)) for v in by_pair.values()]
        out["ci_pairs"] = list(stats.cluster_bootstrap({"all": pair_rows}, lambda g: ratio(g["all"]))[1:])
        if missing_n and missing_n / (n + missing_n) >= WORST_AT:
            out["worst_case"] = [k / (n + missing_n), (k + missing_n) / (n + missing_n)]
    return out


def paired_units(got, pair, a, b):
    """Per scenario (mean of cell b) - (mean of cell a); a and b are (kind, form)."""
    diffs = []
    for s in range(pairs.N_SCENARIOS):
        va = got.get((unit_of(pair, s, a[0]), a[1]), [])
        vb = got.get((unit_of(pair, s, b[0]), b[1]), [])
        if va and vb:
            diffs.append(sum(v[0] for v in vb) / len(vb) - sum(v[0] for v in va) / len(va))
    return diffs


def mean(g):
    return sum(r[0] for r in g) / len(g)


def contrast(by_pair):
    """by_pair: {pair: [unit differences]}. Mean difference, interval over units inside pairs, interval over pairs
    (when there is more than one pair), sign test over units."""
    by_pair = {p: v for p, v in by_pair.items() if v}
    diffs = [x for v in by_pair.values() for x in v]
    if not diffs:
        return {"units": 0, "mean": None}
    pos, neg = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    groups = {p: [(x,) for x in v] for p, v in by_pair.items()}
    flat = lambda g: mean([r for v in g.values() for r in v])
    out = {"units": len(diffs), "mean": sum(diffs) / len(diffs), "ci_scenarios": list(stats.cluster_bootstrap(groups, flat)[1:]),
           "higher": pos, "lower": neg, "sign_p": stats.sign_test(pos, neg)}
    if len(by_pair) > 1:
        sums = [(sum(v), len(v)) for v in by_pair.values()]
        out["ci_pairs"] = list(stats.cluster_bootstrap({"all": sums}, lambda g: ratio(g["all"]))[1:])
    return out


def reduction(got, pair_list):
    """H2: 1 - (G0 unclear_para rate) / (G0 unclear_word rate), pooled; intervals over scenarios inside pairs and
    over pairs."""
    unit_rows = {}
    for p in pair_list:
        w = per_scenario(got, p, "unclear_word", "g0")
        q = per_scenario(got, p, "unclear_para", "g0")
        rr = [(w[s][0], w[s][1], q[s][0], q[s][1]) for s in range(pairs.N_SCENARIOS) if w[s][1] or q[s][1]]
        if rr:
            unit_rows[p] = rr

    def stat(g):
        rr = [r for v in g.values() for r in v]
        nw, nq = sum(r[1] for r in rr), sum(r[3] for r in rr)
        rw = sum(r[0] for r in rr) / nw if nw else 0.0
        rq = sum(r[2] for r in rr) / nq if nq else 0.0
        return 1 - rq / rw if rw > 0 else float("-inf")
    if not unit_rows:
        return None
    point, lo, hi = stats.cluster_bootstrap(unit_rows, stat)
    pair_rows = [tuple(sum(r[i] for r in v) for i in range(4)) for v in unit_rows.values()]
    _, plo, phi = stats.cluster_bootstrap({"all": pair_rows}, stat)
    finite = lambda x: None if x == float("-inf") else x  # -inf: the word rate is 0 in that sample (no reduction exists)
    return {"value": finite(point), "ci_scenarios": [finite(lo), finite(hi)], "ci_pairs": [finite(plo), finite(phi)],
            "note": "a null limit means that the word rate is 0 in some bootstrap samples, so the interval has no lower limit"}


def analyse_model(loaded, chosen):
    got, mr = loaded["got"], loaded["missing_reads"]
    miss = lambda p, k, f: sum(mr.get((p, k, f), {}).values())
    res = {"folders": loaded["used"], "missing_folders": loaded["missing"], "out_of_schema_values": loaded["out_of_schema"],
           "missing_reads": {"|".join(c): dict(v) for c, v in mr.items()},
           "reads_per_unit": max((len(v) for v in got.values()), default=0)}
    res["cells"] = {p: {f"{k}|{f}": cell_rate(got, p, k, f, miss(p, k, f)) for k in KINDS for f in FORMS}
                    for p in chosen + [CAL]}
    res["pooled"] = {f"{k}|{f}": pooled_rate(got, chosen, k, f, sum(miss(p, k, f) for p in chosen))
                     for k in KINDS for f in FORMS}
    res["alone_general_g0"] = pooled_rate(got, chosen, "clear_general", "g0",
                                          sum(miss(p, "clear_general", "g0") for p in chosen), measure=1)
    res["alone_general_g0_cal"] = cell_rate(got, CAL, "clear_general", "g0", miss(CAL, "clear_general", "g0"), measure=1)
    word_para = lambda p: paired_units(got, p, ("unclear_word", "g0"), ("unclear_para", "g0"))
    g4_g0 = lambda p, k: paired_units(got, p, (k, "g0"), (k, "g4"))
    res["per_pair"] = {p: {"para_minus_word_g0": contrast({p: word_para(p)}),
                           "g4_minus_g0_unclear_word": contrast({p: g4_g0(p, "unclear_word")}),
                           "g4_minus_g0_clear_specific": contrast({p: g4_g0(p, "clear_specific")})}
                       for p in chosen + [CAL]}
    res["contrasts"] = {"para_minus_word_g0": contrast({p: word_para(p) for p in chosen}),
                        "g4_minus_g0_unclear_word": contrast({p: g4_g0(p, "unclear_word") for p in chosen}),
                        "g4_minus_g0_clear_specific": contrast({p: g4_g0(p, "clear_specific") for p in chosen})}
    res["h2_reduction"] = reduction(got, chosen)
    return res


def at_least(words, ok, k, named):
    """A prediction that holds when at least k models of `named` meet it."""
    met = [m for m in named if ok.get(m)]
    absent = [m for m in named if m not in ok]
    if len(met) >= k:
        status = "held"
    elif len(met) + len(absent) < k:
        status = "failed"
    else:
        status = "undecided; incomplete (not fetched: " + ", ".join(absent) + ")"
    return {"words": words, "held": status == "held", "status": status, "models_meeting": met, "models_missing": absent}


def every(words, ok, named):
    absent = [m for m in named if m not in ok]
    if not all(ok.values()):
        status = "failed"
    elif absent:
        status = "held so far; incomplete (not fetched: " + ", ".join(absent) + ")"
    else:
        status = "held"
    return {"words": words, "held": status == "held", "status": status, "models_missing": absent}


def predictions(res, n_pairs):
    need_pairs = -(-5 * n_pairs // 8)  # 62.5% of the pairs, rounded up: 8 of 12
    p = {}
    h1 = {m: {"rate": r["pooled"]["unclear_word|g0"]["share"], "pairs_at_10pct": r["pooled"]["unclear_word|g0"]["pairs_at_10pct"]}
          for m, r in res.items()}
    p["H1"] = {**every(f"on the unclear items with the word under G0, Sonnet, Sol and Luna each write the collision "
                       f"value in at least 30% of reads over all pairs, and each in at least {need_pairs} of the "
                       f"{n_pairs} pairs at a rate of 10% or more",
                       {m: v["rate"] is not None and v["rate"] >= 0.30 and v["pairs_at_10pct"] >= need_pairs
                        for m, v in h1.items() if m in ("sonnet", "sol", "luna")}, ("sonnet", "sol", "luna")),
               "value": h1}
    h2 = {m: (r["h2_reduction"] or {}).get("value") for m, r in res.items()}
    p["H2"] = {**at_least("the paraphrase lowers that rate by at least two thirds for at least 3 of the 5 models",
                          {m: v is not None and v >= 2 / 3 for m, v in h2.items() if m in DESIGN}, 3, DESIGN),
               "value": h2}
    h3 = {m: 0.0 - r["contrasts"]["g4_minus_g0_clear_specific"]["mean"] if r["contrasts"]["g4_minus_g0_clear_specific"]["mean"]
          is not None else None for m, r in res.items()}  # G0 minus G4: the fall of the correct value
    p["H3"] = {**at_least("on the clear and specific items, G4 lowers the correct value by at least 10 points for at "
                          "least 3 of the 5 models (the trade repeats)",
                          {m: v is not None and v >= 0.10 for m, v in h3.items() if m in DESIGN}, 3, DESIGN),
               "value": h3}
    h4 = {m: r["alone_general_g0"]["share"] for m, r in res.items()}
    p["H4"] = {**every("on the clear and general items, every model writes the collision value alone in 5% or less of "
                       "G0 reads", {m: v is not None and v <= 0.05 for m, v in h4.items() if m in DESIGN}, DESIGN),
               "value": h4}
    for v in p.values():
        v["note"] = "astra is a fill model: its value is shown and does not count"
    return p


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def pts(x):
    return "-" if x is None else f"{100 * x:+.1f}"


def cell_text(r):
    s = f"{pct(r['share'])} ({r['k']}/{r['n']})"
    if r.get("ci"):
        s += f" [{pct(r['ci'][0])}, {pct(r['ci'][1])}]"
    if r.get("missing"):
        s += f" m={r['missing']}"
    return s


def pooled_text(r):
    s = f"{pct(r['share'])} ({r['k']}/{r['n']})"
    if r.get("ci_scenarios"):
        s += f" [{pct(r['ci_scenarios'][0])}, {pct(r['ci_scenarios'][1])}] / [{pct(r['ci_pairs'][0])}, {pct(r['ci_pairs'][1])}]"
    if r.get("missing"):
        s += f" m={r['missing']}"
    if r.get("worst_case"):
        s += f"; worst case [{pct(r['worst_case'][0])}, {pct(r['worst_case'][1])}]"
    return s


def contrast_text(c):
    if c.get("mean") is None:
        return "-"
    s = f"{pts(c['mean'])} [{pts(c['ci_scenarios'][0])}, {pts(c['ci_scenarios'][1])}]"
    if c.get("ci_pairs"):
        s += f" / [{pts(c['ci_pairs'][0])}, {pts(c['ci_pairs'][1])}]"
    return s + f" ({c['higher']} up, {c['lower']} down, p {c['sign_p']:.2g})"


def rounded(x):
    if isinstance(x, float):
        return round(x, 4)
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rounded(v) for v in x]
    return x


def markdown(res, preds, missing, chosen):
    cells = [f"{k}|{f}" for k in KINDS for f in FORMS]
    L = ["## 5. Word and schema pairs (experiment H)", "",
         f"Exploratory. Constructed text. {len(chosen)} pairs ({', '.join(chosen)}), 20 scenarios per pair, 4 item kinds, "
         "forms G0 (original values) and G4 (a neutral token for the collision value). The calibration pair `hotel` "
         "is reported apart. Outcome: the `type` list holds the collision value (the locked scoring rule). Intervals "
         "of a pooled rate or contrast: first over scenarios inside pairs, then over pairs. The mixed model is not run "
         "(no statsmodels, no R).", ""]
    if missing:
        L += [f"Not fetched at this run: {', '.join(missing)}.", ""]
    L += ["### Reads", "", "| Model | Folders | Reads per item | Valid reads | Missing reads (by reason) | "
          "Out-of-schema type values |", "|---|---|---|---|---|---|"]
    for m, r in res.items():
        n_valid = sum(c["n"] for p in r["cells"].values() for c in p.values())
        reasons = collections.Counter()
        for v in r["missing_reads"].values():
            reasons.update(v)
        L.append(f"| {m} | {', '.join(r['folders'])} | {r['reads_per_unit']} | {n_valid} | "
                 f"{sum(reasons.values())} ({', '.join(f'{k} {v}' for k, v in reasons.items()) or 'none'}) | "
                 f"{r['out_of_schema_values']} |")
    L += ["", "### Pooled over the 12 pairs: rate of the collision value (valid reads; 95% intervals: scenarios inside "
          "pairs / pairs)", "", "| Model | " + " | ".join(c.replace("|", ", ") for c in cells) + " |",
          "|---|" + "---|" * len(cells)]
    for m, r in res.items():
        L.append(f"| {m}{' (fill)' if m not in DESIGN else ''} | " + " | ".join(pooled_text(r["pooled"][c]) for c in cells) + " |")
    L += ["", "### Pooled contrasts (mean of unit differences, points; intervals: scenarios inside pairs / pairs; sign "
          "test over items)", "", "| Model | Paraphrase - word (G0, unclear) | G4 - G0 (unclear_word) | "
          "G4 - G0 (clear_specific) | H2 reduction of the word rate | Pairs with G0 unclear_word >= 10% | "
          "G0 clear_general, collision value alone |", "|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        red = r["h2_reduction"]
        lim = lambda x: "no lower limit" if x is None else pct(x)
        red_t = (f"{pct(red['value'])} [{lim(red['ci_scenarios'][0])}, {pct(red['ci_scenarios'][1])}] / "
                 f"[{lim(red['ci_pairs'][0])}, {pct(red['ci_pairs'][1])}]") if red else "-"
        L.append(f"| {m}{' (fill)' if m not in DESIGN else ''} | {contrast_text(r['contrasts']['para_minus_word_g0'])} | "
                 f"{contrast_text(r['contrasts']['g4_minus_g0_unclear_word'])} | "
                 f"{contrast_text(r['contrasts']['g4_minus_g0_clear_specific'])} | {red_t} | "
                 f"{r['pooled']['unclear_word|g0']['pairs_at_10pct']} of {len(chosen)} | {pooled_text(r['alone_general_g0'])} |")
    for m, r in res.items():
        L += ["", f"### {m}: rate of the collision value per pair, item kind and form (95% interval over scenarios; "
              "m = missing reads)", "", "| Pair | " + " | ".join(c.replace("|", ", ") for c in cells) + " |",
              "|---|" + "---|" * len(cells)]
        for p in chosen + [CAL]:
            label = f"{p} (calibration)" if p == CAL else p
            L.append(f"| {label} | " + " | ".join(cell_text(r["cells"][p][c]) for c in cells) + " |")
    L += ["", "### Per pair: the paired contrasts (points; 95% interval over scenarios; sign test over scenarios or items)",
          "", "| Model | Pair | Paraphrase - word (G0) | G4 - G0 (unclear_word) | G4 - G0 (clear_specific) |",
          "|---|---|---|---|---|"]
    for m, r in res.items():
        for p in chosen + [CAL]:
            c = r["per_pair"][p]
            L.append(f"| {m} | {p}{' (calibration)' if p == CAL else ''} | {contrast_text(c['para_minus_word_g0'])} | "
                     f"{contrast_text(c['g4_minus_g0_unclear_word'])} | {contrast_text(c['g4_minus_g0_clear_specific'])} |")
    L += ["", "### Predictions (point values; the 5 models are Sonnet, Haiku, Opus, Sol, Luna; Astra is shown, not counted)",
          "", "| # | Words | Value | Held |", "|---|---|---|---|"]
    for k, v in preds.items():
        L.append(f"| {k} | {v['words']} | {json.dumps(rounded(v['value']))} | {v['status']} |")
    return "\n".join(L) + "\n"


def main():
    index = spec_index()
    chosen = [c for c in json.loads(pairs.PAIRS_JSON.read_text())["chosen"]]
    res, missing = {}, []
    for m in MODELS:
        loaded = load(m, index)
        if loaded is None:
            missing += [f for f, _, _ in SOURCES[m]] if m == "astra" else [SOURCES[m][0][0]]
            continue
        missing += loaded["missing"]
        res[m] = analyse_model(loaded, chosen)
    preds = predictions(res, len(chosen))
    OUT.mkdir(exist_ok=True)
    (OUT / "h.json").write_text(json.dumps({"exploratory": True, "missing": missing, "pairs": chosen, "calibration": CAL,
                                            "models": res, "predictions": preds}, indent=1, default=float))
    (OUT / "h.md").write_text(markdown(res, preds, missing, chosen))
    with open(OUT / "fig_pairs.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "pair", "kind", "form", "k", "n", "missing", "share", "ci_low", "ci_high"])
        for m, r in res.items():
            for p, cs in r["cells"].items():
                for key, c in cs.items():
                    kind, form = key.split("|")
                    w.writerow([m, p, kind, form, c["k"], c["n"], c["missing"], c["share"],
                                *(c.get("ci") or [None, None])])
    print(f"missing folders: {missing}")
    print((OUT / "h.md").read_text())


if __name__ == "__main__":
    main()
