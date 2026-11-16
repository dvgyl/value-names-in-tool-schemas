"""Analysis of amendment R10-23 (prototypes/explore/PROTOCOL.md): the steering runs when the agent can search again.
Exploratory, fixed in the protocol before the run.

Runs: erq1_<model> to erq4_<model> (round k holds the k-th call of each open conversation), models Haiku, Sol and Luna
(steer3.PLAN). Cells: t0 (the original tool), h1 and g1 (the service rewrites of R10-14). The conversations are
rebuilt from the stored rows with steer3.replay, so the analysis sees the same searches and results as the agent.

Definitions (fixed in R10-23 before any call):
- A conversation is valid when it ended with an answer without a call ("complete") or after the 4th call ("calls").
  Other statuses (a failed row, a row cut at the output cap, an answer with two calls, a round not fetched) are missing.
- First search: the search call of the first answer. A first answer without a call scores 0; a first call that does not
  parse is missing for the first-search outcomes (as in R10-14).
- Last search: the last search call of the conversation that parses (a call of the 4th answer counts, although it got no
  result). A conversation without such a call scores 0.
- Exclusion (r10/analysis/steer_search.failure_tests, fixed in R10-15): open set, hotel-only exclusion (primary; the
  call keeps hotel and not guesthouse, a venue fits the brief and no fitting venue is a hotel), guesthouse-only
  exclusion, and either exclusion; guesthouse set, hotel-only exclusion; specific set, guesthouse-only exclusion.
- Widened: a later search of the conversation whose type is not a one-type filter (null, "any", or both types), after a
  first search with a one-type filter (hotel only or guesthouse only).
- Tells: the text that the traveller sees (all text blocks, joined) matches the R10-7 rule (flag.GUEST_OR_LIMITED or a
  type question, flag.asks_type). It is scored for hotel-only exclusions only; for guesthouse-only exclusions the
  analysis gives the counts of the final search only.
- Per prefix: the mean over the valid conversations of the prefix (Luna has 2 answers). A change is cell minus t0, over
  the prefixes with a valid conversation of both, in points. 95% percentile cluster bootstrap over prefixes (2,000
  draws, seed 20261112); exact two-sided sign test over prefixes (ties dropped).
- Repair categories of the last-search change (cell minus t0): "repaired" when the whole 95% interval is inside -3 to
  +3 points; "persists" when the change is +3 points or more and the interval is above 0; "unresolved" otherwise.

Usage (from explore/):
    python3 -I r10/analysis/steer_search3.py            # the fetched raw.jsonl files
    python3 -I r10/analysis/steer_search3.py --selftest # fake answers
Outputs: r10/analysis/out/steer_search3.json and steer_search3.md.
This file is a copy of the project analysis (workshops/steer-search/analyze.py) with the paths of the study folder; the results are the same.
No model call, no network call. It opens no folder whose name starts with "em", no *.sealed file and no key file.
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import flag  # noqa: E402
import gold  # noqa: E402
import stats  # noqa: E402
import steer3  # noqa: E402
from steer_search import failure_tests  # noqa: E402

OUT = HERE / "out"
DRAWS, SEED = 2000, 20261112
LIMIT = 3.0  # points: the repair band of R10-23
VALID = ("complete", "calls")
STEERED = ("h1", "g1")
SETS = ("open", "specific", "guesthouse")
# (set, outcome name) -> the failure_tests key
OUTCOMES = {("open", "hotel-only"): ("open", "hotel-only failure"),
            ("open", "guesthouse-only"): ("open", "guesthouse-only failure"),
            ("open", "either"): ("open", "any failure"),
            ("guesthouse", "hotel-only"): ("guesthouse", "hotel-only failure"),
            ("specific", "guesthouse-only"): ("specific", "guesthouse-only failure")}


def one_type(t):
    """"hotel" or "guesthouse" when the type is a one-type filter, else None."""
    if isinstance(t, tuple):
        if "hotel" in t and "guesthouse" not in t:
            return "hotel"
        if "guesthouse" in t and "hotel" not in t:
            return "guesthouse"
    return None


def tells(text):
    return bool(flag.GUEST_OR_LIMITED.search(text or "")) or flag.asks_type(text or "")


def outcome(conv, set_name, tests):
    """The outcomes of one conversation, or None when it is not valid."""
    if conv.status not in VALID:
        return None
    first = steer3.parse(conv.rows[0], conv.cell)
    searches = [s for s in conv.searches if s["kind"] == "search"]
    last = searches[-1]["fields"] if searches else None
    out = {"d": conv.d, "cell": conv.cell, "read": conv.read, "set": set_name, "status": conv.status,
           "calls": len(conv.rows), "searches": len(conv.searches), "first": {}, "last": {}}
    for (s, name), key in OUTCOMES.items():
        if s != set_name:
            continue
        test = tests[key]
        out["first"][name] = (test(first[1], conv.d) if first[0] == "search" else 0 if first[0] == "none" else None)
        out["last"][name] = test(last, conv.d) if last is not None else 0
    ft = one_type(first[1].get("type")) if first[0] == "search" else None
    later = searches[1:] if first[0] == "search" else searches
    out["first_one_type"] = ft
    out["widened"] = None if ft is None else int(any(one_type(s["fields"].get("type")) is None for s in later))
    out["switched"] = None if ft is None else int(any(one_type(s["fields"].get("type")) not in (None, ft) for s in later))
    out["searched_again"] = int(len(conv.searches) >= 2)
    out["last_one_type"] = one_type(last.get("type")) if last is not None else None
    out["tells"] = int(tells(conv.reply()))
    out["reply_chars"] = len(conv.reply())
    return out


def load(model, source, data, g, db, tests, sets):
    """{"outcomes": [...], "status": Counter} of one model."""
    keys = steer3.keys(model, data, g) if source == "raw" else steer3.pilot_keys(data, g)
    if steer3.rows_of(model, 1, source) is None:
        return None
    convs = steer3.replay(model, steer3.MAX_CALLS, data, g, source, keys, db, strict=False)
    return {"outcomes": [o for c in convs if (o := outcome(c, sets[c.d], tests)) is not None],
            "status": collections.Counter("unfinished" if c.status == "open" else c.status for c in convs)}


def mean(xs):
    return sum(xs) / len(xs)


def per_prefix(outs, cell, set_name, value):
    """{prefix: mean of value(o) over its valid conversations of the cell}, without None values."""
    by = collections.defaultdict(list)
    for o in outs:
        if o["cell"] == cell and o["set"] == set_name:
            v = value(o)
            if v is not None:
                by[o["d"]].append(v)
    return {d: mean(v) for d, v in by.items() if v}


def boot(diffs, level=0.95):
    if not diffs:
        return None, None, None
    return stats.cluster_bootstrap({"all": [(x,) for x in diffs]}, lambda gr: mean([r[0] for r in gr["all"]]),
                                   draws=DRAWS, seed=SEED, level=level)


def change(outs, set_name, cell, value, base=steer3.CONTROL):
    a, b = per_prefix(outs, base, set_name, value), per_prefix(outs, cell, set_name, value)
    diffs = [100 * (b[d] - a[d]) for d in sorted(set(a) & set(b))]
    point, lo, hi = boot(diffs)
    up, down = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    return {"pairs": len(diffs), "change": point, "interval": None if point is None else [lo, hi], "up": up,
            "down": down, "sign_p": stats.sign_test(up, down)}


def rate(outs, set_name, cell, value):
    vals = [v for o in outs if o["cell"] == cell and o["set"] == set_name and (v := value(o)) is not None]
    return {"k": sum(vals), "n": len(vals), "share": mean(vals) if vals else None}


def category(ch):
    """The repair category of a last-search change (R10-23)."""
    if ch["change"] is None:
        return "n/a"
    lo, hi = ch["interval"]
    if -LIMIT <= lo and hi <= LIMIT:
        return "repaired"
    if ch["change"] >= LIMIT and lo > 0:
        return "persists"
    return "unresolved"


def first_v(name):
    return lambda o: o["first"].get(name)


def last_v(name):
    return lambda o: o["last"].get(name)


def drop_v(name):
    """last minus first within a conversation (None when the first outcome is missing)."""
    return lambda o: None if o["first"].get(name) is None else o["last"][name] - o["first"][name]


def analyse_model(outs, status):
    res = {"status": dict(status), "sets": {}}
    for (s, name) in OUTCOMES:
        if not any(o["set"] == s for o in outs):
            continue
        key = f"{s} | {name}"
        e = {"rates": {}, "first_change": {}, "last_change": {}, "drop_change": {}, "category": {}}
        for cell in steer3.CELLS:
            e["rates"][cell] = {"first": rate(outs, s, cell, first_v(name)), "last": rate(outs, s, cell, last_v(name))}
        for cell in STEERED:
            e["first_change"][cell] = change(outs, s, cell, first_v(name))
            e["last_change"][cell] = change(outs, s, cell, last_v(name))
            e["drop_change"][cell] = change(outs, s, cell, drop_v(name))  # (last - first)[cell] - (last - first)[t0]
            e["category"][cell] = category(e["last_change"][cell])
        res["sets"][key] = e
    res["behaviour"] = behaviour(outs)
    return res


def behaviour(outs):
    """Per cell (open set unless named): searches per conversation, re-search, widening, telling, final searches."""
    out = {}
    for cell in steer3.CELLS:
        os_ = [o for o in outs if o["cell"] == cell]
        op = [o for o in os_ if o["set"] == "open"]
        excl1 = [o for o in op if o["first"].get("either") == 1]
        h_first = [o for o in op if o["first"].get("hotel-only") == 1]
        h_last = [o for o in op if o["last"].get("hotel-only") == 1]
        g_last = [o for o in op if o["last"].get("guesthouse-only") == 1]
        one = [o for o in os_ if o["first_one_type"] is not None]
        out[cell] = {
            "conversations": len(os_), "searches": dict(sorted(collections.Counter(o["searches"] for o in os_).items())),
            "status": dict(collections.Counter(o["status"] for o in os_)),
            "searched_again": {"k": sum(o["searched_again"] for o in os_), "n": len(os_)},
            "widened_after_one_type_first": {"k": sum(o["widened"] for o in one), "n": len(one)},
            "switched_type_after_one_type_first": {"k": sum(o["switched"] for o in one), "n": len(one)},
            "open_first_exclusion_either": {"n": len(excl1), "searched_again": sum(o["searched_again"] for o in excl1),
                                            "widened": sum(o["widened"] or 0 for o in excl1),
                                            "last_still_excludes": sum(o["last"]["either"] for o in excl1)},
            "open_first_hotel_only_exclusion": {"n": len(h_first), "tells": sum(o["tells"] for o in h_first)},
            "open_last_hotel_only_exclusion": {"n": len(h_last), "tells": sum(o["tells"] for o in h_last)},
            "open_last_guesthouse_only_exclusion": {"n": len(g_last)},
            "last_one_type": dict(collections.Counter(str(o["last_one_type"]) for o in os_)),
            "reply_chars_mean": mean([o["reply_chars"] for o in os_]) if os_ else None,
        }
    return out


def panel(results_outs):
    """Description: on the open set, per prefix the mean over the models with a valid pair, of the hotel-only and the
    either last-search change (h1 and g1 against t0)."""
    out = {}
    for name in ("hotel-only", "either"):
        for cell in STEERED:
            for which, fn in (("first", first_v), ("last", last_v)):
                per = collections.defaultdict(list)
                for outs in results_outs.values():
                    a = per_prefix(outs, steer3.CONTROL, "open", fn(name))
                    b = per_prefix(outs, cell, "open", fn(name))
                    for d in set(a) & set(b):
                        per[d].append(100 * (b[d] - a[d]))
                diffs = [mean(v) for _, v in sorted(per.items())]
                point, lo, hi = boot(diffs)
                out[f"{name} | {cell} | {which}"] = {"prefixes": len(diffs), "change": point,
                                                     "interval": None if point is None else [lo, hi]}
    return out


def predictions(res):
    """Q1 to Q5 of R10-23."""
    out = {}

    def per_model(key, part, cell, test):
        per = {}
        for m, r in res.items():
            e = r["sets"].get(key)
            if e is None:
                continue
            per[m] = test(e, part, cell)
        return per

    def up5(e, part, cell):
        x = e[part][cell]
        return "n/a" if x["change"] is None else "holds" if x["change"] >= 5 and x["interval"][0] > 0 else "fails"

    def persists(e, part, cell):
        c = e["category"][cell]
        return {"persists": "holds", "repaired": "fails (repaired)", "unresolved": "fails (unresolved)"}.get(c, "n/a")

    out["Q1"] = per_model("open | hotel-only", "first_change", "h1", up5)
    out["Q2"] = per_model("open | either", "first_change", "g1", up5)
    out["Q3"] = per_model("open | hotel-only", "last_change", "h1", persists)
    out["Q4"] = per_model("open | either", "last_change", "g1", persists)
    q5 = {}
    if "haiku" in res and "open | hotel-only" in res["haiku"]["sets"]:
        x = res["haiku"]["sets"]["open | hotel-only"]["drop_change"]["h1"]
        q5["haiku"] = ("n/a" if x["change"] is None else "holds" if x["change"] <= -3 and x["interval"][1] < 0
                       else "fails")
    out["Q5"] = q5
    return out


def pts(x):
    return "-" if x is None else f"{x:+.1f}"


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def iv(x):
    return "-" if not x["interval"] else f"[{pts(x['interval'][0])}, {pts(x['interval'][1])}]"


def markdown(out):
    L = [f"# The steering runs when the agent can search again (R10-23)"
         f"{' — PILOT ANSWERS (dry run; no result)' if out['pilot'] else ''}", "",
         "Exploratory, fixed in the protocol before the run. Changes: cell − t0 in points, paired by prefix, 95% cluster "
         "bootstrap over prefixes. Repair band ±3 points.", ""]
    if out["missing"]:
        L += [f"Missing: {', '.join(out['missing'])}.", ""]
    L += ["## Predictions", "", "| Prediction | Result per model |", "|---|---|"]
    for k, v in out["predictions"].items():
        L.append(f"| {k} | {json.dumps(v)} |")
    L += ["", "## Exclusion: first search and last search", "",
          "| Model | Set and exclusion | Cell | First: rate | First: change [95%] | Last: rate | Last: change [95%] | "
          "Category | (Last − first) − t0 [95%] |", "|---|---|---|---|---|---|---|---|---|"]
    for m, r in out["models"].items():
        for key, e in r["sets"].items():
            t = e["rates"]["t0"]
            L.append(f"| {m} | {key} | t0 | {pct(t['first']['share'])} ({t['first']['k']}/{t['first']['n']}) | | "
                     f"{pct(t['last']['share'])} ({t['last']['k']}/{t['last']['n']}) | | | |")
            for cell in STEERED:
                rr, f, la, dr = e["rates"][cell], e["first_change"][cell], e["last_change"][cell], e["drop_change"][cell]
                L.append(f"| {m} | {key} | {cell} | {pct(rr['first']['share'])} ({rr['first']['k']}/{rr['first']['n']}) "
                         f"| {pts(f['change'])} {iv(f)} | {pct(rr['last']['share'])} ({rr['last']['k']}/"
                         f"{rr['last']['n']}) | {pts(la['change'])} {iv(la)} (up {la['up']}, down {la['down']}) | "
                         f"{e['category'][cell]} | {pts(dr['change'])} {iv(dr)} |")
    L += ["", "## Panel on the open set (description; mean over the models of each prefix)", "",
          "| Exclusion | Cell | Search | Prefixes | Change [95%] |", "|---|---|---|---:|---|"]
    for key, x in out["panel"].items():
        name, cell, which = key.split(" | ")
        L.append(f"| {name} | {cell} | {which} | {x['prefixes']} | {pts(x['change'])} {iv(x)} |")
    L += ["", "## Behaviour (descriptions)", ""]
    for m, r in out["models"].items():
        L.append(f"- {m}: conversation status {json.dumps(r['status'])}")
        for cell, b in r["behaviour"].items():
            L.append(f"  - {cell}: searches per conversation {json.dumps(b['searches'])}; searched again "
                     f"{b['searched_again']['k']}/{b['searched_again']['n']}; widened after a one-type first search "
                     f"{b['widened_after_one_type_first']['k']}/{b['widened_after_one_type_first']['n']}; switched to the "
                     f"other type {b['switched_type_after_one_type_first']['k']}/"
                     f"{b['switched_type_after_one_type_first']['n']}; open set, "
                     f"first-search exclusion (either) {json.dumps(b['open_first_exclusion_either'])}; tells after a "
                     f"first hotel-only exclusion {b['open_first_hotel_only_exclusion']['tells']}/"
                     f"{b['open_first_hotel_only_exclusion']['n']}; tells after a last hotel-only exclusion "
                     f"{b['open_last_hotel_only_exclusion']['tells']}/{b['open_last_hotel_only_exclusion']['n']}; "
                     f"last search is a guesthouse-only exclusion {b['open_last_guesthouse_only_exclusion']['n']}; "
                     f"last type {json.dumps(b['last_one_type'])}")
    if out.get("references"):
        L += ["", "## Stored single-call references (description; other batches, the one-search text)", "",
              "| Model | Run | Cell | Open set, hotel-only | Open set, either |", "|---|---|---|---|---|"]
        for x in out["references"]:
            L.append(f"| {x['model']} | {x['run']} | {x['cell']} | {pct(x['hotel-only']['share'])} "
                     f"({x['hotel-only']['k']}/{x['hotel-only']['n']}) | {pct(x['either']['share'])} "
                     f"({x['either']['k']}/{x['either']['n']}) |")
    return "\n".join(L) + "\n"


REFERENCES = {"haiku": (("ers_haiku", {"t0": "t0", "th": "h1", "tg": "g1"}), ("erm_haiku", {"t0": "t0", "h1": "h1",
                                                                                            "g1": "g1"})),
              "sol": (("era1_sol", {"t0": "t0"}),), "luna": (("era1_luna", {"t0": "t0"}),)}


def references(data, g, db, tests, sets):
    """The first-search exclusion of the stored single-call runs on the open set (description)."""
    import steer
    out = []
    for m, runs_ in REFERENCES.items():
        for run, cmap in runs_:
            assert not run.startswith("em")
            path = EXPLORE / run / "raw.jsonl"
            if not path.exists():
                continue
            vals = collections.defaultdict(lambda: {"hotel-only": [], "either": []})
            for line in path.read_text().splitlines():
                r = json.loads(line)
                _, did, c, _ = r["custom_id"].split("-")
                d = did + ".json"
                if c not in cmap or sets.get(d) != "open" or r.get("type") != "succeeded" or r.get("stop") in flag.CUT:
                    continue
                kind, f = steer.parse_call(r, c) if c in ("th", "tg") else steer3.parse(r, cmap[c])
                if kind == "invalid":
                    continue
                for name in ("hotel-only", "either"):
                    key = OUTCOMES[("open", name)]
                    vals[cmap[c]][name].append(tests[key](f, d) if kind == "search" else 0)
            for cell, v in vals.items():
                out.append({"model": m, "run": run, "cell": cell,
                            **{n: {"k": sum(x), "n": len(x), "share": mean(x) if x else None} for n, x in v.items()}})
    return out


def run(pilot):
    import control
    import runs
    steer3.check_amendment()
    data, g = runs.context()
    db = gold.hotel_db()
    sets = control.set_of(data, g)
    tests = failure_tests(data, db)
    source = "pilot" if pilot else "raw"
    out = {"amendment": "R10-23", "exploratory": True, "pilot": pilot, "limit": LIMIT, "draws": DRAWS, "seed": SEED,
           "missing": [], "models": {}}
    all_outs = {}
    for m in steer3.MODELS:
        x = load(m, source, data, g, db, tests, sets)
        if x is None:
            out["missing"].append(steer3.run_name(m, 1))
            continue
        if x["status"].get("unfinished"):
            out["missing"].append(f"{m}: {x['status']['unfinished']} conversations not finished (a round not fetched)")
        all_outs[m] = x["outcomes"]
        out["models"][m] = analyse_model(x["outcomes"], x["status"])
    out["panel"] = panel(all_outs)
    out["predictions"] = predictions(out["models"])
    out["references"] = [] if pilot else references(data, g, db, tests, sets)
    OUT.mkdir(exist_ok=True)
    stem = "steer_search3_pilot" if pilot else "steer_search3"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


def selftest():
    """Fake answers. (1) The outcome extraction on real prefixes and the real venue data, with fake rows: a hotel-only
    first search that excludes every fitting venue, a widened second search, a final answer. (2) The aggregation and
    the categories on fake outcomes: a world where the exclusion persists and a world where searching again repairs it.
    (3) The predictions in both worlds."""
    import random
    import runs
    data, g = runs.context()
    db = gold.hotel_db()
    import control
    sets = control.set_of(data, g)
    tests = failure_tests(data, db)
    # (1) PMUL3592: open set, only guesthouses fit (a pilot prefix)
    d = "PMUL3592.json"
    fit = [v for v in __import__("briefsearch").brief_fitting(data[d], db)]
    assert fit and all(v["type"] == "guesthouse" for v in fit), d
    area = fit[0]["area"]

    def call_row(i, inp, text=""):
        return {"type": "succeeded", "stop": "tool_use", "text": text, "input_tokens": 1, "output_tokens": 1,
                "tool_calls": [{"id": f"c{i}", "name": "search_hotels", "input": inp}],
                "content": ([{"type": "text", "text": text}] if text else []) +
                [{"type": "tool_use", "id": f"c{i}", "name": "search_hotels", "input": inp}]}

    base = {"name": None, "area": [area], "pricerange": None, "stars": None, "parking": None, "internet": None}
    h1_first = call_row(1, {**base, "accommodation_type": ["hotel"]}, "I'll search hotels first.")
    h1_second = call_row(2, {**base, "accommodation_type": None})
    final = {"type": "succeeded", "stop": "end_turn", "text": "I found guesthouses in that area.", "input_tokens": 1,
             "output_tokens": 1}
    c = steer3.Conv("haiku", d, "h1", 1, zforms_prefix(data, d))
    for r in (h1_first, h1_second, final):
        c.add(r, db)
    assert c.status == "complete" and len(c.searches) == 2, (c.status, c.searches)
    assert c.history[-1]["role"] == "user" and c.history[-1]["content"][0]["type"] == "tool_result"
    shown = json.loads(c.history[2]["content"][0]["content"])
    assert all("accommodation_type" in x and "type" not in x for x in shown["results"]), shown
    o = outcome(c, sets[d], tests)
    assert o["first"]["hotel-only"] == 1 and o["last"]["hotel-only"] == 0 and o["widened"] == 1, o
    assert o["first"]["either"] == 1 and o["last"]["either"] == 0 and o["tells"] == 1
    # the same conversation that stays hotel-only and does not tell; and a 4-call conversation
    c2 = steer3.Conv("haiku", d, "h1", 1, zforms_prefix(data, d))
    c2.add(h1_first, db)
    c2.add({**final, "text": "Here are the hotels I found."}, db)
    o2 = outcome(c2, sets[d], tests)
    assert o2["last"]["hotel-only"] == 1 and o2["widened"] == 0 and o2["tells"] == 0, o2
    c3 = steer3.Conv("haiku", d, "t0", 1, zforms_prefix(data, d))
    t0_call = call_row(1, {**base, "type": ["hotel"]})
    for i in range(4):
        c3.add(t0_call, db)
    assert c3.status == "calls" and len(c3.rows) == 4 and outcome(c3, "open", tests)["last"]["hotel-only"] == 1
    bad = steer3.Conv("haiku", d, "t0", 1, zforms_prefix(data, d))
    bad.add({**final, "stop": "max_tokens"}, db)
    assert outcome(bad, "open", tests) is None
    # an OpenAI conversation keeps the output items and adds a function_call_output item
    co = steer3.Conv("sol", d, "t0", 1, zforms_prefix(data, d))
    orow = {**t0_call, "output_items": [{"type": "function_call", "call_id": "c1", "name": "search_hotels",
                                         "arguments": "{}"}]}
    co.add(orow, db)
    assert co.history[0]["role"] == "system" and co.history[-1]["type"] == "function_call_output", co.history[-2:]

    # (2) fake outcomes
    rng = random.Random(23)
    ids = [f"O{i}.json" for i in range(448)]

    def world(repair, models=("haiku", "sol", "luna")):
        res, outs_by = {}, {}
        for m in models:
            outs = []
            for dd in ids:
                for cell in steer3.CELLS:
                    p_first = 0.03 if cell == "t0" else 0.20
                    x1 = int(rng.random() < p_first)
                    # repair: the last search excludes as often as the last search of t0 (1%); persist: it keeps x1
                    x_last = int(rng.random() < 0.01) if (repair or cell == "t0") else x1
                    outs.append({"d": dd, "cell": cell, "read": 1, "set": "open", "status": "complete", "calls": 2,
                                 "searches": 1 + x1, "first": {"hotel-only": x1, "guesthouse-only": 0, "either": x1},
                                 "last": {"hotel-only": x_last, "guesthouse-only": 0, "either": x_last},
                                 "first_one_type": "hotel" if x1 else None, "widened": (1 - x_last) if x1 else None,
                                 "switched": 0 if x1 else None,
                                 "searched_again": x1, "last_one_type": "hotel" if x_last else None,
                                 "tells": 0, "reply_chars": 10})
            outs_by[m] = outs
            res[m] = analyse_model(outs, collections.Counter(o["status"] for o in outs))
        return res, outs_by

    persist, persist_outs = world(False)
    for m, r in persist.items():
        e = r["sets"]["open | hotel-only"]
        assert e["category"]["h1"] == "persists", (m, e["last_change"]["h1"])
        assert e["first_change"]["h1"]["change"] > 10
    p = predictions(persist)
    assert all(v == "holds" for v in p["Q1"].values()) and all(v == "holds" for v in p["Q3"].values()), p
    assert p["Q5"]["haiku"] == "fails", p["Q5"]
    repaired, rep_outs = world(True)
    for m, r in repaired.items():
        e = r["sets"]["open | hotel-only"]
        assert e["category"]["h1"] == "repaired", (m, e["last_change"]["h1"])
        assert e["drop_change"]["h1"]["change"] < -10
    p2 = predictions(repaired)
    assert all(v == "fails (repaired)" for v in p2["Q3"].values()) and p2["Q5"]["haiku"] == "holds", p2
    pn = panel(persist_outs)
    assert pn["hotel-only | h1 | last"]["prefixes"] == 448 and pn["hotel-only | h1 | last"]["change"] > 10
    assert category({"change": 1.0, "interval": [-1.0, 4.0]}) == "unresolved"
    assert category({"change": None, "interval": None}) == "n/a"
    md = markdown({"pilot": False, "missing": [], "models": persist, "panel": pn, "predictions": p, "references": []})
    assert "Q3" in md and "persists" in md
    print("selftest passed")


def zforms_prefix(data, d):
    import zforms
    return zforms.prefix_text(data[d])


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        run("--pilot" in sys.argv)
