# Spec: what the stored later-turn conversations hold, and whether a final-recommendation rule is feasible

Written: 2026-11-15 22:51 UTC (`date -u`), before the inventory script ran.

This file is a copy of the spec `SPEC-L2-inventory.md`. The copy changes only the paths, the file names and the title line, and it leaves out one sentence that named the writer. The population, the items and the decision rule are the same. `loyal_final_recommendations_spec_hash.txt` gives the time and the SHA-256 of the original file.

Status label: post hoc description of stored outputs (the conversations exist, and earlier outcomes of them are published in the paper). No model call. No reading of the conversations as an annotator.

## Inputs

- `ert_sonnet/conversations.jsonl` (original tool, arm t0) and `ert1_sonnet/conversations.jsonl` (renamed tool, arm t1). Only these two files of conversations. The pilot files are not used.
- The venue database `hotel_db.json` (via `gold.hotel_db()`), the corpus (`runs.context()`), and the agent system text `flag.multi_system(arm)` and tools `tools.TOOLS[arm]` (code, not outputs).
- The stored full-schema check of the later turns, `r10/analysis/out/loyal_unchecked_runs.json` (counts only).
- No answer folder of the registered held-out test, no sealed file, no key file and no `.env` file.

## Population

One record per dialogue and arm with status "complete" (as `turns_analyze.analyse`: the last complete record of a dialogue). Groups F (brief sets no type; only guesthouses fit) and R (brief sets no type; a hotel fits), as stored in each record.

## Inventory items (counts per arm and group; no fit and no condition comparison of any outcome)

1. Records, complete records, other statuses, duplicate dialogues.
2. Keys of the records; the tool names used in the stored agent calls; any field of a record or of a stored call that names a chosen venue (criterion F1 below).
3. The agent system text of each arm: does it fix a format for a final choice (for example "Recommendation: <name>")? (criterion F2).
4. Agent turns per conversation (`len(replies)`) and traveller messages per conversation.
5. The final agent message (`replies[-1]`): empty or not; stop reason of the last agent call; whether the last turn ended with a search call at the call limit (its result was never answered).
6. Venue names in the final message. A venue is *named* when its normalized name (`gold.norm`) is a substring of the normalized message. A database name that starts with "the " also counts without it. If one named venue's normalized name is a substring of another named venue's normalized name (for example "worth house" inside "warkworth house"), only the longer one counts. Count final messages with 0, 1 and 2 or more named venues.
7. For final messages with exactly one named venue: (a) whether a search of the same conversation showed that venue; (b) whether the message contains a *cue* of rejection or unavailability from this fixed list (case-insensitive regular expression, word boundaries): `unfortunately`, `not available`, `unavailable`, `no longer`, `doesn't`, `does not`, `isn't`, `is not`, `aren't`, `are not`, `don't have`, `do not have`, `couldn't find`, `could not find`, `didn't find`, `did not find`, `no results?`, `none of`, `instead`.
8. Final messages with no named venue where an earlier agent reply of the same conversation names at least one venue.
9. Whether the traveller's last message contains "suit" (description only; the traveller is a model, so this is never used as an endpoint).
10. Conversations with a call that does not parse (`kind` other than "search"), and the stored count of conversations with a call that is not valid after normalization (from `loyal_unchecked_runs.json`).

## Feasibility decision rule (fixed now, before the counts)

A final-recommendation endpoint is added to the paper only if one of the following holds in both arms:

- **F1 (structure).** A stored field names the venue that the agent chose, in at least 95% of the complete conversations.
- **F2 (format).** The agent system text fixes a format that marks one chosen venue, and at least 95% of the final messages follow it.
- **F3 (explicit identity in free text).** All three of: (a) at least 90% of the complete conversations have a final message that names exactly one database venue; (b) of these, at most 5% contain a cue of item 7(b); (c) of these, at least 95% name a venue that a search of the same conversation showed.

Reason for F3 (a): if many final messages name no venue or several venues, the final message is not where the choice is stated, and a rule on it would turn closings and lists into "no recommendation" or "several". Reason for (b): a cue shows that the named venue may be rejected or unavailable; a rule cannot separate these cases without reading. Reason for (c): a named venue that no search showed is not a database-backed choice.

If none of F1, F2 and F3 holds, the decision is **not usable**: no new metric; the paper keeps the search-display outcome and says that the stored transcripts do not support a reliable final-recommendation endpoint. If one holds, a second dated spec fixes the endpoint and the scoring before any fit or comparison is computed.

## Spot check

After the counts, read a few final messages by eye only to find extraction bugs of item 6 (missed or wrong venue names). Report which conversations were read and what was found. A spot check does not change any category of a conversation by judgement.

## Outputs

`r10/analysis/out/loyal_final_recommendations.md` and `loyal_final_recommendations.json`. Script: `r10/analysis/loyal_final_recommendations.py`. Test: `r10/tests/test_loyal_final_recommendations.py`.
