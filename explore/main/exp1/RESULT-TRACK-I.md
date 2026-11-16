# Registration B, Track I: the H4 synthetic family

Status: confirmatory. The frozen analysis ran one time on the unsealed Track I answers.

- Panel: sonnet, haiku, sol, luna, deepseek, qwen, gemma.
- Base objects: 100 (25 per collision word). Requests per model: 1200. One read per request.
- Alpha 0.05, Holm over the 5 contrasts. Permutation test: 10,000 draws, seed 2026111301. Bootstrap: 2,000 draws, seed 20261113.
- Rows read per model: sonnet 1200, haiku 1200, sol 1200, luna 1200, deepseek 1200, qwen 1200, gemma 1200.

## Frozen files (SHA-256)

| File | SHA-256 |
|---|---|
| `main/exp1/analysis_b.py` | `e89c7d6a5d2f4b10b034b92b2cf9cb7cd0dc9e2a672dc88c42476925897de34f` |
| `r10/analysis/stats.py` | `c90eb62a84f69fe2c6352ed4a9d5d9aad9d6265765088f30ba8fc47d36f03982` |

Other inputs:

| File | SHA-256 |
|---|---|
| `main/track_i/SHA256SUMS` | `3de2525ee359618a4256af38bc3bbc350f494abff4d0f8cd24dd6504b0eb236f` |
| `main/track_i/gold.jsonl` | `00e11a9c2256c605e22421a6616852c9ca9117105816141e9aa46dc2d9e3baa6` |
| `main/track_i/objects.json` | `65c0274e25b59dc4561187e51e7488ab7f7451e4ad9abdbb96239647996c092d` |
| `main/track_i/prompts.jsonl` | `791c5eaa6b9ca9096085999b43c20e9dedd204baa6f998a70ca30cee6670c50a` |
| `main/track_i/schema_snapshot.json` | `d3810d0c3a291a5fa5cb8888b7008bebbe2b51ba380ff7fdcfdae946502c1215` |
| `main/wave2_track_i_manifest.json` | `7612d07cb172cdaddcd6a7400516e7c12926e9370220d01bfc7e8411f97b5e63` |
| `unseal_manifest.json` | `8722af479267ae068c3e89d6fc0acaa2a9a357fe19c6d5cbfc5963280c7676be` |
| `em2i_sonnet/raw.jsonl` | `bd1dfeb2786c4b317861791859efcb24bf3015971e95f1b6b732196444c28065` |
| `em2i_haiku/raw.jsonl` | `75b58a4bc9dad2d5824f99b7cec814d8280a6dda58f41c196fbea64771c080a3` |
| `em2i_sol/raw.jsonl` | `1eff25cf5ce708b05196a695de366aeeb83d48e7690bcc2b936fb0178cb539db` |
| `em2i_luna/raw.jsonl` | `bb3444644661804028fedb149616abe401f842b6c080e357a7a96db610ba1a16` |
| `em2i_deepseek/raw.jsonl` | `b4c21be7a21aced49c53153aa33c0785d58145f19e6301b7642328c526898726` |
| `em2i_qwen/raw.jsonl` | `efa2a087e52889da09fa51a18e1b64f19c500dd8bc766f858b4cdb9f84ef282f` |
| `em2i_gemma/raw.jsonl` | `ee5ef03a535308b7967d4a5d6ca08da0c48eb0acb6f3603dbf6e74fcf948369b` |

## 1. The H4 synthetic family

Outcome: the silent error of read 1 (a reply that passes V0 and V1 and has a field that differs from the constructive gold). Per base object: the contrast, averaged over the panel models. Test of the mean: two-sided sign-flip permutation test. A negative value means fewer silent errors under the first form of the contrast.

| # | Contrast | Objects | Panel mean, points | 95% interval | p | Holm p | Rejects at 0.05 | Direction |
|---|---|---|---|---|---|---|---|---|
| 1 | renaming: b_renamed minus c_described, collision wording | 100 | -0.6 | [-3.3, +2.1] | 0.6564 | 0.6564 | no | as predicted |
| 2 | descriptions: c_described minus a_legacy, collision wording | 100 | -2.5 | [-5.0, -0.0] | 0.0604 | 0.2004 | no | as predicted |
| 3 | wording: collision wording minus the mean of the two rewordings, under a_legacy | 100 | -1.2 | [-3.4, +1.0] | 0.2802 | 0.5603 | no | against the prediction |
| 4 | interaction: wording effect under a_legacy minus wording effect under b_renamed | 100 | -3.9 | [-7.3, -0.5] | 0.0238 | 0.1190 | no | against the prediction |
| 5 | value_label: e_value_renamed minus b_renamed, collision wording | 100 | -2.6 | [-4.9, +0.0] | 0.0501 | 0.2004 | no | as predicted |

- Claim 1 holds on constructed items (contrasts 3 and 1 reject, with the predicted signs): no.
- The anchoring reading (Claim 1, and contrast 5 rejects with the predicted sign): no.

## 2. Missing cells and the worst case

A read with no row, a row that did not succeed, a cut reply, or a parse, V0 or V1 failure is a missing cell for the silent error. The primary test leaves it out. The worst case scores it in the direction that shrinks the contrast.

Reads: 8400. Missing for the silent error: 102.

| Model, variant, wording | Missing | Reasons |
|---|---|---|
| sonnet a_legacy collision | 3 | V1 empty report 3 |
| sonnet a_legacy reword_1 | 13 | V1 empty report 13 |
| sonnet a_legacy reword_2 | 5 | V1 empty report 5 |
| sonnet c_described collision | 7 | V1 empty report 7 |
| sonnet c_described reword_1 | 9 | V1 empty report 9 |
| sonnet c_described reword_2 | 4 | V1 empty report 4 |
| sonnet b_renamed collision | 5 | V1 empty report 5 |
| sonnet b_renamed reword_1 | 6 | V1 empty report 6 |
| sonnet b_renamed reword_2 | 5 | V1 empty report 5 |
| sonnet e_value_renamed collision | 4 | V1 empty report 4 |
| sonnet e_value_renamed reword_1 | 5 | V1 empty report 5 |
| sonnet e_value_renamed reword_2 | 2 | V1 empty report 2 |
| haiku a_legacy collision | 1 | V1 empty report 1 |
| haiku a_legacy reword_2 | 1 | V1 empty report 1 |
| haiku c_described collision | 2 | V1 empty report 2 |
| haiku c_described reword_1 | 1 | V1 empty report 1 |
| haiku c_described reword_2 | 2 | V1 empty report 2 |
| haiku b_renamed collision | 2 | V1 empty report 1, V1 unknown organization 1 |
| haiku b_renamed reword_2 | 1 | V1 empty report 1 |
| haiku e_value_renamed collision | 1 | V1 empty report 1 |
| haiku e_value_renamed reword_1 | 1 | V1 empty report 1 |
| deepseek a_legacy reword_2 | 2 | V1 duplicate condition 1, V1 unknown organization 1 |
| deepseek c_described reword_1 | 1 | V1 empty report 1 |
| deepseek b_renamed collision | 2 | V1 duplicate or overlapping organization 1, V1 empty report 1 |
| deepseek b_renamed reword_2 | 1 | V1 empty report 1 |
| deepseek e_value_renamed collision | 1 | V1 empty report 1 |
| deepseek e_value_renamed reword_2 | 2 | V1 empty report 2 |
| qwen a_legacy collision | 1 | V1 empty report 1 |
| qwen a_legacy reword_1 | 2 | V1 duplicate or overlapping organization 2 |
| qwen c_described reword_1 | 1 | V1 unknown organization 1 |
| qwen c_described reword_2 | 1 | V1 duplicate condition 1 |
| qwen b_renamed collision | 1 | V1 duplicate or overlapping organization 1 |
| qwen b_renamed reword_2 | 4 | V1 duplicate condition 1, V1 duplicate or overlapping organization 1, V1 unknown organization 2 |
| qwen e_value_renamed reword_1 | 1 | V1 empty report 1 |
| gemma c_described collision | 1 | V1 duplicate or overlapping organization 1 |
| gemma b_renamed reword_2 | 1 | V1 duplicate or overlapping organization 1 |

Worst case:

| # | Contrast | Objects | Panel mean, points | 95% interval | p | Holm p | Rejects at 0.05 | Direction |
|---|---|---|---|---|---|---|---|---|
| 1 | renaming: b_renamed minus c_described, collision wording | 100 | +0.7 | [-2.1, +3.4] | 0.6871 | 1.0000 | no | against the prediction |
| 2 | descriptions: c_described minus a_legacy, collision wording | 100 | -0.9 | [-3.6, +1.7] | 0.5957 | 1.0000 | no | as predicted |
| 3 | wording: collision wording minus the mean of the two rewordings, under a_legacy | 100 | -0.2 | [-2.4, +1.9] | 0.8916 | 1.0000 | no | against the prediction |
| 4 | interaction: wording effect under a_legacy minus wording effect under b_renamed | 100 | -1.4 | [-4.6, +1.9] | 0.4095 | 1.0000 | no | against the prediction |
| 5 | value_label: e_value_renamed minus b_renamed, collision wording | 100 | -1.7 | [-4.1, +1.0] | 0.2335 | 1.0000 | no | as predicted |

- The decisions are the same as in section 1: yes.
- The claim results are the same as in section 1: yes.

## 3. Each model's paired effect

The sign test is a description, not a registered test.

**1. renaming** (b_renamed minus c_described, collision wording)

| Model | Objects | Mean paired difference, points | 95% interval | Positive | Negative | Sign p (description) |
|---|---|---|---|---|---|---|
| sonnet | 89 | +2.2 | [-3.4, +7.9] | 5 | 3 | 0.7266 |
| haiku | 96 | -12.5 | [-25.0, +0.0] | 14 | 26 | 0.0807 |
| sol | 100 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1.0000 |
| luna | 100 | -1.0 | [-3.0, +0.0] | 0 | 1 | 1.0000 |
| deepseek | 98 | +0.0 | [-7.1, +7.1] | 6 | 6 | 1.0000 |
| qwen | 99 | +6.1 | [-3.0, +15.2] | 14 | 8 | 0.2863 |
| gemma | 99 | +1.0 | [-6.1, +7.1] | 6 | 5 | 1.0000 |

**2. descriptions** (c_described minus a_legacy, collision wording)

| Model | Objects | Mean paired difference, points | 95% interval | Positive | Negative | Sign p (description) |
|---|---|---|---|---|---|---|
| sonnet | 90 | +2.2 | [-2.2, +6.7] | 3 | 1 | 0.6250 |
| haiku | 97 | -1.0 | [-12.4, +10.3] | 15 | 16 | 1.0000 |
| sol | 100 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1.0000 |
| luna | 100 | -15.0 | [-23.0, -8.0] | 1 | 16 | 0.0003 |
| deepseek | 100 | +2.0 | [-5.0, +9.0] | 7 | 5 | 0.7744 |
| qwen | 99 | -4.0 | [-13.1, +4.0] | 8 | 12 | 0.5034 |
| gemma | 99 | -1.0 | [-7.1, +6.1] | 5 | 6 | 1.0000 |

**3. wording** (collision wording minus the mean of the two rewordings, under a_legacy)

| Model | Objects | Mean paired difference, points | 95% interval | Positive | Negative | Sign p (description) |
|---|---|---|---|---|---|---|
| sonnet | 96 | -10.9 | [-16.7, -5.2] | 1 | 18 | 0.0001 |
| haiku | 99 | +9.6 | [+0.5, +18.2] | 33 | 20 | 0.0984 |
| sol | 100 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1.0000 |
| luna | 100 | +3.5 | [-1.5, +8.5] | 16 | 9 | 0.2295 |
| deepseek | 100 | -9.0 | [-14.5, -3.0] | 4 | 25 | 0.0001 |
| qwen | 99 | +4.0 | [-3.0, +11.6] | 12 | 14 | 0.8450 |
| gemma | 100 | -5.5 | [-11.5, +0.5] | 6 | 19 | 0.0146 |

**4. interaction** (wording effect under a_legacy minus wording effect under b_renamed)

| Model | Objects | Mean paired difference, points | 95% interval | Positive | Negative | Sign p (description) |
|---|---|---|---|---|---|---|
| sonnet | 91 | -13.7 | [-20.9, -7.1] | 4 | 21 | 0.0009 |
| haiku | 97 | +5.2 | [-8.2, +18.0] | 40 | 29 | 0.2284 |
| sol | 100 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1.0000 |
| luna | 100 | +3.5 | [-1.5, +8.5] | 16 | 9 | 0.2295 |
| deepseek | 98 | -12.8 | [-21.9, -4.1] | 11 | 29 | 0.0064 |
| qwen | 98 | -0.5 | [-13.3, +11.2] | 24 | 24 | 1.0000 |
| gemma | 100 | -8.5 | [-17.5, -0.5] | 9 | 22 | 0.0294 |

**5. value_label** (e_value_renamed minus b_renamed, collision wording)

| Model | Objects | Mean paired difference, points | 95% interval | Positive | Negative | Sign p (description) |
|---|---|---|---|---|---|---|
| sonnet | 91 | +0.0 | [-6.6, +6.6] | 5 | 5 | 1.0000 |
| haiku | 97 | -5.2 | [-16.5, +6.2] | 12 | 17 | 0.4583 |
| sol | 100 | +0.0 | [+0.0, +0.0] | 0 | 0 | 1.0000 |
| luna | 100 | +1.0 | [+0.0, +3.0] | 1 | 0 | 1.0000 |
| deepseek | 97 | -5.2 | [-11.3, +1.0] | 3 | 8 | 0.2266 |
| qwen | 99 | -9.1 | [-17.2, -1.0] | 5 | 14 | 0.0636 |
| gemma | 100 | +0.0 | [-7.0, +7.0] | 6 | 6 | 1.0000 |

## 4. Each collision word (description, no test)

| Word | Contrast | Objects | Panel mean, points | 95% interval |
|---|---|---|---|---|
| onsite | 1. renaming | 25 | -8.9 | [-14.3, -4.0] |
| onsite | 2. descriptions | 25 | -10.9 | [-15.4, -6.3] |
| onsite | 3. wording | 25 | -3.9 | [-8.9, +1.2] |
| onsite | 4. interaction | 25 | -2.8 | [-9.9, +5.2] |
| onsite | 5. value_label | 25 | +0.1 | [-5.0, +5.1] |
| north | 1. renaming | 25 | +3.0 | [-2.9, +9.1] |
| north | 2. descriptions | 25 | +1.7 | [-2.9, +6.3] |
| north | 3. wording | 25 | -0.6 | [-4.3, +3.0] |
| north | 4. interaction | 25 | -7.0 | [-14.0, +0.3] |
| north | 5. value_label | 25 | -5.6 | [-10.9, +0.2] |
| retail | 1. renaming | 25 | -0.1 | [-4.9, +4.5] |
| retail | 2. descriptions | 25 | +1.1 | [-2.5, +5.2] |
| retail | 3. wording | 25 | -1.1 | [-5.3, +2.7] |
| retail | 4. interaction | 25 | -5.5 | [-10.0, -0.9] |
| retail | 5. value_label | 25 | -4.2 | [-8.3, +0.6] |
| large | 1. renaming | 25 | +3.5 | [-0.8, +8.1] |
| large | 2. descriptions | 25 | -2.0 | [-8.0, +3.3] |
| large | 3. wording | 25 | +0.8 | [-3.4, +5.6] |
| large | 4. interaction | 25 | -0.4 | [-7.0, +6.2] |
| large | 5. value_label | 25 | -0.6 | [-5.7, +4.6] |

## 5. Secondary outcomes (description, no test)

**all_errors**

| Contrast | Objects | Panel mean, points | 95% interval |
|---|---|---|---|
| 1. renaming | 100 | -0.7 | [-3.6, +2.0] |
| 2. descriptions | 100 | -1.6 | [-4.1, +1.0] |
| 3. wording | 100 | -1.9 | [-4.0, +0.4] |
| 4. interaction | 100 | -4.5 | [-8.1, -0.9] |
| 5. value_label | 100 | -3.1 | [-5.7, -0.6] |

**unsupported_commitment**

| Contrast | Objects | Panel mean, points | 95% interval |
|---|---|---|---|
| 1. renaming | 100 | -2.5 | [-4.1, -1.2] |
| 2. descriptions | 100 | -2.6 | [-4.2, -1.1] |
| 3. wording | 100 | +2.2 | [+0.8, +3.7] |
| 4. interaction | 100 | +1.8 | [+0.2, +3.4] |
| 5. value_label | 100 | -0.4 | [-1.0, +0.1] |

## 6. Rates (description)

Count of reads with the outcome / reads with a value.

| Model | Variant and wording | Silent error | All errors | Unsupported commitment |
|---|---|---|---|---|
| sonnet | a_legacy collision | 1/97 (1.0%) | 4/100 (4.0%) | 0/97 (0.0%) |
| sonnet | a_legacy reword_1 | 7/87 (8.0%) | 20/100 (20.0%) | 0/87 (0.0%) |
| sonnet | a_legacy reword_2 | 13/95 (13.7%) | 18/100 (18.0%) | 0/95 (0.0%) |
| sonnet | c_described collision | 3/93 (3.2%) | 10/100 (10.0%) | 0/93 (0.0%) |
| sonnet | c_described reword_1 | 4/91 (4.4%) | 13/100 (13.0%) | 0/91 (0.0%) |
| sonnet | c_described reword_2 | 4/96 (4.2%) | 8/100 (8.0%) | 0/96 (0.0%) |
| sonnet | b_renamed collision | 5/95 (5.3%) | 10/100 (10.0%) | 0/95 (0.0%) |
| sonnet | b_renamed reword_1 | 6/94 (6.4%) | 12/100 (12.0%) | 0/94 (0.0%) |
| sonnet | b_renamed reword_2 | 3/95 (3.2%) | 8/100 (8.0%) | 0/95 (0.0%) |
| sonnet | e_value_renamed collision | 5/96 (5.2%) | 9/100 (9.0%) | 0/96 (0.0%) |
| sonnet | e_value_renamed reword_1 | 2/95 (2.1%) | 7/100 (7.0%) | 0/95 (0.0%) |
| sonnet | e_value_renamed reword_2 | 4/98 (4.1%) | 6/100 (6.0%) | 0/98 (0.0%) |
| haiku | a_legacy collision | 35/99 (35.4%) | 36/100 (36.0%) | 20/99 (20.2%) |
| haiku | a_legacy reword_1 | 17/100 (17.0%) | 17/100 (17.0%) | 0/100 (0.0%) |
| haiku | a_legacy reword_2 | 34/99 (34.3%) | 35/100 (35.0%) | 21/99 (21.2%) |
| haiku | c_described collision | 35/98 (35.7%) | 37/100 (37.0%) | 17/98 (17.3%) |
| haiku | c_described reword_1 | 13/99 (13.1%) | 14/100 (14.0%) | 0/99 (0.0%) |
| haiku | c_described reword_2 | 18/98 (18.4%) | 20/100 (20.0%) | 5/98 (5.1%) |
| haiku | b_renamed collision | 22/98 (22.4%) | 24/100 (24.0%) | 0/98 (0.0%) |
| haiku | b_renamed reword_1 | 19/100 (19.0%) | 19/100 (19.0%) | 0/100 (0.0%) |
| haiku | b_renamed reword_2 | 14/99 (14.1%) | 15/100 (15.0%) | 0/99 (0.0%) |
| haiku | e_value_renamed collision | 16/99 (16.2%) | 17/100 (17.0%) | 0/99 (0.0%) |
| haiku | e_value_renamed reword_1 | 21/99 (21.2%) | 22/100 (22.0%) | 0/99 (0.0%) |
| haiku | e_value_renamed reword_2 | 18/100 (18.0%) | 18/100 (18.0%) | 0/100 (0.0%) |
| sol | a_legacy collision | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | a_legacy reword_1 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | a_legacy reword_2 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | c_described collision | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | c_described reword_1 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | c_described reword_2 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | b_renamed collision | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | b_renamed reword_1 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | b_renamed reword_2 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | e_value_renamed collision | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | e_value_renamed reword_1 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| sol | e_value_renamed reword_2 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| luna | a_legacy collision | 16/100 (16.0%) | 16/100 (16.0%) | 15/100 (15.0%) |
| luna | a_legacy reword_1 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| luna | a_legacy reword_2 | 25/100 (25.0%) | 25/100 (25.0%) | 9/100 (9.0%) |
| luna | c_described collision | 1/100 (1.0%) | 1/100 (1.0%) | 1/100 (1.0%) |
| luna | c_described reword_1 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| luna | c_described reword_2 | 1/100 (1.0%) | 1/100 (1.0%) | 1/100 (1.0%) |
| luna | b_renamed collision | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| luna | b_renamed reword_1 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| luna | b_renamed reword_2 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| luna | e_value_renamed collision | 1/100 (1.0%) | 1/100 (1.0%) | 0/100 (0.0%) |
| luna | e_value_renamed reword_1 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| luna | e_value_renamed reword_2 | 0/100 (0.0%) | 0/100 (0.0%) | 0/100 (0.0%) |
| deepseek | a_legacy collision | 6/100 (6.0%) | 6/100 (6.0%) | 0/100 (0.0%) |
| deepseek | a_legacy reword_1 | 9/100 (9.0%) | 9/100 (9.0%) | 0/100 (0.0%) |
| deepseek | a_legacy reword_2 | 21/98 (21.4%) | 23/100 (23.0%) | 13/98 (13.3%) |
| deepseek | c_described collision | 8/100 (8.0%) | 8/100 (8.0%) | 0/100 (0.0%) |
| deepseek | c_described reword_1 | 5/99 (5.1%) | 6/100 (6.0%) | 0/99 (0.0%) |
| deepseek | c_described reword_2 | 6/100 (6.0%) | 6/100 (6.0%) | 0/100 (0.0%) |
| deepseek | b_renamed collision | 8/98 (8.2%) | 10/100 (10.0%) | 1/98 (1.0%) |
| deepseek | b_renamed reword_1 | 4/100 (4.0%) | 4/100 (4.0%) | 0/100 (0.0%) |
| deepseek | b_renamed reword_2 | 5/99 (5.1%) | 6/100 (6.0%) | 0/99 (0.0%) |
| deepseek | e_value_renamed collision | 4/99 (4.0%) | 5/100 (5.0%) | 0/99 (0.0%) |
| deepseek | e_value_renamed reword_1 | 4/100 (4.0%) | 4/100 (4.0%) | 0/100 (0.0%) |
| deepseek | e_value_renamed reword_2 | 4/98 (4.1%) | 6/100 (6.0%) | 0/98 (0.0%) |
| qwen | a_legacy collision | 12/99 (12.1%) | 13/100 (13.0%) | 4/99 (4.0%) |
| qwen | a_legacy reword_1 | 8/98 (8.2%) | 10/100 (10.0%) | 3/98 (3.1%) |
| qwen | a_legacy reword_2 | 8/100 (8.0%) | 8/100 (8.0%) | 2/100 (2.0%) |
| qwen | c_described collision | 8/100 (8.0%) | 8/100 (8.0%) | 3/100 (3.0%) |
| qwen | c_described reword_1 | 6/99 (6.1%) | 7/100 (7.0%) | 0/99 (0.0%) |
| qwen | c_described reword_2 | 6/99 (6.1%) | 7/100 (7.0%) | 0/99 (0.0%) |
| qwen | b_renamed collision | 14/99 (14.1%) | 15/100 (15.0%) | 3/99 (3.0%) |
| qwen | b_renamed reword_1 | 12/100 (12.0%) | 12/100 (12.0%) | 0/100 (0.0%) |
| qwen | b_renamed reword_2 | 6/96 (6.2%) | 10/100 (10.0%) | 1/96 (1.0%) |
| qwen | e_value_renamed collision | 5/100 (5.0%) | 5/100 (5.0%) | 1/100 (1.0%) |
| qwen | e_value_renamed reword_1 | 6/99 (6.1%) | 7/100 (7.0%) | 2/99 (2.0%) |
| qwen | e_value_renamed reword_2 | 7/100 (7.0%) | 7/100 (7.0%) | 1/100 (1.0%) |
| gemma | a_legacy collision | 6/100 (6.0%) | 6/100 (6.0%) | 0/100 (0.0%) |
| gemma | a_legacy reword_1 | 4/100 (4.0%) | 4/100 (4.0%) | 0/100 (0.0%) |
| gemma | a_legacy reword_2 | 19/100 (19.0%) | 19/100 (19.0%) | 0/100 (0.0%) |
| gemma | c_described collision | 5/99 (5.1%) | 6/100 (6.0%) | 0/99 (0.0%) |
| gemma | c_described reword_1 | 4/100 (4.0%) | 4/100 (4.0%) | 0/100 (0.0%) |
| gemma | c_described reword_2 | 4/100 (4.0%) | 4/100 (4.0%) | 0/100 (0.0%) |
| gemma | b_renamed collision | 6/100 (6.0%) | 6/100 (6.0%) | 0/100 (0.0%) |
| gemma | b_renamed reword_1 | 2/100 (2.0%) | 2/100 (2.0%) | 0/100 (0.0%) |
| gemma | b_renamed reword_2 | 4/99 (4.0%) | 5/100 (5.0%) | 0/99 (0.0%) |
| gemma | e_value_renamed collision | 6/100 (6.0%) | 6/100 (6.0%) | 0/100 (0.0%) |
| gemma | e_value_renamed reword_1 | 10/100 (10.0%) | 10/100 (10.0%) | 0/100 (0.0%) |
| gemma | e_value_renamed reword_2 | 4/100 (4.0%) | 4/100 (4.0%) | 0/100 (0.0%) |

| Word | Variant and wording | Silent error | All errors | Unsupported commitment |
|---|---|---|---|---|
| onsite | a_legacy collision | 46/174 (26.4%) | 47/175 (26.9%) | 38/174 (21.8%) |
| onsite | a_legacy reword_1 | 7/174 (4.0%) | 8/175 (4.6%) | 1/174 (0.6%) |
| onsite | a_legacy reword_2 | 97/172 (56.4%) | 100/175 (57.1%) | 44/172 (25.6%) |
| onsite | c_described collision | 28/174 (16.1%) | 29/175 (16.6%) | 18/174 (10.3%) |
| onsite | c_described reword_1 | 12/174 (6.9%) | 13/175 (7.4%) | 0/174 (0.0%) |
| onsite | c_described reword_2 | 17/175 (9.7%) | 17/175 (9.7%) | 6/175 (3.4%) |
| onsite | b_renamed collision | 12/169 (7.1%) | 18/175 (10.3%) | 0/169 (0.0%) |
| onsite | b_renamed reword_1 | 16/173 (9.2%) | 18/175 (10.3%) | 0/173 (0.0%) |
| onsite | b_renamed reword_2 | 10/172 (5.8%) | 13/175 (7.4%) | 1/172 (0.6%) |
| onsite | e_value_renamed collision | 13/175 (7.4%) | 13/175 (7.4%) | 0/175 (0.0%) |
| onsite | e_value_renamed reword_1 | 14/175 (8.0%) | 14/175 (8.0%) | 0/175 (0.0%) |
| onsite | e_value_renamed reword_2 | 6/175 (3.4%) | 6/175 (3.4%) | 0/175 (0.0%) |
| north | a_legacy collision | 9/174 (5.2%) | 10/175 (5.7%) | 0/174 (0.0%) |
| north | a_legacy reword_1 | 13/170 (7.6%) | 18/175 (10.3%) | 1/170 (0.6%) |
| north | a_legacy reword_2 | 7/175 (4.0%) | 7/175 (4.0%) | 0/175 (0.0%) |
| north | c_described collision | 12/174 (6.9%) | 13/175 (7.4%) | 2/174 (1.1%) |
| north | c_described reword_1 | 9/174 (5.2%) | 10/175 (5.7%) | 0/174 (0.0%) |
| north | c_described reword_2 | 6/173 (3.5%) | 8/175 (4.6%) | 0/173 (0.0%) |
| north | b_renamed collision | 17/175 (9.7%) | 17/175 (9.7%) | 2/175 (1.1%) |
| north | b_renamed reword_1 | 7/172 (4.1%) | 10/175 (5.7%) | 0/172 (0.0%) |
| north | b_renamed reword_2 | 5/173 (2.9%) | 7/175 (4.0%) | 0/173 (0.0%) |
| north | e_value_renamed collision | 6/172 (3.5%) | 9/175 (5.1%) | 0/172 (0.0%) |
| north | e_value_renamed reword_1 | 9/174 (5.2%) | 10/175 (5.7%) | 0/174 (0.0%) |
| north | e_value_renamed reword_2 | 12/174 (6.9%) | 13/175 (7.4%) | 0/174 (0.0%) |
| retail | a_legacy collision | 11/173 (6.4%) | 13/175 (7.4%) | 1/173 (0.6%) |
| retail | a_legacy reword_1 | 17/172 (9.9%) | 20/175 (11.4%) | 0/172 (0.0%) |
| retail | a_legacy reword_2 | 8/172 (4.7%) | 11/175 (6.3%) | 0/172 (0.0%) |
| retail | c_described collision | 13/171 (7.6%) | 17/175 (9.7%) | 1/171 (0.6%) |
| retail | c_described reword_1 | 8/169 (4.7%) | 14/175 (8.0%) | 0/169 (0.0%) |
| retail | c_described reword_2 | 8/170 (4.7%) | 13/175 (7.4%) | 0/170 (0.0%) |
| retail | b_renamed collision | 13/173 (7.5%) | 15/175 (8.6%) | 1/173 (0.6%) |
| retail | b_renamed reword_1 | 8/174 (4.6%) | 9/175 (5.1%) | 0/174 (0.0%) |
| retail | b_renamed reword_2 | 7/171 (4.1%) | 11/175 (6.3%) | 0/171 (0.0%) |
| retail | e_value_renamed collision | 6/174 (3.4%) | 7/175 (4.0%) | 0/174 (0.0%) |
| retail | e_value_renamed reword_1 | 8/172 (4.7%) | 11/175 (6.3%) | 0/172 (0.0%) |
| retail | e_value_renamed reword_2 | 10/172 (5.8%) | 13/175 (7.4%) | 1/172 (0.6%) |
| large | a_legacy collision | 10/174 (5.7%) | 11/175 (6.3%) | 0/174 (0.0%) |
| large | a_legacy reword_1 | 8/169 (4.7%) | 14/175 (8.0%) | 1/169 (0.6%) |
| large | a_legacy reword_2 | 8/173 (4.6%) | 10/175 (5.7%) | 1/173 (0.6%) |
| large | c_described collision | 7/171 (4.1%) | 11/175 (6.3%) | 0/171 (0.0%) |
| large | c_described reword_1 | 3/171 (1.8%) | 7/175 (4.0%) | 0/171 (0.0%) |
| large | c_described reword_2 | 8/175 (4.6%) | 8/175 (4.6%) | 0/175 (0.0%) |
| large | b_renamed collision | 13/173 (7.5%) | 15/175 (8.6%) | 1/173 (0.6%) |
| large | b_renamed reword_1 | 12/175 (6.9%) | 12/175 (6.9%) | 0/175 (0.0%) |
| large | b_renamed reword_2 | 10/172 (5.8%) | 13/175 (7.4%) | 0/172 (0.0%) |
| large | e_value_renamed collision | 12/173 (6.9%) | 14/175 (8.0%) | 1/173 (0.6%) |
| large | e_value_renamed reword_1 | 12/172 (7.0%) | 15/175 (8.6%) | 2/172 (1.2%) |
| large | e_value_renamed reword_2 | 9/175 (5.1%) | 9/175 (5.1%) | 0/175 (0.0%) |

Field kinds of the silent errors (reads with at least one wrong field of the kind):

| Model | Field kinds |
|---|---|
| sonnet | acceptability 1, conditions 56 |
| haiku | acceptability 1, conditions 261, ranking 1 |
| sol | - |
| luna | acceptability 2, conditions 43, ranking 2 |
| deepseek | acceptability 19, conditions 72, ranking 19 |
| qwen | acceptability 22, conditions 78, ranking 25 |
| gemma | conditions 74 |

## Choices (CHOICES)

Where the registration was not specific enough to code a step, the script uses the plainest reading:

- **family**: The 5 contrasts are registration B section 5, H4 synthetic family, items 1 to 5, in that order, with Holm over the 5 p values. Each is a paired difference per base object and model.
- **panel**: The panel is the 7 models that ran Track I (PANEL). gemini-3.8-flash has no Track I answer at the filing; if it runs later, its answers do not enter these tests (registration B section 5b).
- **reply**: The reply is the last top-level JSON object in the answer text: the scan starts at each `{` from the left, and an object that parses moves the scan to its end. No object is a parse failure.
- **V0**: V0 is the closed JSON schema of the request's family and variant in main/track_i/schema_snapshot.json (keys, types, enums, no extra key). A boolean is never a string, and a string is never a boolean.
- **V1**: V1 is the typed validator of PLAN SI-05 for the Track I report, on a reply that passes V0. It rejects: an organization name that is not one of the 6 names of the object (after whitespace and case folding); an organization twice in `ranking`, twice in `unacceptable`, or in both; two conditions with the same organization and attribute; a report with all three lists empty; and a label without a canonical value in the variant's attribute table. Reason: PLAN SI-05 lists unknown values, duplicate or overlapping organizations and an all-empty report; the SI-05 validator itself does not exist yet.
- **canonical**: A V1-valid reply is mapped to the canonical labels by the attribute table of its variant (schema_snapshot.json, `attributes`: name to canonical name, label to canonical value), and it is compared with `gold_canonical` of main/track_i/gold.jsonl.
- **fields**: The fields are those of the repository rule (semantic-integrity si_eval/extraction_task.py, _erroneous_fields), without valuations: `acceptability:<org>` for each of the 6 organizations (acceptable = in `ranking`, unacceptable = in `unacceptable`, else unspecified); `conditions:<org>.<attribute>` for each pair in the gold or the reply; `ranking:full` when the ranked set differs or two organizations of both rankings change order.
- **silent error**: A read scores 1 when it passes V0 and V1 and at least one field differs from the gold, and 0 when it passes V0 and V1 and no field differs. Reason: PLAN SI-08, a field value that passes V1 and differs from the constructive gold; one read is the unit of a cell.
- **missing**: A read is a missing cell for the silent error when it has no row, its row did not succeed, it did not stop at end_turn, or it fails the parse, V0 or V1. Reason: registration A section 7 (a V0 failure or a cut reply is a missing cell); a V1 failure is loud, so it is not silent.
- **gold check**: Before any answer is scored, the gold of each of the 1,200 requests, in the labels of its variant, must pass V0 and V1 and score 0. Else the script stops.
- **contrast value**: Per base object and model, a contrast is the sum of its terms, coefficient times the value. A term on one wording is the read of that cell. A term on the two rewordings is the mean of their valid reads (one or two). A contrast with a term without a value has no value.
- **panel mean**: Per base object, the mean of the contrast over the panel models that have a value. A base object without any value leaves the test. Each base object has equal weight.
- **test**: Two-sided sign-flip permutation test of the mean over base objects (stats.permutation_test), 10,000 draws, seed PERMUTATION_SEED, the same seed for each contrast. Holm (stats.holm) over the 5 contrasts. A contrast rejects when its Holm p is 0.05 or less.
- **predicted signs**: Contrast 1 (renaming) negative, 2 (descriptions) negative, 3 (wording) positive, 4 (interaction) positive, 5 (value label) negative. The tests are two-sided. The signs are used by the claim rules (contrasts 1, 3 and 5) and to break a zero mean in the worst case.
- **claims**: Claim 1 holds on constructed items when contrasts 3 and 1 reject with the predicted signs. The anchoring reading holds when Claim 1 holds and contrast 5 rejects with the predicted sign. Reason: registration B section 5, Claim 1 (decision D1).
- **worst case**: Each missing cell is scored in the direction that shrinks the contrast: against the sign of the primary panel mean of that contrast (the predicted sign when the mean is 0). A cell whose term has a coefficient of the same sign scores 0, else 1. Then the same test and Holm run again.
- **intervals**: Every interval is the 95% percentile interval of stats.cluster_bootstrap, 2,000 draws, BOOTSTRAP_SEED. The cluster is the base object.
- **per model**: Each model's paired effect is the mean of its contrast values over the base objects, with its interval. The exact sign test of each model is a description, not a registered test.
- **per word**: Part 4 gives each contrast on the 25 base objects of each collision word, with its interval and no test. Reason: PLAN SI-11, the results per collision word as description.
- **all errors**: Secondary, no test: a read scores 1 when it fails the parse, V0 or V1, or has a silent error, and 0 when it passes V1 with no wrong field. A read with no row, a row that did not succeed or a cut reply is missing. Reason: PLAN SI-08, all errors add the V0 and V1 failures.
- **unsupported commitment**: Secondary, no test: a V1-valid read scores 1 when it states a condition (organization and attribute) that the gold does not state, else 0. Reason: PLAN SI-08, a value for a field that the text leaves not stated; every Track I text states one condition.
- **one read**: Track I has one read per cell (PLAN SI-10). There is no repeat analysis.
- **frozen inputs**: Every file of main/track_i/SHA256SUMS must have its hash, the SHA-256 of SHA256SUMS must equal track_i_sha256sums of main/wave2_track_i_manifest.json, and the manifest must give 1,200 requests for each panel model.
- **input check**: The input folder must hold em2i_<model> folders of the panel only, and unseal_manifest.json with the same panel. Each raw.jsonl must match the SHA-256 and row count of the manifest. `._*` files are ignored.
