"""Sensitivity of the development results to the fit reference. Post hoc, exploratory, no model call (the paper
review round 6: Sol 1).

The fit rule (the frozen briefsearch.fits) scores the requirements of the corpus goal record (goal.hotel.info: area,
pricerange, stars, parking, internet, name). Two questions about this reference:
(a) The record value "no" for parking or internet comes from task sentences such as "doesn't need to have free parking".
    The fit rule reads it as "must not have". Reading (a) reads it as no requirement.
(b) Some recorded final requirements are not in the written task text. Reading (b) drops each recorded requirement whose
    value the hotel part of the written task (turns.hotel_brief: the text that the simulated traveller of the later turns
    got) does not state. A requirement given by reference ("the same area as the restaurant") counts as stated, because
    the full task states the other part; the script also counts these.
Reading "ab" applies both. The registered held-out measure is not recomputed: its answers stay sealed until the second
look (this script reads no held-out answer).

What the script reports, for the recorded reference and for readings a, b and ab:
1. The development grouping of the 448 tool-call first requests whose brief sets no type: only guesthouses fit (F), a
   hotel fits (R), no venue fits (N); moves against the recorded reference.
2. The search failures of the tool calls (Table 2 of the paper; a_analyze definitions: a valid read of arm t0 or t1
   whose type keeps hotel and not guesthouse, on a request where at least one venue fits and every fitting venue is a
   guesthouse; share of all valid reads on the 448), for the six models.
3. The later turns (ert_sonnet: original tool; ert1_sonnet: renamed tool; the same 260 conversations): each
   conversation is regrouped under the reading; initial failure and "never held" (no search of the conversation shows a
   venue that fits) are scored with the reading; the comparison of the paper (only guesthouses fit: never held after an
   initial failure against without one; difference with a bootstrap interval, two-sided Fisher p) and the two-tool
   counts.
Statement rule for (b) (word patterns on the lower-case hotel text; no person checked them): area and price: the value
word, or "same area as" / "same price range as"; stars: "star of N" or "N star"; parking or internet "yes": "free parking"
or "free wifi" / "internet" in a sentence part without a negated "need" or "have"; "no": "doesn't need to have/include
... parking/internet" or "doesn't have free parking";
name: the normalized name in the normalized text.
Outputs: r10/analysis/out/fitref_sensitivity.md and .json. Usage (from explore/):
.venv/bin/python -I r10/analysis/fitref_sensitivity.py
"""
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a_analyze as A  # noqa: E402  (it sets the import path)
import turns_analyze as ta  # noqa: E402

import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import turns  # noqa: E402

OUT = HERE / "out"
READINGS = ("recorded", "a", "b", "ab")
NEG = re.compile(r"(n't|not|no) (need|have)")
REF = {"area": re.compile(r"same area as"), "pricerange": re.compile(r"same price( range)? as")}


def clauses(text):
    """Sentence parts, split at '.', ',' and ' and '."""
    return [c.strip() for c in re.split(r"[.,]| and ", text) if c.strip()]


def stated(slot, value, text):
    """'value', 'reference' or None: does the hotel text state this recorded requirement?"""
    v = str(value).lower()
    t = text.lower()
    body = re.sub(r"its name is called [^.]*", "", t)
    if slot == "name":
        return "value" if gold.norm(v) in gold.norm(t) else None
    if slot in ("area", "pricerange"):
        word = r"moderate(ly)?" if v == "moderate" else re.escape(v)
        if re.search(rf"\b{word}\b", body):
            return "value"
        return "reference" if REF[slot].search(body) else None
    if slot == "stars":
        return "value" if re.search(rf"star of {re.escape(v)}\b|\b{re.escape(v)}[- ]stars?\b", body) else None
    if slot in ("parking", "internet"):
        words = ("parking",) if slot == "parking" else ("wifi", "internet", "wi-fi")
        parts = [c for c in clauses(body) if any(w in c for w in words)]
        if v == "yes":
            return "value" if any(not NEG.search(c) for c in parts) else None
        if v == "no":
            return "value" if any(NEG.search(c) for c in parts) else None
    return None


def brief_under(d, reading, notes=None):
    """The recorded brief (goal.hotel.info) under a reading."""
    info = dict(bs.brief_of(d))
    if reading in ("a", "ab"):
        for slot in ("parking", "internet"):
            if str(info.get(slot, "")).lower() == "no":
                info.pop(slot)
    if reading in ("b", "ab"):
        text = turns.hotel_brief(d)
        for slot in list(info):
            if slot not in bs.SLOTS:
                continue
            s = stated(slot, info[slot], text)
            if notes is not None:
                notes[(slot, s)] += 1
            if s is None:
                info.pop(slot)
    return info


def fitting(d, db, reading):
    b = brief_under(d, reading)
    return [v for v in db if bs.fits(v, b)]


def group(fit):
    if not fit:
        return "N"
    return "R" if any(v["type"] == "hotel" for v in fit) else "F"


def failure(fields, grp):
    return grp == "F" and gold.hides_guesthouse(fields.get("type"))


def grouping(data, ids, db):
    out, notes = {}, collections.Counter()
    dropped = collections.Counter()
    for d in ids:
        before = sum(notes[k] for k in notes if k[1] is None)
        brief_under(data[d], "b", notes)
        dropped[sum(notes[k] for k in notes if k[1] is None) - before] += 1
    groups = {r: {d: group(fitting(data[d], db, r)) for d in ids} for r in READINGS}
    for r in READINGS:
        moves = collections.Counter(f"{groups['recorded'][d]}->{groups[r][d]}" for d in ids
                                    if groups[r][d] != groups["recorded"][d])
        out[r] = {"F": sum(x == "F" for x in groups[r].values()), "R": sum(x == "R" for x in groups[r].values()),
                  "N": sum(x == "N" for x in groups[r].values()), "moves": dict(moves),
                  "moved_ids": sorted(d for d in ids if groups[r][d] != groups["recorded"][d])}
    slots = collections.Counter()
    for d in ids:
        info = bs.brief_of(data[d])
        for slot in ("parking", "internet"):
            if str(info.get(slot, "")).lower() == "no":
                slots[f"{slot}=no"] += 1
    return out, groups, {"statement": {f"{k[0]}:{k[1]}": v for k, v in sorted(notes.items(), key=str)},
                         "no_values": dict(slots),
                         "b_dropped_requirements": sum(k * v for k, v in dropped.items()),
                         "b_briefs_with_a_dropped_requirement": sum(v for k, v in dropped.items() if k)}


def tool_failures(data, ids, groups):
    out = {}
    for m in A.MODELS:
        reads, _ = A.load(m)
        if reads is None:
            continue
        out[m] = {}
        for r in READINGS:
            for arm in ("t0", "t1"):
                per = []
                for d in ids:
                    k_d, n_d = 0, 0
                    for _, k, f, _ in reads.get((d, arm), []):
                        if k == "invalid":
                            continue
                        n_d += 1
                        k_d += k == "search" and failure(f, groups[r][d])
                    per.append((k_d, n_d))
                out[m][f"{r}|{arm}"] = A.with_ci(per)
    return out


def conv_outcome(rec, data, db, by_name, reading):
    d = data[rec["dialogue"]]
    fit = fitting(d, db, reading)
    names = {gold.norm(v["name"]) for v in fit}
    searches = [s for s in rec["searches"] if s["kind"] == "search"]
    shown = any(gold.norm(n) in names for s in searches for n in s["shown"])
    first = ta.tupled(searches[0]["fields"]) if searches else None
    grp = group(fit)
    return {"dialogue": rec["dialogue"], "sample_group": rec["group"], "group": grp,
            "initial_failure": bool(first) and failure(first, grp), "never_fit": not shown,
            "first_choice": bool(d["goal"]["hotel"].get("fail_info"))
            and d["goal"]["hotel"].get("fail_info") != d["goal"]["hotel"].get("info")}


def later_turns(data, db):
    by_name = {gold.norm(v["name"]): v for v in db}
    recs = {arm: {r["dialogue"]: r for r in (json.loads(x) for x in (ta.EXPLORE / name / "conversations.jsonl")
                                             .read_text().splitlines()) if r["status"] == "complete"}
            for arm, name in ta.RUNS.items()}
    out = {}
    for r in READINGS:
        rows = {arm: {d: conv_outcome(rec, data, db, by_name, r) for d, rec in rs.items()} for arm, rs in recs.items()}
        t0 = list(rows["t0"].values())
        f = [x for x in t0 if x["group"] == "F"]
        ff, fn = [x for x in f if x["initial_failure"]], [x for x in f if not x["initial_failure"]]
        res = {"groups_t0": dict(collections.Counter(x["group"] for x in t0)),
               "regrouped_from_sample": dict(collections.Counter(f"{x['sample_group']}->{x['group']}" for x in t0
                                                                 if x["sample_group"] != x["group"])),
               "F_initial_failure": len(ff), "F_never_after_failure": sum(x["never_fit"] for x in ff),
               "F_never_without": sum(x["never_fit"] for x in fn), "F_without": len(fn),
               "diff": ta.diff(ff, fn, "never_fit"),
               "never_by_group": {arm: {g: [sum(x["never_fit"] for x in v.values() if x["group"] == g),
                                            sum(x["group"] == g for x in v.values())] for g in ("F", "R", "N")}
                                  for arm, v in rows.items()}}
        nf = [x for x in f if not x["first_choice"]]
        nff, nfn = [x for x in nf if x["initial_failure"]], [x for x in nf if not x["initial_failure"]]
        res["no_first_choice"] = {"after_failure": [sum(x["never_fit"] for x in nff), len(nff)],
                                  "without": [sum(x["never_fit"] for x in nfn), len(nfn)],
                                  "diff": ta.diff(nff, nfn, "never_fit")}
        both = [d for d in rows["t0"] if d in rows["t1"] and rows["t0"][d]["group"] == "F"]
        res["paired_F"] = {"n": len(both), "initial_failure": [sum(rows[a][d]["initial_failure"] for d in both)
                                                                for a in ("t0", "t1")],
                           "never": [sum(rows[a][d]["never_fit"] for d in both) for a in ("t0", "t1")]}
        fail20 = [d for d in both if rows["t0"][d]["initial_failure"]]
        res["paired_on_t0_failures"] = {"n": len(fail20), "never": [sum(rows[a][d]["never_fit"] for d in fail20)
                                                                    for a in ("t0", "t1")]}
        res["never_ids_t0"] = sorted(x["dialogue"] for x in t0 if x["never_fit"])
        out[r] = res
    return out


def pts(d):
    if not d:
        return "-"
    return f"{100 * d['diff']:+.1f} [{100 * d['ci'][0]:+.1f}, {100 * d['ci'][1]:+.1f}], Fisher p {d['fisher_p']:.2g}"


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    ids = bs.brief_subsets(data, list(g["booked"]), db)["no_type"]
    assert len(ids) == 448, len(ids)
    grp, groups, notes = grouping(data, ids, db)
    tools_ = tool_failures(data, ids, groups)
    lt = later_turns(data, db)
    res = {"post_hoc": True, "exploratory": True, "readings": READINGS, "grouping_448": grp, "notes_448": notes,
           "tool_search_failures": tools_, "later_turns": lt}
    L = ["## Fit reference: sensitivity of the development results (post hoc)", "",
         "No model call; no held-out answer. Readings: recorded = the corpus goal record as scored (a value 'no' means "
         "must not have); a = parking or internet 'no' read as no requirement; b = drop each recorded requirement that "
         "the hotel part of the written task does not state (a reference to another part counts as stated); ab = both.",
         "", f"Statement check of reading b on the 448 first requests (slot:kind -> count): {json.dumps(notes)}", "",
         "### 1. Grouping of the 448 first requests whose brief sets no type", "",
         "| Reading | Only guesthouses fit (F) | A hotel fits (R) | No venue fits (N) | Moves from the recorded grouping |",
         "|---|---|---|---|---|"]
    for r in READINGS:
        x = grp[r]
        L.append(f"| {r} | {x['F']} | {x['R']} | {x['N']} | {json.dumps(x['moves'])} |")
    L += ["", "### 2. Search failures of the tool calls (share of valid reads on the 448; Table 2)", "",
          "| Model | " + " | ".join(f"{r}: original / renamed" for r in READINGS) + " |",
          "|---|" + "---|" * len(READINGS)]
    for m, x in tools_.items():
        cells = []
        for r in READINGS:
            a, b = x[f"{r}|t0"], x[f"{r}|t1"]
            cells.append(f"{100 * a['share']:.1f}% [{100 * a['ci'][0]:.1f}, {100 * a['ci'][1]:.1f}] / "
                         f"{100 * b['share']:.1f}%")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L += ["", "### 3. Later turns (Sonnet agent; the same 260 conversations, regrouped under each reading)", "",
          "| Reading | Groups (original tool) | Regrouped | F: initial failures | F: never held after one | F: never held without one | Difference | Without first-choice briefs | Never held, original / renamed (F) | On the original tool's initial failures: original / renamed |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in READINGS:
        x = lt[r]
        nfc = x["no_first_choice"]
        L.append(f"| {r} | {json.dumps(x['groups_t0'])} | {json.dumps(x['regrouped_from_sample'])} | "
                 f"{x['F_initial_failure']} | {x['F_never_after_failure']} of {x['F_initial_failure']} | "
                 f"{x['F_never_without']} of {x['F_without']} | {pts(x['diff'])} | "
                 f"{nfc['after_failure'][0]} of {nfc['after_failure'][1]} against {nfc['without'][0]} of "
                 f"{nfc['without'][1]}: {pts(nfc['diff'])} | "
                 f"{x['never_by_group']['t0']['F'][0]} / {x['never_by_group']['t1']['F'][0]} | "
                 f"{x['paired_on_t0_failures']['never'][0]} / {x['paired_on_t0_failures']['never'][1]} "
                 f"(n = {x['paired_on_t0_failures']['n']}) |")
    L += ["", "Never held per group and tool (count, conversations):", ""]
    for r in READINGS:
        L.append(f"- {r}: {json.dumps(lt[r]['never_by_group'])}; original-tool never-held ids: "
                 f"{', '.join(lt[r]['never_ids_t0'])}")
    L += ["", "Moved first requests (448), per reading: " + "; ".join(
        f"{r}: {', '.join(grp[r]['moved_ids']) or 'none'}" for r in READINGS[1:])]
    OUT.mkdir(exist_ok=True)
    (OUT / "fitref_sensitivity.json").write_text(json.dumps(res, indent=1, default=float))
    (OUT / "fitref_sensitivity.md").write_text("\n".join(L) + "\n")
    print((OUT / "fitref_sensitivity.md").read_text())


if __name__ == "__main__":
    main()
