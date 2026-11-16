"""Analysis of amendment R10-22 (prototypes/explore/PROTOCOL.md): two more release tests of harmless updates on the
tool channel, with the rule of R10-20. Exploratory.

Runs: erk2_sol and erk2_luna (tool calls; cells t0 = a fresh control, tord = update (d) the field order, tpar2 =
update (e) the second paraphrase). The 554 first requests of experiment A: open set 448 (1 answer per arm), specific
set 59 (10 answers per arm), guesthouse set 47 (1 answer per arm; description only).

Definitions (fixed in R10-22 before any call; the code of analyze.py, the R10-20 analysis):
- A read is invalid (missing) when its row did not succeed, stopped at the output cap, or harmless2.parse_row gives
  "invalid". A valid read scores 1 when its search call holds hotel in type; a valid read without a search call
  scores 0.
- Per request: the update minus the control, over the requests with a valid read of both. Up and down: the requests
  whose change is above or below 0.
- One release is one update on the models of one output channel: C = models x sets x looks, with the models that run
  the update in harmless2.PLAN (2 models: C = 4, 98.75%; after the cut of update (d) on Sol: C = 2, 97.5%).
  Percentile cluster bootstrap over requests (2,000 draws, seed 20261112). L = 5 points. One look with all requests.
- First rule: decide and release of R10-6 (release_analyze.py). Revised rule: Appendix I with the exact sign condition.
- Descriptions: rates per arm and set; the guesthouse set; the trade ratio and the blocking filters on the open set;
  read kinds; the fresh control against the R10-20 control of the same model (erk_<model> t0; another batch).

Usage (from explore/):
    python3 -I r10/analysis/release_test2.py            # the fetched raw.jsonl files
    python3 -I r10/analysis/release_test2.py --selftest # fake answers
Outputs: r10/analysis/out/release_test2.json and release_test2.md.
This file is a copy of the project analysis (workshops/release-test/analyze2.py) with the paths of the study folder; the results are the same.
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
import release_test as a20  # noqa: E402  (the R10-20 analysis: the rules, set_change, analyse_update; its main does not run)
import harmless2 as h2  # noqa: E402
import release_analyze as ra  # noqa: E402

OUT = HERE / "out"
CUT = a20.CUT
MODEL_OF = {run: model for run, model in h2.MODEL_OF.items()}
FOLDER_OF = {model: run for run, model in MODEL_OF.items()}
R20_CONTROL = {"sol": "erk_sol", "luna": "erk_luna"}  # the R10-20 control t0 of the same model (description)


def levels():
    """{update: interval level}: C = (models that run the update in harmless2.PLAN) x 2 sets x 1 look."""
    out = {}
    for u, cell in h2.UPDATES.items():
        n = sum(cell in cells for cells in h2.PLAN.values())
        out[u] = a20.interval_level(n, a20.SETS, a20.LOOKS) if n else None
    return out


def read_of(row, cell):
    """(kind, fields or reason): kind is "search", "none" or "invalid"."""
    if row.get("type", "succeeded") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in CUT:
        return "invalid", "cut"
    kind, val = h2.parse_row(row, cell)
    if kind not in ("search", "none"):
        return "invalid", val if kind == "invalid" else f"kind {kind}"
    return kind, val


def load(folder, pilot, cells=None, rename=None):
    """{(dialogue id, cell): [(kind, fields or reason), ...]}, or None when the file does not exist. `cells` keeps only
    these cells; `rename` maps a cell to another name (the R10-20 control)."""
    assert not folder.startswith("em"), f"refused: {folder}"
    path = EXPLORE / folder / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    if not path.exists():
        return None
    reads = collections.defaultdict(list)
    for line in path.read_text().splitlines():
        r = json.loads(line)
        _, d, cell, _ = r["custom_id"].split("-")
        if cells is not None and cell not in cells:
            continue
        reads[(d + ".json", (rename or {}).get(cell, cell))].append(read_of(r, cell))
    return reads


def analyse_model(reads, sets, run, data=None, db=None):
    lv = levels()
    out = {"control": h2.CONTROL, "updates": {}}
    for u, cell in h2.UPDATES.items():
        if cell in h2.PLAN[run]:
            out["updates"][u] = {"cell": cell, **a20.analyse_update(reads, sets, h2.CONTROL, cell, lv[u], data, db)}
    out["kinds"] = {c: a20.kinds(reads, c) for c in h2.PLAN[run]}
    return out


def control_drift(reads, sets):
    """The fresh control t0 against the R10-20 control t0_r20 (another batch; description, no decision)."""
    return {s: a20.set_change(reads, sets[s], "t0_r20", h2.CONTROL, a20.TABLE4_LEVEL)[0] for s in sets}


def predictions(res):
    """K4 and K5: no model flags update (d) or (e). Each for both rules."""
    out = {}
    for k, u in (("K4", "d"), ("K5", "e")):
        for rule in ("first", "revised"):
            per = {m: r["updates"][u][rule]["release"] for m, r in res.items() if u in r["updates"]}
            held = {m: d != "flag" for m, d in per.items()}
            out[f"{k}_{rule}"] = {"decisions": per, "held_per_model": held,
                                  "result": "n/a" if not per else "holds" if all(held.values()) else "fails"}
    return out


pts, pct = a20.pts, a20.pct


def markdown(out):
    lv = out["levels"]
    lines = [f"# Release tests of a field-order change and a second paraphrase (R10-22)"
             f"{' — PILOT ANSWERS (dry run; no result)' if out['pilot'] else ''}", "",
             "Exploratory, fixed in the protocol before the run. Change = update − control (a fresh control in the same "
             f"batch), in points. L = {a20.L}. One look with all requests. Levels: "
             + ", ".join(f"({u}) {h2.UPDATE_NAMES[u]} {100 * x:.2f}%" for u, x in lv.items() if x)
             + ". First rule: the R10-6 code. Revised rule: Appendix I with the exact sign condition (post hoc in the "
             "paper).", ""]
    if out["missing"]:
        lines += [f"Missing folders: {', '.join(out['missing'])}.", ""]
    lines += ["## Decisions", "", "| Model | Update | Set | Pairs | Change | Interval | Up / down | Sign p | First rule | "
              "Revised rule |", "|---|---|---|---:|---:|---|---|---:|---|---|"]
    for m, r in out["models"].items():
        for u, e in r["updates"].items():
            for s in ("open", "specific"):
                x = e["sets"][s]
                iv = "-" if not x["interval"] else f"[{pts(x['interval'][0])}, {pts(x['interval'][1])}]"
                lines.append(f"| {m} | ({u}) {h2.UPDATE_NAMES[u]} | {s} | {x['pairs']} | {pts(x['change'])} | {iv} | "
                             f"{x['up']} / {x['down']} | {x['sign_p']:.4f} | {e['first']['sets'][s]} | "
                             f"{e['revised']['sets'][s]} |")
            lines.append(f"| {m} | ({u}) {h2.UPDATE_NAMES[u]} | **model** | | | | | | **{e['first']['release']}** | "
                         f"**{e['revised']['release']}** |")
    lines += ["", "## Predictions", "", "| Prediction | Rule | Decisions | Result |", "|---|---|---|---|"]
    for k, v in out["predictions"].items():
        name, rule = k.split("_")
        lines.append(f"| {name} | {rule} | {json.dumps(v['decisions'])} | {v['result']} |")
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
    lines += ["", "Fresh control against the R10-20 control of the same model (another batch; 98.75% interval; "
              "description):", "", "| Model | Set | Pairs | Change | Interval | Up / down |", "|---|---|---:|---:|---|---|"]
    for m, drift in out["control_drift"].items():
        for s, x in drift.items():
            iv = "-" if not x["interval"] else f"[{pts(x['interval'][0])}, {pts(x['interval'][1])}]"
            lines.append(f"| {m} | {s} | {x['pairs']} | {pts(x['change'])} | {iv} | {x['up']} / {x['down']} |")
    lines += ["", "Read kinds per cell:", ""]
    for m, r in out["models"].items():
        lines.append(f"- {m}: " + "; ".join(f"{c} {json.dumps(k)}" for c, k in r["kinds"].items()))
    return "\n".join(lines) + "\n"


def run(pilot):
    import gold
    import runs
    h2.check_amendment()
    data, g = runs.context()
    db = gold.hotel_db()
    sets = ra.request_sets(data, g)
    out = {"amendment": "R10-22", "exploratory": True, "pilot": pilot, "L": a20.L, "levels": levels(),
           "draws": a20.DRAWS, "seed": a20.SEED, "missing": [], "models": {}, "control_drift": {}}
    for run_name, m in MODEL_OF.items():
        reads = load(run_name, pilot)
        if reads is None:
            out["missing"].append(run_name)
            continue
        out["models"][m] = analyse_model(reads, sets, run_name, data, db)
        old = load(R20_CONTROL[m], False, cells={"t0"}, rename={"t0": "t0_r20"})
        if old is None:
            out["missing"].append(f"{R20_CONTROL[m]} (R10-20 control; description only)")
        else:
            out["control_drift"][m] = control_drift({**old, **reads}, sets)
    out["predictions"] = predictions(out["models"])
    OUT.mkdir(exist_ok=True)
    stem = "release_test2_pilot" if pilot else "release_test2"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


def selftest():
    """Fake reads: harmless updates must not flag; a large fall of update (e) must flag; the levels follow
    harmless2.PLAN (also after the cut of update (d) on Sol); the parse path of the two update cells."""
    rng = random.Random(22)
    sets = {"open": [f"O{i}.json" for i in range(448)], "specific": [f"S{i}.json" for i in range(59)],
            "guesthouse": [f"G{i}.json" for i in range(47)]}
    reads_n = {"open": 1, "specific": 10, "guesthouse": 1}
    hit, miss = ("search", {"type": ("hotel",)}), ("search", {"type": None})

    def fake(run, p_open, p_spec, drop=None, sd=0.15):
        reads = collections.defaultdict(list)
        for s, ids in sets.items():
            for d in ids:
                p = min(1.0, max(0.0, rng.gauss(p_open if s != "specific" else p_spec, sd)))
                p = 0.0 if p < 0.05 else 1.0 if p > 0.95 else p
                for _ in range(reads_n[s]):
                    for c in (*h2.PLAN[run], "t0_r20"):
                        q = p * (1 - drop[1]) if drop and c == drop[0] else p
                        reads[(d, c)].append(hit if rng.random() < q else miss)
        return reads

    lv = levels()
    assert abs(lv["d"] - 0.9875) < 1e-12 and abs(lv["e"] - 0.9875) < 1e-12, lv
    res = {}
    for run in h2.RUNS:
        m = MODEL_OF[run]
        reads = fake(run, 0.25, 0.6)
        res[m] = analyse_model(reads, sets, run)
        for u in ("d", "e"):
            assert res[m]["updates"][u]["first"]["release"] in ("pass", "hold"), (m, u, res[m]["updates"][u])
            assert res[m]["updates"][u]["revised"]["release"] in ("pass", "hold"), (m, u)
            assert "at_98_75" not in res[m]["updates"][u]
        drift = control_drift(reads, sets)
        assert drift["open"]["pairs"] == 448 and drift["specific"]["pairs"] == 59
    p = predictions(res)
    assert all(v["result"] == "holds" for v in p.values()), p
    # a paraphrase that removes most hotel values must flag under both rules, and K5 then fails
    bad = analyse_model(fake("erk2_sol", 0.25, 0.6, drop=("tpar2", 0.8)), sets, "erk2_sol")
    assert bad["updates"]["e"]["first"]["release"] == "flag" and bad["updates"]["e"]["revised"]["release"] == "flag"
    p2 = predictions({"sol": bad, "luna": res["luna"]})
    assert p2["K5_first"]["result"] == "fails" and p2["K4_first"]["result"] == "holds", p2
    md = markdown({"pilot": False, "levels": lv, "missing": [], "models": res, "predictions": p,
                   "control_drift": {"sol": drift}})
    assert "(d) field order" in md and "K5" in md
    # the cut of update (d) on Sol: (d) has one model (97.5%), and the Sol result has no update (d)
    saved = dict(h2.PLAN)
    try:
        h2.PLAN["erk2_sol"] = ("t0", "tpar2")
        lv2 = levels()
        assert abs(lv2["d"] - 0.975) < 1e-12 and abs(lv2["e"] - 0.9875) < 1e-12, lv2
        cut = analyse_model(fake("erk2_sol", 0.25, 0.6), sets, "erk2_sol")
        assert set(cut["updates"]) == {"e"}
        assert predictions({"sol": cut, "luna": res["luna"]})["K4_first"]["decisions"] == \
            {"luna": res["luna"]["updates"]["d"]["first"]["release"]}
    finally:
        h2.PLAN.clear()
        h2.PLAN.update(saved)
    # parse paths: both update cells use the t0 names and values; a cut row is invalid; a text answer is "none"
    row = {"type": "succeeded", "stop": "end_turn", "tool_calls": [{"name": "search_hotels", "input": {
        "area": ["north"], "internet": None, "name": "null", "parking": None, "pricerange": None, "stars": None,
        "type": ["hotel"]}}]}
    for cell in ("tord", "tpar2", "t0"):
        k, f = read_of(row, cell)
        assert k == "search" and f["type"] == ("hotel",) and f["area"] == ("north",) and f["name"] is None, (cell, f)
    assert read_of({**row, "stop": "max_output_tokens"}, "tord") == ("invalid", "cut")
    assert read_of({"type": "succeeded", "stop": "end_turn", "text": "Which area?"}, "tpar2")[0] == "none"
    assert read_of({**row, "tool_calls": row["tool_calls"] * 2}, "tpar2")[0] == "invalid"
    print("selftest passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        run("--pilot" in sys.argv)
