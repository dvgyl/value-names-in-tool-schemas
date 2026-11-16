## The returned flag (amendment R10-7)

Exploratory. Step 2 of experiment A without the one-call limit, on the stage-1 calls whose hotel-only search found nothing and whose search without the type found a guesthouse. Arms in the same batch: plain (the real empty result) and flag (the same result and one line that names the guesthouse count).

Runs used: sonnet: erw_sonnet, erw2_sonnet; haiku: erw_haiku, erw2_haiku, erw3_haiku; opus: erw_opus, erw2_opus.

### Answer kinds

| Model | Arm | Answers | Widen | Tell | Search kept | Other text | Neither | Invalid |
|---|---|---|---|---|---|---|---|---|
| sonnet | plain | 128 | 112 | 0 | 16 | 0 | 0 | 0 |
| sonnet | flag | 128 | 109 | 9 | 10 | 0 | 0 | 0 |
| sonnet | era2 (one-call limit, other batch) | 64 | 17 | 45 | 1 | 1 | 0 | 0 |
| haiku | plain | 87 | 34 | 38 | 6 | 9 | 0 | 0 |
| haiku | flag | 87 | 42 | 45 | 0 | 0 | 0 | 0 |
| haiku | era2 (one-call limit, other batch) | 29 | 3 | 15 | 1 | 10 | 0 | 0 |
| opus | plain | 52 | 45 | 3 | 4 | 0 | 0 | 0 |
| opus | flag | 52 | 27 | 23 | 2 | 0 | 0 | 0 |
| opus | era2 (one-call limit, other batch) | 26 | 2 | 22 | 0 | 2 | 0 | 0 |

### Rates per arm (valid answers; 95% interval over dialogues)

| Model | Outcome | Plain | Flag | era2 (description) |
|---|---|---|---|---|
| sonnet | recovery | 87.5% [75.8%, 96.9%] | 92.2% [82.8%, 100.0%] | 96.9% |
| sonnet | widen | 87.5% [75.8%, 96.9%] | 85.2% [72.7%, 95.3%] | 26.6% |
| sonnet | tell | 0.0% [0.0%, 0.0%] | 7.0% [0.0%, 16.4%] | - |
| haiku | recovery | 82.8% [72.2%, 92.9%] | 100.0% [100.0%, 100.0%] | 62.1% |
| haiku | widen | 39.1% [22.2%, 58.0%] | 48.3% [28.6%, 69.2%] | 10.3% |
| haiku | tell | 43.7% [26.2%, 60.9%] | 51.7% [30.8%, 71.4%] | - |
| opus | recovery | 92.3% [82.7%, 100.0%] | 96.2% [88.5%, 100.0%] | 92.3% |
| opus | widen | 86.5% [73.1%, 96.2%] | 51.9% [36.5%, 69.2%] | 7.7% |
| opus | tell | 5.8% [0.0%, 11.5%] | 44.2% [26.9%, 61.5%] | - |

### Flag minus plain (paired by call; dialogue means; sign test over dialogues)

| Model | Outcome | Dialogues | Calls | Mean, points | 95% interval | Higher | Lower | Sign p | Calls flag above | Calls plain above |
|---|---|---|---|---|---|---|---|---|---|---|
| sonnet | recovery | 32 | 64 | +4.7 | [+0.0, +10.9] | 3 | 0 | 0.25 | 4 | 0 |
| sonnet | widen | 32 | 64 | -2.3 | [-10.9, +4.7] | 2 | 3 | 1 | 2 | 4 |
| sonnet | tell | 32 | 64 | +7.0 | [+0.0, +16.4] | 3 | 0 | 0.25 | 5 | 0 |
| haiku | recovery | 16 | 29 | +15.6 | [+6.2, +26.0] | 8 | 0 | 0.0078 | 11 | 0 |
| haiku | widen | 16 | 29 | +10.4 | [-6.2, +29.2] | 6 | 3 | 0.51 | 8 | 5 |
| haiku | tell | 16 | 29 | +5.2 | [-13.5, +21.9] | 7 | 4 | 0.55 | 10 | 5 |
| opus | recovery | 26 | 26 | +3.8 | [+0.0, +9.6] | 2 | 0 | 0.5 | 2 | 0 |
| opus | widen | 26 | 26 | -34.6 | [-51.9, -17.3] | 1 | 13 | 0.0018 | 1 | 13 |
| opus | tell | 26 | 26 | +38.5 | [+21.2, +53.8] | 15 | 1 | 0.00052 | 15 | 1 |

### Predictions (R10-7)

| # | Words | Value | Held |
|---|---|---|---|
| W1 | with the flag, recovery is 90% or more for each of Sonnet, Haiku and Opus | {"sonnet": 0.921875, "haiku": 1.0, "opus": 0.9615384615384616} | held |
| W2 | Haiku: recovery, flag minus plain, is +15 points or more, and its 95% interval excludes 0 | {"mean": 0.15625, "ci": [0.0625, 0.2604166666666667]} | held |
| W3 | without the flag and without the one-call limit, recovery is 85% or more for Sonnet and Opus | {"sonnet": 0.875, "opus": 0.9230769230769231} | held |
| W4 | Sonnet: a new search without the hotel-only filter, flag minus plain, is +10 points or more | -0.0234375 | failed |
| W5 | Opus: with the flag, a new search without the hotel-only filter is 20% or less | 0.5192307692307693 | failed |
