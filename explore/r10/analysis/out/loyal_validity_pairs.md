## Paired transitions and the second step without calls that are not valid (post hoc)

### 1. Original-tool exclusions whose paired renamed-tool answer has no call (448 no-type first requests)

| Model | Pairs | Original exclusions | of these, renamed answer without a call | Original no-call | Renamed no-call |
|---|---|---|---|---|---|
| sonnet | 1344 | 144 | 1 | 1 | 3 |
| haiku | 894 | 28 | 0 | 29 | 35 |
| opus | 896 | 107 | 0 | 0 | 0 |
| sol | 1344 | 243 | 0 | 0 | 0 |
| luna | 896 | 85 | 0 | 0 | 0 |
| astra | 448 | 85 | 0 | 0 | 0 |

### 2. Table C1 classes, stored and with calls that are not valid missing

| Model | Trials | Removes the filter | Mentions the other type | No mention |
|---|---|---|---|---|
| sonnet (stored) | 96 | 13.5% | 50.0% | 36.5% |
| sonnet (sensitivity) | 94 | 12.8% | 50.0% | 37.2% |
| haiku (stored) | 28 | 17.9% | 39.3% | 42.9% |
| haiku (sensitivity) | 23 | 8.7% | 39.1% | 52.2% |
| opus (stored) | 51 | 2.0% | 51.0% | 47.1% |
| opus (sensitivity) | 46 | 2.2% | 45.7% | 52.2% |
| sol (stored) | 161 | 0.0% | 14.9% | 85.1% |
| sol (sensitivity) | 161 | 0.0% | 14.9% | 85.1% |
| luna (stored) | 85 | 8.2% | 0.0% | 91.8% |
| luna (sensitivity) | 85 | 8.2% | 0.0% | 91.8% |
| astra (stored) | 85 | 0.0% | 14.1% | 85.9% |
| astra (sensitivity) | 85 | 0.0% | 14.1% | 85.9% |

Check: the stored classes equal a.json models.<m>.step2.after_search_failure for every model.
