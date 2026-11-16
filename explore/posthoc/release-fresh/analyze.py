"""Analysis of amendment R10-27 (PROTOCOL.md): a fresh evaluation of the final release-test rule of
the paper on new first requests. Exploratory, fixed in the protocol before the run.

Runs: erk4_luna (cells t0, trep, tord, tpar, tpar2, t1) and erk4_sol (cells t0, trep, t1), tool calls, one batch per
model. Requests: the fresh prefixes of r10/fresh27.py (open 448: 1 answer per cell; specific 59: 10 answers per cell).

Definitions (fixed in R10-27 before any call; the code of the earlier release tests):
- A read is invalid (missing) when its row did not succeed, stopped at the output cap, or fresh27.parse_row gives
  "invalid" (more than one call, another tool name, or no parse). A valid read scores 1 when its search call holds
  hotel in type (natural_analyze.hotel, after the t1 names and values go back to F0); a valid read without a search
  call scores 0 (r10/analysis/release_test.py: read_of, score, valid_scores).
- Per request: the update minus the control (mean of the valid reads of each cell, in points), over the requests with
  a valid read in both cells. The change of a set is the mean over its requests. Up and down: the requests whose
  change is above or below 0.
- One release is one update on every model that receives it: C = (models whose submitted batch holds the update) x 2
  sets x 1 look; level 1 - 0.05/C. Percentile bootstrap over requests, 2,000 draws, seed 20261112 (the draws of
  stats.cluster_bootstrap). L = 5 points. One look with all requests.
- Final rule (primary; Appendix H of the paper): symmetric index k = floor(2,000 x 0.025 / C) (the k-th
  lowest and the k-th highest resampled change); flag if either set has |change| >= L, an interval that excludes 0
  and an exact two-sided sign-test p <= 0.05 / C; pass if both sets have intervals of non-zero width entirely inside
  [-L, +L]; else hold. Code: rtest_final9.boot, set_class, model_dec, decisions ("final").
- Original rule and revised rule (secondary): the index as run (stats.percentile), no sign test (original) or the
  sign test (revised), zero-width intervals allowed ("first_as_run" and "revised_as_run"). Cross-check: the as-run
  interval and both decisions must equal r10/analysis/release_test.py (set_change, decisions).
Usage (from explore/):
    python3 -I posthoc/release-fresh/analyze.py             # the fetched raw.jsonl files
    python3 -I posthoc/release-fresh/analyze.py --pilot     # the pilot rows (dry run)
    python3 -I posthoc/release-fresh/analyze.py --selftest  # fake answers
Outputs: posthoc/release-fresh/out/result.json and result.md (--pilot: pilot_result.*; --selftest: nothing).
No model call, no network call. It opens no folder whose name starts with "em", no *.sealed file and no key file.
"""
import collections
import csv
import hashlib
import importlib.util
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # explore/ of the repository
EXPLORE = ROOT
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import fresh27 as f27  # noqa: E402


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # main() does not run on import
    return m


# Repository copy: the study-folder copies of the two project analyses (the same code with the paths of the
# study folder).
A20_PATH = EXPLORE / "r10" / "analysis" / "release_test.py"
T9_PATH = EXPLORE / "r10" / "analysis" / "rtest_final9.py"
A20 = module("rf_a20", A20_PATH)  # the R10-20 analysis: read_of, score, valid_scores, set_change, decisions, rate
T9 = module("rf_t9", T9_PATH)  # the final-rule code behind Table 12: boot, set_class, model_dec, decisions

OUT = HERE / "out"
L = 5.0
SETS = ("open", "specific")
RULES = {"final": "final", "revised": "revised_as_run", "original": "first_as_run"}
HARMLESS = ("repeat", "field-order edit", "paraphrase 1", "paraphrase 2")
REUSED = {  # every file whose code this analysis or its runs reuse (SHA-256 in result.json)
    "r10/analysis/release_test.py": A20_PATH,
    "r10/analysis/rtest_final9.py": T9_PATH,
    "verify.py of the independent check (not in this repository)": ROOT / "workshops" / "proposals-verified" / "verify.py",
    "verify_release.py of the independent check (not in this repository)": ROOT / "workshops" / "release-test" / "verify_release.py",
    "verify_release2.py of the independent check (not in this repository)": ROOT / "workshops" / "release-test" / "verify_release2.py",
    "r10/analysis/release_analyze.py": EXPLORE / "r10" / "analysis" / "release_analyze.py",
    "r10/analysis/stats.py": EXPLORE / "r10" / "analysis" / "stats.py",
    "r9/natural/natural_analyze.py": EXPLORE / "r9" / "natural" / "natural_analyze.py",
    "r9/natural/natural.py": EXPLORE / "r9" / "natural" / "natural.py",
    "r10/tools.py": EXPLORE / "r10" / "tools.py",
    "r10/control.py": EXPLORE / "r10" / "control.py",
    "r10/harmless.py": EXPLORE / "r10" / "harmless.py",
    "r10/harmless2.py": EXPLORE / "r10" / "harmless2.py",
    "r10/fresh27.py": EXPLORE / "r10" / "fresh27.py",
    "posthoc/release-fresh/analyze.py": pathlib.Path(__file__).resolve(),
}


def sha256(path):
    # Repository copy: some reused files are not in this repository. The stored result.json keeps the values of
    # the study; reproduce.py does not compare the key "sha256".
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "not in this repository"


# ---------------------------------------------------------------------------------------------------- reads

def read_of(row, cell):
    """(kind, fields or reason): A20.read_of with the parse of fresh27 (every cell of R10-27)."""
    if row.get("type", "succeeded") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in A20.CUT:
        return "invalid", "cut"
    kind, val = f27.parse_row(row, cell)
    if kind not in ("search", "none"):
        return "invalid", val if kind == "invalid" else f"kind {kind}"
    return kind, val


def load(run, pilot):
    """{(dialogue id, cell): [(kind, fields or reason), ...]}, or None when the file does not exist."""
    assert not run.startswith("em"), f"refused: {run}"
    path = EXPLORE / run / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    if not path.exists():
        return None
    reads = collections.defaultdict(list)
    for line in path.read_text().splitlines():
        r = json.loads(line)
        _, d, cell, _ = r["custom_id"].split("-")
        reads[(d + ".json", cell)].append(read_of(r, cell))
    return reads


def diffs(reads, ids, control, update):
    out = []
    for d in ids:
        a, b = A20.valid_scores(reads, d, control), A20.valid_scores(reads, d, update)
        if a and b:
            out.append(100 * (A20.mean(b) - A20.mean(a)))
    return out


def kinds(reads, cell):
    c = collections.Counter()
    for (d, x), lst in reads.items():
        if x == cell:
            for k, f in lst:
                c[k if k != "invalid" else f"invalid: {str(f)[:50]}"] += 1
    return dict(c)


def receivers(models_present):
    """{update: [models whose batch holds the update]} for the models in `models_present` (run name -> model)."""
    return {u: [m for run, m in models_present.items() if cell in f27.PLAN[run]] for u, cell in f27.UPDATES.items()}


def level(c):
    return 1 - 0.05 / c


# ---------------------------------------------------------------------------------------------------- analysis

def analyse(reads_of, sets):
    """reads_of: {model: reads}. Returns the per-update, per-model results under the three rules."""
    run_of = {m: run for run, m in f27.MODEL_OF.items()}
    rec = receivers({run_of[m]: m for m in reads_of})
    res, checks = {}, []
    for u, cell in f27.UPDATES.items():
        ms = rec[u]
        if not ms:
            continue
        c = len(ms) * len(SETS) * 1
        lev = level(c)
        entry = {"cell": cell, "C": c, "level": lev, "k_symmetric": T9.k_sym(lev), "models": {}}
        for m in ms:
            reads = reads_of[m]
            ss = {s: T9.boot(diffs(reads, sets[s], f27.CONTROL, cell), lev) for s in SETS}
            dec = T9.decisions(ss["open"], ss["specific"], lev)
            alpha = 1 - lev
            classes = {s: {"original": T9.set_class(ss[s], "as_run"),
                           "revised": T9.set_class(ss[s], "as_run", alpha),
                           "final": T9.set_class(ss[s], "symmetric", alpha, True)} for s in SETS}
            # cross-check with the R10-20 analysis code (as-run interval, original and revised decisions)
            a20 = {s: A20.set_change(reads, sets[s], f27.CONTROL, cell, lev)[0] for s in SETS}
            a20_dec = A20.decisions(a20, lev)
            ok = all(T9.close(ss[s]["change"], a20[s]["change"]) and T9.close(ss[s]["as_run"][0], a20[s]["interval"][0])
                     and T9.close(ss[s]["as_run"][1], a20[s]["interval"][1]) and ss[s]["up"] == a20[s]["up"]
                     and ss[s]["down"] == a20[s]["down"] for s in SETS)
            ok_dec = (a20_dec["first"]["release"], a20_dec["revised"]["release"]) == (dec["first_as_run"],
                                                                                      dec["revised_as_run"])
            checks.append({"update": u, "model": m, "sets_equal_to_release_test_analyze": ok,
                           "decisions_equal_to_release_test_analyze": ok_dec})
            entry["models"][m] = {
                "decisions": {r: dec[k] for r, k in RULES.items()},
                "sets": {s: {**T9.show(ss[s]), "zero_width_symmetric": ss[s]["symmetric"][0] == ss[s]["symmetric"][1],
                             "class": classes[s]} for s in SETS},
                "rates": {s: {"control": A20.rate(reads, sets[s], f27.CONTROL), "update": A20.rate(reads, sets[s], cell)}
                          for s in SETS},
            }
        entry["tally"] = {r: {d: sum(v["decisions"][r] == d for v in entry["models"].values())
                              for d in ("flag", "pass", "hold")} for r in RULES}
        res[u] = entry
    return res, checks


def predictions(res):
    """F1: the full rename is flagged for every model. F2 to F4: no flag for the repeat, the field-order edit,
    paraphrase 1 and paraphrase 2 (F4 covers both paraphrases). Each per model and rule."""
    out = {}
    for name, ups, want in (("F1", ("full rename",), "flag"), ("F2", ("repeat",), "no flag"),
                            ("F3", ("field-order edit",), "no flag"), ("F4", ("paraphrase 1", "paraphrase 2"), "no flag")):
        for rule in RULES:
            per = {f"{u}, {m}": e["models"][m]["decisions"][rule] for u in ups if u in res
                   for m, e in [(m, res[u]) for m in res[u]["models"]]}
            held = {k: (d == "flag") == (want == "flag") for k, d in per.items()}
            out[f"{name}_{rule}"] = {"want": want, "decisions": per, "held": held,
                                     "result": "n/a" if not per else "holds" if all(held.values()) else "fails"}
    return out


def harmless_totals(res):
    out = {}
    for rule in RULES:
        t = collections.Counter()
        for u in HARMLESS:
            if u in res:
                for v in res[u]["models"].values():
                    t[v["decisions"][rule]] += 1
        out[rule] = {d: t[d] for d in ("flag", "pass", "hold")}
    return out


def money():
    """The ledger rows, bounds and batch facts of the runs of R10-27 (no em* folder)."""
    path = EXPLORE / "ledger_openai_r9.csv"
    if not path.exists():  # repository copy: the cost records are not here; keep the stored values
        return json.loads((OUT / "result.json").read_text())["money"]
    rows = [r for r in csv.DictReader(open(path)) if r["experiment"] in f27.PLAN]
    out = {"ledger_rows": rows, "total_list_price_usd": round(sum(float(r["list_price_usd"]) for r in rows), 4),
           "batches": {}}
    for run in f27.PLAN:
        b = EXPLORE / run / "batch.json"
        fin = EXPLORE / run / "batch_final.json"
        if b.exists():
            info = json.loads(b.read_text())
            x = {"bound": info["bound"], "requests": info["requests"], "created": info["created"]}
            if fin.exists():
                fb = json.loads(fin.read_text())
                x.update(status=fb.get("status"), request_counts=fb.get("request_counts"))
            out["batches"][run] = x
    return out


# ---------------------------------------------------------------------------------------------------- output

pts, pct = A20.pts, A20.pct


def iv(x):
    return f"[{pts(x[0])}, {pts(x[1])}]"


def markdown(out):
    lines = [f"# Fresh evaluation of the final release-test rule (R10-27)"
             f"{' — PILOT ANSWERS (dry run; no result)' if out['pilot'] else ''}", "",
             "Exploratory, fixed in the protocol before the run. Change = update − control (same batch), in points. "
             f"L = {L:g}. One look with all requests. Fresh requests: open {out['sizes']['open']} (1 answer per cell), "
             f"specific {out['sizes']['specific']} (10 answers per cell). Final rule (primary): symmetric index, sign "
             "condition, no pass from a zero-width interval, C = models that receive the update × 2 sets × 1 look. "
             "Original and revised rules (secondary): the index as run, without and with the sign condition.", ""]
    if out["missing"]:
        lines += [f"Missing runs: {', '.join(out['missing'])}.", ""]
    lines += ["## Decisions (flag / pass / hold)", "",
              "| Update | C | Level | Model | Final rule | Revised rule | Original rule |", "|---|---:|---:|---|---|---|---|"]
    for u, e in out["updates"].items():
        for m, v in e["models"].items():
            d = v["decisions"]
            lines.append(f"| {u} | {e['C']} | {100 * e['level']:.2f}% | {m} | **{d['final']}** | {d['revised']} | "
                         f"{d['original']} |")
    lines += ["", "| Update | Final: flag / pass / hold | Revised | Original |", "|---|---|---|---|"]
    for u, e in out["updates"].items():
        t = e["tally"]
        lines.append(f"| {u} | " + " | ".join(f"{t[r]['flag']} / {t[r]['pass']} / {t[r]['hold']}" for r in RULES) + " |")
    h = out["harmless_totals"]
    lines.append(f"| harmless updates (repeat, field order, paraphrases) | "
                 + " | ".join(f"{h[r]['flag']} / {h[r]['pass']} / {h[r]['hold']}" for r in RULES) + " |")
    lines += ["", "## Changes by set", "",
              "| Update | Model | Set | Pairs | Change | Interval, symmetric (final) | Interval, as run | Up / down | "
              "Sign p | Final | Revised | Original |", "|---|---|---|---:|---:|---|---|---|---:|---|---|---|"]
    for u, e in out["updates"].items():
        for m, v in e["models"].items():
            for s in SETS:
                x = v["sets"][s]
                lines.append(f"| {u} | {m} | {s} | {x['pairs']} | {pts(x['change'])} | {iv(x['symmetric'])}"
                             f"{' (zero width)' if x['zero_width_symmetric'] else ''} | {iv(x['as_run'])} | "
                             f"{x['up']} / {x['down']} | {x['sign_p']:.4f} | {x['class']['final']} | "
                             f"{x['class']['revised']} | {x['class']['original']} |")
    lines += ["", "## Predictions (fixed in R10-27)", "", "| Prediction | Rule | Want | Decisions | Result |",
              "|---|---|---|---|---|"]
    for k, v in out["predictions"].items():
        name, rule = k.split("_")
        lines.append(f"| {name} | {rule} | {v['want']} | {json.dumps(v['decisions'])} | {v['result']} |")
    lines += ["", "## Rates of a hotel value (valid reads)", "", "| Update | Model | Set | Control | Update |",
              "|---|---|---|---|---|"]
    for u, e in out["updates"].items():
        for m, v in e["models"].items():
            for s in SETS:
                a, b = v["rates"][s]["control"], v["rates"][s]["update"]
                lines.append(f"| {u} | {m} | {s} | {pct(a['share'])} ({a['k']}/{a['n']}) | "
                             f"{pct(b['share'])} ({b['k']}/{b['n']}) |")
    lines += ["", "## Read kinds per cell", ""]
    for m, k in out["kinds"].items():
        lines.append(f"- {m}: " + "; ".join(f"{c} {json.dumps(x)}" for c, x in k.items()))
    lines += ["", "## Selection", "", f"Pool counts: {json.dumps(out['selection']['pool'])}.", "",
              "## Money", "", f"Ledger list price of the R10-27 rows: {out['money']['total_list_price_usd']:.4f} USD.", ""]
    for r in out["money"]["ledger_rows"]:
        lines.append(f"- {r['utc']} {r['experiment']} {r['step']}: bound {r['bound_usd']} USD, list price "
                     f"{r['list_price_usd']} USD")
    for run, b in out["money"]["batches"].items():
        lines.append(f"- {run}: {json.dumps(b)}")
    lines += ["", "## Checks", "", f"- Cross-check with r10/analysis/release_test.py: "
              f"{sum(c['sets_equal_to_release_test_analyze'] and c['decisions_equal_to_release_test_analyze'] for c in out['checks'])}"
              f" of {len(out['checks'])} model-update pairs equal.", "", "## SHA-256 of the reused files", ""]
    for k, v in out["sha256"].items():
        lines.append(f"- `{k}`: `{v}`")
    return "\n".join(lines) + "\n"


def run(pilot):
    import runs
    data, g = runs.context()
    sel = f27.select(data, g)
    sets = {s: sel[s] for s in SETS}
    reads_of, missing = {}, []
    for r, m in f27.MODEL_OF.items():
        # Repository copy: the batch records are not here; a fetched raw.jsonl shows that the batch was submitted.
        submitted = (EXPLORE / r / "batch.json").exists() or (EXPLORE / r / "raw.jsonl").exists() or pilot
        reads = load(r, pilot)
        if reads is None or not submitted:
            missing.append(r)
            continue
        reads_of[m] = reads
    res, checks = analyse(reads_of, sets)
    run_of = {m: r for r, m in f27.MODEL_OF.items()}
    out = {"amendment": "R10-27", "exploratory": True, "pilot": pilot, "L": L, "draws": T9.DRAWS, "seed": T9.SEED,
           "sizes": {s: len(v) for s, v in sets.items()}, "missing": missing, "updates": res, "checks": checks,
           "predictions": predictions(res), "harmless_totals": harmless_totals(res),
           "kinds": {m: {c: kinds(reads_of[m], c) for c in f27.PLAN[run_of[m]]} for m in reads_of},
           "selection": {"pool": sel["pool"], "open": sel["open"], "specific": sel["specific"], "seed": f27.SEED},
           "money": money(), "sha256": {k: sha256(p) for k, p in REUSED.items()}}
    OUT.mkdir(exist_ok=True)
    stem = "pilot_result" if pilot else "result"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


def selftest():
    """Fake answers with known effects: the rename removes most hotel values, the other updates change nothing."""
    rng = random.Random(1)
    sets = {"open": [f"O{i:04d}.json" for i in range(448)], "specific": [f"S{i:04d}.json" for i in range(59)]}
    reads_of = {}
    for m in ("luna", "sol"):
        reads = collections.defaultdict(list)
        for s, ids in sets.items():
            n = 1 if s == "open" else 10
            for d in ids:
                p = 0.25 if s == "open" else 0.5
                for cell in f27.PLAN[f"erk4_{m}"]:
                    q = p * (0.1 if cell == "t1" else 1.0)
                    for _ in range(n):
                        reads[(d, cell)].append(("search", {"type": ("hotel",) if rng.random() < q else None}))
        reads_of[m] = reads
    res, checks = analyse(reads_of, sets)
    assert all(c["sets_equal_to_release_test_analyze"] and c["decisions_equal_to_release_test_analyze"] for c in checks)
    assert res["full rename"]["C"] == 4 and res["field-order edit"]["C"] == 2, (res["full rename"]["C"],)
    assert all(v["decisions"]["final"] == "flag" for v in res["full rename"]["models"].values())
    harmless = {f"{u}, {m}": v["decisions"]["final"] for u in HARMLESS if u in res for m, v in res[u]["models"].items()}
    # a zero-width case: identical answers in both cells give no pass under the final rule, a pass under the original
    same = collections.defaultdict(list)
    for s, ids in sets.items():
        for d in ids:
            for cell in f27.PLAN["erk4_luna"]:
                same[(d, cell)] += [("none", "")] * (1 if s == "open" else 10)
    r2, _ = analyse({"luna": same}, sets)
    v = r2["repeat"]["models"]["luna"]
    assert v["decisions"] == {"final": "hold", "revised": "pass", "original": "pass"}, v["decisions"]
    pr = predictions(res)
    print("selftest ok:", {k: x["result"] for k, x in pr.items()}, "| harmless, final rule:", harmless,
          "| zero-width case:", v["decisions"])


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        run("--pilot" in sys.argv)
