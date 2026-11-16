# X7, second collision words: predictions and build record (written 2026-11-03, before any X7 call)

Source: `PROTOCOL.md` section "X7, second collision words". Claude merges this file into `PROTOCOL.md` before any pilot. The code is `r9/x7/x7.py`. The tests are `r9/x7/test_x7.py`.

## Forms

- **A0** is the E13 form `p_main` for the attraction domain. The code makes four text edits to `p_main` and replaces the allowed-values list. The frame is "a tourist information assistant", the same frame as the X3 attraction form. The fields are `name`, `area`, `type`. The schema is the closed schema of `pmain/e13.py`.
- The `type` values are the 12 types of `attraction_db.json` in sorted order: architecture, boat, cinema, college, concerthall, entertainment, multiple sports, museum, nightclub, park, swimmingpool, theatre.
- `attraction_db.json` and the briefs write one type as `mutliple sports` (a typo). The forms write `multiple sports`, the value that the protocol names. The parser and the group rule map the typo to `multiple sports`.
- **A1** is A0 with `entertainment` replaced by `amusement_venue` and `multiple sports` replaced by `athletics_venue`. Each word keeps its position in the list. No other text changes, in the prompt or in the schema. `check_forms` tests this. The parser maps each neutral word back to the original value. A0 maps no neutral word back.

## Neutral words (the F4 rule, applied mechanically)

The rule: no part of the original value, no size or quality word (the list of `test_natural.py`), and no use in a traveller turn of the training split. The check reads 56,778 traveller turns of the 8,438 training dialogues. A use is the phrase with a space, an underscore, a hyphen, or no character between the parts, plural allowed.

| Candidate | Traveller turns | Parts of the value | Size or quality words | Result |
|---|---:|---|---|---|
| `amusement_venue` | 0 | none | none | used for `entertainment` |
| `leisure_venue` | 0 | none | none | not used (backup) |
| `athletics_venue` | 0 | none | none | used for `multiple sports` |
| `activity_centre` | 0 | none | none | not used (backup) |

## Groups (`ids.json`)

The pool is the 2,718 training dialogues whose goal has the attraction domain. No validation or test dialogue is in the pool. The words match at word boundaries in the traveller turns, plural allowed, as in the E8 and E11 rule. "The brief sets the value" means that `goal.attraction.info.type` or `goal.attraction.fail_info.type` has that value.

| Group | Rule | Dialogues |
|---|---|---:|
| G_ent | "entertainment", and the brief does not set `entertainment` | 15 |
| C_ent | "entertainment", and the brief sets `entertainment` | 205 |
| G_sport | "sport" or "sports", and the brief does not set `multiple sports` | 2 |
| C_sport | "sport" or "sports", and the brief sets `multiple sports` | 126 |
| M | "museum", and the brief sets `museum` | 437 |

The union has 734 dialogues. Each model reads each of them under A0 and A1. A dialogue in two groups counts in each group.

**Size warning.** G_ent and G_sport are very small. With 2 dialogues, the exact sign test of G_sport cannot go below p = 0.5. The cause is `fail_info`. Many travellers ask for entertainment or sports, get no match, and then change to a different type. Thus the brief sets the value in `fail_info`. Under other rules the G groups are larger: `info` only gives 123 and 114 dialogues; the final metadata type gives 126 and 105 (the round-8 counts). The build follows the protocol rule. Only a protocol amendment can change the rule.

**Revealed type.** For each dialogue, the type in `attraction_db.json` of the last attraction name in the per-turn metadata (`metadata.attraction.semi.name`). The name match ignores case, a first "the", punctuation, and the possessive "'s". Counts over the 734 dialogues: no name 317, unmatched 21, a database type 396.

## Folders and requests

| Folder | Account | Model | Reads | Requests |
|---|---|---|---:|---:|
| `ex7_claude` | `anthropic_r9a` | `claude-haiku-5-5` | 3 | 4,404 + 10 pilot |
| `ex7_claude` | `anthropic_r9a` | `claude-sonnet-5-5` | 2 | 2,936 + 10 pilot |
| `ex7_luna` | `openai_r9` | `gpt-6-luna` | 3 | 4,404 |
| `ex7_sol` | `openai_r9` | `gpt-6.1-sol` | 1 | 1,468 |
| `ex7_di` | `deepinfra` | each of the 3 DeepInfra models | 1 | 1,468 each |

The settings are `natural.MODELS`: Claude with the E13 settings, Sol at effort low, Luna at effort none, and the DeepInfra models with `r9/deepinfra_settings.py`. The non-Claude folders take their per-call sizes from the natural-task answers of P (`ep_oa`, `ep_di`) and P2 (`ep_di2`) through `ep.sizes`. These answers come from the hotel form with 7 fields, so the output size is high for a form with 3 fields.

## Predictions (copied from `PROTOCOL.md` X7)

1. For Sonnet, A1 lowers the target value by 3 percentage points or more in G_ent and in G_sport.
2. In C_ent and C_sport, A1 lowers the target value by 5 percentage points or less.
3. In M, `type = museum` moves by 2 percentage points or less between A0 and A1.
4. The drop of prediction 1 occurs for at least 3 of the 7 models in at least one G group.

If prediction 1 holds for at least one word, the paper reports a second natural class-and-member collision. If it holds for neither word, the natural evidence stays one word ("hotel"), and the paper says so.
