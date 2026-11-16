# SPEC T1: comparison of the release rules on the same simulated datasets

Written: 2026-11-15, between 22:53:27 and 22:54:00 UTC (`date -u`), before any T1 output.

Status label in the paper: **post hoc** (a new tabulation of an existing exploratory simulation; the rules were chosen before the simulation, and this comparison was chosen after the simulation results were seen).

## What already exists (checked before this spec)

- Exposure: before writing this spec, the writer read `posthoc/release-sim/REPORT.md` (which gives many of these shares as ranges) and printed the stored counts of the A-both, S-sparse and X-cancel configurations of the paper design. T1 is a new tabulation of outputs that already exist and were already seen; the spec fixes which outputs enter the paper and how they are summarised.

- `posthoc/release-sim/sim.py` (amendment R10-26) ran 126 configurations with 2,000 trials each. In every trial, all five rules (original, revised, final, final without the sign condition `strat_nosign`, pooled) were applied to the **same simulated data and the same bootstrap draws** (`run_config`: one `rng_data` and one `rng_boot` stream per configuration; seeds `release-sim-R10-26|<configuration id>|data` and `|boot`). The decisions of every rule are stored as counts in `posthoc/release-sim/out/sim.json` (`summaries[*].levels[C].decisions[rule][flag|pass|hold] = {k, n, share, ci95}`; `raw_tallies` holds the same counts).
- Therefore T1 needs **no new simulation, no new trials and no refit of the profiles**. T1 reads `sim.json` only.

## Inputs

- `posthoc/release-sim/out/sim.json` (read only). No other input.

## Rules (as defined in `posthoc/release-sim/rules.py`; unchanged)

| Name in the paper | Key | Index of interval ends | Sign condition | Zero-width condition |
|---|---|---|---|---|
| Original rule | `original` | as run (stats.percentile) | no | no |
| Revised rule | `revised` | as run | yes | no |
| Final rule | `final` | symmetric | yes | yes |
| Final rule without the sign condition | `strat_nosign` | symmetric | no | yes |
| Pooled interval (secondary diagnostic) | `pooled` | symmetric, one interval over all 507 requests at level 1 − 0.05/(C/2) | no | no |

The final rule without the sign condition differs from the final rule only in the sign condition. All rules in one comparison use the same level (the same C). The final rule's change in how C is counted changes the level of a release, not the rule at a given level, so it is not part of this comparison (stated in the paper).

## Level

- Primary: C = 4 (98.75%; pooled 97.5%), as in the existing Appendix L.
- Also tabulated in the output files (not in the paper tables): C = 10 (99.5%).

## Scenarios (paper design: 448 open requests × 1 answer, 59 specific requests × 10 answers, unless stated)

| Scenario | Configuration ids in `sim.json` (profile ∈ haiku, deepseek, sol) |
|---|---|
| Zero change | `A-both|<profile>|no change|n59m10` |
| Broad shift beyond the margin | `A-both|<profile>|shift +6 both|n59m10` |
| Specific-only shift beyond the margin | `B-spec|<profile>|shift +6 specific|n59m10` |
| Sparse change on 6 specific requests | `S-sparse|haiku|sparse +8 specific|n59m10`, `S-sparse|deepseek|sparse +8 specific|n59m10`, `S-sparse|sol|sparse -8 specific|n59m10` |
| Cancelling changes, specific set (up to 12 down, 12 up) | `X-cancel|<profile>|cancel 12 down 12 up specific|n59m10` |
| Cancelling changes, open set (10 down, 10 up) | `X-cancel|<profile>|cancel 10 down 10 up open|n59m10` |
| Batch drift +3 with no schema effect | `Z-drift|<profile>|no effect, drift +3|n59m10` |
| Batch drift −3 with a true +6 shift in both sets | `Z-drift|<profile>|shift +6 both, drift -3|n59m10` |
| Zero change, 1 answer per specific request | `N-size|haiku|no change|n59m1`, `N-size|deepseek|no change|n59m1` |

**Change beyond the margin (wrong-pass summary).** All configurations of the paper design without drift (`group` in A-both, B-spec, S-sparse; `design` 59 × 10) whose true change exceeds L = 5 points in size in at least one set. For each rule: the number of wrong passes summed over these configurations and trials, the total trials, and the largest wrong-pass share of one configuration (with its id and its Wilson interval).

## Outcomes

- For each scenario, profile and rule: flag, pass and hold shares, each with k, n (n = 2,000 trials) and the Wilson 95% interval as stored in `sim.json` (`ci95`, z = 1.959964). The script recomputes the Wilson interval from k and n and checks that it equals the stored one.
- False flag = a flag when the true change is 0 in both sets (zero change, cancelling, drift with no effect). Wrong pass = a pass when the true change exceeds L in size in at least one set. A hold is reported separately; it is neither a detection nor a pass.
- Ranges across profiles: the smallest and largest share across the profiles of a scenario. They are **ranges, not intervals**, and their ends can come from different profiles (the paper says so).

## Outputs

- `posthoc/checks/release-rule/out/t1_compare.json` and `t1_compare.md`: the full scenario-by-profile-by-rule table (C = 4 and C = 10), the ranges, and the wrong-pass summary.
- Paper: a compact table in Section 7 (ranges, C = 4; original, final, final without the sign condition) and the full scenario-by-profile table in Appendix L (all five rules, C = 4).

## Decision rule for the interpretation (fixed now)

The paper states the conclusion that the numbers support. In particular: (1) if the final rule and the final rule without the sign condition give flag shares that differ by at most 1 point on zero-change, broad-shift and specific-only-shift scenarios but differ by more than 20 points on sparse changes, the paper says that the sign condition trades sparse-change flags for holds and is not uniformly preferable; (2) if the no-sign variant has a higher false-flag share than the final rule in a scenario, the paper says so with the numbers; (3) holds on unchanged updates are reported as an operational cost, not as protection; (4) the pooled interval is reported as a secondary diagnostic only. No other threshold or subset is chosen after the output.

## Tests

`test_t1.py`: Wilson interval on known cases (k = 0, n = 2,000; k = 80, n = 2,000 computed by hand), the k counts of one configuration equal `raw_tallies`, flag + pass + hold = n for every row, and a hand-checked cell (Haiku zero change, final rule: 0 / 1,920 / 80).
