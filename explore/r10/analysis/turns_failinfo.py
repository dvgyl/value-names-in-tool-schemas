"""Later turns (amendment R10-8): sensitivity to briefs with a failing first choice. Post hoc, no model call.

The outcome of R10-8 stays the primary result. This script reads only the stored conversations of both arms
(ert_sonnet: original tool, t0; ert1_sonnet: renamed tool, t1) and uses the definitions of turns_analyze.py without change
(turns_analyze.outcomes, turns_analyze.diff: percentile bootstrap over conversations, groups resampled apart, 2,000 draws,
seed 20261112; two-sided Fisher exact test).

- first choice: the hotel goal of the corpus brief holds a fail_info (the first choice, which the corpus marks as
  failing) that differs from its info (the final requirements). The fit rule uses info only. For each such brief, the
  script also counts the venues of our venue data that meet the first choice (briefsearch.fits with fail_info), and the
  hotels among them.
- kind of first choice: "name" when fail_info differs from info only in the venue name (a named venue whose booking
  fails), else "requirements".
- Tables: for each brief group (F: only guesthouses fit the final requirements; R: a hotel fits) and arm, the
  conversations, initial failures and "never held a fitting venue", split by first choice yes / no.
- The comparison of Section 5.2 (F, initial failure against none, never held) on the conversations without a first
  choice, and on those with one.
- For the never-held conversations with a first choice: a word check of whether the traveller turns name the final
  value of each slot where the first choice and the final requirements differ, and whether an agent search used it.
  The paper reports the author's reading of these traveller turns; the word check is an aid, not a rule.
Outputs: r10/analysis/out/turns_failinfo.json and turns_failinfo.md.
Usage (from explore/): .venv/bin/python -I r10/analysis/turns_failinfo.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import turns_analyze as ta  # noqa: E402  (it adds r10/ to the path)

import briefsearch as bs  # noqa: E402
import gold  # noqa: E402

OUT = HERE / "out"
WORDS = {"stars": lambda v: [f"{v} star", f"{v}-star", f"{v} stars"],
         "parking": lambda v: ["parking"], "internet": lambda v: ["internet", "wifi", "wi-fi"]}


def load(name):
    path = ta.EXPLORE / name / "conversations.jsonl"
    recs = [json.loads(x) for x in path.read_text().splitlines()]
    return {r["dialogue"]: r for r in recs if r["status"] == "complete"}


def first_choice(d):
    h = d["goal"]["hotel"]
    return bool(h.get("fail_info")) and h.get("fail_info") != h.get("info")


def kind(d):
    h = d["goal"]["hotel"]
    fail, info = h.get("fail_info") or {}, h.get("info") or {}
    diff = {k for k in set(fail) | set(info) if fail.get(k) != info.get(k)}
    return "name" if diff == {"name"} else "requirements"


def count(rows):
    return {"n": len(rows), "initial_failure": sum(r["initial_failure"] for r in rows),
            "never_fit": sum(not r["fit_shown"] for r in rows)}


def reached(rec, d):
    """Per slot where fail_info and info differ: does a traveller turn name the final value; does a search use it."""
    h = d["goal"]["hotel"]
    fail, info = h.get("fail_info") or {}, h.get("info") or {}
    trav = " ".join(t["text"] for t in rec["traveller"]).lower()
    out = {}
    for slot in sorted(set(fail) | set(info)):
        if fail.get(slot) == info.get(slot) or slot not in info:
            continue
        val = str(info[slot]).lower()
        words = WORDS.get(slot, lambda v: [v])(val)
        searched = any(val in {str(x).lower() for x in (s["fields"].get(slot) or [])}
                       for s in rec["searches"] if s["kind"] == "search" and isinstance(s["fields"].get(slot), list))
        out[slot] = {"first": fail.get(slot), "final": info[slot], "named_by_traveller": any(w in trav for w in words),
                     "searched": searched}
    return out


def main():
    import runs
    data, _ = runs.context()
    db = gold.hotel_db()
    by_name = {gold.norm(v["name"]): v for v in db}
    guest = sorted({gold.norm(v["name"]) for v in db if v["type"] == "guesthouse"}, key=len, reverse=True)
    alln = sorted({gold.norm(v["name"]) for v in db}, key=len, reverse=True)
    res = {"post_hoc": True, "arms": {}}
    L = ["## Later turns: briefs with a failing first choice (post hoc sensitivity analysis)", "",
         "First choice: the corpus brief holds a fail_info that differs from its info. The fit rule uses info only.", ""]
    for arm, name in ta.RUNS.items():
        recs = load(name)
        rows = [ta.outcomes(r, data, db, by_name, guest, alln) for r in recs.values()]
        for r in rows:
            r["never_fit"] = not r["fit_shown"]
            r["first_choice"] = first_choice(data[r["dialogue"]])
        a = {"table": {}}
        for grp in ("F", "R"):
            g = [r for r in rows if r["group"] == grp]
            a["table"][grp] = {"all": count(g), "first_choice": count([r for r in g if r["first_choice"]]),
                               "first_choice_name": count([r for r in g if r["first_choice"] and kind(data[r["dialogue"]]) == "name"]),
                               "first_choice_requirements": count([r for r in g if r["first_choice"]
                                                                   and kind(data[r["dialogue"]]) == "requirements"]),
                               "no_first_choice": count([r for r in g if not r["first_choice"]])}
        f = [r for r in rows if r["group"] == "F"]
        for key, keep in (("no_first_choice", False), ("first_choice", True)):
            sub = [r for r in f if r["first_choice"] == keep]
            ff, fn = [r for r in sub if r["initial_failure"]], [r for r in sub if not r["initial_failure"]]
            d = ta.diff(ff, fn, "never_fit")
            a[f"F_{key}_failure_vs_none"] = {"failure": count(ff), "none": count(fn), "diff": d}
        nf = []
        for r in rows:
            if r["never_fit"] and r["first_choice"]:
                d = data[r["dialogue"]]
                fail = d["goal"]["hotel"]["fail_info"]
                fits_first = [v for v in db if bs.fits(v, fail)]
                nf.append({"dialogue": r["dialogue"], "group": r["group"], "initial_failure": r["initial_failure"],
                           "kind": kind(d),
                           "first_choice_venues": len(fits_first),
                           "first_choice_hotels": sum(v["type"] == "hotel" for v in fits_first),
                           "slots": reached(recs[r["dialogue"]], d)})
        a["never_fit_first_choice"] = nf
        a["first_choice_venue_counts"] = {grp: [len([v for v in db if bs.fits(v, data[r["dialogue"]]["goal"]["hotel"]["fail_info"])])
                                                for r in rows if r["group"] == grp and r["first_choice"]] for grp in ("F", "R")}
        res["arms"][arm] = a
        L += [f"### Arm {arm} ({name})", "",
              "| Group | First choice | Conversations | Initial failure | Never held |", "|---|---|---|---|---|"]
        for grp, t in a["table"].items():
            for key in ("all", "first_choice", "first_choice_name", "first_choice_requirements", "no_first_choice"):
                c = t[key]
                L.append(f"| {grp} | {key} | {c['n']} | {c['initial_failure']} | {c['never_fit']} |")
        L.append("")
        for key in ("no_first_choice", "first_choice"):
            x = a[f"F_{key}_failure_vs_none"]
            d = x["diff"]
            txt = "-" if not d else (f"{100 * d['diff']:+.1f} points [{100 * d['ci'][0]:+.1f}, {100 * d['ci'][1]:+.1f}], "
                                     f"Fisher p {d['fisher_p']:.2g}")
            L.append(f"- F, {key}: never held after an initial failure {x['failure']['never_fit']}/{x['failure']['n']}, "
                     f"without one {x['none']['never_fit']}/{x['none']['n']}; difference {txt}")
        fc = a["first_choice_venue_counts"]
        L += ["", f"- Venues of our data that meet the first choice (briefs with a first choice): F {sorted(fc['F'])}; "
              f"R {sorted(fc['R'])}", "",
              "| Never held, first choice | Group | Initial failure | Kind | Venues meeting the first choice (hotels) | "
              "Slot: first -> final; traveller names final; a search uses final |", "|---|---|---|---|---|---|"]
        for x in nf:
            s = "; ".join(f"{k}: {v['first']} -> {v['final']}; {v['named_by_traveller']}; {v['searched']}"
                          for k, v in x["slots"].items())
            L.append(f"| {x['dialogue']} | {x['group']} | {x['initial_failure']} | {x['kind']} | {x['first_choice_venues']} "
                     f"({x['first_choice_hotels']}) | {s} |")
        L.append("")
    OUT.mkdir(exist_ok=True)
    (OUT / "turns_failinfo.json").write_text(json.dumps(res, indent=1, default=float))
    (OUT / "turns_failinfo.md").write_text("\n".join(L) + "\n")
    print((OUT / "turns_failinfo.md").read_text())


if __name__ == "__main__":
    main()
