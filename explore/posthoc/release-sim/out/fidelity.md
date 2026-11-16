# Fidelity check: the simulation's rule code on the stored comparisons (R10-26)

Result: **282 of 282 checks pass** (all).

The rule code of the simulation (`rules.py`) with the frozen bootstrap (random.choices over requests, seed 20261112, 2,000 draws), on the stored per-request answers read by the frozen loaders. Compared with the stored results in `r10/analysis/out/` (release_test.json, release_test2.json, control.json, rtest_final9.json, rtest_check_values.json) and with Tables 5, 11 and 12 of the paper (parsed from the master text).

## 29 stored unchanged-tool comparisons (one answer per request)

| Rule and level | Flag | Pass | Hold |
|---|---:|---:|---:|
| original 98.75% | 2 | 2 | 25 |
| revised 98.75% | 0 | 2 | 27 |
| final 99.5% | 0 | 0 | 29 |

## Decisions of Tables 11 and 12

| Comparison | Open: change [interval as run]; up / down | Specific | Original | Revised | Final (level) |
|---|---|---|---|---|---|
| R10-20 sol a | −0.7 [−2.5, +0.9]; 3 / 6 | +0.0 [−1.7, +1.9]; 5 / 5 | pass | pass | pass (99.50%) |
| R10-20 sol b | −0.4 [−2.5, +1.3]; 5 / 7 | −0.2 [−2.5, +2.4]; 6 / 7 | pass | pass | pass (99.50%) |
| R10-20 sol c | −22.5 [−27.9, −17.9]; 0 / 101 | −62.0 [−74.6, −48.6]; 0 / 46 | flag | flag | flag (99.50%) |
| R10-20 luna a | −2.2 [−4.7, +0.0]; 3 / 13 | +0.5 [−2.4, +3.7]; 5 / 7 | pass | pass | hold (99.50%) |
| R10-20 luna b | −3.1 [−5.8, −0.7]; 4 / 18 | +2.0 [−3.9, +8.0]; 8 / 6 | hold | hold | hold (99.50%) |
| R10-20 luna c | −18.8 [−23.4, −14.3]; 0 / 84 | −33.7 [−49.8, −20.0]; 0 / 27 | flag | flag | flag (99.50%) |
| R10-20 deepseek a | +2.0 [−1.1, +5.4]; 20 / 11 | +3.4 [−0.5, +7.6]; 18 / 5 | hold | hold | hold (99.50%) |
| R10-20 deepseek b | +1.1 [−2.5, +4.5]; 20 / 15 | +5.9 [+1.5, +10.7]; 21 / 5 | flag | flag | flag (99.50%) |
| R10-20 deepseek c | −15.2 [−20.1, −10.7]; 0 / 68 | −30.0 [−43.9, −17.1]; 0 / 28 | flag | flag | flag (99.50%) |
| R10-20 qwen a | +0.5 [−3.3, +3.8]; 16 / 14 | −0.7 [−7.1, +4.7]; 15 / 17 | hold | hold | hold (99.50%) |
| R10-20 qwen b | +0.2 [−3.1, +3.6]; 15 / 14 | +0.6 [−5.9, +6.8]; 18 / 11 | hold | hold | hold (99.50%) |
| R10-20 qwen c | −12.3 [−17.2, −8.2]; 3 / 54 | −30.1 [−42.5, −18.2]; 0 / 33 | flag | flag | flag (99.50%) |
| R10-20 gemma a | +0.0 [−1.6, +1.4]; 3 / 3 | +2.0 [−0.0, +4.7]; 7 / 1 | pass | pass | pass (99.50%) |
| R10-20 gemma b | +0.7 [−1.4, +2.7]; 7 / 4 | +1.7 [−4.7, +7.6]; 5 / 3 | hold | hold | hold (99.50%) |
| R10-20 gemma c | −20.5 [−25.7, −15.8]; 0 / 91 | −49.7 [−66.4, −33.6]; 0 / 32 | flag | flag | flag (99.50%) |
| R10-22 sol d | −1.8 [−3.8, +0.0]; 2 / 10 | −1.2 [−5.8, +3.4]; 5 / 8 | hold | hold | hold (98.75%) |
| R10-22 sol e | −0.2 [−2.5, +1.8]; 6 / 7 | −0.5 [−4.6, +3.7]; 5 / 8 | pass | pass | pass (98.75%) |
| R10-22 luna d | +3.8 [+1.1, +6.7]; 22 / 5 | +3.9 [−2.0, +11.0]; 9 / 5 | hold | hold | hold (98.75%) |
| R10-22 luna e | −1.1 [−4.0, +1.6]; 10 / 15 | −5.9 [−12.2, −1.0]; 4 / 12 | flag | hold | hold (98.75%) |
| R10-16 haiku a (all answers) | +0.2 [−0.9, +1.6]; 3 / 2 | +0.1 [−1.8, +2.2]; 4 / 4 | pass | pass | pass (99.58%) |
| R10-16 haiku d (all answers) | +0.2 [−1.8, +2.2]; 7 / 6 | +1.2 [−3.6, +6.6]; 4 / 5 | hold | hold | hold (99.17%) |
| R10-16 haiku a (first answer) | +0.2 [−0.9, +1.6]; 3 / 2 | −1.7 [−10.2, +5.1]; 1 / 2 | hold | hold | hold (99.58%) |
| R10-16 haiku d (first answer) | +0.2 [−1.8, +2.2]; 7 / 6 | −5.1 [−16.9, +3.4]; 1 / 4 | hold | hold | hold (99.17%) |

## Failed checks

None.
