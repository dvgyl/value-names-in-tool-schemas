"""Tests of r10/analysis/loyal_final_recommendations.py with cases computed by hand. No data access.

Usage (from explore/): python3 -I r10/tests/test_loyal_final_recommendations.py
This file is a copy of a project test with the import path and the module name changed.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "analysis"))
import loyal_final_recommendations as inv  # noqa: E402

DB = [{"name": "worth house", "type": "guesthouse"}, {"name": "warkworth house", "type": "guesthouse"},
      {"name": "the cambridge belfry", "type": "hotel"}, {"name": "a and b guest house", "type": "guesthouse"},
      {"name": "lovell lodge", "type": "hotel"}]
KEYS = inv.name_keys(DB)


def test_names():
    # "worth house" is inside "warkworth house": only the longer name counts.
    assert inv.named_venues("I suggest Warkworth House.", KEYS) == ["warkworth house"]
    # Spec rule (item 6): when both names occur, only the longer one counts. The diagnostic flags such texts.
    assert inv.named_venues("Worth House or Warkworth House?", KEYS) == ["warkworth house"]
    assert inv.shadowed_name("Worth House or Warkworth House?", KEYS)
    assert not inv.shadowed_name("I suggest Warkworth House.", KEYS)
    # A name that starts with "the" also counts without it.
    assert inv.named_venues("Cambridge Belfry is a hotel.", KEYS) == ["the cambridge belfry"]
    assert inv.named_venues("The Cambridge Belfry is a hotel.", KEYS) == ["the cambridge belfry"]
    # "&" reads as "and".
    assert inv.named_venues("A&B Guest House suits you.", KEYS) == ["a and b guest house"]
    assert inv.named_venues("You're welcome! Enjoy your stay.", KEYS) == []


def test_cue():
    assert inv.has_cue("Unfortunately, Lovell Lodge has no parking.")
    assert inv.has_cue("Lovell Lodge does not have free wifi.")
    assert inv.has_cue("I found none of these.")
    assert not inv.has_cue("Lovell Lodge suits all your requirements.")
    assert not inv.has_cue("Nothingness")  # word boundaries: no false hit inside a word


def test_decide():
    def arm(n, one, cue, shown, fields=()):
        return {"all": {"n": n, "named_1": one, "one_named_cue": cue, "one_named_shown": shown,
                        "choice_fields": list(fields)}}
    # 90 of 100 name one; 4 of 90 cues (4.4% <= 5%); 86 of 90 shown (95.6% >= 95%) -> F3 holds.
    out, usable = inv.decide({"t0": arm(100, 90, 4, 86), "t1": arm(100, 95, 0, 95)}, {"t0": False, "t1": False})
    assert usable is True and out["t0"]["F3"] and out["t1"]["F3"]
    # 89 of 100 name one -> F3a fails in t0 -> not usable.
    out, usable = inv.decide({"t0": arm(100, 89, 0, 89), "t1": arm(100, 95, 0, 95)}, {"t0": False, "t1": False})
    assert usable is False and not out["t0"]["F3a"]
    # 5 of 90 cues is 5.6% > 5% -> F3b fails.
    out, usable = inv.decide({"t0": arm(100, 90, 5, 90), "t1": arm(100, 95, 0, 95)}, {"t0": False, "t1": False})
    assert usable is False and not out["t0"]["F3b"]
    # A format word in the system text -> review by hand.
    out, usable = inv.decide({"t0": arm(100, 90, 0, 90), "t1": arm(100, 95, 0, 95)}, {"t0": True, "t1": False})
    assert usable == "review"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
