# SPEC T2: the floor of the sign condition

Written: 2026-11-15, 22:54 UTC (`date -u` gave 22:53:59 just before writing), before any T2 output.

Status label in the paper: **analytical consequence of the stated rule** (not a result of new data; not a general theorem). The descriptive counts from the existing simulation that support it are **post hoc**.

## The rule (Appendix H, steps 4, 6 and 7 of the paper; `posthoc/release-sim/rules.py` `sign_p`)

- Per request, the observed difference is new minus old (average over the request's scorable answers). r = observed positive differences, f = observed negative differences, d = r + f. A difference of exactly zero is a tie and is dropped.
- Two-sided exact sign test: p = min(1, 2 × P(X ≤ min(r, f))), X ~ Binomial(d, 1/2); p = 1 when d = 0.
- A set can meet the flag condition only if p ≤ 0.05/C.

## Derivation to check (numerically, with exact rational arithmetic)

1. For d ≥ 1, the smallest p over all (r, f) with r + f = d is p_min(d) = 2 × (1/2)^d = 2^(1−d), reached when every nonzero difference has the same sign (min(r, f) = 0). Check by enumeration for d = 1 to 30.
2. Necessary condition for a flag: 2^(1−d) ≤ 0.05/C, that is, d ≥ d_min(C) = ceil(1 + log2(C / 0.05)). Check by enumeration and by the closed form, for every C that the paper uses: C = 2 (97.5%), 4 (98.75%), 6 (99.17%), 10 (99.5%) and 12 (99.58%).
3. The p_min table for d = 5 to 9, as exact fractions and decimals.
4. Change floor with one answer per request: each nonzero difference is ±100 points, so d_min(C) differences in one direction on n requests give a mean change of at least 100 × d_min(C) / n points. Check the existing paper values for n = 59: 13.6 points at C = 4 and 15.3 points at C = 10. With m answers per request, a nonzero difference can be as small as 100/m points, so the change floor is 100 × d_min / (m n) (for m = 10 and n = 59: 1.4 points at C = 4), below L.
5. Necessary, not sufficient: mixed directions give larger p; the interval and |change| ≥ L conditions must also hold.

## Observed against truly affected requests (descriptive, from existing outputs only)

- From `posthoc/release-sim/out/sim.json` (no new simulation): for the sparse configurations of the paper design (`S-sparse|*|sparse ±8 specific|n59m10`), the mean number of truly changed specific requests per trial (`effect_info_mean["specific:changed"]`) and the mean number of specific requests with an observed nonzero difference per trial (`mean_changed_requests["specific"]`), for each profile. Also, for comparison, the zero-change configuration of each profile.
- The paper may use these means to state that six truly affected requests do not imply six observed nonzero differences. No per-trial distribution is computed (it is not stored), and no new trial is run.

## Outputs

- `posthoc/checks/release-rule/out/t2_signfloor.json` and `t2_signfloor.md`.
- Paper: a short paragraph in Section 7 and the derivation in Appendix H, merged with the existing paragraph "The floor of the sign condition".

## Tests

`test_t2.py`: hand cases (r = 5, f = 0 gives p = 0.0625; r = 7, f = 0 gives 0.015625; r = 8, f = 0 gives 0.0078125; r = 21, f = 5 gives the paper's p = 0.0025 to 4 decimals; r = 4, f = 12 gives 0.0768 to 4 decimals; r = 0, f = 0 gives 1), the closed form against enumeration for every C, and the 13.6 and 15.3 point floors.
