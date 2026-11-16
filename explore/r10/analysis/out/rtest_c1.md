## Analysis C.1: the revised flag condition, per-request change, detection (post hoc)

Level 98.75% for tool calls (alpha 0.0125); 95% for the form rows (alpha 0.05). L = 5. Revised flag condition: |change| >= L, the interval excludes zero, and the exact sign test over prefixes gives p <= alpha.

### 1. Unchanged tool, one answer per prefix (29 pairs)

| Model | Pair | Open: change [98.75%], up/down | Specific: change [98.75%], up/down, sign p | First rule | Revised (0.0125) | Revised (0.025) |
|---|---|---|---|---|---|---|
| sonnet | era1 read 1 v era1 read 2 | -0.2 [-1.6, +1.1], 2/3 | +8.5 [+1.7, +18.6], 5/0, 0.0625 | flag | hold | hold |
| sonnet | era1 read 1 v fill read 3 | -0.2 [-1.8, +1.3], 3/4 | +3.4 [-5.1, +11.9], 3/1, 0.6250 | hold | hold | hold |
| sonnet | era1 read 1 v erp | -1.3 [-3.6, +0.9], 4/10 | +8.5 [+1.7, +18.6], 5/0, 0.0625 | flag | hold | hold |
| sonnet | era1 read 2 v fill read 3 | +0.0 [-1.8, +1.8], 6/6 | -5.1 [-13.6, +0.0], 0/3, 0.2500 | hold | hold | hold |
| sonnet | era1 read 2 v erp | -1.1 [-3.3, +1.1], 5/10 | +0.0 [+0.0, +0.0], 0/0, 1.0000 | pass | pass | pass |
| sonnet | fill read 3 v erp | -1.1 [-3.3, +0.9], 5/10 | +5.1 [+0.0, +11.9], 3/0, 0.2500 | hold | hold | hold |
| haiku | era1 read 1 v era1 read 2 | +0.9 [-0.7, +2.7], 7/3 | -1.7 [-6.9, +0.0], 0/1, 1.0000 | hold | hold | hold |
| haiku | era1 read 1 v erm | -0.4 [-1.8, +0.7], 1/3 | +1.7 [-5.2, +10.3], 2/1, 1.0000 | hold | hold | hold |
| haiku | era1 read 1 v ers | -0.2 [-1.8, +1.6], 4/5 | +3.4 [-5.2, +12.1], 3/1, 0.6250 | hold | hold | hold |
| haiku | era1 read 1 v erc | +0.0 [-1.6, +1.6], 3/3 | +1.7 [+0.0, +6.9], 1/0, 1.0000 | hold | hold | hold |
| haiku | era1 read 1 v erc2 | +0.2 [-1.6, +2.0], 5/4 | +1.7 [-5.2, +10.3], 2/1, 1.0000 | hold | hold | hold |
| haiku | era1 read 2 v erm | -1.1 [-3.1, +0.7], 3/8 | +3.4 [-3.4, +12.1], 3/1, 0.6250 | hold | hold | hold |
| haiku | era1 read 2 v ers | -0.9 [-2.9, +1.1], 4/8 | +5.2 [-3.4, +15.5], 4/1, 0.3750 | hold | hold | hold |
| haiku | era1 read 2 v erc | -0.7 [-2.5, +1.1], 3/6 | +3.4 [+0.0, +10.3], 2/0, 0.5000 | hold | hold | hold |
| haiku | era1 read 2 v erc2 | -0.4 [-2.2, +1.1], 3/5 | +3.4 [-3.4, +12.1], 3/1, 0.6250 | hold | hold | hold |
| haiku | erm v ers | +0.2 [-1.3, +1.8], 4/3 | +1.7 [+0.0, +6.8], 1/0, 1.0000 | hold | hold | hold |
| haiku | erm v erc | +0.4 [-0.9, +2.0], 4/2 | +1.7 [-5.1, +10.2], 2/1, 1.0000 | hold | hold | hold |
| haiku | erm v erc2 | +0.7 [-0.9, +2.2], 5/2 | +0.0 [+0.0, +0.0], 0/0, 1.0000 | pass | pass | pass |
| haiku | ers v erc | +0.2 [-1.1, +1.8], 4/3 | +0.0 [-10.2, +8.5], 2/2, 1.0000 | hold | hold | hold |
| haiku | ers v erc2 | +0.4 [-0.9, +1.8], 4/2 | -1.7 [-6.8, +0.0], 0/1, 1.0000 | hold | hold | hold |
| haiku | erc v erc2 | +0.2 [-0.9, +1.6], 3/2 | -1.7 [-10.2, +5.1], 1/2, 1.0000 | hold | hold | hold |
| sol | era1 read 1 v era1 read 2 | +1.6 [-0.7, +3.8], 12/5 | -1.7 [-11.9, +8.5], 2/3, 1.0000 | hold | hold | hold |
| sol | era1 read 1 v fill read 3 | +0.9 [-1.1, +2.9], 8/4 | +0.0 [-6.8, +5.1], 1/1, 1.0000 | hold | hold | hold |
| sol | era1 read 1 v erp | -0.4 [-2.5, +1.6], 6/8 | +1.7 [-11.9, +11.9], 4/3, 1.0000 | hold | hold | hold |
| sol | era1 read 2 v fill read 3 | -0.7 [-2.9, +1.6], 6/9 | +1.7 [-5.1, +10.2], 2/1, 1.0000 | hold | hold | hold |
| sol | era1 read 2 v erp | -2.0 [-4.5, +0.0], 3/12 | +3.4 [-6.8, +13.6], 4/2, 0.6875 | hold | hold | hold |
| sol | fill read 3 v erp | -1.3 [-3.3, +0.4], 3/9 | +1.7 [-10.2, +11.9], 3/2, 1.0000 | hold | hold | hold |
| opus | era1 read 1 v fill read 2 | +1.3 [-1.3, +4.5], 16/10 | +3.4 [-5.1, +13.6], 3/1, 0.6250 | hold | hold | hold |
| luna | era1 read 1 v era1 read 2 | +0.9 [-1.6, +3.3], 11/7 | +0.0 [-10.2, +10.2], 3/3, 1.0000 | hold | hold | hold |

Tally: {"first rule: flag": 2, "first rule: hold": 25, "first rule: pass": 2, "open within limits: True": 29, "revised 0.0125: hold": 27, "revised 0.0125: pass": 2, "revised 0.025: hold": 27, "revised 0.025: pass": 2}

| Model | Pairs | First rule | Revised (0.0125) | Open prefixes changed (up/down) of pair-prefixes | Specific prefixes changed (up/down) |
|---|---|---|---|---|---|
| sonnet | 6 | flag 2, hold 3, pass 1 | hold 5, pass 1 | 68 of 2688 (25/43; 2.5%) | 20 of 354 (16/4) |
| haiku | 15 | hold 14, pass 1 | hold 14, pass 1 | 116 of 6710 (57/59; 1.7%) | 39 of 876 (26/13) |
| sol | 6 | hold 6 | hold 6 | 85 of 2688 (38/47; 3.2%) | 28 of 354 (16/12) |
| opus | 1 | hold 1 | hold 1 | 26 of 448 (16/10; 5.8%) | 4 of 59 (3/1) |
| luna | 1 | hold 1 | hold 1 | 18 of 448 (11/7; 4.0%) | 6 of 59 (3/3) |

### 2. Edits on the 554 prefixes (tool calls)

| Edit | Open: change [98.75%], up/down, sign p | Specific: change [98.75%], up/down, sign p | First rule | Revised (0.0125) | Revised (0.025) |
|---|---|---|---|---|---|
| full rename, sonnet | -19.2 [-23.7, -14.7], 0/86, 0 | -44.1 [-61.0, -28.8], 0/26, 0 | flag | flag | flag |
| full rename, haiku | -5.4 [-8.3, -2.9], 0/24, 0 | -8.6 [-19.0, -1.7], 0/5, 0.062 | flag | flag | flag |
| full rename, opus | -20.8 [-25.7, -15.8], 2/95, 0 | -49.2 [-66.1, -33.9], 0/29, 0 | flag | flag | flag |
| full rename, sol | -23.0 [-27.9, -18.1], 0/103, 0 | -57.6 [-72.9, -42.4], 0/34, 0 | flag | flag | flag |
| full rename, astra | -31.0 [-36.4, -25.7], 0/139, 0 | -79.7 [-91.5, -66.1], 0/47, 0 | flag | flag | flag |
| full rename, luna | -17.6 [-22.1, -13.4], 0/79, 0 | -33.9 [-50.8, -20.3], 0/20, 0 | flag | flag | flag |
| broad rewrite, sonnet | +3.6 [+0.9, +6.0], 19/3, 0.0009 | +1.7 [+0.0, +6.8], 1/0, 1 | hold | hold | hold |
| broad rewrite, sol | +5.4 [+2.7, +8.3], 26/2, 0 | +8.5 [-3.4, +20.3], 7/2, 0.18 | flag | flag | flag |
| steered th, sonnet | +8.3 [+5.1, +11.8], 37/0, 0 | +11.9 [+1.7, +23.7], 7/0, 0.016 | flag | flag | flag |
| steered th, haiku | +34.2 [+28.6, +40.0], 154/1, 0 | +69.5 [+54.2, +84.7], 41/0, 0 | flag | flag | flag |
| steered tg, sonnet | +11.6 [+7.8, +15.6], 53/1, 0 | +25.4 [+11.9, +40.7], 15/0, 0.0001 | flag | flag | flag |
| steered tg, haiku | +29.5 [+24.1, +35.3], 133/1, 0 | +49.2 [+30.5, +64.4], 29/0, 0 | flag | flag | flag |
| rewrite h1, haiku | +33.7 [+28.3, +39.5], 151/0, 0 | +74.6 [+57.6, +88.1], 44/0, 0 | flag | flag | flag |
| rewrite h2, haiku | +44.6 [+39.1, +50.7], 200/0, 0 | +84.7 [+72.9, +94.9], 50/0, 0 | flag | flag | flag |
| rewrite h3, haiku | +44.6 [+38.6, +50.9], 200/0, 0 | +83.1 [+69.5, +94.9], 49/0, 0 | flag | flag | flag |
| rewrite g1, haiku | +29.5 [+24.1, +34.8], 132/0, 0 | +44.1 [+28.8, +61.0], 26/0, 0 | flag | flag | flag |
| rewrite g2, haiku | +25.9 [+20.5, +31.9], 117/1, 0 | +52.5 [+35.6, +69.5], 31/0, 0 | flag | flag | flag |
| rewrite g3, haiku | +31.9 [+26.3, +37.9], 144/1, 0 | +50.8 [+35.6, +66.1], 30/0, 0 | flag | flag | flag |
| rewrite n1, haiku | +4.2 [+1.6, +7.1], 22/3, 0.0002 | +11.9 [+1.7, +22.0], 7/0, 0.016 | flag | hold | flag |
| rewrite n2, haiku | +7.8 [+4.7, +11.4], 39/4, 0 | +13.6 [+1.7, +27.1], 9/1, 0.021 | flag | flag | flag |
| rewrite n3, haiku | +6.0 [+2.9, +9.4], 31/4, 0 | +8.5 [-5.1, +22.0], 7/2, 0.18 | flag | flag | flag |
| field order (10 answers), haiku | +0.2 [-1.8, +2.2], 7/6, 1 | +1.2 [-3.6, +6.6], 4/5, 1 | hold | hold | hold |
| repeat (10 answers), haiku | +0.2 [-0.9, +1.6], 3/2, 1 | +0.1 [-1.8, +2.2], 4/4, 1 | pass | pass | pass |

Edit decisions that change at 0.0125: ['rewrite n1, haiku']

### 3. Form rows of Table 14 with stored sign counts (95%, alpha 0.05)

| Row | Open: change [95%], up/down, sign p | Specific: change [95%], up/down, sign p | First rule | Revised (0.05) |
|---|---|---|---|---|
| held-out full rename, sonnet | -11.7 [-16.4, -8.0], 0/25, 0 | -19.5 [-28.6, -10.4], 0/15, 0.0001 | flag | flag |
| held-out full rename, haiku | -4.7 [-7.5, -1.9], 0/10, 0.002 | -23.4 [-32.5, -14.3], 0/18, 0 | flag | flag |
| held-out full rename, sol | -17.4 [-23.0, -12.7], 0/37, 0 | -26.0 [-36.4, -16.9], 0/20, 0 | flag | flag |
| held-out full rename, luna | -17.4 [-23.0, -12.7], 0/37, 0 | -57.1 [-67.5, -46.8], 0/44, 0 | flag | flag |
| held-out full rename, deepseek | -11.7 [-16.4, -7.5], 1/26, 0 | -20.8 [-31.2, -11.7], 1/17, 0.0001 | flag | flag |
| held-out full rename, qwen | -7.5 [-12.3, -3.2], 2/16, 0.0013 | -23.3 [-36.7, -10.0], 4/18, 0.0043 | flag | flag |
| held-out full rename, gemma | -17.9 [-23.6, -13.2], 0/38, 0 | -33.8 [-45.5, -23.4], 0/26, 0 | flag | flag |
| exploratory value-only rename, haiku | -2.2 [-3.2, -1.4], 0/26, 0 | -21.6 [-27.0, -16.7], 4/73, 0 | flag | flag |
| exploratory opaque code, sonnet | -11.6 [-13.8, -9.5], 0/108, 0 | -23.4 [-28.8, -18.5], 0/59, 0 | flag | flag |
| exploratory opaque code, haiku | -0.9 [-1.7, -0.0], 7/20, 0.019 | -7.6 [-11.6, -3.6], 10/34, 0.0004 | flag | flag |

Not checked: held-out panel rows (full rename, neutral value, description edit, unrelated rename) and the held-out neutral value per model: the stored summaries keep no sign counts for them. The description edit and the unrelated rename have no flag, so the condition cannot change them.

### 4. Field order against the repeat, shared control (Haiku)

```
{
 "open": {
  "prefixes": 448,
  "field_order_changed": 13,
  "field_order_up": 7,
  "field_order_down": 6,
  "repeat_changed": 5,
  "repeat_up": 3,
  "repeat_down": 2,
  "changed_under_field_order_only": 10,
  "changed_under_repeat_only": 2,
  "changed_under_both": 3,
  "sign_p_only": 0.03857421875,
  "larger_change_field_order": 10,
  "larger_change_repeat": 2,
  "sign_p_larger": 0.03857421875
 },
 "specific": {
  "prefixes": 59,
  "field_order_changed": 9,
  "field_order_up": 4,
  "field_order_down": 5,
  "repeat_changed": 8,
  "repeat_up": 4,
  "repeat_down": 4,
  "changed_under_field_order_only": 2,
  "changed_under_repeat_only": 1,
  "changed_under_both": 7,
  "sign_p_only": 1.0,
  "larger_change_field_order": 6,
  "larger_change_repeat": 2,
  "sign_p_larger": 0.2890625
 }
}
```

### 5. Detection of the full rename against the open-set size (200 random subsets each)

| Model | Full open set: change [98.75%], up/down | n | First rule: flag | Revised 0.0125: flag | Revised 0.025: flag |
|---|---|---|---|---|---|
| sonnet | -19.2 [-23.7, -14.7], 0/86 (448) | 25 | 43.5% | 7.0% | 15.0% |
| sonnet | -19.2 [-23.7, -14.7], 0/86 (448) | 50 | 97.0% | 76.0% | 87.0% |
| sonnet | -19.2 [-23.7, -14.7], 0/86 (448) | 100 | 100.0% | 100.0% | 100.0% |
| sonnet | -19.2 [-23.7, -14.7], 0/86 (448) | 200 | 100.0% | 100.0% | 100.0% |
| haiku | -5.4 [-8.3, -2.9], 0/24 (446) | 25 | 0.0% | 0.0% | 0.0% |
| haiku | -5.4 [-8.3, -2.9], 0/24 (446) | 50 | 12.5% | 0.5% | 1.5% |
| haiku | -5.4 [-8.3, -2.9], 0/24 (446) | 100 | 54.5% | 17.5% | 29.0% |
| haiku | -5.4 [-8.3, -2.9], 0/24 (446) | 200 | 68.5% | 68.5% | 68.5% |
| opus | -20.8 [-25.7, -15.8], 2/95 (448) | 25 | 60.0% | 12.0% | 21.5% |
| opus | -20.8 [-25.7, -15.8], 2/95 (448) | 50 | 93.5% | 82.5% | 89.5% |
| opus | -20.8 [-25.7, -15.8], 2/95 (448) | 100 | 100.0% | 100.0% | 100.0% |
| opus | -20.8 [-25.7, -15.8], 2/95 (448) | 200 | 100.0% | 100.0% | 100.0% |
| sol | -23.0 [-27.9, -18.1], 0/103 (448) | 25 | 71.0% | 21.0% | 33.0% |
| sol | -23.0 [-27.9, -18.1], 0/103 (448) | 50 | 99.5% | 93.0% | 99.0% |
| sol | -23.0 [-27.9, -18.1], 0/103 (448) | 100 | 100.0% | 100.0% | 100.0% |
| sol | -23.0 [-27.9, -18.1], 0/103 (448) | 200 | 100.0% | 100.0% | 100.0% |
| astra | -31.0 [-36.4, -25.7], 0/139 (448) | 25 | 93.5% | 53.0% | 73.0% |
| astra | -31.0 [-36.4, -25.7], 0/139 (448) | 50 | 100.0% | 99.5% | 100.0% |
| astra | -31.0 [-36.4, -25.7], 0/139 (448) | 100 | 100.0% | 100.0% | 100.0% |
| astra | -31.0 [-36.4, -25.7], 0/139 (448) | 200 | 100.0% | 100.0% | 100.0% |
| luna | -17.6 [-22.1, -13.4], 0/79 (448) | 25 | 46.0% | 5.0% | 10.5% |
| luna | -17.6 [-22.1, -13.4], 0/79 (448) | 50 | 92.5% | 62.0% | 80.5% |
| luna | -17.6 [-22.1, -13.4], 0/79 (448) | 100 | 100.0% | 100.0% | 100.0% |
| luna | -17.6 [-22.1, -13.4], 0/79 (448) | 200 | 100.0% | 100.0% | 100.0% |
