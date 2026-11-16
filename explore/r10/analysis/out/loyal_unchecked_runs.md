## Full-schema sensitivity of the tool-call runs not covered by tool_validity.py (post hoc; no model call)

Answers (or, for conversations, conversations) with a search call that is not valid after the run's declared normalization are missing; the frozen analysis functions then run unchanged.

Answers counted as missing: {"first service run | t0": 37, "first service run | tg": 42, "first service run | th": 61, "release test | g1": 35, "release test | g2": 40, "release test | g3": 31, "release test | h1": 44, "release test | h2": 29, "release test | h3": 35, "release test | n1": 39, "release test | n2": 104, "release test | n3": 48, "release test | t0": 3489, "release test | t1": 80, "release test | tedit": 23, "release test | tg": 42, "release test | th": 61, "release test | tord": 59, "release test | trep": 854, "second service run | g1": 35, "second service run | g2": 40, "second service run | g3": 31, "second service run | h1": 44, "second service run | h2": 29, "second service run | h3": 35, "second service run | n1": 39, "second service run | n2": 104, "second service run | n3": 48, "second service run | t0": 37}

Search-again run, conversations dropped (valid status, any call not valid after unquote and clean_nulls): {"haiku": {"t0": 3, "h1": 5, "g1": 2}, "sol": {}, "luna": {}}
Search-again run, calls that the declared quote rule makes valid: {"haiku": {"t0": 20, "h1": 55, "g1": 37}, "sol": {"t0": 0, "h1": 0, "g1": 0}, "luna": {"t0": 0, "h1": 0, "g1": 0}}
Later turns, complete conversations dropped: {"t0": {"complete conversations": 22}, "t1": {"complete conversations": 8}}
Label-test tool calls not valid: {"luna tl_code": 0, "luna tl_hotel": 0, "luna tl_neutral": 0, "sol tl_code": 0, "sol tl_hotel": 0, "sol tl_neutral": 0}

29 stored pairs, one answer, tally (stored, sensitivity): [{"bootstrap rule: flag": 2, "bootstrap rule: hold": 25, "bootstrap rule: pass": 2, "exact 0.0125: hold": 27, "exact 0.0125: pass": 2, "exact 0.025: hold": 27, "exact 0.025: pass": 2, "open sign p <= 0.0125: False": 29, "specific sign p <= 0.0125: False": 29, "specific zero-width: False": 27, "specific zero-width: True": 2}, {"bootstrap rule: flag": 1, "bootstrap rule: hold": 26, "bootstrap rule: pass": 2, "exact 0.0125: hold": 27, "exact 0.0125: pass": 2, "exact 0.025: hold": 27, "exact 0.025: pass": 2, "open sign p <= 0.0125: False": 29, "specific sign p <= 0.0125: False": 29, "specific zero-width: False": 27, "specific zero-width: True": 2}]

Reported values compared: 384; rounded value changed: 264; largest absolute difference: 3.152; differences of 0.5 or more (points or %): 97

Decision changes: ["29 pairs: sonnet era1 read 1 vs erp, first rule: flag -> hold"]

| Run | Quantity | Reported | Sensitivity | Difference |
|---|---|---|---|---|
| first service run (Table E3) | sonnet hotel only rate original | 10.27 | 10.11 | -0.16 |
| first service run (Table E3) | sonnet hotel only rate G1 | 15.85 | 16.02 | +0.17 |
| first service run (Table E3) | sonnet hotel only change H1 | 3.79 | 3.95 | +0.16 |
| first service run (Table E3) | sonnet hotel only change H1 low | 2.01 | 2.33 | +0.32 |
| first service run (Table E3) | sonnet hotel only change H1 high | 5.58 | 5.81 | +0.23 |
| first service run (Table E3) | sonnet hotel only change G1 | 5.58 | 5.75 | +0.17 |
| first service run (Table E3) | sonnet hotel only change G1 low | 3.57 | 3.68 | +0.11 |
| first service run (Table E3) | sonnet hotel only change G1 high | 7.81 | 8.05 | +0.23 |
| first service run (Table E3) | sonnet guesthouse only rate G1 | 3.12 | 2.75 | -0.38 |
| first service run (Table E3) | sonnet guesthouse only change G1 | 3.12 | 2.76 | -0.37 |
| first service run (Table E3) | sonnet guesthouse only change G1 low | 1.56 | 1.38 | -0.18 |
| first service run (Table E3) | sonnet guesthouse only change G1 high | 4.91 | 4.37 | -0.54 |
| first service run (Table E3) | sonnet either rate original | 10.27 | 10.11 | -0.16 |
| first service run (Table E3) | sonnet either rate G1 | 18.97 | 18.76 | -0.21 |
| first service run (Table E3) | sonnet either change H1 | 3.79 | 3.95 | +0.16 |
| first service run (Table E3) | sonnet either change H1 low | 2.01 | 2.33 | +0.32 |
| first service run (Table E3) | sonnet either change H1 high | 5.58 | 5.81 | +0.23 |
| first service run (Table E3) | sonnet either change G1 | 8.71 | 8.51 | -0.20 |
| first service run (Table E3) | sonnet either change G1 high | 11.38 | 11.26 | -0.12 |
| first service run (Table E3) | haiku hotel only rate original | 3.12 | 3.04 | -0.09 |
| first service run (Table E3) | haiku hotel only rate H1 | 18.30 | 18.18 | -0.12 |
| first service run (Table E3) | haiku hotel only rate G1 | 16.07 | 16.28 | +0.21 |
| first service run (Table E3) | haiku hotel only change H1 | 15.18 | 15.25 | +0.08 |
| first service run (Table E3) | haiku hotel only change H1 low | 11.83 | 11.86 | +0.03 |
| first service run (Table E3) | haiku hotel only change H1 high | 18.75 | 18.89 | +0.14 |
| first service run (Table E3) | haiku hotel only change G1 | 12.95 | 13.27 | +0.32 |
| first service run (Table E3) | haiku hotel only change G1 low | 9.82 | 10.19 | +0.37 |
| first service run (Table E3) | haiku hotel only change G1 high | 16.29 | 16.82 | +0.53 |
| first service run (Table E3) | haiku guesthouse only rate G1 | 5.58 | 5.35 | -0.23 |
| first service run (Table E3) | haiku guesthouse only change G1 | 5.58 | 5.21 | -0.37 |
| first service run (Table E3) | haiku guesthouse only change G1 low | 3.57 | 3.08 | -0.49 |
| first service run (Table E3) | haiku guesthouse only change G1 high | 7.59 | 7.35 | -0.24 |
| first service run (Table E3) | haiku either rate original | 3.12 | 3.04 | -0.09 |
| first service run (Table E3) | haiku either rate H1 | 18.30 | 18.18 | -0.12 |
| first service run (Table E3) | haiku either rate G1 | 21.65 | 21.63 | -0.02 |
| first service run (Table E3) | haiku either change H1 | 15.18 | 15.25 | +0.08 |
| first service run (Table E3) | haiku either change H1 low | 11.83 | 11.86 | +0.03 |
| first service run (Table E3) | haiku either change H1 high | 18.75 | 18.89 | +0.14 |
| first service run (Table E3) | haiku either change G1 low | 14.96 | 14.69 | -0.26 |
| first service run (Table E3) | haiku either change G1 high | 22.32 | 22.51 | +0.19 |
| second service run (Table E1, Figure 2) | hotel filter rate t0 | 6.47 | 6.38 | -0.09 |
| second service run (Table E1, Figure 2) | hotel filter rate h1 | 40.18 | 38.22 | -1.96 |
| second service run (Table E1, Figure 2) | hotel filter rate h2 | 51.12 | 49.65 | -1.47 |
| second service run (Table E1, Figure 2) | hotel filter rate h3 | 51.12 | 49.53 | -1.59 |
| second service run (Table E1, Figure 2) | hotel filter rate g1 | 35.94 | 35.38 | -0.56 |
| second service run (Table E1, Figure 2) | hotel filter rate g2 | 32.37 | 31.59 | -0.77 |
| second service run (Table E1, Figure 2) | hotel filter rate n2 | 14.29 | 13.87 | -0.42 |
| second service run (Table E1, Figure 2) | hotel filter rate n3 | 12.50 | 11.99 | -0.51 |
| second service run (Table E1, Figure 2) | hotel filter h1 change | 33.71 | 31.71 | -2.00 |
| second service run (Table E1, Figure 2) | hotel filter h1 low | 29.24 | 27.07 | -2.17 |
| second service run (Table E1, Figure 2) | hotel filter h1 high | 37.95 | 36.10 | -1.85 |
| second service run (Table E1, Figure 2) | hotel filter h2 change | 44.64 | 42.79 | -1.85 |
| second service run (Table E1, Figure 2) | hotel filter h2 low | 39.96 | 37.98 | -1.97 |
| second service run (Table E1, Figure 2) | hotel filter h2 high | 49.11 | 47.84 | -1.27 |
| second service run (Table E1, Figure 2) | hotel filter h3 change | 44.64 | 43.93 | -0.71 |
| second service run (Table E1, Figure 2) | hotel filter h3 low | 39.96 | 39.08 | -0.88 |
| second service run (Table E1, Figure 2) | hotel filter h3 high | 49.55 | 49.03 | -0.52 |
| second service run (Table E1, Figure 2) | hotel filter g1 change | 29.46 | 28.43 | -1.03 |
| second service run (Table E1, Figure 2) | hotel filter g1 low | 25.22 | 24.10 | -1.13 |
| second service run (Table E1, Figure 2) | hotel filter g1 high | 33.93 | 32.77 | -1.16 |
| second service run (Table E1, Figure 2) | hotel filter g2 change | 25.89 | 25.30 | -0.59 |
| second service run (Table E1, Figure 2) | hotel filter g2 low | 21.65 | 21.20 | -0.45 |
| second service run (Table E1, Figure 2) | hotel filter g2 high | 30.13 | 29.40 | -0.74 |
| second service run (Table E1, Figure 2) | hotel filter g3 change | 31.92 | 32.13 | +0.21 |
| second service run (Table E1, Figure 2) | hotel filter g3 high | 36.61 | 36.96 | +0.35 |
| second service run (Table E1, Figure 2) | hotel filter n1 change | 4.24 | 3.62 | -0.62 |
| second service run (Table E1, Figure 2) | hotel filter n1 low | 2.23 | 1.69 | -0.54 |
| second service run (Table E1, Figure 2) | hotel filter n1 high | 6.47 | 6.04 | -0.43 |
| second service run (Table E1, Figure 2) | hotel filter n2 change | 7.81 | 8.56 | +0.74 |
| second service run (Table E1, Figure 2) | hotel filter n2 low | 5.13 | 5.61 | +0.48 |
| second service run (Table E1, Figure 2) | hotel filter n2 high | 10.71 | 11.76 | +1.05 |
| second service run (Table E1, Figure 2) | hotel filter n3 change | 6.03 | 5.61 | -0.42 |
| second service run (Table E1, Figure 2) | hotel filter n3 low | 3.57 | 3.41 | -0.16 |
| second service run (Table E1, Figure 2) | hotel filter n3 high | 8.48 | 8.29 | -0.19 |
| second service run (Table E1, Figure 2) | hotel filter group H change | 41.00 | 39.83 | -1.17 |
| second service run (Table E1, Figure 2) | hotel filter group H low | 36.90 | 35.39 | -1.51 |
| second service run (Table E1, Figure 2) | hotel filter group H high | 45.09 | 44.10 | -0.99 |
| second service run (Table E1, Figure 2) | hotel filter group G change | 29.09 | 28.71 | -0.38 |
| second service run (Table E1, Figure 2) | hotel filter group G low | 25.37 | 24.76 | -0.61 |
| second service run (Table E1, Figure 2) | hotel filter group G high | 33.04 | 32.46 | -0.57 |
| second service run (Table E1, Figure 2) | hotel filter group N change | 6.03 | 5.53 | -0.50 |
| second service run (Table E1, Figure 2) | hotel filter group N low | 3.94 | 3.46 | -0.48 |
| second service run (Table E1, Figure 2) | hotel filter group N high | 8.18 | 7.72 | -0.47 |
| second service run (Table E1) | hotel filter H-N change | 34.97 | 33.96 | -1.01 |
| second service run (Table E1) | hotel filter H-N low | 31.40 | 29.86 | -1.54 |
| second service run (Table E1) | hotel filter H-N high | 38.69 | 37.63 | -1.06 |
| second service run (Table E1) | hotel filter G-N change | 23.07 | 22.66 | -0.40 |
| second service run (Table E1) | hotel filter G-N low | 19.64 | 19.55 | -0.09 |
| second service run (Table E1) | hotel filter G-N high | 26.26 | 26.09 | -0.17 |
| second service run (Table E1) | hotel filter G-H change | -11.90 | -11.10 | +0.81 |
| second service run (Table E1) | hotel filter G-H low | -15.18 | -14.44 | +0.74 |
| second service run (Table E1) | hotel filter G-H high | -8.71 | -7.64 | +1.06 |
| second service run (Table E1, Figure 2) | guesthouse filter rate t0 | 1.12 | 0.71 | -0.41 |
| second service run (Table E1, Figure 2) | guesthouse filter rate h1 | 3.12 | 2.88 | -0.24 |
| second service run (Table E1, Figure 2) | guesthouse filter rate h2 | 4.46 | 4.22 | -0.25 |
| second service run (Table E1, Figure 2) | guesthouse filter rate h3 | 5.36 | 4.98 | -0.38 |
| second service run (Table E1, Figure 2) | guesthouse filter rate g1 | 20.09 | 18.87 | -1.22 |
| second service run (Table E1, Figure 2) | guesthouse filter rate g2 | 16.74 | 15.44 | -1.30 |
| second service run (Table E1, Figure 2) | guesthouse filter rate g3 | 23.88 | 23.06 | -0.83 |
| second service run (Table E1, Figure 2) | guesthouse filter rate n1 | 0.89 | 0.71 | -0.18 |
| second service run (Table E1, Figure 2) | guesthouse filter rate n2 | 1.56 | 0.53 | -1.03 |
| second service run (Table E1, Figure 2) | guesthouse filter rate n3 | 1.56 | 1.44 | -0.12 |
| second service run (Table E1, Figure 2) | guesthouse filter h1 change | 2.01 | 2.20 | +0.19 |
| second service run (Table E1, Figure 2) | guesthouse filter h1 low | 0.67 | 0.98 | +0.31 |
| second service run (Table E1, Figure 2) | guesthouse filter h1 high | 3.57 | 3.66 | +0.09 |
| second service run (Table E1, Figure 2) | guesthouse filter h2 change | 3.35 | 3.37 | +0.02 |
| second service run (Table E1, Figure 2) | guesthouse filter h2 low | 1.79 | 1.68 | -0.10 |
| second service run (Table E1, Figure 2) | guesthouse filter h2 high | 5.13 | 5.29 | +0.15 |
| second service run (Table E1, Figure 2) | guesthouse filter h3 change | 4.24 | 4.13 | -0.11 |
| second service run (Table E1, Figure 2) | guesthouse filter h3 low | 2.46 | 2.18 | -0.27 |
| second service run (Table E1, Figure 2) | guesthouse filter h3 high | 6.03 | 6.07 | +0.04 |
| second service run (Table E1, Figure 2) | guesthouse filter g1 change | 18.97 | 18.07 | -0.90 |
| second service run (Table E1, Figure 2) | guesthouse filter g1 low | 15.18 | 14.46 | -0.72 |
| second service run (Table E1, Figure 2) | guesthouse filter g1 high | 22.54 | 21.93 | -0.62 |
| second service run (Table E1, Figure 2) | guesthouse filter g2 change | 15.62 | 14.46 | -1.17 |
| second service run (Table E1, Figure 2) | guesthouse filter g2 low | 12.50 | 10.84 | -1.66 |
| second service run (Table E1, Figure 2) | guesthouse filter g2 high | 18.97 | 17.83 | -1.14 |
| second service run (Table E1, Figure 2) | guesthouse filter g3 change | 22.77 | 21.50 | -1.27 |
| second service run (Table E1, Figure 2) | guesthouse filter g3 low | 18.75 | 17.87 | -0.88 |
| second service run (Table E1, Figure 2) | guesthouse filter g3 high | 26.79 | 25.60 | -1.18 |
| second service run (Table E1, Figure 2) | guesthouse filter n1 change | -0.22 | 0.00 | +0.22 |
| second service run (Table E1, Figure 2) | guesthouse filter n1 low | -1.12 | -0.97 | +0.15 |
| second service run (Table E1, Figure 2) | guesthouse filter n1 high | 0.67 | 0.97 | +0.30 |
| second service run (Table E1, Figure 2) | guesthouse filter n2 change | 0.45 | 0.00 | -0.45 |
| second service run (Table E1, Figure 2) | guesthouse filter n2 low | -0.67 | -1.07 | -0.40 |
| second service run (Table E1, Figure 2) | guesthouse filter n2 high | 1.56 | 1.07 | -0.49 |
| second service run (Table E1, Figure 2) | guesthouse filter n3 change | 0.45 | 0.73 | +0.29 |
| second service run (Table E1, Figure 2) | guesthouse filter n3 low | -0.45 | -0.24 | +0.20 |
| second service run (Table E1, Figure 2) | guesthouse filter n3 high | 1.56 | 1.71 | +0.14 |
| second service run (Table E1, Figure 2) | guesthouse filter group H change | 3.20 | 3.40 | +0.21 |
| second service run (Table E1, Figure 2) | guesthouse filter group H low | 2.01 | 2.18 | +0.17 |
| second service run (Table E1, Figure 2) | guesthouse filter group H high | 4.54 | 4.75 | +0.21 |
| second service run (Table E1, Figure 2) | guesthouse filter group G change | 19.12 | 18.40 | -0.72 |
| second service run (Table E1, Figure 2) | guesthouse filter group G low | 16.00 | 15.44 | -0.55 |
| second service run (Table E1, Figure 2) | guesthouse filter group G high | 22.17 | 21.64 | -0.53 |
| second service run (Table E1, Figure 2) | guesthouse filter group N change | 0.22 | 0.32 | +0.10 |
| second service run (Table E1, Figure 2) | guesthouse filter group N low | -0.60 | -0.52 | +0.08 |
| second service run (Table E1, Figure 2) | guesthouse filter group N high | 1.04 | 1.11 | +0.07 |
| second service run (Table E1) | guesthouse filter H-N change | 2.98 | 3.20 | +0.22 |
| second service run (Table E1) | guesthouse filter H-N low | 1.71 | 1.91 | +0.20 |
| second service run (Table E1) | guesthouse filter H-N high | 4.32 | 4.53 | +0.21 |
| second service run (Table E1) | guesthouse filter G-N change | 18.90 | 18.54 | -0.36 |
| second service run (Table E1) | guesthouse filter G-N low | 15.85 | 15.38 | -0.47 |
| second service run (Table E1) | guesthouse filter G-N high | 21.88 | 21.81 | -0.07 |
| second service run (Table E1) | guesthouse filter G-H change | 15.92 | 15.48 | -0.45 |
| second service run (Table E1) | guesthouse filter G-H low | 12.80 | 12.40 | -0.39 |
| second service run (Table E1) | guesthouse filter G-H high | 18.97 | 18.59 | -0.39 |
| second service run (Table E1, Figure 2) | exclusion (either) rate t0 | 2.46 | 2.60 | +0.15 |
| second service run (Table E1, Figure 2) | exclusion (either) rate h1 | 18.53 | 18.75 | +0.22 |
| second service run (Table E1, Figure 2) | exclusion (either) rate h2 | 22.54 | 22.72 | +0.17 |
| second service run (Table E1, Figure 2) | exclusion (either) rate h3 | 23.88 | 24.41 | +0.52 |
| second service run (Table E1, Figure 2) | exclusion (either) rate g1 | 21.88 | 21.46 | -0.41 |
| second service run (Table E1, Figure 2) | exclusion (either) rate g2 | 20.09 | 19.71 | -0.37 |
| second service run (Table E1, Figure 2) | exclusion (either) rate g3 | 22.77 | 22.35 | -0.41 |
| second service run (Table E1, Figure 2) | exclusion (either) rate n1 | 5.80 | 5.69 | -0.12 |
| second service run (Table E1, Figure 2) | exclusion (either) rate n2 | 7.37 | 7.47 | +0.10 |
| second service run (Table E1, Figure 2) | exclusion (either) rate n3 | 5.58 | 5.28 | -0.30 |
| second service run (Table E1, Figure 2) | exclusion (either) h1 high | 19.64 | 19.51 | -0.13 |
| second service run (Table E1, Figure 2) | exclusion (either) h2 change | 20.09 | 19.95 | -0.14 |
| second service run (Table E1, Figure 2) | exclusion (either) h2 low | 16.29 | 16.11 | -0.19 |
| second service run (Table E1, Figure 2) | exclusion (either) h2 high | 24.11 | 23.80 | -0.31 |
| second service run (Table E1, Figure 2) | exclusion (either) h3 change | 21.43 | 21.84 | +0.42 |
| second service run (Table E1, Figure 2) | exclusion (either) h3 low | 17.63 | 17.96 | +0.33 |
| second service run (Table E1, Figure 2) | exclusion (either) h3 high | 25.67 | 25.97 | +0.30 |
| second service run (Table E1, Figure 2) | exclusion (either) g1 change | 19.42 | 18.31 | -1.11 |
| second service run (Table E1, Figure 2) | exclusion (either) g1 low | 15.85 | 14.70 | -1.15 |
| second service run (Table E1, Figure 2) | exclusion (either) g1 high | 23.44 | 22.17 | -1.27 |
| second service run (Table E1, Figure 2) | exclusion (either) g2 change | 17.63 | 16.87 | -0.77 |
| second service run (Table E1, Figure 2) | exclusion (either) g2 low | 14.29 | 13.25 | -1.03 |
| second service run (Table E1, Figure 2) | exclusion (either) g2 high | 21.21 | 20.72 | -0.48 |
| second service run (Table E1, Figure 2) | exclusion (either) g3 change | 20.31 | 19.81 | -0.51 |
| second service run (Table E1, Figure 2) | exclusion (either) g3 low | 16.74 | 15.94 | -0.80 |
| second service run (Table E1, Figure 2) | exclusion (either) g3 high | 24.33 | 24.15 | -0.18 |
| second service run (Table E1, Figure 2) | exclusion (either) n1 change | 3.35 | 2.90 | -0.45 |
| second service run (Table E1, Figure 2) | exclusion (either) n1 low | 1.79 | 1.45 | -0.34 |
| second service run (Table E1, Figure 2) | exclusion (either) n1 high | 5.13 | 4.59 | -0.54 |
| second service run (Table E1, Figure 2) | exclusion (either) n2 change | 4.91 | 4.81 | -0.10 |
| second service run (Table E1, Figure 2) | exclusion (either) n2 low | 3.12 | 2.67 | -0.45 |
| second service run (Table E1, Figure 2) | exclusion (either) n2 high | 7.14 | 7.22 | +0.08 |
| second service run (Table E1, Figure 2) | exclusion (either) n3 change | 3.12 | 2.68 | -0.44 |
| second service run (Table E1, Figure 2) | exclusion (either) n3 low | 1.56 | 0.98 | -0.59 |
| second service run (Table E1, Figure 2) | exclusion (either) n3 high | 5.13 | 4.39 | -0.74 |
| second service run (Table E1, Figure 2) | exclusion (either) group H change | 19.20 | 19.28 | +0.08 |
| second service run (Table E1, Figure 2) | exclusion (either) group H high | 22.84 | 23.12 | +0.28 |
| second service run (Table E1, Figure 2) | exclusion (either) group G change | 19.12 | 18.25 | -0.88 |
| second service run (Table E1, Figure 2) | exclusion (either) group G low | 16.00 | 14.85 | -1.15 |
| second service run (Table E1, Figure 2) | exclusion (either) group G high | 22.62 | 21.72 | -0.90 |
| second service run (Table E1, Figure 2) | exclusion (either) group N change | 3.79 | 3.30 | -0.49 |
| second service run (Table E1, Figure 2) | exclusion (either) group N low | 2.38 | 1.95 | -0.43 |
| second service run (Table E1, Figure 2) | exclusion (either) group N high | 5.51 | 4.93 | -0.57 |
| second service run (Table E1) | exclusion (either) H-N change | 15.40 | 15.77 | +0.37 |
| second service run (Table E1) | exclusion (either) H-N low | 12.50 | 12.69 | +0.19 |
| second service run (Table E1) | exclusion (either) H-N high | 18.45 | 19.01 | +0.56 |
| second service run (Table E1) | exclusion (either) G-N change | 15.33 | 14.99 | -0.34 |
| second service run (Table E1) | exclusion (either) G-N low | 12.57 | 12.07 | -0.50 |
| second service run (Table E1) | exclusion (either) G-N high | 18.30 | 17.83 | -0.47 |
| second service run (Table E1) | exclusion (either) G-H change | -0.07 | -0.96 | -0.89 |
| second service run (Table E1) | exclusion (either) G-H low | -3.12 | -3.69 | -0.56 |
| second service run (Table E1) | exclusion (either) G-H high | 2.83 | 2.07 | -0.75 |
| release test (Appendix E.3) | N1 hotel-brief set change | 11.86 | 10.20 | -1.66 |
| release test (Appendix E.3) | N1 hotel-brief set low | 1.69 | 2.04 | +0.35 |
| release test (Appendix E.3) | N1 hotel-brief set high | 22.03 | 22.45 | +0.42 |
| release test (Appendix E.3) | N1 no-type set change | 4.24 | 3.62 | -0.62 |
| release test (Appendix E.3) | N1 no-type set low | 1.56 | 1.21 | -0.35 |
| release test (Appendix E.3) | N1 no-type set high | 7.14 | 6.52 | -0.62 |
| search-again run (Table E2) | haiku H1 hotel only first search change | 17.23 | 17.42 | +0.19 |
| search-again run (Table E2) | haiku H1 hotel only first search low | 13.65 | 13.80 | +0.15 |
| search-again run (Table E2) | haiku H1 hotel only first search high | 20.81 | 21.04 | +0.24 |
| search-again run (Table E2) | haiku H1 hotel only last search change | 11.16 | 11.09 | -0.07 |
| search-again run (Table E2) | haiku H1 hotel only last search low | 8.26 | 8.14 | -0.11 |
| search-again run (Table E2) | haiku H1 hotel only original-tool first rate | 2.01 | 1.80 | -0.22 |
| search-again run (Table E2) | haiku G1 either first search change | 18.57 | 18.51 | -0.06 |
| search-again run (Table E2) | haiku G1 either first search low | 14.99 | 15.12 | +0.14 |
| search-again run (Table E2) | haiku G1 either first search high | 22.15 | 21.90 | -0.25 |
| search-again run (Table E2) | haiku G1 either last search change | 16.52 | 16.25 | -0.27 |
| search-again run (Table E2) | haiku G1 either last search low | 13.17 | 12.87 | -0.30 |
| search-again run (Table E2) | haiku G1 either last search high | 20.31 | 19.64 | -0.67 |
| search-again run (Table E2) | haiku G1 either original-tool first rate | 2.01 | 1.80 | -0.22 |
| search-again run (Table E2) | haiku searched again t0 | 1.34 | 0.90 | -0.44 |
| search-again run (Table E2) | haiku searched again h1 | 10.94 | 10.16 | -0.78 |
| search-again run (Table E2) | haiku searched again g1 | 8.48 | 8.07 | -0.41 |
| search-again run (Section 5) | haiku H1 later searches removed part low | -8.95 | -9.05 | -0.10 |
| search-again run (Table E2, panel) | panel hotel-only | h1 | first change | 23.03 | 23.07 | +0.04 |
| search-again run (Table E2, panel) | panel hotel-only | h1 | first low | 20.31 | 20.39 | +0.07 |
| search-again run (Table E2, panel) | panel hotel-only | h1 | first high | 25.74 | 25.78 | +0.04 |
| search-again run (Table E2, panel) | panel either | g1 | first change | 25.52 | 25.56 | +0.04 |
| search-again run (Table E2, panel) | panel either | g1 | first high | 28.01 | 28.05 | +0.04 |
| search-again run (Table E2, panel) | panel either | g1 | last change | 20.98 | 20.87 | -0.11 |
| search-again run (Table E2, panel) | panel either | g1 | last low | 18.71 | 18.60 | -0.11 |
| search-again run (Table E2, panel) | panel either | g1 | last high | 23.44 | 23.29 | -0.15 |
| later turns (Table D1) | t0 only guesthouses fit initial_failure (20/130 -> 18/118) | 15.38 | 15.25 | -0.13 |
| later turns (Table D1) | t0 only guesthouses fit fit_shown (123/130 -> 112/118) | 94.62 | 94.92 | +0.30 |
| later turns (Table D1) | t0 only guesthouses fit never_fit (7/130 -> 6/118) | 5.38 | 5.08 | -0.30 |
| later turns (Table D1) | t0 only guesthouses fit hotel_only_end (15/130 -> 13/118) | 11.54 | 11.02 | -0.52 |
| later turns (Table D1) | t0 only guesthouses fit relapse (17/130 -> 15/118) | 13.08 | 12.71 | -0.37 |
| later turns (Table D1) | t0 only guesthouses fit mean searches | 2.55 | 2.42 | -0.12 |
| later turns (Table D1) | t0 after an initial exclusion fit_shown (17/20 -> 15/18) | 85.00 | 83.33 | -1.67 |
| later turns (Table D1) | t0 after an initial exclusion never_fit (3/20 -> 3/18) | 15.00 | 16.67 | +1.67 |
| later turns (Table D1) | t0 after an initial exclusion hotel_only_end (11/20 -> 10/18) | 55.00 | 55.56 | +0.56 |
| later turns (Table D1) | t0 after an initial exclusion relapse (9/20 -> 8/18) | 45.00 | 44.44 | -0.56 |
| later turns (Table D1) | t0 after an initial exclusion mean searches | 4.70 | 4.44 | -0.26 |
| later turns (Table D1) | t0 without one fit_shown (106/110 -> 97/100) | 96.36 | 97.00 | +0.64 |
| later turns (Table D1) | t0 without one never_fit (4/110 -> 3/100) | 3.64 | 3.00 | -0.64 |
| later turns (Table D1) | t0 without one hotel_only_end (4/110 -> 3/100) | 3.64 | 3.00 | -0.64 |
| later turns (Table D1) | t0 without one relapse (8/110 -> 7/100) | 7.27 | 7.00 | -0.27 |
| later turns (Table D1) | t0 without one mean searches | 2.15 | 2.06 | -0.09 |
| later turns (Table D1) | t0 a hotel fits fit_shown (120/130 -> 111/120) | 92.31 | 92.50 | +0.19 |
| later turns (Table D1) | t0 a hotel fits never_fit (10/130 -> 9/120) | 7.69 | 7.50 | -0.19 |
| later turns (Table D1) | t0 a hotel fits hotel_only_end (23/130 -> 22/120) | 17.69 | 18.33 | +0.64 |
| later turns (Table D1) | t0 a hotel fits relapse (13/130 -> 13/120) | 10.00 | 10.83 | +0.83 |
| later turns (Table D1) | t0 a hotel fits mean searches | 2.30 | 2.25 | -0.05 |
| later turns (Table D1) | t1 only guesthouses fit fit_shown (121/130 -> 119/126) | 93.08 | 94.44 | +1.37 |
| later turns (Table D1) | t1 only guesthouses fit never_fit (9/130 -> 7/126) | 6.92 | 5.56 | -1.37 |
| later turns (Table D1) | t1 only guesthouses fit mean searches | 2.07 | 1.94 | -0.12 |
| later turns (Table D1) | t1 without one fit_shown (120/129 -> 118/125) | 93.02 | 94.40 | +1.38 |
| later turns (Table D1) | t1 without one never_fit (9/129 -> 7/125) | 6.98 | 5.60 | -1.38 |
| later turns (Table D1) | t1 without one mean searches | 2.05 | 1.93 | -0.13 |
| later turns (Table D1) | t1 a hotel fits fit_shown (117/130 -> 115/126) | 90.00 | 91.27 | +1.27 |
| later turns (Table D1) | t1 a hotel fits never_fit (13/130 -> 11/126) | 10.00 | 8.73 | -1.27 |
| later turns (Table D1) | t1 a hotel fits hotel_only_end (2/130 -> 2/126) | 1.54 | 1.59 | +0.05 |
| later turns (Table D1) | t1 a hotel fits relapse (2/130 -> 2/126) | 1.54 | 1.59 | +0.05 |
| later turns (Section 6) | t0 never fit: initial exclusion minus none, difference | 11.36 | 13.67 | +2.30 |
| later turns (Section 6) | t0 never fit: initial exclusion minus none, low | -3.64 | -3.00 | +0.64 |
| later turns (Section 6) | t0 never fit: initial exclusion minus none, high | 28.18 | 31.33 | +3.15 |

Note (added after the run). The counter "Answers counted as missing" adds one for each call of the scoring function. For the
first and second service runs each answer is scored once, so their counts are answers (of 554 per tool). The release-test
counts are summed over the repeated scoring calls of verify.item1 and are not answer counts; its answers are those of the
runs above (erm_haiku, ers_*, erp_*) and of the stored unchanged-tool runs. Cross-check: after the sensitivity, the
first service run has 430 / 435 (Sonnet H1 / G1) and 413 / 422 (Haiku) open-set pairs, the same as tool_validity.md.
The changed stored pair (Sonnet era1 read 1 against erp, first rule): specific set +8.47 [+1.69, +18.64] on 59 pairs
(flag) -> +8.93 [+0.00, +19.64] on 56 pairs (hold); open set -1.34 [-3.57, +0.89] -> -1.37 [-3.42, +0.68].
