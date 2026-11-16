# SPEC N3: check of the Table D3 reproduction claim (the paper)

Written: 2026-11-15 22:58 UTC, before the check script ran. Status in the paper: reporting correction (Table D3 is descriptive; no status label changes).

## Question

The caption of Table D3 says: "Applying the trade formula in Appendix C to these counts exactly reproduces the verifier rows of Table D1." Table D3 shows only the no-type group and the hotel group. Table D1 also counts the guesthouse group as unsupported. Does the claim hold (a) with the counts that D3 shows now, and (b) with the guesthouse-group counts added?

## Inputs (stored outputs only; no em* folder, no sealed file, no key file)

- `r10/analysis/out/b_hotel_only.json` (stored output of `b_analyze.py --hotel-only`, the main count of Table D1). Per model (Sonnet, Haiku, Sol, Luna, Opus, Astra):
  - `verify_table["S1t, baseline hotel only"]`, `["S3, baseline hotel only"]`, `["S2, baseline hotel only"]`: verifier answers (yes, no, unclear) for original answers with a hotel-only filter, over answer pairs where the original answer and the verifier answer with the same read number are both valid. S1t = no-type group (994), S3 = guesthouse group (490), S2 = hotel group (545).
  - `rates.f0[G]` = (k0, n0): original hotel-only answers and valid original answers per group. `rates.verify[G]` and `rates["verify_no_only (post hoc)"][G]` = (k1, n1): hotel-only answers after the gate, and valid answer pairs.
  - `trade.verify` and `trade["verify_no_only (post hoc)"]`: the stored point values (removed, lost, ratio, removed_share).
- the paper: the printed Table D1 verifier rows (Removed %, Decreases − increases, Ratio, Meets) and Table D3 rows.

## Definitions

For each model and gate, with V_g = yes + no + unclear of group g (the D3 "Values"), the gate keeps K_g = yes (planned gate) or yes + unclear (clear-no gate), and N = 994, 490, 545:

- Answer bases: n0_g = valid original answers of group g; n1_g = valid answer pairs of group g (from `rates`).
- Check 0 (data identity): V_g equals k0_g (every original hotel-only answer has a valid verifier answer), and K_g equals k1_g.
- Trade formula of Appendix C: R = sum over g in {no-type, guesthouse} of (V_g / n0_g − K_g / n1_g) × N_g; L = (V_h / n0_h − K_h / n1_h) × 545; share removed = R / sum over the two unsupported groups of (V_g / n0_g) × N_g; ratio = L / R.
- Decreases (as Table D1 prints them; one-answer models: counts; two-answer models: halves): removed values = (V_g − K_g) / r summed over the two unsupported groups, lost values = (V_h − K_h) / r, where r = answers per dialogue (1 or 2).
- Variant (a), D3 as printed: the no-type group alone for R (the guesthouse group left out).
- Variant (b), all three groups with the exact bases n0, n1.
- Variant (c), all three groups with the simple bases n0 = n1 = r × N (a reader who ignores the three invalid Luna verifier answers).

## Decision rule (fixed now)

- The problem is confirmed if variant (a) differs from a printed Table D1 point value for at least one model and gate.
- Restore a reproduction claim only if variant (b) reproduces every printed point value of the twelve verifier rows of Table D1 (removed share to one decimal, decreases, ratio to two decimals, and the verdict at the point estimates). The restored claim names the point values only: the 95% intervals need the bootstrap and cannot come from counts.
- If variant (b) fails anywhere, use the minimal caption that claims only what D3 shows.
- If (b) holds but (c) fails anywhere, the caption must state the answer bases that make the reproduction exact.

## Outputs

`posthoc/checks/repair-display/out/n3_d3_check.json` and a printed table. Test: `test_n3_d3_check.py` (Sonnet planned gate by hand: no-type 96 + 76 = 172, guesthouse 14 + 1 = 15, R = 187, L = 99 + 144 = 243, ratio 1.30, share 187 / 203 = 92.1%; variant (a) ratio 243 / 172 = 1.41).
