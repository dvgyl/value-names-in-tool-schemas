## The returned flag (amendment R10-7) - first read only (R10-7 as first run)

Exploratory. Step 2 of experiment A without the one-call limit, on the stage-1 calls whose hotel-only search found nothing and whose search without the type found a guesthouse. Arms in the same batch: plain (the real empty result) and flag (the same result and one line that names the guesthouse count).

Runs used: sonnet: erw_sonnet; haiku: erw_haiku; opus: erw_opus.

### Answer kinds

| Model | Arm | Answers | Widen | Tell | Search kept | Other text | Neither | Invalid |
|---|---|---|---|---|---|---|---|---|
| sonnet | plain | 64 | 56 | 0 | 8 | 0 | 0 | 0 |
| sonnet | flag | 64 | 55 | 4 | 5 | 0 | 0 | 0 |
| sonnet | era2 (one-call limit, other batch) | 64 | 17 | 45 | 1 | 1 | 0 | 0 |
| haiku | plain | 29 | 12 | 9 | 4 | 4 | 0 | 0 |
| haiku | flag | 29 | 15 | 14 | 0 | 0 | 0 | 0 |
| haiku | era2 (one-call limit, other batch) | 29 | 3 | 15 | 1 | 10 | 0 | 0 |
| opus | plain | 26 | 22 | 1 | 3 | 0 | 0 | 0 |
| opus | flag | 26 | 15 | 10 | 1 | 0 | 0 | 0 |
| opus | era2 (one-call limit, other batch) | 26 | 2 | 22 | 0 | 2 | 0 | 0 |

### Rates per arm (valid answers; 95% interval over dialogues)

| Model | Outcome | Plain | Flag | era2 (description) |
|---|---|---|---|---|
| sonnet | recovery | 87.5% [75.0%, 96.9%] | 92.2% [82.8%, 100.0%] | 96.9% |
| sonnet | widen | 87.5% [75.0%, 96.9%] | 85.9% [73.4%, 96.9%] | 26.6% |
| sonnet | tell | 0.0% [0.0%, 0.0%] | 6.2% [0.0%, 15.6%] | - |
| haiku | recovery | 72.4% [53.6%, 89.7%] | 100.0% [100.0%, 100.0%] | 62.1% |
| haiku | widen | 41.4% [20.0%, 65.5%] | 51.7% [29.0%, 75.0%] | 10.3% |
| haiku | tell | 31.0% [11.5%, 50.0%] | 48.3% [25.0%, 71.0%] | - |
| opus | recovery | 88.5% [76.9%, 100.0%] | 96.2% [88.5%, 100.0%] | 92.3% |
| opus | widen | 84.6% [69.2%, 96.2%] | 57.7% [38.5%, 76.9%] | 7.7% |
| opus | tell | 3.8% [0.0%, 11.5%] | 38.5% [19.2%, 57.7%] | - |

### Flag minus plain (paired by call; dialogue means; sign test over dialogues)

| Model | Outcome | Dialogues | Calls | Mean, points | 95% interval | Higher | Lower | Sign p | Calls flag above | Calls plain above |
|---|---|---|---|---|---|---|---|---|---|---|
| sonnet | recovery | 32 | 64 | +4.7 | [+0.0, +12.5] | 2 | 0 | 0.5 | 3 | 0 |
| sonnet | widen | 32 | 64 | -1.6 | [-9.4, +4.7] | 1 | 1 | 1 | 1 | 2 |
| sonnet | tell | 32 | 64 | +6.2 | [+0.0, +15.6] | 2 | 0 | 0.5 | 4 | 0 |
| haiku | recovery | 16 | 29 | +25.0 | [+9.4, +43.8] | 6 | 0 | 0.031 | 8 | 0 |
| haiku | widen | 16 | 29 | +12.5 | [-9.4, +34.4] | 3 | 2 | 1 | 6 | 3 |
| haiku | tell | 16 | 29 | +12.5 | [-9.4, +34.4] | 6 | 2 | 0.29 | 7 | 2 |
| opus | recovery | 26 | 26 | +7.7 | [+0.0, +19.2] | 2 | 0 | 0.5 | 2 | 0 |
| opus | widen | 26 | 26 | -26.9 | [-46.2, -7.7] | 1 | 8 | 0.039 | 1 | 8 |
| opus | tell | 26 | 26 | +34.6 | [+11.5, +53.8] | 10 | 1 | 0.012 | 10 | 1 |

### Predictions (R10-7)

| # | Words | Value | Held |
|---|---|---|---|
| W1 | with the flag, recovery is 90% or more for each of Sonnet, Haiku and Opus | {"sonnet": 0.921875, "haiku": 1.0, "opus": 0.9615384615384616} | held |
| W2 | Haiku: recovery, flag minus plain, is +15 points or more, and its 95% interval excludes 0 | {"mean": 0.25, "ci": [0.09375, 0.4375]} | held |
| W3 | without the flag and without the one-call limit, recovery is 85% or more for Sonnet and Opus | {"sonnet": 0.875, "opus": 0.8846153846153846} | held |
| W4 | Sonnet: a new search without the hotel-only filter, flag minus plain, is +10 points or more | -0.015625 | failed |
| W5 | Opus: with the flag, a new search without the hotel-only filter is 20% or less | 0.5769230769230769 | failed |
