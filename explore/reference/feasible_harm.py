"""Offline harm count for a `type = hotel` commitment (review of 2026-11-12). Data files only: no model read, no API call.

For each training dialogue of the round-9 group S1t (994: the 2.1 gold sets no type, a traveller turn says "hotel"), the
script takes the brief (`goal.hotel.info`) as the traveller's true constraints and searches `hotel_db.json` two times:
with the brief only, and with the brief plus `type = hotel`. It reports how often the added filter removes every venue
that fits the brief, and what share of the fitting venues it hides. Exploratory: the analysis was chosen after round 9.
Usage (from explore/): python3 -I reference/feasible_harm.py
"""
import collections
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "r9" / "free"))
import gold  # noqa: E402
from gold import anth  # noqa: E402

SLOTS = ("area", "pricerange", "stars", "parking", "internet", "name")


def fits(venue, brief):
    for slot in SLOTS:
        want = brief.get(slot)
        if want is None or str(want).lower() in ("dontcare", "don't care", "do nt care"):
            continue
        have = str(venue.get(slot, "")).lower()
        if slot == "name":
            if gold.norm(have) != gold.norm(str(want)):
                return False
        elif have != str(want).lower():
            return False
    return True


def report(label, ids, data, db):
    rows = []
    for i in ids:
        brief = data[i]["goal"]["hotel"].get("info", {})
        all_fit = [v for v in db if fits(v, brief)]
        rows.append((len(all_fit), sum(1 for v in all_fit if v["type"] == "hotel")))
    some = [(a, h) for a, h in rows if a > 0]
    empty = sum(1 for a, h in some if h == 0)
    hidden = [1 - h / a for a, h in some]
    print(f"\n{label}: {len(ids)} dialogues; {len(some)} have 1 or more venues that fit the brief")
    print(f"  type = hotel leaves no fitting venue: {empty} of {len(some)} ({100 * empty / len(some):.1f}%)")
    print(f"  type = hotel hides 1 or more fitting venues: {sum(1 for x in hidden if x > 0)} of {len(some)} "
          f"({100 * sum(1 for x in hidden if x > 0) / len(some):.1f}%)")
    print(f"  mean share of fitting venues hidden: {100 * statistics.mean(hidden):.1f}%; median "
          f"{100 * statistics.median(hidden):.1f}%")
    print(f"  mean fitting venues: {statistics.mean(a for a, h in some):.2f} without the filter, "
          f"{statistics.mean(h for a, h in some):.2f} with it")


def main():
    print(gold.EXPLORATORY)
    data = anth.multiwoz()
    db = gold.hotel_db()
    types = gold.db_types(db)
    t994 = gold.dialogue_sets(data)["994"]
    brief = {i: gold.brief_type(data[i]) for i in t994}
    fail = {i: gold.brief_type(data[i], "fail_info") for i in t994}
    booked = {i: gold.booked_type(data[i], types) for i in t994}
    print("the 994 by brief type (info):", dict(collections.Counter(brief.values())))
    free = [i for i in t994 if brief[i] is None and fail[i] is None]
    print("brief sets no type in info or fail_info:", len(free))
    named = [i for i in free if data[i]["goal"]["hotel"].get("info", {}).get("name")]
    print("  of these, the brief names a venue:", len(named),
          dict(collections.Counter(types.get(gold.norm(data[i]['goal']['hotel']['info']['name']), 'unmatched') for i in named)))
    report("S1t, brief sets no type", free, data, db)
    report("S1t, brief sets no type and names no venue", [i for i in free if i not in set(named)], data, db)
    report("S1t, brief sets no type, booked a guesthouse", [i for i in free if booked[i] == "guesthouse"], data, db)
    report("all 994", t994, data, db)


if __name__ == "__main__":
    main()
