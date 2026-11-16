# SPEC N2: one verifier-gated soft type filter (the paper)

Written: 2026-11-15 23:00 UTC, before any code of this analysis ran and before any outcome of this policy was computed. Status in the paper: **a new exploratory policy, defined before this analysis, evaluated on reused development dialogues** (the training dialogues of Table 3, which the paper already analysed). It is not a fresh or held-out test. One policy, one evaluation; the gate is not changed after the results.

## Why the development dialogues

N1 found that the held-out original answers exist only in `em*` folders, so no policy can be replayed on the held-out dialogues (SPEC-N1-heldout.md). The plan then allows the development dialogues of Table 3, labelled exploratory.

## Inputs (stored outputs only)

- Development answers of the nine models of Table 3 (Sonnet, Haiku, Sol, Luna, Opus, Astra, DeepSeek, Qwen, Gemma), loaded with `verify.py of the independent check (not in this repository)` (`V.gots`), whose loader refuses any folder that starts with `em`. Display code: `r10/analysis/repair_rule.py` (`show`, `sees`, `base_reads`, `policy_answer`), imported without change. Word rule: `clear_rule.label`. Venue data: `gold.hotel_db()`.
- Stored comparator values: `r10/analysis/out/repair_rule.json` (`part4_display`) and `posthoc/checks/repair-counts/out/plan_counts.json` (`part_a`), for a self-check and for the comparator gross transitions.

## Population (as Table 3)

- NT: the 807 development dialogues whose brief and label set no type. H: the 233 whose brief and label set `hotel`; stated: the 89 H dialogues that the word rule marks as requiring a hotel.
- Base answers: a read counts only when its original-form answer and its verifier answer (same dialogue, same read) are both valid (`base_reads`), so every policy uses the same answers. A dialogue with no base answer is left out of every policy (Table 3: Qwen 801 NT and 227 H, Gemma 806 NT).
- Missingness reported per model: answers left out because the original answer or the verifier answer is invalid, and dialogues without a base answer.

## The policy G (frozen)

For each base answer with original fields f0 and verifier answer v (valid by construction):

1. D0 = the original display: the first five venues of `bs.search(db, f0)`, in venue-data order (alphabetical).
2. If the `type` of f0 is not a hotel-only filter (a list that holds `hotel` and not `guesthouse`), return D0.
3. If D0 has five venues, return D0.
4. If v is "yes" or "unclear", return D0. (Invalid or missing answers cannot occur in the base; operationally they would also return D0.)
5. If v is "no": run one second search with only the type filter removed (`{**f0, "type": None}`), and append its venues that are not already in D0, in venue-data order, until the display has five venues or no candidates remain. Every venue of D0 keeps its position.

The policy never reads the brief, the label or the word rule. A model call is needed only in steps 4 to 5 (the trigger: a hotel-only filter and fewer than five displayed venues). A second search happens only in step 5.

## Outcomes (dialogue-level; models with two answers contribute the mean of their answers, as in Table 3)

- Net visible failures avoided on NT: sum over dialogues of (original miss − G miss), miss = 1 if no displayed venue fits the brief. Also gross: failures ended and caused.
- On H: gross losses (sum of max(G miss − original miss, 0), miss = no displayed fitting hotel), gross gains (sum of max(original miss − G miss, 0)), net added = losses − gains.
- Guesthouses newly shown on the stated H briefs: per answer, 1 if the original display shows no guesthouse and the G display shows at least one; dialogue mean; summed over the 89 stated briefs (Qwen 87). Same definition as `plan_counts.py` part A (the Table 3 column "Guesthouse shown"). Also reported, secondary: the same count on the not-stated H briefs.
- Model calls: historical = one verifier call per base answer (the development runs called the verifier for every answer); conditional = the share of base answers on NT and H that meet the trigger (hotel-only filter and fewer than five displayed venues).
- Database searches (offline replay): share of base answers on NT and H with a second search (trigger and "no").
- Paired differences on NT, in dialogues: G − verifier (planned gate) and G − soft type filter, net failures avoided. 95% interval: `stats.cluster_bootstrap` over the NT dialogues, 2,000 draws, seed 20261112, each dialogue keeps its answers (the method of Table 3, `repair_limits.py` part 2).
- Display loss ratio: not computed (G adds no visible loss by construction, so the ratio has no meaning beyond the counts).

## Checks

- Self-check: the same code reproduces the stored Table 3 values for the verifier, the relaxation policy and the soft filter (net failures avoided, net losses added; `repair_rule.json`) and the stored "Guesthouse shown" counts (`plan_counts.json`), for every model. If a check fails, stop and report.
- Structure: for every base answer on NT and H, D0 is a prefix of the G display and of the soft-filter display (same venues in the same first positions). Count violations (expected 0). G gross losses on H must be 0.
- G acts only on answers where the soft filter acts with a hotel-only filter; on every answer, the G display is either D0 or the soft-filter display. Count both cases.

## Decision rule and reporting (fixed now)

Report the result whatever it is: one appendix row group for G (nine models: net failures avoided with the two paired differences, H gross losses / gains, guesthouses newly shown on stated briefs, conditional calls, second searches), comparators by reference to Table 3, and at most one main-text sentence. No other gate (for example "no" or "unclear"), no other display size, no other set. The wording follows the numbers; a policy that avoids fewer failures than the soft filter while showing fewer guesthouses is reported as a trade-off, not as a success or failure.

Outputs: `out/n2_gated_soft.json`, printed table. Test: `test_n2_gated_soft.py` (constructed venue lists and answers: the gate keeps D0 after "yes", "unclear", a non-hotel-only filter and a full display; it appends in order after "no"; prefix check).
