"""Analysis of the round-9 natural runs (X1, the natural part of X2, B1), fixed before any call (PREDICTIONS.md).

It reads raw.jsonl of each r9/natural experiment, E13 (F0 and F1 on S1, Claude), and E14 (F0 on the E4 condition-a
items, Claude). The rows of `ex1_s1` under F0 are the drift check, so they are the form `f0_drift`.
1. The share of reads with `type = hotel` (the E8 measure) per model, form, and group.
2. The dialogue-level exact sign test of each form against F0 (forms/e8_measure.py), per model and group.
3. The booked-venue exclusion (review/plan13/revealed_r9b.py): on S1t, by the venue type that the traveller booked, the
   share of reads whose type hides every guesthouse, and the sign test against F0 on the guesthouse-booked dialogues.
A valid read is a succeeded row that stopped at end_turn and parses. Usage: python3 -I r9/natural/natural_analyze.py
"""
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural  # noqa: E402
from e8_measure import sign_test  # noqa: E402

GROUPS = ("S1t", "S1", "S2", "S2_booked_hotel", "S2_brief_hotel", "S3", "S4", "S5", "drift", "tc_amb", "tc_clr")
BOOKED = ("guesthouse", "hotel", "none", "unmatched")
OLD = {("e13", "p_main"): "f0", ("e13", "p_main_renamed"): "f1", ("e14", "p_main"): "f0"}


def key(cid):
    """(experiment, model, form, unit, read). E14 item ids hold "-", so its unit gets "_" as in the r9 custom ids."""
    if cid.startswith("e14-"):
        item, form, read, model = cid[4:].rsplit("-", 3)
        return "e14", model, form, item.replace("-", "_"), int(read.removeprefix("r"))
    name, unit, form, read, model = cid.split("-")
    return name, model, form, unit, int(read)


def label(name, form, unit):
    """The round-9 form of a row, or None for a row outside the analysis."""
    if name in ("e13", "e14"):
        return OLD.get((name, form)) if name == "e13" or unit.startswith("xa_") else None
    return "f0_drift" if (name, form) == ("ex1_s1", "f0") else form


def load(explore=natural.EXPLORE, names=tuple(natural.EXPERIMENTS) + ("e13", "e14")):
    """reads[(model, form)][unit] = parsed `type` values of the valid reads; invalid[(model, form)] = other rows."""
    reads = collections.defaultdict(lambda: collections.defaultdict(list))
    invalid = collections.Counter()
    for name in names:
        path = pathlib.Path(explore) / name / "raw.jsonl"
        for line in open(path) if path.exists() else []:
            r = json.loads(line)
            exp, model, form, unit, _ = key(r["custom_id"])
            f = label(exp, form, unit)
            if f is None:
                continue
            if r["type"] != "succeeded" or r.get("stop") != "end_turn":
                invalid[(model, f)] += 1
                continue
            try:
                value = natural.parse(r["text"], natural.FORMS[f.removesuffix("_drift")])["type"]
            except (ValueError, KeyError, TypeError):
                invalid[(model, f)] += 1
                continue
            reads[(model, f)][unit].append(value)
    return reads, invalid


def hotel(v):
    return isinstance(v, tuple) and "hotel" in v


def hides(v):
    return isinstance(v, tuple) and "hotel" in v and "guesthouse" not in v


def group_units(groups):
    """Group name -> unit ids. The Track C groups are the E4 condition-a items, ambiguous and clear."""
    out = {g: {d.removesuffix(".json") for d in groups[g]} for g in GROUPS if g in groups}
    items = [it.id.replace("-", "_") for it in natural.templates.items() if it.condition == "a"]
    out["tc_amb"] = {i for i in items if i.endswith("_amb")}
    out["tc_clr"] = {i for i in items if i.endswith("_clr")}
    return out


def hits(reads, cell, units, measure):
    return {u: [measure(v) for v in vs] for u, vs in reads.get(cell, {}).items() if u in units}


def shares(reads, units_of, measure=hotel):
    """Rows (group, model, form, units, hits, reads). The drift group shows only F0 and the drift reads."""
    rows = []
    for g, units in units_of.items():
        for model, form in sorted(reads):
            if g == "drift" and form not in ("f0", "f0_drift"):
                continue
            h = hits(reads, (model, form), units, measure)
            n = sum(map(len, h.values()))
            if n:
                rows.append((g, model, form, len(h), sum(map(sum, h.values())), n))
    return rows


def signs(reads, units_of, measure=hotel):
    """Rows (group, model, form, F0 higher, F0 lower, exact p) over the units with reads under both forms."""
    rows = []
    for g, units in units_of.items():
        for model, form in sorted(reads):
            if form == "f0" or (model, "f0") not in reads:
                continue
            if (form == "f0_drift") != (g == "drift"):  # the drift reads meet F0 only on the drift group
                continue
            a, b = hits(reads, (model, "f0"), units, measure), hits(reads, (model, form), units, measure)
            if set(a) & set(b):
                rows.append((g, model, form, *sign_test(a, b)))
    return rows


def exclusion(reads, groups):
    """Hiding shares on S1t per booked group, and the guesthouse-booked sign test against F0 (revealed_r9b.py)."""
    units_of = {k: {d.removesuffix(".json") for d in groups[f"S1t_booked_{k}"]} for k in BOOKED}
    rows = []
    for model, form in sorted(reads):
        cells = []
        for k in BOOKED:
            h = hits(reads, (model, form), units_of[k], hides)
            cells.append((k, sum(map(sum, h.values())), sum(map(len, h.values()))))
        if not any(n for _, _, n in cells):
            continue
        a = hits(reads, (model, "f0"), units_of["guesthouse"], hides)
        b = hits(reads, (model, form), units_of["guesthouse"], hides)
        test = sign_test(a, b) if form != "f0" and set(a) & set(b) else None
        rows.append((model, form, cells, sum(1 for v in a.values() if any(v)), test))
    return rows


def pct(k, n):
    return f"{k:5d}/{n:5d} ({100 * k / n:5.1f}%)" if n else "    -"


def main():
    reads, invalid = load()
    groups = natural.ids()
    units_of = group_units(groups)
    print("== 1. reads with type = hotel (group, model, form: units, hits/reads)")
    for g, model, form, u, k, n in shares(reads, units_of):
        print(f"{g:16} {model:8} {form:8} {u:5d} units  {pct(k, n)}")
    print("\n== 2. exact sign test against F0 (units where F0 has the higher share, the lower share, p)")
    for g, model, form, more, less, p in signs(reads, units_of):
        print(f"{g:16} {model:8} {form:8} F0 higher {more:4d}, lower {less:4d}, p = {p:.2g}")
    print("\n== 3. booked-venue exclusion on S1t: reads whose type hides every guesthouse, by the booked type")
    for model, form, cells, hit, test in exclusion(reads, groups):
        parts = " | ".join(f"{k} {pct(h, n)}" for k, h, n in cells if n)
        sign = f"; sign {test[0]} to {test[1]}, p = {test[2]:.2g}" if test else ""
        print(f"{model:8} {form:8} | {parts} | guesthouse dialogues with a hiding F0 read: {hit}{sign}")
    if invalid:
        print("\ninvalid rows (not succeeded, not end_turn, or not parsed): "
              + ", ".join(f"{m} {f} {n}" for (m, f), n in sorted(invalid.items())))


if __name__ == "__main__":
    main()
