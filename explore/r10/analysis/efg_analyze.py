"""Experiments E, F and G: Opus and Astra as panel models, and more reasoning. Exploratory.

Design and predictions: PROTOCOL.md "## Round 10 runs", sections E, F and G, with amendment R10-4 (the fill runs).
Inputs (raw.jsonl):
- E: ere_opus (Opus, effort low; cells f0 and f1 on S1t, S3 and S2; read 1).
- G: erg_astra (Astra, effort low; the same cells and groups; read 1).
- F, the high setting (r10/models.py *_high; cells f0 and f1 on S1t and S2): erf_sonnet, erf_haiku, erf_sol,
  erf_luna (read 1); erx_f2_haiku and erx_f2_luna (read 2); erx_f0h_opus (f0) and erx_f1h_opus (f1) for Opus.
- F, the baseline setting of the same model (the locked text of F): F0 from the fresh F0 arm of experiment B
  (erb_sonnet, erb_haiku, erb_sol, erb_luna; S1t and S2 only), F1 from the round-9 natural runs
  (natural_analyze.load: E13 for Sonnet and Haiku, X2 for Sol and Luna). For Opus the baseline is ere_opus (effort
  low), F0 and F1. The round-9 F0 rate is shown as a reference column only.
MultiWOZ 2.4 and the groups come from runs.context(); hotel_db.json from gold.hotel_db(). Outputs:
r10/analysis/out/efg.json, efg.md and fig_effort.csv.

Definitions (fixed here before the first run of this script; only the row format of the raw files was looked at):
- A read is valid when its row succeeded, did not stop at the length limit, and parses: natural.parse with
  natural.FORMS["f0"] or ["f1"] (the round-9 form parser; F1 maps `property_kind` and `large_property` back). The
  round-9 baseline reads use the validity rule of natural_analyze.load (a succeeded row that stopped at end_turn and
  parses), and their invalid counts are over all round-9 groups.
- The outcome is natural_analyze.hotel of the parsed `type`: the list holds `hotel`.
- A missing read is a request of the design (dialogue, cell, read number of a fetched folder) with no row.
- Rates are over valid reads, with a 95% cluster bootstrap interval over dialogues (stats.cluster_bootstrap, 2,000
  draws, seed 20261112). A cell with 2% or more invalid or missing reads also shows the worst-case bound.
- S1t subsets (briefsearch.brief_subsets): "no type" (807: the brief sets no type) and "no type, no name" (423).
- Search failure: briefsearch.search_failure of a valid read, as a share of all valid reads on the 807 (the rule of
  a_analyze.py and review/plan14/harm_by_model.py).
- Paired contrasts: per dialogue, the mean of the valid reads of one cell minus the other; a dialogue enters when
  both cells have a valid read; interval of the mean; stats.sign_test over dialogues.
- The trade (E and G only): stats.trade_interval with the paired estimator of b_analyze.py: per dialogue (F0 hits,
  F0 reads, F1 hits, F1 reads) over the dialogues with both cells valid; sizes S1t 994, S3 490, S2 545. The trade rule
  (at least 50% of the F0 wrong values removed, at most 0.30 correct values lost per wrong value removed) is shown.
  F has no S3, so F gives only the rates and the paired contrasts.
- E1 and G1: the F0 rate on S1t is at least 10%, and the paired mean of F0 minus F1 on S1t is at least 5 points.
- F1: for a model, the high-setting F0 rate on S1t falls by less than half of the baseline F0 rate:
  (baseline - high) < 0.5 x baseline. A rise counts as a fall of less than half. Held when at least 3 of the 4 models
  meet it.
- F2: at the high setting, the paired mean of F0 minus F1 on S1t is at least 5 points, for every model.
- Choice 1: "the 4 models" of F1 and F2 are Sonnet, Haiku, Sol and Luna, the models of the locked F design. Opus at
  high effort is a fill run; it is shown and does not count. Reason: the design names the four models.
- Choice 2: E1 and G1 use the paired mean of F0 minus F1 for "F1 lowers it". Reason: it is the within-model
  contrast of the analysis rules; with 1 read and no invalid read it equals the difference of the two rates.
- A prediction that needs a model that is not fetched shows "incomplete" unless the fetched models already decide it.
Usage (from explore/): .venv/bin/python -I r10/analysis/efg_analyze.py
"""
import collections
import csv
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import natural  # noqa: E402
import natural_analyze as na  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
SIZES = {"S1t": 994, "S3": 490, "S2": 545}
GROUP_KEY = {"S1t": "s1t", "S3": "s3", "S2": "s2"}
CELLS = ("f0", "f1")
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
WORST_AT = 0.02
ALL3, F_GROUPS = ("S1t", "S3", "S2"), ("S1t", "S2")
# A source: (folder, cells, read numbers, groups).
PANEL = {"E": ("opus", (("ere_opus", CELLS, (1,), ALL3),)),
         "G": ("astra", (("erg_astra", CELLS, (1,), ALL3),))}
F_MODELS = ("sonnet", "haiku", "sol", "luna")
F_HIGH = {
    "sonnet": (("erf_sonnet", CELLS, (1,), F_GROUPS),),
    "haiku": (("erf_haiku", CELLS, (1,), F_GROUPS), ("erx_f2_haiku", CELLS, (2,), F_GROUPS)),
    "sol": (("erf_sol", CELLS, (1,), F_GROUPS),),
    "luna": (("erf_luna", CELLS, (1,), F_GROUPS), ("erx_f2_luna", CELLS, (2,), F_GROUPS)),
    "opus": (("erx_f0h_opus", ("f0",), (1,), F_GROUPS), ("erx_f1h_opus", ("f1",), (1,), F_GROUPS)),
}
F_BASE_F0 = {  # the fresh F0 arm of experiment B (read numbers as in r10/runs.py)
    "sonnet": (("erb_sonnet", ("f0",), (1,), F_GROUPS),),
    "haiku": (("erb_haiku", ("f0",), (1, 2), F_GROUPS),),
    "sol": (("erb_sol", ("f0",), (1,), F_GROUPS),),
    "luna": (("erb_luna", ("f0",), (1, 2), F_GROUPS),),
    "opus": (("ere_opus", ("f0",), (1,), F_GROUPS),),
}
F_BASE_F1_OPUS = (("ere_opus", ("f1",), (1,), F_GROUPS),)


def rows(folder):
    path = EXPLORE / folder / "raw.jsonl"
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None


def split(cid):
    name, did, cell, read = cid.split("-")
    return did + ".json", cell, int(read)


def read_of(row, cell):
    if row.get("type") != "succeeded":
        return False, "failed"
    if row.get("stop") in CUT:
        return False, "cut"
    try:
        return True, natural.parse(row.get("text", ""), natural.FORMS[cell])
    except (ValueError, KeyError, TypeError):
        return False, "parse"


class Reads:
    """The valid reads per (dialogue, cell), and the invalid and missing counts per (group, cell)."""

    def __init__(self):
        self.got = collections.defaultdict(list)
        self.invalid = collections.defaultdict(collections.Counter)
        self.absent = collections.Counter()
        self.used, self.missing = [], []

    def bad(self, group, cell):
        return sum(self.invalid[(group, cell)].values()) + self.absent[(group, cell)]


def load(sources, ids_by_group, group_of, out=None):
    """Add the reads of `sources` to `out` (a new Reads when None). A folder that is not fetched is listed in
    out.missing and skipped."""
    out = out or Reads()
    for folder, cells, reads, groups in sources:
        rr = rows(folder)
        if rr is None:
            out.missing.append(folder)
            continue
        out.used.append(folder)
        expected = {(d, c, r) for G in groups for d in ids_by_group[G] for c in cells for r in reads}
        seen = set()
        for row in rr:
            d, cell, read = split(row["custom_id"])
            if (d, cell, read) not in expected:
                continue  # another arm of the folder (B) or a group outside this analysis
            seen.add((d, cell, read))
            ok, val = read_of(row, cell)
            if ok:
                out.got[(d, cell)].append(val)
            else:
                out.invalid[(group_of[d], cell)][val] += 1
        for d, c, _ in expected - seen:
            out.absent[(group_of[d], c)] += 1
    return out


def r9_reads(model, r9, ids_by_group):
    """The round-9 F0 and F1 reads of a model on S1t and S2 as a Reads (fields hold `type` only)."""
    out = Reads()
    out.used.append("round-9 natural runs (natural_analyze.load)")
    reads, invalid = r9
    units = {d.removesuffix(".json"): d for G in F_GROUPS for d in ids_by_group[G]}
    for cell in CELLS:
        for u, vals in reads.get((model, cell), {}).items():
            if u in units:
                out.got[(units[u], cell)] += [{"type": v} for v in vals]
        out.invalid[("all round-9 groups", cell)]["invalid (natural_analyze)"] += invalid.get((model, cell), 0)
    return out


def is_hotel(f):
    return na.hotel(f.get("type"))


def interval(per):
    per = [r for r in per if r[1]]
    if not per:
        return None
    return stats.cluster_bootstrap({"all": per}, lambda g: sum(r[0] for r in g["all"]) / sum(r[1] for r in g["all"]))


def mean_interval(diffs):
    if not diffs:
        return None
    return stats.cluster_bootstrap({"all": [(x,) for x in diffs]}, lambda g: sum(r[0] for r in g["all"]) / len(g["all"]))


def rate(R, ids, cell, test=is_hotel, bad=0):
    per = [(sum(test(f) for f in R.got.get((d, cell), [])), len(R.got.get((d, cell), []))) for d in ids]
    k, n = sum(r[0] for r in per), sum(r[1] for r in per)
    out = {"k": k, "n": n, "dialogues": sum(1 for r in per if r[1]), "share": k / n if n else None}
    ci = interval(per)
    if ci:
        out["ci"] = [ci[1], ci[2]]
    if bad and n and bad / (n + bad) >= WORST_AT:
        out["worst_case"] = [k / (n + bad), (k + bad) / (n + bad)]
    return out


def paired(Ra, ca, Rb, cb, ids):
    """b minus a per dialogue: (Rb, cb) - (Ra, ca)."""
    diffs = []
    for d in ids:
        va, vb = Ra.got.get((d, ca)), Rb.got.get((d, cb))
        if va and vb:
            diffs.append(sum(map(is_hotel, vb)) / len(vb) - sum(map(is_hotel, va)) / len(va))
    pos, neg = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    ci = mean_interval(diffs)
    return {"dialogues": len(diffs), "mean": ci[0] if ci else None, "ci": [ci[1], ci[2]] if ci else None,
            "higher": pos, "lower": neg, "sign_p": stats.sign_test(pos, neg)}


def trade(R, ids_by_group):
    cells = {}
    for G in SIZES:
        cells[G] = []
        for d in ids_by_group[G]:
            a, b = R.got.get((d, "f0")), R.got.get((d, "f1"))
            if a and b:
                cells[G].append((sum(map(is_hotel, a)), len(a), sum(map(is_hotel, b)), len(b)))
    if not all(cells.values()):
        return None
    (removed, lost, ratio), lo, hi = stats.trade_interval(cells, SIZES)
    f0_wrong = sum(sum(r[0] for r in cells[G]) / sum(r[1] for r in cells[G]) * SIZES[G] for G in ("S1t", "S3"))
    frac = removed / f0_wrong if f0_wrong > 0 else None
    if removed <= 0:
        ratio, lo, hi = None, None, None
    return {"removed": removed, "lost": lost, "ratio": ratio, "ci": [lo, hi], "f0_wrong": f0_wrong,
            "removed_share": frac,
            "meets_rule": bool(frac is not None and ratio is not None and frac >= 0.5 and 0 <= ratio <= 0.30),
            "dialogues": {G: len(cells[G]) for G in SIZES}}


def views(ids_by_group, sub, groups):
    """The dialogue lists of the tables: each group, and the two S1t subsets."""
    out = {G: list(ids_by_group[G]) for G in groups}
    out["S1t no type (807)"] = list(sub["no_type"])
    out["S1t no type, no name (423)"] = list(sub["no_name"])
    return out


def bad_of(R, view, cell):
    """Invalid and missing reads of a view, for the worst case: the count of a group; for an S1t subset no worst case
    (the counts are kept per group, not per subset)."""
    return R.bad(view, cell) if view in SIZES else 0


def search_fail(R, ids, cell, data, db):
    per = []
    for d in ids:
        vals = R.got.get((d, cell), [])
        per.append((sum(bs.search_failure(f, data[d], db) for f in vals), len(vals)))
    k, n = sum(r[0] for r in per), sum(r[1] for r in per)
    out = {"k": k, "n": n, "share": k / n if n else None}
    ci = interval(per)
    if ci:
        out["ci"] = [ci[1], ci[2]]
    return out


def counts(R):
    return {"folders": R.used, "missing_folders": R.missing,
            "invalid": {f"{g}|{c}": dict(v) for (g, c), v in R.invalid.items() if sum(v.values())},
            "missing_reads": {f"{g}|{c}": v for (g, c), v in R.absent.items() if v}}


def panel(R, ids_by_group, sub, group_of, data, db):
    vs = views(ids_by_group, sub, ALL3)
    res = {"reads": counts(R)}
    res["rates"] = {v: {c: rate(R, ids, c, bad=bad_of(R, v, c)) for c in CELLS} for v, ids in vs.items()}
    res["f1_minus_f0"] = {v: paired(R, "f0", R, "f1", ids) for v, ids in vs.items()}
    res["search_failure"] = {c: search_fail(R, sub["no_type"], c, data, db) for c in CELLS}
    res["trade"] = trade(R, ids_by_group)
    return res


def effort(high, base0, base1, r9base, ids_by_group, sub, group_of, data, db):
    vs = views(ids_by_group, sub, F_GROUPS)
    res = {"reads": {"high": counts(high), "baseline_f0": counts(base0), "baseline_f1": counts(base1)}}
    res["rates"] = {}
    for v, ids in vs.items():
        res["rates"][v] = {
            "high_f0": rate(high, ids, "f0", bad=bad_of(high, v, "f0")),
            "high_f1": rate(high, ids, "f1", bad=bad_of(high, v, "f1")),
            "base_f0": rate(base0, ids, "f0", bad=bad_of(base0, v, "f0")),
            "base_f1": rate(base1, ids, "f1", bad=bad_of(base1, v, "f1")),
        }
        if r9base is not None:
            res["rates"][v]["r9_f0_reference"] = rate(r9base, ids, "f0")
    res["contrasts"] = {v: {"high_f0_minus_base_f0": paired(base0, "f0", high, "f0", ids),
                            "high_f1_minus_base_f1": paired(base1, "f1", high, "f1", ids),
                            "high_f1_minus_high_f0": paired(high, "f0", high, "f1", ids),
                            "base_f1_minus_base_f0": paired(base0, "f0", base1, "f1", ids)} for v, ids in vs.items()}
    res["search_failure"] = {"high_f0": search_fail(high, sub["no_type"], "f0", data, db),
                             "high_f1": search_fail(high, sub["no_type"], "f1", data, db),
                             "base_f0": search_fail(base0, sub["no_type"], "f0", data, db),
                             "base_f1": search_fail(base1, sub["no_type"], "f1", data, db)}
    return res


def at_least(words, ok, k, named):
    met = [m for m in named if ok.get(m)]
    absent = [m for m in named if m not in ok]
    if len(met) >= k:
        status = "held"
    elif len(met) + len(absent) < k:
        status = "failed"
    else:
        status = "undecided; incomplete (not available: " + ", ".join(absent) + ")"
    return {"words": words, "held": status == "held", "status": status, "models_meeting": met, "models_missing": absent}


def every(words, ok, named):
    absent = [m for m in named if m not in ok]
    if not all(ok.values()):
        status = "failed"
    elif absent:
        status = "held so far; incomplete (not available: " + ", ".join(absent) + ")"
    else:
        status = "held"
    return {"words": words, "held": status == "held", "status": status, "models_missing": absent}


def predictions(res):
    p = {}
    for exp, model, key in (("E", "opus", "E1"), ("G", "astra", "G1")):
        r = res["panel"].get(exp)
        name = "Opus" if model == "opus" else "Astra"
        words = f"{name} F0 writes type = hotel on at least 10% of S1t, and F1 lowers it by at least 5 points"
        if not r:
            p[key] = {"words": words, "held": False, "status": "not run or not fetched", "value": None}
            continue
        f0 = r["rates"]["S1t"]["f0"]["share"]
        drop = 0.0 - r["f1_minus_f0"]["S1t"]["mean"] if r["f1_minus_f0"]["S1t"]["mean"] is not None else None
        held = f0 is not None and drop is not None and f0 >= 0.10 and drop >= 0.05
        p[key] = {"words": words, "held": held, "status": "held" if held else "failed",
                  "value": {"f0_rate_S1t": f0, "f0_minus_f1_S1t": drop}}
    f = res["effort"]
    f1v, f1ok, f2v, f2ok = {}, {}, {}, {}
    for m, r in f.items():
        hi, lo = r["rates"]["S1t"]["high_f0"]["share"], r["rates"]["S1t"]["base_f0"]["share"]
        if hi is not None and lo is not None:
            f1v[m] = {"base_f0": lo, "high_f0": hi, "fall": lo - hi, "half_of_base": lo / 2}
            if m in F_MODELS:
                f1ok[m] = (lo - hi) < 0.5 * lo
        gap = r["contrasts"]["S1t"]["high_f1_minus_high_f0"]["mean"]
        if gap is not None and r["rates"]["S1t"]["high_f1"]["n"]:
            f2v[m] = 0.0 - gap
            if m in F_MODELS:
                f2ok[m] = -gap >= 0.05
    p["F1"] = {**at_least("at effort high, the F0 rate on S1t falls by less than half of the low-effort rate for at "
                          "least 3 of the 4 models", f1ok, 3, F_MODELS), "value": f1v,
               "note": "baseline F0: the fresh F0 arm of experiment B; Opus (fill, baseline ere_opus) is shown and "
                       "does not count"}
    p["F2"] = {**every("the F0 minus F1 gap on S1t stays at 5 points or more on every model", f2ok, F_MODELS),
               "value": f2v, "note": "the gap at the high setting; Opus is shown and does not count"}
    return p


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def rate_text(r):
    if not r or not r.get("n"):
        return "-"
    s = f"{pct(r['share'])} ({r['k']}/{r['n']})"
    if r.get("ci"):
        s += f" [{pct(r['ci'][0])}, {pct(r['ci'][1])}]"
    if r.get("worst_case"):
        s += f"; worst case [{pct(r['worst_case'][0])}, {pct(r['worst_case'][1])}]"
    return s


def contrast_row(label, c):
    if c["mean"] is None:
        return f"| {label} | 0 | - | - | - | - | - |"
    return (f"| {label} | {c['dialogues']} | {100 * c['mean']:+.1f} | [{100 * c['ci'][0]:+.1f}, {100 * c['ci'][1]:+.1f}] | "
            f"{c['higher']} | {c['lower']} | {c['sign_p']:.2g} |")


def reads_text(c):
    inv = "; ".join(f"{k}: {sum(v.values())}" for k, v in c["invalid"].items()) or "0"
    mis = "; ".join(f"{k}: {v}" for k, v in c["missing_reads"].items()) or "0"
    return f"{', '.join(c['folders']) or '-'} | {', '.join(c['missing_folders']) or '-'} | {inv} | {mis}"


def rounded(x):
    if isinstance(x, float):
        return round(x, 4)
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rounded(v) for v in x]
    return x


def markdown(res, preds, missing, sizes):
    L = ["## 6. Stronger models and more reasoning (experiments E, F, G)", "",
         "Exploratory. Groups: S1t (994: the traveller says \"hotel\" and the gold sets no type), S3 (490: gold "
         f"guesthouse), S2 (545: gold hotel). S1t subsets: the brief sets no type ({sizes['no_type']}); of those, the "
         f"brief names no venue ({sizes['no_name']}). Outcome: `type` holds `hotel`.", ""]
    if missing:
        L += [f"Not fetched at this run: {', '.join(sorted(set(missing)))}.", ""]
    L += ["### Reads", "", "| Experiment, model, reads | Folders | Not fetched | Invalid (group or source and cell) | "
          "Missing reads |", "|---|---|---|---|---|"]
    for exp, r in res["panel"].items():
        L.append(f"| {exp}, {PANEL[exp][0]} | {reads_text(r['reads'])} |")
    for m, r in res["effort"].items():
        for key, c in r["reads"].items():
            L.append(f"| F, {m}, {key} | {reads_text(c)} |")
    for exp, r in res["panel"].items():
        model = PANEL[exp][0]
        L += ["", f"### {exp}: {model} as a panel model (effort low). Exploratory.", "",
              "| Dialogues | F0 | F1 | F1 - F0, points [95% interval] (higher, lower, sign p) |", "|---|---|---|---|"]
        for v, cr in r["rates"].items():
            c = r["f1_minus_f0"][v]
            ct = "-" if c["mean"] is None else (f"{100 * c['mean']:+.1f} [{100 * c['ci'][0]:+.1f}, {100 * c['ci'][1]:+.1f}] "
                                                f"({c['higher']}, {c['lower']}, p {c['sign_p']:.2g})")
            L.append(f"| {v} | {rate_text(cr['f0'])} | {rate_text(cr['f1'])} | {ct} |")
        sf = r["search_failure"]
        L += ["", f"Search failure on the {sizes['no_type']} no-type dialogues of S1t (share of all valid reads): "
              f"F0 {rate_text(sf['f0'])}; F1 {rate_text(sf['f1'])}.", ""]
        t = r["trade"]
        if t:
            if t["ratio"] is None:
                ratio = "- (F1 adds wrong values)"
            else:
                hi = "no upper limit" if t["ci"][1] == float("inf") else f"{t['ci'][1]:.2f}"
                ratio = f"{t['ratio']:.2f} [{t['ci'][0]:.2f}, {hi}]"
            L.append(f"Trade of F1 against F0 (paired estimator; dialogues {t['dialogues']}): wrong removed "
                     f"{t['removed']:.1f} of {t['f0_wrong']:.1f} ({pct(t['removed_share'])}); correct lost {t['lost']:.1f}; "
                     f"ratio {ratio}; meets the trade rule: {'yes' if t['meets_rule'] else 'no'}.")
        else:
            L.append("Trade: not computed (a group has no paired dialogue).")
    L += ["", "### F: more reasoning (high setting) against the baseline setting of the same model. Exploratory.", "",
          "Baseline F0: the fresh F0 arm of experiment B (for Opus: ere_opus, effort low). Baseline F1: the round-9 "
          "natural runs (for Opus: ere_opus). Round-9 Sol S2 reads cover 229 of the 545 dialogues. The round-9 F0 "
          "column is a reference only.", "",
          "| Model | Dialogues | Baseline F0 | High F0 | Baseline F1 | High F1 | Round-9 F0 (reference) |",
          "|---|---|---|---|---|---|---|"]
    for m, r in res["effort"].items():
        for v, cr in r["rates"].items():
            L.append(f"| {m}{' (fill)' if m not in F_MODELS else ''} | {v} | {rate_text(cr['base_f0'])} | "
                     f"{rate_text(cr['high_f0'])} | {rate_text(cr['base_f1'])} | {rate_text(cr['high_f1'])} | "
                     f"{rate_text(cr.get('r9_f0_reference'))} |")
    L += ["", "Paired contrasts (per-dialogue means; sign test over dialogues):", "",
          "| Model, dialogues, contrast | Dialogues | Mean, points | 95% interval | Higher | Lower | Sign p |",
          "|---|---|---|---|---|---|---|"]
    for m, r in res["effort"].items():
        for v, cs in r["contrasts"].items():
            for key, c in cs.items():
                L.append(contrast_row(f"{m}, {v}, {key}", c))
    L += ["", "Search failure on the no-type dialogues of S1t (share of all valid reads):", "",
          "| Model | Baseline F0 | High F0 | Baseline F1 | High F1 |", "|---|---|---|---|---|"]
    for m, r in res["effort"].items():
        s = r["search_failure"]
        L.append(f"| {m} | {rate_text(s['base_f0'])} | {rate_text(s['high_f0'])} | {rate_text(s['base_f1'])} | "
                 f"{rate_text(s['high_f1'])} |")
    L += ["", "### Predictions (point values)", "", "| # | Words | Value | Held |", "|---|---|---|---|"]
    for k, v in preds.items():
        L.append(f"| {k} | {v['words']} | {json.dumps(rounded(v['value']))} | {v['status']} |")
    return "\n".join(L) + "\n"


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    ids_by_group = {G: list(g[GROUP_KEY[G]]) for G in SIZES}
    group_of = {d: G for G, ids in ids_by_group.items() for d in ids}
    sub = bs.brief_subsets(data, ids_by_group["S1t"], db)
    res, missing = {"panel": {}, "effort": {}}, []
    for exp, (model, sources) in PANEL.items():
        R = load(sources, ids_by_group, group_of)
        missing += R.missing
        if R.used:
            res["panel"][exp] = panel(R, ids_by_group, sub, group_of, data, db)
    r9 = na.load()
    for m, sources in F_HIGH.items():
        high = load(sources, ids_by_group, group_of)
        missing += high.missing
        if not high.used:
            continue
        base0 = load(F_BASE_F0[m], ids_by_group, group_of)
        missing += base0.missing
        if m == "opus":
            base1, r9base = load(F_BASE_F1_OPUS, ids_by_group, group_of), None
        else:
            base1 = r9base = r9_reads(m, r9, ids_by_group)
        res["effort"][m] = effort(high, base0, base1, r9base, ids_by_group, sub, group_of, data, db)
    preds = predictions(res)
    OUT.mkdir(exist_ok=True)
    sizes = {k: len(v) for k, v in sub.items()}
    (OUT / "efg.json").write_text(json.dumps({"exploratory": True, "missing": sorted(set(missing)), "subsets": sizes,
                                              "results": res, "predictions": preds}, indent=1, default=float))
    (OUT / "efg.md").write_text(markdown(res, preds, missing, sizes))
    with open(OUT / "fig_effort.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "setting", "form", "dialogues", "k", "n", "share", "ci_low", "ci_high"])
        for m, r in res["effort"].items():
            for v, cr in r["rates"].items():
                for key, c in cr.items():
                    if key == "r9_f0_reference" or not c.get("n"):
                        continue
                    setting, form = key.split("_")
                    w.writerow([m, setting, form, v, c["k"], c["n"], c["share"], *(c.get("ci") or [None, None])])
    print(f"missing folders: {sorted(set(missing))}")
    print((OUT / "efg.md").read_text())


if __name__ == "__main__":
    main()
