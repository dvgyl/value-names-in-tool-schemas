# Release tests of harmless updates (R10-20)

Exploratory, fixed in the protocol before the run. Change = update − control, in points. L = 5. One look with all requests. Levels: tool channel 98.75% (C = 4), form channel 99.17% (C = 6). First rule: the R10-6 code. Revised rule: Appendix I with the exact sign condition (post hoc in the paper).

## Decisions

| Model | Update | Set | Pairs | Change | Interval | Up / down | Sign p | First rule | Revised rule |
|---|---|---|---:|---:|---|---|---:|---|---|
| sol | (a) unchanged (repeat) | open | 448 | -0.7 | [-2.5, +0.9] | 3 / 6 | 0.5078 | absent | within limits |
| sol | (a) unchanged (repeat) | specific | 59 | +0.0 | [-1.7, +1.9] | 5 / 5 | 1.0000 | absent | within limits |
| sol | (a) unchanged (repeat) | **model** | | | | | | **pass** | **pass** |
| sol | (b) paraphrase | open | 448 | -0.4 | [-2.5, +1.3] | 5 / 7 | 0.7744 | absent | within limits |
| sol | (b) paraphrase | specific | 59 | -0.2 | [-2.5, +2.4] | 6 / 7 | 1.0000 | absent | within limits |
| sol | (b) paraphrase | **model** | | | | | | **pass** | **pass** |
| sol | (c) rename | open | 448 | -22.5 | [-27.9, -17.9] | 0 / 101 | 0.0000 | flag-worthy | meets flag rule |
| sol | (c) rename | specific | 59 | -62.0 | [-74.6, -48.6] | 0 / 46 | 0.0000 | flag-worthy | meets flag rule |
| sol | (c) rename | **model** | | | | | | **flag** | **flag** |
| luna | (a) unchanged (repeat) | open | 448 | -2.2 | [-4.7, +0.0] | 3 / 13 | 0.0213 | absent | within limits |
| luna | (a) unchanged (repeat) | specific | 59 | +0.5 | [-2.4, +3.7] | 5 / 7 | 0.7744 | absent | within limits |
| luna | (a) unchanged (repeat) | **model** | | | | | | **pass** | **pass** |
| luna | (b) paraphrase | open | 448 | -3.1 | [-5.8, -0.7] | 4 / 18 | 0.0043 | unresolved | unresolved |
| luna | (b) paraphrase | specific | 59 | +2.0 | [-3.9, +8.0] | 8 / 6 | 0.7905 | unresolved | unresolved |
| luna | (b) paraphrase | **model** | | | | | | **hold** | **hold** |
| luna | (c) rename | open | 448 | -18.8 | [-23.4, -14.3] | 0 / 84 | 0.0000 | flag-worthy | meets flag rule |
| luna | (c) rename | specific | 59 | -33.7 | [-49.8, -20.0] | 0 / 27 | 0.0000 | flag-worthy | meets flag rule |
| luna | (c) rename | **model** | | | | | | **flag** | **flag** |
| deepseek | (a) unchanged (repeat) | open | 447 | +2.0 | [-1.1, +5.4] | 20 / 11 | 0.1496 | unresolved | unresolved |
| deepseek | (a) unchanged (repeat) | specific | 59 | +3.4 | [-0.5, +7.6] | 18 / 5 | 0.0106 | unresolved | unresolved |
| deepseek | (a) unchanged (repeat) | **model** | | | | | | **hold** | **hold** |
| deepseek | (b) paraphrase | open | 447 | +1.1 | [-2.5, +4.5] | 20 / 15 | 0.4996 | absent | within limits |
| deepseek | (b) paraphrase | specific | 59 | +5.9 | [+1.5, +10.7] | 21 / 5 | 0.0025 | flag-worthy | meets flag rule |
| deepseek | (b) paraphrase | **model** | | | | | | **flag** | **flag** |
| deepseek | (c) rename | open | 448 | -15.2 | [-20.1, -10.7] | 0 / 68 | 0.0000 | flag-worthy | meets flag rule |
| deepseek | (c) rename | specific | 59 | -30.0 | [-43.9, -17.1] | 0 / 28 | 0.0000 | flag-worthy | meets flag rule |
| deepseek | (c) rename | **model** | | | | | | **flag** | **flag** |
| qwen | (a) unchanged (repeat) | open | 418 | +0.5 | [-3.3, +3.8] | 16 / 14 | 0.8555 | absent | within limits |
| qwen | (a) unchanged (repeat) | specific | 59 | -0.7 | [-7.1, +4.7] | 15 / 17 | 0.8601 | unresolved | unresolved |
| qwen | (a) unchanged (repeat) | **model** | | | | | | **hold** | **hold** |
| qwen | (b) paraphrase | open | 413 | +0.2 | [-3.1, +3.6] | 15 / 14 | 1.0000 | absent | within limits |
| qwen | (b) paraphrase | specific | 59 | +0.6 | [-5.9, +6.8] | 18 / 11 | 0.2649 | unresolved | unresolved |
| qwen | (b) paraphrase | **model** | | | | | | **hold** | **hold** |
| qwen | (c) rename | open | 413 | -12.3 | [-17.2, -8.2] | 3 / 54 | 0.0000 | flag-worthy | meets flag rule |
| qwen | (c) rename | specific | 59 | -30.1 | [-42.5, -18.2] | 0 / 33 | 0.0000 | flag-worthy | meets flag rule |
| qwen | (c) rename | **model** | | | | | | **flag** | **flag** |
| gemma | (a) unchanged (repeat) | open | 444 | +0.0 | [-1.6, +1.4] | 3 / 3 | 1.0000 | absent | within limits |
| gemma | (a) unchanged (repeat) | specific | 59 | +2.0 | [-0.0, +4.7] | 7 / 1 | 0.0703 | absent | within limits |
| gemma | (a) unchanged (repeat) | **model** | | | | | | **pass** | **pass** |
| gemma | (b) paraphrase | open | 443 | +0.7 | [-1.4, +2.7] | 7 / 4 | 0.5488 | absent | within limits |
| gemma | (b) paraphrase | specific | 59 | +1.7 | [-4.7, +7.6] | 5 / 3 | 0.7266 | unresolved | unresolved |
| gemma | (b) paraphrase | **model** | | | | | | **hold** | **hold** |
| gemma | (c) rename | open | 444 | -20.5 | [-25.7, -15.8] | 0 / 91 | 0.0000 | flag-worthy | meets flag rule |
| gemma | (c) rename | specific | 59 | -49.7 | [-66.4, -33.6] | 0 / 32 | 0.0000 | flag-worthy | meets flag rule |
| gemma | (c) rename | **model** | | | | | | **flag** | **flag** |

## Description: form-channel decisions at 98.75% (the level of Table 4)

| Model | Update | First rule | Revised rule |
|---|---|---|---|
| deepseek | (a) | hold | hold |
| deepseek | (b) | flag | flag |
| deepseek | (c) | flag | flag |
| qwen | (a) | hold | hold |
| qwen | (b) | hold | hold |
| qwen | (c) | flag | flag |
| gemma | (a) | pass | pass |
| gemma | (b) | hold | hold |
| gemma | (c) | flag | flag |

## Descriptions: rates of a hotel value (valid reads), the guesthouse set, trade, blocking

| Model | Update | Set | Control | Update | Guesthouse-set change |
|---|---|---|---|---|---|
| sol | (a) | open | 36.2% (162/448) | 35.5% (159/448) |  |
| sol | (a) | specific | 84.4% (498/590) | 84.4% (498/590) |  |
| sol | (a) | guesthouse | 76.6% (36/47) | 74.5% (35/47) | -2.1 |
| sol | (b) | open | 36.2% (162/448) | 35.7% (160/448) |  |
| sol | (b) | specific | 84.4% (498/590) | 84.2% (497/590) |  |
| sol | (b) | guesthouse | 76.6% (36/47) | 76.6% (36/47) | +0.0 |
| sol | (c) | open | 36.2% (162/448) | 13.6% (61/448) |  |
| sol | (c) | specific | 84.4% (498/590) | 22.4% (132/590) |  |
| sol | (c) | guesthouse | 76.6% (36/47) | 34.0% (16/47) | -42.6 |
| luna | (a) | open | 20.1% (90/448) | 17.9% (80/448) |  |
| luna | (a) | specific | 35.4% (209/590) | 35.9% (212/590) |  |
| luna | (a) | guesthouse | 46.8% (22/47) | 48.9% (23/47) | +2.1 |
| luna | (b) | open | 20.1% (90/448) | 17.0% (76/448) |  |
| luna | (b) | specific | 35.4% (209/590) | 37.5% (221/590) |  |
| luna | (b) | guesthouse | 46.8% (22/47) | 40.4% (19/47) | -6.4 |
| luna | (c) | open | 20.1% (90/448) | 1.3% (6/448) |  |
| luna | (c) | specific | 35.4% (209/590) | 1.7% (10/590) |  |
| luna | (c) | guesthouse | 46.8% (22/47) | 10.6% (5/47) | -36.2 |
| deepseek | (a) | open | 17.4% (78/448) | 19.2% (86/447) |  |
| deepseek | (a) | specific | 32.1% (189/589) | 35.6% (210/590) |  |
| deepseek | (a) | guesthouse | 54.3% (25/46) | 48.9% (23/47) | -6.5 |
| deepseek | (b) | open | 17.4% (78/448) | 18.6% (83/447) |  |
| deepseek | (b) | specific | 32.1% (189/589) | 38.1% (225/590) |  |
| deepseek | (b) | guesthouse | 54.3% (25/46) | 46.8% (22/47) | -8.7 |
| deepseek | (c) | open | 17.4% (78/448) | 2.2% (10/448) |  |
| deepseek | (c) | specific | 32.1% (189/589) | 2.2% (13/590) |  |
| deepseek | (c) | guesthouse | 54.3% (25/46) | 6.4% (3/47) | -47.8 |
| qwen | (a) | open | 15.2% (66/434) | 15.8% (68/430) |  |
| qwen | (a) | specific | 31.2% (174/558) | 30.2% (166/549) |  |
| qwen | (a) | guesthouse | 40.9% (18/44) | 38.5% (15/39) | +8.3 |
| qwen | (b) | open | 15.2% (66/434) | 14.7% (62/423) |  |
| qwen | (b) | specific | 31.2% (174/558) | 32.2% (181/562) |  |
| qwen | (b) | guesthouse | 40.9% (18/44) | 34.9% (15/43) | -5.0 |
| qwen | (c) | open | 15.2% (66/434) | 1.9% (8/424) |  |
| qwen | (c) | specific | 31.2% (174/558) | 2.4% (13/553) |  |
| qwen | (c) | guesthouse | 40.9% (18/44) | 7.0% (3/43) | -34.1 |
| gemma | (a) | open | 22.3% (99/444) | 22.8% (102/448) |  |
| gemma | (a) | specific | 51.9% (303/584) | 53.7% (313/583) |  |
| gemma | (a) | guesthouse | 56.5% (26/46) | 55.6% (25/45) | +0.0 |
| gemma | (b) | open | 22.3% (99/444) | 23.1% (103/446) |  |
| gemma | (b) | specific | 51.9% (303/584) | 53.7% (317/590) |  |
| gemma | (b) | guesthouse | 56.5% (26/46) | 57.4% (27/47) | +0.0 |
| gemma | (c) | open | 22.3% (99/444) | 1.8% (8/448) |  |
| gemma | (c) | specific | 51.9% (303/584) | 2.4% (14/587) |  |
| gemma | (c) | guesthouse | 56.5% (26/46) | 10.9% (5/46) | -46.7 |

| Model | Update | Trade: wrong removed, correct lost, ratio | Blocking filters, open set: control; update |
|---|---|---|---|
| sol | (a) | 3.0, 0.0, 0.00 | 18.5% (83/448); 18.5% (83/448) |
| sol | (b) | 2.0, 0.1, 0.05 | 18.5% (83/448); 18.3% (82/448) |
| sol | (c) | 101.0, 36.6, 0.36 | 18.5% (83/448); 8.0% (36/448) |
| luna | (a) | 10.0, -0.3, -0.03 | 10.3% (46/448); 8.5% (38/448) |
| luna | (b) | 14.0, -1.2, -0.09 | 10.3% (46/448); 8.0% (36/448) |
| luna | (c) | 84.0, 19.9, 0.24 | 10.3% (46/448); 0.4% (2/448) |
| deepseek | (a) | -9.0, -2.1, not defined | 9.6% (43/448); 10.3% (46/447) |
| deepseek | (b) | -5.0, -3.6, not defined | 9.6% (43/448); 9.8% (44/447) |
| deepseek | (c) | 68.0, 17.6, 0.26 | 9.6% (43/448); 1.1% (5/448) |
| qwen | (a) | -2.1, 0.6, not defined | 7.4% (32/434); 7.7% (33/430) |
| qwen | (b) | -1.1, -0.6, not defined | 7.4% (32/434); 7.3% (31/423) |
| qwen | (c) | 55.3, 17.0, 0.31 | 7.4% (32/434); 0.7% (3/424) |
| gemma | (a) | 0.0, -1.1, not defined | 12.2% (54/444); 12.3% (55/448) |
| gemma | (b) | -3.0, -1.1, not defined | 12.2% (54/444); 12.1% (54/446) |
| gemma | (c) | 91.8, 29.2, 0.32 | 12.2% (54/444); 0.7% (3/448) |

Read kinds per cell:

- sol: t0 {"search": 1085}; trep {"search": 1085}; tpar {"search": 1085}; t1 {"search": 1085}
- luna: t0 {"search": 1085}; trep {"search": 1085}; tpar {"search": 1085}; t1 {"search": 1085}
- deepseek: p0 {"search": 1083, "invalid: cut": 2}; prep {"search": 1084, "invalid: cut": 1}; ppar {"search": 1084, "invalid: cut": 1}; p1 {"search": 1085}
- qwen: p0 {"search": 1036, "invalid: cut": 49}; prep {"search": 1018, "invalid: cut": 67}; ppar {"invalid: cut": 57, "search": 1028}; p1 {"search": 1020, "invalid: cut": 65}
- gemma: p0 {"search": 1074, "invalid: cut": 11}; prep {"search": 1076, "invalid: cut": 9}; ppar {"search": 1083, "invalid: cut": 2}; p1 {"search": 1081, "invalid: cut": 4}

## Predictions

| Prediction | Rule | Decisions | Result |
|---|---|---|---|
| K1 | first | {"sol": "pass", "luna": "pass", "deepseek": "hold", "qwen": "hold", "gemma": "pass"} | holds |
| K1 | revised | {"sol": "pass", "luna": "pass", "deepseek": "hold", "qwen": "hold", "gemma": "pass"} | holds |
| K2 | first | {"sol": "pass", "luna": "hold", "deepseek": "flag", "qwen": "hold", "gemma": "hold"} | fails |
| K2 | revised | {"sol": "pass", "luna": "hold", "deepseek": "flag", "qwen": "hold", "gemma": "hold"} | fails |
| K3 | first | {"sol": "flag", "luna": "flag", "deepseek": "flag", "qwen": "flag", "gemma": "flag"} | holds |
| K3 | revised | {"sol": "flag", "luna": "flag", "deepseek": "flag", "qwen": "flag", "gemma": "flag"} | holds |
