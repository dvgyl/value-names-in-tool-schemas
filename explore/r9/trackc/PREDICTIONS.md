# Predictions of builder B (P, X2 Track C, X2 on-site, X5)

Written 2026-11-03, before any call. Sources: `../../../../ROUND9-EXPERIMENT-PLAN.md` section 3 and `../../../../review/plan13/claude-draft.md` (X2, predictions Q3 to Q6). Claude merges these entries into `PROTOCOL.md` before the pilot P.

All runs are exploratory. No request holds a Track P, gate-set, validation, or test dialogue.

## P, the token and format pilot (`ep_oa` on `openai_r9`, `ep_di` on `deepinfra`)

- **Requests:** 20 per task (natural dialogue, Track C, on-site) on each of the 5 non-Claude models. `gpt-6.1-sol` also reads the same 60 units at its default effort. `gpt-6-astra` makes 24 annotation calls with the E3 prompt (16 E4 items and 8 E7 training dialogues). 204 requests on OpenAI and 180 on DeepInfra, synchronous, at standard prices.
- **Measures:** input, output, and reasoning tokens; valid JSON; cut-off answers (stop at the token limit); the cost of one call per model and task.
- **Analysis:** `python3 -I r9/trackc/ep_summary.py`.
- **Prediction (Q6):** `gpt-6.1-sol` at effort low uses 1,000 reasoning tokens or fewer per call. A `gpt-6-astra` annotation call uses fewer than 8,000 input tokens and fewer than 4,000 output tokens.
- **Cut rule (fixed now):** if one `gpt-6.1-sol` natural call at effort low costs more than 0.0070 USD at batch list prices, Sol keeps only the core parts of X2 and leaves X3.
- **What changes:** if Q6 fails, rerun `budget_v11.py --reasoning gpt-6.1-sol=<measured>`. Then the operator chooses a lower Sol effort or a smaller Track C for the main study.

## X2, Claim 2 part (`ex2c_oa` on `openai_r9`, `ex2c_di` on `deepinfra`, `ex2c_an` on `anthropic_r9a`)

- **Requests:** the 320 E4 items under `p_main`, `p_null`, `p_unclear`, and `p_option`. `p_option` has the "unclear" value in the schema and no sentence about ambiguity. Reads: `gpt-6.1-sol` 2, `gpt-6-luna` 3, each DeepInfra model 1. The Claude models read only `p_option`, with the E14 settings and schema: Haiku 7 reads, Sonnet 4 reads. Their `p_main`, `p_null`, and `p_unclear` cells come from E14.
- **Analysis:** `python3 -I r9/trackc/ex2c_analyze.py`, the E4 scorer without changes, with `p_option` added to the compared forms.
- **Prediction (Q3):** on the 5 non-Claude models, `p_unclear` against `p_null` differs by 5 percentage points or less in most ambiguous cells (conditions a, b, c). Condition d stays at 0% commitment under every form.
- **Prediction (Q4):** for Sonnet in condition b, `p_option` commits at least as often as `p_unclear`.
- **What changes:** if Q3 holds, the option-specific claim becomes secondary. If Q4 holds, `p_option` goes into the main study. If the option backfires on 2 or more non-Claude models, the main study gets a directional hypothesis in the decomposition family.

## X2, on-site part (`ex2s_oa` on `openai_r9`, `ex2s_di` on `deepinfra`)

- **Requests:** the 38 E2 cases x 3 arms (orig, office, renamed) x 5 reads on the 5 non-Claude models, with the frozen E2 prompts and no schema.
- **Analysis:** `harness/.venv/bin/python r9/trackc/ex2s_analyze.py`, the E2 scorer without changes.
- **Prediction (Q5):** the renamed arm gives fewer wrong extractions than the original arm for 3 or more of the 5 models.

## X5, independent check of the item readings (`ex5_an` on `anthropic_r9a`, `ex5_oa` on `openai_r9`)

- **Requests:** `claude-opus-5-5` and `gpt-6-astra` each read the same seeded 80 E4 items (both items of 10 goals per condition) and 40 E7 training dialogues with the E3 codebook prompt. They see no model answer. Each annotator reads a seeded 20 of these 120 units again. 140 calls each.
- **Analysis:** `python3 -I r9/trackc/ex5_analyze.py`.
- **Prediction:** the two annotators disagree on the target field class more often on the ambiguous E4 items (two or more readings) than on the clear E4 items.
- **Limit:** agreement between two models is not human validation. It does not replace the operator's blind coding.
