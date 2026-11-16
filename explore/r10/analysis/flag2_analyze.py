"""Amendment R10-13: the returned flag with travellers who require a hotel (arm a, Claude) and the GPT models (arm b).
Exploratory.

Inputs: eru_<model>/raw.jsonl (or pilot_raw.jsonl with --pilot, a dry run of the code), and era2_<model>/raw.jsonl of
Sol and Astra for a description. Outputs: r10/analysis/out/flag2.md and flag2.json (--pilot: flag2_pilot.*).

Definitions (fixed in R10-13 before any call of the amendment):
- Arm (a): each answer gets one kind by flag2.classify_a: widen_silent, widen_told, kept, tell, neither, invalid.
  Primary: silent widening (widen_silent, the wrong action for these travellers) and tell (the right action).
  Secondary: any widening (widen_silent or widen_told); tell that matches the R10-7 word rule. Conditions: brief
  (cells plain, flag) and explicit (xplain, xflag).
- Arm (b): flag.classify (widen, kept, tell, other, neither, invalid). Recovery = widen or tell (primary).
- A unit is a dialogue. A pair is one stage-1 call (dialogue and read) with a valid answer in both cells. The paired
  difference of a dialogue is the mean over its pairs of (cell B minus cell A), 1 for a hit and 0 for a miss.
- 95% intervals: percentile cluster bootstrap over dialogues (stats.cluster_bootstrap, 2,000 draws, seed 20261112).
  Sign test: stats.sign_test over dialogues (ties dropped). No correction for multiple tests (exploratory).
- Descriptions: the widening answers of arm (a) split by text (no text, word rule, other text; the note of
  2026-11-12 18:35 UTC); arm (b) on the calls whose brief sets no type; the era2 answers of the same calls (one-call
  limit, another batch).
Usage (from explore/): .venv/bin/python -I r10/analysis/flag2_analyze.py [--pilot]
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
import flag2  # noqa: E402
import gold  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
CONDITIONS = {"brief": ("plain", "flag"), "explicit": ("xplain", "xflag")}
# Hit functions on an answer (kind, details).
A_OUTCOMES = {
    "silent_widening": lambda k, d: k == "widen_silent",
    "tell": lambda k, d: k == "tell",
    "any_widening": lambda k, d: k in ("widen_silent", "widen_told"),
    "tell_word_rule": lambda k, d: k == "tell" and bool((d or {}).get("word")),
}
B_OUTCOMES = {
    "recovery": lambda k, d: k in ("widen", "tell"),
    "widen": lambda k, d: k == "widen",
    "tell": lambda k, d: k == "tell",
}
A_KINDS = ("widen_silent", "widen_told", "kept", "tell", "neither", "invalid")
B_KINDS = ("widen", "tell", "kept", "other", "neither", "invalid")
# (cell A, cell B) of each paired comparison of arm (a): B minus A.
A_CONTRASTS = {"flag_minus_plain (brief)": ("plain", "flag"), "flag_minus_plain (explicit)": ("xplain", "xflag"),
               "explicit_minus_brief (plain)": ("plain", "xplain"), "explicit_minus_brief (flag)": ("flag", "xflag")}


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None


def widen_text(row):
    text = (row.get("text") or "").strip()
    return "no text" if not text else "word rule" if flag2.told(text) else "other text"


def answers(model, pilot, classify):
    """{(dialogue, read): {cell: [(kind, details), ...]}} and the widening text split; None when not fetched."""
    rr = rows(EXPLORE / f"eru_{model}" / ("pilot_raw.jsonl" if pilot else "raw.jsonl"))
    if rr is None:
        return None, None
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    split = collections.defaultdict(collections.Counter)
    for r in rr:
        _, did, cell, read = r["custom_id"].split("-")
        kind, details = classify(r)
        out[(did, int(read))][cell].append((kind, details))
        if kind in ("widen_silent", "widen_told", "widen"):
            split[cell][widen_text(r)] += 1
    return out, {c: dict(v) for c, v in split.items()}


def valid(lst):
    return [x for x in lst or [] if x[0] != "invalid"]


def share_ci(per_dialogue):
    per_dialogue = [x for x in per_dialogue if x[1]]
    if not per_dialogue:
        return None

    def stat(g):
        n = sum(r[1] for r in g["all"])
        return sum(r[0] for r in g["all"]) / n if n else 0.0
    return stats.cluster_bootstrap({"all": per_dialogue}, stat)


def cell_rate(ans, cell, hit):
    per = collections.defaultdict(lambda: [0, 0])
    for (did, _), a in ans.items():
        for k, d in valid(a.get(cell)):
            per[did][0] += hit(k, d)
            per[did][1] += 1
    return share_ci([tuple(v) for v in per.values()])


def paired(ans, a_cell, b_cell, hit):
    """Per call: the mean hit of b_cell minus that of a_cell; the dialogue value is the mean over its calls."""
    per = collections.defaultdict(list)
    for (did, _), a in ans.items():
        p, f = valid(a.get(a_cell)), valid(a.get(b_cell))
        if not p or not f:
            continue
        per[did].append(sum(hit(*x) for x in f) / len(f) - sum(hit(*x) for x in p) / len(p))
    diffs = [sum(v) / len(v) for v in per.values()]
    if not diffs:
        return None
    ci = stats.cluster_bootstrap({"all": [(x,) for x in diffs]}, lambda g: sum(r[0] for r in g["all"]) / len(g["all"]))
    pos, neg = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    return {"dialogues": len(diffs), "pairs": sum(len(v) for v in per.values()), "mean": ci[0], "ci": [ci[1], ci[2]],
            "higher": pos, "lower": neg, "sign_p": stats.sign_test(pos, neg)}


def kinds(ans, cell):
    return dict(collections.Counter(k for a in ans.values() for k, _ in a.get(cell, [])))


def analyse_a(ans, split):
    cells = flag2.CELLS_A
    return {"calls": len(ans), "dialogues": len({d for d, _ in ans}),
            "kinds": {c: kinds(ans, c) for c in cells},
            "rates": {o: {c: cell_rate(ans, c, hit) for c in cells} for o, hit in A_OUTCOMES.items()},
            "contrasts": {name: {o: paired(ans, a, b, hit) for o, hit in A_OUTCOMES.items()}
                          for name, (a, b) in A_CONTRASTS.items()},
            "widen_text": split}


def era2_kinds(model, ans_keys):
    """{kind: count} of the era2 answers (one-call limit) on the same stage-1 calls."""
    e2 = {r["custom_id"]: r for r in rows(EXPLORE / f"era2_{model}" / "raw.jsonl") or []}
    c = collections.Counter()
    for did, read in ans_keys:
        r = e2.get(f"era2_{model}-{did}-s2-{read}")
        c[flag.classify(r)[0] if r else "absent"] += 1
    return dict(c)


def analyse_b(model, ans, split):
    import runs
    data, _ = runs.context()
    res = {"calls": len(ans), "dialogues": len({d for d, _ in ans}),
           "kinds": {arm: kinds(ans, arm) for arm in flag.ARMS},
           "rates": {o: {arm: cell_rate(ans, arm, hit) for arm in flag.ARMS} for o, hit in B_OUTCOMES.items()},
           "flag_minus_plain": {o: paired(ans, "plain", "flag", hit) for o, hit in B_OUTCOMES.items()},
           "widen_text": split}
    no_type = {k: v for k, v in ans.items() if gold.brief_type(data[k[0] + ".json"]) is None
               and gold.brief_type(data[k[0] + ".json"], "fail_info") is None}
    res["no_type_only"] = {"calls": len(no_type), "dialogues": len({d for d, _ in no_type}),
                           "rates": {"recovery": {arm: cell_rate(no_type, arm, B_OUTCOMES["recovery"])
                                                  for arm in flag.ARMS}},
                           "flag_minus_plain": {"recovery": paired(no_type, "plain", "flag", B_OUTCOMES["recovery"])}}
    c = era2_kinds(model, list(ans))
    n = sum(v for k, v in c.items() if k not in ("invalid", "absent"))
    res["era2"] = {"kinds": c, "recovery": (c.get("widen", 0) + c.get("tell", 0)) / n if n else None}
    return res


def point(r):
    return r[0] if r else None


def predictions(a, b):
    """The predictions of R10-13 (fixed before any call). A model that did not run gives "n/a"."""
    p = {}

    def contrast(m, name, o="silent_widening"):
        return ((a.get(m) or {}).get("contrasts", {}).get(name) or {}).get(o)

    def judge(words, values, ok):
        if any(v is None for v in values.values()):
            return {"words": words, "value": values, "held": "n/a"}
        return {"words": words, "value": values, "held": "held" if ok(values) else "failed"}

    for key, cond in (("U1", "brief"), ("U2", "explicit")):
        v = {m: (contrast(m, f"flag_minus_plain ({cond})") or {}).get("mean") for m in flag2.MODELS_A}
        p[key] = judge(f"{cond} condition: silent widening, flag minus plain, is +10 points or less for each of Sonnet, "
                       f"Haiku and Opus", v, lambda v: all(x <= 0.10 for x in v.values()))
    o = contrast("opus", "flag_minus_plain (brief)")
    p["U3"] = judge("Opus, brief condition: silent widening, flag minus plain, is -15 points or less, and its 95% "
                    "interval excludes 0", {"opus": o and {"mean": o["mean"], "ci": o["ci"]}},
                    lambda v: v["opus"]["mean"] <= -0.15 and v["opus"]["ci"][1] < 0)
    rate = lambda m, o, c: point(((a.get(m) or {}).get("rates", {}).get(o) or {}).get(c))  # noqa: E731
    v = {"opus": rate("opus", "silent_widening", "plain"), "sonnet": rate("sonnet", "silent_widening", "plain")}
    p["U4"] = judge("brief condition, plain arm: silent widening is 50% or more for Opus and 20% or more for Sonnet", v,
                    lambda v: v["opus"] >= 0.50 and v["sonnet"] >= 0.20)
    v = {m: (contrast(m, "explicit_minus_brief (plain)") or {}).get("mean") for m in ("sonnet", "opus")}
    p["U5"] = judge("plain arm: silent widening, explicit minus brief, is -20 points or less for Sonnet and for Opus", v,
                    lambda v: all(x <= -0.20 for x in v.values()))
    v = {m: rate(m, "tell", "xflag") for m in flag2.MODELS_A}
    p["U6"] = judge("explicit condition, flag arm: tell is 60% or more for each of Sonnet, Haiku and Opus", v,
                    lambda v: all(x >= 0.60 for x in v.values()))
    rb = lambda m, arm: point(((b.get(m) or {}).get("rates", {}).get("recovery") or {}).get(arm))  # noqa: E731
    v = {m: rb(m, "flag") for m in flag2.MODELS_B}
    p["U7"] = judge("arm (b): with the flag, recovery is 90% or more for Sol and for Astra", v,
                    lambda v: all(x >= 0.90 for x in v.values()))
    v = {m: (((b.get(m) or {}).get("flag_minus_plain") or {}).get("recovery") or {}).get("mean") for m in flag2.MODELS_B}
    p["U8"] = judge("arm (b): recovery, flag minus plain, is +10 points or more for Sol and for Astra", v,
                    lambda v: all(x >= 0.10 for x in v.values()))
    v = {m: rb(m, "plain") for m in flag2.MODELS_B}
    p["U9"] = judge("arm (b), plain arm: recovery is 50% or more for Sol and for Astra", v,
                    lambda v: all(x >= 0.50 for x in v.values()))
    return p


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def ci_text(r):
    return "-" if not r else f"{pct(r[0])} [{pct(r[1])}, {pct(r[2])}]"


def contrast_row(label, o, c):
    return (f"| {label} | {o} | {c['dialogues']} | {c['pairs']} | {100 * c['mean']:+.1f} | "
            f"[{100 * c['ci'][0]:+.1f}, {100 * c['ci'][1]:+.1f}] | {c['higher']} | {c['lower']} | {c['sign_p']:.2g} |")


def markdown(a, b, preds, missing, pilot):
    L = ["## The returned flag with travellers who require a hotel, and the GPT models (amendment R10-13)"
         + (" - pilot rows only (dry run; no result)" if pilot else ""), "",
         "Exploratory. Step 2 of experiment A without the one-call limit. Arm (a): Claude models on the prefixes whose "
         "brief sets type hotel; the empty hotel-only result is constructed; cells plain and flag in two text conditions "
         "(brief: the prefix unchanged; explicit: the traveller adds \"It must be a hotel, not a guesthouse.\"). Arm (b): "
         "Sol and Astra on the R10-7 sample rule (briefs with no type or guesthouse). Intervals: 95% percentile cluster "
         "bootstrap over dialogues (2,000 draws, seed 20261112); sign test: exact, over dialogues.", ""]
    if missing:
        L += [f"Not fetched at this run: {', '.join(missing)}.", ""]
    L += ["### Arm (a): answer kinds", "", "| Model | Cell | Answers | " + " | ".join(A_KINDS) + " |",
          "|---|---|---|" + "---|" * len(A_KINDS)]
    for m, r in a.items():
        for c in flag2.CELLS_A:
            k = r["kinds"][c]
            L.append(f"| {m} | {c} | {sum(k.values())} | " + " | ".join(str(k.get(x, 0)) for x in A_KINDS) + " |")
    L += ["", "### Arm (a): rates per cell (valid answers; 95% interval over dialogues)", "",
          "| Model | Outcome | plain | flag | xplain | xflag |", "|---|---|---|---|---|---|"]
    for m, r in a.items():
        for o in A_OUTCOMES:
            L.append(f"| {m} | {o} | " + " | ".join(ci_text(r["rates"][o][c]) for c in flag2.CELLS_A) + " |")
    L += ["", "### Arm (a): paired differences (by call; dialogue means; points)", "",
          "| Model, contrast | Outcome | Dialogues | Calls | Mean | 95% interval | Higher | Lower | Sign p |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m, r in a.items():
        for name, per in r["contrasts"].items():
            for o, c in per.items():
                if c and o in ("silent_widening", "tell", "any_widening"):
                    L.append(contrast_row(f"{m}, {name}", o, c))
    L += ["", "Description (note of 18:35 UTC): widening answers by their text, per cell.", ""]
    for m, r in a.items():
        L.append(f"- {m}: " + "; ".join(f"{c} {json.dumps(r['widen_text'].get(c, {}))}" for c in flag2.CELLS_A))
    L += ["", "### Arm (b): answer kinds", "", "| Model | Arm | Answers | " + " | ".join(B_KINDS) + " |",
          "|---|---|---|" + "---|" * len(B_KINDS)]
    for m, r in b.items():
        for arm in flag.ARMS:
            k = r["kinds"][arm]
            L.append(f"| {m} | {arm} | {sum(k.values())} | " + " | ".join(str(k.get(x, 0)) for x in B_KINDS) + " |")
        e = r["era2"]["kinds"]
        L.append(f"| {m} | era2 (one-call limit, other batch) | {sum(e.values())} | "
                 + " | ".join(str(e.get(x, 0)) for x in B_KINDS) + " |")
    L += ["", "### Arm (b): rates and flag minus plain", "", "| Model | Outcome | Plain | Flag |", "|---|---|---|---|"]
    for m, r in b.items():
        for o in B_OUTCOMES:
            L.append(f"| {m} | {o} | {ci_text(r['rates'][o]['plain'])} | {ci_text(r['rates'][o]['flag'])} |")
        nt = r["no_type_only"]["rates"]["recovery"]
        L.append(f"| {m} | recovery, no-type briefs only ({r['no_type_only']['calls']} calls) | {ci_text(nt['plain'])} | "
                 f"{ci_text(nt['flag'])} |")
    L += ["", "| Model | Outcome | Dialogues | Calls | Mean | 95% interval | Higher | Lower | Sign p |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m, r in b.items():
        for o, c in r["flag_minus_plain"].items():
            if c:
                L.append(contrast_row(m, o, c))
        c = r["no_type_only"]["flag_minus_plain"]["recovery"]
        if c:
            L.append(contrast_row(f"{m}, no-type briefs only", "recovery", c))
    L += ["", "### Predictions (R10-13)", "", "| # | Words | Value | Result |", "|---|---|---|---|"]
    for k, v in preds.items():
        L.append(f"| {k} | {v['words']} | {json.dumps(v['value'], default=lambda x: round(x, 4))} | {v['held']} |")
    return "\n".join(L) + "\n"


def main():
    pilot = "--pilot" in sys.argv
    a, b, missing = {}, {}, []
    for m in flag2.MODELS_A:
        ans, split = answers(m, pilot, flag2.classify_a)
        if ans is None:
            missing.append(f"eru_{m}")
            continue
        a[m] = analyse_a(ans, split)
    for m in flag2.MODELS_B:
        ans, split = answers(m, pilot, flag.classify)
        if ans is None:
            missing.append(f"eru_{m}")
            continue
        b[m] = analyse_b(m, ans, split)
    preds = predictions(a, b)
    OUT.mkdir(exist_ok=True)
    stem = "flag2_pilot" if pilot else "flag2"
    (OUT / f"{stem}.json").write_text(json.dumps({"amendment": "R10-13", "exploratory": True, "pilot": pilot,
                                                  "missing": missing, "arm_a": a, "arm_b": b, "predictions": preds},
                                                 indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(a, b, preds, missing, pilot))
    print((OUT / f"{stem}.md").read_text())


if __name__ == "__main__":
    main()
