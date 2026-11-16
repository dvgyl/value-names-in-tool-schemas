# SPEC T3 addendum: rows of the appendix table (presentation only)

Written: 2026-11-15, 23:06 UTC (`date -u` gave 23:05:48 just before writing), **after** the T3 output (`out/t3_bootstrap.*`, finished 23:04:15 UTC). `SPEC-T3-bootstrap-precision.md` is unchanged and stays in force.

## Why

The row rule of the spec (rule-decisions whose 100,000-draw decision differs from the 2,000-draw decision for at least one seed, or whose five seeds disagree) selects one rule-decision of 187. A table with one row does not show the reader how the other decisions that the paper already calls seed-dependent behave with more draws.

## What is added (no analysis changes)

The appendix table also lists the rule-decisions that the paper text **before T3** names as dependent on the bootstrap seed at 2,000 draws (Appendix L "Bootstrap tails" and Appendix H "Fresh-test results" of the master backed up in `stage3_tools/trust/pre_final_plan/`):

1. Luna's repeat, final rule, 99.5% (the row that the spec rule also selects);
2. Gemma's repeat, final rule, 99.5% ("passes ... with 18 of the 20 seeds");
3. and 4. the two original-rule false flags on stored Sonnet answers, 98.75% ("remains a flag with 15 of the 20 seeds");
5. Luna's paraphrase 1 in the fresh test, final rule, 97.5% ("1 of 20 other seeds holds paraphrase 1").

This list comes from the earlier paper text, not from the T3 values. The one-line count of all other rule-decisions stays as in the spec. No decision, seed, draw count, level, index or boundary definition changes. The report states this addendum.
