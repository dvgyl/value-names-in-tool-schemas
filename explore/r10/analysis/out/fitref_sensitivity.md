## Fit reference: sensitivity of the development results (post hoc)

No model call; no held-out answer. Readings: recorded = the corpus goal record as scored (a value 'no' means must not have); a = parking or internet 'no' read as no requirement; b = drop each recorded requirement that the hotel part of the written task does not state (a reference to another part counts as stated); ab = both.

Statement check of reading b on the 448 first requests (slot:kind -> count): {"statement": {"area:reference": 25, "area:value": 128, "area:None": 12, "internet:value": 168, "internet:None": 1, "name:value": 214, "parking:value": 148, "parking:None": 2, "pricerange:reference": 11, "pricerange:value": 146, "pricerange:None": 6, "stars:value": 164}, "no_values": {"parking=no": 19, "internet=no": 2}, "b_dropped_requirements": 21, "b_briefs_with_a_dropped_requirement": 18}

### 1. Grouping of the 448 first requests whose brief sets no type

| Reading | Only guesthouses fit (F) | A hotel fits (R) | No venue fits (N) | Moves from the recorded grouping |
|---|---|---|---|---|
| recorded | 254 | 194 | 0 | {} |
| a | 249 | 199 | 0 | {"F->R": 5} |
| b | 249 | 199 | 0 | {"F->R": 5} |
| ab | 244 | 204 | 0 | {"F->R": 10} |

### 2. Search failures of the tool calls (share of valid reads on the 448; Table 2)

| Model | recorded: original / renamed | a: original / renamed | b: original / renamed | ab: original / renamed |
|---|---|---|---|---|
| sonnet | 10.7% [8.0, 13.8] / 1.1% | 10.1% [7.4, 13.2] / 1.1% | 10.3% [7.5, 13.3] / 1.1% | 9.7% [7.1, 12.6] / 1.1% |
| haiku | 3.1% [1.7, 4.8] / 0.2% | 3.0% [1.7, 4.7] / 0.2% | 3.1% [1.7, 4.8] / 0.2% | 3.0% [1.7, 4.7] / 0.2% |
| opus | 11.9% [9.0, 15.0] / 1.3% | 11.3% [8.5, 14.2] / 1.3% | 11.2% [8.4, 14.2] / 1.1% | 10.5% [7.8, 13.4] / 1.1% |
| sol | 18.1% [14.6, 21.9] / 6.9% | 17.4% [13.9, 21.1] / 6.5% | 17.4% [14.0, 21.1] / 6.6% | 16.7% [13.3, 20.4] / 6.2% |
| luna | 9.5% [6.9, 12.4] / 0.1% | 9.0% [6.5, 11.8] / 0.1% | 9.0% [6.5, 11.8] / 0.1% | 8.6% [6.1, 11.3] / 0.1% |
| astra | 19.0% [15.4, 22.8] / 2.7% | 18.3% [14.7, 22.1] / 2.7% | 18.1% [14.5, 21.7] / 2.5% | 17.4% [13.8, 21.0] / 2.5% |

### 3. Later turns (Sonnet agent; the same 260 conversations, regrouped under each reading)

| Reading | Groups (original tool) | Regrouped | F: initial failures | F: never held after one | F: never held without one | Difference | Without first-choice briefs | Never held, original / renamed (F) | On the original tool's initial failures: original / renamed |
|---|---|---|---|---|---|---|---|---|---|
| recorded | {"R": 130, "F": 130} | {} | 20 | 3 of 20 | 4 of 110 | +11.4 [-3.6, +28.2], Fisher p 0.073 | 1 of 13 against 0 of 70: +7.7 [+0.0, +23.1], Fisher p 0.16 | 7 / 9 | 3 / 3 (n = 20) |
| a | {"R": 134, "F": 126} | {"F->R": 4} | 19 | 2 of 19 | 2 of 107 | +8.7 [-2.8, +24.4], Fisher p 0.11 | 1 of 13 against 0 of 70: +7.7 [+0.0, +23.1], Fisher p 0.16 | 4 / 5 | 2 / 2 (n = 19) |
| b | {"R": 133, "F": 127} | {"F->R": 3} | 19 | 2 of 19 | 2 of 108 | +8.7 [-2.8, +24.5], Fisher p 0.11 | 1 of 13 against 0 of 70: +7.7 [+0.0, +23.1], Fisher p 0.16 | 4 / 6 | 2 / 2 (n = 19) |
| ab | {"R": 137, "F": 123} | {"F->R": 7} | 18 | 1 of 18 | 0 of 105 | +5.6 [+0.0, +16.7], Fisher p 0.15 | 1 of 13 against 0 of 70: +7.7 [+0.0, +23.1], Fisher p 0.16 | 1 / 2 | 1 / 1 (n = 18) |

Never held per group and tool (count, conversations):

- recorded: {"t0": {"F": [7, 130], "R": [10, 130], "N": [0, 0]}, "t1": {"F": [9, 130], "R": [13, 130], "N": [0, 0]}}; original-tool never-held ids: MUL0085.json, MUL0606.json, MUL0709.json, MUL1075.json, MUL1087.json, MUL1097.json, MUL1142.json, MUL2131.json, PMUL0035.json, PMUL0123.json, PMUL0371.json, PMUL0388.json, PMUL2698.json, PMUL2982.json, PMUL3693.json, PMUL4111.json, PMUL4661.json
- a: {"t0": {"F": [4, 126], "R": [11, 134], "N": [0, 0]}, "t1": {"F": [5, 126], "R": [16, 134], "N": [0, 0]}}; original-tool never-held ids: MUL0085.json, MUL0606.json, MUL0709.json, MUL1075.json, MUL1097.json, MUL1142.json, MUL2131.json, PMUL0035.json, PMUL0371.json, PMUL0388.json, PMUL2698.json, PMUL2982.json, PMUL3693.json, PMUL4111.json, PMUL4661.json
- b: {"t0": {"F": [4, 127], "R": [2, 133], "N": [0, 0]}, "t1": {"F": [6, 127], "R": [6, 133], "N": [0, 0]}}; original-tool never-held ids: MUL1087.json, MUL1097.json, MUL2131.json, PMUL0123.json, PMUL0371.json, PMUL2982.json
- ab: {"t0": {"F": [1, 123], "R": [3, 137], "N": [0, 0]}, "t1": {"F": [2, 123], "R": [9, 137], "N": [0, 0]}}; original-tool never-held ids: MUL1097.json, MUL2131.json, PMUL0371.json, PMUL2982.json

Moved first requests (448), per reading: a: MUL0700.json, MUL1087.json, MUL1222.json, PMUL0123.json, PMUL0371.json; b: MUL0085.json, MUL0137.json, MUL0606.json, PMUL1749.json, PMUL2698.json; ab: MUL0085.json, MUL0137.json, MUL0606.json, MUL0700.json, MUL1087.json, MUL1222.json, PMUL0123.json, PMUL0371.json, PMUL1749.json, PMUL2698.json
