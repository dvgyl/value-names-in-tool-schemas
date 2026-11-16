"""Post hoc: the rename effect split by whether the traveller's own words state the type (clear_rule.py).

Question. The "guess" reading says that the renamed value name acts mainly when the dialogue leaves the type open.
Test: report the effect of the rename on correct values separately for clear requests (the traveller's words require
a hotel or exclude guesthouses: clear_rule label "hotel_only") and unclear requests (label "unclear"). For
completeness, the same split on unsupported values (dialogues whose brief sets no type).

Sources (no model call; every answer below was fetched and opened before this script):
1. Tool calls at the first request: r10/analysis/a_analyze.py load(), arms t0 (legacy tool) and t1 (renamed tool).
   Prefix sets a_hotel (59, brief sets hotel) and a_no_type (448). Measure: a_analyze.is_hotel. A cell is the mean
   over the valid reads of the dialogue (all reads of era1 and the fill runs).
2. Round-9 form runs on full dialogues: r9/natural/natural_analyze.py load(), F1 and F6 against F0. Sets b_hotel (233
   S2 dialogues whose brief sets hotel, gold.brief_type) and b_no_type (807 S1t dialogues whose brief sets no type).
   Measure: natural_analyze.hotel. A cell is the mean over the valid reads.
3. The held-out test, stage 1 (opened and analysed once before): main/exp0/open/em1_<model>/raw.jsonl read through
   main/exp0/analysis.load (its checks and parsers; its main is not run and it writes nothing). t_renamed against
   t_legacy, read 1, the frozen measure analysis.hotel. Sets c_hotel (77, part hot) and c_no_type (213, part nat).
   "panel" is the per-dialogue mean over the panel models with both cells valid (analysis.panel_values).

Statistics. Per dialogue: d = renamed cell minus legacy cell. Per group: the mean of d with a 95% cluster bootstrap
interval over dialogues (stats.cluster_bootstrap, 2,000 draws, seed 20261112), the exact sign test over dialogues
(stats.sign_test), and the relative change (mean renamed - mean legacy) / mean legacy with its interval. The
difference "clear minus unclear" resamples dialogues inside each group (the same function, two groups). A pooled row
of sources 1 and 2 averages the per-model d of each dialogue, with equal model weight, as the panel row of source 3.
Intervals are not shown for a group of fewer than MIN_N dialogues. No correction for multiple comparisons: every value
is post hoc and descriptive. The rule is clear_rule.py; this script stops when its SHA-256 differs from
out/clear_rule.md, which was written before any split was computed. The pre-declared secondary rule `strict` (families
E and R) gets the same tables. One breakdown was added after the first run and is marked so in the report: the
dialogues that are clear by the main rule but unclear by the strict rule (p_t_only).
Outputs: out/clear_split.md and out/clear_split.json.
Usage (from explore/): .venv/bin/python -I r10/analysis/clear_split.py
"""
import collections
import datetime
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parents[1]
sys.path.insert(0, str(HERE))
import clear_rule as cr  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
OPEN = EXPLORE / "main" / "exp0" / "open"
DRAWS, SEED, MIN_N = 2000, 20261112, 5
CLEAR, UNCLEAR = "hotel_only", "unclear"
SOURCES = {
    "1": {"title": "Tool calls at the first request (experiment A, prefixes)", "base": "t0", "forms": ("t1",),
          "correct": "a_hotel", "unsupported": "a_no_type"},
    "2": {"title": "Round-9 form runs on full dialogues", "base": "f0", "forms": ("f1", "f6"),
          "correct": "b_hotel", "unsupported": "b_no_type"},
    "3": {"title": "Held-out test, stage 1 (post hoc look at opened answers)", "base": "t_legacy",
          "forms": ("t_renamed",), "correct": "c_hotel", "unsupported": "c_no_type"},
}


# ------------------------------------------------------------------------------------------------------ the guard
def check_rule():
    """Stop when clear_rule.py is not the file that out/clear_rule.md recorded before any split."""
    doc = cr.DOC.read_text()
    m = re.search(r"SHA-256 of `r10/analysis/clear_rule\.py`: `([0-9a-f]{64})`", doc)
    if not m or m.group(1) != cr.file_sha256():
        sys.exit("Stopped: clear_rule.py differs from the version that out/clear_rule.md records.")
    return m.group(1)


# ------------------------------------------------------------------------------------------------- the statistics
def mean(xs):
    return sum(xs) / len(xs) if xs else None


def diff_mean(rows):
    return mean([b - a for a, b in rows])


def relative(rows):
    base = sum(a for a, _ in rows)
    return (sum(b for _, b in rows) - base) / base if base else None


def boot(groups, stat):
    """stats.cluster_bootstrap with the fixed draws and seed; None when a group is smaller than MIN_N or a draw has no
    defined value."""
    if any(len(r) < MIN_N for r in groups.values()):
        return None
    try:
        _, lo, hi = stats.cluster_bootstrap(groups, stat, DRAWS, SEED)
    except (TypeError, ZeroDivisionError):
        return None
    return [lo, hi]


def summary(rows):
    """rows: one (legacy cell, renamed cell) per dialogue."""
    if not rows:
        return {"dialogues": 0}
    d = [b - a for a, b in rows]
    hi, lo = sum(x > 0 for x in d), sum(x < 0 for x in d)
    rel = relative(rows)
    return {"dialogues": len(rows), "legacy": mean([a for a, _ in rows]), "renamed": mean([b for _, b in rows]),
            "effect": mean(d), "effect_ci": boot({"all": rows}, lambda g: diff_mean(g["all"])),
            "renamed_higher": hi, "renamed_lower": lo, "sign_p": stats.sign_test(hi, lo),
            "relative": rel, "relative_ci": boot({"all": rows}, lambda g: relative(g["all"])) if rel is not None
            else None}


def difference(clear, unclear):
    """Clear minus unclear: the effect (points) and the relative change, each with its interval. None when a group has
    fewer than MIN_N dialogues (a point value from 1 to 4 dialogues would mislead)."""
    if len(clear) < MIN_N or len(unclear) < MIN_N:
        return None
    g = {"clear": clear, "unclear": unclear}
    rel = (lambda x: None if relative(x["clear"]) is None or relative(x["unclear"]) is None
           else relative(x["clear"]) - relative(x["unclear"]))
    point_rel = rel(g)
    return {"effect": diff_mean(clear) - diff_mean(unclear),
            "effect_ci": boot(g, lambda x: diff_mean(x["clear"]) - diff_mean(x["unclear"])),
            "relative": point_rel, "relative_ci": boot(g, rel) if point_rel is not None else None}


def split_block(cells, labels):
    """cells: {dialogue: (legacy, renamed)}; labels: {dialogue: label}. Summaries per label and the difference."""
    by = collections.defaultdict(list)
    for d, pair in cells.items():
        by[labels[d]].append(pair)
    out = {"all": summary(list(cells.values()))}
    for lab in cr.LABELS:
        if by[lab]:
            out[lab] = summary(by[lab])
    out["clear_minus_unclear"] = difference(by[CLEAR], by[UNCLEAR])
    return out


def p_t_only(main_label, strict_label):
    """Derived after the first run of this script (not pre-declared): clear by the main rule, unclear by the strict
    rule. These dialogues state the type only by a P or T pattern ("it should be a hotel", "a hotel type")."""
    return main_label == CLEAR and strict_label == UNCLEAR


def pooled(per_model):
    """{model: {dialogue: (a, b)}} -> {dialogue: (mean a, mean b)} over the models with both cells (equal weight)."""
    acc = collections.defaultdict(list)
    for cells in per_model.values():
        for d, pair in cells.items():
            acc[d].append(pair)
    return {d: (mean([a for a, _ in v]), mean([b for _, b in v])) for d, v in acc.items()}


# ------------------------------------------------------------------------------------------------------ the sources
def source1(sets):
    import a_analyze as aa
    out, used = {}, {}
    for m in aa.MODELS:
        reads, folders = aa.load(m)
        if reads is None:
            continue
        used[m] = folders
        for side in ("correct", "unsupported"):
            cells = {}
            for d, _ in sets[SOURCES["1"][side]]:
                va = [aa.is_hotel(k, f) for _, k, f, _ in reads.get((d, "t0"), []) if k != "invalid"]
                vb = [aa.is_hotel(k, f) for _, k, f, _ in reads.get((d, "t1"), []) if k != "invalid"]
                if va and vb:
                    cells[d] = (mean(va), mean(vb))
            out.setdefault(side, {}).setdefault("t1", {})[m] = cells
    return out, used


def source2(sets):
    sys.path.insert(0, str(EXPLORE / "r9" / "natural"))
    import natural_analyze as na
    reads, _ = na.load()
    models = sorted({m for m, _ in reads})
    out = {}
    for side in ("correct", "unsupported"):
        units = [d for d, _ in sets[SOURCES["2"][side]]]
        for form in SOURCES["2"]["forms"]:
            for m in models:
                base, other = reads.get((m, "f0"), {}), reads.get((m, form), {})
                cells = {}
                for d in units:
                    va = [na.hotel(v) for v in base.get(d.removesuffix(".json"), [])]
                    vb = [na.hotel(v) for v in other.get(d.removesuffix(".json"), [])]
                    if va and vb:
                        cells[d] = (mean(va), mean(vb))
                if cells:
                    out.setdefault(side, {}).setdefault(form, {})[m] = cells
    return out


def source3(sets, data):
    sys.path.insert(0, str(EXPLORE / "main" / "exp0"))
    import analysis
    assert pathlib.Path(analysis.__file__).resolve() == (EXPLORE / "main" / "exp0" / "analysis.py").resolve()
    cells, _, units, _, nrows, _ = analysis.load(OPEN, analysis.PANEL, data=data)
    contrast = {"correct": analysis.FAMILY[1], "unsupported": analysis.FAMILY[0]}
    out, check = {}, {}
    for side, c in contrast.items():
        ids = [d.removesuffix(".json") for d, _ in sets[SOURCES["3"][side]]]
        assert sorted(ids) == sorted(units[c.sample]), f"{side}: the set is not the stage-1 {c.sample} sample"
        for m in analysis.PANEL:
            pairs = {}
            for d in ids:
                a = analysis.value(cells, m, c.base, d)
                b = analysis.value(cells, m, c.form, d)
                if a is not None and b is not None:
                    pairs[d + ".json"] = (a, b)
            out.setdefault(side, {}).setdefault("t_renamed", {})[m] = pairs
        check[c.name] = mean(analysis.panel_values(cells, c, ids, analysis.PANEL))
    return out, check, nrows


# --------------------------------------------------------------------------------------------------------- the run
def run():
    sha = check_rule()
    data, sets = cr.sets()
    labels = {k: {d: cr.label(data[d], end) for d, end in v} for k, v in sets.items()}
    strict = {k: {d: cr.label_strict(data[d], end) for d, end in v} for k, v in sets.items()}
    s1, used1 = source1(sets)
    s2 = source2(sets)
    s3, check3, nrows3 = source3(sets, data)
    raw = {"1": s1, "2": s2, "3": s3}
    res = {}
    for src, spec in SOURCES.items():
        for side in ("correct", "unsupported"):
            set_name = spec[side]
            for form, per_model in raw[src].get(side, {}).items():
                rows = {**per_model, ("panel" if src == "3" else "pooled"): pooled(per_model)}
                block = {}
                for m, cells in rows.items():
                    block[m] = {"main": split_block(cells, labels[set_name]),
                                "strict": split_block(cells, strict[set_name]),
                                "derived_p_t_only": summary([p for d, p in cells.items() if p_t_only(
                                    labels[set_name][d], strict[set_name][d])])}
                res.setdefault(src, {}).setdefault(side, {})[form] = block
    counts = {k: {"main": dict(collections.Counter(v.values())), "strict": dict(collections.Counter(strict[k].values())),
                  "dialogues": len(v)} for k, v in labels.items()}
    clear_ids = {k: sorted(d.removesuffix(".json") for d, lab in v.items() if lab == CLEAR) for k, v in labels.items()}
    checks = {"source3_panel_mean_all_dialogues": check3,
              "source3_stage1_report": {"wrong_values": -0.130, "correct_values_kept": -0.291}}
    meta = {"post_hoc": True, "rule_sha256": sha, "time": datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds"), "bootstrap": {"draws": DRAWS, "seed": SEED}, "min_n_for_interval": MIN_N,
        "clear": CLEAR, "unclear": UNCLEAR, "source1_folders": used1, "source3_rows": nrows3,
        "sets": cr.SET_TEXT}
    return {"meta": meta, "counts": counts, "clear_ids": clear_ids, "checks": checks, "results": res}


# ------------------------------------------------------------------------------------------------------ the report
def clean(x):
    if isinstance(x, float):
        return None if math.isnan(x) or math.isinf(x) else round(x, 6)
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
    return "-" if not ci else f"[{100 * ci[0]:+.1f}, {100 * ci[1]:+.1f}]"


def pval(p):
    return "-" if p is None else (f"{p:.3f}" if p >= 0.001 else f"{p:.1e}")


def effect_cell(s):
    if not s or not s.get("dialogues"):
        return "-"
    return f"{pts(s['effect'])} {ci_pts(s['effect_ci'])}"


def group_rows(model, block):
    out = []
    for lab, name in ((CLEAR, "clear"), (UNCLEAR, "unclear"), ("all", "all")):
        s = block.get(lab)
        if not s or not s.get("dialogues"):
            out.append(f"| {model} | {name} | 0 | - | - | - | - | - | - |")
            continue
        out.append(f"| {model} | {name} | {s['dialogues']} | {pct(s['legacy'])} | {pct(s['renamed'])} | "
                   f"{effect_cell(s)} | {s['renamed_higher']} / {s['renamed_lower']} | {pval(s['sign_p'])} | "
                   f"{pts(s['relative'])}% {ci_pts(s['relative_ci'])} |")
    dif = block.get("clear_minus_unclear")
    if dif:
        out.append(f"| {model} | **clear minus unclear** | | | | {pts(dif['effect'])} {ci_pts(dif['effect_ci'])} | | | "
                   f"{pts(dif['relative'])}% {ci_pts(dif['relative_ci'])} |")
    return out


HEAD = ["| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | "
        "Sign p | Relative change [95% CI] |", "|---|---|---|---|---|---|---|---|---|"]


def render(r):
    meta, counts, res = r["meta"], r["counts"], r["results"]
    L = ["# Rename effect, split by clear and unclear requests (post hoc)", "",
         "Status: post hoc and descriptive. No model call. The split rule is `clear_rule.py` (SHA-256 "
         f"`{meta['rule_sha256']}`). It was fixed in `out/clear_rule.md` before any split was computed. This script "
         "stops when the rule file differs.", "",
         "- **Clear**: a traveller sentence requires a hotel or excludes the guesthouse kinds (label `hotel_only`).",
         "- **Unclear**: no traveller sentence states a type (label `unclear`). Labels `guesthouse_only` and `mixed` "
         "are in the counts and in the JSON file only.",
         "- **Effect**: per dialogue, the renamed cell minus the legacy cell (share of reads with `type = hotel`), "
         "then the mean over dialogues. A negative effect on the correct side means fewer correct `hotel` values "
         "under the renamed schema.",
         "- **Relative change**: (mean renamed minus mean legacy) / mean legacy. It removes the effect of a "
         "different starting share.",
         f"- **Intervals**: 95% cluster bootstrap over dialogues, {meta['bootstrap']['draws']:,} draws, seed "
         f"{meta['bootstrap']['seed']} (`stats.cluster_bootstrap`). The clear-minus-unclear interval resamples inside "
         f"each group. No interval for a group of fewer than {meta['min_n_for_interval']} dialogues.",
         "- **Sign test**: exact, over dialogues (`stats.sign_test`). Higher / lower: dialogues whose renamed cell "
         "is higher / lower than the legacy cell.",
         "- **pooled** (sources 1 and 2) and **panel** (source 3): per dialogue, the mean of the per-model effects "
         "over the models with both cells, equal weight for each model.",
         "- No correction for multiple comparisons.", "",
         "## Counts of clear and unclear", "",
         "| Set | Dialogues | Clear (hotel_only) | Unclear | guesthouse_only | mixed | Strict rule: clear | "
         "Strict rule: unclear |", "|---|---|---|---|---|---|---|---|"]
    for k, c in counts.items():
        m, s = c["main"], c["strict"]
        L.append(f"| {k} | {c['dialogues']} | {m.get(CLEAR, 0)} | {m.get(UNCLEAR, 0)} | {m.get('guesthouse_only', 0)} "
                 f"| {m.get('mixed', 0)} | {s.get(CLEAR, 0)} | {s.get(UNCLEAR, 0)} |")
    L += [""] + [f"- `{k}`: {t}." for k, t in meta["sets"].items()]

    L += ["", "## Summary: correct side, pooled or panel row", "",
          "| Source | Contrast | Clear: dialogues, effect [95% CI] | Unclear: dialogues, effect [95% CI] | "
          "Clear minus unclear [95% CI] | Relative change, clear / unclear |", "|---|---|---|---|---|---|"]
    for src, spec in SOURCES.items():
        for form, block in res.get(src, {}).get("correct", {}).items():
            row = block["panel" if src == "3" else "pooled"]["main"]
            c, u, dif = row.get(CLEAR, {}), row.get(UNCLEAR, {}), row.get("clear_minus_unclear")
            L.append(f"| {src} | {form} vs {spec['base']} | {c.get('dialogues', 0)}, {effect_cell(c)} | "
                     f"{u.get('dialogues', 0)}, {effect_cell(u)} | "
                     f"{(pts(dif['effect']) + ' ' + ci_pts(dif['effect_ci'])) if dif else '-'} | "
                     f"{pts(c.get('relative'))}% / {pts(u.get('relative'))}% |")

    for src, spec in SOURCES.items():
        L += ["", f"## Source {src}: {spec['title']}", ""]
        if src == "1":
            L += ["Folders read: " + "; ".join(f"{m}: {', '.join(f)}" for m, f in meta["source1_folders"].items())
                  + ".", ""]
        if src == "3":
            L += ["Post hoc look at the opened stage-1 answers (read 1), through `main/exp0/analysis.load`. Rows per "
                  "model: " + ", ".join(f"{m} {n}" for m, n in meta["source3_rows"].items()) + ".", ""]
        for side in ("correct", "unsupported"):
            set_name = spec[side]
            for form, block in res.get(src, {}).get(side, {}).items():
                what = "correct values" if side == "correct" else "unsupported values (for completeness)"
                L += [f"### {form} against {spec['base']}, {what}: set `{set_name}`", ""] + HEAD
                for m, b in block.items():
                    L += group_rows(m, b["main"])
                L += [""]
    L += ["## Secondary: the strict rule (families E and R only)", "",
          "Correct side. Same statistics; the clear group has fewer dialogues.", "",
          "| Source | Contrast | Model | Clear: dialogues, effect [95% CI] | Unclear: dialogues, effect [95% CI] | "
          "Clear minus unclear [95% CI] |", "|---|---|---|---|---|---|"]
    for src, spec in SOURCES.items():
        for form, block in res.get(src, {}).get("correct", {}).items():
            for m, b in block.items():
                row = b["strict"]
                c, u, dif = row.get(CLEAR, {}), row.get(UNCLEAR, {}), row.get("clear_minus_unclear")
                L.append(f"| {src} | {form} vs {spec['base']} | {m} | {c.get('dialogues', 0)}, {effect_cell(c)} | "
                         f"{u.get('dialogues', 0)}, {effect_cell(u)} | "
                         f"{(pts(dif['effect']) + ' ' + ci_pts(dif['effect_ci'])) if dif else '-'} |")
    ch = r["checks"]
    L += ["", "## Derived after the first run: clear only by a P or T pattern (not pre-declared)", "",
          "These dialogues are clear by the main rule and unclear by the strict rule. They state the type only with a "
          "predicate or type word (\"it should be a hotel\", \"a hotel type\") and exclude nothing. This breakdown "
          "was added after the first run of this script showed a gap between the main and strict clear groups. It "
          "is a difference of the two fixed rules, not a new rule.", "",
          "| Source | Contrast | Model | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | "
          "Sign p |", "|---|---|---|---|---|---|---|---|"]
    for src, spec in SOURCES.items():
        for form, block in res.get(src, {}).get("correct", {}).items():
            for m, b in block.items():
                s = b["derived_p_t_only"]
                if not s.get("dialogues"):
                    continue
                L.append(f"| {src} | {form} vs {spec['base']} | {m} | {s['dialogues']} | {pct(s['legacy'])} | "
                         f"{pct(s['renamed'])} | {effect_cell(s)} | {pval(s['sign_p'])} |")
    L += ["", "## Checks", "",
          "Source 3, all dialogues, panel mean of `t_renamed` minus `t_legacy` (read 1): "
          + ", ".join(f"{k} {pts(v)} points" for k, v in ch["source3_panel_mean_all_dialogues"].items())
          + ". RESULT-STAGE1.md reports wrong_values -13.0 and correct_values_kept -29.1.", ""]
    return "\n".join(L) + "\n"


def main():
    r = run()
    OUT.mkdir(exist_ok=True)
    (OUT / "clear_split.json").write_text(json.dumps(clean(r), indent=1))
    (OUT / "clear_split.md").write_text(render(r))
    print((OUT / "clear_split.md").read_text())


if __name__ == "__main__":
    main()
