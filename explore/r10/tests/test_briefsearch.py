"""Test of r10/briefsearch.py. Data files only; no model call.

1. The moved `fits` gives the counts of review/plan14/feasible_harm.out: 807 dialogues of S1t whose brief sets no type,
   451 of them where no hotel fits the brief, 423 with no named venue, 184 of those where no hotel fits.
2. `search`, `search_failure`, `hidden_share` and `relaxation` give the right answer on hand-made calls.
Usage (from explore/): .venv/bin/python -I r10/tests/test_briefsearch.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import anth  # noqa: E402
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402


def test_plan14_counts():
    data, db = anth.multiwoz(), gold.hotel_db()
    t994 = gold.dialogue_sets(data)["994"]
    sub = bs.brief_subsets(data, t994, db)
    assert len(sub["no_type"]) == 807, len(sub["no_type"])
    assert len(sub["no_hotel_fits"]) == 451, len(sub["no_hotel_fits"])
    assert len(sub["no_name"]) == 423, len(sub["no_name"])
    no_name_empty = [i for i in sub["no_name"] if i in set(sub["no_hotel_fits"])]
    assert len(no_name_empty) == 184, len(no_name_empty)
    print("ok test_plan14_counts")


def test_hand_calls():
    db = [{"name": "a house", "type": "guesthouse", "area": "north", "pricerange": "cheap", "stars": "4",
           "parking": "yes", "internet": "yes"},
          {"name": "b hotel", "type": "hotel", "area": "north", "pricerange": "expensive", "stars": "4",
           "parking": "yes", "internet": "yes"}]
    call = {"name": None, "area": ("north",), "pricerange": ("cheap",), "stars": None, "type": ("hotel",),
            "parking": None, "internet": "any"}
    assert bs.search(db, call) == []
    assert bs.search(db, {**call, "type": None}) == [db[0]]
    assert bs.search(db, {**call, "type": "unclear"}) == [db[0]]
    assert bs.search(db, {**call, "type": ("hotel", "guesthouse")}) == [db[0]]
    assert bs.relaxation(call, db) == {"count": 0, "count_without_type": 1, "flag": True}
    assert bs.relaxation({**call, "type": None}, db)["flag"] is False
    d = {"goal": {"hotel": {"info": {"area": "north", "pricerange": "cheap"}}}}
    assert bs.search_failure(call, d, db) is True
    assert bs.search_failure({**call, "type": ("hotel", "guesthouse")}, d, db) is False
    assert bs.hidden_share(call, d, db) == 1.0
    assert bs.hidden_share({**call, "type": None}, d, db) == 0.0
    d2 = {"goal": {"hotel": {"info": {"area": "north"}}}}
    assert bs.search_failure(call, d2, db) is False  # a hotel fits this brief
    assert bs.hidden_share(call, d2, db) == 0.5
    assert bs.result_rows(db, limit=1) == {"results": [{"name": "a house", "type": "guesthouse", "area": "north",
                                                        "pricerange": "cheap", "stars": "4"}], "total": 2}
    print("ok test_hand_calls")


def main():
    test_plan14_counts()
    test_hand_calls()
    print("briefsearch test passed")


if __name__ == "__main__":
    main()
