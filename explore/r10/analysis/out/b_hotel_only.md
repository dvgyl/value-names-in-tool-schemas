## 3. Repairs (experiment B) — sensitivity: hotel-only outcome (post hoc)

Exploratory. Groups: 994 dialogues where the traveller says "hotel" and the gold sets no type (wrong value if written), 490 where the gold is guesthouse (wrong), 545 where the gold is hotel (correct). Trade rule: a repair works when it removes at least 50% of the baseline wrong values and loses at most 0.30 correct values per wrong value removed.

### Rate of `type = hotel` per group (valid reads)

| Model | Arm | No type (994) | Guesthouse (490) | Hotel (545) |
|---|---|---|---|---|
| sonnet | f0 | 18.9% (188/994) | 3.1% (15/490) | 67.7% (369/545) |
| sonnet | b_list | 14.6% (145/994) | 2.0% (10/490) | 59.8% (326/545) |
| sonnet | b_shot | 17.1% (170/994) | 2.7% (13/490) | 66.8% (364/545) |
| sonnet | b_evidence | 25.8% (256/994) | 2.7% (13/490) | 76.3% (416/545) |
| sonnet | verify | 1.6% (16/994) | 0.0% (0/490) | 23.1% (126/545) |
| sonnet | verify_no_only (post hoc) | 9.3% (92/994) | 0.2% (1/490) | 49.5% (270/545) |
| haiku | f0 | 4.5% (89/1988) | 2.1% (21/980) | 40.5% (441/1090) |
| haiku | b_list | 8.1% (161/1988) | 1.1% (11/980) | 46.1% (502/1090) |
| haiku | b_shot | 4.8% (96/1988) | 1.7% (17/980) | 44.6% (486/1090) |
| haiku | b_evidence | 6.3% (125/1988) | 2.2% (22/980) | 44.6% (486/1090) |
| haiku | verify | 3.2% (64/1988) | 1.0% (10/980) | 33.1% (361/1090) |
| haiku | verify_no_only (post hoc) | 3.8% (75/1988) | 1.0% (10/980) | 35.5% (387/1090) |
| sol | f0 | 41.6% (414/994) | 8.8% (43/490) | 89.7% (489/545) |
| sol | b_list | 42.6% (423/994) | 5.7% (28/490) | 88.6% (483/545) |
| sol | b_shot | 21.7% (216/994) | 4.7% (23/490) | 70.1% (382/545) |
| sol | b_evidence | 44.6% (443/994) | 8.0% (39/490) | 89.4% (487/545) |
| sol | verify | 11.4% (113/994) | 0.2% (1/490) | 54.9% (299/545) |
| sol | b_define | - (0/0) | 2.7% (13/490) | 55.0% (300/545) |
| sol | verify_no_only (post hoc) | 21.2% (211/994) | 0.4% (2/490) | 78.5% (428/545) |
| luna | f0 | 21.5% (427/1988) | 4.0% (39/980) | 65.0% (709/1090) |
| luna | b_list | 14.6% (291/1988) | 2.4% (24/980) | 54.0% (589/1090) |
| luna | b_shot | 21.2% (422/1988) | 4.4% (43/980) | 68.3% (744/1090) |
| luna | b_evidence | 29.1% (578/1988) | 7.3% (72/980) | 68.3% (744/1090) |
| luna | verify | 1.4% (28/1987) | 0.0% (0/978) | 18.9% (206/1090) |
| luna | b_define | - (0/0) | 2.7% (26/980) | 51.7% (564/1090) |
| luna | verify_no_only (post hoc) | 12.1% (240/1987) | 0.2% (2/978) | 40.6% (443/1090) |
| opus | f0 | 18.9% (188/994) | 2.4% (12/490) | 76.0% (414/545) |
| opus | b_list | 17.0% (169/994) | 1.0% (5/490) | 74.3% (405/545) |
| opus | verify | 5.1% (51/994) | 0.2% (1/490) | 40.4% (220/545) |
| opus | verify_no_only (post hoc) | 12.7% (126/994) | 0.4% (2/490) | 67.0% (365/545) |
| astra | f0 | 42.1% (418/994) | 8.8% (43/490) | 89.7% (489/545) |
| astra | b_list | 39.2% (390/994) | 5.3% (26/490) | 87.5% (477/545) |
| astra | verify | 7.6% (76/994) | 0.2% (1/490) | 42.4% (231/545) |
| astra | verify_no_only (post hoc) | 22.1% (220/994) | 0.4% (2/490) | 78.7% (429/545) |

### The trade against the baseline (paired estimator, 95% interval)

| Model | Arm | Wrong removed | Share of baseline wrong removed | Correct lost | Ratio | 95% interval | Meets rule |
|---|---|---|---|---|---|---|---|
| sonnet | b_list | 48.0 | 23.6% | 43.0 | 0.90 | [0.54, 1.50] | no |
| sonnet | b_shot | 20.0 | 9.9% | 5.0 | 0.25 | [-0.46, 2.40] | no |
| sonnet | b_evidence | -66.0 | -32.5% | -47.0 | - (adds wrong values) | - | no |
| sonnet | verify | 187.0 | 92.1% | 243.0 | 1.30 | [1.11, 1.53] | no |
| sonnet | verify_no_only (post hoc) | 110.0 | 54.2% | 99.0 | 0.90 | [0.69, 1.16] | no |
| haiku | b_list | -31.0 | -56.4% | -30.5 | - (adds wrong values) | - | no |
| haiku | b_shot | -1.5 | -2.7% | -22.5 | - (adds wrong values) | - | no |
| haiku | b_evidence | -18.5 | -33.6% | -22.5 | - (adds wrong values) | - | no |
| haiku | verify | 18.0 | 32.7% | 40.0 | 2.22 | [1.36, 3.88] | no |
| haiku | verify_no_only (post hoc) | 12.5 | 22.7% | 27.0 | 2.16 | [1.21, 4.21] | no |
| sol | b_list | 6.0 | 1.3% | 6.0 | 1.00 | [-0.15, no upper limit] | no |
| sol | b_shot | 218.0 | 47.7% | 107.0 | 0.49 | [0.39, 0.60] | no |
| sol | b_evidence | -25.0 | -5.5% | 2.0 | - (adds wrong values) | - | no |
| sol | verify | 343.0 | 75.1% | 190.0 | 0.55 | [0.48, 0.64] | no |
| sol | verify_no_only (post hoc) | 244.0 | 53.4% | 61.0 | 0.25 | [0.19, 0.32] | yes |
| luna | b_list | 75.5 | 32.4% | 60.0 | 0.79 | [0.55, 1.12] | no |
| luna | b_shot | 0.5 | 0.2% | -17.5 | -35.00 | [-40.00, no upper limit] | no |
| luna | b_evidence | -92.0 | -39.5% | -17.5 | - (adds wrong values) | - | no |
| luna | verify | 219.0 | 94.0% | 251.5 | 1.15 | [1.00, 1.33] | no |
| luna | verify_no_only (post hoc) | 111.9 | 48.0% | 133.0 | 1.19 | [0.96, 1.47] | no |
| opus | b_list | 26.0 | 13.0% | 9.0 | 0.35 | [-0.19, 1.21] | no |
| opus | verify | 148.0 | 74.0% | 194.0 | 1.31 | [1.09, 1.58] | no |
| opus | verify_no_only (post hoc) | 72.0 | 36.0% | 49.0 | 0.68 | [0.47, 0.97] | no |
| astra | b_list | 45.0 | 9.8% | 12.0 | 0.27 | [0.09, 0.54] | no |
| astra | verify | 384.0 | 83.3% | 258.0 | 0.67 | [0.59, 0.76] | no |
| astra | verify_no_only (post hoc) | 239.0 | 51.8% | 60.0 | 0.25 | [0.19, 0.32] | yes |

Reference (post hoc): the ratio of a repair that deletes baseline `hotel` values at random, correct values lost per wrong value removed: sonnet 1.82, haiku 4.01, sol 1.07, luna 1.52, opus 2.07, astra 1.06.

### B-evidence: the labels of the wrong `hotel` values (no type and guesthouse groups)

| Model | Wrong hotel values (raw) | Labelled stated requirement | Quote given | Quote verbatim |
|---|---|---|---|---|
| sonnet | 365 | 300 (82.2%) | 365 | 364 (99.7%) |
| haiku | 213 | 169 (79.3%) | 213 | 208 (97.7%) |
| sol | 671 | 501 (74.7%) | 671 | 671 (100.0%) |
| luna | 765 | 746 (97.5%) | 765 | 758 (99.1%) |

### The verifier's answers ("Does the traveller exclude guesthouses?")

| Model | Group and baseline value | yes | no | unclear |
|---|---|---|---|---|
| sonnet | S1t, baseline hotel and guesthouse | 0 | 3 | 0 |
| sonnet | S1t, baseline hotel only | 16 | 96 | 76 |
| sonnet | S1t, baseline no hotel | 1 | 634 | 168 |
| sonnet | S2, baseline hotel and guesthouse | 0 | 6 | 0 |
| sonnet | S2, baseline hotel only | 126 | 99 | 144 |
| sonnet | S2, baseline no hotel | 1 | 90 | 79 |
| sonnet | S3, baseline hotel and guesthouse | 0 | 21 | 0 |
| sonnet | S3, baseline hotel only | 0 | 14 | 1 |
| sonnet | S3, baseline no hotel | 3 | 451 | 0 |
| haiku | S1t, baseline hotel and guesthouse | 5 | 7 | 2 |
| haiku | S1t, baseline hotel only | 64 | 14 | 11 |
| haiku | S1t, baseline no hotel | 106 | 1117 | 662 |
| haiku | S2, baseline hotel and guesthouse | 1 | 5 | 0 |
| haiku | S2, baseline hotel only | 361 | 54 | 26 |
| haiku | S2, baseline no hotel | 77 | 260 | 306 |
| haiku | S3, baseline hotel and guesthouse | 1 | 24 | 0 |
| haiku | S3, baseline hotel only | 10 | 11 | 0 |
| haiku | S3, baseline no hotel | 55 | 859 | 20 |
| sol | S1t, baseline hotel and guesthouse | 0 | 3 | 0 |
| sol | S1t, baseline hotel only | 113 | 203 | 98 |
| sol | S1t, baseline no hotel | 1 | 417 | 159 |
| sol | S2, baseline hotel and guesthouse | 2 | 5 | 0 |
| sol | S2, baseline hotel only | 299 | 61 | 129 |
| sol | S2, baseline no hotel | 3 | 26 | 20 |
| sol | S3, baseline hotel and guesthouse | 0 | 16 | 0 |
| sol | S3, baseline hotel only | 1 | 41 | 1 |
| sol | S3, baseline no hotel | 0 | 431 | 0 |
| luna | S1t, baseline hotel and guesthouse | 0 | 23 | 0 |
| luna | S1t, baseline hotel only | 28 | 187 | 212 |
| luna | S1t, baseline no hotel | 1 | 912 | 624 |
| luna | S2, baseline hotel and guesthouse | 0 | 31 | 1 |
| luna | S2, baseline hotel only | 206 | 266 | 237 |
| luna | S2, baseline no hotel | 0 | 118 | 231 |
| luna | S3, baseline hotel and guesthouse | 0 | 71 | 0 |
| luna | S3, baseline hotel only | 0 | 37 | 2 |
| luna | S3, baseline no hotel | 2 | 857 | 9 |
| opus | S1t, baseline hotel and guesthouse | 0 | 11 | 0 |
| opus | S1t, baseline hotel only | 51 | 62 | 75 |
| opus | S1t, baseline no hotel | 3 | 715 | 77 |
| opus | S2, baseline hotel and guesthouse | 2 | 17 | 0 |
| opus | S2, baseline hotel only | 220 | 49 | 145 |
| opus | S2, baseline no hotel | 5 | 76 | 31 |
| opus | S3, baseline hotel and guesthouse | 0 | 38 | 0 |
| opus | S3, baseline hotel only | 1 | 10 | 1 |
| opus | S3, baseline no hotel | 0 | 440 | 0 |
| astra | S1t, baseline hotel and guesthouse | 0 | 3 | 0 |
| astra | S1t, baseline hotel only | 76 | 198 | 144 |
| astra | S1t, baseline no hotel | 2 | 410 | 161 |
| astra | S2, baseline hotel and guesthouse | 1 | 6 | 0 |
| astra | S2, baseline hotel only | 231 | 60 | 198 |
| astra | S2, baseline no hotel | 4 | 28 | 17 |
| astra | S3, baseline hotel and guesthouse | 0 | 17 | 0 |
| astra | S3, baseline hotel only | 1 | 41 | 1 |
| astra | S3, baseline no hotel | 0 | 430 | 0 |

### Predictions

| # | Words | Value | Held |
|---|---|---|---|
| B1 | B-list meets the trade rule on at least 2 of the 4 models | [] | failed |
| B2 | B-evidence labels at least 80% of the wrong type = hotel values as stated requirement, so it does not meet the rule on Claude | {"sonnet": 0.821917808219178, "haiku": 0.7934272300469484, "sol": 0.7466467958271237, "luna": 0.9751633986928104} | failed |
| B3 | B-verify meets the trade rule on at least 2 of the 4 models | [] | failed |
| B5 | B-shot removes at least 50% of the F0 wrong values on at least 2 of the 4 models, and it meets the full trade rule on 1 model or more | {"removes_half": [], "meets": []} | failed |
| B4 | Sol's B-define loses 0.50 correct values or fewer per wrong value removed | "see b_define rows: S1t has no fresh b_define read, so the locked ratio needs the earlier S1 definition reads; reported separately" | - |
