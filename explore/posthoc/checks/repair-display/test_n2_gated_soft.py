"""Tests of the frozen policy G (SPEC-N2-gated-soft.md) on constructed venue data. Run: python3 -I <file>"""
import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("n2", HERE / "n2_gated_soft.py")
n2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n2)

# Constructed venue data in alphabetical order: two hotels (A, C) and three guesthouses (B, D, E) in the north,
# and one hotel elsewhere (F).
DB = [{"name": "A", "type": "hotel", "area": "north"}, {"name": "B", "type": "guesthouse", "area": "north"},
      {"name": "C", "type": "hotel", "area": "north"}, {"name": "D", "type": "guesthouse", "area": "north"},
      {"name": "E", "type": "guesthouse", "area": "north"}, {"name": "F", "type": "hotel", "area": "south"},
      {"name": "G", "type": "guesthouse", "area": "north"}]


def search(f):
    return [v for v in DB if (f.get("type") is None or v["type"] in f["type"]) and v["area"] == f["area"]]


def names(shown):
    return [v["name"] for v in shown]


hotel_north = {"area": "north", "type": ("hotel",)}
# "no" on a hotel-only filter with two hotels displayed: keep A, C first, then append B, D, E in order (5 venues).
shown, n, trig, wid = n2.gated_display(search, hotel_north, "no")
assert names(shown) == ["A", "C", "B", "D", "E"] and n == 2 and trig and wid
assert n2.is_prefix(search(hotel_north)[:5], shown)
# "yes", "unclear" and an invalid answer (None) keep the original display.
for ans in ("yes", "unclear", None):
    shown, n, trig, wid = n2.gated_display(search, hotel_north, ans)
    assert names(shown) == ["A", "C"] and n == 1 and trig and not wid, ans
# A list with both types, a guesthouse filter or no filter: not hotel-only, so no trigger even after "no".
for t in (("hotel", "guesthouse"), ("guesthouse",), None):
    shown, n, trig, wid = n2.gated_display(search, {"area": "north", "type": t}, "no")
    assert not trig and not wid and n == 1, t
# A full display (five or more matches) is never widened.
full = {"area": "north", "type": None}
assert len(search(full)) >= 5
shown, n, trig, wid = n2.gated_display(search, {"area": "north", "type": ("hotel", "guesthouse")}, "no")
assert names(shown) == ["A", "B", "C", "D", "E"] and not trig
# An empty hotel-only search with "no" shows the first five venues without the type filter.
shown, n, trig, wid = n2.gated_display(search, {"area": "east", "type": ("hotel",)}, "no")
assert shown == [] and wid  # no venue in the east at all
# The prefix check detects a reordered display.
assert not n2.is_prefix([{"name": "A"}, {"name": "C"}], [{"name": "C"}, {"name": "A"}])
print("test_n2_gated_soft: all tests passed")
