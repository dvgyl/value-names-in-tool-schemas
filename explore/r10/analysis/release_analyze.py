"""The forward release test of amendment R10-6 (PROTOCOL.md "### R10-6"). Exploratory; no prediction.

Inputs: erp_sonnet/raw.jsonl and erp_sol/raw.jsonl (arms t0 and tedit, 1 read, the 554 prefixes of experiment A), the
frozen edit r10/release/edit.json, MultiWOZ 2.4 and hotel_db.json. Outputs: r10/analysis/out/release.md and release.json.
With --pilot it reads erp_<model>/pilot_raw.jsonl instead and writes out/release_pilot_dryrun.md and .json: a dry run
of the code. Its numbers are no result (the pilot draws other prefixes for each arm, so few prefixes pair).

Definitions (fixed in R10-6, before any answer of these runs existed):
- Sets: open = the 448 prefixes whose brief sets no type (gold.brief_type of info and of fail_info both None);
  specific = the 59 prefixes whose brief sets hotel (gold.brief_type(d) == "hotel"); the 47 guesthouse prefixes are
  described only.
- A read is invalid (missing) when its row did not succeed, stopped at the length limit, or release.parse_call gives
  "invalid". A valid read scores 1 when it is a search whose type holds "hotel" (natural_analyze.hotel, after the
  tedit values go back through the reversed value_map); a valid read without a search call scores 0.
- Per prefix: tedit minus t0 (mean of the valid reads of each arm, in points), over the prefixes with a valid read in
  both arms. The change of a set is the mean of these differences.
- The rule: Appendix I of the paper (decide, release, interval_level, copied unchanged below). L = 5 points;
  one look with all requests (n = n_max); C = 2 models x 2 sets x 1 look; level 1 - 0.05/4 = 0.9875; percentile
  cluster bootstrap over prefixes (stats.cluster_bootstrap, 2,000 draws, seed 20261112).
- Descriptions: rates per arm and set; trade ratio (stats.trade: wrong group open, correct group specific, sizes 448
  and 59; correct values lost / wrong values removed; 95% interval by stats.trade_interval); blocking filters on the
  open set (briefsearch.search_failure per valid read, share per arm, 95% cluster bootstrap); read kinds per arm.
Usage (from explore/): .venv/bin/python -I r10/analysis/release_analyze.py [--pilot]
"""
import collections
import json
import math
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
import natural_analyze as na  # noqa: E402
import release as rel  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
MODELS = {"sonnet": "erp_sonnet", "sol": "erp_sol"}
ARMS = ("t0", "tedit")
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
SIZES = {"open": 448, "specific": 59, "guesthouse": 47}
L, SETS, LOOKS = 5, 2, 1
DRAWS, SEED = 2000, 20261112
N_MAX = 554  # the largest number: all prefixes, 1 read per arm


# ---- Appendix I of the paper, unchanged ----
def decide(change, low, high, L):
    """One model, one request set: the change and its interval, in points.
    The interval level is fixed before the run (see interval_level)."""
    if abs(change) >= L and (low > 0 or high < 0):
        return "flag-worthy"  # the estimate is at least L; the true change may be smaller
    if -L <= low and high <= L:
        return "absent"
    return "unresolved"


def release(open_set, specific_set, L, n, n_max):
    """One model. Each set is (change, low, high), or None when it was not measured.
    n: requests collected so far; n_max: the largest number, fixed before the run."""
    d = [decide(*s, L) for s in (open_set, specific_set) if s is not None]
    if "flag-worthy" in d:
        return "flag"
    if len(d) == 2 and all(x == "absent" for x in d):
        return "pass"
    if n >= n_max:
        return "hold"  # a precaution, not a detected change
    return "more data"


def interval_level(models, sets=2, looks=1, error=0.05):
    """Bonferroni level for each interval. If every interval has this coverage, the chance that
    any interval misses its true change is at most `error`. Outside that chance, no set without
    a true change is "flag-worthy", and no set whose true change exceeds L in size is "absent".
    Holds at n_max are not covered. Bootstrap coverage is approximate."""
    return 1 - error / (models * sets * looks)  # 7 models, 2 sets, 1 look: 0.9964
# ---- end of Appendix I ----


LEVEL = interval_level(len(MODELS), SETS, LOOKS)


def request_sets(data, g):
    ids = list(g["booked"])
    out = {"open": [d for d in ids if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None],
           "specific": [d for d in ids if gold.brief_type(data[d]) == "hotel"],
           "guesthouse": [d for d in ids if gold.brief_type(data[d]) == "guesthouse"]}
    assert {k: len(v) for k, v in out.items()} == SIZES, {k: len(v) for k, v in out.items()}
    return out


def read_of(row, arm):
    """(kind, fields or reason): kind is "search", "none" or "invalid"."""
    if row.get("type") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in CUT:
        return "invalid", "cut"
    kind, val = rel.parse_call(row, arm)
    if kind not in ("search", "none"):
        return "invalid", val if kind == "invalid" else f"kind {kind}"
    return kind, val


def load(folder, pilot):
    """{(dialogue id, arm): [(kind, fields or reason), ...]}, or None when the file does not exist."""
    path = EXPLORE / folder / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    if not path.exists():
        return None
    reads = collections.defaultdict(list)
    for line in path.read_text().splitlines():
        r = json.loads(line)
        _, d, arm, _ = r["custom_id"].split("-")
        reads[(d + ".json", arm)].append(read_of(r, arm))
    return reads


def score(kind, fields):
    return int(kind == "search" and na.hotel(fields.get("type")))


def valid_scores(reads, d, arm):
    return [score(k, f) for k, f in reads.get((d, arm), []) if k != "invalid"]


def mean(xs):
    return sum(xs) / len(xs)


def change(reads, ids):
    """(change, low, high) in points at LEVEL, the number of paired prefixes, and the per-prefix rows for the trade."""
    diffs, rows = [], []
    for d in ids:
        a, b = valid_scores(reads, d, "t0"), valid_scores(reads, d, "tedit")
        if a and b:
            diffs.append(100 * (mean(b) - mean(a)))
            rows.append((sum(a), len(a), sum(b), len(b)))
    if not diffs:
        return None, 0, rows
    ci = stats.cluster_bootstrap({"all": [(x,) for x in diffs]}, lambda g: mean([r[0] for r in g["all"]]),
                                 draws=DRAWS, seed=SEED, level=LEVEL)
    return ci, len(diffs), rows


def rate(reads, ids, arm):
    vals = [x for d in ids for x in valid_scores(reads, d, arm)]
    return {"k": sum(vals), "n": len(vals), "share": mean(vals) if vals else None}


def blocking(reads, ids, arm, data, db):
    """Search failure on the open set: per prefix (failures, valid reads); share and 95% cluster bootstrap."""
    per = []
    for d in ids:
        k = n = 0
        for kind, f in reads.get((d, arm), []):
            if kind == "invalid":
                continue
            n += 1
            k += kind == "search" and bs.search_failure(f, data[d], db)
        if n:
            per.append((k, n))
    if not per:
        return {"k": 0, "n": 0, "share": None}
    k, n = sum(r[0] for r in per), sum(r[1] for r in per)
    _, lo, hi = stats.cluster_bootstrap({"all": per}, lambda g: sum(r[0] for r in g["all"]) / sum(r[1] for r in g["all"]),
                                        draws=DRAWS, seed=SEED)
    return {"k": k, "n": n, "share": k / n, "ci95": [lo, hi]}


def trade(rows_open, rows_spec):
    if not rows_open or not rows_spec or not sum(r[1] for r in rows_open) or not sum(r[1] for r in rows_spec):
        return None
    cells, sizes = {"open": rows_open, "specific": rows_spec}, {"open": SIZES["open"], "specific": SIZES["specific"]}
    (removed, lost, ratio), lo, hi = stats.trade_interval(cells, sizes, wrong=("open",), correct="specific")
    return {"wrong_removed": removed, "correct_lost": lost, "ratio": ratio if math.isfinite(ratio) else None,
            "ratio_ci95": [lo if math.isfinite(lo) else None, hi if math.isfinite(hi) else None],
            "defined": removed > 0}


def kinds(reads, arm):
    c = collections.Counter()
    types = collections.Counter()
    for (d, a), lst in reads.items():
        if a != arm:
            continue
        for k, f in lst:
            c[k if k != "invalid" else f"invalid: {str(f)[:60]}"] += 1
            if k == "search":
                t = f.get("type")
                types["null" if t is None else t if isinstance(t, str) else "+".join(t)] += 1
    return dict(c), dict(types)


def analyse(reads, sets, data, db):
    res = {"rates": {s: {arm: rate(reads, ids, arm) for arm in ARMS} for s, ids in sets.items()}}
    res["kinds"], res["type_values"] = {}, {}
    for arm in ARMS:
        res["kinds"][arm], res["type_values"][arm] = kinds(reads, arm)
    res["sets"], rows = {}, {}
    for s in ("open", "specific", "guesthouse"):
        ci, n_pairs, rows[s] = change(reads, sets[s])
        entry = {"pairs": n_pairs, "change": None, "interval": None, "decision": None}
        if ci:
            entry.update(change=ci[0], interval=[ci[1], ci[2]])
            if s != "guesthouse":  # the guesthouse set enters no decision
                entry["decision"] = decide(ci[0], ci[1], ci[2], L)
        res["sets"][s] = entry
    as_tuple = lambda e: (e["change"], *e["interval"]) if e["interval"] else None  # noqa: E731
    res["release"] = release(as_tuple(res["sets"]["open"]), as_tuple(res["sets"]["specific"]), L, N_MAX, N_MAX)
    res["trade"] = trade(rows["open"], rows["specific"])
    res["blocking_open"] = {arm: blocking(reads, sets["open"], arm, data, db) for arm in ARMS}
    return res


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def pts(x):
    return "-" if x is None else f"{x:+.1f}"


def markdown(out):
    dry = out["dry_run"]
    L_ = ["## Forward release test (amendment R10-6)", ""]
    if dry:
        L_ += ["**DRY RUN on the pilot rows (pilot_raw.jsonl). These numbers are no result.** The pilot draws other "
               "prefixes for each arm, so few or no prefixes pair, and the decisions below only test the code.", ""]
    L_ += [f"Exploratory. Edit: Claude Opus 5.5 rewrote the search tool (r10/release/edit.json, SHA-256 "
           f"`{out['edit_sha256']}`). L = {L} points; one look with all requests; C = {out['C']}; interval level "
           f"{100 * out['level']:.2f}% (percentile cluster bootstrap over prefixes, {DRAWS} draws, seed {SEED}). "
           f"Sets: open {SIZES['open']}, specific {SIZES['specific']} (guesthouse {SIZES['guesthouse']}, no decision).", ""]
    if out["missing"]:
        L_ += [f"Not fetched at this run: {', '.join(out['missing'])}.", ""]
    L_ += ["### Decisions", "", f"| Model | Set | Pairs | Change, points | {100 * out['level']:.2f}% interval | Set decision |"
           " Model decision |", "|---|---|---|---|---|---|---|"]
    for m, r in out["models"].items():
        for s in ("open", "specific"):
            e = r["sets"][s]
            iv = f"[{pts(e['interval'][0])}, {pts(e['interval'][1])}]" if e["interval"] else "-"
            L_.append(f"| {m} | {s} | {e['pairs']} | {pts(e['change'])} | {iv} | {e['decision'] or 'not measured'} | "
                      f"{r['release'] if s == 'open' else ''} |")
    L_ += ["", "### Descriptions (no decision)", "", "Rate of `type` holding hotel (valid reads):", "",
           "| Model | Set | t0 | tedit | Guesthouse-set change, points |", "|---|---|---|---|---|"]
    for m, r in out["models"].items():
        for s in ("open", "specific", "guesthouse"):
            a, b = r["rates"][s]["t0"], r["rates"][s]["tedit"]
            g = r["sets"]["guesthouse"]
            L_.append(f"| {m} | {s} | {pct(a['share'])} ({a['k']}/{a['n']}) | {pct(b['share'])} ({b['k']}/{b['n']}) | "
                      f"{pts(g['change']) if s == 'guesthouse' else ''} |")
    L_ += ["", "| Model | Trade: wrong removed | correct lost | ratio [95%] | Blocking filters, open set: t0 | tedit |",
           "|---|---|---|---|---|---|"]
    for m, r in out["models"].items():
        t, bo = r["trade"], r["blocking_open"]
        if t is None:
            tr = "- | - | not computed (a set has no pair)"
        elif not t["defined"]:
            tr = f"{t['wrong_removed']:.1f} | {t['correct_lost']:.1f} | not defined (the edit removes no wrong value)"
        else:
            ci = t["ratio_ci95"]
            tr = (f"{t['wrong_removed']:.1f} | {t['correct_lost']:.1f} | {t['ratio']:.2f} "
                  f"[{'-' if ci[0] is None else f'{ci[0]:.2f}'}, {'inf' if ci[1] is None else f'{ci[1]:.2f}'}]")
        bl = " | ".join(f"{pct(bo[a]['share'])} ({bo[a]['k']}/{bo[a]['n']})" for a in ARMS)
        L_.append(f"| {m} | {tr} | {bl} |")
    L_ += ["", "Read kinds and `type` values of the search calls, per arm:", ""]
    for m, r in out["models"].items():
        for arm in ARMS:
            L_.append(f"- {m} {arm}: kinds {json.dumps(r['kinds'][arm])}; type {json.dumps(r['type_values'][arm])}")
    return "\n".join(L_) + "\n"


def main():
    pilot = "--pilot" in sys.argv
    rel.check_amendment()  # the analysis uses the edit whose SHA-256 the amendment holds
    data, g = runs.context()
    db = gold.hotel_db()
    sets = request_sets(data, g)
    out = {"amendment": "R10-6", "exploratory": True, "dry_run": pilot, "edit_sha256": rel.sha256(), "L": L,
           "C": len(MODELS) * SETS * LOOKS, "level": LEVEL, "draws": DRAWS, "seed": SEED, "n_max": N_MAX,
           "sets": SIZES, "missing": [], "models": {}}
    for m, folder in MODELS.items():
        reads = load(folder, pilot)
        if reads is None:
            out["missing"].append(folder)
            continue
        out["models"][m] = analyse(reads, sets, data, db)
    OUT.mkdir(exist_ok=True)
    stem = "release_pilot_dryrun" if pilot else "release"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


if __name__ == "__main__":
    main()
