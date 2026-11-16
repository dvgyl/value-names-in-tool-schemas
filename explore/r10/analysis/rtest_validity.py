"""Final-9 count (post hoc report of a stored count): how many first answers of the two
registered tests fitted the closed schema of their form.

The registered stage-1 analysis (prototypes/explore/main/exp0/analysis.py, run once after decryption) calls a read
valid when its row succeeded, stopped at end_turn, its last JSON object parses and fits the closed schema of its form
(fits_schema, "V0"). A read that fails any part is a missing cell, and the analysis stores the reason of each missing
first answer ("read 1") in stage1.json, results/part2_missing. This script reads only that stored file. It opens no
answer file, no folder whose name starts with "em", no sealed file and no key.

This file is a copy of the project analysis (an internal file) with the paths of the study folder and neutral names;
the results are the same. Usage (from explore/): python3 -I r10/analysis/rtest_validity.py
Output: r10/analysis/out/rtest_validity.json and rtest_validity.md.
"""
import collections
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
STAGE1 = EXPLORE / "main" / "exp0" / "stage1.json"
FAMILY = {("nat", "t_legacy"), ("nat", "t_renamed"), ("hot", "t_legacy"), ("hot", "t_renamed")}


def main():
    s = json.loads(STAGE1.read_text())
    miss = s["results"]["part2_missing"]
    cells = miss["cells"]
    fam_missing, fam_reasons, all_reasons, by_model = 0, collections.Counter(), collections.Counter(), collections.Counter()
    for key, e in cells.items():
        model, part, form = key.split()
        for reason, n in e["read1_reasons"].items():
            all_reasons[reason] += n
            if (part, form) in FAMILY:
                fam_reasons[reason] += n
                by_model[model] += n
        if (part, form) in FAMILY:
            fam_missing += sum(e["read1_reasons"].values())
    out = {
        "post_hoc_report_of_a_stored_count": True,
        "rule": miss["rule"],
        "family_read1_cells": miss["family_read1_cells"],
        "family_read1_missing_stored": miss["family_read1_missing"],
        "family_read1_missing_recounted": fam_missing,
        "family_read1_valid": miss["family_read1_cells"] - miss["family_read1_missing"],
        "family_read1_missing_reasons": dict(fam_reasons),
        "family_read1_missing_by_model": dict(by_model),
        "family_read1_schema_failures": fam_reasons.get("schema (V0)", 0),
        "all_parts_read1_missing_reasons": dict(all_reasons),
        "all_parts_read1_schema_failures": all_reasons.get("schema (V0)", 0),
        "note": "family = the two registered tests: parts nat (213 open dialogues) and hot (77 specific dialogues), forms "
                "t_legacy and t_renamed, 7 models: 7 x 290 x 2 = 4,060 first answers. Only first answers have stored "
                "reasons; the repeat answers of 20% of the dialogues are not counted here.",
    }
    assert out["family_read1_missing_recounted"] == out["family_read1_missing_stored"]
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "rtest_validity.json").write_text(json.dumps(out, indent=1))
    md = ["## Final-9: validity of the first answers of the registered tests (stored count, reported post hoc)", ""]
    md += [f"- {k}: {v}" for k, v in out.items()]
    (HERE / "out" / "rtest_validity.md").write_text("\n".join(md) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
