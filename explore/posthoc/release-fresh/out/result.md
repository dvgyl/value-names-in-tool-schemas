# Fresh evaluation of the final release-test rule (R10-27)

Exploratory, fixed in the protocol before the run. Change = update − control (same batch), in points. L = 5. One look with all requests. Fresh requests: open 448 (1 answer per cell), specific 59 (10 answers per cell). Final rule (primary): symmetric index, sign condition, no pass from a zero-width interval, C = models that receive the update × 2 sets × 1 look. Original and revised rules (secondary): the index as run, without and with the sign condition.

## Decisions (flag / pass / hold)

| Update | C | Level | Model | Final rule | Revised rule | Original rule |
|---|---:|---:|---|---|---|---|
| repeat | 4 | 98.75% | luna | **pass** | pass | pass |
| repeat | 4 | 98.75% | sol | **pass** | pass | pass |
| field-order edit | 2 | 97.50% | luna | **hold** | hold | hold |
| paraphrase 1 | 2 | 97.50% | luna | **pass** | pass | pass |
| paraphrase 2 | 2 | 97.50% | luna | **hold** | hold | hold |
| full rename | 4 | 98.75% | luna | **flag** | flag | flag |
| full rename | 4 | 98.75% | sol | **flag** | flag | flag |

| Update | Final: flag / pass / hold | Revised | Original |
|---|---|---|---|
| repeat | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| field-order edit | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 |
| paraphrase 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| paraphrase 2 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 |
| full rename | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| harmless updates (repeat, field order, paraphrases) | 0 / 3 / 2 | 0 / 3 / 2 | 0 / 3 / 2 |

## Changes by set

| Update | Model | Set | Pairs | Change | Interval, symmetric (final) | Interval, as run | Up / down | Sign p | Final | Revised | Original |
|---|---|---|---:|---:|---|---|---|---:|---|---|---|
| repeat | luna | open | 448 | -0.7 | [-3.3, +2.0] | [-3.3, +2.0] | 11 / 14 | 0.6900 | within limits | within limits | within limits |
| repeat | luna | specific | 59 | -0.8 | [-2.9, +0.7] | [-2.9, +0.7] | 3 / 5 | 0.7266 | within limits | within limits | within limits |
| repeat | sol | open | 448 | +1.1 | [-1.1, +3.8] | [-1.1, +3.8] | 12 / 7 | 0.3593 | within limits | within limits | within limits |
| repeat | sol | specific | 59 | +1.4 | [+0.2, +2.9] | [+0.2, +2.9] | 6 / 0 | 0.0312 | within limits | within limits | within limits |
| field-order edit | luna | open | 448 | +3.6 | [+0.7, +6.7] | [+0.7, +6.7] | 26 / 10 | 0.0113 | unresolved | unresolved | unresolved |
| field-order edit | luna | specific | 59 | +4.1 | [+0.7, +9.0] | [+0.7, +9.0] | 7 / 2 | 0.1797 | unresolved | unresolved | unresolved |
| paraphrase 1 | luna | open | 448 | -1.1 | [-3.8, +1.6] | [-3.8, +1.6] | 12 / 17 | 0.4583 | within limits | within limits | within limits |
| paraphrase 1 | luna | specific | 59 | -1.0 | [-4.7, +3.1] | [-4.7, +2.9] | 4 / 5 | 1.0000 | within limits | within limits | within limits |
| paraphrase 2 | luna | open | 448 | -4.7 | [-7.6, -1.8] | [-7.6, -1.8] | 6 / 27 | 0.0003 | unresolved | unresolved | unresolved |
| paraphrase 2 | luna | specific | 59 | -3.9 | [-8.5, +0.2] | [-8.5, +0.2] | 2 / 8 | 0.1094 | unresolved | unresolved | unresolved |
| full rename | luna | open | 448 | -30.4 | [-35.9, -25.2] | [-35.9, -25.2] | 2 / 138 | 0.0000 | meets flag rule | meets flag rule | meets flag rule |
| full rename | luna | specific | 59 | -40.5 | [-54.7, -26.8] | [-54.7, -26.9] | 0 / 33 | 0.0000 | meets flag rule | meets flag rule | meets flag rule |
| full rename | sol | open | 448 | -28.1 | [-33.9, -22.5] | [-33.9, -22.5] | 0 / 126 | 0.0000 | meets flag rule | meets flag rule | meets flag rule |
| full rename | sol | specific | 59 | -33.2 | [-46.9, -19.5] | [-46.9, -19.7] | 0 / 26 | 0.0000 | meets flag rule | meets flag rule | meets flag rule |

## Predictions (fixed in R10-27)

| Prediction | Rule | Want | Decisions | Result |
|---|---|---|---|---|
| F1 | final | flag | {"full rename, luna": "flag", "full rename, sol": "flag"} | holds |
| F1 | revised | flag | {"full rename, luna": "flag", "full rename, sol": "flag"} | holds |
| F1 | original | flag | {"full rename, luna": "flag", "full rename, sol": "flag"} | holds |
| F2 | final | no flag | {"repeat, luna": "pass", "repeat, sol": "pass"} | holds |
| F2 | revised | no flag | {"repeat, luna": "pass", "repeat, sol": "pass"} | holds |
| F2 | original | no flag | {"repeat, luna": "pass", "repeat, sol": "pass"} | holds |
| F3 | final | no flag | {"field-order edit, luna": "hold"} | holds |
| F3 | revised | no flag | {"field-order edit, luna": "hold"} | holds |
| F3 | original | no flag | {"field-order edit, luna": "hold"} | holds |
| F4 | final | no flag | {"paraphrase 1, luna": "pass", "paraphrase 2, luna": "hold"} | holds |
| F4 | revised | no flag | {"paraphrase 1, luna": "pass", "paraphrase 2, luna": "hold"} | holds |
| F4 | original | no flag | {"paraphrase 1, luna": "pass", "paraphrase 2, luna": "hold"} | holds |

## Rates of a hotel value (valid reads)

| Update | Model | Set | Control | Update |
|---|---|---|---|---|
| repeat | luna | open | 34.4% (154/448) | 33.7% (151/448) |
| repeat | luna | specific | 65.8% (388/590) | 64.9% (382/589) |
| repeat | sol | open | 55.1% (247/448) | 56.2% (252/448) |
| repeat | sol | specific | 90.8% (536/590) | 92.2% (544/590) |
| field-order edit | luna | open | 34.4% (154/448) | 37.9% (170/448) |
| field-order edit | luna | specific | 65.8% (388/590) | 69.8% (412/590) |
| paraphrase 1 | luna | open | 34.4% (154/448) | 33.3% (149/448) |
| paraphrase 1 | luna | specific | 65.8% (388/590) | 64.7% (382/590) |
| paraphrase 2 | luna | open | 34.4% (154/448) | 29.7% (133/448) |
| paraphrase 2 | luna | specific | 65.8% (388/590) | 61.9% (365/590) |
| full rename | luna | open | 34.4% (154/448) | 4.0% (18/448) |
| full rename | luna | specific | 65.8% (388/590) | 25.3% (149/590) |
| full rename | sol | open | 55.1% (247/448) | 27.0% (121/448) |
| full rename | sol | specific | 90.8% (536/590) | 57.6% (340/590) |

## Read kinds per cell

- luna: t0 {"search": 1038}; trep {"search": 1037, "invalid: cut": 1}; tord {"search": 1037, "none": 1}; tpar {"search": 1038}; tpar2 {"search": 1038}; t1 {"search": 1037, "none": 1}
- sol: t0 {"search": 1038}; trep {"search": 1038}; t1 {"search": 1038}

## Selection

Pool counts: {"e7": 2874, "after_exclusions": 2320, "traveller_says_hotel": 1504, "eligible_open": 711, "eligible_specific": 296, "release_test_dialogues": 554, "release_test_outside_554": 0}.

## Money

Ledger list price of the R10-27 rows: 3.0255 USD.

- 2026-11-15T15:12:38+00:00 erk4_luna pilot: bound 0.03 USD, list price 0.0011 USD
- 2026-11-15T15:13:08+00:00 erk4_sol pilot: bound 0.26 USD, list price 0.0108 USD
- 2026-11-15T16:00:25+00:00 erk4_sol batch: bound 3.44 USD, list price 2.7395 USD
- 2026-11-15T16:04:36+00:00 erk4_luna batch: bound 0.35 USD, list price 0.2741 USD
- erk4_luna: {"bound": 0.35, "requests": 6228, "created": "2026-11-15T15:15:01.354921+00:00", "status": "completed", "request_counts": {"total": 6228, "completed": 6228, "failed": 0}}
- erk4_sol: {"bound": 3.44, "requests": 3114, "created": "2026-11-15T15:15:44.885755+00:00", "status": "completed", "request_counts": {"total": 3114, "completed": 3114, "failed": 0}}

## Checks

- Cross-check with r10/analysis/release_test.py: 7 of 7 model-update pairs equal.

## SHA-256 of the reused files

- `r10/analysis/release_test.py`: `da7b68c154ed3e44d69e1be0ed7aad7671123b896fd5cba15c8aa7097198021a`
- `r10/analysis/rtest_final9.py`: `5e98f0ec93609d5ffb6972c2a57bcba2b48c09c26f82eab94d3080491bd07f11`
- `verify.py of the independent check (not in this repository)`: `636bb367ccb475525f177fa5d4cfa0e5cbeb574606a5a22a5b9f078266f948c3`
- `verify_release.py of the independent check (not in this repository)`: `883dbcaf856a8b1704c1b77e29fa7bb1ccf66d0d5d8782166d6841db19f696d4`
- `verify_release2.py of the independent check (not in this repository)`: `2583c266454b79090e30d6253773a7473314208ce8a998e8cb5cbca69e464f26`
- `r10/analysis/release_analyze.py`: `416f5302b8f95c4dee0d2d5c9ede7bb8aad047550270aa7f941fdd9cd4c8f729`
- `r10/analysis/stats.py`: `c90eb62a84f69fe2c6352ed4a9d5d9aad9d6265765088f30ba8fc47d36f03982`
- `r9/natural/natural_analyze.py`: `275d0b99105c088857d22ef1e021bb5d0a46db30c6c1067251d853c03e16245e`
- `r9/natural/natural.py`: `a28868ae705282b5e9dd259d36c23953fd890b3273e7ed8b42f27da5d628b8c3`
- `r10/tools.py`: `7c3b562b04fab5c9683e6fc0579c771892acd77e018c67240bfc2497bfdbc5d2`
- `r10/control.py`: `bf4ac3f0886732e139a30501148d077b70f6bfba4e0870b2e3daa53c4d077934`
- `r10/harmless.py`: `4f4d4cddbbd5988005681d31fab2f2c1329fec892a8db93086cac4ecdf6854c1`
- `r10/harmless2.py`: `df30c41ef0efeb9469f22fadfa73614a503883d3a76e1aaf53c75e303e7e616b`
- `r10/fresh27.py`: `51ef3e5e8f5d65909e263da1e8c4f4578eb18114a27b3a734253eee706782ae7`
- `posthoc/release-fresh/analyze.py`: `295a158054bd7f6efae11f55ffc7c7c3b7d8a014c3c113bda9e948023ee91fa0`

## Post hoc: bootstrap sensitivity of the final-rule decisions

Post hoc (added on request after the design was fixed; not part of the primary analysis). Each final-rule decision recomputed on the same answers with 20,000 draws (seed 20261112) and with 2,000 draws and each of 20 other seeds (20261113 to 20261132). The primary decision comes first.

| Update | Model | Level | Primary (2,000 draws, seed 20261112) | 20,000 draws | 20 other seeds: flag / pass / hold | 20,000-draw intervals (open; specific) |
|---|---|---:|---|---|---|---|
| repeat | luna | 98.75% | **pass** | pass | 0 / 20 / 0 | [-3.6, +2.0]; [-2.9, +0.7] |
| repeat | sol | 98.75% | **pass** | pass | 0 / 20 / 0 | [-1.3, +3.6]; [+0.2, +2.9] |
| field-order edit | luna | 97.50% | **hold** | hold | 0 / 0 / 20 | [+0.7, +6.7]; [+0.5, +8.8] |
| paraphrase 1 | luna | 97.50% | **pass** | pass | 0 / 19 / 1 | [-3.8, +1.6]; [-4.9, +2.9] |
| paraphrase 2 | luna | 97.50% | **hold** | hold | 0 / 0 / 20 | [-7.6, -2.0]; [-8.5, +0.3] |
| full rename | luna | 98.75% | **flag** | flag | 20 / 0 / 0 | [-35.9, -25.0]; [-54.7, -26.6] |
| full rename | sol | 98.75% | **flag** | flag | 20 / 0 / 0 | [-33.5, -23.0]; [-47.3, -19.5] |
