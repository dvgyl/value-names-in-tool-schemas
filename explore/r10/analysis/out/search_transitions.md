## Repair details (post hoc)

### Transitions of the verifier gates (dialogues; Haiku and Luna: halves)

| Model | Gate | No-type: fixed | broken | still failing | still fine | Net avoided | Hotel: lost | regained | still lost | still fine | Net added |
|---|---|---|---|---|---|---|---|---|---|---|---|
| sonnet | verify | 37 | 0 | 103 | 667 | 37 | 8 | 0 | 35 | 190 | 8 |
| sonnet | verify_no_only (post hoc) | 27 | 0 | 113 | 667 | 27 | 3 | 0 | 35 | 195 | 3 |
| haiku | verify | 0.5 | 0 | 123.5 | 683 | 0.5 | 4.5 | 0 | 41.5 | 187 | 4.5 |
| haiku | verify_no_only (post hoc) | 0 | 0 | 124 | 683 | 0 | 2.5 | 0 | 41.5 | 189 | 2.5 |
| sol | verify | 100 | 1 | 115 | 591 | 99 | 4 | 0 | 29 | 200 | 4 |
| sol | verify_no_only (post hoc) | 91 | 0 | 124 | 592 | 91 | 0 | 0 | 29 | 204 | 0 |
| luna | verify | 36.5 | 0 | 151 | 619.5 | 36.5 | 9 | 0 | 42.5 | 181.5 | 9 |
| luna | verify_no_only (post hoc) | 25 | 0 | 162.5 | 619.5 | 25 | 4.5 | 0 | 42.5 | 186 | 4.5 |
| opus | verify | 22 | 1 | 76 | 708 | 21 | 3 | 0 | 29 | 201 | 3 |
| opus | verify_no_only (post hoc) | 18 | 0 | 80 | 709 | 18 | 0 | 0 | 29 | 204 | 0 |
| astra | verify | 108 | 1 | 104 | 594 | 107 | 7 | 0 | 29 | 197 | 7 |
| astra | verify_no_only (post hoc) | 92 | 0 | 120 | 595 | 92 | 0 | 0 | 29 | 204 | 0 |

### Share removed with 95% intervals (main count, all dialogues)

| Model | Repair | Share removed |
|---|---|---|
| sonnet | b_list | 23.6% [16.5, 30.8] |
| sonnet | b_shot | 9.9% [1.4, 18.0] |
| sonnet | b_evidence | -32.5% [-45.5, -21.1] |
| sonnet | verify | 92.1% [88.3, 95.7] |
| sonnet | verify_no_only (post hoc) | 54.2% [47.3, 60.8] |
| haiku | b_list | -56.4% [-91.2, -30.7] |
| haiku | b_shot | -2.7% [-22.2, 13.6] |
| haiku | b_evidence | -33.6% [-66.3, -9.6] |
| haiku | verify | 32.7% [21.4, 45.6] |
| haiku | verify_no_only (post hoc) | 22.7% [12.6, 33.7] |
| sol | b_list | 1.3% [-2.6, 5.0] |
| sol | b_shot | 47.7% [43.0, 52.6] |
| sol | b_evidence | -5.5% [-9.8, -1.7] |
| sol | verify | 75.1% [70.9, 79.0] |
| sol | verify_no_only (post hoc) | 53.4% [48.9, 58.1] |
| luna | b_list | 32.4% [26.3, 38.7] |
| luna | b_shot | 0.2% [-6.6, 6.6] |
| luna | b_evidence | -39.5% [-51.7, -28.9] |
| luna | verify | 94.0% [90.8, 96.8] |
| luna | verify_no_only (post hoc) | 48.0% [42.5, 53.4] |
| opus | b_list | 13.0% [5.5, 20.2] |
| opus | verify | 74.0% [67.9, 80.2] |
| opus | verify_no_only (post hoc) | 36.0% [29.3, 42.6] |
| astra | b_list | 9.8% [6.5, 13.1] |
| astra | verify | 83.3% [79.8, 86.8] |
| astra | verify_no_only (post hoc) | 51.8% [47.3, 56.6] |
