## 2. Tool calls at the agent's timing (experiment A)

Exploratory. 554 prefixes up to the first traveller turn that says "hotel" (355 guesthouse bookings, 199 hotel bookings). Prefixes whose brief sets no type: 448; of those, the brief names no venue: 234; no hotel fits the brief: 254.

### Rate of `type = hotel` per arm (valid reads, 95% interval)

| Model | P0 (form) | T0 (tool) | T1 (renamed tool) | T0+ask |
|---|---|---|---|---|
| sonnet | 31.3% [27.7%, 35.0%] | 28.0% [24.3%, 31.5%] | 3.9% [2.3%, 5.5%] | 24.2% [20.7%, 27.6%] |
| haiku | 6.4% [4.5%, 8.4%] | 8.3% [6.2%, 10.5%] | 2.2% [1.1%, 3.4%] | 7.8% [5.7%, 10.1%] |
| opus | 36.4% [32.5%, 40.2%] | 33.6% [30.0%, 37.4%] | 7.1% [5.1%, 9.1%] | 24.6% [21.3%, 27.9%] |
| sol | 44.1% [40.1%, 48.0%] | 44.0% [39.9%, 47.8%] | 14.5% [11.8%, 17.3%] | 42.4% [38.4%, 46.5%] |
| luna | 26.2% [22.6%, 29.6%] | 22.7% [19.5%, 26.0%] | 1.4% [0.5%, 2.5%] | 21.8% [18.5%, 25.1%] |
| astra | 46.0% [41.9%, 49.8%] | 45.8% [41.7%, 49.8%] | 7.2% [5.2%, 9.4%] | 43.1% [39.0%, 47.1%] |

### Paired contrasts (per-dialogue means; sign test over dialogues)

| Model | Contrast | Dialogues | Mean, points | 95% interval | Higher | Lower | Sign p |
|---|---|---|---|---|---|---|---|
| sonnet | t0_minus_p0 | 554 | -3.4 | [-5.7, -1.0] | 21 | 46 | 0.0031 |
| sonnet | t1_minus_t0 | 554 | -24.1 | [-27.4, -20.7] | 1 | 145 | 3.3e-42 |
| sonnet | t0ask_minus_t0 | 554 | -3.8 | [-5.3, -2.3] | 6 | 42 | 1e-07 |
| sonnet | t1_minus_t0_no_type | 448 | -19.1 | [-22.8, -15.6] | 1 | 92 | 1.9e-26 |
| haiku | t0_minus_p0 | 553 | +1.9 | [+0.0, +3.9] | 24 | 14 | 0.14 |
| haiku | t1_minus_t0 | 553 | -6.1 | [-8.0, -4.3] | 0 | 42 | 4.5e-13 |
| haiku | t0ask_minus_t0 | 553 | -0.6 | [-1.5, +0.2] | 7 | 13 | 0.26 |
| haiku | t1_minus_t0_no_type | 448 | -5.8 | [-7.9, -3.9] | 0 | 32 | 4.7e-10 |
| opus | t0_minus_p0 | 554 | -2.8 | [-5.1, -0.5] | 34 | 55 | 0.033 |
| opus | t1_minus_t0 | 554 | -26.4 | [-30.0, -23.0] | 3 | 173 | 1.9e-47 |
| opus | t0ask_minus_t0 | 554 | -8.9 | [-11.5, -6.6] | 19 | 86 | 2.3e-11 |
| opus | t1_minus_t0_no_type | 448 | -21.9 | [-25.7, -18.3] | 1 | 115 | 2.8e-33 |
| sol | t0_minus_p0 | 554 | -0.1 | [-1.3, +1.0] | 21 | 24 | 0.77 |
| sol | t1_minus_t0 | 554 | -29.5 | [-33.0, -25.9] | 0 | 194 | 8e-59 |
| sol | t0ask_minus_t0 | 554 | -1.6 | [-2.9, -0.1] | 17 | 31 | 0.059 |
| sol | t1_minus_t0_no_type | 448 | -24.0 | [-27.8, -20.3] | 0 | 129 | 2.9e-39 |
| luna | t0_minus_p0 | 554 | -3.4 | [-5.1, -1.8] | 8 | 36 | 2.5e-05 |
| luna | t1_minus_t0 | 554 | -21.3 | [-24.5, -17.9] | 0 | 132 | 3.7e-40 |
| luna | t0ask_minus_t0 | 554 | -0.9 | [-2.5, +0.7] | 21 | 30 | 0.26 |
| luna | t1_minus_t0_no_type | 448 | -18.2 | [-21.7, -14.8] | 0 | 91 | 8.1e-28 |
| astra | t0_minus_p0 | 554 | -0.2 | [-2.2, +1.6] | 14 | 15 | 1 |
| astra | t1_minus_t0 | 554 | -38.6 | [-42.4, -34.5] | 0 | 214 | 7.6e-65 |
| astra | t0ask_minus_t0 | 554 | -2.7 | [-4.5, -1.1] | 5 | 20 | 0.0041 |
| astra | t1_minus_t0_no_type | 448 | -31.0 | [-35.3, -27.0] | 0 | 139 | 2.9e-42 |

### Cost of the call (prefixes whose brief sets no type for search failure)

| Model | Search failure T0 | Search failure T1 | Hidden share T0 (mean) | Booked guesthouse missing T0 | Precision of hotel (T0; base 35.9%) | Ask share (T0+ask) | No tool call T0 | Invalid T0 |
|---|---|---|---|---|---|---|---|---|
| sonnet | 10.7% [8.0%, 13.8%] | 1.1% [0.2%, 2.2%] | 15.2% | 33.9% [29.0%, 38.7%] | 38.9% (181/465) | 4.5% | 0.2% | 0.0% |
| haiku | 3.1% [1.7%, 4.8%] | 0.2% [0.0%, 0.7%] | 6.8% | 23.0% [18.7%, 27.3%] | 43.5% (40/92) | 6.4% | 2.9% | 0.4% |
| opus | 11.9% [9.0%, 15.0%] | 1.3% [0.4%, 2.5%] | 16.3% | 36.8% [32.1%, 41.4%] | 43.5% (162/372) | 2.5% | 0.0% | 0.0% |
| sol | 18.1% [14.6%, 21.9%] | 6.9% [4.8%, 9.4%] | 23.3% | 47.8% [42.8%, 52.7%] | 38.0% (278/731) | 2.7% | 0.0% | 0.0% |
| luna | 9.5% [6.9%, 12.4%] | 0.1% [0.0%, 0.3%] | 12.7% | 32.4% [27.6%, 37.0%] | 38.9% (98/252) | 4.2% | 0.0% | 0.0% |
| astra | 19.0% [15.4%, 22.8%] | 2.7% [1.3%, 4.2%] | 24.1% | 49.6% [44.5%, 54.9%] | 38.6% (98/254) | 3.4% | 0.0% | 0.0% |

### The relaxation check (T0 searches on the no-type prefixes; no brief needed)

| Model | Calls | Flagged (empty with type, not empty without) | Search failures | Failures flagged |
|---|---|---|---|---|
| sonnet | 1343 | 68 | 144 | 63 |
| haiku | 865 | 22 | 28 | 18 |
| opus | 896 | 36 | 107 | 31 |
| sol | 1344 | 105 | 243 | 94 |
| luna | 896 | 36 | 85 | 35 |
| astra | 448 | 38 | 85 | 35 |

### Step 2: the agent sees its own search result

| Model | Result | Reads | New search, no hotel-only filter | New search, filter kept | Text names a guesthouse or the limit | Other text | Neither |
|---|---|---|---|---|---|---|---|
| sonnet | nonempty | 219 | 0 (0.0%) | 0 (0.0%) | 47 (21.5%) | 172 (78.5%) | 0 (0.0%) |
| sonnet | empty | 88 | 23 (26.1%) | 1 (1.1%) | 63 (71.6%) | 1 (1.1%) | 0 (0.0%) |
| haiku | nonempty | 39 | 0 (0.0%) | 0 (0.0%) | 3 (7.7%) | 36 (92.3%) | 0 (0.0%) |
| haiku | empty | 49 | 11 (22.4%) | 2 (4.1%) | 24 (49.0%) | 12 (24.5%) | 0 (0.0%) |
| opus | nonempty | 132 | 0 (0.0%) | 0 (0.0%) | 24 (18.2%) | 104 (78.8%) | 4 (3.0%) |
| opus | empty | 47 | 3 (6.4%) | 0 (0.0%) | 41 (87.2%) | 3 (6.4%) | 0 (0.0%) |
| sol | nonempty | 351 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 348 (99.1%) | 3 (0.9%) |
| sol | empty | 134 | 0 (0.0%) | 0 (0.0%) | 35 (26.1%) | 98 (73.1%) | 1 (0.7%) |
| luna | nonempty | 179 | 15 (8.4%) | 66 (36.9%) | 0 (0.0%) | 49 (27.4%) | 49 (27.4%) |
| luna | empty | 70 | 7 (10.0%) | 46 (65.7%) | 0 (0.0%) | 13 (18.6%) | 4 (5.7%) |
| astra | nonempty | 183 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 183 (100.0%) | 0 (0.0%) |
| astra | empty | 70 | 0 (0.0%) | 0 (0.0%) | 17 (24.3%) | 53 (75.7%) | 0 (0.0%) |

### Predictions

| # | Words | Value | Held |
|---|---|---|---|
| A1 | in T0 the Sonnet rate is within 10 points of P0 | -3.369434416365824 | held |
| A2 | T1 is lower than T0 for every model (sign test over dialogues, p < 0.01) | {"sonnet": [-0.24127557160048133, 3.29585398809197e-42], "haiku": [-0.06148282097649186, 4.547473508864641e-13], "opus": [-0.2644404332129964, 1.8976149179245744e-47], "sol": [-0.29482551143200963, 7.965459555662261e-59], "luna": [-0.21299638989169675, 3.6734198463196485e-40], "astra": [-0.3862815884476534, 7.596454196607839e-65]} | held |
| A3 | the booked venue is missing in at least 15% of the guesthouse-booked T0 reads for Sonnet, Sol and Luna | {"sonnet": 0.3389671361502347, "sol": 0.4779342723004695, "luna": 0.323943661971831} | held |
| A3b | on the prefixes whose brief sets no type, at least 8% of all T0 reads are a search failure, for Sonnet and for Sol | {"sonnet": 0.10714285714285714, "sol": 0.18080357142857142} | held |
| A4 | ask_traveller is called in less than 10% of T0+ask reads, and the rate of type = hotel falls by 5 points or less against T0 | {"sonnet": [0.044524669073405534, -0.03790613718411551], "haiku": [0.06407942238267147, -0.005716004813477726], "opus": [0.02527075812274368, -0.08935018050541516], "sol": [0.02707581227436823, -0.015643802647412774], "luna": [0.04151624548736462, -0.009025270758122761], "astra": [0.03429602888086643, -0.027075812274368227]} | failed |
| A5 | when the step-2 result holds 1 or more venues, the model searches again without the filter in less than 10% of reads, for every model | {"sonnet": 0.0, "haiku": 0.0, "opus": 0.0, "sol": 0.0, "luna": 0.08379888268156424, "astra": 0.0} | held |
