## Answer classes of the first-request tool calls (post hoc; no model call)

Scorable = parsed after the declared normalization (tools.parse_call after tools.clean_nulls). Schema-valid = the arguments after this normalization fit the closed input schema (tool_validity.problems).

| Model | Tool | answers | not completed | non-call | ask call | other | search, schema-valid | search, not schema-valid |
|---|---|---|---|---|---|---|---|---|
| sonnet | t0 | 1662 | 0 | 3 | 0 | 0 | 1630 | 29 |
| sonnet | t1 | 1662 | 0 | 5 | 0 | 0 | 1636 | 21 |
| sonnet | t0ask | 1662 | 0 | 0 | 74 | 0 | 1562 | 26 |
| haiku | t0 | 1108 | 0 | 32 | 0 | 4 | 996 | 76 |
| haiku | t1 | 1108 | 0 | 40 | 0 | 1 | 992 | 75 |
| haiku | t0ask | 1108 | 0 | 11 | 71 | 0 | 954 | 72 |
| opus | t0 | 1108 | 0 | 0 | 0 | 0 | 1035 | 73 |
| opus | t1 | 1108 | 0 | 0 | 0 | 0 | 1041 | 67 |
| opus | t0ask | 1108 | 0 | 0 | 28 | 0 | 1014 | 66 |
| sol | t0 | 1662 | 0 | 0 | 0 | 0 | 1662 | 0 |
| sol | t1 | 1662 | 0 | 0 | 0 | 0 | 1662 | 0 |
| sol | t0ask | 1662 | 0 | 0 | 45 | 0 | 1617 | 0 |
| luna | t0 | 1108 | 0 | 0 | 0 | 0 | 1108 | 0 |
| luna | t1 | 1108 | 0 | 0 | 0 | 0 | 1108 | 0 |
| luna | t0ask | 1108 | 0 | 0 | 46 | 0 | 1062 | 0 |
| astra | t0 | 554 | 0 | 0 | 0 | 0 | 554 | 0 |
| astra | t1 | 554 | 0 | 0 | 0 | 0 | 554 | 0 |
| astra | t0ask | 554 | 0 | 0 | 19 | 0 | 535 | 0 |

Exclusion on the 448 first requests whose brief sets no type (k / n):

| Model | Tool | Scorable answers (primary) | Schema-invalid calls missing (sensitivity) | Exclusions in removed calls |
|---|---|---|---|---|
| sonnet | t0 | 144/1344 = 10.71% | 142/1322 = 10.74% | 2 |
| sonnet | t1 | 15/1344 = 1.12% | 15/1329 = 1.13% | 0 |
| sonnet | t0ask | 123/1344 = 9.15% | 121/1325 = 9.13% | 2 |
| haiku | t0 | 28/894 = 3.13% | 25/839 = 2.98% | 3 |
| haiku | t1 | 2/895 = 0.22% | 2/840 = 0.24% | 0 |
| haiku | t0ask | 25/896 = 2.79% | 22/841 = 2.62% | 3 |
| opus | t0 | 107/896 = 11.94% | 97/842 = 11.52% | 10 |
| opus | t1 | 12/896 = 1.34% | 12/845 = 1.42% | 0 |
| opus | t0ask | 69/896 = 7.70% | 64/847 = 7.56% | 5 |
| sol | t0 | 243/1344 = 18.08% | 243/1344 = 18.08% | 0 |
| sol | t1 | 93/1344 = 6.92% | 93/1344 = 6.92% | 0 |
| sol | t0ask | 223/1344 = 16.59% | 223/1344 = 16.59% | 0 |
| luna | t0 | 85/896 = 9.49% | 85/896 = 9.49% | 0 |
| luna | t1 | 1/896 = 0.11% | 1/896 = 0.11% | 0 |
| luna | t0ask | 81/896 = 9.04% | 81/896 = 9.04% | 0 |
| astra | t0 | 85/448 = 18.97% | 85/448 = 18.97% | 0 |
| astra | t1 | 12/448 = 2.68% | 12/448 = 2.68% | 0 |
| astra | t0ask | 79/448 = 17.63% | 79/448 = 17.63% | 0 |

All six models, exclusions among scorable answers / of these in calls that are not schema-valid: t0 692 / 15; t1 135 / 0; t0ask 600 / 10

Step 2 (era2 trials joined to their era1 original-tool search, as in a_analyze.step2):

- sonnet: {"empty trials": 88, "empty trials after a call that is not schema-valid": 8, "trials after an exclusion": 96, "trials after an exclusion, call not schema-valid": 2, "nonempty trials": 219, "nonempty trials after a call that is not schema-valid": 0, "empty, not valid: a search without the invalid fields finds a venue": 8, "empty, not valid: kinds quoted value": 8}
- haiku: {"empty trials": 49, "empty trials after a call that is not schema-valid": 14, "nonempty trials": 39, "nonempty trials after a call that is not schema-valid": 0, "empty, not valid: a search without the invalid fields finds a venue": 9, "empty, not valid: kinds quoted value": 14, "trials after an exclusion": 28, "trials after an exclusion, call not schema-valid": 3}
- opus: {"nonempty trials": 132, "nonempty trials after a call that is not schema-valid": 0, "empty trials": 47, "empty trials after a call that is not schema-valid": 12, "trials after an exclusion": 51, "trials after an exclusion, call not schema-valid": 5, "empty, not valid: a search without the invalid fields finds a venue": 11, "empty, not valid: kinds quoted value": 12}
- sol: {"empty trials": 134, "empty trials after a call that is not schema-valid": 0, "nonempty trials": 351, "nonempty trials after a call that is not schema-valid": 0, "trials after an exclusion": 161, "trials after an exclusion, call not schema-valid": 0}
- luna: {"nonempty trials": 179, "nonempty trials after a call that is not schema-valid": 0, "trials after an exclusion": 85, "trials after an exclusion, call not schema-valid": 0, "empty trials": 70, "empty trials after a call that is not schema-valid": 0}
- astra: {"empty trials": 70, "empty trials after a call that is not schema-valid": 0, "nonempty trials": 183, "nonempty trials after a call that is not schema-valid": 0, "trials after an exclusion": 85, "trials after an exclusion, call not schema-valid": 0}

Renamed minus original tool, hotel filter, paired per first request (points): stored a.json against the sensitivity of tool_validity.json (calls that are not schema-valid missing):

- sonnet all 554: -24.13 against -24.24 (difference -0.11)
- sonnet brief no type 448: -19.12 against -19.29 (difference -0.17)
- haiku all 554: -6.15 against -5.58 (difference +0.57)
- haiku brief no type 448: -5.80 against -5.52 (difference +0.29)
- opus all 554: -26.44 against -26.88 (difference -0.43)
- opus brief no type 448: -21.88 against -21.62 (difference +0.26)
- sol all 554: -29.48 against -29.48 (difference +0.00)
- sol brief no type 448: -23.96 against -23.96 (difference +0.00)
- luna all 554: -21.30 against -21.30 (difference +0.00)
- luna brief no type 448: -18.19 against -18.19 (difference +0.00)
- astra all 554: -38.63 against -38.63 (difference +0.00)
- astra brief no type 448: -31.03 against -31.03 (difference +0.00)

Ask share of the ask option (t0ask; a_analyze share_ask: ask calls / scorable answers), stored and with the search calls that are not schema-valid counted as missing:

- sonnet: 74/1662 = 4.45% -> 74/1636 = 4.52% (+0.07 points)
- haiku: 71/1108 = 6.41% -> 71/1036 = 6.85% (+0.45 points)
- opus: 28/1108 = 2.53% -> 28/1042 = 2.69% (+0.16 points)
- sol: 45/1662 = 2.71% -> 45/1662 = 2.71% (+0.00 points)
- luna: 46/1108 = 4.15% -> 46/1108 = 4.15% (+0.00 points)
- astra: 19/554 = 3.43% -> 19/554 = 3.43% (+0.00 points)

Checks: answers, non-calls and schema-valid calls equal tool_validity.json; the sensitivity counts equal tool_validity.json (_blocking); the primary shares equal a.json (search_failure); the ask counts equal a.json (share_ask).
