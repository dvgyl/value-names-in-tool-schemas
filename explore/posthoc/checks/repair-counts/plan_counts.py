"""Post hoc counts for the the paper plan revision (2026-11-15). No model call, no network call, no paid call.

Usage (from explore/):
    python3 -I posthoc/checks/repair-counts/plan_counts.py [out.json]

Data: the stored development answers that r10/analysis/repair_rule.py reads (the repair folders
of b_analyze.SOURCES and ery_deepseek, ery_qwen, ery_gemma), through the same loaders (r10/analysis/repair_loaders.py, the loaders of the
independent check). The loaders refuse any folder whose name starts with "em". This script opens no sealed file, no key file,
no .env file and no held-out answer. It reuses the display and policy functions of repair_rule.py without change.

Part A (plan item NS-03). On the 233 hotel briefs (89 stated by the word rule), for each display policy: the number of
        dialogues whose display shows at least one guesthouse while the original display shows none ("newly shows a
        guesthouse"). Models with two answers contribute the mean of their answers, so halves occur. A display that
        newly shows a guesthouse on a stated brief shows a venue type that the traveller's words exclude.
Part B (plan item NS-09). On the 1,040 evaluated dialogues (807 no-type and 233 hotel briefs), the share of base
        answers with a hotel-only filter: the verifier calls per answer that a service would need if it called the
        verifier only for these answers. In the runs, the verifier was called once for every answer.
Part C (plan item NS-05). On the three label groups of the trade rule (994 no-type, 490 guesthouse, 545 hotel), the raw
        transitions per dialogue of each repair against the original form (main count, hotel-only filters):
        unsupported filters removed and added (no-type and guesthouse groups), supported filters lost and gained
        (hotel group). Each dialogue gives the mean over its valid original answers and the mean over its valid repair
        answers, as in b_analyze.cells. The net values (removed - added, lost - gained) are checked against the stored
        trade values of r10/analysis/out/b_hotel_only.json.
"""
import collections
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]  # explore/ of the repository
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent / "out/plan_counts.json"
sys.argv = sys.argv[:1]  # repair_rule reads sys.argv at import
spec = importlib.util.spec_from_file_location("nf5", ROOT / "r10/analysis/repair_rule.py")
F5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F5)
V, B, bs, cr, gold, runs = F5.V, F5.B, F5.bs, F5.cr, F5.gold, F5.runs
ho, mean = F5.ho, F5.mean

DISPLAY_POLICIES = ("verify", "clear_no", "relax_any", "soft", "word_rule", "always")
REPAIRS = ("b_list", "b_shot", "b_evidence", "verify", B.POSTHOC)


def has_guesthouse(shown):
    return any(v["type"] == "guesthouse" for v in shown)


def part_a(G, db, h, stated):
    out = {}
    for m, got in G.items():
        newly = collections.defaultdict(lambda: {"stated": 0.0, "not_stated": 0.0})
        shows = collections.defaultdict(lambda: {"stated": 0.0, "not_stated": 0.0})
        n = {"stated": 0, "not_stated": 0}
        for d in h:
            reads = F5.base_reads(got, d)
            if not reads:
                continue
            key = "stated" if stated[d] else "not_stated"
            n[key] += 1
            acc_new, acc_show = collections.defaultdict(list), collections.defaultdict(list)
            for rd in reads:
                f0 = F5.policy_answer(got, d, rd, "original", stated[d])
                orig_shown, _ = F5.show(db, f0, "original")
                acc_show["original"].append(has_guesthouse(orig_shown))
                for p in DISPLAY_POLICIES:
                    f = F5.policy_answer(got, d, rd, p, stated[d])
                    shown, _ = F5.show(db, f, p)
                    acc_show[p].append(has_guesthouse(shown))
                    acc_new[p].append(has_guesthouse(shown) and not has_guesthouse(orig_shown))
            for p, vals in acc_new.items():
                newly[p][key] += mean(vals)
            for p, vals in acc_show.items():
                shows[p][key] += mean(vals)
        out[m] = {"dialogues": n, "newly_shows_guesthouse": dict(newly), "shows_guesthouse": dict(shows)}
    return out


def part_b(G, nt, h):
    out = {}
    for m, got in G.items():
        k = n = 0
        for d in nt + h:
            for rd in F5.base_reads(got, d):
                n += 1
                k += ho(got[(d, "f0", rd)]["type"])
        out[m] = {"answers": n, "hotel_only": k, "share": k / n if n else None}
    return out


def part_c(G, ids, stored):
    out = {}
    for m, got in G.items():
        if m not in stored:
            continue
        row = {}
        for arm in REPAIRS:
            src = "verify" if arm in ("verify", B.POSTHOC) else arm
            t = {"removed": 0.0, "added": 0.0, "lost": 0.0, "gained": 0.0}
            dialogues = collections.Counter()
            for grp in ("S1t", "S3", "S2"):
                for d in ids[grp]:
                    f0 = [B.scored(got, d, "f0", r) for r in B.reads_of(got, d, "f0")]
                    f0 = [x for x in f0 if x is not None]
                    ar = [B.scored(got, d, arm, r) for r in B.reads_of(got, d, src)]
                    ar = [x for x in ar if x is not None]
                    if not (f0 and ar):
                        continue
                    dialogues[grp] += 1
                    a, b = mean(ho(x["type"]) for x in f0), mean(ho(x["type"]) for x in ar)
                    if grp == "S2":
                        t["lost"] += max(a - b, 0.0)
                        t["gained"] += max(b - a, 0.0)
                    else:
                        t["removed"] += max(a - b, 0.0)
                        t["added"] += max(b - a, 0.0)
            if not dialogues:
                continue
            st = stored[m]["trade"].get(arm, {})
            t["net_removed"] = t["removed"] - t["added"]
            t["net_lost"] = t["lost"] - t["gained"]
            t["stored_net_removed"] = st.get("removed")
            t["stored_net_lost"] = st.get("lost")
            t["dialogues"] = dict(dialogues)
            row[arm] = t
        out[m] = row
    return out


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    ids = {k: list(g[B.GROUP_KEY[k]]) for k in B.SIZES}
    group_of = {d: k for k, lst in ids.items() for d in lst}
    nt = [d for d in ids["S1t"] if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    h = [d for d in ids["S2"] if gold.brief_type(data[d]) == "hotel"]
    assert (len(nt), len(h)) == (807, 233)
    every = sorted(set(d for lst in ids.values() for d in lst))
    stated = {d: cr.label(data[d]) == "hotel_only" for d in every}
    assert sum(stated[d] for d in h) == 89
    G = V.gots(data, group_of)
    stored = json.loads((ROOT / "r10/analysis/out/b_hotel_only.json").read_text())["models"]
    out = {"post_hoc": True, "note": "the paper plan revision counts; see the docstring"}
    out["part_a_explicit_constraint_displays"] = part_a(G, db, h, stated)
    print("part A done", flush=True)
    out["part_b_triggered_verifier_calls"] = part_b(G, nt, h)
    out["part_c_raw_transitions"] = part_c(G, ids, stored)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
