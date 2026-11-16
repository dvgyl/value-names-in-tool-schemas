## Tool calls at the first request: type outputs and the hotel-only outcome (post hoc)

No model call. Valid reads of a_analyze.load. t0: original tool; t1: renamed tool (values mapped back).

### Hotel-only outcome on the 59 prefixes whose brief sets hotel

| Model | t0 | t1 | Change, points [95%] | Lower / higher | Sign p |
|---|---|---|---|---|---|
| sonnet | 51.4% (91/177) | 4.5% (8/177) | -46.9 [-59.9, -35.0] | 31 / 0 | 9.3e-10 |
| haiku | 9.5% (11/116) | 1.7% (2/118) | -7.8 [-15.5, -1.7] | 5 / 0 | 0.062 |
| opus | 69.5% (82/118) | 19.5% (23/118) | -50.0 [-61.9, -38.1] | 34 / 0 | 1.2e-10 |
| sol | 80.8% (143/177) | 23.7% (42/177) | -57.1 [-68.4, -45.2] | 38 / 0 | 7.3e-12 |
| luna | 35.6% (42/118) | 1.7% (2/118) | -33.9 [-46.6, -22.0] | 23 / 0 | 2.4e-07 |
| astra | 91.5% (54/59) | 11.9% (7/59) | -79.7 [-89.8, -69.5] | 47 / 0 | 1.4e-14 |

### Type outputs (valid reads)

| Model | Tool and group | hotel only | both types | guesthouse only | null | any | other | non-call |
|---|---|---|---|---|---|---|---|---|
| sonnet | t0 brief hotel | 91 | 0 | 0 | 84 | 0 | 0 | 2 |
| sonnet | t0 brief no type | 298 | 0 | 3 | 1033 | 7 | 2 | 1 |
| sonnet | t0 brief guesthouse | 73 | 3 | 12 | 53 | 0 | 0 | 0 |
| sonnet | t1 brief hotel | 8 | 0 | 0 | 168 | 0 | 0 | 1 |
| sonnet | t1 brief no type | 41 | 0 | 4 | 1285 | 10 | 1 | 3 |
| sonnet | t1 brief guesthouse | 12 | 3 | 12 | 113 | 0 | 0 | 1 |
| haiku | t0 brief hotel | 11 | 2 | 0 | 100 | 1 | 1 | 1 |
| haiku | t0 brief no type | 64 | 0 | 10 | 734 | 41 | 16 | 29 |
| haiku | t0 brief guesthouse | 13 | 2 | 9 | 63 | 1 | 4 | 2 |
| haiku | t1 brief hotel | 2 | 1 | 1 | 106 | 3 | 3 | 2 |
| haiku | t1 brief no type | 12 | 0 | 11 | 794 | 24 | 19 | 35 |
| haiku | t1 brief guesthouse | 7 | 2 | 9 | 69 | 3 | 1 | 3 |
| opus | t0 brief hotel | 82 | 2 | 0 | 34 | 0 | 0 | 0 |
| opus | t0 brief no type | 232 | 0 | 0 | 654 | 3 | 7 | 0 |
| opus | t0 brief guesthouse | 54 | 2 | 8 | 30 | 0 | 0 | 0 |
| opus | t1 brief hotel | 23 | 1 | 0 | 94 | 0 | 0 | 0 |
| opus | t1 brief no type | 36 | 0 | 0 | 849 | 1 | 10 | 0 |
| opus | t1 brief guesthouse | 17 | 2 | 8 | 67 | 0 | 0 | 0 |
| sol | t0 brief hotel | 143 | 0 | 0 | 34 | 0 | 0 | 0 |
| sol | t0 brief no type | 479 | 0 | 0 | 856 | 9 | 0 | 0 |
| sol | t0 brief guesthouse | 106 | 3 | 12 | 20 | 0 | 0 | 0 |
| sol | t1 brief hotel | 42 | 0 | 0 | 135 | 0 | 0 | 0 |
| sol | t1 brief no type | 157 | 0 | 0 | 1178 | 9 | 0 | 0 |
| sol | t1 brief guesthouse | 39 | 3 | 12 | 87 | 0 | 0 | 0 |
| luna | t0 brief hotel | 42 | 0 | 0 | 76 | 0 | 0 | 0 |
| luna | t0 brief no type | 167 | 1 | 11 | 709 | 8 | 0 | 0 |
| luna | t0 brief guesthouse | 40 | 2 | 10 | 41 | 1 | 0 | 0 |
| luna | t1 brief hotel | 2 | 0 | 0 | 116 | 0 | 0 | 0 |
| luna | t1 brief no type | 5 | 0 | 9 | 874 | 8 | 0 | 0 |
| luna | t1 brief guesthouse | 7 | 2 | 8 | 77 | 0 | 0 | 0 |
| astra | t0 brief hotel | 54 | 0 | 0 | 5 | 0 | 0 | 0 |
| astra | t0 brief no type | 163 | 0 | 0 | 282 | 3 | 0 | 0 |
| astra | t0 brief guesthouse | 36 | 1 | 4 | 6 | 0 | 0 | 0 |
| astra | t1 brief hotel | 7 | 0 | 0 | 52 | 0 | 0 | 0 |
| astra | t1 brief no type | 24 | 0 | 0 | 421 | 3 | 0 | 0 |
| astra | t1 brief guesthouse | 8 | 1 | 4 | 34 | 0 | 0 | 0 |
