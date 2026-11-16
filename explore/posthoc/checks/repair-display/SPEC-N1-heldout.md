# SPEC N1: held-out benefits, display costs and computation costs (the paper)

Written: 2026-11-15 22:59 UTC, before the extraction script ran. During the availability check (22:50 to 22:58 UTC) I printed these stored aggregates once; no choice below depends on them, and every listed field is reported for every model. Status in the paper: descriptive counts from the exploratory held-out test (Section 6), reported post hoc; they are not among the seven predictions.

## 1. Data availability (the finding that decides the scope)

- The existing held-out display results of the paper (Appendix D, "Held-out display results"; Table D6, display columns) come from `r10/analysis/out/heldout_confirm.json` and `result.md` (sources rows 446, 448, 475, 483). The script an internal file produced them.
- `analyze.py` reads the held-out original answers only through `r10/confirm25.py`, which reads `main/exp0/open/em1_<model>/raw.jsonl`. The verifier answers are in `ern_<model>/raw.jsonl` (outside `em*`), but they hold only the verifier's yes / no / unclear for each (dialogue, read). A display needs every field of the original answer (area, price, stars, parking, internet, name, type).
- A search of all `.json`, `.jsonl`, `.tsv` and `.csv` files outside `em*` folders for the held-out form name `t_legacy` found only aggregate result files and source tables (no per-answer copy of the held-out original answers).
- Decision (rule of the study): **no new computation on per-answer held-out data.** In particular, guesthouses newly shown by the planned verifier gate and by the soft type filter on the 18 word-rule-stated hotel briefs are **not computed**. The paper keeps its present statement for these two cells.

## 2. What the stored aggregates already contain (coverage), and what this extraction reports

Input: `r10/analysis/out/heldout_confirm.json`, `models.<m>.read1` (primary unit: the first answer of each dialogue), for the seven held-out models (Sonnet, Haiku, Sol, Luna, DeepSeek, Qwen, Gemma). Policies: `planned` (verifier, planned gate), `relax_any` (relaxation policy), `soft` (soft type filter). Code definitions (read in `analyze.py`, `display_level`): per dialogue, miss = 1 when no displayed venue fits the brief (NT: any type; H: a hotel); with one answer per dialogue, every count is an integer number of dialogues.

| Outcome | Population | Field |
|---|---|---|
| Comparable dialogues | NT (no-type briefs), H (final-hotel briefs: the brief's final request sets `hotel`), G | `display.dialogues` |
| Original visible failures; original visible losses | NT; H | `display.original.failures_NT`, `losses_H` |
| Net visible failures avoided; gross failures ended / caused | NT | `display.<p>.net_avoided_NT`, `failures_ended_NT`, `failures_caused_NT` |
| Previously visible fitting hotels lost (gross losses: original shows a fitting hotel, policy does not) | H | `display.<p>.losses_caused_H` |
| Fitting hotels newly made visible (gross gains) | H | `display.<p>.losses_ended_H` |
| Net visible losses added (losses − gains) | H | `display.<p>.net_added_H` |
| Guesthouses newly shown on word-rule-stated hotel briefs | the 18 stated H briefs | relaxation policy only: `display.relax_any_on_H.stated_dialogues_changed` (a relaxed display was empty before, so any guesthouse in it is newly shown); planned gate and soft filter: **not computed** |
| Extra model calls | all first answers | historical held-out calls = conditional need = sum of `read1.verifier_answers` (the held-out run called the verifier only for answers with a hotel-only filter); relaxation and soft filter: 0 |
| Extra database searches (offline replay) | all first answers | round((`searches_per_answer.<p>` − 1) × `display.answers`); planned gate: 0 |

Checks: losses_caused_H − losses_ended_H = net_added_H; failures_ended_NT − failures_caused_NT = net_avoided_NT; the relaxation policy and the soft filter have losses_caused_H = 0 (the stored script also asserted per dialogue that these two policies add no visible failure or loss). Each value is printed beside the paper's existing held-out numbers that come from the same file (Table D6 display differences; 1.4% to 14.8% and 26.2% to 43.4% second searches; 533 calls).

Missing answers: Qwen has no valid first answer on 14 NT, 6 H and 2 G dialogues, Gemma on 1 NT; these dialogues are left out of every policy (same comparable set for all policies). The paper keeps its Qwen caveat.

No resampling, no new interval, no test. Output: `out/n1_heldout_stored.json`. Test: `test_n1_heldout_stored.py` (Sonnet by hand from the stored fields).
