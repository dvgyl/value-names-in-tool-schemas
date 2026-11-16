## 4. The reverse text edit (experiment I)

Exploratory. 233 training dialogues whose gold sets no type and whose traveller turns hold a lodging phrase and no "hotel". The edit changes the lodging phrase in the traveller turns to "hotel" (textedit.py). Parts: an assistant turn says "hotel" (115); no turn says "hotel" (118). Outcome: `type` holds `hotel`.

### Valid, invalid and missing reads per cell

| Model | Folders | Reads per dialogue | orig_f0 | ins_f0 | orig_f1 | ins_f1 |
|---|---|---|---|---|---|---|
| sonnet | eri_sonnet, erx_i3_sonnet | 3 | 699 valid, 0 invalid, 0 missing | 699 valid, 0 invalid, 0 missing | 699 valid, 0 invalid, 0 missing | 699 valid, 0 invalid, 0 missing |
| haiku | eri_haiku | 2 | 466 valid, 0 invalid, 0 missing | 466 valid, 0 invalid, 0 missing | 466 valid, 0 invalid, 0 missing | 466 valid, 0 invalid, 0 missing |
| sol | eri_sol, erx_i3_sol | 3 | 699 valid, 0 invalid, 0 missing | 699 valid, 0 invalid, 0 missing | 699 valid, 0 invalid, 0 missing | 699 valid, 0 invalid, 0 missing |
| luna | eri_luna | 2 | 463 valid, 3 invalid (failed 3), 0 missing | 462 valid, 4 invalid (failed 4), 0 missing | 464 valid, 2 invalid (failed 2), 0 missing | 462 valid, 4 invalid (failed 4), 0 missing |

### Rate of `type = hotel` per cell, part: all (233 dialogues; valid reads, 95% interval)

| Model | orig_f0 | ins_f0 | orig_f1 | ins_f1 |
|---|---|---|---|---|
| sonnet | 0.0% (0/699) [0.0%, 0.0%] | 16.0% (112/699) [11.6%, 20.9%] | 0.0% (0/699) [0.0%, 0.0%] | 0.4% (3/699) [0.0%, 1.3%] |
| haiku | 0.4% (2/466) [0.0%, 1.3%] | 0.9% (4/466) [0.0%, 2.1%] | 0.4% (2/466) [0.0%, 1.3%] | 0.2% (1/466) [0.0%, 0.6%] |
| sol | 0.0% (0/699) [0.0%, 0.0%] | 66.4% (464/699) [60.2%, 72.1%] | 0.0% (0/699) [0.0%, 0.0%] | 5.4% (38/699) [3.1%, 8.2%] |
| luna | 2.6% (12/463) [0.9%, 4.6%] | 17.7% (82/462) [13.2%, 22.6%] | 0.6% (3/464) [0.0%, 1.7%] | 0.2% (1/462) [0.0%, 0.9%] |

### Rate of `type = hotel` per cell, part: assistant_says_hotel (115 dialogues; valid reads, 95% interval)

| Model | orig_f0 | ins_f0 | orig_f1 | ins_f1 |
|---|---|---|---|---|
| sonnet | 0.0% (0/345) [0.0%, 0.0%] | 13.3% (46/345) [7.8%, 19.7%] | 0.0% (0/345) [0.0%, 0.0%] | 0.9% (3/345) [0.0%, 2.6%] |
| haiku | 0.9% (2/230) [0.0%, 2.6%] | 1.7% (4/230) [0.0%, 4.3%] | 0.9% (2/230) [0.0%, 2.6%] | 0.4% (1/230) [0.0%, 1.3%] |
| sol | 0.0% (0/345) [0.0%, 0.0%] | 63.8% (220/345) [55.1%, 71.6%] | 0.0% (0/345) [0.0%, 0.0%] | 6.4% (22/345) [2.9%, 10.4%] |
| luna | 4.8% (11/229) [1.7%, 8.7%] | 16.7% (38/228) [10.5%, 23.6%] | 1.3% (3/230) [0.0%, 3.5%] | 0.4% (1/229) [0.0%, 1.3%] |

### Rate of `type = hotel` per cell, part: no_turn_says_hotel (118 dialogues; valid reads, 95% interval)

| Model | orig_f0 | ins_f0 | orig_f1 | ins_f1 |
|---|---|---|---|---|
| sonnet | 0.0% (0/354) [0.0%, 0.0%] | 18.6% (66/354) [11.6%, 25.4%] | 0.0% (0/354) [0.0%, 0.0%] | 0.0% (0/354) [0.0%, 0.0%] |
| haiku | 0.0% (0/236) [0.0%, 0.0%] | 0.0% (0/236) [0.0%, 0.0%] | 0.0% (0/236) [0.0%, 0.0%] | 0.0% (0/236) [0.0%, 0.0%] |
| sol | 0.0% (0/354) [0.0%, 0.0%] | 68.9% (244/354) [61.0%, 76.6%] | 0.0% (0/354) [0.0%, 0.0%] | 4.5% (16/354) [1.7%, 7.9%] |
| luna | 0.4% (1/234) [0.0%, 1.3%] | 18.8% (44/234) [11.9%, 26.0%] | 0.0% (0/234) [0.0%, 0.0%] | 0.0% (0/233) [0.0%, 0.0%] |

### The edit effect and the difference in differences (per-dialogue means; sign test over dialogues)

| Model, part, contrast | Dialogues | Mean, points | 95% interval | Higher | Lower | Sign p |
|---|---|---|---|---|---|---|
| sonnet, all, edit under F0 (ins_f0 - orig_f0) | 233 | +16.0 | [+11.6, +20.9] | 43 | 0 | 2.3e-13 |
| sonnet, all, edit under F1 (ins_f1 - orig_f1) | 233 | +0.4 | [+0.0, +1.3] | 1 | 0 | 1 |
| sonnet, all, difference in differences (F0 edit - F1 edit) | 233 | +15.6 | [+11.3, +20.5] | 42 | 0 | 4.5e-13 |
| sonnet, assistant_says_hotel, edit under F0 (ins_f0 - orig_f0) | 115 | +13.3 | [+7.8, +19.7] | 18 | 0 | 7.6e-06 |
| sonnet, assistant_says_hotel, edit under F1 (ins_f1 - orig_f1) | 115 | +0.9 | [+0.0, +2.6] | 1 | 0 | 1 |
| sonnet, assistant_says_hotel, difference in differences (F0 edit - F1 edit) | 115 | +12.5 | [+7.2, +18.6] | 17 | 0 | 1.5e-05 |
| sonnet, no_turn_says_hotel, edit under F0 (ins_f0 - orig_f0) | 118 | +18.6 | [+11.6, +25.4] | 25 | 0 | 6e-08 |
| sonnet, no_turn_says_hotel, edit under F1 (ins_f1 - orig_f1) | 118 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1 |
| sonnet, no_turn_says_hotel, difference in differences (F0 edit - F1 edit) | 118 | +18.6 | [+11.6, +25.4] | 25 | 0 | 6e-08 |
| haiku, all, edit under F0 (ins_f0 - orig_f0) | 233 | +0.4 | [+0.0, +1.3] | 1 | 0 | 1 |
| haiku, all, edit under F1 (ins_f1 - orig_f1) | 233 | -0.2 | [-0.6, +0.0] | 0 | 1 | 1 |
| haiku, all, difference in differences (F0 edit - F1 edit) | 233 | +0.6 | [+0.0, +1.7] | 2 | 0 | 0.5 |
| haiku, assistant_says_hotel, edit under F0 (ins_f0 - orig_f0) | 115 | +0.9 | [+0.0, +2.6] | 1 | 0 | 1 |
| haiku, assistant_says_hotel, edit under F1 (ins_f1 - orig_f1) | 115 | -0.4 | [-1.3, +0.0] | 0 | 1 | 1 |
| haiku, assistant_says_hotel, difference in differences (F0 edit - F1 edit) | 115 | +1.3 | [+0.0, +3.5] | 2 | 0 | 0.5 |
| haiku, no_turn_says_hotel, edit under F0 (ins_f0 - orig_f0) | 118 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1 |
| haiku, no_turn_says_hotel, edit under F1 (ins_f1 - orig_f1) | 118 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1 |
| haiku, no_turn_says_hotel, difference in differences (F0 edit - F1 edit) | 118 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1 |
| sol, all, edit under F0 (ins_f0 - orig_f0) | 233 | +66.4 | [+60.2, +72.1] | 168 | 0 | 5.3e-51 |
| sol, all, edit under F1 (ins_f1 - orig_f1) | 233 | +5.4 | [+3.1, +8.2] | 21 | 0 | 9.5e-07 |
| sol, all, difference in differences (F0 edit - F1 edit) | 233 | +60.9 | [+55.1, +66.5] | 162 | 0 | 3.4e-49 |
| sol, assistant_says_hotel, edit under F0 (ins_f0 - orig_f0) | 115 | +63.8 | [+55.1, +71.6] | 80 | 0 | 1.7e-24 |
| sol, assistant_says_hotel, edit under F1 (ins_f1 - orig_f1) | 115 | +6.4 | [+2.9, +10.4] | 12 | 0 | 0.00049 |
| sol, assistant_says_hotel, difference in differences (F0 edit - F1 edit) | 115 | +57.4 | [+49.3, +65.2] | 76 | 0 | 2.6e-23 |
| sol, no_turn_says_hotel, edit under F0 (ins_f0 - orig_f0) | 118 | +68.9 | [+61.0, +76.6] | 88 | 0 | 6.5e-27 |
| sol, no_turn_says_hotel, edit under F1 (ins_f1 - orig_f1) | 118 | +4.5 | [+1.7, +7.9] | 9 | 0 | 0.0039 |
| sol, no_turn_says_hotel, difference in differences (F0 edit - F1 edit) | 118 | +64.4 | [+55.9, +72.6] | 86 | 0 | 2.6e-26 |
| luna, all, edit under F0 (ins_f0 - orig_f0) | 233 | +15.2 | [+10.7, +20.2] | 42 | 5 | 2.5e-08 |
| luna, all, edit under F1 (ins_f1 - orig_f1) | 233 | -0.4 | [-1.1, +0.0] | 0 | 2 | 0.5 |
| luna, all, difference in differences (F0 edit - F1 edit) | 233 | +15.7 | [+11.2, +20.6] | 43 | 5 | 1.4e-08 |
| luna, assistant_says_hotel, edit under F0 (ins_f0 - orig_f0) | 115 | +11.7 | [+4.8, +18.7] | 18 | 5 | 0.011 |
| luna, assistant_says_hotel, edit under F1 (ins_f1 - orig_f1) | 115 | -0.9 | [-2.2, +0.0] | 0 | 2 | 0.5 |
| luna, assistant_says_hotel, difference in differences (F0 edit - F1 edit) | 115 | +12.6 | [+5.7, +20.0] | 19 | 5 | 0.0066 |
| luna, no_turn_says_hotel, edit under F0 (ins_f0 - orig_f0) | 118 | +18.6 | [+11.9, +25.4] | 24 | 0 | 1.2e-07 |
| luna, no_turn_says_hotel, edit under F1 (ins_f1 - orig_f1) | 118 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1 |
| luna, no_turn_says_hotel, difference in differences (F0 edit - F1 edit) | 118 | +18.6 | [+11.9, +25.4] | 24 | 0 | 1.2e-07 |

### The I3 reference: F0 rate on the 423 dialogues of S1t whose brief sets no type and names no venue

Source: review/plan14/harm_by_model.out, row "brief: no type, no name" (round-9 natural reads: E13 for Sonnet and Haiku, X2 for Sol and Luna).

| Model | Reference F0 rate | Half of it | ins_f0 rate (233) |
|---|---|---|---|
| sonnet | 26.1% (331/1269) | 13.0% | 16.0% (112/699) [11.6%, 20.9%] |
| haiku | 5.7% (72/1269) | 2.8% | 0.9% (4/466) [0.0%, 2.1%] |
| sol | 58.8% (248/422) | 29.4% | 66.4% (464/699) [60.2%, 72.1%] |
| luna | 31.0% (394/1269) | 15.5% | 17.7% (82/462) [13.2%, 22.6%] |

### Predictions (judged on all 233 dialogues by the point value)

| # | Words | Value | Held |
|---|---|---|---|
| I1 | under F0 the edit raises type = hotel by at least 10 points for Sonnet, Sol and Luna | {"sonnet": 0.1602, "sol": 0.6638, "luna": 0.1524} | held |
| I2 | under F1 the edit raises it by 3 points or less for every model | {"sonnet": 0.0043, "haiku": -0.0021, "sol": 0.0544, "luna": -0.0043} | failed |
| I3 | the F0 rate on the edited text is at least half of the model's F0 rate on the 423 no-name dialogues of experiment 2 | {"sonnet": {"ins_f0": 0.1602, "reference_423": 0.2608, "half_reference": 0.1304}, "haiku": {"ins_f0": 0.0086, "reference_423": 0.0567, "half_reference": 0.0284}, "sol": {"ins_f0": 0.6638, "reference_423": 0.5877, "half_reference": 0.2938}, "luna": {"ins_f0": 0.1775, "reference_423": 0.3105, "half_reference": 0.1552}} | failed |
