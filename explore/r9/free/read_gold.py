"""Brief gold and booked gold on every existing read of E7, E11, E12, and E13 (Z0 items 1, 7, and 8; addon-opus R1,
addon-sonnet F1, F5, F6, F9, and the Y1 free precedent). Local files only, no API call.

Usage: python3 -I read_gold.py
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gold  # noqa: E402
from gold import CELLS, OUTCOMES, anth, check, count, pct  # noqa: E402

HOLDS, HIDES = OUTCOMES
CELL = {c[:3]: c for c in CELLS}
REVEALED = {  # review/plan13/revealed_r9b.out: booked guesthouse, hotel, none (original, renamed); any-hit; sign; p
    ("E7/E11", "haiku", "p4"): ("3.1", "0.7", "21.8", "6.0", "10.7", "3.4", "22", "20", "0", "1.9e-06"),
    ("E7/E11", "haiku", "p5"): ("1.7", "0.2", "14.1", "5.2", "9.1", "2.3", "13", "12", "0", "0.00049"),
    ("E7/E11", "sonnet", "p4"): ("15.1", "1.0", "42.4", "8.5", "23.3", "4.8", "57", "54", "0", "1.1e-16"),
    ("E7/E11", "sonnet", "p5"): ("10.0", "0.0", "30.3", "4.4", "16.7", "2.4", "44", "44", "0", "1.1e-13"),
    ("E7/E11", "opus", "p4"): ("2.7", "0.6", "39.4", "17.4", "17.9", "10.3", "15", "14", "1", "0.00098"),
    ("E7/E11", "opus", "p5"): ("0.2", "0.0", "13.4", "5.0", "7.4", "3.9", "2", "2", "0", "0.5"),
    ("E13", "haiku", "p_main"): ("0.9", "0.2", "7.5", "2.8", "6.1", "1.1", "4", "3", "0", "0.25"),
    ("E13", "sonnet", "p_main"): ("13.2", "2.1", "25.3", "8.9", "18.5", "5.1", "53", "46", "1", "6.8e-13"),
}
F1 = [  # addon-sonnet F1, type holds hotel: cell, booked group, original, renamed, sign, p
    (("E13", "sonnet", "p_main"), "guesthouse", "13.7", "2.6", "45", "0", "5.7e-14"),
    (("E13", "sonnet", "p_main"), "hotel", "25.3", "8.9", "38", "1", None),
    (("E13", "haiku", "p_main"), "guesthouse", "1.3", "0.3", "4", "0", "0.125"),
    (("E13", "haiku", "p_main"), "hotel", "7.9", "3.2", "13", "2", None),
    (("E7/E11", "opus", "p4"), "guesthouse", "8.1", "3.6", "30", "1", None),
    (("E7/E11", "sonnet", "p4"), "guesthouse", "16.0", "1.3", "58", "0", None),
]
PLAN = [  # PLAN.md lines 1469 to 1471, type holds hotel on all of the 994: cell, original, renamed, sign
    ("PLAN.md:1469", ("E7/E11", "haiku", "p4"), "10.9", "3.3", "131", "1"),
    ("PLAN.md:1469", ("E7/E11", "sonnet", "p4"), "24.9", "4.5", "226", "0"),
    ("PLAN.md:1469", ("E7/E11", "opus", "p4"), "20.3", "10.2", "160", "4"),
    ("PLAN.md:1469", ("E7/E11", "haiku", "p5"), "7.8", "2.4", None, None),
    ("PLAN.md:1469", ("E7/E11", "sonnet", "p5"), "17.3", "2.1", None, None),
    ("PLAN.md:1469", ("E7/E11", "opus", "p5"), "7.2", "3.5", None, None),
    ("PLAN.md:1470", ("E12", "sonnet", "p4"), "19.2", "3.8", "168", "2"),
    ("PLAN.md:1471", ("E13", "haiku", "p_main"), "5.1", "1.3", "48", "2"),
    ("PLAN.md:1471", ("E13", "sonnet", "p_main"), "18.4", "5.2", "150", "1"),
]


def check_contrast(source, label, c, r0=None, r1=None, more=None, less=None, p=None, any0=None):
    for name, planner, mine in (("original %", r0, pct(c.k0, c.n0)), ("renamed %", r1, pct(c.k1, c.n1)),
                                ("sign original higher", more, c.more), ("sign renamed higher", less, c.less),
                                ("sign p", p, c.p), ("dialogues with any hit, original", any0, c.any0)):
        if planner is not None:
            check(source, f"{label}, {name}", planner, mine)


def groups(ids, brief, booked):
    g = {"all": ids}
    for b in (None, "hotel", "guesthouse"):
        g[f"brief {b or 'none'}"] = [i for i in ids if brief[i] == b]
    for b in ("guesthouse", "hotel", "none", "unmatched"):
        sel = [i for i in ids if booked[i] == b]
        if sel or b != "unmatched":
            g[f"booked {b}"] = sel
    return g


def main():
    print(gold.EXPLORATORY)
    print("Definitions: brief and booked as in briefs.py. A valid read is succeeded, stop end_turn, and parsed by "
          "common.parse. 'type holds hotel': the parsed type is a list that holds hotel (addon-sonnet F1). 'type hides "
          "every guesthouse': it holds hotel and not guesthouse (revealed_r9b.py). Rates are shares of valid reads. The "
          "sign test compares per-dialogue rates, original against renamed form (e8_measure.sign_test).")
    data = anth.multiwoz()
    db = gold.hotel_db()
    types = gold.db_types(db)
    sets = gold.dialogue_sets(data)
    brief = {i: gold.brief_type(data[i]) for i in sets["e7"]}
    booked = {i: gold.booked_type(data[i], types) for i in sets["e7"]}
    reads, bad = gold.load_reads(set(sets["1136"]) | set(sets["256"]))
    print("\nrows without a valid read, on the 1,136 and the 256:", dict(bad) or "none")
    hits = {(*key, o): gold.hits(cell, f) for key, cell in reads.items() for o, f in OUTCOMES.items()}

    res = {}
    for base in ("994", "1136"):
        grp = groups(sets[base], brief, booked)
        print(f"\n######## base {base}: " + ", ".join(f"{g} {len(v)}" for g, v in grp.items()))
        for outcome in OUTCOMES:
            for kind in ("brief", "booked"):
                print(f"\n== base {base}, '{outcome}', by {kind} group: share of reads, original -> renamed "
                      "(dialogues original higher : renamed higher, exact two-sided p)")
                for cell in CELLS:
                    a, b = hits[(*cell[:3], outcome)], hits[(cell[0], cell[1], cell[3], outcome)]
                    parts = []
                    for g in ["all"] + [k for k in grp if k.startswith(kind)]:
                        res[(base, cell, outcome, g)] = c = gold.contrast(a, b, grp[g])
                        parts.append(f"{g} {c.text()}")
                    print(f"{cell[0]:6} {cell[1]:6} {cell[2]:6} | " + " | ".join(parts))

    print("\n== precision against the brief, the 994: reads with brief hotel / reads that hold hotel (base rate 109 of 994)")
    for cell in CELLS:
        row = []
        for form in cell[2:]:
            h = hits[(cell[0], cell[1], form, HOLDS)]
            hb, n = count(h, [i for i in sets["994"] if brief[i] == "hotel"]), count(h, sets["994"])
            row.append(f"{form} {hb[0]}/{n[0]} = {pct(hb[0], n[0]):.1f}%")
        print(f"{cell[0]:6} {cell[1]:6} | " + " | ".join(row))

    print("\n== planner checks, base 994")
    grp = groups(sets["994"], brief, booked)
    for g, n in (("guesthouse", "355"), ("none", "440"), ("hotel", "199")):
        check("revealed_r9b.out", f"booked group {g}", n, len(grp[f"booked {g}"]))
    for key, v in REVEALED.items():
        for k, g in enumerate(("guesthouse", "hotel", "none")):
            c = res[("994", CELL[key], HIDES, f"booked {g}")]
            check_contrast("revealed_r9b.out", f"{' '.join(key)} hides, booked {g}", c, v[2 * k], v[2 * k + 1])
        c = res[("994", CELL[key], HIDES, "booked guesthouse")]
        check_contrast("revealed_r9b.out", f"{' '.join(key)} hides, booked guesthouse", c, more=v[7], less=v[8], p=v[9],
                       any0=v[6])
    sonnet = CELL[("E13", "sonnet", "p_main")]
    check_contrast("ROUND9-ADDITIONS s2", "E13 sonnet hides, booked guesthouse",
                   res[("994", sonnet, HIDES, "booked guesthouse")], "13.2", "2.1", "46", "1", "6.8e-13")
    check_contrast("ROUND9-ADDITIONS s2", "E13 sonnet hides, booked hotel", res[("994", sonnet, HIDES, "booked hotel")],
                   "25.3", "8.9")
    for key, g, r0, r1, more, less, p in F1:
        check_contrast("addon-sonnet F1", f"{' '.join(key)} holds hotel, booked {g}", res[("994", CELL[key], HOLDS,
                                                                                            f"booked {g}")],
                       r0, r1, more, less, p)
    for source, key, r0, r1, more, less in PLAN:
        check_contrast(source, f"{' '.join(key)} holds hotel, all", res[("994", CELL[key], HOLDS, "all")], r0, r1, more,
                       less)

    print("\n== read agreement (F5): dialogues of the 994 with 3 valid reads that all hold hotel, by booked type. "
          "precision = booked hotel / (booked hotel + booked guesthouse). V3 = the read matches 1 or more hotel_db "
          "venues (gold.matches on the full read).")
    agree = {}
    for cell in CELLS:
        for form in cell[2:]:
            h, cellreads = hits[(cell[0], cell[1], form, HOLDS)], reads[(cell[0], cell[1], form)]
            all3 = [d for d in sets["994"] if len(h.get(d, ())) == 3 and all(h[d])]
            c = collections.Counter(booked[d] for d in all3)
            gh = [d for d in all3 if booked[d] == "guesthouse"]
            v3_all = sum(1 for d in gh if all(gold.matches(r, db) for r in cellreads[d]))
            v3_any = sum(1 for d in gh if any(gold.matches(r, db) for r in cellreads[d]))
            agree[(cell[0], cell[1], form)] = (c, v3_all)
            print(f"{cell[0]:6} {cell[1]:6} {form:14} | all 3 hold hotel: {len(all3)}; booked hotel {c['hotel']}, "
                  f"guesthouse {c['guesthouse']}, none {c['none']}; precision {pct(c['hotel'], c['hotel'] + c['guesthouse']):.0f}% "
                  f"| booked guesthouse and every read passes V3: {v3_all}; some read passes V3: {v3_any}")
    for form, nh, ng, prec in (("p_main", "47", "43", "52%"), ("p_main_renamed", "16", "9", "64%")):
        c, v3 = agree[("E13", "sonnet", form)]
        check("addon-sonnet F5", f"E13 sonnet {form} all 3 hold hotel, booked hotel", nh, c["hotel"])
        check("addon-sonnet F5", f"E13 sonnet {form} all 3 hold hotel, booked guesthouse", ng, c["guesthouse"])
        check("addon-sonnet F5", f"E13 sonnet {form} precision", prec, pct(c["hotel"], c["hotel"] + c["guesthouse"]))
    check("addon-sonnet F5", "E13 sonnet p_main, of the booked-guesthouse dialogues, every read passes V3", "18",
          agree[("E13", "sonnet", "p_main")][1])

    print("\n== reads in agreement (F9): dialogues of the 994 with 3 valid reads, by the number k that hold hotel; "
          "hotel share = booked hotel / (booked hotel + booked guesthouse)")
    for cell in CELLS:
        for form in cell[2:]:
            h = hits[(cell[0], cell[1], form, HOLDS)]
            by_k = collections.defaultdict(collections.Counter)
            for d in sets["994"]:
                if len(h.get(d, ())) == 3:
                    by_k[sum(h[d])][booked[d]] += 1
            parts = [f"k={k}: n {sum(by_k[k].values())}, {pct(by_k[k]['hotel'], by_k[k]['hotel'] + by_k[k]['guesthouse']):4.1f}% "
                     f"({by_k[k]['hotel']}/{by_k[k]['hotel'] + by_k[k]['guesthouse']})" for k in range(4)]
            print(f"{cell[0]:6} {cell[1]:6} {form:14} | " + " | ".join(parts))

    print("\n== where 'unclear' fires (F6): E7 p5, share of reads with type 'unclear'")
    unclear = {m: gold.hits(reads[("E7/E11", m, "p5")], gold.is_unclear) for m in ("haiku", "sonnet", "opus")}
    for m, h in unclear.items():
        parts = [f"{g} {pct(*count(h, grp[g])):4.1f}%" for g in ("booked guesthouse", "booked hotel", "booked none")]
        print(f"   {m:6} the 994 by booked group: " + " | ".join(parts) +
              f" || word present (994) {pct(*count(h, sets['994'])):4.1f}% against absent (256) {pct(*count(h, sets['256'])):4.1f}%")
    for m, gh, ho in (("sonnet", "10.0", "2.5"), ("haiku", "4.8", "1.7"), ("opus", "20.8", "32.0")):
        check("addon-sonnet F6", f"E7 p5 {m} unclear, booked guesthouse %", gh, pct(*count(unclear[m], grp["booked guesthouse"])))
        check("addon-sonnet F6", f"E7 p5 {m} unclear, booked hotel %", ho, pct(*count(unclear[m], grp["booked hotel"])))
    for m, present, absent in (("opus", "24.6", "0.8"), ("sonnet", "7.3", "0.4")):
        check("addon-sonnet F6", f"E7 p5 {m} unclear, word present (994) %", present, pct(*count(unclear[m], sets["994"])))
        check("addon-sonnet F6", f"E7 p5 {m} unclear, word absent (256) %", absent, pct(*count(unclear[m], sets["256"])))

    print("\n== Y1 free precedent: E7 p4, share of reads where type holds hotel, the 256 against the 994")
    no_guest = sum(1 for i in sets["256"] if not any(gold.GUEST.search(t) for t in gold.traveller(data[i])))
    check("addon-sonnet Y1", "lodging-phrase dialogues", "256", len(sets["256"]))
    check("addon-sonnet Y1", "of them without 'guesthouse'", "238", no_guest)
    for m, a256, a994 in (("haiku", "1.2", "10.9"), ("sonnet", "0.4", "24.9"), ("opus", "0.4", "20.3")):
        h = hits[("E7/E11", m, "p4", HOLDS)]
        print(f"   {m:6} 256: {pct(*count(h, sets['256'])):4.1f}% | 994: {pct(*count(h, sets['994'])):4.1f}%")
        check("addon-sonnet Y1", f"E7 p4 {m} holds hotel, the 256 %", a256, pct(*count(h, sets["256"])))
        check("addon-sonnet Y1", f"E7 p4 {m} holds hotel, the 994 %", a994, pct(*count(h, sets["994"])))
    gold.summary()


if __name__ == "__main__":
    main()
