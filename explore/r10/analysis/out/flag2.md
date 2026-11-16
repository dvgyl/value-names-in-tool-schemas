## The returned flag with travellers who require a hotel, and the GPT models (amendment R10-13)

Exploratory. Step 2 of experiment A without the one-call limit. Arm (a): Claude models on the prefixes whose brief sets type hotel; the empty hotel-only result is constructed; cells plain and flag in two text conditions (brief: the prefix unchanged; explicit: the traveller adds "It must be a hotel, not a guesthouse."). Arm (b): Sol and Astra on the R10-7 sample rule (briefs with no type or guesthouse). Intervals: 95% percentile cluster bootstrap over dialogues (2,000 draws, seed 20261112); sign test: exact, over dialogues.

### Arm (a): answer kinds

| Model | Cell | Answers | widen_silent | widen_told | kept | tell | neither | invalid |
|---|---|---|---|---|---|---|---|---|
| sonnet | plain | 38 | 12 | 22 | 0 | 4 | 0 | 0 |
| sonnet | flag | 38 | 16 | 16 | 1 | 5 | 0 | 0 |
| sonnet | xplain | 38 | 4 | 1 | 23 | 10 | 0 | 0 |
| sonnet | xflag | 38 | 2 | 0 | 10 | 26 | 0 | 0 |
| haiku | plain | 38 | 14 | 10 | 4 | 10 | 0 | 0 |
| haiku | flag | 38 | 11 | 19 | 0 | 8 | 0 | 0 |
| haiku | xplain | 38 | 0 | 0 | 14 | 24 | 0 | 0 |
| haiku | xflag | 38 | 0 | 0 | 10 | 28 | 0 | 0 |
| opus | plain | 25 | 22 | 0 | 0 | 3 | 0 | 0 |
| opus | flag | 25 | 5 | 0 | 0 | 20 | 0 | 0 |
| opus | xplain | 25 | 0 | 0 | 4 | 21 | 0 | 0 |
| opus | xflag | 25 | 1 | 0 | 0 | 24 | 0 | 0 |

### Arm (a): rates per cell (valid answers; 95% interval over dialogues)

| Model | Outcome | plain | flag | xplain | xflag |
|---|---|---|---|---|---|
| sonnet | silent_widening | 31.6% [14.7%, 50.0%] | 42.1% [28.9%, 54.3%] | 10.5% [0.0%, 23.7%] | 5.3% [0.0%, 13.2%] |
| sonnet | tell | 10.5% [0.0%, 25.0%] | 13.2% [2.6%, 27.0%] | 26.3% [8.3%, 46.2%] | 68.4% [51.2%, 85.4%] |
| sonnet | any_widening | 89.5% [75.0%, 100.0%] | 84.2% [69.4%, 95.1%] | 13.2% [2.6%, 26.3%] | 5.3% [0.0%, 13.2%] |
| sonnet | tell_word_rule | 7.9% [0.0%, 21.1%] | 13.2% [2.6%, 27.0%] | 26.3% [8.3%, 46.2%] | 68.4% [51.2%, 85.4%] |
| haiku | silent_widening | 36.8% [21.6%, 52.4%] | 28.9% [14.3%, 44.7%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] |
| haiku | tell | 26.3% [11.1%, 43.6%] | 21.1% [7.9%, 35.3%] | 63.2% [45.9%, 80.0%] | 73.7% [56.8%, 89.7%] |
| haiku | any_widening | 63.2% [43.8%, 80.0%] | 78.9% [64.7%, 91.9%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] |
| haiku | tell_word_rule | 23.7% [8.8%, 41.0%] | 21.1% [7.9%, 35.3%] | 57.9% [38.9%, 75.8%] | 73.7% [56.8%, 89.7%] |
| opus | silent_widening | 88.0% [76.0%, 100.0%] | 20.0% [8.0%, 36.0%] | 0.0% [0.0%, 0.0%] | 4.0% [0.0%, 12.0%] |
| opus | tell | 12.0% [0.0%, 24.0%] | 80.0% [64.0%, 92.0%] | 84.0% [68.0%, 96.0%] | 96.0% [88.0%, 100.0%] |
| opus | any_widening | 88.0% [76.0%, 100.0%] | 20.0% [8.0%, 36.0%] | 0.0% [0.0%, 0.0%] | 4.0% [0.0%, 12.0%] |
| opus | tell_word_rule | 12.0% [0.0%, 24.0%] | 80.0% [64.0%, 92.0%] | 84.0% [68.0%, 96.0%] | 96.0% [88.0%, 100.0%] |

### Arm (a): paired differences (by call; dialogue means; points)

| Model, contrast | Outcome | Dialogues | Calls | Mean | 95% interval | Higher | Lower | Sign p |
|---|---|---|---|---|---|---|---|---|
| sonnet, flag_minus_plain (brief) | silent_widening | 23 | 38 | +13.0 | [-4.3, +30.4] | 7 | 2 | 0.18 |
| sonnet, flag_minus_plain (brief) | tell | 23 | 38 | +0.0 | [-13.0, +8.7] | 2 | 1 | 1 |
| sonnet, flag_minus_plain (brief) | any_widening | 23 | 38 | -2.2 | [-13.0, +10.9] | 1 | 3 | 0.62 |
| sonnet, flag_minus_plain (explicit) | silent_widening | 23 | 38 | -4.3 | [-13.0, +0.0] | 0 | 1 | 1 |
| sonnet, flag_minus_plain (explicit) | tell | 23 | 38 | +43.5 | [+19.6, +65.2] | 13 | 1 | 0.0018 |
| sonnet, flag_minus_plain (explicit) | any_widening | 23 | 38 | -6.5 | [-17.4, +0.0] | 0 | 2 | 0.5 |
| sonnet, explicit_minus_brief (plain) | silent_widening | 23 | 38 | -19.6 | [-41.3, +4.3] | 3 | 9 | 0.15 |
| sonnet, explicit_minus_brief (plain) | tell | 23 | 38 | +10.9 | [-6.5, +28.3] | 4 | 1 | 0.38 |
| sonnet, explicit_minus_brief (plain) | any_widening | 23 | 38 | -73.9 | [-89.1, -56.5] | 0 | 18 | 7.6e-06 |
| sonnet, explicit_minus_brief (flag) | silent_widening | 23 | 38 | -37.0 | [-54.3, -17.4] | 1 | 14 | 0.00098 |
| sonnet, explicit_minus_brief (flag) | tell | 23 | 38 | +54.3 | [+32.6, +73.9] | 16 | 1 | 0.00027 |
| sonnet, explicit_minus_brief (flag) | any_widening | 23 | 38 | -78.3 | [-91.3, -63.0] | 0 | 20 | 1.9e-06 |
| haiku, flag_minus_plain (brief) | silent_widening | 23 | 38 | -10.9 | [-26.1, +2.2] | 2 | 5 | 0.45 |
| haiku, flag_minus_plain (brief) | tell | 23 | 38 | -4.3 | [-21.7, +10.9] | 3 | 4 | 1 |
| haiku, flag_minus_plain (brief) | any_widening | 23 | 38 | +17.4 | [+2.2, +37.0] | 6 | 2 | 0.29 |
| haiku, flag_minus_plain (explicit) | silent_widening | 23 | 38 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1 |
| haiku, flag_minus_plain (explicit) | tell | 23 | 38 | +13.0 | [+0.0, +28.3] | 6 | 2 | 0.29 |
| haiku, flag_minus_plain (explicit) | any_widening | 23 | 38 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1 |
| haiku, explicit_minus_brief (plain) | silent_widening | 23 | 38 | -37.0 | [-54.3, -21.7] | 0 | 12 | 0.00049 |
| haiku, explicit_minus_brief (plain) | tell | 23 | 38 | +34.8 | [+17.4, +54.3] | 12 | 1 | 0.0034 |
| haiku, explicit_minus_brief (plain) | any_widening | 23 | 38 | -58.7 | [-78.3, -39.1] | 0 | 15 | 6.1e-05 |
| haiku, explicit_minus_brief (flag) | silent_widening | 23 | 38 | -26.1 | [-41.3, -13.0] | 0 | 9 | 0.0039 |
| haiku, explicit_minus_brief (flag) | tell | 23 | 38 | +52.2 | [+34.8, +69.6] | 15 | 0 | 6.1e-05 |
| haiku, explicit_minus_brief (flag) | any_widening | 23 | 38 | -76.1 | [-91.3, -60.9] | 0 | 19 | 3.8e-06 |
| opus, flag_minus_plain (brief) | silent_widening | 25 | 25 | -68.0 | [-84.0, -48.0] | 0 | 17 | 1.5e-05 |
| opus, flag_minus_plain (brief) | tell | 25 | 25 | +68.0 | [+48.0, +84.0] | 17 | 0 | 1.5e-05 |
| opus, flag_minus_plain (brief) | any_widening | 25 | 25 | -68.0 | [-84.0, -48.0] | 0 | 17 | 1.5e-05 |
| opus, flag_minus_plain (explicit) | silent_widening | 25 | 25 | +4.0 | [+0.0, +12.0] | 1 | 0 | 1 |
| opus, flag_minus_plain (explicit) | tell | 25 | 25 | +12.0 | [-4.0, +32.0] | 4 | 1 | 0.38 |
| opus, flag_minus_plain (explicit) | any_widening | 25 | 25 | +4.0 | [+0.0, +12.0] | 1 | 0 | 1 |
| opus, explicit_minus_brief (plain) | silent_widening | 25 | 25 | -88.0 | [-100.0, -76.0] | 0 | 22 | 4.8e-07 |
| opus, explicit_minus_brief (plain) | tell | 25 | 25 | +72.0 | [+48.0, +88.0] | 19 | 1 | 4e-05 |
| opus, explicit_minus_brief (plain) | any_widening | 25 | 25 | -88.0 | [-100.0, -76.0] | 0 | 22 | 4.8e-07 |
| opus, explicit_minus_brief (flag) | silent_widening | 25 | 25 | -16.0 | [-32.0, -4.0] | 0 | 4 | 0.12 |
| opus, explicit_minus_brief (flag) | tell | 25 | 25 | +16.0 | [+4.0, +32.0] | 4 | 0 | 0.12 |
| opus, explicit_minus_brief (flag) | any_widening | 25 | 25 | -16.0 | [-32.0, -4.0] | 0 | 4 | 0.12 |

Description (note of 18:35 UTC): widening answers by their text, per cell.

- sonnet: plain {"word rule": 22, "other text": 10, "no text": 2}; flag {"word rule": 16, "other text": 13, "no text": 3}; xplain {"word rule": 1, "other text": 4}; xflag {"other text": 2}
- haiku: plain {"word rule": 10, "other text": 14}; flag {"other text": 11, "word rule": 19}; xplain {}; xflag {}
- opus: plain {"no text": 22}; flag {"no text": 5}; xplain {}; xflag {"no text": 1}

### Arm (b): answer kinds

| Model | Arm | Answers | widen | tell | kept | other | neither | invalid |
|---|---|---|---|---|---|---|---|---|
| sol | plain | 96 | 4 | 46 | 0 | 46 | 0 | 0 |
| sol | flag | 96 | 5 | 86 | 2 | 3 | 0 | 0 |
| sol | era2 (one-call limit, other batch) | 96 | 0 | 27 | 0 | 69 | 0 | 0 |
| astra | plain | 51 | 2 | 21 | 0 | 28 | 0 | 0 |
| astra | flag | 51 | 3 | 44 | 1 | 3 | 0 | 0 |
| astra | era2 (one-call limit, other batch) | 51 | 0 | 14 | 0 | 37 | 0 | 0 |

### Arm (b): rates and flag minus plain

| Model | Outcome | Plain | Flag |
|---|---|---|---|
| sol | recovery | 52.1% [38.7%, 64.9%] | 94.8% [88.7%, 99.0%] |
| sol | widen | 4.2% [0.0%, 10.5%] | 5.2% [1.0%, 11.5%] |
| sol | tell | 47.9% [35.1%, 60.4%] | 89.6% [81.1%, 96.8%] |
| sol | recovery, no-type briefs only (70 calls) | 52.9% [37.1%, 68.1%] | 97.1% [92.9%, 100.0%] |
| astra | recovery | 45.1% [31.4%, 58.8%] | 92.2% [84.3%, 98.0%] |
| astra | widen | 3.9% [0.0%, 9.8%] | 5.9% [0.0%, 13.7%] |
| astra | tell | 41.2% [27.5%, 54.9%] | 86.3% [76.5%, 94.1%] |
| astra | recovery, no-type briefs only (38 calls) | 50.0% [34.2%, 65.8%] | 92.1% [81.6%, 100.0%] |

| Model | Outcome | Dialogues | Calls | Mean | 95% interval | Higher | Lower | Sign p |
|---|---|---|---|---|---|---|---|---|
| sol | recovery | 49 | 96 | +43.9 | [+30.6, +57.1] | 27 | 2 | 1.6e-06 |
| sol | widen | 49 | 96 | +2.0 | [-2.0, +7.1] | 2 | 1 | 1 |
| sol | tell | 49 | 96 | +41.8 | [+28.6, +55.1] | 26 | 2 | 3e-06 |
| sol, no-type briefs only | recovery | 36 | 70 | +45.8 | [+29.2, +62.5] | 20 | 2 | 0.00012 |
| astra | recovery | 51 | 51 | +47.1 | [+31.4, +60.8] | 25 | 1 | 8e-07 |
| astra | widen | 51 | 51 | +2.0 | [-3.9, +9.8] | 2 | 1 | 1 |
| astra | tell | 51 | 51 | +45.1 | [+29.4, +60.8] | 25 | 2 | 5.6e-06 |
| astra, no-type briefs only | recovery | 38 | 38 | +42.1 | [+23.7, +57.9] | 17 | 1 | 0.00014 |

### Predictions (R10-13)

| # | Words | Value | Result |
|---|---|---|---|
| U1 | brief condition: silent widening, flag minus plain, is +10 points or less for each of Sonnet, Haiku and Opus | {"sonnet": 0.13043478260869565, "haiku": -0.10869565217391304, "opus": -0.68} | failed |
| U2 | explicit condition: silent widening, flag minus plain, is +10 points or less for each of Sonnet, Haiku and Opus | {"sonnet": -0.043478260869565216, "haiku": 0.0, "opus": 0.04} | held |
| U3 | Opus, brief condition: silent widening, flag minus plain, is -15 points or less, and its 95% interval excludes 0 | {"opus": {"mean": -0.68, "ci": [-0.84, -0.48]}} | held |
| U4 | brief condition, plain arm: silent widening is 50% or more for Opus and 20% or more for Sonnet | {"opus": 0.88, "sonnet": 0.3157894736842105} | held |
| U5 | plain arm: silent widening, explicit minus brief, is -20 points or less for Sonnet and for Opus | {"sonnet": -0.1956521739130435, "opus": -0.88} | failed |
| U6 | explicit condition, flag arm: tell is 60% or more for each of Sonnet, Haiku and Opus | {"sonnet": 0.6842105263157895, "haiku": 0.7368421052631579, "opus": 0.96} | held |
| U7 | arm (b): with the flag, recovery is 90% or more for Sol and for Astra | {"sol": 0.9479166666666666, "astra": 0.9215686274509803} | held |
| U8 | arm (b): recovery, flag minus plain, is +10 points or more for Sol and for Astra | {"sol": 0.4387755102040816, "astra": 0.47058823529411764} | held |
| U9 | arm (b), plain arm: recovery is 50% or more for Sol and for Astra | {"sol": 0.5208333333333334, "astra": 0.45098039215686275} | failed |
