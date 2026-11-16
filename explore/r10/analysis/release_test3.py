"""Analysis of amendment R10-24 (prototypes/explore/PROTOCOL.md): the replication of the two paraphrase flags of the
release test, each with a fresh control in the same batch or run. Exploratory, fixed in the protocol before the run.

Runs: erk3_deepseek (form answers; cells p0 = the control, ppar = update (b) of R10-20) and erk3_luna (tool calls;
cells t0 = the control, tpar2 = update (e) of R10-22). The 554 first requests of experiment A: open set 448 (1 answer
per arm), specific set 59 (10 answers per arm), guesthouse set 47 (1 answer per arm; description only).

Definitions (fixed in R10-24 before any call; the code of analyze.py, the R10-20 analysis):
- A read is invalid (missing) when its row did not succeed, stopped at the output cap, or harmless3.parse_row gives
  "invalid". A valid read scores 1 when its search holds hotel in type; a valid read without a search call scores 0.
- Per request: the update minus the control, over the requests with a valid read of both. Up and down counts.
- The level of the flagged decision: DeepSeek 99.17% (R10-20, form channel, C = 6), Luna 98.75% (R10-22, tool channel,
  C = 4). Percentile cluster bootstrap over requests (2,000 draws, seed 20261112). L = 5 points. One look.
- First rule: decide and release of R10-6. Revised rule: Appendix I with the exact sign condition.
- Categories of each replication (both rules): "noise" when the decision is hold or pass and the specific-set interval
  covers 0; "real" when the decision is flag and the specific-set change is flag-worthy with the sign of the original
  change; "unresolved" otherwise.
- The original flag against the measured change (the replication): "wrong flag" when the replication's specific-set
  change is absent (the whole interval inside -5 to +5 points); "confirmed flag" when it is flag-worthy with the same
  sign; "not settled" otherwise.
- Descriptions: the original change of the flagged run (the same code on its stored answers), the pooled change of the
  original and the replication (all reads of both runs together), the 95% intervals, rates and read kinds.

Usage (from explore/):
    python3 -I r10/analysis/release_test3.py            # the fetched raw.jsonl files
    python3 -I r10/analysis/release_test3.py --selftest # fake answers
Outputs: r10/analysis/out/release_test3.json and release_test3.md.
This file is a copy of the project analysis (workshops/release-test/analyze3.py) with the paths of the study folder; the results are the same.
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
import release_test as a20  # noqa: E402  (the R10-20 analysis: the rules and set_change; its main does not run)
import harmless3 as h3  # noqa: E402
import release_analyze as ra  # noqa: E402

OUT = HERE / "out"
CUT = a20.CUT
SUFFIX = "_orig"  # the cells of the original flagged run


def read_of(row, cell):
    if row.get("type", "succeeded") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in CUT:
        return "invalid", "cut"
    kind, val = h3.parse_row(row, cell)
    if kind not in ("search", "none"):
        return "invalid", val if kind == "invalid" else f"kind {kind}"
    return kind, val


def load(folder, pilot, cells, suffix=""):
    assert not folder.startswith("em"), f"refused: {folder}"
    path = EXPLORE / folder / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    if not path.exists():
        return None
    reads = collections.defaultdict(list)
    for line in path.read_text().splitlines():
        r = json.loads(line)
        _, d, cell, _ = r["custom_id"].split("-")
        if cell in cells:
            reads[(d + ".json", cell + suffix)].append(read_of(r, cell))
    return reads


def category(dec, spec, orig_sign):
    """The R10-24 category of one replication decision."""
    if spec["interval"] is None:
        return "n/a"
    lo, hi = spec["interval"]
    if dec["release"] in ("hold", "pass") and lo <= 0 <= hi:
        return "noise"
    same = orig_sign != 0 and spec["change"] is not None and (spec["change"] > 0) == (orig_sign > 0)
    # The first rule calls a flag set "flag-worthy"; the revised rule calls it "meets flag rule" (label fix,
    # 2026-11-15, after the independent check VERIFIED-RELEASE3.md; no result changed).
    if dec["release"] == "flag" and dec["sets"]["specific"] in FLAG_LABELS and same:
        return "real"
    return "unresolved"


FLAG_LABELS = ("flag-worthy", "meets flag rule")


def measured(dec, spec, orig_sign, orig_release=None):
    """The original flag against the measured change of the replication (R10-24): "wrong flag" when the
    replication's specific-set interval at the flagged level is inside -L to +L; "confirmed flag" when the
    replication's specific set is a flag set with the same sign; "not settled" otherwise; "no flag to judge" when
    the original decision under the same rule was not a flag. Label fix (2026-11-15, after the independent check
    VERIFIED-RELEASE3.md): the test reads the interval, not the set label, because the revised rule labels an
    absent change "within limits"."""
    if spec["interval"] is None:
        return "n/a"
    if orig_release is not None and orig_release != "flag":
        return "no flag to judge"
    same = spec["change"] is not None and orig_sign != 0 and (spec["change"] > 0) == (orig_sign > 0)
    lo, hi = spec["interval"]
    if -a20.L <= lo and hi <= a20.L:
        return "wrong flag"
    if dec["sets"]["specific"] in FLAG_LABELS and same:
        return "confirmed flag"
    return "not settled"


def analyse(run, reads, orig_reads, sets):
    control, (u, upd) = h3.CONTROL_OF[run], h3.UPDATE_OF[run]
    level = h3.LEVEL[run]
    rep = a20.analyse_update(reads, sets, control, upd, level)
    out = {"model": h3.MODEL_OF[run], "update": u, "cells": [control, upd], "level": level, "replication": rep,
           "at_95": {s: a20.set_change(reads, sets[s], control, upd, 0.95)[0] for s in ("open", "specific")},
           "kinds": {c: a20.kinds(reads, c) for c in (control, upd)}}
    orig = None
    if orig_reads is not None:
        orig = a20.analyse_update(orig_reads, sets, control + SUFFIX, upd + SUFFIX, level)
        pooled_reads = collections.defaultdict(list)
        for (d, c), v in reads.items():
            pooled_reads[(d, c)].extend(v)
        for (d, c), v in orig_reads.items():
            pooled_reads[(d, c.removesuffix(SUFFIX))].extend(v)
        out["pooled"] = {s: a20.set_change(pooled_reads, sets[s], control, upd, level)[0] for s in ("open", "specific")}
    out["original"] = orig
    sign = 0 if orig is None or orig["sets"]["specific"]["change"] is None else (
        1 if orig["sets"]["specific"]["change"] > 0 else -1 if orig["sets"]["specific"]["change"] < 0 else 0)
    out["original_sign"] = sign
    for rule in ("first", "revised"):
        out[f"category_{rule}"] = category(rep[rule], rep["sets"]["specific"], sign)
        out[f"measured_{rule}"] = measured(rep[rule], rep["sets"]["specific"], sign,
                                           None if orig is None else orig[rule]["release"])
    return out


def predictions(res):
    """P1 (DeepSeek) and P2 (Luna): the flag was run-to-run noise ("noise" under both rules)."""
    out = {}
    for k, run in (("P1", "erk3_deepseek"), ("P2", "erk3_luna")):
        r = res.get(run)
        if r is None:
            out[k] = {"result": "n/a"}
            continue
        cats = {rule: r[f"category_{rule}"] for rule in ("first", "revised")}
        out[k] = {"model": r["model"], "categories": cats,
                  "result": "n/a" if "n/a" in cats.values() else "holds" if all(c == "noise" for c in cats.values()) else
                  "fails (real)" if any(c == "real" for c in cats.values()) else "fails (unresolved)"}
    return out


pts, pct = a20.pts, a20.pct


def ivs(x):
    return "-" if not x or not x["interval"] else f"[{pts(x['interval'][0])}, {pts(x['interval'][1])}]"


def markdown(out):
    L = [f"# Replication of the two paraphrase flags (R10-24)"
         f"{' — PILOT ANSWERS (dry run; no result)' if out['pilot'] else ''}", "",
         "Exploratory, fixed in the protocol before the run. Change = update − control (a fresh control in the same "
         f"batch or run), in points. L = {a20.L}. One look. Levels: DeepSeek 99.17%, Luna 98.75% (the levels of the "
         "flagged decisions).", ""]
    if out["missing"]:
        L += [f"Missing folders: {', '.join(out['missing'])}.", ""]
    L += ["## Decisions of the replication", "", "| Model | Update | Set | Pairs | Change | Interval | Up / down | Sign p | "
          "First rule | Revised rule | 95% interval |", "|---|---|---|---:|---:|---|---|---:|---|---|---|"]
    for run, r in out["runs"].items():
        e = r["replication"]
        for s in ("open", "specific"):
            x = e["sets"][s]
            L.append(f"| {r['model']} | ({r['update']}) | {s} | {x['pairs']} | {pts(x['change'])} | {ivs(x)} | "
                     f"{x['up']} / {x['down']} | {x['sign_p']:.4f} | {e['first']['sets'][s]} | {e['revised']['sets'][s]} "
                     f"| {ivs(r['at_95'][s])} |")
        L.append(f"| {r['model']} | ({r['update']}) | **model** | | | | | | **{e['first']['release']}** | "
                 f"**{e['revised']['release']}** | |")
    L += ["", "## Categories and predictions", "", "| Model | Category, first rule | Category, revised rule | "
          "Original flag against the measured change (first / revised) |", "|---|---|---|---|"]
    for run, r in out["runs"].items():
        L.append(f"| {r['model']} | {r['category_first']} | {r['category_revised']} | {r['measured_first']} / "
                 f"{r['measured_revised']} |")
    L += ["", "| Prediction | Result |", "|---|---|"]
    for k, v in out["predictions"].items():
        L.append(f"| {k} | {json.dumps(v)} |")
    L += ["", "## The original flagged run and the pooled estimate (descriptions)", "",
          "| Model | Set | Original change | Original interval | Original decision (first / revised) | Pooled change | "
          "Pooled interval |", "|---|---|---:|---|---|---:|---|"]
    for run, r in out["runs"].items():
        o = r["original"]
        for s in ("open", "specific"):
            if o is None:
                L.append(f"| {r['model']} | {s} | - | - | - | - | - |")
                continue
            x, p = o["sets"][s], r["pooled"][s]
            L.append(f"| {r['model']} | {s} | {pts(x['change'])} | {ivs(x)} | {o['first']['release']} / "
                     f"{o['revised']['release']} | {pts(p['change'])} | {ivs(p)} |")
    L += ["", "Read kinds per cell:", ""]
    for run, r in out["runs"].items():
        L.append(f"- {r['model']}: " + "; ".join(f"{c} {json.dumps(k)}" for c, k in r["kinds"].items()))
    return "\n".join(L) + "\n"


def run(pilot):
    import runs
    h3.check_amendment()
    data, g = runs.context()
    sets = ra.request_sets(data, g)
    out = {"amendment": "R10-24", "exploratory": True, "pilot": pilot, "L": a20.L, "draws": a20.DRAWS,
           "seed": a20.SEED, "missing": [], "runs": {}}
    for run_name, cells in h3.PLAN.items():
        reads = load(run_name, pilot, set(cells))
        if reads is None:
            out["missing"].append(run_name)
            continue
        orig = load(h3.ORIGINAL[run_name], False, set(cells), SUFFIX)
        if orig is None:
            out["missing"].append(f"{h3.ORIGINAL[run_name]} (the original run; description only)")
        out["runs"][run_name] = analyse(run_name, reads, orig, sets)
    out["predictions"] = predictions(out["runs"])
    OUT.mkdir(exist_ok=True)
    stem = "release_test3_pilot" if pilot else "release_test3"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


def selftest():
    """Fake reads: noise replications must give "noise"; a replication with the same real rise must give "real" and a
    confirmed flag; an absent change must make the original flag a wrong flag; the parse paths of the four cells."""
    rng = random.Random(24)
    sets = {"open": [f"O{i}.json" for i in range(448)], "specific": [f"S{i}.json" for i in range(59)],
            "guesthouse": [f"G{i}.json" for i in range(47)]}
    n_reads = {"open": 1, "specific": 10, "guesthouse": 1}
    hit, miss = ("search", {"type": ("hotel",)}), ("search", {"type": None})

    def fake(cells, p_open, p_spec, rise=0.0, suffix="", sd=0.15):
        reads = collections.defaultdict(list)
        for s, ids in sets.items():
            for d in ids:
                p = min(1.0, max(0.0, rng.gauss(p_open if s != "specific" else p_spec, sd)))
                p = 0.0 if p < 0.05 else 1.0 if p > 0.95 else p
                for _ in range(n_reads[s]):
                    same = rng.random() < p  # off the specific set, both arms get the same read (no change)
                    for i, c in enumerate(cells):
                        if s != "specific":
                            reads[(d, c + suffix)].append(hit if same else miss)
                            continue
                        q = min(1.0, p + rise) if i == 1 else p
                        reads[(d, c + suffix)].append(hit if rng.random() < q else miss)
        return reads

    res = {}
    for run_name, cells in h3.PLAN.items():
        orig = fake(cells, 0.2, 0.5, rise=0.08, suffix=SUFFIX)
        reads = fake(cells, 0.2, 0.5)
        res[run_name] = analyse(run_name, reads, orig, sets)
        r = res[run_name]
        assert r["original_sign"] == 1, r["original"]["sets"]["specific"]
        assert r["category_first"] == "noise" and r["category_revised"] == "noise", (run_name, r["replication"]["sets"])
        assert r["pooled"]["specific"]["pairs"] == 59
    p = predictions(res)
    assert p["P1"]["result"] == "holds" and p["P2"]["result"] == "holds", p
    # a real rise of 15 points on the specific set flags again with the same sign
    cells = h3.PLAN["erk3_luna"]
    real = analyse("erk3_luna", fake(cells, 0.2, 0.5, rise=0.15), fake(cells, 0.2, 0.5, rise=0.15, suffix=SUFFIX), sets)
    assert real["category_first"] == "real" and real["measured_first"] == "confirmed flag", real["replication"]["sets"]
    assert predictions({"erk3_luna": real})["P2"]["result"] == "fails (real)"
    # an absent change makes the original flag a wrong flag (measured)
    tiny = collections.defaultdict(list)
    for s, ids in sets.items():
        for d in ids:
            for _ in range(n_reads[s]):
                for c in cells:
                    tiny[(d, c)].append(miss)
    wrong = analyse("erk3_luna", tiny, fake(cells, 0.2, 0.5, rise=0.08, suffix=SUFFIX), sets)
    assert wrong["measured_first"] == "wrong flag" and wrong["category_first"] == "noise", wrong["replication"]["sets"]
    md = markdown({"pilot": False, "missing": [], "runs": res, "predictions": p})
    assert "P1" in md and "noise" in md
    # parse paths: form cells (DeepSeek) and tool cells (Luna)
    form_row = {"type": "succeeded", "stop": "end_turn", "text": json.dumps(
        {"name": None, "area": ["north"], "pricerange": None, "stars": None, "type": ["hotel"], "parking": None,
         "internet": None})}
    for cell in ("p0", "ppar"):
        k, f = read_of(form_row, cell)
        assert k == "search" and f["type"] == ("hotel",), (cell, k, f)
    tool_row = {"type": "succeeded", "stop": "end_turn", "tool_calls": [{"name": "search_hotels", "input": {
        "name": "null", "area": ["north"], "pricerange": None, "stars": None, "type": ["hotel"], "parking": None,
        "internet": None}}]}
    for cell in ("t0", "tpar2"):
        k, f = read_of(tool_row, cell)
        assert k == "search" and f["type"] == ("hotel",) and f["name"] is None, (cell, f)
    assert read_of({**tool_row, "stop": "max_output_tokens"}, "tpar2") == ("invalid", "cut")
    assert read_of({**form_row, "text": "not json"}, "ppar")[0] == "invalid"
    print("selftest passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        run("--pilot" in sys.argv)
