"""Review round 2: four post hoc analyses (an internal file, "New post hoc analyses", items
1 to 4). Exploratory and post hoc: every analysis here was chosen after the results. No model call.

Inputs: the opened stage-1 answers main/exp0/open/em1_<model>/raw.jsonl (7 models, the opened held-out subset), read
with the functions of the frozen main/exp0/analysis.py (imported; its main never runs and its outputs are not
written); the round-9 reads of natural_analyze.load(); MultiWOZ 2.4 and hotel_db.json. Outputs:
r10/analysis/out/r2_posthoc.md and r2_posthoc.json.

Definitions (fixed here):
1. Held-out test with the hotel-only outcome. Registered outcome: the parsed `type` list holds `hotel`
   (analysis.hotel). Hotel-only outcome: the list holds `hotel` and not `guesthouse`. Parsing, validity, samples (213
   natural, 77 goal-hotel), read 1 and the panel mean are those of analysis.py: per dialogue, the mean over the models
   with a valid pair of (t_renamed minus t_legacy); then the mean over dialogues. Per model: the mean paired
   difference over dialogues and the exact sign test over dialogues (stats.sign_test). Base rate: the share of valid
   read 1 under t_legacy with the outcome, per model and sample.
2. Random-deletion reference. A form that deletes baseline `hotel` values at random, with no regard to the dialogue,
   loses (baseline correct rate x correct weight) / (baseline wrong rate x wrong weight) correct values per wrong value
   removed, at any deletion size. Held-out: weights 281 (natural, wrong) and 97 (goal-hotel, correct), baseline
   t_legacy, renames t_renamed and f4 (analysis.trade_rows and trade_block: read 1, dialogues with both cells valid,
   the panel row adds the models' read-1 values per dialogue). Earlier: weights 994 (S1t) + 490 (S3) wrong and 545
   (S2) correct, baseline F0, renames F1, F2, F4, F6, the paired cells of review/plan14/harm_by_model.py (pooled reads
   over the dialogues with reads under both forms), stats.trade_interval.
   Selectivity D = (share of baseline correct values kept) minus (share of baseline wrong values kept). When the rename
   removes wrong values, its ratio is below the random-deletion ratio exactly when D > 0. D has a 95% cluster
   bootstrap interval (stats.cluster_bootstrap, dialogues resampled inside each group).
3. Word-or-meaning tests. Groups: S2 dialogues whose brief sets hotel (gold.brief_type(d) == "hotel"); S1t dialogues
   whose brief sets no type in info and in fail_info; S3 dialogues whose brief sets guesthouse (gold.brief_type(d) ==
   "guesthouse"). Outcome natural_analyze.hotel. Rate: pooled over valid reads. Paired difference: per dialogue, the
   mean of the form's valid reads minus the mean of the F0 valid reads, over dialogues with both; mean, 95% cluster
   bootstrap interval, exact sign test over dialogues.
4. Visibility. The call is the brief (briefsearch.brief_of: area, pricerange, stars, parking, internet, name; no
   brief in these sets names a venue) with `type` removed, or with type = ("hotel",). The tool shows the first 5
   venues of briefsearch.search in the order of hotel_db.json (briefsearch.result_rows). A fitting hotel is a venue of
   type hotel for which briefsearch.fits(venue, brief) is true. Sets: the S2 dialogues whose brief sets hotel, and the
   prefixes of the 554 (r10 group "booked") whose brief sets hotel. This uses the brief as the call, not the model's
   call.

Choices (where the request was not specific, the plainest reading, with the reason):
- Random-deletion baseline rates come from the same paired rows as the rename's trade (like for like). The
  unpaired t_legacy base rates are in analysis 1.
- Earlier trades need S1t, S3 and S2 reads, as harm_by_model.py and b_analyze.py require. Cells without S3 reads (Luna
  F2 and F6, the open models) get a second, labelled variant with S1t as the only wrong group (weight 994): the rename
  ratio and the random-deletion ratio then use the same groups.
- "Brief sets hotel" for the 554 prefixes uses goal.hotel.info only (gold.brief_type), as for S2, because the search
  uses info. The count of prefixes where only fail_info sets hotel is reported.
- The held-out hotel-only trade (analysis 2, extra rows) uses the same estimator with the hotel-only outcome, because
  REVISION-DECISIONS-R2.md asks for the hotel-only outcome wherever the hotel filter is counted.
- Analysis 4 intervals: stats.cluster_bootstrap over dialogues of the 0/1 values. They describe the dialogue sample;
  the venue search itself has no randomness.
Usage (from explore/): .venv/bin/python -I r10/analysis/r2_posthoc.py
"""
import importlib.util
import json
import math
import pathlib
import sys

sys.dont_write_bytecode = True  # write no cache file next to the frozen analysis.py

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import natural_analyze as na  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
EXP0 = EXPLORE / "main" / "exp0"
OPEN = EXP0 / "open"
DRAWS, SEED = 2000, 20261112
R9_MODELS = ("sonnet", "haiku", "sol", "luna", "deepseek", "qwen", "gemma")
R9_FORMS = ("f1", "f2", "f4", "f6")
R9_SIZES = {"S1t": 994, "S3": 490, "S2": 545}
R9_SIZES_NO_S3 = {"S1t": 994, "S2": 545}
SHOWN = 5  # the tool shows at most 5 venues (briefsearch.result_rows)


def frozen_analysis():
    """main/exp0/analysis.py as a module under another name (r10/analysis is a package called `analysis`)."""
    spec = importlib.util.spec_from_file_location("exp0_frozen_analysis", EXP0 / "analysis.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.stats is stats and mod.bs is bs, "the frozen analysis imported other stats or briefsearch modules"
    return mod


X0 = frozen_analysis()


def hotel_only(f, d=None):
    t = f["type"]
    return isinstance(t, tuple) and "hotel" in t and "guesthouse" not in t


OUTCOMES = {"registered": X0.hotel, "hotel_only": hotel_only}


def interval(vals):
    if not vals:
        return {"n": 0, "mean": None, "ci95": [None, None]}
    point, lo, hi = stats.cluster_bootstrap({"u": vals}, lambda g: sum(g["u"]) / len(g["u"]), DRAWS, SEED)
    return {"n": len(vals), "mean": point, "ci95": [lo, hi]}


def paired(diffs):
    row = interval(diffs)
    up, down = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    row.update(form_higher=up, form_lower=down, sign_p=stats.sign_test(up, down))
    return row


# ------------------------------------------------------------------------------------------------- 1. held-out test
def heldout_tests(cells, units):
    panel = list(X0.PANEL)
    tests = {}
    for c in X0.FAMILY:
        u = units[c.sample]
        block = {"sample": c.sample, "dialogues": len(u)}
        for name, measure in OUTCOMES.items():
            per_d = []
            for d in u:
                diffs = [x for m in panel if (x := X0.model_diff(cells, m, c, d, measure=measure)) is not None]
                if diffs:
                    per_d.append(sum(diffs) / len(diffs))
            models = {m: paired([x for d in u if (x := X0.model_diff(cells, m, c, d, measure=measure)) is not None])
                      for m in panel}
            block[name] = {"panel": interval(per_d), "models": models}
        tests[c.name] = block
    base = {s: {m: {name: X0.share_block(cells, m, (p, "t_legacy"), units[s], measure)
                    for name, measure in OUTCOMES.items()} for m in panel}
            for s, p in (("natural", "nat"), ("goal_hotel", "hot"))}
    return {"tests": tests, "base_rates_t_legacy": base}


def check_reproduction(h1, trades):
    """The registered outcome and the trades must equal stage1.json (the output of the frozen run)."""
    ref = json.loads((EXP0 / "stage1.json").read_text())["results"]
    out = []
    for t in ref["part1_family"]["tests"]:
        mine = h1["tests"][t["test"]]["registered"]["panel"]
        out.append(abs(mine["mean"] - t["mean"]) < 1e-5 and all(abs(a - b) < 1e-5 for a, b in zip(mine["ci95"], t["ci95"])))
    for form, rows in ref["part5_a1"]["c_trade"].items():
        for m, t in rows.items():
            mine = trades[form][m]["trade"]
            out.append(abs(mine["ratio"] - t["ratio"]) < 1e-5 and all(abs(a - b) < 1e-5
                                                                      for a, b in zip(mine["ci95"], t["ci95"])))
    return all(out), len(out)


# --------------------------------------------------------------------------------------- 2. random-deletion reference
def pooled(rows, i):
    n = sum(r[i + 1] for r in rows)
    return sum(r[i] for r in rows) / n if n else None


def random_ratio(rows_by_group, sizes, wrong, correct):
    w0 = sum(pooled(rows_by_group[g], 0) * sizes[g] for g in wrong)
    c0 = pooled(rows_by_group[correct], 0) * sizes[correct]
    return c0 / w0 if w0 > 0 else None


def selectivity(rows_by_group, sizes, wrong, correct):
    """D = share of baseline correct values kept minus share of baseline wrong values kept, with its interval."""
    bad = [0]

    def stat(s):
        w0 = sum(pooled(s[g], 0) * sizes[g] for g in wrong)
        w1 = sum(pooled(s[g], 2) * sizes[g] for g in wrong)
        c0, c1 = pooled(s[correct], 0), pooled(s[correct], 2)
        if not w0 or not c0:
            bad[0] += 1
            return 0.0
        return c1 / c0 - w1 / w0

    groups = {g: rows_by_group[g] for g in (*wrong, correct)}
    point, lo, hi = stats.cluster_bootstrap(groups, stat, DRAWS, SEED)
    return {"D": point, "ci95": [lo, hi], "draws_without_baseline_values": bad[0]}


def compare(rows_by_group, sizes, wrong, correct):
    groups = {g: rows_by_group[g] for g in (*wrong, correct)}
    (removed, lost, ratio), lo, hi = stats.trade_interval(groups, sizes, DRAWS, SEED, wrong=wrong, correct=correct)
    rnd = random_ratio(groups, sizes, wrong, correct)
    sel = selectivity(groups, sizes, wrong, correct)
    defined = removed > 0
    return {"paired_dialogues": {g: len(r) for g, r in groups.items()},
            "baseline_rates": {g: pooled(r, 0) for g, r in groups.items()},
            "trade": {"removed": removed, "lost": lost, "ratio": ratio if defined else None, "ci95": [lo, hi]},
            "random_deletion_ratio": rnd, "selectivity": sel,
            "below_random": (ratio < rnd) if defined and rnd is not None else None,
            "below_random_interval_excludes_0": sel["ci95"][0] > 0 or sel["ci95"][1] < 0}


def trade_rows_measure(cells, models, form, units, measure):
    """analysis.trade_rows with another outcome (analysis.trade_rows has no measure argument)."""
    out = {}
    for group, sample in (("nat", "natural"), ("hot", "goal_hotel")):
        rows = []
        for d in units[sample]:
            pairs = [(a, b) for m in models
                     if (a := X0.value(cells, m, (group, "t_legacy"), d, measure)) is not None
                     and (b := X0.value(cells, m, (group, form), d, measure)) is not None]
            if pairs:
                rows.append((sum(a for a, _ in pairs), len(pairs), sum(b for _, b in pairs), len(pairs)))
        out[group] = rows
    return out


def heldout_random(cells, units):
    panel = list(X0.PANEL)
    res = {}
    for name, measure in OUTCOMES.items():
        res[name] = {}
        for form in ("t_renamed", "f4"):
            res[name][form] = {}
            for who in panel + ["panel"]:
                models = panel if who == "panel" else [who]
                rows = (X0.trade_rows(cells, models, form, units) if name == "registered"
                        else trade_rows_measure(cells, models, form, units, measure))
                res[name][form][who] = compare(rows, X0.TRADE_SIZES, ("nat",), "hot")
    return res


def r9_cells(reads, model, form, units_of, groups):
    out = {}
    for g in groups:
        a = na.hits(reads, (model, "f0"), units_of[g], na.hotel)
        b = na.hits(reads, (model, form), units_of[g], na.hotel)
        out[g] = [(sum(a[d]), len(a[d]), sum(b[d]), len(b[d])) for d in sorted(set(a) & set(b))]
    return out


def earlier_random(reads, g):
    units_of = {G: {d.removesuffix(".json") for d in g[k]} for G, k in (("S1t", "s1t"), ("S3", "s3"), ("S2", "s2"))}
    res = {}
    for m in R9_MODELS:
        for f in R9_FORMS:
            c = r9_cells(reads, m, f, units_of, R9_SIZES)
            row = {"paired_dialogues": {G: len(v) for G, v in c.items()}}
            if all(c.values()):
                row["main"] = compare(c, R9_SIZES, ("S1t", "S3"), "S2")
            if c["S1t"] and c["S2"]:
                row["no_s3_variant"] = compare(c, R9_SIZES_NO_S3, ("S1t",), "S2")
            res[f"{m} {f}"] = row
    return res


# ----------------------------------------------------------------------------------------- 3. word-or-meaning tests
def brief_groups(data, g):
    s2 = [d for d in g["s2"] if gold.brief_type(data[d]) == "hotel"]
    s1t = [d for d in g["s1t"] if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    s3 = [d for d in g["s3"] if gold.brief_type(data[d]) == "guesthouse"]
    strip = lambda ids: {d.removesuffix(".json") for d in ids}
    return {"S2, brief sets hotel": strip(s2), "S1t, brief sets no type": strip(s1t),
            "S3, brief sets guesthouse": strip(s3)}


def word_or_meaning(reads, groups):
    res = {}
    for gname, units in groups.items():
        res[gname] = {"dialogues": len(units), "models": {}}
        for m in R9_MODELS:
            base = na.hits(reads, (m, "f0"), units, na.hotel)
            row = {}
            for f in ("f0",) + R9_FORMS:
                h = na.hits(reads, (m, f), units, na.hotel)
                k, n = sum(map(sum, h.values())), sum(map(len, h.values()))
                if not n:
                    continue
                cell = {"k": k, "n": n, "dialogues": len(h), "rate": k / n}
                if f != "f0" and base:
                    both = sorted(set(h) & set(base))
                    diffs = [sum(h[d]) / len(h[d]) - sum(base[d]) / len(base[d]) for d in both]
                    cell["paired"] = paired(diffs) if diffs else None
                row[f] = cell
            if row:
                res[gname]["models"][m] = row
    return res


# ------------------------------------------------------------------------------------------------- 4. visibility
def call_of(brief, keep_type):
    fields = {f: None for f in bs.FIELDS}
    for slot in ("area", "pricerange", "stars", "parking", "internet"):
        v = brief.get(slot)
        if v is not None and str(v).lower() not in bs.DONTCARE:
            fields[slot] = (str(v).lower(),)
    name = brief.get("name")
    fields["name"] = name if name and str(name).lower() not in bs.DONTCARE else None
    fields["type"] = ("hotel",) if keep_type else None
    return fields


def visibility(data, ids, db):
    by_name = {gold.norm(v["name"]): v for v in db}
    rows = {"type_removed": [], "type_hotel_kept": []}
    for d in ids:
        brief = bs.brief_of(data[d])
        fitting = [v for v in db if v["type"] == "hotel" and bs.fits(v, brief)]
        for key, keep in (("type_removed", False), ("type_hotel_kept", True)):
            found = bs.search(db, call_of(brief, keep))
            shown = [by_name[gold.norm(r["name"])] for r in bs.result_rows(found, SHOWN)["results"]]
            in_view = any(v["type"] == "hotel" and bs.fits(v, brief) for v in shown)
            rows[key].append({"none_in_first_5": not in_view, "no_hotel_fits": not fitting,
                              "hidden_by_limit": bool(fitting) and not in_view, "total": len(found)})
    out = {"dialogues": len(ids), "named_briefs": sum(1 for d in ids if bs.brief_of(data[d]).get("name"))}
    for key, rr in rows.items():
        out[key] = {k: interval([float(r[k]) for r in rr]) for k in ("none_in_first_5", "no_hotel_fits",
                                                                       "hidden_by_limit")}
        out[key]["more_than_5_results"] = sum(r["total"] > SHOWN for r in rr)
        out[key]["empty_results"] = sum(r["total"] == 0 for r in rr)
        out[key]["mean_results"] = sum(r["total"] for r in rr) / len(rr) if rr else None
    return out


# ------------------------------------------------------------------------------------------------------ the report
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
    return "-" if x is None or (isinstance(x, float) and (math.isinf(x) or math.isnan(x))) else f"{x:.{digits}f}"


def ci_num(ci):
    hi = "no upper limit" if ci[1] is not None and math.isinf(ci[1]) else num(ci[1])
    return f"[{num(ci[0])}, {hi}]"


def pval(p):
    return f"{p:.4f}" if p >= 0.00005 else f"{p:.1e}"


def yes(b):
    return "-" if b is None else ("yes" if b else "no")


def md_heldout(h1, ok):
    L = ["## 1. Held-out test with the hotel-only outcome (post hoc)", "",
         "Read 1 of the opened stage-1 answers, 7 models. Registered outcome: `type` holds `hotel`. Hotel-only: `type` "
         "holds `hotel` and not `guesthouse`. Panel mean of t_renamed minus t_legacy, in points; 95% cluster bootstrap "
         "interval over dialogues. Registered columns reproduce RESULT-STAGE1.md part 1 and part 5(c): "
         f"{yes(ok)}.", "",
         "| Test | Sample | Panel, registered | 95% interval | Panel, hotel-only | 95% interval |", "|---|---|---|---|---|---|"]
    for name, t in h1["tests"].items():
        a, b = t["registered"]["panel"], t["hotel_only"]["panel"]
        L.append(f"| {name} | {t['sample']} ({a['n']}) | {pts(a['mean'])} | {ci_pts(a['ci95'])} | {pts(b['mean'])} | "
                 f"{ci_pts(b['ci95'])} |")
    for name, t in h1["tests"].items():
        L += ["", f"**{name}** ({t['sample']} sample), per model (post hoc)", "",
              "| Model | Dialogues | Registered | 95% interval | Sign (higher/lower), p | Hotel-only | 95% interval | "
              "Sign (higher/lower), p |", "|---|---|---|---|---|---|---|---|"]
        for m, a in t["registered"]["models"].items():
            b = t["hotel_only"]["models"][m]
            L.append(f"| {m} | {a['n']} | {pts(a['mean'])} | {ci_pts(a['ci95'])} | {a['form_higher']}/{a['form_lower']}, "
                     f"{pval(a['sign_p'])} | {pts(b['mean'])} | {ci_pts(b['ci95'])} | {b['form_higher']}/"
                     f"{b['form_lower']}, {pval(b['sign_p'])} |")
    L += ["", "**Base rates under t_legacy** (read 1, post hoc)", "",
          "| Model | Natural, registered | Natural, hotel-only | Goal-hotel, registered | Goal-hotel, hotel-only |",
          "|---|---|---|---|---|"]
    base = h1["base_rates_t_legacy"]
    for m in base["natural"]:
        cell = lambda s, o: (f"{base[s][m][o]['k']}/{base[s][m][o]['n']} ({pct(base[s][m][o]['share'])}, "
                             f"{ci_pct(base[s][m][o]['ci95'])})")
        L.append(f"| {m} | {cell('natural', 'registered')} | {cell('natural', 'hotel_only')} | "
                 f"{cell('goal_hotel', 'registered')} | {cell('goal_hotel', 'hotel_only')} |")
    return L


def compare_row(label, r):
    t, s = r["trade"], r["selectivity"]
    ratio = num(t["ratio"]) if t["ratio"] is not None else "- (removes no wrong values)"
    return (f"| {label} | {', '.join(str(v) for v in r['paired_dialogues'].values())} | {num(t['removed'], 1)} | "
            f"{num(t['lost'], 1)} | {ratio} | {ci_num(t['ci95'])} | {num(r['random_deletion_ratio'])} | "
            f"{yes(r['below_random'])} | {num(s['D'])} {ci_num(s['ci95'])} |")


HEAD2 = ("| {who} | Paired dialogues | Wrong removed | Correct lost | Rename ratio | 95% interval | Random-deletion "
         "ratio | Below random | D [95% interval] |")


def md_random(h2, e2):
    L = ["", "## 2. Random-deletion reference for the renames (post hoc)", "",
         "Random deletion of baseline `hotel` values loses (baseline correct rate x correct weight) / (baseline wrong "
         "rate x wrong weight) correct values per wrong value removed. D = share of baseline correct values kept minus "
         "share of baseline wrong values kept; D > 0 means the rename keeps correct values better than random "
         "deletion (its ratio is lower).", "",
         "### 2a. Held-out (weights natural 281, goal-hotel 97; baseline t_legacy; read 1)", ""]
    for name, forms in h2.items():
        for form, rows in forms.items():
            L += [f"**{form}**, {name} outcome" + (" (extra rows, post hoc)" if name == "hotel_only" else ""), "",
                  HEAD2.format(who="Model"), "|---|---|---|---|---|---|---|---|---|"]
            L += [compare_row(m, r) for m, r in rows.items()] + [""]
    L += ["### 2b. Earlier experiments (round 9; weights S1t 994 + S3 490 wrong, S2 545 correct; baseline F0)", "",
          "Paired dialogues: S1t, S3, S2.", "", HEAD2.format(who="Model, form"), "|---|---|---|---|---|---|---|---|---|"]
    L += [compare_row(k, r["main"]) for k, r in e2.items() if "main" in r]
    L += ["", "Variant without S3 (S1t 994 wrong, S2 545 correct), for every cell with S1t and S2 reads. Paired "
          "dialogues: S1t, S2.", "", HEAD2.format(who="Model, form"), "|---|---|---|---|---|---|---|---|---|"]
    L += [compare_row(k, r["no_s3_variant"]) for k, r in e2.items() if "no_s3_variant" in r]
    none = [f"{k} ({', '.join(f'{g} {n}' for g, n in r['paired_dialogues'].items())})" for k, r in e2.items()
            if "main" not in r]
    L += ["", "Cells without reads on all three groups (paired dialogues per group): " + "; ".join(none) + "."]
    return L


def md_words(w3):
    L = ["", "## 3. Word-or-meaning tests on brief-agreeing dialogues (post hoc)", "",
         "Round-9 reads (natural_analyze.load). Rate of `type = hotel` over valid reads (dialogues with reads). Paired "
         "difference: form minus F0, per-dialogue means, in points, 95% cluster bootstrap interval, exact sign test "
         "over dialogues (form higher / form lower). A dash: no reads.", ""]
    for gname, gr in w3.items():
        L += [f"### {gname} ({gr['dialogues']} dialogues)", "",
              "| Model | F0 | F1 | F2 | F4 | F6 |", "|---|---|---|---|---|---|"]
        for m, row in gr["models"].items():
            cells = []
            for f in ("f0",) + R9_FORMS:
                c = row.get(f)
                if c is None:
                    cells.append("-")
                    continue
                txt = f"{pct(c['rate'])} ({c['dialogues']})"
                p = c.get("paired")
                if p:
                    txt += (f"; {pts(p['mean'])} {ci_pts(p['ci95'])}, {p['form_higher']}/{p['form_lower']}, "
                            f"p {pval(p['sign_p'])}")
                cells.append(txt)
            L.append(f"| {m} | " + " | ".join(cells) + " |")
        L.append("")
    return L


def md_visibility(v4):
    L = ["## 4. Visibility of fitting hotels when a correct filter is dropped (post hoc, venue data only)", "",
         "The call is the brief itself, not the model's call: the brief's area, price range, stars, parking and "
         "internet, with `type` removed (or with type = hotel kept). The tool shows the first 5 venues in the order "
         "of hotel_db.json (33 venues: 24 guesthouses, 9 hotels). Shares over dialogues, 95% cluster bootstrap "
         "interval.", "",
         "| Set | Call | Dialogues | No fitting hotel in the first 5 | No hotel fits the brief at all | A fitting hotel "
         "exists but is not in the first 5 | More than 5 results | Empty result |", "|---|---|---|---|---|---|---|---|"]
    for sname, v in v4.items():
        for key, label in (("type_removed", "type removed"), ("type_hotel_kept", "type = hotel kept")):
            x = v[key]
            f = lambda k: f"{pct(x[k]['mean'])} {ci_pct(x[k]['ci95'])}"
            L.append(f"| {sname} | {label} | {v['dialogues']} | {f('none_in_first_5')} | {f('no_hotel_fits')} | "
                     f"{f('hidden_by_limit')} | {x['more_than_5_results']} | {x['empty_results']} |")
    notes = [f"{s}: briefs that name a venue {v['named_briefs']}" for s, v in v4.items()]
    if "554 prefixes, brief sets hotel" in v4:
        notes.append(f"prefixes where only fail_info sets hotel (not counted): {v4['554 prefixes, brief sets hotel']['fail_info_only']}")
    L += ["", "Notes: " + "; ".join(notes) + "."]
    return L


def main():
    data, g = runs.context()
    db = gold.hotel_db()

    cells, _, units, _, nrows, _ = X0.load(OPEN, list(X0.PANEL))
    h1 = heldout_tests(cells, units)
    h2 = heldout_random(cells, units)
    ok, n_checked = check_reproduction(h1, h2["registered"])

    reads, invalid = na.load()
    e2 = earlier_random(reads, g)
    w3 = word_or_meaning(reads, brief_groups(data, g))

    s2_hotel = [d for d in g["s2"] if gold.brief_type(data[d]) == "hotel"]
    pre_hotel = [d for d in g["booked"] if gold.brief_type(data[d]) == "hotel"]
    fail_only = sum(1 for d in g["booked"] if gold.brief_type(data[d]) is None
                    and gold.brief_type(data[d], "fail_info") == "hotel")
    v4 = {"S2, brief sets hotel": visibility(data, s2_hotel, db),
          "554 prefixes, brief sets hotel": {**visibility(data, pre_hotel, db), "fail_info_only": fail_only}}

    res = {"post_hoc": True, "exploratory": True, "bootstrap": {"draws": DRAWS, "seed": SEED},
           "heldout_rows_read": nrows, "reproduces_stage1": {"ok": ok, "values_checked": n_checked},
           "a1_heldout_hotel_only": h1, "a2_random_deletion": {"heldout": h2, "earlier": e2},
           "a3_word_or_meaning": w3, "a4_visibility": v4,
           "r9_invalid_reads": {f"{m} {f}": n for (m, f), n in sorted(invalid.items())}}
    L = ["# Review round 2: post hoc analyses (exploratory)", "",
         "Every section is post hoc: chosen after the results. No model call. Definitions and choices: the docstring of "
         "r10/analysis/r2_posthoc.py. Bootstrap: 2,000 draws, seed 20261112.", ""]
    L += md_heldout(h1, ok) + md_random(h2, e2) + md_words(w3) + md_visibility(v4)
    OUT.mkdir(exist_ok=True)
    (OUT / "r2_posthoc.json").write_text(json.dumps(clean(res), indent=1))
    (OUT / "r2_posthoc.md").write_text("\n".join(L) + "\n")
    print((OUT / "r2_posthoc.md").read_text())


if __name__ == "__main__":
    main()
