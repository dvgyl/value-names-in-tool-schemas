"""Experiment I: the reverse text edit (the word "hotel" put into the traveller turns). Exploratory.

Design and predictions: PROTOCOL.md "## Round 10 runs", section I, with its differences 2 and 3. Inputs: the raw.jsonl
of eri_<model> (Sonnet, Haiku, Sol, Luna; cells orig_f0, ins_f0, orig_f1, ins_f1; reads 1 and 2) and of the fill runs
erx_i3_sonnet and erx_i3_sol (read 3 of the same cells), MultiWOZ 2.4 through runs.context() (the groups `ins`,
`ins_assistant_hotel` and `ins_clean`), and review/plan14/harm_by_model.out (the reference rate of I3). Outputs:
r10/analysis/out/i.json and i.md.

Definitions (fixed here before the first run of this script; only the row format of the raw files was looked at):
- A read is valid when its row succeeded, did not stop at the length limit, and parses. The parser is the round-9
  form parser, as r10/runs.py build_i builds the requests (zforms.FORMS f0 and f1): natural.parse with
  natural.FORMS["f0"] for the cells *_f0 and natural.FORMS["f1"] for the cells *_f1 (F1 maps `property_kind` and
  `large_property` back to `type` and `hotel`).
- The outcome is natural_analyze.hotel of the parsed `type`: the list holds `hotel`.
- A missing read is a request of the design (dialogue, cell, read number of a fetched folder) with no row. Invalid and
  missing reads are counted per cell. A cell with 2% or more invalid or missing reads also shows the worst-case
  bound (every such read scored 0, then every such read scored 1).
- Rates are over valid reads. The intervals are 95% cluster bootstraps over dialogues (stats.cluster_bootstrap,
  2,000 draws, seed 20261112).
- The edit effect under a form: per dialogue, the mean of the valid reads of ins_<form> minus the mean of the valid
  reads of orig_<form>. A dialogue enters when both cells have a valid read. Interval: cluster bootstrap of the mean
  difference. Test: stats.sign_test over dialogues (ties dropped).
- The difference in differences: per dialogue, (ins_f0 - orig_f0) - (ins_f1 - orig_f1), each term a mean over valid
  reads. A dialogue enters when all four cells have a valid read. Interval and test as above.
- Parts (difference 3): all 233 dialogues; `ins_assistant_hotel` (115: an assistant turn says "hotel");
  `ins_clean` (118: no turn says "hotel").
- Choice 1: the predictions are judged on all 233 dialogues, by the point values. Reason: the locked words of I1 to
  I3 name no part, and the design group is the 233. The tables give each part beside them.
- Choice 2: the read-3 fill (erx_i3_sonnet, erx_i3_sol) is pooled with reads 1 and 2. Reason: it is a later read of
  the same locked design (amendment R10-4), with the same texts, schemas and settings.
- Choice 3 (I3): the reference is the model's F0 rate on the 423 dialogues of S1t whose brief sets no type and names
  no venue, from review/plan14/harm_by_model.out ("brief: no type, no name", the round-9 natural reads: E13 for Sonnet
  and Haiku, X2 for Sol and Luna). Reason: this file computes "experiment 2" of the round-10 plan;
  main/exp0/RESULT-STAGE1.md reports held-out dialogues, and its no-name subsets are not the 423. I3 holds for a model
  when its pooled ins_f0 rate (all valid reads on the 233) is at least half of the reference rate.
Usage (from explore/): .venv/bin/python -I r10/analysis/i_analyze.py
"""
import collections
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
import natural  # noqa: E402
import natural_analyze as na  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
HARM = EXPLORE / "reference" / "harm_by_model.out"  # repository copy: the file is in explore/reference/
MODELS = ("sonnet", "haiku", "sol", "luna")
CELLS = ("orig_f0", "ins_f0", "orig_f1", "ins_f1")
PARTS = {"all": "ins", "assistant_says_hotel": "ins_assistant_hotel", "no_turn_says_hotel": "ins_clean"}
SOURCES = {  # model: ((folder, read numbers of the design), ...); the first folder is the wave-1 run
    "sonnet": (("eri_sonnet", (1, 2)), ("erx_i3_sonnet", (3,))),
    "haiku": (("eri_haiku", (1, 2)),),
    "sol": (("eri_sol", (1, 2)), ("erx_i3_sol", (3,))),
    "luna": (("eri_luna", (1, 2)),),
}
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
WORST_AT = 0.02


def rows(folder):
    path = EXPLORE / folder / "raw.jsonl"
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None


def split(cid):
    name, did, cell, read = cid.split("-")
    return did + ".json", cell, int(read)


def read_of(row, cell):
    """(valid, hotel or the reason of the invalid read)."""
    if row.get("type") != "succeeded":
        return False, "failed"
    if row.get("stop") in CUT:
        return False, "cut"
    try:
        fields = natural.parse(row.get("text", ""), natural.FORMS[cell.rsplit("_", 1)[1]])
    except (ValueError, KeyError, TypeError):
        return False, "parse"
    return True, na.hotel(fields.get("type"))


def load(model, ids):
    """{(d, cell): [hotel, ...] over valid reads}, invalid counts per cell, missing counts per cell, used folders,
    missing folders. None when the wave-1 folder is not fetched."""
    got = collections.defaultdict(list)
    invalid = collections.defaultdict(collections.Counter)
    seen = set()
    used, missing, expected = [], [], set()
    for i, (folder, reads) in enumerate(SOURCES[model]):
        rr = rows(folder)
        if rr is None:
            missing.append(folder)
            if i == 0:
                return None
            continue
        used.append(folder)
        expected |= {(d, c, r) for d in ids for c in CELLS for r in reads}
        for row in rr:
            d, cell, read = split(row["custom_id"])
            seen.add((d, cell, read))
            ok, val = read_of(row, cell)
            if ok:
                got[(d, cell)].append(val)
            else:
                invalid[cell][val] += 1
    absent = collections.Counter(c for d, c, r in expected - seen)
    return got, invalid, absent, used, missing


def interval(per):
    """per: list of (k, n) per dialogue. (point, low, high) of sum k / sum n."""
    per = [r for r in per if r[1]]
    if not per:
        return None
    return stats.cluster_bootstrap({"all": per}, lambda g: sum(r[0] for r in g["all"]) / sum(r[1] for r in g["all"]))


def mean_interval(diffs):
    if not diffs:
        return None
    return stats.cluster_bootstrap({"all": [(x,) for x in diffs]},
                                   lambda g: sum(r[0] for r in g["all"]) / len(g["all"]))


def mean(xs):
    return sum(xs) / len(xs)


def cell_rate(got, ids, cell, bad=0):
    per = [(sum(got.get((d, cell), [])), len(got.get((d, cell), []))) for d in ids]
    k, n = sum(r[0] for r in per), sum(r[1] for r in per)
    out = {"k": k, "n": n, "dialogues": sum(1 for r in per if r[1]), "share": k / n if n else None}
    ci = interval(per)
    if ci:
        out["ci"] = [ci[1], ci[2]]
    if bad and bad / (n + bad) >= WORST_AT:
        out["worst_case"] = [k / (n + bad), (k + bad) / (n + bad)]
    return out


def contrast(diffs):
    pos, neg = sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)
    ci = mean_interval(diffs)
    return {"dialogues": len(diffs), "mean": ci[0] if ci else None, "ci": [ci[1], ci[2]] if ci else None,
            "higher": pos, "lower": neg, "sign_p": stats.sign_test(pos, neg)}


def edit_effect(got, ids, form):
    a, b = f"orig_{form}", f"ins_{form}"
    return contrast([mean(got[(d, b)]) - mean(got[(d, a)]) for d in ids if got.get((d, a)) and got.get((d, b))])


def did(got, ids):
    diffs = [(mean(got[(d, "ins_f0")]) - mean(got[(d, "orig_f0")])) - (mean(got[(d, "ins_f1")]) - mean(got[(d, "orig_f1")]))
             for d in ids if all(got.get((d, c)) for c in CELLS)]
    return contrast(diffs)


def reference_423():
    """{model: {"k", "n", "share"}} of F0 on "brief: no type, no name" in harm_by_model.out; {} if the file is absent."""
    if not HARM.exists():
        return {}
    block = re.search(r"^brief: no type, no name\n((?:[ \t]+.*\n)+)", HARM.read_text(), re.M)
    if not block:
        return {}
    out = {}
    for m, k, n in re.findall(r"^[ \t]+(\w+)[ \t]+F0 (\d+)/(\d+) ", block.group(1), re.M):
        out[m] = {"k": int(k), "n": int(n), "share": int(k) / int(n)}
    return out


def analyse_model(model, loaded, g):
    got, invalid, absent, used, missing = loaded
    res = {"folders": used, "missing_folders": missing,
           "invalid": {c: dict(invalid[c]) for c in CELLS}, "missing_reads": {c: absent.get(c, 0) for c in CELLS},
           "reads_per_dialogue": {c: max((len(got.get((d, c), [])) for d in g["ins"]), default=0) for c in CELLS}}
    for part, key in PARTS.items():
        ids = list(g[key])
        r = {"dialogues": len(ids)}
        part_set = set(ids)
        for c in CELLS:
            # the invalid and missing counts are per model and cell; the worst case uses them for the full group only
            bad = (sum(invalid[c].values()) + absent.get(c, 0)) if part == "all" else 0
            r[c] = cell_rate(got, ids, c, bad)
        r["edit_f0"] = edit_effect(got, ids, "f0")
        r["edit_f1"] = edit_effect(got, ids, "f1")
        r["did"] = did(got, ids)
        res[part] = r
        assert part_set <= set(g["ins"])
    return res


def every(words, ok, named):
    """A prediction that must hold for every model of `named`: `ok` maps each model with a value to True or False.
    It fails as soon as one model fails; it holds only when every named model has a value."""
    absent = [m for m in named if m not in ok]
    if not all(ok.values()):
        status = "failed"
    elif absent:
        status = "held so far; incomplete (not fetched: " + ", ".join(absent) + ")"
    else:
        status = "held"
    return {"words": words, "held": status == "held", "status": status, "models_missing": absent}


def predictions(res, ref):
    p = {}
    i1 = {m: res[m]["all"]["edit_f0"]["mean"] for m in ("sonnet", "sol", "luna") if m in res}
    p["I1"] = {**every("under F0 the edit raises type = hotel by at least 10 points for Sonnet, Sol and Luna",
                       {m: v is not None and v >= 0.10 for m, v in i1.items()}, ("sonnet", "sol", "luna")),
               "value": i1}
    i2 = {m: r["all"]["edit_f1"]["mean"] for m, r in res.items()}
    p["I2"] = {**every("under F1 the edit raises it by 3 points or less for every model",
                       {m: v is not None and v <= 0.03 for m, v in i2.items()}, MODELS), "value": i2}
    i3 = {}
    for m, r in res.items():
        if m in ref:
            i3[m] = {"ins_f0": r["all"]["ins_f0"]["share"], "reference_423": ref[m]["share"],
                     "half_reference": ref[m]["share"] / 2}
    p["I3"] = {**every("the F0 rate on the edited text is at least half of the model's F0 rate on the 423 no-name "
                       "dialogues of experiment 2",
                       {m: v["ins_f0"] is not None and v["ins_f0"] >= v["half_reference"] for m, v in i3.items()}, MODELS),
               "value": i3,
               "source": "review/plan14/harm_by_model.out, 'brief: no type, no name', F0 (round-9 natural reads)"}
    return p


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def rounded(x):
    if isinstance(x, float):
        return round(x, 4)
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rounded(v) for v in x]
    return x


def rate_text(r):
    s = f"{pct(r['share'])} ({r['k']}/{r['n']})"
    if r.get("ci"):
        s += f" [{pct(r['ci'][0])}, {pct(r['ci'][1])}]"
    if r.get("worst_case"):
        s += f"; worst case [{pct(r['worst_case'][0])}, {pct(r['worst_case'][1])}]"
    return s


def contrast_row(label, c):
    if c["mean"] is None:
        return f"| {label} | 0 | - | - | - | - | - |"
    return (f"| {label} | {c['dialogues']} | {100 * c['mean']:+.1f} | [{100 * c['ci'][0]:+.1f}, {100 * c['ci'][1]:+.1f}] | "
            f"{c['higher']} | {c['lower']} | {c['sign_p']:.2g} |")


def markdown(res, preds, missing, ref):
    L = ["## 4. The reverse text edit (experiment I)", "",
         "Exploratory. 233 training dialogues whose gold sets no type and whose traveller turns hold a lodging phrase "
         "and no \"hotel\". The edit changes the lodging phrase in the traveller turns to \"hotel\" (textedit.py). "
         "Parts: an assistant turn says \"hotel\" (115); no turn says \"hotel\" (118). Outcome: `type` holds `hotel`.", ""]
    if missing:
        L += [f"Not fetched at this run: {', '.join(missing)}.", ""]
    L += ["### Valid, invalid and missing reads per cell", "",
          "| Model | Folders | Reads per dialogue | " + " | ".join(CELLS) + " |", "|---|---|---|" + "---|" * len(CELLS)]
    for m, r in res.items():
        cells = []
        for c in CELLS:
            inv = r["invalid"][c]
            cells.append(f"{r['all'][c]['n']} valid, {sum(inv.values())} invalid"
                         + (f" ({', '.join(f'{k} {v}' for k, v in inv.items())})" if inv else "")
                         + f", {r['missing_reads'][c]} missing")
        L.append(f"| {m} | {', '.join(r['folders'])} | {r['reads_per_dialogue']['orig_f0']} | " + " | ".join(cells) + " |")
    for part in PARTS:
        n = next(iter(res.values()))[part]["dialogues"] if res else 0
        L += ["", f"### Rate of `type = hotel` per cell, part: {part} ({n} dialogues; valid reads, 95% interval)", "",
              "| Model | " + " | ".join(CELLS) + " |", "|---|" + "---|" * len(CELLS)]
        for m, r in res.items():
            L.append(f"| {m} | " + " | ".join(rate_text(r[part][c]) for c in CELLS) + " |")
    L += ["", "### The edit effect and the difference in differences (per-dialogue means; sign test over dialogues)", "",
          "| Model, part, contrast | Dialogues | Mean, points | 95% interval | Higher | Lower | Sign p |",
          "|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        for part in PARTS:
            for key, label in (("edit_f0", "edit under F0 (ins_f0 - orig_f0)"), ("edit_f1", "edit under F1 (ins_f1 - orig_f1)"),
                               ("did", "difference in differences (F0 edit - F1 edit)")):
                L.append(contrast_row(f"{m}, {part}, {label}", r[part][key]))
    L += ["", "### The I3 reference: F0 rate on the 423 dialogues of S1t whose brief sets no type and names no venue", "",
          "Source: review/plan14/harm_by_model.out, row \"brief: no type, no name\" (round-9 natural reads: E13 for "
          "Sonnet and Haiku, X2 for Sol and Luna).", "", "| Model | Reference F0 rate | Half of it | ins_f0 rate (233) |",
          "|---|---|---|---|"]
    for m in MODELS:
        x = ref.get(m)
        ins = res[m]["all"]["ins_f0"] if m in res else None
        ref_text = f"{pct(x['share'])} ({x['k']}/{x['n']})" if x else "-"
        L.append(f"| {m} | {ref_text} | {pct(x['share'] / 2) if x else '-'} | "
                 f"{rate_text(ins) if ins else 'not fetched'} |")
    L += ["", "### Predictions (judged on all 233 dialogues by the point value)", "", "| # | Words | Value | Held |",
          "|---|---|---|---|"]
    for k, v in preds.items():
        L.append(f"| {k} | {v['words']} | {json.dumps(rounded(v['value']))} | {v['status']} |")
    return "\n".join(L) + "\n"


def main():
    data, g = runs.context()
    ref = reference_423()
    res, missing = {}, []
    for m in MODELS:
        loaded = load(m, list(g["ins"]))
        if loaded is None:
            missing.append(SOURCES[m][0][0])
            continue
        missing += loaded[4]
        res[m] = analyse_model(m, loaded, g)
    preds = predictions(res, ref)
    OUT.mkdir(exist_ok=True)
    (OUT / "i.json").write_text(json.dumps({"exploratory": True, "missing": missing, "parts": {p: len(g[k]) for p, k in
                                                                                               PARTS.items()},
                                            "reference_423": ref, "models": res, "predictions": preds},
                                           indent=1, default=float))
    (OUT / "i.md").write_text(markdown(res, preds, missing, ref))
    print(f"missing folders: {missing}")
    print((OUT / "i.md").read_text())


if __name__ == "__main__":
    main()
