# Amendment A1 to registration A (draft for the operator's approval)

Status: **DRAFT, 2026-11-12.** The operator reads this file, approves it, and files it on OSF together with registration A, the corrected texts of part 2, and the hash list `main/exp0/sealed_hashes.txt`, before any answer of wave 1 is unsealed. The SHA-256 values in part 1 were computed on 2026-11-12 after an independent review of the script; a later change of any of the three files makes them wrong, and the filing must then wait.

## 1. The amendment

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

## 2. Corrected texts (applied after the operator's approval; the diff is shown to the operator)

### `main/REGISTRATION-A.md`

- Line 11, replace with: "The wave-1 calls ran from 2026-11-04, under this text as a draft and before this filing. Each answer was encrypted when it arrived (section 9). At the time of this filing, no person and no agent has read an answer. Section 11 gives the SHA-256 of every sealed file, so a reader can check that no answer changed after the filing. No person reads an answer of a Track P sample dialogue before the operator's codes and the test-retest are frozen."
- Section 4, add after the goal-hotel line: "68 of the 281 natural dialogues and 20 of the 97 goal-hotel dialogues are also in the Track P sample. Their answers stay sealed until the Track P codes are frozen. The other 213 and 77 dialogues are the uncoded subset."
- Section 6, add: "The interim panel (amendment A1) is the 7 models that are not Google models. The final panel adds `gemini-3.8-flash` if it has run."
- New section 7b, "Amendment A1 (filed with this registration, before any unseal)": the text of part 1 of this file.
- Section 7, "Smallest effects of interest", add: "No test uses this value. It is a reading aid for the size of an effect."
- Section 10, add: "The calls ran before this filing (section 1)."
- Section 11, add rows for the hash list `main/exp0/sealed_hashes.txt` and for the three scripts of part 1.

### `REVISION-12.md`

- Line 59, replace with: "213 of the 281 natural dialogues and 77 of the 97 goal-hotel dialogues are outside the Track P sample, so the operator never codes them. Their answers are sealed so that the analysis runs once, under the frozen specification. The other 68 and 20 dialogues are in the Track P sample, and their answers stay sealed for blinding."
- Section 3, add: "The registrations were filed after the calls and before any unseal. The paper says so."
- Section 2, row D9, add: "Reversed for round 10 by the operator on 2026-11-12 (`ROUND10-EXPERIMENT-PLAN.md`)."

## 3. The operator's steps (about 1.5 hours)

1. Read parts 1 and 2. Tell Opus "A1 approved" or the changes.
2. After the DeepInfra main-study runs end, run in the macOS Terminal app: `bash main/exp0/hash_sealed.sh` (from `prototypes/explore/`). It reads bytes only and needs no key.
3. Upload to OSF (osf.io, a free account; a new registration or a public project with a time stamp): registration A with its corrections, this file, `main/exp0/sealed_hashes.txt`, and `PROTOCOL.md`. Give Opus the URL and the time stamp.
4. Then run the stage-1 unseal (Opus gives the one command), and type the passphrase of the sealing key.
