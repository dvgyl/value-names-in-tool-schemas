# Registration A: sealed natural-dialogue collection (wave 1)

Status: **DRAFT for the operator's review.** The operator files it before the first wave-1 call. At filing, the operator fills in the final SHA-256 hashes in section 11 and confirms the smallest effects in section 7.

Author: Dev Goyal (independent researcher, India). Project: Semantic Integrity Harness. Plan: `improvement-plan/REVISION-12.md` over `improvement-plan/PLAN.md` revision 11.

## 1. What this registration covers

- Wave 1 of the confirmatory collection: the H4 natural test on MultiWOZ 2.4 dialogues, its two new outcomes (correct values kept and the prefix), the placebo form, and the Track P written sample.
- It does not cover Track I or Track C. Registration B covers them before wave 2.
- The wave-1 calls ran from 2026-11-04, under this text as a draft and before this filing. Each answer was encrypted when it arrived (section 9). At the time of this filing, no person and no agent has read an answer. Section 11 gives the SHA-256 of every sealed file, so a reader can check that no answer changed after the filing. No person reads an answer of a Track P sample dialogue before the operator's codes and the test-retest are frozen.

## 2. Earlier data (full disclosure)

- Prototypes P1 to P5, exploratory runs E1 to E15, and round 9 (runs X1, X2, X5, X7, Z1 to Z3, B1 to B4) ran before this registration. Their results are in `prototypes/explore/RESULTS.md` and `prototypes/explore/RESULTS-R9.md`.
- These runs used the MultiWOZ training split and the 123 single-domain P4 dialogues only. Every exploratory request builder checks that no dialogue of the validation and test pool is in a request (`lib/anth.py`, `assert_outside_trackp`).
- Round 9 changed the design. Its main results:
  - Renaming the `type` value lowers wrong `type = hotel` values on all 7 models tested.
  - The rename also lowers correct `type = hotel` values.
  - The value word carries the effect, not the field name.
  - At the prefix, the commitment is near the base rate of a hotel booking.

## 3. Claim and hypotheses

- **Claim 1 (H4), as changed by decision D1:** a schema value word anchors extraction when the same word is in the text. Schema wording sets the balance between wrong and correct values. The study does not call a rename a fix.
- **H4 natural, wrong values:** under `t_renamed`, models write `type = hotel` less often than under `t_legacy` on dialogues where the goal sets no hotel type (prediction from round 9: lower on every model).
- **H4 natural, correct values kept (decision D2):** under `t_renamed`, models also write `type = hotel` less often on dialogues where the goal sets `type` = `hotel` (prediction from round 9: lower on every model).
- Claim 1 transfers to natural dialogue when the wrong-value contrast rejects (PLAN SI-10). The anchoring reading needs both contrasts to reject in the same direction.

## 4. Units and split

- Pool: the 687 multi-domain hotel dialogues of the MultiWOZ 2.4 validation and test sets.
- Order: one random order of the sorted pool. The seed is the first 16 hex digits of the SHA-256 of the text "Semantic Integrity revision 12, Track P split, 2026-11-04", as an integer (14829592008656330191). The seed text was fixed before any call and before any model output on the pool existed.
- Gate set: the first 64 dialogues of the order. **No model call reads a gate-set dialogue.** The gate pilot of revision 11 does not run.
- Pool order: the other 623 dialogues, in the same order.
- Track P sample: the first 144 dialogues of the pool order.
- Natural sample (`nat`): every pool-order dialogue outside the gate set whose goal sets no hotel type (in `info` or `fail_info`) and whose traveller turns hold "hotel" or "hotels" (DECISIONS-R5). Count: 281.
- Goal-hotel sample (`hot`, decision D2): every pool-order dialogue outside the gate set whose goal sets `type` = `hotel`. Count: 97.
- 68 of the 281 natural dialogues and 20 of the 97 goal-hotel dialogues are also in the Track P sample. Their answers stay sealed until the Track P codes are frozen. The other 213 and 77 dialogues are the uncoded subset.
- Prefix (`pre`, decision D5): each natural-sample dialogue up to and including the first traveller turn with "hotel" or "hotels".
- Repeat subsets: a seeded 20% of each sample (natural 57, goal-hotel 20, Track P 29). Every compared form reads these dialogues 3 times and the rest once (DECISIONS-R7 item 7).
- All lists: `main/wave1_ids.json`. The rule that makes them: `main/wave1.py`.

## 5. Forms

All forms are the E13 `p_main` prompt and closed JSON schema with named changes (`main/wave1.py`, `FORMS`).

| Form | Change against `t_legacy` | Used on |
|---|---|---|
| `t_legacy` | none (E13 `p_main`) | nat, hot, pre |
| `t_renamed` | `type` becomes `property_kind`, `hotel` becomes `large_property` | nat, hot, pre |
| `t_described` | one-line field descriptions after the allowed values (text in `wave1.py`, `DESCRIPTIONS`) | nat, hot, pre |
| `f4` | `hotel` becomes `serviced_property` | nat, hot, pre |
| `f5` (placebo) | `area` becomes `district`, `pricerange` becomes `price_band` | nat, Claude models only |
| `p_main` | none (Track P form) | tp |
| `p_unclear` | `p_main` with the value "unclear" and its sentence | tp |

Each reply is mapped back to the legacy names before scoring.

## 6. Models and settings

- The panel of PLAN revision 11: `claude-sonnet-5-5`, `claude-haiku-5-5`, `gpt-6.1-sol`, `gpt-6-luna`, `DeepSeek-V4.1-Flash`, `Qwen3.8-27B`, `gemma-4-31B-it`, and `gemini-3.8-flash`.
- Settings: the E13 settings for the Claude models, effort low for `gpt-6.1-sol`, no reasoning for `gpt-6-luna`, and the round-9 DeepInfra settings (`r9/deepinfra_settings.py`). The `gemini-3.8-flash` settings are fixed in the manifest before filing.
- If `gemini-3.8-flash` cannot run before 2026-11-20, it runs later on cash under this registration, and the report says so.
- The interim panel (amendment A1) is the 7 models that are not Google models. The final panel adds `gemini-3.8-flash` if it has run.

## 7. Outcomes and tests

**Primary.** H4 natural: the share of reads that write `type = hotel` after the mapping back, per dialogue, form, and model (PLAN SI-08).

**H4 natural family (Holm, 2 tests):**

1. Wrong values: `t_renamed` against `t_legacy` on the natural sample.
2. Correct values kept: `t_renamed` against `t_legacy` on the goal-hotel sample (decision D2).

**Statistics (PLAN SI-10).** Each test is a paired cluster test. The cluster is the dialogue. For each dialogue, average the paired difference over the panel models. Test the mean with a two-sided sign-flip permutation test of 10,000 draws at 0.05. Read 1 is the primary read. The repeat means are sensitivity analyses. A V0 failure or a cut reply is a missing cell, and a worst-case sensitivity analysis scores each missing cell in the direction that shrinks the paired difference. Report each model's paired effect with a cluster bootstrap interval and the count of dialogues.

**Smallest effects of interest (stated before the filing; no test uses them, see below):** 5 percentage points for each family test. Round 9 found falls of 3.8 points (Haiku) to 26.9 points (Sol) on the wrong-value contrast of the training dialogues (`RESULTS-R9.md` section 2). The test averages over the panel, so the panel mean is the relevant size. No test uses this value. It is a reading aid for the size of an effect.

**Secondary, each with a cluster bootstrap interval, no test:**

- The ratio "correct values lost per wrong value removed" for `t_renamed` and for `f4`, per model.
- `f4` against `t_legacy` on both samples (decision D3).
- `t_described` against `t_legacy` on both samples (PLAN SI-10).
- The placebo: `f5` against `t_legacy` on the natural sample, Claude models. Claim 1 is stated net of it: the wrong-value effect minus the placebo effect (decision D4).
- The prefix (decision D5): the share of `type = hotel` per form, and the share of reads whose `type` excludes the type of the venue that the traveller later booked, per model. The booked venue comes from the dialogue's booking turn and `hotel_db.json` (rule of `r9/additions/zruns.py`, `booked_venue`).
- Any `type` commitment (PLAN SI-08).

**Track P (descriptive).** `p_main` against `p_unclear` on the 144 sample dialogues, scored later against the operator's frozen blind codes. G8a is not claimed, so Track P stays descriptive (REVISION-12 section 4).

**Effort ablation.** `gpt-6.1-sol` at its default effort reads the 29 Track P `sample_repeat` dialogues under `p_main`. Registration B, section 5a, registers it with the Track C part.

## 7b. Amendment A1 (filed with this registration, before any unseal)

- **Two looks.** The two tests of the H4 natural family run on the uncoded subset now (the interim look) and on all dialogues after the Track P codes and the test-retest are frozen (the final look). Each look uses alpha 0.025, with Holm over the two tests inside the look. The report gives both looks.
- **The two tests of the family.** For each dialogue and each model of the interim panel: D = (read 1 of `t_renamed` writes `type = hotel`) minus (read 1 of `t_legacy` writes `type = hotel`), each scored 0 or 1 with the parser of `main/wave1.py`. D is averaged over the models with a valid pair, then the two-sided sign-flip permutation test (10,000 draws) tests the mean over dialogues.
  1. `wrong_values`: part `nat`, the 213 natural dialogues outside the Track P sample.
  2. `correct_values_kept`: part `hot`, the 77 goal-hotel dialogues outside the Track P sample.
- **The interim panel.** The 7 models whose wave-1 run is complete at the filing: `claude-sonnet-5-5`, `claude-haiku-5-5`, `gpt-6.1-sol`, `gpt-6-luna`, `DeepSeek-V4.1-Flash`, `Qwen3.8-27B`, `gemma-4-31B-it`. The final panel adds `gemini-3.8-flash` if it has run.
- **Staged unseal.** Stage 1: the answers of the uncoded subset, all wave-1 forms (parts `nat`, `plc`, `hot`, `pre`), now. Stage 2: the Track P sample and the other 68 natural and 20 goal-hotel dialogues, after the codes and the test-retest are frozen. The stage-1 script `main/exp0/subset_unseal.py` writes only rows of uncoded dialogues; a planted-marker test (`main/exp0/test_subset_unseal.py`) shows it.
- **New secondary outcomes, fixed before stage 1.** (a) Each registered contrast on the dialogues whose goal names no venue. (b) Search failure: the share of reads whose `type` keeps `hotel` and not `guesthouse` on dialogues where no hotel in `hotel_db.json` fits the goal (`info`), per model and form. (c) The ratio "correct values lost per wrong value removed", with a 95% cluster bootstrap interval. Outcome (d), a mixed logistic model, is **removed**: no package for it is installed, and the frozen script does not fit it.
- **Seeds.** Permutation `2026111201`; bootstrap `20261112` (2,000 draws).
- **The analysis script.** `main/exp0/analysis.py`, SHA-256 `c8841480ae3016d3ca71ab64daf265281f57b6dee800a9a4a73eaf2a8aa4d0d9`; it imports `r10/briefsearch.py`, SHA-256 `2615e6ac412c49ee507c6b2a5d76441df1e2d404ec789a33b9b6963d9fe09dce`, and `r10/analysis/stats.py`, SHA-256 `c90eb62a84f69fe2c6352ed4a9d5d9aad9d6265765088f30ba8fc47d36f03982`. The script also records the SHA-256 of `pmain/e13.py`, `r9/free/gold.py`, `r9/additions/zforms.py`, `lib/anth.py` and `main/wave1_manifest.json`, and it stops if the form hashes differ from the registered manifest. It refuses any panel other than the interim panel. It was tested on simulated answers only (`main/exp0/test_analysis.py`). The builder's choices where the registration was not specific are listed in its constant `CHOICES`, and they are part of this amendment.
- **Reason for the amendment.** The promo credits end after 2026-11-20, and two workshop papers are due on that date. The round-9 results that the amendment tests are disclosed in section 2 of registration A.

## 7a. Annotator models (PLAN SI-17)

- `gpt-6-astra` and `claude-opus-5-5` each code the 64 gate-set dialogues and a random half of the Track P sample (72 dialogues), once. The half is drawn from the seed text "Semantic Integrity revision 12, annotator half, 2026-11-04" (`main/annotators.py`, `main/annotators_ids.json`).
- The prompt is the draft codebook `annot/codebook.md` (SHA-256 `bff44f7a881d84e3327f76021eb6b21f834935d584f4a62cd04a4ce837613154`), the text of runs E3 and X5. The frozen codebook of SI-10 does not exist yet, so this registration freezes the draft text.
- The annotators never see a model answer. Their codes are sealed like the answers, and the operator opens them only after the test-retest (PLAN SI-17).
- Settings: those of X5 (Opus effort medium, Astra effort low, 16,000 output tokens).

## 8. Exclusions and missing data

- No exclusion of a dialogue after this filing.
- A request with no answer after the registered reruns is a missing cell (section 7).
- If a batch does not end before the credits expire after 2026-11-20, its missing requests run on cash under this registration, and the report says so.

## 9. Sealing

- Every answer is encrypted when it arrives (`lib/seal.py`). Only status, token usage, the served model, the stop reason, and whether the text parses as a JSON object stay in plain text.
- The operator holds the only private key. No agent can open the answers.
- A planted-marker test checks every collection path (`lib/test_seal.py`).
- The answers are opened only after the Track P codes and the test-retest are frozen. The operator records the date of opening.
- If sealing fails for a run, that run loses confirmatory status and stays in the release as exploratory.

## 10. Deviations from PLAN revision 11

- The model calls run before the operator's codes, under the sealing rule of section 9. Revision 11 required that no output exist before the codes are frozen.
- No call on the gate set. The gate pilot (SI-16) and the gates G3, G5, and G8a do not run or are not claimed.
- New outcomes and forms from the round-9 decisions: D2 (correct values kept), D3 (`f4`), D4 (`f5`), and D5 (prefix).
- The split seed is stated here, not drawn in a separate step.
- The calls ran before this filing (section 1).

## 11. Frozen files

| File | SHA-256 |
|---|---|
| `main/wave1.py` | `bca97b4406466458ea750e3e96c3c69758aa6269c1e351c1b54dd39a81566072` |
| `main/wave1_ids.json` | `54743585a28df8ae39200c10fd526e55d3e07b4f87005989524fcc21428ae8f0` |
| `main/wave1_manifest.json` (request counts and request hashes per model, form hashes) | `274fe1219e1ae28b8bef13a51df1c45a8796d5b3cf9f456746bc407b32c699ce` |
| `lib/seal.py` | `46d9b6ca34f4904828e030dbbef4f0cf80d44adc6fa796c4eb272f9549c2ea4a` |
| `main/annotators.py`, `main/annotators_ids.json`, `main/annotators_manifest.json` | `2b8a6801ee3e5d6bcfb1d1c6258682d7c70bdd774c6ce9b86f0c380bb649f085`, `f0e4474272aeec40e8f17d7bc892b7502f4bee74e3efb4d648cfae565cc8915c`, `b9f4b574e69234aad90741fb685bbc521bca6c6619a9c4af1501255a6f12feac` |
| `main/exp0/sealed_hashes.txt` (the SHA-256 of every sealed file, made by `main/exp0/hash_sealed.sh`) | `e834eb54103d4095bf122a6a502e857f6562aa4d8c87a1e21022384c273c2daf` (193 files, made 2026-11-12; the runs still collecting at that time are named in the list and are covered by registration B) |
| `main/exp0/analysis.py`, `r10/briefsearch.py`, `r10/analysis/stats.py` (amendment A1) | `c8841480ae3016d3ca71ab64daf265281f57b6dee800a9a4a73eaf2a8aa4d0d9`, `2615e6ac412c49ee507c6b2a5d76441df1e2d404ec789a33b9b6963d9fe09dce`, `c90eb62a84f69fe2c6352ed4a9d5d9aad9d6265765088f30ba8fc47d36f03982` |

Command for the hashes: `shasum -a 256 main/wave1.py main/wave1_ids.json main/wave1_manifest.json lib/seal.py` (from `prototypes/explore/`).
