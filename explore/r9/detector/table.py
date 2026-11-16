"""X0 detector table and the X3 and Z4 pair selection (PROTOCOL.md section "X3 and Z4" and its amendment 1). Local
files only, no API call.

Writes `table.tsv` (every slot value of the three domains) and `selection.json` (the selected pairs, their neutral
values, and their dialogue instances). The selection is fixed before any call: if `selection.json` exists and the
recomputed selection differs from it, the script stops and writes nothing.
Usage: python3 -I r9/detector/table.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lib"))
sys.path.insert(0, str(HERE))
import anth  # noqa: E402
import pairs  # noqa: E402

X3_TOTAL, X3_DEEPINFRA = 1200, 600  # review/plan13/r9_counts.py: N3 and the DeepInfra share
Z4_PER_PAIR = 120  # amendment 1: 120 instances for each Z4 pair
SELECTION, TABLE = HERE / "selection.json", HERE / "table.tsv"


def training_ids(data):
    val, test = anth.splits()
    ids = sorted(k for k in data if k not in val | test)
    anth.assert_outside_trackp(ids, data)
    return ids


def select(rows, traveller_text, goals):
    """The selected pairs in a fixed order (X3 high risk, X3 controls, then the other Z4 pairs), each with its roles,
    neutral value, instances, and the instances whose brief sets the value (`brief_match`)."""
    high, control = pairs.select_x3(rows)
    z4 = pairs.select_z4(rows) or []
    chosen = {}
    for role, group in (("x3_high", high), ("x3_control", control), ("z4", z4)):
        for rank, r in enumerate(group, 1):
            chosen.setdefault(r.pair, {"row": r, "roles": {}})["roles"][role] = rank
    items = list(chosen.values())
    x3 = [x for x in items if set(x["roles"]) & {"x3_high", "x3_control"}]
    n_x3 = pairs.allocate([len(x["row"].words) for x in x3], X3_TOTAL)
    n_di = pairs.allocate(n_x3, X3_DEEPINFRA)
    for x, a, b in zip(x3, n_x3, n_di):
        x["x3"], x["x3_deepinfra"] = a, b
    for x in items:
        if "z4" in x["roles"] and "x3" not in x:
            x["z4"] = min(len(x["row"].words), Z4_PER_PAIR)
    for x in items:
        if "z4" in x["roles"] and "x3" in x:
            assert x["x3"] >= Z4_PER_PAIR, x
    out = []
    for k, x in enumerate(items, 1):
        r = x["row"]
        sample = pairs.order(r.words, r.pair)
        used = sample[:max(x.get(k, 0) for k in ("x3", "z4"))]
        out.append({"id": f"q{k:02d}", "domain": r.pair.domain, "slot": r.pair.slot, "value": r.pair.value,
                    "neutral": pairs.neutral(r.pair, traveller_text), "roles": x["roles"], "rule_b": r.rule_b,
                    "mismatch": r.mismatch, "word_dialogues": len(r.words), "briefs": r.briefs, "rule_l": r.rule_l,
                    **{key: sample[:x[key]] for key in ("x3", "x3_deepinfra", "z4") if key in x},
                    **({"z4_reads": "ex3 (the first 120 of x3)"} if "z4" in x["roles"] and "x3" in x else {}),
                    "brief_match": sorted(i for i in used if pairs.brief_sets(goals[i], r.pair))})
    return out, len(z4) == pairs.Z4_PAIRS


def write_table(rows, info_rows, chosen):
    role = {(p["domain"], p["slot"], p["value"]): ",".join(p["roles"]) for p in chosen}
    x3_rank = {r.pair: k for k, r in enumerate(pairs.ranked(rows, pairs.X3_MIN), 1)}
    z4_rank = {r.pair: k for k, r in enumerate(pairs.ranked(rows, pairs.Z4_MIN), 1)}
    info = {r.pair: r for r in info_rows}
    lines = ["\t".join(("domain", "slot", "value", "slot_size", "not_candidate", "word_dialogues", "mismatch",
                        "rule_b", "briefs", "rule_l", "rank_50", "rank_120", "selected", "rule_b_info_only"))]
    for r in sorted(rows, key=lambda r: (bool(r.out), -(r.rule_b or 0), r.pair)):
        b = "" if r.rule_b is None else f"{r.rule_b:.4f}"
        bi = "" if info[r.pair].rule_b is None else f"{info[r.pair].rule_b:.4f}"
        lines.append("\t".join(map(str, (*r.pair, r.slot_size, r.out, len(r.words), r.mismatch, b, r.briefs, r.rule_l,
                                         x3_rank.get(r.pair, ""), z4_rank.get(r.pair, ""), role.get(tuple(r.pair), ""),
                                         bi))))
    TABLE.write_text("\n".join(lines) + "\n")


def main():
    data = anth.multiwoz()
    ontology = json.loads((anth.DATA / "ontology.json").read_text())
    ids = training_ids(data)
    traveller_text = "\n".join(t for i in ids for t in pairs.traveller(data[i]))
    rows = pairs.table(data, ontology, ids)
    info_rows = pairs.table(data, ontology, ids, ("info",))
    goals = {i: data[i]["goal"] for i in ids}
    chosen, z4_ok = select(rows, traveller_text, goals)
    info_chosen, _ = select(info_rows, traveller_text, goals)
    write_table(rows, info_rows, chosen)
    print(f"table: {len(rows)} slot values, {sum(not r.out for r in rows)} candidates, "
          f"{len(pairs.ranked(rows, pairs.X3_MIN))} with {pairs.X3_MIN} or more word dialogues, "
          f"{len(pairs.ranked(rows, pairs.Z4_MIN))} with {pairs.Z4_MIN} or more; written to {TABLE.name}")
    for p in chosen:
        sizes = ", ".join(f"{k} {len(p[k])}" for k in ("x3", "x3_deepinfra", "z4") if k in p)
        print(f"  {p['id']} {p['domain']}-{p['slot']} = {p['value']!r} -> {p['neutral']!r}: roles {p['roles']}, "
              f"Rule B {p['rule_b']:.4f} ({p['mismatch']} of {p['word_dialogues']}), briefs {p['briefs']}, "
              f"Rule L {p['rule_l'] or '-'}; "
              f"instances {sizes}")
    same = [(p["domain"], p["slot"], p["value"], p["roles"]) for p in info_chosen] == \
           [(p["domain"], p["slot"], p["value"], p["roles"]) for p in chosen]
    print(f"Z4: {'16 pairs selected' if z4_ok else 'not run, fewer than 16 candidates have 120 or more dialogues'}")
    print(f"sensitivity, Rule B from goal.<domain>.info only: the selection is {'the same' if same else 'DIFFERENT'}")
    record = {"rule": "PROTOCOL.md section 'X3 and Z4' with amendment 1 (2026-11-03); readings in r9/detector/pairs.py",
              "counts": {"x3": X3_TOTAL, "x3_deepinfra": X3_DEEPINFRA, "z4_per_pair": Z4_PER_PAIR},
              "z4_selected": z4_ok, "pairs": chosen}
    text = json.dumps(record, indent=1) + "\n"
    if SELECTION.exists():
        if SELECTION.read_text() != text:
            sys.exit(f"Not written. {SELECTION.name} exists and differs from the recomputed selection. The selection "
                     f"is fixed before any call; find the cause before you change it.")
        print(f"{SELECTION.name}: unchanged")
    else:
        SELECTION.write_text(text)
        print(f"{SELECTION.name}: written")


if __name__ == "__main__":
    main()
