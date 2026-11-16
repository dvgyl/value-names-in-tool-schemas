"""Experiment A: the tool call at the agent's timing, and step 2 (the agent sees its own search result). Exploratory.

Design and predictions: PROTOCOL.md "## Round 10 runs", section A, with amendments R10-2 and R10-3. Inputs: the raw.jsonl
of era1_<model> (arms p0, t0, t1, t0ask), the fill runs erx_a*_<model> (more reads of the same cells), era2_<model>
(step 2), MultiWOZ 2.4 and hotel_db.json. Outputs: r10/analysis/out/a.json, a.md and fig_funnel.csv.

Definitions (fixed here, before this script read any round-10 answer):
- A read is valid when its row succeeded, did not stop at the length limit, and parses: p0 by natural.parse with form
  f0; a tool arm by tools.parse_call ("search", "ask" or "none" are valid; "invalid" is not).
- "type = hotel" (the rate of the call) is natural_analyze.hotel: the parsed `type` list holds `hotel`. "hides" is
  gold.hides_guesthouse: the list holds `hotel` and not `guesthouse`. An "ask" or "none" read scores 0 on both.
- Rates are over valid reads. Paired contrasts use the per-dialogue mean over the valid reads of each cell; a
  dialogue enters a contrast when both cells have a valid read. Intervals: 95% cluster bootstrap over dialogues
  (stats.cluster_bootstrap, 2,000 draws, seed 20261112). Sign tests: stats.sign_test over dialogues.
- Search failure (A3b): briefsearch.search_failure of a valid T0 read, as a share of all valid T0 reads on the
  prefixes whose brief sets no type. A read without a search is not a failure.
- Booked venue missing (A3): on the prefixes whose booked venue is a guesthouse, a valid T0 read whose full search
  result (briefsearch.search, no row limit) does not hold the booked venue. A read without a search does not miss it.
- Precision: of the valid T0 reads with type = hotel, the share whose booked venue is a hotel (base rate 199/554).
- Step 2: each era2 row joins its era1 T0 read (same dialogue and read). The result is empty when the stage-1 search
  found no venue. Answer kinds: "search_unfiltered" (a new search whose type does not hide guesthouses),
  "search_filtered", "text_mentions" (a text answer that matches GUEST_OR_LIMITED), "text_other", "neither", "invalid".
- The relaxation check: briefsearch.relaxation of each T0 search (no call; it needs no brief).
Usage (from explore/): .venv/bin/python -I r10/analysis/a_analyze.py
"""
import collections
import csv
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import natural  # noqa: E402
import natural_analyze as na  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402
import zruns  # noqa: E402

OUT = HERE / "out"
MODELS = ("sonnet", "haiku", "opus", "sol", "luna", "astra")
ARMS = ("p0", "t0", "t1", "t0ask")
FILL = {"sonnet": ("erx_a1_sonnet", "erx_a2_sonnet"), "opus": ("erx_a2_opus",), "sol": ("erx_a3_sol",)}
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
GUEST_OR_LIMITED = re.compile(r"guest ?houses?|only hotels|hotels only", re.I)
BASE = 199 / 554


def rows(folder):
    path = EXPLORE / folder / "raw.jsonl"
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None


def split(cid):
    name, did, cell, read = cid.split("-")
    return did + ".json", cell, int(read)


def read_of(row, arm):
    """(kind, fields): kind is "form", "search", "ask", "none" or "invalid"."""
    if row.get("type") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in CUT:
        return "invalid", "cut"
    if arm == "p0":
        try:
            return "form", natural.parse(row.get("text", ""), natural.FORMS["f0"])
        except (ValueError, KeyError, TypeError):
            return "invalid", "parse"
    kind, val = tools.parse_call(row, arm)
    return kind, val


def is_hotel(kind, fields):
    return kind in ("form", "search") and na.hotel(fields.get("type"))


def hides(kind, fields):
    return kind in ("form", "search") and gold.hides_guesthouse(fields.get("type"))


def interval(per_dialogue):
    """per_dialogue: list of (k, n). Returns (point, low, high) of sum k / sum n, or None."""
    per_dialogue = [r for r in per_dialogue if r[1]]
    if not per_dialogue:
        return None

    def stat(g):
        k = sum(r[0] for r in g["all"])
        n = sum(r[1] for r in g["all"])
        return k / n if n else 0.0
    return stats.cluster_bootstrap({"all": per_dialogue}, stat)


def mean_interval(diffs):
    if not diffs:
        return None
    return stats.cluster_bootstrap({"all": [(d,) for d in diffs]},
                                   lambda g: sum(r[0] for r in g["all"]) / len(g["all"]))


def load(model):
    """{(dialogue, arm): [(read, kind, fields), ...]} over era1 and the fill runs; None when era1 is not fetched."""
    folders = [f"era1_{model}", *FILL.get(model, ())]
    first = rows(folders[0])
    if first is None:
        return None, []
    out = collections.defaultdict(list)
    used = []
    for folder in folders:
        rr = first if folder == folders[0] else rows(folder)
        if rr is None:
            continue
        used.append(folder)
        for r in rr:
            d, arm, read = split(r["custom_id"])
            kind, val = read_of(r, arm)
            out[(d, arm)].append((read, kind, val if isinstance(val, dict) else None, folder))
    return out, used


def cell_counts(reads, ids, arm, test):
    """Per dialogue (k, n) of `test(kind, fields)` over the valid reads of `arm`."""
    res = []
    for d in ids:
        vals = [test(k, f) for _, k, f, _ in reads.get((d, arm), []) if k != "invalid"]
        res.append((sum(vals), len(vals)))
    return res


def rate(per):
    k, n = sum(r[0] for r in per), sum(r[1] for r in per)
    return {"k": k, "n": n, "share": k / n if n else None}


def with_ci(per):
    out = rate(per)
    ci = interval(per)
    if ci:
        out["ci"] = [ci[1], ci[2]]
    return out


def paired(reads, ids, a, b, test):
    """b minus a per dialogue (means over valid reads); sign test; bootstrap interval of the mean difference."""
    diffs, pos, neg = [], 0, 0
    for d in ids:
        va = [test(k, f) for _, k, f, _ in reads.get((d, a), []) if k != "invalid"]
        vb = [test(k, f) for _, k, f, _ in reads.get((d, b), []) if k != "invalid"]
        if not va or not vb:
            continue
        x = sum(vb) / len(vb) - sum(va) / len(va)
        diffs.append(x)
        pos += x > 0
        neg += x < 0
    ci = mean_interval(diffs)
    return {"dialogues": len(diffs), "mean": ci[0] if ci else None, "ci": [ci[1], ci[2]] if ci else None,
            "higher": pos, "lower": neg, "sign_p": stats.sign_test(pos, neg)}


def analyse_model(model, reads, used, data, g, db, sub, by_key):
    ids = list(g["booked"])
    res = {"folders": used}
    kinds = {arm: collections.Counter(k for d in ids for _, k, _, _ in reads.get((d, arm), [])) for arm in ARMS}
    res["kinds"] = {arm: dict(c) for arm, c in kinds.items()}
    res["reads_per_dialogue"] = {arm: max((len(reads.get((d, arm), [])) for d in ids), default=0) for arm in ARMS}
    res["hotel"] = {arm: with_ci(cell_counts(reads, ids, arm, is_hotel)) for arm in ARMS}
    res["hides"] = {arm: rate(cell_counts(reads, ids, arm, hides)) for arm in ARMS}
    res["hotel_no_type"] = {arm: rate(cell_counts(reads, sub["no_type"], arm, is_hotel)) for arm in ARMS}
    res["hotel_no_name"] = {arm: rate(cell_counts(reads, sub["no_name"], arm, is_hotel)) for arm in ARMS}
    res["t0_minus_p0"] = paired(reads, ids, "p0", "t0", is_hotel)
    res["t1_minus_t0"] = paired(reads, ids, "t0", "t1", is_hotel)
    res["t0ask_minus_t0"] = paired(reads, ids, "t0", "t0ask", is_hotel)
    res["t1_minus_t0_no_type"] = paired(reads, sub["no_type"], "t0", "t1", is_hotel)
    for arm in ("t0", "t1", "t0ask"):
        n_valid = sum(v for k, v in kinds[arm].items() if k != "invalid")
        res.setdefault("share_none", {})[arm] = kinds[arm].get("none", 0) / n_valid if n_valid else None
        res.setdefault("share_invalid", {})[arm] = kinds[arm].get("invalid", 0) / max(1, sum(kinds[arm].values()))
    n_ask = sum(v for k, v in kinds["t0ask"].items() if k != "invalid")
    res["share_ask"] = {"k": kinds["t0ask"].get("ask", 0), "n": n_ask,
                        "share": kinds["t0ask"].get("ask", 0) / n_ask if n_ask else None}
    # Search failure, hidden share and the relaxation check on the prefixes whose brief sets no type (T0, T1).
    for arm in ("t0", "t1", "t0ask", "p0"):
        per, hid, rel = [], [], collections.Counter()
        for d in sub["no_type"]:
            k_d, n_d = 0, 0
            for _, k, f, _ in reads.get((d, arm), []):
                if k == "invalid":
                    continue
                n_d += 1
                if k in ("search", "form"):
                    fail = bs.search_failure(f, data[d], db)
                    k_d += fail
                    h = bs.hidden_share(f, data[d], db)
                    if h is not None:
                        hid.append(h)
                    if arm == "t0" and k == "search":
                        flag = bs.relaxation(f, db)["flag"]
                        rel["calls"] += 1
                        rel["flag"] += flag
                        rel["failures"] += fail
                        rel["failures_flagged"] += fail and flag
            per.append((k_d, n_d))
        res.setdefault("search_failure", {})[arm] = with_ci(per) if arm in ("t0", "t1") else rate(per)
        res.setdefault("hidden_share_mean", {})[arm] = sum(hid) / len(hid) if hid else None
        if arm == "t0":
            res["relaxation_t0"] = dict(rel)
    # Booked venue missing (guesthouse bookings) and precision (T0).
    miss, prec = [], collections.Counter()
    for d in ids:
        venue = zruns.booked_venue(data[d], by_key)
        k_d, n_d = 0, 0
        for _, k, f, _ in reads.get((d, "t0"), []):
            if k == "invalid":
                continue
            if venue and venue["type"] == "guesthouse":
                n_d += 1
                if k == "search":
                    names = {zruns._key(v["name"]) for v in bs.search(db, f)}
                    k_d += zruns._key(venue["name"]) not in names
            if is_hotel(k, f) and venue:
                prec["hotel_reads"] += 1
                prec["booked_hotel"] += venue["type"] == "hotel"
        if venue and venue["type"] == "guesthouse":
            miss.append((k_d, n_d))
    res["booked_missing_guesthouse"] = with_ci(miss)
    res["precision_t0"] = {**prec, "share": prec["booked_hotel"] / prec["hotel_reads"] if prec["hotel_reads"] else None,
                           "base_rate": BASE}
    return res


def step2(model, reads, data, db, sub):
    """Join era2 rows to their era1 T0 reads; count the answer kinds by empty and non-empty result."""
    rr = rows(f"era2_{model}")
    if rr is None:
        return None
    first = {(d, read): f for (d, arm), lst in reads.items() if arm == "t0"
             for read, k, f, folder in lst if folder == f"era1_{model}" and k == "search"}
    out = {"empty": collections.Counter(), "nonempty": collections.Counter()}
    fail = collections.Counter()
    for r in rr:
        d, _, read = split(r["custom_id"])
        f1 = first.get((d, read))
        if f1 is None:
            out.setdefault("unmatched", collections.Counter())["rows"] += 1
            continue
        part = "empty" if not bs.search(db, f1) else "nonempty"
        if r.get("type") != "succeeded" or r.get("stop") in CUT:
            kind = "invalid"
        elif r.get("tool_calls"):
            k2, f2 = tools.parse_call(r, "t0")
            kind = "invalid" if k2 != "search" else ("search_filtered" if gold.hides_guesthouse(f2.get("type"))
                                                     else "search_unfiltered")
        elif (r.get("text") or "").strip():
            kind = "text_mentions" if GUEST_OR_LIMITED.search(r["text"]) else "text_other"
        else:
            kind = "neither"
        out[part][kind] += 1
        if d in sub["no_type"] and bs.search_failure(f1, data[d], db):
            fail[kind] += 1
    res = {p: dict(c) for p, c in out.items()}
    for p in ("empty", "nonempty"):
        n = sum(v for k, v in out[p].items() if k != "invalid")
        res[f"{p}_reads"] = n
        res[f"{p}_unfiltered_share"] = out[p]["search_unfiltered"] / n if n else None
        res[f"{p}_recovers_share"] = (out[p]["search_unfiltered"] + out[p]["text_mentions"]) / n if n else None
    res["after_search_failure"] = dict(fail)
    return res


def predictions(res):
    """The A predictions, judged by the point values (the tables give the intervals)."""
    p = {}
    s = res.get("sonnet")
    if s:
        diff = s["hotel"]["t0"]["share"] - s["hotel"]["p0"]["share"]
        p["A1"] = {"words": "in T0 the Sonnet rate is within 10 points of P0", "value": diff * 100,
                   "held": abs(diff) <= 0.10}
    a2 = {m: r["t1_minus_t0"] for m, r in res.items()}
    p["A2"] = {"words": "T1 is lower than T0 for every model (sign test over dialogues, p < 0.01)",
               "value": {m: [v["mean"], v["sign_p"]] for m, v in a2.items()},
               "held": all(v["mean"] is not None and v["mean"] < 0 and v["sign_p"] < 0.01 for v in a2.values())}
    a3 = {m: res[m]["booked_missing_guesthouse"]["share"] for m in ("sonnet", "sol", "luna") if m in res}
    p["A3"] = {"words": "the booked venue is missing in at least 15% of the guesthouse-booked T0 reads for Sonnet, Sol "
                        "and Luna", "value": a3, "held": len(a3) == 3 and all(v >= 0.15 for v in a3.values()),
               "complete": len(a3) == 3}
    a3b = {m: res[m]["search_failure"]["t0"]["share"] for m in ("sonnet", "sol") if m in res}
    p["A3b"] = {"words": "on the prefixes whose brief sets no type, at least 8% of all T0 reads are a search failure, "
                         "for Sonnet and for Sol", "value": a3b,
                "held": len(a3b) == 2 and all(v >= 0.08 for v in a3b.values())}
    a4 = {m: [r["share_ask"]["share"], r["hotel"]["t0ask"]["share"] - r["hotel"]["t0"]["share"]] for m, r in res.items()}
    p["A4"] = {"words": "ask_traveller is called in less than 10% of T0+ask reads, and the rate of type = hotel falls by "
                        "5 points or less against T0", "value": a4,
               "held": all(v[0] < 0.10 and v[1] >= -0.05 for v in a4.values())}
    a5 = {m: r["step2"]["nonempty_unfiltered_share"] for m, r in res.items() if r.get("step2")}
    p["A5"] = {"words": "when the step-2 result holds 1 or more venues, the model searches again without the filter in "
                        "less than 10% of reads, for every model", "value": a5,
               "held": bool(a5) and all(v is not None and v < 0.10 for v in a5.values()),
               "models": sorted(a5)}
    return p


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def ci_text(r):
    return f"{pct(r['share'])} [{pct(r['ci'][0])}, {pct(r['ci'][1])}]" if r.get("ci") else pct(r.get("share"))


def markdown(res, preds, missing, sub_sizes):
    L = ["## 2. Tool calls at the agent's timing (experiment A)", "",
         "Exploratory. 554 prefixes up to the first traveller turn that says \"hotel\" (355 guesthouse bookings, 199 "
         f"hotel bookings). Prefixes whose brief sets no type: {sub_sizes['no_type']}; of those, the brief names no "
         f"venue: {sub_sizes['no_name']}; no hotel fits the brief: {sub_sizes['no_hotel_fits']}.", ""]
    if missing:
        L += [f"Not fetched at this run: {', '.join(missing)}.", ""]
    L += ["### Rate of `type = hotel` per arm (valid reads, 95% interval)", "",
          "| Model | P0 (form) | T0 (tool) | T1 (renamed tool) | T0+ask |", "|---|---|---|---|---|"]
    for m, r in res.items():
        L.append(f"| {m} | " + " | ".join(ci_text(r["hotel"][a]) for a in ARMS) + " |")
    L += ["", "### Paired contrasts (per-dialogue means; sign test over dialogues)", "",
          "| Model | Contrast | Dialogues | Mean, points | 95% interval | Higher | Lower | Sign p |", "|---|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        for key in ("t0_minus_p0", "t1_minus_t0", "t0ask_minus_t0", "t1_minus_t0_no_type"):
            c = r[key]
            if c["mean"] is None:
                continue
            L.append(f"| {m} | {key} | {c['dialogues']} | {100 * c['mean']:+.1f} | [{100 * c['ci'][0]:+.1f}, "
                     f"{100 * c['ci'][1]:+.1f}] | {c['higher']} | {c['lower']} | {c['sign_p']:.2g} |")
    L += ["", "### Cost of the call (prefixes whose brief sets no type for search failure)", "",
          "| Model | Search failure T0 | Search failure T1 | Hidden share T0 (mean) | Booked guesthouse missing T0 | "
          "Precision of hotel (T0; base 35.9%) | Ask share (T0+ask) | No tool call T0 | Invalid T0 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        L.append(f"| {m} | {ci_text(r['search_failure']['t0'])} | {ci_text(r['search_failure']['t1'])} | "
                 f"{pct(r['hidden_share_mean']['t0'])} | {ci_text(r['booked_missing_guesthouse'])} | "
                 f"{pct(r['precision_t0']['share'])} ({r['precision_t0'].get('booked_hotel', 0)}/"
                 f"{r['precision_t0'].get('hotel_reads', 0)}) | {pct(r['share_ask']['share'])} | "
                 f"{pct(r['share_none']['t0'])} | {pct(r['share_invalid']['t0'])} |")
    L += ["", "### The relaxation check (T0 searches on the no-type prefixes; no brief needed)", "",
          "| Model | Calls | Flagged (empty with type, not empty without) | Search failures | Failures flagged |",
          "|---|---|---|---|---|"]
    for m, r in res.items():
        x = r["relaxation_t0"]
        L.append(f"| {m} | {x.get('calls', 0)} | {x.get('flag', 0)} | {x.get('failures', 0)} | "
                 f"{x.get('failures_flagged', 0)} |")
    L += ["", "### Step 2: the agent sees its own search result", "",
          "| Model | Result | Reads | New search, no hotel-only filter | New search, filter kept | Text names a guesthouse or "
          "the limit | Other text | Neither |", "|---|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        s = r.get("step2")
        if not s:
            L.append(f"| {m} | not run or not fetched | | | | | | |")
            continue
        for part in ("nonempty", "empty"):
            c = s.get(part, {})
            n = s[f"{part}_reads"]
            L.append(f"| {m} | {part} | {n} | " + " | ".join(
                f"{c.get(k, 0)} ({pct(c.get(k, 0) / n if n else None)})" for k in
                ("search_unfiltered", "search_filtered", "text_mentions", "text_other", "neither")) + " |")
    L += ["", "### Predictions", "", "| # | Words | Value | Held |", "|---|---|---|---|"]
    for k, v in preds.items():
        L.append(f"| {k} | {v['words']} | {json.dumps(v['value'], default=lambda x: round(x, 4))} | "
                 f"{'held' if v['held'] else 'failed'}{'' if v.get('complete', True) else ' (incomplete)'} |")
    return "\n".join(L) + "\n"


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    by_key = {zruns._key(h["name"]): h for h in zforms.HOTELS}
    sub = bs.brief_subsets(data, list(g["booked"]), db)
    res, missing = {}, []
    for m in MODELS:
        reads, used = load(m)
        if reads is None:
            missing.append(f"era1_{m}")
            continue
        r = analyse_model(m, reads, used, data, g, db, sub, by_key)
        r["step2"] = step2(m, reads, data, db, sub)
        res[m] = r
    preds = predictions(res)
    OUT.mkdir(exist_ok=True)
    sizes = {k: len(v) for k, v in sub.items()}
    (OUT / "a.json").write_text(json.dumps({"exploratory": True, "subsets": sizes, "missing": missing,
                                            "models": res, "predictions": preds}, indent=1, default=float))
    (OUT / "a.md").write_text(markdown(res, preds, missing, sizes))
    with open(OUT / "fig_funnel.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "hotel_only_filter_t0", "search_failure_t0", "recovers_after_failure", "asks_t0ask"])
        for m, r in res.items():
            s2 = (r.get("step2") or {}).get("after_search_failure", {})
            n2 = sum(v for k, v in s2.items() if k != "invalid")
            rec = (s2.get("search_unfiltered", 0) / n2) if n2 else None
            w.writerow([m, r["hides"]["t0"]["share"], r["search_failure"]["t0"]["share"], rec,
                        r["share_ask"]["share"]])
    print((OUT / "a.md").read_text())


if __name__ == "__main__":
    main()
