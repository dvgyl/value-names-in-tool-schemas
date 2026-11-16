## Steering decisions: sensitivity to the bootstrap (post hoc)

No model call. Level 98.75%, L = 5, hotel value. Registered: 2000 draws, seed 20261112. Check: 20000 draws, seed 20261112, then 11 seeds (20261112 to 20261122). The rule of Appendix I decides, unchanged.

| Agent | Cell | Set | Pairs | Change | 2,000 draws | Decision | 20,000 draws | Decision | Ends over seeds (low; high) | Decisions over seeds |
|---|---|---|---|---|---|---|---|---|---|---|
| sonnet | th | open | 448 | +8.26 | [+5.13, +11.83] | flag-worthy | [+5.13, +11.61] | flag-worthy | +5.13 to +5.13; +11.61 to +11.61 | flag-worthy |
| sonnet | th | specific | 59 | +11.86 | [+1.69, +23.73] | flag-worthy | [+3.39, +23.73] | flag-worthy | +1.69 to +3.39; +23.73 to +23.73 | flag-worthy |
| sonnet | tg | open | 448 | +11.61 | [+7.81, +15.62] | flag-worthy | [+7.81, +15.62] | flag-worthy | +7.81 to +8.04; +15.62 to +15.62 | flag-worthy |
| sonnet | tg | specific | 59 | +25.42 | [+11.86, +40.68] | flag-worthy | [+11.86, +40.68] | flag-worthy | +11.86 to +11.86; +38.98 to +40.68 | flag-worthy |
| haiku | th | open | 448 | +34.15 | [+28.57, +39.96] | flag-worthy | [+28.57, +39.96] | flag-worthy | +28.57 to +28.57; +39.73 to +39.96 | flag-worthy |
| haiku | th | specific | 59 | +69.49 | [+54.24, +84.75] | flag-worthy | [+54.24, +83.05] | flag-worthy | +54.24 to +54.24; +83.05 to +84.75 | flag-worthy |
| haiku | tg | open | 448 | +29.46 | [+24.11, +35.27] | flag-worthy | [+23.88, +35.04] | flag-worthy | +23.88 to +24.11; +34.82 to +35.04 | flag-worthy |
| haiku | tg | specific | 59 | +49.15 | [+30.51, +64.41] | flag-worthy | [+32.20, +66.10] | flag-worthy | +32.20 to +33.90; +64.41 to +66.10 | flag-worthy |

- sonnet th: model decision flag (2,000 draws), flag (20,000 draws), flag (each of the seeds).
- sonnet tg: model decision flag (2,000 draws), flag (20,000 draws), flag (each of the seeds).
- haiku th: model decision flag (2,000 draws), flag (20,000 draws), flag (each of the seeds).
- haiku tg: model decision flag (2,000 draws), flag (20,000 draws), flag (each of the seeds).
