# R10-25: held-out confirmation of the repair results

Status: exploratory, fixed in `prototypes/explore/PROTOCOL.md` (amendment R10-25) before any computation of these outcomes. Data: the stage-1 held-out answers (read 1, form t_legacy) and the verifier runs `ern_<model>`. Mix: the label-group mix (545 hotel to 994 no-type). Limits: share removed 50% or more; loss ratio 0.30 or less. Intervals: 95%, 2,000 bootstrap samples, seed 20261112. Tolerance of D1 and D2: 2.0 points.

- Models with verifier answers (M): sonnet, haiku, sol, luna, deepseek, qwen, gemma.
- Models without verifier answers: none.

## Predictions

| Prediction | Verdict | Detail |
|---|---|---|
| V1 | holds | {"k": 3, "models_that_meet": ["sonnet", "sol", "deepseek", "gemma"]} |
| V1w | fails | {"models": {"sol": true, "gemma": false}} |
| V2 | fails | - |
| V4 | holds | - |
| V3 | holds | {"models_that_meet": []} |
| D1 | fails | {"models": {"sonnet": true, "haiku": true, "sol": true, "luna": true, "deepseek": true, "qwen": false, "gemma": true}} |
| D2 | holds | {"models": {"sonnet": true, "haiku": true, "sol": true, "luna": true, "deepseek": true, "qwen": true, "gemma": true}} |

## Value level (read 1)

### Against the word rule (primary)

| Model | Gate | Dialogues | Share removed [95% interval] | Loss ratio [95% interval] | Meets: point / whole interval |
|---|---|---|---|---|---|
| sonnet | verifier, planned gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 90.0% [78.3%, 100.0%] | 0.26 [0.05, 0.56] | yes / no |
| sonnet | verifier, clear-no gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 63.3% [44.8%, 80.0%] | 0.19 [0.00, 0.51] | yes / no |
| haiku | verifier, planned gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 27.3% [0.0%, 57.1%] | 1.18 [0.00, no upper limit] | no / no |
| haiku | verifier, clear-no gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 9.1% [0.0%, 30.8%] | 1.77 [0.00, no upper limit] | no / no |
| sol | verifier, planned gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 71.6% [60.8%, 82.1%] | 0.00 [0.00, 0.00] | yes / yes |
| sol | verifier, clear-no gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 47.8% [35.8%, 59.4%] | 0.00 [0.00, 0.00] | no / no |
| luna | verifier, planned gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 97.0% [90.2%, 100.0%] | 0.39 [0.16, 0.69] | no / no |
| luna | verifier, clear-no gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 54.5% [38.5%, 71.4%] | 0.49 [0.15, 1.06] | no / no |
| deepseek | verifier, planned gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 65.5% [47.8%, 82.8%] | 0.28 [0.00, 0.71] | yes / no |
| deepseek | verifier, clear-no gate | {"NT": 213, "H stated": 18, "H not stated": 48} | 44.8% [27.3%, 63.9%] | 0.27 [0.00, 0.88] | no / no |
| qwen | verifier, planned gate | {"NT": 199, "H stated": 17, "H not stated": 43} | 89.5% [73.7%, 100.0%] | 0.43 [0.09, 0.99] | no / no |
| qwen | verifier, clear-no gate | {"NT": 199, "H stated": 17, "H not stated": 43} | 78.9% [58.8%, 95.2%] | 0.48 [0.10, 1.21] | no / no |
| gemma | verifier, planned gate | {"NT": 212, "H stated": 18, "H not stated": 48} | 92.1% [82.8%, 100.0%] | 0.20 [0.05, 0.41] | yes / no |
| gemma | verifier, clear-no gate | {"NT": 212, "H stated": 18, "H not stated": 48} | 55.3% [39.4%, 70.7%] | 0.17 [0.00, 0.47] | yes / no |

### Against the brief

| Model | Gate | Dialogues | Share removed [95% interval] | Loss ratio [95% interval] | Meets: point / whole interval |
|---|---|---|---|---|---|
| sonnet | verifier, planned gate | {"NT": 213, "H": 66} | 90.0% [78.3%, 100.0%] | 1.70 [1.06, 2.71] | no / no |
| sonnet | verifier, clear-no gate | {"NT": 213, "H": 66} | 63.3% [44.8%, 80.0%] | 0.93 [0.40, 1.77] | no / no |
| haiku | verifier, planned gate | {"NT": 213, "H": 66} | 27.3% [0.0%, 57.1%] | 4.13 [1.11, no upper limit] | no / no |
| haiku | verifier, clear-no gate | {"NT": 213, "H": 66} | 9.1% [0.0%, 30.8%] | 7.08 [0.88, no upper limit] | no / no |
| sol | verifier, planned gate | {"NT": 213, "H": 66} | 71.6% [60.8%, 82.1%] | 0.74 [0.45, 1.11] | no / no |
| sol | verifier, clear-no gate | {"NT": 213, "H": 66} | 47.8% [35.8%, 59.4%] | 0.17 [0.00, 0.40] | no / no |
| luna | verifier, planned gate | {"NT": 213, "H": 66} | 97.0% [90.2%, 100.0%] | 1.94 [1.29, 2.92] | no / no |
| luna | verifier, clear-no gate | {"NT": 213, "H": 66} | 54.5% [38.5%, 71.4%] | 1.97 [1.11, 3.54] | no / no |
| deepseek | verifier, planned gate | {"NT": 213, "H": 66} | 65.5% [47.8%, 82.8%] | 1.02 [0.44, 2.06] | no / no |
| deepseek | verifier, clear-no gate | {"NT": 213, "H": 66} | 44.8% [27.3%, 63.9%] | 0.82 [0.24, 1.99] | no / no |
| qwen | verifier, planned gate | {"NT": 199, "H": 60} | 89.5% [73.7%, 100.0%] | 2.25 [1.24, 4.18] | no / no |
| qwen | verifier, clear-no gate | {"NT": 199, "H": 60} | 78.9% [58.8%, 95.2%] | 2.55 [1.39, 4.79] | no / no |
| gemma | verifier, planned gate | {"NT": 212, "H": 66} | 92.1% [82.8%, 100.0%] | 1.26 [0.78, 1.94] | no / no |
| gemma | verifier, clear-no gate | {"NT": 212, "H": 66} | 55.3% [39.4%, 70.7%] | 1.17 [0.59, 2.20] | no / no |

### Against the corpus label (three label groups)

| Model | Gate | Dialogues | Share removed [95% interval] | Loss ratio [95% interval] | Meets: point / whole interval |
|---|---|---|---|---|---|
| sonnet | verifier, planned gate | {"LN": 187, "LG": 19, "LH": 74} | 96.4% [86.5%, 100.0%] | 1.76 [1.02, 3.64] | no / no |
| sonnet | verifier, clear-no gate | {"LN": 187, "LG": 19, "LH": 74} | 74.7% [50.0%, 91.0%] | 1.07 [0.48, 2.82] | no / no |
| haiku | verifier, planned gate | {"LN": 187, "LG": 19, "LH": 74} | 66.2% [14.3%, 93.6%] | 1.24 [0.30, 12.47] | no / no |
| haiku | verifier, clear-no gate | {"LN": 187, "LG": 19, "LH": 74} | 57.8% [0.0%, 88.7%] | 0.61 [0.00, no upper limit] | no / no |
| sol | verifier, planned gate | {"LN": 187, "LG": 19, "LH": 74} | 90.6% [83.9%, 96.1%] | 0.38 [0.24, 0.59] | no / no |
| sol | verifier, clear-no gate | {"LN": 187, "LG": 19, "LH": 74} | 67.7% [53.1%, 79.8%] | 0.19 [0.08, 0.36] | yes / no |
| luna | verifier, planned gate | {"LN": 187, "LG": 19, "LH": 74} | 100.0% [100.0%, 100.0%] | 2.14 [1.36, 3.65] | no / no |
| luna | verifier, clear-no gate | {"LN": 187, "LG": 19, "LH": 74} | 53.3% [29.0%, 74.7%] | 2.52 [1.24, 6.70] | no / no |
| deepseek | verifier, planned gate | {"LN": 187, "LG": 19, "LH": 74} | 75.0% [52.4%, 94.7%] | 2.19 [1.08, 4.71] | no / no |
| deepseek | verifier, clear-no gate | {"LN": 187, "LG": 19, "LH": 74} | 56.2% [30.8%, 81.8%] | 1.69 [0.65, 4.35] | no / no |
| qwen | verifier, planned gate | {"LN": 175, "LG": 17, "LH": 67} | 100.0% [100.0%, 100.0%] | 1.85 [0.94, 4.83] | no / no |
| qwen | verifier, clear-no gate | {"LN": 175, "LG": 17, "LH": 67} | 95.0% [79.3%, 100.0%] | 1.87 [0.95, 5.19] | no / no |
| gemma | verifier, planned gate | {"LN": 186, "LG": 19, "LH": 74} | 100.0% [100.0%, 100.0%] | 1.47 [0.92, 2.62] | no / no |
| gemma | verifier, clear-no gate | {"LN": 186, "LG": 19, "LH": 74} | 76.2% [57.1%, 90.5%] | 1.02 [0.53, 2.17] | no / no |

### Verifier answers for the hotel-only filters (read 1; yes / no / unclear)

| Model | NT | H | G |
|---|---|---|---|
| sonnet | 3 / 19 / 8 | 20 / 10 / 16 | 0 / 0 / 0 |
| haiku | 8 / 1 / 2 | 29 / 4 / 3 | 0 / 1 / 0 |
| sol | 19 / 32 / 16 | 39 / 3 / 17 | 0 / 5 / 0 |
| luna | 1 / 18 / 14 | 11 / 20 / 15 | 0 / 0 / 0 |
| deepseek | 10 / 13 / 6 | 22 / 6 / 5 | 0 / 1 / 0 |
| qwen | 2 / 15 / 2 | 9 / 21 / 0 | 0 / 0 / 0 |
| gemma | 3 / 21 / 14 | 22 / 14 / 11 | 0 / 2 / 0 |

## Display level (read 1)

Net visible failures avoided on NT and net visible losses added on H, in dialogues. Paired differences on NT: policy minus verifier (planned gate), in dialogues and in points.

| Model | Original: failures / losses | Avoided: verifier / relaxation / soft | Added: verifier | Relaxation − verifier, points [95%] | Soft − verifier, points [95%] |
|---|---|---|---|---|---|
| sonnet | 20 / 5 | 10 / 10 / 10 | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| haiku | 23 / 2 | 2 / 2 / 2 | 1 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| sol | 44 / 4 | 29 / 30 / 30 | 3 | 0.47 [0.00, 1.41] | 0.47 [0.00, 1.41] |
| luna | 31 / 11 | 10 / 10 / 10 | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| deepseek | 30 / 8 | 7 / 9 / 9 | 0 | 0.94 [0.00, 2.35] | 0.94 [0.00, 2.35] |
| qwen | 39 / 14 | 5 / 4 / 6 | 2 | -0.50 [-2.51, 1.01] | 0.50 [0.00, 1.51] |
| gemma | 38 / 7 | 13 / 14 / 14 | 2 | 0.47 [0.00, 1.42] | 0.47 [0.00, 1.42] |

### Symbolic policies on every model (read 1; no model call)

| Model | Dialogues NT / H / G | Original: failures / losses / G failures | Avoided: relaxation / soft / word rule | Added: word rule / always | Relaxation changes H displays (stated) |
|---|---|---|---|---|---|
| sonnet | 213 / 66 / 11 | 20 / 5 / 0 | 10 / 10 / 10 | 1 / 4 | 1 (1) |
| haiku | 213 / 66 / 11 | 23 / 2 / 1 | 2 / 2 / 2 | 0 / 3 | 0 (0) |
| sol | 213 / 66 / 11 | 44 / 4 / 5 | 30 / 30 / 30 | 4 / 5 | 0 (0) |
| luna | 213 / 66 / 11 | 31 / 11 / 0 | 10 / 10 / 10 | 1 / 3 | 2 (1) |
| deepseek | 213 / 66 / 11 | 30 / 8 / 1 | 9 / 9 / 9 | 0 / 0 | 0 (0) |
| qwen | 199 / 60 / 9 | 39 / 14 / 0 | 4 / 6 / 6 | 2 / 4 | 0 (0) |
| gemma | 212 / 66 / 11 | 38 / 7 / 2 | 14 / 14 / 14 | 2 / 5 | 0 (0) |

## Sensitivity: the mean of the base reads

| Model | Planned gate vs word rule: share / ratio / meets | Relaxation − verifier, points | Soft − verifier, points |
|---|---|---|---|---|
| sonnet | 90.0% / 0.26 / yes | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| haiku | 27.3% / 1.18 / no | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| sol | 73.1% / 0.00 / yes | 0.47 [0.00, 1.41] | 0.47 [0.00, 1.41] |
| luna | 97.0% / 0.39 / no | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| deepseek | 65.1% / 0.28 / yes | 0.94 [0.00, 2.35] | 0.94 [0.00, 2.35] |
| qwen | 87.5% / 0.48 / no | -0.33 [-1.81, 1.15] | 0.49 [0.00, 1.48] |
| gemma | 92.1% / 0.22 / yes | 0.47 [0.00, 1.42] | 0.47 [0.00, 1.42] |

## Missing answers

- sonnet: none
- haiku: none
- sol: none
- luna: none
- deepseek: none
- qwen: G | read 1 | original answer not valid: 2; H | read 1 | original answer not valid: 6; NT | read 1 | original answer not valid: 14; NT | reads 2-3 | original answer not valid: 1
- gemma: H | reads 2-3 | original answer not valid: 1; NT | read 1 | original answer not valid: 1

The JSON file holds every value, also the evaluated mix, the guesthouse briefs (G), the caused and ended errors, the searches per answer and the display loss ratios.
