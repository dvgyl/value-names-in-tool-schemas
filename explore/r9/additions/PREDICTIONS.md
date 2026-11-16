# Predictions for Z1 to Z3 and B2 to B4 (round 9, builder D)

Status: written on 2026-11-03, before any pilot or batch. No API call has run. Claude merges this file into `PROTOCOL.md` before the first pilot.

The predictions come from the plan files: `ROUND9-ADDITIONS.md` sections 3 and 9, `review/plan13/addon-opus.md` (A1, A2), and `review/plan13/addon-sonnet.md` (Y1, Y2, Y3). Each prediction names its source.

## Terms

- **F0** is the E13 form `p_main`. **F1** is the E13 form `p_main_renamed`. All forms use structured output and the E13 settings.
- **The 994** are the E11 dialogues by the traveller-turns rule: the gold sets no type, and a traveller turn says "hotel".
- **`type = hotel`** is the E8 measure: the share of valid reads whose `type` list holds "hotel".
- **Booked-venue exclusion** is the share of valid reads whose `type` list does not hold the type of the venue that the traveller booked (`hotel_db.json`).
- **Sonnet** (`claude-sonnet-5-5`) is the primary model. The other models give descriptive results.
- The analysis script is `r9/additions/zanalyze.py`. A synthetic test checks it (`test_analyze.py`).

## Z1. Which word must be present (`ez1_claude` on `anthropic_r9b`, `ez1_luna` on `openai_r9`)

Design: in the traveller turns of the 994, "hotel" becomes "place to stay" and "hotels" becomes "places to stay". Venue names that hold "hotel" do not change. The edited text is read under F0 and F1. The frame part reads a seeded 500 of the 994 with "accommodation booking assistant" in place of "hotel booking assistant", under the original and the edited text, under F0 and F1. The original-text cells under the original frame come from E13 (Claude) and X2 (`gpt-6-luna`).

Predictions:

1. For Sonnet, the text edit removes most of the effect. Under F0, the edit removes at least two thirds of the F0 to F1 difference in `type = hotel` (addon-opus A2; ROUND9-ADDITIONS Z1).
2. For Sonnet, the edited text under F0 gives `type = hotel` in 8% of reads or less. The original text under F0 gave 18.4% in E13 (addon-sonnet Y1).
3. Under F1, the edit changes `type = hotel` by 2 percentage points or less (addon-opus A2).
4. For Sonnet, on the edited text, F0 is at most 3 percentage points above F1 (addon-sonnet Y1).
5. The difference in differences, (F0 minus F1 on the original text) minus (F0 minus F1 on the edited text), is positive (addon-sonnet Y1).

What changes: if Sonnet still writes `type = hotel` in 10% of reads or more on the edited text under F0, the paper drops the word "collision" and says "schema-value anchoring" (addon-sonnet Y1; ROUND9-ADDITIONS Z1).

The frame part: the plan files give no prediction for the frame cells. Claude must write one before the pilot, or the report gives these cells as descriptive results.

## Z2. The agent's real timing (`ez2_claude` on `anthropic_r9b`, `ez2_luna` on `openai_r9`)

Design: the 554 dialogues of the 994 whose booked venue is in `hotel_db.json` (355 guesthouses, 199 hotels). The prefix is all turns up to and including the first traveller turn that says "hotel". The prefix is read under F0, F1, and `p_unclear_nat` (F0 plus the E14 "unclear" option and its sentence). On Claude, a recognition probe reads the same prefix with no form and asks: "Does the traveller's wording fix the venue type to hotel? Answer fixes, does not fix, or cannot tell." The full-dialogue comparison is E13 (Claude) and X2 (`gpt-6-luna`).

Predictions:

1. Sonnet under F0 writes `type = hotel` more often on the prefix than on the full dialogue (ROUND9-ADDITIONS Z2; addon-sonnet Y2 gives 18.4% for the full dialogue).
2. On the prefixes, the precision of `type = hotel` (the share of those reads whose booked venue is a hotel) stays below 52%, near the base rate of 36% (199 of 554) (addon-sonnet Y2).

The recognition probe has no numeric prediction. The cell of interest is the dialogues whose probe answer is "does not fix" and whose F0 read writes `type = hotel` (addon-sonnet Y2).

What changes (addon-sonnet Y2; ROUND9-ADDITIONS Z2):

- If Sonnet under F0 excludes the booked venue on 20% or more of the prefix reads, this becomes the headline.
- If the precision on the prefixes is 60% or more, the harm sentence of Claim 1 becomes weaker.
- If the model answers "does not fix" and then writes `type = hotel`, the paper can show that the model knows that the word is general and still commits.

## Z3. A table of fixes (`ez3_haiku` and `ez3_sonnet` on `anthropic_r9b`, `ez3_luna` on `openai_r9`)

Design: four forms on the X1 groups. S1 is the 1,136 E11 dialogues. S2 to S5 are the other 1,738 E7 dialogues. The forms:

- `p_define`: F0 plus "`hotel` means the database category hotel, not the traveller's general word for a place to stay."
- `p_split`: `type` becomes `type_required` and `type_preferred`. Only `type_required` filters.
- `p_null_nat`: F0 plus the E14 ambiguity sentence with "write null".
- `p_unclear_nat`: F0 plus the E14 "unclear" option and its sentence.

The F0 and F1 comparisons come from E13 and X1 (Claude) and X2 (`gpt-6-luna`).

Predictions (addon-opus A1, unless the line names another source):

1. For Sonnet, `type_required = hotel` under `p_split` on S1 is at most 2 percentage points above F1.
2. `type_preferred = hotel` appears in at least half of the S1 dialogues in which F0 wrote `type = hotel`.
3. In the gold-hotel group (S2), `type_required` plus `type_preferred` keep at least 95% of the F0 `type = hotel` values.
4. `p_null_nat` lowers `type = hotel` by 5 percentage points or more against F0, but by less than F1.
5. For Sonnet, `p_unclear_nat` gives `type = hotel` at least 3 percentage points above `p_null_nat`, as in E14 and E15.
6. For Sonnet, `p_define` removes at least half of the F0 to F1 difference in `type = hotel` (addon-sonnet Y3).
7. `p_split` keeps most of the hotel values as preferences, and `type_required` seldom excludes a guesthouse that the traveller booked (ROUND9-ADDITIONS Z3; no number given).

What changes (ROUND9-ADDITIONS Z3):

- If `p_split` works, the design rule of the paper becomes "keep must apart from prefer".
- If `p_unclear_nat` backfires for Sonnet, the backfire of Claim 2 also holds on real dialogues.

## B2 to B4. The provider balance pack

Runs: `eb2_sol`, `eb3_sol`, `eb4_sol` on `openai_r9` (`gpt-6.1-sol`, 1 read). `eb2_open`, `eb3_open`, `eb4_open` on `deepinfra` (`DeepSeek-V4.1-Flash`, `Qwen3.8-27B`, `gemma-4-31B-it`, 1 read).

- B2 is the Z1 text edit under F0 and F1 on the 994.
- B3 is the Z2 prefix under F0, F1, and `p_unclear_nat` on the 554 booked dialogues.
- B4 is `p_split` and `p_define` on S1 for `gpt-6.1-sol`, and all four Z3 forms on S1 and S2 (the 545 gold-hotel dialogues) for each open model.

The plan files give no separate prediction for B2 to B4 (ROUND9-ADDITIONS section 9). The aim is that each key test has at least one run on `gpt-6.1-sol` and on the three open models. The report gives the Z1 to Z3 measures for each of these models as descriptive results. The original-text cells come from X2 and B1.
