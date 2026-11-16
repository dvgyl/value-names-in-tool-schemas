"""Analysis of X7, fixed before any call (PROTOCOL.md X7, r9/x7/PREDICTIONS.md).

It reads raw.jsonl of the four X7 folders. A dialogue in more than one group counts in each of its groups.
1. The share of valid reads that write the target value of the group, per group, model, and form.
2. The dialogue-level exact sign test of A1 against A0 (forms/e8_measure.py), per group and model, with the drop in
   percentage points (A0 share minus A1 share).
3. Revealed choice: on the dialogues whose revealed type (ids.json) is a database type, the share of reads whose `type`
   is a list without that type, and the sign test of A1 against A0 on that measure.
A valid read is a succeeded row that stopped at end_turn and parses. Usage: python3 -I r9/x7/x7_analyze.py
"""
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x7  # noqa: E402
from e8_measure import sign_test  # noqa: E402


def load(explore=x7.EXPLORE, names=tuple(x7.EXPERIMENTS)):
    """reads[(model, form)][unit] = parsed `type` values of the valid reads; invalid[(model, form)] = other rows."""
    reads = collections.defaultdict(lambda: collections.defaultdict(list))
    invalid = collections.Counter()
    for name in names:
        path = pathlib.Path(explore) / name / "raw.jsonl"
        for line in open(path) if path.exists() else []:
            r = json.loads(line)
            _, unit, form, _, model = r["custom_id"].split("-")
            if r["type"] != "succeeded" or r.get("stop") != "end_turn":
                invalid[(model, form)] += 1
                continue
            try:
                value = x7.parse(r["text"], x7.FORMS[form])["type"]
            except (ValueError, KeyError, TypeError, AttributeError):
                invalid[(model, form)] += 1
                continue
            reads[(model, form)][unit].append(value)
    return reads, invalid


def target(value):
    return lambda unit, v: isinstance(v, tuple) and value in v


def excludes(revealed):
    return lambda unit, v: isinstance(v, tuple) and revealed[unit] not in v


def hits(reads, cell, units, measure):
    return {u: [measure(u, v) for v in vs] for u, vs in reads.get(cell, {}).items() if u in units}


def shares(reads, units_of, measure_of):
    """Rows (group, model, form, units, hits, reads)."""
    rows = []
    for g, units in units_of.items():
        for model, form in sorted(reads):
            h = hits(reads, (model, form), units, measure_of(g))
            n = sum(map(len, h.values()))
            if n:
                rows.append((g, model, form, len(h), sum(map(sum, h.values())), n))
    return rows


def signs(reads, units_of, measure_of):
    """Rows (group, model, drop in points, A0 higher, A0 lower, exact p) over the units with reads under both forms."""
    rows = []
    for g, units in units_of.items():
        for model in sorted({m for m, _ in reads}):
            a, b = (hits(reads, (model, f), units, measure_of(g)) for f in ("a0", "a1"))
            if set(a) & set(b):
                share = lambda h: 100 * sum(map(sum, h.values())) / sum(map(len, h.values()))  # noqa: E731
                rows.append((g, model, share(a) - share(b), *sign_test(a, b)))
    return rows


def group_units(stored):
    return {g: {d.removesuffix(".json") for d in v} for g, v in stored["groups"].items()}


def revealed_units(stored):
    """The units of each group whose revealed type is a database type (not "none" or "unmatched")."""
    return {g: {u for u in units if stored["revealed"][u] in x7.TYPES} for g, units in group_units(stored).items()}


def pct(k, n):
    return f"{k:5d}/{n:5d} ({100 * k / n:5.1f}%)" if n else "    -"


def main():
    reads, invalid = load()
    stored = x7.ids()
    of_target = lambda g: target(x7.GROUPS[g].value)  # noqa: E731
    of_revealed = lambda g: excludes(stored["revealed"])  # noqa: E731
    print("== 1. reads that write the target value (group, model, form: units, hits/reads)")
    for g, model, form, u, k, n in shares(reads, group_units(stored), of_target):
        print(f"{g:8} {model:9} {form:3} {u:4d} units  {pct(k, n)}")
    print("\n== 2. exact sign test of A1 against A0 (drop = A0 share minus A1 share, units where A0 is higher, lower, p)")
    for g, model, drop, more, less, p in signs(reads, group_units(stored), of_target):
        print(f"{g:8} {model:9} drop {drop:+6.1f} points, A0 higher {more:4d}, lower {less:4d}, p = {p:.2g}")
    print("\n== 3. revealed choice: reads whose type excludes the revealed database type")
    units_of = revealed_units(stored)
    for g, model, form, u, k, n in shares(reads, units_of, of_revealed):
        print(f"{g:8} {model:9} {form:3} {u:4d} units  {pct(k, n)}")
    for g, model, drop, more, less, p in signs(reads, units_of, of_revealed):
        print(f"{g:8} {model:9} A0 minus A1 {drop:+6.1f} points, A0 higher {more:4d}, lower {less:4d}, p = {p:.2g}")
    if invalid:
        print("\ninvalid rows (not succeeded, not end_turn, or not parsed): "
              + ", ".join(f"{m} {f} {n}" for (m, f), n in sorted(invalid.items())))


if __name__ == "__main__":
    main()
