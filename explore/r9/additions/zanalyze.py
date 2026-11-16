"""Analysis of Z1 to Z3 and B2 to B4 (ROUND9-ADDITIONS.md sections 3 and 9; the predictions are in PREDICTIONS.md).

Usage, from explore/: python3 -I r9/additions/zanalyze.py [experiment ...] [--alias form=cell ...]
With no experiment, it reads each run of zruns.RUNS that has a raw.jsonl, and e13 (the Claude cells of the original
text under F0 and F1). --alias maps the form name of a comparator run (X1, X2) to a cell of zruns.CELLS.
The summary goes to r9/additions/out/summary.json.

A read is valid when it succeeded, stopped at end_turn, and parses. `type = hotel` is the E8 measure: the `type` list
holds "hotel". A read excludes the booked venue when its `type` list lacks the venue's type (`type` alone), or when
common.acceptable_rank rejects the venue on all six fields ("unclear" counts as no constraint). For p_split, `type` is
`type_required`, the field that filters.
"""
import collections
import json
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zforms  # noqa: E402
import zruns  # noqa: E402
from zforms import EXPLORE, anth, common  # noqa: E402

ALIASES = {"p_main": "orig_f0", "p_main_renamed": "orig_f1"}  # the E13 form names
MODEL_ORDER = ("haiku", "sonnet", "luna", "sol", "deepseek", "qwen", "gemma")
BOOT, BOOT_SEED = 1000, 20261103
OUT = zforms.EXPLORE / "r9" / "additions" / "out" / "summary.json"


def index(rows, aliases):
    """reads[(model, cell)][dialogue] is the list of parsed valid reads; missing[(model, cell)] counts the others."""
    reads, missing = collections.defaultdict(lambda: collections.defaultdict(list)), collections.defaultdict(
        collections.Counter)
    for r in rows:
        try:
            _, d, form, _, model = common.split_custom_id(r["custom_id"])
        except ValueError:
            missing[("?", "?")]["unknown custom_id"] += 1
            continue
        cell = aliases.get(form, form)
        key = (model, cell)
        if cell not in zruns.CELLS:
            missing[key]["unknown cell"] += 1
        elif r["type"] != "succeeded":
            missing[key][r["type"]] += 1
        elif r.get("stop") != "end_turn":
            missing[key][str(r.get("stop"))] += 1
        else:
            try:
                reads[key][d].append(zforms.parse(zruns.CELLS[cell].form, r["text"]))
            except (ValueError, KeyError, TypeError, AttributeError):
                missing[key]["parse_fail"] += 1
    return reads, missing


def says_hotel(field="type"):
    return lambda d, a: isinstance(a.get(field), tuple) and "hotel" in a[field]


def is_unclear(d, a):
    return a["type"] == "unclear"


def kept_either(d, a):
    return says_hotel()(d, a) or says_hotel("type_preferred")(d, a)


def excludes_type(g):
    return lambda d, a: isinstance(a["type"], tuple) and g.venue[d]["type"] not in a["type"]


def excludes_venue(g):
    def measure(d, a):
        v = g.venue[d]
        form = {f: None if a[f] == "unclear" else a[f] for f in common.FIELDS}
        return not common.acceptable_rank(form, [v], {v["name"]: 0})
    return measure


def share(cell, ids, measure):
    """The pooled share of valid reads on `ids` that the measure counts (the e8_measure rate)."""
    values = [measure(d, a) for d in ids for a in cell.get(d, ())]
    return {"reads": len(values), "share": round(sum(values) / len(values), 4) if values else None}


def sign_p(more, less):
    n = more + less
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(more, less) + 1)) / 2 ** n) if n else 1.0


def effect(reads, model, ids, plus, minus, measure):
    """The mean over dialogues of (sum of `plus` cell shares) minus (sum of `minus` cell shares), on the dialogues with
    a valid read in every cell, with a dialogue bootstrap interval and the exact sign test of the per-dialogue values."""
    per = []
    for d in ids:
        cells = [reads.get((model, c), {}).get(d) for c in plus + minus]
        if all(cells):
            v = [sum(measure(d, a) for a in x) / len(x) for x in cells]
            per.append(sum(v[:len(plus)]) - sum(v[len(plus):]))
    if not per:
        return None
    rng = random.Random(BOOT_SEED)
    means = sorted(sum(rng.choices(per, k=len(per))) / len(per) for _ in range(BOOT))
    more, less = sum(x > 0 for x in per), sum(x < 0 for x in per)
    return {"dialogues": len(per), "mean": round(sum(per) / len(per), 4),
            "ci95": [round(means[int(0.025 * BOOT)], 4), round(means[int(0.975 * BOOT) - 1], 4)],
            "sign_test": {"positive": more, "negative": less, "p_exact": sign_p(more, less)}}


def models_with(reads, cells):
    present = {m for m, c in reads if c in cells}
    return [m for m in MODEL_ORDER if m in present] + sorted(present - set(MODEL_ORDER))


def z1(reads, g):
    """Z1 and B2: the text edit, the frame edit, and their difference in differences with the F0/F1 rename."""
    hot, out = says_hotel(), {}
    text = ("orig_f0", "orig_f1", "edit_f0", "edit_f1")
    for m in models_with(reads, zruns.EDIT + zruns.FRAMED):
        cell = {c: reads.get((m, c), {}) for c in zruns.CELLS}
        t = {c: share(cell[c], g.t994, hot) for c in text}
        o0, o1, e0 = (t[c]["share"] for c in text[:3])
        out[m] = {
            "t994_type_hotel": t,
            "rename_effect_original_text": effect(reads, m, g.t994, ["orig_f0"], ["orig_f1"], hot),
            "rename_effect_edited_text": effect(reads, m, g.t994, ["edit_f0"], ["edit_f1"], hot),
            "edit_effect_under_f0": effect(reads, m, g.t994, ["orig_f0"], ["edit_f0"], hot),
            "edit_effect_under_f1": effect(reads, m, g.t994, ["orig_f1"], ["edit_f1"], hot),
            "did_text_x_rename": effect(reads, m, g.t994, ["orig_f0", "edit_f1"], ["orig_f1", "edit_f0"], hot),
            "share_of_rename_gap_removed_by_edit": (round((o0 - e0) / (o0 - o1), 4)
                                                    if None not in (o0, o1, e0) and o0 != o1 else None),
            "frame500_type_hotel": {c: share(cell[c], g.frame500, hot) for c in text + zruns.FRAMED},
            "frame_effect_under_f0_original_text": effect(reads, m, g.frame500, ["orig_f0"], ["acc_orig_f0"], hot),
            "frame_effect_under_f0_edited_text": effect(reads, m, g.frame500, ["edit_f0"], ["acc_edit_f0"], hot),
            "did_frame_x_rename_original_text": effect(reads, m, g.frame500, ["orig_f0", "acc_orig_f1"],
                                                       ["orig_f1", "acc_orig_f0"], hot),
        }
    return out


def precision(cell, g, ids):
    """Among valid reads that write `type = hotel`, the share whose booked venue is a hotel."""
    hits = [g.venue[d]["type"] == "hotel" for d in ids for a in cell.get(d, ()) if says_hotel()(d, a)]
    return {"reads": len(hits), "share": round(sum(hits) / len(hits), 4) if hits else None}


def recognition(reads, m, ids):
    """Dialogues by their modal probe answer ("split" on a tie), with the `type = hotel` share of each prefix form."""
    probe, rows = reads.get((m, "pre_probe"), {}), collections.defaultdict(list)
    for d in ids:
        top = collections.Counter(a["answer"] for a in probe.get(d, ())).most_common(2)
        if top:
            rows[top[0][0] if len(top) == 1 or top[0][1] > top[1][1] else "split"].append(d)
    return {label: {"dialogues": len(rows[label]),
                    **{f"{c}_type_hotel": share(reads.get((m, c), {}), rows[label], says_hotel()) for c in zruns.PREFIX},
                    "pre_unclear_type_unclear": share(reads.get((m, "pre_unclear"), {}), rows[label], is_unclear)}
            for label in zforms.PROBE_VALUES + ("split",) if rows[label]}


def z2(reads, g):
    """Z2 and B3: premature booked-venue exclusion on the prefixes, against the full dialogue, and recognition."""
    groups = {"all": g.booked, **{t: [d for d in g.booked if g.venue[d]["type"] == t] for t in ("guesthouse", "hotel")}}
    out = {}
    for m in models_with(reads, zruns.PREFIX + ("pre_probe",)):
        cells = {}
        for c in zruns.PREFIX + ("orig_f0", "orig_f1"):
            cell = reads.get((m, c), {})
            cells[c] = {"type_hotel": share(cell, g.booked, says_hotel()),
                        "type_unclear": share(cell, g.booked, is_unclear),
                        "excludes_booked_type": {k: share(cell, ids, excludes_type(g)) for k, ids in groups.items()},
                        "excludes_booked_venue_all_fields": {k: share(cell, ids, excludes_venue(g))
                                                             for k, ids in groups.items()},
                        "precision_of_type_hotel": precision(cell, g, g.booked)}
        out[m] = {"booked554": cells,
                  "prefix_minus_full_f0_type_hotel": effect(reads, m, g.booked, ["pre_f0"], ["orig_f0"], says_hotel()),
                  "prefix_minus_full_f0_excludes_booked_type": effect(reads, m, g.booked, ["pre_f0"], ["orig_f0"],
                                                                      excludes_type(g)),
                  "recognition_by_commitment": recognition(reads, m, g.booked)}
    return out


def z3(reads, g):
    """Z3 and B4: the fix table. Booked-venue exclusion on the booked S1 dialogues against `type = hotel` kept in the
    certified subgroups (gold hotel and booked hotel; gold hotel and brief hotel)."""
    s1_booked = [d for d in g.s1 if d in g.venue]
    certified = {"gold_and_booked_hotel": [d for d in g.s2 if d in g.venue and g.venue[d]["type"] == "hotel"],
                 "gold_and_brief_hotel": [d for d in g.s2 if g.brief[d] == "hotel"]}
    out = {}
    for m in models_with(reads, zruns.FIXES):
        rows = {}
        for c in ("orig_f0", "orig_f1") + zruns.FIXES:
            cell = reads.get((m, c), {})
            if not cell:
                continue
            row = {"s1_type_hotel": share(cell, g.s1, says_hotel()), "t994_type_hotel": share(cell, g.t994, says_hotel()),
                   "s2_type_hotel": share(cell, g.s2, says_hotel()),
                   "s1_booked_excludes_type": share(cell, s1_booked, excludes_type(g)),
                   "s1_booked_excludes_venue_all_fields": share(cell, s1_booked, excludes_venue(g)),
                   **{f"kept_{k}": share(cell, ids, says_hotel()) for k, ids in certified.items()}}
            if c == "p_split":
                row["s1_type_preferred_hotel"] = share(cell, g.s1, says_hotel("type_preferred"))
                row["s2_required_or_preferred_hotel"] = share(cell, g.s2, kept_either)
                row.update({f"kept_required_or_preferred_{k}": share(cell, ids, kept_either)
                            for k, ids in certified.items()})
                f0 = reads.get((m, "orig_f0"), {})
                hit = [d for d in g.s1 if any(says_hotel()(d, a) for a in f0.get(d, ())) and cell.get(d)]
                pref = [d for d in hit if any(says_hotel("type_preferred")(d, a) for a in cell[d])]
                row["dialogues_preferred_hotel_where_f0_hotel"] = {
                    "dialogues": len(hit), "share": round(len(pref) / len(hit), 4) if hit else None}
            if c == "p_unclear_nat":
                row["s1_type_unclear"] = share(cell, g.s1, is_unclear)
            rows[c] = row
        f0_s2 = rows.get("orig_f0", {}).get("s2_type_hotel", {}).get("share")
        if "p_split" in rows and f0_s2:
            either = rows["p_split"]["s2_required_or_preferred_hotel"]["share"]
            rows["p_split"]["s2_kept_share_of_f0"] = round(either / f0_s2, 4) if either is not None else None
        out[m] = {"forms": rows,
                  "s1_type_hotel_f0_minus_form": {c: effect(reads, m, g.s1, ["orig_f0"], [c], says_hotel())
                                                  for c in ("orig_f1",) + zruns.FIXES},
                  "s1_type_hotel_unclear_minus_null": effect(reads, m, g.s1, ["p_unclear_nat"], ["p_null_nat"],
                                                             says_hotel())}
    return out


def analyze(rows, g, aliases=ALIASES):
    reads, missing = index(rows, aliases)
    return {"missing": {f"{m}|{c}": dict(v) for (m, c), v in sorted(missing.items())},
            "z1_b2": z1(reads, g), "z2_b3": z2(reads, g), "z3_b4": z3(reads, g)}


def main(argv):
    names, aliases, args = [], dict(ALIASES), iter(argv)
    for a in args:
        if a == "--alias":
            form, cell = next(args).split("=")
            aliases[form] = cell
        else:
            names.append(a)
    names = names or [n for n in (*zruns.RUNS, "e13") if (EXPLORE / n / "raw.jsonl").exists()]
    rows = [json.loads(line) for n in names for line in open(EXPLORE / n / "raw.jsonl")]
    summary = {"experiments": names, "aliases": aliases, **analyze(rows, zruns.groups(anth.multiwoz()), aliases)}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
