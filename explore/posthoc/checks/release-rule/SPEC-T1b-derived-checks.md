# SPEC T1b: derived checks behind the T1 sentences of the paper

Written: 2026-11-15, 23:37 UTC (`date -u` gave 23:36:28 just before writing), **after** the T1 output (`out/t1_compare.*`) and after a first draft of the paper text. `SPEC-T1-rule-comparison.md` stays in force; this spec adds no new simulation, no new scenario and no new threshold.

Status label in the paper: post hoc (as T1).

## Why

Some sentences of the draft summarise `posthoc/release-sim/out/sim.json` over more configurations than the T1 tables show (for example, "the sign condition changed no pass in any setting"). An ad hoc printout checked them while the text was drafted. This spec fixes a script that recomputes each of these summaries from `sim.json`, so that each sentence has a recorded source. If a value differs from the draft, the paper text follows the script.

## Inputs

`posthoc/release-sim/out/sim.json` only (read only).

## Outputs (`out/t1_derived.json`, `out/t1_derived.md`)

1. For every configuration and both levels (C = 4 and C = 10): whether the final rule and the final rule without the sign condition have equal pass counts, and whether the original and revised rules have equal pass counts. Report the number of configurations where they differ.
2. Paper design (59 × 10), no drift, groups A-both and B-spec (shifts), C = 4 and C = 10: the largest difference in flag share between the final rule without and with the sign condition, with its configuration.
3. The same difference for the groups S-sparse, X-cancel and Z-drift (paper design), and for N-size (other designs), C = 4.
4. Zero change, paper design, C = 4: total flags over the three profiles, final rule and final rule without the sign condition (and the number of trials).
5. Zero change with 1 answer per specific request (59 × 1), C = 4: flag share ranges of the original rule, the final rule and the final rule without the sign condition.
6. Batch drift +3 with no schema effect, C = 4: the smallest and largest flag share over the profiles and over the four rules that keep the sets apart.

## Test

`test_t1b.py`: on a hand-made two-configuration `sim.json`-like dictionary, the functions give the expected equal-pass count, largest difference and totals.
