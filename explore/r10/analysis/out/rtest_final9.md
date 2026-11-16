## Final-9: release decisions with a symmetric percentile index (post hoc)

As run: the low end is the k-th lowest and the high end the (k + 1)-th highest of 2,000 resampled means.
Symmetric: the k-th lowest and the k-th highest, k = floor(2,000 x (1 - level) / 2).
Final rule: revised rule, symmetric index, level of one release (one update on every model that received it), zero-width interval not within limits.

Checks against result.json, result2.json and verify_out.json: 57 of 57 part-A checks pass; part B one-answer pairs equal: 29 of 29.

### A. Prospective tests (Tables 4 and 19)

| Test | Model | Update | Level as run | Open (as run; symmetric high end) | Specific (as run; symmetric high end) | First as run | Revised as run | First sym. | Revised sym. | Final rule (level) |
|---|---|---|---|---|---|---|---|---|---|---|
| R10-20 | sol | repeat | 98.75% | -0.7 [-2.46, +0.89] 3/6 p=0.5078; +0.89 | +0.0 [-1.69, +1.86] 5/5 p=1; +1.86 | pass | pass | pass | pass | pass (99.50%) |
| R10-20 | sol | first paraphrase | 98.75% | -0.4 [-2.46, +1.34] 5/7 p=0.7744; +1.34 | -0.2 [-2.54, +2.37] 6/7 p=1; +2.37 | pass | pass | pass | pass | pass (99.50%) |
| R10-20 | sol | full rename | 98.75% | -22.5 [-27.90, -17.86] 0/101 p=0; -17.86 | -62.0 [-74.58, -48.64] 0/46 p=0; -48.47 | flag | flag | flag | flag | flag (99.50%) |
| R10-20 | luna | repeat | 98.75% | -2.2 [-4.69, +0.00] 3/13 p=0.02127; +0.00 | +0.5 [-2.37, +3.73] 5/7 p=0.7744; +3.73 | pass | pass | pass | pass | hold (99.50%) |
| R10-20 | luna | first paraphrase | 98.75% | -3.1 [-5.80, -0.67] 4/18 p=0.004344; -0.67 | +2.0 [-3.90, +7.97] 8/6 p=0.7905; +7.97 | hold | hold | hold | hold | hold (99.50%) |
| R10-20 | luna | full rename | 98.75% | -18.8 [-23.44, -14.29] 0/84 p=0; -14.29 | -33.7 [-49.83, -20.00] 0/27 p=0; -19.83 | flag | flag | flag | flag | flag (99.50%) |
| R10-20 | deepseek | repeat | 99.17% | +2.0 [-1.12, +5.37] 20/11 p=0.1496; +5.59 | +3.4 [-0.51, +7.63] 18/5 p=0.01062; +7.63 | hold | hold | hold | hold | hold (99.50%) |
| R10-20 | deepseek | first paraphrase | 99.17% | +1.1 [-2.46, +4.47] 20/15 p=0.4996; +4.47 | +5.9 [+1.53, +10.68] 21/5 p=0.002494; +10.68 | flag | flag | flag | flag | flag (99.50%) |
| R10-20 | deepseek | full rename | 99.17% | -15.2 [-20.09, -10.71] 0/68 p=0; -10.71 | -30.0 [-43.90, -17.12] 0/28 p=0; -17.12 | flag | flag | flag | flag | flag (99.50%) |
| R10-20 | qwen | repeat | 99.17% | +0.5 [-3.35, +3.83] 16/14 p=0.8555; +3.83 | -0.7 [-7.10, +4.72] 15/17 p=0.86; +4.76 | hold | hold | hold | hold | hold (99.50%) |
| R10-20 | qwen | first paraphrase | 99.17% | +0.2 [-3.15, +3.63] 15/14 p=1; +3.63 | +0.6 [-5.86, +6.81] 18/11 p=0.2649; +6.82 | hold | hold | hold | hold | hold (99.50%) |
| R10-20 | qwen | full rename | 99.17% | -12.3 [-17.19, -8.23] 3/54 p=0; -7.75 | -30.1 [-42.46, -18.25] 0/33 p=0; -18.22 | flag | flag | flag | flag | flag (99.50%) |
| R10-20 | gemma | repeat | 99.17% | +0.0 [-1.58, +1.35] 3/3 p=1; +1.35 | +2.0 [-0.00, +4.75] 7/1 p=0.07031; +4.75 | pass | pass | pass | pass | pass (99.50%) |
| R10-20 | gemma | first paraphrase | 99.17% | +0.7 [-1.35, +2.71] 7/4 p=0.5488; +2.71 | +1.7 [-4.75, +7.63] 5/3 p=0.7266; +7.63 | hold | hold | hold | hold | hold (99.50%) |
| R10-20 | gemma | full rename | 99.17% | -20.5 [-25.68, -15.77] 0/91 p=0; -15.54 | -49.7 [-66.44, -33.56] 0/32 p=0; -33.39 | flag | flag | flag | flag | flag (99.50%) |
| R10-22 | sol | field-order edit | 98.75% | -1.8 [-3.79, +0.00] 2/10 p=0.03857; +0.00 | -1.2 [-5.76, +3.39] 5/8 p=0.5811; +3.39 | hold | hold | hold | hold | hold (98.75%) |
| R10-22 | sol | second paraphrase | 98.75% | -0.2 [-2.46, +1.79] 6/7 p=1; +1.79 | -0.5 [-4.58, +3.73] 5/8 p=0.5811; +3.90 | pass | pass | pass | pass | pass (98.75%) |
| R10-22 | luna | field-order edit | 98.75% | +3.8 [+1.12, +6.70] 22/5 p=0.001514; +6.70 | +3.9 [-2.03, +11.02] 9/5 p=0.4239; +11.19 | hold | hold | hold | hold | hold (98.75%) |
| R10-22 | luna | second paraphrase | 98.75% | -1.1 [-4.02, +1.56] 10/15 p=0.4244; +1.56 | -5.9 [-12.20, -1.02] 4/12 p=0.07681; -1.02 | flag | hold | flag | hold | hold (98.75%) |

Final level of R10-20 (C = 10, 99.5%), sets:

- sol, repeat: open -0.7 [-2.46, +1.34] 3/6 p=0.5078; specific +0.0 [-1.86, +2.03] 5/5 p=1; first pass; revised pass; final pass
- sol, first paraphrase: open -0.4 [-2.68, +1.56] 5/7 p=0.7744; specific -0.2 [-2.71, +2.71] 6/7 p=1; first pass; revised pass; final pass
- sol, full rename: open -22.5 [-28.35, -17.19] 0/101 p=0; specific -62.0 [-75.59, -46.78] 0/46 p=0; first flag; revised flag; final flag
- luna, repeat: open -2.2 [-5.13, +0.45] 3/13 p=0.02127; specific +0.5 [-2.71, +4.07] 5/7 p=0.7744; first hold; revised hold; final hold
- luna, first paraphrase: open -3.1 [-6.03, -0.22] 4/18 p=0.004344; specific +2.0 [-4.58, +8.81] 8/6 p=0.7905; first hold; revised hold; final hold
- luna, full rename: open -18.8 [-23.88, -13.39] 0/84 p=0; specific -33.7 [-51.86, -18.31] 0/27 p=0; first flag; revised flag; final flag
- deepseek, repeat: open +2.0 [-1.57, +5.82] 20/11 p=0.1496; specific +3.4 [-1.02, +8.14] 18/5 p=0.01062; first hold; revised hold; final hold
- deepseek, first paraphrase: open +1.1 [-2.68, +4.70] 20/15 p=0.4996; specific +5.9 [+1.53, +11.02] 21/5 p=0.002494; first flag; revised flag; final flag
- deepseek, full rename: open -15.2 [-20.09, -9.82] 0/68 p=0; specific -30.0 [-44.58, -16.10] 0/28 p=0; first flag; revised flag; final flag
- qwen, repeat: open +0.5 [-3.35, +4.07] 16/14 p=0.8555; specific -0.7 [-7.93, +5.05] 15/17 p=0.86; first hold; revised hold; final hold
- qwen, first paraphrase: open +0.2 [-3.39, +4.12] 15/14 p=1; specific +0.6 [-5.93, +6.92] 18/11 p=0.2649; first hold; revised hold; final hold
- qwen, full rename: open -12.3 [-17.43, -7.02] 3/54 p=0; specific -30.1 [-42.89, -18.03] 0/33 p=0; first flag; revised flag; final flag
- gemma, repeat: open +0.0 [-1.58, +1.58] 3/3 p=1; specific +2.0 [-0.17, +4.92] 7/1 p=0.07031; first pass; revised pass; final pass
- gemma, first paraphrase: open +0.7 [-1.35, +2.93] 7/4 p=0.5488; specific +1.7 [-4.75, +8.14] 5/3 p=0.7266; first hold; revised hold; final hold
- gemma, full rename: open -20.5 [-25.90, -15.32] 0/91 p=0; specific -49.7 [-66.78, -32.20] 0/32 p=0; first flag; revised flag; final flag

Post hoc descriptions (as-run level, both indices):

- R10-20 sol, first paraphrase against the repeat: open +0.2 [-2.01, +2.46] 8/7 p=1, symmetric [-2.0089, 2.4554]; specific -0.2 [-1.86, +1.69] 6/7 p=1, symmetric [-1.8644, 1.6949]; first pass / pass; revised pass / pass
- R10-20 luna, first paraphrase against the repeat: open -0.9 [-3.57, +1.79] 9/13 p=0.5235, symmetric [-3.5714, 1.7857]; specific +1.5 [-4.41, +7.12] 8/5 p=0.5811, symmetric [-4.4068, 7.1186]; first hold / hold; revised hold / hold
- R10-20 deepseek, first paraphrase against the repeat: open -0.9 [-4.48, +2.69] 15/19 p=0.6076, symmetric [-4.4843, 2.6906]; specific +2.5 [-3.39, +8.98] 16/11 p=0.4421, symmetric [-3.3898, 8.9831]; first hold / hold; revised hold / hold
- R10-20 qwen, first paraphrase against the repeat: open -0.5 [-4.38, +3.41] 18/20 p=0.8714, symmetric [-4.3796, 3.4063]; specific +1.3 [-4.32, +6.32] 20/14 p=0.3915, symmetric [-4.3187, 6.4501]; first hold / hold; revised hold / hold
- R10-20 gemma, first paraphrase against the repeat: open +0.7 [-0.90, +2.24] 5/2 p=0.4531, symmetric [-0.8969, 2.2422]; specific -0.3 [-5.42, +4.92] 3/5 p=0.7266, symmetric [-5.4237, 4.9153]; first hold / hold; revised hold / hold
- R10-22 sol, fresh control against the R10-20 control, open: -0.9 [-2.46, +0.67] 2/6 p=0.2891; symmetric [-2.4554, 0.6696]
- R10-22 sol, fresh control against the R10-20 control, specific: -1.2 [-4.75, +2.54] 5/9 p=0.4239; symmetric [-4.7458, 2.5424]
- R10-22 luna, fresh control against the R10-20 control, open: -2.9 [-5.36, -0.67] 2/15 p=0.00235; symmetric [-5.3571, -0.6696]
- R10-22 luna, fresh control against the R10-20 control, specific: +0.7 [-1.02, +2.54] 6/3 p=0.5078; symmetric [-1.0169, 2.5424]

### B. Stored tool calls (Table 16; prospective rows of Table 15)

Tally (variant | level | rule | decision):

```
all_answers | 98.75 | final | hold: 27
all_answers | 98.75 | final | pass: 2
all_answers | 98.75 | first_as_run | flag: 2
all_answers | 98.75 | first_as_run | hold: 23
all_answers | 98.75 | first_as_run | pass: 4
all_answers | 98.75 | first_as_run reversed | flag: 2
all_answers | 98.75 | first_as_run reversed | hold: 23
all_answers | 98.75 | first_as_run reversed | pass: 4
all_answers | 98.75 | first_symmetric | flag: 2
all_answers | 98.75 | first_symmetric | hold: 24
all_answers | 98.75 | first_symmetric | pass: 3
all_answers | 98.75 | first_symmetric reversed | flag: 2
all_answers | 98.75 | first_symmetric reversed | hold: 24
all_answers | 98.75 | first_symmetric reversed | pass: 3
all_answers | 98.75 | revised_as_run | hold: 25
all_answers | 98.75 | revised_as_run | pass: 4
all_answers | 98.75 | revised_symmetric | hold: 26
all_answers | 98.75 | revised_symmetric | pass: 3
all_answers | 99.5 | final | hold: 28
all_answers | 99.5 | final | pass: 1
all_answers | 99.5 | first_as_run | hold: 27
all_answers | 99.5 | first_as_run | pass: 2
all_answers | 99.5 | first_as_run reversed | hold: 27
all_answers | 99.5 | first_as_run reversed | pass: 2
all_answers | 99.5 | first_symmetric | hold: 27
all_answers | 99.5 | first_symmetric | pass: 2
all_answers | 99.5 | first_symmetric reversed | hold: 27
all_answers | 99.5 | first_symmetric reversed | pass: 2
all_answers | 99.5 | revised_as_run | hold: 27
all_answers | 99.5 | revised_as_run | pass: 2
all_answers | 99.5 | revised_symmetric | hold: 27
all_answers | 99.5 | revised_symmetric | pass: 2
one_answer | 98.75 | final | hold: 29
one_answer | 98.75 | first_as_run | flag: 2
one_answer | 98.75 | first_as_run | hold: 25
one_answer | 98.75 | first_as_run | pass: 2
one_answer | 98.75 | first_as_run reversed | flag: 2
one_answer | 98.75 | first_as_run reversed | hold: 25
one_answer | 98.75 | first_as_run reversed | pass: 2
one_answer | 98.75 | first_symmetric | flag: 2
one_answer | 98.75 | first_symmetric | hold: 25
one_answer | 98.75 | first_symmetric | pass: 2
one_answer | 98.75 | first_symmetric reversed | flag: 2
one_answer | 98.75 | first_symmetric reversed | hold: 25
one_answer | 98.75 | first_symmetric reversed | pass: 2
one_answer | 98.75 | revised_as_run | hold: 27
one_answer | 98.75 | revised_as_run | pass: 2
one_answer | 98.75 | revised_symmetric | hold: 27
one_answer | 98.75 | revised_symmetric | pass: 2
one_answer | 99.5 | final | hold: 29
one_answer | 99.5 | first_as_run | hold: 27
one_answer | 99.5 | first_as_run | pass: 2
one_answer | 99.5 | first_as_run reversed | hold: 27
one_answer | 99.5 | first_as_run reversed | pass: 2
one_answer | 99.5 | first_symmetric | hold: 27
one_answer | 99.5 | first_symmetric | pass: 2
one_answer | 99.5 | first_symmetric reversed | hold: 27
one_answer | 99.5 | first_symmetric reversed | pass: 2
one_answer | 99.5 | revised_as_run | hold: 27
one_answer | 99.5 | revised_as_run | pass: 2
one_answer | 99.5 | revised_symmetric | hold: 27
one_answer | 99.5 | revised_symmetric | pass: 2
```

Unchanged pairs whose decision is not a hold under some rule:

| Variant | Pair | Level | Open | Specific (as run; symmetric) | First as run | Revised as run | First sym. | Revised sym. | Final | Reversed (first as run; first sym.) |
|---|---|---|---|---|---|---|---|---|---|---|
| one_answer | sonnet era1 read 1 v era1 read 2 | 98.75 | -0.2 [-1.56, +1.12] 2/3 p=1 | +8.5 [+1.69, +18.64] 5/0 p=0.0625; [1.6949, 18.6441] | flag | hold | flag | hold | hold | flag; flag |
| one_answer | sonnet era1 read 1 v erp | 98.75 | -1.3 [-3.57, +0.89] 4/10 p=0.1796 | +8.5 [+1.69, +18.64] 5/0 p=0.0625; [1.6949, 18.6441] | flag | hold | flag | hold | hold | flag; flag |
| one_answer | sonnet era1 read 2 v erp | 98.75 | -1.1 [-3.35, +1.12] 5/10 p=0.3018 | +0.0 [+0.00, +0.00] 0/0 p=1; [0.0, 0.0] | pass | pass | pass | pass | hold | pass; pass |
| one_answer | sonnet era1 read 2 v erp | 99.5 | -1.1 [-3.79, +1.12] 5/10 p=0.3018 | +0.0 [+0.00, +0.00] 0/0 p=1; [0.0, 0.0] | pass | pass | pass | pass | hold | pass; pass |
| one_answer | haiku erm v erc2 | 98.75 | +0.7 [-0.89, +2.23] 5/2 p=0.4531 | +0.0 [+0.00, +0.00] 0/0 p=1; [0.0, 0.0] | pass | pass | pass | pass | hold | pass; pass |
| one_answer | haiku erm v erc2 | 99.5 | +0.7 [-0.89, +2.46] 5/2 p=0.4531 | +0.0 [+0.00, +0.00] 0/0 p=1; [0.0, 0.0] | pass | pass | pass | pass | hold | pass; pass |
| all_answers | sonnet era1 read 1 v era1 read 2 | 98.75 | -0.2 [-1.56, +1.12] 2/3 p=1 | +8.5 [+1.69, +18.64] 5/0 p=0.0625; [1.6949, 18.6441] | flag | hold | flag | hold | hold | flag; flag |
| all_answers | sonnet era1 read 1 v erp | 98.75 | -1.3 [-3.57, +0.89] 4/10 p=0.1796 | +8.5 [+1.69, +18.64] 5/0 p=0.0625; [1.6949, 18.6441] | flag | hold | flag | hold | hold | flag; flag |
| all_answers | sonnet era1 read 2 v erp | 98.75 | -1.1 [-3.35, +1.12] 5/10 p=0.3018 | +0.0 [+0.00, +0.00] 0/0 p=1; [0.0, 0.0] | pass | pass | pass | pass | hold | pass; pass |
| all_answers | sonnet era1 read 2 v erp | 99.5 | -1.1 [-3.79, +1.12] 5/10 p=0.3018 | +0.0 [+0.00, +0.00] 0/0 p=1; [0.0, 0.0] | pass | pass | pass | pass | hold | pass; pass |
| all_answers | haiku era1 read 1 v erc2 | 98.75 | +0.2 [-1.57, +2.02] 5/4 p=1 | +0.7 [-3.28, +5.00] 3/3 p=1; [-3.2759, 5.1724] | pass | pass | hold | hold | hold | hold; hold |
| all_answers | haiku erm v erc | 98.75 | +0.4 [-0.89, +2.01] 4/2 p=0.6875 | -0.2 [-5.08, +4.58] 3/3 p=1; [-5.0847, 4.5763] | hold | hold | hold | hold | hold | pass; hold |
| all_answers | haiku erm v erc2 | 98.75 | +0.7 [-0.89, +2.23] 5/2 p=0.4531 | -0.1 [-4.65, +4.52] 3/4 p=1; [-4.6516, 4.5951] | pass | pass | pass | pass | pass | pass; pass |
| all_answers | haiku erc v erc2 | 98.75 | +0.2 [-0.89, +1.56] 3/2 p=1 | +0.1 [-1.75, +2.20] 4/4 p=1; [-1.7514, 2.2034] | pass | pass | pass | pass | pass | pass; pass |
| all_answers | haiku erc v erc2 | 99.5 | +0.2 [-1.12, +1.79] 3/2 p=1 | +0.1 [-2.00, +2.37] 4/4 p=1; [-1.9962, 2.3729] | pass | pass | pass | pass | pass | pass; pass |

| Edit | Status | Level | Open (as run; sym.) | Specific (as run; sym.) | First as run | Revised as run | First sym. | Revised sym. | Final | L=3 (as run; sym.) | L=10 (as run; sym.) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full rename, sonnet | post hoc | 98.75 | -19.2 [-23.66, -14.73] 0/86 p=0; [-23.6607, -14.5089] | -44.1 [-61.02, -28.81] 0/26 p=0; [-61.0169, -28.8136] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, sonnet | post hoc | 99.58 (C = 12) | -19.2 [-24.78, -14.06] 0/86 p=0; [-24.7768, -13.8393] | -44.1 [-62.71, -25.42] 0/26 p=0; [-62.7119, -25.4237] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, haiku | post hoc | 98.75 | -5.4 [-8.30, -2.91] 0/24 p=0; [-8.296, -2.9148] | -8.6 [-18.97, -1.72] 0/5 p=0.0625; [-18.9655, -1.7241] | flag | flag | flag | flag | flag | flag; flag | hold; hold |
| full rename, haiku | post hoc | 99.58 (C = 12) | -5.4 [-8.74, -2.69] 0/24 p=0; [-8.7444, -2.6906] | -8.6 [-20.69, +0.00] 0/5 p=0.0625; [-20.6897, 0.0] | flag | flag | flag | flag | flag | flag; flag | hold; hold |
| full rename, opus | post hoc | 98.75 | -20.8 [-25.67, -15.85] 2/95 p=0; [-25.6696, -15.625] | -49.2 [-66.10, -33.90] 0/29 p=0; [-66.1017, -33.8983] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, opus | post hoc | 99.58 (C = 12) | -20.8 [-26.79, -14.73] 2/95 p=0; [-26.7857, -14.7321] | -49.2 [-67.80, -32.20] 0/29 p=0; [-67.7966, -32.2034] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, sol | post hoc | 98.75 | -23.0 [-27.90, -18.08] 0/103 p=0; [-27.9018, -18.0804] | -57.6 [-72.88, -42.37] 0/34 p=0; [-72.8814, -42.3729] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, sol | post hoc | 99.58 (C = 12) | -23.0 [-29.02, -17.19] 0/103 p=0; [-29.0179, -17.1875] | -57.6 [-76.27, -38.98] 0/34 p=0; [-76.2712, -38.9831] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, astra | post hoc | 98.75 | -31.0 [-36.38, -25.67] 0/139 p=0; [-36.3839, -25.6696] | -79.7 [-91.53, -66.10] 0/47 p=0; [-91.5254, -66.1017] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, astra | post hoc | 99.58 (C = 12) | -31.0 [-37.50, -25.00] 0/139 p=0; [-37.5, -25.0] | -79.7 [-93.22, -64.41] 0/47 p=0; [-93.2203, -64.4068] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, luna | post hoc | 98.75 | -17.6 [-22.10, -13.39] 0/79 p=0; [-22.0982, -13.1696] | -33.9 [-50.85, -20.34] 0/20 p=2e-06; [-50.8475, -18.6441] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| full rename, luna | post hoc | 99.58 (C = 12) | -17.6 [-22.77, -12.95] 0/79 p=0; [-22.7679, -12.5] | -33.9 [-54.24, -18.64] 0/20 p=2e-06; [-54.2373, -16.9492] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| broad rewrite, sonnet | prospective | 98.75 | +3.6 [+0.89, +6.03] 19/3 p=0.000855; [0.8929, 6.0268] | +1.7 [+0.00, +6.78] 1/0 p=1; [0.0, 6.7797] | hold | hold | hold | hold | hold | flag; flag | pass; pass |
| broad rewrite, sonnet | prospective | 99.17 (C = 6) | +3.6 [+0.89, +6.25] 19/3 p=0.000855; [0.8929, 6.25] | +1.7 [+0.00, +6.78] 1/0 p=1; [0.0, 6.7797] | hold | hold | hold | hold | hold | flag; flag | pass; pass |
| broad rewrite, sol | prospective | 98.75 | +5.4 [+2.68, +8.26] 26/2 p=3e-06; [2.6786, 8.2589] | +8.5 [-3.39, +20.34] 7/2 p=0.1797; [-3.3898, 22.0339] | flag | flag | flag | flag | flag | flag; flag | hold; hold |
| broad rewrite, sol | prospective | 99.17 (C = 6) | +5.4 [+2.46, +8.48] 26/2 p=3e-06; [2.4554, 8.4821] | +8.5 [-3.39, +22.03] 7/2 p=0.1797; [-3.3898, 22.0339] | flag | flag | flag | flag | flag | flag; flag | hold; hold |
| steered th, sonnet | prospective | 98.75 | +8.3 [+5.13, +11.83] 37/0 p=0; [5.1339, 11.8304] | +11.9 [+1.69, +23.73] 7/0 p=0.01562; [1.6949, 23.7288] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| steered th, sonnet | prospective | 98.75 (C = 4) | +8.3 [+5.13, +11.83] 37/0 p=0; [5.1339, 11.8304] | +11.9 [+1.69, +23.73] 7/0 p=0.01562; [1.6949, 23.7288] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| steered th, haiku | prospective | 98.75 | +34.2 [+28.57, +39.96] 154/1 p=0; [28.5714, 39.9554] | +69.5 [+54.24, +84.75] 41/0 p=0; [54.2373, 84.7458] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| steered th, haiku | prospective | 98.75 (C = 4) | +34.2 [+28.57, +39.96] 154/1 p=0; [28.5714, 39.9554] | +69.5 [+54.24, +84.75] 41/0 p=0; [54.2373, 84.7458] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| steered tg, sonnet | prospective | 98.75 | +11.6 [+7.81, +15.62] 53/1 p=0; [7.8125, 15.8482] | +25.4 [+11.86, +40.68] 15/0 p=6.1e-05; [11.8644, 40.678] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| steered tg, sonnet | prospective | 98.75 (C = 4) | +11.6 [+7.81, +15.62] 53/1 p=0; [7.8125, 15.8482] | +25.4 [+11.86, +40.68] 15/0 p=6.1e-05; [11.8644, 40.678] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| steered tg, haiku | prospective | 98.75 | +29.5 [+24.11, +35.27] 133/1 p=0; [24.1071, 35.2679] | +49.2 [+30.51, +64.41] 29/0 p=0; [30.5085, 64.4068] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| steered tg, haiku | prospective | 98.75 (C = 4) | +29.5 [+24.11, +35.27] 133/1 p=0; [24.1071, 35.2679] | +49.2 [+30.51, +64.41] 29/0 p=0; [30.5085, 64.4068] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite h1, haiku | post hoc | 98.75 | +33.7 [+28.35, +39.51] 151/0 p=0; [28.3482, 39.5089] | +74.6 [+57.63, +88.14] 44/0 p=0; [57.6271, 88.1356] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite h1, haiku | post hoc | 98.75 (C = 4) | +33.7 [+28.35, +39.51] 151/0 p=0; [28.3482, 39.5089] | +74.6 [+57.63, +88.14] 44/0 p=0; [57.6271, 88.1356] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite h2, haiku | post hoc | 98.75 | +44.6 [+39.06, +50.67] 200/0 p=0; [39.0625, 50.6696] | +84.7 [+72.88, +94.92] 50/0 p=0; [72.8814, 96.6102] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite h2, haiku | post hoc | 97.50 (C = 2) | +44.6 [+39.29, +50.00] 200/0 p=0; [39.2857, 50.0] | +84.7 [+74.58, +94.92] 50/0 p=0; [74.5763, 94.9153] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite h3, haiku | post hoc | 98.75 | +44.6 [+38.62, +50.89] 200/0 p=0; [38.6161, 51.1161] | +83.1 [+69.49, +94.92] 49/0 p=0; [69.4915, 94.9153] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite h3, haiku | post hoc | 97.50 (C = 2) | +44.6 [+39.06, +50.00] 200/0 p=0; [39.0625, 50.2232] | +83.1 [+71.19, +93.22] 49/0 p=0; [71.1864, 93.2203] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite g1, haiku | post hoc | 98.75 | +29.5 [+24.11, +34.82] 132/0 p=0; [24.1071, 34.8214] | +44.1 [+28.81, +61.02] 26/0 p=0; [28.8136, 61.0169] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite g1, haiku | post hoc | 98.75 (C = 4) | +29.5 [+24.11, +34.82] 132/0 p=0; [24.1071, 34.8214] | +44.1 [+28.81, +61.02] 26/0 p=0; [28.8136, 61.0169] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite g2, haiku | post hoc | 98.75 | +25.9 [+20.54, +31.92] 117/1 p=0; [20.5357, 31.9196] | +52.5 [+35.59, +69.49] 31/0 p=0; [35.5932, 69.4915] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite g2, haiku | post hoc | 97.50 (C = 2) | +25.9 [+21.21, +30.80] 117/1 p=0; [21.2054, 31.0268] | +52.5 [+38.98, +67.80] 31/0 p=0; [38.9831, 67.7966] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite g3, haiku | post hoc | 98.75 | +31.9 [+26.34, +37.95] 144/1 p=0; [26.3393, 38.1696] | +50.8 [+35.59, +66.10] 30/0 p=0; [35.5932, 66.1017] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite g3, haiku | post hoc | 97.50 (C = 2) | +31.9 [+26.79, +37.28] 144/1 p=0; [26.7857, 37.2768] | +50.8 [+37.29, +64.41] 30/0 p=0; [37.2881, 64.4068] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite n1, haiku | post hoc | 98.75 | +4.2 [+1.56, +7.14] 22/3 p=0.000157; [1.5625, 7.1429] | +11.9 [+1.69, +22.03] 7/0 p=0.01562; [1.6949, 22.0339] | flag | hold | flag | hold | hold | flag; flag | flag; flag |
| rewrite n1, haiku | post hoc | 99.17 (C = 6) | +4.2 [+1.56, +7.37] 22/3 p=0.000157; [1.5625, 7.3661] | +11.9 [+1.69, +23.73] 7/0 p=0.01562; [1.6949, 23.7288] | flag | hold | flag | hold | hold | flag; flag | flag; flag |
| rewrite n2, haiku | post hoc | 98.75 | +7.8 [+4.69, +11.38] 39/4 p=0; [4.6875, 11.6071] | +13.6 [+1.69, +27.12] 9/1 p=0.02148; [1.6949, 27.1186] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite n2, haiku | post hoc | 97.50 (C = 2) | +7.8 [+4.91, +11.16] 39/4 p=0; [4.9107, 11.1607] | +13.6 [+3.39, +25.42] 9/1 p=0.02148; [3.3898, 25.4237] | flag | flag | flag | flag | flag | flag; flag | flag; flag |
| rewrite n3, haiku | post hoc | 98.75 | +6.0 [+2.90, +9.38] 31/4 p=3e-06; [2.9018, 9.375] | +8.5 [-5.08, +22.03] 7/2 p=0.1797; [-5.0847, 22.0339] | flag | flag | flag | flag | flag | flag; flag | hold; hold |
| rewrite n3, haiku | post hoc | 97.50 (C = 2) | +6.0 [+3.12, +8.93] 31/4 p=3e-06; [3.125, 8.9286] | +8.5 [-3.39, +20.34] 7/2 p=0.1797; [-3.3898, 20.339] | flag | flag | flag | flag | flag | flag; flag | hold; hold |
| field order (10 answers), haiku | prospective | 98.75 | +0.2 [-1.79, +2.23] 7/6 p=1; [-1.7857, 2.2321] | +1.2 [-3.56, +6.61] 4/5 p=1; [-3.5593, 6.6102] | hold | hold | hold | hold | hold | hold; hold | pass; pass |
| field order (10 answers), haiku | prospective | 99.17 (C = 6) | +0.2 [-2.01, +2.23] 7/6 p=1; [-2.0089, 2.2321] | +1.2 [-3.73, +6.78] 4/5 p=1; [-3.7288, 7.1186] | hold | hold | hold | hold | hold | hold; hold | pass; pass |
| repeat (10 answers), haiku | prospective | 98.75 | +0.2 [-0.89, +1.56] 3/2 p=1; [-0.8929, 1.5625] | +0.1 [-1.75, +2.20] 4/4 p=1; [-1.7514, 2.2034] | pass | pass | pass | pass | pass | pass; pass | pass; pass |
| repeat (10 answers), haiku | prospective | 99.58 (C = 12) | +0.2 [-1.12, +1.79] 3/2 p=1; [-1.1161, 1.7857] | +0.1 [-2.02, +2.37] 4/4 p=1; [-2.0151, 2.467] | pass | pass | pass | pass | pass | pass; pass | pass; pass |

### C. Table 15 exploratory rows

- value-only rename, sonnet, 99.5%: open -12.4 [-15.49, -8.88] 0/113 p=0; sym [-15.4895, -8.8393]; specific -31.3 [-39.48, -22.96] 0/79 p=0; sym [-39.485, -22.5322]; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- value-only rename, haiku, 99.5%: open -2.2 [-3.63, -1.07] 0/26 p=0; sym [-3.6349, -1.0326]; specific -21.6 [-28.47, -14.45] 4/73 p=0; sym [-28.4692, -14.3062]; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- value-only rename, sol, 99.5%: open -18.4 [-22.51, -15.05] 1/149 p=0; sym [-22.5124, -14.9254]; specific -; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- value-only rename, luna, 99.5%: open -16.9 [-20.49, -13.59] 1/173 p=0; sym [-20.4874, -13.5068]; specific -43.6 [-52.22, -34.62] 1/120 p=0; sym [-52.2175, -34.6209]; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- value-only rename, deepseek, 99.5%: open -10.3 [-13.90, -7.32] 2/85 p=0; sym [-13.8958, -7.3201]; specific -; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- value-only rename, qwen, 99.5%: open -8.7 [-11.91, -5.54] 6/69 p=0; sym [-11.9114, -5.4017]; specific -; L=5 first flag/flag; L=3 flag/flag; L=10 hold/hold; changed by the index: none
- value-only rename, gemma, 99.5%: open -17.6 [-21.70, -14.21] 0/141 p=0; sym [-21.6958, -14.2145]; specific -; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- opaque code, sonnet, 99.5%: open -11.6 [-14.79, -8.38] 0/108 p=0; sym [-14.7873, -8.261]; specific -23.4 [-31.12, -15.45] 0/59 p=0; sym [-31.1159, -15.4506]; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- opaque code, haiku, 99.5%: open -0.9 [-2.07, +0.29] 7/20 p=0.01916; sym [-2.0653, 0.2891]; specific -7.6 [-13.16, -2.00] 10/34 p=0.000388; sym [-13.1617, -2.0029]; L=5 first flag/flag; L=3 flag/flag; L=10 hold/hold; changed by the index: none
- opaque code, sol, 99.5%: open -6.0 [-8.57, -3.73] 3/51 p=0; sym [-8.5714, -3.6025]; specific -; L=5 first flag/flag; L=3 flag/flag; L=10 hold/hold; changed by the index: none
- opaque code, luna, 99.5%: open -15.0 [-18.50, -11.90] 5/162 p=0; sym [-18.5048, -11.8959]; specific -22.3 [-30.04, -15.31] 2/65 p=0; sym [-30.0429, -15.1645]; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- opaque code, deepseek, 99.5%: open -7.4 [-10.79, -4.34] 12/72 p=0; sym [-10.794, -4.0943]; specific -; L=5 first flag/flag; L=3 flag/flag; L=10 hold/hold; changed by the index: none
- opaque code, qwen, 99.5%: open -5.3 [-8.85, -1.80] 24/62 p=5.1e-05; sym [-8.852, -1.7981]; specific -; L=5 first flag/flag; L=3 flag/flag; L=10 hold/hold; changed by the index: none
- opaque code, gemma, 99.5%: open -16.8 [-20.50, -13.38] 0/134 p=0; sym [-20.5, -13.25]; specific -; L=5 first flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- tool-call full rename, all answers, sonnet, 99.58%: open -19.1 [-24.44, -13.84] 1/89 p=0; sym [-24.442, -13.6161]; specific -47.5 [-65.25, -28.81] 0/31 p=0; sym [-65.2542, -28.8136]; L=5 flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- tool-call full rename, all answers, haiku, 99.58%: open -5.8 [-8.93, -3.24] 0/32 p=0; sym [-8.9286, -3.2366]; specific -8.6 [-19.83, -0.86] 0/6 p=0.03125; sym [-19.8276, -0.8621]; L=5 flag/flag; L=3 flag/flag; L=10 hold/hold; changed by the index: none
- tool-call full rename, all answers, opus, 99.58%: open -20.8 [-26.79, -14.73] 2/95 p=0; sym [-26.7857, -14.7321]; specific -49.2 [-67.80, -32.20] 0/29 p=0; sym [-67.7966, -32.2034]; L=5 flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- tool-call full rename, all answers, sol, 99.58%: open -23.5 [-29.13, -17.86] 0/118 p=0; sym [-29.1295, -17.7455]; specific -57.6 [-74.58, -40.68] 0/38 p=0; sym [-74.5763, -40.678]; L=5 flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- tool-call full rename, all answers, astra, 99.58%: open -31.0 [-37.50, -25.00] 0/139 p=0; sym [-37.5, -25.0]; specific -79.7 [-93.22, -64.41] 0/47 p=0; sym [-93.2203, -64.4068]; L=5 flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none
- tool-call full rename, all answers, luna, 99.58%: open -18.2 [-23.21, -13.28] 0/91 p=0; sym [-23.2143, -13.1696]; specific -33.9 [-52.54, -18.64] 0/23 p=0; sym [-52.5424, -18.6441]; L=5 flag/flag; L=3 flag/flag; L=10 flag/flag; changed by the index: none

### D. Error-rate model (59 requests, one answer each, 98.75%)

```
{
 "n": 59,
 "level": 0.9875,
 "low_end": "12th lowest (both rules)",
 "high_end_as_run": "13th highest",
 "high_end_symmetric": "12th highest",
 "true_change_zero": [
  {
   "p_up": 0.01,
   "p_down": 0.01,
   "true_change": 0.0,
   "first_as_run": 0.000256,
   "first_symmetric": 0.000238,
   "revised_as_run": 0.0,
   "revised_symmetric": 0.0
  },
  {
   "p_up": 0.02,
   "p_down": 0.02,
   "true_change": 0.0,
   "first_as_run": 0.003125,
   "first_symmetric": 0.002935,
   "revised_as_run": 1.6e-05,
   "revised_symmetric": 1.6e-05
  },
  {
   "p_up": 0.04,
   "p_down": 0.04,
   "true_change": 0.0,
   "first_as_run": 0.014433,
   "first_symmetric": 0.013783,
   "revised_as_run": 0.000601,
   "revised_symmetric": 0.000601
  },
  {
   "p_up": 0.06,
   "p_down": 0.06,
   "true_change": 0.0,
   "first_as_run": 0.017343,
   "first_symmetric": 0.016728,
   "revised_as_run": 0.002423,
   "revised_symmetric": 0.002423
  },
  {
   "p_up": 0.1,
   "p_down": 0.1,
   "true_change": 0.0,
   "first_as_run": 0.013598,
   "first_symmetric": 0.013159,
   "revised_as_run": 0.005032,
   "revised_symmetric": 0.005032
  }
 ],
 "true_change_above_L": [
  {
   "p_up": 0.051,
   "true_change": 5.1,
   "as_run": 0.045573,
   "symmetric": 0.045573,
   "final": 0.0,
   "no_request_changes": 0.045573
  },
  {
   "p_up": 0.06,
   "true_change": 6.0,
   "as_run": 0.025974,
   "symmetric": 0.025974,
   "final": 0.0,
   "no_request_changes": 0.025974
  }
 ]
}
```

### E. Floor of the sign condition (one answer per request, no change in the other direction)

```
{
 "97.50%": {
  "alpha": 0.025,
  "min_changes_one_direction": 7,
  "sign_p_at_min": 0.015625,
  "sign_p_one_fewer": 0.03125,
  "points_on_59": 11.86,
  "points_on_448": 1.56
 },
 "98.75%": {
  "alpha": 0.0125,
  "min_changes_one_direction": 8,
  "sign_p_at_min": 0.007812,
  "sign_p_one_fewer": 0.015625,
  "points_on_59": 13.56,
  "points_on_448": 1.79
 },
 "99.17%": {
  "alpha": 0.008333,
  "min_changes_one_direction": 8,
  "sign_p_at_min": 0.007812,
  "sign_p_one_fewer": 0.015625,
  "points_on_59": 13.56,
  "points_on_448": 1.79
 },
 "99.50%": {
  "alpha": 0.005,
  "min_changes_one_direction": 9,
  "sign_p_at_min": 0.003906,
  "sign_p_one_fewer": 0.007812,
  "points_on_59": 15.25,
  "points_on_448": 2.01
 }
}
```

### F. Summary for the paper

```
{
 "decisions_changed_by_the_index_at_levels_as_run": [],
 "largest_high_end_moves": [
  [
   1.7241,
   "pair haiku era1 read 2 v erm specific"
  ],
  [
   1.7241,
   "pair haiku era1 read 2 v erc2 specific"
  ],
  [
   1.7241,
   "pair haiku era1 read 1 v ers specific"
  ],
  [
   1.6949,
   "pair sonnet fill read 3 v erp specific"
  ],
  [
   1.6949,
   "edit rewrite h2, haiku specific"
  ]
 ],
 "final_rule": {
  "R10-20 at 99.5%": {
   "sol": {
    "a": "pass",
    "b": "pass",
    "c": "flag"
   },
   "luna": {
    "a": "hold",
    "b": "hold",
    "c": "flag"
   },
   "deepseek": {
    "a": "hold",
    "b": "flag",
    "c": "flag"
   },
   "qwen": {
    "a": "hold",
    "b": "hold",
    "c": "flag"
   },
   "gemma": {
    "a": "pass",
    "b": "hold",
    "c": "flag"
   }
  },
  "R10-22 at 98.75%": {
   "sol": {
    "d": "hold",
    "e": "pass"
   },
   "luna": {
    "d": "hold",
    "e": "hold"
   }
  },
  "Table 18 rows": {
   "full rename, sonnet": "flag",
   "full rename, haiku": "flag",
   "full rename, opus": "flag",
   "full rename, sol": "flag",
   "full rename, astra": "flag",
   "full rename, luna": "flag",
   "broad rewrite, sonnet": "hold",
   "broad rewrite, sol": "flag",
   "steered th, sonnet": "flag",
   "steered th, haiku": "flag",
   "steered tg, sonnet": "flag",
   "steered tg, haiku": "flag",
   "rewrite h1, haiku": "flag",
   "rewrite h2, haiku": "flag",
   "rewrite h3, haiku": "flag",
   "rewrite g1, haiku": "flag",
   "rewrite g2, haiku": "flag",
   "rewrite g3, haiku": "flag",
   "rewrite n1, haiku": "hold",
   "rewrite n2, haiku": "flag",
   "rewrite n3, haiku": "flag",
   "field order (10 answers), haiku": "hold",
   "repeat (10 answers), haiku": "pass"
  },
  "unchanged one answer at 99.5%": {
   "hold": 29
  },
  "unchanged all answers at 99.5%": {
   "hold": 28,
   "pass": 1
  },
  "all answers, first rule at 98.75%, as run / reversed / symmetric": [
   {
    "flag": 2,
    "hold": 23,
    "pass": 4
   },
   {
    "flag": 2,
    "hold": 23,
    "pass": 4
   },
   {
    "flag": 2,
    "hold": 24,
    "pass": 3
   }
  ]
 }
}
```
