# Replication of the two paraphrase flags (R10-24)

Exploratory, fixed in the protocol before the run. Change = update − control (a fresh control in the same batch or run), in points. L = 5. One look. Levels: DeepSeek 99.17%, Luna 98.75% (the levels of the flagged decisions).

## Decisions of the replication

| Model | Update | Set | Pairs | Change | Interval | Up / down | Sign p | First rule | Revised rule | 95% interval |
|---|---|---|---:|---:|---|---|---:|---|---|---|
| deepseek | (b) | open | 447 | +0.9 | [-2.7, +4.3] | 18 / 14 | 0.5966 | absent | within limits | [-1.6, +3.4] |
| deepseek | (b) | specific | 59 | +1.1 | [-1.9, +4.1] | 13 / 10 | 0.6776 | absent | within limits | [-1.1, +3.4] |
| deepseek | (b) | **model** | | | | | | **pass** | **pass** | |
| luna | (e) | open | 448 | -1.3 | [-4.2, +1.3] | 9 / 15 | 0.3075 | absent | within limits | [-3.6, +0.9] |
| luna | (e) | specific | 59 | +0.5 | [-2.9, +3.9] | 7 / 6 | 1.0000 | absent | within limits | [-2.2, +3.2] |
| luna | (e) | **model** | | | | | | **pass** | **pass** | |

## Categories and predictions

| Model | Category, first rule | Category, revised rule | Original flag against the measured change (first / revised) |
|---|---|---|---|
| deepseek | noise | noise | wrong flag / wrong flag |
| luna | noise | noise | wrong flag / no flag to judge |

| Prediction | Result |
|---|---|
| P1 | {"model": "deepseek", "categories": {"first": "noise", "revised": "noise"}, "result": "holds"} |
| P2 | {"model": "luna", "categories": {"first": "noise", "revised": "noise"}, "result": "holds"} |

## The original flagged run and the pooled estimate (descriptions)

| Model | Set | Original change | Original interval | Original decision (first / revised) | Pooled change | Pooled interval |
|---|---|---:|---|---|---:|---|
| deepseek | open | +1.1 | [-2.5, +4.5] | flag / flag | +1.0 | [-1.8, +3.6] |
| deepseek | specific | +5.9 | [+1.5, +10.7] | flag / flag | +3.5 | [+0.6, +6.6] |
| luna | open | -1.1 | [-4.0, +1.6] | flag / hold | -1.2 | [-3.6, +0.8] |
| luna | specific | -5.9 | [-12.2, -1.0] | flag / hold | -2.7 | [-7.0, +0.7] |

Read kinds per cell:

- deepseek: p0 {"search": 1084, "invalid: cut": 1}; ppar {"search": 1083, "invalid: cut": 2}
- luna: t0 {"search": 1085}; tpar2 {"search": 1085}
