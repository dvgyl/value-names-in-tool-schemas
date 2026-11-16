# Release tests of a field-order change and a second paraphrase (R10-22)

Exploratory, fixed in the protocol before the run. Change = update − control (a fresh control in the same batch), in points. L = 5. One look with all requests. Levels: (d) field order 98.75%, (e) second paraphrase 98.75%. First rule: the R10-6 code. Revised rule: Appendix I with the exact sign condition (post hoc in the paper).

## Decisions

| Model | Update | Set | Pairs | Change | Interval | Up / down | Sign p | First rule | Revised rule |
|---|---|---|---:|---:|---|---|---:|---|---|
| sol | (d) field order | open | 448 | -1.8 | [-3.8, +0.0] | 2 / 10 | 0.0386 | absent | within limits |
| sol | (d) field order | specific | 59 | -1.2 | [-5.8, +3.4] | 5 / 8 | 0.5811 | unresolved | unresolved |
| sol | (d) field order | **model** | | | | | | **hold** | **hold** |
| sol | (e) second paraphrase | open | 448 | -0.2 | [-2.5, +1.8] | 6 / 7 | 1.0000 | absent | within limits |
| sol | (e) second paraphrase | specific | 59 | -0.5 | [-4.6, +3.7] | 5 / 8 | 0.5811 | absent | within limits |
| sol | (e) second paraphrase | **model** | | | | | | **pass** | **pass** |
| luna | (d) field order | open | 448 | +3.8 | [+1.1, +6.7] | 22 / 5 | 0.0015 | unresolved | unresolved |
| luna | (d) field order | specific | 59 | +3.9 | [-2.0, +11.0] | 9 / 5 | 0.4240 | unresolved | unresolved |
| luna | (d) field order | **model** | | | | | | **hold** | **hold** |
| luna | (e) second paraphrase | open | 448 | -1.1 | [-4.0, +1.6] | 10 / 15 | 0.4244 | absent | within limits |
| luna | (e) second paraphrase | specific | 59 | -5.9 | [-12.2, -1.0] | 4 / 12 | 0.0768 | flag-worthy | unresolved |
| luna | (e) second paraphrase | **model** | | | | | | **flag** | **hold** |

## Predictions

| Prediction | Rule | Decisions | Result |
|---|---|---|---|
| K4 | first | {"sol": "hold", "luna": "hold"} | holds |
| K4 | revised | {"sol": "hold", "luna": "hold"} | holds |
| K5 | first | {"sol": "pass", "luna": "flag"} | fails |
| K5 | revised | {"sol": "pass", "luna": "hold"} | holds |

## Descriptions: rates of a hotel value (valid reads), the guesthouse set, trade, blocking

| Model | Update | Set | Control | Update | Guesthouse-set change |
|---|---|---|---|---|---|
| sol | (d) | open | 35.3% (158/448) | 33.5% (150/448) |  |
| sol | (d) | specific | 83.2% (491/590) | 82.0% (484/590) |  |
| sol | (d) | guesthouse | 76.6% (36/47) | 78.7% (37/47) | +2.1 |
| sol | (e) | open | 35.3% (158/448) | 35.0% (157/448) |  |
| sol | (e) | specific | 83.2% (491/590) | 82.7% (488/590) |  |
| sol | (e) | guesthouse | 76.6% (36/47) | 76.6% (36/47) | +0.0 |
| luna | (d) | open | 17.2% (77/448) | 21.0% (94/448) |  |
| luna | (d) | specific | 36.1% (213/590) | 40.0% (236/590) |  |
| luna | (d) | guesthouse | 40.4% (19/47) | 53.2% (25/47) | +12.8 |
| luna | (e) | open | 17.2% (77/448) | 16.1% (72/448) |  |
| luna | (e) | specific | 36.1% (213/590) | 30.2% (178/590) |  |
| luna | (e) | guesthouse | 40.4% (19/47) | 36.2% (17/47) | -4.3 |

| Model | Update | Trade: wrong removed, correct lost, ratio | Blocking filters, open set: control; update |
|---|---|---|---|
| sol | (d) | 8.0, 0.7, 0.09 | 17.9% (80/448); 17.4% (78/448) |
| sol | (e) | 1.0, 0.3, 0.30 | 17.9% (80/448); 18.5% (83/448) |
| luna | (d) | -17.0, -2.3, not defined | 8.3% (37/448); 10.3% (46/448) |
| luna | (e) | 5.0, 3.5, 0.70 | 8.3% (37/448); 7.8% (35/448) |

Fresh control against the R10-20 control of the same model (another batch; 98.75% interval; description):

| Model | Set | Pairs | Change | Interval | Up / down |
|---|---|---:|---:|---|---|
| sol | open | 448 | -0.9 | [-2.5, +0.7] | 2 / 6 |
| sol | specific | 59 | -1.2 | [-4.7, +2.5] | 5 / 9 |
| sol | guesthouse | 47 | +0.0 | [-8.5, +8.5] | 1 / 1 |
| luna | open | 448 | -2.9 | [-5.4, -0.7] | 2 / 15 |
| luna | specific | 59 | +0.7 | [-1.0, +2.5] | 6 / 3 |
| luna | guesthouse | 47 | -6.4 | [-17.0, +0.0] | 0 / 3 |

Read kinds per cell:

- sol: t0 {"search": 1085}; tord {"search": 1085}; tpar2 {"search": 1085}
- luna: t0 {"search": 1085}; tord {"search": 1084, "none": 1}; tpar2 {"search": 1085}
