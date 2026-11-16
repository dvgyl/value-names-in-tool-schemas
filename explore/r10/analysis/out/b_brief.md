## 3. Repairs (experiment B)

Exploratory. Groups: 994 dialogues where the traveller says "hotel" and the gold sets no type (wrong value if written), 490 where the gold is guesthouse (wrong), 545 where the gold is hotel (correct). Trade rule: a repair works when it removes at least 50% of the baseline wrong values and loses at most 0.30 correct values per wrong value removed.

### Rate of `type = hotel` per group (valid reads)

| Model | Arm | No type (994) | Guesthouse (490) | Hotel (545) |
|---|---|---|---|---|
| sonnet | f0 | 14.6% (118/807) | 5.6% (22/394) | 83.7% (195/233) |
| sonnet | b_list | 11.4% (92/807) | 1.3% (5/394) | 73.4% (171/233) |
| sonnet | b_shot | 13.3% (107/807) | 3.6% (14/394) | 83.7% (195/233) |
| sonnet | b_evidence | 20.7% (167/807) | 4.8% (19/394) | 89.3% (208/233) |
| sonnet | verify | 0.5% (4/807) | 3.8% (15/394) | 39.1% (91/233) |
| sonnet | verify_no_only (post hoc) | 7.1% (57/807) | 3.8% (15/394) | 67.8% (158/233) |
| haiku | f0 | 3.3% (54/1614) | 4.1% (32/788) | 56.4% (263/466) |
| haiku | b_list | 6.6% (107/1614) | 0.9% (7/788) | 61.6% (287/466) |
| haiku | b_shot | 3.0% (48/1614) | 3.0% (24/788) | 61.6% (287/466) |
| haiku | b_evidence | 3.9% (63/1614) | 3.2% (25/788) | 63.5% (296/466) |
| haiku | verify | 2.7% (43/1614) | 2.9% (23/788) | 44.0% (205/466) |
| haiku | verify_no_only (post hoc) | 2.9% (47/1614) | 2.9% (23/788) | 47.9% (223/466) |
| sol | f0 | 34.1% (275/807) | 6.3% (25/394) | 99.1% (231/233) |
| sol | b_list | 35.2% (284/807) | 2.8% (11/394) | 94.8% (221/233) |
| sol | b_shot | 16.5% (133/807) | 4.8% (19/394) | 85.0% (198/233) |
| sol | b_evidence | 37.3% (301/807) | 5.8% (23/394) | 97.9% (228/233) |
| sol | verify | 8.3% (67/807) | 2.3% (9/394) | 70.4% (164/233) |
| sol | b_define | - (0/0) | 2.5% (10/394) | 72.5% (169/233) |
| sol | verify_no_only (post hoc) | 16.2% (131/807) | 2.3% (9/394) | 90.1% (210/233) |
| luna | f0 | 17.2% (278/1614) | 7.7% (61/788) | 81.1% (378/466) |
| luna | b_list | 10.6% (171/1614) | 1.5% (12/788) | 68.0% (317/466) |
| luna | b_shot | 17.2% (278/1614) | 6.0% (47/788) | 81.8% (381/466) |
| luna | b_evidence | 24.6% (397/1614) | 11.0% (87/788) | 83.0% (387/466) |
| luna | verify | 1.4% (23/1614) | 5.2% (41/786) | 31.1% (145/466) |
| luna | b_define | - (0/0) | 4.2% (33/788) | 68.7% (320/466) |
| luna | verify_no_only (post hoc) | 9.9% (159/1614) | 5.2% (41/786) | 53.6% (250/466) |
| opus | f0 | 13.8% (111/807) | 5.6% (22/394) | 91.0% (212/233) |
| opus | b_list | 11.5% (93/807) | 0.5% (2/394) | 84.5% (197/233) |
| opus | verify | 3.0% (24/807) | 4.6% (18/394) | 61.8% (144/233) |
| opus | verify_no_only (post hoc) | 8.4% (68/807) | 4.8% (19/394) | 82.4% (192/233) |
| astra | f0 | 34.4% (278/807) | 6.3% (25/394) | 98.7% (230/233) |
| astra | b_list | 31.6% (255/807) | 3.0% (12/394) | 94.8% (221/233) |
| astra | verify | 5.3% (43/807) | 2.5% (10/394) | 60.9% (142/233) |
| astra | verify_no_only (post hoc) | 16.7% (135/807) | 2.5% (10/394) | 89.7% (209/233) |

### The trade against the baseline (paired estimator, 95% interval)

| Model | Arm | Wrong removed | Share of baseline wrong removed | Correct lost | Ratio | 95% interval | Meets rule |
|---|---|---|---|---|---|---|---|
| sonnet | b_list | 53.2 | 30.8% | 56.1 | 1.06 | [0.57, 1.89] | no |
| sonnet | b_shot | 23.5 | 13.6% | 0.0 | 0.00 | [-0.95, 1.18] | no |
| sonnet | b_evidence | -56.6 | -32.8% | -30.4 | - (adds wrong values) | - | no |
| sonnet | verify | 149.1 | 86.3% | 243.3 | 1.63 | [1.32, 2.03] | no |
| sonnet | verify_no_only (post hoc) | 83.8 | 48.5% | 86.5 | 1.03 | [0.69, 1.49] | no |
| haiku | b_list | -17.1 | -32.2% | -28.1 | - (adds wrong values) | - | no |
| haiku | b_shot | 8.7 | 16.3% | -28.1 | -3.24 | [-31.80, no upper limit] | no |
| haiku | b_evidence | -1.2 | -2.2% | -38.6 | - (adds wrong values) | - | no |
| haiku | verify | 12.4 | 23.3% | 67.8 | 5.48 | [2.97, 12.28] | no |
| haiku | verify_no_only (post hoc) | 9.9 | 18.6% | 46.8 | 4.72 | [2.31, 11.83] | no |
| sol | b_list | 6.3 | 1.7% | 23.4 | 3.70 | [0.63, no upper limit] | no |
| sol | b_shot | 182.4 | 49.3% | 77.2 | 0.42 | [0.28, 0.58] | no |
| sol | b_evidence | -29.5 | -8.0% | 7.0 | - (adds wrong values) | - | no |
| sol | verify | 276.1 | 74.7% | 156.7 | 0.57 | [0.43, 0.70] | no |
| sol | verify_no_only (post hoc) | 197.3 | 53.3% | 49.1 | 0.25 | [0.15, 0.37] | yes |
| luna | b_list | 96.4 | 46.1% | 71.3 | 0.74 | [0.47, 1.06] | no |
| luna | b_shot | 8.7 | 4.2% | -3.5 | -0.40 | [-8.19, no upper limit] | no |
| luna | b_evidence | -89.5 | -42.8% | -10.5 | - (adds wrong values) | - | no |
| luna | verify | 169.4 | 81.0% | 272.5 | 1.61 | [1.32, 1.95] | no |
| luna | verify_no_only (post hoc) | 85.7 | 41.0% | 149.7 | 1.75 | [1.33, 2.33] | no |
| opus | b_list | 47.0 | 28.7% | 35.1 | 0.75 | [0.30, 1.60] | no |
| opus | verify | 112.1 | 68.3% | 159.1 | 1.42 | [1.06, 1.87] | no |
| opus | verify_no_only (post hoc) | 56.7 | 34.6% | 46.8 | 0.83 | [0.46, 1.35] | no |
| astra | b_list | 44.5 | 11.9% | 21.1 | 0.47 | [0.20, 1.03] | no |
| astra | verify | 308.1 | 82.5% | 205.8 | 0.67 | [0.54, 0.81] | no |
| astra | verify_no_only (post hoc) | 194.8 | 52.2% | 49.1 | 0.25 | [0.15, 0.37] | yes |

Reference (post hoc): the ratio of a repair that deletes baseline `hotel` values at random, correct values lost per wrong value removed: sonnet 2.64, haiku 5.79, sol 1.46, luna 2.11, opus 3.02, astra 1.44.

### B-evidence: the labels of the wrong `hotel` values (no type and guesthouse groups)

| Model | Wrong hotel values (raw) | Labelled stated requirement | Quote given | Quote verbatim |
|---|---|---|---|---|
| sonnet | 234 | 186 (79.5%) | 234 | 234 (100.0%) |
| haiku | 123 | 88 (71.5%) | 123 | 121 (98.4%) |
| sol | 485 | 324 (66.8%) | 485 | 485 (100.0%) |
| luna | 502 | 484 (96.4%) | 502 | 496 (98.8%) |

### The verifier's answers ("Does the traveller exclude guesthouses?")

| Model | Group and baseline value | yes | no | unclear |
|---|---|---|---|---|
| sonnet | S1t, baseline hotel and guesthouse | 0 | 1 | 0 |
| sonnet | S1t, baseline hotel only | 3 | 61 | 53 |
| sonnet | S1t, baseline no hotel | 1 | 548 | 140 |
| sonnet | S2, baseline hotel and guesthouse | 0 | 2 | 0 |
| sonnet | S2, baseline hotel only | 89 | 37 | 67 |
| sonnet | S2, baseline no hotel | 1 | 21 | 16 |
| sonnet | S3, baseline hotel and guesthouse | 0 | 15 | 0 |
| sonnet | S3, baseline hotel only | 0 | 7 | 0 |
| sonnet | S3, baseline no hotel | 2 | 370 | 0 |
| haiku | S1t, baseline hotel and guesthouse | 3 | 2 | 1 |
| haiku | S1t, baseline hotel only | 37 | 7 | 4 |
| haiku | S1t, baseline no hotel | 89 | 921 | 550 |
| haiku | S2, baseline hotel only | 205 | 40 | 18 |
| haiku | S2, baseline no hotel | 20 | 83 | 100 |
| haiku | S3, baseline hotel and guesthouse | 1 | 18 | 0 |
| haiku | S3, baseline hotel only | 4 | 9 | 0 |
| haiku | S3, baseline no hotel | 41 | 708 | 7 |
| sol | S1t, baseline hotel and guesthouse | 0 | 2 | 0 |
| sol | S1t, baseline hotel only | 65 | 144 | 64 |
| sol | S1t, baseline no hotel | 1 | 379 | 152 |
| sol | S2, baseline hotel and guesthouse | 2 | 2 | 0 |
| sol | S2, baseline hotel only | 160 | 21 | 46 |
| sol | S2, baseline no hotel | 0 | 1 | 1 |
| sol | S3, baseline hotel and guesthouse | 0 | 9 | 0 |
| sol | S3, baseline hotel only | 0 | 16 | 0 |
| sol | S3, baseline no hotel | 0 | 369 | 0 |
| luna | S1t, baseline hotel and guesthouse | 0 | 12 | 0 |
| luna | S1t, baseline hotel only | 11 | 119 | 136 |
| luna | S1t, baseline no hotel | 1 | 796 | 539 |
| luna | S2, baseline hotel and guesthouse | 0 | 17 | 1 |
| luna | S2, baseline hotel only | 127 | 128 | 105 |
| luna | S2, baseline no hotel | 0 | 17 | 71 |
| luna | S3, baseline hotel and guesthouse | 0 | 41 | 0 |
| luna | S3, baseline hotel only | 0 | 20 | 0 |
| luna | S3, baseline no hotel | 2 | 721 | 2 |
| opus | S1t, baseline hotel and guesthouse | 0 | 4 | 0 |
| opus | S1t, baseline hotel only | 20 | 43 | 44 |
| opus | S1t, baseline no hotel | 3 | 629 | 64 |
| opus | S2, baseline hotel and guesthouse | 1 | 8 | 0 |
| opus | S2, baseline hotel only | 135 | 20 | 48 |
| opus | S2, baseline no hotel | 2 | 11 | 8 |
| opus | S3, baseline hotel and guesthouse | 0 | 18 | 0 |
| opus | S3, baseline hotel only | 0 | 3 | 1 |
| opus | S3, baseline no hotel | 0 | 372 | 0 |
| astra | S1t, baseline hotel and guesthouse | 0 | 2 | 0 |
| astra | S1t, baseline hotel only | 41 | 143 | 92 |
| astra | S1t, baseline no hotel | 2 | 373 | 154 |
| astra | S2, baseline hotel and guesthouse | 1 | 2 | 0 |
| astra | S2, baseline hotel only | 139 | 21 | 67 |
| astra | S2, baseline no hotel | 1 | 2 | 0 |
| astra | S3, baseline hotel and guesthouse | 0 | 10 | 0 |
| astra | S3, baseline hotel only | 0 | 15 | 0 |
| astra | S3, baseline no hotel | 0 | 369 | 0 |

### Predictions

| # | Words | Value | Held |
|---|---|---|---|
| B1 | B-list meets the trade rule on at least 2 of the 4 models | [] | failed |
| B2 | B-evidence labels at least 80% of the wrong type = hotel values as stated requirement, so it does not meet the rule on Claude | {"sonnet": 0.7948717948717948, "haiku": 0.7154471544715447, "sol": 0.668041237113402, "luna": 0.9641434262948207} | failed |
| B3 | B-verify meets the trade rule on at least 2 of the 4 models | [] | failed |
| B5 | B-shot removes at least 50% of the F0 wrong values on at least 2 of the 4 models, and it meets the full trade rule on 1 model or more | {"removes_half": [], "meets": []} | failed |
| B4 | Sol's B-define loses 0.50 correct values or fewer per wrong value removed | "see b_define rows: S1t has no fresh b_define read, so the locked ratio needs the earlier S1 definition reads; reported separately" | - |
