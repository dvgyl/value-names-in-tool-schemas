"""Experiment B: structural fixes, examples and a verifier, scored by the trade rule. Exploratory.

Design and predictions: PROTOCOL.md "## Round 10 runs", section B, its differences 1 and the two build decisions,
amendments R10-1 and R10-5. Inputs: erb_<model>/raw.jsonl (Sonnet, Haiku, Sol, Luna: arms f0, b_list, b_shot,
b_evidence, verify; Sol and Luna also b_define on S2 and S3); for Opus and Astra the fill runs erx_b1/b2/b3_<model>
(b_list and verify on S1t, S2, S3) with the F0 reads of ere_opus and erg_astra as the baseline. Outputs:
r10/analysis/out/b.json, b.md, fig_trade.csv.

Definitions (fixed here, before this script read any B answer):
- A read is valid when its row succeeded, did not stop at the length limit, and forms10.parse accepts it.
- The outcome is natural_analyze.hotel of the scored `type`: the list holds `hotel`. The scored answer of each arm is
  forms10.parse (b_list maps a list with both types to null; b_evidence keeps a value only with the status "stated
  requirement"). B-verify: forms10.b_verify(the F0 answer of the same dialogue and read, the verifier answer); for
  Opus and Astra the F0 answer is read 1 of ere_opus or erg_astra.
- The trade (stats.trade_interval, the paired estimator): per dialogue (F0 hits, F0 reads, arm hits, arm reads) over
  the dialogues with both cells valid. Wrong values = S1t x 994 + S3 x 490; correct values = S2 x 545. An arm meets
  the rule on a model when it removes at least 50% of the F0 wrong values and loses at most 0.30 correct values per
  wrong value removed (point values; the interval is reported).
- B2: among the b_evidence reads on S1t and S3 whose raw `type` holds `hotel`, the share with status "stated
  requirement", and the share of those quotes that occur verbatim in a traveller turn.
Usage (from explore/): .venv/bin/python -I r10/analysis/b_analyze.py
"""
import collections
import csv
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import forms10  # noqa: E402
import natural_analyze as na  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
# The locked outcome is natural_analyze.hotel ("type holds hotel"). With --hotel-only the script reports the
# sensitivity analysis asked for in review (2026-11-12): "type holds hotel and not guesthouse", the value that hides
# every guesthouse in a search. Outputs then get the suffix _hotel_only. Post hoc.
HOTEL_ONLY = "--hotel-only" in sys.argv
# --brief-groups (post hoc, review 2026-11-12): keep in each group only the dialogues where the brief agrees with the
# label (no type: the brief sets no type; guesthouse: the brief sets guesthouse; hotel: the brief sets hotel). The
# trade weights stay 994, 490, 545, so the ratio stays comparable.
BRIEF_GROUPS = "--brief-groups" in sys.argv
SUFFIX = ("_hotel_only" if HOTEL_ONLY else "") + ("_brief" if BRIEF_GROUPS else "")


def hit(fields):
    t = fields["type"]
    return na.hotel(t) and not (HOTEL_ONLY and "guesthouse" in t)
SIZES = {"S1t": 994, "S3": 490, "S2": 545}
GROUP_KEY = {"S1t": "s1t", "S3": "s3", "S2": "s2"}
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
ARMS = ("b_list", "b_shot", "b_evidence", "verify", "b_define")
POSTHOC = "verify_no_only (post hoc)"  # added 2026-11-12 after the B results: the gate acts only on a clear "no"
SOURCES = {  # model: (folders with B arms, folder with the F0 baseline or None when the B folder holds f0)
    "sonnet": (("erb_sonnet",), None), "haiku": (("erb_haiku",), None), "sol": (("erb_sol",), None),
    "luna": (("erb_luna",), None),
    "opus": (("erx_b1_opus", "erx_b2_opus", "erx_b3_opus"), "ere_opus"),
    "astra": (("erx_b1_astra", "erx_b2_astra", "erx_b3_astra"), "erg_astra"),
}


def rows(folder):
    path = EXPLORE / folder / "raw.jsonl"
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None


def split(cid):
    name, did, cell, read = cid.split("-")
    return did + ".json", cell, int(read)


def parse_row(row, arm, turns):
    if row.get("type") != "succeeded" or row.get("stop") in CUT:
        return None
    try:
        return forms10.parse(arm, row.get("text", ""), turns)
    except (ValueError, KeyError, TypeError):
        return None


def load(model, data, group_of):
    """{(d, arm, read): parsed or None}; the f0 baseline from the B folder or the E/G folder; missing folders."""
    folders, base = SOURCES[model]
    got, missing = {}, []
    turns = {}
    for folder in folders + ((base,) if base else ()):
        rr = rows(folder)
        if rr is None:
            missing.append(folder)
            continue
        for r in rr:
            d, arm, read = split(r["custom_id"])
            if d not in group_of:
                continue
            if folder == base and arm != "f0":
                continue
            if arm == "b_evidence" and d not in turns:
                turns[d] = forms10.traveller_turns(data[d])
            got[(d, arm, read)] = parse_row(r, arm, turns.get(d))
    return got, missing


def scored(got, d, arm, read):
    """The scored answer of one read, or None when it is not valid."""
    if arm in ("verify", POSTHOC):
        f0, v = got.get((d, "f0", read)), got.get((d, "verify", read))
        if f0 is None or v is None:
            return None
        if arm == POSTHOC:  # post hoc: "unclear" keeps the value; only "no" removes a hotel-only value
            out = dict(f0)
            t = out["type"]
            if v["answer"] == "no" and isinstance(t, tuple) and "hotel" in t and "guesthouse" not in t:
                out["type"] = None
            return out
        return forms10.b_verify(f0, v["answer"])
    return got.get((d, arm, read))


_INDEX = {}


def reads_of(got, d, arm):
    idx = _INDEX.get(id(got))
    if idx is None:
        idx = collections.defaultdict(set)
        for (dd, a, r) in got:
            idx[(dd, a)].add(r)
        _INDEX[id(got)] = idx
    return sorted(idx.get((d, arm), ()))


def cells(got, ids_by_group, arm):
    out = {}
    for grp, ids in ids_by_group.items():
        rows_ = []
        for d in ids:
            f0 = [scored(got, d, "f0", r) for r in reads_of(got, d, "f0")]
            f0 = [x for x in f0 if x is not None]
            ar = [scored(got, d, arm, r) for r in reads_of(got, d, "verify" if arm in ("verify", POSTHOC) else arm)]
            ar = [x for x in ar if x is not None]
            if f0 and ar:
                rows_.append((sum(hit(x) for x in f0), len(f0), sum(hit(x) for x in ar), len(ar)))
        out[grp] = rows_
    return out


def group_rates(got, ids_by_group, arm):
    res = {}
    for grp, ids in ids_by_group.items():
        k = n = 0
        for d in ids:
            for r in reads_of(got, d, "verify" if arm in ("verify", POSTHOC) else arm):
                x = scored(got, d, arm, r)
                if x is not None:
                    n += 1
                    k += hit(x)
        res[grp] = {"k": k, "n": n, "share": k / n if n else None}
    return res


def trade_of(c):
    if not all(c.get(g) for g in SIZES):
        return None
    (removed, lost, ratio), lo, hi = stats.trade_interval(c, SIZES)
    f0_wrong = sum(sum(r[0] for r in c[g]) / sum(r[1] for r in c[g]) * SIZES[g] for g in ("S1t", "S3"))
    frac = removed / f0_wrong if f0_wrong > 0 else None
    if removed <= 0:  # the arm adds wrong values: no ratio exists
        ratio, lo, hi = None, None, None
    return {"removed": removed, "lost": lost, "ratio": ratio, "ci": [lo, hi], "f0_wrong": f0_wrong,
            "removed_share": frac,
            "meets_rule": bool(frac is not None and ratio is not None and frac >= 0.5 and 0 <= ratio <= 0.30),
            "dialogues": {g: len(c[g]) for g in SIZES}}


def evidence_stats(got, ids):
    c = collections.Counter()
    for d in ids:
        for r in reads_of(got, d, "b_evidence"):
            x = got.get((d, "b_evidence", r))
            if x is None:
                continue
            raw_t = (x.get("raw") or {}).get("type")
            if na.hotel(raw_t):
                c["wrong_hotel_raw"] += 1
                st = (x.get("status") or {}).get("type")
                c["stated"] += st == "stated requirement"
                vb = (x.get("verbatim") or {}).get("type")
                c["quote_given"] += vb is not None
                c["quote_verbatim"] += vb is True
    return dict(c)


def verify_table(got, ids_by_group):
    tab = collections.defaultdict(collections.Counter)
    for grp, ids in ids_by_group.items():
        for d in ids:
            for r in reads_of(got, d, "verify"):
                v, f0 = got.get((d, "verify", r)), got.get((d, "f0", r))
                if v is None or f0 is None:
                    continue
                t = f0["type"]
                kind = ("hotel only" if na.hotel(t) and "guesthouse" not in t else
                        "hotel and guesthouse" if na.hotel(t) else "no hotel")
                tab[f"{grp}, baseline {kind}"][v["answer"]] += 1
    return {k: dict(v) for k, v in sorted(tab.items())}


def predictions(res):
    base = [m for m in ("sonnet", "haiku", "sol", "luna") if m in res]
    meets = lambda arm: [m for m in base if (res[m]["trade"].get(arm) or {}).get("meets_rule")]
    p = {}
    p["B1"] = {"words": "B-list meets the trade rule on at least 2 of the 4 models", "value": meets("b_list"),
               "held": len(meets("b_list")) >= 2, "models": base}
    ev = {m: res[m]["evidence"] for m in base if res[m].get("evidence")}
    share = {m: (v["stated"] / v["wrong_hotel_raw"] if v.get("wrong_hotel_raw") else None) for m, v in ev.items()}
    claude_meets = [m for m in ("sonnet", "haiku") if m in res and (res[m]["trade"].get("b_evidence") or {}).get("meets_rule")]
    p["B2"] = {"words": "B-evidence labels at least 80% of the wrong type = hotel values as stated requirement, so it does "
                        "not meet the rule on Claude", "value": share,
               "held": all(v is not None and v >= 0.80 for v in share.values()) and not claude_meets, "models": base}
    p["B3"] = {"words": "B-verify meets the trade rule on at least 2 of the 4 models", "value": meets("verify"),
               "held": len(meets("verify")) >= 2, "models": base}
    shot = {m: (res[m]["trade"].get("b_shot") or {}) for m in base}
    half = [m for m, t in shot.items() if (t.get("removed_share") or 0) >= 0.5]
    p["B5"] = {"words": "B-shot removes at least 50% of the F0 wrong values on at least 2 of the 4 models, and it meets "
                      "the full trade rule on 1 model or more", "value": {"removes_half": half, "meets": meets("b_shot")},
               "held": len(half) >= 2 and len(meets("b_shot")) >= 1, "models": base}
    p["B4"] = {"words": "Sol's B-define loses 0.50 correct values or fewer per wrong value removed",
               "value": "see b_define rows: S1t has no fresh b_define read, so the locked ratio needs the earlier S1 "
                        "definition reads; reported separately", "held": None}
    return p


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def markdown(res, preds):
    L = ["## 3. Repairs (experiment B)" + (" — sensitivity: hotel-only outcome (post hoc)" if HOTEL_ONLY else ""), "",
         "Exploratory. Groups: 994 dialogues where the traveller says \"hotel\" and the gold sets no type (wrong value "
         "if written), 490 where the gold is guesthouse (wrong), 545 where the gold is hotel (correct). Trade rule: a "
         "repair works when it removes at least 50% of the baseline wrong values and loses at most 0.30 correct values "
         "per wrong value removed.", "",
         "### Rate of `type = hotel` per group (valid reads)", "",
         "| Model | Arm | No type (994) | Guesthouse (490) | Hotel (545) |", "|---|---|---|---|---|"]
    for m, r in res.items():
        for arm, gr in r["rates"].items():
            if not any(v["n"] for v in gr.values()):
                continue
            L.append(f"| {m} | {arm} | " + " | ".join(
                f"{pct(gr[g]['share'])} ({gr[g]['k']}/{gr[g]['n']})" for g in SIZES) + " |")
    L += ["", "### The trade against the baseline (paired estimator, 95% interval)", "",
          "| Model | Arm | Wrong removed | Share of baseline wrong removed | Correct lost | Ratio | 95% interval | "
          "Meets rule |", "|---|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        for arm, t in r["trade"].items():
            if not t:
                continue
            if t["ratio"] is None:
                ratio_txt = "- (adds wrong values) | -"
            else:
                hi = "no upper limit" if t["ci"][1] == float("inf") else f"{t['ci'][1]:.2f}"
                ratio_txt = f"{t['ratio']:.2f} | [{t['ci'][0]:.2f}, {hi}]"
            L.append(f"| {m} | {arm} | {t['removed']:.1f} | {pct(t['removed_share'])} | {t['lost']:.1f} | "
                     f"{ratio_txt} | {'yes' if t['meets_rule'] else 'no'} |")
    L += ["", "Reference (post hoc): the ratio of a repair that deletes baseline `hotel` values at random, "
          "correct values lost per wrong value removed: " + ", ".join(
              f"{m} {r['random_deletion_ratio']:.2f}" for m, r in res.items() if r.get("random_deletion_ratio")) + "."]
    L += ["", "### B-evidence: the labels of the wrong `hotel` values (no type and guesthouse groups)", "",
          "| Model | Wrong hotel values (raw) | Labelled stated requirement | Quote given | Quote verbatim |",
          "|---|---|---|---|---|"]
    for m, r in res.items():
        e = r.get("evidence") or {}
        n = e.get("wrong_hotel_raw", 0)
        if n:
            L.append(f"| {m} | {n} | {e.get('stated', 0)} ({pct(e.get('stated', 0) / n)}) | {e.get('quote_given', 0)} | "
                     f"{e.get('quote_verbatim', 0)} ({pct(e.get('quote_verbatim', 0) / max(1, e.get('quote_given', 0)))}) |")
    L += ["", "### The verifier's answers (\"Does the traveller exclude guesthouses?\")", "",
          "| Model | Group and baseline value | yes | no | unclear |", "|---|---|---|---|---|"]
    for m, r in res.items():
        for k, v in r["verify_table"].items():
            L.append(f"| {m} | {k} | {v.get('yes', 0)} | {v.get('no', 0)} | {v.get('unclear', 0)} |")
    L += ["", "### Predictions", "", "| # | Words | Value | Held |", "|---|---|---|---|"]
    for k, v in preds.items():
        held = "-" if v["held"] is None else ("held" if v["held"] else "failed")
        if v.get("models") and len(v["models"]) < 4 and v["held"] is not None:
            held += f" (models so far: {', '.join(v['models'])})"
        L.append(f"| {k} | {v['words']} | {json.dumps(v['value'], default=lambda x: round(x, 4))} | {held} |")
    return "\n".join(L) + "\n"


def main():
    data, g = runs.context()
    ids_by_group = {G: list(g[GROUP_KEY[G]]) for G in SIZES}
    if BRIEF_GROUPS:
        import gold
        want = {"S1t": None, "S3": "guesthouse", "S2": "hotel"}
        def agrees(d, G):
            b1, b2 = gold.brief_type(data[d]), gold.brief_type(data[d], "fail_info")
            return (b1 is None and b2 is None) if want[G] is None else b1 == want[G]
        ids_by_group = {G: [d for d in ids if agrees(d, G)] for G, ids in ids_by_group.items()}
        print("brief groups:", {G: len(v) for G, v in ids_by_group.items()})
    group_of = {d: G for G, ids in ids_by_group.items() for d in ids}
    res, missing_all = {}, []
    for m in SOURCES:
        got, missing = load(m, data, group_of)
        missing_all += missing
        if not got:
            continue
        arms = [a for a in ARMS if any(k[1] == a for k in got)]
        r = {"missing_folders": missing, "rates": {"f0": group_rates(got, ids_by_group, "f0")}, "trade": {}}
        for arm in arms:
            r["rates"][arm] = group_rates(got, ids_by_group, arm)
            r["trade"][arm] = trade_of(cells(got, ids_by_group, arm))
        if "b_evidence" in arms:
            r["evidence"] = evidence_stats(got, ids_by_group["S1t"] + ids_by_group["S3"])
        r["verify_table"] = verify_table(got, ids_by_group) if "verify" in arms else {}
        f0r = r["rates"]["f0"]  # post hoc reference (review 2026-11-12): delete baseline values at random
        wrong = sum((f0r[G]["share"] or 0) * SIZES[G] for G in ("S1t", "S3"))
        r["random_deletion_ratio"] = (f0r["S2"]["share"] or 0) * SIZES["S2"] / wrong if wrong else None
        if "verify" in arms:  # post hoc, outside the predictions
            r["rates"][POSTHOC] = group_rates(got, ids_by_group, POSTHOC)
            r["trade"][POSTHOC] = trade_of(cells(got, ids_by_group, POSTHOC))
        res[m] = r
    preds = predictions(res)
    OUT.mkdir(exist_ok=True)
    (OUT / f"b{SUFFIX}.json").write_text(json.dumps({"exploratory": True, "missing": missing_all, "models": res,
                                            "predictions": preds}, indent=1, default=float))
    (OUT / f"b{SUFFIX}.md").write_text(markdown(res, preds))
    with open(OUT / f"fig_trade{SUFFIX}.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "arm", "wrong_removed", "correct_lost", "ratio", "ci_low", "ci_high", "meets_rule"])
        for m, r in res.items():
            for arm, t in r["trade"].items():
                if t:
                    w.writerow([m, arm, t["removed"], t["lost"], t["ratio"], t["ci"][0], t["ci"][1], t["meets_rule"]])
    print(f"missing folders: {missing_all}")
    print((OUT / f"b{SUFFIX}.md").read_text())


if __name__ == "__main__":
    main()
