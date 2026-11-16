# T2: floor of the sign condition

p_min(d) = 2^(1−d): the smallest two-sided exact sign-test p with d nonzero differences (ties dropped). Checked by enumeration for d = 1 to 30.

| d | p_min (fraction) | p_min |
|---:|---|---:|
| 1 | 1 | 1 |
| 2 | 1/2 | 0.5 |
| 3 | 1/4 | 0.25 |
| 4 | 1/8 | 0.125 |
| 5 | 1/16 | 0.0625 |
| 6 | 1/32 | 0.03125 |
| 7 | 1/64 | 0.015625 |
| 8 | 1/128 | 0.0078125 |
| 9 | 1/256 | 0.00390625 |
| 10 | 1/512 | 0.001953125 |
| 11 | 1/1024 | 0.0009765625 |
| 12 | 1/2048 | 0.0004882812 |

| C | Level | 0.05/C | d_min (enumeration = closed form) | p at d_min | p at d_min − 1 | Change floor, 59 × 1 (points) | 448 × 1 | 59 × 10 | Used in the paper |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 97.50% | 0.025 | 7 | 0.015625 | 0.03125 | 11.86 | 1.56 | 1.19 | 97.5% (fresh test, Luna-only updates) |
| 4 | 98.75% | 0.0125 | 8 | 0.0078125 | 0.015625 | 13.56 | 1.79 | 1.36 | 98.75% (tool calls, two-model test, fresh test) |
| 6 | 99.17% | 0.00833333 | 8 | 0.0078125 | 0.015625 | 13.56 | 1.79 | 1.36 | 99.17% (forms in the five-model test; final rule for Haiku's field-order edit) |
| 10 | 99.50% | 0.005 | 9 | 0.00390625 | 0.0078125 | 15.25 | 2.01 | 1.53 | 99.5% (final rule, five-model test and stored comparisons) |
| 12 | 99.58% | 0.00416667 | 9 | 0.00390625 | 0.0078125 | 15.25 | 2.01 | 1.53 | 99.58% (final rule, Haiku's repeat) |

## Truly changed against observed nonzero specific differences (sim.json, means per trial)

| Configuration | Truly changed specific requests | Specific requests with an observed nonzero difference |
|---|---:|---:|
| `A-both|haiku|no change|n59m10` | 0 | 6.20 |
| `A-both|deepseek|no change|n59m10` | 0 | 20.20 |
| `A-both|sol|no change|n59m10` | 0 | 12.12 |
| `S-sparse|haiku|sparse +8 specific|n59m10` | 6 | 12.04 |
| `S-sparse|deepseek|sparse +8 specific|n59m10` | 6 | 25.06 |
| `S-sparse|sol|sparse -8 specific|n59m10` | 6 | 17.66 |
