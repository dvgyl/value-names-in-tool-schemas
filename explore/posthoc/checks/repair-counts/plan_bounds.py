"""Post hoc bounds from stored result files for the the paper plan revision (2026-11-15). No model call, no answer file.

Usage (from explore/): python3 -I posthoc/checks/repair-counts/plan_bounds.py [out.json]

Inputs (stored outputs only):
- main/exp0/stage1.json, results.part1_family.tests: the registered goal-hotel mean (77 dialogues).
- r10/analysis/out/heldout_confirm.json: the held-out repair test (totals per model and set NT, H, G; `missing`).

1. NS-01. Each dialogue change of the registered test is a mean of per-model changes in {-1, 0, +1}, so it lies in
   [-1, +1]. With mean m over 77 dialogues and 11 dialogues whose final request sets guesthouse, the mean over the 66
   others is at most (77 m + 11) / 66 (all 11 at -1) and at least (77 m - 11) / 66 (all 11 at +1).
2. NS-06. Zero losses on n independent filters: one-sided 95% upper bound 1 - 0.05^(1/n).
3. NS-08. Worst and best assignments of the missing first answers of the held-out test, at the point estimates:
   - value level, planned gate: the loss ratio (label-group mix) is (lost / H_dialogues x 545) /
     (removed / NT_dialogues x 994), as in result.json; a missing no-type answer can add an original filter (kept or
     removed); a missing hotel answer can add a loss only on a stated brief;
   - display level: a missing no-type dialogue can change a paired difference (policy minus verifier) by -1 or +1.
   - review fix (2026-11-15): `rule_met_if`, the fewest removed filters among the missing no-type answers that make
     the point estimates meet the rule, without and with a loss on the missing stated brief.
4. NS-09. Verifier calls per first answer (read 1) and second searches per first answer in the held-out test.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]  # explore/ of the repository
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent / "out/plan_bounds.json"
WH, WNT = 545, 994


def ratio(lost, nh, removed, nnt):
    return (lost / nh * WH) / (removed / nnt * WNT) if removed > 0 else float("inf")


def main():
    out = {"post_hoc": True}
    # 1. NS-01
    tests = json.loads((ROOT / "main/exp0/stage1.json").read_text())["results"]["part1_family"]["tests"]
    gh = [t for t in tests if t["sample"] == "goal_hotel"][0]
    m, n, k = gh["mean"], gh["dialogues"], 11
    out["ns01"] = {"registered_mean": m, "dialogues": n, "final_guesthouse": k,
                   "mean_66_at_most_points": 100 * (n * m + k) / (n - k),
                   "mean_66_at_least_points": 100 * (n * m - k) / (n - k)}
    # 2. NS-06
    out["ns06_zero_loss_bound"] = {str(x): 1 - 0.05 ** (1 / x) for x in (13, 17, 18)}
    # 3. NS-08 and 4. NS-09
    res = json.loads((ROOT / "r10/analysis/out/heldout_confirm.json").read_text())["models"]
    full = {"NT": 213, "H": 66, "H stated": 18}
    ns08, ns09 = {}, {}
    for mod, v in res.items():
        wr = v["read1"]["value"]["planned"]["word_rule"]
        br = v["read1"]["value"]["planned"]["brief"]
        dn = wr["dialogues"]
        nnt, nh = dn["NT"], dn["H stated"] + dn["H not stated"]
        miss_nt, miss_h = full["NT"] - nnt, full["H"] - nh
        miss_st = full["H stated"] - dn["H stated"]
        orig, rem, lost = wr["original_values_NT"], wr["removed"], wr["lost_stated"]
        row = {"missing_first_answers": {"NT": miss_nt, "H": miss_h, "H stated": miss_st},
               "observed": {"share_removed": rem / orig, "ratio": ratio(lost, nh, rem, nnt),
                            "ratio_stored": wr["ratio"][0], "brief_ratio": ratio(br["lost"], nh, br["removed"], nnt),
                            "brief_ratio_stored": br["ratio"][0]}}
        if miss_nt or miss_h:
            # worst for the rule: every missing NT answer has a filter that the gate keeps; every missing stated brief loses one
            row["worst"] = {"share_removed": rem / (orig + miss_nt),
                            "ratio": ratio(lost + miss_st, full["H"], rem, full["NT"])}
            # best for the rule: every missing NT answer has a filter that the gate removes; no missing brief loses
            row["best"] = {"share_removed": (rem + miss_nt) / (orig + miss_nt),
                           "ratio": ratio(lost, full["H"], rem + miss_nt, full["NT"]),
                           "brief_ratio": ratio(br["lost"], full["H"], br["removed"] + miss_nt, full["NT"])}
            # review fix (2026-11-15): the fewest removed filters among the missing no-type answers that make the
            # point estimates meet the rule (share >= 0.5 and ratio <= 0.30), with the other missing no-type answers
            # holding a filter that the gate keeps (the lowest share), without and with a loss on each missing stated brief
            need = {}
            for extra_loss in (0, miss_st):
                k = next((k for k in range(miss_nt + 1)
                          if (rem + k) / (orig + miss_nt) >= 0.5
                          and ratio(lost + extra_loss, full["H"], rem + k, full["NT"]) <= 0.30), None)
                need[f"missing_stated_losses_{extra_loss}"] = None if k is None else {
                    "removals_needed": k, "share_removed": (rem + k) / (orig + miss_nt),
                    "ratio": ratio(lost + extra_loss, full["H"], rem + k, full["NT"]),
                    "ratio_one_fewer": ratio(lost + extra_loss, full["H"], rem + k - 1, full["NT"]) if k else None}
            row["rule_met_if"] = need
            disp = v["read1"]["display"]
            for key in ("relax_minus_verifier", "soft_minus_verifier"):
                dd = disp[key]["dialogues"][0]
                row[key] = {"observed_points": disp[key]["points"][0],
                            "worst_points": 100 * (dd - miss_nt) / full["NT"],
                            "best_points": 100 * (dd + miss_nt) / full["NT"]}
        ns08[mod] = row
        va = v["read1"]["verifier_answers"]
        calls = sum(sum(x.values()) for x in va.values())
        disp = v["read1"]["display"]
        ns09[mod] = {"first_answers": disp["answers"], "verifier_calls_read1": calls,
                     "calls_per_first_answer": calls / disp["answers"],
                     "verifier_calls_all_reads": sum(sum(x.values()) for x in v["mean"]["verifier_answers"].values()),
                     "second_search_share_relax": disp["searches_per_answer"]["relax_any"] - 1,
                     "second_search_share_soft": disp["searches_per_answer"]["soft"] - 1,
                     "relax_any_on_H": disp["relax_any_on_H"]}
    out["ns08"] = ns08
    out["ns09"] = ns09
    out["ns09_total_calls_all_reads"] = sum(r["verifier_calls_all_reads"] for r in ns09.values())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
