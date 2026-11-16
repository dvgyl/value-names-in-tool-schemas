# Track C drafts for experiment E4

These files are exploratory drafts for E4 only. Do not reuse these templates, goals, or items in a calibration family or in a confirmatory family. Every template, goal, and item id starts with `x`, so that you can find them in any later set.

## Files

- `templates.py` holds the 8 template families, the 160 goals, the 320 items, and the three form prompts.
- `check_items.py` checks every item and every form prompt.
- `e4.py` builds the 8,640 requests and runs the steps of `lib/anth.py`.
- `analyze.py` reads `explore/e4/raw.jsonl` and writes `explore/e4/summary.json`.
- `test_analyze.py` tests `analyze.py` on synthetic replies. It makes no API call.

## Commands

Run each command from the `explore` folder.

```
python3 -I trackc/check_items.py
python3 -I trackc/test_analyze.py
python3 -I trackc/e4.py estimate
python3 -I trackc/analyze.py
```

The steps `pilot`, `submit`, and `fetch` cost money. Run them only after the operator approves the printed bound in writing.

## Items

Each goal gives one ambiguous item and one clear control. The clear control is the ambiguous item plus the clarifying sentences. The two texts have no other difference.

| Condition | Target field | Readings, ambiguous item | Reading, clear control |
|---|---|---|---|
| a, the word "hotel" | `type` | null, `[hotel]` | `[hotel]` |
| b, a feature question | `parking` | null, `[yes]` | `[yes]` |
| c, a new value after a failed search | `area` or `pricerange` | `[new]`, `[first, new]` | `[first, new]` |
| d, an unstated deciding fact | `stars` or `parking` | null | `[value]` |

The hotel database makes every assistant sentence true. In condition c, the first value matches no hotel. In conditions a, b, and d, the target value removes some of the hotels that fit the other stated fields.

The 33 hotels allow only 13 to 46 different goal objects per family. Thus goals repeat the same form values with other wording and booking details. The bootstrap of the exchange rate counts goals with the same target field and form values as one cluster.

## Forms

`p_unclear` is the P5 prompt. `p_main` is the P5 prompt without the ambiguity sentence. `p_null` is the P5 prompt with "write null" in place of "write \"unclear\"". `check_items.py` compares the three prompts with `p5_unclear/run.py`.

The scorer uses the P5 parser for all three forms, as note 1 of `PROTOCOL.md` sets for E1, E5, and E6. Thus "unclear" in `p_main` or `p_null` counts as no constraint. A reply that stops at `max_tokens` is a missing cell, as note 4 sets.
