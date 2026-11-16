## 6. Stronger models and more reasoning (experiments E, F, G)

Exploratory. Groups: S1t (994: the traveller says "hotel" and the gold sets no type), S3 (490: gold guesthouse), S2 (545: gold hotel). S1t subsets: the brief sets no type (807); of those, the brief names no venue (423). Outcome: `type` holds `hotel`.

### Reads

| Experiment, model, reads | Folders | Not fetched | Invalid (group or source and cell) | Missing reads |
|---|---|---|---|---|
| E, opus | ere_opus | - | 0 | 0 |
| G, astra | erg_astra | - | 0 | 0 |
| F, sonnet, high | erf_sonnet | - | 0 | 0 |
| F, sonnet, baseline_f0 | erb_sonnet | - | 0 | 0 |
| F, sonnet, baseline_f1 | round-9 natural runs (natural_analyze.load) | - | 0 | 0 |
| F, haiku, high | erf_haiku, erx_f2_haiku | - | 0 | 0 |
| F, haiku, baseline_f0 | erb_haiku | - | 0 | 0 |
| F, haiku, baseline_f1 | round-9 natural runs (natural_analyze.load) | - | 0 | 0 |
| F, sol, high | erf_sol | - | 0 | 0 |
| F, sol, baseline_f0 | erb_sol | - | 0 | 0 |
| F, sol, baseline_f1 | round-9 natural runs (natural_analyze.load) | - | all round-9 groups|f0: 3; all round-9 groups|f1: 1 | 0 |
| F, luna, high | erf_luna, erx_f2_luna | - | 0 | 0 |
| F, luna, baseline_f0 | erb_luna | - | 0 | 0 |
| F, luna, baseline_f1 | round-9 natural runs (natural_analyze.load) | - | 0 | 0 |
| F, opus, high | erx_f0h_opus, erx_f1h_opus | - | 0 | 0 |
| F, opus, baseline_f0 | ere_opus | - | 0 | 0 |
| F, opus, baseline_f1 | ere_opus | - | 0 | 0 |

### E: opus as a panel model (effort low). Exploratory.

| Dialogues | F0 | F1 | F1 - F0, points [95% interval] (higher, lower, sign p) |
|---|---|---|---|
| S1t | 20.0% (199/994) [17.6%, 22.5%] | 8.9% (88/994) [7.0%, 10.6%] | -11.2 [-13.3, -9.2] (4, 115, p 2.5e-29) |
| S3 | 10.2% (50/490) [7.6%, 13.1%] | 6.5% (32/490) [4.5%, 8.8%] | -3.7 [-5.7, -1.8] (3, 21, p 0.00028) |
| S2 | 79.4% (433/545) [76.1%, 82.8%] | 58.2% (317/545) [54.1%, 62.2%] | -21.3 [-25.0, -17.8] (4, 120, p 9.1e-31) |
| S1t no type (807) | 13.8% (111/807) [11.3%, 16.1%] | 4.8% (39/807) [3.5%, 6.4%] | -8.9 [-11.0, -6.9] (1, 73, p 7.9e-21) |
| S1t no type, no name (423) | 25.3% (107/423) [21.0%, 29.6%] | 9.0% (38/423) [6.4%, 11.8%] | -16.3 [-20.1, -12.5] (1, 70, p 6.1e-20) |

Search failure on the 807 no-type dialogues of S1t (share of all valid reads): F0 4.5% (36/807) [3.1%, 5.9%]; F1 0.9% (7/807) [0.2%, 1.6%].

Trade of F1 against F0 (paired estimator; dialogues {'S1t': 994, 'S3': 490, 'S2': 545}): wrong removed 129.0 of 249.0 (51.8%); correct lost 116.0; ratio 0.90 [0.70, 1.14]; meets the trade rule: no.

### G: astra as a panel model (effort low). Exploratory.

| Dialogues | F0 | F1 | F1 - F0, points [95% interval] (higher, lower, sign p) |
|---|---|---|---|
| S1t | 42.4% (421/994) [39.3%, 45.5%] | 13.7% (136/994) [11.6%, 15.9%] | -28.7 [-31.6, -25.8] (0, 285, p 3.2e-86) |
| S3 | 12.2% (60/490) [9.4%, 15.1%] | 5.7% (28/490) [3.7%, 7.8%] | -6.5 [-8.8, -4.5] (0, 32, p 4.7e-10) |
| S2 | 91.0% (496/545) [88.4%, 93.4%] | 62.8% (342/545) [58.7%, 67.0%] | -28.3 [-31.9, -24.4] (0, 154, p 8.8e-47) |
| S1t no type (807) | 34.4% (278/807) [31.1%, 37.8%] | 9.4% (76/807) [7.6%, 11.5%] | -25.0 [-28.0, -22.1] (0, 202, p 3.1e-61) |
| S1t no type, no name (423) | 60.8% (257/423) [55.8%, 65.2%] | 17.0% (72/423) [13.5%, 20.6%] | -43.7 [-48.5, -39.0] (0, 185, p 4.1e-56) |

Search failure on the 807 no-type dialogues of S1t (share of all valid reads): F0 15.9% (128/807) [13.4%, 18.3%]; F1 3.3% (27/807) [2.2%, 4.6%].

Trade of F1 against F0 (paired estimator; dialogues {'S1t': 994, 'S3': 490, 'S2': 545}): wrong removed 317.0 of 481.0 (65.9%); correct lost 154.0; ratio 0.49 [0.41, 0.57]; meets the trade rule: no.

### F: more reasoning (high setting) against the baseline setting of the same model. Exploratory.

Baseline F0: the fresh F0 arm of experiment B (for Opus: ere_opus, effort low). Baseline F1: the round-9 natural runs (for Opus: ere_opus). Round-9 Sol S2 reads cover 229 of the 545 dialogues. The round-9 F0 column is a reference only.

| Model | Dialogues | Baseline F0 | High F0 | Baseline F1 | High F1 | Round-9 F0 (reference) |
|---|---|---|---|---|---|---|
| sonnet | S1t | 19.2% (191/994) [16.8%, 21.7%] | 21.6% (215/994) [19.0%, 24.2%] | 5.2% (154/2982) [3.9%, 6.5%] | 6.0% (60/994) [4.5%, 7.5%] | 18.4% (550/2982) [16.0%, 20.8%] |
| sonnet | S2 | 68.8% (375/545) [65.0%, 72.8%] | 69.5% (379/545) [65.5%, 73.4%] | 43.3% (472/1090) [39.4%, 47.2%] | 46.1% (251/545) [42.0%, 50.3%] | 68.6% (748/1090) [64.7%, 72.7%] |
| sonnet | S1t no type (807) | 14.6% (118/807) [12.1%, 17.1%] | 16.9% (136/807) [14.1%, 19.5%] | 3.0% (72/2421) [1.9%, 4.1%] | 3.6% (29/807) [2.4%, 4.8%] | 14.0% (339/2421) [11.6%, 16.4%] |
| sonnet | S1t no type, no name (423) | 26.5% (112/423) [22.2%, 30.7%] | 30.7% (130/423) [26.5%, 35.0%] | 5.4% (69/1269) [3.5%, 7.6%] | 6.6% (28/423) [4.5%, 9.0%] | 26.1% (331/1269) [21.9%, 30.3%] |
| haiku | S1t | 5.2% (103/1988) [3.8%, 6.5%] | 8.5% (168/1988) [6.7%, 10.0%] | 1.3% (38/2982) [0.7%, 2.0%] | 1.1% (22/1988) [0.6%, 1.8%] | 5.1% (151/2982) [3.7%, 6.4%] |
| haiku | S2 | 41.0% (447/1090) [36.9%, 45.2%] | 49.4% (539/1090) [45.5%, 53.5%] | 21.7% (355/1635) [18.5%, 25.3%] | 18.0% (196/1090) [15.0%, 21.2%] | 39.9% (652/1635) [35.8%, 43.9%] |
| haiku | S1t no type (807) | 3.3% (54/1614) [2.2%, 4.6%] | 5.1% (82/1614) [3.8%, 6.5%] | 0.6% (14/2421) [0.1%, 1.2%] | 0.5% (8/1614) [0.1%, 0.9%] | 3.1% (76/2421) [2.1%, 4.3%] |
| haiku | S1t no type, no name (423) | 5.8% (49/846) [3.7%, 8.0%] | 8.6% (73/846) [6.3%, 11.1%] | 1.1% (14/1269) [0.2%, 2.1%] | 0.7% (6/846) [0.2%, 1.3%] | 5.7% (72/1269) [3.7%, 7.9%] |
| sol | S1t | 42.0% (417/994) [38.8%, 45.1%] | 44.9% (446/994) [41.9%, 48.0%] | 14.7% (146/994) [12.6%, 16.9%] | 23.8% (237/994) [21.2%, 26.7%] | 41.6% (413/992) [38.5%, 45.0%] |
| sol | S2 | 91.0% (496/545) [88.6%, 93.4%] | 91.0% (496/545) [88.4%, 93.4%] | 62.0% (142/229) [55.9%, 68.1%] | 78.7% (429/545) [75.2%, 82.2%] | 91.7% (210/229) [88.2%, 95.2%] |
| sol | S1t no type (807) | 34.1% (275/807) [30.7%, 37.4%] | 37.7% (304/807) [34.3%, 41.1%] | 10.4% (84/807) [8.3%, 12.6%] | 18.7% (151/807) [16.0%, 21.4%] | 33.5% (270/805) [30.4%, 36.9%] |
| sol | S1t no type, no name (423) | 60.0% (254/423) [55.1%, 64.8%] | 61.9% (262/423) [57.2%, 66.4%] | 18.9% (80/423) [15.1%, 22.5%] | 34.0% (144/423) [29.6%, 38.5%] | 58.8% (248/422) [54.3%, 63.5%] |
| luna | S1t | 22.6% (450/1988) [20.0%, 25.3%] | 27.5% (547/1988) [24.9%, 30.2%] | 1.8% (53/2982) [1.0%, 2.6%] | 4.2% (84/1988) [3.1%, 5.4%] | 22.8% (680/2982) [20.3%, 25.3%] |
| luna | S2 | 68.0% (741/1090) [64.3%, 71.9%] | 72.4% (789/1090) [69.1%, 76.1%] | 24.2% (395/1635) [20.9%, 27.6%] | 39.7% (433/1090) [35.6%, 43.9%] | 68.0% (1111/1635) [64.2%, 71.9%] |
| luna | S1t no type (807) | 17.2% (278/1614) [14.6%, 19.8%] | 21.6% (349/1614) [19.1%, 24.3%] | 0.9% (22/2421) [0.3%, 1.6%] | 2.5% (41/1614) [1.5%, 3.6%] | 17.8% (430/2421) [15.4%, 20.3%] |
| luna | S1t no type, no name (423) | 30.5% (258/846) [26.4%, 34.6%] | 37.5% (317/846) [33.2%, 41.8%] | 1.7% (22/1269) [0.7%, 3.0%] | 4.5% (38/846) [2.8%, 6.4%] | 31.0% (394/1269) [27.0%, 34.9%] |
| opus (fill) | S1t | 20.0% (199/994) [17.6%, 22.5%] | 13.0% (129/994) [10.9%, 15.1%] | 8.9% (88/994) [7.0%, 10.6%] | 7.1% (71/994) [5.5%, 8.8%] | - |
| opus (fill) | S2 | 79.4% (433/545) [76.1%, 82.8%] | 67.3% (367/545) [63.3%, 71.4%] | 58.2% (317/545) [54.1%, 62.2%] | 56.1% (306/545) [52.1%, 60.4%] | - |
| opus (fill) | S1t no type (807) | 13.8% (111/807) [11.3%, 16.1%] | 7.7% (62/807) [5.8%, 9.5%] | 4.8% (39/807) [3.5%, 6.4%] | 3.3% (27/807) [2.2%, 4.6%] | - |
| opus (fill) | S1t no type, no name (423) | 25.3% (107/423) [21.0%, 29.6%] | 13.9% (59/423) [10.6%, 17.3%] | 9.0% (38/423) [6.4%, 11.8%] | 6.1% (26/423) [4.0%, 8.3%] | - |

Paired contrasts (per-dialogue means; sign test over dialogues):

| Model, dialogues, contrast | Dialogues | Mean, points | 95% interval | Higher | Lower | Sign p |
|---|---|---|---|---|---|---|
| sonnet, S1t, high_f0_minus_base_f0 | 994 | +2.4 | [+0.9, +4.1] | 45 | 21 | 0.0043 |
| sonnet, S1t, high_f1_minus_base_f1 | 994 | +0.9 | [-0.2, +1.9] | 23 | 15 | 0.26 |
| sonnet, S1t, high_f1_minus_high_f0 | 994 | -15.6 | [-18.0, -13.4] | 1 | 156 | 1.7e-45 |
| sonnet, S1t, base_f1_minus_base_f0 | 994 | -14.1 | [-16.2, -11.9] | 1 | 145 | 3.3e-42 |
| sonnet, S2, high_f0_minus_base_f0 | 545 | +0.7 | [-1.5, +2.9] | 21 | 17 | 0.63 |
| sonnet, S2, high_f1_minus_base_f1 | 545 | +2.8 | [+0.7, +5.0] | 32 | 14 | 0.011 |
| sonnet, S2, high_f1_minus_high_f0 | 545 | -23.5 | [-27.2, -19.8] | 4 | 132 | 3.2e-34 |
| sonnet, S2, base_f1_minus_base_f0 | 545 | -25.5 | [-29.1, -21.9] | 1 | 145 | 3.3e-42 |
| sonnet, S1t no type (807), high_f0_minus_base_f0 | 807 | +2.2 | [+0.6, +3.8] | 31 | 13 | 0.0096 |
| sonnet, S1t no type (807), high_f1_minus_base_f1 | 807 | +0.6 | [-0.3, +1.7] | 13 | 9 | 0.52 |
| sonnet, S1t no type (807), high_f1_minus_high_f0 | 807 | -13.3 | [-15.6, -10.9] | 1 | 108 | 3.4e-31 |
| sonnet, S1t no type (807), base_f1_minus_base_f0 | 807 | -11.6 | [-14.0, -9.4] | 1 | 97 | 6.2e-28 |
| sonnet, S1t no type, no name (423), high_f0_minus_base_f0 | 423 | +4.3 | [+1.4, +7.1] | 28 | 10 | 0.0051 |
| sonnet, S1t no type, no name (423), high_f1_minus_base_f1 | 423 | +1.2 | [-0.8, +3.1] | 13 | 9 | 0.52 |
| sonnet, S1t no type, no name (423), high_f1_minus_high_f0 | 423 | -24.1 | [-28.1, -20.1] | 1 | 103 | 1e-29 |
| sonnet, S1t no type, no name (423), base_f1_minus_base_f0 | 423 | -21.0 | [-25.0, -17.2] | 1 | 92 | 1.9e-26 |
| haiku, S1t, high_f0_minus_base_f0 | 994 | +3.3 | [+2.0, +4.6] | 58 | 18 | 4.7e-06 |
| haiku, S1t, high_f1_minus_base_f1 | 994 | -0.2 | [-0.7, +0.4] | 8 | 9 | 1 |
| haiku, S1t, high_f1_minus_high_f0 | 994 | -7.3 | [-8.9, -5.8] | 1 | 92 | 1.9e-26 |
| haiku, S1t, base_f1_minus_base_f0 | 994 | -3.9 | [-5.1, -2.7] | 1 | 46 | 6.8e-13 |
| haiku, S2, high_f0_minus_base_f0 | 545 | +8.4 | [+5.9, +11.1] | 78 | 18 | 4.4e-10 |
| haiku, S2, high_f1_minus_base_f1 | 545 | -3.7 | [-5.9, -1.5] | 31 | 62 | 0.0017 |
| haiku, S2, high_f1_minus_high_f0 | 545 | -31.5 | [-35.0, -28.0] | 0 | 211 | 6.1e-64 |
| haiku, S2, base_f1_minus_base_f0 | 545 | -19.3 | [-22.5, -16.2] | 6 | 127 | 1.3e-30 |
| haiku, S1t no type (807), high_f0_minus_base_f0 | 807 | +1.7 | [+0.4, +3.0] | 34 | 15 | 0.0094 |
| haiku, S1t no type (807), high_f1_minus_base_f1 | 807 | -0.1 | [-0.6, +0.4] | 5 | 5 | 1 |
| haiku, S1t no type (807), high_f1_minus_high_f0 | 807 | -4.6 | [-5.9, -3.3] | 1 | 51 | 2.4e-14 |
| haiku, S1t no type (807), base_f1_minus_base_f0 | 807 | -2.8 | [-3.9, -1.7] | 0 | 27 | 1.5e-08 |
| haiku, S1t no type, no name (423), high_f0_minus_base_f0 | 423 | +2.8 | [+0.6, +5.1] | 29 | 13 | 0.02 |
| haiku, S1t no type, no name (423), high_f1_minus_base_f1 | 423 | -0.4 | [-1.4, +0.5] | 4 | 5 | 1 |
| haiku, S1t no type, no name (423), high_f1_minus_high_f0 | 423 | -7.9 | [-10.3, -5.7] | 1 | 45 | 1.3e-12 |
| haiku, S1t no type, no name (423), base_f1_minus_base_f0 | 423 | -4.7 | [-6.8, -2.8] | 0 | 24 | 1.2e-07 |
| sol, S1t, high_f0_minus_base_f0 | 994 | +2.9 | [+1.5, +4.3] | 39 | 10 | 3.8e-05 |
| sol, S1t, high_f1_minus_base_f1 | 994 | +9.2 | [+7.3, +11.1] | 93 | 2 | 2.3e-25 |
| sol, S1t, high_f1_minus_high_f0 | 994 | -21.0 | [-23.5, -18.5] | 0 | 209 | 2.4e-63 |
| sol, S1t, base_f1_minus_base_f0 | 994 | -27.3 | [-30.0, -24.5] | 0 | 271 | 5.3e-82 |
| sol, S2, high_f0_minus_base_f0 | 545 | +0.0 | [-1.1, +1.1] | 5 | 5 | 1 |
| sol, S2, high_f1_minus_base_f1 | 229 | +14.8 | [+10.0, +20.5] | 39 | 5 | 1.4e-07 |
| sol, S2, high_f1_minus_high_f0 | 545 | -12.3 | [-15.0, -9.5] | 0 | 67 | 1.4e-20 |
| sol, S2, base_f1_minus_base_f0 | 229 | -28.8 | [-34.9, -23.1] | 0 | 66 | 2.7e-20 |
| sol, S1t no type (807), high_f0_minus_base_f0 | 807 | +3.6 | [+2.1, +5.1] | 36 | 7 | 9e-06 |
| sol, S1t no type (807), high_f1_minus_base_f1 | 807 | +8.3 | [+6.3, +10.3] | 69 | 2 | 2.2e-18 |
| sol, S1t no type (807), high_f1_minus_high_f0 | 807 | -19.0 | [-21.7, -16.2] | 0 | 153 | 1.8e-46 |
| sol, S1t no type (807), base_f1_minus_base_f0 | 807 | -23.7 | [-26.6, -20.8] | 0 | 191 | 6.4e-58 |
| sol, S1t no type, no name (423), high_f0_minus_base_f0 | 423 | +1.9 | [-0.2, +4.3] | 15 | 7 | 0.13 |
| sol, S1t no type, no name (423), high_f1_minus_base_f1 | 423 | +15.1 | [+11.8, +18.7] | 66 | 2 | 1.6e-17 |
| sol, S1t no type, no name (423), high_f1_minus_high_f0 | 423 | -27.9 | [-32.4, -23.9] | 0 | 118 | 6e-36 |
| sol, S1t no type, no name (423), base_f1_minus_base_f0 | 423 | -41.1 | [-45.9, -36.6] | 0 | 174 | 8.4e-53 |
| luna, S1t, high_f0_minus_base_f0 | 994 | +4.9 | [+3.1, +6.8] | 116 | 54 | 2.3e-06 |
| luna, S1t, high_f1_minus_base_f1 | 994 | +2.4 | [+1.6, +3.3] | 37 | 3 | 1.9e-08 |
| luna, S1t, high_f1_minus_high_f0 | 994 | -23.3 | [-25.8, -20.8] | 5 | 284 | 3.3e-77 |
| luna, S1t, base_f1_minus_base_f0 | 994 | -20.9 | [-23.4, -18.4] | 0 | 233 | 1.4e-70 |
| luna, S2, high_f0_minus_base_f0 | 545 | +4.4 | [+1.8, +6.9] | 68 | 34 | 0.00099 |
| luna, S2, high_f1_minus_base_f1 | 545 | +15.6 | [+13.0, +18.3] | 122 | 6 | 3.3e-29 |
| luna, S2, high_f1_minus_high_f0 | 545 | -32.7 | [-36.3, -29.0] | 1 | 215 | 4.1e-63 |
| luna, S2, base_f1_minus_base_f0 | 545 | -43.8 | [-47.7, -39.9] | 0 | 278 | 4.1e-84 |
| luna, S1t no type (807), high_f0_minus_base_f0 | 807 | +4.4 | [+2.5, +6.3] | 85 | 41 | 0.00011 |
| luna, S1t no type (807), high_f1_minus_base_f1 | 807 | +1.6 | [+0.8, +2.4] | 21 | 2 | 6.6e-05 |
| luna, S1t no type (807), high_f1_minus_high_f0 | 807 | -19.1 | [-21.7, -16.7] | 4 | 193 | 6.2e-52 |
| luna, S1t no type (807), base_f1_minus_base_f0 | 807 | -16.3 | [-18.8, -13.8] | 0 | 148 | 5.6e-45 |
| luna, S1t no type, no name (423), high_f0_minus_base_f0 | 423 | +7.0 | [+3.5, +10.4] | 70 | 35 | 0.00082 |
| luna, S1t no type, no name (423), high_f1_minus_base_f1 | 423 | +2.8 | [+1.4, +4.2] | 19 | 2 | 0.00022 |
| luna, S1t no type, no name (423), high_f1_minus_high_f0 | 423 | -33.0 | [-37.4, -28.7] | 4 | 171 | 1.6e-45 |
| luna, S1t no type, no name (423), base_f1_minus_base_f0 | 423 | -28.8 | [-32.9, -24.7] | 0 | 136 | 2.3e-41 |
| opus, S1t, high_f0_minus_base_f0 | 994 | -7.0 | [-8.9, -5.2] | 11 | 81 | 2.5e-14 |
| opus, S1t, high_f1_minus_base_f1 | 994 | -1.7 | [-3.1, -0.4] | 14 | 31 | 0.016 |
| opus, S1t, high_f1_minus_high_f0 | 994 | -5.8 | [-7.4, -4.3] | 4 | 62 | 2.1e-14 |
| opus, S1t, base_f1_minus_base_f0 | 994 | -11.2 | [-13.3, -9.2] | 4 | 115 | 2.5e-29 |
| opus, S2, high_f0_minus_base_f0 | 545 | -12.1 | [-15.2, -9.2] | 8 | 74 | 1.6e-14 |
| opus, S2, high_f1_minus_base_f1 | 545 | -2.0 | [-4.4, +0.6] | 20 | 31 | 0.16 |
| opus, S2, high_f1_minus_high_f0 | 545 | -11.2 | [-14.1, -8.4] | 6 | 67 | 3.9e-14 |
| opus, S2, base_f1_minus_base_f0 | 545 | -21.3 | [-25.0, -17.8] | 4 | 120 | 9.1e-31 |
| opus, S1t no type (807), high_f0_minus_base_f0 | 807 | -6.1 | [-8.1, -4.2] | 5 | 54 | 1.9e-11 |
| opus, S1t no type (807), high_f1_minus_base_f1 | 807 | -1.5 | [-2.7, -0.4] | 6 | 18 | 0.023 |
| opus, S1t no type (807), high_f1_minus_high_f0 | 807 | -4.3 | [-5.8, -3.0] | 1 | 36 | 5.5e-10 |
| opus, S1t no type (807), base_f1_minus_base_f0 | 807 | -8.9 | [-11.0, -6.9] | 1 | 73 | 7.9e-21 |
| opus, S1t no type, no name (423), high_f0_minus_base_f0 | 423 | -11.3 | [-14.9, -8.0] | 4 | 52 | 1.1e-11 |
| opus, S1t no type, no name (423), high_f1_minus_base_f1 | 423 | -2.8 | [-5.2, -0.7] | 6 | 18 | 0.023 |
| opus, S1t no type, no name (423), high_f1_minus_high_f0 | 423 | -7.8 | [-10.6, -5.2] | 1 | 34 | 2.1e-09 |
| opus, S1t no type, no name (423), base_f1_minus_base_f0 | 423 | -16.3 | [-20.1, -12.5] | 1 | 70 | 6.1e-20 |

Search failure on the no-type dialogues of S1t (share of all valid reads):

| Model | Baseline F0 | High F0 | Baseline F1 | High F1 |
|---|---|---|---|---|
| sonnet | 6.2% (50/807) [4.7%, 8.1%] | 7.8% (63/807) [6.1%, 9.8%] | 0.6% (14/2421) [0.1%, 1.1%] | 1.0% (8/807) [0.4%, 1.7%] |
| haiku | 0.6% (9/1614) [0.1%, 1.1%] | 0.9% (15/1614) [0.4%, 1.5%] | 0.3% (8/2421) [0.0%, 0.7%] | 0.1% (1/1614) [0.0%, 0.2%] |
| sol | 15.7% (127/807) [13.4%, 18.3%] | 17.6% (142/807) [15.0%, 20.2%] | 4.3% (35/807) [3.0%, 5.8%] | 8.6% (69/807) [6.7%, 10.5%] |
| luna | 6.1% (99/1614) [4.6%, 7.8%] | 10.7% (172/1614) [8.7%, 12.8%] | 0.2% (5/2421) [0.0%, 0.5%] | 0.8% (13/1614) [0.3%, 1.4%] |
| opus | 4.5% (36/807) [3.1%, 5.9%] | 1.7% (14/807) [0.9%, 2.7%] | 0.9% (7/807) [0.2%, 1.6%] | 0.7% (6/807) [0.2%, 1.4%] |

### Predictions (point values)

| # | Words | Value | Held |
|---|---|---|---|
| E1 | Opus F0 writes type = hotel on at least 10% of S1t, and F1 lowers it by at least 5 points | {"f0_rate_S1t": 0.2002, "f0_minus_f1_S1t": 0.1117} | held |
| G1 | Astra F0 writes type = hotel on at least 10% of S1t, and F1 lowers it by at least 5 points | {"f0_rate_S1t": 0.4235, "f0_minus_f1_S1t": 0.2867} | held |
| F1 | at effort high, the F0 rate on S1t falls by less than half of the low-effort rate for at least 3 of the 4 models | {"sonnet": {"base_f0": 0.1922, "high_f0": 0.2163, "fall": -0.0241, "half_of_base": 0.0961}, "haiku": {"base_f0": 0.0518, "high_f0": 0.0845, "fall": -0.0327, "half_of_base": 0.0259}, "sol": {"base_f0": 0.4195, "high_f0": 0.4487, "fall": -0.0292, "half_of_base": 0.2098}, "luna": {"base_f0": 0.2264, "high_f0": 0.2752, "fall": -0.0488, "half_of_base": 0.1132}, "opus": {"base_f0": 0.2002, "high_f0": 0.1298, "fall": 0.0704, "half_of_base": 0.1001}} | held |
| F2 | the F0 minus F1 gap on S1t stays at 5 points or more on every model | {"sonnet": 0.1559, "haiku": 0.0734, "sol": 0.2103, "luna": 0.2329, "opus": 0.0584} | held |
