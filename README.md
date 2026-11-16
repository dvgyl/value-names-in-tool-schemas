# How an Everyday Word in a Tool Schema Changes AI Agents' Searches While Every Call Stays Valid

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24270645.svg)](https://doi.org/10.5281/zenodo.24270645)

Code, data and results for the preprint by Dev D. Goyal (Independent Researcher), 2026. Archived on Zenodo: https://doi.org/10.5281/zenodo.24270645.

- The preprint: `paper/preprint.pdf`.
- Registration A, filed 2026-11-12: https://osf.io/bv8q9
- Registration B, filed 2026-11-13: https://osf.io/jy3pd

A *registration* is a public plan with a date and a time. We filed the plan of the main test before we opened its answers. Thus, the plan could not follow the results.

## 1. What the study asks

An AI agent uses *tools*. For example, a booking agent calls a search tool to find hotels for a traveller. Each tool has a *schema*: a list of its fields and, for some fields, a closed list of allowed values.

Some allowed values are also everyday words. A traveller writes:

> "I need a cheap hotel in the north of town."

In everyday English, "hotel" often means any place to stay. The search tool has a field `type` with two allowed values, `hotel` and `guesthouse`. The agent sends this search:

```
search_hotels(area = ["north"], pricerange = ["cheap"], type = ["hotel"])
```

The tool accepts the call, because each value is an allowed value. But in the venue data of the corpus, no hotel is cheap and in the north, and two guesthouses are. Thus, the search finds nothing. If the traveller meant "any place to stay", the filter hid the two places that fit.

The preprint has three parts:

1. **The registered test, and searches that exclude what the brief allows.** Does the name of a value change what the agent searches for, while every call stays valid?
2. **A release test for schema updates.** Can a test before release find a schema update that changes the searches?
3. **Neural and symbolic repairs.** How do we measure a repair that must make the values match what the traveller asked for?

We used booking dialogues of the public corpus MultiWOZ 2.4. Each dialogue has a recorded goal of the traveller (the *brief*), which the model did not see. Two results:

- In a test registered before we opened the answers, seven models completed a search form. We renamed the field and the value (`type: hotel` to `property_kind: large_property`). Where the brief did not need a hotel, the share of hotel values fell by 13.0 percentage points, from 17.3%. Where the first or the final choice of the brief was a hotel, the share fell by 29.1 points, from 62.3%. Every finished answer fitted the schema.
- On 213 held-out dialogues whose brief sets no type, 5.6% to 18.8% of the valid answers of seven models at the traveller's first "hotel" would have searched only hotels and excluded every venue that fits the brief.

The preprint gives all results, the exploratory studies and their limits. Each analysis is *registered* (planned and filed before we opened the answers) or *exploratory*. A *post hoc* analysis is an exploratory analysis that we chose after we saw results.

## 2. What is in this repository

| Folder or file | What it holds |
|---|---|
| `README.md` | This text. |
| `paper/` | The preprint (PDF). |
| `reproduce.py` | One command that reruns the analyses and compares each output with the stored result file (section 3). |
| `analyses.json` | The list of the analyses: the part of the preprint, the commands, the outputs and the comparison rules. `reproduce.py` reads it. |
| `explore/` | The study folder: code, texts, answer data, results and the protocol. Every script runs from this folder. |
| `explore/r10/analysis/` | The analysis scripts of round 10, the main round of the exploratory studies, and the post hoc scripts. |
| `explore/r10/analysis/out/` | The result files (Markdown and JSON) and the data of the figures (CSV). |
| `explore/r10/` | The code that built the requests of round 10: tool texts, repair texts, word pairs, run definitions, the code of the protocol amendments, and the unit tests (`tests/`). |
| `explore/posthoc/` | The post hoc analyses of the last revisions, with their outputs (`out/`): the simulation of the release rules (`release-sim/`), the fresh release test (`release-fresh/`), checks of the release rule (`checks/release-rule/`) and checks of the repairs (`checks/repair-display/`, `checks/repair-counts/`). Some of these folders hold the specification of a check (`SPEC-*.md`), which we wrote before the check ran. |
| `explore/r9/` | Round 9: request builders, forms, predictions (`PREDICTIONS.md`) and analysis scripts. |
| `explore/lib/`, `forms/`, `pmain/`, `sonnet/`, `onsite/`, `annot/`, `trackc/` | Shared code, and code of earlier rounds that the later code imports. |
| `explore/main/` | The registered tests. Registration A: the request builder (`wave1.py`), its dialogue lists, the frozen analysis (`exp0/analysis.py`), the aggregated results (`exp0/RESULT-STAGE1.md`, `exp0/stage1.json`) and the registration as filed (`exp0/registration/`). Registration B, test on constructed texts: the frozen analysis (`exp1/analysis_b.py`), the aggregated results (`exp1/RESULT-TRACK-I.md`, `exp1/track_i.json`) and the registration as filed (`exp1/registration/`). |
| `explore/PROTOCOL.md` | The study protocol, with the date and the time of each part (section 7). |
| `explore/<run>/raw.jsonl.gz` | The answers of one run of the exploratory studies, one row for each answer (section 6). |
| `explore/smoke_test.py`, `explore/smoke_test_expected.json` | The smoke test and its expected values (section 3, step 3). |
| `explore/answer_tables.py`, `explore/verify_requests.py`, `explore/export_examples.py` | The scripts that write the scored tables, check the requests, and write the request examples. |
| `explore/logs/analysis/` | The printed results of the analyses that print their results. |
| `explore/reference/` | A reference count that one analysis reads (`harm_by_model.out`), and the scripts that write it. |
| `annotation/` | The author's blind check of the word rule: the items as the labeller saw them, the analysis script and the report. The labels and the key are not here (section 8). |
| `tables/` | Scored answer tables, one row for each answer (gzip CSV; section 6). |
| `examples/` | Requests as the runs sent them, with their answers (section 7). |
| `LICENSE`, `LICENSE-CC-BY-4.0.md` | The licenses (section 10). |
| `CITATION.cff`, `.zenodo.json` | Citation data (section 11). |

The repository holds 138 run folders with 684,162 answer rows. It does not hold the corpus. It does not hold the answers of the registered tests, and it does not hold the private labels of the author's blind checks (section 8).

## 3. How to reproduce

### Step 1: Python

Use Python 3.14. We tested with Python 3.14.6. The analyses use only the Python standard library. No analysis makes a model call or a network call.

Use the flag `-I` (isolated mode) in every command, as below. The scripts set their own import paths.

### Step 2: the public corpus

The study uses MultiWOZ 2.4 (Ye, Manotumruksa and Yilmaz, SIGDIAL 2022), a public corpus of written booking dialogues. Its repository states the MIT License. This repository does not include the corpus.

- Source: https://github.com/smartyfh/MultiWOZ2.4, file `data/MULTIWOZ2.4.zip`.
- The file that the study used: 13,790,771 bytes, SHA-256 `d4c66523614af016c1d2dafa35b4a548c96cb9ffadb71338937b60ac51272fe5`.

Do these steps in the repository folder:

```
curl -L -o MULTIWOZ2.4.zip https://github.com/smartyfh/MultiWOZ2.4/raw/main/data/MULTIWOZ2.4.zip
shasum -a 256 MULTIWOZ2.4.zip
unzip MULTIWOZ2.4.zip -d corpus/
```

Make sure that the checksum is the same as the checksum above. After the last step, the file `corpus/MULTIWOZ2.4/data.json` must exist.

### Step 3: the smoke test

Do the smoke test first:

```
python3 -I reproduce.py --smoke
```

The smoke test takes about 10 seconds. It unpacks the answer rows of one run (`era1_haiku`: Haiku with the original tool at the first request). It scores the answers with the code of the analysis, and it compares five values with the expected values in `explore/smoke_test_expected.json`. Two values are the hotel-filter share (8.3%) and the exclusion share (3.1%) of `explore/r10/analysis/out/a.md`. The other three values come from the full-schema check (`tool_validity.md`). The smoke test needs the corpus. It needs no key and no network, and it writes no file. The last line must be:

```
smoke test: 5 of 5 values as expected
```

### Step 4: rerun the analyses

```
python3 -I reproduce.py
```

This command:

1. unpacks the answer rows (`explore/<run>/raw.jsonl.gz` to `raw.jsonl`),
2. runs each analysis of section 4 that can run here,
3. compares each output with the stored result file, byte for byte.

On our computer, it took about 20 minutes. The last line tells how many analyses gave the stored results. When an output differs, the new file stays in its place, so `git diff` shows the difference.

Other forms of the command:

```
python3 -I reproduce.py --list          list the analyses
python3 -I reproduce.py a h i           run only the analyses a, h and i
python3 -I reproduce.py --checks        also run the checks of section 5
python3 -I reproduce.py --slow          also run the slow simulation steps (about 20 minutes)
python3 -I reproduce.py --unpack        only unpack the answer rows
```

You can also run one script yourself. Unpack the answer rows first, then run the script from `explore/`:

```
python3 -I reproduce.py --unpack
cd explore
python3 -I r10/analysis/a_analyze.py
```

### Step 5: read the results

The result files are plain Markdown and JSON. Start with `explore/main/exp0/RESULT-STAGE1.md` (the registered test) and `explore/r10/analysis/out/a.md` (tool calls at the first request).

## 4. Map of the analyses

Each row is one analysis. "Name" is its name in `reproduce.py` and `analyses.json`. Run each script from `explore/` with `python3 -I`. The outputs are in `explore/r10/analysis/out/`, unless the row gives another folder. The column "Runs here" tells whether the analysis can run from this repository. Of the 95 analyses, 80 run with the default command, 3 run with `--slow`, 4 need the held-out answers, 6 read files that are not here, 1 needs the private labels, and 1 has no script.

### Part 1: the registered test, and searches that exclude what the brief allows

| Name | What it shows | Status | Script (from `explore/`) | Outputs | Runs here |
|---|---|---|---|---|---|
| `exp0` | The registered test on held-out dialogues (registration A, stage 1) | registered | `main/exp0/analysis.py <folder of held-out answers>` | `main/exp0/RESULT-STAGE1.md`, `main/exp0/stage1.json` | no: held-out answers |
| `clear_split` | Registered test: clear and unclear requests | exploratory, post hoc | `r10/analysis/clear_split.py` | `clear_split.json`, `clear_split.md` | no: held-out answers |
| `r2_posthoc` | Registered test: random deletion, word or meaning, visibility | exploratory, post hoc | `r10/analysis/r2_posthoc.py` | `r2_posthoc.json`, `r2_posthoc.md` | no: held-out answers |
| `heldout_fitref_bound` | Registered test: bound of the fit reference on held-out dialogues | exploratory, post hoc | `r10/analysis/heldout_fitref_bound.py` | `heldout_fitref_bound.json`, `heldout_fitref_bound.md` | yes |
| `loyal_stored_counts` | Registered tests: stored validity counts and the types of the 77 hotel-sample dialogues | exploratory, post hoc | `r10/analysis/loyal_stored_counts.py` | `loyal_stored_counts.json`, `loyal_stored_counts.md` | yes |
| `loyal_tracki_tables` | Registered test on constructed texts (registration B): tables from the aggregated output | exploratory, post hoc | `r10/analysis/loyal_tracki_tables.py` | `loyal_tracki_tables.json`, `loyal_tracki_tables.md` | yes |
| `loyal_heldout_phrase` | Registered test: the phrase rule on held-out first requests | exploratory, post hoc | `r10/analysis/loyal_heldout_phrase.py` | `loyal_heldout_phrase.json`, `loyal_heldout_phrase.md` | yes |
| `a` | Tool calls at the first request (experiment A) | exploratory | `r10/analysis/a_analyze.py` | `a.json`, `a.md`, `fig_funnel.csv` | yes |
| `tool_validity` | Full-schema check of the tool calls | exploratory, post hoc | `r10/analysis/tool_validity.py` | `tool_validity.json`, `tool_validity.md` | yes |
| `tool_types` | The type values of the tool calls | exploratory | `r10/analysis/tool_types.py` | `tool_types.json`, `tool_types.md` | yes |
| `tool_ratio` | Trade of the tool calls (renamed tool) | exploratory | `r10/analysis/tool_ratio.py` | `tool_ratio.json`, `tool_ratio.md` | yes |
| `tool_by_brief` | Tool calls by brief type | exploratory | none | `tool_by_brief.json` | no (no script) |
| `loyal_first_request` | Exclusions at the first request in which the call without its type finds a venue | exploratory, post hoc | `r10/analysis/loyal_first_request.py` | `loyal_first_request.json`, `loyal_first_request.md` | yes |
| `loyal_tool_classes` | Scorable and valid tool calls, the ask share, the second-step trials | exploratory, post hoc | `r10/analysis/loyal_tool_classes.py` | `loyal_tool_classes.json`, `loyal_tool_classes.md` | yes |
| `loyal_validity_pairs` | Paired no-call transitions; second-step classes with invalid calls as missing | exploratory, post hoc | `r10/analysis/loyal_validity_pairs.py` | `loyal_validity_pairs.json`, `loyal_validity_pairs.md` | yes |
| `loyal_unchecked_runs` | Full-schema check of the other tool-call runs | exploratory, post hoc | `r10/analysis/loyal_unchecked_runs.py` | `loyal_unchecked_runs.json`, `loyal_unchecked_runs.md` | no: files not here |
| `loyal_booked_sets` | The booked venues of the dialogues | exploratory, post hoc | `r10/analysis/loyal_booked_sets.py` | `loyal_booked_sets.json` | yes |
| `loyal_cp_bounds` | Exact binomial bounds of small counts | exploratory, post hoc | `r10/analysis/loyal_cp_bounds.py` | printed text, stored in `logs/analysis/loyal_cp_bounds.log` | yes |
| `loyal_hostel_check` | Venue names with the word hostel | exploratory, post hoc | `r10/analysis/loyal_hostel_check.py` | printed text, stored in `logs/analysis/loyal_hostel_check.log` | yes |
| `loyal_values_a` | Values copied from check reports (a) | exploratory, post hoc | `r10/analysis/loyal_values_a.py compute` | `loyal_values_a.json`, `loyal_values_a.md` | no: files not here |
| `loyal_values_b` | Values copied from check reports (b) | exploratory, post hoc | `r10/analysis/loyal_values_b.py compute` | `loyal_values_b.json`, `loyal_values_b.md` | no: files not here |
| `loyal_values_c` | Values copied from check reports (c) | exploratory, post hoc | `r10/analysis/loyal_values_c.py compute` | `loyal_values_c.json`, `loyal_values_c.md` | no: files not here |
| `fitref_sensitivity` | Other readings of the fit reference | exploratory, post hoc | `r10/analysis/fitref_sensitivity.py` | `fitref_sensitivity.json`, `fitref_sensitivity.md` | yes |
| `human` | The people in the corpus | exploratory | `r10/analysis/human_baseline.py` | `human.json`, `human.md` | yes |
| `step2_links` | The second step after a hotel-only search | exploratory | `r10/analysis/step2_links.py` | `step2_links.json`, `step2_links.md` | yes |
| `turns` | Later turns with a simulated traveller (experiment T) | exploratory | `r10/analysis/turns_analyze.py` | `turns.json`, `turns.md` | yes |
| `turns_paired` | Later turns, paired | exploratory | `r10/analysis/turns_paired.py` | `turns_paired.json`, `turns_paired.md` | yes |
| `turns_failinfo` | Later turns and the failure information | exploratory | `r10/analysis/turns_failinfo.py` | `turns_failinfo.json`, `turns_failinfo.md` | yes |
| `loyal_final_recommendations` | Later turns: the final recommendation | exploratory, post hoc | `r10/analysis/loyal_final_recommendations.py` | `loyal_final_recommendations.json`, `loyal_final_recommendations.md` | yes |
| `r9_natural` | Round 9: renamed and other forms on full dialogues | exploratory | `r9/natural/natural_analyze.py` | printed text, stored in `logs/analysis/r9_natural_final.log` | yes |
| `r9_tradeoff` | Round 9: the trade of the forms | exploratory | `r9/natural/tradeoff.py logs/analysis/r9_natural_final.log` | printed text, stored in `logs/analysis/r9_tradeoff_final.log` | yes |
| `r9_z` | Round 9: text edits and instruction changes | exploratory | `r9/additions/zanalyze.py` with 17 run names and 2 options (note 1) | `r9/additions/out/summary.json`, printed text, stored in `logs/analysis/r9_z_final.log` | yes |
| `i` | The word "hotel" put into the traveller's turns (experiment I) | exploratory | `r10/analysis/i_analyze.py` | `i.json`, `i.md` | yes |
| `efg` | More models and a high reasoning setting (experiments E, F, G) | exploratory | `r10/analysis/efg_analyze.py` | `efg.json`, `efg.md`, `fig_effort.csv` | yes |
| `h` | Twelve other service words (experiment H) | exploratory | `r10/analysis/h_analyze.py` | `h.json`, `h.md`, `fig_pairs.csv` | yes |
| `clear_rule` | The word rule for clear requests | exploratory | `r10/analysis/clear_rule.py` | `clear_rule.md` | yes |
| `label_test` | Label test: one definition under the labels hotel and category_A (R10-18) | exploratory | `r10/analysis/label_test.py` | `label_test.json`, `label_test.md` | yes |
| `label_test2` | Label test: a third label, serviced_property (R10-19) | exploratory | `r10/analysis/label_test2.py` | `label_test2.json`, `label_test2.md` | yes |
| `label_test3` | Label test with tool calls (R10-21) | exploratory | `r10/analysis/label_test3.py` | `label_test3.json`, `label_test3.md` | yes |
| `steer` | Tool texts that a model rewrote to steer the agents (experiment S) | exploratory | `r10/analysis/steer_analyze.py` | `steer.json`, `steer.md` | yes |
| `steer_quote` | What the steering rewrites say | exploratory | `r10/analysis/steer_quote.py` | `steer_quote.json`, `steer_quote.md` | yes |
| `steer_words` | The words of the steering rewrites | exploratory | `r10/analysis/steer_words.py` | `steer_words.json`, `steer_words.md` | yes |
| `steer_search` | The steered searches | exploratory | `r10/analysis/steer_search.py` | `steer_search.json`, `steer_search.md` | yes |
| `steer2` | Three service rewrites for each interest, on Haiku (experiment M) | exploratory | `r10/analysis/steer2_analyze.py` | `steer2.json`, `steer2.md` | yes |
| `steer_search3` | Steering when the agent can search again (R10-23) | exploratory | `r10/analysis/steer_search3.py` | `steer_search3.json`, `steer_search3.md` | yes |
| `harm_by_model` | Reference rates that analysis i reads | exploratory | `reference/harm_by_model.py` | printed text, stored in `reference/harm_by_model.out` | yes |
| `annotation` | The author's blind checks: the word rule, the agents' replies and the model's readings | exploratory | `annotation/analyze_labels.py --local --out annotation/labels_report.md` (from the repository folder) | `annotation/labels_report.md` | no: private labels |

### Part 2: a release test for schema updates

| Name | What it shows | Status | Script (from `explore/`) | Outputs | Runs here |
|---|---|---|---|---|---|
| `release` | Prospective release test of rewrite N1 (experiment R) | exploratory, prospective | `r10/analysis/release_analyze.py` | `release.json`, `release.md` | yes |
| `release_sensitivity` | Rewrite N1: sensitivity | exploratory | `r10/analysis/release_sensitivity.py` | `release_sensitivity.json`, `release_sensitivity.md` | yes |
| `release_values` | Rewrite N1: the values | exploratory | `r10/analysis/release_values.py` | `release_values.json`, `release_values.md` | yes |
| `steer_sensitivity` | Release test of the steering rewrites: sensitivity | exploratory | `r10/analysis/steer_sensitivity.py` | `steer_sensitivity.json`, `steer_sensitivity.md` | yes |
| `control` | Two control updates (experiment C) | exploratory | `r10/analysis/control_analyze.py` | `control.json`, `control.md` | yes |
| `control_spread` | Two control updates: spread | exploratory | `r10/analysis/control_spread.py` | `control_spread.json`, `control_spread.md` | yes |
| `release_test` | Release tests of harmless updates (R10-20) | exploratory | `r10/analysis/release_test.py` | `release_test.json`, `release_test.md` | yes |
| `release_test2` | Release tests: field order and a second paraphrase (R10-22) | exploratory | `r10/analysis/release_test2.py` | `release_test2.json`, `release_test2.md` | yes |
| `release_test3` | Replication of the two paraphrase flags (R10-24) | exploratory | `r10/analysis/release_test3.py` | `release_test3.json`, `release_test3.md` | yes |
| `rtest_c1` | Release test: per-request changes and the sign test | exploratory, post hoc | `r10/analysis/rtest_c1.py` | `rtest_c1.json`, `rtest_c1.md`, `rtest_check_values.json` | yes |
| `rtest_levels` | Release test: the levels of the intervals | exploratory, post hoc | `r10/analysis/rtest_levels.py` | `rtest_levels.json`, `rtest_levels.md` | yes |
| `rtest_symmetric` | Release test: every decision with a symmetric interval index | exploratory, post hoc | `r10/analysis/rtest_symmetric.py` | `rtest_symmetric.json`, `rtest_symmetric.md` | yes |
| `rtest_final9` | Release test: the final rule | exploratory, post hoc | `r10/analysis/rtest_final9.py` | `rtest_final9.json`, `rtest_final9.md` | yes |
| `rtest_validity` | Registered tests: first answers that fit the closed schema | exploratory, post hoc | `r10/analysis/rtest_validity.py` | `rtest_validity.json`, `rtest_validity.md` | yes |
| `sim_fit` | Simulation of the release rules (R10-26): fit of the base distributions | exploratory, post hoc | `posthoc/release-sim/stored.py fit` | `posthoc/release-sim/out/fit.json`, `posthoc/release-sim/out/fit.md` | yes |
| `sim_fidelity` | Simulation of the release rules: the rule code on the stored comparisons | exploratory, post hoc | `posthoc/release-sim/stored.py fidelity` | `posthoc/release-sim/out/fidelity.json`, `posthoc/release-sim/out/fidelity.md` | no: files not here |
| `sim_run` | Simulation of the release rules: every configuration (126 x 2,000 trials) | exploratory, post hoc | `posthoc/release-sim/sim.py run --workers 7` | `posthoc/release-sim/out/sim.json`, `posthoc/release-sim/out/sim.md` | yes, with `--slow` |
| `sim_tails` | Simulation of the release rules: the stored comparisons with other seeds and 20,000 draws | exploratory, post hoc | `posthoc/release-sim/stored.py tails` | `posthoc/release-sim/out/tails_stored.json`, `posthoc/release-sim/out/tails_stored.md` | yes, with `--slow` |
| `sim_tables` | Simulation of the release rules: compact tables | exploratory, post hoc | `posthoc/release-sim/report_tables.py` | `posthoc/release-sim/out/report_tables.md` | yes |
| `fresh_test` | Fresh release test of the final rule (R10-27), and its bootstrap sensitivity | exploratory, post hoc | `posthoc/release-fresh/analyze.py`; then `posthoc/release-fresh/sensitivity.py` | `posthoc/release-fresh/out/result.json`, `posthoc/release-fresh/out/result.md`, `posthoc/release-fresh/out/sensitivity.json`, `posthoc/release-fresh/out/sensitivity.md` | yes |
| `rule_compare` | Release rules compared on the same simulated data (T1) | exploratory, post hoc | `posthoc/checks/release-rule/t1_compare.py`; then `posthoc/checks/release-rule/t1_derived.py` | `posthoc/checks/release-rule/out/t1_compare.json`, `posthoc/checks/release-rule/out/t1_compare.md`, `posthoc/checks/release-rule/out/t1_derived.json`, `posthoc/checks/release-rule/out/t1_derived.md` | yes |
| `sign_floor` | The floor of the sign condition (T2) | exploratory, post hoc | `posthoc/checks/release-rule/t2_signfloor.py` | `posthoc/checks/release-rule/out/t2_signfloor.json`, `posthoc/checks/release-rule/out/t2_signfloor.md` | yes |
| `boot_collect` | Bootstrap precision (T3), step 1: the paired differences of every release decision | exploratory, post hoc | `posthoc/checks/release-rule/t3_collect.py stored`; then `posthoc/checks/release-rule/t3_collect.py fresh`; then `posthoc/checks/release-rule/t3_collect.py replication`; then `posthoc/checks/release-rule/t3_collect.py merge` | `posthoc/checks/release-rule/out/t3_diffs_stored.json`, `posthoc/checks/release-rule/out/t3_diffs_fresh.json`, `posthoc/checks/release-rule/out/t3_diffs_replication.json`, `posthoc/checks/release-rule/out/t3_diffs.json` | yes |
| `boot_precision` | Bootstrap precision (T3), step 2: 100,000 draws and 5 seeds | exploratory, post hoc | `posthoc/checks/release-rule/t3_boot.py` | `posthoc/checks/release-rule/out/t3_bootstrap.json`, `posthoc/checks/release-rule/out/t3_bootstrap.md` | yes, with `--slow` |
| `rule_tables` | The tables of the rule comparison and the bootstrap precision | exploratory, post hoc | `posthoc/checks/release-rule/paper/gen_tables.py` | `posthoc/checks/release-rule/paper/tables.md`, `posthoc/checks/release-rule/paper/numbers.json` | yes |

### Part 3: neural and symbolic repairs

| Name | What it shows | Status | Script (from `explore/`) | Outputs | Runs here |
|---|---|---|---|---|---|
| `b` | Four repairs and the verifier (experiment B) | exploratory | `r10/analysis/b_analyze.py` | `b.json`, `b.md`, `fig_trade.csv` | yes |
| `b_hotel_only` | Repairs: hotel-only count | exploratory | `r10/analysis/b_analyze.py --hotel-only` | `b_hotel_only.json`, `b_hotel_only.md`, `fig_trade_hotel_only.csv` | yes |
| `b_brief` | Repairs: dialogues where the brief agrees with the label | exploratory | `r10/analysis/b_analyze.py --brief-groups` | `b_brief.json`, `b_brief.md`, `fig_trade_brief.csv` | yes |
| `search_side` | Counting what the traveller sees | exploratory | `r10/analysis/search_side.py` | `search_side.json`, `search_side.md` | yes |
| `search_sym` | The repairs on the search | exploratory | `r10/analysis/search_sym.py` | `search_sym.json`, `search_sym.md` | yes |
| `search_transitions` | The repairs on the search: transitions | exploratory | `r10/analysis/search_transitions.py` | `search_transitions.json`, `search_transitions.md` | yes |
| `trade_prospective` | The search measure, fixed in advance, on three open models (experiment Y) | exploratory, prospective | `r10/analysis/trade_prospective.py` | `trade_prospective.json`, `trade_prospective.md` | yes |
| `sol_astra` | Sol and Astra answer alike | exploratory, post hoc | `r10/analysis/sol_astra_agreement.py` | `sol_astra_agreement.json`, `sol_astra_agreement.md` | yes |
| `repair_refs` | Repairs: references and display results | exploratory, post hoc | `r10/analysis/repair_refs.py` | `repair_refs.json` | yes |
| `repair_rule` | Repairs: the trade rule against the brief and the word rule | exploratory, post hoc | `r10/analysis/repair_rule.py` | `repair_rule.json` | yes |
| `repair_limits` | Repairs: limits of the comparisons | exploratory, post hoc | `r10/analysis/repair_limits.py` | `repair_limits.json`, `repair_rename_check.json` | yes |
| `heldout_confirm` | Held-out confirmation of the repair results (R10-25) | exploratory | `r10/analysis/heldout_confirm.py` | `heldout_confirm.json`, `heldout_confirm.md` | no: held-out answers |
| `flag` | The returned note and the one-search text (experiment W) | exploratory | `r10/analysis/flag_analyze.py` | `flag.json`, `flag.md` | yes |
| `flag_read1` | The returned note: first answers only | exploratory | `r10/analysis/flag_analyze.py --read1` | `flag_read1.json`, `flag_read1.md` | yes |
| `flag_audit` | The returned note: reading of the answers | exploratory | `r10/analysis/flag_audit.py` | `flag_audit.json`, `flag_audit_numbers.md`, `flag_audit.md`, `flag_audit_labels.tsv` | yes |
| `flag2` | The returned note with travellers who need a hotel (experiment U) | exploratory | `r10/analysis/flag2_analyze.py` | `flag2.json`, `flag2.md` | yes |
| `heldout_display` | Held-out display outcomes from the stored aggregate result (N1) | exploratory, post hoc | `posthoc/checks/repair-display/n1_heldout_stored.py` | `posthoc/checks/repair-display/out/n1_heldout_stored.json` | yes |
| `gated_soft` | A verifier-gated soft type filter on the development dialogues (N2) | exploratory, post hoc | `posthoc/checks/repair-display/n2_gated_soft.py`; then `posthoc/checks/repair-display/n2_added_types_check.py` | `posthoc/checks/repair-display/out/n2_gated_soft.json`, `posthoc/checks/repair-display/out/n2_added_types_check.json` | yes |
| `d3_check` | The guesthouse group of the verifier table (N3) | exploratory, post hoc | `posthoc/checks/repair-display/n3_d3_check.py` | `posthoc/checks/repair-display/out/n3_d3_check.json` | no: files not here |
| `display_values` | The numbers of the display checks, as printed | exploratory, post hoc | `posthoc/checks/repair-display/make_paper_values.py`; then `posthoc/checks/repair-display/make_review_values.py` | `posthoc/checks/repair-display/out/paper_values.json`, `posthoc/checks/repair-display/out/review_values.json` | yes |
| `display_counts` | Displays of the policies on stated hotel briefs, base rates and raw trade values | exploratory, post hoc | `posthoc/checks/repair-counts/plan_counts.py` | `posthoc/checks/repair-counts/out/plan_counts.json` | yes |
| `display_bounds` | Bounds from stored results: the goal-hotel mean and zero losses | exploratory, post hoc | `posthoc/checks/repair-counts/plan_bounds.py` | `posthoc/checks/repair-counts/out/plan_bounds.json` | yes |
| `strict_check` | Can a call that does not fit the schema enter the returned-note experiment? | exploratory, post hoc | `posthoc/checks/repair-counts/strict_check.py` | `posthoc/checks/repair-counts/out/strict_check.json` | yes |

Note 1. The full command of `r9_z`: `python3 -I r9/additions/zanalyze.py ez1_claude ez1_luna ez2_claude ez2_luna ez3_haiku ez3_sonnet ez3_luna eb2_sol eb2_open eb3_sol eb3_open eb4_sol eb4_open e13 ex2n_di ex2n_sol ex2n_luna --alias f0=orig_f0 --alias f1=orig_f1`.

Notes:

- **Registered test.** Some scripts need the answers of the registered test. These answers stay encrypted (section 8), so these scripts cannot run here. Their stored outputs are the results of one run on the opened answers of stage 1. To see the frozen analysis work, run `main/exp0/test_analysis.py` (section 5): it runs the analysis on simulated answers.
- **Frozen files.** Registration A fixes the SHA-256 of these files, and they are byte-identical here: `main/wave1.py`, `main/wave1_ids.json`, `main/wave1_manifest.json`, `lib/seal.py`, `main/exp0/analysis.py`, `r10/briefsearch.py` and `r10/analysis/stats.py`. To compare, run `shasum -a 256` on them from `explore/`, and read section 11 of `main/exp0/registration/REGISTRATION-A.md` and amendment A1.
- **`tool_by_brief.json`.** It holds the tool calls by brief type. A post hoc script wrote it, and that script was not kept. You can count the same values from `tables/answers_hotel.csv.gz` (experiment A, cells `t0` and `t1`, column `brief_type`).
- **Times and checksums.** Some outputs hold the time of the run, a duration, the number of worker processes, or the SHA-256 of a project file. `analyses.json` names these keys and lines (`ignore_keys`, `ignore_lines`), and `reproduce.py` does not compare them. For example, `clear_rule.md` holds the time when it was written, and `posthoc/release-fresh/out/result.json` holds the SHA-256 of the files that the study ran (key `sha256`).
- **Printed results.** Some scripts print their results and write no file. `reproduce.py` compares the printed text with the files in `explore/logs/analysis/`. `r9/natural/tradeoff.py` reads the printed output of `natural_analyze.py`.
- **`harm_by_model`.** `r10/analysis/i_analyze.py` reads the reference rates of its prediction I3 from `explore/reference/harm_by_model.out`. The script `reference/harm_by_model.py` writes this text again from the round-9 answers.
- **`loyal_final_recommendations`.** The script also writes `loyal_final_recommendations_rows.json`, one row for each conversation. This repository does not store that file, so `reproduce.py` removes it after the run. We fixed the rule of the script before the counts, in `r10/analysis/loyal_final_recommendations_spec.md`.
- **Order.** Some post hoc scripts read the outputs of other scripts. `reproduce.py` runs them in the order of the table. For example, `repair_limits.py` reads the outputs of `repair_refs.py` and `repair_rule.py`, and `t3_boot.py` reads the output of `t3_collect.py`.
- **Specifications.** `explore/posthoc/checks/*/SPEC-HASHES.txt` and `r10/analysis/loyal_final_recommendations_spec_hash.txt` give the time and the SHA-256 of each specification as we wrote it, before the check ran. The copies here have the text changes of section 9, so their SHA-256 values are different.
- **Slow steps.** The simulation of the release rules (`sim_run`, about 15 minutes with 7 worker processes on our computer), the stored comparisons with other seeds (`sim_tails`, about 2 minutes) and the bootstrap precision (`boot_precision`, about 3 minutes) take long. They run only with `--slow` or with their names. Their stored outputs are here.

## 5. Checks of the code

`python3 -I reproduce.py --checks` also runs these checks:

- `verify_requests.py` builds the requests of each round-10 run again from the code and the corpus. It compares the number of requests and their SHA-256 with `r10/manifest.json`, which was written before the runs. Some runs build their requests from the full stored answers of an earlier step (for example the second step `era2_*`, the returned note `erw*` and `eru_*`, and the later rounds of the steering runs `erq2_*` to `erq4_*`). The held-out confirmation (`ern_*`) builds its requests from the registered held-out answers. This repository does not hold those answers, so the check shows these runs as "not rebuilt". The fresh release test (`erk4_*`) builds its requests in `r10/fresh27.py`, not in `r10/runs.py`, so the check also shows it as "not rebuilt". In our test, 84 runs were the same, 0 were different, and 34 were not rebuilt.
- `main/exp0/test_analysis.py` runs the frozen analysis of the registered test on simulated answers.
- `answer_tables.py` writes the scored tables again, and the check compares them with `tables/`.
- `smoke_test.py` (section 3, step 3).
- The unit tests of round 10 (`r10/tests/`) and of the post hoc analyses (`explore/posthoc/`). The unit tests that `analyses.json` lists in `unit_tests_need_data` need data that this repository does not hold (section 8), so they must fail here.

## 6. Answer data

### 6.1 Answer rows: `explore/<run>/raw.jsonl.gz`

Each line is one answer of one model to one request. `reproduce.py` unpacks these files, and the analysis scripts read the unpacked `raw.jsonl`. Each row holds the parsed answer of the model service, not the full service response.

| Field | Meaning |
|---|---|
| `custom_id` | The request: run, dialogue or item, condition (cell), and answer number (read). See below. |
| `type` | `succeeded`, or the kind of failure (for example `errored`). |
| `model` | The model identifier that the service returned. |
| `stop` | Why the answer stopped: `end_turn`, `tool_use`, or a length limit (`max_tokens`, `length`, `incomplete`). |
| `provider_stop` | The stop value of the service, where it differs from `stop`. |
| `input_tokens`, `output_tokens`, `reasoning_tokens` | Token counts. |
| `text` | The text of the answer. For a form answer, this is the JSON object that the model wrote. |
| `tool_calls` | The tool calls: `name` and `input`, as the service returned them. |
| `status`, `error` | For a failed request: the status code and the error message. |
| `provider_cost`, `cost` | The cost in USD that the service reported (some runs only). |

The `custom_id` has these forms:

- Round 10: `<run>-<dialogue>-<cell>-<read>`, for example `era1_sol-MUL0001-t0-1`.
- Round 9 and the earlier run `e13`: `<run>-<dialogue>-<cell>-<read>-<model>`, for example `ez3_sonnet-MUL2198-p_null_nat-1-sonnet`.
- Word pairs (round 10, experiment H): `<run>-<item unit>-<form>-<read>`.
- Constructed items (`e14`): the item identifier, the form, the read and the model.

A dialogue identifier, for example `MUL0001`, is the name of a dialogue in the corpus (`MUL0001.json`). The code of each round defines the cell names: `r10/runs.py` (round 10), `r9/natural/natural.py` (`FORMS`), `r9/additions/zruns.py` (`CELLS`), and `r10/tools.py` (tool cells `t0`, `t1`, `t0ask`, form cell `p0`).

The run folders, by experiment:

| Run folders | Experiment |
|---|---|
| `era1_astra`, `era1_haiku`, `era1_luna`, `era1_opus`, `era1_sol`, `era1_sonnet`, `erx_a1_sonnet`, `erx_a2_opus`, `erx_a2_sonnet`, `erx_a3_sol` | Experiment A: the form answer (`p0`) and the tool calls (`t0` original tool, `t1` renamed tool, `t0ask` with the ask tool) at the first request |
| `era2_astra`, `era2_haiku`, `era2_luna`, `era2_opus`, `era2_sol`, `era2_sonnet` | Experiment A2: the second step after a hotel-only search |
| `erw2_haiku`, `erw2_opus`, `erw2_sonnet`, `erw3_haiku`, `erw_haiku`, `erw_opus`, `erw_sonnet` | Experiment W: the step without the one-search text, with and without the returned note |
| `eru_astra`, `eru_haiku`, `eru_opus`, `eru_sol`, `eru_sonnet` | Experiment U: the returned note, with travellers who need a hotel |
| `ert1_sonnet`, `ert_sonnet` | Experiment T: later turns with a simulated traveller (original and renamed tool) |
| `erb_haiku`, `erb_luna`, `erb_sol`, `erb_sonnet`, `erx_b1_astra`, `erx_b1_opus`, `erx_b2_astra`, `erx_b2_opus`, `erx_b3_astra`, `erx_b3_opus` | Experiment B: four repairs and the verifier |
| `ere_opus`, `erg_astra` | Experiments E and G: the forms on Opus and Astra |
| `erf_haiku`, `erf_luna`, `erf_sol`, `erf_sonnet`, `erx_f0h_opus`, `erx_f1h_opus`, `erx_f2_haiku`, `erx_f2_luna` | Experiment F: a high reasoning setting |
| `eri_haiku`, `eri_luna`, `eri_sol`, `eri_sonnet`, `erx_i3_sol`, `erx_i3_sonnet` | Experiment I: the word "hotel" put into the traveller's turns |
| `erh_haiku`, `erh_luna`, `erh_opus`, `erh_sol`, `erh_sonnet`, `erx_h1_astra`, `erx_h2_astra`, `erx_h34_haiku`, `erx_h34_luna` | Experiment H: 12 constructed word pairs |
| `erl_haiku`, `erl_luna`, `erl_sol`, `erl_sonnet`, `erl_sonnet_hb` | Label test (amendment R10-18): one written definition under the labels `hotel` and `category_A` |
| `erl2_deepseek`, `erl2_gemma`, `erl2_haiku`, `erl2_luna`, `erl2_qwen`, `erl2_sol`, `erl2_sonnet_a`, `erl2_sonnet_b` | Label test (amendment R10-19): the same definition under `serviced_property` too |
| `erl3_luna`, `erl3_sol` | Label test with tool calls (amendment R10-21) |
| `erk_deepseek`, `erk_gemma`, `erk_luna`, `erk_qwen`, `erk_sol` | Release tests of harmless updates (amendment R10-20): the unchanged tool sent again, a paraphrase, and the rename |
| `erk2_luna`, `erk2_sol` | Release tests (amendment R10-22): a field-order change and a second paraphrase |
| `erk3_deepseek`, `erk3_luna` | Replication of the two paraphrase flags (amendment R10-24) |
| `erk4_luna`, `erk4_sol` | Fresh release test of the final rule on new first requests (amendment R10-27) |
| `erp_sol`, `erp_sonnet` | Experiment R: the prospective release test of rewrite N1 |
| `ers_haiku`, `ers_sonnet` | Experiment S: tool texts that a model rewrote to steer the agents (rewrites H1 and G1) |
| `erm_haiku` | Experiment M: three service rewrites for each interest, on Haiku |
| `erq1_haiku`, `erq1_luna`, `erq1_sol`, `erq2_haiku`, `erq2_luna`, `erq2_sol`, `erq3_haiku`, `erq3_luna`, `erq3_sol`, `erq4_luna` | Steering when the agent can search again (amendment R10-23), rounds 1 to 4 |
| `erc2_haiku`, `erc_haiku` | Experiment C: two control updates |
| `ery_deepseek`, `ery_gemma`, `ery_qwen` | Experiment Y: the search measure, fixed in advance, on three open models |
| `eb1_di`, `eb1_luna`, `eb1_sol`, `ex1_f6`, `ex1_grp`, `ex1_s1`, `ex1_tc`, `ex2n_di`, `ex2n_luna`, `ex2n_sol`, `ex2n_sol_f4`, `ex2n_sol_sub` | Round 9: renamed and other forms on full dialogues (X1, X2, B1) |
| `eb2_open`, `eb2_sol`, `eb3_open`, `eb3_sol`, `eb4_open`, `eb4_sol`, `ez1_claude`, `ez1_luna`, `ez2_claude`, `ez2_luna`, `ez3_haiku`, `ez3_luna`, `ez3_sonnet` | Round 9: text edits, the first request, instruction changes (Z1 to Z3, B2 to B4) |
| `e13`, `e14` | Earlier runs that the round-9 analysis reads as the Claude baseline |

### 6.2 Scored tables: `tables/`

`explore/answer_tables.py` wrote these tables from the answer rows, with the parsers of the analysis scripts. Each table is a gzip CSV file with a header row.

`answers_hotel.csv.gz`: one row for each form answer or tool call on the hotel field.

| Column | Meaning |
|---|---|
| `round` | 8 (the baseline runs `e13`, `e14`), 9 or 10. |
| `run`, `experiment`, `model`, `dialogue`, `cell`, `read` | The answer (section 6.1). |
| `status`, `stop` | As in the answer row. |
| `valid` | 1 when the answer is scorable: it finished, and its parser read it after the declared normalization. The parser does not check the allowed values. Else 0. |
| `invalid_reason` | When `valid` is 0: `failed`, `cut` (length limit), or `parse`. |
| `schema_valid` | 1 when the answer is scorable and its tool call fits the full input schema of the called tool after the declared normalization (`r10/analysis/tool_validity.py`, `problems`). For a form answer, a verifier answer and an answer without a tool call, the same value as `valid`. |
| `schema_problems` | The problems that the full-schema check found, joined with "; ". |
| `kind` | `form`, `search` (a call of `search_hotels`), `ask`, `none` (no tool call), or `verify` (a verifier answer). |
| `type` | The `type` list of the answer, with renamed values mapped back to the original names. |
| `hotel` | 1 when `type` holds `hotel`. A scorable answer without a search scores 0. |
| `hotel_only` | 1 when `type` holds `hotel` and not `guesthouse`. |
| `verifier_answer` | `yes`, `no` or `unclear`, for the verifier cell of experiment B. |
| `brief_type` | The venue type that the brief sets: `none`, `hotel` or `guesthouse`. Empty for a constructed item. |
| `search_failure` | 1 when the answer has a hotel-only filter, no hotel fits the brief, and another venue fits. |
| `fields` | All parsed fields of the answer, as JSON. |

A scorable answer without a tool call is not a search: count the search calls with `kind` = `search`.

`answers_next_step.csv.gz`: one row for each answer of the second step (`era2_*`) and of the step without the one-search text (`erw*`). The column `kind` is the class of `r10/flag.py` (`classify`): `widen` (a new search without the hotel-only filter), `kept` (a new search with it), `tell` (a reply that names the other type or asks about the type), `other`, `neither`, or `invalid`.

`answers_word_pairs.csv.gz`: one row for each answer of the word pairs. `writes_colliding_value` is 1 when the `type` list holds the value that has the same name as the person's word. `only_colliding_value` is 1 when the list holds only that value.

`conversations_turns.csv.gz`: one row for each conversation of the later turns, with the outcomes of `r10/analysis/turns_analyze.py`.

Some runs have no scored table, because each of them uses its own tools or forms (for example experiments S, M, C and U, the label tests and the release tests of the amendments). Their answer rows are in their run folders.

## 7. Texts, schemas, examples and protocol

The texts are in the code, as the models got them.

| Text | File and name |
|---|---|
| Original form (system text, field list, allowed values) | `forms/common.py` (`FORMS["p_main"]`), `r9/natural/natural.py` (`system`, `schema`) |
| Renamed, neutral-value, value-only, field-only, placebo and coded-value forms | `r9/natural/natural.py` (`FORMS` f0 to f6, `NEUTRAL`) |
| Described form of the held-out test | `main/wave1.py` (`DESCRIPTIONS`, `FORMS`) |
| Answer schemas | `pmain/e13.py` (`schema`), `r9/natural/natural.py` (`schema`), `r9/additions/zforms.py` (`schema`) |
| Tool definitions (`search_hotels`, `ask_traveller`) and the tool instruction | `r10/tools.py` (`SEARCH_DESCRIPTION`, `ASK_DESCRIPTION`, `ASK_NEW`, `END_NEW`, `END_NEW_ASK`, `TOOLS`) |
| Tool result and second-step message | `r10/briefsearch.py` (`result_rows`), `r10/stage2.py` |
| Step without the one-search text, and the returned note | `r10/flag.py` (`multi_system`, `flag_line`), `r10/flag2.py` |
| Later turns and the simulated traveller | `r10/turns.py` |
| Repairs (list, worked examples, quote) and the verifier | `r10/forms10.py` (`LIST_RULE`, `EXAMPLE_1`, `EXAMPLE_2`, `EVIDENCE_SENTENCES`, `evidence_schema`, `VERIFY_QUESTION`, `VERIFY_SCHEMA`) |
| Instruction changes of round 9 (definition, required or preferred, null, unclear) | `r9/additions/zforms.py` (`DEFINE`, `SPLIT_*`, `NULL_SENTENCE`, `UNCLEAR_SENTENCE`) |
| Text edits ("place to stay"; "a hotel" put in) | `r9/additions/zforms.py`, `r10/textedit.py` |
| Word pairs: pairs, templates, and every constructed request with its intended reading | `r10/pairs.py`, `r10/pairs.json`, `r10/pairs_review.md` |
| Constructed Track C items (the clear controls of round 9) | `trackc/templates.py` |
| Prospective release test: the request to the developer model, its answers, the accepted edit | `r10/release.py`, `r10/release/request.json`, `r10/release/answers.jsonl`, `r10/release/edit.json`, amendment R10-6 in `PROTOCOL.md` |
| Steering service: the briefs and the requests to the service model, and the steered tools | `r10/steer.py`, `r10/steer/`, amendment R10-14 in `PROTOCOL.md` |
| Three service rewrites for each interest | `r10/steer2.py`, `r10/steer2/`, amendment R10-15 in `PROTOCOL.md` |
| Two control updates | `r10/control.py`, amendment R10-16 in `PROTOCOL.md` |
| Release tests of harmless updates: the paraphrases and the field-order tool | `r10/harmless.py` (`TOOL_PARAPHRASE`, `FORM_PARAPHRASE`), `r10/harmless2.py` (`TOOL_PARAPHRASE2`), `r10/control.py` (`ordered_tool`), amendments R10-20 and R10-22 in `PROTOCOL.md` |
| Label test: the forms with one written definition (labels `hotel`, `category_A`, `serviced_property`) | `r10/labeltest.py` (`NOTE`, `FORMS`), `r10/labeltest2.py` (`TYPE_LINE`, `FORMS`), amendments R10-18 and R10-19 in `PROTOCOL.md` |
| Label test with tool calls: the system texts and the tools of the three labels | `r10/labeltest3.py` (`system`, `tool`), amendment R10-21 in `PROTOCOL.md` |
| The search trade measure on three open models (the verifier texts of the repairs) | `r10/forms10.py`, amendment R10-17 in `PROTOCOL.md` |
| Model identifiers and settings | `r10/models.py`, `pmain/e13.py`, `r9/natural/natural.py` (`MODELS`), `r9/deepinfra_settings.py` |
| Word rule for clear and unclear requests | `r10/analysis/clear_rule.py` |
| Steering when the agent can search again | `r10/steer3.py`, amendment R10-23 in `PROTOCOL.md` |
| Replication of the two paraphrase flags | `r10/harmless3.py`, amendment R10-24 in `PROTOCOL.md` |
| Held-out confirmation of the repairs (the verifier requests) | `r10/confirm25.py`, amendment R10-25 in `PROTOCOL.md` |
| Simulation of the release rules | `posthoc/release-sim/sim.py`, `rules.py`, amendment R10-26 in `PROTOCOL.md` |
| Fresh release test: the selection of the new first requests and the cells | `r10/fresh27.py`, amendment R10-27 in `PROTOCOL.md` |
| Items of the author's blind check, as the labeller saw them (no label, no key) | `annotation/game_items.json` |

Each run script, for example `r10/era1_sol.py`, builds its requests with `r10/runs.py`. The request builder of a run is the `build` function in `runs.RUNS`.

The folder `examples/` shows requests as the runs sent them, with their answer rows. Each file is one run. It holds the first request of each condition: the model, the settings, the system text, the user text (a corpus dialogue, MIT License), the tool definitions or the answer schema, and the strict-mode setting.

The protocol and the registrations:

- **Registration A** (https://osf.io/bv8q9, filed 2026-11-12 at 04:25 UTC) covers the registered test. `explore/main/exp0/registration/` holds `REGISTRATION-A.md` and `AMENDMENT-A1.md` as filed, byte for byte. The registry also holds the protocol as it was at the filing, and the SHA-256 of every encrypted answer file.
- **Registration B** (https://osf.io/jy3pd, filed 2026-11-13) covers more tests. Its test on constructed job-search texts is opened and analysed: `explore/main/exp1/` holds the frozen analysis, which ran one time, its aggregated results, and `REGISTRATION-B.md` and its addendum as filed, byte for byte. The answers of that test and of the other tests of registration B are not here (section 8).
- **The study protocol** (`explore/PROTOCOL.md`). Each part has the date and the time (UTC) when we wrote it. Most parts tell which runs or results existed at that time. The text up to amendment R10-4 is the version filed with registration A, with the changes of section 9. The amendments R10-5 to R10-27 and the parts on experiment H came later. Some code reads the protocol and checks that an amendment did not change (for example `r10/release.py`, `r10/flag.py`, `r10/steer.py`).

The predictions of round 9 are also in `explore/r9/*/PREDICTIONS.md`.

## 8. What is not in this repository, and why

| Item | Why | Effect |
|---|---|---|
| The public corpus MultiWOZ 2.4 | It is public. Section 3 tells how to get it. | Most analyses need it. |
| The answers of the registered tests | They stay encrypted until their registered analyses run. Only the aggregated results of stage 1 are here. | The scripts of the registered test cannot run here (section 4). Their stored outputs are here. |
| The verifier answers of the held-out confirmation (amendment R10-25, run folders `ern_*`) | The verifier read the opened held-out answers of stage 1. Each row names a held-out dialogue whose answer had a hotel-only filter, and the verifier's verdict. This repository holds no row of a single answer of the registered tests. | `heldout_confirm.py` cannot run here (it also needs the held-out answers). Its stored outputs are here. |
| The labels of the author's blind checks (`annotation/labels_local.jsonl`) and the labelling keys (`key.json`, `key2.json`) | They are private. The keys are the hidden answer sheets of the blind labelling task. | The `annotation` analysis cannot run here. Its stored report (`annotation/labels_report.md`) is here. |
| The answers and items of registration B | The test on constructed texts ran one time on its opened answers. The other tests are still encrypted, and the items are held out for them. | `exp1/analysis_b.py` cannot run here. Its stored results are here. |
| The constructed items of later registered tests | They are held out for those tests. | `r10/groups.py` cannot check that a new text does not copy them (section 9). `test_groups.py` fails. |
| The full service responses and the request files | The request files repeat the corpus text. The full responses hold service identifiers. The answer rows keep every answer text and every tool call. | `verify_requests.py` builds the requests again (section 5). Some runs need the full responses of an earlier step, so the check cannot rebuild them, and some unit tests fail (`analyses.json`, `unit_tests_need_data`). |
| The cost records, the money limits of the paid steps (`r10/newmoney.py`) and the account balances | They hold the account limits and balances. `PROTOCOL.md` holds the bounds of each step, but the account balances are withheld. | No analysis reads them. Two unit tests import `newmoney.py`, so they fail. `posthoc/release-fresh/analyze.py` keeps the stored cost values. |
| The independent checks of some post hoc numbers (check scripts, their outputs and reports) | The check scripts also read the request files, the full service responses and the cost records, and they also check work that the preprint does not report. | Some post hoc scripts read stored values of a check: `r10/analysis/out/rtest_check_values.json` and `repair_rename_check.json`. `rtest_v.py`, `rtest_vr.py`, `rtest_vr2.py` and `repair_loaders.py` are the loaders and parsers of the checks, copied verbatim. `loyal_unchecked_runs.py` and `loyal_values_a.py` to `loyal_values_c.py` read other check files, so they cannot run here. |
| The manuscripts | Two checks parse tables of a manuscript (`sim_fidelity`, `d3_check`). | These two checks cannot run here. Their stored outputs are here. |
| The hidden reasoning of the models (Claude thinking blocks, encrypted reasoning items of the GPT models) | They are not part of any measure. | None for the analyses. |
| Runs that the preprint does not report, pilot answers, run logs, plans, reviews, working notes and the scripts that draw the figures | They are not results of the preprint. | None for the analyses. |
| The script that wrote `tool_by_brief.json` | It was not kept. | Section 4 tells how to count the same values. |

## 9. Differences from the working copy of the study

This repository differs from the working copy only in these points:

- Paths on the author's computer, the name of the drive, the user name, the country and the names of other manuscripts and of internal files are replaced with neutral text, for example "the paper" or "an internal file". Paths of the project become paths of this repository.
- The answer rows hold no service identifiers (message, call and batch identifiers), no opaque signatures and no full content blocks. Every answer text and every tool call stays. The rows are stored as gzip files.
- `lib/anth.py` and `r10/analysis/rtest_vr.py` read the corpus from `corpus/MULTIWOZ2.4` in this repository.
- `lib/accounts.py` holds no comments about money. `r10/labeltest3.py` holds no account balance.
- `r10/groups.py` skips the withheld item files, and prints a note when it skips them.
- `r10/steer3.py` cannot build the next request of a replay without the call identifiers. The outcomes of the analysis do not need it.
- `r10/analysis/i_analyze.py` reads its reference file from `explore/reference/`. The two scripts in that folder find the study folder from their new place.
- `annotation/analyze_labels.py` has a shorter usage text.
- `explore/PROTOCOL.md`: the same changes as above, and the account balances in the money rules are withheld.
- `explore/posthoc/`: each script is a copy of a project script outside the study folder. Only the lines that find the study folder, the stored outputs and the corpus differ, and the text changes of this section. `posthoc/release-fresh/analyze.py` keeps the stored cost values when the cost records are absent. The outputs have the same text changes.
- The study-folder copies of other post hoc scripts (`r10/analysis/loyal_*.py`, `rtest_*.py`, `repair_*.py`) have the paths of the study folder and neutral names. Their results are the same as those of the project scripts.

The files that registration A fixes (section 4) and the registration files are byte-identical. The changes do not change a request text, a parser or an analysis.

## 10. Licenses

| What | License |
|---|---|
| Code: every `.py` and `.sh` file, including `reproduce.py`, the scripts in `explore/` and `annotation/analyze_labels.py` | MIT License (`LICENSE`) |
| Text and data: `README.md`, `paper/`, `analyses.json`, `explore/PROTOCOL.md`, the registration files, the result files, the answer rows, `tables/`, `examples/`, the data of `annotation/`, and every other file that is not code | CC BY 4.0 (`LICENSE-CC-BY-4.0.md`) |

The dialogue text of the corpus, which is in `examples/` and in some answers, comes from MultiWOZ 2.4 under the MIT License.

## 11. How to cite

Please cite the preprint:

> Dev D. Goyal. 2026. How an Everyday Word in a Tool Schema Changes AI Agents' Searches While Every Call Stays Valid. Preprint. Zenodo. https://doi.org/10.5281/zenodo.24270645

```bibtex
@misc{goyal2026valuenames,
  author       = {Goyal, Dev D.},
  title        = {How an Everyday Word in a Tool Schema Changes AI Agents' Searches While Every Call Stays Valid},
  year         = {2026},
  note         = {Preprint},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.24270645},
  url          = {https://doi.org/10.5281/zenodo.24270645}
}
```

GitHub also shows these data under "Cite this repository" (`CITATION.cff`).
