"""Held-out fit reference: a brief-based bound for the first-request search failures. Post hoc, exploratory, no model
call (the paper review round 7: Sol 1; decisions of round 11, item 4).

The registered held-out measure (main/exp0/analysis.py, part5_a1 b_search_failure) counts a search failure when a
first-request answer keeps hotel and not guesthouse on a natural dialogue where at least one venue fits the brief and
no hotel fits it (group F). This script reads no held-out answer. It reads only:
- main/wave1_ids.json (the dialogue ID lists), from which it takes the 213 stage-1 natural dialogues exactly as
  exp0/analysis.stage1_units does (the natural list without the dialogues of the "sample" list);
- the public MultiWOZ 2.4 goal records (goal.hotel.info and the goal message) and hotel_db.json.
For each reading of fitref_sensitivity.py (recorded, a, b, ab), it groups the 213 dialogues into F (only guesthouses
fit), R (a hotel fits) and N (no venue fits). A search failure can only occur in group F. So, under a reading, a
model's search-failure share can fall by at most (dialogues that leave F) / (its valid answers), and it can rise by at
most (dialogues that enter F) / (its valid answers). Readings a and b only drop requirements, so a dialogue can leave F
only for R, and enter F only from N.
Outputs: r10/analysis/out/heldout_fitref_bound.md and .json. Usage (from explore/):
.venv/bin/python -I r10/analysis/heldout_fitref_bound.py
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fitref_sensitivity as F  # noqa: E402  (it sets the import path; it reads no answer at import)

import anth  # noqa: E402
import gold  # noqa: E402

EXPLORE = HERE.parents[1]
IDS = EXPLORE / "main" / "wave1_ids.json"
OUT = HERE / "out"
EXPECTED = 213
# Valid first-request answers of Table 1 (original form), from the registered result: the smallest is the bound's
# denominator for "any model".
VALID_MIN = 203


def stage1_natural(lists):
    sample = set(lists["sample"])
    return [d for d in lists["natural"] if d not in sample]


def main():
    lists = json.loads(IDS.read_text())
    ids = stage1_natural(lists)
    assert len(ids) == EXPECTED, len(ids)
    data = anth.multiwoz()
    db = gold.hotel_db()
    no_type = [d for d in ids if gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None]
    assert len(no_type) == EXPECTED, len(no_type)
    groups, errors = {}, []
    for r in F.READINGS:
        groups[r] = {}
        for d in ids:
            try:
                groups[r][d] = F.group(F.fitting(data[d], db, r))
            except AssertionError:  # turns.hotel_brief finds no single hotel part
                errors.append((r, d))
                groups[r][d] = groups["recorded"][d]
    no_values, notes, dropped = collections.Counter(), collections.Counter(), 0
    grows = collections.Counter()
    for d in ids:
        info = F.bs.brief_of(data[d])
        for slot in ("parking", "internet"):
            if str(info.get(slot, "")).lower() == "no":
                no_values[f"{slot}=no"] += 1
        before = sum(v for k, v in notes.items() if k[1] is None)
        F.brief_under(data[d], "b", notes)
        dropped += sum(v for k, v in notes.items() if k[1] is None) > before
        rec = len(F.fitting(data[d], db, "recorded"))
        for r in F.READINGS[1:]:
            grows[r] += len(F.fitting(data[d], db, r)) != rec
    res = {"post_hoc": True, "exploratory": True, "reads_answers": False, "dialogues": len(ids),
           "hotel_text_errors": sorted({d for _, d in errors}), "no_values": dict(no_values),
           "b_statement": {f"{k[0]}:{k[1]}": v for k, v in sorted(notes.items(), key=str)},
           "b_briefs_with_a_dropped_requirement": dropped, "briefs_whose_fitting_set_grows": dict(grows),
           "readings": {}}
    for r in F.READINGS:
        g = groups[r]
        moves = collections.Counter(f"{groups['recorded'][d]}->{g[d]}" for d in ids if g[d] != groups["recorded"][d])
        leave = sum(1 for d in ids if groups["recorded"][d] == "F" and g[d] != "F")
        enter = sum(1 for d in ids if groups["recorded"][d] != "F" and g[d] == "F")
        res["readings"][r] = {"F": sum(x == "F" for x in g.values()), "R": sum(x == "R" for x in g.values()),
                              "N": sum(x == "N" for x in g.values()), "moves": dict(moves),
                              "leave_F": leave, "enter_F": enter,
                              "max_fall_points_213": round(100 * leave / EXPECTED, 2),
                              "max_fall_points_any_model": round(100 * leave / VALID_MIN, 2),
                              "max_rise_points_any_model": round(100 * enter / VALID_MIN, 2),
                              "moved_ids": sorted(d for d in ids if g[d] != groups["recorded"][d])}
    L = ["## Held-out fit reference: brief-based bound of the first-request search failures (post hoc)", "",
         "No model call; no held-out answer read. Inputs: main/wave1_ids.json (213 stage-1 natural dialogues: natural "
         "minus sample) and the public MultiWOZ 2.4 goal records. Readings as in fitref_sensitivity.md.", "",
         f"Dialogues: {len(ids)}; hotel-text errors (kept at the recorded group): {res['hotel_text_errors'] or 'none'}",
         "", f"Recorded 'no' values (reading a): {json.dumps(res['no_values'])}. Statement check of reading b "
         f"(slot:kind -> count): {json.dumps(res['b_statement'])}; briefs with a dropped requirement: {dropped}. "
         f"Briefs whose set of fitting venues grows: {json.dumps(res['briefs_whose_fitting_set_grows'])}.",
         "", "| Reading | Only guesthouses fit (F) | A hotel fits (R) | No venue fits (N) | Moves | Leave F | Enter F | "
         "Max fall, points (of 213) | Max fall, points (of 203) | Max rise, points (of 203) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in F.READINGS:
        x = res["readings"][r]
        L.append(f"| {r} | {x['F']} | {x['R']} | {x['N']} | {json.dumps(x['moves'])} | {x['leave_F']} | "
                 f"{x['enter_F']} | {x['max_fall_points_213']:.2f} | {x['max_fall_points_any_model']:.2f} | "
                 f"{x['max_rise_points_any_model']:.2f} |")
    L += ["", "Moved dialogues, per reading: " + "; ".join(
        f"{r}: {', '.join(res['readings'][r]['moved_ids']) or 'none'}" for r in F.READINGS[1:])]
    OUT.mkdir(exist_ok=True)
    (OUT / "heldout_fitref_bound.json").write_text(json.dumps(res, indent=1))
    (OUT / "heldout_fitref_bound.md").write_text("\n".join(L) + "\n")
    print((OUT / "heldout_fitref_bound.md").read_text())


if __name__ == "__main__":
    main()
