## Symmetric search-harm measure (exploratory, post hoc)

Both sides replay the answer's own search and look at the first 5 rows. Visible failure: no venue that fits a no-type brief (807 dialogues). Visible loss: no hotel that fits a hotel brief (233 dialogues). Ratio: extra visible losses per visible failure avoided, against F0; 95% cluster bootstrap interval.

| Model | Arm | Visible failure (F0 -> arm) | Visible loss (F0 -> arm) | Ratio, subset weights | Ratio, group weights |
|---|---|---|---|---|---|
| sonnet | b_list | 17.3% -> 16.6% | 15.0% -> 15.5% | 0.17 [-1.00, no benefit] | 0.32 [-1.90, no benefit] |
| sonnet | b_shot | 17.3% -> 17.7% | 15.0% -> 15.5% | no benefit [-1.00, no benefit] | no benefit [-1.90, no benefit] |
| sonnet | b_evidence | 17.3% -> 20.9% | 15.0% -> 14.2% | no benefit [no benefit, no benefit] | no benefit [no benefit, no benefit] |
| sonnet | verify | 17.3% -> 12.8% | 15.0% -> 18.5% | 0.22 [0.08, 0.43] | 0.41 [0.15, 0.81] |
| sonnet | verify_no_only (post hoc) | 17.3% -> 14.0% | 15.0% -> 16.3% | 0.11 [0.00, 0.29] | 0.21 [0.00, 0.54] |
| haiku | b_list | 15.4% -> 16.0% | 17.8% -> 18.7% | no benefit [-0.40, no benefit] | no benefit [-0.76, no benefit] |
| haiku | b_shot | 15.4% -> 15.5% | 17.8% -> 20.4% | no benefit [0.05, no benefit] | no benefit [0.09, no benefit] |
| haiku | b_evidence | 15.4% -> 18.4% | 17.8% -> 18.9% | no benefit [no benefit, no benefit] | no benefit [no benefit, no benefit] |
| haiku | verify | 15.4% -> 15.3% | 17.8% -> 19.7% | 9.00 [1.33, no benefit] | 17.09 [2.53, no benefit] |
| haiku | verify_no_only (post hoc) | 15.4% -> 15.4% | 17.8% -> 18.9% | no benefit [no benefit, no benefit] | no benefit [no benefit, no benefit] |
| sol | b_list | 26.6% -> 27.5% | 12.4% -> 12.0% | no benefit [-1.00, no benefit] | no benefit [-1.90, no benefit] |
| sol | b_shot | 26.6% -> 18.2% | 12.4% -> 14.6% | 0.07 [-0.01, 0.16] | 0.14 [-0.03, 0.31] |
| sol | b_evidence | 26.6% -> 27.6% | 12.4% -> 12.9% | no benefit [-0.25, no benefit] | no benefit [-0.47, no benefit] |
| sol | verify | 26.6% -> 14.4% | 12.4% -> 14.2% | 0.04 [0.01, 0.08] | 0.08 [0.02, 0.16] |
| sol | verify_no_only (post hoc) | 26.6% -> 15.4% | 12.4% -> 12.4% | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| luna | b_list | 23.2% -> 21.1% | 18.2% -> 23.8% | 0.76 [0.29, 2.46] | 1.45 [0.56, 4.67] |
| luna | b_shot | 23.2% -> 23.7% | 18.2% -> 20.2% | no benefit [-0.25, no benefit] | no benefit [-0.47, no benefit] |
| luna | b_evidence | 23.2% -> 41.9% | 18.2% -> 18.2% | no benefit [no benefit, no benefit] | no benefit [no benefit, no benefit] |
| luna | verify | 23.2% -> 18.7% | 18.2% -> 22.1% | 0.25 [0.11, 0.46] | 0.47 [0.21, 0.87] |
| luna | verify_no_only (post hoc) | 23.2% -> 20.1% | 18.2% -> 20.2% | 0.18 [0.04, 0.40] | 0.34 [0.08, 0.76] |
| opus | b_list | 12.1% -> 11.8% | 12.4% -> 10.7% | -1.33 [-5.00, no benefit] | -2.53 [-9.50, no benefit] |
| opus | verify | 12.1% -> 9.5% | 12.4% -> 13.7% | 0.14 [0.00, 0.38] | 0.27 [0.00, 0.73] |
| opus | verify_no_only (post hoc) | 12.1% -> 9.9% | 12.4% -> 12.4% | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| astra | b_list | 26.3% -> 24.2% | 12.4% -> 12.9% | 0.06 [-0.16, 0.33] | 0.11 [-0.30, 0.63] |
| astra | verify | 26.3% -> 13.0% | 12.4% -> 15.5% | 0.07 [0.02, 0.12] | 0.12 [0.04, 0.22] |
| astra | verify_no_only (post hoc) | 26.3% -> 14.9% | 12.4% -> 12.4% | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
