## Later turns: briefs with a failing first choice (post hoc sensitivity analysis)

First choice: the corpus brief holds a fail_info that differs from its info. The fit rule uses info only.

### Arm t0 (ert_sonnet)

| Group | First choice | Conversations | Initial failure | Never held |
|---|---|---|---|---|
| F | all | 130 | 20 | 7 |
| F | first_choice | 47 | 7 | 6 |
| F | first_choice_name | 26 | 0 | 0 |
| F | first_choice_requirements | 21 | 7 | 6 |
| F | no_first_choice | 83 | 13 | 1 |
| R | all | 130 | 0 | 10 |
| R | first_choice | 46 | 0 | 8 |
| R | first_choice_name | 16 | 0 | 0 |
| R | first_choice_requirements | 30 | 0 | 8 |
| R | no_first_choice | 84 | 0 | 2 |

- F, no_first_choice: never held after an initial failure 1/13, without one 0/70; difference +7.7 points [+0.0, +23.1], Fisher p 0.16
- F, first_choice: never held after an initial failure 2/7, without one 4/40; difference +18.6 points [-12.5, +56.4], Fisher p 0.21

- Venues of our data that meet the first choice (briefs with a first choice): F [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]; R [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

| Never held, first choice | Group | Initial failure | Kind | Venues meeting the first choice (hotels) | Slot: first -> final; traveller names final; a search uses final |
|---|---|---|---|---|---|
| PMUL0388.json | R | False | requirements | 0 (0) | pricerange: moderate -> cheap; False; False; stars: 5 -> 4; True; True |
| MUL1075.json | R | False | requirements | 0 (0) | area: east -> north; False; False; internet: no -> yes; True; False; pricerange: expensive -> moderate; False; False |
| PMUL3693.json | R | False | requirements | 0 (0) | area: east -> centre; False; False; internet: no -> yes; False; False |
| MUL1087.json | F | False | requirements | 0 (0) | pricerange: expensive -> moderate; True; True |
| PMUL0035.json | R | False | requirements | 0 (0) | internet: no -> yes; True; True; pricerange: cheap -> moderate; False; False |
| MUL0085.json | F | True | requirements | 0 (0) | area: west -> centre; False; False; pricerange: moderate -> cheap; True; True |
| MUL0709.json | R | False | requirements | 0 (0) | area: east -> west; False; False; parking: no -> yes; False; False; pricerange: expensive -> cheap; False; False |
| PMUL0123.json | F | True | requirements | 0 (0) | area: south -> north; True; True |
| PMUL4111.json | R | False | requirements | 0 (0) | area: west -> east; False; False; parking: no -> yes; False; False |
| PMUL2698.json | F | False | requirements | 0 (0) | area: east -> south; False; False; pricerange: expensive -> cheap; False; False |
| MUL1142.json | R | False | requirements | 0 (0) | area: west -> south; False; False; parking: no -> yes; True; False |
| PMUL4661.json | R | False | requirements | 0 (0) | area: east -> west; False; False; internet: no -> yes; True; False |
| MUL0606.json | F | False | requirements | 0 (0) | pricerange: expensive -> moderate; False; False; stars: 5 -> 4; True; True |
| PMUL0371.json | F | False | requirements | 0 (0) | area: south -> north; False; False |

### Arm t1 (ert1_sonnet)

| Group | First choice | Conversations | Initial failure | Never held |
|---|---|---|---|---|
| F | all | 130 | 1 | 9 |
| F | first_choice | 47 | 0 | 8 |
| F | first_choice_name | 26 | 0 | 0 |
| F | first_choice_requirements | 21 | 0 | 8 |
| F | no_first_choice | 83 | 1 | 1 |
| R | all | 130 | 0 | 13 |
| R | first_choice | 46 | 0 | 9 |
| R | first_choice_name | 16 | 0 | 1 |
| R | first_choice_requirements | 30 | 0 | 8 |
| R | no_first_choice | 84 | 0 | 4 |

- F, no_first_choice: never held after an initial failure 0/1, without one 1/82; difference -1.2 points [-3.7, +0.0], Fisher p 1
- F, first_choice: never held after an initial failure 0/0, without one 8/47; difference -

- Venues of our data that meet the first choice (briefs with a first choice): F [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]; R [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

| Never held, first choice | Group | Initial failure | Kind | Venues meeting the first choice (hotels) | Slot: first -> final; traveller names final; a search uses final |
|---|---|---|---|---|---|
| PMUL0388.json | R | False | requirements | 0 (0) | pricerange: moderate -> cheap; False; False; stars: 5 -> 4; True; True |
| MUL1075.json | R | False | requirements | 0 (0) | area: east -> north; False; False; internet: no -> yes; True; True; pricerange: expensive -> moderate; False; False |
| PMUL0370.json | F | False | requirements | 0 (0) | internet: no -> yes; True; True |
| PMUL3693.json | R | False | requirements | 0 (0) | area: east -> centre; False; False; internet: no -> yes; False; False |
| MUL1087.json | F | False | requirements | 0 (0) | pricerange: expensive -> moderate; True; True |
| PMUL0035.json | R | False | requirements | 0 (0) | internet: no -> yes; True; False; pricerange: cheap -> moderate; False; False |
| MUL0085.json | F | False | requirements | 0 (0) | area: west -> centre; False; False; pricerange: moderate -> cheap; True; True |
| MUL0709.json | R | False | requirements | 0 (0) | area: east -> west; False; False; parking: no -> yes; True; True; pricerange: expensive -> cheap; False; False |
| PMUL0123.json | F | False | requirements | 0 (0) | area: south -> north; False; False |
| PMUL4111.json | R | False | requirements | 0 (0) | area: west -> east; False; False; parking: no -> yes; True; True |
| PMUL2698.json | F | False | requirements | 0 (0) | area: east -> south; False; False; pricerange: expensive -> cheap; False; False |
| MUL1142.json | R | False | requirements | 0 (0) | area: west -> south; False; False; parking: no -> yes; True; True |
| PMUL4661.json | R | False | requirements | 0 (0) | area: east -> west; False; False; internet: no -> yes; True; True |
| MUL1222.json | F | False | requirements | 0 (0) | area: west -> north; False; False |
| MUL0606.json | F | False | requirements | 0 (0) | pricerange: expensive -> moderate; False; False; stars: 5 -> 4; True; True |
| PMUL0371.json | F | False | requirements | 0 (0) | area: south -> north; False; False |
| PMUL2650.json | R | False | name | 1 (0) | name: bridge guest house -> the lensfield hotel; True; False |

