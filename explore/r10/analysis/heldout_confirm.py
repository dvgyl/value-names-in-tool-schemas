"""Amendment R10-25 (prototypes/explore/PROTOCOL.md): the held-out confirmation of the repair results of the
paper. Exploratory, fixed in the protocol before the run. No model call, no network.

Usage (from explore/; the paths below are those of the project copy):
    python3 -I r10/analysis/heldout_confirm.py              the result, after the runs
    python3 -I r10/analysis/heldout_confirm.py --selftest   development values and
                                                                                          constructed answers
    python3 -I r10/analysis/heldout_confirm.py --pilot      the join of the pilot rows
Outputs: r10/analysis/out/heldout_confirm.md and heldout_confirm.json (the result); heldout_confirm_pilot.md (the
pilot join, counts only).
This file is a copy of the project analysis (an internal file) with the paths of the study folder and
a neutral title line; the results are the same. It needs the opened held-out answers, which the supplementary
package does not hold.

Data. The held-out answers come only through r10/confirm25.py, which reads main/exp0/open/em1_<model>/raw.jsonl with
the frozen loader main/exp0/analysis.load. The verifier answers come from the runs ern_<model> (raw.jsonl). The
self-test reads the stored development answers of erb_sonnet, erb_sol and ery_gemma and the stored result files of
the paper. The script opens no other em* folder, no sealed file, no key file and no .env file.

Imports. The shared rule modules (briefsearch, clear_rule, forms10, stats, gold, common) and the run module
r10/confirm25.py (the sets and the frozen loader). No development analysis script. The display code `show` is the code
of the paper's Table 3 (an internal file), copied without a change of behaviour; the
self-test proves that it gives the stored values.

Definitions: amendment R10-25, sections "Policies", "Outcomes on the value level", "Outcomes on the display level" and
"Predictions". The primary unit is read 1 ("read1"); the sensitivity analysis uses the mean of the base reads of a
dialogue ("mean"). The development values use "mean", as the paper does.
"""
import collections
import hashlib
import json
import math
import pathlib
import sys
from typing import NamedTuple

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
for sub in ("lib", "forms", "pmain", "trackc", "r9", "r9/natural", "r9/additions", "r9/free", "main", "r10",
            "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import briefsearch as bs  # noqa: E402
import clear_rule as cr  # noqa: E402
import confirm25 as c25  # noqa: E402
import forms10  # noqa: E402
import gold  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
INF = float("inf")
W_HOTEL, W_NOTYPE, W_GH = 545, 994, 490  # the label-group mix (fixed in R10-25)
LIMIT_SHARE, LIMIT_RATIO = 0.50, 0.30
DELTA = 2.0  # points: the tolerance of D1 and D2
DRAWS, SEED = 2000, 20261112
DEV_PASS = ("sonnet", "sol", "gemma")  # the held-out models that met the rule against the word rule in development
DEV_WHOLE = ("sol", "gemma")  # ... with the whole interval
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
SHA256 = {EXPLORE / "r10/analysis/clear_rule.py": "e8cd2490a137a888a3463420f7da4349f29b645fb780a72288400cbaa7291794",
          EXPLORE / "r10/briefsearch.py": "2615e6ac412c49ee507c6b2a5d76441df1e2d404ec789a33b9b6963d9fe09dce"}
GATES = ("planned", "clear_no")
POLICIES = ("original", "planned", "clear_no", "relax_any", "relax_hotel_only", "soft", "always", "word_rule")
SYMBOLIC = ("original", "relax_any", "relax_hotel_only", "soft", "always", "word_rule")
NAME = {"planned": "verifier, planned gate", "clear_no": "verifier, clear-no gate", "relax_any": "relaxation policy",
        "relax_hotel_only": "relaxation policy, hotel-only filters", "soft": "soft type filter",
        "always": "always remove", "word_rule": "word rule as a repair", "original": "original"}
WANT = {"NT": None, "H": "hotel", "G": "guesthouse"}


class Read(NamedTuple):
    fields: dict  # the parsed original answer (F0 fields)
    answer: str  # the verifier answer ("yes", "no", "unclear"), or None when the read needs none or has none


def check_hashes():
    for path, want in SHA256.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != want:
            sys.exit(f"Stopped. {path.relative_to(EXPLORE)} differs from the SHA-256 that R10-25 fixed.")


def ho(t):
    return c25.hotel_only(t)


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


# ------------------------------------------------------------------------------------------------ rows and loaders
def parse_row(row, cell):
    """The parsed answer of a stored row, or None (failed row, output cap, or no parse)."""
    if row is None or row.get("type") != "succeeded" or row.get("stop") in CUT:
        return None
    try:
        return forms10.parse(cell, row.get("text", ""))
    except (ValueError, KeyError, TypeError, RuntimeError):
        return None


def rows_of(folder, name="raw.jsonl"):
    assert not folder.startswith("em"), f"refused: {folder}"
    path = EXPLORE / folder / name
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else None


def split_cid(cid):
    _name, did, cell, read = cid.split("-")
    return did + ".json", cell, int(read)


def verifier_rows(model, name="raw.jsonl"):
    """{(dialogue, read): parsed verifier answer or None} of the run of `model`, or None when the run has no file.
    A row whose key is not a call key of R10-25 stops the analysis."""
    run = c25.RUN_OF[model]
    rows = rows_of(run, name)
    if rows is None:
        return None
    keys = set(c25.call_keys(model))
    out = {}
    for r in rows:
        d, cell, read = split_cid(r["custom_id"])
        if cell != c25.CELL or (d, read) not in keys:
            sys.exit(f"Stopped. {run}/{name}: the row {r['custom_id']} is not a request of R10-25.")
        out[(d, read)] = parse_row(r, cell)
    return out


def heldout_model(model, vrows):
    """(base, missing): base = {(dialogue, read): Read} of the reads that enter; missing counts per (set, reason).
    vrows None: no verifier run, so the base holds the valid originals (symbolic policies only)."""
    s, _ = SETS
    where = {d: k for k in ("NT", "H", "G") for d in s[k]}
    base, missing = {}, collections.Counter()
    for (d, r), f in c25.original_reads(model).items():
        tag = (where[d], "read 1" if r == 1 else "reads 2-3")
        if f is None:
            missing[tag + ("original answer not valid",)] += 1
            continue
        if ho(f["type"]) and vrows is not None:
            v = vrows.get((d, r))
            if v is None:
                missing[tag + ("verifier answer missing or not valid",)] += 1
                continue
            base[(d, r)] = Read(f, v["answer"])
        else:
            base[(d, r)] = Read(f, None)
    return base, missing


def dev_model(folder, ids, base_folder=None):
    """{(dialogue, read): Read} of a development run: reads whose f0 answer and verifier answer are both valid (the
    base of Table 3). ids: the dialogues to keep."""
    got = {}
    for fld in (folder,) + ((base_folder,) if base_folder else ()):
        for r in rows_of(fld):
            d, cell, read = split_cid(r["custom_id"])
            if d in ids and cell in ("f0", "verify") and (fld == folder or cell == "f0"):
                got[(d, cell, read)] = parse_row(r, cell)
    out = {}
    for (d, cell, read), x in got.items():
        v = got.get((d, "verify", read))
        if cell == "f0" and x is not None and v is not None:
            out[(d, read)] = Read(x, v["answer"])
    return out


# ------------------------------------------------------------------------------------------------ policies
def gate(x, kind):
    f = x.fields
    if kind == "original" or not ho(f["type"]):
        return f
    if kind == "planned":
        return forms10.b_verify(f, x.answer)
    if kind == "clear_no":  # the post hoc gate of the paper (b_analyze.POSTHOC): only "no" removes the filter
        out = dict(f)
        if x.answer == "no":
            out["type"] = None
        return out
    raise ValueError(kind)


def policy_fields(x, policy, stated):
    if policy in ("original", "relax_any", "relax_hotel_only", "soft"):
        return x.fields
    if policy in GATES:
        return gate(x, policy)
    if policy in ("always", "word_rule"):
        out = dict(x.fields)
        if ho(out["type"]) and not (policy == "word_rule" and stated):
            out["type"] = None
        return out
    raise ValueError(policy)


def show(db, fields, policy):
    """(displayed venues, database searches) for one answer under one display policy. The code of repair_rule.show."""
    rows = bs.search(db, fields)
    t = fields.get("type")
    if policy in ("relax_any", "relax_hotel_only"):
        acts = not rows and t is not None and (policy == "relax_any" or ho(t))
        if acts:
            wide = bs.search(db, {**fields, "type": None})
            return (wide if wide else rows)[:5], 2
        return rows[:5], 1
    if policy == "soft":
        if len(rows) >= 5 or t is None:
            return rows[:5], 1
        shown = rows[:5]
        names = {v["name"] for v in shown}
        for v in bs.search(db, {**fields, "type": None}):
            if len(shown) >= 5:
                break
            if v["name"] not in names:
                shown.append(v)
                names.add(v["name"])
        return shown, 2
    return rows[:5], 1


def sees(shown, brief, want):
    return any(bs.fits(v, brief) and (want is None or v["type"] == want) for v in shown)


def selected(md, mode):
    """{dialogue: [Read, ...]}: read 1 only ("read1") or every base read ("mean"), in read order."""
    by = collections.defaultdict(list)
    for (d, r), x in sorted(md.items(), key=lambda kv: kv[0][1]):
        if mode == "mean" or r == 1:
            by[d].append(x)
    return by


# ------------------------------------------------------------------------------------------------ value level
def value_pairs(md, ids, kind, mode, stated=None):
    """{d: (mean original hotel-only, mean hotel-only after the gate)} over the selected reads, in the order of ids.
    kind "word_rule" is the word rule as a repair."""
    by = selected(md, mode)
    out = {}
    for d in ids:
        xs = by.get(d)
        if xs:
            if kind == "word_rule":
                b = [ho(policy_fields(x, "word_rule", stated[d])["type"]) for x in xs]
            else:
                b = [ho(gate(x, kind)["type"]) for x in xs]
            out[d] = (mean(ho(x.fields["type"]) for x in xs), mean(b))
    return out


def text_ratio(g, wh, wnt):
    """Loss per value removed against a text reference: lost on the stated dialogues of H; removed on NT."""
    removed = sum(a - b for a, b in g["nt"])
    lost = sum(a - b for a, b in g["st"])
    n_h = len(g["st"]) + len(g["ns"])
    return lost / n_h * wh / (removed / len(g["nt"]) * wnt) if removed > 0 else INF


def brief_ratio(g, wh, wnt):
    removed = sum(a - b for a, b in g["nt"])
    lost = sum(a - b for a, b in g["h"])
    return lost / len(g["h"]) * wh / (removed / len(g["nt"]) * wnt) if removed > 0 else INF


def share_removed(g):
    orig = sum(a for a, _ in g["nt"])
    return sum(a - b for a, b in g["nt"]) / orig if orig > 0 else -INF


def verdict(share, ratio, removed):
    """(meets at the point estimates, meets with the whole interval); share and ratio are [point, low, high]."""
    point = bool(removed > 0 and share[0] >= LIMIT_SHARE and ratio[0] <= LIMIT_RATIO)
    whole = bool(removed > 0 and share[1] >= LIMIT_SHARE and ratio[2] <= LIMIT_RATIO)
    return point, whole


def text_block(nt, h, stated, wh=W_HOTEL, wnt=W_NOTYPE):
    """The word-rule reference: three bootstrap groups (NT, stated H, other H), in this order."""
    g = {"nt": list(nt.values()), "st": [p for d, p in h.items() if stated[d]],
         "ns": [p for d, p in h.items() if not stated[d]]}
    if not g["nt"] or not (g["st"] or g["ns"]):
        return None
    share = list(stats.cluster_bootstrap(g, share_removed, DRAWS, SEED))
    ratio = list(stats.cluster_bootstrap(g, lambda s: text_ratio(s, wh, wnt), DRAWS, SEED))
    removed = sum(a - b for a, b in g["nt"])
    point, whole = verdict(share, ratio, removed)
    return {"dialogues": {"NT": len(g["nt"]), "H stated": len(g["st"]), "H not stated": len(g["ns"])},
            "original_values_NT": sum(a for a, _ in g["nt"]), "removed": removed,
            "lost_stated": sum(a - b for a, b in g["st"]), "share_removed": share, "ratio": ratio,
            "meets_point": point, "meets_whole": whole}


def brief_block(nt, h, wh=W_HOTEL, wnt=W_NOTYPE):
    g = {"nt": list(nt.values()), "h": list(h.values())}
    if not g["nt"] or not g["h"]:
        return None
    share = list(stats.cluster_bootstrap(g, share_removed, DRAWS, SEED))
    ratio = list(stats.cluster_bootstrap(g, lambda s: brief_ratio(s, wh, wnt), DRAWS, SEED))
    removed = sum(a - b for a, b in g["nt"])
    point, whole = verdict(share, ratio, removed)
    return {"dialogues": {"NT": len(g["nt"]), "H": len(g["h"])}, "removed": removed,
            "lost": sum(a - b for a, b in g["h"]), "share_removed": share, "ratio": ratio,
            "meets_point": point, "meets_whole": whole}


def label_cells(md, groups, kind, mode):
    """stats.trade cells: per label group, one row (original hits, reads, gate hits, reads) per dialogue."""
    by = selected(md, mode)
    out = {}
    for grp, ids in groups.items():
        rows_ = []
        for d in ids:
            xs = by.get(d)
            if xs:
                rows_.append((sum(ho(x.fields["type"]) for x in xs), len(xs),
                              sum(ho(gate(x, kind)["type"]) for x in xs), len(xs)))
        out[grp] = rows_
    return out


def label_block(cells, sizes, wrong, correct):
    if not all(cells.get(g) for g in sizes):
        return None
    (removed, lost, ratio), lo, hi = stats.trade_interval(cells, sizes, DRAWS, SEED, wrong=wrong, correct=correct)

    def share(c):
        orig = sum(sum(r[0] for r in c[g]) / sum(r[1] for r in c[g]) * sizes[g] for g in wrong)
        rem = stats.trade(c, sizes, wrong, correct)[0]
        return rem / orig if orig > 0 else -INF
    sh = list(stats.cluster_bootstrap(cells, share, DRAWS, SEED))
    point, whole = verdict(sh, [ratio, lo, hi], removed)
    return {"dialogues": {g: len(cells[g]) for g in sizes}, "removed": removed, "lost": lost, "share_removed": sh,
            "ratio": [ratio, lo, hi], "meets_point": point, "meets_whole": whole}


def value_level(md, S, stated, mode, label_groups=None, sizes=None, wrong=None, correct=None):
    out = {}
    for kind in GATES + ("word_rule",):
        nt = value_pairs(md, S["NT"], kind, mode, stated)
        h = value_pairs(md, S["H"], kind, mode, stated)
        e = {"word_rule": text_block(nt, h, stated), "brief": brief_block(nt, h),
             "evaluated_mix": {"word_rule": text_block(nt, h, stated, len(S["H"]), len(S["NT"])),
                               "brief": brief_block(nt, h, len(S["H"]), len(S["NT"]))}}
        if S.get("G"):
            gp = value_pairs(md, S["G"], kind, mode, stated)
            orig = sum(a for a, _ in gp.values())
            e["G"] = {"dialogues": len(gp), "original_values": orig, "removed": sum(a - b for a, b in gp.values()),
                      "share_removed": (sum(a - b for a, b in gp.values()) / orig) if orig else None}
        if label_groups and kind in GATES:
            e["label"] = label_block(label_cells(md, label_groups, kind, mode), sizes, wrong, correct)
        out[kind] = e
    return out


def verifier_answers(md, S, mode="read1"):
    by = selected(md, mode)
    out = {}
    for side in ("NT", "H", "G"):
        c = collections.Counter(x.answer for d in S.get(side, []) for x in by.get(d, []) if ho(x.fields["type"]))
        out[side] = {a: c.get(a, 0) for a in forms10.VERIFY_VALUES}
    return out


# ------------------------------------------------------------------------------------------------ display level
def display_level(md, S, stated, data, db, mode, policies=POLICIES):
    by = selected(md, mode)
    per = collections.defaultdict(dict)  # (side, policy) -> {d: mean miss}
    searches, answers = collections.Counter(), 0
    relax_h = {"dialogues_changed": set(), "stated_changed": set(), "answers_changed_show_guesthouse": 0}
    for side in ("NT", "H", "G"):
        for d in S.get(side, []):
            xs = by.get(d)
            if not xs:
                continue
            brief = bs.brief_of(data[d])
            acc = collections.defaultdict(list)
            for x in xs:
                answers += 1
                for p in policies:
                    f = policy_fields(x, p, stated[d])
                    shown, n = show(db, f, p)
                    searches[p] += n
                    acc[p].append(0.0 if sees(shown, brief, WANT[side]) else 1.0)
                    if side == "H" and p == "relax_any":
                        if [v["name"] for v in shown] != [v["name"] for v in bs.search(db, f)[:5]]:
                            relax_h["dialogues_changed"].add(d)
                            if stated[d]:
                                relax_h["stated_changed"].add(d)
                            relax_h["answers_changed_show_guesthouse"] += any(v["type"] == "guesthouse" for v in shown)
            for p in policies:
                per[(side, p)][d] = mean(acc[p])
    o = {side: per[(side, "original")] for side in ("NT", "H", "G")}
    res = {"answers": answers, "dialogues": {s: len(o[s]) for s in o},
           "original": {"failures_NT": sum(o["NT"].values()), "losses_H": sum(o["H"].values()),
                        "failures_G": sum(o["G"].values())},
           "searches_per_answer": {p: searches[p] / answers if answers else None for p in policies},
           "relax_any_on_H": {"dialogues_changed": len(relax_h["dialogues_changed"]),
                              "stated_dialogues_changed": len(relax_h["stated_changed"]),
                              "answers_changed_show_guesthouse": relax_h["answers_changed_show_guesthouse"]}}
    for p in policies[1:]:
        a = {side: per[(side, p)] for side in o}
        pnt = [(o["NT"][d], a["NT"][d]) for d in o["NT"]]
        ph = [(o["H"][d], a["H"][d]) for d in o["H"]]
        pg = [(o["G"][d], a["G"][d]) for d in o["G"]]
        e = {"net_avoided_NT": sum(x - y for x, y in pnt), "net_added_H": sum(y - x for x, y in ph),
             "failures_caused_NT": sum(max(y - x, 0) for x, y in pnt),
             "failures_ended_NT": sum(max(x - y, 0) for x, y in pnt),
             "losses_caused_H": sum(max(y - x, 0) for x, y in ph), "losses_ended_H": sum(max(x - y, 0) for x, y in ph),
             "failures_G": sum(y for _, y in pg), "net_avoided_G": sum(x - y for x, y in pg)}
        if p in ("relax_any", "relax_hotel_only", "soft"):  # no added error by construction: check each dialogue
            assert all(y <= x + 1e-12 for x, y in pnt + ph + pg), f"{p} added an error"
        if p in GATES and pnt and ph:
            def stat(gr):
                ben = sum(x - y for x, y in gr["nt"]) / len(gr["nt"])
                cost = sum(y - x for x, y in gr["h"]) / len(gr["h"])
                return cost * W_HOTEL / (ben * W_NOTYPE) if ben > 0 else INF
            e["display_loss_ratio"] = list(stats.cluster_bootstrap({"nt": pnt, "h": ph}, stat, DRAWS, SEED))
        res[p] = e
    if "planned" in policies:
        ids = list(o["NT"])
        n = len(ids)
        units = [(per[("NT", "planned")][d], per[("NT", "relax_any")][d], per[("NT", "soft")][d]) for d in ids]
        for name, k in (("relax_minus_verifier", 1), ("soft_minus_verifier", 2)):
            pt, lo, hi = stats.cluster_bootstrap({"nt": units}, lambda g, k=k: sum(u[0] - u[k] for u in g["nt"]),
                                                 DRAWS, SEED)
            pts = [100 * x / n for x in (pt, lo, hi)]
            res[name] = {"dialogues": [pt, lo, hi], "points": pts, "not_worse": bool(pts[1] >= -DELTA - 1e-12),
                         "equivalent": bool(pts[1] >= -DELTA - 1e-12 and pts[2] <= DELTA + 1e-12)}
    return res


# ------------------------------------------------------------------------------------------------ predictions
def predictions(res):
    """res: {model: {"value": ..., "display": ...}} of the models of M (with verifier answers)."""
    M = [m for m in c25.PANEL if m in res]
    out = {}
    if not M:
        return {k: {"verdict": "n/a"} for k in ("V1", "V1w", "V2", "V3", "V4", "D1", "D2")}
    k = sum(m in M for m in DEV_PASS)
    meets = [m for m in M if res[m]["value"]["planned"]["word_rule"]["meets_point"]]
    out["V1"] = {"k": k, "models_that_meet": meets, "verdict": "holds" if len(meets) >= k else "fails"}
    w = [m for m in DEV_WHOLE if m in M]
    out["V1w"] = {"models": {m: res[m]["value"]["planned"]["word_rule"]["meets_whole"] for m in w},
                  "verdict": "n/a" if not w else ("holds" if all(res[m]["value"]["planned"]["word_rule"]["meets_whole"]
                                                                 for m in w) else "fails")}
    if "sol" in M:
        cn = res["sol"]["value"]["clear_no"]
        out["V2"] = {"verdict": "holds" if cn["word_rule"]["meets_point"] else "fails"}
        lab = cn.get("label")
        out["V4"] = {"verdict": "n/a" if lab is None else ("holds" if lab["meets_point"] else "fails")}
    else:
        out["V2"] = out["V4"] = {"verdict": "n/a"}
    b = [m for m in M if res[m]["value"]["planned"]["brief"]["meets_point"]]
    out["V3"] = {"models_that_meet": b, "verdict": "holds" if not b else "fails"}
    d1 = {m: res[m]["display"]["relax_minus_verifier"]["not_worse"] for m in M}
    out["D1"] = {"models": d1, "verdict": "holds" if all(d1.values()) else "fails"}
    d2 = {m: bool(res[m]["display"]["soft_minus_verifier"]["not_worse"]
                  and res[m]["display"]["soft_minus_verifier"]["dialogues"][0] >= -1e-12) for m in M}
    out["D2"] = {"models": d2, "verdict": "holds" if all(d2.values()) else "fails"}
    return out


# ------------------------------------------------------------------------------------------------ report
def f2(x):
    if x is None:
        return "-"
    if isinstance(x, float) and math.isinf(x):
        return "no upper limit" if x > 0 else "not defined"
    return f"{x:.2f}"


def pc(x):
    return "-" if x is None or (isinstance(x, float) and math.isinf(x)) else f"{100 * x:.1f}%"


def ci(v, fmt=f2):
    return f"{fmt(v[0])} [{fmt(v[1])}, {fmt(v[2])}]"


def yn(b):
    return "yes" if b else "no"


def clean(x):
    if isinstance(x, float):
        return "inf" if math.isinf(x) and x > 0 else ("-inf" if math.isinf(x) else x)
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, set):
        return sorted(x)
    return x


def render(result):
    L = ["# R10-25: held-out confirmation of the repair results", "",
         "Status: exploratory, fixed in `prototypes/explore/PROTOCOL.md` (amendment R10-25) before any computation of "
         "these outcomes. Data: the stage-1 held-out answers (read 1, form t_legacy) and the verifier runs "
         "`ern_<model>`. Mix: the label-group mix (545 hotel to 994 no-type). Limits: share removed 50% or more; loss "
         "ratio 0.30 or less. Intervals: 95%, 2,000 bootstrap samples, seed 20261112. Tolerance of D1 and D2: "
         f"{DELTA:.1f} points.", "",
         f"- Models with verifier answers (M): {', '.join(result['M']) or 'none'}.",
         f"- Models without verifier answers: {', '.join(m for m in c25.PANEL if m not in result['M']) or 'none'}.", "",
         "## Predictions", "", "| Prediction | Verdict | Detail |", "|---|---|---|"]
    for k, v in result["predictions"].items():
        detail = {kk: vv for kk, vv in v.items() if kk != "verdict"}
        L.append(f"| {k} | {v['verdict']} | {json.dumps(clean(detail)) if detail else '-'} |")
    L += ["", "## Value level (read 1)", ""]
    for ref, title in (("word_rule", "Against the word rule (primary)"), ("brief", "Against the brief"),
                       ("label", "Against the corpus label (three label groups)")):
        L += [f"### {title}", "", "| Model | Gate | Dialogues | Share removed [95% interval] | Loss ratio [95% interval] "
              "| Meets: point / whole interval |", "|---|---|---|---|---|---|"]
        for m in result["M"]:
            for gk in GATES:
                b = result["models"][m]["read1"]["value"][gk].get(ref)
                if b is None:
                    continue
                L.append(f"| {m} | {NAME[gk]} | {json.dumps(b['dialogues'])} | {ci(b['share_removed'], pc)} | "
                         f"{ci(b['ratio'])} | {yn(b['meets_point'])} / {yn(b['meets_whole'])} |")
        L.append("")
    L += ["### Verifier answers for the hotel-only filters (read 1; yes / no / unclear)", "",
          "| Model | NT | H | G |", "|---|---|---|---|"]
    for m in result["M"]:
        va = result["models"][m]["read1"]["verifier_answers"]
        L.append(f"| {m} | " + " | ".join(" / ".join(str(va[s][a]) for a in forms10.VERIFY_VALUES)
                                          for s in ("NT", "H", "G")) + " |")
    L += ["", "## Display level (read 1)", "",
          "Net visible failures avoided on NT and net visible losses added on H, in dialogues. Paired differences on "
          "NT: policy minus verifier (planned gate), in dialogues and in points.", "",
          "| Model | Original: failures / losses | Avoided: verifier / relaxation / soft | Added: verifier | "
          "Relaxation − verifier, points [95%] | Soft − verifier, points [95%] |", "|---|---|---|---|---|---|"]
    for m in result["M"]:
        dsp = result["models"][m]["read1"]["display"]
        o = dsp["original"]
        L.append(f"| {m} | {o['failures_NT']:g} / {o['losses_H']:g} | {dsp['planned']['net_avoided_NT']:g} / "
                 f"{dsp['relax_any']['net_avoided_NT']:g} / {dsp['soft']['net_avoided_NT']:g} | "
                 f"{dsp['planned']['net_added_H']:g} | {ci(dsp['relax_minus_verifier']['points'])} | "
                 f"{ci(dsp['soft_minus_verifier']['points'])} |")
    L += ["", "### Symbolic policies on every model (read 1; no model call)", "",
          "| Model | Dialogues NT / H / G | Original: failures / losses / G failures | Avoided: relaxation / soft / "
          "word rule | Added: word rule / always | Relaxation changes H displays (stated) |",
          "|---|---|---|---|---|---|"]
    for m in c25.PANEL:
        dsp = result["models"][m]["symbolic"]
        o = dsp["original"]
        L.append(f"| {m} | {dsp['dialogues']['NT']} / {dsp['dialogues']['H']} / {dsp['dialogues']['G']} | "
                 f"{o['failures_NT']:g} / {o['losses_H']:g} / {o['failures_G']:g} | "
                 f"{dsp['relax_any']['net_avoided_NT']:g} / {dsp['soft']['net_avoided_NT']:g} / "
                 f"{dsp['word_rule']['net_avoided_NT']:g} | {dsp['word_rule']['net_added_H']:g} / "
                 f"{dsp['always']['net_added_H']:g} | {dsp['relax_any_on_H']['dialogues_changed']} "
                 f"({dsp['relax_any_on_H']['stated_dialogues_changed']}) |")
    L += ["", "## Sensitivity: the mean of the base reads", "", "| Model | Planned gate vs word rule: share / ratio / "
          "meets | Relaxation − verifier, points | Soft − verifier, points |", "|---|---|---|---|---|"]
    for m in result["M"]:
        s = result["models"][m]["mean"]
        w = s["value"]["planned"]["word_rule"]
        L.append(f"| {m} | {pc(w['share_removed'][0])} / {f2(w['ratio'][0])} / {yn(w['meets_point'])} | "
                 f"{ci(s['display']['relax_minus_verifier']['points'])} | "
                 f"{ci(s['display']['soft_minus_verifier']['points'])} |")
    L += ["", "## Missing answers", ""]
    for m in c25.PANEL:
        miss = result["models"][m]["missing"]
        L.append(f"- {m}: " + ("; ".join(f"{k}: {v}" for k, v in sorted(miss.items())) or "none"))
    L += ["", "The JSON file holds every value, also the evaluated mix, the guesthouse briefs (G), the caused and "
          "ended errors, the searches per answer and the display loss ratios."]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ main modes
SETS = None


def heldout_context():
    global SETS
    import runs
    data, _g = runs.context()
    SETS = c25.sets(data)
    c25.originals(data)  # the frozen loader reads the held-out answers once, with this data
    s, _ = SETS
    stated = {d: cr.label(data[d]) == "hotel_only" for k in ("NT", "H", "G") for d in s[k]}
    assert sum(stated[d] for d in s["NT"]) == c25.STATED["NT"] and sum(stated[d] for d in s["H"]) == c25.STATED["H"]
    labels = {"LN": s["LN"], "LG": s["LG"], "LH": s["LH"]}
    return data, gold.hotel_db(), s, stated, labels


def analyse(md, data, db, S, stated, labels, with_verifier):
    out = {}
    for mode in ("read1", "mean"):
        if with_verifier:
            out[mode] = {"value": value_level(md, S, stated, mode, labels, {"LN": W_NOTYPE, "LG": W_GH, "LH": W_HOTEL},
                                              ("LN", "LG"), "LH"),
                         "display": display_level(md, S, stated, data, db, mode),
                         "verifier_answers": verifier_answers(md, S, mode)}
    return out


def main():
    check_hashes()
    have = [m for m in c25.PANEL if (EXPLORE / c25.RUN_OF[m] / "raw.jsonl").exists()]
    if not have:
        sys.exit("Stopped. No run ern_<model> is fetched, so nothing is computed. Use --selftest or --pilot.")
    data, db, s, stated, labels = heldout_context()
    S = {k: s[k] for k in ("NT", "H", "G")}
    result = {"amendment": "R10-25", "exploratory": True, "M": have, "models": {}}
    res_m = {}
    for m in c25.PANEL:
        vrows = verifier_rows(m) if m in have else None
        md, missing = heldout_model(m, vrows)
        sym_md, _ = heldout_model(m, None)
        e = {"missing": {" | ".join(k): v for k, v in missing.items()},
             "symbolic": display_level(sym_md, S, stated, data, db, "read1", SYMBOLIC)}
        if vrows is not None:
            e.update(analyse(md, data, db, S, stated, labels, True))
            res_m[m] = e["read1"]
        result["models"][m] = e
        print(f"{m} done", flush=True)
    result["predictions"] = predictions(res_m)
    OUT.mkdir(exist_ok=True)
    (OUT / "heldout_confirm.json").write_text(json.dumps(clean(result), indent=1))
    (OUT / "heldout_confirm.md").write_text(render(result))
    print(f"wrote {OUT / 'heldout_confirm.md'} and {OUT / 'heldout_confirm.json'}")
    for k, v in result["predictions"].items():
        print(k, v["verdict"])


def pilot():
    """The join of the pilot verifier rows with the held-out answers: counts only, no outcome value."""
    check_hashes()
    data, db, s, stated, labels = heldout_context()
    where = {d: k for k in ("NT", "H", "G") for d in s[k]}
    L = ["# R10-25 pilot join (counts only; no outcome value)", "",
         "| Run | Pilot rows | Request of R10-25 | Original answer has a hotel-only filter | Verifier answer parses | "
         "Sets (NT / H / G) |", "|---|---|---|---|---|---|"]
    ok = True
    for m in c25.PANEL:
        run = c25.RUN_OF[m]
        rows = rows_of(run, "pilot_raw.jsonl")
        if rows is None:
            L.append(f"| {run} | no pilot | - | - | - | - |")
            continue
        keys = set(c25.call_keys(m))
        orig = c25.original_reads(m)
        n_req = n_ho = n_parse = 0
        sides = collections.Counter()
        for r in rows:
            d, cell, read = split_cid(r["custom_id"])
            n_req += (d, read) in keys and cell == c25.CELL
            f = orig.get((d, read))
            n_ho += f is not None and ho(f["type"])
            n_parse += parse_row(r, cell) is not None
            sides[where.get(d, "?")] += 1
        ok &= n_req == n_ho == n_parse == len(rows)
        L.append(f"| {run} | {len(rows)} | {n_req} | {n_ho} | {n_parse} | {sides['NT']} / {sides['H']} / "
                 f"{sides['G']} |")
    L += ["", f"Join: {'PASS' if ok else 'FAIL'}. Each pilot row must be a request of R10-25, pair with a valid original "
          "answer with a hotel-only filter, and parse."]
    OUT.mkdir(exist_ok=True)
    (OUT / "heldout_confirm_pilot.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return ok


# ------------------------------------------------------------------------------------------------ self-test
# Printed values of the paper (Table D13 with the evaluated mix; Table 3; Table D1), for the check of the reproduction.
PAPER_D13 = {  # model: {gate: (share removed %, word-rule ratio, [low, high], brief ratio)}
    "sonnet": {"planned": (97.4, 0.15, (0.08, 0.22), 0.91), "clear_no": (52.1, 0.11, (0.04, 0.22), 0.61)},
    "sol": {"planned": (76.2, 0.02, (0.00, 0.04), 0.32), "clear_no": (52.7, 0.03, (0.01, 0.06), 0.15)},
    "gemma": {"planned": (94.4, 0.08, (0.04, 0.13), 0.66), "clear_no": (60.1, 0.04, (0.01, 0.08), 0.37)},
}
PAPER_T3 = {  # model: (original failures, original losses, avoided verifier, relaxation, soft, relax - verifier [3],
    #                   soft - verifier [3], added verifier)
    "sonnet": (140, 35, 37, 37, 37, (0, -3, 3), (0, -3, 3), 8),
    "sol": (215, 29, 99, 103, 109, (4, -4, 11), (10, 4, 17), 4),
    "gemma": (206.5, 40.5, 54.5, 55, 58, (0.5, -4.5, 5.5), (3.5, 0.5, 7.5), 5),
}
PAPER_D1_SOL = {"planned": (75.1, 0.55, (0.48, 0.64)), "clear_no": (53.4, 0.25, (0.19, 0.32))}
DEV = {"sonnet": "erb_sonnet", "sol": "erb_sol", "gemma": "ery_gemma"}
FACTOR = (545 / 233) / (994 / 807)


def close(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol


def selftest_dev():
    import runs
    data, g = runs.context()
    db = gold.hotel_db()
    nt = [d for d in g["s1t"] if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    h = [d for d in g["s2"] if gold.brief_type(data[d]) == "hotel"]
    assert (len(nt), len(h)) == (807, 233)
    stated = {d: cr.label(data[d]) == "hotel_only" for d in set(nt) | set(h)}
    S = {"NT": nt, "H": h, "G": []}
    f8 = json.loads((OUT / "repair_limits.json").read_text())
    f5 = json.loads((OUT / "repair_rule.json").read_text())
    bho = json.loads((EXPLORE / "r10/analysis/out/b_hotel_only.json").read_text())["models"]
    num = lambda x: INF if x == "inf" else float(x)  # noqa: E731
    labels = {"S1t": list(g["s1t"]), "S3": list(g["s3"]), "S2": list(g["s2"])}
    for m, folder in DEV.items():
        keep = set(nt) | set(h) | (set(d for v in labels.values() for d in v) if m == "sol" else set())
        md = dev_model(folder, keep)
        stated_all = {**{d: cr.label(data[d]) == "hotel_only" for d in keep}, **stated}
        val = value_level(md, S, stated_all, "mean",
                          {"S1t": labels["S1t"], "S3": labels["S3"], "S2": labels["S2"]} if m == "sol" else None,
                          {"S1t": W_NOTYPE, "S3": W_GH, "S2": W_HOTEL}, ("S1t", "S3"), "S2")
        for gk, key in (("planned", "verifier, planned gate"), ("clear_no", "verifier, clear-no gate")):
            st = f8["part1a_text_reference"]["models"][m][key]
            wr, br = val[gk]["word_rule"], val[gk]["brief"]
            assert all(close(a, b) for a, b in zip(wr["share_removed"], st["share_removed_ci"])), (m, gk, "share")
            assert close(wr["ratio"][0], st["word rule"]["group"]["ratio"]), (m, gk, "ratio")
            assert all(close(a, num(b)) for a, b in zip(wr["ratio"][1:], st["word rule"]["group"]["ci"])), (m, gk)
            assert close(br["ratio"][0], st["brief"]["group"]["ratio"]), (m, gk, "brief")
            ev = val[gk]["evaluated_mix"]
            share, ratio, (lo, hi), brief = PAPER_D13[m][gk]
            assert round(100 * wr["share_removed"][0], 1) == share, (m, gk)
            assert round(ev["word_rule"]["ratio"][0], 2) == ratio and round(ev["brief"]["ratio"][0], 2) == brief, (m, gk)
            assert (round(ev["word_rule"]["ratio"][1], 2), round(ev["word_rule"]["ratio"][2], 2)) == (lo, hi), (m, gk)
            assert close(ev["word_rule"]["ratio"][0] * FACTOR, wr["ratio"][0], 1e-9)
        dsp = display_level(md, S, stated_all, data, db, "mean")
        t3 = f8["part2_table3_paired"][m]
        o_f, o_l, av_v, av_r, av_s, rv, sv, add_v = PAPER_T3[m]
        assert (dsp["original"]["failures_NT"], dsp["original"]["losses_H"]) == (o_f, o_l), (m, dsp["original"])
        assert (dsp["planned"]["net_avoided_NT"], dsp["relax_any"]["net_avoided_NT"],
                dsp["soft"]["net_avoided_NT"]) == (av_v, av_r, av_s), m
        assert dsp["planned"]["net_added_H"] == add_v and dsp["relax_any"]["net_added_H"] <= 0, m
        assert all(close(a, num(b)) for a, b in zip(dsp["relax_minus_verifier"]["dialogues"], t3["relax_minus_verify"]))
        assert all(close(a, num(b)) for a, b in zip(dsp["soft_minus_verifier"]["dialogues"], t3["soft_minus_verify"]))
        assert tuple(dsp["relax_minus_verifier"]["dialogues"]) == rv and tuple(dsp["soft_minus_verifier"]["dialogues"]) == sv
        stored = f5["part4_display"][m]["verify"]["group_ratio"]
        assert all(close(a, num(b)) for a, b in zip(dsp["planned"]["display_loss_ratio"], stored)), m
        print(f"  {m}: Table D13 (share removed, word-rule and brief ratios, intervals), Table 3 (counts, paired "
              f"differences, intervals) and the display loss ratio: reproduced")
        if m == "sol":
            for gk, key in (("planned", "verify"), ("clear_no", "verify_no_only (post hoc)")):
                lb, stv = val[gk]["label"], bho["sol"]["trade"][key]
                assert close(lb["removed"], stv["removed"]) and close(lb["ratio"][0], stv["ratio"]), gk
                assert close(lb["ratio"][1], stv["ci"][0]) and close(lb["ratio"][2], stv["ci"][1]), gk
                share, ratio, (lo, hi) = PAPER_D1_SOL[gk]
                assert round(100 * lb["share_removed"][0], 1) == share and round(lb["ratio"][0], 2) == ratio
                assert (round(lb["ratio"][1], 2), round(lb["ratio"][2], 2)) == (lo, hi)
            print("  sol: Table D1 (the label trade of both gates, with the interval): reproduced")


def selftest_constructed():
    """The rules on constructed answers: the base, the pairing, the verdicts, the tolerance and the predictions."""
    db = gold.hotel_db()
    briefs = {"N1.json": {"area": "north"}, "N2.json": {"area": "west"}, "N3.json": {"area": "centre"},
              "H1.json": {"area": "north", "type": "hotel"}, "H2.json": {"area": "centre", "type": "hotel"},
              "H3.json": {"area": "west", "type": "hotel"}}
    data = {d: {"goal": {"hotel": {"info": b}}} for d, b in briefs.items()}
    S = {"NT": ["N1.json", "N2.json", "N3.json"], "H": ["H1.json", "H2.json", "H3.json"], "G": []}
    stated = {"N1.json": False, "N2.json": False, "N3.json": False, "H1.json": True, "H2.json": True,
              "H3.json": False}
    blank = {"name": None, "area": None, "pricerange": None, "stars": None, "type": None, "parking": None,
             "internet": None}
    f = lambda area, t: {**blank, "area": (area,), "type": t}  # noqa: E731
    # A verifier that says "yes" only where the words state the type: no stated loss, so the word rule is met, while
    # the brief counts the loss on H3.
    md = {("N1.json", 1): Read(f("north", ("hotel",)), "no"), ("N2.json", 1): Read(f("west", ("hotel",)), "unclear"),
          ("N3.json", 1): Read(f("centre", None), None), ("H1.json", 1): Read(f("north", ("hotel",)), "yes"),
          ("H2.json", 1): Read(f("centre", ("hotel",)), "yes"), ("H3.json", 1): Read(f("west", ("hotel",)), "no"),
          ("N1.json", 2): Read(f("north", ("hotel",)), "yes")}
    val = value_level(md, S, stated, "read1")
    p, c = val["planned"], val["clear_no"]
    assert p["word_rule"]["removed"] == 2 and p["word_rule"]["lost_stated"] == 0 and p["word_rule"]["meets_point"]
    assert p["brief"]["lost"] == 1 and close(p["brief"]["ratio"][0], (1 / 3 * 545) / (2 / 3 * 994))
    assert p["brief"]["meets_point"]  # 0.27 at the point and 100% removed
    assert not p["brief"]["meets_whole"]  # with 3 dialogues, some samples remove nothing: no upper limit
    assert c["word_rule"]["removed"] == 1 and close(c["word_rule"]["share_removed"][0], 0.5)
    mean_val = value_level(md, S, stated, "mean")  # N1 has a second read with "yes": the mean of the reads is 0.5
    assert close(mean_val["planned"]["word_rule"]["removed"], 1.5)
    # The base: a hotel-only read without a verifier answer leaves; a read without a hotel-only filter stays.
    global SETS
    saved_sets, saved_reads = SETS, c25.original_reads
    try:
        SETS = ({"NT": ["N1.json", "N2.json"], "H": [], "G": []}, {})
        c25.original_reads = lambda model, data=None: {("N1.json", 1): f("north", ("hotel",)),
                                                       ("N2.json", 1): f("west", None), ("N2.json", 2): None}
        base, missing = heldout_model("sol", {})
        assert set(base) == {("N2.json", 1)} and sum(missing.values()) == 2
        base, _ = heldout_model("sol", None)
        assert set(base) == {("N1.json", 1), ("N2.json", 1)} and base[("N1.json", 1)].answer is None
    finally:
        SETS, c25.original_reads = saved_sets, saved_reads
    assert split_cid("ern_sol-PMUL0001-verify-2") == ("PMUL0001.json", "verify", 2)
    # The display: the relaxation policy and the soft type filter add no error; the paired difference and the tolerance.
    dsp = display_level(md, S, stated, data, db, "read1")
    assert dsp["relax_any"]["net_added_H"] <= 0 and dsp["soft"]["net_added_H"] <= 0
    assert dsp["planned"]["net_added_H"] >= 0
    for k in ("relax_minus_verifier", "soft_minus_verifier"):
        x = dsp[k]
        assert close(x["points"][0], 100 * x["dialogues"][0] / 3) and x["not_worse"] == (x["points"][1] >= -DELTA)
    # The predictions: k, n/a and the verdicts, on constructed results.
    def fake(meets=True, whole=True, brief=False, d1=0.0, d2=0.0, label=True):
        wr = {"meets_point": meets, "meets_whole": whole}
        return {"value": {"planned": {"word_rule": wr, "brief": {"meets_point": brief}},
                          "clear_no": {"word_rule": {"meets_point": meets}, "label": {"meets_point": label}}},
                "display": {"relax_minus_verifier": {"not_worse": d1 >= -DELTA, "dialogues": [d1]},
                            "soft_minus_verifier": {"not_worse": d2 >= -DELTA, "dialogues": [d2]}}}
    pr = predictions({m: fake() for m in c25.PANEL})
    assert pr["V1"]["k"] == 3 and all(v["verdict"] == "holds" for v in pr.values()), pr
    pr = predictions({"sol": fake(), "gemma": fake(meets=False), "haiku": fake(meets=True)})
    assert pr["V1"]["k"] == 2 and pr["V1"]["verdict"] == "holds"  # the count, not the names
    pr = predictions({"sol": fake(), "gemma": fake(meets=False, whole=False), "qwen": fake(meets=False)})
    assert pr["V1"]["verdict"] == "fails" and pr["V1w"]["verdict"] == "fails"
    pr = predictions({"gemma": fake(brief=True, d1=-2.5, d2=-0.5)})
    assert pr["V2"]["verdict"] == pr["V4"]["verdict"] == "n/a" and pr["V1"]["k"] == 1
    assert pr["V3"]["verdict"] == "fails" and pr["D1"]["verdict"] == "fails" and pr["D2"]["verdict"] == "fails"
    assert predictions({})["V1"]["verdict"] == "n/a"
    print("  constructed answers: base, pairing, gates, references, verdicts, tolerance and predictions")


def selftest():
    check_hashes()
    assert forms10.VERIFY_SYSTEM.endswith(forms10.VERIFY_QUESTION)
    selftest_constructed()
    selftest_dev()
    print("selftest passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--pilot" in sys.argv:
        sys.exit(0 if pilot() else 1)
    else:
        main()
