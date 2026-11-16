"""Brief and booking counts D1 to D8 (`review/plan13/addon-opus.md` section 0), the human wizard's first venue (D5, R3),
and the decision-rule number (R7). Data files only: no model read, no API call.

Usage: python3 -I briefs.py
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gold  # noqa: E402
from gold import anth, check, common, pct  # noqa: E402

OPUS, SONNET, ADD = "addon-opus", "addon-sonnet", "ROUND9-ADDITIONS s2"


def tally(ids, f):
    return collections.Counter(f(i) for i in ids)


def main():
    print(gold.EXPLORATORY)
    print("Definitions: brief = goal.hotel.info.type. booked = type of the last metadata.hotel.book.booked name, matched to "
          "hotel_db.json after gold.norm (lower case, '&' to 'and', a-z0-9 only). 'hotel' word = \\bhotels?\\b; "
          "'guesthouse' word = guest ?house; both case-insensitive. gold = common.gold_form (MultiWOZ 2.1 label).")
    data = anth.multiwoz()
    acts = json.loads((anth.DATA / "dialogue_acts.json").read_text())
    db = gold.hotel_db()
    types = gold.db_types(db)
    sets = gold.dialogue_sets(data)
    e7, t994 = sets["e7"], sets["994"]
    brief = {i: gold.brief_type(data[i]) for i in e7}
    fail = {i: gold.brief_type(data[i], "fail_info") for i in e7}
    booked = {i: gold.booked_type(data[i], types) for i in e7}
    gtype = {i: common.gold_form(data[i])["type"] for i in e7}
    says = lambda i, rx: any(rx.search(t) for t in gold.traveller(data[i]))

    print("\n== fail_info check (E7, 2,874): info type x fail_info type")
    print("  ", dict(tally(e7, lambda i: (brief[i], fail[i]))))
    print("   dialogues where fail_info sets a type and info sets none:", sum(1 for i in e7 if fail[i] and not brief[i]))
    either = lambda v: (lambda i: brief[i] == v or fail[i] == v)

    print("\n== D1: E7 dialogues with 'hotel(s)' in a traveller turn, by brief type")
    d1 = [i for i in e7 if says(i, gold.WORD)]
    c = tally(d1, brief.get)
    print("  ", len(d1), dict(c), "| brief with fail_info fallback:", dict(tally(d1, lambda i: brief[i] or fail[i])))
    check(OPUS, "D1 dialogues", "2058", len(d1))
    for v, n, p in (("hotel", "355", "17.2"), ("guesthouse", "544", "26.4"), (None, "1159", "56.3")):
        check(OPUS, f"D1 brief {v}", n, c[v])
        check(OPUS, f"D1 brief {v} %", p, pct(c[v], len(d1)))
    check(ADD, "of 2,058 saying hotel, brief guesthouse", "544", c["guesthouse"])
    check(ADD, "of 2,058 saying hotel, brief hotel", "355", c["hotel"])
    check(OPUS, "R2 Rule B hotel = 1 - 355/2,058 (info only)", "82.8%", 100 - pct(c["hotel"], len(d1)))
    check("PROTOCOL X3 and Z4", "Rule B hotel quoted 82.8%, recomputed with its wording (info or fail_info)", "82.8%",
          100 - pct(sum(map(either("hotel"), d1)), len(d1)))

    print("\n== D2: E7 dialogues with 'guesthouse' or 'guest house' in a traveller turn, by brief type")
    d2 = [i for i in e7 if says(i, gold.GUEST)]
    c = tally(d2, brief.get)
    print("  ", len(d2), dict(c), "| brief with fail_info fallback:", dict(tally(d2, lambda i: brief[i] or fail[i])))
    check(OPUS, "D2 dialogues", "1146", len(d2))
    for v, n in (("guesthouse", "837"), ("hotel", "98"), (None, "211")):
        check(OPUS, f"D2 brief {v}", n, c[v])
    check(OPUS, "D2 brief guesthouse %", "73.0", pct(c["guesthouse"], len(d2)))
    check(ADD, "of 1,146 saying guesthouse, brief guesthouse", "837", c["guesthouse"])
    check(OPUS, "R2 Rule B guesthouse = 1 - 837/1,146 (info only)", "27.0%", 100 - pct(c["guesthouse"], len(d2)))
    check("PROTOCOL X3 and Z4", "Rule B guesthouse quoted 27.0%, recomputed with its wording (info or fail_info)", "27.0%",
          100 - pct(sum(map(either("guesthouse"), d2)), len(d2)))

    print("\n== D3: the 994 (gold no type, 'hotel' in a traveller turn), by brief type")
    c = tally(t994, brief.get)
    print("  ", dict(c), "| brief with fail_info fallback:", dict(tally(t994, lambda i: brief[i] or fail[i])))
    for v, n, p in ((None, "807", "81.2"), ("hotel", "109", "11.0"), ("guesthouse", "78", "7.8")):
        check(OPUS, f"D3 brief {v}", n, c[v])
        check(OPUS, f"D3 brief {v} %", p, pct(c[v], len(t994)))
    print("   the 1,136 (all-turns rule), brief:", dict(tally(sets["1136"], brief.get)),
          "booked:", dict(tally(sets["1136"], booked.get)))

    print("\n== D4: the 994, brief x booked type")
    c = tally(t994, lambda i: (brief[i], booked[i]))
    print("  ", dict(sorted(c.items(), key=str)))
    for b, row in ((None, (("guesthouse", "296"), ("hotel", "152"), ("none", "359"))),
                   ("hotel", (("hotel", "40"), ("guesthouse", "19"), ("none", "50"))),
                   ("guesthouse", (("guesthouse", "40"), ("hotel", "7"), ("none", "31")))):
        for k, n in row:
            check(OPUS, f"D4 brief {b}, booked {k}", n, c[(b, k)])
    c = tally(t994, booked.get)
    for k, n in (("guesthouse", "355"), ("hotel", "199"), ("none", "440")):
        check(ADD, f"the 994, booked {k}", n, c[k])
    check(OPUS, "arithmetic: guesthouse share of booked in the 994 (count)", "355", c["guesthouse"])
    check(OPUS, "arithmetic: booked dialogues in the 994", "554", c["guesthouse"] + c["hotel"] + c["unmatched"])
    check(OPUS, "arithmetic: guesthouse share of booked in the 994 %", "64.1", pct(c["guesthouse"], 554))

    print("\n== D5: the 994, first venue that the human wizard names (dialogue_acts.json)")
    plain = lambda v: types.get(gold.norm(v), "unmatched")
    rebuild = tally(t994, lambda i: gold.wizard_first(acts[i.removesuffix(".json")], plain))
    print("   method A (rebuilds the planner): first Name slot of a Hotel-* or Booking-* act in turn order, any value "
          "('?' included), exact gold.norm match:", dict(rebuild))
    for k, n in (("guesthouse", "369"), ("hotel", "179"), ("unmatched", "298"), ("none", "148")):
        check(OPUS, f"D5 {k}", n, rebuild[k])
    loose = lambda v: gold.loose_type(v, types)
    r3 = {i: gold.wizard_first(acts[i.removesuffix(".json")], loose, ("Hotel",), ("?", "none")) for i in t994}
    print("   method B (R3): Hotel-* acts only, '?' and 'none' skipped, match without a leading 'the' or by a unique "
          "start of a venue name:", dict(tally(t994, r3.get)))
    print("   method B x booked:", dict(sorted(tally(t994, lambda i: (r3[i], booked[i])).items())))

    print("\n== D6: E7 gold-no-type dialogues with no 'hotel(s)' in any turn, by booked type")
    d6 = [i for i in e7 if gtype[i] is None and not any(gold.WORD.search(t["text"]) for t in data[i]["log"])]
    c = tally(d6, booked.get)
    print("  ", len(d6), dict(c))
    check(OPUS, "D6 dialogues", "235", len(d6))
    for k, n in (("guesthouse", "118"), ("hotel", "6"), ("none", "111")):
        check(OPUS, f"D6 booked {k}", n, c[k])

    print("\n== D7: the 994, 'hotel(s)' occurrences in traveller turns (matches, not turns)")
    c = tally(t994, lambda i: min(gold.hotel_words(data[i]), 4))
    print("  ", dict(sorted(c.items())))
    for k, n in zip((1, 2, 3, 4), ("541", "291", "108", "54")):
        check(OPUS, f"D7 count {k if k < 4 else '4 or more'}", n, c[k])

    print("\n== D8 and F3: booked type by gold type (E7)")
    hot = [i for i in e7 if gtype[i] == ("hotel",)]
    c = tally(hot, booked.get)
    print("   gold hotel:", len(hot), dict(c))
    check(OPUS, "D8 gold hotel dialogues", "545", len(hot))
    for k, n in (("hotel", "293"), ("guesthouse", "33"), ("none", "219")):
        check(OPUS, f"D8 booked {k}", n, c[k])
    check(OPUS, "D8 booked dialogues", "326", c["hotel"] + c["guesthouse"] + c["unmatched"])
    check(OPUS, "D8 guesthouse % of booked", "10.1", pct(c["guesthouse"], 326))
    check(SONNET, "F3 gold hotel, booked hotel of booked %", "90%", pct(c["hotel"], c["hotel"] + c["guesthouse"]))
    none = tally([i for i in e7 if gtype[i] is None], booked.get)
    print("   gold no type:", sum(none.values()), dict(none))
    check(SONNET, "F3 gold no type, booked guesthouse", "519", none["guesthouse"])
    check(SONNET, "F3 gold no type, booked", "763", none["guesthouse"] + none["hotel"] + none["unmatched"])
    check(SONNET, "F3 gold no type, booked guesthouse %", "68%", pct(none["guesthouse"], 763))

    print("\n== hotel_db and the decision rule")
    c = collections.Counter(h["type"] for h in db)
    print("   hotel_db:", len(db), dict(c))
    check(ADD, "hotel_db guesthouses", "24", c["guesthouse"])
    check(ADD, "hotel_db hotels", "9", c["hotel"])
    check(OPUS, "arithmetic: type = hotel removes venues", "24", c["guesthouse"])
    check(OPUS, "arithmetic: type = hotel removes venues %", "72.7", pct(c["guesthouse"], len(db)))
    k = sum(1 for i in t994 if brief[i] == "hotel")
    check(OPUS, "R7 decision rule: brief hotel among the 994", "109", k)
    check(OPUS, "R7 decision rule: brief hotel share of the 994 %", "11.0", pct(k, len(t994)))
    gold.summary()


if __name__ == "__main__":
    main()
