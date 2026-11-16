# Round 9 natural runs X1, X2 natural, and B1: predictions (written 2026-11-03, before any call)

Sources: `../../../../ROUND9-EXPERIMENT-PLAN.md` section 3 (X1, X2), `../../../../review/plan13/claude-draft.md` (X1 P1 to P7, X2 Q1 and Q2), `../../../../ROUND9-ADDITIONS.md` sections 2 and 9 (booked venue, B1), and `../../../../review/plan13/planner-gpt-6.1-sol.md` R4 (F6). Claude merges this file into `PROTOCOL.md` before any pilot.

## Forms

The base form is E13 `p_main` for the dialogues and E14 `p_main` for the E4 items. Each form changes only the named tokens in the field list, the allowed values, and the schema. The parser of each form maps the tokens back, so all forms are scored on the same fields and values. `test_natural.py` checks each edit.

| Form | Field | Value for "hotel" | Other change |
|---|---|---|---|
| F0 | `type` | `hotel` | none (equals `p_main`) |
| F1 | `property_kind` | `large_property` | none (equals `p_main_renamed`) |
| F2 | `type` | `large_property` | none |
| F3 | `property_kind` | `hotel` | none |
| F4 | `type` | `serviced_property` | none |
| F5 | `type` | `hotel` | `area` is `district`, `pricerange` is `price_band`; values unchanged |
| F6 | `type` | `category_A` | the allowed values say `type: guesthouse, category_A (any venue type that is not a guesthouse).` |

**F4 token check (mechanical, `test_natural.py check_neutral`).** The rule: no "hotel" substring, no size or quality word, and no use in a traveller turn of the training split (8,438 dialogues). `serviced_property` has no "hotel" substring and no word from the size and quality list. Traveller turns that hold "serviced property" (space, underscore, or hyphen; plural allowed): 0. So F4 uses `serviced_property`. The backup `full_service` is not used.

## Groups (`ids.json`, seed 20261103)

All groups come from the 2,874 E7 training dialogues. The counts are asserted in `natural.compute_ids`.

| Group | Rule | Dialogues |
|---|---|---:|
| S1 | gold sets no type, and some turn says "hotel" (the E11 set) | 1,136 |
| S1t | S1, and a traveller turn says "hotel" (the primary analysis set) | 994 |
| S2 | gold `type` is `hotel` | 545 |
| S3 | gold `type` is `guesthouse`, and a traveller turn says "hotel" | 490 |
| S4 | gold `type` is `guesthouse`, and no traveller turn says "hotel" | 423 |
| S5 | the rest: gold sets no type and no turn says "hotel" (235), or gold says "any" (45) | 280 |
| drift | a seeded 20% of S1 | 228 |
| sub600 | a seeded 600 of S2, S3, and S4 | 600 |
| S2_booked_hotel | S2, and the last booked venue is a hotel in `hotel_db.json` (the `revealed_r9b.py` rule) | 293 |
| S2_brief_hotel | S2, and the brief says `goal.hotel.info.type` = `hotel` | 233 |
| S1t_booked_* | S1t by the booked venue type: guesthouse, hotel, none, unmatched | 355, 199, 440, 0 |

S2 to S5 hold 1,738 dialogues. With S1 they hold all 2,874. The two certified groups are the correct-value groups: the gold, and the booking or the brief, both say "hotel".

## Settings

- Claude: the E13 settings. Haiku has thinking disabled at effort `medium`. Sonnet has thinking `between_tools` at effort `high`. `max_tokens` is 4,096. Structured output uses the closed E13 schema.
- `gpt-6.1-sol` reasoning effort `low`, `gpt-6-luna` reasoning effort `none`, no temperature, `max_output_tokens` 4,000, strict JSON schema. Source: SYN-S5 section 3.2, which PLAN SI-09 names, and the 4,000 cap of PLAN SI-02.
- DeepInfra: temperature 1.0, top_p 1.0, and a seed (CRC32 of the custom_id), `max_tokens` 4,000, strict JSON schema. DeepSeek gets `reasoning_effort` `low` (its lowest effort). Qwen gets `reasoning_effort` `none` (thinking off). Gemma gets no reasoning option. UNVERIFIED: the DeepInfra names and values of these options, and whether DeepInfra applies the seed and the strict schema for each model.

## Experiments

| Experiment | Account | Run | Content | Requests per model |
|---|---|---|---|---|
| `ex1_s1` | anthropic_r9a | X1 | S1 x F2, F3, F4, F5, 3 reads; drift x F0, 3 reads | Haiku 14,316; Sonnet 14,316 |
| `ex1_grp` | anthropic_r9a | X1 | S2 to S5 x F0, F1, F2, F4 | Haiku 20,856 (3 reads); Sonnet 13,904 (2 reads) |
| `ex1_f6` | anthropic_r9a | X1 | S1 x F6, 3 reads; S2 to S5 x F6, Haiku 3 and Sonnet 2 reads | Haiku 8,622; Sonnet 6,884 |
| `ex1_tc` | anthropic_r9a | X1 | E4 condition a x F1, F2, F4 (Haiku 7 reads, Sonnet 6); Sonnet F0 reads 3 to 6 | Haiku 1,680; Sonnet 1,760 |
| `ex2n_sol` | openai_r9 | X2 | S1 x F0, F1, 1 read | Sol 2,272 |
| `ex2n_sol_f4` | openai_r9 | X2 | S1 x F4, 1 read | Sol 1,136 |
| `ex2n_sol_sub` | openai_r9 | X2 | sub600 x F0, F1, F4, 1 read | Sol 1,800 |
| `ex2n_luna` | openai_r9 | X2 | all 2,874 x F0, F1, F4, 3 reads | Luna 25,866 |
| `ex2n_di` | deepinfra | X2 | S1 x F0, F1, 1 read | each DeepInfra model 2,272 |
| `eb1_luna` | openai_r9 | B1 | S1 and S2 x F2, F3, F5, F6, 3 reads | Luna 20,172 |
| `eb1_sol` | openai_r9 | B1 | S1 x F2, F6, 1 read | Sol 2,272 |
| `eb1_di` | deepinfra | B1 | S1 x F2 to F6; S2 x F0, F1, F4; 1 read | each DeepInfra model 7,315 |

Each X1 folder has a pilot of 10 calls per model, so X1 has 40 pilot calls per model. With them, X1 is Haiku 45,514 and Sonnet 36,904, as `r9_counts.py --balance` gives. The other folders refuse the pilot step, because the X2 pilot P measures this task and `r9_counts.py` counts no other pilot. The F0 and F1 reads of Claude on S1 come from E13. The Track C F0 reads come from E14: Haiku reads 1 to 7, Sonnet reads 1 and 2, and `ex1_tc` adds Sonnet reads 3 to 6 with the same request.

**X2 Sol cut rule (plan section 3).** If one `gpt-6.1-sol` call in pilot P costs more than 0.0070 USD, Sol keeps only S1 x F0 and F1. Then do not submit `ex2n_sol_f4` and `ex2n_sol_sub`. **B1 Sol** runs only while the OpenAI money allows it, in the order B2, B1, B3, B4 (ROUND9-ADDITIONS section 9).

## Measures and analysis

Run `python3 -I r9/natural/natural_analyze.py`. A valid read succeeded, stopped at `end_turn`, and parses.

- The share of valid reads that write `type = hotel` (the E8 measure), per model, form, and group. On S2 and on the certified groups this share is the share of correct values kept.
- The exact two-sided sign test of each form against F0, per model and group, over dialogues with reads under both forms (`forms/e8_measure.py`).
- The booked-venue exclusion on S1t: by the booked venue type, the share of reads whose `type` holds "hotel" and not "guesthouse", so a search hides every guesthouse; and the sign test against F0 on the guesthouse-booked dialogues (`revealed_r9b.py`). On the E13 rows the script gives the `revealed_r9b.out` numbers.

E13 reference on S1t (RESULTS.md section 10): Haiku 5.1% under F0 and 1.3% under F1; Sonnet 18.4% and 5.2%.

## Predictions

Each prediction names its primary cell first. Builder A chose the primary cells from the plan text and the caller's design note. Claude can change them when merging, before any pilot.

**X1** (Haiku 5.5 and Sonnet 5.5):

- P1, specificity. Primary cell: Sonnet on S2_booked_hotel. Under F1 and under F4, the share of `type = hotel` falls by 5 percentage points or less against F0. The same holds on S2_brief_hotel (check). On S2, the F0-to-F1 fall is at most half of the F0-to-F1 fall on S1t.
- P2, known errors. Primary cell: Sonnet on S3. Under F1 and under F4, `type = hotel` reads fall against F0.
- P3, which word. Primary cell: Sonnet on S1t. F2 gives at least two thirds of the F0-to-F1 fall. F3 gives one third of it or less.
- P4, the size meaning. Primary cell: Sonnet on S1t. The F0-to-F4 fall is within 5 percentage points of the F0-to-F1 fall.
- P5, placebo. Primary cell: Sonnet on S1t. F5 moves the share by 2 percentage points or less against F0.
- P6, clear controls. Primary cell: Sonnet on the 40 E4 condition-a clear controls. `type = hotel` stays at 95% or more under F0, F1, F2, and F4.
- P7, drift. Primary cell: Sonnet on the 228 drift dialogues. The new F0 reads are within 3 percentage points of the E13 F0 reads on the same dialogues.
- F6 (Sol memo R4). Primary cell: Sonnet on S2_booked_hotel. F6 keeps more correct values than F1: its `type = hotel` share is higher.

What changes (plan section 3 and the draft): if P1 fails, the paper does not call renaming a fix, and the main study adds a "correct values kept" outcome. If P4 holds, F4 against F0 becomes the H4 natural main contrast. The best of F1, F4, and F6 becomes the main-study contrast. If P3 fails, the paper drops the simple value-token rule. If P5 fails, the paper states the claim net of the placebo. If P7 fails, rerun F0 and F1 on S1 before any comparison.

**X2 natural** (`gpt-6.1-sol`, `gpt-6-luna`, `DeepSeek-V4.1-Flash`, `Qwen3.8-27B`, `gemma-4-31B-it`):

- Q1. Primary cell: each model on S1t. F0 to F1 lowers `type = hotel` for 3 or more of the 5 models (exact sign test, p < 0.01).
- Q2. For the models where Q1 holds, the F0-to-F4 fall is within 5 percentage points of the F0-to-F1 fall. The DeepInfra F4 reads on S1 come from `eb1_di`.
- If Q1 fails, the paper calls Claim 1 model-dependent and reports each provider apart.

**B1** (ROUND9-ADDITIONS section 9 gives no separate prediction). B1 repeats the X1 mechanism tests on the non-Claude models, so it carries these X1 predictions to each model with B1 reads, on S1t: P3 (F2 and F3), P4 (F4, for the open models), P5 (F5), and the F6 prediction. On S2 it carries P1 for `gpt-6-luna` and the open models. The B1 results are exploratory and are reported per model.
