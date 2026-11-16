"""The venue search over hotel_db.json and the brief outcomes of round 10 (ROUND10-EXPERIMENT-PLAN.md experiment 2,
review/plan15/ACTION-PLAN.md section 2.4). Data files only: no model call, no answer of a sealed run.

`fits` is the logic of review/plan14/feasible_harm.py, moved here without a change of behaviour (that script stays
as it is; tests/test_briefsearch.py checks that this module gives its counts). The other functions take the fields of
one parsed form answer or tool call, in the format of forms/common.parse: `name` is a string or None, and each field
of common.FIELDS is None (not stated), "any", "unclear", or a tuple of values.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
sys.path.insert(0, str(EXPLORE / "r9" / "free"))
sys.path.insert(0, str(EXPLORE / "forms"))
import common  # noqa: E402
import gold  # noqa: E402

SLOTS = ("area", "pricerange", "stars", "parking", "internet", "name")  # the brief slots of feasible_harm.py
FIELDS = tuple(common.FIELDS)  # area, pricerange, stars, type, parking, internet
DONTCARE = ("dontcare", "don't care", "do nt care")


def fits(venue, brief):
    """True when the venue meets every constraint of a MultiWOZ brief (goal.hotel.info). Unchanged from plan 14."""
    for slot in SLOTS:
        want = brief.get(slot)
        if want is None or str(want).lower() in DONTCARE:
            continue
        have = str(venue.get(slot, "")).lower()
        if slot == "name":
            if gold.norm(have) != gold.norm(str(want)):
                return False
        elif have != str(want).lower():
            return False
    return True


def keeps(venue, field, value):
    """One field of a call as a filter. None, "any" and "unclear" are no filter; a tuple keeps a venue whose value is
    in the tuple."""
    if value is None or value in ("any", "unclear"):
        return True
    have = str(venue.get(field, "")).lower()
    return have in {str(v).lower() for v in value}


def search(db, fields):
    """The venues that fit the fields of one parsed call, in the order of hotel_db.json."""
    out = []
    for v in db:
        if fields.get("name") and gold.norm(str(v.get("name", ""))) != gold.norm(str(fields["name"])):
            continue
        if all(keeps(v, f, fields.get(f)) for f in FIELDS):
            out.append(v)
    return out


def result_rows(venues, limit=5):
    """The tool result that step 2 of experiment A sends: the first `limit` venues and the total count."""
    keys = ("name", "type", "area", "pricerange", "stars")
    return {"results": [{k: v.get(k) for k in keys} for v in venues[:limit]], "total": len(venues)}


def brief_of(d):
    return d["goal"]["hotel"].get("info", {})


def brief_fitting(d, db):
    return [v for v in db if fits(v, brief_of(d))]


def brief_subsets(data, ids, db):
    """For a list of dialogues: "no_type" (the brief sets no type in info or fail_info), "no_name" (of those, the brief
    names no venue), and "no_hotel_fits" (of those, no hotel of the venue data fits the brief)."""
    no_type = [i for i in ids if gold.brief_type(data[i]) is None and gold.brief_type(data[i], "fail_info") is None]
    no_name = [i for i in no_type if not brief_of(data[i]).get("name")]
    no_hotel = [i for i in no_type if not any(v["type"] == "hotel" for v in brief_fitting(data[i], db))]
    return {"no_type": no_type, "no_name": no_name, "no_hotel_fits": no_hotel}


def type_filter(fields):
    return fields.get("type")


def search_failure(fields, d, db):
    """True when the call's type keeps hotel and not guesthouse, and no hotel fits the brief: the search with this
    type shows no venue that the traveller's brief accepts."""
    t = type_filter(fields)
    if not gold.hides_guesthouse(t):
        return False
    return bool(brief_fitting(d, db)) and not any(v["type"] == "hotel" for v in brief_fitting(d, db))


def hidden_share(fields, d, db):
    """The share of the brief's fitting venues that the call's type filter hides; None when no venue fits the brief."""
    fit = brief_fitting(d, db)
    if not fit:
        return None
    t = type_filter(fields)
    return sum(1 for v in fit if not keeps(v, "type", t)) / len(fit)


def relaxation(fields, db):
    """The relaxation check (ACTION-PLAN section 0, item 6): the result count of the call, and the count with the type
    field removed. `flag` is True when the call finds nothing and the same call without its type finds something."""
    n = len(search(db, fields))
    m = len(search(db, {**fields, "type": None}))
    return {"count": n, "count_without_type": m, "flag": n == 0 and m > 0}
