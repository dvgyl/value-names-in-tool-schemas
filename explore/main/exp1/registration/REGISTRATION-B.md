# Registration B: sealed constructed collection (wave 2: Track I and Track C)

Status: final text for the OSF filing. It is filed after the wave-2 calls and before any wave-2 answer is opened (section 1). Section 9 lists the changes to the draft of 2026-11-07.

Author: Dev Goyal (independent researcher, India). Plan: `improvement-plan/REVISION-12.md` over `improvement-plan/PLAN.md` revision 11. Registration A (https://osf.io/bv8q9, filed on 2026-11-12) covers wave 1. Its section 2 discloses the data before wave 1, and it applies here too. Section 1a adds the data seen after registration A.

## 1. What this registration covers

- Track I: Claim 1 on constructed job-placement reports with four collision words (PLAN SI-11).
- Track C: Claim 2, now secondary (decision D6), on constructed hotel dialogues with known readings (PLAN SI-12b, SI-19a).
- The answers are sealed as in registration A, section 9. Track I and Track C need no human code for their outcomes, but they are sealed so that the analysis runs once, under this specification.
- The wave-2 calls ran before this filing:
  - Batches (the Claude and OpenAI models): submitted on 2026-11-04 (Track I, Track C, and the annotator check of section 6) and on 2026-11-07 (the paraphrase arm of section 3a and the effort ablation of section 5a). Every batch was downloaded on 2026-11-11, from 23:20 to 23:22 UTC.
  - Synchronous runs (the 3 DeepInfra models): from 2026-11-11 23:21 UTC (pilots) to 2026-11-12 06:06 UTC. The Track I runs ended at 02:41 UTC on 2026-11-12.
- Each answer was encrypted when it reached the project computer: a batch answer when it was downloaded, a synchronous answer when it arrived (registration A, section 9).
- At the time of this filing, no person and no agent has decrypted or read a wave-2 answer. A check on 2026-11-13 used file names and the key names of the plain-text files, and it opened no sealed file. The wave-2 run folders hold only sealed answers, the public fields of registration A section 9, the requests, batch records, and token summaries. No decrypted copy of a wave-2 answer was found in the project folder, the home folder, the temporary folders, or the other attached drives. The only decrypted answers are the wave-1 stage-1 answers of registration A (`main/exp0/open/`, 7 `em1_` folders).
- This registration is filed before any wave-2 answer is opened. Section 8 gives the SHA-256 of every sealed wave-2 file, so a reader can check that no answer changed after the filing.
- This filing also carries a short addendum to registration A, `TRACKP-CODING-ADDENDUM.md`: the operator coding of the Track P sample and the seed of its re-code.

## 1a. Data seen after registration A (disclosure)

- The stage-1 result of registration A (amendment A1) was opened on 2026-11-12. Both tests of the H4 natural family rejected: under `t_renamed`, models wrote `type = hotel` less often on the natural and on the goal-hotel dialogues (`main/exp0/RESULT-STAGE1.md`). The author knew this result when this text was finished. Sections 2 to 6, except section 5b and the changes of section 9, are the draft of 2026-11-07, written before that result existed.
- The exploratory round-10 runs started on 2026-11-12 (`PROTOCOL.md`, "Round 10 runs"). The round-10 build stops any constructed text that shares a sentence of 4 or more words with a Track I or Track C item (`r10/groups.py`, `assert_new_text`). Round-10 results are exploratory.

## 2. Track I design (`main/track_i/`, README there)

- 4 collision words: "on-site", "north", "retail", "large". Each equals a name or a value label of the legacy schema.
- 25 new base objects per word (seed 20261104). No object, market, or text of P1, P2, P3, or E2 (the check is in `test_track_i.py`).
- 3 wordings per object: the collision wording and two rewordings without the word. All other sentences are fixed.
- 4 schema variants per family: `a_legacy`, `c_described` (descriptions added), `b_renamed` (renamed names, descriptions), and `e_value_renamed` (`b_renamed` with only the collision value label renamed). `e_value_renamed` replaces `d_neutral` of revision 11 (REVISION-12 O1), because round 9 found that the value word, not the field name, carries the effect.
- 1,200 requests per model, 1 read each (PLAN SI-10).

## 3. Track C design (`main/track_c/`, README there)

- 150 new objects (seed 20261107), 9 items each: an ambiguous item and its clear control in conditions a to d, and an accepted-offer control. 1,350 items.
- 4 new template families per condition. No family, template, sentence, or goal of E4, E9, E10, E14, E15, or any round-9 Track C run (the check is in `check_track_c.py`).
- Forms: `p_main`, `p_unclear`, `p_null`, copied byte for byte from the E14 requests. `p_option` is not in the study (decision D6).
- Every item runs once per form. The 30 repeat objects (seed "20261107-repeat") run 3 times per form. 5,670 requests per model.
- Shortcut baseline B1 (`main/track_c_b1.py`): the largest share of items that a regex reader of names and numbers rebuilds in one family is 26.3%. No family reaches the 50% exclusion rule (W9).

## 3a. Track C paraphrase arm (secondary evidence, PLAN SI-19a)

- Restored by the operator on 2026-11-07. Revision 11 cut it first in the registered cut order to save cash. The credits now pay for most of it.
- `claude-opus-5-5` (outside the panel) paraphrases each item of the first 60 objects (m001 to m060) once: 540 items, folder `mp_opus` (`main/paraphrase.py`). The prompt is in `main/paraphrase.py`. The code keeps the turns and speakers, and the model rewrites only the words of each turn. The paraphrases are inputs, so they are not sealed.
- Mechanical checks (`main/paraphrase_check.py`): the answer parses with the same turns; the interpretation set recomputed from the traveller's words equals the registered set; the wording rules of the template check; the same field values, hotel names, numbers and days, and no new hotel name; no MultiWOZ or exploratory sentence of 4 or more words. A failing paraphrase is excluded and listed. If more than 10% of a condition fails, the prompt is fixed and that condition is paraphrased again once (PLAN SI-19a). Round 1 (`mp_opus`) failed in conditions a to d, mostly on stock booking phrases that are MultiWOZ turns. Round 2 (`mp_opus2`, conditions a to d) adds rule 9 against stock phrases. Condition o keeps its round-1 paraphrases. A condition that fails round 2 has no paraphrase arm. There is no round 3. **Result (2026-11-07):** round 2 passes in a (4.2% failed) and d (5.0%), and condition o passed round 1 (6.7%). Conditions b (15.0%) and c (21.7%) fail round 2, so they have no paraphrase arm. The arm holds 285 checked paraphrases (conditions a, d, and o).
- Every checked paraphrase of a passing condition ran under `p_main` and `p_unclear`, K = 1, on the panel models of section 4 (folders `em2p_<model>`, sealed, 570 requests per model).
- Reference check: `gpt-6-astra` read 5 checked paraphrases per condition and kind of conditions a and d under `p_unclear` (20 reads, folder `em2pa_astra`, sealed). The share whose reading stays inside the compatible set is reported as description.
- Outcome: the H6 commitment contrast (`p_unclear` against `p_main`) on the paraphrases of condition a (the only ambiguous condition left; d is the negative control), with cluster bootstrap intervals and no test. Free rewriting can change the interpretation set, so this arm is secondary evidence only.

## 4. Models and settings

- The panel and settings of registration A, section 6.
- At this filing, the 7 models that are not Google models have an answer for every wave-2 request: every row of each run's `raw.jsonl` is `succeeded` (per model: Track I 1,200, Track C 5,670, paraphrase arm 570). The annotator check has 80 answers per annotator model, the reference check 20, and the effort ablation 299, all `succeeded`.
- `gemini-3.8-flash` has answered no wave-2 request.

## 5. Outcomes and tests

**Statistics:** as registration A, section 7. The cluster is the base object for Track I and the constructed object for Track C. For each cluster, average the paired difference over the panel models. Two-sided sign-flip permutation test, 10,000 draws, 0.05, Holm inside each family. Per-model effects with cluster bootstrap intervals.

**H4 synthetic family (Track I, Holm, 5 contrasts).** The primary outcome is the silent error: a field value that passes V1 and differs from the constructive gold (PLAN SI-08).

1. Renaming: `b_renamed` against `c_described`, on the collision wording.
2. Descriptions: `c_described` against `a_legacy`, on the collision wording.
3. Wording: the collision wording against the two rewordings, under `a_legacy`.
4. The wording-by-schema interaction: the wording effect under `a_legacy` against the wording effect under `b_renamed`.
5. The value label (new, REVISION-12 O1): `e_value_renamed` against `b_renamed`, on the collision wording.

**Claim 1 (decision D1).** Claim 1 holds on constructed items when contrasts 3 and 1 reject in the expected direction (PLAN SI-10). The anchoring reading also needs contrast 5 to reject: renaming only the value label lowers the silent error.

**H6 constructed family (Track C, secondary, Holm, 3 contrasts).** `p_unclear` against `p_main`, commitment on the built fields of the ambiguous items, conditions a, b, and c (PLAN SI-10, DECISIONS-R7 item 4). Constraint retention on the clear controls is judged by the retention margin of 5 percentage points, not by a test.

**H6 decomposition family (Track C, secondary, Holm).** `p_unclear` against `p_null` (the option) and `p_null` against `p_main` (the instruction), per ambiguous condition (C1).

**Condition d** is a negative control. Its gap-fill rate is reported apart, with zero-event upper bounds.

**Smallest effects of interest:** 5 percentage points (confirmed by the operator on 2026-11-13) for each H4 synthetic contrast and each H6 commitment contrast.

## 5a. Effort ablation (descriptive, PLAN SI-19a, N7)

- `gpt-6.1-sol` at its default reasoning effort (the `reasoning` setting is left out), K = 1, under `p_main`, on the items that the registered runs read 3 times: the 270 template items of the 30 Track C repeat objects and the 29 dialogues of the Track P `sample_repeat` list. 299 requests in folder `em3e_sol` (`main/effort_ablation.py`). Each request equals the registered `p_main` request with only the `reasoning` setting removed.
- Outcome: the paired difference between the default effort and the registered effort (`low`, read 1) in the commitment rate on the built fields of the ambiguous items and in the error rate on the clear fields. Track P is compared later against the operator's codes. No test.
- Submitted on 2026-11-07 under the standing approval, before this filing. The answers are sealed.

## 5b. The frozen Track I analysis

- Script: `main/exp1/analysis_b.py` (SHA-256 in section 8). It imports `r10/analysis/stats.py`, the statistics module of amendment A1 (SHA-256 `c90eb62a84f69fe2c6352ed4a9d5d9aad9d6265765088f30ba8fc47d36f03982`). It reads only the Track I answers that `main/exp1/unseal_track_i.py` writes, and it stops on any other row. It never overwrites its outputs, so it runs one time.
- Panel: the 7 models of section 4. If `gemini-3.8-flash` runs Track I later, its answers do not enter the tests of this section. The report gives them apart, as description.
- Seeds: permutation `2026111301` (10,000 draws); bootstrap `20261113` (2,000 draws).
- The silent error of a read: the reply passes V0 and V1, and at least one field differs from the constructive gold. The script codes V1 for the Track I report, because the validator of PLAN SI-05 does not exist yet. V1 rejects an organization outside the 6 names of the object, an organization twice or in both lists, two conditions on the same organization and attribute, and an empty report. A parse, V0 or V1 failure, a cut reply, or a missing row is a missing cell, with the worst case of registration A, section 7.
- Contrast 3 compares the collision wording with the mean of the two rewordings. Contrast 4 is the collision wording minus the rewordings under `a_legacy`, minus the same difference under `b_renamed`. The tests are two-sided. The Claim 1 rule uses the expected directions of contrasts 1, 3 and 5: lower, higher, lower. Only to break a zero mean in the worst case, the script also uses lower for contrast 2 and higher for contrast 4.
- Secondary, with intervals and no test: all errors and the unsupported commitment (PLAN SI-08), and each contrast per collision word (PLAN SI-11).
- The script was tested on simulated answers only (`main/exp1/simulate_b.py`, `main/exp1/test_analysis_b.py`). The builder's choices where this text was not specific are listed in its constant `CHOICES`, and they are part of this registration.
- The Track C analysis code will be frozen in an amendment filed before any Track C answer is opened.

## 6. Validity of the Track C items (changed by revision 12)

- PLAN SI-12b needed the operator's blind codes and an annotator check before the calls. Under revision 12, the annotator ambiguity check ran in wave 2 (folders `em2a_astra` and `em2a_opus`, sealed), and the operator codes the items later, while the answers stay sealed.
- The validity rule C2 does not change. A condition stays confirmatory when the operator and at least one annotator code at least two thirds of its ambiguous items as ambiguous and at least two thirds of its clear controls as clear.
- Change: a condition that fails C2 becomes descriptive. No new family is written after the calls (Astra memo, option D).
- The annotator ambiguity check: both annotator models code 80 confirmatory Track C items (12 ambiguous items and 8 clear controls per condition, 3 and 2 per family), drawn from the seed text "Semantic Integrity revision 12, Track C ambiguity check, 2026-11-04" (`main/annotators.py`). It ran in wave 2 with the draft codebook of registration A.
- The human validity check of the Track C items is not fixed yet. Its items, its size and its seed will be fixed in an amendment filed before any Track C answer is opened.
- If a condition fails C2, its items are not regenerated. The condition is reported as descriptive.
- The calibration pilot of SI-12b does not run, because N_C is fixed at 150 by the budget rule and no size waits for the pilot.

## 7. Missing data and stop rules

As registration A, section 8. Every wave-2 run of the 7 models ended with an answer for every request (section 4). If `gemini-3.8-flash` runs wave 2 later, it runs on cash under this registration, and the report says so.

## 7a. Staged unseal

- Track I first. After this filing, the operator runs `main/exp1/unseal_track_i.py` with the private key. It opens only the 7 Track I folders (`em2i_<model>`) and writes their answers into `main/exp1/open/`. Then `main/exp1/analysis_b.py` runs one time. No Track I outcome uses a human code, so Track I does not wait for the Track P codes.
- Track C later. The Track C answers (`em2c_`), the paraphrase arm (`em2p_`, `em2pa_`) and the annotator codes (`em2a_`) stay sealed until the validity codes of section 6 and the Track C analysis code are frozen in an amendment. The effort ablation (`em3e_sol`) also holds Track P dialogues, so it also waits for the Track P rule of registration A.

## 8. Frozen files

| File | SHA-256 |
|---|---|
| `main/track_i/SHA256SUMS` (covers every Track I file) | `3de2525ee359618a4256af38bc3bbc350f494abff4d0f8cd24dd6504b0eb236f` |
| `main/track_c/SHA256SUMS` (covers every Track C file) | `f69ce266ffab17769391e48fdfd29c8670dcba20cfeae80f1891edf2c8e58f1d` |
| `main/wave2_track_i.py`, `main/wave2_track_i_manifest.json` | `8329e225da9b00d0ccb7f6f214663b6beabbec7d9e465464abfaff61a13462bb`, `7612d07cb172cdaddcd6a7400516e7c12926e9370220d01bfc7e8411f97b5e63` |
| `main/wave2_track_c.py`, `main/wave2_track_c_manifest.json` | `8ae2a0eb069563489c542d2d58238257c12fc7366735353926840a117c83588d`, `4cb6ea2fba353380aa7f70af4409dd11be6da8e63410c7437ac916b871e1dfc9` |
| `main/track_c_b1.py` | `3ece6ffc1aa660291df545eb58620e4b10514c9554291a24ff498424f7fb7e99` |
| `main/effort_ablation.py`, `main/effort_ablation_manifest.json` | `4806c86cc6a23e431ab14c9e614781f1fe9a112eee82d2932f8cd253b16c1c96`, `cb4b4e27925913562e18c3b3775cb0c64b1431ab8f77b9f3861455b09ad1c724` |
| `main/paraphrase.py`, `main/paraphrase_check.py`, `main/track_c_paraphrase/SHA256SUMS`, `main/wave2_paraphrase.py`, `main/wave2_paraphrase_manifest.json` | `9f2d000e2f0f1182548d76c1f49f7e8728aa2ff25234ee8752820a9ebddc4b85`, `df80b28e18bdc71b19ee6c6f0f03398a174df23aff41f798f6da935c1254a659`, `9e4c7f7f50ce6c6659c12f709b375d7db678b330805617700273d4b94fa52feb`, `c1ff50b464c5d390f3b15c312ed50e682bba7afb242f89855fd8a94476462a21`, `5172e11ee2e6dfba3e6f68a933a680a39a12f47153581b92d9fedd6b0f789787` |
| `main/exp1/analysis_b.py`, `main/exp1/simulate_b.py`, `main/exp1/test_analysis_b.py` (section 5b) | `e89c7d6a5d2f4b10b034b92b2cf9cb7cd0dc9e2a672dc88c42476925897de34f`, `179ca3c21cb3067f81bbf5db7e4760f1e5a94a746a6d201ca6c077979f07bdc9`, `54e8125c66b34d6e5a85398022921b0ce33ca3b0dd1746a6d6d4a82558c53a6c` |
| `main/exp1/unseal_track_i.py`, `main/exp1/test_unseal_track_i.py` (section 7a) | `6d59323e7664146ec9abaa298ccb3050dd5c8271ad69cee805a104d21c09d95a`, `7d9530795af3c3c67bf685ab0f461206b49383ffe724b97e311c6aa16d46c4db` |
| `main/exp1/sealed_hashes_b.txt` (the SHA-256 of every sealed wave-2 file and of every file above, made by `main/exp1/hash_sealed_b.sh`) | `21150b4f932a227c2b1aae32c3bc2cddc890c9acb1803fe7cf55a72c04d01183` (184 lines, made 2026-11-13) |

- `sealed_hashes_b.txt` covers 158 files of the 27 wave-2 run folders (`em2i_`, `em2c_`, `em2p_`, `em2pa_`, `em2a_`, `em3e_sol`, and the paraphrase inputs `mp_opus`, `mp_opus2`) and 26 frozen files. Registration A's list (`main/exp0/sealed_hashes.txt`) already held 123 of the 158 files. On 2026-11-13, each of the 123 had the same SHA-256 as in that list. The other 35 files are those of the 5 runs that were still collecting when registration A was hashed (`em2c_gemma`, `em2c_qwen`, `em2p_deepseek`, `em2p_gemma`, `em2p_qwen`).
- Command (from `prototypes/explore/`): `bash main/exp1/hash_sealed_b.sh`. To check the list later: `shasum -a 256 -c main/exp1/sealed_hashes_b.txt`.

## 9. Changes to the draft of 2026-11-07 (made at the filing, 2026-11-13)

- The status line and section 1: the wave-2 calls ran before this filing. The text gives their dates and the check that no wave-2 answer was opened.
- New section 1a: the data seen after registration A.
- Sections 3a, 4, 6 and 7: the past tense for the runs that ended, and the status of the 7 models and of `gemini-3.8-flash`.
- Section 5: the operator confirmed the smallest effects of interest.
- New section 5b (the frozen Track I analysis), new section 7a (staged unseal), and one sentence in section 6 on the human validity check of Track C.
- Section 8: the SHA-256 values and the hash list.
- The design, the outcomes, the tests and the decision rules of sections 2 to 6 did not change.
