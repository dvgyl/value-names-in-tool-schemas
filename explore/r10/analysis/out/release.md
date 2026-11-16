## Forward release test (amendment R10-6)

Exploratory. Edit: Claude Opus 5.5 rewrote the search tool (r10/release/edit.json, SHA-256 `c6918fbea8ac5e4c14e8b225206a379a4dfb525cbfb1d815c5e1af5a66ca7ac3`). L = 5 points; one look with all requests; C = 4; interval level 98.75% (percentile cluster bootstrap over prefixes, 2000 draws, seed 20261112). Sets: open 448, specific 59 (guesthouse 47, no decision).

### Decisions

| Model | Set | Pairs | Change, points | 98.75% interval | Set decision | Model decision |
|---|---|---|---|---|---|---|
| sonnet | open | 448 | +3.6 | [+0.9, +6.0] | unresolved | hold |
| sonnet | specific | 59 | +1.7 | [+0.0, +6.8] | unresolved |  |
| sol | open | 448 | +5.4 | [+2.7, +8.3] | flag-worthy | flag |
| sol | specific | 59 | +8.5 | [-3.4, +20.3] | unresolved |  |

### Descriptions (no decision)

Rate of `type` holding hotel (valid reads):

| Model | Set | t0 | tedit | Guesthouse-set change, points |
|---|---|---|---|---|
| sonnet | open | 21.0% (94/448) | 24.6% (110/448) |  |
| sonnet | specific | 55.9% (33/59) | 57.6% (34/59) |  |
| sonnet | guesthouse | 51.1% (24/47) | 61.7% (29/47) | +10.6 |
| sol | open | 34.4% (154/448) | 39.7% (178/448) |  |
| sol | specific | 83.1% (49/59) | 91.5% (54/59) |  |
| sol | guesthouse | 78.7% (37/47) | 78.7% (37/47) | +0.0 |

| Model | Trade: wrong removed | correct lost | ratio [95%] | Blocking filters, open set: t0 | tedit |
|---|---|---|---|---|---|
| sonnet | -16.0 | -1.0 | not defined (the edit removes no wrong value) | 10.3% (46/448) | 11.6% (52/448) |
| sol | -24.0 | -5.0 | not defined (the edit removes no wrong value) | 17.6% (79/448) | 19.6% (88/448) |

Read kinds and `type` values of the search calls, per arm:

- sonnet t0: kinds {"search": 553, "none": 1}; type {"null": 395, "hotel": 150, "any": 3, "hotel+guesthouse": 1, "guesthouse": 4}
- sonnet tedit: kinds {"search": 554}; type {"null": 372, "hotel": 172, "guesthouse": 6, "hotel+guesthouse": 1, "any": 1, "\"dont_care\"": 2}
- sol t0: kinds {"search": 554}; type {"hotel": 239, "null": 307, "guesthouse": 4, "hotel+guesthouse": 1, "any": 3}
- sol tedit: kinds {"search": 554}; type {"hotel": 268, "null": 277, "guesthouse": 5, "hotel+guesthouse": 1, "any": 3}
