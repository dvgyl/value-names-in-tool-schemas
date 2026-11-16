# T3: every actual release decision with 100,000 draws (post hoc numerical sensitivity)

Seeds 20271101, 20271102, 20271103, 20271104, 20271105; 100,000 draws each. Primary: 2,000 draws, seed 20261112 (the paper). Same answers, pairing, averaging, validity rule, L, C, index convention and decision order. Rule-decisions: 187 in 67 comparisons. Run time 228 s with 8 workers.

- Rule-decisions whose 100,000-draw decision differs from the 2,000-draw decision for at least one seed, or whose five seeds disagree: **1**.
- Rule-decisions with the same decision under the 2,000-draw primary and all five seeds: **186**.

- Smallest distance to a responsible boundary among the stable ones: 0.000 points (Sonnet: era1 read 2 v fill read 3, original rule, 0 on the specific set).

## Decisions that change or whose seeds disagree

| Comparison | Rule (level) | 2,000 draws | 20,000 (stored) | 100,000: five seeds | Deciding set: 2,000-draw interval; 100,000-draw end range | Boundary |
|---|---|---|---|---|---|---|
| Luna, repeat | final (99.50%) | hold | pass | pass, pass, pass, pass, pass | open: [−5.13, +0.45]; low −4.91 to −4.91, high +0.00 to +0.22 | -L (open) |

## Every rule-decision

| Group | Comparison | Rule (level) | Change open / specific | 2,000 | 20,000 (stored) | 100,000 (5 seeds) | Boundary (set): smallest distance |
|---|---|---|---|---|---|---|---|
| five-model test | Sol, repeat | original (98.75%) | −0.67 / +0.00 | pass | pass | pass, pass, pass, pass, pass | -L (open): 2.54 |
| five-model test | Sol, repeat | revised (98.75%) | −0.67 / +0.00 | pass | pass | pass, pass, pass, pass, pass | -L (open): 2.54 |
| five-model test | Sol, repeat | final (99.50%) | −0.67 / +0.00 | pass | pass | pass, pass, pass, pass, pass | -L (open): 2.32 |
| five-model test | Sol, paraphrase 1 | original (98.75%) | −0.45 / −0.17 | pass | pass | pass, pass, pass, pass, pass | -L (specific): 2.29 |
| five-model test | Sol, paraphrase 1 | revised (98.75%) | −0.45 / −0.17 | pass | pass | pass, pass, pass, pass, pass | -L (specific): 2.29 |
| five-model test | Sol, paraphrase 1 | final (99.50%) | −0.45 / −0.17 | pass | pass | pass, pass, pass, pass, pass | -L (specific): 1.95 |
| five-model test | Sol, full rename | original (98.75%) | −22.54 / −62.03 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 48.31 |
| five-model test | Sol, full rename | revised (98.75%) | −22.54 / −62.03 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 48.31 |
| five-model test | Sol, full rename | final (99.50%) | −22.54 / −62.03 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 46.27 |
| five-model test | Luna, repeat | original (98.75%) | −2.23 / +0.51 | pass | pass | pass, pass, pass, pass, pass | -L (open): 0.31 |
| five-model test | Luna, repeat | revised (98.75%) | −2.23 / +0.51 | pass | pass | pass, pass, pass, pass, pass | -L (open): 0.31 |
| five-model test | Luna, repeat | final (99.50%) | −2.23 / +0.51 | hold | pass | pass, pass, pass, pass, pass | -L (open) (changes) |
| five-model test | Luna, paraphrase 1 | original (98.75%) | −3.12 / +2.03 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 2.97 |
| five-model test | Luna, paraphrase 1 | revised (98.75%) | −3.12 / +2.03 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 2.97 |
| five-model test | Luna, paraphrase 1 | final (99.50%) | −3.12 / +2.03 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 3.81 |
| five-model test | Luna, full rename | original (98.75%) | −18.75 / −33.73 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 20.00 |
| five-model test | Luna, full rename | revised (98.75%) | −18.75 / −33.73 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 20.00 |
| five-model test | Luna, full rename | final (99.50%) | −18.75 / −33.73 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 18.31 |
| five-model test | DeepSeek, repeat | original (99.17%) | +2.01 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 2.63 |
| five-model test | DeepSeek, repeat | revised (99.17%) | +2.01 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 2.63 |
| five-model test | DeepSeek, repeat | final (99.50%) | +2.01 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 3.14 |
| five-model test | DeepSeek, paraphrase 1 | original (99.17%) | +1.12 / +5.93 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 1.53 |
| five-model test | DeepSeek, paraphrase 1 | revised (99.17%) | +1.12 / +5.93 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 1.53 |
| five-model test | DeepSeek, paraphrase 1 | final (99.50%) | +1.12 / +5.93 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 1.36 |
| five-model test | DeepSeek, full rename | original (99.17%) | −15.18 / −30.00 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 17.12 |
| five-model test | DeepSeek, full rename | revised (99.17%) | −15.18 / −30.00 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 17.12 |
| five-model test | DeepSeek, full rename | final (99.50%) | −15.18 / −30.00 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 16.10 |
| five-model test | Qwen, repeat | original (99.17%) | +0.48 / −0.68 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.42 |
| five-model test | Qwen, repeat | revised (99.17%) | +0.48 / −0.68 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.42 |
| five-model test | Qwen, repeat | final (99.50%) | +0.48 / −0.68 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.77 |
| five-model test | Qwen, paraphrase 1 | original (99.17%) | +0.24 / +0.58 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.73 |
| five-model test | Qwen, paraphrase 1 | revised (99.17%) | +0.24 / +0.58 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.73 |
| five-model test | Qwen, paraphrase 1 | final (99.50%) | +0.24 / +0.58 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.92 |
| five-model test | Qwen, full rename | original (99.17%) | −12.35 / −30.10 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 18.25 |
| five-model test | Qwen, full rename | revised (99.17%) | −12.35 / −30.10 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 18.25 |
| five-model test | Qwen, full rename | final (99.50%) | −12.35 / −30.10 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 17.64 |
| five-model test | Gemma, repeat | original (99.17%) | +0.00 / +2.03 | pass | pass | pass, pass, pass, pass, pass | +L (specific): 0.25 |
| five-model test | Gemma, repeat | revised (99.17%) | +0.00 / +2.03 | pass | pass | pass, pass, pass, pass, pass | +L (specific): 0.25 |
| five-model test | Gemma, repeat | final (99.50%) | +0.00 / +2.03 | pass | pass | pass, pass, pass, pass, pass | +L (specific): 0.08 |
| five-model test | Gemma, paraphrase 1 | original (99.17%) | +0.68 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 2.63 |
| five-model test | Gemma, paraphrase 1 | revised (99.17%) | +0.68 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 2.63 |
| five-model test | Gemma, paraphrase 1 | final (99.50%) | +0.68 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 3.14 |
| five-model test | Gemma, full rename | original (99.17%) | −20.50 / −49.66 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 33.39 |
| five-model test | Gemma, full rename | revised (99.17%) | −20.50 / −49.66 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 33.39 |
| five-model test | Gemma, full rename | final (99.50%) | −20.50 / −49.66 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 32.20 |
| two-model test | Sol, field-order edit | original (98.75%) | −1.79 / −1.19 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 0.76 |
| two-model test | Sol, field-order edit | revised (98.75%) | −1.79 / −1.19 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 0.76 |
| two-model test | Sol, field-order edit | final (98.75%) | −1.79 / −1.19 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 0.76 |
| two-model test | Sol, paraphrase 2 | original (98.75%) | −0.22 / −0.51 | pass | pass | pass, pass, pass, pass, pass | -L (specific): 0.42 |
| two-model test | Sol, paraphrase 2 | revised (98.75%) | −0.22 / −0.51 | pass | pass | pass, pass, pass, pass, pass | -L (specific): 0.42 |
| two-model test | Sol, paraphrase 2 | final (98.75%) | −0.22 / −0.51 | pass | pass | pass, pass, pass, pass, pass | -L (specific): 0.42 |
| two-model test | Luna, field-order edit | original (98.75%) | +3.79 / +3.90 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.85 |
| two-model test | Luna, field-order edit | revised (98.75%) | +3.79 / +3.90 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.85 |
| two-model test | Luna, field-order edit | final (98.75%) | +3.79 / +3.90 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.85 |
| two-model test | Luna, paraphrase 2 | original (98.75%) | −1.12 / −5.93 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 0.85 |
| two-model test | Luna, paraphrase 2 | revised (98.75%) | −1.12 / −5.93 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 7.20 |
| two-model test | Luna, paraphrase 2 | final (98.75%) | −1.12 / −5.93 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 7.20 |
| Haiku controls | Haiku, repeat | original (98.75%) | +0.22 / +0.09 | pass | pass | pass, pass, pass, pass, pass | +L (specific): 2.80 |
| Haiku controls | Haiku, repeat | revised (98.75%) | +0.22 / +0.09 | pass | pass | pass, pass, pass, pass, pass | +L (specific): 2.80 |
| Haiku controls | Haiku, repeat | final (99.58%) | +0.22 / +0.09 | pass | pass | pass, pass, pass, pass, pass | +L (specific): 2.46 |
| Haiku controls | Haiku, field-order edit | original (98.75%) | +0.22 / +1.19 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.61 |
| Haiku controls | Haiku, field-order edit | revised (98.75%) | +0.22 / +1.19 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.61 |
| Haiku controls | Haiku, field-order edit | final (99.17%) | +0.22 / +1.19 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 2.12 |
| Haiku controls | Haiku, repeat, first answer only | original (98.75%) | +0.22 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 5.17 |
| Haiku controls | Haiku, field-order edit, first answer only | original (98.75%) | +0.22 / −5.08 | hold | hold | hold, hold, hold, hold, hold | 0 (specific): 3.39 |
| stored comparisons | Sonnet: era1 read 1 v era1 read 2 | original (98.75%) | −0.22 / +8.47 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 1.69 |
| stored comparisons | Sonnet: era1 read 1 v era1 read 2 | revised (98.75%) | −0.22 / +8.47 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 13.64 |
| stored comparisons | Sonnet: era1 read 1 v era1 read 2 | final (99.50%) | −0.22 / +8.47 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 15.34 |
| stored comparisons | Sonnet: era1 read 1 v fill read 3 | original (98.75%) | −0.22 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 6.86 |
| stored comparisons | Sonnet: era1 read 1 v fill read 3 | revised (98.75%) | −0.22 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 6.86 |
| stored comparisons | Sonnet: era1 read 1 v fill read 3 | final (99.50%) | −0.22 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 8.56 |
| stored comparisons | Sonnet: era1 read 1 v erp | original (98.75%) | −1.34 / +8.47 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 1.69 |
| stored comparisons | Sonnet: era1 read 1 v erp | revised (98.75%) | −1.34 / +8.47 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 13.64 |
| stored comparisons | Sonnet: era1 read 1 v erp | final (99.50%) | −1.34 / +8.47 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 15.34 |
| stored comparisons | Sonnet: era1 read 2 v fill read 3 | original (98.75%) | +0.00 / −5.08 | hold | hold | hold, hold, hold, hold, hold | 0 (specific): 0.00 |
| stored comparisons | Sonnet: era1 read 2 v fill read 3 | revised (98.75%) | +0.00 / −5.08 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 8.56 |
| stored comparisons | Sonnet: era1 read 2 v fill read 3 | final (99.50%) | +0.00 / −5.08 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 8.56 |
| stored comparisons | Sonnet: era1 read 2 v erp | original (98.75%) | −1.12 / +0.00 | pass | pass | pass, pass, pass, pass, pass | -L (open): 1.65 |
| stored comparisons | Sonnet: era1 read 2 v erp | revised (98.75%) | −1.12 / +0.00 | pass | pass | pass, pass, pass, pass, pass | -L (open): 1.65 |
| stored comparisons | Sonnet: era1 read 2 v erp | final (99.50%) | −1.12 / +0.00 | hold | hold | hold, hold, hold, hold, hold | zero width (specific): inf |
| stored comparisons | Sonnet: fill read 3 v erp | original (98.75%) | −1.12 / +5.08 | hold | hold | hold, hold, hold, hold, hold | 0 (specific): -0.00 |
| stored comparisons | Sonnet: fill read 3 v erp | revised (98.75%) | −1.12 / +5.08 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 6.86 |
| stored comparisons | Sonnet: fill read 3 v erp | final (99.50%) | −1.12 / +5.08 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 8.56 |
| stored comparisons | Haiku: era1 read 1 v era1 read 2 | original (98.75%) | +0.90 / −1.72 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.90 |
| stored comparisons | Haiku: era1 read 1 v era1 read 2 | revised (98.75%) | +0.90 / −1.72 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.90 |
| stored comparisons | Haiku: era1 read 1 v era1 read 2 | final (99.50%) | +0.90 / −1.72 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 3.62 |
| stored comparisons | Haiku: era1 read 1 v erm | original (98.75%) | −0.45 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.34 |
| stored comparisons | Haiku: era1 read 1 v erm | revised (98.75%) | −0.45 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.34 |
| stored comparisons | Haiku: era1 read 1 v erm | final (99.50%) | −0.45 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.34 |
| stored comparisons | Haiku: era1 read 1 v ers | original (98.75%) | −0.22 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 7.07 |
| stored comparisons | Haiku: era1 read 1 v ers | revised (98.75%) | −0.22 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 7.07 |
| stored comparisons | Haiku: era1 read 1 v ers | final (99.50%) | −0.22 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 8.79 |
| stored comparisons | Haiku: era1 read 1 v erc | original (98.75%) | +0.00 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.90 |
| stored comparisons | Haiku: era1 read 1 v erc | revised (98.75%) | +0.00 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.90 |
| stored comparisons | Haiku: era1 read 1 v erc | final (99.50%) | +0.00 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 3.62 |
| stored comparisons | Haiku: era1 read 1 v erc2 | original (98.75%) | +0.22 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.34 |
| stored comparisons | Haiku: era1 read 1 v erc2 | revised (98.75%) | +0.22 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.34 |
| stored comparisons | Haiku: era1 read 1 v erc2 | final (99.50%) | +0.22 / +1.72 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.34 |
| stored comparisons | Haiku: era1 read 2 v erm | original (98.75%) | −1.12 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 7.07 |
| stored comparisons | Haiku: era1 read 2 v erm | revised (98.75%) | −1.12 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 7.07 |
| stored comparisons | Haiku: era1 read 2 v erm | final (99.50%) | −1.12 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 8.79 |
| stored comparisons | Haiku: era1 read 2 v ers | original (98.75%) | −0.89 / +5.17 | hold | hold | hold, hold, hold, hold, hold | 0 (specific): 3.45 |
| stored comparisons | Haiku: era1 read 2 v ers | revised (98.75%) | −0.89 / +5.17 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 10.52 |
| stored comparisons | Haiku: era1 read 2 v ers | final (99.50%) | −0.89 / +5.17 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 12.24 |
| stored comparisons | Haiku: era1 read 2 v erc | original (98.75%) | −0.67 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.34 |
| stored comparisons | Haiku: era1 read 2 v erc | revised (98.75%) | −0.67 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.34 |
| stored comparisons | Haiku: era1 read 2 v erc | final (99.50%) | −0.67 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 7.07 |
| stored comparisons | Haiku: era1 read 2 v erc2 | original (98.75%) | −0.45 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 7.07 |
| stored comparisons | Haiku: era1 read 2 v erc2 | revised (98.75%) | −0.45 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 7.07 |
| stored comparisons | Haiku: era1 read 2 v erc2 | final (99.50%) | −0.45 / +3.45 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 8.79 |
| stored comparisons | Haiku: erm v ers | original (98.75%) | +0.22 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.78 |
| stored comparisons | Haiku: erm v ers | revised (98.75%) | +0.22 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 1.78 |
| stored comparisons | Haiku: erm v ers | final (99.50%) | +0.22 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 3.47 |
| stored comparisons | Haiku: erm v erc | original (98.75%) | +0.45 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.17 |
| stored comparisons | Haiku: erm v erc | revised (98.75%) | +0.45 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.17 |
| stored comparisons | Haiku: erm v erc | final (99.50%) | +0.45 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.17 |
| stored comparisons | Haiku: erm v erc2 | original (98.75%) | +0.67 / +0.00 | pass | pass | pass, pass, pass, pass, pass | +L (open): 2.77 |
| stored comparisons | Haiku: erm v erc2 | revised (98.75%) | +0.67 / +0.00 | pass | pass | pass, pass, pass, pass, pass | +L (open): 2.77 |
| stored comparisons | Haiku: erm v erc2 | final (99.50%) | +0.67 / +0.00 | hold | hold | hold, hold, hold, hold, hold | zero width (specific): inf |
| stored comparisons | Haiku: ers v erc | original (98.75%) | +0.22 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 3.47 |
| stored comparisons | Haiku: ers v erc | revised (98.75%) | +0.22 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 3.47 |
| stored comparisons | Haiku: ers v erc | final (99.50%) | +0.22 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 5.17 |
| stored comparisons | Haiku: ers v erc2 | original (98.75%) | +0.45 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.78 |
| stored comparisons | Haiku: ers v erc2 | revised (98.75%) | +0.45 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.78 |
| stored comparisons | Haiku: ers v erc2 | final (99.50%) | +0.45 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 3.47 |
| stored comparisons | Haiku: erc v erc2 | original (98.75%) | +0.22 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 5.17 |
| stored comparisons | Haiku: erc v erc2 | revised (98.75%) | +0.22 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 5.17 |
| stored comparisons | Haiku: erc v erc2 | final (99.50%) | +0.22 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 5.17 |
| stored comparisons | Sol: era1 read 1 v era1 read 2 | original (98.75%) | +1.56 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 6.86 |
| stored comparisons | Sol: era1 read 1 v era1 read 2 | revised (98.75%) | +1.56 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 6.86 |
| stored comparisons | Sol: era1 read 1 v era1 read 2 | final (99.50%) | +1.56 / −1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 6.86 |
| stored comparisons | Sol: era1 read 1 v fill read 3 | original (98.75%) | +0.89 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.78 |
| stored comparisons | Sol: era1 read 1 v fill read 3 | revised (98.75%) | +0.89 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.78 |
| stored comparisons | Sol: era1 read 1 v fill read 3 | final (99.50%) | +0.89 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 1.78 |
| stored comparisons | Sol: era1 read 1 v erp | original (98.75%) | −0.45 / +1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 6.86 |
| stored comparisons | Sol: era1 read 1 v erp | revised (98.75%) | −0.45 / +1.69 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 6.86 |
| stored comparisons | Sol: era1 read 1 v erp | final (99.50%) | −0.45 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 10.25 |
| stored comparisons | Sol: era1 read 2 v fill read 3 | original (98.75%) | −0.67 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.17 |
| stored comparisons | Sol: era1 read 2 v fill read 3 | revised (98.75%) | −0.67 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.17 |
| stored comparisons | Sol: era1 read 2 v fill read 3 | final (99.50%) | −0.67 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 5.17 |
| stored comparisons | Sol: era1 read 2 v erp | original (98.75%) | −2.01 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 8.56 |
| stored comparisons | Sol: era1 read 2 v erp | revised (98.75%) | −2.01 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 8.56 |
| stored comparisons | Sol: era1 read 2 v erp | final (99.50%) | −2.01 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 10.25 |
| stored comparisons | Sol: fill read 3 v erp | original (98.75%) | −1.34 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 6.86 |
| stored comparisons | Sol: fill read 3 v erp | revised (98.75%) | −1.34 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 6.86 |
| stored comparisons | Sol: fill read 3 v erp | final (99.50%) | −1.34 / +1.69 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 6.86 |
| stored comparisons | opus: era1 read 1 v fill read 2 | original (98.75%) | +1.34 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 6.86 |
| stored comparisons | opus: era1 read 1 v fill read 2 | revised (98.75%) | +1.34 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 6.86 |
| stored comparisons | opus: era1 read 1 v fill read 2 | final (99.50%) | +1.34 / +3.39 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 8.56 |
| stored comparisons | Luna: era1 read 1 v era1 read 2 | original (98.75%) | +0.89 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 5.17 |
| stored comparisons | Luna: era1 read 1 v era1 read 2 | revised (98.75%) | +0.89 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 5.17 |
| stored comparisons | Luna: era1 read 1 v era1 read 2 | final (99.50%) | +0.89 / +0.00 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 5.17 |
| steered rewrites | Sonnet, hotel rewrite | original (98.75%) | +8.26 / +11.86 | flag | - | flag, flag, flag, flag, flag | 0 (open): 5.13 |
| steered rewrites | Sonnet, hotel rewrite | revised (98.75%) | +8.26 / +11.86 | flag | - | flag, flag, flag, flag, flag | 0 (open): 5.13 |
| steered rewrites | Haiku, hotel rewrite | original (98.75%) | +34.15 / +69.49 | flag | - | flag, flag, flag, flag, flag | 0 (specific): 54.24 |
| steered rewrites | Haiku, hotel rewrite | revised (98.75%) | +34.15 / +69.49 | flag | - | flag, flag, flag, flag, flag | 0 (specific): 54.24 |
| steered rewrites | Sonnet, guesthouse rewrite | original (98.75%) | +11.61 / +25.42 | flag | - | flag, flag, flag, flag, flag | 0 (specific): 11.86 |
| steered rewrites | Sonnet, guesthouse rewrite | revised (98.75%) | +11.61 / +25.42 | flag | - | flag, flag, flag, flag, flag | 0 (specific): 11.86 |
| steered rewrites | Haiku, guesthouse rewrite | original (98.75%) | +29.46 / +49.15 | flag | - | flag, flag, flag, flag, flag | 0 (specific): 30.51 |
| steered rewrites | Haiku, guesthouse rewrite | revised (98.75%) | +29.46 / +49.15 | flag | - | flag, flag, flag, flag, flag | 0 (specific): 30.51 |
| broad rewrite | Sonnet, broad rewrite | original (98.75%) | +3.57 / +1.69 | hold | - | hold, hold, hold, hold, hold | +L (specific): 1.78 |
| broad rewrite | Sol, broad rewrite | original (98.75%) | +5.36 / +8.47 | flag | - | flag, flag, flag, flag, flag | 0 (open): 2.68 |
| fresh test | Luna, repeat | final (98.75%) | −0.67 / −0.85 | pass | pass | pass, pass, pass, pass, pass | -L (open): 1.43 |
| fresh test | Luna, repeat | revised (98.75%) | −0.67 / −0.85 | pass | - | pass, pass, pass, pass, pass | -L (open): 1.43 |
| fresh test | Luna, repeat | original (98.75%) | −0.67 / −0.85 | pass | - | pass, pass, pass, pass, pass | -L (open): 1.43 |
| fresh test | Sol, repeat | final (98.75%) | +1.12 / +1.36 | pass | pass | pass, pass, pass, pass, pass | +L (open): 1.21 |
| fresh test | Sol, repeat | revised (98.75%) | +1.12 / +1.36 | pass | - | pass, pass, pass, pass, pass | +L (open): 1.21 |
| fresh test | Sol, repeat | original (98.75%) | +1.12 / +1.36 | pass | - | pass, pass, pass, pass, pass | +L (open): 1.21 |
| fresh test | Luna, field-order edit | final (97.50%) | +3.57 / +4.07 | hold | hold | hold, hold, hold, hold, hold | +L (specific): 3.81 |
| fresh test | Luna, field-order edit | revised (97.50%) | +3.57 / +4.07 | hold | - | hold, hold, hold, hold, hold | +L (specific): 3.81 |
| fresh test | Luna, field-order edit | original (97.50%) | +3.57 / +4.07 | hold | - | hold, hold, hold, hold, hold | +L (specific): 3.81 |
| fresh test | Luna, paraphrase 1 | final (97.50%) | −1.12 / −1.02 | pass | pass | pass, pass, pass, pass, pass | -L (specific): 0.08 |
| fresh test | Luna, paraphrase 1 | revised (97.50%) | −1.12 / −1.02 | pass | - | pass, pass, pass, pass, pass | -L (specific): 0.08 |
| fresh test | Luna, paraphrase 1 | original (97.50%) | −1.12 / −1.02 | pass | - | pass, pass, pass, pass, pass | -L (specific): 0.08 |
| fresh test | Luna, paraphrase 2 | final (97.50%) | −4.69 / −3.90 | hold | hold | hold, hold, hold, hold, hold | -L (specific): 3.31 |
| fresh test | Luna, paraphrase 2 | revised (97.50%) | −4.69 / −3.90 | hold | - | hold, hold, hold, hold, hold | -L (specific): 3.31 |
| fresh test | Luna, paraphrase 2 | original (97.50%) | −4.69 / −3.90 | hold | - | hold, hold, hold, hold, hold | -L (specific): 3.31 |
| fresh test | Luna, full rename | final (98.75%) | −30.36 / −40.51 | flag | flag | flag, flag, flag, flag, flag | 0 (specific): 26.78 |
| fresh test | Luna, full rename | revised (98.75%) | −30.36 / −40.51 | flag | - | flag, flag, flag, flag, flag | 0 (specific): 26.78 |
| fresh test | Luna, full rename | original (98.75%) | −30.36 / −40.51 | flag | - | flag, flag, flag, flag, flag | 0 (specific): 26.78 |
| fresh test | Sol, full rename | final (98.75%) | −28.12 / −33.22 | flag | flag | flag, flag, flag, flag, flag | 0 (open): 22.54 |
| fresh test | Sol, full rename | revised (98.75%) | −28.12 / −33.22 | flag | - | flag, flag, flag, flag, flag | 0 (open): 22.54 |
| fresh test | Sol, full rename | original (98.75%) | −28.12 / −33.22 | flag | - | flag, flag, flag, flag, flag | 0 (open): 22.54 |
| replication | DeepSeek, paraphrase 1 (replication) | original (99.17%) | +0.89 / +1.07 | pass | - | pass, pass, pass, pass, pass | +L (open): 0.75 |
| replication | DeepSeek, paraphrase 1 (replication) | revised (99.17%) | +0.89 / +1.07 | pass | - | pass, pass, pass, pass, pass | +L (open): 0.75 |
| replication | Luna, paraphrase 2 (replication) | original (98.75%) | −1.34 / +0.51 | pass | - | pass, pass, pass, pass, pass | -L (open): 0.76 |
| replication | Luna, paraphrase 2 (replication) | revised (98.75%) | −1.34 / +0.51 | pass | - | pass, pass, pass, pass, pass | -L (open): 0.76 |
