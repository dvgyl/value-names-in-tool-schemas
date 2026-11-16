# The clear-request rule (post hoc)

- SHA-256 of `r10/analysis/clear_rule.py`: `e8cd2490a137a888a3463420f7da4349f29b645fb780a72288400cbaa7291794`
- Written: 2026-11-12T16:27:01+00:00

This rule was written and fixed before any split by it was computed. `clear_split.py` computes the splits. It stops when the SHA-256 of `clear_rule.py` is not the value above. The rule reads traveller words only: no brief, no gold state, no model answer, and no sealed file. No sealed second-look answer was read.

## The rule

A traveller turn is split into sentences. Each pattern runs on one sentence. A dialogue (or a prefix) gets one label from its traveller turns:

- `hotel_only`: a sentence requires a hotel or excludes the guesthouse kinds, and no sentence does the mirror.
- `guesthouse_only`: the mirror case.
- `mixed`: sentences of both kinds.
- `unclear`: no sentence matches. The plain head noun ("I need a hotel", "a cheap hotel in the north", "I prefer a hotel") never matches.

For prefixes (source 1), only the traveller turns up to and including the first traveller turn that says "hotel" count. For the other sources, all traveller turns count.

In the effect tables, **clear** is `hotel_only` and **unclear** is `unclear`. `guesthouse_only` and `mixed` are counted and shown separately. The secondary rule `strict` keeps the E and R families only.

### Kind words

| Kind | Regular expression |
|---|---|
| hotel | `hotels?` |
| guesthouse | `(?:guest ?houses?\|b ?& ?bs?\|b and bs?\|bed and breakfasts?\|hostels?)` |

### Patterns

`{want}` is the kind that the sentence requires. `{other}` is the kind that it excludes. For `hotel_only`, `{want}` is hotel and `{other}` is the guesthouse kinds. The mirror swaps them. All patterns ignore case.

| Pattern | Family | Template |
|---|---|---|
| E1_not_other | E | `(?:\bnot\|\b(?:is\|was\|are\|were)n't)\s+(?:an?\s+\|in\s+an?\s+\|at\s+an?\s+)?{other}\b` |
| E2_dont_want_other | E | `(?:\bnot\|n't\|\bnever)\s+(?:really\s+\|even\s+\|particularly\s+)?(?:want\|like\|care\s+for\|wish)\w*\s+(?:to\s+(?:stay\|be\|sleep)\s+(?:in\|at)\s+)?(?:an?\s+\|any\s+)?{other}\b` |
| E3_dislike_other | E | `(?:\b(?:hates?\|dislikes?\|detest\|avoid)\s+(?:\w+\s+){0,2}?\|\bnot\s+(?:too\s+\|very\s+\|really\s+\|a\s+big\s+\|much\s+of\s+)?(?:fond\s+of\|a\s+fan\s+of\|interested\s+in\|keen\s+on)\s+(?:\w+\s+){0,3}?){other}\b` |
| E4_rather_than_other | E | `\b(?:rather\s+than\|instead\s+of\|as\s+opposed\s+to)\s+(?:(?:stay(?:ing)?\|be(?:ing)?)\s+(?:in\|at)\s+)?(?:an?\s+\|in\s+an?\s+\|at\s+an?\s+)?{other}\b` |
| E5_no_other | E | `(?:^\|[.,;:!(]\s*\|\b(?:and\|but\|please,?)\s+)no\s+{other}(?=\s*(?:[.,;:!?)]\|please\b\|thanks?\b\|$))` |
| R1_only_want | R | `\b(?:only\|strictly\|exclusively)\s+(?:(?:want\|consider\|book\|stay\|look\|search\|check)\w*\s+(?:to\s+(?:stay\|book)\s+)?(?:in\s+\|at\s+\|for\s+)?\|for\s+\|in\s+)?(?:an?\s+)?{want}\b` |
| R2_want_only | R | `\b{want}\s+only(?=\s*(?:[.,;:!?)]\|please\b\|thanks?\b\|$))` |
| R3_actual_want | R | `\b(?:actual\|proper\|real\|regular\|true\|traditional\|normal\|full[- ]service)\s+{want}\b` |
| P1_must_be_want | P | `\b(?:has\s+to\|have\s+to\|needs?\s+to\|must\|should\|will\s+need\s+to\|would\s+need\s+to\|(?:has\s+\|have\s+)?got\s+to\|ought\s+to)\s+(?:also\s+\|definitely\s+\|really\s+\|absolutely\s+)?be\s+(?:an?\s+\|in\s+an?\s+\|at\s+an?\s+)?(?:actual\s+\|proper\s+\|real\s+)?{want}\b` |
| P2_want_it_to_be_want | P | `\b(?:want\|like\|need\|prefer\|require\|wish)\w*\s+(?:for\s+)?(?:it\|the\s+(?:hotel\|place\|lodging\|accommodations?\|room))\s+to\s+(?:also\s+\|definitely\s+)?be\s+(?:an?\s+\|in\s+an?\s+\|at\s+an?\s+)?(?:actual\s+\|proper\s+\|real\s+)?{want}\b` |
| P3_make_sure_it_is_want | P | `\b(?:make\s+sure\|making\s+sure\|as\s+long\s+as\|so\s+long\s+as\|provided)\s+(?:that\s+)?(?:it\|this\|that\|the\s+place\|the\s+hotel)\s*(?:'s\|s\|\s+is\|\s+will\s+be\|\s+would\s+be)\s+(?:an?\s+\|in\s+an?\s+\|at\s+an?\s+)?(?:actual\s+\|proper\s+\|real\s+)?{want}\b` |
| P4_that_is_want | P | `\b(?:that\|which\|and)\s+(?:is\|'s)\s+(?:also\s+)?(?:an?\s+)?(?:actual\s+)?{want}\b` |
| T1_kind_type | T | `\ban?\s+(?:(?!(?:the\|of\|their\|its\|this\|that)\b)[\w-]+\s+){0,3}?{want}[- ]type\b` |
| T2_in_the_type_of | T | `\b(?:in\|of)\s+the\s+type\s+of\s+(?:an?\s+)?{want}\b` |
| T3_type_is | T | `\btype\s+(?:should\|must\|needs\s+to\|has\s+to\|would\s+need\s+to\|is)\s+(?:be\s+)?(?:an?\s+)?{want}\b` |

Families: E exclusion, R restriction, P predicate, T type word.

### Guards

A match does not count when:

- the sentence is a yes/no question about a venue: it ends with "?" and starts with "is", "isn't", "was", "am", or "are they / those / these / any of";
- (P) a negation comes just before it ("it doesn't have to be a hotel");
- (P1) its subject is a person ("I need to be in a hotel");
- (R, P, T) the kind word is followed by "or <other kind>", "that is <other kind>", or "if";
- (R1) it follows "the" ("the only hotel in the area");
- (E1) it follows "there is" or "there are" ("if there is not a guesthouse ...");
- (E) the sentence names another domain (restaurant, attraction, train, taxi, museum, college, food) and no venue kind before the match.

Known limit: a short answer to an assistant's type question ("A hotel, please.") stays `unclear`.

## Labels per set

| Set | Dialogues | hotel_only | guesthouse_only | mixed | unclear | strict: hotel_only | strict: unclear |
|---|---|---|---|---|---|---|---|
| a_hotel | 59 | 1 | 0 | 0 | 58 | 1 | 58 |
| a_no_type | 448 | 0 | 0 | 0 | 448 | 0 | 448 |
| b_hotel | 233 | 89 | 3 | 1 | 140 | 54 | 179 |
| b_no_type | 807 | 4 | 1 | 0 | 802 | 4 | 802 |
| c_hotel | 77 | 20 | 0 | 0 | 57 | 10 | 67 |
| c_no_type | 213 | 3 | 0 | 0 | 210 | 2 | 211 |

Sets:

- `a_hotel`: Source 1, tool calls at the first request: prefixes whose brief sets `type` = hotel.
- `a_no_type`: Source 1, tool calls at the first request: prefixes whose brief sets no type.
- `b_hotel`: Source 2, round-9 form runs: S2 full dialogues whose brief sets `type` = hotel.
- `b_no_type`: Source 2, round-9 form runs: S1t full dialogues whose brief sets no type.
- `c_hotel`: Source 3, held-out test stage 1: goal-hotel sample, full dialogues.
- `c_no_type`: Source 3, held-out test stage 1: natural sample (the goal sets no type), full dialogues.

## Dialogues per pattern

A dialogue counts once per pattern. One dialogue can match more than one pattern.

| Side | Pattern | a_hotel | a_no_type | b_hotel | b_no_type | c_hotel | c_no_type |
|---|---|---|---|---|---|---|---|
| hotel_only | E1_not_other | 1 | 0 | 23 | 3 | 3 | 1 |
| hotel_only | E2_dont_want_other | 0 | 0 | 6 | 1 | 1 | 0 |
| hotel_only | E3_dislike_other | 0 | 0 | 2 | 0 | 2 | 0 |
| hotel_only | E4_rather_than_other | 0 | 0 | 16 | 0 | 3 | 1 |
| hotel_only | E5_no_other | 0 | 0 | 2 | 0 | 1 | 0 |
| hotel_only | R1_only_want | 0 | 0 | 0 | 0 | 0 | 0 |
| hotel_only | R2_want_only | 0 | 0 | 0 | 0 | 0 | 0 |
| hotel_only | R3_actual_want | 0 | 0 | 6 | 0 | 2 | 0 |
| hotel_only | P1_must_be_want | 0 | 0 | 18 | 0 | 5 | 0 |
| hotel_only | P2_want_it_to_be_want | 0 | 0 | 10 | 0 | 6 | 0 |
| hotel_only | P3_make_sure_it_is_want | 1 | 0 | 3 | 0 | 1 | 1 |
| hotel_only | P4_that_is_want | 0 | 0 | 3 | 1 | 2 | 0 |
| hotel_only | T1_kind_type | 0 | 0 | 7 | 0 | 3 | 0 |
| hotel_only | T2_in_the_type_of | 0 | 0 | 6 | 0 | 0 | 0 |
| hotel_only | T3_type_is | 0 | 0 | 1 | 0 | 0 | 0 |
| guesthouse_only | E1_not_other | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | E2_dont_want_other | 0 | 0 | 0 | 1 | 0 | 0 |
| guesthouse_only | E3_dislike_other | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | E4_rather_than_other | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | E5_no_other | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | R1_only_want | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | R2_want_only | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | R3_actual_want | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | P1_must_be_want | 0 | 0 | 2 | 0 | 0 | 0 |
| guesthouse_only | P2_want_it_to_be_want | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | P3_make_sure_it_is_want | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | P4_that_is_want | 0 | 0 | 1 | 0 | 0 | 0 |
| guesthouse_only | T1_kind_type | 0 | 0 | 0 | 0 | 0 | 0 |
| guesthouse_only | T2_in_the_type_of | 0 | 0 | 1 | 0 | 0 | 0 |
| guesthouse_only | T3_type_is | 0 | 0 | 0 | 0 | 0 | 0 |

## Example sentences (corpus text only)

Each set: 10 matched sentences and 10 unmatched sentences, drawn at random (seed 20261112). An unmatched sentence names a venue kind (hotel, guesthouse, guest house, B&B, bed and breakfast, hostel) but matches no pattern. These are the sentences where a missed type statement would show.

### a_hotel

Source 1, tool calls at the first request: prefixes whose brief sets `type` = hotel. Matched sentences: 1. Unmatched sentences that name a kind: 58.

Matched:

1. `PMUL4655` turn 10: "I don't need parking, but I would like to make sure it is a hotel, not a guesthouse." (hotel_only: E1_not_other; hotel_only: P3_make_sure_it_is_want)

Unmatched:

1. `PMUL4292` turn 2: "Price doesn't matter but would like a 4 star hotel in the west that includes free parking."
2. `PMUL1757` turn 0: "need a hotel with free wifi please"
3. `MUL1263` turn 0: "I'm looking for a 2 star hotel."
4. `PMUL0111` turn 10: "Do you have an expensive hotel that meets my other criteria?"
5. `PMUL4377` turn 6: "Thank you, I also need to find a hotel with free wifi."
6. `PMUL3512` turn 8: "A hotel in the heart of the center of the city that is a two star hotel or a hostel."
7. `MUL2085` turn 8: "I need a hotel in the west ,  free parking is not necessary but it should be rated 4 stars."
8. `PMUL2842` turn 0: "I need to find a hotel quick, can you make it happen?"
9. `MUL1023` turn 12: "I don't really have any preferences other than I want it to be in the same area as the hotel."
10. `PMUL4038` turn 6: "Get me a hotel in the same area with the same price range for 5 staying for 2 nights, with a taxi that arrives at the restaurant by the booked time"

### a_no_type

Source 1, tool calls at the first request: prefixes whose brief sets no type. Matched sentences: 0. Unmatched sentences that name a kind: 471.

Matched:

None.

Unmatched:

1. `MUL2118` turn 6: "I'm also looking for the gonville hotel."
2. `PMUL3869` turn 2: "I need a 3 star rated hotel"
3. `PMUL1687` turn 0: "I'm looking for a particular hotel called the kirkwood house."
4. `MUL2104` turn 6: "I'm also looking for a particular hotel."
5. `PMUL0263` turn 0: "I'm looking for a hotel called a and b quest house."
6. `PMUL4079` turn 0: "I'm looking for this hotel called home from home, please."
7. `PMUL3375` turn 0: "Can you help me find a hotel called Limehouse?"
8. `PMUL4584` turn 0: "I'm planning a trip to Cambridge and I would like to find a hotel on the East side that offers free parking"
9. `MUL2278` turn 0: "I'm looking for a hotel called Worth House."
10. `PMUL2653` turn 8: "Yes, can you get me information about Huntingdon Marriott Hotel?"

### b_hotel

Source 2, round-9 form runs: S2 full dialogues whose brief sets `type` = hotel. Matched sentences: 98. Unmatched sentences that name a kind: 435.

Matched:

1. `MUL2171` turn 6: "Can you find me a hotel type place?" (hotel_only: T1_kind_type)
2. `PMUL2892` turn 10: "I don't like guesthouses." (hotel_only: E2_dont_want_other)
3. `PMUL1866` turn 4: "But I would like it to be a hotel rather than a guesthouse." (hotel_only: E4_rather_than_other; hotel_only: P2_want_it_to_be_want)
4. `PMUL4794` turn 10: "I would actually prefer a hotel rather  than a guest house." (hotel_only: E4_rather_than_other)
5. `MUL2652` turn 2: "It does need to be a hotel and parking isn't really an issue with us." (hotel_only: P1_must_be_want)
6. `PMUL3704` turn 2: "I don't want to stay in a guesthouse." (hotel_only: E2_dont_want_other)
7. `MUL1265` turn 2: "I would prefer a hotel type hotel, it just needs to be in the moderate price range and doesn't need to have free parking, but needs wifi" (hotel_only: T1_kind_type)
8. `PMUL4904` turn 4: "I do not have a preference on price as long as it has a 4 star rating and is a hotel." (hotel_only: P4_that_is_want)
9. `PMUL2714` turn 8: "The hotel should be in the type of hotel and should include free wifi." (hotel_only: T2_in_the_type_of)
10. `PMUL1723` turn 8: "It needs to be a hotel." (hotel_only: P1_must_be_want)

Unmatched:

1. `MUL1331` turn 14: "Does that hotel have free Internet?"
2. `PMUL4499` turn 10: "Yes, can you help me find a place to stay, a 4 star hotel?"
3. `PMUL1728` turn 8: "I'm also looking for a hotel to stay in."
4. `PMUL2557` turn 4: "Can you recommend a hotel in the West area, please?"
5. `MUL2153` turn 12: "Yes, I'll need a hotel for 7 people for 4 nights starting Friday."
6. `MUL2196` turn 6: "I just need a moderately priced hotel with free wifi and parking."
7. `PMUL1863` turn 10: "I'd rather have a hotel."
8. `PMUL1510` turn 6: "Can you also recommend a three star hotel that has free wifi?"
9. `PMUL1532` turn 10: "Is A and B an expensive, 4-star guesthouse?"
10. `MUL0104` turn 4: "The University Arms Hotel."

### b_no_type

Source 2, round-9 form runs: S1t full dialogues whose brief sets no type. Matched sentences: 5. Unmatched sentences that name a kind: 1391.

Matched:

1. `MUL2632` turn 2: "That is a hotel and not a guesthouse right?" (hotel_only: E1_not_other; hotel_only: P4_that_is_want)
2. `PMUL4817` turn 4: "not a guest house?" (hotel_only: E1_not_other)
3. `PMUL1527` turn 4: "Do you have any thing that is not a guesthouse in other areas?" (hotel_only: E1_not_other)
4. `MUL2528` turn 10: "I don't like guest houses." (hotel_only: E2_dont_want_other)
5. `PMUL0070` turn 2: "I don't want a hotel." (guesthouse_only: E2_dont_want_other)

Unmatched:

1. `MUL2540` turn 8: "Alexander Bed and breakfast, can I get the address and hotel type please?"
2. `PMUL1963` turn 2: "Could you look to see if there are any 4 star hotels that offer free wifi instead and are in the north section?"
3. `PMUL0371` turn 4: "I think I'd like Bridge Guest House please."
4. `MUL1334` turn 4: "I am also looking for a hotel."
5. `PMUL2695` turn 0: "I need help finding a hotel called Bridge Guest House."
6. `PMUL3234` turn 10: "Can you tell me the phone number, hotel type, and postcode?"
7. `MUL2182` turn 0: "Have you ever heard of alexander bed and breakfast?"
8. `MUL2518` turn 6: "I am also looking for a Hotel named Worth House."
9. `PMUL2862` turn 0: "I am looking for information about a hotel called aylesbray lodge guest house."
10. `PMUL1934` turn 0: "Find me a hotel like that with a star of 4."

### c_hotel

Source 3, held-out test stage 1: goal-hotel sample, full dialogues. Matched sentences: 21. Unmatched sentences that name a kind: 158.

Matched:

1. `MUL1379` turn 12: "I need it to be a hotel type with free parking and four stars, please." (hotel_only: P2_want_it_to_be_want; hotel_only: T1_kind_type)
2. `PMUL1949` turn 4: "I do not have a preference on price as long as it has a 4 star rating and is a hotel." (hotel_only: P4_that_is_want)
3. `MUL0731` turn 4: "And the place needs to be a hotel type." (hotel_only: P1_must_be_want; hotel_only: T1_kind_type)
4. `MUL1117` turn 2: "No star preference, but I would like it to be a hotel type." (hotel_only: P2_want_it_to_be_want; hotel_only: T1_kind_type)
5. `PMUL3979` turn 2: "I want it to be a hotel and also include free wifi." (hotel_only: P2_want_it_to_be_want)
6. `PMUL4446` turn 6: "I really want it to be a hotel as opposed to a guesthouse." (hotel_only: E4_rather_than_other; hotel_only: P2_want_it_to_be_want)
7. `PMUL3883` turn 16: "I don't want a B&B." (hotel_only: E2_dont_want_other)
8. `PMUL4643` turn 8: "I'd like a hotel, not a guesthouse, and I'd like a 2-star place." (hotel_only: E1_not_other)
9. `PMUL2953` turn 6: "Ugh, I hate guesthouses though so it needs to be a hotel room in the west." (hotel_only: E3_dislike_other; hotel_only: P1_must_be_want)
10. `MUL2177` turn 0: "It doesn't need to include internet and should be a hotel." (hotel_only: P1_must_be_want)

Unmatched:

1. `MUL0707` turn 4: "I would also like the star of the hotel, the postcode, and the phone number please."
2. `MUL1288` turn 8: "I would like it to be the same price range as the hotel if you can."
3. `PMUL3883` turn 12: "I also need a hotel that has free parking and wifi."
4. `MUL0099` turn 8: "Actually, I'm looking for a hotel and in the same price range as the restaurant."
5. `MUL1286` turn 0: "I'm looking for a hotel."
6. `MUL1318` turn 16: "Actually, I'd like to book a taxi from the hotel to The Missing Sock."
7. `PMUL1613` turn 8: "Can you help me find a hotel instead?"
8. `MUL0126` turn 10: "How about any type of hotel in Cambridge, guesthouse or other?"
9. `MUL1117` turn 4: "The Ashley Hotel will do fine."
10. `PMUL1623` turn 12: "could you provide the postcode and star of the hotel."

### c_no_type

Source 3, held-out test stage 1: natural sample (the goal sets no type), full dialogues. Matched sentences: 3. Unmatched sentences that name a kind: 371.

Matched:

1. `PMUL1779` turn 10: "Do they have free wifi, I was really looking for a hotel rather than a guesthouse though." (hotel_only: E4_rather_than_other)
2. `MUL2086` turn 14: "Ss the gonville hotel a hotel and not a guesthouse?" (hotel_only: E1_not_other)
3. `MUL2526` turn 10: "That is fine, as long as it is a hotel." (hotel_only: P3_make_sure_it_is_want)

Unmatched:

1. `PMUL1779` turn 12: "A guesthouse will be fine I guess."
2. `MUL2014` turn 8: "I need a train departing from Bishops Stortford leaving after 15:15 for Cambridge on the same day as the booking for the hotel."
3. `MUL1247` turn 2: "Let's go with a hotel."
4. `MUL0198` turn 10: "Yes, I'm looking for a hotel named Limehouse?"
5. `PMUL0012` turn 14: "I want to book a taxi from the hotel to the restaurant, that arrives at 11:30."
6. `PMUL0262` turn 0: "I am looking for the cityroomz hotel"
7. `MUL2020` turn 6: "Yes, I'm also looking for a hotel called avalon."
8. `MUL2270` turn 8: "I am also looking for a hotel called Archway House."
9. `PMUL3015` turn 12: "Yes, a guesthouse is fine."
10. `PMUL2599` turn 0: "I'm looking for a 0 star hotel that is expensive."
