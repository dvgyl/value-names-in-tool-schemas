"""the paper, no model call: the dialogue sets behind the booked-venue column of Table 1.

Reads only the corpus (dialogues, briefs, the dialogue state) and hotel_db.json for the 213 held-out no-type
dialogues of the first analysis (main/exp0/analysis.stage1_units). It reads no model answer and no sealed file.
Output: the number of dialogues with a matched booking (the rule of main/exp0/analysis.py: zruns.booked_venue),
the type of the booked venue, the number of dialogues where only guesthouses fit the brief, the overlap of the two
sets, and the number of briefs that name a venue.
Usage (from explore/):
  python3 -I r10/analysis/loyal_booked_sets.py [out folder]
The default out folder is r10/analysis/out.
This file is a copy of the project script loyal_booked_sets.py with the paths of the study folder; the results are the same.
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parents[1]  # this file is in explore/r10/analysis/
for sub in ("lib", "forms", "pmain", "trackc", "r9", "r9/natural", "r9/additions", "r9/free", "main", "r10"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(EXPLORE / "main" / "exp0"))
import analysis  # noqa: E402  (only stage1_units)
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import wave1  # noqa: E402
import zruns  # noqa: E402


def main(out_dir):
    data, _ = runs.context()
    units, _ = analysis.stage1_units(wave1.ids())
    nat = [d + ".json" for d in units["natural"]]
    db = gold.hotel_db()
    by_key = {zruns._key(h["name"]): h for h in db}
    venue = {d: v for d in nat if (v := zruns.booked_venue(data[d], by_key))}
    fit = {d: bs.brief_fitting(data[d], db) for d in nat}
    only_gh = {d for d in nat if fit[d] and not any(v["type"] == "hotel" for v in fit[d])}
    res = {"no_type_dialogues": len(nat), "matched_booking": len(venue),
           "booked_type": dict(collections.Counter(v["type"] for v in venue.values())),
           "only_guesthouses_fit": len(only_gh), "overlap": len(set(venue) & only_gh),
           "briefs_name_a_venue": sum(1 for d in nat if bs.brief_of(data[d]).get("name"))}
    assert res["no_type_dialogues"] == 213 and res["matched_booking"] == 128, res
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "loyal_booked_sets.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "out")
