# Base distributions (beta-binomial fit, unchanged tool or form)

Per request: the hotel values k among the m valid answers, pooled over the stored sources below. Fit: Beta(a, b) for the per-request probability, by maximum likelihood (Nelder-Mead on log a, log b). Check: observed and predicted numbers of requests with no hotel value, only hotel values and a mix, among the requests with the modal number of answers.

| Profile | Set | Requests | Answers | Rate | a | b | Mean | Modal m | All 0 obs / pred | All m obs / pred | Mixed obs / pred |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| haiku | open | 448 | 2686 | 6.9% | 0.0111 | 0.1474 | 7.0% | 6 | 406 / 405.2 | 23 / 22.7 | 17 / 18.1 |
| haiku | specific | 59 | 1413 | 13.3% | 0.0260 | 0.1760 | 12.9% | 24 | 47 / 46.2 | 4 / 4.0 | 7 / 7.8 |
| deepseek | open | 448 | 1343 | 18.7% | 0.0500 | 0.2167 | 18.7% | 3 | 342 / 341.2 | 62 / 62.8 | 43 / 43.0 |
| deepseek | specific | 59 | 1768 | 34.0% | 0.1342 | 0.2512 | 34.8% | 30 | 23 / 23.5 | 7 / 8.2 | 28 / 26.4 |
| sol | open | 448 | 3136 | 35.5% | 0.0226 | 0.0412 | 35.5% | 7 | 274 / 274.0 | 144 / 144.0 | 30 / 30.0 |
| sol | specific | 59 | 2006 | 83.7% | 0.2918 | 0.0612 | 82.7% | 34 | 4 / 3.4 | 39 / 39.0 | 16 / 16.7 |

- haiku: era1 read 1 (read 1), era1 read 2 (read 2), erm (read 1), ers (read 1), erc (all), erc2 (all)
- deepseek: erk_deepseek p0, erk_deepseek prep, erk3_deepseek p0
- sol: era1 read 1 (read 1), era1 read 2 (read 2), fill read 3 (read 3), erp (read 1), erk_sol t0, erk_sol trep, erk2_sol t0
