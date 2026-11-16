# Review round 2: post hoc analyses (exploratory)

Every section is post hoc: chosen after the results. No model call. Definitions and choices: the docstring of r10/analysis/r2_posthoc.py. Bootstrap: 2,000 draws, seed 20261112.

## 1. Held-out test with the hotel-only outcome (post hoc)

Read 1 of the opened stage-1 answers, 7 models. Registered outcome: `type` holds `hotel`. Hotel-only: `type` holds `hotel` and not `guesthouse`. Panel mean of t_renamed minus t_legacy, in points; 95% cluster bootstrap interval over dialogues. Registered columns reproduce RESULT-STAGE1.md part 1 and part 5(c): yes.

| Test | Sample | Panel, registered | 95% interval | Panel, hotel-only | 95% interval |
|---|---|---|---|---|---|
| wrong_values | natural (213) | -13.0 | [-16.0, -10.1] | -11.6 | [-14.5, -8.9] |
| correct_values_kept | goal_hotel (77) | -29.1 | [-35.1, -23.9] | -26.1 | [-32.0, -20.7] |

**wrong_values** (natural sample), per model (post hoc)

| Model | Dialogues | Registered | 95% interval | Sign (higher/lower), p | Hotel-only | 95% interval | Sign (higher/lower), p |
|---|---|---|---|---|---|---|---|
| sonnet | 213 | -11.7 | [-16.4, -8.0] | 0/25, 6.0e-08 | -11.3 | [-16.0, -7.5] | 0/24, 1.2e-07 |
| haiku | 213 | -4.7 | [-7.5, -1.9] | 0/10, 0.0020 | -4.2 | [-7.0, -1.9] | 0/9, 0.0039 |
| sol | 213 | -17.4 | [-23.0, -12.7] | 0/37, 1.5e-11 | -17.4 | [-23.0, -12.7] | 0/37, 1.5e-11 |
| luna | 213 | -17.4 | [-23.0, -12.7] | 0/37, 1.5e-11 | -14.1 | [-19.2, -9.9] | 0/30, 1.9e-09 |
| deepseek | 213 | -11.7 | [-16.4, -7.5] | 1/26, 4.2e-07 | -10.3 | [-14.6, -6.1] | 1/23, 3.0e-06 |
| qwen | 187 | -7.5 | [-12.3, -3.2] | 2/16, 0.0013 | -6.4 | [-10.7, -2.7] | 1/13, 0.0018 |
| gemma | 212 | -17.9 | [-23.6, -13.2] | 0/38, 7.3e-12 | -15.1 | [-20.3, -10.4] | 0/32, 4.7e-10 |

**correct_values_kept** (goal_hotel sample), per model (post hoc)

| Model | Dialogues | Registered | 95% interval | Sign (higher/lower), p | Hotel-only | 95% interval | Sign (higher/lower), p |
|---|---|---|---|---|---|---|---|
| sonnet | 77 | -19.5 | [-28.6, -10.4] | 0/15, 0.0001 | -16.9 | [-27.3, -7.8] | 2/15, 0.0023 |
| haiku | 77 | -23.4 | [-32.5, -14.3] | 0/18, 7.6e-06 | -23.4 | [-32.5, -14.3] | 0/18, 7.6e-06 |
| sol | 77 | -26.0 | [-36.4, -16.9] | 0/20, 1.9e-06 | -26.0 | [-36.4, -16.9] | 0/20, 1.9e-06 |
| luna | 77 | -57.1 | [-67.5, -46.8] | 0/44, 1.1e-13 | -48.1 | [-59.7, -37.7] | 0/37, 1.5e-11 |
| deepseek | 77 | -20.8 | [-31.2, -11.7] | 1/17, 0.0001 | -16.9 | [-26.0, -7.8] | 1/14, 0.0010 |
| qwen | 60 | -23.3 | [-36.7, -10.0] | 4/18, 0.0043 | -20.0 | [-33.3, -6.7] | 4/16, 0.0118 |
| gemma | 77 | -33.8 | [-45.5, -23.4] | 0/26, 3.0e-08 | -31.2 | [-42.9, -20.8] | 0/24, 1.2e-07 |

**Base rates under t_legacy** (read 1, post hoc)

| Model | Natural, registered | Natural, hotel-only | Goal-hotel, registered | Goal-hotel, hotel-only |
|---|---|---|---|---|
| sonnet | 32/213 (15.0%, [10.8%, 20.2%]) | 30/213 (14.1%, [9.9%, 19.2%]) | 50/77 (64.9%, [54.5%, 75.3%]) | 46/77 (59.7%, [49.4%, 70.1%]) |
| haiku | 12/213 (5.6%, [2.8%, 8.9%]) | 11/213 (5.2%, [2.3%, 8.0%]) | 37/77 (48.1%, [36.4%, 59.7%]) | 37/77 (48.1%, [36.4%, 59.7%]) |
| sol | 68/213 (31.9%, [25.8%, 38.5%]) | 67/213 (31.5%, [25.4%, 38.0%]) | 65/77 (84.4%, [76.6%, 92.2%]) | 64/77 (83.1%, [74.0%, 90.9%]) |
| luna | 40/213 (18.8%, [14.1%, 24.4%]) | 33/213 (15.5%, [10.8%, 20.7%]) | 53/77 (68.8%, [58.4%, 79.2%]) | 46/77 (59.7%, [49.4%, 70.1%]) |
| deepseek | 33/213 (15.5%, [10.8%, 20.7%]) | 29/213 (13.6%, [8.9%, 18.3%]) | 38/77 (49.4%, [37.7%, 61.0%]) | 34/77 (44.2%, [33.8%, 55.8%]) |
| qwen | 24/199 (12.1%, [8.0%, 16.6%]) | 19/199 (9.5%, [6.0%, 13.6%]) | 34/69 (49.3%, [37.7%, 60.9%]) | 30/69 (43.5%, [31.9%, 55.1%]) |
| gemma | 46/212 (21.7%, [16.5%, 27.4%]) | 38/212 (17.9%, [13.2%, 23.1%]) | 54/77 (70.1%, [59.7%, 80.5%]) | 49/77 (63.6%, [53.2%, 74.0%]) |

## 2. Random-deletion reference for the renames (post hoc)

Random deletion of baseline `hotel` values loses (baseline correct rate x correct weight) / (baseline wrong rate x wrong weight) correct values per wrong value removed. D = share of baseline correct values kept minus share of baseline wrong values kept; D > 0 means the rename keeps correct values better than random deletion (its ratio is lower).

### 2a. Held-out (weights natural 281, goal-hotel 97; baseline t_legacy; read 1)

**t_renamed**, registered outcome

| Model | Paired dialogues | Wrong removed | Correct lost | Rename ratio | 95% interval | Random-deletion ratio | Below random | D [95% interval] |
|---|---|---|---|---|---|---|---|---|
| sonnet | 213, 77 | 33.0 | 18.9 | 0.57 | [0.30, 1.03] | 1.49 | yes | 0.48 [0.28, 0.67] |
| haiku | 213, 77 | 13.2 | 22.7 | 1.72 | [0.88, 4.06] | 2.94 | yes | 0.35 [0.05, 0.61] |
| sol | 213, 77 | 48.8 | 25.2 | 0.52 | [0.32, 0.82] | 0.91 | yes | 0.24 [0.07, 0.39] |
| luna | 213, 77 | 48.8 | 55.4 | 1.14 | [0.81, 1.67] | 1.27 | yes | 0.09 [-0.03, 0.22] |
| deepseek | 213, 77 | 33.0 | 20.2 | 0.61 | [0.31, 1.10] | 1.10 | yes | 0.34 [0.11, 0.56] |
| qwen | 187, 60 | 21.0 | 22.6 | 1.08 | [0.39, 2.63] | 1.70 | yes | 0.27 [-0.07, 0.59] |
| gemma | 212, 77 | 50.4 | 32.8 | 0.65 | [0.42, 0.98] | 1.12 | yes | 0.34 [0.17, 0.51] |
| panel | 213, 77 | 35.7 | 28.4 | 0.80 | [0.58, 1.08] | 1.27 | yes | 0.28 [0.16, 0.39] |

**f4**, registered outcome

| Model | Paired dialogues | Wrong removed | Correct lost | Rename ratio | 95% interval | Random-deletion ratio | Below random | D [95% interval] |
|---|---|---|---|---|---|---|---|---|
| sonnet | 213, 77 | 40.9 | 45.4 | 1.11 | [0.75, 1.67] | 1.49 | yes | 0.25 [0.11, 0.39] |
| haiku | 213, 77 | 7.9 | 22.7 | 2.86 | [1.31, 10.03] | 2.94 | yes | 0.01 [-0.33, 0.36] |
| sol | 213, 77 | 77.8 | 32.8 | 0.42 | [0.28, 0.61] | 0.91 | yes | 0.47 [0.32, 0.60] |
| luna | 213, 77 | 51.5 | 56.7 | 1.10 | [0.78, 1.59] | 1.27 | yes | 0.13 [0.02, 0.24] |
| deepseek | 213, 77 | 43.5 | 42.8 | 0.98 | [0.66, 1.45] | 1.10 | yes | 0.11 [0.02, 0.21] |
| qwen | 191, 63 | 23.5 | 21.6 | 0.92 | [0.38, 1.90] | 1.80 | yes | 0.44 [0.16, 0.72] |
| gemma | 210, 77 | 60.2 | 56.7 | 0.94 | [0.68, 1.29] | 1.13 | yes | 0.17 [0.08, 0.27] |
| panel | 213, 77 | 43.9 | 40.3 | 0.92 | [0.71, 1.21] | 1.27 | yes | 0.26 [0.18, 0.34] |

**t_renamed**, hotel_only outcome (extra rows, post hoc)

| Model | Paired dialogues | Wrong removed | Correct lost | Rename ratio | 95% interval | Random-deletion ratio | Below random | D [95% interval] |
|---|---|---|---|---|---|---|---|---|
| sonnet | 213, 77 | 31.7 | 16.4 | 0.52 | [0.22, 1.01] | 1.46 | yes | 0.52 [0.30, 0.72] |
| haiku | 213, 77 | 11.9 | 22.7 | 1.91 | [0.95, 4.77] | 3.21 | yes | 0.33 [0.03, 0.60] |
| sol | 213, 77 | 48.8 | 25.2 | 0.52 | [0.32, 0.82] | 0.91 | yes | 0.24 [0.07, 0.40] |
| luna | 213, 77 | 39.6 | 46.6 | 1.18 | [0.79, 1.87] | 1.33 | yes | 0.10 [-0.04, 0.25] |
| deepseek | 213, 77 | 29.0 | 16.4 | 0.56 | [0.25, 1.11] | 1.12 | yes | 0.38 [0.13, 0.62] |
| qwen | 187, 60 | 18.0 | 19.4 | 1.08 | [0.36, 2.77] | 1.75 | yes | 0.29 [-0.05, 0.65] |
| gemma | 212, 77 | 42.4 | 30.2 | 0.71 | [0.44, 1.12] | 1.23 | yes | 0.35 [0.17, 0.53] |
| panel | 213, 77 | 31.9 | 25.5 | 0.80 | [0.57, 1.13] | 1.31 | yes | 0.29 [0.16, 0.40] |

**f4**, hotel_only outcome (extra rows, post hoc)

| Model | Paired dialogues | Wrong removed | Correct lost | Rename ratio | 95% interval | Random-deletion ratio | Below random | D [95% interval] |
|---|---|---|---|---|---|---|---|---|
| sonnet | 213, 77 | 38.3 | 44.1 | 1.15 | [0.75, 1.77] | 1.46 | yes | 0.21 [0.07, 0.34] |
| haiku | 213, 77 | 6.6 | 27.7 | 4.20 | [1.91, 21.01] | 3.21 | no | -0.14 [-0.48, 0.23] |
| sol | 213, 77 | 76.5 | 32.8 | 0.43 | [0.29, 0.62] | 0.91 | yes | 0.46 [0.31, 0.59] |
| luna | 213, 77 | 42.2 | 47.9 | 1.13 | [0.77, 1.74] | 1.33 | yes | 0.14 [0.02, 0.28] |
| deepseek | 213, 77 | 38.3 | 39.1 | 1.02 | [0.66, 1.61] | 1.12 | yes | 0.09 [0.00, 0.20] |
| qwen | 191, 63 | 19.1 | 23.1 | 1.21 | [0.55, 2.62] | 2.02 | yes | 0.37 [0.13, 0.64] |
| gemma | 210, 77 | 49.5 | 51.6 | 1.04 | [0.73, 1.47] | 1.25 | yes | 0.16 [0.07, 0.27] |
| panel | 213, 77 | 38.9 | 38.4 | 0.99 | [0.74, 1.33] | 1.32 | yes | 0.23 [0.14, 0.32] |

### 2b. Earlier experiments (round 9; weights S1t 994 + S3 490 wrong, S2 545 correct; baseline F0)

Paired dialogues: S1t, S3, S2.

| Model, form | Paired dialogues | Wrong removed | Correct lost | Rename ratio | 95% interval | Random-deletion ratio | Below random | D [95% interval] |
|---|---|---|---|---|---|---|---|---|
| sonnet f1 | 994, 490, 545 | 154.5 | 138.0 | 0.89 | [0.73, 1.09] | 1.72 | yes | 0.34 [0.26, 0.42] |
| sonnet f2 | 994, 490, 545 | 171.8 | 172.5 | 1.00 | [0.84, 1.21] | 1.72 | yes | 0.33 [0.26, 0.40] |
| sonnet f4 | 994, 490, 545 | 202.2 | 273.5 | 1.35 | [1.17, 1.57] | 1.72 | yes | 0.20 [0.14, 0.25] |
| sonnet f6 | 994, 490, 545 | 159.7 | 138.0 | 0.86 | [0.70, 1.06] | 1.72 | yes | 0.36 [0.29, 0.44] |
| haiku f1 | 994, 490, 545 | 53.7 | 99.0 | 1.84 | [1.39, 2.58] | 3.05 | yes | 0.30 [0.18, 0.41] |
| haiku f2 | 994, 490, 545 | 48.7 | 85.0 | 1.75 | [1.26, 2.43] | 3.05 | yes | 0.29 [0.18, 0.40] |
| haiku f4 | 994, 490, 545 | 49.3 | 94.3 | 1.91 | [1.42, 2.68] | 3.05 | yes | 0.26 [0.14, 0.37] |
| haiku f6 | 994, 490, 545 | 20.3 | 22.3 | 1.10 | [0.43, 2.69] | 3.05 | yes | 0.18 [0.03, 0.33] |
| sol f1 | 992, 201, 229 | 294.4 | 161.8 | 0.55 | [0.43, 0.68] | 1.06 | yes | 0.30 [0.22, 0.38] |
| sol f4 | 992, 201, 228 | 355.3 | 224.7 | 0.63 | [0.52, 0.75] | 1.06 | yes | 0.31 [0.23, 0.39] |
| luna f1 | 994, 490, 545 | 255.3 | 238.7 | 0.93 | [0.81, 1.07] | 1.31 | yes | 0.26 [0.21, 0.32] |
| luna f4 | 994, 490, 545 | 266.3 | 294.0 | 1.10 | [0.98, 1.25] | 1.31 | yes | 0.15 [0.11, 0.19] |

Variant without S3 (S1t 994 wrong, S2 545 correct), for every cell with S1t and S2 reads. Paired dialogues: S1t, S2.

| Model, form | Paired dialogues | Wrong removed | Correct lost | Rename ratio | 95% interval | Random-deletion ratio | Below random | D [95% interval] |
|---|---|---|---|---|---|---|---|---|
| sonnet f1 | 994, 545 | 132.0 | 138.0 | 1.05 | [0.85, 1.29] | 2.04 | yes | 0.35 [0.27, 0.43] |
| sonnet f2 | 994, 545 | 148.3 | 172.5 | 1.16 | [0.96, 1.40] | 2.04 | yes | 0.35 [0.27, 0.42] |
| sonnet f4 | 994, 545 | 171.7 | 273.5 | 1.59 | [1.37, 1.86] | 2.04 | yes | 0.21 [0.15, 0.26] |
| sonnet f6 | 994, 545 | 135.7 | 138.0 | 1.02 | [0.83, 1.25] | 2.04 | yes | 0.37 [0.29, 0.45] |
| haiku f1 | 994, 545 | 37.7 | 99.0 | 2.63 | [1.93, 3.82] | 4.32 | yes | 0.29 [0.16, 0.42] |
| haiku f2 | 994, 545 | 32.3 | 85.0 | 2.63 | [1.85, 3.90] | 4.32 | yes | 0.25 [0.12, 0.39] |
| haiku f4 | 994, 545 | 32.0 | 94.3 | 2.95 | [2.12, 4.43] | 4.32 | yes | 0.20 [0.06, 0.33] |
| haiku f6 | 994, 545 | 11.7 | 22.3 | 1.91 | [0.71, 7.89] | 4.32 | yes | 0.13 [-0.05, 0.29] |
| sol f1 | 992, 229 | 267.5 | 161.8 | 0.60 | [0.48, 0.75] | 1.21 | yes | 0.32 [0.24, 0.40] |
| sol f4 | 992, 228 | 323.7 | 224.7 | 0.69 | [0.56, 0.83] | 1.21 | yes | 0.33 [0.25, 0.41] |
| luna f1 | 994, 545 | 209.0 | 238.7 | 1.14 | [0.99, 1.32] | 1.63 | yes | 0.28 [0.22, 0.33] |
| luna f2 | 994, 545 | 208.3 | 231.3 | 1.11 | [0.96, 1.29] | 1.63 | yes | 0.29 [0.24, 0.35] |
| luna f4 | 994, 545 | 217.7 | 294.0 | 1.35 | [1.19, 1.54] | 1.63 | yes | 0.17 [0.12, 0.21] |
| luna f6 | 994, 545 | 178.0 | 147.7 | 0.83 | [0.69, 0.99] | 1.63 | yes | 0.39 [0.32, 0.46] |
| deepseek f1 | 990, 545 | 135.5 | 144.0 | 1.06 | [0.83, 1.33] | 1.76 | yes | 0.33 [0.24, 0.42] |
| deepseek f4 | 992, 545 | 149.3 | 208.0 | 1.39 | [1.16, 1.69] | 1.77 | yes | 0.19 [0.12, 0.26] |
| qwen f1 | 882, 451 | 108.2 | 169.2 | 1.56 | [1.22, 2.05] | 1.96 | yes | 0.15 [0.05, 0.25] |
| qwen f4 | 876, 458 | 127.1 | 205.9 | 1.62 | [1.30, 2.06] | 1.94 | yes | 0.14 [0.05, 0.23] |
| gemma f1 | 988, 538 | 218.3 | 208.7 | 0.96 | [0.82, 1.13] | 1.63 | yes | 0.36 [0.30, 0.43] |
| gemma f4 | 979, 534 | 244.7 | 359.3 | 1.47 | [1.30, 1.68] | 1.63 | yes | 0.10 [0.06, 0.13] |

Cells without reads on all three groups (paired dialogues per group): sol f2 (S1t 991, S3 0, S2 0); sol f6 (S1t 992, S3 0, S2 0); luna f2 (S1t 994, S3 0, S2 545); luna f6 (S1t 994, S3 0, S2 545); deepseek f1 (S1t 990, S3 0, S2 545); deepseek f2 (S1t 992, S3 0, S2 0); deepseek f4 (S1t 992, S3 0, S2 545); deepseek f6 (S1t 993, S3 0, S2 0); qwen f1 (S1t 882, S3 0, S2 451); qwen f2 (S1t 872, S3 0, S2 0); qwen f4 (S1t 876, S3 0, S2 458); qwen f6 (S1t 885, S3 0, S2 0); gemma f1 (S1t 988, S3 0, S2 538); gemma f2 (S1t 985, S3 0, S2 0); gemma f4 (S1t 979, S3 0, S2 534); gemma f6 (S1t 982, S3 0, S2 0).

## 3. Word-or-meaning tests on brief-agreeing dialogues (post hoc)

Round-9 reads (natural_analyze.load). Rate of `type = hotel` over valid reads (dialogues with reads). Paired difference: form minus F0, per-dialogue means, in points, 95% cluster bootstrap interval, exact sign test over dialogues (form higher / form lower). A dash: no reads.

### S2, brief sets hotel (233 dialogues)

| Model | F0 | F1 | F2 | F4 | F6 |
|---|---|---|---|---|---|
| sonnet | 83.9% (233) | 58.8% (233); -25.1 [-30.7, -19.5], 0/63, p 2.2e-19 | 52.6% (233); -31.3 [-37.3, -25.5], 0/79, p 3.3e-24 | 28.8% (233); -55.2 [-61.6, -48.7], 0/136, p 2.3e-41 | 60.5% (233); -23.4 [-28.8, -18.5], 0/59, p 3.5e-18 |
| haiku | 55.9% (233) | 30.2% (233); -25.8 [-31.2, -20.5], 4/76, p 2.8e-18 | 34.3% (233); -21.6 [-27.0, -16.7], 4/73, p 1.9e-17 | 32.5% (233); -23.5 [-28.5, -18.3], 4/77, p 1.4e-18 | 48.4% (233); -7.6 [-11.6, -3.6], 10/34, p 0.0004 |
| sol | 98.1% (103) | 79.6% (103); -18.4 [-27.2, -11.7], 0/19, p 3.8e-06 | - | 72.8% (103); -25.2 [-34.0, -17.5], 0/26, p 3.0e-08 | - |
| luna | 79.7% (233) | 34.2% (233); -45.5 [-51.4, -39.5], 2/128, p 1.3e-35 | 36.1% (233); -43.6 [-49.8, -37.9], 1/120, p 9.2e-35 | 20.6% (233); -59.1 [-64.8, -53.4], 1/162, p 2.8e-47 | 57.4% (233); -22.3 [-27.5, -17.5], 2/65, p 3.1e-17 |
| deepseek | 65.7% (233) | 36.9% (233); -28.8 [-35.6, -21.9], 9/76, p 2.4e-14 | - | 21.9% (233); -43.8 [-50.6, -36.9], 3/105, p 1.3e-27 | - |
| qwen | 65.7% (210) | 27.4% (215); -37.4 [-45.5, -29.3], 8/82, p 1.4e-16 | - | 21.5% (219); -44.8 [-53.2, -36.8], 10/100, p 8.0e-20 | - |
| gemma | 85.8% (232) | 49.4% (233); -36.6 [-42.7, -31.0], 0/85, p 5.2e-26 | - | 15.6% (231); -70.1 [-75.8, -64.5], 0/162, p 3.4e-49 | - |

### S1t, brief sets no type (807 dialogues)

| Model | F0 | F1 | F2 | F4 | F6 |
|---|---|---|---|---|---|
| sonnet | 14.0% (807) | 3.0% (807); -11.0 [-13.3, -9.0], 1/101, p 4.1e-29 | 1.7% (807); -12.4 [-14.7, -10.2], 0/113, p 1.9e-34 | 0.5% (807); -13.5 [-15.9, -11.2], 0/120, p 1.5e-36 | 2.4% (807); -11.6 [-13.8, -9.5], 0/108, p 6.2e-33 |
| haiku | 3.1% (807) | 0.6% (807); -2.6 [-3.6, -1.6], 0/28, p 7.5e-09 | 0.9% (807); -2.2 [-3.2, -1.4], 0/26, p 3.0e-08 | 0.9% (807); -2.3 [-3.3, -1.4], 0/27, p 1.5e-08 | 2.3% (807); -0.9 [-1.7, -0.0], 7/20, p 0.0192 |
| sol | 33.5% (805) | 10.4% (807); -23.1 [-26.0, -20.2], 0/186, p 2.0e-56 | 15.1% (806); -18.4 [-21.4, -15.8], 1/149, p 2.1e-43 | 5.8% (807); -27.7 [-30.9, -24.7], 0/223, p 1.5e-67 | 27.5% (807); -6.0 [-7.8, -4.3], 3/51, p 2.9e-12 |
| luna | 17.8% (807) | 0.9% (807); -16.9 [-19.4, -14.5], 0/172, p 3.3e-52 | 0.9% (807); -16.9 [-19.4, -14.5], 1/173, p 1.5e-50 | 0.5% (807); -17.3 [-19.8, -15.0], 0/177, p 1.0e-53 | 2.7% (807); -15.0 [-17.4, -12.8], 5/162, p 1.1e-41 |
| deepseek | 11.8% (807) | 2.0% (805); -9.8 [-12.0, -7.7], 3/82, p 5.3e-21 | 1.5% (806); -10.3 [-12.4, -8.3], 2/85, p 4.9e-23 | 0.5% (805); -11.3 [-13.5, -9.2], 1/92, p 1.9e-26 | 4.3% (806); -7.4 [-9.8, -5.3], 12/72, p 1.4e-11 |
| qwen | 11.1% (760) | 2.1% (761); -8.1 [-10.5, -5.9], 9/68, p 2.4e-12 | 1.7% (759); -8.7 [-10.9, -6.5], 6/69, p 1.2e-14 | 1.6% (755); -9.3 [-11.5, -7.1], 3/70, p 1.4e-17 | 5.1% (762); -5.3 [-7.9, -2.8], 24/62, p 0.0001 |
| gemma | 19.2% (804) | 1.4% (806); -17.8 [-20.7, -15.2], 0/143, p 1.8e-43 | 1.6% (805); -17.6 [-20.4, -15.0], 0/141, p 7.2e-43 | 0.1% (798); -19.0 [-21.7, -16.3], 0/151, p 7.0e-46 | 2.2% (803); -16.8 [-19.5, -14.1], 0/134, p 9.2e-41 |

### S3, brief sets guesthouse (394 dialogues)

| Model | F0 | F1 | F2 | F4 | F6 |
|---|---|---|---|---|---|
| sonnet | 4.8% (394) | 1.6% (394); -3.2 [-4.9, -1.6], 0/15, p 0.0001 | 1.9% (394); -2.9 [-4.6, -1.4], 0/14, p 0.0001 | 1.0% (394); -3.8 [-5.7, -2.0], 0/17, p 1.5e-05 | 1.5% (394); -3.3 [-5.2, -1.6], 0/15, p 0.0001 |
| haiku | 3.6% (394) | 0.9% (394); -2.7 [-4.4, -1.1], 1/15, p 0.0005 | 0.7% (394); -3.0 [-4.7, -1.5], 0/14, p 0.0001 | 0.8% (394); -2.8 [-4.4, -1.4], 0/14, p 0.0001 | 1.9% (394); -1.8 [-3.4, -0.3], 2/10, p 0.0386 |
| sol | 7.3% (164) | 3.7% (164); -3.7 [-6.7, -1.2], 0/6, p 0.0312 | - | 3.0% (164); -4.3 [-7.3, -1.2], 0/7, p 0.0156 | - |
| luna | 8.1% (394) | 1.8% (394); -6.3 [-8.7, -4.2], 1/33, p 4.1e-09 | - | 1.4% (394); -6.7 [-9.1, -4.6], 1/37, p 2.8e-10 | - |

## 4. Visibility of fitting hotels when a correct filter is dropped (post hoc, venue data only)

The call is the brief itself, not the model's call: the brief's area, price range, stars, parking and internet, with `type` removed (or with type = hotel kept). The tool shows the first 5 venues in the order of hotel_db.json (33 venues: 24 guesthouses, 9 hotels). Shares over dialogues, 95% cluster bootstrap interval.

| Set | Call | Dialogues | No fitting hotel in the first 5 | No hotel fits the brief at all | A fitting hotel exists but is not in the first 5 | More than 5 results | Empty result |
|---|---|---|---|---|---|---|---|
| S2, brief sets hotel | type removed | 233 | 12.9% [8.6%, 17.6%] | 0.0% [0.0%, 0.0%] | 12.9% [8.6%, 17.6%] | 55 | 0 |
| S2, brief sets hotel | type = hotel kept | 233 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 7 | 0 |
| 554 prefixes, brief sets hotel | type removed | 59 | 10.2% [3.4%, 18.6%] | 0.0% [0.0%, 0.0%] | 10.2% [3.4%, 18.6%] | 12 | 0 |
| 554 prefixes, brief sets hotel | type = hotel kept | 59 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 1 | 0 |

Notes: S2, brief sets hotel: briefs that name a venue 0; 554 prefixes, brief sets hotel: briefs that name a venue 0; prefixes where only fail_info sets hotel (not counted): 0.
