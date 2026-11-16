# Rename effect, split by clear and unclear requests (post hoc)

Status: post hoc and descriptive. No model call. The split rule is `clear_rule.py` (SHA-256 `e8cd2490a137a888a3463420f7da4349f29b645fb780a72288400cbaa7291794`). It was fixed in `out/clear_rule.md` before any split was computed. This script stops when the rule file differs.

- **Clear**: a traveller sentence requires a hotel or excludes the guesthouse kinds (label `hotel_only`).
- **Unclear**: no traveller sentence states a type (label `unclear`). Labels `guesthouse_only` and `mixed` are in the counts and in the JSON file only.
- **Effect**: per dialogue, the renamed cell minus the legacy cell (share of reads with `type = hotel`), then the mean over dialogues. A negative effect on the correct side means fewer correct `hotel` values under the renamed schema.
- **Relative change**: (mean renamed minus mean legacy) / mean legacy. It removes the effect of a different starting share.
- **Intervals**: 95% cluster bootstrap over dialogues, 2,000 draws, seed 20261112 (`stats.cluster_bootstrap`). The clear-minus-unclear interval resamples inside each group. No interval for a group of fewer than 5 dialogues.
- **Sign test**: exact, over dialogues (`stats.sign_test`). Higher / lower: dialogues whose renamed cell is higher / lower than the legacy cell.
- **pooled** (sources 1 and 2) and **panel** (source 3): per dialogue, the mean of the per-model effects over the models with both cells, equal weight for each model.
- No correction for multiple comparisons.

## Counts of clear and unclear

| Set | Dialogues | Clear (hotel_only) | Unclear | guesthouse_only | mixed | Strict rule: clear | Strict rule: unclear |
|---|---|---|---|---|---|---|---|
| a_hotel | 59 | 1 | 58 | 0 | 0 | 1 | 58 |
| a_no_type | 448 | 0 | 448 | 0 | 0 | 0 | 448 |
| b_hotel | 233 | 89 | 140 | 3 | 1 | 54 | 179 |
| b_no_type | 807 | 4 | 802 | 1 | 0 | 4 | 802 |
| c_hotel | 77 | 20 | 57 | 0 | 0 | 10 | 67 |
| c_no_type | 213 | 3 | 210 | 0 | 0 | 2 | 211 |

- `a_hotel`: Source 1, tool calls at the first request: prefixes whose brief sets `type` = hotel.
- `a_no_type`: Source 1, tool calls at the first request: prefixes whose brief sets no type.
- `b_hotel`: Source 2, round-9 form runs: S2 full dialogues whose brief sets `type` = hotel.
- `b_no_type`: Source 2, round-9 form runs: S1t full dialogues whose brief sets no type.
- `c_hotel`: Source 3, held-out test stage 1: goal-hotel sample, full dialogues.
- `c_no_type`: Source 3, held-out test stage 1: natural sample (the goal sets no type), full dialogues.

## Summary: correct side, pooled or panel row

| Source | Contrast | Clear: dialogues, effect [95% CI] | Unclear: dialogues, effect [95% CI] | Clear minus unclear [95% CI] | Relative change, clear / unclear |
|---|---|---|---|---|---|
| 1 | t1 vs t0 | 1, +0.0 - | 58, -47.0 [-52.5, -41.5] | - | +0.0% / -83.3% |
| 2 | f1 vs f0 | 89, -21.4 [-26.9, -16.6] | 140, -38.8 [-43.1, -34.5] | +17.4 [+10.8, +24.1] | -23.0% / -62.5% |
| 2 | f6 vs f0 | 89, -5.9 [-9.7, -2.6] | 140, -25.8 [-30.4, -21.2] | +19.9 [+14.0, +25.5] | -6.2% / -44.7% |
| 3 | t_renamed vs t_legacy | 20, -19.4 [-30.1, -9.9] | 57, -32.5 [-39.1, -26.2] | +13.1 [+1.7, +25.3] | -21.3% / -61.8% |

## Source 1: Tool calls at the first request (experiment A, prefixes)

Folders read: sonnet: era1_sonnet, erx_a1_sonnet, erx_a2_sonnet; haiku: era1_haiku; opus: era1_opus, erx_a2_opus; sol: era1_sol, erx_a3_sol; luna: era1_luna; astra: era1_astra.

### t1 against t0, correct values: set `a_hotel`

| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | Sign p | Relative change [95% CI] |
|---|---|---|---|---|---|---|---|---|
| sonnet | clear | 1 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| sonnet | unclear | 58 | 50.6% | 2.9% | -47.7 [-60.3, -36.2] | 0 / 31 | 9.3e-10 | -94.3% [-100.0, -85.1] |
| sonnet | all | 59 | 51.4% | 4.5% | -46.9 [-59.9, -35.0] | 0 / 31 | 9.3e-10 | -91.2% [-100.0, -79.8] |
| haiku | clear | 1 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| haiku | unclear | 57 | 9.6% | 0.9% | -8.8 [-16.7, -2.6] | 0 / 6 | 0.031 | -90.9% - |
| haiku | all | 58 | 11.2% | 2.6% | -8.6 [-16.4, -2.6] | 0 / 6 | 0.031 | -76.9% [-100.0, -40.0] |
| opus | clear | 1 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| opus | unclear | 58 | 70.7% | 19.0% | -51.7 [-62.9, -39.7] | 0 / 35 | 5.8e-11 | -73.2% [-85.4, -60.0] |
| opus | all | 59 | 71.2% | 20.3% | -50.8 [-62.7, -39.0] | 0 / 35 | 5.8e-11 | -71.4% [-83.6, -58.2] |
| sol | clear | 1 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| sol | unclear | 58 | 80.5% | 22.4% | -58.0 [-69.5, -46.0] | 0 / 38 | 7.3e-12 | -72.1% [-83.3, -59.3] |
| sol | all | 59 | 80.8% | 23.7% | -57.1 [-68.4, -45.2] | 0 / 38 | 7.3e-12 | -70.6% [-82.9, -57.1] |
| luna | clear | 1 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| luna | unclear | 58 | 34.5% | 0.0% | -34.5 [-46.6, -23.3] | 0 / 23 | 2.4e-07 | -100.0% [-100.0, -100.0] |
| luna | all | 59 | 35.6% | 1.7% | -33.9 [-46.6, -22.0] | 0 / 23 | 2.4e-07 | -95.2% [-100.0, -83.8] |
| astra | clear | 1 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| astra | unclear | 58 | 91.4% | 10.3% | -81.0 [-91.4, -70.7] | 0 / 47 | 1.4e-14 | -88.7% [-96.3, -79.2] |
| astra | all | 59 | 91.5% | 11.9% | -79.7 [-89.8, -69.5] | 0 / 47 | 1.4e-14 | -87.0% [-96.0, -77.6] |
| pooled | clear | 1 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| pooled | unclear | 58 | 56.5% | 9.4% | -47.0 [-52.5, -41.5] | 0 / 55 | 5.6e-17 | -83.3% [-89.6, -76.5] |
| pooled | all | 59 | 57.2% | 11.0% | -46.3 [-51.8, -40.9] | 0 / 55 | 5.6e-17 | -80.9% [-88.7, -72.7] |

### t1 against t0, unsupported values (for completeness): set `a_no_type`

| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | Sign p | Relative change [95% CI] |
|---|---|---|---|---|---|---|---|---|
| sonnet | clear | 0 | - | - | - | - | - | - |
| sonnet | unclear | 448 | 22.2% | 3.1% | -19.1 [-22.8, -15.6] | 1 / 92 | 1.9e-26 | -86.2% [-92.6, -79.8] |
| sonnet | all | 448 | 22.2% | 3.1% | -19.1 [-22.8, -15.6] | 1 / 92 | 1.9e-26 | -86.2% [-92.6, -79.8] |
| haiku | clear | 0 | - | - | - | - | - | - |
| haiku | unclear | 448 | 7.1% | 1.3% | -5.8 [-7.9, -3.9] | 0 / 32 | 4.7e-10 | -81.2% [-93.8, -67.9] |
| haiku | all | 448 | 7.1% | 1.3% | -5.8 [-7.9, -3.9] | 0 / 32 | 4.7e-10 | -81.2% [-93.8, -67.9] |
| opus | clear | 0 | - | - | - | - | - | - |
| opus | unclear | 448 | 25.9% | 4.0% | -21.9 [-25.7, -18.3] | 1 / 115 | 2.8e-33 | -84.5% [-90.3, -78.3] |
| opus | all | 448 | 25.9% | 4.0% | -21.9 [-25.7, -18.3] | 1 / 115 | 2.8e-33 | -84.5% [-90.3, -78.3] |
| sol | clear | 0 | - | - | - | - | - | - |
| sol | unclear | 448 | 35.6% | 11.7% | -24.0 [-27.8, -20.3] | 0 / 129 | 2.9e-39 | -67.2% [-74.0, -60.2] |
| sol | all | 448 | 35.6% | 11.7% | -24.0 [-27.8, -20.3] | 0 / 129 | 2.9e-39 | -67.2% [-74.0, -60.2] |
| luna | clear | 0 | - | - | - | - | - | - |
| luna | unclear | 448 | 18.8% | 0.6% | -18.2 [-21.7, -14.8] | 0 / 91 | 8.1e-28 | -97.0% [-100.0, -93.2] |
| luna | all | 448 | 18.8% | 0.6% | -18.2 [-21.7, -14.8] | 0 / 91 | 8.1e-28 | -97.0% [-100.0, -93.2] |
| astra | clear | 0 | - | - | - | - | - | - |
| astra | unclear | 448 | 36.4% | 5.4% | -31.0 [-35.3, -27.0] | 0 / 139 | 2.9e-42 | -85.3% [-90.4, -79.6] |
| astra | all | 448 | 36.4% | 5.4% | -31.0 [-35.3, -27.0] | 0 / 139 | 2.9e-42 | -85.3% [-90.4, -79.6] |
| pooled | clear | 0 | - | - | - | - | - | - |
| pooled | unclear | 448 | 24.3% | 4.3% | -20.0 [-22.5, -17.4] | 0 / 192 | 3.2e-58 | -82.2% [-86.1, -78.1] |
| pooled | all | 448 | 24.3% | 4.3% | -20.0 [-22.5, -17.4] | 0 / 192 | 3.2e-58 | -82.2% [-86.1, -78.1] |


## Source 2: Round-9 form runs on full dialogues

### f1 against f0, correct values: set `b_hotel`

| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | Sign p | Relative change [95% CI] |
|---|---|---|---|---|---|---|---|---|
| deepseek | clear | 89 | 80.9% | 60.7% | -20.2 [-31.5, -7.9] | 7 / 25 | 0.002 | -25.0% [-38.2, -10.8] |
| deepseek | unclear | 140 | 55.0% | 20.7% | -34.3 [-42.9, -25.7] | 2 / 50 | 6.1e-13 | -62.3% [-74.0, -50.7] |
| deepseek | all | 233 | 65.7% | 36.9% | -28.8 [-35.6, -21.9] | 9 / 76 | 2.4e-14 | -43.8% [-52.7, -34.7] |
| deepseek | **clear minus unclear** | | | | +14.1 [+0.1, +28.6] | | | +37.3% [+19.7, +55.0] |
| gemma | clear | 89 | 100.0% | 89.9% | -10.1 [-16.9, -4.5] | 0 / 9 | 0.004 | -10.1% [-16.9, -4.5] |
| gemma | unclear | 139 | 76.3% | 22.3% | -54.0 [-62.6, -46.0] | 0 / 75 | 5.3e-23 | -70.8% [-79.8, -62.0] |
| gemma | all | 232 | 85.8% | 49.1% | -36.6 [-42.7, -31.0] | 0 / 85 | 5.2e-26 | -42.7% [-49.5, -35.9] |
| gemma | **clear minus unclear** | | | | +43.8 [+33.4, +54.1] | | | +60.6% [+50.4, +71.2] |
| haiku | clear | 89 | 89.5% | 56.2% | -33.3 [-43.1, -23.6] | 3 / 38 | 1.0e-08 | -37.2% [-47.8, -26.8] |
| haiku | unclear | 140 | 33.3% | 12.6% | -20.7 [-27.4, -14.0] | 1 / 36 | 5.5e-10 | -62.1% [-75.4, -48.9] |
| haiku | all | 233 | 55.9% | 30.2% | -25.8 [-31.2, -20.5] | 4 / 76 | 2.8e-18 | -46.0% [-54.1, -37.6] |
| haiku | **clear minus unclear** | | | | -12.6 [-24.3, -1.1] | | | +24.9% [+7.7, +41.6] |
| luna | clear | 89 | 99.3% | 61.4% | -37.8 [-47.6, -28.5] | 1 / 40 | 3.8e-11 | -38.1% [-47.7, -28.8] |
| luna | unclear | 140 | 66.7% | 16.4% | -50.2 [-57.9, -42.6] | 1 / 85 | 2.2e-24 | -75.4% [-83.0, -66.9] |
| luna | all | 233 | 79.7% | 34.2% | -45.5 [-51.4, -39.5] | 2 / 128 | 1.3e-35 | -57.1% [-63.6, -50.6] |
| luna | **clear minus unclear** | | | | +12.4 [+0.7, +23.8] | | | +37.2% [+25.2, +49.4] |
| qwen | clear | 73 | 83.6% | 47.9% | -35.6 [-49.3, -21.9] | 5 / 31 | 1.3e-05 | -42.6% [-56.5, -28.1] |
| qwen | unclear | 121 | 53.7% | 16.5% | -37.2 [-47.1, -27.3] | 3 / 48 | 2.0e-11 | -69.2% [-81.0, -56.1] |
| qwen | all | 198 | 65.2% | 27.8% | -37.4 [-45.5, -29.3] | 8 / 82 | 1.4e-16 | -57.4% [-66.4, -47.8] |
| qwen | **clear minus unclear** | | | | +1.6 [-14.9, +19.4] | | | +26.6% [+8.0, +45.9] |
| sol | clear | 46 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | +0.0% [+0.0, +0.0] |
| sol | unclear | 57 | 96.5% | 63.2% | -33.3 [-45.6, -21.1] | 0 / 19 | 3.8e-06 | -34.5% [-47.3, -22.2] |
| sol | all | 103 | 98.1% | 79.6% | -18.4 [-27.2, -11.7] | 0 / 19 | 3.8e-06 | -18.8% [-27.2, -11.8] |
| sol | **clear minus unclear** | | | | +33.3 [+21.1, +45.6] | | | +34.5% [+22.2, +47.3] |
| sonnet | clear | 89 | 100.0% | 94.4% | -5.6 [-10.7, -1.7] | 0 / 6 | 0.031 | -5.6% [-10.7, -1.7] |
| sonnet | unclear | 140 | 73.2% | 35.0% | -38.2 [-47.1, -30.4] | 0 / 57 | 1.4e-17 | -52.2% [-62.4, -42.8] |
| sonnet | all | 233 | 83.9% | 58.8% | -25.1 [-30.7, -19.5] | 0 / 63 | 2.2e-19 | -29.9% [-36.2, -23.6] |
| sonnet | **clear minus unclear** | | | | +32.6 [+23.6, +42.1] | | | +46.6% [+36.3, +57.5] |
| pooled | clear | 89 | 93.0% | 71.6% | -21.4 [-26.9, -16.6] | 7 / 59 | 2.4e-11 | -23.0% [-28.8, -18.0] |
| pooled | unclear | 140 | 62.1% | 23.3% | -38.8 [-43.1, -34.5] | 1 / 117 | 7.2e-34 | -62.5% [-69.6, -56.1] |
| pooled | all | 233 | 74.5% | 42.4% | -32.1 [-35.6, -28.5] | 8 / 180 | 1.8e-43 | -43.1% [-48.1, -38.3] |
| pooled | **clear minus unclear** | | | | +17.4 [+10.8, +24.1] | | | +39.5% [+31.3, +48.3] |

### f6 against f0, correct values: set `b_hotel`

| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | Sign p | Relative change [95% CI] |
|---|---|---|---|---|---|---|---|---|
| haiku | clear | 89 | 89.5% | 80.1% | -9.4 [-16.9, -2.2] | 6 / 18 | 0.023 | -10.5% [-18.5, -2.5] |
| haiku | unclear | 140 | 33.3% | 26.7% | -6.7 [-11.4, -2.1] | 4 / 16 | 0.012 | -20.0% [-33.1, -6.8] |
| haiku | all | 233 | 55.9% | 48.4% | -7.6 [-11.6, -3.6] | 10 / 34 | 3.9e-04 | -13.6% [-20.1, -6.5] |
| haiku | **clear minus unclear** | | | | -2.7 [-12.1, +5.8] | | | +9.5% [-6.2, +24.5] |
| luna | clear | 89 | 99.3% | 94.8% | -4.5 [-9.0, -1.1] | 1 / 7 | 0.070 | -4.5% [-9.1, -1.1] |
| luna | unclear | 140 | 66.7% | 32.4% | -34.3 [-41.4, -27.1] | 1 / 58 | 2.1e-16 | -51.4% [-61.2, -41.8] |
| luna | all | 233 | 79.7% | 57.4% | -22.3 [-27.5, -17.5] | 2 / 65 | 3.1e-17 | -28.0% [-34.5, -22.0] |
| luna | **clear minus unclear** | | | | +29.8 [+21.9, +37.9] | | | +46.9% [+36.7, +57.1] |
| sonnet | clear | 89 | 100.0% | 96.1% | -3.9 [-8.4, -0.6] | 0 / 4 | 0.125 | -3.9% [-8.4, -0.6] |
| sonnet | unclear | 140 | 73.2% | 36.8% | -36.4 [-44.3, -28.9] | 0 / 55 | 5.6e-17 | -49.8% [-59.4, -40.3] |
| sonnet | all | 233 | 83.9% | 60.5% | -23.4 [-28.8, -18.5] | 0 / 59 | 3.5e-18 | -27.9% [-34.1, -22.2] |
| sonnet | **clear minus unclear** | | | | +32.5 [+24.3, +41.0] | | | +45.8% [+36.1, +56.2] |
| pooled | clear | 89 | 96.3% | 90.3% | -5.9 [-9.7, -2.6] | 7 / 24 | 0.003 | -6.2% [-10.1, -2.6] |
| pooled | unclear | 140 | 57.7% | 31.9% | -25.8 [-30.4, -21.2] | 2 / 80 | 1.4e-21 | -44.7% [-53.5, -36.1] |
| pooled | all | 233 | 73.2% | 55.4% | -17.8 [-21.4, -14.4] | 9 / 104 | 1.3e-21 | -24.3% [-29.3, -19.7] |
| pooled | **clear minus unclear** | | | | +19.9 [+14.0, +25.5] | | | +38.5% [+29.6, +47.8] |

### f1 against f0, unsupported values (for completeness): set `b_no_type`

| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | Sign p | Relative change [95% CI] |
|---|---|---|---|---|---|---|---|---|
| deepseek | clear | 4 | 25.0% | 25.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| deepseek | unclear | 800 | 11.8% | 1.9% | -9.9 [-12.0, -7.8] | 3 / 82 | 5.3e-21 | -84.0% [-91.2, -76.4] |
| deepseek | all | 805 | 11.8% | 2.0% | -9.8 [-12.0, -7.7] | 3 / 82 | 5.3e-21 | -83.2% [-90.6, -74.8] |
| gemma | clear | 4 | 100.0% | 25.0% | -75.0 - | 0 / 3 | 0.250 | -75.0% - |
| gemma | unclear | 798 | 18.7% | 1.1% | -17.5 [-20.3, -14.9] | 0 / 140 | 1.4e-42 | -94.0% [-97.6, -89.7] |
| gemma | all | 803 | 19.1% | 1.2% | -17.8 [-20.7, -15.2] | 0 / 143 | 1.8e-43 | -93.5% [-97.0, -89.4] |
| haiku | clear | 4 | 25.0% | 0.0% | -25.0 - | 0 / 1 | 1.000 | -100.0% - |
| haiku | unclear | 802 | 3.0% | 0.6% | -2.5 [-3.5, -1.5] | 0 / 27 | 1.5e-08 | -80.8% [-95.5, -65.6] |
| haiku | all | 807 | 3.1% | 0.6% | -2.6 [-3.6, -1.6] | 0 / 28 | 7.5e-09 | -81.6% [-95.5, -65.9] |
| luna | clear | 4 | 50.0% | 0.0% | -50.0 - | 0 / 3 | 0.250 | -100.0% - |
| luna | unclear | 802 | 17.6% | 0.9% | -16.7 [-19.2, -14.4] | 0 / 169 | 2.7e-51 | -94.8% [-98.1, -91.3] |
| luna | all | 807 | 17.8% | 0.9% | -16.9 [-19.4, -14.5] | 0 / 172 | 3.3e-52 | -94.9% [-98.1, -91.3] |
| qwen | clear | 4 | 25.0% | 25.0% | +0.0 - | 1 / 1 | 1.000 | +0.0% - |
| qwen | unclear | 720 | 10.1% | 1.9% | -8.2 [-10.6, -6.1] | 8 / 67 | 1.0e-12 | -80.8% [-90.4, -69.6] |
| qwen | all | 725 | 10.2% | 2.1% | -8.1 [-10.5, -5.9] | 9 / 68 | 2.4e-12 | -79.7% [-89.2, -68.2] |
| sol | clear | 4 | 100.0% | 75.0% | -25.0 - | 0 / 1 | 1.000 | -25.0% - |
| sol | unclear | 800 | 33.2% | 10.1% | -23.1 [-26.0, -20.2] | 0 / 185 | 4.1e-56 | -69.5% [-75.2, -64.2] |
| sol | all | 805 | 33.5% | 10.4% | -23.1 [-26.0, -20.2] | 0 / 186 | 2.0e-56 | -68.9% [-74.3, -63.2] |
| sonnet | clear | 4 | 50.0% | 25.0% | -25.0 - | 0 / 1 | 1.000 | -50.0% - |
| sonnet | unclear | 802 | 13.8% | 2.9% | -11.0 [-13.1, -8.9] | 1 / 100 | 8.0e-29 | -79.3% [-86.8, -71.6] |
| sonnet | all | 807 | 14.0% | 3.0% | -11.0 [-13.3, -9.0] | 1 / 101 | 4.1e-29 | -78.8% [-85.9, -71.3] |
| pooled | clear | 4 | 53.6% | 25.0% | -28.6 - | 1 / 3 | 0.625 | -53.3% - |
| pooled | unclear | 802 | 15.8% | 2.8% | -13.0 [-14.6, -11.6] | 3 / 297 | 4.4e-84 | -82.0% [-85.7, -78.1] |
| pooled | all | 807 | 16.0% | 3.0% | -13.0 [-14.5, -11.6] | 4 / 300 | 2.2e-83 | -81.5% [-85.1, -77.8] |

### f6 against f0, unsupported values (for completeness): set `b_no_type`

| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | Sign p | Relative change [95% CI] |
|---|---|---|---|---|---|---|---|---|
| deepseek | clear | 4 | 25.0% | 25.0% | +0.0 - | 1 / 1 | 1.000 | +0.0% - |
| deepseek | unclear | 801 | 11.7% | 4.2% | -7.5 [-9.7, -5.4] | 11 / 71 | 6.8e-12 | -63.8% [-74.7, -51.2] |
| deepseek | all | 806 | 11.8% | 4.3% | -7.4 [-9.8, -5.3] | 12 / 72 | 1.4e-11 | -63.2% [-74.1, -50.5] |
| gemma | clear | 3 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| gemma | unclear | 796 | 18.6% | 1.8% | -16.8 [-19.6, -14.3] | 0 / 134 | 9.2e-41 | -90.5% [-95.0, -85.7] |
| gemma | all | 800 | 18.9% | 2.1% | -16.8 [-19.5, -14.1] | 0 / 134 | 9.2e-41 | -88.7% [-93.4, -83.6] |
| haiku | clear | 4 | 25.0% | 16.7% | -8.3 - | 1 / 1 | 1.000 | -33.3% - |
| haiku | unclear | 802 | 3.0% | 2.2% | -0.8 [-1.7, -0.1] | 6 / 19 | 0.015 | -27.4% [-49.4, -3.3] |
| haiku | all | 807 | 3.1% | 2.3% | -0.9 [-1.7, -0.0] | 7 / 20 | 0.019 | -27.6% [-50.0, -1.8] |
| luna | clear | 4 | 50.0% | 16.7% | -33.3 - | 1 / 3 | 0.625 | -66.7% - |
| luna | unclear | 802 | 17.6% | 2.7% | -15.0 [-17.4, -12.8] | 4 / 159 | 5.0e-42 | -84.9% [-90.0, -79.6] |
| luna | all | 807 | 17.8% | 2.7% | -15.0 [-17.4, -12.8] | 5 / 162 | 1.1e-41 | -84.7% [-90.0, -79.0] |
| qwen | clear | 4 | 25.0% | 0.0% | -25.0 - | 0 / 1 | 1.000 | -100.0% - |
| qwen | unclear | 718 | 10.2% | 5.0% | -5.2 [-7.8, -2.6] | 24 / 61 | 7.4e-05 | -50.7% [-66.3, -31.6] |
| qwen | all | 723 | 10.2% | 5.0% | -5.3 [-7.9, -2.8] | 24 / 62 | 5.1e-05 | -51.4% [-67.7, -31.9] |
| sol | clear | 4 | 100.0% | 75.0% | -25.0 - | 0 / 1 | 1.000 | -25.0% - |
| sol | unclear | 800 | 33.2% | 27.4% | -5.9 [-7.6, -4.1] | 3 / 50 | 5.5e-12 | -17.7% [-22.6, -12.6] |
| sol | all | 805 | 33.5% | 27.6% | -6.0 [-7.8, -4.3] | 3 / 51 | 2.9e-12 | -17.8% [-22.8, -13.2] |
| sonnet | clear | 4 | 50.0% | 16.7% | -33.3 - | 0 / 2 | 0.500 | -66.7% - |
| sonnet | unclear | 802 | 13.8% | 2.3% | -11.5 [-13.7, -9.4] | 0 / 106 | 2.5e-32 | -83.2% [-89.6, -76.5] |
| sonnet | all | 807 | 14.0% | 2.4% | -11.6 [-13.8, -9.5] | 0 / 108 | 6.2e-33 | -82.9% [-89.4, -75.9] |
| pooled | clear | 4 | 52.2% | 32.1% | -20.0 - | 1 / 2 | 1.000 | -38.4% - |
| pooled | unclear | 802 | 15.8% | 6.7% | -9.1 [-10.5, -7.9] | 20 / 248 | 3.3e-51 | -57.8% [-61.6, -53.9] |
| pooled | all | 807 | 16.0% | 6.8% | -9.2 [-10.6, -8.0] | 21 / 250 | 6.3e-51 | -57.5% [-61.5, -53.5] |


## Source 3: Held-out test, stage 1 (post hoc look at opened answers)

Post hoc look at the opened stage-1 answers (read 1), through `main/exp0/analysis.load`. Rows per model: sonnet 3103, haiku 3103, sol 2804, luna 2804, deepseek 2804, qwen 2804, gemma 2804.

### t_renamed against t_legacy, correct values: set `c_hotel`

| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | Sign p | Relative change [95% CI] |
|---|---|---|---|---|---|---|---|---|
| sonnet | clear | 20 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | +0.0% [+0.0, +0.0] |
| sonnet | unclear | 57 | 56.1% | 29.8% | -26.3 [-38.6, -15.8] | 0 / 15 | 6.1e-05 | -46.9% [-64.0, -29.0] |
| sonnet | all | 77 | 64.9% | 45.5% | -19.5 [-28.6, -10.4] | 0 / 15 | 6.1e-05 | -30.0% [-43.6, -17.4] |
| sonnet | **clear minus unclear** | | | | +26.3 [+15.8, +38.6] | | | +46.9% [+29.4, +64.0] |
| haiku | clear | 20 | 90.0% | 65.0% | -25.0 [-45.0, -5.0] | 0 / 5 | 0.062 | -27.8% [-50.0, -6.2] |
| haiku | unclear | 57 | 33.3% | 10.5% | -22.8 [-33.3, -12.3] | 0 / 13 | 2.4e-04 | -68.4% [-88.2, -46.2] |
| haiku | all | 77 | 48.1% | 24.7% | -23.4 [-32.5, -14.3] | 0 / 18 | 7.6e-06 | -48.6% [-65.0, -32.5] |
| haiku | **clear minus unclear** | | | | -2.2 [-23.9, +19.8] | | | +40.6% [+10.8, +69.7] |
| sol | clear | 20 | 95.0% | 90.0% | -5.0 [-15.0, +0.0] | 0 / 1 | 1.000 | -5.3% [-16.7, +0.0] |
| sol | unclear | 57 | 80.7% | 47.4% | -33.3 [-45.6, -21.1] | 0 / 19 | 3.8e-06 | -41.3% [-55.6, -27.1] |
| sol | all | 77 | 84.4% | 58.4% | -26.0 [-36.4, -16.9] | 0 / 20 | 1.9e-06 | -30.8% [-43.1, -20.0] |
| sol | **clear minus unclear** | | | | +28.3 [+11.3, +42.4] | | | +36.0% [+16.4, +52.9] |
| luna | clear | 20 | 100.0% | 45.0% | -55.0 [-75.0, -30.0] | 0 / 11 | 9.8e-04 | -55.0% [-75.0, -30.0] |
| luna | unclear | 57 | 57.9% | 0.0% | -57.9 [-71.9, -45.6] | 0 / 33 | 2.3e-10 | -100.0% [-100.0, -100.0] |
| luna | all | 77 | 68.8% | 11.7% | -57.1 [-67.5, -46.8] | 0 / 44 | 1.1e-13 | -83.0% [-92.6, -72.5] |
| luna | **clear minus unclear** | | | | +2.9 [-20.6, +28.4] | | | +45.0% [+25.0, +65.0] |
| deepseek | clear | 20 | 85.0% | 70.0% | -15.0 [-35.0, +5.0] | 1 / 4 | 0.375 | -17.6% [-41.2, +6.7] |
| deepseek | unclear | 57 | 36.8% | 14.0% | -22.8 [-35.1, -12.3] | 0 / 13 | 2.4e-04 | -61.9% [-82.4, -40.0] |
| deepseek | all | 77 | 49.4% | 28.6% | -20.8 [-31.2, -11.7] | 1 / 17 | 1.4e-04 | -42.1% [-58.3, -25.0] |
| deepseek | **clear minus unclear** | | | | +7.8 [-17.2, +31.1] | | | +44.3% [+11.0, +76.7] |
| qwen | clear | 15 | 80.0% | 53.3% | -26.7 [-60.0, +6.7] | 2 / 6 | 0.289 | -33.3% [-69.2, +11.1] |
| qwen | unclear | 45 | 40.0% | 17.8% | -22.2 [-37.8, -8.9] | 2 / 12 | 0.013 | -55.6% [-78.9, -25.0] |
| qwen | all | 60 | 50.0% | 26.7% | -23.3 [-36.7, -10.0] | 4 / 18 | 0.004 | -46.7% [-67.7, -22.2] |
| qwen | **clear minus unclear** | | | | -4.4 [-42.2, +33.3] | | | +22.2% [-23.7, +76.9] |
| gemma | clear | 20 | 95.0% | 85.0% | -10.0 [-25.0, +0.0] | 0 / 2 | 0.500 | -10.5% [-26.3, +0.0] |
| gemma | unclear | 57 | 61.4% | 19.3% | -42.1 [-56.1, -29.8] | 0 / 24 | 1.2e-07 | -68.6% [-83.3, -52.8] |
| gemma | all | 77 | 70.1% | 36.4% | -33.8 [-45.5, -23.4] | 0 / 26 | 3.0e-08 | -48.1% [-62.0, -34.6] |
| gemma | **clear minus unclear** | | | | +32.1 [+13.3, +49.4] | | | +58.0% [+36.5, +77.6] |
| panel | clear | 20 | 91.2% | 71.8% | -19.4 [-30.1, -9.9] | 2 / 13 | 0.007 | -21.3% [-33.1, -10.8] |
| panel | unclear | 57 | 52.7% | 20.1% | -32.5 [-39.1, -26.2] | 1 / 47 | 3.5e-13 | -61.8% [-70.4, -52.6] |
| panel | all | 77 | 62.7% | 33.5% | -29.1 [-35.1, -23.9] | 3 / 60 | 9.0e-15 | -46.5% [-55.6, -38.5] |
| panel | **clear minus unclear** | | | | +13.1 [+1.7, +25.3] | | | +40.5% [+26.7, +54.8] |

### t_renamed against t_legacy, unsupported values (for completeness): set `c_no_type`

| Model | Group | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Higher / lower | Sign p | Relative change [95% CI] |
|---|---|---|---|---|---|---|---|---|
| sonnet | clear | 3 | 66.7% | 33.3% | -33.3 - | 0 / 1 | 1.000 | -50.0% - |
| sonnet | unclear | 210 | 14.3% | 2.9% | -11.4 [-16.2, -7.1] | 0 / 24 | 1.2e-07 | -80.0% [-93.9, -63.2] |
| sonnet | all | 213 | 15.0% | 3.3% | -11.7 [-16.4, -8.0] | 0 / 25 | 6.0e-08 | -78.1% [-92.0, -62.9] |
| haiku | clear | 3 | 66.7% | 0.0% | -66.7 - | 0 / 2 | 0.500 | -100.0% - |
| haiku | unclear | 210 | 4.8% | 1.0% | -3.8 [-6.7, -1.4] | 0 / 8 | 0.008 | -80.0% [-100.0, -50.0] |
| haiku | all | 213 | 5.6% | 0.9% | -4.7 [-7.5, -1.9] | 0 / 10 | 0.002 | -83.3% [-100.0, -58.8] |
| sol | clear | 3 | 66.7% | 66.7% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| sol | unclear | 210 | 31.4% | 13.8% | -17.6 [-22.9, -12.9] | 0 / 37 | 1.5e-11 | -56.1% [-68.1, -44.3] |
| sol | all | 213 | 31.9% | 14.6% | -17.4 [-23.0, -12.7] | 0 / 37 | 1.5e-11 | -54.4% [-66.7, -42.4] |
| luna | clear | 3 | 66.7% | 0.0% | -66.7 - | 0 / 2 | 0.500 | -100.0% - |
| luna | unclear | 210 | 18.1% | 1.4% | -16.7 [-21.9, -11.9] | 0 / 35 | 5.8e-11 | -92.1% [-100.0, -82.4] |
| luna | all | 213 | 18.8% | 1.4% | -17.4 [-23.0, -12.7] | 0 / 37 | 1.5e-11 | -92.5% [-100.0, -83.3] |
| deepseek | clear | 3 | 33.3% | 33.3% | +0.0 - | 1 / 1 | 1.000 | +0.0% - |
| deepseek | unclear | 210 | 15.2% | 3.3% | -11.9 [-16.2, -7.6] | 0 / 25 | 6.0e-08 | -78.1% [-92.0, -63.3] |
| deepseek | all | 213 | 15.5% | 3.8% | -11.7 [-16.4, -7.5] | 1 / 26 | 4.2e-07 | -75.8% [-90.3, -59.4] |
| qwen | clear | 3 | 33.3% | 66.7% | +33.3 - | 1 / 0 | 1.000 | +100.0% - |
| qwen | unclear | 184 | 9.8% | 1.6% | -8.2 [-12.5, -4.3] | 1 / 16 | 2.7e-04 | -83.3% [-100.0, -61.1] |
| qwen | all | 187 | 10.2% | 2.7% | -7.5 [-12.3, -3.2] | 2 / 16 | 0.001 | -73.7% [-94.1, -46.7] |
| gemma | clear | 3 | 100.0% | 100.0% | +0.0 - | 0 / 0 | 1.000 | +0.0% - |
| gemma | unclear | 209 | 20.6% | 2.4% | -18.2 [-23.4, -12.9] | 0 / 38 | 7.3e-12 | -88.4% [-97.4, -77.8] |
| gemma | all | 212 | 21.7% | 3.8% | -17.9 [-23.6, -13.2] | 0 / 38 | 7.3e-12 | -82.6% [-93.2, -70.8] |
| panel | clear | 3 | 61.9% | 42.9% | -19.0 - | 0 / 2 | 0.500 | -30.8% - |
| panel | unclear | 210 | 16.8% | 3.9% | -12.9 [-16.0, -9.9] | 0 / 73 | 2.1e-22 | -76.6% [-83.9, -68.6] |
| panel | all | 213 | 17.4% | 4.5% | -13.0 [-16.0, -10.1] | 0 / 75 | 5.3e-23 | -74.3% [-81.7, -66.7] |

## Secondary: the strict rule (families E and R only)

Correct side. Same statistics; the clear group has fewer dialogues.

| Source | Contrast | Model | Clear: dialogues, effect [95% CI] | Unclear: dialogues, effect [95% CI] | Clear minus unclear [95% CI] |
|---|---|---|---|---|---|
| 1 | t1 vs t0 | sonnet | 1, +0.0 - | 58, -47.7 [-60.3, -36.2] | - |
| 1 | t1 vs t0 | haiku | 1, +0.0 - | 57, -8.8 [-16.7, -2.6] | - |
| 1 | t1 vs t0 | opus | 1, +0.0 - | 58, -51.7 [-62.9, -39.7] | - |
| 1 | t1 vs t0 | sol | 1, +0.0 - | 58, -58.0 [-69.5, -46.0] | - |
| 1 | t1 vs t0 | luna | 1, +0.0 - | 58, -34.5 [-46.6, -23.3] | - |
| 1 | t1 vs t0 | astra | 1, +0.0 - | 58, -81.0 [-91.4, -70.7] | - |
| 1 | t1 vs t0 | pooled | 1, +0.0 - | 58, -47.0 [-52.5, -41.5] | - |
| 2 | f1 vs f0 | deepseek | 54, -5.6 [-18.5, +7.4] | 179, -35.8 [-43.6, -27.9] | +30.2 [+14.4, +45.0] |
| 2 | f1 vs f0 | gemma | 54, +0.0 [+0.0, +0.0] | 178, -47.8 [-55.1, -40.4] | +47.8 [+40.4, +55.1] |
| 2 | f1 vs f0 | haiku | 54, -12.3 [-21.6, -2.5] | 179, -29.8 [-35.9, -23.3] | +17.4 [+6.0, +28.2] |
| 2 | f1 vs f0 | luna | 54, -12.3 [-21.6, -4.3] | 179, -55.5 [-61.8, -48.6] | +43.1 [+32.5, +53.0] |
| 2 | f1 vs f0 | qwen | 42, -14.3 [-31.0, +2.4] | 156, -43.6 [-51.9, -34.6] | +29.3 [+9.8, +47.6] |
| 2 | f1 vs f0 | sol | 27, +0.0 [+0.0, +0.0] | 76, -25.0 [-35.5, -15.8] | +25.0 [+15.8, +34.2] |
| 2 | f1 vs f0 | sonnet | 54, +0.0 [+0.0, +0.0] | 179, -32.7 [-39.7, -26.0] | +32.7 [+26.3, +39.7] |
| 2 | f1 vs f0 | pooled | 54, -6.8 [-11.1, -2.6] | 179, -39.7 [-43.4, -36.0] | +32.9 [+27.4, +38.4] |
| 2 | f6 vs f0 | haiku | 54, +3.1 [-3.1, +10.5] | 179, -10.8 [-15.5, -6.1] | +13.9 [+5.9, +21.9] |
| 2 | f6 vs f0 | luna | 54, +0.6 [+0.0, +1.9] | 179, -29.2 [-35.8, -23.1] | +29.9 [+23.7, +36.2] |
| 2 | f6 vs f0 | sonnet | 54, +0.0 [+0.0, +0.0] | 179, -30.4 [-37.4, -24.0] | +30.4 [+24.3, +37.4] |
| 2 | f6 vs f0 | pooled | 54, +1.2 [-0.8, +3.7] | 179, -23.5 [-27.7, -19.5] | +24.7 [+20.4, +29.3] |
| 3 | t_renamed vs t_legacy | sonnet | 10, +0.0 [+0.0, +0.0] | 67, -22.4 [-32.8, -13.4] | +22.4 [+13.4, +32.8] |
| 3 | t_renamed vs t_legacy | haiku | 10, +0.0 [+0.0, +0.0] | 67, -26.9 [-37.3, -16.4] | +26.9 [+16.4, +37.3] |
| 3 | t_renamed vs t_legacy | sol | 10, +0.0 [+0.0, +0.0] | 67, -29.9 [-40.3, -19.4] | +29.9 [+19.4, +41.8] |
| 3 | t_renamed vs t_legacy | luna | 10, -30.0 [-60.0, +0.0] | 67, -61.2 [-73.1, -49.3] | +31.2 [-0.3, +60.1] |
| 3 | t_renamed vs t_legacy | deepseek | 10, +0.0 [-30.0, +30.0] | 67, -23.9 [-35.8, -14.9] | +23.9 [-4.6, +54.3] |
| 3 | t_renamed vs t_legacy | qwen | 7, +0.0 [-57.1, +57.1] | 53, -26.4 [-39.6, -11.3] | +26.4 [-30.7, +82.5] |
| 3 | t_renamed vs t_legacy | gemma | 10, +0.0 [+0.0, +0.0] | 67, -38.8 [-50.7, -28.4] | +38.8 [+28.4, +50.7] |
| 3 | t_renamed vs t_legacy | panel | 10, -4.5 [-13.1, +2.9] | 67, -32.8 [-38.9, -26.9] | +28.3 [+18.1, +37.9] |

## Derived after the first run: clear only by a P or T pattern (not pre-declared)

These dialogues are clear by the main rule and unclear by the strict rule. They state the type only with a predicate or type word ("it should be a hotel", "a hotel type") and exclude nothing. This breakdown was added after the first run of this script showed a gap between the main and strict clear groups. It is a difference of the two fixed rules, not a new rule.

| Source | Contrast | Model | Dialogues | Legacy share | Renamed share | Effect, points [95% CI] | Sign p |
|---|---|---|---|---|---|---|---|
| 2 | f1 vs f0 | deepseek | 36 | 75.0% | 33.3% | -41.7 [-61.1, -22.2] | 7.3e-04 |
| 2 | f1 vs f0 | gemma | 36 | 100.0% | 75.0% | -25.0 [-38.9, -11.1] | 0.004 |
| 2 | f1 vs f0 | haiku | 36 | 86.1% | 22.2% | -63.9 [-77.8, -49.1] | 4.2e-07 |
| 2 | f1 vs f0 | luna | 36 | 99.1% | 24.1% | -75.0 [-86.1, -62.0] | 9.3e-10 |
| 2 | f1 vs f0 | qwen | 32 | 81.2% | 15.6% | -65.6 [-84.4, -43.8] | 5.7e-06 |
| 2 | f1 vs f0 | sol | 19 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 1.000 |
| 2 | f1 vs f0 | sonnet | 36 | 100.0% | 86.1% | -13.9 [-25.0, -4.2] | 0.031 |
| 2 | f1 vs f0 | pooled | 36 | 91.1% | 47.9% | -43.2 [-49.3, -37.1] | 5.8e-11 |
| 2 | f6 vs f0 | haiku | 36 | 86.1% | 58.3% | -27.8 [-40.7, -14.8] | 9.8e-04 |
| 2 | f6 vs f0 | luna | 36 | 99.1% | 87.0% | -12.0 [-22.2, -3.7] | 0.016 |
| 2 | f6 vs f0 | sonnet | 36 | 100.0% | 90.3% | -9.7 [-19.4, -1.4] | 0.125 |
| 2 | f6 vs f0 | pooled | 36 | 95.1% | 78.5% | -16.5 [-22.5, -10.3] | 2.1e-05 |
| 3 | t_renamed vs t_legacy | sonnet | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 1.000 |
| 3 | t_renamed vs t_legacy | haiku | 10 | 90.0% | 40.0% | -50.0 [-80.0, -20.0] | 0.062 |
| 3 | t_renamed vs t_legacy | sol | 10 | 100.0% | 90.0% | -10.0 [-30.0, +0.0] | 1.000 |
| 3 | t_renamed vs t_legacy | luna | 10 | 100.0% | 20.0% | -80.0 [-100.0, -50.0] | 0.008 |
| 3 | t_renamed vs t_legacy | deepseek | 10 | 90.0% | 60.0% | -30.0 [-60.0, +0.0] | 0.250 |
| 3 | t_renamed vs t_legacy | qwen | 8 | 87.5% | 37.5% | -50.0 [-87.5, -12.5] | 0.125 |
| 3 | t_renamed vs t_legacy | gemma | 10 | 100.0% | 80.0% | -20.0 [-50.0, +0.0] | 0.500 |
| 3 | t_renamed vs t_legacy | panel | 10 | 93.8% | 59.5% | -34.3 [-46.7, -21.4] | 0.004 |

## Checks

Source 3, all dialogues, panel mean of `t_renamed` minus `t_legacy` (read 1): correct_values_kept -29.1 points, wrong_values -13.0 points. RESULT-STAGE1.md reports wrong_values -13.0 and correct_values_kept -29.1.

