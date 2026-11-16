## Held-out fit reference: brief-based bound of the first-request search failures (post hoc)

No model call; no held-out answer read. Inputs: main/wave1_ids.json (213 stage-1 natural dialogues: natural minus sample) and the public MultiWOZ 2.4 goal records. Readings as in fitref_sensitivity.md.

Dialogues: 213; hotel-text errors (kept at the recorded group): none

Recorded 'no' values (reading a): {"parking=no": 3}. Statement check of reading b (slot:kind -> count): {"area:reference": 9, "area:value": 55, "internet:value": 69, "name:value": 113, "parking:value": 63, "pricerange:reference": 6, "pricerange:value": 66, "stars:value": 69}; briefs with a dropped requirement: 0. Briefs whose set of fitting venues grows: {"a": 0, "b": 0, "ab": 0}.

| Reading | Only guesthouses fit (F) | A hotel fits (R) | No venue fits (N) | Moves | Leave F | Enter F | Max fall, points (of 213) | Max fall, points (of 203) | Max rise, points (of 203) |
|---|---|---|---|---|---|---|---|---|---|
| recorded | 128 | 85 | 0 | {} | 0 | 0 | 0.00 | 0.00 | 0.00 |
| a | 128 | 85 | 0 | {} | 0 | 0 | 0.00 | 0.00 | 0.00 |
| b | 128 | 85 | 0 | {} | 0 | 0 | 0.00 | 0.00 | 0.00 |
| ab | 128 | 85 | 0 | {} | 0 | 0 | 0.00 | 0.00 | 0.00 |

Moved dialogues, per reading: a: none; b: none; ab: none
