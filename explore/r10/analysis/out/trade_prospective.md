## The search trade measure on three open models (amendment R10-17)

Exploratory. A test fixed in advance on new models, not on new dialogues: the 807 no-type-brief and 233 hotel-brief dialogues are the development dialogues of the paper's search-trade analysis, and the measure was chosen after the answers of six other models on them. DeepSeek, Qwen and gemma (round-9 DeepInfra settings) answered the original form (F0) and the verifier, 2 reads per dialogue. Ratio: visible losses added per visible failure avoided; 95% cluster bootstrap interval (2,000 draws, seed 20261112). Limit 0.30.

Self-check (the copied code gives the stored search_sym.json values): {"sonnet verify": "equal", "sonnet verify_no_only (post hoc)": "equal", "haiku verify": "equal", "haiku verify_no_only (post hoc)": "equal"}.

### Table 3 for the new models

| Model | Gate | Visible failure (%) | Visible loss (%) | Net avoided / added (dialogues, mean of reads) | Ratio, subset weights [95%] | Ratio, group weights [95%] | Verdict |
|---|---|---|---|---|---|---|---|
| deepseek | planned gate | 22.0 -> 18.3 | 21.9 -> 24.0 | 30.0 / 5.0 | 0.17 [0.05, 0.34] | 0.32 [0.09, 0.65] | point under, subset weights only |
| deepseek | clear-no gate | 22.0 -> 19.0 | 21.9 -> 23.2 | 24.0 / 3.0 | 0.12 [0.02, 0.28] | 0.24 [0.04, 0.54] | point under, both weightings (interval crosses 0.30) |
| qwen | planned gate | 28.0 -> 25.9 | 28.0 -> 36.8 | 16.5 / 20.0 | 1.23 [0.68, 2.45] | 2.35 [1.29, 4.64] | over at the point value |
| qwen | clear-no gate | 28.0 -> 26.3 | 28.0 -> 35.9 | 13.0 / 18.0 | 1.41 [0.72, 3.12] | 2.68 [1.37, 5.93] | over at the point value |
| gemma | planned gate | 25.6 -> 18.9 | 17.4 -> 19.5 | 54.5 / 5.0 | 0.09 [0.02, 0.19] | 0.17 [0.04, 0.37] | point under, both weightings (interval crosses 0.30) |
| gemma | clear-no gate | 25.6 -> 20.0 | 17.4 -> 17.6 | 45.0 / 0.5 | 0.01 [0.00, 0.04] | 0.02 [0.00, 0.07] | under (whole interval, both weightings) |

### Descriptions

| Model | Form | Hotel-only, 807 no-type | Hotel-only, 233 hotel | Search failure, 807 |
|---|---|---|---|---|
| deepseek | F0 | 12.5% (201/1614) | 59.0% (275/466) | 5.1% (83/1614) |
| deepseek | planned gate | 3.0% (48/1614) | 37.1% (173/466) | 0.9% (15/1614) |
| deepseek | clear-no gate | 5.6% (90/1614) | 44.2% (206/466) | 1.7% (28/1614) |
| qwen | F0 | 8.6% (132/1539) | 58.4% (247/423) | 3.2% (50/1539) |
| qwen | planned gate | 0.5% (8/1539) | 19.6% (83/423) | 0.2% (3/1539) |
| qwen | clear-no gate | 1.6% (25/1539) | 22.2% (94/423) | 0.5% (7/1539) |
| gemma | F0 | 18.7% (300/1604) | 81.2% (376/463) | 8.2% (132/1604) |
| gemma | planned gate | 1.0% (16/1604) | 40.2% (186/463) | 0.5% (8/1604) |
| gemma | clear-no gate | 7.4% (118/1604) | 66.3% (307/463) | 2.2% (35/1604) |

Verifier answers for the hotel-only F0 values: deepseek: no_type {"yes": 48, "no": 111, "unclear": 42}, hotel {"unclear": 33, "no": 69, "yes": 173}; qwen: no_type {"no": 107, "unclear": 17, "yes": 8}, hotel {"no": 153, "yes": 83, "unclear": 11}; gemma: no_type {"yes": 16, "no": 182, "unclear": 102}, hotel {"no": 69, "unclear": 121, "yes": 186}

Value count on the two sets (not the paper's trade rule, which also needs the guesthouse group; weights 994 and 545):

| Model | Gate | Removed (share of F0 hotel-only, no-type) | Lost | Ratio [95%] |
|---|---|---|---|---|
| deepseek | planned gate | 94.2 (76.1%) | 119.3 | 1.27 [0.95, 1.66] |
| deepseek | clear-no gate | 68.4 (55.2%) | 80.7 | 1.18 [0.84, 1.62] |
| qwen | planned gate | 80.1 (93.5%) | 211.3 | 2.64 [2.05, 3.41] |
| qwen | clear-no gate | 69.1 (80.7%) | 197.1 | 2.85 [2.19, 3.75] |
| gemma | planned gate | 176.0 (93.3%) | 223.7 | 1.27 [1.02, 1.55] |
| gemma | clear-no gate | 112.8 (59.8%) | 81.2 | 0.72 [0.50, 1.00] |

### Predictions (R10-17)

| # | Words | Value | Result |
|---|---|---|---|
| V1 | for each model, the planned gate's search trade ratio (subset weights) is under 0.30 at the point value | {"deepseek": 0.16666666666666666, "qwen": 1.2349094005743697, "gemma": 0.09162943510339575} | failed |
| V2 | for at least one model, the whole 95% interval of the planned gate's ratio is under 0.30 with both weightings | {"deepseek": {"subset_ci": [0.04838709677419355, 0.3404255319148936], "groups_ci": [0.09188768217779612, 0.646472203690594]}, "qwen": {"subset_ci": [0.6792001703159032, 2.445120613137252], "groups_ci": [1.2898093406252493, 4.643313626250898]}, "gemma": {"subset_ci": [0.01939341441994201, 0.1939341441994201], "groups_ci": [0.036828328611613004, 0.3682832861161301]}} | failed |
| V3 | for each model, the planned gate's value-count ratio on the two sets is above 0.30 at the point value, or not defined | {"deepseek": 1.2660080655607466, "qwen": 2.638338610938106, "gemma": 1.270775261491989} | held |
| V4 | for each model, the clear-no gate's search trade ratio (subset weights) is under 0.30 at the point value | {"deepseek": 0.125, "qwen": 1.4106465075791836, "gemma": 0.011097342695855706} | failed |
