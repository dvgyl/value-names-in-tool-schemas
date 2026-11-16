## the paper, final 8: new numbers (post hoc descriptions; no model call)

- Chapter 2 (author's blind check): 30 of 30 replies labelled; groups {'Claude replies from the flag runs (audited)': 12, 'Sol and Astra replies': 8, 'Claude replies on hotel briefs': 10}; the author judged 29 of 30 as telling the traveller something; the word rule agreed on 22 of 30 (73%), kappa -0.06; 8 disagreements, of which 7 are rule 'no tell' where the author saw a hotels-only statement (c01, c08, c16, c17, c24, c27, c28).
- Verifier run of the open-weight models: 2080 original-form answers per model (2 x (807 + 233)); cut at the output limit: {'deepseek': 0, 'qwen': 118, 'gemma': 13}.
- Constructed texts: size values ['small', 'large'], glosses ['fewer than 50 employees', '50 employees or more'].
- First service run, Haiku, rewrite G1, 448 no-type requests: exclusion change +18.5 (either type), of which hotel-only +12.9.
- Test 1, hotel-only score: -11.6 [-14.5, -8.9] (registered score -13.0 [-16.0, -10.1]).
