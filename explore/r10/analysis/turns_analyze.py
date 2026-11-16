"""Amendment R10-8: later turns with a simulated traveller. Exploratory.

Inputs: ert_sonnet/conversations.jsonl (arm t0) and ert1_sonnet/conversations.jsonl (arm t1, if it ran), or the
pilot_conversations.jsonl files with --pilot. Outputs: r10/analysis/out/turns.json and turns.md (--pilot: turns_pilot.*).

Definitions (fixed in R10-8 before any call of the amendment):
- A search is a search_hotels call that parses (tools.parse_call). It "shows" the first 5 venues of its result.
- fit: a shown venue meets the brief (briefsearch.fits with goal.hotel.info). fit_shown: a search of the conversation
  shows a fitting venue. first_fit_turn: the agent turn (1 to 4) of the first such search.
- initial failure: the first search of the conversation is a search failure (briefsearch.search_failure).
- guesthouse named or offered: an agent reply (the text blocks of a turn) matches "guest ?houses?" or holds the name of a
  guesthouse of the venue data (gold.norm, as a substring).
- hotel-only at the end: the last search of the conversation keeps hotel and not guesthouse (gold.hides_guesthouse).
- simulator leak: a traveller message names a guesthouse before any agent reply does.
- prior venue (R10-9, a description only): an earlier turn of the prefix names a venue of the hotel data, or the corpus
  metadata of an earlier turn holds a hotel booking. The "fresh" sets leave these prefixes out.
- Post hoc descriptions (added after the t0 run, not in R10-8): relapse = a search shows a fitting venue and a later
  search keeps hotel and not guesthouse; t0 versus t1 = the dialogues complete in both arms, paired (sign test over
  dialogues with different outcomes).
- Units: conversations (one per prefix). 95% intervals: percentile bootstrap over conversations (stats.cluster_bootstrap,
  2,000 draws, seed 20261112; for a difference, each group is resampled apart). Two-sided Fisher exact test for a 2x2
  table. Only conversations with status "complete" enter; the others are counted.
Usage (from explore/): .venv/bin/python -I r10/analysis/turns_analyze.py [--pilot]
"""
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import stats  # noqa: E402
import turns  # noqa: E402

OUT = HERE / "out"
RUNS = {"t0": "ert_sonnet", "t1": "ert1_sonnet"}


def prior_venue(d, names):
    import zforms
    for turn in d["log"][:zforms.prefix_end(d)]:
        flat = gold.norm(turn["text"])
        if any(n in flat for n in names) or ((turn.get("metadata") or {}).get("hotel", {}).get("book", {}).get("booked")):
            return True
    return False


def tupled(fields):
    return {k: tuple(v) if isinstance(v, list) else v for k, v in fields.items()}


def outcomes(rec, data, db, by_name, guest_names, all_names):
    d = data[rec["dialogue"]]
    brief = bs.brief_of(d)
    searches = [s for s in rec["searches"] if s["kind"] == "search"]
    fits = [any(bs.fits(by_name[gold.norm(n)], brief) for n in s["shown"]) for s in searches]
    fit_turns = [s["turn"] for s, f in zip(searches, fits) if f]
    first_fit = fits.index(True) if True in fits else None
    relapse = first_fit is not None and any(gold.hides_guesthouse(tupled(s["fields"]).get("type"))
                                            for s in searches[first_fit + 1:])
    first = tupled(searches[0]["fields"]) if searches else None
    last = tupled(searches[-1]["fields"]) if searches else None

    def names_guest(text):
        flat = gold.norm(text or "")
        return bool(turns.GUEST_WORD.search(text or "")) or any(g in flat for g in guest_names)
    agent_first = next((i for i, r in enumerate(rec["replies"]) if names_guest(r)), None)
    trav_first = next((i for i, t in enumerate(rec["traveller"]) if names_guest(t["text"])), None)
    # Traveller message i follows agent reply i, so a leak is a traveller mention before any agent mention.
    leak = trav_first is not None and (agent_first is None or trav_first < agent_first)
    return {"group": rec["group"], "fit_shown": bool(fit_turns), "first_fit_turn": min(fit_turns) if fit_turns else None,
            "initial_failure": bool(first) and bs.search_failure(first, d, db),
            "guest_offered": agent_first is not None,
            "hotel_only_end": bool(last) and gold.hides_guesthouse(last.get("type")),
            "searches": len(searches), "invalid_calls": len(rec["searches"]) - len(searches),
            "agent_calls": len(rec["calls"]), "leak": leak, "relapse": relapse, "dialogue": rec["dialogue"], "cost": rec["cost"], "prior": prior_venue(d, all_names),
            "no_reply_turns": sum(not r for r in rec["replies"])}


def share(rows, key):
    if not rows:
        return None
    ci = stats.cluster_bootstrap({"a": [(bool(r[key]),) for r in rows]},
                                 lambda g: sum(x[0] for x in g["a"]) / len(g["a"]))
    return {"k": sum(bool(r[key]) for r in rows), "n": len(rows), "share": ci[0], "ci": [ci[1], ci[2]]}


def fisher(a, b, c, d):
    """Two-sided Fisher exact p of the table [[a, b], [c, d]]."""
    n1, n2, k = a + b, c + d, a + c
    total = math.comb(n1 + n2, k)

    def p(x):
        return math.comb(n1, x) * math.comb(n2, k - x) / total
    obs = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, k - n2), min(k, n1) + 1) if p(x) <= obs * (1 + 1e-9)))


def diff(rows_a, rows_b, key):
    """Share in a minus share in b, a bootstrap interval (groups resampled apart) and the Fisher p."""
    if not rows_a or not rows_b:
        return None
    g = {"a": [(bool(r[key]),) for r in rows_a], "b": [(bool(r[key]),) for r in rows_b]}
    ci = stats.cluster_bootstrap(g, lambda s: sum(x[0] for x in s["a"]) / len(s["a"]) - sum(x[0] for x in s["b"]) /
                                 len(s["b"]))
    ka, kb = sum(x[0] for x in g["a"]), sum(x[0] for x in g["b"])
    return {"diff": ci[0], "ci": [ci[1], ci[2]], "fisher_p": fisher(ka, len(rows_a) - ka, kb, len(rows_b) - kb),
            "n": [len(rows_a), len(rows_b)]}


def turn_mean(rows):
    t = [r["first_fit_turn"] for r in rows if r["first_fit_turn"] is not None]
    return sum(t) / len(t) if t else None


def summary(rows):
    out = {"n": len(rows)}
    for key in ("initial_failure", "fit_shown", "guest_offered", "hotel_only_end", "leak", "relapse"):
        out[key] = share(rows, key)
    for r in rows:
        r["never_fit"] = not r["fit_shown"]
    out["never_fit"] = share(rows, "never_fit")
    out["first_fit_turn"] = {str(t): sum(r["first_fit_turn"] == t for r in rows) for t in (1, 2, 3, 4)}
    out["first_fit_turn"]["never"] = sum(r["first_fit_turn"] is None for r in rows)
    out["first_fit_turn_mean"] = turn_mean(rows)
    with_search = [r for r in rows if r["searches"]]
    out["hotel_only_end_of_searching"] = share(with_search, "hotel_only_end")
    for key in ("searches", "agent_calls", "cost"):
        out[f"mean_{key}"] = sum(r[key] for r in rows) / len(rows) if rows else None
    out["no_search"] = sum(not r["searches"] for r in rows)
    out["invalid_calls"] = sum(r["invalid_calls"] for r in rows)
    out["no_reply_turns"] = sum(r["no_reply_turns"] for r in rows)
    return out


def analyse(recs, data, db):
    by_name = {gold.norm(v["name"]): v for v in db}
    guest_names = sorted({gold.norm(v["name"]) for v in db if v["type"] == "guesthouse"}, key=len, reverse=True)
    done = list({r["dialogue"]: r for r in recs if r["status"] == "complete"}.values())  # one record per dialogue
    all_names = sorted({gold.norm(v["name"]) for v in db}, key=len, reverse=True)
    rows = [outcomes(r, data, db, by_name, guest_names, all_names) for r in done]
    f = [r for r in rows if r["group"] == "F"]
    res = {"conversations": len({r["dialogue"] for r in recs}), "complete": len(done),
           "stopped": len({r["dialogue"] for r in recs}) - len(done),
           "cost": sum(r["cost"] for r in recs), "F": summary(f), "R": summary([r for r in rows if r["group"] == "R"])}
    ff, fn = [r for r in f if r["initial_failure"]], [r for r in f if not r["initial_failure"]]
    res["F_initial_failure"], res["F_no_initial_failure"] = summary(ff), summary(fn)
    res["never_fit_failure_minus_no_failure"] = diff(ff, fn, "never_fit")
    res["never_fit_F_minus_R"] = diff(f, [r for r in rows if r["group"] == "R"], "never_fit")
    res["F_fresh"] = summary([r for r in f if not r["prior"]])
    res["F_fresh_initial_failure"] = summary([r for r in ff if not r["prior"]])
    res["R_fresh"] = summary([r for r in rows if r["group"] == "R" and not r["prior"]])
    a, b = turn_mean(ff), turn_mean(fn)
    res["first_fit_turn_delay"] = None if a is None or b is None else a - b
    res["_rows"] = rows
    return res


def paired_arms(r0, r1):
    """Post hoc description: t1 minus t0 on the dialogues complete in both arms, per set."""
    a = {r["dialogue"]: r for r in r0["_rows"]}
    b = {r["dialogue"]: r for r in r1["_rows"]}
    out = {}
    for grp in ("F", "R"):
        both = [d for d in a if d in b and a[d]["group"] == grp]
        for key in ("initial_failure", "never_fit", "hotel_only_end"):
            x0 = sum(bool(a[d][key]) for d in both)
            x1 = sum(bool(b[d][key]) for d in both)
            up = sum(bool(b[d][key]) and not a[d][key] for d in both)
            down = sum(bool(a[d][key]) and not b[d][key] for d in both)
            out[f"{grp}_{key}"] = {"n": len(both), "t0": x0, "t1": x1, "t1_only": up, "t0_only": down,
                                   "sign_p": stats.sign_test(up, down)}
    return out


def val(x):
    return None if x is None else x["share"]


def predictions(res):
    """The predictions of R10-8 for the original tool (arm t0), fixed before any call."""
    r = res.get("t0")
    p = {}
    if not r:
        return p
    ff = r["F_initial_failure"]
    v = val(r["F"]["initial_failure"])
    p["B1"] = {"words": "in F, the first search is a search failure in 10% to 30% of the conversations", "value": v,
               "held": v is not None and 0.10 <= v <= 0.30}
    v = val(ff["fit_shown"])
    p["B2"] = {"words": "in F after an initial failure, a fitting venue is shown by the end in 50% or more", "value": v,
               "held": v is not None and v >= 0.50}
    d = r["never_fit_failure_minus_no_failure"]
    p["B3"] = {"words": "never-fit share: F after an initial failure minus F without one is +10 points or more",
               "value": d and d["diff"], "held": bool(d) and d["diff"] >= 0.10}
    v = val(ff["guest_offered"])
    p["B4"] = {"words": "in F after an initial failure, the agent names or offers a guesthouse in 70% or more",
               "value": v, "held": v is not None and v >= 0.70}
    v = val(ff["hotel_only_end"])
    p["B5"] = {"words": "in F after an initial failure, the last search still keeps the hotel-only filter in 35% or less",
               "value": v, "held": v is not None and v <= 0.35}
    v = r["first_fit_turn_delay"]
    p["B6"] = {"words": "of the F conversations that show a fitting venue, the mean first-fit turn is 0.7 turn or more "
                        "later after an initial failure", "value": v, "held": v is not None and v >= 0.7}
    return p


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def cell(x):
    return "-" if not x else f"{x['k']}/{x['n']} = {pct(x['share'])} [{pct(x['ci'][0])}, {pct(x['ci'][1])}]"


def markdown(res, preds, missing, pilot):
    L = ["## Later turns with a simulated traveller (amendment R10-8)" + (" - pilot only (dry run)" if pilot else ""),
         "", "Exploratory. Agent: Claude Sonnet 5.5 with the search tool, no limit on calls. Traveller: Claude Haiku 5.5 "
         "with the written brief. Four agent turns (the first request and three traveller turns). F: the brief sets no "
         "type and every fitting venue is a guesthouse; R: the brief sets no type and a hotel fits.", ""]
    if missing:
        L += [f"Not run or not complete at this run: {', '.join(missing)}.", ""]
    for arm, r in res.items():
        L += [f"### Arm {arm}: {r['complete']} complete conversations ({r['stopped']} stopped at the cap), cost "
              f"{r['cost']:.2f} USD at list prices", "",
              "| Set | n | Initial failure | Fitting venue shown | Never shown | First fit turn (1/2/3/4/never) | "
              "Guesthouse named | Hotel-only at the end | Relapse (post hoc) | Mean searches | Simulator leaks |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for key, label in (("F", "F"), ("F_initial_failure", "F, initial failure"),
                           ("F_no_initial_failure", "F, no initial failure"), ("R", "R"),
                           ("F_fresh", "F, no prior venue (description)"),
                           ("F_fresh_initial_failure", "F, no prior venue, initial failure (description)"),
                           ("R_fresh", "R, no prior venue (description)")):
            s = r[key]
            if not s["n"]:
                L.append(f"| {label} | 0 | | | | | | | | | |")
                continue
            t = s["first_fit_turn"]
            L.append(f"| {label} | {s['n']} | {cell(s['initial_failure'])} | {cell(s['fit_shown'])} | "
                     f"{cell(s['never_fit'])} | {t['1']}/{t['2']}/{t['3']}/{t['4']}/{t['never']} | "
                     f"{cell(s['guest_offered'])} | {cell(s['hotel_only_end'])} | {cell(s['relapse'])} | "
                     f"{s['mean_searches']:.2f} | "
                     f"{s['leak']['k']} |")
        L.append("")
        for key, label in (("never_fit_failure_minus_no_failure", "Never shown: F initial failure minus F without"),
                           ("never_fit_F_minus_R", "Never shown: F minus R")):
            d = r[key]
            if d:
                L.append(f"- {label}: {100 * d['diff']:+.1f} points [{100 * d['ci'][0]:+.1f}, {100 * d['ci'][1]:+.1f}], "
                         f"Fisher p {d['fisher_p']:.2g} (n {d['n'][0]} and {d['n'][1]})")
        if r["first_fit_turn_delay"] is not None:
            L.append(f"- First fit turn, F initial failure minus F without (conversations that show one): "
                     f"{r['first_fit_turn_delay']:+.2f} turns")
        L.append("")
    if "t0" in res and "t1" in res:
        L += ["### Arm t1 minus arm t0, paired by dialogue (post hoc description)", "",
              "| Set and outcome | Dialogues in both | t0 | t1 | t1 only | t0 only | Sign p |", "|---|---|---|---|---|---|---|"]
        for k, v in paired_arms(res["t0"], res["t1"]).items():
            L.append(f"| {k} | {v['n']} | {v['t0']} | {v['t1']} | {v['t1_only']} | {v['t0_only']} | {v['sign_p']:.2g} |")
        L.append("")
    L += ["### Predictions (R10-8, arm t0)", "", "| # | Words | Value | Held |", "|---|---|---|---|"]
    for k, v in preds.items():
        verdict = "n/a" if v["value"] is None else "held" if v["held"] else "failed"
        L.append(f"| {k} | {v['words']} | {json.dumps(v['value'], default=lambda x: round(x, 4))} | {verdict} |")
    return "\n".join(L) + "\n"


def main():
    import runs
    pilot = "--pilot" in sys.argv
    data, _ = runs.context()
    db = gold.hotel_db()
    res, missing = {}, []
    for arm, name in RUNS.items():
        path = EXPLORE / name / ("pilot_conversations.jsonl" if pilot else "conversations.jsonl")
        if not path.exists():
            missing.append(name)
            continue
        recs = [json.loads(x) for x in path.read_text().splitlines()]
        res[arm] = analyse(recs, data, db)
    preds = predictions(res)
    md = markdown(res, preds, missing, pilot)
    for r in res.values():
        r.pop("_rows", None)
    OUT.mkdir(exist_ok=True)
    stem = "turns_pilot" if pilot else "turns"
    (OUT / f"{stem}.json").write_text(json.dumps({"exploratory": True, "pilot": pilot, "missing": missing, "arms": res,
                                                  "predictions": preds}, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(md)
    print((OUT / f"{stem}.md").read_text())


if __name__ == "__main__":
    main()
