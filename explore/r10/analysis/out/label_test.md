# Label test with one fixed definition (R10-18)

Exploratory, fixed in the protocol before the run. D = share(l_code) − share(l_hotel), in points.

Word rule on the 233 hotel briefs: {'unclear': 140, 'hotel_only': 89, 'guesthouse_only': 3, 'mixed': 1}.

## Outcome: hotel value

| Model | Set | l_hotel % (n) | l_code % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sonnet | no_type | 16.5 (807) | 3.1 (807) | 807 | -13.4 | [-15.9, -11.0] | 0.0001 | 0/108 |
| sonnet | hotel | 85.4 (233) | 61.8 (233) | 233 | -23.6 | [-28.8, -18.5] | 0.0001 | 0/55 |
| sonnet | stated | 100.0 (89) | 94.4 (89) | 89 | -5.6 | [-11.2, -1.1] | 0.0635 | 0/5 |
| sonnet | not_stated | 75.7 (140) | 40.0 (140) | 140 | -35.7 | [-43.6, -27.9] | 0.0001 | 0/50 |
| haiku | no_type | 4.2 (807) | 2.5 (807) | 807 | -1.7 | [-2.8, -0.7] | 0.0029 | 7/24 |
| haiku | hotel | 58.4 (233) | 48.3 (233) | 233 | -10.1 | [-14.4, -6.0] | 0.0001 | 5/37 |
| haiku | stated | 92.7 (89) | 77.5 (89) | 89 | -15.2 | [-23.0, -7.9] | 0.0001 | 2/20 |
| haiku | not_stated | 35.4 (140) | 28.2 (140) | 140 | -7.1 | [-12.1, -2.5] | 0.0065 | 3/17 |
| sol | no_type | 33.6 (807) | 28.6 (807) | 807 | -5.0 | [-6.8, -3.3] | 0.0001 | 6/46 |
| sol | hotel | 98.3 (233) | 94.8 (233) | 233 | -3.4 | [-6.0, -1.3] | 0.0075 | 0/8 |
| sol | stated | 100.0 (89) | 100.0 (89) | 89 | 0.0 | [0.0, 0.0] | 1.0000 | 0/0 |
| sol | not_stated | 97.1 (140) | 91.4 (140) | 140 | -5.7 | [-9.3, -2.1] | 0.0096 | 0/8 |
| luna | no_type | 18.0 (807) | 2.9 (807) | 807 | -15.2 | [-17.6, -12.9] | 0.0001 | 3/147 |
| luna | hotel | 80.5 (233) | 57.9 (233) | 233 | -22.5 | [-27.5, -17.8] | 0.0001 | 0/65 |
| luna | stated | 100.0 (89) | 93.8 (89) | 89 | -6.2 | [-10.7, -2.8] | 0.0038 | 0/9 |
| luna | not_stated | 67.5 (140) | 33.9 (140) | 140 | -33.6 | [-40.7, -26.1] | 0.0001 | 0/56 |
| panel | no_type | 18.1 | 9.3 | 807 | -8.8 | [-10.0, -7.7] | 0.0001 | 10/220 |
| panel | hotel | 80.6 | 65.7 | 233 | -14.9 | [-17.5, -12.6] | 0.0001 | 4/108 |
| panel | stated | 98.2 | 91.4 | 89 | -6.7 | [-9.8, -4.1] | 0.0001 | 2/23 |
| panel | not_stated | 68.9 | 48.4 | 140 | -20.5 | [-24.0, -17.2] | 0.0001 | 2/85 |

Panel value trade (l_code against l_hotel, in dialogues): removed 71.0, lost stated 6.0, lost not stated 28.8; brief 0.49 [0.39, 0.59], T1 0.08 [0.05, 0.13], T2 0.06 [0.03, 0.09].

## Outcome: hotel_only value

| Model | Set | l_hotel % (n) | l_code % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sonnet | no_type | 16.4 (807) | 3.0 (807) | 807 | -13.4 | [-15.9, -11.0] | 0.0001 | 0/108 |
| sonnet | hotel | 83.7 (233) | 60.9 (233) | 233 | -22.7 | [-28.3, -17.2] | 0.0001 | 2/55 |
| sonnet | stated | 98.9 (89) | 94.4 (89) | 89 | -4.5 | [-10.1, 0.0] | 0.2230 | 1/5 |
| sonnet | not_stated | 74.3 (140) | 38.6 (140) | 140 | -35.7 | [-43.6, -27.9] | 0.0001 | 0/50 |
| haiku | no_type | 4.0 (807) | 2.4 (807) | 807 | -1.5 | [-2.6, -0.6] | 0.0056 | 6/21 |
| haiku | hotel | 58.4 (233) | 48.3 (233) | 233 | -10.1 | [-14.4, -6.0] | 0.0001 | 5/37 |
| haiku | stated | 92.7 (89) | 77.5 (89) | 89 | -15.2 | [-23.0, -7.9] | 0.0001 | 2/20 |
| haiku | not_stated | 35.4 (140) | 28.2 (140) | 140 | -7.1 | [-12.1, -2.5] | 0.0065 | 3/17 |
| sol | no_type | 33.5 (807) | 28.4 (807) | 807 | -5.1 | [-6.9, -3.5] | 0.0001 | 5/46 |
| sol | hotel | 96.6 (233) | 93.6 (233) | 233 | -3.0 | [-5.6, -0.9] | 0.0381 | 1/8 |
| sol | stated | 100.0 (89) | 100.0 (89) | 89 | 0.0 | [0.0, 0.0] | 1.0000 | 0/0 |
| sol | not_stated | 94.3 (140) | 89.3 (140) | 140 | -5.0 | [-9.3, -0.7] | 0.0369 | 1/8 |
| luna | no_type | 17.2 (807) | 2.8 (807) | 807 | -14.4 | [-16.9, -12.2] | 0.0001 | 3/142 |
| luna | hotel | 78.1 (233) | 54.1 (233) | 233 | -24.0 | [-29.2, -19.1] | 0.0001 | 2/72 |
| luna | stated | 97.8 (89) | 91.6 (89) | 89 | -6.2 | [-11.2, -2.2] | 0.0087 | 1/10 |
| luna | not_stated | 65.7 (140) | 29.6 (140) | 140 | -36.1 | [-43.2, -28.6] | 0.0001 | 0/61 |
| panel | no_type | 17.8 | 9.1 | 807 | -8.6 | [-9.8, -7.5] | 0.0001 | 8/214 |
| panel | hotel | 79.2 | 64.2 | 233 | -15.0 | [-17.5, -12.5] | 0.0001 | 5/110 |
| panel | stated | 97.3 | 90.9 | 89 | -6.5 | [-9.6, -3.8] | 0.0001 | 3/22 |
| panel | not_stated | 67.4 | 46.4 | 140 | -21.0 | [-24.3, -17.7] | 0.0001 | 1/87 |

Panel value trade (l_code against l_hotel, in dialogues): removed 69.5, lost stated 5.8, lost not stated 29.4; brief 0.51 [0.41, 0.61], T1 0.08 [0.05, 0.13], T2 0.06 [0.03, 0.09].

## Predictions (primary outcome)

- L1: holds
- L2: holds
- L3: holds
- L4: holds
- L5 (l_code within 3 points of the stored round-9 F6 on the no-type set): sonnet holds, haiku holds, sol holds, luna holds
- Against the shared-word reading: a_inside_3 fails, b_reversed fails, c_sonnet_inside_3 fails
- Category: shared word acts (L1 holds).
- Holm-adjusted p of L1 and L3 (description): 0.0002, 0.0002.

## Reads per arm

- sonnet: l_hotel {'valid': 1040}; l_code {'valid': 1040}
- haiku: l_hotel {'valid': 2080}; l_code {'valid': 2080}
- sol: l_hotel {'valid': 1040}; l_code {'valid': 1040}
- luna: l_hotel {'valid': 2080}; l_code {'valid': 2080}

## Stored references (other runs, other days; descriptions)

| Model and form | no_type | hotel | stated | not_stated |
|---|---:|---:|---:|---:|
| sonnet|f0_round10 | 14.6 (807) | 83.7 (233) | 100.0 (89) | 72.9 (140) |
| haiku|f0_round10 | 3.3 (807) | 56.4 (233) | 89.9 (89) | 33.9 (140) |
| sol|f0_round10 | 34.1 (807) | 99.1 (233) | 100.0 (89) | 98.6 (140) |
| luna|f0_round10 | 17.2 (807) | 81.1 (233) | 100.0 (89) | 68.6 (140) |
| sonnet|f6_round9 | 2.4 (807) | 60.5 (233) | 96.1 (89) | 36.8 (140) |
| sonnet|f1_round9 | 3.0 (807) | 58.8 (233) | 94.4 (89) | 35.0 (140) |
| haiku|f6_round9 | 2.3 (807) | 48.4 (233) | 80.1 (89) | 26.7 (140) |
| haiku|f1_round9 | 0.6 (807) | 30.2 (233) | 56.2 (89) | 12.6 (140) |
| sol|f6_round9 | 27.5 (807) | n/a (0) | n/a (0) | n/a (0) |
| sol|f1_round9 | 10.4 (807) | 79.6 (103) | 100.0 (46) | 63.2 (57) |
| luna|f6_round9 | 2.7 (807) | 57.4 (233) | 94.8 (89) | 32.4 (140) |
| luna|f1_round9 | 0.9 (807) | 34.2 (233) | 61.4 (89) | 16.4 (140) |
