## Later turns with a simulated traveller (amendment R10-8)

Exploratory. Agent: Claude Sonnet 5.5 with the search tool, no limit on calls. Traveller: Claude Haiku 5.5 with the written brief. Four agent turns (the first request and three traveller turns). F: the brief sets no type and every fitting venue is a guesthouse; R: the brief sets no type and a hotel fits.

### Arm t0: 260 complete conversations (0 stopped at the cap), cost 4.86 USD at list prices

| Set | n | Initial failure | Fitting venue shown | Never shown | First fit turn (1/2/3/4/never) | Guesthouse named | Hotel-only at the end | Relapse (post hoc) | Mean searches | Simulator leaks |
|---|---|---|---|---|---|---|---|---|---|---|
| F | 130 | 20/130 = 15.4% [9.2%, 21.5%] | 123/130 = 94.6% [90.0%, 98.5%] | 7/130 = 5.4% [1.5%, 10.0%] | 104/14/4/1/7 | 130/130 = 100.0% [100.0%, 100.0%] | 15/130 = 11.5% [6.2%, 16.9%] | 17/130 = 13.1% [7.7%, 19.2%] | 2.55 | 3 |
| F, initial failure | 20 | 20/20 = 100.0% [100.0%, 100.0%] | 17/20 = 85.0% [70.0%, 100.0%] | 3/20 = 15.0% [0.0%, 30.0%] | 9/5/2/1/3 | 20/20 = 100.0% [100.0%, 100.0%] | 11/20 = 55.0% [35.0%, 75.0%] | 9/20 = 45.0% [25.0%, 65.0%] | 4.70 | 0 |
| F, no initial failure | 110 | 0/110 = 0.0% [0.0%, 0.0%] | 106/110 = 96.4% [92.7%, 99.1%] | 4/110 = 3.6% [0.9%, 7.3%] | 95/9/2/0/4 | 110/110 = 100.0% [100.0%, 100.0%] | 4/110 = 3.6% [0.9%, 7.3%] | 8/110 = 7.3% [2.7%, 12.7%] | 2.15 | 3 |
| R | 130 | 0/130 = 0.0% [0.0%, 0.0%] | 120/130 = 92.3% [87.7%, 96.2%] | 10/130 = 7.7% [3.8%, 12.3%] | 99/19/1/1/10 | 61/130 = 46.9% [38.5%, 54.6%] | 23/130 = 17.7% [11.5%, 24.6%] | 13/130 = 10.0% [5.4%, 15.4%] | 2.30 | 1 |
| F, no prior venue (description) | 104 | 18/104 = 17.3% [10.6%, 25.0%] | 99/104 = 95.2% [90.4%, 99.0%] | 5/104 = 4.8% [1.0%, 9.6%] | 81/14/3/1/5 | 104/104 = 100.0% [100.0%, 100.0%] | 12/104 = 11.5% [5.8%, 18.3%] | 12/104 = 11.5% [5.8%, 18.3%] | 2.58 | 3 |
| F, no prior venue, initial failure (description) | 18 | 18/18 = 100.0% [100.0%, 100.0%] | 15/18 = 83.3% [66.7%, 100.0%] | 3/18 = 16.7% [0.0%, 33.3%] | 7/5/2/1/3 | 18/18 = 100.0% [100.0%, 100.0%] | 10/18 = 55.6% [33.3%, 77.8%] | 8/18 = 44.4% [22.2%, 66.7%] | 4.83 | 0 |
| R, no prior venue (description) | 102 | 0/102 = 0.0% [0.0%, 0.0%] | 93/102 = 91.2% [85.3%, 96.1%] | 9/102 = 8.8% [3.9%, 14.7%] | 72/19/1/1/9 | 50/102 = 49.0% [39.2%, 58.8%] | 23/102 = 22.5% [14.7%, 31.4%] | 12/102 = 11.8% [5.9%, 18.6%] | 2.44 | 1 |

- Never shown: F initial failure minus F without: +11.4 points [-3.6, +28.2], Fisher p 0.073 (n 20 and 110)
- Never shown: F minus R: -2.3 points [-7.7, +3.8], Fisher p 0.62 (n 130 and 130)
- First fit turn, F initial failure minus F without (conversations that show one): +0.58 turns

### Arm t1: 260 complete conversations (0 stopped at the cap), cost 4.66 USD at list prices

| Set | n | Initial failure | Fitting venue shown | Never shown | First fit turn (1/2/3/4/never) | Guesthouse named | Hotel-only at the end | Relapse (post hoc) | Mean searches | Simulator leaks |
|---|---|---|---|---|---|---|---|---|---|---|
| F | 130 | 1/130 = 0.8% [0.0%, 2.3%] | 121/130 = 93.1% [88.5%, 96.9%] | 9/130 = 6.9% [3.1%, 11.5%] | 106/15/0/0/9 | 129/130 = 99.2% [97.7%, 100.0%] | 1/130 = 0.8% [0.0%, 2.3%] | 1/130 = 0.8% [0.0%, 2.3%] | 2.07 | 3 |
| F, initial failure | 1 | 1/1 = 100.0% [100.0%, 100.0%] | 1/1 = 100.0% [100.0%, 100.0%] | 0/1 = 0.0% [0.0%, 0.0%] | 1/0/0/0/0 | 1/1 = 100.0% [100.0%, 100.0%] | 0/1 = 0.0% [0.0%, 0.0%] | 0/1 = 0.0% [0.0%, 0.0%] | 4.00 | 0 |
| F, no initial failure | 129 | 0/129 = 0.0% [0.0%, 0.0%] | 120/129 = 93.0% [88.4%, 96.9%] | 9/129 = 7.0% [3.1%, 11.6%] | 105/15/0/0/9 | 128/129 = 99.2% [97.7%, 100.0%] | 1/129 = 0.8% [0.0%, 2.3%] | 1/129 = 0.8% [0.0%, 2.3%] | 2.05 | 3 |
| R | 130 | 0/130 = 0.0% [0.0%, 0.0%] | 117/130 = 90.0% [84.6%, 94.6%] | 13/130 = 10.0% [5.4%, 15.4%] | 95/22/0/0/13 | 90/130 = 69.2% [61.5%, 76.9%] | 2/130 = 1.5% [0.0%, 3.8%] | 2/130 = 1.5% [0.0%, 3.8%] | 2.22 | 0 |
| F, no prior venue (description) | 104 | 1/104 = 1.0% [0.0%, 2.9%] | 99/104 = 95.2% [90.4%, 99.0%] | 5/104 = 4.8% [1.0%, 9.6%] | 84/15/0/0/5 | 103/104 = 99.0% [97.1%, 100.0%] | 0/104 = 0.0% [0.0%, 0.0%] | 0/104 = 0.0% [0.0%, 0.0%] | 2.09 | 3 |
| F, no prior venue, initial failure (description) | 1 | 1/1 = 100.0% [100.0%, 100.0%] | 1/1 = 100.0% [100.0%, 100.0%] | 0/1 = 0.0% [0.0%, 0.0%] | 1/0/0/0/0 | 1/1 = 100.0% [100.0%, 100.0%] | 0/1 = 0.0% [0.0%, 0.0%] | 0/1 = 0.0% [0.0%, 0.0%] | 4.00 | 0 |
| R, no prior venue (description) | 102 | 0/102 = 0.0% [0.0%, 0.0%] | 91/102 = 89.2% [83.3%, 95.1%] | 11/102 = 10.8% [4.9%, 16.7%] | 69/22/0/0/11 | 76/102 = 74.5% [65.7%, 82.4%] | 2/102 = 2.0% [0.0%, 4.9%] | 2/102 = 2.0% [0.0%, 4.9%] | 2.37 | 0 |

- Never shown: F initial failure minus F without: -7.0 points [-11.6, -3.1], Fisher p 1 (n 1 and 129)
- Never shown: F minus R: -3.1 points [-10.0, +3.8], Fisher p 0.5 (n 130 and 130)
- First fit turn, F initial failure minus F without (conversations that show one): -0.12 turns

### Arm t1 minus arm t0, paired by dialogue (post hoc description)

| Set and outcome | Dialogues in both | t0 | t1 | t1 only | t0 only | Sign p |
|---|---|---|---|---|---|---|
| F_initial_failure | 130 | 20 | 1 | 0 | 19 | 3.8e-06 |
| F_never_fit | 130 | 7 | 9 | 3 | 1 | 0.62 |
| F_hotel_only_end | 130 | 15 | 1 | 0 | 14 | 0.00012 |
| R_initial_failure | 130 | 0 | 0 | 0 | 0 | 1 |
| R_never_fit | 130 | 10 | 13 | 3 | 0 | 0.25 |
| R_hotel_only_end | 130 | 23 | 2 | 2 | 23 | 1.9e-05 |

### Predictions (R10-8, arm t0)

| # | Words | Value | Held |
|---|---|---|---|
| B1 | in F, the first search is a search failure in 10% to 30% of the conversations | 0.15384615384615385 | held |
| B2 | in F after an initial failure, a fitting venue is shown by the end in 50% or more | 0.85 | held |
| B3 | never-fit share: F after an initial failure minus F without one is +10 points or more | 0.11363636363636363 | held |
| B4 | in F after an initial failure, the agent names or offers a guesthouse in 70% or more | 1.0 | held |
| B5 | in F after an initial failure, the last search still keeps the hotel-only filter in 35% or less | 0.55 | failed |
| B6 | of the F conversations that show a fitting venue, the mean first-fit turn is 0.7 turn or more later after an initial failure | 0.5832408435072141 | failed |
