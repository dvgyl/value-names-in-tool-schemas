"""Amendment R10-7: the returned flag. Exploratory.

Inputs: erw_<model>/raw.jsonl and the planned repeats of R10-12 (erw2_<model>, erw3_haiku), or pilot_raw.jsonl with
--pilot, and era2_<model>/raw.jsonl for a description of the same calls under the one-call limit. Outputs:
r10/analysis/out/flag.json and flag.md (--pilot: flag_pilot.*; --read1: flag_read1.*, the first read only).

Definitions (fixed in R10-7 before any call of the amendment):
- Each answer gets one kind by flag.classify: widen, kept, tell, other, neither, invalid. Recovery = widen or tell.
- A unit is a dialogue. A pair is one stage-1 call (dialogue and read) with a valid answer in both arms. The paired
  difference of a dialogue is the mean over its pairs of (flag minus plain), with 1 for a hit and 0 for a miss.
- R10-12: with repeats, the value of a call in an arm is the mean over the valid answers of all its repeats; the pair
  difference is the flag mean minus the plain mean. Rates per arm and answer kinds count every answer.
- 95% intervals: percentile cluster bootstrap over dialogues (stats.cluster_bootstrap, 2,000 draws, seed 20261112).
  Sign test: stats.sign_test over dialogues (ties dropped). No correction for multiple tests (exploratory).
Usage (from explore/): .venv/bin/python -I r10/analysis/flag_analyze.py [--pilot]
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import flag  # noqa: E402
import gold  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
OUTCOMES = {"recovery": ("widen", "tell"), "widen": ("widen",), "tell": ("tell",)}
KINDS = ("widen", "tell", "kept", "other", "neither", "invalid")
REPEATS = {"sonnet": ("erw_sonnet", "erw2_sonnet"), "haiku": ("erw_haiku", "erw2_haiku", "erw3_haiku"),
           "opus": ("erw_opus", "erw2_opus")}


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None


def answers(model, pilot, read1=False):
    """({(dialogue, read): {arm: [kind, ...]}}, folders used); None when the first run is not fetched. One kind per
    repeat (R10-12)."""
    folders = (f"erw_{model}",) if pilot or read1 else REPEATS[model]
    out, used = collections.defaultdict(lambda: collections.defaultdict(list)), []
    for folder in folders:
        rr = rows(EXPLORE / folder / ("pilot_raw.jsonl" if pilot else "raw.jsonl"))
        if rr is None:
            if folder == folders[0]:
                return None, []
            continue
        used.append(folder)
        for r in rr:
            _, did, arm, read = r["custom_id"].split("-")
            out[(did, int(read))][arm].append(flag.classify(r)[0])
    return out, used


def era2_answers(model, db):
    """{(dialogue, read): kind} of the step-2 answers (one-call limit) on the same stage-1 calls."""
    e2 = {r["custom_id"]: r for r in rows(EXPLORE / f"era2_{model}" / "raw.jsonl") or []}
    out = {}
    for row, _, _ in flag.sample(model, db):
        _, did, _, read = row["custom_id"].split("-")
        r2 = e2.get(row["custom_id"].replace(f"era1_{model}-", f"era2_{model}-", 1).replace("-t0-", "-s2-"))
        if r2 is not None:
            out[(did, int(read))] = flag.classify(r2)[0]
    return out


def share_ci(per_dialogue):
    """per_dialogue: [(hits, n)]. (share, low, high) of sum hits / sum n."""
    per_dialogue = [x for x in per_dialogue if x[1]]
    if not per_dialogue:
        return None

    def stat(g):
        n = sum(r[1] for r in g["all"])
        return sum(r[0] for r in g["all"]) / n if n else 0.0
    return stats.cluster_bootstrap({"all": per_dialogue}, stat)


def valid(kinds):
    return [k for k in kinds or [] if k != "invalid"]


def arm_rates(ans, arm, hit):
    per = collections.defaultdict(lambda: [0, 0])
    for (did, _), a in ans.items():
        for k in valid(a.get(arm)):
            per[did][0] += k in hit
            per[did][1] += 1
    return share_ci([tuple(v) for v in per.values()])


def paired(ans, hit):
    """Per call: the mean hit over the valid repeats of flag minus that of plain. "flag_only" and "plain_only" count the
    calls whose difference is above or below 0."""
    per = collections.defaultdict(list)
    only = collections.Counter()
    for (did, _), a in ans.items():
        p, f = valid(a.get("plain")), valid(a.get("flag"))
        if not p or not f:
            continue
        x = sum(k in hit for k in f) / len(f) - sum(k in hit for k in p) / len(p)
        per[did].append(x)
        only["flag_only"] += x > 0
        only["plain_only"] += x < 0
    diffs = [sum(v) / len(v) for v in per.values()]
    if not diffs:
        return None
    ci = stats.cluster_bootstrap({"all": [(x,) for x in diffs]}, lambda g: sum(r[0] for r in g["all"]) / len(g["all"]))
    pos, neg = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    return {"dialogues": len(diffs), "pairs": sum(len(v) for v in per.values()), "mean": ci[0], "ci": [ci[1], ci[2]],
            "higher": pos, "lower": neg, "sign_p": stats.sign_test(pos, neg), **only}


def analyse(model, ans, e2, used):
    res = {"calls": len(ans), "dialogues": len({d for d, _ in ans}), "runs": used}
    res["kinds"] = {arm: dict(collections.Counter(k for a in ans.values() for k in a.get(arm, []))) for arm in flag.ARMS}
    res["rates"] = {o: {arm: arm_rates(ans, arm, hit) for arm in flag.ARMS} for o, hit in OUTCOMES.items()}
    res["flag_minus_plain"] = {o: paired(ans, hit) for o, hit in OUTCOMES.items()}
    c = collections.Counter(e2.values())
    n = sum(v for k, v in c.items() if k != "invalid")
    res["era2"] = {"kinds": dict(c), "recovery": (c["widen"] + c["tell"]) / n if n else None,
                   "widen": c["widen"] / n if n else None}
    return res


def point(res, model, o, arm):
    r = res.get(model, {}).get("rates", {}).get(o, {}).get(arm)
    return r[0] if r else None


def predictions(res):
    """The predictions of R10-7 (fixed before any call), judged on the point values and, where named, the interval."""
    p = {}
    v = {m: point(res, m, "recovery", "flag") for m in flag.MODELS}
    p["W1"] = {"words": "with the flag, recovery is 90% or more for each of Sonnet, Haiku and Opus", "value": v,
               "held": all(x is not None and x >= 0.90 for x in v.values())}
    h = (res.get("haiku") or {}).get("flag_minus_plain", {}).get("recovery")
    p["W2"] = {"words": "Haiku: recovery, flag minus plain, is +15 points or more, and its 95% interval excludes 0",
               "value": h and {"mean": h["mean"], "ci": h["ci"]},
               "held": bool(h) and h["mean"] >= 0.15 and h["ci"][0] > 0}
    v = {m: point(res, m, "recovery", "plain") for m in ("sonnet", "opus")}
    p["W3"] = {"words": "without the flag and without the one-call limit, recovery is 85% or more for Sonnet and Opus",
               "value": v, "held": all(x is not None and x >= 0.85 for x in v.values())}
    s = (res.get("sonnet") or {}).get("flag_minus_plain", {}).get("widen")
    p["W4"] = {"words": "Sonnet: a new search without the hotel-only filter, flag minus plain, is +10 points or more",
               "value": s and s["mean"], "held": bool(s) and s["mean"] >= 0.10}
    o = point(res, "opus", "widen", "flag")
    p["W5"] = {"words": "Opus: with the flag, a new search without the hotel-only filter is 20% or less", "value": o,
               "held": o is not None and o <= 0.20}
    for k in p:
        p[k]["complete"] = all(m in res for m in flag.MODELS)
    return p


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def ci_text(r):
    return "-" if not r else f"{pct(r[0])} [{pct(r[1])}, {pct(r[2])}]"


def markdown(res, preds, missing, pilot, read1=False):
    L = ["## The returned flag (amendment R10-7)" + (" - pilot rows only (dry run)" if pilot else "")
         + (" - first read only (R10-7 as first run)" if read1 else ""), "",
         "Exploratory. Step 2 of experiment A without the one-call limit, on the stage-1 calls whose hotel-only search "
         "found nothing and whose search without the type found a guesthouse. Arms in the same batch: plain (the real "
         "empty result) and flag (the same result and one line that names the guesthouse count).", ""]
    if missing:
        L += [f"Not fetched at this run: {', '.join(missing)}.", ""]
    L += ["Runs used: " + "; ".join(f"{m}: {', '.join(r['runs'])}" for m, r in res.items()) + ".", ""]
    L += ["### Answer kinds", "", "| Model | Arm | Answers | Widen | Tell | Search kept | Other text | Neither | Invalid |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        for arm in flag.ARMS:
            k = r["kinds"][arm]
            L.append(f"| {m} | {arm} | {sum(k.values())} | " + " | ".join(str(k.get(x, 0)) for x in KINDS) + " |")
        e = r["era2"]["kinds"]
        L.append(f"| {m} | era2 (one-call limit, other batch) | {sum(e.values())} | "
                 + " | ".join(str(e.get(x, 0)) for x in KINDS) + " |")
    L += ["", "### Rates per arm (valid answers; 95% interval over dialogues)", "",
          "| Model | Outcome | Plain | Flag | era2 (description) |", "|---|---|---|---|---|"]
    for m, r in res.items():
        for o in OUTCOMES:
            e2 = r["era2"].get(o)
            L.append(f"| {m} | {o} | {ci_text(r['rates'][o]['plain'])} | {ci_text(r['rates'][o]['flag'])} | "
                     f"{pct(e2) if o != 'tell' else '-'} |")
    L += ["", "### Flag minus plain (paired by call; dialogue means; sign test over dialogues)", "",
          "| Model | Outcome | Dialogues | Calls | Mean, points | 95% interval | Higher | Lower | Sign p | Calls flag above | "
          "Calls plain above |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        for o in OUTCOMES:
            c = r["flag_minus_plain"][o]
            if not c:
                continue
            L.append(f"| {m} | {o} | {c['dialogues']} | {c['pairs']} | {100 * c['mean']:+.1f} | "
                     f"[{100 * c['ci'][0]:+.1f}, {100 * c['ci'][1]:+.1f}] | {c['higher']} | {c['lower']} | "
                     f"{c['sign_p']:.2g} | {c['flag_only']} | {c['plain_only']} |")
    L += ["", "### Predictions (R10-7)", "", "| # | Words | Value | Held |", "|---|---|---|---|"]
    for k, v in preds.items():
        L.append(f"| {k} | {v['words']} | {json.dumps(v['value'], default=lambda x: round(x, 4))} | "
                 f"{'held' if v['held'] else 'failed'}{'' if v['complete'] else ' (incomplete)'} |")
    return "\n".join(L) + "\n"


def main():
    pilot, read1 = "--pilot" in sys.argv, "--read1" in sys.argv
    db = gold.hotel_db()
    res, missing = {}, []
    for m in flag.MODELS:
        ans, used = answers(m, pilot, read1)
        if ans is None:
            missing.append(f"erw_{m}")
            continue
        if not pilot and not read1:
            missing += [f for f in REPEATS[m] if f not in used]
        res[m] = analyse(m, ans, era2_answers(m, db), used)
    preds = predictions(res)
    OUT.mkdir(exist_ok=True)
    stem = "flag_pilot" if pilot else "flag_read1" if read1 else "flag"
    (OUT / f"{stem}.json").write_text(json.dumps({"exploratory": True, "pilot": pilot, "missing": missing,
                                                  "models": res, "predictions": preds}, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(res, preds, missing, pilot, read1))
    print((OUT / f"{stem}.md").read_text())


if __name__ == "__main__":
    main()
