# SPEC T3: higher-precision bootstrap for every actual release decision

Written: 2026-11-15, 22:55 UTC (`date -u` gave 22:54:43 just before writing), before any T3 output.

Status label in the paper: **post hoc numerical sensitivity**. The 2,000-draw decisions (seed 20261112) stay the primary results with their original status. The new computation changes no answer, request, pairing, averaging, validity rule, L, C, index convention or decision order.

## Exposure

The writer has seen the 2,000-draw decisions and intervals of every comparison below (they are in the paper), the 20-seed and 20,000-draw results of `posthoc/release-sim/out/tails_stored.*` and `posthoc/release-fresh/out/sensitivity.*`. The 100,000-draw values below have not been computed before.

## Fixed settings

- Draws: B = 100,000.
- Seeds: 20271101, 20271102, 20271103, 20271104, 20271105 (five seeds, all reported; none is chosen or dropped after the output).
- Bootstrap: the frozen procedure of the paper (`rtest_final9.boot`, `release-sim/stored.py boot_vals`, the same draws as `stats.cluster_bootstrap`): for one set, `rng = random.Random(seed)`, then B times the mean of `rng.choices(diffs, k=n)`, sorted. `diffs` are the paired per-request differences (points), so whole requests are resampled with their old/new pairing; the answers of one request are averaged before resampling, as in the paper. Each set has its own `random.Random(seed)`, as in the frozen code.
- Index conventions, unchanged, with B in place of 2,000 (a = (1 − level)/2):
  - original and revised rules (as run, stats.percentile): low end = sorted value at index round(a B) − 1, high end = sorted value at index round((1 − a) B) − 1 (0-based, clipped to [0, B − 1]);
  - final rule (symmetric): k = max(1, floor(a B + 1e-9)); low end = k-th lowest, high end = k-th highest.
- Rules (`posthoc/release-sim/rules.py`, unchanged): set classes flag condition / within limits / unresolved; model decision: flag if a set meets the flag condition, else pass if both sets are within limits, else hold (one look with all requests). Sign condition (revised, final): exact two-sided sign test p ≤ 1 − level. Zero-width condition (final): a zero-width interval is never within limits. L = 5 points.

## Comparisons and the rules and levels the paper reports for each

| Group | Comparisons | Data loader (stored answers; no `em*` folder) | Rules: level |
|---|---|---|---|
| Five-model test (Tables 5, 13) | Sol, Luna, DeepSeek, Qwen, Gemma × repeat, paraphrase 1, full rename (15) | `release-sim/stored.py comparisons()` ("R10-20 …"), runs `erk_*` | original and revised: 98.75% (tool calls) or 99.17% (forms); final: 99.5% |
| Two-model test (Tables 5, 13) | Sol, Luna × field-order edit, paraphrase 2 (4) | `stored.py comparisons()` ("R10-22 …"), runs `erk2_*` | original, revised, final: 98.75% |
| Haiku controls (Tables 5, 12) | repeat, field-order edit; all answers (2) and first answer only (2) | `stored.py comparisons()` ("R10-16 …"), runs `erc_haiku`, `erc2_haiku` | all answers: original and revised 98.75%; final 99.58% (repeat, C = 12) and 99.17% (field-order edit, C = 6). First answer only: original 98.75% |
| Stored comparisons (Table 9) | 29 pairs of stored answers to the unchanged tool | `stored.py comparisons()` ("unchanged …") | original and revised 98.75%; final 99.5% |
| Fresh test (Table 11) | Luna × 5 updates, Sol × repeat and full rename (7) | `release-fresh/analyze.py` (`load`, `diffs`, `f27.select`), runs `erk4_luna`, `erk4_sol` | final, revised, original at the update's level: 98.75% (repeat, full rename) or 97.5% (other updates) |
| Steered rewrites (Table 14) | Sonnet, Haiku × hotel and guesthouse rewrites (4) | `rtest_v.tool_reads` as in `rtest_final9.part_b` (`erp_sonnet` t0, `ers_haiku` t0, `ers_*` th and tg; first answer) | original and revised: 98.75% |
| Broad rewrite (Section 7, Appendix J) | Sonnet, Sol (2) | `rtest_v.tool_reads` as in `rtest_final9.part_b` (`erp_*` t0 and tedit; first answer) | original: 98.75% |
| Replication (Section 7, Appendix I) | DeepSeek paraphrase 1, Luna paraphrase 2 (2) | `r10/analysis/release_test3.py` (`load`, request sets, cells) on `erk3_deepseek`, `erk3_luna` | original and revised: 99.17% (DeepSeek), 98.75% (Luna) |

Every 2,000-draw decision of the paper must be reproduced first (seed 20261112, 2,000 draws, same code path), against the stored outputs: `release-sim/out/fidelity.json` (first four groups), `release-fresh/out/result.json`, `r10/analysis/out/rtest_final9.json` (`B.edits`) and `r10/analysis/out/release_test3.json`. If any decision or interval end (to 1e-6 points) differs, the analysis stops and the report says so; nothing is fitted or changed to make them agree.

## Outputs per comparison and rule

- the 2,000-draw decision (primary) and its intervals;
- the 20,000-draw decision where a stored output has one (`tails_stored.json` key `<level>|<rule>|20000`; `sensitivity.json` `draws_20000`); no new 20,000-draw computation;
- for each of the five seeds: the 100,000-draw decision and the interval ends of both sets;
- for each set: the range over the five seeds of the low end and of the high end;
- the *boundary responsible*: for a decision that differs between seeds or from the 2,000-draw decision, the boundary (0, +L or −L, and the set) that an interval end crosses; for a stable decision, the nearest boundary whose crossing would change the decision and the smallest distance of the relevant end to it over the six computations (2,000 draws and the five seeds). Definitions: a pass changes if any end of either set crosses ±L; a flag changes only if every set that meets the flag condition loses it (its end nearest zero crosses 0); a hold becomes a flag if a set with |change| ≥ L and a passing sign test gets an interval that excludes 0, and becomes a pass only if every set gets both ends within ±L (not possible for a zero-width interval under the final rule).

Files: `posthoc/checks/release-rule/out/t3_diffs.json` (the per-request differences and metadata; collected by `t3_collect.py`), `t3_bootstrap.json` and `t3_bootstrap.md` (by `t3_boot.py`).

## Paper

- Main text: one summary sentence or two in Section 7 with the counts of decisions that keep or change their decision, and the three uncertainty types kept apart (bootstrap Monte Carlo error, finite requests, batch variation).
- Appendix: one table that lists every rule-decision whose 100,000-draw decision differs from its 2,000-draw decision for at least one seed, or whose five seeds disagree, with the original decision, the 20,000-draw decision where stored, the endpoint range of the deciding set, the five decisions and the boundary responsible; and one line that counts all other rule-decisions and gives their smallest distance to a boundary. This row rule is fixed here and is not changed after the output.

## Tests

`test_t3.py`: the as-run and symmetric indices for B = 2,000 and B = 100,000 at 97.5%, 98.75%, 99.17%, 99.5% and 99.58% (hand values: 98.75%, B = 2,000: as run 12th lowest and 13th highest, symmetric k = 12; B = 100,000: as run index 624 and 99374, symmetric k = 625); the bootstrap with B = 2,000 and seed 20261112 equals `stored.boot_vals` on a small list; the boundary function on hand cases (a pass at [−4.9, +1.0] responsible −L; a flag at [+0.3, +9] responsible 0; a hold with [−6, +6] and |change| < L responsible ±L).
