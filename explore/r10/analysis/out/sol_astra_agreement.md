## Same answers of two models on the repair dialogues (post hoc)

No model call. Read 1 of each dialogue, on the 2,029 dialogues of experiment B (groups S1t 994, S3 490, S2 545). Same text: the two answer texts are equal, character for character. Same value: both answers parse and give the same `type` (original form; null is a value) or the same `answer` (verifier).

| Pair | Same text | Same value |
|---|---|---|
| Sol and Astra, original form | 1,885 of 2,029 (92.9%) | 1,977 of 2,029 (97.4%) |
| Sonnet and Opus, original form (reference) | 1,356 of 2,029 (66.8%) | 1,734 of 2,029 (85.5%) |
| Sol and Astra, verifier | 1,853 of 2,029 (91.3%) | 1,853 of 2,029 (91.3%) |

### By group

| Pair | Group | Same text | Same value |
|---|---|---|---|
| Sol and Astra, original form | S1t | 921 of 994 (92.7%) | 964 of 994 (97.0%) |
| Sol and Astra, original form | S3 | 459 of 490 (93.7%) | 482 of 490 (98.4%) |
| Sol and Astra, original form | S2 | 505 of 545 (92.7%) | 531 of 545 (97.4%) |
| Sonnet and Opus, original form (reference) | S1t | 689 of 994 (69.3%) | 857 of 994 (86.2%) |
| Sonnet and Opus, original form (reference) | S3 | 361 of 490 (73.7%) | 444 of 490 (90.6%) |
| Sonnet and Opus, original form (reference) | S2 | 306 of 545 (56.1%) | 433 of 545 (79.4%) |
| Sol and Astra, verifier | S1t | 899 of 994 (90.4%) | 899 of 994 (90.4%) |
| Sol and Astra, verifier | S3 | 490 of 490 (100.0%) | 490 of 490 (100.0%) |
| Sol and Astra, verifier | S2 | 464 of 545 (85.1%) | 464 of 545 (85.1%) |

Inputs: Sol and Astra, original form: erb_sol against erg_astra, cell f0; Sonnet and Opus, original form (reference): erb_sonnet against ere_opus, cell f0; Sol and Astra, verifier: erb_sol against erx_b1_astra, erx_b2_astra, erx_b3_astra, cell verify.
