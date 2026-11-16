## 3. Repairs (experiment B)

Exploratory. Groups: 994 dialogues where the traveller says "hotel" and the gold sets no type (wrong value if written), 490 where the gold is guesthouse (wrong), 545 where the gold is hotel (correct). Trade rule: a repair works when it removes at least 50% of the baseline wrong values and loses at most 0.30 correct values per wrong value removed.

### Rate of `type = hotel` per group (valid reads)

| Model | Arm | No type (994) | Guesthouse (490) | Hotel (545) |
|---|---|---|---|---|
| sonnet | f0 | 19.2% (191/994) | 7.3% (36/490) | 68.8% (375/545) |
| sonnet | b_list | 14.6% (145/994) | 2.0% (10/490) | 59.8% (326/545) |
| sonnet | b_shot | 17.4% (173/994) | 5.3% (26/490) | 67.7% (369/545) |
| sonnet | b_evidence | 26.3% (261/994) | 8.0% (39/490) | 78.7% (429/545) |
| sonnet | verify | 1.9% (19/994) | 4.3% (21/490) | 24.2% (132/545) |
| sonnet | verify_no_only (post hoc) | 9.6% (95/994) | 4.5% (22/490) | 50.6% (276/545) |
| haiku | f0 | 5.2% (103/1988) | 4.7% (46/980) | 41.0% (447/1090) |
| haiku | b_list | 8.1% (161/1988) | 1.1% (11/980) | 46.1% (502/1090) |
| haiku | b_shot | 5.6% (112/1988) | 4.1% (40/980) | 45.8% (499/1090) |
| haiku | b_evidence | 6.6% (132/1988) | 3.8% (37/980) | 45.1% (492/1090) |
| haiku | verify | 3.9% (78/1988) | 3.6% (35/980) | 33.7% (367/1090) |
| haiku | verify_no_only (post hoc) | 4.5% (89/1988) | 3.6% (35/980) | 36.1% (393/1090) |
| sol | f0 | 42.0% (417/994) | 12.0% (59/490) | 91.0% (496/545) |
| sol | b_list | 42.6% (423/994) | 5.7% (28/490) | 88.6% (483/545) |
| sol | b_shot | 22.0% (219/994) | 8.6% (42/490) | 71.2% (388/545) |
| sol | b_evidence | 45.0% (447/994) | 11.0% (54/490) | 90.5% (493/545) |
| sol | verify | 11.7% (116/994) | 3.5% (17/490) | 56.1% (306/545) |
| sol | b_define | - (0/0) | 5.3% (26/490) | 56.1% (306/545) |
| sol | verify_no_only (post hoc) | 21.5% (214/994) | 3.7% (18/490) | 79.8% (435/545) |
| luna | f0 | 22.6% (450/1988) | 11.2% (110/980) | 68.0% (741/1090) |
| luna | b_list | 14.6% (291/1988) | 2.4% (24/980) | 54.0% (589/1090) |
| luna | b_shot | 21.9% (435/1988) | 8.3% (81/980) | 69.4% (756/1090) |
| luna | b_evidence | 30.1% (598/1988) | 15.1% (148/980) | 71.3% (777/1090) |
| luna | verify | 2.6% (51/1987) | 7.3% (71/978) | 21.8% (238/1090) |
| luna | b_define | - (0/0) | 5.6% (55/980) | 53.4% (582/1090) |
| luna | verify_no_only (post hoc) | 13.2% (263/1987) | 7.5% (73/978) | 43.6% (475/1090) |
| opus | f0 | 20.0% (199/994) | 10.2% (50/490) | 79.4% (433/545) |
| opus | b_list | 17.0% (169/994) | 1.0% (5/490) | 74.3% (405/545) |
| opus | verify | 6.2% (62/994) | 8.0% (39/490) | 43.9% (239/545) |
| opus | verify_no_only (post hoc) | 13.8% (137/994) | 8.2% (40/490) | 70.5% (384/545) |
| astra | f0 | 42.4% (421/994) | 12.2% (60/490) | 91.0% (496/545) |
| astra | b_list | 39.2% (390/994) | 5.3% (26/490) | 87.5% (477/545) |
| astra | verify | 7.9% (79/994) | 3.7% (18/490) | 43.7% (238/545) |
| astra | verify_no_only (post hoc) | 22.4% (223/994) | 3.9% (19/490) | 80.0% (436/545) |

### The trade against the baseline (paired estimator, 95% interval)

| Model | Arm | Wrong removed | Share of baseline wrong removed | Correct lost | Ratio | 95% interval | Meets rule |
|---|---|---|---|---|---|---|---|
| sonnet | b_list | 72.0 | 31.7% | 49.0 | 0.68 | [0.44, 1.02] | no |
| sonnet | b_shot | 28.0 | 12.3% | 6.0 | 0.21 | [-0.25, 1.00] | no |
| sonnet | b_evidence | -73.0 | -32.2% | -54.0 | - (adds wrong values) | - | no |
| sonnet | verify | 187.0 | 82.4% | 243.0 | 1.30 | [1.11, 1.53] | no |
| sonnet | verify_no_only (post hoc) | 110.0 | 48.5% | 99.0 | 0.90 | [0.69, 1.16] | no |
| haiku | b_list | -11.5 | -15.4% | -27.5 | - (adds wrong values) | - | no |
| haiku | b_shot | -1.5 | -2.0% | -26.0 | - (adds wrong values) | - | no |
| haiku | b_evidence | -10.0 | -13.4% | -22.5 | - (adds wrong values) | - | no |
| haiku | verify | 18.0 | 24.2% | 40.0 | 2.22 | [1.36, 3.88] | no |
| haiku | verify_no_only (post hoc) | 12.5 | 16.8% | 27.0 | 2.16 | [1.21, 4.21] | no |
| sol | b_list | 25.0 | 5.3% | 13.0 | 0.52 | [0.15, 2.75] | no |
| sol | b_shot | 215.0 | 45.2% | 108.0 | 0.50 | [0.40, 0.62] | no |
| sol | b_evidence | -25.0 | -5.3% | 3.0 | - (adds wrong values) | - | no |
| sol | verify | 343.0 | 72.1% | 190.0 | 0.55 | [0.48, 0.64] | no |
| sol | verify_no_only (post hoc) | 244.0 | 51.3% | 61.0 | 0.25 | [0.19, 0.32] | yes |
| luna | b_list | 122.5 | 43.8% | 76.0 | 0.62 | [0.47, 0.80] | no |
| luna | b_shot | 22.0 | 7.9% | -7.5 | -0.34 | [-2.00, 0.22] | no |
| luna | b_evidence | -93.0 | -33.2% | -18.0 | - (adds wrong values) | - | no |
| luna | verify | 218.9 | 78.2% | 251.5 | 1.15 | [1.00, 1.33] | no |
| luna | verify_no_only (post hoc) | 111.9 | 39.9% | 133.0 | 1.19 | [0.96, 1.47] | no |
| opus | b_list | 75.0 | 30.1% | 28.0 | 0.37 | [0.15, 0.64] | no |
| opus | verify | 148.0 | 59.4% | 194.0 | 1.31 | [1.09, 1.58] | no |
| opus | verify_no_only (post hoc) | 72.0 | 28.9% | 49.0 | 0.68 | [0.47, 0.97] | no |
| astra | b_list | 65.0 | 13.5% | 19.0 | 0.29 | [0.15, 0.50] | no |
| astra | verify | 384.0 | 79.8% | 258.0 | 0.67 | [0.59, 0.76] | no |
| astra | verify_no_only (post hoc) | 239.0 | 49.7% | 60.0 | 0.25 | [0.19, 0.32] | no |

Reference (post hoc): the ratio of a repair that deletes baseline `hotel` values at random, correct values lost per wrong value removed: sonnet 1.65, haiku 3.00, sol 1.04, luna 1.32, opus 1.74, astra 1.03.

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
