"""Later turns (amendment R10-8): the requests whose first search failed under the original tool. Post hoc, no model call.

It reads only the stored conversations of the two arms (ert_sonnet: original tool, t0; ert1_sonnet: renamed tool, t1)
and uses the definitions of turns_analyze.py without change. For the group F requests (the brief sets no type, and every
fitting venue is a guesthouse) whose first search under the original tool is a search failure, it gives the outcomes of
the same requests under the renamed tool. It also gives two descriptions that the reviews asked for:
- named in text: in a conversation that shows a fitting venue, an agent reply names a fitting venue that a search showed
  (gold.norm of the venue name, as a substring of gold.norm of the reply text);
- the last search of each conversation that never shows a fitting venue after an initial failure: its type filter, and
  the fields that the brief does not set;
- first choice: the hotel goal of the brief holds a fail_info (a first choice that the corpus marks as failing) that
  differs from its info (the final requirements). The fit rule uses info only. Counts per set, and among the
  conversations that never show a fitting venue.
Outputs: r10/analysis/out/turns_paired.json and turns_paired.md.
Usage (from explore/): .venv/bin/python -I r10/analysis/turns_paired.py
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


def load(name):
    path = ta.EXPLORE / name / "conversations.jsonl"
    recs = [json.loads(x) for x in path.read_text().splitlines()]
    return {r["dialogue"]: r for r in recs if r["status"] == "complete"}


def named_in_text(rec, d, by_name):
    """True when an agent reply names a fitting venue that a search of the conversation showed."""
    brief = bs.brief_of(d)
    shown = {gold.norm(n) for s in rec["searches"] if s["kind"] == "search" for n in s["shown"]}
    fitting = [n for n in shown if bs.fits(by_name[n], brief)]
    text = gold.norm(" ".join(r or "" for r in rec["replies"]))
    return any(n in text for n in fitting)


def main():
    import runs
    data, _ = runs.context()
    db = gold.hotel_db()
    by_name = {gold.norm(v["name"]): v for v in db}
    guest_names = sorted({gold.norm(v["name"]) for v in db if v["type"] == "guesthouse"}, key=len, reverse=True)
    all_names = sorted({gold.norm(v["name"]) for v in db}, key=len, reverse=True)
    recs = {arm: load(name) for arm, name in ta.RUNS.items()}
    rows = {arm: {k: ta.outcomes(r, data, db, by_name, guest_names, all_names) for k, r in recs[arm].items()}
            for arm in recs}
    t0, t1 = rows["t0"], rows["t1"]
    fail = sorted(k for k, r in t0.items() if r["group"] == "F" and r["initial_failure"])
    both = [k for k in fail if k in t1]
    res = {"post_hoc": True, "F_initial_failure_t0": len(fail), "in_both_arms": len(both)}
    for arm, rr in (("t0", t0), ("t1", t1)):
        res[f"{arm}_initial_failure"] = sum(rr[k]["initial_failure"] for k in both)
        res[f"{arm}_never_fit"] = sum(not rr[k]["fit_shown"] for k in both)
        res[f"{arm}_hotel_only_end"] = sum(rr[k]["hotel_only_end"] for k in both)
    res["never_fit_both_arms"] = sum(not t0[k]["fit_shown"] and not t1[k]["fit_shown"] for k in both)
    res["never_fit_t0_only"] = sum(not t0[k]["fit_shown"] and t1[k]["fit_shown"] for k in both)
    res["never_fit_t1_only"] = sum(t0[k]["fit_shown"] and not t1[k]["fit_shown"] for k in both)
    # Named in text: conversations that show a fitting venue, per arm and set.
    named = {}
    for arm in ("t0", "t1"):
        for label, keep in (("F", lambda r: r["group"] == "F"), ("R", lambda r: r["group"] == "R"),
                            ("F_initial_failure", lambda r: r["group"] == "F" and r["initial_failure"])):
            ks = [k for k, r in rows[arm].items() if keep(r) and r["fit_shown"]]
            hit = sum(named_in_text(recs[arm][k], data[k], by_name) for k in ks)
            named[f"{arm}_{label}"] = {"shown": len(ks), "named": hit}
    res["named_in_text"] = named
    # The last search of the conversations that never show a fitting venue after an initial failure (arm t0).
    last = []
    for k in fail:
        if t0[k]["fit_shown"]:
            continue
        searches = [s for s in recs["t0"][k]["searches"] if s["kind"] == "search"]
        f = ta.tupled(searches[-1]["fields"])
        brief = bs.brief_of(data[k])
        extra = sorted(x for x, v in f.items() if v not in (None, "any") and x != "type" and x not in brief)
        last.append({"dialogue": k, "searches": len(searches), "hotel_only_last": gold.hides_guesthouse(f.get("type")),
                     "fields_not_in_brief": extra, "brief_fields": sorted(brief)})
    res["never_fit_after_failure_last_search"] = last

    def first_choice(k):
        h = data[k]["goal"]["hotel"]
        return bool(h.get("fail_info")) and h.get("fail_info") != h.get("info")
    fc = {}
    for label, keep in (("F", lambda r: r["group"] == "F"), ("R", lambda r: r["group"] == "R"),
                        ("F_initial_failure", lambda r: r["group"] == "F" and r["initial_failure"])):
        ks = [k for k, r in t0.items() if keep(r)]
        never = [k for k in ks if not t0[k]["fit_shown"]]
        fc[label] = {"n": len(ks), "first_choice": sum(map(first_choice, ks)), "never_fit": len(never),
                     "never_fit_first_choice": sum(map(first_choice, never)),
                     "never_fit_dialogues": sorted(never)}
    res["first_choice_t0"] = fc
    OUT.mkdir(exist_ok=True)
    (OUT / "turns_paired.json").write_text(json.dumps(res, indent=1))
    L = ["## Later turns: the requests whose first search failed under the original tool (post hoc)", "",
         f"Group F requests with an initial failure under the original tool: {len(fail)}; complete in both arms: "
         f"{len(both)}.", "",
         "| Outcome on these requests | Original tool (t0) | Renamed tool (t1) |", "|---|---|---|",
         f"| Initial failure | {res['t0_initial_failure']} | {res['t1_initial_failure']} |",
         f"| Never shown | {res['t0_never_fit']} | {res['t1_never_fit']} |",
         f"| Hotel-only at the end | {res['t0_hotel_only_end']} | {res['t1_hotel_only_end']} |", "",
         f"Never shown in both arms: {res['never_fit_both_arms']}; only under t0: {res['never_fit_t0_only']}; only under "
         f"t1: {res['never_fit_t1_only']}.", "",
         "### Named in text (conversations that show a fitting venue)", "",
         "| Arm and set | Show a fitting venue | An agent reply names a fitting shown venue |", "|---|---|---|"]
    for key, v in named.items():
        L.append(f"| {key} | {v['shown']} | {v['named']} |")
    L += ["", "### Never shown after an initial failure (t0): the last search", "",
          "| Dialogue | Searches | Hotel-only in the last search | Fields of the last search that the brief does not set |",
          "|---|---|---|---|"]
    for x in last:
        L.append(f"| {x['dialogue']} | {x['searches']} | {x['hotel_only_last']} | {', '.join(x['fields_not_in_brief']) or '-'} |")
    L += ["", "### Briefs with a first choice that the corpus marks as failing (t0)", "",
          "| Set | Conversations | With a first choice | Never shown | Never shown, with a first choice |", "|---|---|---|---|---|"]
    for key, v in fc.items():
        L.append(f"| {key} | {v['n']} | {v['first_choice']} | {v['never_fit']} | {v['never_fit_first_choice']} |")
    (OUT / "turns_paired.md").write_text("\n".join(L) + "\n")
    print((OUT / "turns_paired.md").read_text())


if __name__ == "__main__":
    main()
