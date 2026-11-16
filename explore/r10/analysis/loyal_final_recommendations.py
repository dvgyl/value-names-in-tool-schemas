"""Final recommendations: an inventory of the stored later-turn conversations (spec:
loyal_final_recommendations_spec.md, fixed before this script ran). Post hoc description; no model call.

It reads only the two stored later-turn conversation files (ert_sonnet: original tool, t0; ert1_sonnet: renamed tool,
t1), the venue database, the corpus, the agent system text and tools (code), and the stored full-schema counts of
out/loyal_unchecked_runs.json. It computes no fit and no comparison of outcomes between the tools. It applies
the feasibility decision rule (F1, F2, F3) of the spec.
Outputs: out/loyal_final_recommendations.json and out/loyal_final_recommendations.md (next to this script), and
out/loyal_final_recommendations_rows.json (one row for each conversation).
Usage (from explore/): python3 -I r10/analysis/loyal_final_recommendations.py
This file is a copy of a project script with the paths of the study folder and the names of its files changed; the
results are the same. The title line of the Markdown output is shorter, and both outputs name the spec copy
loyal_final_recommendations_spec.md.
"""
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parents[1]  # explore/ (this file is in explore/r10/analysis/)
OUT = HERE / "out"
RUNS = {"t0": "ert_sonnet", "t1": "ert1_sonnet"}
UNCHECKED = OUT / "loyal_unchecked_runs.json"  # the stored outputs of loyal_unchecked_runs.py

CUE = re.compile(r"\b(unfortunately|not available|unavailable|no longer|doesn't|does not|isn't|is not|aren't|are not|"
                 r"don't have|do not have|couldn't find|could not find|didn't find|did not find|no results?|none of|"
                 r"instead)\b", re.I)
FORMAT_WORDS = re.compile(r"recommend|final (choice|answer|recommendation)|format|chosen|choose one", re.I)


def norm(text):
    """gold.norm: lower case, '&' as 'and', only letters and digits."""
    return re.sub(r"[^a-z0-9]", "", (text or "").lower().replace("&", "and"))


def name_keys(db):
    """For each venue name, the normalized keys that count as naming it (spec item 6)."""
    keys = {}
    for v in db:
        k = {norm(v["name"])}
        if v["name"].lower().startswith("the "):
            k.add(norm(v["name"][4:]))
        keys[v["name"]] = k
    return keys


def named_venues(text, keys):
    """The venues named in `text` (spec item 6), with the longest-match rule."""
    flat = norm(text)
    hit = {name for name, ks in keys.items() if any(k in flat for k in ks)}
    full = {name: norm(name) for name in hit}
    return sorted(n for n in hit if not any(n != m and full[n] in full[m] for m in hit))


def shadowed_name(text, keys):
    """Diagnostic (not a category): a shorter name that the longest-match rule drops still occurs after the longer
    name's text is removed (for example "worth house" next to "warkworth house")."""
    flat = norm(text)
    hit = {name for name, ks in keys.items() if any(k in flat for k in ks)}
    for n in hit:
        for m in hit:
            if n != m and norm(n) in norm(m) and norm(n) in flat.replace(norm(m), ""):
                return True
    return False


def has_cue(text):
    return bool(CUE.search(text or ""))


def complete_records(path):
    recs = [json.loads(x) for x in path.read_text().splitlines()]
    done = list({r["dialogue"]: r for r in recs if r["status"] == "complete"}.values())
    return recs, done


def structured_choice_fields(rec):
    """Spec item 2 / F1: keys of the record or of its stored calls that could name a chosen venue."""
    words = re.compile(r"recommend|choice|chosen|final|selected|booking", re.I)
    found = {k for k in rec if words.search(k)}
    for c in rec["calls"]:
        found |= {f"call.{k}" for k in c if words.search(k)}
        for tc in c.get("tool_calls") or []:
            if tc.get("name") != "search_hotels":
                found.add(f"tool.{tc.get('name')}")
    return sorted(found)


def inventory_one(rec, keys):
    replies = rec["replies"]
    final = replies[-1] if replies else ""
    last_call = rec["calls"][-1] if rec["calls"] else {}
    last_turn_calls = [c for c in rec["calls"] if c.get("turn") == len(replies)]
    pending = bool(last_turn_calls) and len(last_turn_calls) == 4 and bool(last_turn_calls[-1].get("tool_calls"))
    named = named_venues(final, keys)
    shown = {norm(n) for s in rec["searches"] if s["kind"] == "search" for n in s["shown"]}
    earlier = any(named_venues(r, keys) for r in replies[:-1])
    trav_last = rec["traveller"][-1]["text"] if rec["traveller"] else ""
    return {"dialogue": rec["dialogue"], "group": rec["group"], "agent_turns": len(replies),
            "traveller_msgs": len(rec["traveller"]), "final_empty": not final.strip(),
            "last_stop": last_call.get("stop"), "pending_search_at_limit": pending,
            "n_named": len(named), "named": named, "shadowed_name": shadowed_name(final, keys),
            "one_named_shown": len(named) == 1 and norm(named[0]) in shown,
            "one_named_cue": len(named) == 1 and has_cue(final),
            "none_named_earlier_named": not named and earlier,
            "traveller_last_suit": "suit" in trav_last.lower(),
            "unparsed_calls": sum(s["kind"] != "search" for s in rec["searches"]),
            "choice_fields": structured_choice_fields(rec), "tools": sorted({tc.get("name") for c in rec["calls"]
                                                                            for tc in c.get("tool_calls") or []})}


def summarise(rows):
    n = len(rows)
    one = [r for r in rows if r["n_named"] == 1]
    return {"n": n,
            "agent_turns": dict(collections.Counter(r["agent_turns"] for r in rows)),
            "traveller_msgs": dict(collections.Counter(r["traveller_msgs"] for r in rows)),
            "final_empty": sum(r["final_empty"] for r in rows),
            "last_stop": dict(collections.Counter(str(r["last_stop"]) for r in rows)),
            "pending_search_at_limit": sum(r["pending_search_at_limit"] for r in rows),
            "named_0": sum(r["n_named"] == 0 for r in rows), "named_1": len(one),
            "named_2plus": sum(r["n_named"] >= 2 for r in rows),
            "shadowed_name": sum(r["shadowed_name"] for r in rows),
            "one_named_shown": sum(r["one_named_shown"] for r in one),
            "one_named_cue": sum(r["one_named_cue"] for r in one),
            "none_named_earlier_named": sum(r["none_named_earlier_named"] for r in rows),
            "traveller_last_suit": sum(r["traveller_last_suit"] for r in rows),
            "with_unparsed_call": sum(r["unparsed_calls"] > 0 for r in rows),
            "choice_fields": sorted({f for r in rows for f in r["choice_fields"]}),
            "tools": sorted({t for r in rows for t in r["tools"]})}


def decide(per_arm, system_has_format):
    """The feasibility rule of the spec, per arm; the endpoint needs one criterion in both arms."""
    out = {}
    for arm, s in per_arm.items():
        a = s["all"]
        # F1: no candidate field at all -> False; a candidate field -> "review" (a person checks what it holds).
        f1 = "review" if a["choice_fields"] else False
        # F2: no format word in the system text -> False; a format word -> "review" (95% rule checked by hand).
        f2 = "review" if system_has_format[arm] else False
        one = a["named_1"]
        f3a = one >= 0.90 * a["n"]
        f3b = one > 0 and a["one_named_cue"] <= 0.05 * one
        f3c = one > 0 and a["one_named_shown"] >= 0.95 * one
        out[arm] = {"F1": f1, "F2": f2, "F3a": f3a, "F3b": f3b, "F3c": f3c, "F3": f3a and f3b and f3c,
                    "share_named_1": one / a["n"], "share_cue_among_1": a["one_named_cue"] / one if one else None,
                    "share_shown_among_1": a["one_named_shown"] / one if one else None}
    if any(v["F1"] == "review" or v["F2"] == "review" for v in out.values()):
        return out, "review"
    usable = all(v["F3"] for v in out.values())
    return out, usable


def main():
    sys.path.insert(0, str(EXPLORE / "r10" / "analysis"))
    import turns_analyze as ta  # noqa: E402  (adds r10/ and the lib folders to the path)
    import flag  # noqa: E402
    import gold  # noqa: E402
    db = gold.hotel_db()
    keys = name_keys(db)
    system_text = {arm: flag.multi_system(arm) for arm in RUNS}
    format_hits = {arm: [m.group(0) for m in FORMAT_WORDS.finditer(t)] for arm, t in system_text.items()}
    system_has_format = {arm: bool(h) for arm, h in format_hits.items()}
    res = {"post_hoc": True, "no_model_call": True, "spec": "loyal_final_recommendations_spec.md", "arms": {}, "records": {}}
    rows_all = {}
    for arm, name in RUNS.items():
        recs, done = complete_records(EXPLORE / name / "conversations.jsonl")
        rows = [inventory_one(r, keys) for r in done]
        rows_all[arm] = rows
        res["records"][arm] = {"records": len(recs), "complete": len(done),
                               "status": dict(collections.Counter(r["status"] for r in recs)),
                               "record_keys": sorted({k for r in recs for k in r})}
        res["arms"][arm] = {"all": summarise(rows)}
        for g in ("F", "R"):
            res["arms"][arm][g] = summarise([r for r in rows if r["group"] == g])
    stored = json.loads(UNCHECKED.read_text())["later_turns_dropped"]
    res["not_valid_conversations_stored"] = stored
    res["system_text"] = system_text
    res["system_format_words"] = format_hits
    res["decision"], res["usable"] = decide(res["arms"], system_has_format)
    OUT.mkdir(exist_ok=True)
    (OUT / "loyal_final_recommendations.json").write_text(json.dumps(res, indent=1))
    (OUT / "loyal_final_recommendations_rows.json").write_text(json.dumps(rows_all, indent=1))
    L = ["## Inventory of the stored later-turn conversations (post hoc description; no model call)", "",
         "Spec: loyal_final_recommendations_spec.md. No fit and no comparison of outcomes between the tools.", ""]
    for arm in RUNS:
        r = res["records"][arm]
        L.append(f"- {arm} ({RUNS[arm]}): {r['records']} records, {r['complete']} complete; statuses {r['status']}; "
                 f"keys {r['record_keys']}")
    L += ["", f"- Agent system text, words that could fix a final-choice format: {format_hits}",
          f"- Stored conversations with a call that is not valid after normalization (stored count): {stored}", "",
          "| Arm | Set | n | Agent turns | Final empty | Pending search at the call limit | Final names 0 | 1 | 2+ | "
          "1 name: shown by a search | 1 name: cue | 0 names, an earlier reply names one | Traveller's last message has 'suit' "
          "| With a call that does not parse | Shadowed name (diagnostic) | Tools | Fields that could name a choice |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm in RUNS:
        for g in ("all", "F", "R"):
            s = res["arms"][arm][g]
            L.append(f"| {arm} | {g} | {s['n']} | {s['agent_turns']} | {s['final_empty']} | "
                     f"{s['pending_search_at_limit']} | {s['named_0']} | {s['named_1']} | {s['named_2plus']} | "
                     f"{s['one_named_shown']} | {s['one_named_cue']} | {s['none_named_earlier_named']} | "
                     f"{s['traveller_last_suit']} | {s['with_unparsed_call']} | {s['shadowed_name']} | {s['tools']} | "
                     f"{s['choice_fields']} |")
    L += ["", "### Feasibility decision (spec rule)", "", "| Arm | F1 | F2 | F3a (>= 90% name one) | F3b (cue <= 5%) | "
          "F3c (shown >= 95%) | Share naming one | Cue share | Shown share |", "|---|---|---|---|---|---|---|---|---|"]
    for arm, d in res["decision"].items():
        f = (lambda x: "-" if x is None else f"{100 * x:.1f}%")
        L.append(f"| {arm} | {d['F1']} | {d['F2']} | {d['F3a']} | {d['F3b']} | {d['F3c']} | {f(d['share_named_1'])} | "
                 f"{f(d['share_cue_among_1'])} | {f(d['share_shown_among_1'])} |")
    verdict = {True: "usable (write a second dated spec next)", False: "not usable", "review": "review F1/F2 by hand"}
    L += ["", f"Decision: {verdict[res['usable']]}", ""]
    (OUT / "loyal_final_recommendations.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
