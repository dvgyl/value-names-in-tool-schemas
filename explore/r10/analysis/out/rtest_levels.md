## Final-5 analysis: interval levels, zero-width intervals, error rates near the limits, arm order

Status: post hoc, exploratory. L = 5 points.

### A1. Table 4 rows at the stated level

Unchanged tool, 29 pairs, one answer per prefix. Tally (level, rule, decision):

```
97.5 exact_first: hold: 29
97.5 exact_revised: hold: 29
97.5 first: flag: 2
97.5 first: hold: 25
97.5 first: pass: 2
97.5 revised: hold: 27
97.5 revised: pass: 2
98.75 exact_first: hold: 29
98.75 exact_revised: hold: 29
98.75 first: flag: 2
98.75 first: hold: 25
98.75 first: pass: 2
98.75 revised: hold: 27
98.75 revised: pass: 2
99.5 exact_first: hold: 29
99.5 exact_revised: hold: 29
99.5 first: hold: 27
99.5 first: pass: 2
99.5 revised: hold: 27
99.5 revised: pass: 2
```

| Edit | Status | C | Level | First | Revised | Exact first | Exact revised | Open | Specific |
|---|---|---|---|---|---|---|---|---|---|
| full rename, sonnet | post hoc, 6 models | 12 | 98.75 (0.995833) | flag | flag | flag | flag | -19.2 [-23.7, -14.7] 0/86 | -44.1 [-61.0, -28.8] 0/26 p=0 |
| full rename, sonnet | post hoc, 6 models | 12 | stated (0.995833) | flag | flag | flag | flag | -19.2 [-24.8, -14.1] 0/86 | -44.1 [-62.7, -25.4] 0/26 p=0 |
| full rename, sonnet | post hoc, 6 models | 12 | 97.5 (0.995833) | flag | flag | flag | flag | -19.2 [-23.4, -15.0] 0/86 | -44.1 [-59.3, -28.8] 0/26 p=0 |
| full rename, haiku | post hoc, 6 models | 12 | 98.75 (0.995833) | flag | flag | flag | flag | -5.4 [-8.3, -2.9] 0/24 | -8.6 [-19.0, -1.7] 0/5 p=0.0625 |
| full rename, haiku | post hoc, 6 models | 12 | stated (0.995833) | flag | flag | flag | flag | -5.4 [-8.7, -2.7] 0/24 | -8.6 [-20.7, +0.0] 0/5 p=0.0625 |
| full rename, haiku | post hoc, 6 models | 12 | 97.5 (0.995833) | flag | flag | flag | flag | -5.4 [-7.8, -3.1] 0/24 | -8.6 [-17.2, -1.7] 0/5 p=0.0625 |
| full rename, opus | post hoc, 6 models | 12 | 98.75 (0.995833) | flag | flag | flag | flag | -20.8 [-25.7, -15.8] 2/95 | -49.2 [-66.1, -33.9] 0/29 p=0 |
| full rename, opus | post hoc, 6 models | 12 | stated (0.995833) | flag | flag | flag | flag | -20.8 [-26.8, -14.7] 2/95 | -49.2 [-67.8, -32.2] 0/29 p=0 |
| full rename, opus | post hoc, 6 models | 12 | 97.5 (0.995833) | flag | flag | flag | flag | -20.8 [-25.2, -16.3] 2/95 | -49.2 [-64.4, -35.6] 0/29 p=0 |
| full rename, sol | post hoc, 6 models | 12 | 98.75 (0.995833) | flag | flag | flag | flag | -23.0 [-27.9, -18.1] 0/103 | -57.6 [-72.9, -42.4] 0/34 p=0 |
| full rename, sol | post hoc, 6 models | 12 | stated (0.995833) | flag | flag | flag | flag | -23.0 [-29.0, -17.2] 0/103 | -57.6 [-76.3, -39.0] 0/34 p=0 |
| full rename, sol | post hoc, 6 models | 12 | 97.5 (0.995833) | flag | flag | flag | flag | -23.0 [-27.5, -18.5] 0/103 | -57.6 [-71.2, -44.1] 0/34 p=0 |
| full rename, astra | post hoc, 6 models | 12 | 98.75 (0.995833) | flag | flag | flag | flag | -31.0 [-36.4, -25.7] 0/139 | -79.7 [-91.5, -66.1] 0/47 p=0 |
| full rename, astra | post hoc, 6 models | 12 | stated (0.995833) | flag | flag | flag | flag | -31.0 [-37.5, -25.0] 0/139 | -79.7 [-93.2, -64.4] 0/47 p=0 |
| full rename, astra | post hoc, 6 models | 12 | 97.5 (0.995833) | flag | flag | flag | flag | -31.0 [-35.9, -26.3] 0/139 | -79.7 [-91.5, -67.8] 0/47 p=0 |
| full rename, luna | post hoc, 6 models | 12 | 98.75 (0.995833) | flag | flag | flag | flag | -17.6 [-22.1, -13.4] 0/79 | -33.9 [-50.8, -20.3] 0/20 p=0 |
| full rename, luna | post hoc, 6 models | 12 | stated (0.995833) | flag | flag | flag | flag | -17.6 [-22.8, -12.9] 0/79 | -33.9 [-54.2, -18.6] 0/20 p=0 |
| full rename, luna | post hoc, 6 models | 12 | 97.5 (0.995833) | flag | flag | flag | flag | -17.6 [-21.9, -13.6] 0/79 | -33.9 [-49.2, -20.3] 0/20 p=0 |
| broad rewrite, sonnet | prospective, 2 models | 4 | 98.75 (0.9875) | hold | hold | hold | hold | +3.6 [+0.9, +6.0] 19/3 | +1.7 [+0.0, +6.8] 1/0 p=1 |
| broad rewrite, sonnet | prospective, 2 models | 4 | stated (0.9875) | hold | hold | hold | hold | +3.6 [+0.9, +6.0] 19/3 | +1.7 [+0.0, +6.8] 1/0 p=1 |
| broad rewrite, sonnet | prospective, 2 models | 4 | 97.5 (0.9875) | hold | hold | hold | hold | +3.6 [+1.1, +5.8] 19/3 | +1.7 [+0.0, +6.8] 1/0 p=1 |
| broad rewrite, sol | prospective, 2 models | 4 | 98.75 (0.9875) | flag | flag | flag | flag | +5.4 [+2.7, +8.3] 26/2 | +8.5 [-3.4, +20.3] 7/2 p=0.18 |
| broad rewrite, sol | prospective, 2 models | 4 | stated (0.9875) | flag | flag | flag | flag | +5.4 [+2.7, +8.3] 26/2 | +8.5 [-3.4, +20.3] 7/2 p=0.18 |
| broad rewrite, sol | prospective, 2 models | 4 | 97.5 (0.9875) | flag | flag | flag | flag | +5.4 [+2.9, +8.0] 26/2 | +8.5 [-1.7, +20.3] 7/2 p=0.18 |
| steered th, sonnet | prospective, 2 models | 4 | 98.75 (0.9875) | flag | flag | flag | flag | +8.3 [+5.1, +11.8] 37/0 | +11.9 [+1.7, +23.7] 7/0 p=0.0156 |
| steered th, sonnet | prospective, 2 models | 4 | stated (0.9875) | flag | flag | flag | flag | +8.3 [+5.1, +11.8] 37/0 | +11.9 [+1.7, +23.7] 7/0 p=0.0156 |
| steered th, sonnet | prospective, 2 models | 4 | 97.5 (0.9875) | flag | flag | flag | flag | +8.3 [+5.4, +11.4] 37/0 | +11.9 [+3.4, +22.0] 7/0 p=0.0156 |
| steered th, haiku | prospective, 2 models | 4 | 98.75 (0.9875) | flag | flag | flag | flag | +34.2 [+28.6, +40.0] 154/1 | +69.5 [+54.2, +84.7] 41/0 p=0 |
| steered th, haiku | prospective, 2 models | 4 | stated (0.9875) | flag | flag | flag | flag | +34.2 [+28.6, +40.0] 154/1 | +69.5 [+54.2, +84.7] 41/0 p=0 |
| steered th, haiku | prospective, 2 models | 4 | 97.5 (0.9875) | flag | flag | flag | flag | +34.2 [+29.2, +39.5] 154/1 | +69.5 [+55.9, +83.1] 41/0 p=0 |
| steered tg, sonnet | prospective, 2 models | 4 | 98.75 (0.9875) | flag | flag | flag | flag | +11.6 [+7.8, +15.6] 53/1 | +25.4 [+11.9, +40.7] 15/0 p=0.0001 |
| steered tg, sonnet | prospective, 2 models | 4 | stated (0.9875) | flag | flag | flag | flag | +11.6 [+7.8, +15.6] 53/1 | +25.4 [+11.9, +40.7] 15/0 p=0.0001 |
| steered tg, sonnet | prospective, 2 models | 4 | 97.5 (0.9875) | flag | flag | flag | flag | +11.6 [+8.3, +15.2] 53/1 | +25.4 [+13.6, +37.3] 15/0 p=0.0001 |
| steered tg, haiku | prospective, 2 models | 4 | 98.75 (0.9875) | flag | flag | flag | flag | +29.5 [+24.1, +35.3] 133/1 | +49.2 [+30.5, +64.4] 29/0 p=0 |
| steered tg, haiku | prospective, 2 models | 4 | stated (0.9875) | flag | flag | flag | flag | +29.5 [+24.1, +35.3] 133/1 | +49.2 [+30.5, +64.4] 29/0 p=0 |
| steered tg, haiku | prospective, 2 models | 4 | 97.5 (0.9875) | flag | flag | flag | flag | +29.5 [+24.6, +34.6] 133/1 | +49.2 [+33.9, +62.7] 29/0 p=0 |
| rewrite h1, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | flag | flag | flag | +33.7 [+28.3, +39.5] 151/0 | +74.6 [+57.6, +88.1] 44/0 p=0 |
| rewrite h1, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | flag | flag | +33.7 [+28.8, +39.1] 151/0 | +74.6 [+61.0, +86.4] 44/0 p=0 |
| rewrite h1, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | flag | flag | +33.7 [+28.8, +39.1] 151/0 | +74.6 [+61.0, +86.4] 44/0 p=0 |
| rewrite h2, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | flag | flag | flag | +44.6 [+39.1, +50.7] 200/0 | +84.7 [+72.9, +94.9] 50/0 p=0 |
| rewrite h2, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | flag | flag | +44.6 [+39.3, +50.0] 200/0 | +84.7 [+74.6, +94.9] 50/0 p=0 |
| rewrite h2, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | flag | flag | +44.6 [+39.3, +50.0] 200/0 | +84.7 [+74.6, +94.9] 50/0 p=0 |
| rewrite h3, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | flag | flag | flag | +44.6 [+38.6, +50.9] 200/0 | +83.1 [+69.5, +94.9] 49/0 p=0 |
| rewrite h3, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | flag | flag | +44.6 [+39.1, +50.0] 200/0 | +83.1 [+71.2, +93.2] 49/0 p=0 |
| rewrite h3, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | flag | flag | +44.6 [+39.1, +50.0] 200/0 | +83.1 [+71.2, +93.2] 49/0 p=0 |
| rewrite g1, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | flag | flag | flag | +29.5 [+24.1, +34.8] 132/0 | +44.1 [+28.8, +61.0] 26/0 p=0 |
| rewrite g1, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | flag | flag | +29.5 [+24.8, +34.4] 132/0 | +44.1 [+30.5, +59.3] 26/0 p=0 |
| rewrite g1, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | flag | flag | +29.5 [+24.8, +34.4] 132/0 | +44.1 [+30.5, +59.3] 26/0 p=0 |
| rewrite g2, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | flag | flag | flag | +25.9 [+20.5, +31.9] 117/1 | +52.5 [+35.6, +69.5] 31/0 p=0 |
| rewrite g2, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | flag | flag | +25.9 [+21.2, +30.8] 117/1 | +52.5 [+39.0, +67.8] 31/0 p=0 |
| rewrite g2, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | flag | flag | +25.9 [+21.2, +30.8] 117/1 | +52.5 [+39.0, +67.8] 31/0 p=0 |
| rewrite g3, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | flag | flag | flag | +31.9 [+26.3, +37.9] 144/1 | +50.8 [+35.6, +66.1] 30/0 p=0 |
| rewrite g3, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | flag | flag | +31.9 [+26.8, +37.3] 144/1 | +50.8 [+37.3, +64.4] 30/0 p=0 |
| rewrite g3, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | flag | flag | +31.9 [+26.8, +37.3] 144/1 | +50.8 [+37.3, +64.4] 30/0 p=0 |
| rewrite n1, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | hold | hold | hold | +4.2 [+1.6, +7.1] 22/3 | +11.9 [+1.7, +22.0] 7/0 p=0.0156 |
| rewrite n1, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | hold | hold | +4.2 [+2.0, +6.9] 22/3 | +11.9 [+3.4, +22.0] 7/0 p=0.0156 |
| rewrite n1, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | hold | hold | +4.2 [+2.0, +6.9] 22/3 | +11.9 [+3.4, +22.0] 7/0 p=0.0156 |
| rewrite n2, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | flag | flag | flag | +7.8 [+4.7, +11.4] 39/4 | +13.6 [+1.7, +27.1] 9/1 p=0.0215 |
| rewrite n2, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | flag | flag | +7.8 [+4.9, +11.2] 39/4 | +13.6 [+3.4, +25.4] 9/1 p=0.0215 |
| rewrite n2, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | flag | flag | +7.8 [+4.9, +11.2] 39/4 | +13.6 [+3.4, +25.4] 9/1 p=0.0215 |
| rewrite n3, haiku | post hoc, 1 model | 2 | 98.75 (0.975) | flag | flag | flag | flag | +6.0 [+2.9, +9.4] 31/4 | +8.5 [-5.1, +22.0] 7/2 p=0.18 |
| rewrite n3, haiku | post hoc, 1 model | 2 | stated (0.975) | flag | flag | flag | flag | +6.0 [+3.1, +8.9] 31/4 | +8.5 [-3.4, +20.3] 7/2 p=0.18 |
| rewrite n3, haiku | post hoc, 1 model | 2 | 97.5 (0.975) | flag | flag | flag | flag | +6.0 [+3.1, +8.9] 31/4 | +8.5 [-3.4, +20.3] 7/2 p=0.18 |
| field order (10 answers), haiku | prospective, 1 model, 2 updates | 4 | 98.75 (0.9875) | hold | hold | hold | hold | +0.2 [-1.8, +2.2] 7/6 | +1.2 [-3.6, +6.6] 4/5 p=1 |
| field order (10 answers), haiku | prospective, 1 model, 2 updates | 4 | stated (0.9875) | hold | hold | hold | hold | +0.2 [-1.8, +2.2] 7/6 | +1.2 [-3.6, +6.6] 4/5 p=1 |
| field order (10 answers), haiku | prospective, 1 model, 2 updates | 4 | 97.5 (0.9875) | hold | hold | hold | hold | +0.2 [-1.6, +2.0] 7/6 | +1.2 [-3.2, +5.9] 4/5 p=1 |
| repeat (10 answers), haiku | prospective, 1 model, 2 updates | 4 | 98.75 (0.9875) | pass | pass | pass | pass | +0.2 [-0.9, +1.6] 3/2 | +0.1 [-1.8, +2.2] 4/4 p=1 |
| repeat (10 answers), haiku | prospective, 1 model, 2 updates | 4 | stated (0.9875) | pass | pass | pass | pass | +0.2 [-0.9, +1.6] 3/2 | +0.1 [-1.8, +2.2] 4/4 p=1 |
| repeat (10 answers), haiku | prospective, 1 model, 2 updates | 4 | 97.5 (0.9875) | pass | pass | pass | pass | +0.2 [-0.9, +1.3] 3/2 | +0.1 [-1.5, +1.9] 4/4 p=1 |

Unchanged pairs whose decision is not a hold at some level:

| Pair | Level | First | Revised | Exact first | Specific | Exact specific |
|---|---|---|---|---|---|---|
| sonnet era1 read 1 v era1 read 2 | 98.75 | flag | hold | hold | +8.5 [+1.7, +18.6] 5/0 | [-7.64, 23.12] |
| sonnet era1 read 1 v era1 read 2 | 97.5 | flag | hold | hold | +8.5 [+1.7, +16.9] 5/0 | [-6.26, 21.72] |
| sonnet era1 read 1 v erp | 98.75 | flag | hold | hold | +8.5 [+1.7, +18.6] 5/0 | [-7.64, 23.12] |
| sonnet era1 read 1 v erp | 97.5 | flag | hold | hold | +8.5 [+1.7, +16.9] 5/0 | [-6.26, 21.72] |
| sonnet era1 read 2 v erp | 98.75 | pass | pass | hold | +0.0 [+0.0, +0.0] 0/0 | [-9.31, 9.31] |
| sonnet era1 read 2 v erp | 99.5 | pass | pass | hold | +0.0 [+0.0, +0.0] 0/0 | [-10.71, 10.71] |
| sonnet era1 read 2 v erp | 97.5 | pass | pass | hold | +0.0 [+0.0, +0.0] 0/0 | [-8.24, 8.24] |
| haiku erm v erc2 | 98.75 | pass | pass | hold | +0.0 [+0.0, +0.0] 0/0 | [-9.31, 9.31] |
| haiku erm v erc2 | 99.5 | pass | pass | hold | +0.0 [+0.0, +0.0] 0/0 | [-10.71, 10.71] |
| haiku erm v erc2 | 97.5 | pass | pass | hold | +0.0 [+0.0, +0.0] 0/0 | [-8.24, 8.24] |

### A2. Table 15 exploratory rows

- value-only rename, sonnet, 95%: open -12.35 [-14.66, -10.24] 0/113; specific -31.3 [-37.3, -25.5] 0/79 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, sonnet, 99.5%: open -12.35 [-15.49, -8.88] 0/113; specific -31.3 [-39.5, -23.0] 0/79 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, haiku, 95%: open -2.23 [-3.22, -1.36] 0/26; specific -21.6 [-27.0, -16.7] 4/73 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, haiku, 99.5%: open -2.23 [-3.63, -1.07] 0/26; specific -21.6 [-28.5, -14.4] 4/73 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, sol, 95%: open -18.41 [-21.39, -15.80] 1/149; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, sol, 99.5%: open -18.41 [-22.51, -15.05] 1/149; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, luna, 95%: open -16.89 [-19.41, -14.54] 1/173; specific -43.6 [-49.8, -37.9] 1/120 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, luna, 99.5%: open -16.89 [-20.49, -13.59] 1/173; specific -43.6 [-52.2, -34.6] 1/120 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, deepseek, 95%: open -10.30 [-12.41, -8.31] 2/85; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, deepseek, 99.5%: open -10.30 [-13.90, -7.32] 2/85; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, qwen, 95%: open -8.73 [-10.94, -6.51] 6/69; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- value-only rename, qwen, 99.5%: open -8.73 [-11.91, -5.54] 6/69; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- value-only rename, gemma, 95%: open -17.58 [-20.45, -14.96] 0/141; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- value-only rename, gemma, 99.5%: open -17.58 [-21.70, -14.21] 0/141; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- opaque code, sonnet, 95%: open -11.61 [-13.80, -9.54] 0/108; specific -23.4 [-28.8, -18.5] 0/59 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- opaque code, sonnet, 99.5%: open -11.61 [-14.79, -8.38] 0/108; specific -23.4 [-31.1, -15.5] 0/59 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- opaque code, haiku, 95%: open -0.87 [-1.73, -0.04] 7/20; specific -7.6 [-11.6, -3.6] 10/34 p=0.0004; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- opaque code, haiku, 99.5%: open -0.87 [-2.07, +0.29] 7/20; specific -7.6 [-13.2, -2.0] 10/34 p=0.0004; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- opaque code, sol, 95%: open -5.96 [-7.83, -4.35] 3/51; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- opaque code, sol, 99.5%: open -5.96 [-8.57, -3.73] 3/51; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- opaque code, luna, 95%: open -15.04 [-17.43, -12.80] 5/162; specific -22.3 [-27.5, -17.5] 2/65 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- opaque code, luna, 99.5%: open -15.04 [-18.50, -11.90] 5/162; specific -22.3 [-30.0, -15.3] 2/65 p=0; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- opaque code, deepseek, 95%: open -7.44 [-9.80, -5.33] 12/72; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- opaque code, deepseek, 99.5%: open -7.44 [-10.79, -4.34] 12/72; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- opaque code, qwen, 95%: open -5.26 [-7.88, -2.77] 24/62; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- opaque code, qwen, 99.5%: open -5.26 [-8.85, -1.80] 24/62; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- opaque code, gemma, 95%: open -16.75 [-19.50, -14.12] 0/134; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- opaque code, gemma, 99.5%: open -16.75 [-20.50, -13.38] 0/134; specific -; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), sonnet, 95%: open -19.1 [-22.8, -15.5] 1/89; specific -47.5 [-60.2, -35.6] 0/31; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), sonnet, 99.58%: open -19.1 [-24.4, -13.8] 1/89; specific -47.5 [-65.3, -28.8] 0/31; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), haiku, 95%: open -5.8 [-7.9, -3.9] 0/32; specific -8.6 [-16.4, -2.6] 0/6; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- tool-call full rename (all answers), haiku, 99.58%: open -5.8 [-8.9, -3.2] 0/32; specific -8.6 [-19.8, -0.9] 0/6; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'hold', 'revised': 'hold'}
- tool-call full rename (all answers), opus, 95%: open -20.8 [-24.8, -17.0] 2/95; specific -49.2 [-62.7, -37.3] 0/29; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), opus, 99.58%: open -20.8 [-26.8, -14.7] 2/95; specific -49.2 [-67.8, -32.2] 0/29; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), sol, 95%: open -23.5 [-27.5, -19.8] 0/118; specific -57.6 [-69.5, -45.8] 0/38; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), sol, 99.58%: open -23.5 [-29.1, -17.9] 0/118; specific -57.6 [-74.6, -40.7] 0/38; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), astra, 95%: open -31.0 [-35.3, -27.0] 0/139; specific -79.7 [-89.8, -69.5] 0/47; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), astra, 99.58%: open -31.0 [-37.5, -25.0] 0/139; specific -79.7 [-93.2, -64.4] 0/47; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), luna, 95%: open -18.2 [-21.7, -14.8] 0/91; specific -33.9 [-46.6, -22.0] 0/23; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}
- tool-call full rename (all answers), luna, 99.58%: open -18.2 [-23.2, -13.3] 0/91; specific -33.9 [-52.5, -18.6] 0/23; L3 {'first': 'flag', 'revised': 'flag'}; L5 {'first': 'flag', 'revised': 'flag'}; L10 {'first': 'flag', 'revised': 'flag'}

### A3. Held-out rows (approximate)

```
{
 "note": "approximate: normal approximation from the stored 95% intervals; the sign condition is not applied (no stored sign counts for most rows)",
 "full rename": {
  "C": 14,
  "level": 0.996429,
  "95": {
   "panel": {
    "decision": "flag",
    "sets": [
     [
      -12.95,
      -15.88,
      -10.02
     ],
     [
      -29.13,
      -34.74,
      -23.52
     ]
    ]
   },
   "sonnet": {
    "decision": "flag",
    "sets": [
     [
      -11.74,
      -15.96,
      -7.51
     ],
     [
      -19.48,
      -28.57,
      -10.39
     ]
    ]
   },
   "haiku": {
    "decision": "flag",
    "sets": [
     [
      -4.69,
      -7.51,
      -1.88
     ],
     [
      -23.38,
      -32.47,
      -14.29
     ]
    ]
   },
   "sol": {
    "decision": "flag",
    "sets": [
     [
      -17.37,
      -22.54,
      -12.21
     ],
     [
      -25.97,
      -35.71,
      -16.23
     ]
    ]
   },
   "luna": {
    "decision": "flag",
    "sets": [
     [
      -17.37,
      -22.54,
      -12.21
     ],
     [
      -57.14,
      -67.53,
      -46.75
     ]
    ]
   },
   "deepseek": {
    "decision": "flag",
    "sets": [
     [
      -11.74,
      -16.2,
      -7.28
     ],
     [
      -20.78,
      -30.52,
      -11.04
     ]
    ]
   },
   "qwen": {
    "decision": "flag",
    "sets": [
     [
      -7.49,
      -12.03,
      -2.94
     ],
     [
      -23.33,
      -36.67,
      -10.0
     ]
    ]
   },
   "gemma": {
    "decision": "flag",
    "sets": [
     [
      -17.92,
      -23.11,
      -12.74
     ],
     [
      -33.77,
      -44.81,
      -22.73
     ]
    ]
   },
   "tally_models": {
    "flag": 7
   }
  },
  "stated": {
   "panel": {
    "decision": "flag",
    "sets": [
     [
      -12.95,
      -17.31,
      -8.6
     ],
     [
      -29.13,
      -37.47,
      -20.78
     ]
    ]
   },
   "sonnet": {
    "decision": "flag",
    "sets": [
     [
      -11.74,
      -18.02,
      -5.46
     ],
     [
      -19.48,
      -33.0,
      -5.97
     ]
    ]
   },
   "haiku": {
    "decision": "flag",
    "sets": [
     [
      -4.69,
      -8.88,
      -0.51
     ],
     [
      -23.38,
      -36.89,
      -9.86
     ]
    ]
   },
   "sol": {
    "decision": "flag",
    "sets": [
     [
      -17.37,
      -25.05,
      -9.69
     ],
     [
      -25.97,
      -40.45,
      -11.49
     ]
    ]
   },
   "luna": {
    "decision": "flag",
    "sets": [
     [
      -17.37,
      -25.05,
      -9.69
     ],
     [
      -57.14,
      -72.59,
      -41.7
     ]
    ]
   },
   "deepseek": {
    "decision": "flag",
    "sets": [
     [
      -11.74,
      -18.37,
      -5.11
     ],
     [
      -20.78,
      -35.26,
      -6.3
     ]
    ]
   },
   "qwen": {
    "decision": "flag",
    "sets": [
     [
      -7.49,
      -14.24,
      -0.73
     ],
     [
      -23.33,
      -43.15,
      -3.51
     ]
    ]
   },
   "gemma": {
    "decision": "flag",
    "sets": [
     [
      -17.92,
      -25.64,
      -10.21
     ],
     [
      -33.77,
      -50.18,
      -17.36
     ]
    ]
   },
   "tally_models": {
    "flag": 7
   }
  }
 },
 "neutral value": {
  "C": 14,
  "level": 0.996429,
  "95": {
   "panel": {
    "decision": "flag",
    "sets": [
     [
      -16.12,
      -19.71,
      -12.53
     ],
     [
      -41.5,
      -47.65,
      -35.34
     ]
    ]
   },
   "sonnet": {
    "decision": "flag",
    "sets": [
     [
      -14.55,
      -19.25,
      -9.86
     ],
     [
      -46.75,
      -57.79,
      -35.71
     ]
    ]
   },
   "haiku": {
    "decision": "flag",
    "sets": [
     [
      -2.82,
      -4.93,
      -0.7
     ],
     [
      -23.38,
      -33.12,
      -13.64
     ]
    ]
   },
   "sol": {
    "decision": "flag",
    "sets": [
     [
      -27.7,
      -33.57,
      -21.83
     ],
     [
      -33.77,
      -44.81,
      -22.73
     ]
    ]
   },
   "luna": {
    "decision": "flag",
    "sets": [
     [
      -18.31,
      -23.71,
      -12.91
     ],
     [
      -58.44,
      -69.48,
      -47.4
     ]
    ]
   },
   "deepseek": {
    "decision": "flag",
    "sets": [
     [
      -15.49,
      -20.42,
      -10.56
     ],
     [
      -44.16,
      -55.84,
      -32.47
     ]
    ]
   },
   "qwen": {
    "decision": "flag",
    "sets": [
     [
      -8.38,
      -12.3,
      -4.45
     ],
     [
      -22.22,
      -34.92,
      -9.52
     ]
    ]
   },
   "gemma": {
    "decision": "flag",
    "sets": [
     [
      -21.43,
      -26.9,
      -15.95
     ],
     [
      -58.44,
      -68.83,
      -48.05
     ]
    ]
   },
   "tally_models": {
    "flag": 7
   }
  },
  "stated": {
   "panel": {
    "decision": "flag",
    "sets": [
     [
      -16.12,
      -21.45,
      -10.78
     ],
     [
      -41.5,
      -50.64,
      -32.35
     ]
    ]
   },
   "sonnet": {
    "decision": "flag",
    "sets": [
     [
      -14.55,
      -21.53,
      -7.57
     ],
     [
      -46.75,
      -63.16,
      -30.34
     ]
    ]
   },
   "haiku": {
    "decision": "flag",
    "sets": [
     [
      -2.82,
      -5.96,
      0.32
     ],
     [
      -23.38,
      -37.86,
      -8.9
     ]
    ]
   },
   "sol": {
    "decision": "flag",
    "sets": [
     [
      -27.7,
      -36.42,
      -18.98
     ],
     [
      -33.77,
      -50.18,
      -17.36
     ]
    ]
   },
   "luna": {
    "decision": "flag",
    "sets": [
     [
      -18.31,
      -26.34,
      -10.28
     ],
     [
      -58.44,
      -74.85,
      -42.03
     ]
    ]
   },
   "deepseek": {
    "decision": "flag",
    "sets": [
     [
      -15.49,
      -22.82,
      -8.16
     ],
     [
      -44.16,
      -61.53,
      -26.78
     ]
    ]
   },
   "qwen": {
    "decision": "flag",
    "sets": [
     [
      -8.38,
      -14.21,
      -2.54
     ],
     [
      -22.22,
      -41.1,
      -3.34
     ]
    ]
   },
   "gemma": {
    "decision": "flag",
    "sets": [
     [
      -21.43,
      -29.57,
      -13.29
     ],
     [
      -58.44,
      -73.89,
      -43.0
     ]
    ]
   },
   "tally_models": {
    "flag": 7
   }
  }
 },
 "description edit": {
  "C": 14,
  "level": 0.996429,
  "95": {
   "panel": {
    "decision": "pass",
    "sets": [
     [
      0.88,
      -0.32,
      2.07
     ],
     [
      0.74,
      -2.61,
      4.1
     ]
    ]
   },
   "sonnet": {
    "decision": "more data",
    "sets": [
     [
      1.88,
      -0.94,
      4.69
     ],
     [
      2.6,
      -5.19,
      10.39
     ]
    ]
   },
   "haiku": {
    "decision": "more data",
    "sets": [
     [
      -0.94,
      -3.29,
      1.41
     ],
     [
      -5.19,
      -11.69,
      1.3
     ]
    ]
   },
   "sol": {
    "decision": "pass",
    "sets": [
     [
      -0.94,
      -3.76,
      1.88
     ],
     [
      1.3,
      -0.65,
      3.25
     ]
    ]
   },
   "luna": {
    "decision": "more data",
    "sets": [
     [
      2.82,
      -0.23,
      5.87
     ],
     [
      0.0,
      -6.49,
      6.49
     ]
    ]
   },
   "deepseek": {
    "decision": "more data",
    "sets": [
     [
      0.94,
      -3.3,
      5.19
     ],
     [
      5.19,
      -5.19,
      15.58
     ]
    ]
   },
   "qwen": {
    "decision": "more data",
    "sets": [
     [
      2.13,
      -2.13,
      6.38
     ],
     [
      0.0,
      -12.1,
      12.1
     ]
    ]
   },
   "gemma": {
    "decision": "pass",
    "sets": [
     [
      0.47,
      -1.9,
      2.84
     ],
     [
      1.32,
      -0.66,
      3.29
     ]
    ]
   },
   "tally_models": {
    "more data": 5,
    "pass": 2
   }
  },
  "stated": {
   "panel": {
    "decision": "more data",
    "sets": [
     [
      0.88,
      -0.9,
      2.65
     ],
     [
      0.74,
      -4.25,
      5.73
     ]
    ]
   },
   "sonnet": {
    "decision": "more data",
    "sets": [
     [
      1.88,
      -2.31,
      6.07
     ],
     [
      2.6,
      -8.99,
      14.18
     ]
    ]
   },
   "haiku": {
    "decision": "more data",
    "sets": [
     [
      -0.94,
      -4.43,
      2.55
     ],
     [
      -5.19,
      -14.85,
      4.46
     ]
    ]
   },
   "sol": {
    "decision": "more data",
    "sets": [
     [
      -0.94,
      -5.13,
      3.25
     ],
     [
      1.3,
      -1.6,
      4.19
     ]
    ]
   },
   "luna": {
    "decision": "more data",
    "sets": [
     [
      2.82,
      -1.72,
      7.35
     ],
     [
      0.0,
      -9.65,
      9.65
     ]
    ]
   },
   "deepseek": {
    "decision": "more data",
    "sets": [
     [
      0.94,
      -5.37,
      7.25
     ],
     [
      5.19,
      -10.25,
      20.64
     ]
    ]
   },
   "qwen": {
    "decision": "more data",
    "sets": [
     [
      2.13,
      -4.2,
      8.45
     ],
     [
      0.0,
      -17.98,
      17.98
     ]
    ]
   },
   "gemma": {
    "decision": "pass",
    "sets": [
     [
      0.47,
      -3.05,
      4.0
     ],
     [
      1.32,
      -1.62,
      4.25
     ]
    ]
   },
   "tally_models": {
    "more data": 6,
    "pass": 1
   }
  }
 },
 "unrelated rename": {
  "C": 2,
  "level": 0.975,
  "95": {
   "panel": {
    "decision": "more data",
    "sets": [
     [
      0.23,
      -1.64,
      2.11
     ]
    ]
   },
   "sonnet": {
    "decision": "more data",
    "sets": [
     [
      0.94,
      -1.88,
      3.76
     ]
    ]
   },
   "haiku": {
    "decision": "more data",
    "sets": [
     [
      -0.47,
      -3.05,
      2.11
     ]
    ]
   },
   "tally_models": {
    "more data": 2
   }
  },
  "stated": {
   "panel": {
    "decision": "more data",
    "sets": [
     [
      0.23,
      -1.91,
      2.38
     ]
    ]
   },
   "sonnet": {
    "decision": "more data",
    "sets": [
     [
      0.94,
      -2.28,
      4.16
     ]
    ]
   },
   "haiku": {
    "decision": "more data",
    "sets": [
     [
      -0.47,
      -3.42,
      2.48
     ]
    ]
   },
   "tally_models": {
    "more data": 2
   }
  }
 }
}
```

### C. Error rates of one set with one answer per request (n = 59, 98.75%)

```
{
 "n": 59,
 "level": 0.9875,
 "nominal_error_one_tail": 0.00625,
 "exact_interval_no_change": [
  -9.314,
  9.314
 ],
 "exact_within_limits_counts": [],
 "true_change_above_L": [
  {
   "p_up": 0.051,
   "p_down": 0.0,
   "true_change": 5.1,
   "no_request_changes": 0.04557,
   "within_limits_percentile": 0.04557,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.18178,
   "meets_flag_revised_percentile": 0.00992,
   "meets_flag_exact": 1e-05
  },
  {
   "p_up": 0.06,
   "p_down": 0.0,
   "true_change": 6.0,
   "no_request_changes": 0.02597,
   "within_limits_percentile": 0.02597,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.27932,
   "meets_flag_revised_percentile": 0.02414,
   "meets_flag_exact": 4e-05
  },
  {
   "p_up": 0.08,
   "p_down": 0.0,
   "true_change": 8.0,
   "no_request_changes": 0.0073,
   "within_limits_percentile": 0.0073,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.51463,
   "meets_flag_revised_percentile": 0.09695,
   "meets_flag_exact": 0.00066
  },
  {
   "p_up": 0.07,
   "p_down": 0.01,
   "true_change": 6.0,
   "no_request_changes": 0.0073,
   "within_limits_percentile": 0.0073,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.23109,
   "meets_flag_revised_percentile": 0.03279,
   "meets_flag_exact": 0.00011
  },
  {
   "p_up": 0.08,
   "p_down": 0.02,
   "true_change": 6.0,
   "no_request_changes": 0.002,
   "within_limits_percentile": 0.002,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.17953,
   "meets_flag_revised_percentile": 0.03891,
   "meets_flag_exact": 0.00025
  },
  {
   "p_up": 0.1,
   "p_down": 0.04,
   "true_change": 6.0,
   "no_request_changes": 0.00014,
   "within_limits_percentile": 0.00014,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.10921,
   "meets_flag_revised_percentile": 0.04238,
   "meets_flag_exact": 0.00067
  }
 ],
 "true_change_zero": [
  {
   "p_up": 0.01,
   "p_down": 0.01,
   "true_change": 0.0,
   "no_request_changes": 0.30363,
   "within_limits_percentile": 0.30363,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.00037,
   "meets_flag_revised_percentile": 0.0,
   "meets_flag_exact": 0.0
  },
  {
   "p_up": 0.02,
   "p_down": 0.02,
   "true_change": 0.0,
   "no_request_changes": 0.08995,
   "within_limits_percentile": 0.08995,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.00432,
   "meets_flag_revised_percentile": 2e-05,
   "meets_flag_exact": 0.0
  },
  {
   "p_up": 0.04,
   "p_down": 0.04,
   "true_change": 0.0,
   "no_request_changes": 0.0073,
   "within_limits_percentile": 0.0073,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.0181,
   "meets_flag_revised_percentile": 0.0006,
   "meets_flag_exact": 0.0
  },
  {
   "p_up": 0.06,
   "p_down": 0.06,
   "true_change": 0.0,
   "no_request_changes": 0.00053,
   "within_limits_percentile": 0.00053,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.01916,
   "meets_flag_revised_percentile": 0.00242,
   "meets_flag_exact": 0.0
  },
  {
   "p_up": 0.1,
   "p_down": 0.1,
   "true_change": 0.0,
   "no_request_changes": 0.0,
   "within_limits_percentile": 0.0,
   "within_limits_exact": 0.0,
   "meets_flag_first_percentile": 0.01266,
   "meets_flag_revised_percentile": 0.00503,
   "meets_flag_exact": 6e-05
  }
 ],
 "note": "within limits with a true change above L is a wrong pass of this set; meets flag rule with a true change of 0 is a wrong flag of this set. The percentile bootstrap for each count uses 2,000 binomial draws (the same distribution as resampling requests)."
}
```

### D. Order of the two arms

```
[
 {
  "case": "haiku: era1 read 1 against erc2 (all_answers)",
  "original index rule": {
   "forward": "pass",
   "reverse": "hold",
   "forward_specific": [
    0.69,
    -3.276,
    5.0
   ],
   "reverse_specific": [
    -0.69,
    -5.172,
    3.103
   ]
  },
  "symmetric index rule": {
   "forward": "hold",
   "reverse": "hold",
   "forward_specific": [
    0.69,
    -3.276,
    5.172
   ],
   "reverse_specific": [
    -0.69,
    -5.172,
    3.276
   ]
  }
 },
 {
  "case": "haiku: erm against erc (all_answers)",
  "original index rule": {
   "forward": "hold",
   "reverse": "pass",
   "forward_specific": [
    -0.169,
    -5.085,
    4.576
   ],
   "reverse_specific": [
    0.169,
    -4.576,
    4.915
   ]
  },
  "symmetric index rule": {
   "forward": "hold",
   "reverse": "hold",
   "forward_specific": [
    -0.169,
    -5.085,
    4.576
   ],
   "reverse_specific": [
    0.169,
    -4.576,
    5.085
   ]
  }
 }
]
```
