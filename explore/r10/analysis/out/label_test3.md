# Label test in the tool channel (R10-21)

Exploratory, fixed in the protocol before the run. Contrasts in points, paired by prefix: D_c = tl_code − tl_hotel, D_n = tl_neutral − tl_hotel, D_nc = tl_neutral − tl_code. Sets: no-type 448, hotel-brief 59, guesthouse-brief 47 (description). On the hotel-brief set the search failure is 0 by construction.

## Predictions (primary outcome, no-type prefixes)

- T1 (panel D_c ≤ −3 with the interval below 0): holds; shared word acts
- T2 (panel D_n ≤ −3 with the interval below 0): holds; shared word acts
- T3 (the whole interval of the panel D_nc inside ±3): fails; unresolved
- Holm-adjusted p of T1 and T2 (description): 0.0002, 0.0002

## Outcome: hotel

### D_c = tl_code − tl_hotel

| Model | Set | tl_code % (n) | tl_hotel % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 28.4 (448) | 35.3 (448) | 448 | -6.8 | [-8.9, -5.1] | 0.0001 | 1/55 |
| luna | no_type | 2.3 (448) | 19.3 (448) | 448 | -17.0 | [-20.4, -13.8] | 0.0001 | 1/92 |
| panel | no_type |  |  | 448 | -11.9 | [-13.8, -10.2] | 0.0001 | 2/140 |
| sol | hotel_brief | 66.7 (59) | 87.6 (59) | 59 | -20.9 | [-29.4, -13.0] | 0.0001 | 0/21 |
| luna | hotel_brief | 4.7 (59) | 37.7 (59) | 59 | -33.1 | [-45.3, -22.0] | 0.0001 | 0/25 |
| panel | hotel_brief |  |  | 59 | -27.0 | [-32.2, -21.8] | 0.0001 | 0/44 |
| sol | guesthouse | 64.5 (47) | 74.5 (47) | 47 | -9.9 | [-16.3, -4.3] | 0.0051 | 1/11 |
| luna | guesthouse | 10.6 (47) | 46.3 (47) | 47 | -35.6 | [-48.9, -22.9] | 0.0001 | 0/20 |
| panel | guesthouse |  |  | 47 | -22.8 | [-30.0, -15.9] | 0.0001 | 0/27 |

### D_n = tl_neutral − tl_hotel

| Model | Set | tl_neutral % (n) | tl_hotel % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 24.6 (448) | 35.3 (448) | 448 | -10.7 | [-13.2, -8.3] | 0.0001 | 1/76 |
| luna | no_type | 1.7 (448) | 19.3 (448) | 448 | -17.6 | [-21.0, -14.3] | 0.0001 | 0/95 |
| panel | no_type |  |  | 448 | -14.2 | [-16.3, -12.1] | 0.0001 | 1/156 |
| sol | hotel_brief | 58.2 (59) | 87.6 (59) | 59 | -29.4 | [-39.5, -19.2] | 0.0001 | 0/24 |
| luna | hotel_brief | 2.5 (59) | 37.7 (59) | 59 | -35.2 | [-47.9, -23.3] | 0.0001 | 0/25 |
| panel | hotel_brief |  |  | 59 | -32.3 | [-37.6, -26.9] | 0.0001 | 0/47 |
| sol | guesthouse | 63.1 (47) | 74.5 (47) | 47 | -11.3 | [-19.1, -5.0] | 0.0050 | 1/11 |
| luna | guesthouse | 10.6 (47) | 46.3 (47) | 47 | -35.6 | [-48.9, -22.9] | 0.0001 | 0/20 |
| panel | guesthouse |  |  | 47 | -23.5 | [-30.0, -17.2] | 0.0001 | 0/29 |

### D_nc = tl_neutral − tl_code

| Model | Set | tl_neutral % (n) | tl_code % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 24.6 (448) | 28.4 (448) | 448 | -3.9 | [-5.4, -2.5] | 0.0001 | 11/48 |
| luna | no_type | 1.7 (448) | 2.3 (448) | 448 | -0.6 | [-1.3, -0.2] | 0.0336 | 0/6 |
| panel | no_type |  |  | 448 | -2.2 | [-3.1, -1.5] | 0.0001 | 11/54 |
| sol | hotel_brief | 58.2 (59) | 66.7 (59) | 59 | -8.5 | [-15.8, -1.7] | 0.0371 | 5/12 |
| luna | hotel_brief | 2.5 (59) | 4.7 (59) | 59 | -2.1 | [-4.7, -0.4] | 0.1272 | 0/4 |
| panel | hotel_brief |  |  | 59 | -5.3 | [-9.2, -1.7] | 0.0068 | 5/16 |
| sol | guesthouse | 63.1 (47) | 64.5 (47) | 47 | -1.4 | [-8.5, 5.0] | 0.8495 | 5/7 |
| luna | guesthouse | 10.6 (47) | 10.6 (47) | 47 | 0.0 | [0.0, 0.0] | 1.0000 | 0/0 |
| panel | guesthouse |  |  | 47 | -0.7 | [-4.3, 2.5] | 0.8495 | 5/7 |

## Outcome: hotel_only

### D_c = tl_code − tl_hotel

| Model | Set | tl_code % (n) | tl_hotel % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 28.4 (448) | 35.3 (448) | 448 | -6.8 | [-8.9, -5.1] | n/a | 1/55 |
| luna | no_type | 2.2 (448) | 19.3 (448) | 448 | -17.0 | [-20.3, -13.8] | n/a | 0/92 |
| panel | no_type |  |  | 448 | -11.9 | [-13.8, -10.2] | n/a | 1/140 |
| sol | hotel_brief | 66.7 (59) | 87.6 (59) | 59 | -20.9 | [-29.4, -13.0] | n/a | 0/21 |
| luna | hotel_brief | 4.7 (59) | 37.7 (59) | 59 | -33.1 | [-45.3, -22.0] | n/a | 0/25 |
| panel | hotel_brief |  |  | 59 | -27.0 | [-32.2, -21.8] | n/a | 0/44 |
| sol | guesthouse | 62.4 (47) | 72.3 (47) | 47 | -9.9 | [-16.3, -4.3] | n/a | 1/11 |
| luna | guesthouse | 8.5 (47) | 44.1 (47) | 47 | -35.6 | [-48.9, -22.9] | n/a | 0/20 |
| panel | guesthouse |  |  | 47 | -22.8 | [-30.0, -15.9] | n/a | 0/27 |

### D_n = tl_neutral − tl_hotel

| Model | Set | tl_neutral % (n) | tl_hotel % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 24.6 (448) | 35.3 (448) | 448 | -10.7 | [-13.2, -8.3] | n/a | 1/76 |
| luna | no_type | 1.7 (448) | 19.3 (448) | 448 | -17.6 | [-20.9, -14.3] | n/a | 0/95 |
| panel | no_type |  |  | 448 | -14.1 | [-16.2, -12.1] | n/a | 1/156 |
| sol | hotel_brief | 58.2 (59) | 87.6 (59) | 59 | -29.4 | [-39.5, -19.2] | n/a | 0/24 |
| luna | hotel_brief | 2.5 (59) | 37.7 (59) | 59 | -35.2 | [-47.9, -23.3] | n/a | 0/25 |
| panel | hotel_brief |  |  | 59 | -32.3 | [-37.6, -26.9] | n/a | 0/47 |
| sol | guesthouse | 61.0 (47) | 72.3 (47) | 47 | -11.3 | [-19.1, -5.0] | n/a | 1/11 |
| luna | guesthouse | 8.5 (47) | 44.1 (47) | 47 | -35.6 | [-48.9, -22.9] | n/a | 0/20 |
| panel | guesthouse |  |  | 47 | -23.5 | [-30.0, -17.2] | n/a | 0/29 |

### D_nc = tl_neutral − tl_code

| Model | Set | tl_neutral % (n) | tl_code % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 24.6 (448) | 28.4 (448) | 448 | -3.9 | [-5.4, -2.5] | n/a | 11/48 |
| luna | no_type | 1.7 (448) | 2.2 (448) | 448 | -0.6 | [-1.2, -0.1] | n/a | 0/5 |
| panel | no_type |  |  | 448 | -2.2 | [-3.0, -1.5] | n/a | 11/53 |
| sol | hotel_brief | 58.2 (59) | 66.7 (59) | 59 | -8.5 | [-15.8, -1.7] | n/a | 5/12 |
| luna | hotel_brief | 2.5 (59) | 4.7 (59) | 59 | -2.1 | [-4.7, -0.4] | n/a | 0/4 |
| panel | hotel_brief |  |  | 59 | -5.3 | [-9.2, -1.7] | n/a | 5/16 |
| sol | guesthouse | 61.0 (47) | 62.4 (47) | 47 | -1.4 | [-8.5, 5.0] | n/a | 5/7 |
| luna | guesthouse | 8.5 (47) | 8.5 (47) | 47 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| panel | guesthouse |  |  | 47 | -0.7 | [-4.3, 2.5] | n/a | 5/7 |

## Outcome: search_failure

### D_c = tl_code − tl_hotel

| Model | Set | tl_code % (n) | tl_hotel % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 14.8 (448) | 18.0 (448) | 448 | -3.2 | [-4.8, -1.9] | n/a | 1/24 |
| luna | no_type | 0.8 (448) | 9.9 (448) | 448 | -9.2 | [-11.8, -6.7] | n/a | 0/51 |
| panel | no_type |  |  | 448 | -6.2 | [-7.6, -4.8] | n/a | 1/73 |
| sol | hotel_brief | 0.0 (59) | 0.0 (59) | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| luna | hotel_brief | 0.0 (59) | 0.0 (59) | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| panel | hotel_brief |  |  | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| sol | guesthouse | 47.5 (47) | 51.8 (47) | 47 | -4.3 | [-8.5, 0.0] | n/a | 1/6 |
| luna | guesthouse | 8.5 (47) | 33.5 (47) | 47 | -25.0 | [-37.2, -13.8] | n/a | 0/14 |
| panel | guesthouse |  |  | 47 | -14.6 | [-21.0, -8.8] | n/a | 0/18 |

### D_n = tl_neutral − tl_hotel

| Model | Set | tl_neutral % (n) | tl_hotel % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 12.9 (448) | 18.0 (448) | 448 | -5.1 | [-7.0, -3.4] | n/a | 1/36 |
| luna | no_type | 0.6 (448) | 9.9 (448) | 448 | -9.3 | [-12.0, -6.9] | n/a | 0/52 |
| panel | no_type |  |  | 448 | -7.2 | [-8.9, -5.6] | n/a | 1/80 |
| sol | hotel_brief | 0.0 (59) | 0.0 (59) | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| luna | hotel_brief | 0.0 (59) | 0.0 (59) | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| panel | hotel_brief |  |  | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| sol | guesthouse | 46.1 (47) | 51.8 (47) | 47 | -5.7 | [-12.1, -0.7] | n/a | 1/6 |
| luna | guesthouse | 8.5 (47) | 33.5 (47) | 47 | -25.0 | [-37.2, -13.8] | n/a | 0/14 |
| panel | guesthouse |  |  | 47 | -15.3 | [-21.7, -9.3] | n/a | 0/19 |

### D_nc = tl_neutral − tl_code

| Model | Set | tl_neutral % (n) | tl_code % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 12.9 (448) | 14.8 (448) | 448 | -1.9 | [-3.0, -1.0] | n/a | 4/23 |
| luna | no_type | 0.6 (448) | 0.8 (448) | 448 | -0.2 | [-0.4, 0.0] | n/a | 0/2 |
| panel | no_type |  |  | 448 | -1.1 | [-1.6, -0.6] | n/a | 4/25 |
| sol | hotel_brief | 0.0 (59) | 0.0 (59) | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| luna | hotel_brief | 0.0 (59) | 0.0 (59) | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| panel | hotel_brief |  |  | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| sol | guesthouse | 46.1 (47) | 47.5 (47) | 47 | -1.4 | [-6.4, 3.5] | n/a | 3/5 |
| luna | guesthouse | 8.5 (47) | 8.5 (47) | 47 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| panel | guesthouse |  |  | 47 | -0.7 | [-3.2, 1.8] | n/a | 3/5 |

## Descriptions

### Value trade against tl_hotel (wrong values removed on no-type, correct values lost on hotel-brief)

| Model | Arm | Wrong removed | Correct lost | Ratio |
|---|---|---:|---:|---|
| sol | tl_code | 30.7 | 12.3 | 0.40 |
| sol | tl_neutral | 48.0 | 17.3 | 0.36 |
| luna | tl_code | 76.3 | 19.5 | 0.26 |
| luna | tl_neutral | 79.1 | 20.8 | 0.26 |

### tl_hotel against the stored t0 (the definition on the label hotel; other batches and days)

Outcome hotel:

| Model | Set | tl_hotel % (n) | t0 (stored) % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 35.3 (448) | 35.6 (448) | 448 | -0.4 | [-1.5, 0.7] | n/a | 14/15 |
| luna | no_type | 19.3 (448) | 18.8 (448) | 448 | 0.6 | [-0.9, 2.0] | n/a | 24/14 |
| panel | no_type |  |  | 448 | 0.1 | [-0.8, 1.0] | n/a | 38/28 |
| sol | hotel_brief | 87.6 (59) | 80.8 (59) | 59 | 6.8 | [2.3, 12.4] | n/a | 8/1 |
| luna | hotel_brief | 37.7 (59) | 35.6 (59) | 59 | 2.1 | [-2.1, 6.4] | n/a | 6/3 |
| panel | hotel_brief |  |  | 59 | 4.4 | [1.1, 7.7] | n/a | 14/4 |
| sol | guesthouse | 74.5 (47) | 77.3 (47) | 47 | -2.8 | [-5.7, -0.7] | n/a | 0/4 |
| luna | guesthouse | 46.3 (47) | 44.7 (47) | 47 | 1.6 | [-2.1, 5.3] | n/a | 4/3 |
| panel | guesthouse |  |  | 47 | -0.6 | [-2.6, 1.2] | n/a | 4/6 |

Outcome hotel_only:

| Model | Set | tl_hotel % (n) | t0 (stored) % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 35.3 (448) | 35.6 (448) | 448 | -0.4 | [-1.5, 0.7] | n/a | 14/15 |
| luna | no_type | 19.3 (448) | 18.6 (448) | 448 | 0.6 | [-0.8, 2.0] | n/a | 24/13 |
| panel | no_type |  |  | 448 | 0.1 | [-0.8, 1.0] | n/a | 38/27 |
| sol | hotel_brief | 87.6 (59) | 80.8 (59) | 59 | 6.8 | [2.3, 12.4] | n/a | 8/1 |
| luna | hotel_brief | 37.7 (59) | 35.6 (59) | 59 | 2.1 | [-2.1, 6.4] | n/a | 6/3 |
| panel | hotel_brief |  |  | 59 | 4.4 | [1.1, 7.7] | n/a | 14/4 |
| sol | guesthouse | 72.3 (47) | 75.2 (47) | 47 | -2.8 | [-5.7, -0.7] | n/a | 0/4 |
| luna | guesthouse | 44.1 (47) | 42.6 (47) | 47 | 1.6 | [-2.1, 5.3] | n/a | 4/3 |
| panel | guesthouse |  |  | 47 | -0.6 | [-2.6, 1.2] | n/a | 4/6 |

Outcome search_failure:

| Model | Set | tl_hotel % (n) | t0 (stored) % (n) | pairs | D | 95% interval | perm p | up/down |
|---|---|---:|---:|---:|---:|---|---:|---:|
| sol | no_type | 18.0 (448) | 18.1 (448) | 448 | -0.1 | [-0.8, 0.6] | n/a | 5/4 |
| luna | no_type | 9.9 (448) | 9.5 (448) | 448 | 0.4 | [-0.6, 1.5] | n/a | 15/7 |
| panel | no_type |  |  | 448 | 0.2 | [-0.5, 0.8] | n/a | 20/11 |
| sol | hotel_brief | 0.0 (59) | 0.0 (59) | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| luna | hotel_brief | 0.0 (59) | 0.0 (59) | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| panel | hotel_brief |  |  | 59 | 0.0 | [0.0, 0.0] | n/a | 0/0 |
| sol | guesthouse | 51.8 (47) | 53.2 (47) | 47 | -1.4 | [-3.5, 0.0] | n/a | 0/2 |
| luna | guesthouse | 33.5 (47) | 34.0 (47) | 47 | -0.5 | [-2.7, 1.6] | n/a | 2/3 |
| panel | guesthouse |  |  | 47 | -1.0 | [-2.5, 0.4] | n/a | 2/5 |

### Stored t0 references (percent of valid reads)

| Model and set | Reads | hotel | hotel_only | search_failure |
|---|---:|---:|---:|---:|
| sol|no_type | 1344 | 35.6 | 35.6 | 18.1 |
| sol|hotel_brief | 177 | 80.8 | 80.8 | 0.0 |
| sol|guesthouse | 141 | 77.3 | 75.2 | 53.2 |
| luna|no_type | 896 | 18.8 | 18.6 | 9.5 |
| luna|hotel_brief | 118 | 35.6 | 35.6 | 0.0 |
| luna|guesthouse | 94 | 44.7 | 42.6 | 34.0 |

### Read kinds per arm

- sol: tl_code {"search": 1662}; tl_hotel {"search": 1662}; tl_neutral {"search": 1662}
- luna: tl_code {"search": 2215, "none": 1}; tl_hotel {"search": 2212, "invalid: cut": 2, "none": 2}; tl_neutral {"search": 2212, "none": 3, "invalid: cut": 1}
