## Full-schema validity of the stored tool calls (post hoc)

No model call. Each answer of a tool-call arm is checked against the input schema of its own condition (type, allowed values, anyOf, items, minItems, required keys, no extra keys). Raw: the arguments as stored. After normalization: after tools.clean_nulls (amendment R10-3). Non-call: no tool call.

| Run | Model | Condition | Answers | Not completed | Non-call | Other call | Search calls | Raw valid | Valid after normalization | Invalid after normalization | Problems after normalization |
|---|---|---|---|---|---|---|---|---|---|---|---|
| first request | sonnet | form (p0) | 1662 | 0 | 0 | 0 | 1662 | 1662 | 1662 | 0 | {} |
| first request | sonnet | original tool (t0) | 1662 | 0 | 3 | 0 | 1659 | 8 | 1630 | 29 | {"quoted value": 29} |
| first request | sonnet | renamed tool (t1) | 1662 | 0 | 5 | 0 | 1657 | 5 | 1636 | 21 | {"quoted value": 21} |
| first request | haiku | form (p0) | 1108 | 0 | 0 | 0 | 1108 | 1108 | 1108 | 0 | {} |
| first request | haiku | original tool (t0) | 1108 | 0 | 32 | 0 | 1076 | 44 | 996 | 80 | {"quoted value": 68, "option word in a list": 9, "other": 4} |
| first request | haiku | renamed tool (t1) | 1108 | 0 | 40 | 0 | 1068 | 35 | 992 | 76 | {"quoted value": 71, "option word in a list": 4, "other": 1} |
| first request | opus | form (p0) | 1108 | 0 | 0 | 0 | 1108 | 1108 | 1108 | 0 | {} |
| first request | opus | original tool (t0) | 1108 | 0 | 0 | 0 | 1108 | 7 | 1035 | 73 | {"quoted value": 73} |
| first request | opus | renamed tool (t1) | 1108 | 0 | 0 | 0 | 1108 | 5 | 1041 | 67 | {"quoted value": 67} |
| first request | sol | form (p0) | 1662 | 0 | 0 | 0 | 1662 | 1662 | 1662 | 0 | {} |
| first request | sol | original tool (t0) | 1662 | 0 | 0 | 0 | 1662 | 1662 | 1662 | 0 | {} |
| first request | sol | renamed tool (t1) | 1662 | 0 | 0 | 0 | 1662 | 1662 | 1662 | 0 | {} |
| first request | luna | form (p0) | 1108 | 0 | 0 | 0 | 1108 | 1108 | 1108 | 0 | {} |
| first request | luna | original tool (t0) | 1108 | 0 | 0 | 0 | 1108 | 1108 | 1108 | 0 | {} |
| first request | luna | renamed tool (t1) | 1108 | 0 | 0 | 0 | 1108 | 1108 | 1108 | 0 | {} |
| first request | astra | form (p0) | 554 | 0 | 0 | 0 | 554 | 554 | 554 | 0 | {} |
| first request | astra | original tool (t0) | 554 | 0 | 0 | 0 | 554 | 554 | 554 | 0 | {} |
| first request | astra | renamed tool (t1) | 554 | 0 | 0 | 0 | 554 | 554 | 554 | 0 | {} |
| forward release test | sonnet | original tool (t0) | 554 | 0 | 1 | 0 | 553 | 3 | 548 | 5 | {"quoted value": 4, "bare value": 1} |
| forward release test | sonnet | edited tool (tedit) | 554 | 0 | 0 | 0 | 554 | 3 | 531 | 23 | {"bare value": 1, "quoted value": 22} |
| forward release test | sol | original tool (t0) | 554 | 0 | 0 | 0 | 554 | 554 | 554 | 0 | {} |
| forward release test | sol | edited tool (tedit) | 554 | 0 | 0 | 0 | 554 | 554 | 554 | 0 | {} |
| steering run | sonnet | hotel rewrite (th) | 554 | 0 | 1 | 0 | 553 | 6 | 531 | 22 | {"quoted value": 22} |
| steering run | haiku | hotel rewrite (th) | 554 | 0 | 27 | 0 | 527 | 19 | 488 | 39 | {"quoted value": 33, "option word in a list": 8} |
| steering run | sonnet | guesthouse rewrite (tg) | 554 | 0 | 0 | 0 | 554 | 6 | 540 | 14 | {"quoted value": 14} |
| steering run | haiku | guesthouse rewrite (tg) | 554 | 0 | 24 | 0 | 530 | 17 | 502 | 28 | {"quoted value": 25, "option word in a list": 2, "bare value": 1} |
| steering run | haiku | original tool (t0) | 554 | 0 | 20 | 0 | 534 | 19 | 502 | 32 | {"quoted value": 30, "option word in a list": 2} |
| control updates | haiku | control (t0) | 1085 | 0 | 19 | 0 | 1066 | 31 | 983 | 83 | {"quoted value": 68, "option word in a list": 15} |
| control updates | haiku | repeat (trep) | 1085 | 0 | 22 | 0 | 1063 | 41 | 977 | 86 | {"option word in a list": 12, "quoted value": 73, "other": 1} |
| control updates | haiku | field-order edit (tord) | 1085 | 0 | 30 | 0 | 1055 | 25 | 996 | 59 | {"quoted value": 51, "option word in a list": 8} |

Raw problems per condition (answers with each kind):

- first request, sonnet, original tool (t0): {"value outside the allowed values": 1651}
- first request, sonnet, renamed tool (t1): {"value outside the allowed values": 1652}
- first request, haiku, original tool (t0): {"value outside the allowed values": 1032}
- first request, haiku, renamed tool (t1): {"value outside the allowed values": 1033}
- first request, opus, original tool (t0): {"value outside the allowed values": 1101}
- first request, opus, renamed tool (t1): {"value outside the allowed values": 1103}
- forward release test, sonnet, original tool (t0): {"value outside the allowed values": 550}
- forward release test, sonnet, edited tool (tedit): {"value outside the allowed values": 551}
- steering run, sonnet, hotel rewrite (th): {"value outside the allowed values": 547}
- steering run, haiku, hotel rewrite (th): {"value outside the allowed values": 508}
- steering run, sonnet, guesthouse rewrite (tg): {"value outside the allowed values": 548}
- steering run, haiku, guesthouse rewrite (tg): {"value outside the allowed values": 513}
- steering run, haiku, original tool (t0): {"value outside the allowed values": 515}
- control updates, haiku, control (t0): {"value outside the allowed values": 1035}
- control updates, haiku, repeat (trep): {"value outside the allowed values": 1022}
- control updates, haiku, field-order edit (tord): {"value outside the allowed values": 1030}

Examples of problems after normalization (at most 3 answers per condition):

- first request, sonnet, original tool (t0): $.internet: "\"any\"" not in the allowed values
- first request, sonnet, original tool (t0): $.parking: "\"any\"" not in the allowed values
- first request, sonnet, original tool (t0): $.internet: "\"any\"" not in the allowed values
- first request, sonnet, renamed tool (t1): $.parking: "\"any\"" not in the allowed values
- first request, sonnet, renamed tool (t1): $.property_kind: "\"any\"" not in the allowed values
- first request, sonnet, renamed tool (t1): $.stars: "\"any\"" not in the allowed values
- first request, haiku, original tool (t0): $.parking: "\"any\"" not in the allowed values
- first request, haiku, original tool (t0): $.pricerange: "\"any\"" not in the allowed values; $.type: "\"any\"" not in the allowed values
- first request, haiku, original tool (t0): $.internet: "\"any\"" not in the allowed values
- first request, haiku, renamed tool (t1): $.internet: "\"any\"" not in the allowed values
- first request, haiku, renamed tool (t1): $.area: "\"any\"" not in the allowed values; $.property_kind: "\"any\"" not in the allowed values
- first request, haiku, renamed tool (t1): $.pricerange: "\"any\"" not in the allowed values; $.property_kind: "\"any\"" not in the allowed values
- first request, opus, original tool (t0): $.pricerange: "\"any\"" not in the allowed values; $.internet: "\"any\"" not in the allowed values
- first request, opus, original tool (t0): $.type: "\"any\"" not in the allowed values
- first request, opus, original tool (t0): $.parking: "\"any\"" not in the allowed values
- first request, opus, renamed tool (t1): $.internet: "\"any\"" not in the allowed values
- first request, opus, renamed tool (t1): $.internet: "\"any\"" not in the allowed values
- first request, opus, renamed tool (t1): $.internet: "\"any\"" not in the allowed values
- forward release test, sonnet, original tool (t0): $.internet: "\"any\"" not in the allowed values
- forward release test, sonnet, original tool (t0): $.area: "west" not in the allowed values
- forward release test, sonnet, original tool (t0): $.parking: "\"any\"" not in the allowed values
- forward release test, sonnet, edited tool (tedit): $.area: "east" not in the allowed values; $.pricerange: "cheap" not in the allowed values
- forward release test, sonnet, edited tool (tedit): $.parking: "\"dont_care\"" not in the allowed values
- forward release test, sonnet, edited tool (tedit): $.internet: "\"dont_care\"" not in the allowed values
- steering run, sonnet, hotel rewrite (th): $.internet: "\"any\"" not in the allowed values
- steering run, sonnet, hotel rewrite (th): $.parking: "\"any\"" not in the allowed values
- steering run, sonnet, hotel rewrite (th): $.parking: "\"any\"" not in the allowed values
- steering run, haiku, hotel rewrite (th): $.pricerange: "\"any\"" not in the allowed values
- steering run, haiku, hotel rewrite (th): $.pricerange: "\"any\"" not in the allowed values
- steering run, haiku, hotel rewrite (th): $.area[0]: "any" not in the allowed values
- steering run, sonnet, guesthouse rewrite (tg): $.parking: "\"any\"" not in the allowed values
- steering run, sonnet, guesthouse rewrite (tg): $.pricerange: "\"any\"" not in the allowed values
- steering run, sonnet, guesthouse rewrite (tg): $.pricerange: "\"any\"" not in the allowed values; $.parking: "\"any\"" not in the allowed values
- steering run, haiku, guesthouse rewrite (tg): $.parking: "\"any\"" not in the allowed values
- steering run, haiku, guesthouse rewrite (tg): $.area[0]: "any" not in the allowed values
- steering run, haiku, guesthouse rewrite (tg): $.type: "\"any\"" not in the allowed values
- steering run, haiku, original tool (t0): $.internet: "\"any\"" not in the allowed values
- steering run, haiku, original tool (t0): $.parking: "\"any\"" not in the allowed values; $.internet: "\"any\"" not in the allowed values
- steering run, haiku, original tool (t0): $.area[0]: "any" not in the allowed values
- control updates, haiku, control (t0): $.pricerange: "\"any\"" not in the allowed values
- control updates, haiku, control (t0): $.parking: "\"any\"" not in the allowed values
- control updates, haiku, control (t0): $.parking: "\"any\"" not in the allowed values
- control updates, haiku, repeat (trep): $.area[0]: "any" not in the allowed values
- control updates, haiku, repeat (trep): $.parking: "\"any\"" not in the allowed values
- control updates, haiku, repeat (trep): $.pricerange: "\"any\"" not in the allowed values; $.type: "\"any\"" not in the allowed values
- control updates, haiku, field-order edit (tord): $.internet: "\"any\"" not in the allowed values
- control updates, haiku, field-order edit (tord): $.internet: "\"any\"" not in the allowed values
- control updates, haiku, field-order edit (tord): $.area: "\"any\"" not in the allowed values

### Sensitivity: invalid search calls counted as missing

Forward release test (98.75%, 2,000 draws, seed 20261112, L = 5):

- sonnet open: 430 pairs, +3.95 [+1.40, +6.98], unresolved
- sonnet specific: 56 pairs, +1.79 [+0.00, +7.14], unresolved
- sonnet: model decision hold
- sol open: 448 pairs, +5.36 [+2.68, +8.26], flag-worthy
- sol specific: 59 pairs, +8.47 [-3.39, +20.34], unresolved
- sol: model decision flag

Steering run (release rule of steer_analyze.py on the hotel value):

- sonnet th: open 430 pairs +8.60 [+5.35, +12.33] flag-worthy; specific 57 pairs +12.28 [+1.75, +24.56] flag-worthy; model decision flag
- sonnet tg: open 435 pairs +11.72 [+7.82, +15.63] flag-worthy; specific 57 pairs +26.32 [+10.53, +40.35] flag-worthy; model decision flag
- haiku th: open 413 pairs +33.17 [+27.60, +38.74] flag-worthy; specific 52 pairs +71.15 [+55.77, +84.62] flag-worthy; model decision flag
- haiku tg: open 422 pairs +28.91 [+23.22, +34.12] flag-worthy; specific 52 pairs +50.00 [+32.69, +67.31] flag-worthy; model decision flag

First-request runs, renamed minus original tool (95% interval, a_analyze.paired):

| Model | All 554: prefixes, change [95%] | Brief no type 448 | Brief hotel 59 |
|---|---|---|---|
| sonnet | 548, -24.2 [-27.8, -20.8], lower 144 / higher 1 | 445, -19.3 [-23.0, -15.8], lower 92 / higher 1 | 57, -48.5 [-60.8, -36.8], lower 31 / higher 0 |
| haiku | 511, -5.6 [-7.5, -3.8], lower 34 / higher 0 | 417, -5.5 [-7.7, -3.6], lower 27 / higher 0 | 53, -5.7 [-12.3, -0.9], lower 4 / higher 0 |
| opus | 519, -26.9 [-30.5, -23.5], lower 165 / higher 1 | 421, -21.6 [-25.4, -17.8], lower 108 / higher 1 | 55, -54.5 [-65.5, -42.7], lower 35 / higher 0 |
| sol | 554, -29.5 [-33.0, -25.9], lower 194 / higher 0 | 448, -24.0 [-27.8, -20.3], lower 129 / higher 0 | 59, -57.1 [-68.4, -45.2], lower 38 / higher 0 |
| luna | 554, -21.3 [-24.5, -17.9], lower 132 / higher 0 | 448, -18.2 [-21.7, -14.8], lower 91 / higher 0 | 59, -33.9 [-46.6, -22.0], lower 23 / higher 0 |
| astra | 554, -38.6 [-42.4, -34.5], lower 214 / higher 0 | 448, -31.0 [-35.3, -27.0], lower 139 / higher 0 | 59, -79.7 [-89.8, -69.5], lower 47 / higher 0 |

Exact two-sided sign test on the 59 prefixes whose brief sets hotel, invalid search calls missing:

- sonnet: lower 31 / higher 0, p = 9.31e-10
- haiku: lower 4 / higher 0, p = 0.125
- opus: lower 35 / higher 0, p = 5.82e-11
- sol: lower 38 / higher 0, p = 7.28e-12
- luna: lower 23 / higher 0, p = 2.38e-07
- astra: lower 47 / higher 0, p = 1.42e-14

Blocking filters on the 448 no-type prefixes, invalid search calls missing (share of valid answers):

- sonnet: original 10.7% (142/1322), renamed 1.1% (15/1329)
- haiku: original 3.0% (25/839), renamed 0.2% (2/840)
- opus: original 11.5% (97/842), renamed 1.4% (12/845)
- sol: original 18.1% (243/1344), renamed 6.9% (93/1344)
- luna: original 9.5% (85/896), renamed 0.1% (1/896)
- astra: original 19.0% (85/448), renamed 2.7% (12/448)

Control updates (R10-16; rule of control_analyze.py: L = 5, 98.75%, 2,000 draws, seed 20261112), invalid search calls missing. Post hoc (added after the control results were known):

| Update | Reads | Dropped: control / update | Set | Pairs | Rate: control | Rate: update | Change [98.75%] | Set decision | Update decision |
|---|---|---|---|---|---|---|---|---|---|
| haiku trep (a) | all reads | 83 / 86 | open | 415 | 6.6% (28/422) | 6.6% (28/422) | +0.00 [-1.20, +1.20] | absent | pass |
| haiku trep (a) | all reads | 83 / 86 | specific | 57 | 10.4% (56/536) | 11.0% (59/535) | +0.27 [-1.54, +2.38] | absent |  |
| haiku trep (a) | all reads | 83 / 86 | guesthouse | 42 | 18.2% (8/44) | 14.3% (6/42) | -2.38 [-9.52, +0.00] | no decision |  |
| haiku trep (a) | read 1 only | 35 / 37 | open | 415 | 6.6% (28/422) | 6.6% (28/422) | +0.00 [-1.20, +1.20] | absent | hold |
| haiku trep (a) | read 1 only | 35 / 37 | specific | 52 | 13.2% (7/53) | 11.3% (6/53) | -1.92 [-11.54, +5.77] | unresolved |  |
| haiku trep (a) | read 1 only | 35 / 37 | guesthouse | 42 | 18.2% (8/44) | 14.3% (6/42) | -2.38 [-9.52, +0.00] | no decision |  |
| haiku tord (b) | all reads | 83 / 59 | open | 414 | 6.6% (28/422) | 7.4% (32/431) | +0.48 [-1.45, +2.42] | absent | hold |
| haiku tord (b) | all reads | 83 / 59 | specific | 57 | 10.4% (56/536) | 12.3% (68/551) | +1.67 [-3.16, +7.63] | unresolved |  |
| haiku tord (b) | all reads | 83 / 59 | guesthouse | 43 | 18.2% (8/44) | 15.9% (7/44) | -4.65 [-16.28, +6.98] | no decision |  |
| haiku tord (b) | read 1 only | 35 / 25 | open | 414 | 6.6% (28/422) | 7.4% (32/431) | +0.48 [-1.45, +2.42] | absent | hold |
| haiku tord (b) | read 1 only | 35 / 25 | specific | 51 | 13.2% (7/53) | 5.6% (3/54) | -5.88 [-17.65, +3.92] | unresolved |  |
| haiku tord (b) | read 1 only | 35 / 25 | guesthouse | 43 | 18.2% (8/44) | 15.9% (7/44) | -4.65 [-16.28, +6.98] | no decision |  |
