## Harmless control updates under the release rule (amendment R10-16)

Exploratory. Haiku answered the 554 first requests of experiment A with the original tool (t0, the control), with the original tool again in a new batch (trep, update a), and with the same tool whose schema fields are in alphabetical order (tord, update b). Reads per arm: 10 on the specific set, 1 on the open and guesthouse sets. Rule of R10-6 (Appendix I, unchanged): L = 5 points, one look, 98.75% percentile cluster bootstrap intervals over prefixes (2000 draws, seed 20261112).

### Decisions: All reads (the design of R10-16)

| Update | Set | Pairs | Change, points | 98.75% interval | Half-width | Set decision | Update decision |
|---|---|---|---|---|---|---|---|
| haiku trep (a) | open | 448 | +0.2 | [-0.9, +1.6] | 1.2 | absent | pass |
| haiku trep (a) | specific | 59 | +0.1 | [-1.8, +2.2] | 2.0 | absent |  |
| haiku tord (b) | open | 448 | +0.2 | [-1.8, +2.2] | 2.0 | absent | hold |
| haiku tord (b) | specific | 59 | +1.2 | [-3.6, +6.6] | 5.1 | unresolved |  |

### Decisions: Description: read 1 of each arm only (the design of R10-6)

| Update | Set | Pairs | Change, points | 98.75% interval | Half-width | Set decision | Update decision |
|---|---|---|---|---|---|---|---|
| haiku trep (a) | open | 448 | +0.2 | [-0.9, +1.6] | 1.2 | absent | hold |
| haiku trep (a) | specific | 59 | -1.7 | [-10.2, +5.1] | 7.6 | unresolved |  |
| haiku tord (b) | open | 448 | +0.2 | [-1.8, +2.2] | 2.0 | absent | hold |
| haiku tord (b) | specific | 59 | -5.1 | [-16.9, +3.4] | 10.2 | unresolved |  |

### Descriptions (all reads)

Rate of `type` holding hotel (valid reads):

| Update | Set | Control (t0) | Update | Reads per prefix (control and update: prefixes) |
|---|---|---|---|---|
| haiku trep (a) | open | 6.9% (31/448) | 7.1% (32/448) | {"1 and 1": 448} |
| haiku trep (a) | specific | 13.4% (79/590) | 13.4% (79/589) | {"10 and 10": 59} |
| haiku trep (a) | guesthouse | 19.1% (9/47) | 17.0% (8/47) | {"1 and 1": 47} |
| haiku tord (b) | open | 6.9% (31/448) | 7.1% (32/448) | {"1 and 1": 448} |
| haiku tord (b) | specific | 13.4% (79/590) | 14.6% (86/590) | {"10 and 10": 59} |
| haiku tord (b) | guesthouse | 19.1% (9/47) | 14.9% (7/47) | {"1 and 1": 47} |

| Update | Trade: wrong removed | correct lost | ratio | Blocking filters, open set: control | update |
|---|---|---|---|---|---|
| haiku trep (a) | -1.0 | -0.0 | not defined (no wrong value removed) | 3.1% (14/448) | 3.1% (14/448) |
| haiku tord (b) | -1.0 | -0.7 | not defined (no wrong value removed) | 3.1% (14/448) | 3.3% (15/448) |

Read kinds and `type` values, per arm:

- haiku trep (a) control: kinds {"search": 1066, "none": 19}; type {"null": 895, "hotel": 108, "\"any\"": 10, "any": 32, "hotel+guesthouse": 11, "guesthouse": 10}
- haiku trep (a) update: kinds {"search": 1062, "none": 22, "invalid: JSONDecodeError: Expecting property name enclosed in double ": 1}; type {"null": 885, "hotel+guesthouse": 11, "hotel": 108, "\"any\"": 9, "any": 39, "\"hotel\"": 1, "guesthouse": 9}
- haiku tord (b) control: kinds {"search": 1066, "none": 19}; type {"null": 895, "hotel": 108, "\"any\"": 10, "any": 32, "hotel+guesthouse": 11, "guesthouse": 10}
- haiku tord (b) update: kinds {"search": 1055, "none": 30}; type {"hotel": 114, "null": 880, "any": 26, "hotel+guesthouse": 11, "\"any\"": 7, "\"hotel\"": 4, "guesthouse": 13}

### Predictions (R10-16)

| # | Words | Value | Result |
|---|---|---|---|
| C1 | Haiku, update trep (a): the rule gives "pass" | "pass" | held |
| C2 | Haiku, update tord (b): the rule gives "pass" | "hold" | failed |
| C3 | no set of a control update is "flag-worthy" | {"haiku trep (a)": ["absent", "absent"], "haiku tord (b)": ["absent", "unresolved"]} | held |
| C4 | Sonnet, update (a): the rule gives "pass" | null | n/a (Sonnet did not run: its bound did not fit the shared limit) |
