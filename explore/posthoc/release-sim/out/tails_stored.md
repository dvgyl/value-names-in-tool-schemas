# Tails of the percentile interval on the stored comparisons (R10-26)

Frozen bootstrap (random.choices over requests). Levels: the level as run (Tables 11 and 12: 98.75% or 99.17%), the final rule's level, and 99.5%. Seeds 20261112 to 20261131 with 2,000 draws; 20,000 draws with seed 20261112. Original and revised rules: as-run index; final rule: symmetric index; orig_sym: the original rule with the symmetric index.

Comparisons: 52. Comparisons with a decision that changes with the seed (any rule, any level): 6; with 20,000 draws: 2; with the index: 0.

| Comparison | Level: rule | Decision (seed 20261112) | Decisions over 20 seeds | 20,000 draws |
|---|---|---|---|---|
| R10-20 luna a | 99.5 (99.50%): final | hold | {"hold": 6, "pass": 14} | pass |
| R10-20 luna a | 99.5 (99.50%): orig_sym | hold | {"hold": 6, "pass": 14} | - |
| R10-20 luna a | 99.5 (99.50%): original | hold | {"hold": 5, "pass": 15} | pass |
| R10-20 luna a | 99.5 (99.50%): revised | hold | {"hold": 5, "pass": 15} | pass |
| R10-20 luna a | final (99.50%): final | hold | {"hold": 6, "pass": 14} | pass |
| R10-20 luna a | final (99.50%): orig_sym | hold | {"hold": 6, "pass": 14} | - |
| R10-20 luna a | final (99.50%): original | hold | {"hold": 5, "pass": 15} | pass |
| R10-20 luna a | final (99.50%): revised | hold | {"hold": 5, "pass": 15} | pass |
| R10-20 gemma a | 99.5 (99.50%): final | pass | {"pass": 18, "hold": 2} | pass |
| R10-20 gemma a | 99.5 (99.50%): orig_sym | pass | {"pass": 18, "hold": 2} | - |
| R10-20 gemma a | final (99.50%): final | pass | {"pass": 18, "hold": 2} | pass |
| R10-20 gemma a | final (99.50%): orig_sym | pass | {"pass": 18, "hold": 2} | - |
| R10-22 sol e | 99.5 (99.50%): final | pass | {"pass": 8, "hold": 12} | hold |
| R10-22 sol e | 99.5 (99.50%): orig_sym | pass | {"pass": 8, "hold": 12} | - |
| R10-22 sol e | 99.5 (99.50%): original | pass | {"pass": 9, "hold": 11} | hold |
| R10-22 sol e | 99.5 (99.50%): revised | pass | {"pass": 9, "hold": 11} | hold |
| R10-22 luna e | 99.5 (99.50%): orig_sym | flag | {"flag": 15, "hold": 5} | - |
| unchanged sonnet: era1 read 1 v era1 read 2 | run (98.75%): orig_sym | flag | {"flag": 15, "hold": 5} | - |
| unchanged sonnet: era1 read 1 v era1 read 2 | run (98.75%): original | flag | {"flag": 15, "hold": 5} | flag |
| unchanged sonnet: era1 read 1 v erp | run (98.75%): orig_sym | flag | {"flag": 15, "hold": 5} | - |
| unchanged sonnet: era1 read 1 v erp | run (98.75%): original | flag | {"flag": 15, "hold": 5} | flag |

Decisions that change with the index rule (seed 20261112, 2,000 draws; original rule):

- none

Range of the as-run interval ends over the 20 seeds, Table 11 and 12 comparisons at 99.5% (points):

| Comparison | Open low | Open high | Specific low | Specific high |
|---|---|---|---|---|
| R10-20 sol a | -2.90 to -2.46 | +1.12 to +1.34 | -2.20 to -1.86 | +1.69 to +2.20 |
| R10-20 sol b | -2.90 to -2.46 | +1.34 to +1.79 | -3.39 to -2.71 | +2.54 to +2.88 |
| R10-20 sol c | -29.02 to -27.68 | -17.63 to -16.74 | -78.14 to -75.59 | -48.31 to -44.92 |
| R10-20 luna a | -5.36 to -4.69 | -0.22 to +0.45 | -2.88 to -2.37 | +3.90 to +4.92 |
| R10-20 luna b | -6.47 to -5.80 | -0.67 to +0.00 | -5.59 to -3.73 | +8.31 to +9.49 |
| R10-20 luna c | -24.78 to -23.66 | -14.29 to -13.39 | -52.20 to -48.81 | -20.00 to -17.46 |
| R10-20 deepseek a | -1.79 to -1.34 | +5.15 to +5.82 | -1.19 to -0.34 | +7.63 to +8.47 |
| R10-20 deepseek b | -2.68 to -2.24 | +4.47 to +5.15 | +0.68 to +1.53 | +10.85 to +11.69 |
| R10-20 deepseek c | -20.54 to -19.87 | -10.94 to -10.27 | -46.61 to -43.90 | -17.63 to -15.76 |
| R10-20 qwen a | -3.83 to -2.87 | +3.83 to +4.55 | -7.93 to -6.29 | +4.78 to +5.71 |
| R10-20 qwen b | -3.87 to -3.15 | +3.63 to +4.36 | -7.48 to -5.63 | +6.45 to +8.09 |
| R10-20 qwen c | -17.68 to -16.95 | -7.99 to -7.51 | -45.18 to -42.17 | -18.54 to -16.85 |
| R10-20 gemma a | -1.80 to -1.35 | +1.35 to +1.80 | -0.17 to +0.17 | +4.41 to +4.92 |
| R10-20 gemma b | -1.58 to -1.13 | +2.71 to +3.16 | -5.76 to -4.24 | +7.46 to +9.32 |
| R10-20 gemma c | -26.80 to -25.68 | -15.99 to -14.86 | -69.15 to -65.42 | -33.90 to -31.69 |
| R10-22 sol d | -4.24 to -4.02 | +0.00 to +0.45 | -7.29 to -5.93 | +3.22 to +4.24 |
| R10-22 sol e | -2.90 to -2.23 | +1.79 to +2.23 | -5.42 to -4.41 | +3.73 to +4.92 |
| R10-22 luna d | +0.45 to +0.89 | +6.92 to +7.37 | -3.22 to -2.20 | +11.02 to +12.88 |
| R10-22 luna e | -4.69 to -4.02 | +1.79 to +2.68 | -14.58 to -12.88 | -0.68 to -0.00 |
| R10-16 haiku a (all answers) | -1.34 to -1.12 | +1.56 to +1.79 | -2.11 to -1.69 | +2.20 to +2.71 |
| R10-16 haiku d (all answers) | -2.46 to -1.79 | +2.46 to +2.68 | -4.41 to -3.73 | +7.12 to +8.81 |
| R10-16 haiku a (first answer) | -1.34 to -1.12 | +1.56 to +1.79 | -11.86 to -10.17 | +5.08 to +6.78 |
| R10-16 haiku d (first answer) | -2.46 to -1.79 | +2.46 to +2.68 | -18.64 to -15.25 | +3.39 to +5.08 |
