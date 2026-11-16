"""Amendment R10-17: the search trade measure of the paper, fixed in advance, on three open models (DeepSeek,
Qwen, gemma) that played no part in the choice of the measure. Exploratory. The dialogues are not new: they are the
807 no-type-brief and 233 hotel-brief dialogues of search_sym.py.

Inputs: ery_<model>/raw.jsonl (cells f0 and verify, reads 1 and 2), MultiWOZ 2.4 and hotel_db.json. For the self-check
it also reads erb_sonnet and erb_haiku (the earlier verifier runs) and out/search_sym.json. Outputs:
r10/analysis/out/trade_prospective.md and .json (--pilot: trade_prospective_pilot.*, a dry run on the pilot rows).

Definitions (fixed in R10-17 before any call):
- Reads: b_analyze.parse_row (valid: succeeded, not cut, forms10.parse accepts it). Planned gate: b_analyze.scored with
  arm "verify" (forms10.b_verify); clear-no gate: arm b_analyze.POSTHOC.
- Visible failure / visible loss: search_sym.per_dialogue, unchanged (first five venues of the answer's own search).
- Search trade ratio: the statistic of search_sym.main, copied without change (`ratio_stat`), with search_sym.WEIGHTS
  (subset 233 / 807, groups 545 / 994) and stats.cluster_bootstrap (2,000 draws, seed 20261112).
- Limit 0.30; verdict categories of Section 6.2 of the paper (`verdict`).
Usage (from explore/): .venv/bin/python -I r10/analysis/trade_prospective.py [--pilot]
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
import b_analyze as B  # noqa: E402
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import search_sym as SS  # noqa: E402
import stats  # noqa: E402
import verify3  # noqa: E402

OUT = HERE / "out"
MODELS = {"deepseek": "ery_deepseek", "qwen": "ery_qwen", "gemma": "ery_gemma"}
GATES = {"verify": "planned gate", B.POSTHOC: "clear-no gate"}
LIMIT = 0.30
INF = float("inf")


def ratio_stat(nt, h, wh, wnt):
    """The statistic of search_sym.main, unchanged: pairs (F0 value, gate value) per dialogue."""
    def stat(gr, wh=wh, wnt=wnt):
        ben = sum(r[0] - r[1] for r in gr["nt"]) / len(gr["nt"])
        cost = sum(r[1] - r[0] for r in gr["h"]) / len(gr["h"])
        return cost * wh / (ben * wnt) if ben > 0 else float("inf")
    point, lo, hi = stats.cluster_bootstrap({"nt": nt, "h": h}, stat)
    return {"ratio": point, "ci": [lo, hi]}


def measure(got, sets, arm, data, db):
    """As the loop body of search_sym.main for one model and arm, plus the net counts in dialogues."""
    f_nt = SS.per_dialogue(got, sets["no_type"], "f0", data, db, False)
    f_h = SS.per_dialogue(got, sets["hotel"], "f0", data, db, True)
    a_nt = SS.per_dialogue(got, sets["no_type"], arm, data, db, False)
    a_h = SS.per_dialogue(got, sets["hotel"], arm, data, db, True)
    nt = [(f_nt[d], a_nt[d]) for d in f_nt if d in a_nt]
    h = [(f_h[d], a_h[d]) for d in f_h if d in a_h]
    out = {"f0": {"visible_failure": sum(f_nt.values()) / len(f_nt), "visible_loss": sum(f_h.values()) / len(f_h)},
           "gate": {"visible_failure": sum(a_nt.values()) / len(a_nt), "visible_loss": sum(a_h.values()) / len(a_h)},
           "paired": [len(nt), len(h)],
           "net_failures_avoided": sum(r[0] - r[1] for r in nt), "net_losses_added": sum(r[1] - r[0] for r in h),
           "failures_ended": sum(max(r[0] - r[1], 0) for r in nt), "failures_caused": sum(max(r[1] - r[0], 0) for r in nt),
           "losses_caused": sum(max(r[1] - r[0], 0) for r in h), "losses_ended": sum(max(r[0] - r[1], 0) for r in h)}
    for wname, (wh, wnt) in SS.WEIGHTS.items():
        out[wname] = ratio_stat(nt, h, wh, wnt)
    out["verdict"] = verdict(out["subset"], out["groups"])
    return out


def verdict(sub, grp):
    """The categories of Section 6.2: under (whole interval under the limit with both weightings), point under with
    both weightings, point under with subset weights only, over at the point value, avoids none."""
    if sub["ratio"] == INF:
        return "avoids none"
    if sub["ci"][1] < LIMIT and grp["ci"][1] < LIMIT:
        return "under (whole interval, both weightings)"
    if sub["ratio"] < LIMIT and grp["ratio"] < LIMIT:
        return "point under, both weightings (interval crosses 0.30)"
    if sub["ratio"] < LIMIT:
        return "point under, subset weights only"
    return "over at the point value"


def load(folder, pilot):
    """{(dialogue id + ".json", arm, read): parsed or None} in the format of b_analyze.load; None when not fetched."""
    path = EXPLORE / folder / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    if not path.exists():
        return None
    got = {}
    for line in path.read_text().splitlines():
        r = json.loads(line)
        d, arm, read = B.split(r["custom_id"])
        got[(d, arm, read)] = B.parse_row(r, arm, None)
    return got


def hotel_only(t):
    return isinstance(t, tuple) and "hotel" in t and "guesthouse" not in t


def descriptions(got, sets, data, db):
    """Table D6 and D5 style counts, and the value count on the two sets (not the paper's trade rule)."""
    out = {"hotel_only_share": {}, "search_failure_807": {}, "verifier_answers_for_hotel_only": {}, "value_count": {}}
    for arm in ("f0", "verify", B.POSTHOC):
        for s, ids in sets.items():
            k = n = 0
            for d in ids:
                for r in B.reads_of(got, d, "verify" if arm != "f0" else "f0"):
                    x = B.scored(got, d, arm, r)
                    if x is not None:
                        n += 1
                        k += hotel_only(x["type"])
            out["hotel_only_share"][f"{arm} | {s}"] = {"k": k, "n": n, "share": k / n if n else None}
        k = n = 0
        for d in sets["no_type"]:
            for r in B.reads_of(got, d, "verify" if arm != "f0" else "f0"):
                x = B.scored(got, d, arm, r)
                if x is not None:
                    n += 1
                    k += bool(bs.search_failure(x, data[d], db))
        out["search_failure_807"][arm] = {"k": k, "n": n, "share": k / n if n else None}
    for s, ids in sets.items():
        c = collections.Counter()
        for d in ids:
            for r in B.reads_of(got, d, "f0"):
                f0, v = got.get((d, "f0", r)), got.get((d, "verify", r))
                if f0 is not None and v is not None and hotel_only(f0["type"]):
                    c[v["answer"]] += 1
        out["verifier_answers_for_hotel_only"][s] = dict(c)
    for arm in ("verify", B.POSTHOC):
        cells = {}
        for s, key in (("no_type", "S1t"), ("hotel", "S2")):
            rows = []
            for d in sets[s]:
                a = [hotel_only(got[(d, "f0", r)]["type"]) for r in B.reads_of(got, d, "f0") if got.get((d, "f0", r))]
                b = [hotel_only(x["type"]) for r in B.reads_of(got, d, "verify")
                     if (x := B.scored(got, d, arm, r)) is not None]
                if a and b:
                    rows.append((sum(a), len(a), sum(b), len(b)))
            cells[key] = rows
        (removed, lost, ratio), lo, hi = stats.trade_interval(cells, {"S1t": 994, "S2": 545}, wrong=("S1t",),
                                                              correct="S2")
        base = sum(r[0] / r[1] for r in cells["S1t"]) / len(cells["S1t"]) * 994
        out["value_count"][arm] = {"removed": removed, "lost": lost, "share_removed": removed / base if base else None,
                                   "ratio": ratio if removed > 0 else None, "ci": [lo, hi]}
    return out


def self_check(data, db, sets):
    """The copied statistic and per_dialogue give the stored search_sym.json ratios of two earlier models."""
    stored = json.loads((OUT / "search_sym.json").read_text())["models"]
    ids = {G: list(runs.context()[1][B.GROUP_KEY[G]]) for G in B.SIZES}
    group_of = {d: G for G, lst in ids.items() for d in lst}
    done = {}
    for m in ("sonnet", "haiku"):
        got, _ = B.load(m, data, group_of)
        for arm in ("verify", B.POSTHOC):
            new = measure(got, sets, arm, data, db)
            old = stored[m][arm]
            for w in SS.WEIGHTS:
                a, b = [new[w]["ratio"], *new[w]["ci"]], [old[w]["ratio"], *old[w]["ci"]]
                assert all(x == y or (math.isinf(x) and math.isinf(y)) for x, y in zip(a, b)), (m, arm, w, a, b)
            done[f"{m} {arm}"] = "equal"
    return done


def fmt(x):
    return "no upper limit" if x == INF else f"{x:.2f}"


def predictions(res):
    def get(m, arm):
        return (res.get(m) or {}).get("gates", {}).get(arm)

    p = {}
    v = {m: (get(m, "verify") or {}).get("subset", {}).get("ratio") for m in MODELS}
    p["V1"] = {"words": "for each model, the planned gate's search trade ratio (subset weights) is under 0.30 at the "
                        "point value", "value": v,
               "held": "n/a" if any(x is None for x in v.values()) else
               "held" if all(x < LIMIT for x in v.values()) else "failed"}
    v = {m: get(m, "verify") and {"subset_ci": get(m, "verify")["subset"]["ci"],
                                  "groups_ci": get(m, "verify")["groups"]["ci"]} for m in MODELS}
    p["V2"] = {"words": "for at least one model, the whole 95% interval of the planned gate's ratio is under 0.30 with "
                        "both weightings", "value": v,
               "held": "n/a" if not any(v.values()) else
               "held" if any(x and x["subset_ci"][1] < LIMIT and x["groups_ci"][1] < LIMIT for x in v.values())
               else "failed"}
    v = {m: ((res.get(m) or {}).get("descriptions", {}).get("value_count", {}).get("verify") or {}).get("ratio", "missing")
         for m in MODELS}
    p["V3"] = {"words": "for each model, the planned gate's value-count ratio on the two sets is above 0.30 at the "
                        "point value, or not defined", "value": v,
               "held": "n/a" if any(x == "missing" for x in v.values()) else
               "held" if all(x is None or x > LIMIT for x in v.values()) else "failed"}
    v = {m: (get(m, B.POSTHOC) or {}).get("subset", {}).get("ratio") for m in MODELS}
    p["V4"] = {"words": "for each model, the clear-no gate's search trade ratio (subset weights) is under 0.30 at the "
                        "point value", "value": v,
               "held": "n/a" if any(x is None for x in v.values()) else
               "held" if all(x < LIMIT for x in v.values()) else "failed"}
    return p


def markdown(out):
    L = ["## The search trade measure on three open models (amendment R10-17)" +
         (" - pilot rows only (dry run; no result)" if out["pilot"] else ""), "",
         "Exploratory. A test fixed in advance on new models, not on new dialogues: the 807 no-type-brief and 233 "
         "hotel-brief dialogues are the development dialogues of the paper's search-trade analysis, and the measure "
         "was chosen after the answers of six other models on them. DeepSeek, Qwen and gemma (round-9 DeepInfra "
         "settings) answered the original form (F0) and the verifier, 2 reads per dialogue. Ratio: visible losses "
         "added per visible failure avoided; 95% cluster bootstrap interval (2,000 draws, seed 20261112). Limit 0.30.",
         "", f"Self-check (the copied code gives the stored search_sym.json values): {json.dumps(out['self_check'])}.", ""]
    if out["missing"]:
        L += [f"Not fetched at this run: {', '.join(out['missing'])}.", ""]
    L += ["### Table 3 for the new models", "", "| Model | Gate | Visible failure (%) | Visible loss (%) | Net avoided / "
          "added (dialogues, mean of reads) | Ratio, subset weights [95%] | Ratio, group weights [95%] | Verdict |",
          "|---|---|---|---|---|---|---|---|"]
    for m, r in out["models"].items():
        for arm, e in r["gates"].items():
            s, g = e["subset"], e["groups"]
            L.append(f"| {m} | {GATES[arm]} | {100 * e['f0']['visible_failure']:.1f} -> "
                     f"{100 * e['gate']['visible_failure']:.1f} | {100 * e['f0']['visible_loss']:.1f} -> "
                     f"{100 * e['gate']['visible_loss']:.1f} | {e['net_failures_avoided']:.1f} / "
                     f"{e['net_losses_added']:.1f} | {fmt(s['ratio']) if s['ratio'] != INF else 'avoids none'} "
                     f"[{fmt(s['ci'][0])}, {fmt(s['ci'][1])}] | "
                     f"{fmt(g['ratio']) if g['ratio'] != INF else 'avoids none'} [{fmt(g['ci'][0])}, {fmt(g['ci'][1])}]"
                     f" | {e['verdict']} |")
    L += ["", "### Descriptions", "", "| Model | Form | Hotel-only, 807 no-type | Hotel-only, 233 hotel | Search "
          "failure, 807 |", "|---|---|---|---|---|"]
    for m, r in out["models"].items():
        d = r["descriptions"]
        for arm, name in (("f0", "F0"), ("verify", "planned gate"), (B.POSTHOC, "clear-no gate")):
            a, b, c = d["hotel_only_share"][f"{arm} | no_type"], d["hotel_only_share"][f"{arm} | hotel"], \
                d["search_failure_807"][arm]
            L.append(f"| {m} | {name} | {100 * a['share']:.1f}% ({a['k']}/{a['n']}) | {100 * b['share']:.1f}% "
                     f"({b['k']}/{b['n']}) | {100 * c['share']:.1f}% ({c['k']}/{c['n']}) |")
    L += ["", "Verifier answers for the hotel-only F0 values: " + "; ".join(
        f"{m}: " + ", ".join(f"{s} {json.dumps(v)}" for s, v in r["descriptions"]["verifier_answers_for_hotel_only"].items())
        for m, r in out["models"].items()), "",
          "Value count on the two sets (not the paper's trade rule, which also needs the guesthouse group; weights 994 "
          "and 545):", "", "| Model | Gate | Removed (share of F0 hotel-only, no-type) | Lost | Ratio [95%] |",
          "|---|---|---|---|---|"]
    for m, r in out["models"].items():
        for arm, e in r["descriptions"]["value_count"].items():
            ratio = "not defined" if e["ratio"] is None else f"{e['ratio']:.2f} [{fmt(e['ci'][0])}, {fmt(e['ci'][1])}]"
            share = "-" if e["share_removed"] is None else f"{100 * e['share_removed']:.1f}%"
            L.append(f"| {m} | {GATES[arm]} | {e['removed']:.1f} ({share}) | {e['lost']:.1f} | {ratio} |")
    L += ["", "### Predictions (R10-17)", "", "| # | Words | Value | Result |", "|---|---|---|---|"]
    for k, v in out["predictions"].items():
        L.append(f"| {k} | {v['words']} | {json.dumps(v['value'], default=lambda x: round(x, 3))} | {v['held']} |")
    return "\n".join(L) + "\n"


def main():
    pilot = "--pilot" in sys.argv
    verify3.check_amendment()
    data, g = runs.context()
    db = gold.hotel_db()
    sets = verify3.sets(data, g)
    out = {"amendment": "R10-17", "exploratory": True, "pilot": pilot, "limit": LIMIT, "weights": SS.WEIGHTS,
           "sizes": verify3.SIZES, "self_check": self_check(data, db, sets), "missing": [], "models": {}}
    for m, folder in MODELS.items():
        got = load(folder, pilot)
        if got is None:
            out["missing"].append(folder)
            continue
        try:
            out["models"][m] = {"gates": {arm: measure(got, sets, arm, data, db) for arm in GATES},
                                "descriptions": descriptions(got, sets, data, db)}
        except ZeroDivisionError:  # a dry run on the pilot rows can leave a set with no pair
            out["missing"].append(f"{folder} (no pair in a set)")
    out["predictions"] = predictions(out["models"])
    OUT.mkdir(exist_ok=True)
    stem = "trade_prospective_pilot" if pilot else "trade_prospective"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1, default=lambda x: "inf" if x == INF else float(x)))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


if __name__ == "__main__":
    main()
