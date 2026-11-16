## Audit of the "tell" answers of the returned-flag test (post hoc, no model call)

Reading rule: see the module text of r10/analysis/flag_audit.py (fixed before the reading). Labels: out/flag_audit_labels.tsv (one row per answer that the word rule calls tell or other).

### Codes by model, arm and word-rule kind

| Model | Arm | Word rule | Answers | Verdict tell | Verdict no tell | G | L | Q | E |
|---|---|---|---|---|---|---|---|---|---|
| sonnet | flag | tell | 9 | 9 | 0 | 9 | 8 | 9 | 0 |
| haiku | plain | tell | 38 | 31 | 7 | 31 | 8 | 24 | 0 |
| haiku | plain | other | 9 | 0 | 9 | 0 | 0 | 0 | 0 |
| haiku | flag | tell | 45 | 45 | 0 | 45 | 42 | 32 | 25 |
| opus | plain | tell | 3 | 3 | 0 | 3 | 1 | 2 | 0 |
| opus | flag | tell | 23 | 23 | 0 | 23 | 8 | 22 | 2 |

### Audited rates and flag minus plain (all answers)

| Model | Outcome | Plain | Flag | Flag minus plain, points [95% interval] | Dialogues higher / lower | Sign p |
|---|---|---|---|---|---|---|
| sonnet | recovery | 87.5% [75.8%, 96.9%] | 92.2% [82.8%, 100.0%] | +4.7 [+0.0, +10.9] | 3 / 0 | 0.25 |
| sonnet | widen | 87.5% [75.8%, 96.9%] | 85.2% [72.7%, 95.3%] | -2.3 [-10.9, +4.7] | 2 / 3 | 1 |
| sonnet | tell | 0.0% [0.0%, 0.0%] | 7.0% [0.0%, 16.4%] | +7.0 [+0.0, +16.4] | 3 / 0 | 0.25 |
| haiku | recovery | 74.7% [59.8%, 87.8%] | 100.0% [100.0%, 100.0%] | +22.9 [+10.4, +37.5] | 10 / 0 | 0.002 |
| haiku | widen | 39.1% [22.2%, 58.0%] | 48.3% [28.6%, 69.2%] | +10.4 [-6.2, +29.2] | 6 / 3 | 0.51 |
| haiku | tell | 35.6% [19.4%, 52.4%] | 51.7% [30.8%, 71.4%] | +12.5 [-9.4, +34.4] | 8 / 4 | 0.39 |
| opus | recovery | 92.3% [82.7%, 100.0%] | 96.2% [88.5%, 100.0%] | +3.8 [+0.0, +9.6] | 2 / 0 | 0.5 |
| opus | widen | 86.5% [73.1%, 96.2%] | 51.9% [36.5%, 69.2%] | -34.6 [-51.9, -17.3] | 1 / 13 | 0.0018 |
| opus | tell | 5.8% [0.0%, 11.5%] | 44.2% [26.9%, 61.5%] | +38.5 [+21.2, +53.8] | 15 / 1 | 0.00052 |

### Audited rates and flag minus plain (first answers)

| Model | Outcome | Plain | Flag | Flag minus plain, points [95% interval] | Dialogues higher / lower | Sign p |
|---|---|---|---|---|---|---|
| sonnet | recovery | 87.5% [75.0%, 96.9%] | 92.2% [82.8%, 100.0%] | +4.7 [+0.0, +12.5] | 2 / 0 | 0.5 |
| sonnet | widen | 87.5% [75.0%, 96.9%] | 85.9% [73.4%, 96.9%] | -1.6 [-9.4, +4.7] | 1 / 1 | 1 |
| sonnet | tell | 0.0% [0.0%, 0.0%] | 6.2% [0.0%, 15.6%] | +6.2 [+0.0, +15.6] | 2 / 0 | 0.5 |
| haiku | recovery | 65.5% [46.4%, 85.2%] | 100.0% [100.0%, 100.0%] | +31.2 [+12.5, +50.0] | 7 / 0 | 0.016 |
| haiku | widen | 41.4% [20.0%, 65.5%] | 51.7% [29.0%, 75.0%] | +12.5 [-9.4, +34.4] | 3 / 2 | 1 |
| haiku | tell | 24.1% [8.3%, 41.4%] | 48.3% [25.0%, 71.0%] | +18.8 [-6.2, +43.8] | 7 / 2 | 0.18 |
| opus | recovery | 88.5% [76.9%, 100.0%] | 96.2% [88.5%, 100.0%] | +7.7 [+0.0, +19.2] | 2 / 0 | 0.5 |
| opus | widen | 84.6% [69.2%, 96.2%] | 57.7% [38.5%, 76.9%] | -26.9 [-46.2, -7.7] | 1 / 8 | 0.039 |
| opus | tell | 3.8% [0.0%, 11.5%] | 38.5% [19.2%, 57.7%] | +34.6 [+11.5, +53.8] | 10 / 1 | 0.012 |

### Answer kinds (audited) in the dialogues where the traveller's words ask for a hotel (X: MUL0666, PMUL2861, PMUL3761)

| Model | Arm | Kinds |
|---|---|---|
| sonnet | plain | kept 7, widen 5 |
| sonnet | flag | kept 4, tell 8 |
| haiku | plain | kept 5, other 6, tell 7 |
| haiku | flag | tell 18 |
| opus | plain | kept 4, tell 2 |
| opus | flag | kept 2, tell 4 |
