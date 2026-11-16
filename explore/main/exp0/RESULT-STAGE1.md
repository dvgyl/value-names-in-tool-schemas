# Experiment 0, stage 1: the held-out test of H4 natural (interim look)

Status: held-out. The frozen analysis ran once on the stage-1 answers. Section 9 of RESULTS-R10.md copies this file without a change.

- Panel: sonnet, haiku, sol, luna, deepseek, qwen, gemma.
- Parts: nat, plc, hot, pre. The part tp is not read.
- Dialogues: natural 213 (43 with repeat reads), goal-hotel 77 (13 with repeat reads).
- Alpha 0.025 for this look, Holm over the 2 tests. Permutation test: 10,000 draws, seed 2026111201. Bootstrap: 2,000 draws, seed 20261112.
- Rows read per model: sonnet 3103, haiku 3103, sol 2804, luna 2804, deepseek 2804, qwen 2804, gemma 2804.

## Frozen files (SHA-256)

| File | SHA-256 |
|---|---|
| `main/exp0/analysis.py` | `c8841480ae3016d3ca71ab64daf265281f57b6dee800a9a4a73eaf2a8aa4d0d9` |
| `r10/briefsearch.py` | `2615e6ac412c49ee507c6b2a5d76441df1e2d404ec789a33b9b6963d9fe09dce` |
| `r10/analysis/stats.py` | `c90eb62a84f69fe2c6352ed4a9d5d9aad9d6265765088f30ba8fc47d36f03982` |

Other inputs:

| File | SHA-256 |
|---|---|
| `main/wave1.py` | `bca97b4406466458ea750e3e96c3c69758aa6269c1e351c1b54dd39a81566072` |
| `main/wave1_ids.json` | `54743585a28df8ae39200c10fd526e55d3e07b4f87005989524fcc21428ae8f0` |
| `main/wave1_manifest.json` | `274fe1219e1ae28b8bef13a51df1c45a8796d5b3cf9f456746bc407b32c699ce` |
| `r9/natural/natural.py` | `a28868ae705282b5e9dd259d36c23953fd890b3273e7ed8b42f27da5d628b8c3` |
| `forms/common.py` | `bae614a6f15b0497e8986e1eed42a0adb9dd97eeb9d3ab0f46765c2d8590524a` |
| `pmain/e13.py` | `1588ef48b26e3590c56edbbf615cb90d0eae0bf84ae624ba15f1aa1e24fbe3a5` |
| `r9/free/gold.py` | `a5f92368d2c394a7587b61abdc8ae401b847156e66eda591c0ab45ecb3e28081` |
| `r9/additions/zforms.py` | `d0f2b8849b2413d0a38a7de5dacfe63f178bc09ad35962ce1b246d07bcede643` |
| `lib/anth.py` | `b775266c6d476280247f7b4e6e598d82bf787a94f11730f02ca569aa57cee058` |
| `r9/additions/zruns.py` | `15ee608ea2ab480919033fea6a0695845bd21ace3f16a4cbd1a86003e71f439d` |
| `hotel_db.json` | `972bbd65beada7c64f0b87322c694fd9173b46cf8e61ca3bbe951717ac1d1662` |
| `data.json (MultiWOZ 2.4)` | `3555f1c34334353f950d1a627f197cabe74f6dc5725254f49e5427a8d9f7f1bd` |
| `unseal_manifest.json` | `6b9a8120bf8b6fc4f7485af6bb72fc2ea2f28d434dceb11d07c9377433a3a3ae` |
| `em1_sonnet/raw.jsonl` | `6bd43a3168e62d7d53fbeb38c6b066575b5b971cefa4796217f814da36e7c99f` |
| `em1_haiku/raw.jsonl` | `1e0a5978b52493a4eb5fc0b3a83a8d6c7c2b5a64e032e9acb03346d5f5d8bde4` |
| `em1_sol/raw.jsonl` | `a95fb226d1fa3f2f075835e008cd9b5fbe6e17aba31b03d8a7d024185d66c143` |
| `em1_luna/raw.jsonl` | `efc0671aba79ef76d4e77ab923448fe457e6ef3367969e8a4f7e23c5e9c92137` |
| `em1_deepseek/raw.jsonl` | `2ce74177cb36ed8f8a5ab1a178b7ce7f10795d35c8a139d7887c6995c53c3f2b` |
| `em1_qwen/raw.jsonl` | `b17f5f390363b9d306c1ab1af5c3b6da7bb8ae4eddd3e338b95466be7c491b0e` |
| `em1_gemma/raw.jsonl` | `15518cddff458473aaf6aecaa3b457ce6799df5a7591b3054c22f107ca55c230` |

## 1. The H4 natural family

Per dialogue: the paired difference `t_renamed` minus `t_legacy` of read 1, `type = hotel`, averaged over the panel models. Test of the mean: two-sided sign-flip permutation test. A negative value means fewer `type = hotel` reads under `t_renamed`. The prediction is negative for both tests.

| Test | Sample | Dialogues | Panel mean, points | 95% interval | p | Holm p | Rejects at 0.025 |
|---|---|---|---|---|---|---|---|
| wrong_values | natural | 213 | -13.0 | [-16.0, -10.1] | 0.0001 | 0.0002 | yes |
| correct_values_kept | goal_hotel | 77 | -29.1 | [-35.1, -23.9] | 0.0001 | 0.0002 | yes |

- Claim 1 transfers to natural dialogue (the wrong-value test rejects, `t_renamed` lower): yes.
- The anchoring reading (both tests reject, both lower): yes.

## 2. Missing cells and the worst case

A V0 failure, a cut reply, or any other request without a valid read is a missing cell. The primary test leaves it out. The worst case scores it in the direction that shrinks the paired difference.

Read-1 cells of the family: 4060. Missing: 55.

| Model, part, form | Missing read 1 | Missing, all reads | Reasons (read 1) |
|---|---|---|---|
| deepseek nat t_described | 1 | 1 | stop max_tokens 1 |
| deepseek nat t_renamed | 0 | 1 | - |
| gemma hot t_described | 1 | 1 | stop max_tokens 1 |
| gemma hot t_legacy | 0 | 1 | - |
| gemma nat f4 | 2 | 2 | stop max_tokens 2 |
| gemma nat t_described | 1 | 1 | stop max_tokens 1 |
| gemma nat t_legacy | 1 | 1 | stop max_tokens 1 |
| gemma pre f4 | 1 | 1 | stop max_tokens 1 |
| gemma pre t_described | 2 | 3 | stop max_tokens 2 |
| gemma pre t_legacy | 3 | 3 | stop max_tokens 3 |
| gemma pre t_renamed | 1 | 1 | stop max_tokens 1 |
| qwen hot f4 | 7 | 10 | stop max_tokens 7 |
| qwen hot t_described | 10 | 14 | stop max_tokens 10 |
| qwen hot t_legacy | 8 | 8 | stop max_tokens 8 |
| qwen hot t_renamed | 14 | 18 | stop max_tokens 14 |
| qwen nat f4 | 9 | 16 | stop max_tokens 9 |
| qwen nat t_described | 17 | 23 | stop max_tokens 17 |
| qwen nat t_legacy | 14 | 15 | stop max_tokens 14 |
| qwen nat t_renamed | 18 | 21 | stop max_tokens 18 |
| qwen pre f4 | 15 | 18 | stop max_tokens 15 |
| qwen pre t_described | 12 | 17 | stop max_tokens 12 |
| qwen pre t_legacy | 10 | 13 | stop max_tokens 10 |
| qwen pre t_renamed | 9 | 15 | stop max_tokens 9 |

Worst case:

| Test | Sample | Dialogues | Panel mean, points | 95% interval | p | Holm p | Rejects at 0.025 |
|---|---|---|---|---|---|---|---|
| wrong_values | natural | 213 | -11.5 | [-14.5, -8.7] | 0.0001 | 0.0002 | yes |
| correct_values_kept | goal_hotel | 77 | -26.3 | [-32.5, -20.8] | 0.0001 | 0.0002 | yes |

- wrong_values: missing t_renamed scores 1, missing t_legacy scores 0.
- correct_values_kept: missing t_renamed scores 1, missing t_legacy scores 0.
- The decisions are the same as in section 1: yes.

## 3. Each model's paired effect

Read 1. The sign test is a description, not a registered test.

**wrong_values**

| Model | Dialogues | Mean paired difference, points | 95% interval | Form higher | Form lower | Sign p (description) |
|---|---|---|---|---|---|---|
| sonnet | 213 | -11.7 | [-16.4, -8.0] | 0 | 25 | 6.0e-08 |
| haiku | 213 | -4.7 | [-7.5, -1.9] | 0 | 10 | 0.0020 |
| sol | 213 | -17.4 | [-23.0, -12.7] | 0 | 37 | 1.5e-11 |
| luna | 213 | -17.4 | [-23.0, -12.7] | 0 | 37 | 1.5e-11 |
| deepseek | 213 | -11.7 | [-16.4, -7.5] | 1 | 26 | 4.2e-07 |
| qwen | 187 | -7.5 | [-12.3, -3.2] | 2 | 16 | 0.0013 |
| gemma | 212 | -17.9 | [-23.6, -13.2] | 0 | 38 | 7.3e-12 |

**correct_values_kept**

| Model | Dialogues | Mean paired difference, points | 95% interval | Form higher | Form lower | Sign p (description) |
|---|---|---|---|---|---|---|
| sonnet | 77 | -19.5 | [-28.6, -10.4] | 0 | 15 | 0.0001 |
| haiku | 77 | -23.4 | [-32.5, -14.3] | 0 | 18 | 7.6e-06 |
| sol | 77 | -26.0 | [-36.4, -16.9] | 0 | 20 | 1.9e-06 |
| luna | 77 | -57.1 | [-67.5, -46.8] | 0 | 44 | 1.1e-13 |
| deepseek | 77 | -20.8 | [-31.2, -11.7] | 1 | 17 | 0.0001 |
| qwen | 60 | -23.3 | [-36.7, -10.0] | 4 | 18 | 0.0043 |
| gemma | 77 | -33.8 | [-45.5, -23.4] | 0 | 26 | 3.0e-08 |

### 3b. Repeat reads (sensitivity analysis)

Repeat dialogues in stage 1: natural 43, goal-hotel 13. Each cell value is the mean of its valid reads.

| Test | Sample | Dialogues | Panel mean, points | 95% interval | p | Holm p | Rejects at 0.025 |
|---|---|---|---|---|---|---|---|
| wrong_values | natural | 213 | -12.6 | [-15.6, -9.8] | 0.0001 | 0.0002 | yes |
| correct_values_kept | goal_hotel | 77 | -28.7 | [-34.6, -23.5] | 0.0001 | 0.0002 | yes |

**wrong_values**, repeat means

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 213 | -11.6 | [-16.3, -7.5] |
| haiku | 213 | -4.4 | [-7.2, -1.9] |
| sol | 213 | -16.7 | [-21.9, -12.2] |
| luna | 213 | -17.2 | [-22.5, -12.5] |
| deepseek | 213 | -11.7 | [-16.3, -7.5] |
| qwen | 192 | -6.6 | [-10.9, -2.8] |
| gemma | 212 | -17.9 | [-23.6, -13.2] |

**correct_values_kept**, repeat means

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 77 | -19.0 | [-28.6, -10.4] |
| haiku | 77 | -23.8 | [-33.8, -14.7] |
| sol | 77 | -25.5 | [-36.4, -16.0] |
| luna | 77 | -56.3 | [-67.1, -45.9] |
| deepseek | 77 | -19.9 | [-29.9, -10.4] |
| qwen | 63 | -23.0 | [-36.5, -9.5] |
| gemma | 77 | -33.8 | [-45.5, -23.4] |

## 4. Registered secondary outcomes

No test. Each value has its 95% interval.

### 4.1 `f4` against `t_legacy`

**f4_natural**: f4 (part nat) minus t_legacy (part nat), natural sample. Panel mean -16.1 points [-19.9, -12.7], 213 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 213 | -14.6 | [-19.7, -10.3] |
| haiku | 213 | -2.8 | [-5.2, -0.9] |
| sol | 213 | -27.7 | [-33.8, -22.1] |
| luna | 213 | -18.3 | [-23.9, -13.1] |
| deepseek | 213 | -15.5 | [-20.7, -10.8] |
| qwen | 191 | -8.4 | [-12.6, -4.7] |
| gemma | 210 | -21.4 | [-27.1, -16.2] |

**f4_goal_hotel**: f4 (part hot) minus t_legacy (part hot), goal_hotel sample. Panel mean -41.5 points [-47.9, -35.6], 77 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 77 | -46.8 | [-58.4, -36.4] |
| haiku | 77 | -23.4 | [-33.8, -14.3] |
| sol | 77 | -33.8 | [-45.5, -23.4] |
| luna | 77 | -58.4 | [-70.1, -48.1] |
| deepseek | 77 | -44.2 | [-55.8, -32.5] |
| qwen | 63 | -22.2 | [-34.9, -9.5] |
| gemma | 77 | -58.4 | [-68.8, -48.1] |

### 4.2 `t_described` against `t_legacy`

**t_described_natural**: t_described (part nat) minus t_legacy (part nat), natural sample. Panel mean +0.9 points [-0.3, +2.1], 213 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 213 | +1.9 | [-0.9, +4.7] |
| haiku | 213 | -0.9 | [-3.3, +1.4] |
| sol | 213 | -0.9 | [-3.8, +1.9] |
| luna | 213 | +2.8 | [+0.0, +6.1] |
| deepseek | 212 | +0.9 | [-3.3, +5.2] |
| qwen | 188 | +2.1 | [-2.1, +6.4] |
| gemma | 211 | +0.5 | [-1.9, +2.8] |

**t_described_goal_hotel**: t_described (part hot) minus t_legacy (part hot), goal_hotel sample. Panel mean +0.7 points [-2.7, +4.0], 77 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 77 | +2.6 | [-5.2, +10.4] |
| haiku | 77 | -5.2 | [-11.7, +1.3] |
| sol | 77 | +1.3 | [+0.0, +3.9] |
| luna | 77 | +0.0 | [-6.5, +6.5] |
| deepseek | 77 | +5.2 | [-5.2, +15.6] |
| qwen | 62 | +0.0 | [-12.9, +11.3] |
| gemma | 76 | +1.3 | [+0.0, +3.9] |

### 4.3 The placebo (Claude models)

Claude models of the panel: sonnet, haiku.

**placebo**: f5 (part plc) minus t_legacy (part nat), natural sample. Panel mean +0.2 points [-1.6, +2.1], 213 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 213 | +0.9 | [-1.9, +3.8] |
| haiku | 213 | -0.5 | [-3.3, +1.9] |

**placebo_net**: t_renamed (part nat) minus f5 (part plc), natural sample. Panel mean -8.5 points [-11.5, -5.6], 213 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 213 | -12.7 | [-17.4, -8.5] |
| haiku | 213 | -4.2 | [-7.0, -1.4] |

### 4.4 The prefix

Share of read 1 with `type = hotel` on the prefix, per form.

| Model | Cell | Hits/reads | Share | 95% interval |
|---|---|---|---|---|
| sonnet | t_legacy | 49/213 | 23.0% | [17.8%, 28.6%] |
| sonnet | t_renamed | 4/213 | 1.9% | [0.5%, 3.8%] |
| sonnet | t_described | 54/213 | 25.4% | [19.7%, 31.5%] |
| sonnet | f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| haiku | t_legacy | 17/213 | 8.0% | [4.7%, 11.7%] |
| haiku | t_renamed | 1/213 | 0.5% | [0.0%, 1.4%] |
| haiku | t_described | 17/213 | 8.0% | [4.7%, 12.2%] |
| haiku | f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| sol | t_legacy | 74/213 | 34.7% | [28.6%, 41.8%] |
| sol | t_renamed | 31/213 | 14.6% | [9.9%, 19.7%] |
| sol | t_described | 73/213 | 34.3% | [28.2%, 40.8%] |
| sol | f4 | 10/213 | 4.7% | [2.3%, 8.0%] |
| luna | t_legacy | 46/213 | 21.6% | [16.4%, 27.7%] |
| luna | t_renamed | 0/213 | 0.0% | [0.0%, 0.0%] |
| luna | t_described | 50/213 | 23.5% | [17.8%, 29.1%] |
| luna | f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| deepseek | t_legacy | 38/213 | 17.8% | [13.1%, 23.0%] |
| deepseek | t_renamed | 5/213 | 2.3% | [0.5%, 4.7%] |
| deepseek | t_described | 39/213 | 18.3% | [13.1%, 23.9%] |
| deepseek | f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| qwen | t_legacy | 28/203 | 13.8% | [9.4%, 18.7%] |
| qwen | t_renamed | 2/204 | 1.0% | [0.0%, 2.5%] |
| qwen | t_described | 30/201 | 14.9% | [10.0%, 19.9%] |
| qwen | f4 | 1/198 | 0.5% | [0.0%, 1.5%] |
| gemma | t_legacy | 50/210 | 23.8% | [18.1%, 29.5%] |
| gemma | t_renamed | 4/212 | 1.9% | [0.5%, 3.8%] |
| gemma | t_described | 50/211 | 23.7% | [18.0%, 29.4%] |
| gemma | f4 | 0/212 | 0.0% | [0.0%, 0.0%] |

Share of read 1 whose `type` excludes the type of the booked venue, on the 128 dialogues with a matched booking.

| Model | Cell | Hits/reads | Share | 95% interval |
|---|---|---|---|---|
| sonnet | t_legacy | 17/128 | 13.3% | [7.8%, 19.5%] |
| sonnet | t_renamed | 1/128 | 0.8% | [0.0%, 2.3%] |
| sonnet | t_described | 20/128 | 15.6% | [9.4%, 21.9%] |
| sonnet | f4 | 0/128 | 0.0% | [0.0%, 0.0%] |
| haiku | t_legacy | 6/128 | 4.7% | [1.6%, 8.6%] |
| haiku | t_renamed | 1/128 | 0.8% | [0.0%, 2.3%] |
| haiku | t_described | 5/128 | 3.9% | [0.8%, 7.0%] |
| haiku | f4 | 0/128 | 0.0% | [0.0%, 0.0%] |
| sol | t_legacy | 25/128 | 19.5% | [13.3%, 26.6%] |
| sol | t_renamed | 12/128 | 9.4% | [4.7%, 14.8%] |
| sol | t_described | 26/128 | 20.3% | [13.3%, 27.3%] |
| sol | f4 | 2/128 | 1.6% | [0.0%, 3.9%] |
| luna | t_legacy | 16/128 | 12.5% | [7.0%, 18.8%] |
| luna | t_renamed | 0/128 | 0.0% | [0.0%, 0.0%] |
| luna | t_described | 17/128 | 13.3% | [7.8%, 19.5%] |
| luna | f4 | 0/128 | 0.0% | [0.0%, 0.0%] |
| deepseek | t_legacy | 14/128 | 10.9% | [5.5%, 16.4%] |
| deepseek | t_renamed | 3/128 | 2.3% | [0.0%, 5.5%] |
| deepseek | t_described | 13/128 | 10.2% | [5.5%, 15.6%] |
| deepseek | f4 | 1/128 | 0.8% | [0.0%, 2.3%] |
| qwen | t_legacy | 7/123 | 5.7% | [2.4%, 10.6%] |
| qwen | t_renamed | 1/121 | 0.8% | [0.0%, 2.5%] |
| qwen | t_described | 11/123 | 8.9% | [4.1%, 14.6%] |
| qwen | f4 | 0/119 | 0.0% | [0.0%, 0.0%] |
| gemma | t_legacy | 17/127 | 13.4% | [7.9%, 19.7%] |
| gemma | t_renamed | 2/127 | 1.6% | [0.0%, 3.9%] |
| gemma | t_described | 19/126 | 15.1% | [8.7%, 21.4%] |
| gemma | f4 | 0/127 | 0.0% | [0.0%, 0.0%] |

### 4.5 The trade ratio (point values)

Correct values lost per wrong value removed, against `t_legacy`. Weights: natural 281, goal-hotel 97.

**t_renamed**

| Model | Paired dialogues (nat, hot) | Wrong values removed | Correct values lost | Ratio |
|---|---|---|---|---|
| sonnet | 213, 77 | 33.0 | 18.9 | 0.57 |
| haiku | 213, 77 | 13.2 | 22.7 | 1.72 |
| sol | 213, 77 | 48.8 | 25.2 | 0.52 |
| luna | 213, 77 | 48.8 | 55.4 | 1.14 |
| deepseek | 213, 77 | 33.0 | 20.2 | 0.61 |
| qwen | 187, 60 | 21.0 | 22.6 | 1.08 |
| gemma | 212, 77 | 50.4 | 32.8 | 0.65 |
| panel | 213, 77 | 35.7 | 28.4 | 0.80 |

**f4**

| Model | Paired dialogues (nat, hot) | Wrong values removed | Correct values lost | Ratio |
|---|---|---|---|---|
| sonnet | 213, 77 | 40.9 | 45.4 | 1.11 |
| haiku | 213, 77 | 7.9 | 22.7 | 2.86 |
| sol | 213, 77 | 77.8 | 32.8 | 0.42 |
| luna | 213, 77 | 51.5 | 56.7 | 1.10 |
| deepseek | 213, 77 | 43.5 | 42.8 | 0.98 |
| qwen | 191, 63 | 23.5 | 21.6 | 0.92 |
| gemma | 210, 77 | 60.2 | 56.7 | 0.94 |
| panel | 213, 77 | 43.9 | 40.3 | 0.92 |

### 4.6 Any `type` commitment

Share of read 1 whose `type` is a list. Cell: part and form.

| Model | Cell | Hits/reads | Share | 95% interval |
|---|---|---|---|---|
| sonnet | nat t_legacy | 37/213 | 17.4% | [12.7%, 22.5%] |
| sonnet | nat t_renamed | 17/213 | 8.0% | [4.7%, 11.7%] |
| sonnet | nat t_described | 43/213 | 20.2% | [15.0%, 25.8%] |
| sonnet | nat f4 | 10/213 | 4.7% | [1.9%, 7.5%] |
| sonnet | hot t_legacy | 53/77 | 68.8% | [58.4%, 79.2%] |
| sonnet | hot t_renamed | 38/77 | 49.4% | [37.7%, 61.0%] |
| sonnet | hot t_described | 55/77 | 71.4% | [61.0%, 80.5%] |
| sonnet | hot f4 | 19/77 | 24.7% | [15.6%, 33.8%] |
| sonnet | pre t_legacy | 51/213 | 23.9% | [18.3%, 29.6%] |
| sonnet | pre t_renamed | 4/213 | 1.9% | [0.5%, 3.8%] |
| sonnet | pre t_described | 57/213 | 26.8% | [20.7%, 32.9%] |
| sonnet | pre f4 | 2/213 | 0.9% | [0.0%, 2.3%] |
| sonnet | plc f5 | 40/213 | 18.8% | [13.6%, 24.4%] |
| haiku | nat t_legacy | 39/213 | 18.3% | [13.1%, 23.5%] |
| haiku | nat t_renamed | 30/213 | 14.1% | [9.4%, 18.8%] |
| haiku | nat t_described | 38/213 | 17.8% | [12.7%, 23.0%] |
| haiku | nat f4 | 31/213 | 14.6% | [9.9%, 19.2%] |
| haiku | hot t_legacy | 43/77 | 55.8% | [44.2%, 66.2%] |
| haiku | hot t_renamed | 27/77 | 35.1% | [24.7%, 45.5%] |
| haiku | hot t_described | 39/77 | 50.6% | [39.0%, 62.3%] |
| haiku | hot f4 | 28/77 | 36.4% | [24.7%, 46.8%] |
| haiku | pre t_legacy | 19/213 | 8.9% | [5.2%, 13.1%] |
| haiku | pre t_renamed | 4/213 | 1.9% | [0.5%, 3.8%] |
| haiku | pre t_described | 20/213 | 9.4% | [5.6%, 13.6%] |
| haiku | pre f4 | 3/213 | 1.4% | [0.0%, 3.3%] |
| haiku | plc f5 | 35/213 | 16.4% | [11.3%, 21.1%] |
| sol | nat t_legacy | 72/213 | 33.8% | [27.7%, 40.4%] |
| sol | nat t_renamed | 36/213 | 16.9% | [11.7%, 22.1%] |
| sol | nat t_described | 72/213 | 33.8% | [27.7%, 40.4%] |
| sol | nat f4 | 15/213 | 7.0% | [3.8%, 10.8%] |
| sol | hot t_legacy | 68/77 | 88.3% | [80.5%, 94.8%] |
| sol | hot t_renamed | 48/77 | 62.3% | [51.9%, 72.7%] |
| sol | hot t_described | 69/77 | 89.6% | [81.8%, 96.1%] |
| sol | hot f4 | 42/77 | 54.5% | [42.9%, 66.2%] |
| sol | pre t_legacy | 75/213 | 35.2% | [29.1%, 41.8%] |
| sol | pre t_renamed | 32/213 | 15.0% | [10.3%, 20.2%] |
| sol | pre t_described | 74/213 | 34.7% | [28.6%, 41.3%] |
| sol | pre f4 | 11/213 | 5.2% | [2.3%, 8.5%] |
| luna | nat t_legacy | 57/213 | 26.8% | [20.7%, 32.9%] |
| luna | nat t_renamed | 25/213 | 11.7% | [7.5%, 16.4%] |
| luna | nat t_described | 62/213 | 29.1% | [23.0%, 35.2%] |
| luna | nat f4 | 25/213 | 11.7% | [7.5%, 16.0%] |
| luna | hot t_legacy | 56/77 | 72.7% | [63.6%, 81.8%] |
| luna | hot t_renamed | 18/77 | 23.4% | [14.3%, 32.5%] |
| luna | hot t_described | 58/77 | 75.3% | [66.2%, 84.4%] |
| luna | hot f4 | 18/77 | 23.4% | [14.3%, 32.5%] |
| luna | pre t_legacy | 47/213 | 22.1% | [16.9%, 28.2%] |
| luna | pre t_renamed | 1/213 | 0.5% | [0.0%, 1.4%] |
| luna | pre t_described | 51/213 | 23.9% | [18.3%, 29.6%] |
| luna | pre f4 | 2/213 | 0.9% | [0.0%, 2.3%] |
| deepseek | nat t_legacy | 50/213 | 23.5% | [17.8%, 29.1%] |
| deepseek | nat t_renamed | 22/213 | 10.3% | [6.6%, 14.1%] |
| deepseek | nat t_described | 47/212 | 22.2% | [16.5%, 27.8%] |
| deepseek | nat f4 | 20/213 | 9.4% | [5.6%, 13.6%] |
| deepseek | hot t_legacy | 42/77 | 54.5% | [42.9%, 64.9%] |
| deepseek | hot t_renamed | 28/77 | 36.4% | [26.0%, 46.8%] |
| deepseek | hot t_described | 45/77 | 58.4% | [48.1%, 68.8%] |
| deepseek | hot f4 | 17/77 | 22.1% | [13.0%, 31.2%] |
| deepseek | pre t_legacy | 41/213 | 19.2% | [14.1%, 24.4%] |
| deepseek | pre t_renamed | 6/213 | 2.8% | [0.9%, 5.2%] |
| deepseek | pre t_described | 42/213 | 19.7% | [14.6%, 25.4%] |
| deepseek | pre f4 | 3/213 | 1.4% | [0.0%, 2.8%] |
| qwen | nat t_legacy | 30/199 | 15.1% | [10.6%, 20.1%] |
| qwen | nat t_renamed | 16/195 | 8.2% | [4.6%, 11.8%] |
| qwen | nat t_described | 31/196 | 15.8% | [10.7%, 20.9%] |
| qwen | nat f4 | 16/204 | 7.8% | [4.4%, 11.8%] |
| qwen | hot t_legacy | 39/69 | 56.5% | [44.9%, 68.1%] |
| qwen | hot t_renamed | 23/63 | 36.5% | [23.8%, 47.6%] |
| qwen | hot t_described | 36/67 | 53.7% | [41.8%, 65.7%] |
| qwen | hot f4 | 25/70 | 35.7% | [24.3%, 47.1%] |
| qwen | pre t_legacy | 29/203 | 14.3% | [9.9%, 19.7%] |
| qwen | pre t_renamed | 3/204 | 1.5% | [0.0%, 3.4%] |
| qwen | pre t_described | 32/201 | 15.9% | [10.9%, 20.9%] |
| qwen | pre f4 | 2/198 | 1.0% | [0.0%, 2.5%] |
| gemma | nat t_legacy | 46/212 | 21.7% | [16.5%, 27.4%] |
| gemma | nat t_renamed | 15/213 | 7.0% | [3.8%, 10.3%] |
| gemma | nat t_described | 49/212 | 23.1% | [17.9%, 29.2%] |
| gemma | nat f4 | 10/211 | 4.7% | [1.9%, 7.6%] |
| gemma | hot t_legacy | 57/77 | 74.0% | [64.9%, 83.1%] |
| gemma | hot t_renamed | 34/77 | 44.2% | [32.5%, 54.5%] |
| gemma | hot t_described | 57/76 | 75.0% | [64.5%, 84.2%] |
| gemma | hot f4 | 16/77 | 20.8% | [11.7%, 29.9%] |
| gemma | pre t_legacy | 50/210 | 23.8% | [18.1%, 29.5%] |
| gemma | pre t_renamed | 5/212 | 2.4% | [0.5%, 4.7%] |
| gemma | pre t_described | 50/211 | 23.7% | [18.0%, 29.4%] |
| gemma | pre f4 | 1/212 | 0.5% | [0.0%, 1.4%] |

## 5. New outcomes of amendment A1

### (a) Contrasts on the dialogues whose goal names no venue

Dialogues: natural 100, goal-hotel 77.

**wrong_values**: t_renamed (part nat) minus t_legacy (part nat), natural sample. Panel mean -26.4 points [-31.7, -21.4], 100 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 100 | -24.0 | [-33.0, -16.0] |
| haiku | 100 | -10.0 | [-16.0, -5.0] |
| sol | 100 | -33.0 | [-43.0, -24.0] |
| luna | 100 | -35.0 | [-45.0, -25.0] |
| deepseek | 100 | -25.0 | [-34.0, -16.0] |
| qwen | 74 | -17.6 | [-28.4, -8.1] |
| gemma | 99 | -38.4 | [-47.5, -29.3] |

**correct_values_kept**: t_renamed (part hot) minus t_legacy (part hot), goal_hotel sample. Panel mean -29.1 points [-35.1, -23.9], 77 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 77 | -19.5 | [-28.6, -10.4] |
| haiku | 77 | -23.4 | [-32.5, -14.3] |
| sol | 77 | -26.0 | [-36.4, -16.9] |
| luna | 77 | -57.1 | [-67.5, -46.8] |
| deepseek | 77 | -20.8 | [-31.2, -11.7] |
| qwen | 60 | -23.3 | [-36.7, -10.0] |
| gemma | 77 | -33.8 | [-45.5, -23.4] |

**f4_natural**: f4 (part nat) minus t_legacy (part nat), natural sample. Panel mean -33.2 points [-39.4, -27.3], 100 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 100 | -30.0 | [-39.0, -21.0] |
| haiku | 100 | -6.0 | [-10.0, -2.0] |
| sol | 100 | -55.0 | [-65.0, -45.0] |
| luna | 100 | -37.0 | [-47.0, -27.0] |
| deepseek | 100 | -33.0 | [-43.0, -24.0] |
| qwen | 78 | -19.2 | [-29.5, -10.3] |
| gemma | 97 | -46.4 | [-56.7, -37.1] |

**f4_goal_hotel**: f4 (part hot) minus t_legacy (part hot), goal_hotel sample. Panel mean -41.5 points [-47.9, -35.6], 77 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 77 | -46.8 | [-58.4, -36.4] |
| haiku | 77 | -23.4 | [-33.8, -14.3] |
| sol | 77 | -33.8 | [-45.5, -23.4] |
| luna | 77 | -58.4 | [-70.1, -48.1] |
| deepseek | 77 | -44.2 | [-55.8, -32.5] |
| qwen | 63 | -22.2 | [-34.9, -9.5] |
| gemma | 77 | -58.4 | [-68.8, -48.1] |

**t_described_natural**: t_described (part nat) minus t_legacy (part nat), natural sample. Panel mean +1.6 points [-0.7, +3.9], 100 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 100 | +4.0 | [-2.0, +10.0] |
| haiku | 100 | -2.0 | [-7.0, +3.0] |
| sol | 100 | -3.0 | [-8.0, +1.0] |
| luna | 100 | +4.0 | [-1.0, +9.0] |
| deepseek | 99 | +2.0 | [-7.1, +11.1] |
| qwen | 75 | +6.7 | [-2.7, +16.0] |
| gemma | 98 | +1.0 | [-4.1, +6.1] |

**t_described_goal_hotel**: t_described (part hot) minus t_legacy (part hot), goal_hotel sample. Panel mean +0.7 points [-2.7, +4.0], 77 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 77 | +2.6 | [-5.2, +10.4] |
| haiku | 77 | -5.2 | [-11.7, +1.3] |
| sol | 77 | +1.3 | [+0.0, +3.9] |
| luna | 77 | +0.0 | [-6.5, +6.5] |
| deepseek | 77 | +5.2 | [-5.2, +15.6] |
| qwen | 62 | +0.0 | [-12.9, +11.3] |
| gemma | 76 | +1.3 | [+0.0, +3.9] |

**placebo**: f5 (part plc) minus t_legacy (part nat), natural sample. Panel mean +0.5 points [-3.5, +4.5], 100 dialogues.

| Model | Dialogues | Mean paired difference, points | 95% interval |
|---|---|---|---|
| sonnet | 100 | +2.0 | [-4.0, +8.0] |
| haiku | 100 | -1.0 | [-6.0, +4.0] |

### (b) Search failure per model and form

Read 1 whose `type` keeps hotel and not guesthouse, on a dialogue where no hotel fits the brief, as a share of all valid read 1 on the 213 dialogues whose brief sets no type. No hotel fits the brief on 128 dialogues; another venue fits on 128 of them.

| Model | Cell | Hits/reads | Share | 95% interval |
|---|---|---|---|---|
| sonnet | nat t_legacy | 11/213 | 5.2% | [2.3%, 8.5%] |
| sonnet | nat t_renamed | 0/213 | 0.0% | [0.0%, 0.0%] |
| sonnet | nat t_described | 11/213 | 5.2% | [2.3%, 8.5%] |
| sonnet | nat f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| sonnet | plc f5 | 12/213 | 5.6% | [2.8%, 8.9%] |
| sonnet | pre t_legacy | 26/213 | 12.2% | [8.0%, 16.4%] |
| sonnet | pre t_renamed | 3/213 | 1.4% | [0.0%, 3.3%] |
| sonnet | pre t_described | 29/213 | 13.6% | [9.4%, 18.3%] |
| sonnet | pre f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| haiku | nat t_legacy | 3/213 | 1.4% | [0.0%, 3.3%] |
| haiku | nat t_renamed | 0/213 | 0.0% | [0.0%, 0.0%] |
| haiku | nat t_described | 3/213 | 1.4% | [0.0%, 3.3%] |
| haiku | nat f4 | 1/213 | 0.5% | [0.0%, 1.4%] |
| haiku | plc f5 | 3/213 | 1.4% | [0.0%, 3.3%] |
| haiku | pre t_legacy | 12/213 | 5.6% | [2.8%, 8.9%] |
| haiku | pre t_renamed | 1/213 | 0.5% | [0.0%, 1.4%] |
| haiku | pre t_described | 10/213 | 4.7% | [2.3%, 7.5%] |
| haiku | pre f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| sol | nat t_legacy | 31/213 | 14.6% | [9.9%, 19.2%] |
| sol | nat t_renamed | 14/213 | 6.6% | [3.3%, 10.3%] |
| sol | nat t_described | 30/213 | 14.1% | [9.4%, 18.8%] |
| sol | nat f4 | 3/213 | 1.4% | [0.0%, 3.3%] |
| sol | pre t_legacy | 40/213 | 18.8% | [13.6%, 24.4%] |
| sol | pre t_renamed | 17/213 | 8.0% | [4.7%, 11.7%] |
| sol | pre t_described | 41/213 | 19.2% | [14.1%, 24.4%] |
| sol | pre f4 | 4/213 | 1.9% | [0.5%, 3.8%] |
| luna | nat t_legacy | 11/213 | 5.2% | [2.3%, 8.5%] |
| luna | nat t_renamed | 0/213 | 0.0% | [0.0%, 0.0%] |
| luna | nat t_described | 13/213 | 6.1% | [2.8%, 9.9%] |
| luna | nat f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| luna | pre t_legacy | 26/213 | 12.2% | [8.0%, 16.9%] |
| luna | pre t_renamed | 0/213 | 0.0% | [0.0%, 0.0%] |
| luna | pre t_described | 27/213 | 12.7% | [8.5%, 17.4%] |
| luna | pre f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| deepseek | nat t_legacy | 10/213 | 4.7% | [1.9%, 7.5%] |
| deepseek | nat t_renamed | 1/213 | 0.5% | [0.0%, 1.4%] |
| deepseek | nat t_described | 11/212 | 5.2% | [2.4%, 8.5%] |
| deepseek | nat f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| deepseek | pre t_legacy | 23/213 | 10.8% | [7.0%, 15.0%] |
| deepseek | pre t_renamed | 4/213 | 1.9% | [0.5%, 3.8%] |
| deepseek | pre t_described | 23/213 | 10.8% | [7.0%, 15.0%] |
| deepseek | pre f4 | 0/213 | 0.0% | [0.0%, 0.0%] |
| qwen | nat t_legacy | 7/199 | 3.5% | [1.0%, 6.0%] |
| qwen | nat t_renamed | 0/195 | 0.0% | [0.0%, 0.0%] |
| qwen | nat t_described | 8/196 | 4.1% | [1.5%, 7.1%] |
| qwen | nat f4 | 0/204 | 0.0% | [0.0%, 0.0%] |
| qwen | pre t_legacy | 15/203 | 7.4% | [3.9%, 10.8%] |
| qwen | pre t_renamed | 1/204 | 0.5% | [0.0%, 1.5%] |
| qwen | pre t_described | 19/201 | 9.5% | [5.5%, 13.9%] |
| qwen | pre f4 | 0/198 | 0.0% | [0.0%, 0.0%] |
| gemma | nat t_legacy | 16/212 | 7.5% | [4.2%, 11.3%] |
| gemma | nat t_renamed | 2/213 | 0.9% | [0.0%, 2.3%] |
| gemma | nat t_described | 16/212 | 7.5% | [4.2%, 11.3%] |
| gemma | nat f4 | 0/211 | 0.0% | [0.0%, 0.0%] |
| gemma | pre t_legacy | 28/210 | 13.3% | [9.0%, 17.6%] |
| gemma | pre t_renamed | 3/212 | 1.4% | [0.0%, 3.3%] |
| gemma | pre t_described | 29/211 | 13.7% | [9.5%, 18.5%] |
| gemma | pre f4 | 0/212 | 0.0% | [0.0%, 0.0%] |

### (c) The trade ratio with its 95% interval

**t_renamed**

| Model | Paired dialogues (nat, hot) | Wrong values removed | Correct values lost | Ratio | 95% interval |
|---|---|---|---|---|---|
| sonnet | 213, 77 | 33.0 | 18.9 | 0.57 | [0.30, 1.03] |
| haiku | 213, 77 | 13.2 | 22.7 | 1.72 | [0.88, 4.06] |
| sol | 213, 77 | 48.8 | 25.2 | 0.52 | [0.32, 0.82] |
| luna | 213, 77 | 48.8 | 55.4 | 1.14 | [0.81, 1.67] |
| deepseek | 213, 77 | 33.0 | 20.2 | 0.61 | [0.31, 1.10] |
| qwen | 187, 60 | 21.0 | 22.6 | 1.08 | [0.39, 2.63] |
| gemma | 212, 77 | 50.4 | 32.8 | 0.65 | [0.42, 0.98] |
| panel | 213, 77 | 35.7 | 28.4 | 0.80 | [0.58, 1.08] |

**f4**

| Model | Paired dialogues (nat, hot) | Wrong values removed | Correct values lost | Ratio | 95% interval |
|---|---|---|---|---|---|
| sonnet | 213, 77 | 40.9 | 45.4 | 1.11 | [0.75, 1.67] |
| haiku | 213, 77 | 7.9 | 22.7 | 2.86 | [1.31, 10.03] |
| sol | 213, 77 | 77.8 | 32.8 | 0.42 | [0.28, 0.61] |
| luna | 213, 77 | 51.5 | 56.7 | 1.10 | [0.78, 1.59] |
| deepseek | 213, 77 | 43.5 | 42.8 | 0.98 | [0.66, 1.45] |
| qwen | 191, 63 | 23.5 | 21.6 | 0.92 | [0.38, 1.90] |
| gemma | 210, 77 | 60.2 | 56.7 | 0.94 | [0.68, 1.29] |
| panel | 213, 77 | 43.9 | 40.3 | 0.92 | [0.71, 1.21] |

### (d) The mixed model

outcome (d) removed: no package.

## Choices (CHOICES)

Where the registration was not specific enough to code a step, the script uses the plainest reading:

- **family**: The two tests are registration A section 7 items 1 and 2: t_renamed minus t_legacy on the natural sample (part nat), and on the goal-hotel sample (part hot), stage-1 dialogues only.
- **outcome**: A read scores 1 when its parsed `type` list holds `hotel` after the form's mapping back (wave1.FORMS parser of r9/natural/natural.py; the E8 measure of natural_analyze.hotel), else 0.
- **valid read**: A read is valid when its row succeeded, stopped at end_turn, its last JSON object parses and fits the closed schema of its form. Reason: section 7 makes a V0 failure or a cut reply a missing cell, and PLAN.md defines V0 as schema validity.
- **primary missing**: A model enters the panel mean of a dialogue only when both of its cells are valid. A dialogue with no valid pair leaves the test. Reason: section 7 gives no imputation for the primary test; the worst case is its sensitivity analysis.
- **panel mean**: Each model with a valid pair has equal weight in a dialogue, and each dialogue has equal weight in the mean. Reason: section 7, average over the panel models per dialogue.
- **worst-case direction**: A missing cell is scored against the sign of the primary panel mean of its test (the predicted sign, negative, when the mean is 0). For a negative mean, a missing t_renamed cell scores 1 and a missing t_legacy cell scores 0. Reason: section 7, the direction that shrinks the paired difference.
- **decision**: A test rejects when its Holm-adjusted p is 0.025 or less. Reason: A1 alpha 0.025 for this look.
- **repeat means**: The repeat sensitivity analysis replaces read 1 by the mean of the valid reads of each cell (3 reads on the repeat dialogues, 1 elsewhere), with the same test and seed. Reason: section 7.
- **read 1 elsewhere**: Every secondary and A1 outcome uses read 1 only. Reason: read 1 is the primary read.
- **secondary statistics**: A secondary contrast gives each model's mean paired difference and the panel mean, each with a 95% interval, and no p value. Reason: section 7, 'no test'.
- **sign counts**: Part 3 also shows the exact sign test of each model as a description, not as a registered test. Reason: ACTION-PLAN section 3.4 gives each per-model contrast the sign test.
- **intervals**: Every interval is the 95% percentile interval of stats.cluster_bootstrap, 2,000 draws, BOOTSTRAP_SEED. The cluster is the dialogue.
- **placebo net**: The placebo effect is f5 (part plc) minus t_legacy (part nat). The net wrong-value effect is t_renamed minus f5 on the dialogues where both cells are valid, per Claude model and for the mean of the Claude models of the panel. Reason: decision D4, effect minus placebo effect.
- **prefix exclusion**: The booked venue is zruns.booked_venue (the last booked name, matched to hotel_db.json). A read excludes it when its `type` is a list without the venue's type (zanalyze excludes_type). Dialogues without a matched booking leave this share.
- **trade sizes**: The trade weights are the registered sample sizes, natural 281 (wrong values) and goal-hotel 97 (correct values). Reason: the interim and the final look then estimate the same ratio.
- **trade estimator**: The trade is stats.trade_interval on read 1 of the dialogues with both cells valid. Wrong group nat, correct group hot. The panel row adds the read-1 values of all panel models per dialogue. Part 4 gives the point values, part 5(c) the interval.
- **no venue**: A goal names no venue when goal.hotel.info has no `name` (briefsearch.brief_of). On the natural sample this is briefsearch.brief_subsets 'no_name'. On the goal-hotel sample the no-type condition of brief_subsets cannot hold, so only the name rule applies.
- **search failure**: Search failure is briefsearch.search_failure of read 1. The denominator is every valid read 1 on the dialogues whose brief sets no type (all stage-1 natural dialogues). Parts nat, plc and pre. Reason: ROUND10-EXPERIMENT-PLAN.md and harm_by_model.py use that denominator.
- **search failure fit**: briefsearch.search_failure also requires that some venue fits the brief. On the 213 dialogues this changes nothing: each of the 128 with no fitting hotel has a fitting venue.
- **commitment**: Any type commitment is a parsed `type` that is a list (not null, 'any' or 'unclear'). An empty list parses to None, so it is not a commitment.
- **claims**: claim1_transfers and anchoring_reading also require the direction 't_renamed lower'. Reason: registration A section 3, both contrasts reject in the same direction, the predicted one.
- **mixed model**: Outcome (d) is removed: MIXED_MODEL is False, because no machine of the project has statsmodels at the freeze (amendment A1). The script has no mixed-model code.
- **panel check**: The panel must be PANEL, the interim panel of A1. The panel of the manifest must equal it, and each raw.jsonl must match the SHA-256 and row count of the manifest. A directory of the input that is not a panel folder stops the script; `._*` files are ignored.
- **forms**: The form hashes of wave1.FORMS (prompt and schema) must equal forms_sha256 of main/wave1_manifest.json, so the scoring schemas are the registered ones.
