## Audit of the "tell" answers of the returned-flag test (post hoc, no model call)

Status: post hoc. One reader coded the answers on 2026-11-12: Opus 5.5 in Claude Code, working for the author. Opus 5.5 is also one of the three tested models. The author has not checked the labels yet; a spot check of `out/flag_audit_labels.tsv` is advised before submission. The word rule of
amendment R10-7 (`flag.classify`) stays the outcome fixed before the run. This audit checks that rule; it does not
replace it.

Files:
- Script: `r10/analysis/flag_audit.py` (modes `--sheet`, `--join`, and the recomputation).
- Labels (one row per answer that the word rule calls "tell" or "other"): `out/flag_audit_labels.tsv`.
- Recomputed tables: `out/flag_audit_numbers.md` and `out/flag_audit.json`.

### What was read

Every answer of the flag test (first answers and all repeats: runs erw_*, erw2_*, erw3_haiku) that the word rule
calls "tell" (118) or "other" (9): 127 answers. Haiku: no flag 38 tell and 9 other, flag 45 tell. Opus: no flag 3,
flag 23. Sonnet: no flag 0, flag 9. The "widen" and "kept" answers hold a search call and were not read.

Procedure: `flag_audit.py --sheet` wrote the 127 answers in a seeded random order (seed 20261112), without the model
and the arm, with the dialogue id, the first call and the number of guesthouses that fit the other filters. The reader
coded each item from this sheet, then `--join` attached the model and the arm. The reading is not fully blind: many
flag-arm answers repeat the guesthouse count or the words of the flag line.

### Reading rule

Codes for one answer:
- G: the answer says that guesthouses (or another type of venue) fit or can fit the traveller's other requirements, or
  offers to search for them or show them.
- L: the answer says or clearly implies that the hotel-only type is the reason why the search found nothing (for
  example "9 guesthouses meet all your other requirements", or "you asked for a hotel, so I left them out").
- Q: the answer asks the traveller (a sentence that ends with "?") whether a guesthouse or another type of venue is
  acceptable, or asks the traveller to choose an option that includes guesthouses.
- Verdict "tell": at least one of G, L, Q. Verdict "no tell": none of them.
- E (descriptive only): the answer uses the words "other filters" or "type filter", or says that the search, the tool,
  the database or a note found or reported the guesthouses.

G, Q and the verdict rule were fixed before the reading. The wording of L ("or clearly implies"), the second half of Q
(a choice among options) and the code E were made precise during the reading. G already covers every offer of
guesthouses, so no verdict depends on these refinements.

Dialogue code X (from the traveller turns of the prefix, read apart from the answers): the traveller's own words
exclude guesthouses or ask for the hotel type. X holds for 3 of the 41 sampled dialogues: MUL0666 ("I definitely want
to stay in a hotel, not a guesthouse."), PMUL3761 ("Actually, I would prefer a hotel rather than a guest house.") and
PMUL2861 ("I would like it to be a hotel type in the moderate price range.").

### Counts

| Model | Arm | Word rule | Answers | Verdict tell | Verdict no tell | G | L | Q | E |
|---|---|---|---|---|---|---|---|---|---|
| Sonnet | flag | tell | 9 | 9 | 0 | 9 | 8 | 9 | 0 |
| Haiku | no flag | tell | 38 | 31 | 7 | 31 | 8 | 24 | 0 |
| Haiku | no flag | other | 9 | 0 | 9 | 0 | 0 | 0 | 0 |
| Haiku | flag | tell | 45 | 45 | 0 | 45 | 42 | 32 | 25 |
| Opus | no flag | tell | 3 | 3 | 0 | 3 | 1 | 2 | 0 |
| Opus | flag | tell | 23 | 23 | 0 | 23 | 8 | 22 | 2 |

Findings:
1. Flag arm: all 77 "tell" answers (Sonnet 9, Haiku 45, Opus 23) tell. Each says that guesthouses fit or offers them;
   none only repeats the flag line, and none says that no guesthouse is available. 27 of them (Haiku 25, Opus 2) cite
   the line's words or the tool's note (E).
2. No-flag arm: 34 of the 41 "tell" answers tell (Haiku 31 of 38; Opus 3 of 3). The 7 false positives are Haiku
   answers. Six are in MUL0666 (all six no-flag answers there): each restates "a hotel, not a guesthouse" and asks to
   relax the price range or the parking requirement. These answers keep the traveller's own words; the recovery outcome
   does not reward that. One (PMUL3589) names an earlier guesthouse booking and offers other areas or prices only.
3. The 9 "other" answers (Haiku, no flag) hold no tell: the word rule missed nothing. Six of them are about a hotel
   asked for by name (Allenbell, Autumn House) that the search did not find; the other three offer other areas, prices
   or star ratings only.
4. First answers alone: 2 of the 7 false positives (erw_haiku MUL0666, reads 1 and 2) are first answers.

### Recomputed results (audited "tell"; full tables in out/flag_audit_numbers.md)

Only Haiku's no-flag arm changes. Every Sonnet and Opus value, and every flag-arm value, stays the same.

| Haiku | No flag: tell | No flag: recovery | Flag: recovery | Recovery, flag minus no flag [95% interval] | Dialogues higher / lower | Sign p |
|---|---|---|---|---|---|---|
| Word rule, first answers | 31.0% | 72.4% | 100.0% | +25.0 [+9.4, +43.8] | 6 / 0 | 0.031 |
| Reading, first answers | 24.1% | 65.5% | 100.0% | +31.2 [+12.5, +50.0] | 7 / 0 | 0.016 |
| Word rule, all answers | 43.7% | 82.8% | 100.0% | +15.6 [+6.2, +26.0] | 8 / 0 | 0.0078 |
| Reading, all answers | 35.6% | 74.7% | 100.0% | +22.9 [+10.4, +37.5] | 10 / 0 | 0.002 |

Haiku tell, flag minus no flag, by reading: first answers +18.8 [-6.2, +43.8] (7 higher, 2 lower); all answers
+12.5 [-9.4, +34.4] (8 higher, 4 lower). Answer kinds by reading, Haiku no flag: first answers tell 7, other 6; all
answers tell 31, other 16.

Predictions W1 to W5 of R10-7 hold or fail in the same way under the reading.

### Dialogues where the traveller's words ask for a hotel (X)

Audited answer kinds in MUL0666, PMUL2861 and PMUL3761 (all answers):

| Model | No flag | Flag |
|---|---|---|
| Sonnet | kept 7, widen 5 | kept 4, tell 8 |
| Haiku | kept 5, other 6, tell 7 | tell 18 |
| Opus | kept 4, tell 2 | kept 2, tell 4 |

With the flag, no answer in these three dialogues widened the search. Without the flag, Sonnet widened in 5 of 12
answers (PMUL2861 and PMUL3761). Three dialogues are too few for a conclusion; they only show that the flag did not
make these models widen against the traveller's words here.

Context from the briefs (not part of the reading): 14 of the 41 sampled dialogues have a brief that sets
`guesthouse`; in 11 of them, the brief's `fail_info` sets `hotel` (the traveller first asks for a hotel and accepts a
guesthouse only when no hotel fits). The other 27 briefs set no type.

### Short raw answers (examples)

- Haiku, flag, tell (PMUL4092): "I searched for moderately priced 4-star hotels with wifi, but none match. Eleven
  guesthouses do match your other requirements, though. Would you like me to show you those instead?"
- Haiku, no flag, tell (PMUL4376, first answer): "I'm sorry, but I couldn't find any 0-star hotels in the north of
  Cambridge. Would you like me to widen the search, for example by including guesthouses or looking at a different star
  rating?"
- Haiku, no flag, word rule "tell", reading "no tell" (MUL0666, first answer): "The traveller asked for a hotel, not a
  guesthouse, so I kept the type as hotel. [...] Would you like me to relax the price range or the parking requirement
  to see what other south-area hotels are available?"
