"""Analysis of amendment R10-20 (prototypes/explore/PROTOCOL.md): release tests of harmless updates and of an unchanged
tool, with the registered rename as a known change. Exploratory.

Runs: erk_sol, erk_luna (tool calls; cells t0, trep, tpar, t1) and erk_deepseek, erk_qwen, erk_gemma (form answers;
cells p0, prep, ppar, p1). The 554 first requests of experiment A: open set 448 (1 answer per arm), specific set 59
(10 answers per arm), guesthouse set 47 (1 answer per arm; description only).

Definitions (fixed in R10-20 before any call):
- A read is invalid (missing) when its row did not succeed, stopped at the output cap, or harmless.parse_row gives
  "invalid" (more than one call, another tool name, or no parse). A valid read scores 1 when it is a search (a tool
  call, or a form answer) whose type holds hotel after the names and values go back to F0; a valid read without a
  search call scores 0.
- Per request: the update minus the control (mean of the valid reads of each arm, in points), over the requests with a
  valid read of both. The change of a set is the mean over its requests. Up and down: the requests whose change is
  above or below 0 (the per-request change).
- One release is one update on the models of one output channel. Level 1 - 0.05/C with C = models x sets x looks:
  tool channel C = 2 x 2 x 1 = 4 (98.75%); form channel C = 3 x 2 x 1 = 6 (99.17%). Percentile cluster bootstrap over
  requests (stats.cluster_bootstrap, 2,000 draws, seed 20261112). L = 5 points. One look with all requests (n = n_max).
- First rule: decide and release of R10-6 (release_analyze.py, the code fixed before the R10-6 run). Revised rule:
  decide and release of Appendix I of the paper, with the exact sign condition at alpha = 1 - level.
- Descriptions: every decision at 98.75% (the level of Table 4 of the paper); rates per arm and set; the guesthouse
  set; the trade ratio and the blocking filters on the open set (release_analyze.trade and blocking); read kinds.

Usage (from explore/):
    python3 -I r10/analysis/release_test.py            # the fetched raw.jsonl files
    python3 -I r10/analysis/release_test.py --selftest # fake answers
Outputs: r10/analysis/out/release_test.json and release_test.md.
This file is a copy of the project analysis (workshops/release-test/analyze.py) with the paths of the study folder; the results are the same.
No model call, no network call. It opens no folder whose name starts with "em", no *.sealed file and no key file.
"""
import collections
import json
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import harmless as hm  # noqa: E402
import natural_analyze as na  # noqa: E402
import release_analyze as ra  # noqa: E402  (its main does not run)
import stats  # noqa: E402

OUT = HERE / "out"
CUT = ra.CUT
MODELS = {"sol": "erk_sol", "luna": "erk_luna", "deepseek": "erk_deepseek", "qwen": "erk_qwen", "gemma": "erk_gemma"}
L, SETS, LOOKS, DRAWS, SEED = 5, 2, 1, 2000, 20261112
TABLE4_LEVEL = 0.9875
UPDATE_NAMES = {"a": "unchanged (repeat)", "b": "paraphrase", "c": "rename"}


# ---- Appendix I of the paper (revised rule), unchanged ----
def sign_p(up, down):
    """Two-sided exact sign test over requests: up and down count rises and falls; ties are dropped."""
    n, k = up + down, min(up, down)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0


def decide(change, low, high, L, up, down, alpha):
    """One model, one request set: the change and its interval, in points. The interval level
    1 - alpha is fixed before the run (see interval_level). The sign condition was added post hoc."""
    if abs(change) >= L and (low > 0 or high < 0) and sign_p(up, down) <= alpha:
        return "meets flag rule"  # the estimate is at least L; the true change may be smaller
    if -L <= low and high <= L:
        return "within limits"
    return "unresolved"


def release(open_set, specific_set, L, alpha, n, n_max):
    """One model. Each set is (change, low, high, up, down), or None when it was not measured.
    n: requests collected so far; n_max: the largest number, fixed before the run."""
    d = [decide(*s[:3], L, *s[3:], alpha) for s in (open_set, specific_set) if s is not None]
    if "meets flag rule" in d:
        return "flag"
    if len(d) == 2 and all(x == "within limits" for x in d):
        return "pass"
    if n >= n_max:
        return "hold"  # a precaution, not a detected change
    return "more data"


def interval_level(models, sets=2, looks=1, error=0.05):
    return 1 - error / (models * sets * looks)
# ---- end of Appendix I ----


def channel_models(channel):
    return [m for m in MODELS if hm.CHANNEL[m] == channel]


LEVELS = {ch: interval_level(len(channel_models(ch)), SETS, LOOKS) for ch in ("tool", "form")}
assert abs(LEVELS["tool"] - 0.9875) < 1e-12 and abs(LEVELS["form"] - (1 - 0.05 / 6)) < 1e-12, LEVELS


def read_of(row, cell):
    """(kind, fields or reason): kind is "search", "none" or "invalid"."""
    if row.get("type", "succeeded") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in CUT:
        return "invalid", "cut"
    kind, val = hm.parse_row(row, cell)
    if kind not in ("search", "none"):
        return "invalid", val if kind == "invalid" else f"kind {kind}"
    return kind, val


def load(folder, pilot):
    """{(dialogue id, cell): [(kind, fields or reason), ...]}, or None when the file does not exist."""
    assert not folder.startswith("em"), f"refused: {folder}"
    path = EXPLORE / folder / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    if not path.exists():
        return None
    reads = collections.defaultdict(list)
    for line in path.read_text().splitlines():
        r = json.loads(line)
        _, d, cell, _ = r["custom_id"].split("-")
        reads[(d + ".json", cell)].append(read_of(r, cell))
    return reads


def score(kind, fields):
    return int(kind == "search" and na.hotel(fields.get("type")))


def valid_scores(reads, d, cell):
    return [score(k, f) for k, f in reads.get((d, cell), []) if k != "invalid"]


def mean(xs):
    return sum(xs) / len(xs)


def set_change(reads, ids, control, update, level):
    """The change, its interval at `level`, the pairs, the per-request up and down counts, the sign p, the trade rows."""
    diffs, rows = [], []
    for d in ids:
        a, b = valid_scores(reads, d, control), valid_scores(reads, d, update)
        if a and b:
            diffs.append(100 * (mean(b) - mean(a)))
            rows.append((sum(a), len(a), sum(b), len(b)))
    out = {"pairs": len(diffs), "change": None, "interval": None, "up": sum(x > 0 for x in diffs),
           "down": sum(x < 0 for x in diffs)}
    out["sign_p"] = sign_p(out["up"], out["down"])
    if diffs:
        point, lo, hi = stats.cluster_bootstrap({"all": [(x,) for x in diffs]}, lambda g: mean([r[0] for r in g["all"]]),
                                                draws=DRAWS, seed=SEED, level=level)
        out.update(change=point, interval=[lo, hi])
    return out, rows


def decisions(sets_res, level):
    """First rule (R10-6 code) and revised rule (Appendix I) for one model and update, at `level`."""
    alpha = 1 - level
    first, revised = {}, {}
    for s in ("open", "specific"):
        e = sets_res[s]
        if e["interval"] is None:
            first[s] = revised[s] = None
            continue
        first[s] = ra.decide(e["change"], *e["interval"], L)
        revised[s] = decide(e["change"], *e["interval"], L, e["up"], e["down"], alpha)
    t1 = lambda s: None if sets_res[s]["interval"] is None else (sets_res[s]["change"], *sets_res[s]["interval"])  # noqa: E731
    t2 = lambda s: None if sets_res[s]["interval"] is None else (  # noqa: E731
        sets_res[s]["change"], *sets_res[s]["interval"], sets_res[s]["up"], sets_res[s]["down"])
    return {"first": {"sets": first, "release": ra.release(t1("open"), t1("specific"), L, 1, 1)},
            "revised": {"sets": revised, "release": release(t2("open"), t2("specific"), L, alpha, 1, 1)}}


def analyse_update(reads, sets, control, update, level, data=None, db=None):
    res = {"level": level, "sets": {}}
    rows = {}
    for s in ("open", "specific", "guesthouse"):
        res["sets"][s], rows[s] = set_change(reads, sets[s], control, update, level)
    res.update(decisions(res["sets"], level))
    if abs(level - TABLE4_LEVEL) > 1e-12:  # description: the same rule at the Table 4 level
        t4 = {s: set_change(reads, sets[s], control, update, TABLE4_LEVEL)[0] for s in ("open", "specific")}
        res["at_98_75"] = {"sets": {s: {k: t4[s][k] for k in ("change", "interval")} for s in t4},
                           **decisions(t4, TABLE4_LEVEL)}
    res["rates"] = {s: {arm: rate(reads, sets[s], cell) for arm, cell in (("control", control), ("update", update))}
                    for s in sets}
    res["trade"] = ra.trade(rows["open"], rows["specific"])
    if data is not None:
        both = {(d, "t0" if c == control else "tedit"): v for (d, c), v in reads.items() if c in (control, update)}
        res["blocking_open"] = {arm: ra.blocking(both, sets["open"], arm, data, db) for arm in ("t0", "tedit")}
    return res


def rate(reads, ids, cell):
    vals = [x for d in ids for x in valid_scores(reads, d, cell)]
    return {"k": sum(vals), "n": len(vals), "share": mean(vals) if vals else None}


def kinds(reads, cell):
    c = collections.Counter()
    for (d, x), lst in reads.items():
        if x == cell:
            for k, f in lst:
                c[k if k != "invalid" else f"invalid: {str(f)[:50]}"] += 1
    return dict(c)


def analyse_model(reads, sets, model, data=None, db=None):
    ch = hm.CHANNEL[model]
    control = hm.CONTROL_CELL[ch]
    out = {"channel": ch, "control": control, "updates": {}}
    for u, cells in hm.UPDATES.items():
        out["updates"][u] = {"cell": cells[ch], **analyse_update(reads, sets, control, cells[ch], LEVELS[ch], data, db)}
    out["kinds"] = {c: kinds(reads, c) for c in hm.CELLS_OF[ch]}
    return out


def predictions(res):
    """K1 and K2: no model flags update (a) or (b). K3: every model flags update (c). Each for both rules."""
    out = {}
    for k, u, want_flag in (("K1", "a", False), ("K2", "b", False), ("K3", "c", True)):
        for rule in ("first", "revised"):
            per = {m: r["updates"][u][rule]["release"] for m, r in res.items()}
            held = {m: (d == "flag") == want_flag for m, d in per.items()}
            out[f"{k}_{rule}"] = {"decisions": per, "held_per_model": held,
                                  "result": "n/a" if not per else "holds" if all(held.values()) else "fails"}
    return out


def pts(x):
    return "-" if x is None else f"{x:+.1f}"


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def markdown(out):
    lines = [f"# Release tests of harmless updates (R10-20){' — PILOT ANSWERS (dry run; no result)' if out['pilot'] else ''}",
             "", "Exploratory, fixed in the protocol before the run. Change = update − control, in points. "
             f"L = {L}. One look with all requests. Levels: tool channel {100 * LEVELS['tool']:.2f}% (C = 4), form "
             f"channel {100 * LEVELS['form']:.2f}% (C = 6). First rule: the R10-6 code. Revised rule: Appendix I with "
             "the exact sign condition (post hoc in the paper).", ""]
    if out["missing"]:
        lines += [f"Missing folders: {', '.join(out['missing'])}.", ""]
    lines += ["## Decisions", "", "| Model | Update | Set | Pairs | Change | Interval | Up / down | Sign p | First rule | "
              "Revised rule |", "|---|---|---|---:|---:|---|---|---:|---|---|"]
    for m, r in out["models"].items():
        for u, e in r["updates"].items():
            for s in ("open", "specific"):
                x = e["sets"][s]
                iv = "-" if not x["interval"] else f"[{pts(x['interval'][0])}, {pts(x['interval'][1])}]"
                lines.append(f"| {m} | ({u}) {UPDATE_NAMES[u]} | {s} | {x['pairs']} | {pts(x['change'])} | {iv} | "
                             f"{x['up']} / {x['down']} | {x['sign_p']:.4f} | {e['first']['sets'][s]} | "
                             f"{e['revised']['sets'][s]} |")
            lines.append(f"| {m} | ({u}) {UPDATE_NAMES[u]} | **model** | | | | | | **{e['first']['release']}** | "
                         f"**{e['revised']['release']}** |")
    lines += ["", "## Description: form-channel decisions at 98.75% (the level of Table 4)", "",
              "| Model | Update | First rule | Revised rule |", "|---|---|---|---|"]
    for m, r in out["models"].items():
        for u, e in r["updates"].items():
            if "at_98_75" in e:
                lines.append(f"| {m} | ({u}) | {e['at_98_75']['first']['release']} | {e['at_98_75']['revised']['release']} |")
    lines += ["", "## Descriptions: rates of a hotel value (valid reads), the guesthouse set, trade, blocking", "",
              "| Model | Update | Set | Control | Update | Guesthouse-set change |", "|---|---|---|---|---|---|"]
    for m, r in out["models"].items():
        for u, e in r["updates"].items():
            for s in ("open", "specific", "guesthouse"):
                a, b = e["rates"][s]["control"], e["rates"][s]["update"]
                g = e["sets"]["guesthouse"]
                lines.append(f"| {m} | ({u}) | {s} | {pct(a['share'])} ({a['k']}/{a['n']}) | {pct(b['share'])} "
                             f"({b['k']}/{b['n']}) | {pts(g['change']) if s == 'guesthouse' else ''} |")
    lines += ["", "| Model | Update | Trade: wrong removed, correct lost, ratio | Blocking filters, open set: control; update |",
              "|---|---|---|---|"]
    for m, r in out["models"].items():
        for u, e in r["updates"].items():
            t = e["trade"]
            tr = ("not computed" if t is None else f"{t['wrong_removed']:.1f}, {t['correct_lost']:.1f}, "
                  + ("not defined" if not t["defined"] else f"{t['ratio']:.2f}"))
            bo = e.get("blocking_open")
            bl = "-" if not bo else "; ".join(f"{pct(bo[a]['share'])} ({bo[a]['k']}/{bo[a]['n']})" for a in ("t0", "tedit"))
            lines.append(f"| {m} | ({u}) | {tr} | {bl} |")
    lines += ["", "Read kinds per cell:", ""]
    for m, r in out["models"].items():
        lines.append(f"- {m}: " + "; ".join(f"{c} {json.dumps(k)}" for c, k in r["kinds"].items()))
    lines += ["", "## Predictions", "", "| Prediction | Rule | Decisions | Result |", "|---|---|---|---|"]
    for k, v in out["predictions"].items():
        name, rule = k.split("_")
        lines.append(f"| {name} | {rule} | {json.dumps(v['decisions'])} | {v['result']} |")
    return "\n".join(lines) + "\n"


def run(pilot):
    import gold
    import runs
    data, g = runs.context()
    db = gold.hotel_db()
    sets = ra.request_sets(data, g)
    out = {"amendment": "R10-20", "exploratory": True, "pilot": pilot, "L": L, "levels": LEVELS, "draws": DRAWS,
           "seed": SEED, "missing": [], "models": {}}
    for m, folder in MODELS.items():
        reads = load(folder, pilot)
        if reads is None:
            out["missing"].append(folder)
            continue
        out["models"][m] = analyse_model(reads, sets, m, data, db)
    out["predictions"] = predictions(out["models"])
    OUT.mkdir(exist_ok=True)
    stem = "release_test_pilot" if pilot else "release_test"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


def selftest():
    """Fake reads: an update with no change must not flag; a large fall (the rename) must flag; the sign condition
    must turn a flag with few changed requests into a hold; and the parse path of both channels."""
    rng = random.Random(5)
    sets = {"open": [f"O{i}.json" for i in range(448)], "specific": [f"S{i}.json" for i in range(59)],
            "guesthouse": [f"G{i}.json" for i in range(47)]}
    reads_n = {"open": 1, "specific": 10, "guesthouse": 1}
    hit, miss = ("search", {"type": ("hotel",)}), ("search", {"type": None})

    def fake(model, p_open, p_spec, rename_drop, sd=0.15):
        ch = hm.CHANNEL[model]
        cells = hm.CELLS_OF[ch]
        reads = collections.defaultdict(list)
        for s, ids in sets.items():
            for d in ids:
                # a per-request propensity, the same for the control and the harmless updates
                p = min(1.0, max(0.0, rng.gauss(p_open if s != "specific" else p_spec, sd)))
                p = 0.0 if p < 0.05 else 1.0 if p > 0.95 else p
                for _ in range(reads_n[s]):
                    for c in cells:
                        q = p * (1 - rename_drop) if c in ("t1", "p1") else p
                        reads[(d, c)].append(hit if rng.random() < q else miss)
        return reads

    res = {}
    for m in MODELS:
        res[m] = analyse_model(fake(m, 0.15, 0.5, 0.8), sets, m)
        for u in ("a", "b"):
            assert res[m]["updates"][u]["first"]["release"] in ("pass", "hold"), (m, u, res[m]["updates"][u])
        assert res[m]["updates"]["c"]["first"]["release"] == "flag", (m, res[m]["updates"]["c"])
        assert res[m]["updates"]["c"]["revised"]["release"] == "flag", m
        lvl = res[m]["updates"]["a"]["level"]
        assert abs(lvl - (0.9875 if hm.CHANNEL[m] == "tool" else 1 - 0.05 / 6)) < 1e-12
        assert ("at_98_75" in res[m]["updates"]["a"]) == (hm.CHANNEL[m] == "form")
    p = predictions(res)
    assert all(v["result"] == "holds" for v in p.values()), p
    # a deterministic model (no answer changes) gives zero-width intervals: pass
    sure = analyse_model(fake("sol", 0.0, 1.0, 1.0, sd=0.0), sets, "sol")
    assert sure["updates"]["a"]["first"]["release"] == "pass", sure["updates"]["a"]
    # the sign condition: 5 requests up and none down on the specific set, with 1 answer, can meet the first rule only
    e = {"open": {"change": 0.0, "interval": [-1.0, 1.0], "up": 3, "down": 3},
         "specific": {"change": 8.5, "interval": [1.7, 18.6], "up": 5, "down": 0}}
    d = decisions(e, 0.9875)
    assert d["first"]["release"] == "flag" and d["revised"]["release"] == "hold", d
    assert abs(sign_p(5, 0) - 0.0625) < 1e-12 and sign_p(0, 0) == 1.0
    # parse paths: a t1 call maps property_kind / large_property back; a form p1 answer the same; a cut row is invalid
    row = {"type": "succeeded", "stop": "tool_use", "tool_calls": [{"name": "search_hotels", "input": {
        "name": "null", "area": ["north"], "pricerange": None, "stars": None, "property_kind": ["large_property"],
        "parking": None, "internet": None}}]}
    k, f = read_of(row, "t1")
    assert k == "search" and f["type"] == ("hotel",) and f["area"] == ("north",), (k, f)
    row2 = {"type": "succeeded", "stop": "end_turn", "text": json.dumps({"name": None, "area": None, "pricerange": None,
            "stars": None, "property_kind": ["guesthouse", "large_property"], "parking": None, "internet": None})}
    assert read_of(row2, "p1")[1]["type"] == ("guesthouse", "hotel")
    assert read_of({**row2, "stop": "max_tokens"}, "ppar") == ("invalid", "cut")
    assert read_of({"type": "succeeded", "stop": "end_turn", "text": ""}, "tpar")[0] == "none"
    print("selftest passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        run("--pilot" in sys.argv)
