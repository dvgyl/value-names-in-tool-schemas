# T1b: derived checks (post hoc; sim.json only)

- C = 4: configurations 126; final vs without sign, pass counts differ in 0; original vs revised differ in 0.
- C = 10: configurations 126; final vs without sign, pass counts differ in 0; original vs revised differ in 0.
- Largest flag-share difference (without sign minus final), shifts A-both and B-spec, paper design, C=4: 0.95 points (`A-both|deepseek|shift -5 both|n59m10`).
- Largest flag-share difference (without sign minus final), shifts A-both and B-spec, paper design, C=10: 2.80 points (`B-spec|sol|shift +6 specific|n59m10`).
- Largest flag-share difference (without sign minus final), S-sparse, paper design, C=4: 72.45 points (`S-sparse|deepseek|sparse +15 specific|n59m10`).
- Largest flag-share difference (without sign minus final), X-cancel, paper design, C=4: 0.00 points (`X-cancel|haiku|cancel 2 down 2 up specific|n59m10`).
- Largest flag-share difference (without sign minus final), Z-drift, paper design, C=4: 4.65 points (`Z-drift|sol|shift +6 both, drift -3|n59m10`).
- Largest flag-share difference (without sign minus final), N-size, other designs, C=4: 21.40 points (`N-size|haiku|shift +8 specific|n59m1`).
- Zero change, paper design, C = 4: flags final 4, without sign 5, original 5, of 6000 trials.
- Zero change, 59 x 1, C = 4, original: flag share 0.30% to 1.90%.
- Zero change, 59 x 1, C = 4, final: flag share 0.00% to 0.45%.
- Zero change, 59 x 1, C = 4, strat_nosign: flag share 0.30% to 1.90%.
- Drift +3, no effect, C = 4, four stratified rules: flag share 5.65% to 15.50%.
