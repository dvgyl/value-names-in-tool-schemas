"""Stored counts (post hoc report; no model call, no answer file).

1. Validity of the first answers behind Table 1 (part "pre": original, renamed and serviced_property forms) and the two
   registered tests (parts "nat" and "hot", original and renamed forms). Source: main/exp0/stage1.json,
   results.part2_missing (the registered analysis stores the reason of each missing first answer; "schema (V0)" is
   the closed-schema check). The script opens no answer file, no folder whose name starts with "em", no sealed file
   and no key.
2. The final type of the 77 first-analysis dialogues of the registered hotel sample. Source: main/wave1_ids.json
   (goal_hotel minus the Track P sample; the sample rule of main/wave1.py: hotel in goal.hotel.info or fail_info)
   and the public corpus (data.json).
3. A bound for Test 2 on the 66 dialogues whose final requirement is hotel, from the stored registered mean
   (results.part1_family): each dialogue mean of model differences lies in [-1, +1], so the sum over the other 66 is
   at most 77 * mean + 11.
Usage (from explore/): python3 -I r10/analysis/loyal_stored_counts.py
Outputs: r10/analysis/out/loyal_stored_counts.md and loyal_stored_counts.json. It needs the public corpus (lib/anth.py, DATA).
This file is a copy of the project script stored_counts.py with the paths of the study folder and the names of its output files changed; the results are the same. The title line of the Markdown output does not name the paper.
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
sys.path.insert(0, str(EXPLORE / "lib"))
import anth  # noqa: E402  (the corpus folder)

DATA = anth.DATA / "data.json"
PANEL = 7


def main():
    s = json.loads((EXPLORE / "main" / "exp0" / "stage1.json").read_text())
    miss = s["results"]["part2_missing"]
    by = collections.defaultdict(collections.Counter)
    for key, e in miss["cells"].items():
        model, part, form = key.split()
        for reason, n in e["read1_reasons"].items():
            by[(part, form)][reason] += n
    table1_forms = ("t_legacy", "t_renamed", "f4")
    t1_missing = collections.Counter()
    for f in table1_forms:
        t1_missing.update(by[("pre", f)])
    out = {
        "table1_first_answers": PANEL * 213 * len(table1_forms),
        "table1_missing_reasons": dict(t1_missing),
        "table1_missing_by_form": {f: dict(by[("pre", f)]) for f in table1_forms},
        "tests_first_answers": miss["family_read1_cells"],
        "tests_missing": miss["family_read1_missing"],
        "schema_failures_all_parts": sum(c.get("schema (V0)", 0) for c in by.values()),
    }
    assert out["tests_first_answers"] == PANEL * (213 + 77) * 2
    ids = json.loads((EXPLORE / "main" / "wave1_ids.json").read_text())
    data = json.loads(DATA.read_text())
    sample = set(ids["sample"])
    hot = [k for k in ids["goal_hotel"] if k not in sample]
    assert len(hot) == 77
    types = collections.Counter()
    for k in hot:
        g = data[k]["goal"]["hotel"]
        types[f"first choice {g.get('fail_info', {}).get('type')}, final {g.get('info', {}).get('type')}"] += 1
    final_hotel = sum(1 for k in hot if data[k]["goal"]["hotel"].get("info", {}).get("type") == "hotel")
    out["hotel_sample_77_types"] = dict(types)
    out["hotel_sample_77_final_hotel"] = final_hotel
    test2 = next(t for t in s["results"]["part1_family"]["tests"] if t["test"] == "correct_values_kept")
    assert test2["dialogues"] == 77
    other = 77 - final_hotel
    bound = (77 * test2["mean"] + other) / final_hotel
    out["test2_mean"] = test2["mean"]
    out["test2_bound_on_final_hotel"] = {"dialogues": final_hotel, "largest_possible_mean": bound,
                                         "formula": f"(77 x {test2['mean']} + {other}) / {final_hotel}"}
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "loyal_stored_counts.json").write_text(json.dumps(out, indent=1))
    md = ["## Stored counts (post hoc report; no model call, no answer file)", ""]
    md += [f"- {k}: {v}" for k, v in out.items()]
    (HERE / "out" / "loyal_stored_counts.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
