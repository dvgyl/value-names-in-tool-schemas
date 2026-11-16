"""Strata of the existing reads (Z0 items 4, 5, and 6): dose response by the "hotel" count (addon-opus D7 and R5),
availability strata (addon-sonnet F2), and database feasibility (F4, rung V3). Local files only, no API call.

Usage: python3 -I read_strata.py
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gold  # noqa: E402
from gold import CELLS, anth, check, common, count, pct  # noqa: E402

SONNET = "addon-sonnet"


def main():
    print(gold.EXPLORATORY)
    print("Definitions: brief, booked, valid read, and 'type holds hotel' as in read_gold.py. 'hotel' count = matches of "
          "\\bhotels?\\b in the traveller turns. Availability class = which venue types of hotel_db.json match the gold "
          "(common.gold_form) without type. Database feasibility (V3) = the number of hotel_db venues that the full "
          "parsed read accepts (common.acceptable_rank; 'unclear' counts as no constraint; the name is not used).")
    data = anth.multiwoz()
    db = gold.hotel_db()
    types = gold.db_types(db)
    sets = gold.dialogue_sets(data)
    t994 = sets["994"]
    booked = {i: gold.booked_type(data[i], types) for i in sets["1136"]}
    reads, bad = gold.load_reads(set(t994))
    print("\nrows without a valid read, on the 994:", dict(bad) or "none")

    print("\n== dose response (D7, R5): the 994, share of reads where type holds hotel, by the 'hotel' count")
    words = {i: min(gold.hotel_words(data[i]), 4) for i in t994}
    buckets = {k: [i for i in t994 if words[i] == k] for k in (1, 2, 3, 4)}
    print("   dialogues per count: " + ", ".join(f"{k if k < 4 else '4+'}: {len(v)}" for k, v in buckets.items()))
    for k, n in zip(buckets, ("541", "291", "108", "54")):
        check("addon-opus D7", f"dialogues with 'hotel' count {k if k < 4 else '4 or more'}", n, len(buckets[k]))
    for cell in CELLS:
        for form in cell[2:]:
            h = gold.hits(reads[(cell[0], cell[1], form)], gold.holds_hotel)
            parts = [f"{k if k < 4 else '4+'}: {pct(*count(h, ids)):5.1f}% ({count(h, ids)[1]})" for k, ids in buckets.items()]
            print(f"{cell[0]:6} {cell[1]:6} {form:14} | " + " | ".join(parts))

    print("\n== availability strata (F2): hotel_db venue types that match the gold without type, and the booked type")
    for base in ("994", "1136"):
        avail = {i: gold.availability(common.gold_form(data[i]), db) for i in sets[base]}
        cls = collections.Counter(avail.values())
        bk = collections.Counter((avail[i], booked[i]) for i in sets[base])
        print(f"   base {base}:")
        for a in gold.AVAIL.values():
            g, h = bk[(a, "guesthouse")], bk[(a, "hotel")]
            print(f"     {a:15} {cls[a]:4} dialogues | booked guesthouse {g}, hotel {h}, none {bk[(a, 'none')]}, "
                  f"unmatched {bk[(a, 'unmatched')]} | guesthouse share of booked {pct(g, g + h):.1f}%")
        if base == "994":
            for a, n in (("both", "572"), ("only guesthouse", "230"), ("only hotel", "171"), ("neither", "21")):
                check(SONNET, f"F2 class {a}", n, cls[a])
            g, h = bk[("both", "guesthouse")], bk[("both", "hotel")]
            check(SONNET, "F2 class both, booked guesthouse", "220", g)
            check(SONNET, "F2 class both, booked hotel", "92", h)
            check(SONNET, "F2 class both, booked", "312", g + h)
            check(SONNET, "F2 class both, guesthouse share of booked %", "70.5", pct(g, g + h))
            only = [i for i in t994 if avail[i] == "only guesthouse"]
            zero = sum(1 for i in only if not gold.matches({**common.gold_form(data[i]), "type": ("hotel",)}, db))
            check(SONNET, "F2 class only guesthouse, the gold with type = hotel matches no venue", "230", zero)

    print("\n== database feasibility (F4, V3): the 994, reads where type holds hotel, and those that match zero venues")
    zero = {}
    for cell in CELLS:
        for form in cell[2:]:
            cr = reads[(cell[0], cell[1], form)]
            parts = []
            for g in ("guesthouse", "hotel"):
                rs = [r for d in t994 if booked[d] == g for r in cr.get(d, ()) if gold.holds_hotel(r["type"])]
                z = sum(1 for r in rs if not gold.matches(r, db))
                zero[(cell[0], cell[1], form, g)] = (z, len(rs))
                parts.append(f"booked {g}: {z} of {len(rs)} match zero venues ({pct(z, len(rs)):.0f}%)")
            print(f"{cell[0]:6} {cell[1]:6} {form:14} | " + " | ".join(parts))
    for model, form, z, n in (("sonnet", "p_main", "79", "146"), ("sonnet", "p_main_renamed", "10", "28"),
                              ("haiku", "p_main", "8", "14")):
        mz, mn = zero[("E13", model, form, "guesthouse")]
        check(SONNET, f"F4 E13 {model} {form}, booked guesthouse, reads that hold hotel", n, mn)
        check(SONNET, f"F4 E13 {model} {form}, booked guesthouse, of them zero venues", z, mz)
    check(SONNET, "F4 E13 sonnet p_main, zero-venue share %", "54%", pct(*zero[("E13", "sonnet", "p_main", "guesthouse")]))
    gold.summary()


if __name__ == "__main__":
    main()
