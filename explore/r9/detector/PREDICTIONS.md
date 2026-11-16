# Predictions of the X3 and Z4 runs (Builder C, written 2026-11-03, before any call)

Sources: `PROTOCOL.md` section "X3 and Z4" and its amendment 1, `../../ROUND9-EXPERIMENT-PLAN.md` X3, `../../ROUND9-ADDITIONS.md` Z4. Claude merges this text into `PROTOCOL.md` before any pilot.

## Facts fixed before any call

- `r9/detector/table.py` applied the rule with amendment 1 and wrote `table.tsv` and `selection.json` (`logs/analysis/r9_detector_table_a1.log`). No model output for a non-hotel pair exists. The first selection, before the amendment, is in `logs/analysis/r9_detector_table.log`.
- The rule gives 46 candidates. Each candidate has 120 or more word dialogues, so Z4 can run.
- The slot `attraction-type` has 43 values in `ontology.json`, so the rule removes it.
- Four Z4 candidates have Rule B 0.5000 (ranks 14 to 17). The word dialogues, then the alphabetical order, put `train-departure` = birmingham new street at rank 16, which Z4 takes. The alphabetical step is a reading of the rule text (`pairs.py`).
- The neutral value of every pair is "dax".
- If Rule B and the brief count read only `goal.<domain>.info`, the selection does not change.

## X3

- **Runs:** `ex3c` (`anthropic_r9a`: Haiku 3 reads, Sonnet 2), `ex3l` (`openai_r9`: `gpt-6-luna` 3 reads), `ex3s` (`openai_r9`: `gpt-6.1-sol` 1 read), `ex3d` (`deepinfra`: each open model 1 read on 600 of the 1,200 instances).
- **Pairs (200 instances each):**

| Id | Pair | Role | Rule B | Briefs | Word dialogues |
|---|---|---|---:|---:|---:|
| q01 | `train-destination` = ely | high risk | 0.585 | 125 | 265 |
| q02 | `train-departure` = stevenage | high risk | 0.578 | 109 | 223 |
| q03 | `attraction-area` = north | high risk | 0.561 | 164 | 264 |
| q04 | `train-destination` = kings lynn | high risk | 0.556 | 114 | 241 |
| q05 | `restaurant-area` = centre | control | 0.131 | 1,315 | 1,220 |
| q06 | `restaurant-pricerange` = expensive | control | 0.092 | 1,184 | 1,152 |

- **Measure:** the share of reads whose pair field holds the pair value, under the original form and under the neutral form. The parser maps "dax" back to the original value. The drop is the difference in percentage points. The test is the dialogue-level exact sign test of `forms/e8_measure.py`.
- **Analysis:** `python3 -I r9/detector/analyze.py`.
- **Prediction:** under the neutral value, the 4 high-risk pairs drop by 3 percentage points or more for Sonnet, and the 2 control pairs move by 2 points or less.
- **What changes:** if the high-risk pairs drop and the control pairs do not, the paper can describe Rule B as a schema check that flags risky values before an agent uses the schema.

## Z4

- **Runs:** `ez4c` (`anthropic_r9b`: Haiku 3 reads, Sonnet 2), `ez4l` (`openai_r9`: `gpt-6-luna` 3 reads).
- **Pairs:** 16 pairs at evenly spaced ranks of Rule B (`selection.json`, role `z4`), each with 120 instances. Three of them are X3 pairs (q01, q04, q06). Their Z4 reads are the X3 reads of their first 120 instances. The 13 other pairs (q07 to q19) have 1,560 new instances.
- **Measure and analysis:** as in X3, then the Spearman correlation between Rule B and the drop over the 16 pairs, for each model.
- **Prediction:** the Spearman correlation between Rule B and the measured drop is above 0.
- **What changes:** if Rule B does not predict the drop, the word "detector" leaves the abstract.

## X0 and Z0

The free analyses (`r9/free/`) have no prediction. They ran after the reads, and their logs say that they are exploratory.
