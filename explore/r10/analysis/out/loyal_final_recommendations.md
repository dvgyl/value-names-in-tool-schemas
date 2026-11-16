## Inventory of the stored later-turn conversations (post hoc description; no model call)

Spec: loyal_final_recommendations_spec.md. No fit and no comparison of outcomes between the tools.

- t0 (ert_sonnet): 261 records, 260 complete; statuses {'complete': 260, 'cap': 1}; keys ['arm', 'brief', 'calls', 'cap', 'cost', 'dialogue', 'group', 'replies', 'searches', 'status', 'traveller']
- t1 (ert1_sonnet): 260 records, 260 complete; statuses {'complete': 260}; keys ['arm', 'brief', 'calls', 'cost', 'dialogue', 'group', 'replies', 'searches', 'status', 'traveller']

- Agent system text, words that could fix a final-choice format: {'t0': [], 't1': []}
- Stored conversations with a call that is not valid after normalization (stored count): {'t0': {'complete conversations': 22}, 't1': {'complete conversations': 8}}

| Arm | Set | n | Agent turns | Final empty | Pending search at the call limit | Final names 0 | 1 | 2+ | 1 name: shown by a search | 1 name: cue | 0 names, an earlier reply names one | Traveller's last message has 'suit' | With a call that does not parse | Shadowed name (diagnostic) | Tools | Fields that could name a choice |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t0 | all | 260 | {4: 260} | 0 | 2 | 81 | 138 | 41 | 136 | 22 | 81 | 35 | 0 | 0 | ['search_hotels'] | [] |
| t0 | F | 130 | {4: 130} | 0 | 1 | 39 | 67 | 24 | 66 | 10 | 39 | 12 | 0 | 0 | ['search_hotels'] | [] |
| t0 | R | 130 | {4: 130} | 0 | 1 | 42 | 71 | 17 | 70 | 12 | 42 | 23 | 0 | 0 | ['search_hotels'] | [] |
| t1 | all | 260 | {4: 260} | 0 | 0 | 78 | 152 | 30 | 150 | 15 | 77 | 35 | 0 | 0 | ['search_hotels'] | [] |
| t1 | F | 130 | {4: 130} | 0 | 0 | 37 | 84 | 9 | 84 | 9 | 37 | 12 | 0 | 0 | ['search_hotels'] | [] |
| t1 | R | 130 | {4: 130} | 0 | 0 | 41 | 68 | 21 | 66 | 6 | 40 | 23 | 0 | 0 | ['search_hotels'] | [] |

### Feasibility decision (spec rule)

| Arm | F1 | F2 | F3a (>= 90% name one) | F3b (cue <= 5%) | F3c (shown >= 95%) | Share naming one | Cue share | Shown share |
|---|---|---|---|---|---|---|---|---|
| t0 | False | False | False | False | True | 53.1% | 15.9% | 98.6% |
| t1 | False | False | False | False | True | 58.5% | 9.9% | 98.7% |

Decision: not usable

