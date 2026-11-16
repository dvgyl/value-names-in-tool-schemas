## Search-side outcomes (exploratory, post hoc)

### The relaxation check by what the brief sets (T0 searches, 554 prefixes)

| Model | Brief | Searches | Flags | Flags on a search failure |
|---|---|---|---|---|
| sonnet | no type | 1343 | 68 | 63 |
| sonnet | hotel | 175 | 0 | 0 |
| sonnet | guesthouse | 141 | 30 | 27 |
| haiku | no type | 865 | 22 | 18 |
| haiku | hotel | 115 | 0 | 0 |
| haiku | guesthouse | 92 | 10 | 8 |
| opus | no type | 896 | 36 | 31 |
| opus | hotel | 118 | 0 | 0 |
| opus | guesthouse | 94 | 21 | 19 |
| sol | no type | 1344 | 105 | 94 |
| sol | hotel | 177 | 3 | 0 |
| sol | guesthouse | 141 | 39 | 36 |
| luna | no type | 896 | 36 | 35 |
| luna | hotel | 118 | 2 | 0 |
| luna | guesthouse | 94 | 14 | 12 |
| astra | no type | 448 | 38 | 35 |
| astra | hotel | 59 | 1 | 0 |
| astra | guesthouse | 47 | 13 | 12 |

### Repairs: search failure (brief sets no type, 807) and hotel-only filter kept (brief sets hotel, 233)

| Model | Arm | Search failure | Hotel-only filter kept where the brief sets hotel |
|---|---|---|---|
| sonnet | f0 | 50/807 (6.2%) | 193/233 (82.8%) |
| sonnet | b_list | 37/807 (4.6%) | 171/233 (73.4%) |
| sonnet | b_shot | 44/807 (5.5%) | 194/233 (83.3%) |
| sonnet | b_evidence | 70/807 (8.7%) | 201/233 (86.3%) |
| sonnet | verify | 1/807 (0.1%) | 89/233 (38.2%) |
| sonnet | verify_no_only (post hoc) | 16/807 (2.0%) | 156/233 (67.0%) |
| haiku | f0 | 9/1614 (0.6%) | 263/466 (56.4%) |
| haiku | b_list | 18/1614 (1.1%) | 287/466 (61.6%) |
| haiku | b_shot | 7/1614 (0.4%) | 283/466 (60.7%) |
| haiku | b_evidence | 19/1614 (1.2%) | 296/466 (63.5%) |
| haiku | verify | 8/1614 (0.5%) | 205/466 (44.0%) |
| haiku | verify_no_only (post hoc) | 9/1614 (0.6%) | 223/466 (47.9%) |
| sol | f0 | 127/807 (15.7%) | 227/233 (97.4%) |
| sol | b_list | 130/807 (16.1%) | 221/233 (94.8%) |
| sol | b_shot | 56/807 (6.9%) | 195/233 (83.7%) |
| sol | b_evidence | 132/807 (16.4%) | 225/233 (96.6%) |
| sol | verify | 16/807 (2.0%) | 160/233 (68.7%) |
| sol | b_define | - | 166/233 (71.2%) |
| sol | verify_no_only (post hoc) | 27/807 (3.3%) | 206/233 (88.4%) |
| luna | f0 | 99/1614 (6.1%) | 360/466 (77.3%) |
| luna | b_list | 54/1614 (3.3%) | 317/466 (68.0%) |
| luna | b_shot | 99/1614 (6.1%) | 377/466 (80.9%) |
| luna | b_evidence | 198/1614 (12.3%) | 366/466 (78.5%) |
| luna | verify | 2/1614 (0.1%) | 127/466 (27.3%) |
| luna | b_define | - | 310/466 (66.5%) |
| luna | verify_no_only (post hoc) | 38/1614 (2.4%) | 232/466 (49.8%) |
| opus | f0 | 36/807 (4.5%) | 203/233 (87.1%) |
| opus | b_list | 26/807 (3.2%) | 197/233 (84.5%) |
| opus | verify | 4/807 (0.5%) | 135/233 (57.9%) |
| opus | verify_no_only (post hoc) | 15/807 (1.9%) | 183/233 (78.5%) |
| astra | f0 | 128/807 (15.9%) | 227/233 (97.4%) |
| astra | b_list | 111/807 (13.8%) | 221/233 (94.8%) |
| astra | verify | 6/807 (0.7%) | 139/233 (59.7%) |
| astra | verify_no_only (post hoc) | 29/807 (3.6%) | 206/233 (88.4%) |

### Repairs: extra visible losses per search failure avoided (post hoc; review round 3, N1)

A visible loss: on a dialogue whose brief sets hotel, the answer keeps no hotel-only filter and the first 5 rows of its own search hold no hotel that fits the brief. Rates are per answer; the ratio uses the subset sizes (807 no-type briefs, 233 hotel briefs): (visible-loss rate of the arm - of F0) x 233 / ((search-failure rate of F0 - of the arm) x 807).

| Model | Arm | Search failure | Visible loss | Extra visible losses per search failure avoided |
|---|---|---|---|---|
| sonnet | f0 | 50/807 (6.2%) | 13/233 (5.6%) | - |
| sonnet | b_list | 37/807 (4.6%) | 12/233 (5.2%) | -0.08 |
| sonnet | b_shot | 44/807 (5.5%) | 9/233 (3.9%) | -0.67 |
| sonnet | b_evidence | 70/807 (8.7%) | 7/233 (3.0%) | - (no search failure avoided) |
| sonnet | verify | 1/807 (0.1%) | 32/233 (13.7%) | 0.39 |
| sonnet | verify_no_only (post hoc) | 16/807 (2.0%) | 18/233 (7.7%) | 0.15 |
| haiku | f0 | 9/1614 (0.6%) | 48/466 (10.3%) | - |
| haiku | b_list | 18/1614 (1.1%) | 35/466 (7.5%) | - (no search failure avoided) |
| haiku | b_shot | 7/1614 (0.4%) | 45/466 (9.7%) | -1.50 |
| haiku | b_evidence | 19/1614 (1.2%) | 48/466 (10.3%) | - (no search failure avoided) |
| haiku | verify | 8/1614 (0.5%) | 65/466 (13.9%) | 17.00 |
| haiku | verify_no_only (post hoc) | 9/1614 (0.6%) | 60/466 (12.9%) | - (no search failure avoided) |
| sol | f0 | 127/807 (15.7%) | 3/233 (1.3%) | - |
| sol | b_list | 130/807 (16.1%) | 3/233 (1.3%) | - (no search failure avoided) |
| sol | b_shot | 56/807 (6.9%) | 12/233 (5.2%) | 0.13 |
| sol | b_evidence | 132/807 (16.4%) | 3/233 (1.3%) | - (no search failure avoided) |
| sol | verify | 16/807 (2.0%) | 15/233 (6.4%) | 0.11 |
| sol | b_define | - | 16/233 (6.9%) | - (no search failure avoided) |
| sol | verify_no_only (post hoc) | 27/807 (3.3%) | 6/233 (2.6%) | 0.03 |
| luna | f0 | 99/1614 (6.1%) | 21/466 (4.5%) | - |
| luna | b_list | 54/1614 (3.3%) | 37/466 (7.9%) | 0.36 |
| luna | b_shot | 99/1614 (6.1%) | 23/466 (4.9%) | - (no search failure avoided) |
| luna | b_evidence | 198/1614 (12.3%) | 26/466 (5.6%) | - (no search failure avoided) |
| luna | verify | 2/1614 (0.1%) | 81/466 (17.4%) | 0.62 |
| luna | b_define | - | 44/466 (9.4%) | - (no search failure avoided) |
| luna | verify_no_only (post hoc) | 38/1614 (2.4%) | 53/466 (11.4%) | 0.52 |
| opus | f0 | 36/807 (4.5%) | 11/233 (4.7%) | - |
| opus | b_list | 26/807 (3.2%) | 9/233 (3.9%) | -0.20 |
| opus | verify | 4/807 (0.5%) | 17/233 (7.3%) | 0.19 |
| opus | verify_no_only (post hoc) | 15/807 (1.9%) | 11/233 (4.7%) | 0.00 |
| astra | f0 | 128/807 (15.9%) | 3/233 (1.3%) | - |
| astra | b_list | 111/807 (13.8%) | 4/233 (1.7%) | 0.06 |
| astra | verify | 6/807 (0.7%) | 20/233 (8.6%) | 0.14 |
| astra | verify_no_only (post hoc) | 29/807 (3.6%) | 7/233 (3.0%) | 0.04 |
