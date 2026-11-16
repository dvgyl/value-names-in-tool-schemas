# T1: the release rules on the same simulated datasets

Post hoc tabulation of the existing simulation (R10-26; `posthoc/release-sim/out/sim.json`). 2,000 trials per configuration; every rule of one trial uses the same simulated data and the same bootstrap draws. Shares in percent; brackets: Wilson 95% interval of the simulation uncertainty. Paper design: 448 open requests × 1 answer, 59 specific requests × 10 answers, unless stated. L = 5.

## C = 4 (level 98.75%; pooled 97.50%)

### Ranges across profiles (not intervals; the ends can come from different profiles)

| Scenario | Original F / P / H | Revised F / P / H | Final F / P / H | Final without sign F / P / H | Pooled F / P / H |
|---|---|---|---|---|---|
| Zero change | 0.0–0.2 / 52.6–96.5 / 3.5–47.1 | 0.0–0.2 / 52.6–96.5 / 3.5–47.1 | 0.0–0.2 / 52.0–96.0 / 4.0–47.8 | 0.0–0.2 / 52.0–96.0 / 4.0–47.8 | 0.0 / 97.8–100.0 / 0.0–2.2 |
| Shift of +6 in both sets | 92.5–96.2 / 0.0 / 3.9–7.5 | 92.3–96.0 / 0.0 / 4.0–7.6 | 92.3–96.0 / 0.0 / 4.0–7.6 | 92.5–96.2 / 0.0 / 3.9–7.5 | 77.1–82.2 / 0.1–0.3 / 17.6–22.6 |
| Shift of +6 in the specific set only | 73.2–82.1 / 0.0–0.1 / 17.8–26.8 | 73.0–81.2 / 0.0–0.1 / 18.8–27.0 | 73.0–81.2 / 0.0–0.1 / 18.8–27.0 | 73.2–82.1 / 0.0–0.1 / 17.8–26.8 | 0.0 / 95.0–100.0 / 0.0–5.0 |
| Sparse change on 6 specific requests (mean 8 points) | 53.6–80.5 / 0.0 / 19.4–46.4 | 4.5–11.1 / 0.0 / 88.9–95.5 | 4.5–11.1 / 0.0 / 88.9–95.5 | 53.6–80.5 / 0.0 / 19.4–46.4 | 0.0 / 91.0–100.0 / 0.0–9.0 |
| Cancelling changes, specific set (up to 12 down, 12 up) | 0.0 / 0.0–0.1 / 100.0 | 0.0 / 0.0–0.1 / 100.0 | 0.0 / 0.0–0.1 / 100.0 | 0.0 / 0.0–0.1 / 100.0 | 0.0 / 92.2–100.0 / 0.0–7.8 |
| Cancelling changes, open set (10 down, 10 up) | 0.0–0.1 / 42.3–97.2 / 2.9–57.6 | 0.0–0.1 / 42.3–97.2 / 2.9–57.6 | 0.0–0.1 / 41.1–97.1 / 2.9–58.8 | 0.0–0.1 / 41.1–97.1 / 2.9–58.8 | 0.0 / 92.5–100.0 / 0.0–7.4 |
| Drift of +3 on the new answers, no schema effect | 5.7–15.5 / 1.9–10.8 / 82.5–87.5 | 5.7–14.9 / 1.9–10.8 / 83.1–87.6 | 5.7–14.9 / 1.7–10.2 / 83.4–88.2 | 5.7–15.5 / 1.7–10.2 / 82.8–88.1 | 1.9–5.9 / 28.1–45.6 / 52.4–66.0 |
| Drift of -3 on the new answers, true shift of +6 in both sets | 5.4–16.1 / 1.4–9.2 / 82.6–87.7 | 5.4–14.6 / 1.4–9.2 / 84.0–92.3 | 5.4–14.6 / 1.1–8.6 / 84.2–92.6 | 5.4–16.1 / 1.1–8.6 / 82.8–87.9 | 1.4–5.9 / 26.0–46.2 / 52.4–68.1 |
| Zero change, 1 answer per specific request | 0.3–1.9 / 0.0–10.0 / 89.8–98.1 | 0.0–0.4 / 0.0–10.0 / 90.0–99.6 | 0.0–0.4 / 0.0 / 99.6–100.0 | 0.3–1.9 / 0.0 / 98.1–99.7 | 0.0 / 94.7–100.0 / 0.0–5.3 |

### Every scenario and profile

| Scenario | Profile | Rule | Flag % [95%] | Pass % [95%] | Hold % [95%] | k flag / pass / hold of n |
|---|---|---|---|---|---|---|
| Zero change | haiku | Original | 0.0 [0.0, 0.2] | 96.5 [95.5, 97.2] | 3.5 [2.8, 4.5] | 0 / 1929 / 71 of 2000 |
| Zero change | haiku | Revised | 0.0 [0.0, 0.2] | 96.5 [95.5, 97.2] | 3.5 [2.8, 4.5] | 0 / 1929 / 71 of 2000 |
| Zero change | haiku | Final | 0.0 [0.0, 0.2] | 96.0 [95.0, 96.8] | 4.0 [3.2, 5.0] | 0 / 1920 / 80 of 2000 |
| Zero change | haiku | Final without sign | 0.0 [0.0, 0.2] | 96.0 [95.0, 96.8] | 4.0 [3.2, 5.0] | 0 / 1920 / 80 of 2000 |
| Zero change | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Zero change | deepseek | Original | 0.2 [0.1, 0.5] | 52.6 [50.5, 54.8] | 47.1 [45.0, 49.3] | 4 / 1053 / 943 of 2000 |
| Zero change | deepseek | Revised | 0.2 [0.1, 0.5] | 52.6 [50.5, 54.8] | 47.1 [45.0, 49.3] | 4 / 1053 / 943 of 2000 |
| Zero change | deepseek | Final | 0.2 [0.1, 0.5] | 52.0 [49.8, 54.2] | 47.8 [45.6, 50.0] | 4 / 1040 / 956 of 2000 |
| Zero change | deepseek | Final without sign | 0.2 [0.1, 0.5] | 52.0 [49.8, 54.2] | 47.8 [45.6, 50.0] | 4 / 1040 / 956 of 2000 |
| Zero change | deepseek | Pooled | 0.0 [0.0, 0.2] | 97.8 [97.1, 98.4] | 2.2 [1.6, 2.9] | 0 / 1956 / 44 of 2000 |
| Zero change | sol | Original | 0.1 [0.0, 0.3] | 86.8 [85.2, 88.2] | 13.2 [11.7, 14.7] | 1 / 1736 / 263 of 2000 |
| Zero change | sol | Revised | 0.0 [0.0, 0.2] | 86.8 [85.2, 88.2] | 13.2 [11.8, 14.8] | 0 / 1736 / 264 of 2000 |
| Zero change | sol | Final | 0.0 [0.0, 0.2] | 86.4 [84.8, 87.8] | 13.6 [12.2, 15.2] | 0 / 1728 / 272 of 2000 |
| Zero change | sol | Final without sign | 0.1 [0.0, 0.3] | 86.4 [84.8, 87.8] | 13.6 [12.1, 15.1] | 1 / 1728 / 271 of 2000 |
| Zero change | sol | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Shift of +6 in both sets | haiku | Original | 95.5 [94.5, 96.3] | 0.0 [0.0, 0.2] | 4.5 [3.7, 5.5] | 1910 / 0 / 90 of 2000 |
| Shift of +6 in both sets | haiku | Revised | 95.5 [94.5, 96.3] | 0.0 [0.0, 0.2] | 4.5 [3.7, 5.5] | 1910 / 0 / 90 of 2000 |
| Shift of +6 in both sets | haiku | Final | 95.5 [94.5, 96.3] | 0.0 [0.0, 0.2] | 4.5 [3.7, 5.5] | 1910 / 0 / 90 of 2000 |
| Shift of +6 in both sets | haiku | Final without sign | 95.5 [94.5, 96.3] | 0.0 [0.0, 0.2] | 4.5 [3.7, 5.5] | 1910 / 0 / 90 of 2000 |
| Shift of +6 in both sets | haiku | Pooled | 82.2 [80.4, 83.8] | 0.2 [0.1, 0.5] | 17.6 [16.0, 19.4] | 1643 / 4 / 353 of 2000 |
| Shift of +6 in both sets | deepseek | Original | 92.5 [91.2, 93.5] | 0.0 [0.0, 0.2] | 7.5 [6.5, 8.8] | 1849 / 0 / 151 of 2000 |
| Shift of +6 in both sets | deepseek | Revised | 92.3 [91.1, 93.4] | 0.0 [0.0, 0.2] | 7.6 [6.6, 8.9] | 1847 / 0 / 153 of 2000 |
| Shift of +6 in both sets | deepseek | Final | 92.3 [91.1, 93.4] | 0.0 [0.0, 0.2] | 7.6 [6.6, 8.9] | 1847 / 0 / 153 of 2000 |
| Shift of +6 in both sets | deepseek | Final without sign | 92.5 [91.2, 93.5] | 0.0 [0.0, 0.2] | 7.5 [6.5, 8.8] | 1849 / 0 / 151 of 2000 |
| Shift of +6 in both sets | deepseek | Pooled | 77.1 [75.3, 78.9] | 0.3 [0.1, 0.7] | 22.6 [20.8, 24.4] | 1543 / 6 / 451 of 2000 |
| Shift of +6 in both sets | sol | Original | 96.2 [95.2, 96.9] | 0.0 [0.0, 0.2] | 3.9 [3.1, 4.8] | 1923 / 0 / 77 of 2000 |
| Shift of +6 in both sets | sol | Revised | 96.0 [95.0, 96.7] | 0.0 [0.0, 0.2] | 4.0 [3.3, 5.0] | 1919 / 0 / 81 of 2000 |
| Shift of +6 in both sets | sol | Final | 96.0 [95.0, 96.7] | 0.0 [0.0, 0.2] | 4.0 [3.3, 5.0] | 1919 / 0 / 81 of 2000 |
| Shift of +6 in both sets | sol | Final without sign | 96.2 [95.2, 96.9] | 0.0 [0.0, 0.2] | 3.9 [3.1, 4.8] | 1923 / 0 / 77 of 2000 |
| Shift of +6 in both sets | sol | Pooled | 82.0 [80.3, 83.6] | 0.1 [0.0, 0.4] | 17.9 [16.3, 19.6] | 1640 / 2 / 358 of 2000 |
| Shift of +6 in the specific set only | haiku | Original | 79.0 [77.2, 80.8] | 0.1 [0.0, 0.3] | 20.9 [19.2, 22.7] | 1581 / 1 / 418 of 2000 |
| Shift of +6 in the specific set only | haiku | Revised | 79.0 [77.2, 80.8] | 0.1 [0.0, 0.3] | 20.9 [19.2, 22.7] | 1581 / 1 / 418 of 2000 |
| Shift of +6 in the specific set only | haiku | Final | 79.0 [77.2, 80.8] | 0.1 [0.0, 0.3] | 20.9 [19.2, 22.7] | 1581 / 1 / 418 of 2000 |
| Shift of +6 in the specific set only | haiku | Final without sign | 79.0 [77.2, 80.8] | 0.1 [0.0, 0.3] | 20.9 [19.2, 22.7] | 1581 / 1 / 418 of 2000 |
| Shift of +6 in the specific set only | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Shift of +6 in the specific set only | deepseek | Original | 73.2 [71.2, 75.1] | 0.0 [0.0, 0.2] | 26.8 [24.9, 28.8] | 1464 / 0 / 536 of 2000 |
| Shift of +6 in the specific set only | deepseek | Revised | 73.0 [71.0, 74.9] | 0.0 [0.0, 0.2] | 27.0 [25.1, 29.0] | 1460 / 0 / 540 of 2000 |
| Shift of +6 in the specific set only | deepseek | Final | 73.0 [71.0, 74.9] | 0.0 [0.0, 0.2] | 27.0 [25.1, 29.0] | 1460 / 0 / 540 of 2000 |
| Shift of +6 in the specific set only | deepseek | Final without sign | 73.2 [71.2, 75.1] | 0.0 [0.0, 0.2] | 26.8 [24.9, 28.8] | 1464 / 0 / 536 of 2000 |
| Shift of +6 in the specific set only | deepseek | Pooled | 0.0 [0.0, 0.2] | 95.0 [94.0, 95.9] | 5.0 [4.1, 6.0] | 0 / 1900 / 100 of 2000 |
| Shift of +6 in the specific set only | sol | Original | 82.1 [80.4, 83.7] | 0.1 [0.0, 0.3] | 17.8 [16.2, 19.6] | 1642 / 1 / 357 of 2000 |
| Shift of +6 in the specific set only | sol | Revised | 81.2 [79.4, 82.8] | 0.1 [0.0, 0.3] | 18.8 [17.1, 20.6] | 1623 / 1 / 376 of 2000 |
| Shift of +6 in the specific set only | sol | Final | 81.2 [79.4, 82.8] | 0.1 [0.0, 0.3] | 18.8 [17.1, 20.6] | 1623 / 1 / 376 of 2000 |
| Shift of +6 in the specific set only | sol | Final without sign | 82.1 [80.4, 83.7] | 0.1 [0.0, 0.3] | 17.8 [16.2, 19.6] | 1642 / 1 / 357 of 2000 |
| Shift of +6 in the specific set only | sol | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.7, 100.0] | 0.1 [0.0, 0.3] | 0 / 1999 / 1 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Original | 80.5 [78.8, 82.2] | 0.0 [0.0, 0.2] | 19.4 [17.8, 21.2] | 1611 / 0 / 389 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Revised | 11.1 [9.8, 12.6] | 0.0 [0.0, 0.2] | 88.9 [87.4, 90.2] | 222 / 0 / 1778 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Final | 11.1 [9.8, 12.6] | 0.0 [0.0, 0.2] | 88.9 [87.4, 90.2] | 222 / 0 / 1778 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Final without sign | 80.5 [78.8, 82.2] | 0.0 [0.0, 0.2] | 19.4 [17.8, 21.2] | 1611 / 0 / 389 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Original | 53.6 [51.4, 55.8] | 0.0 [0.0, 0.2] | 46.4 [44.2, 48.6] | 1072 / 0 / 928 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Revised | 4.5 [3.7, 5.5] | 0.0 [0.0, 0.2] | 95.5 [94.5, 96.3] | 90 / 0 / 1910 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Final | 4.5 [3.7, 5.5] | 0.0 [0.0, 0.2] | 95.5 [94.5, 96.3] | 90 / 0 / 1910 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Final without sign | 53.6 [51.4, 55.8] | 0.0 [0.0, 0.2] | 46.4 [44.2, 48.6] | 1072 / 0 / 928 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Pooled | 0.0 [0.0, 0.2] | 91.0 [89.7, 92.2] | 9.0 [7.8, 10.3] | 0 / 1820 / 180 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Original | 68.6 [66.5, 70.6] | 0.0 [0.0, 0.2] | 31.4 [29.4, 33.5] | 1372 / 0 / 628 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Revised | 7.4 [6.3, 8.6] | 0.0 [0.0, 0.2] | 92.6 [91.4, 93.7] | 148 / 0 / 1852 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Final | 7.4 [6.3, 8.6] | 0.0 [0.0, 0.2] | 92.6 [91.4, 93.7] | 148 / 0 / 1852 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Final without sign | 67.0 [64.9, 69.0] | 0.0 [0.0, 0.2] | 33.0 [31.0, 35.1] | 1340 / 0 / 660 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Pooled | 0.0 [0.0, 0.2] | 99.8 [99.4, 99.9] | 0.2 [0.1, 0.6] | 0 / 1995 / 5 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Original | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Revised | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Final | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Final without sign | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Original | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Revised | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Final | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Final without sign | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Pooled | 0.0 [0.0, 0.2] | 92.2 [90.9, 93.2] | 7.8 [6.8, 9.1] | 0 / 1843 / 157 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Original | 0.0 [0.0, 0.2] | 0.1 [0.0, 0.3] | 100.0 [99.7, 100.0] | 0 / 1 / 1999 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Revised | 0.0 [0.0, 0.2] | 0.1 [0.0, 0.3] | 100.0 [99.7, 100.0] | 0 / 1 / 1999 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Final | 0.0 [0.0, 0.2] | 0.1 [0.0, 0.3] | 100.0 [99.7, 100.0] | 0 / 1 / 1999 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Final without sign | 0.0 [0.0, 0.2] | 0.1 [0.0, 0.3] | 100.0 [99.7, 100.0] | 0 / 1 / 1999 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Pooled | 0.0 [0.0, 0.2] | 99.9 [99.6, 100.0] | 0.1 [0.0, 0.4] | 0 / 1998 / 2 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Original | 0.0 [0.0, 0.2] | 97.2 [96.3, 97.8] | 2.9 [2.2, 3.7] | 0 / 1943 / 57 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Revised | 0.0 [0.0, 0.2] | 97.2 [96.3, 97.8] | 2.9 [2.2, 3.7] | 0 / 1943 / 57 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Final | 0.0 [0.0, 0.2] | 97.1 [96.3, 97.7] | 2.9 [2.3, 3.7] | 0 / 1942 / 58 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Final without sign | 0.0 [0.0, 0.2] | 97.1 [96.3, 97.7] | 2.9 [2.3, 3.7] | 0 / 1942 / 58 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Original | 0.1 [0.0, 0.3] | 42.3 [40.2, 44.5] | 57.6 [55.5, 59.8] | 1 / 846 / 1153 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Revised | 0.1 [0.0, 0.3] | 42.3 [40.2, 44.5] | 57.6 [55.5, 59.8] | 1 / 846 / 1153 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Final | 0.1 [0.0, 0.3] | 41.1 [39.0, 43.3] | 58.8 [56.6, 60.9] | 1 / 823 / 1176 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Final without sign | 0.1 [0.0, 0.3] | 41.1 [39.0, 43.3] | 58.8 [56.6, 60.9] | 1 / 823 / 1176 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Pooled | 0.0 [0.0, 0.2] | 92.5 [91.3, 93.6] | 7.4 [6.4, 8.7] | 0 / 1851 / 149 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Original | 0.0 [0.0, 0.2] | 83.2 [81.5, 84.8] | 16.8 [15.2, 18.5] | 0 / 1664 / 336 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Revised | 0.0 [0.0, 0.2] | 83.2 [81.5, 84.8] | 16.8 [15.2, 18.5] | 0 / 1664 / 336 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Final | 0.0 [0.0, 0.2] | 82.5 [80.7, 84.1] | 17.5 [15.9, 19.3] | 0 / 1649 / 351 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Final without sign | 0.0 [0.0, 0.2] | 82.5 [80.7, 84.1] | 17.5 [15.9, 19.3] | 0 / 1649 / 351 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Pooled | 0.0 [0.0, 0.2] | 99.8 [99.4, 99.9] | 0.2 [0.1, 0.6] | 0 / 1995 / 5 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Original | 5.7 [4.7, 6.7] | 10.8 [9.5, 12.2] | 83.5 [81.9, 85.1] | 113 / 216 / 1671 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Revised | 5.7 [4.7, 6.7] | 10.8 [9.5, 12.2] | 83.5 [81.9, 85.1] | 113 / 216 / 1671 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Final | 5.7 [4.7, 6.7] | 10.2 [9.0, 11.7] | 84.1 [82.4, 85.6] | 113 / 205 / 1682 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Final without sign | 5.7 [4.7, 6.7] | 10.2 [9.0, 11.7] | 84.1 [82.4, 85.6] | 113 / 205 / 1682 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Pooled | 1.9 [1.4, 2.6] | 45.6 [43.5, 47.8] | 52.4 [50.3, 54.6] | 38 / 913 / 1049 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Original | 15.5 [14.0, 17.2] | 1.9 [1.4, 2.7] | 82.5 [80.8, 84.2] | 310 / 39 / 1651 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Revised | 14.9 [13.5, 16.6] | 1.9 [1.4, 2.7] | 83.1 [81.4, 84.7] | 299 / 39 / 1662 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Final | 14.9 [13.5, 16.6] | 1.7 [1.2, 2.4] | 83.4 [81.7, 84.9] | 299 / 34 / 1667 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Final without sign | 15.5 [14.0, 17.2] | 1.7 [1.2, 2.4] | 82.8 [81.1, 84.4] | 310 / 34 / 1656 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Pooled | 5.9 [4.9, 7.0] | 28.1 [26.2, 30.1] | 66.0 [63.9, 68.1] | 117 / 562 / 1321 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Original | 6.3 [5.4, 7.5] | 6.1 [5.1, 7.2] | 87.5 [86.0, 88.9] | 127 / 122 / 1751 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Revised | 6.2 [5.3, 7.4] | 6.1 [5.1, 7.2] | 87.6 [86.1, 89.0] | 125 / 122 / 1753 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Final | 6.2 [5.3, 7.4] | 5.5 [4.6, 6.6] | 88.2 [86.7, 89.5] | 125 / 111 / 1764 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Final without sign | 6.3 [5.4, 7.5] | 5.5 [4.6, 6.6] | 88.1 [86.6, 89.4] | 127 / 111 / 1762 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Pooled | 2.1 [1.6, 2.9] | 43.9 [41.7, 46.1] | 53.9 [51.8, 56.1] | 43 / 878 / 1079 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Original | 5.4 [4.5, 6.5] | 9.2 [8.0, 10.5] | 85.5 [83.8, 86.9] | 108 / 183 / 1709 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Revised | 5.4 [4.5, 6.5] | 9.2 [8.0, 10.5] | 85.5 [83.8, 86.9] | 108 / 183 / 1709 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Final | 5.4 [4.5, 6.5] | 8.6 [7.4, 9.9] | 86.1 [84.5, 87.5] | 108 / 171 / 1721 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Final without sign | 5.4 [4.5, 6.5] | 8.6 [7.4, 9.9] | 86.1 [84.5, 87.5] | 108 / 171 / 1721 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Pooled | 1.4 [1.0, 2.0] | 46.2 [44.0, 48.3] | 52.4 [50.3, 54.6] | 28 / 923 / 1049 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Original | 16.1 [14.5, 17.7] | 1.4 [0.9, 2.0] | 82.6 [80.9, 84.2] | 321 / 27 / 1652 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Revised | 14.6 [13.1, 16.2] | 1.4 [0.9, 2.0] | 84.0 [82.4, 85.6] | 292 / 27 / 1681 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Final | 14.6 [13.1, 16.2] | 1.2 [0.8, 1.8] | 84.2 [82.5, 85.7] | 292 / 24 / 1684 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Final without sign | 16.1 [14.5, 17.7] | 1.2 [0.8, 1.8] | 82.8 [81.0, 84.3] | 321 / 24 / 1655 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Pooled | 5.9 [4.9, 7.0] | 26.0 [24.1, 28.0] | 68.1 [66.0, 70.1] | 118 / 520 / 1362 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Original | 10.9 [9.7, 12.4] | 1.4 [0.9, 2.0] | 87.7 [86.2, 89.1] | 219 / 27 / 1754 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Revised | 6.3 [5.3, 7.5] | 1.4 [0.9, 2.0] | 92.3 [91.1, 93.4] | 126 / 27 / 1847 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Final | 6.3 [5.3, 7.5] | 1.1 [0.7, 1.7] | 92.6 [91.4, 93.7] | 126 / 22 / 1852 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Final without sign | 10.9 [9.7, 12.4] | 1.1 [0.7, 1.7] | 87.9 [86.5, 89.3] | 219 / 22 / 1759 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Pooled | 4.2 [3.4, 5.2] | 31.2 [29.2, 33.3] | 64.6 [62.5, 66.7] | 84 / 624 / 1292 of 2000 |
| Zero change, 1 answer per specific request | haiku | Original | 0.3 [0.1, 0.7] | 10.0 [8.7, 11.3] | 89.8 [88.3, 91.0] | 6 / 199 / 1795 of 2000 |
| Zero change, 1 answer per specific request | haiku | Revised | 0.0 [0.0, 0.2] | 10.0 [8.7, 11.3] | 90.0 [88.7, 91.3] | 0 / 199 / 1801 of 2000 |
| Zero change, 1 answer per specific request | haiku | Final | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Zero change, 1 answer per specific request | haiku | Final without sign | 0.3 [0.1, 0.7] | 0.0 [0.0, 0.2] | 99.7 [99.3, 99.9] | 6 / 0 / 1994 of 2000 |
| Zero change, 1 answer per specific request | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Original | 1.9 [1.4, 2.6] | 0.0 [0.0, 0.2] | 98.1 [97.4, 98.6] | 38 / 0 / 1962 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Revised | 0.4 [0.2, 0.9] | 0.0 [0.0, 0.2] | 99.6 [99.1, 99.8] | 9 / 0 / 1991 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Final | 0.4 [0.2, 0.9] | 0.0 [0.0, 0.2] | 99.6 [99.1, 99.8] | 9 / 0 / 1991 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Final without sign | 1.9 [1.4, 2.6] | 0.0 [0.0, 0.2] | 98.1 [97.4, 98.6] | 38 / 0 / 1962 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Pooled | 0.0 [0.0, 0.2] | 94.7 [93.6, 95.6] | 5.3 [4.4, 6.4] | 0 / 1893 / 107 of 2000 |

### Change beyond the margin: wrong passes

Configurations (29): `A-both|deepseek|shift +15 both|n59m10`, `A-both|deepseek|shift +6 both|n59m10`, `A-both|deepseek|shift +8 both|n59m10`, `A-both|deepseek|shift -6 both|n59m10`, `A-both|haiku|shift +15 both|n59m10`, `A-both|haiku|shift +6 both|n59m10`, `A-both|haiku|shift +8 both|n59m10`, `A-both|sol|shift +15 both|n59m10`, `A-both|sol|shift +6 both|n59m10`, `A-both|sol|shift +8 both|n59m10`, `A-both|sol|shift -6 both|n59m10`, `B-spec|deepseek|shift +15 specific|n59m10`, `B-spec|deepseek|shift +6 specific|n59m10`, `B-spec|deepseek|shift +8 specific|n59m10`, `B-spec|haiku|shift +15 specific|n59m10`, `B-spec|haiku|shift +6 specific|n59m10`, `B-spec|haiku|shift +8 specific|n59m10`, `B-spec|sol|shift +15 specific|n59m10`, `B-spec|sol|shift +6 specific|n59m10`, `B-spec|sol|shift +8 specific|n59m10`, `S-sparse|deepseek|sparse +15 specific|n59m10`, `S-sparse|deepseek|sparse +6 specific|n59m10`, `S-sparse|deepseek|sparse +8 specific|n59m10`, `S-sparse|haiku|sparse +15 specific|n59m10`, `S-sparse|haiku|sparse +6 specific|n59m10`, `S-sparse|haiku|sparse +8 specific|n59m10`, `S-sparse|sol|sparse -15 specific|n59m10`, `S-sparse|sol|sparse -6 specific|n59m10`, `S-sparse|sol|sparse -8 specific|n59m10`

| Rule | Wrong passes / trials | Share % [95%] | Largest configuration share % [95%] |
|---|---|---|---|
| Original | 2 / 58000 | 0.0 [0.0, 0.0] | 0.1 [0.0, 0.3] (`B-spec|sol|shift +6 specific|n59m10`, 1 of 2000) |
| Revised | 2 / 58000 | 0.0 [0.0, 0.0] | 0.1 [0.0, 0.3] (`B-spec|sol|shift +6 specific|n59m10`, 1 of 2000) |
| Final | 2 / 58000 | 0.0 [0.0, 0.0] | 0.1 [0.0, 0.3] (`B-spec|sol|shift +6 specific|n59m10`, 1 of 2000) |
| Final without sign | 2 / 58000 | 0.0 [0.0, 0.0] | 0.1 [0.0, 0.3] (`B-spec|sol|shift +6 specific|n59m10`, 1 of 2000) |
| Pooled | 34258 / 58000 | 59.1 [58.7, 59.5] | 100.0 [99.8, 100.0] (`S-sparse|haiku|sparse +8 specific|n59m10`, 2000 of 2000) |

## C = 10 (level 99.50%; pooled 99.00%)

### Ranges across profiles (not intervals; the ends can come from different profiles)

| Scenario | Original F / P / H | Revised F / P / H | Final F / P / H | Final without sign F / P / H | Pooled F / P / H |
|---|---|---|---|---|---|
| Zero change | 0.0–0.2 / 35.5–94.0 / 6.0–64.2 | 0.0–0.1 / 35.5–94.0 / 6.0–64.3 | 0.0–0.1 / 33.6–93.2 / 6.8–66.3 | 0.0–0.2 / 33.6–93.2 / 6.8–66.2 | 0.0 / 94.8–100.0 / 0.0–5.2 |
| Shift of +6 in both sets | 92.0–96.0 / 0.0 / 4.0–8.1 | 91.5–95.4 / 0.0 / 4.6–8.5 | 91.5–95.4 / 0.0 / 4.6–8.5 | 92.0–96.0 / 0.0 / 4.0–8.1 | 77.1–82.2 / 0.1 / 17.8–22.8 |
| Shift of +6 in the specific set only | 70.7–81.8 / 0.0 / 18.1–29.3 | 69.0–79.0 / 0.0 / 20.9–31.1 | 69.0–79.0 / 0.0 / 20.9–31.1 | 70.7–81.8 / 0.0 / 18.1–29.3 | 0.0 / 90.2–100.0 / 0.0–9.8 |
| Sparse change on 6 specific requests (mean 8 points) | 33.2–59.3 / 0.0 / 40.7–66.8 | 2.2–4.5 / 0.0 / 95.5–97.8 | 2.2–4.5 / 0.0 / 95.5–97.8 | 33.2–59.3 / 0.0 / 40.7–66.8 | 0.0 / 83.3–100.0 / 0.0–16.7 |
| Cancelling changes, specific set (up to 12 down, 12 up) | 0.0 / 0.0 / 100.0 | 0.0 / 0.0 / 100.0 | 0.0 / 0.0 / 100.0 | 0.0 / 0.0 / 100.0 | 0.0 / 81.2–100.0 / 0.1–18.8 |
| Cancelling changes, open set (10 down, 10 up) | 0.0–0.1 / 22.4–93.4 / 6.6–77.5 | 0.0–0.1 / 22.4–93.4 / 6.6–77.5 | 0.0–0.1 / 20.4–93.0 / 7.0–79.5 | 0.0–0.1 / 20.4–93.0 / 7.0–79.5 | 0.0 / 83.7–100.0 / 0.0–16.4 |
| Drift of +3 on the new answers, no schema effect | 5.7–14.9 / 0.9–5.7 / 84.1–91.0 | 5.7–13.8 / 0.9–5.7 / 85.2–91.1 | 5.7–13.8 / 0.8–4.8 / 85.5–91.4 | 5.7–14.9 / 0.8–4.8 / 84.3–91.2 | 1.9–5.9 / 18.3–33.5 / 64.6–75.8 |
| Drift of -3 on the new answers, true shift of +6 in both sets | 5.4–15.2 / 0.4–5.1 / 84.4–90.5 | 5.3–13.0 / 0.4–5.1 / 86.7–93.3 | 5.3–13.0 / 0.3–4.2 / 86.7–93.4 | 5.4–15.2 / 0.3–4.2 / 84.4–90.5 | 1.4–5.9 / 16.2–34.1 / 64.5–78.0 |
| Zero change, 1 answer per specific request | 0.1–1.3 / 0.0–10.0 / 90.0–98.7 | 0.0–0.1 / 0.0–10.0 / 90.0–99.9 | 0.0–0.1 / 0.0 / 99.9–100.0 | 0.1–1.2 / 0.0 / 98.8–100.0 | 0.0 / 87.7–100.0 / 0.0–12.3 |

### Every scenario and profile

| Scenario | Profile | Rule | Flag % [95%] | Pass % [95%] | Hold % [95%] | k flag / pass / hold of n |
|---|---|---|---|---|---|---|
| Zero change | haiku | Original | 0.0 [0.0, 0.2] | 94.0 [92.9, 95.0] | 6.0 [5.0, 7.1] | 0 / 1880 / 120 of 2000 |
| Zero change | haiku | Revised | 0.0 [0.0, 0.2] | 94.0 [92.9, 95.0] | 6.0 [5.0, 7.1] | 0 / 1880 / 120 of 2000 |
| Zero change | haiku | Final | 0.0 [0.0, 0.2] | 93.2 [92.0, 94.2] | 6.8 [5.8, 8.0] | 0 / 1864 / 136 of 2000 |
| Zero change | haiku | Final without sign | 0.0 [0.0, 0.2] | 93.2 [92.0, 94.2] | 6.8 [5.8, 8.0] | 0 / 1864 / 136 of 2000 |
| Zero change | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Zero change | deepseek | Original | 0.2 [0.1, 0.5] | 35.5 [33.5, 37.7] | 64.2 [62.1, 66.3] | 4 / 711 / 1285 of 2000 |
| Zero change | deepseek | Revised | 0.1 [0.0, 0.4] | 35.5 [33.5, 37.7] | 64.3 [62.2, 66.4] | 2 / 711 / 1287 of 2000 |
| Zero change | deepseek | Final | 0.1 [0.0, 0.4] | 33.6 [31.6, 35.7] | 66.3 [64.2, 68.3] | 2 / 672 / 1326 of 2000 |
| Zero change | deepseek | Final without sign | 0.2 [0.1, 0.5] | 33.6 [31.6, 35.7] | 66.2 [64.1, 68.2] | 4 / 672 / 1324 of 2000 |
| Zero change | deepseek | Pooled | 0.0 [0.0, 0.2] | 94.8 [93.7, 95.6] | 5.2 [4.4, 6.3] | 0 / 1895 / 105 of 2000 |
| Zero change | sol | Original | 0.1 [0.0, 0.3] | 78.8 [76.9, 80.5] | 21.2 [19.5, 23.0] | 1 / 1575 / 424 of 2000 |
| Zero change | sol | Revised | 0.0 [0.0, 0.2] | 78.8 [76.9, 80.5] | 21.2 [19.5, 23.1] | 0 / 1575 / 425 of 2000 |
| Zero change | sol | Final | 0.0 [0.0, 0.2] | 77.5 [75.7, 79.3] | 22.4 [20.7, 24.3] | 0 / 1551 / 449 of 2000 |
| Zero change | sol | Final without sign | 0.1 [0.0, 0.3] | 77.5 [75.7, 79.3] | 22.4 [20.6, 24.3] | 1 / 1551 / 448 of 2000 |
| Zero change | sol | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Shift of +6 in both sets | haiku | Original | 95.4 [94.4, 96.2] | 0.0 [0.0, 0.2] | 4.6 [3.8, 5.6] | 1908 / 0 / 92 of 2000 |
| Shift of +6 in both sets | haiku | Revised | 95.4 [94.4, 96.2] | 0.0 [0.0, 0.2] | 4.6 [3.8, 5.6] | 1908 / 0 / 92 of 2000 |
| Shift of +6 in both sets | haiku | Final | 95.4 [94.4, 96.2] | 0.0 [0.0, 0.2] | 4.6 [3.8, 5.6] | 1908 / 0 / 92 of 2000 |
| Shift of +6 in both sets | haiku | Final without sign | 95.4 [94.4, 96.2] | 0.0 [0.0, 0.2] | 4.6 [3.8, 5.6] | 1908 / 0 / 92 of 2000 |
| Shift of +6 in both sets | haiku | Pooled | 82.2 [80.4, 83.8] | 0.1 [0.0, 0.4] | 17.8 [16.1, 19.5] | 1643 / 2 / 355 of 2000 |
| Shift of +6 in both sets | deepseek | Original | 92.0 [90.7, 93.1] | 0.0 [0.0, 0.2] | 8.1 [6.9, 9.3] | 1839 / 0 / 161 of 2000 |
| Shift of +6 in both sets | deepseek | Revised | 91.5 [90.2, 92.7] | 0.0 [0.0, 0.2] | 8.5 [7.3, 9.8] | 1831 / 0 / 169 of 2000 |
| Shift of +6 in both sets | deepseek | Final | 91.5 [90.2, 92.7] | 0.0 [0.0, 0.2] | 8.5 [7.3, 9.8] | 1831 / 0 / 169 of 2000 |
| Shift of +6 in both sets | deepseek | Final without sign | 92.0 [90.7, 93.1] | 0.0 [0.0, 0.2] | 8.1 [6.9, 9.3] | 1839 / 0 / 161 of 2000 |
| Shift of +6 in both sets | deepseek | Pooled | 77.1 [75.3, 78.9] | 0.1 [0.0, 0.4] | 22.8 [21.0, 24.6] | 1543 / 2 / 455 of 2000 |
| Shift of +6 in both sets | sol | Original | 96.0 [95.1, 96.8] | 0.0 [0.0, 0.2] | 4.0 [3.2, 4.9] | 1921 / 0 / 79 of 2000 |
| Shift of +6 in both sets | sol | Revised | 95.3 [94.3, 96.2] | 0.0 [0.0, 0.2] | 4.7 [3.8, 5.7] | 1907 / 0 / 93 of 2000 |
| Shift of +6 in both sets | sol | Final | 95.3 [94.3, 96.2] | 0.0 [0.0, 0.2] | 4.7 [3.8, 5.7] | 1907 / 0 / 93 of 2000 |
| Shift of +6 in both sets | sol | Final without sign | 96.0 [95.1, 96.8] | 0.0 [0.0, 0.2] | 4.0 [3.2, 4.9] | 1921 / 0 / 79 of 2000 |
| Shift of +6 in both sets | sol | Pooled | 82.0 [80.3, 83.6] | 0.1 [0.0, 0.3] | 17.9 [16.3, 19.7] | 1640 / 1 / 359 of 2000 |
| Shift of +6 in the specific set only | haiku | Original | 78.8 [77.0, 80.6] | 0.0 [0.0, 0.2] | 21.1 [19.4, 23.0] | 1577 / 0 / 423 of 2000 |
| Shift of +6 in the specific set only | haiku | Revised | 78.8 [77.0, 80.6] | 0.0 [0.0, 0.2] | 21.1 [19.4, 23.0] | 1577 / 0 / 423 of 2000 |
| Shift of +6 in the specific set only | haiku | Final | 78.8 [77.0, 80.6] | 0.0 [0.0, 0.2] | 21.1 [19.4, 23.0] | 1577 / 0 / 423 of 2000 |
| Shift of +6 in the specific set only | haiku | Final without sign | 78.8 [77.0, 80.6] | 0.0 [0.0, 0.2] | 21.1 [19.4, 23.0] | 1577 / 0 / 423 of 2000 |
| Shift of +6 in the specific set only | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Shift of +6 in the specific set only | deepseek | Original | 70.7 [68.6, 72.6] | 0.0 [0.0, 0.2] | 29.3 [27.4, 31.4] | 1413 / 0 / 587 of 2000 |
| Shift of +6 in the specific set only | deepseek | Revised | 69.0 [66.9, 70.9] | 0.0 [0.0, 0.2] | 31.1 [29.1, 33.1] | 1379 / 0 / 621 of 2000 |
| Shift of +6 in the specific set only | deepseek | Final | 69.0 [66.9, 70.9] | 0.0 [0.0, 0.2] | 31.1 [29.1, 33.1] | 1379 / 0 / 621 of 2000 |
| Shift of +6 in the specific set only | deepseek | Final without sign | 70.7 [68.6, 72.6] | 0.0 [0.0, 0.2] | 29.3 [27.4, 31.4] | 1413 / 0 / 587 of 2000 |
| Shift of +6 in the specific set only | deepseek | Pooled | 0.0 [0.0, 0.2] | 90.2 [88.8, 91.4] | 9.8 [8.6, 11.2] | 0 / 1804 / 196 of 2000 |
| Shift of +6 in the specific set only | sol | Original | 81.8 [80.1, 83.5] | 0.0 [0.0, 0.2] | 18.1 [16.5, 19.9] | 1637 / 0 / 363 of 2000 |
| Shift of +6 in the specific set only | sol | Revised | 79.0 [77.2, 80.8] | 0.0 [0.0, 0.2] | 20.9 [19.2, 22.8] | 1581 / 0 / 419 of 2000 |
| Shift of +6 in the specific set only | sol | Final | 79.0 [77.2, 80.8] | 0.0 [0.0, 0.2] | 20.9 [19.2, 22.8] | 1581 / 0 / 419 of 2000 |
| Shift of +6 in the specific set only | sol | Final without sign | 81.8 [80.1, 83.5] | 0.0 [0.0, 0.2] | 18.1 [16.5, 19.9] | 1637 / 0 / 363 of 2000 |
| Shift of +6 in the specific set only | sol | Pooled | 0.0 [0.0, 0.2] | 99.7 [99.3, 99.9] | 0.3 [0.1, 0.7] | 0 / 1994 / 6 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Original | 59.3 [57.1, 61.4] | 0.0 [0.0, 0.2] | 40.7 [38.6, 42.9] | 1186 / 0 / 814 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Revised | 4.5 [3.7, 5.5] | 0.0 [0.0, 0.2] | 95.5 [94.5, 96.3] | 90 / 0 / 1910 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Final | 4.5 [3.7, 5.5] | 0.0 [0.0, 0.2] | 95.5 [94.5, 96.3] | 90 / 0 / 1910 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Final without sign | 59.3 [57.1, 61.4] | 0.0 [0.0, 0.2] | 40.7 [38.6, 42.9] | 1186 / 0 / 814 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Original | 33.2 [31.2, 35.3] | 0.0 [0.0, 0.2] | 66.8 [64.7, 68.8] | 664 / 0 / 1336 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Revised | 2.2 [1.6, 2.9] | 0.0 [0.0, 0.2] | 97.8 [97.1, 98.4] | 44 / 0 / 1956 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Final | 2.2 [1.6, 2.9] | 0.0 [0.0, 0.2] | 97.8 [97.1, 98.4] | 44 / 0 / 1956 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Final without sign | 33.2 [31.2, 35.3] | 0.0 [0.0, 0.2] | 66.8 [64.7, 68.8] | 664 / 0 / 1336 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | deepseek | Pooled | 0.0 [0.0, 0.2] | 83.3 [81.6, 84.9] | 16.7 [15.1, 18.4] | 0 / 1666 / 334 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Original | 50.3 [48.1, 52.5] | 0.0 [0.0, 0.2] | 49.7 [47.5, 51.9] | 1006 / 0 / 994 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Revised | 3.6 [2.9, 4.5] | 0.0 [0.0, 0.2] | 96.4 [95.5, 97.1] | 72 / 0 / 1928 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Final | 3.6 [2.9, 4.5] | 0.0 [0.0, 0.2] | 96.4 [95.5, 97.1] | 72 / 0 / 1928 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Final without sign | 46.1 [43.9, 48.3] | 0.0 [0.0, 0.2] | 53.9 [51.7, 56.1] | 922 / 0 / 1078 of 2000 |
| Sparse change on 6 specific requests (mean 8 points) | sol | Pooled | 0.0 [0.0, 0.2] | 99.4 [98.9, 99.6] | 0.7 [0.4, 1.1] | 0 / 1987 / 13 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Original | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Revised | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Final | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Final without sign | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.7, 100.0] | 0.1 [0.0, 0.3] | 0 / 1999 / 1 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Original | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Revised | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Final | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Final without sign | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | deepseek | Pooled | 0.0 [0.0, 0.2] | 81.2 [79.5, 82.9] | 18.8 [17.1, 20.5] | 0 / 1625 / 375 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Original | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Revised | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Final | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Final without sign | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Cancelling changes, specific set (up to 12 down, 12 up) | sol | Pooled | 0.0 [0.0, 0.2] | 99.6 [99.2, 99.8] | 0.4 [0.2, 0.8] | 0 / 1992 / 8 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Original | 0.0 [0.0, 0.2] | 93.4 [92.2, 94.4] | 6.6 [5.6, 7.8] | 0 / 1868 / 132 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Revised | 0.0 [0.0, 0.2] | 93.4 [92.2, 94.4] | 6.6 [5.6, 7.8] | 0 / 1868 / 132 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Final | 0.0 [0.0, 0.2] | 93.0 [91.7, 94.0] | 7.0 [6.0, 8.3] | 0 / 1859 / 141 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Final without sign | 0.0 [0.0, 0.2] | 93.0 [91.7, 94.0] | 7.0 [6.0, 8.3] | 0 / 1859 / 141 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Original | 0.1 [0.0, 0.3] | 22.4 [20.6, 24.3] | 77.5 [75.7, 79.3] | 1 / 448 / 1551 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Revised | 0.1 [0.0, 0.3] | 22.4 [20.6, 24.3] | 77.5 [75.7, 79.3] | 1 / 448 / 1551 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Final | 0.1 [0.0, 0.3] | 20.4 [18.7, 22.2] | 79.5 [77.7, 81.3] | 1 / 408 / 1591 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Final without sign | 0.1 [0.0, 0.3] | 20.4 [18.7, 22.2] | 79.5 [77.7, 81.3] | 1 / 408 / 1591 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | deepseek | Pooled | 0.0 [0.0, 0.2] | 83.7 [82.0, 85.2] | 16.4 [14.8, 18.0] | 0 / 1673 / 327 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Original | 0.0 [0.0, 0.2] | 71.0 [68.9, 72.9] | 29.0 [27.1, 31.1] | 0 / 1419 / 581 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Revised | 0.0 [0.0, 0.2] | 71.0 [68.9, 72.9] | 29.0 [27.1, 31.1] | 0 / 1419 / 581 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Final | 0.0 [0.0, 0.2] | 69.7 [67.6, 71.6] | 30.3 [28.4, 32.4] | 0 / 1393 / 607 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Final without sign | 0.0 [0.0, 0.2] | 69.7 [67.6, 71.6] | 30.3 [28.4, 32.4] | 0 / 1393 / 607 of 2000 |
| Cancelling changes, open set (10 down, 10 up) | sol | Pooled | 0.0 [0.0, 0.2] | 99.4 [99.0, 99.7] | 0.6 [0.3, 1.0] | 0 / 1988 / 12 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Original | 5.7 [4.7, 6.7] | 5.7 [4.8, 6.8] | 88.6 [87.2, 90.0] | 113 / 114 / 1773 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Revised | 5.7 [4.7, 6.7] | 5.7 [4.8, 6.8] | 88.6 [87.2, 90.0] | 113 / 114 / 1773 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Final | 5.7 [4.7, 6.7] | 4.8 [3.9, 5.8] | 89.6 [88.2, 90.9] | 113 / 95 / 1792 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Final without sign | 5.7 [4.7, 6.7] | 4.8 [3.9, 5.8] | 89.6 [88.2, 90.9] | 113 / 95 / 1792 of 2000 |
| Drift of +3 on the new answers, no schema effect | haiku | Pooled | 1.9 [1.4, 2.6] | 33.5 [31.5, 35.6] | 64.6 [62.5, 66.7] | 38 / 670 / 1292 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Original | 14.9 [13.5, 16.6] | 0.9 [0.6, 1.5] | 84.1 [82.4, 85.6] | 299 / 19 / 1682 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Revised | 13.8 [12.4, 15.4] | 0.9 [0.6, 1.5] | 85.2 [83.6, 86.7] | 276 / 19 / 1705 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Final | 13.8 [12.4, 15.4] | 0.8 [0.5, 1.2] | 85.5 [83.8, 86.9] | 276 / 15 / 1709 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Final without sign | 14.9 [13.5, 16.6] | 0.8 [0.5, 1.2] | 84.3 [82.6, 85.8] | 299 / 15 / 1686 of 2000 |
| Drift of +3 on the new answers, no schema effect | deepseek | Pooled | 5.9 [4.9, 7.0] | 18.3 [16.7, 20.1] | 75.8 [73.9, 77.7] | 117 / 366 / 1517 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Original | 6.3 [5.4, 7.5] | 2.7 [2.1, 3.5] | 91.0 [89.6, 92.1] | 127 / 54 / 1819 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Revised | 6.2 [5.2, 7.3] | 2.7 [2.1, 3.5] | 91.1 [89.8, 92.3] | 123 / 54 / 1823 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Final | 6.2 [5.2, 7.3] | 2.5 [1.9, 3.2] | 91.4 [90.1, 92.6] | 123 / 49 / 1828 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Final without sign | 6.3 [5.4, 7.5] | 2.5 [1.9, 3.2] | 91.2 [89.9, 92.4] | 127 / 49 / 1824 of 2000 |
| Drift of +3 on the new answers, no schema effect | sol | Pooled | 2.1 [1.6, 2.9] | 30.5 [28.5, 32.6] | 67.3 [65.3, 69.4] | 43 / 610 / 1347 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Original | 5.4 [4.5, 6.5] | 5.1 [4.2, 6.1] | 89.5 [88.1, 90.8] | 108 / 101 / 1791 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Revised | 5.3 [4.4, 6.4] | 5.1 [4.2, 6.1] | 89.6 [88.2, 90.9] | 107 / 101 / 1792 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Final | 5.3 [4.4, 6.4] | 4.2 [3.4, 5.2] | 90.5 [89.1, 91.7] | 107 / 84 / 1809 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Final without sign | 5.4 [4.5, 6.5] | 4.2 [3.4, 5.2] | 90.4 [89.0, 91.6] | 108 / 84 / 1808 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | haiku | Pooled | 1.4 [1.0, 2.0] | 34.1 [32.0, 36.2] | 64.5 [62.4, 66.6] | 28 / 681 / 1291 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Original | 15.2 [13.7, 16.9] | 0.4 [0.2, 0.7] | 84.4 [82.7, 85.9] | 305 / 7 / 1688 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Revised | 13.0 [11.5, 14.5] | 0.4 [0.2, 0.7] | 86.7 [85.1, 88.1] | 259 / 7 / 1734 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Final | 13.0 [11.5, 14.5] | 0.4 [0.2, 0.7] | 86.7 [85.1, 88.1] | 259 / 7 / 1734 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Final without sign | 15.2 [13.7, 16.9] | 0.4 [0.2, 0.7] | 84.4 [82.7, 85.9] | 305 / 7 / 1688 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | deepseek | Pooled | 5.9 [4.9, 7.0] | 16.2 [14.6, 17.8] | 78.0 [76.1, 79.7] | 118 / 323 / 1559 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Original | 9.2 [8.0, 10.5] | 0.4 [0.2, 0.8] | 90.5 [89.1, 91.7] | 183 / 8 / 1809 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Revised | 6.3 [5.3, 7.5] | 0.4 [0.2, 0.8] | 93.3 [92.1, 94.3] | 126 / 8 / 1866 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Final | 6.3 [5.3, 7.5] | 0.3 [0.1, 0.7] | 93.4 [92.2, 94.4] | 126 / 6 / 1868 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Final without sign | 9.2 [8.0, 10.5] | 0.3 [0.1, 0.7] | 90.5 [89.2, 91.8] | 183 / 6 / 1811 of 2000 |
| Drift of -3 on the new answers, true shift of +6 in both sets | sol | Pooled | 4.2 [3.4, 5.2] | 20.8 [19.1, 22.7] | 75.0 [73.0, 76.8] | 84 / 417 / 1499 of 2000 |
| Zero change, 1 answer per specific request | haiku | Original | 0.1 [0.0, 0.3] | 10.0 [8.7, 11.3] | 90.0 [88.6, 91.2] | 1 / 199 / 1800 of 2000 |
| Zero change, 1 answer per specific request | haiku | Revised | 0.0 [0.0, 0.2] | 10.0 [8.7, 11.3] | 90.0 [88.7, 91.3] | 0 / 199 / 1801 of 2000 |
| Zero change, 1 answer per specific request | haiku | Final | 0.0 [0.0, 0.2] | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0 / 0 / 2000 of 2000 |
| Zero change, 1 answer per specific request | haiku | Final without sign | 0.1 [0.0, 0.3] | 0.0 [0.0, 0.2] | 100.0 [99.7, 100.0] | 1 / 0 / 1999 of 2000 |
| Zero change, 1 answer per specific request | haiku | Pooled | 0.0 [0.0, 0.2] | 100.0 [99.8, 100.0] | 0.0 [0.0, 0.2] | 0 / 2000 / 0 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Original | 1.3 [0.9, 1.9] | 0.0 [0.0, 0.2] | 98.7 [98.1, 99.1] | 26 / 0 / 1974 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Revised | 0.1 [0.1, 0.4] | 0.0 [0.0, 0.2] | 99.9 [99.6, 99.9] | 3 / 0 / 1997 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Final | 0.1 [0.1, 0.4] | 0.0 [0.0, 0.2] | 99.9 [99.6, 99.9] | 3 / 0 / 1997 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Final without sign | 1.2 [0.8, 1.8] | 0.0 [0.0, 0.2] | 98.8 [98.2, 99.2] | 24 / 0 / 1976 of 2000 |
| Zero change, 1 answer per specific request | deepseek | Pooled | 0.0 [0.0, 0.2] | 87.7 [86.2, 89.1] | 12.3 [10.9, 13.8] | 0 / 1754 / 246 of 2000 |

### Change beyond the margin: wrong passes

Configurations (29): `A-both|deepseek|shift +15 both|n59m10`, `A-both|deepseek|shift +6 both|n59m10`, `A-both|deepseek|shift +8 both|n59m10`, `A-both|deepseek|shift -6 both|n59m10`, `A-both|haiku|shift +15 both|n59m10`, `A-both|haiku|shift +6 both|n59m10`, `A-both|haiku|shift +8 both|n59m10`, `A-both|sol|shift +15 both|n59m10`, `A-both|sol|shift +6 both|n59m10`, `A-both|sol|shift +8 both|n59m10`, `A-both|sol|shift -6 both|n59m10`, `B-spec|deepseek|shift +15 specific|n59m10`, `B-spec|deepseek|shift +6 specific|n59m10`, `B-spec|deepseek|shift +8 specific|n59m10`, `B-spec|haiku|shift +15 specific|n59m10`, `B-spec|haiku|shift +6 specific|n59m10`, `B-spec|haiku|shift +8 specific|n59m10`, `B-spec|sol|shift +15 specific|n59m10`, `B-spec|sol|shift +6 specific|n59m10`, `B-spec|sol|shift +8 specific|n59m10`, `S-sparse|deepseek|sparse +15 specific|n59m10`, `S-sparse|deepseek|sparse +6 specific|n59m10`, `S-sparse|deepseek|sparse +8 specific|n59m10`, `S-sparse|haiku|sparse +15 specific|n59m10`, `S-sparse|haiku|sparse +6 specific|n59m10`, `S-sparse|haiku|sparse +8 specific|n59m10`, `S-sparse|sol|sparse -15 specific|n59m10`, `S-sparse|sol|sparse -6 specific|n59m10`, `S-sparse|sol|sparse -8 specific|n59m10`

| Rule | Wrong passes / trials | Share % [95%] | Largest configuration share % [95%] |
|---|---|---|---|
| Original | 0 / 58000 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.2] (`S-sparse|sol|sparse -8 specific|n59m10`, 0 of 2000) |
| Revised | 0 / 58000 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.2] (`S-sparse|sol|sparse -8 specific|n59m10`, 0 of 2000) |
| Final | 0 / 58000 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.2] (`S-sparse|sol|sparse -8 specific|n59m10`, 0 of 2000) |
| Final without sign | 0 / 58000 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.2] (`S-sparse|sol|sparse -8 specific|n59m10`, 0 of 2000) |
| Pooled | 33007 / 58000 | 56.9 [56.5, 57.3] | 100.0 [99.8, 100.0] (`S-sparse|haiku|sparse +8 specific|n59m10`, 2000 of 2000) |

