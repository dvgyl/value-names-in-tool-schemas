# Experiment H: the word and schema pairs for review (version 3)

Status: **a proposal for the operator's approval. No call has run.** `python3 -I r10/pairs.py review` writes this text from `r10/pairs.py` and `r10/pairs.json`. Version 1 (16 pairs, before the template review) is in `pairs.v1.json` and `pairs_review.v1.md`. Version 2 (before the second review) is in `pairs.v2.json` and `pairs_review.v2.md`.

## 1. The steps for the reviewers

1. Operator: read sections 2 and 3. Approve the change from 16 to 12 pairs (check 3), or reject it, before any H call.
2. Template reviewer: read section 5. For each item, write down if the stated reading (unclear, specific, general) is not the only reasonable reading.
3. Correct a template, not a single item. A template change changes `requests_sha256`, so `pairs.chosen()` then stops. Rename `pairs.json` and write it again only before the approval.

## 2. The chosen pairs

Value changes against the plan's candidate list (the operator approves them with the list): `boat`: `ferry` becomes `punt` (a ferry is not hired by the hour and cannot be taken out; review of 2026-11-12).

Rule: the candidates in the order of ROUND10-EXPERIMENT-PLAN.md H that pass checks 1 and 2 and are not in RULE_D_EXCLUDED, at most 16; if fewer than 12 remain, H does not run. Seed of the scenario draw: 20261112.

| # | Collision value | Other values | Assistant phrase | Role | G4 token |
|---|---|---|---|---|---|
| 1 | `table` | `booth`, `bar seat` | table booking assistant | traveller | `open_floor` |
| 2 | `room` | `suite`, `apartment` | room booking assistant | traveller | `lodging_unit` |
| 3 | `restaurant` | `cafe`, `pub` | restaurant booking assistant | traveller | `dining_venue` |
| 4 | `car` | `van`, `minibus` | car booking assistant | traveller | `private_vehicle` |
| 5 | `taxi` | `minibus`, `limousine` | taxi booking assistant | traveller | `metered_vehicle` |
| 6 | `doctor` | `nurse practitioner`, `pharmacist` | doctor appointment assistant | traveller | `licensed_physician` |
| 7 | `school` | `college`, `academy` | school enrolment assistant | traveller | `education_provider` |
| 8 | `bike` | `e-bike`, `scooter` | bike booking assistant | traveller | `pedal_cycle` |
| 9 | `boat` | `punt`, `kayak` | boat booking assistant | traveller | `private_vessel` |
| 10 | `letter` | `email`, `fax` | letter sending assistant | customer | `postal_item` |
| 11 | `coffee` | `tea`, `hot chocolate` | coffee ordering assistant | traveller | `bean_brew` |
| 12 | `camera` | `camcorder`, `webcam` | camera hire assistant | traveller | `photo_device` |
| calibration | `hotel` | `guesthouse`, `hostel` | hotel booking assistant | traveller | `serviced_property` |

Requests per read: 1,920 for the chosen pairs, plus 160 for the calibration pair (cell tags `cal_g0`, `cal_g4`). SHA-256 of all requests: `200df66153104739eed6ad5c6d01afcd78f92447a30702451e03ab3f5ebf9557`.

## 3. The checks of each candidate

Check 1: the G4 token is in no traveller turn of the MultiWOZ training split, it holds no value word of the pair, and no part of it is a size or quality word (the round-9 F4 rule). Check 2: no `unclear_para` item and no part of its template holds a value word of the pair. Check 3 (`RULE_D_EXCLUDED`, a judgement of the template review): the collision word is the everyday word for all three values.

| Order | Candidate | Failed checks 1 and 2 | Check 3 | Result |
|---|---|---|---|---|
| 1 | `table` | none | passes | chosen |
| 2 | `room` | none | passes | chosen |
| 3 | `restaurant` | none | passes | chosen |
| 4 | `car` | none | passes | chosen |
| 5 | `taxi` | none | passes | chosen |
| 6 | `doctor` | none | passes | chosen |
| 7 | `gym` | none | a pool or a yoga studio is not "a gym" | excluded |
| 8 | `school` | none | passes | chosen |
| 9 | `bike` | none | passes | chosen |
| 10 | `apartment` | none | "an apartment" excludes "a house", and a studio is a kind of apartment | excluded |
| 11 | `office` | none | "office" is not the everyday word for a job; the frame and the days are also unnatural | excluded |
| 12 | `movie` | none | a movie does not include a series | excluded |
| 13 | `boat` | none | passes | chosen |
| 14 | `truck` | none | in a British setting "van" is the general word, and a trailer is not a vehicle | excluded |
| 15 | `letter` | none | passes | chosen |
| 16 | `call` | none | a call does not include a message | excluded |
| 17 | `coffee` | none | passes | chosen |
| 18 | `camera` | none | passes | chosen |
| 19 | `box` | none | weak by the same rule: "a box" does not include an envelope or a tube | excluded |
| 20 | `flowers` | none | weak by the same rule: "flowers" does not include a plant or a wreath | excluded |
| calibration | `hotel` | none | passes | reported apart |

## 4. The system text

One frame for all pairs. It is `zforms.F0` with these changes only: the assistant phrase, the role word ("traveller" in F0), the service noun of "requirements for the hotel", the field list (the `name` field and its sentence are removed), and the allowed values. G4 changes only the collision value of `type` to the G4 token, in the text and in the schema.

```text
You read a conversation between a {role} and {a_assistant} in Cambridge. Write down the {role}'s requirements for the {service} as one JSON object. Use only what the {role} said or agreed to. Fields: {fields}. For each field give null if the {role} never stated a requirement, "any" if the {role} said it does not matter, or a list of acceptable values in the {role}'s order of preference (first is most preferred). Allowed values: {allowed} If the {role} changed their mind, give the final requirement. An option that the {role} only accepted from the assistant's offers is not a requirement. Output only the JSON object.
```

Example: G0 of `table`.

```text
You read a conversation between a traveller and a table booking assistant in Cambridge. Write down the traveller's requirements for the table as one JSON object. Use only what the traveller said or agreed to. Fields: area, pricerange, people, type, day. For each field give null if the traveller never stated a requirement, "any" if the traveller said it does not matter, or a list of acceptable values in the traveller's order of preference (first is most preferred). Allowed values: area: centre, north, south, east, west. pricerange: cheap, moderate, expensive. people: 1, 2. type: booth, bar seat, table. day: monday, tuesday, wednesday, thursday, friday, saturday, sunday. If the traveller changed their mind, give the final requirement. An option that the traveller only accepted from the assistant's offers is not a requirement. Output only the JSON object.
```

Decisions for the reviewers to check:
- The service noun is the collision value, as `hotel` is in F0.
- The assistant phrase is "<service> booking assistant", as in F0, except where "booking" is not natural: doctor (appointment), school (enrolment), letter (sending), coffee (ordering), camera (hire).
- One wording per price level where the price field is `price` or `fees`: "It should be cheap", "A moderate price is fine", "I am happy to pay a lot". `table`, `room` and `restaurant` keep the wording of the calibration pair ("should be cheap / moderately priced / expensive").
- The role word is "traveller", as in F0, except for `letter` ("customer"). The user text starts with the same role word ("Customer: ...").
- The fields are place, price, size, `type` and day. Some pairs change a list: `letter` has the language in place of the area; `doctor` has the time of day in place of the price; `doctor`, `school` and `letter` have Monday to Friday only. The calibration pair also has these fields, so its text differs from F0 in the field list and the allowed values.
- The user text is one traveller turn, in the form of `common.dialogue_text` ("Traveller: ...").
- Check 1 is the round-9 rule with "hotel" replaced by every word of every value of the pair. This is stricter than the round-9 rule.
- The size lists fit all three values (for example, a table for one or two, a car or a boat by days or hours, not by people).
- The two clear sentences are the same in all scenarios of a pair.

## 5. Example items (scenarios 0 and 1 of each pair)

### `table`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need a table for one on Monday. The restaurant should be cheap and in the south. |
| 0 | `unclear_para` | I need somewhere to sit for one on Monday. The restaurant should be cheap and in the south. |
| 0 | `clear_specific` | I need a table for one on Monday. The restaurant should be cheap and in the south. It has to be a table, not a booth or a bar seat. |
| 0 | `clear_general` | I need a table for one on Monday. The restaurant should be cheap and in the south. A table, a booth or a bar seat would all be fine. |
| 1 | `unclear_word` | I need a table for one on Tuesday. The restaurant should be cheap and in the east. |
| 1 | `unclear_para` | I need somewhere to sit for one on Tuesday. The restaurant should be cheap and in the east. |
| 1 | `clear_specific` | I need a table for one on Tuesday. The restaurant should be cheap and in the east. It has to be a table, not a booth or a bar seat. |
| 1 | `clear_general` | I need a table for one on Tuesday. The restaurant should be cheap and in the east. A table, a booth or a bar seat would all be fine. |

### `room`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need a room for one person from Thursday. The place should be moderately priced and in the east. |
| 0 | `unclear_para` | I need somewhere to sleep for one person from Thursday. The place should be moderately priced and in the east. |
| 0 | `clear_specific` | I need a room for one person from Thursday. The place should be moderately priced and in the east. It has to be a room, not a suite or an apartment. |
| 0 | `clear_general` | I need a room for one person from Thursday. The place should be moderately priced and in the east. A room, a suite or an apartment would all be fine. |
| 1 | `unclear_word` | I need a room for one person from Wednesday. The place should be moderately priced and in the south. |
| 1 | `unclear_para` | I need somewhere to sleep for one person from Wednesday. The place should be moderately priced and in the south. |
| 1 | `clear_specific` | I need a room for one person from Wednesday. The place should be moderately priced and in the south. It has to be a room, not a suite or an apartment. |
| 1 | `clear_general` | I need a room for one person from Wednesday. The place should be moderately priced and in the south. A room, a suite or an apartment would all be fine. |

### `restaurant`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I am looking for a restaurant for two on Wednesday. The place should be expensive and in the centre. |
| 0 | `unclear_para` | I am looking for somewhere to eat for two on Wednesday. The place should be expensive and in the centre. |
| 0 | `clear_specific` | I am looking for a restaurant for two on Wednesday. The place should be expensive and in the centre. It has to be a restaurant, not a cafe or a pub. |
| 0 | `clear_general` | I am looking for a restaurant for two on Wednesday. The place should be expensive and in the centre. A restaurant, a cafe or a pub would all be fine. |
| 1 | `unclear_word` | I am looking for a restaurant for three on Saturday. The place should be cheap and in the centre. |
| 1 | `unclear_para` | I am looking for somewhere to eat for three on Saturday. The place should be cheap and in the centre. |
| 1 | `clear_specific` | I am looking for a restaurant for three on Saturday. The place should be cheap and in the centre. It has to be a restaurant, not a cafe or a pub. |
| 1 | `clear_general` | I am looking for a restaurant for three on Saturday. The place should be cheap and in the centre. A restaurant, a cafe or a pub would all be fine. |

### `car`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need a car for two days from Thursday. It should be cheap, and the pick-up should be in the west. |
| 0 | `unclear_para` | I need something to drive for two days from Thursday. It should be cheap, and the pick-up should be in the west. |
| 0 | `clear_specific` | I need a car for two days from Thursday. It should be cheap, and the pick-up should be in the west. It has to be a car, not a van or a minibus. |
| 0 | `clear_general` | I need a car for two days from Thursday. It should be cheap, and the pick-up should be in the west. A car, a van or a minibus would all be fine. |
| 1 | `unclear_word` | I need a car for three days from Sunday. A moderate price is fine, and the pick-up should be in the north. |
| 1 | `unclear_para` | I need something to drive for three days from Sunday. A moderate price is fine, and the pick-up should be in the north. |
| 1 | `clear_specific` | I need a car for three days from Sunday. A moderate price is fine, and the pick-up should be in the north. It has to be a car, not a van or a minibus. |
| 1 | `clear_general` | I need a car for three days from Sunday. A moderate price is fine, and the pick-up should be in the north. A car, a van or a minibus would all be fine. |

### `taxi`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need a taxi for four people on Tuesday. A moderate price is fine, and the pick-up is in the north. |
| 0 | `unclear_para` | I need a ride for four people on Tuesday. A moderate price is fine, and the pick-up is in the north. |
| 0 | `clear_specific` | I need a taxi for four people on Tuesday. A moderate price is fine, and the pick-up is in the north. It has to be a taxi, not a minibus or a limousine. |
| 0 | `clear_general` | I need a taxi for four people on Tuesday. A moderate price is fine, and the pick-up is in the north. A taxi, a minibus or a limousine would all be fine. |
| 1 | `unclear_word` | I need a taxi for four people on Sunday. It should be cheap, and the pick-up is in the west. |
| 1 | `unclear_para` | I need a ride for four people on Sunday. It should be cheap, and the pick-up is in the west. |
| 1 | `clear_specific` | I need a taxi for four people on Sunday. It should be cheap, and the pick-up is in the west. It has to be a taxi, not a minibus or a limousine. |
| 1 | `clear_general` | I need a taxi for four people on Sunday. It should be cheap, and the pick-up is in the west. A taxi, a minibus or a limousine would all be fine. |

### `doctor`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need to see a doctor about a sore throat on Thursday, just for me. I would like to go in the evening, somewhere in the centre. |
| 0 | `unclear_para` | I need to see someone about a sore throat on Thursday, just for me. I would like to go in the evening, somewhere in the centre. |
| 0 | `clear_specific` | I need to see a doctor about a sore throat on Thursday, just for me. I would like to go in the evening, somewhere in the centre. It has to be a doctor, not a nurse practitioner or a pharmacist. |
| 0 | `clear_general` | I need to see a doctor about a sore throat on Thursday, just for me. I would like to go in the evening, somewhere in the centre. A doctor, a nurse practitioner or a pharmacist would all be fine. |
| 1 | `unclear_word` | I need to see a doctor about a sore throat on Wednesday, just for me. I would like to go in the evening, somewhere in the south. |
| 1 | `unclear_para` | I need to see someone about a sore throat on Wednesday, just for me. I would like to go in the evening, somewhere in the south. |
| 1 | `clear_specific` | I need to see a doctor about a sore throat on Wednesday, just for me. I would like to go in the evening, somewhere in the south. It has to be a doctor, not a nurse practitioner or a pharmacist. |
| 1 | `clear_general` | I need to see a doctor about a sore throat on Wednesday, just for me. I would like to go in the evening, somewhere in the south. A doctor, a nurse practitioner or a pharmacist would all be fine. |

### `school`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I am looking for a school that teaches English for two people, starting on Tuesday. A moderate price is fine, and the lessons should be in the north. |
| 0 | `unclear_para` | I am looking for somewhere that teaches English for two people, starting on Tuesday. A moderate price is fine, and the lessons should be in the north. |
| 0 | `clear_specific` | I am looking for a school that teaches English for two people, starting on Tuesday. A moderate price is fine, and the lessons should be in the north. It has to be a school, not a college or an academy. |
| 0 | `clear_general` | I am looking for a school that teaches English for two people, starting on Tuesday. A moderate price is fine, and the lessons should be in the north. A school, a college or an academy would all be fine. |
| 1 | `unclear_word` | I am looking for a school that teaches English for three people, starting on Monday. A moderate price is fine, and the lessons should be in the west. |
| 1 | `unclear_para` | I am looking for somewhere that teaches English for three people, starting on Monday. A moderate price is fine, and the lessons should be in the west. |
| 1 | `clear_specific` | I am looking for a school that teaches English for three people, starting on Monday. A moderate price is fine, and the lessons should be in the west. It has to be a school, not a college or an academy. |
| 1 | `clear_general` | I am looking for a school that teaches English for three people, starting on Monday. A moderate price is fine, and the lessons should be in the west. A school, a college or an academy would all be fine. |

### `bike`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need a bike for one day from Thursday. I am happy to pay a lot, and the pick-up should be in the south. |
| 0 | `unclear_para` | I need something to ride for one day from Thursday. I am happy to pay a lot, and the pick-up should be in the south. |
| 0 | `clear_specific` | I need a bike for one day from Thursday. I am happy to pay a lot, and the pick-up should be in the south. It has to be a bike, not an e-bike or a scooter. |
| 0 | `clear_general` | I need a bike for one day from Thursday. I am happy to pay a lot, and the pick-up should be in the south. A bike, an e-bike or a scooter would all be fine. |
| 1 | `unclear_word` | I need a bike for four days from Tuesday. It should be cheap, and the pick-up should be in the east. |
| 1 | `unclear_para` | I need something to ride for four days from Tuesday. It should be cheap, and the pick-up should be in the east. |
| 1 | `clear_specific` | I need a bike for four days from Tuesday. It should be cheap, and the pick-up should be in the east. It has to be a bike, not an e-bike or a scooter. |
| 1 | `clear_general` | I need a bike for four days from Tuesday. It should be cheap, and the pick-up should be in the east. A bike, an e-bike or a scooter would all be fine. |

### `boat`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need a boat for three hours on Monday. I am happy to pay a lot, and I want to leave from the west. |
| 0 | `unclear_para` | I need something to take out on the water for three hours on Monday. I am happy to pay a lot, and I want to leave from the west. |
| 0 | `clear_specific` | I need a boat for three hours on Monday. I am happy to pay a lot, and I want to leave from the west. It has to be a boat, not a punt or a kayak. |
| 0 | `clear_general` | I need a boat for three hours on Monday. I am happy to pay a lot, and I want to leave from the west. A boat, a punt or a kayak would all be fine. |
| 1 | `unclear_word` | I need a boat for three hours on Saturday. A moderate price is fine, and I want to leave from the south. |
| 1 | `unclear_para` | I need something to take out on the water for three hours on Saturday. A moderate price is fine, and I want to leave from the south. |
| 1 | `clear_specific` | I need a boat for three hours on Saturday. A moderate price is fine, and I want to leave from the south. It has to be a boat, not a punt or a kayak. |
| 1 | `clear_general` | I need a boat for three hours on Saturday. A moderate price is fine, and I want to leave from the south. A boat, a punt or a kayak would all be fine. |

### `letter`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need to send a letter to three people by Tuesday. A moderate price is fine, and the language should be French. |
| 0 | `unclear_para` | I need to send something in writing to three people by Tuesday. A moderate price is fine, and the language should be French. |
| 0 | `clear_specific` | I need to send a letter to three people by Tuesday. A moderate price is fine, and the language should be French. It has to be a letter, not an email or a fax. |
| 0 | `clear_general` | I need to send a letter to three people by Tuesday. A moderate price is fine, and the language should be French. A letter, an email or a fax would all be fine. |
| 1 | `unclear_word` | I need to send a letter to three people by Thursday. A moderate price is fine, and the language should be French. |
| 1 | `unclear_para` | I need to send something in writing to three people by Thursday. A moderate price is fine, and the language should be French. |
| 1 | `clear_specific` | I need to send a letter to three people by Thursday. A moderate price is fine, and the language should be French. It has to be a letter, not an email or a fax. |
| 1 | `clear_general` | I need to send a letter to three people by Thursday. A moderate price is fine, and the language should be French. A letter, an email or a fax would all be fine. |

### `coffee`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I want to arrange coffee for a meeting of three people on Saturday morning. A moderate price is fine, and the meeting is in the north. |
| 0 | `unclear_para` | I want to arrange something warm to drink for a meeting of three people on Saturday morning. A moderate price is fine, and the meeting is in the north. |
| 0 | `clear_specific` | I want to arrange coffee for a meeting of three people on Saturday morning. A moderate price is fine, and the meeting is in the north. It has to be coffee, not tea or hot chocolate. |
| 0 | `clear_general` | I want to arrange coffee for a meeting of three people on Saturday morning. A moderate price is fine, and the meeting is in the north. Coffee, tea or hot chocolate would all be fine. |
| 1 | `unclear_word` | I want to arrange coffee for a meeting of five people on Monday morning. I am happy to pay a lot, and the meeting is in the north. |
| 1 | `unclear_para` | I want to arrange something warm to drink for a meeting of five people on Monday morning. I am happy to pay a lot, and the meeting is in the north. |
| 1 | `clear_specific` | I want to arrange coffee for a meeting of five people on Monday morning. I am happy to pay a lot, and the meeting is in the north. It has to be coffee, not tea or hot chocolate. |
| 1 | `clear_general` | I want to arrange coffee for a meeting of five people on Monday morning. I am happy to pay a lot, and the meeting is in the north. Coffee, tea or hot chocolate would all be fine. |

### `camera`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I want to hire a camera for one day from Sunday. I am happy to pay a lot, and the pick-up should be in the centre. |
| 0 | `unclear_para` | I want to hire something to take pictures or video with for one day from Sunday. I am happy to pay a lot, and the pick-up should be in the centre. |
| 0 | `clear_specific` | I want to hire a camera for one day from Sunday. I am happy to pay a lot, and the pick-up should be in the centre. It has to be a camera, not a camcorder or a webcam. |
| 0 | `clear_general` | I want to hire a camera for one day from Sunday. I am happy to pay a lot, and the pick-up should be in the centre. A camera, a camcorder or a webcam would all be fine. |
| 1 | `unclear_word` | I want to hire a camera for four days from Tuesday. I am happy to pay a lot, and the pick-up should be in the north. |
| 1 | `unclear_para` | I want to hire something to take pictures or video with for four days from Tuesday. I am happy to pay a lot, and the pick-up should be in the north. |
| 1 | `clear_specific` | I want to hire a camera for four days from Tuesday. I am happy to pay a lot, and the pick-up should be in the north. It has to be a camera, not a camcorder or a webcam. |
| 1 | `clear_general` | I want to hire a camera for four days from Tuesday. I am happy to pay a lot, and the pick-up should be in the north. A camera, a camcorder or a webcam would all be fine. |

### `hotel`

| Scenario | Kind | Traveller text |
|---|---|---|
| 0 | `unclear_word` | I need a hotel for one person from Sunday. The place should be cheap and in the east. |
| 0 | `unclear_para` | I need a place to stay for one person from Sunday. The place should be cheap and in the east. |
| 0 | `clear_specific` | I need a hotel for one person from Sunday. The place should be cheap and in the east. It has to be a hotel, not a guesthouse or a hostel. |
| 0 | `clear_general` | I need a hotel for one person from Sunday. The place should be cheap and in the east. A hotel, a guesthouse or a hostel would all be fine. |
| 1 | `unclear_word` | I need a hotel for one person from Tuesday. The place should be expensive and in the east. |
| 1 | `unclear_para` | I need a place to stay for one person from Tuesday. The place should be expensive and in the east. |
| 1 | `clear_specific` | I need a hotel for one person from Tuesday. The place should be expensive and in the east. It has to be a hotel, not a guesthouse or a hostel. |
| 1 | `clear_general` | I need a hotel for one person from Tuesday. The place should be expensive and in the east. A hotel, a guesthouse or a hostel would all be fine. |

## 6. pairs.json

```json
{
 "seed": 20261112,
 "rule": "the candidates in the order of ROUND10-EXPERIMENT-PLAN.md H that pass checks 1 and 2 and are not in RULE_D_EXCLUDED, at most 16; if fewer than 12 remain, H does not run",
 "checked": [
  {
   "pair": "table",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "room",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "restaurant",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "car",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "taxi",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "doctor",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "gym",
   "failed": [],
   "excluded": "a pool or a yoga studio is not \"a gym\""
  },
  {
   "pair": "school",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "bike",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "apartment",
   "failed": [],
   "excluded": "\"an apartment\" excludes \"a house\", and a studio is a kind of apartment"
  },
  {
   "pair": "office",
   "failed": [],
   "excluded": "\"office\" is not the everyday word for a job; the frame and the days are also unnatural"
  },
  {
   "pair": "movie",
   "failed": [],
   "excluded": "a movie does not include a series"
  },
  {
   "pair": "boat",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "truck",
   "failed": [],
   "excluded": "in a British setting \"van\" is the general word, and a trailer is not a vehicle"
  },
  {
   "pair": "letter",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "call",
   "failed": [],
   "excluded": "a call does not include a message"
  },
  {
   "pair": "coffee",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "camera",
   "failed": [],
   "excluded": null
  },
  {
   "pair": "box",
   "failed": [],
   "excluded": "weak by the same rule: \"a box\" does not include an envelope or a tube"
  },
  {
   "pair": "flowers",
   "failed": [],
   "excluded": "weak by the same rule: \"flowers\" does not include a plant or a wreath"
  }
 ],
 "chosen": [
  "table",
  "room",
  "restaurant",
  "car",
  "taxi",
  "doctor",
  "school",
  "bike",
  "boat",
  "letter",
  "coffee",
  "camera"
 ],
 "value_changes": {
  "boat": [
   "ferry",
   "punt",
   "a ferry is not hired by the hour and cannot be taken out; review of 2026-11-12"
  ]
 },
 "calibration": {
  "pair": "hotel",
  "failed": []
 },
 "pairs": {
  "table": {
   "collision": "table",
   "others": [
    "booth",
    "bar seat"
   ],
   "service": "table",
   "neutral": "open_floor",
   "nouns": [
    "a table",
    "a booth",
    "a bar seat"
   ],
   "word": "a table",
   "para": "somewhere to sit",
   "request": "I need {thing} for {size} on {day}.",
   "constraint": "The restaurant should be {price} and in the {place}.",
   "size": {
    "field": "people",
    "values": [
     "1",
     "2"
    ],
    "phrases": [
     "one",
     "two"
    ]
   },
   "price": {
    "field": "pricerange",
    "values": [
     "cheap",
     "moderate",
     "expensive"
    ],
    "phrases": [
     "cheap",
     "moderately priced",
     "expensive"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "table booking assistant",
   "role": "traveller"
  },
  "room": {
   "collision": "room",
   "others": [
    "suite",
    "apartment"
   ],
   "service": "room",
   "neutral": "lodging_unit",
   "nouns": [
    "a room",
    "a suite",
    "an apartment"
   ],
   "word": "a room",
   "para": "somewhere to sleep",
   "request": "I need {thing} for {size} from {day}.",
   "constraint": "The place should be {price} and in the {place}.",
   "size": {
    "field": "people",
    "values": [
     "1",
     "2",
     "3"
    ],
    "phrases": [
     "one person",
     "two people",
     "three people"
    ]
   },
   "price": {
    "field": "pricerange",
    "values": [
     "cheap",
     "moderate",
     "expensive"
    ],
    "phrases": [
     "cheap",
     "moderately priced",
     "expensive"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "room booking assistant",
   "role": "traveller"
  },
  "restaurant": {
   "collision": "restaurant",
   "others": [
    "cafe",
    "pub"
   ],
   "service": "restaurant",
   "neutral": "dining_venue",
   "nouns": [
    "a restaurant",
    "a cafe",
    "a pub"
   ],
   "word": "a restaurant",
   "para": "somewhere to eat",
   "request": "I am looking for {thing} for {size} on {day}.",
   "constraint": "The place should be {price} and in the {place}.",
   "size": {
    "field": "people",
    "values": [
     "2",
     "3",
     "4",
     "5",
     "6"
    ],
    "phrases": [
     "two",
     "three",
     "four",
     "five",
     "six"
    ]
   },
   "price": {
    "field": "pricerange",
    "values": [
     "cheap",
     "moderate",
     "expensive"
    ],
    "phrases": [
     "cheap",
     "moderately priced",
     "expensive"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "restaurant booking assistant",
   "role": "traveller"
  },
  "car": {
   "collision": "car",
   "others": [
    "van",
    "minibus"
   ],
   "service": "car",
   "neutral": "private_vehicle",
   "nouns": [
    "a car",
    "a van",
    "a minibus"
   ],
   "word": "a car",
   "para": "something to drive",
   "request": "I need {thing} for {size} from {day}.",
   "constraint": "{price}, and the pick-up should be in the {place}.",
   "size": {
    "field": "days",
    "values": [
     "1",
     "2",
     "3",
     "4"
    ],
    "phrases": [
     "one day",
     "two days",
     "three days",
     "four days"
    ]
   },
   "price": {
    "field": "price",
    "values": [
     "low",
     "moderate",
     "high"
    ],
    "phrases": [
     "It should be cheap",
     "A moderate price is fine",
     "I am happy to pay a lot"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "car booking assistant",
   "role": "traveller"
  },
  "taxi": {
   "collision": "taxi",
   "others": [
    "minibus",
    "limousine"
   ],
   "service": "taxi",
   "neutral": "metered_vehicle",
   "nouns": [
    "a taxi",
    "a minibus",
    "a limousine"
   ],
   "word": "a taxi",
   "para": "a ride",
   "request": "I need {thing} for {size} on {day}.",
   "constraint": "{price}, and the pick-up is in the {place}.",
   "size": {
    "field": "people",
    "values": [
     "2",
     "3",
     "4"
    ],
    "phrases": [
     "two people",
     "three people",
     "four people"
    ]
   },
   "price": {
    "field": "price",
    "values": [
     "low",
     "moderate",
     "high"
    ],
    "phrases": [
     "It should be cheap",
     "A moderate price is fine",
     "I am happy to pay a lot"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "taxi booking assistant",
   "role": "traveller"
  },
  "doctor": {
   "collision": "doctor",
   "others": [
    "nurse practitioner",
    "pharmacist"
   ],
   "service": "doctor",
   "neutral": "licensed_physician",
   "nouns": [
    "a doctor",
    "a nurse practitioner",
    "a pharmacist"
   ],
   "word": "a doctor",
   "para": "someone",
   "request": "I need to see {thing} about a sore throat on {day}, {size}.",
   "constraint": "I would like to go in the {price}, somewhere in the {place}.",
   "size": {
    "field": "people",
    "values": [
     "1",
     "2",
     "3"
    ],
    "phrases": [
     "just for me",
     "for me and my son",
     "for me and my two sons"
    ]
   },
   "price": {
    "field": "time",
    "values": [
     "morning",
     "afternoon",
     "evening"
    ],
    "phrases": [
     "morning",
     "afternoon",
     "evening"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday"
    ]
   },
   "assistant": "doctor appointment assistant",
   "role": "traveller"
  },
  "school": {
   "collision": "school",
   "others": [
    "college",
    "academy"
   ],
   "service": "school",
   "neutral": "education_provider",
   "nouns": [
    "a school",
    "a college",
    "an academy"
   ],
   "word": "a school that teaches English",
   "para": "somewhere that teaches English",
   "request": "I am looking for {thing} for {size}, starting on {day}.",
   "constraint": "{price}, and the lessons should be in the {place}.",
   "size": {
    "field": "people",
    "values": [
     "1",
     "2",
     "3"
    ],
    "phrases": [
     "one person",
     "two people",
     "three people"
    ]
   },
   "price": {
    "field": "fees",
    "values": [
     "low",
     "moderate",
     "high"
    ],
    "phrases": [
     "It should be cheap",
     "A moderate price is fine",
     "I am happy to pay a lot"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday"
    ]
   },
   "assistant": "school enrolment assistant",
   "role": "traveller"
  },
  "bike": {
   "collision": "bike",
   "others": [
    "e-bike",
    "scooter"
   ],
   "service": "bike",
   "neutral": "pedal_cycle",
   "nouns": [
    "a bike",
    "an e-bike",
    "a scooter"
   ],
   "word": "a bike",
   "para": "something to ride",
   "request": "I need {thing} for {size} from {day}.",
   "constraint": "{price}, and the pick-up should be in the {place}.",
   "size": {
    "field": "days",
    "values": [
     "1",
     "2",
     "3",
     "4"
    ],
    "phrases": [
     "one day",
     "two days",
     "three days",
     "four days"
    ]
   },
   "price": {
    "field": "price",
    "values": [
     "low",
     "moderate",
     "high"
    ],
    "phrases": [
     "It should be cheap",
     "A moderate price is fine",
     "I am happy to pay a lot"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "bike booking assistant",
   "role": "traveller"
  },
  "boat": {
   "collision": "boat",
   "others": [
    "punt",
    "kayak"
   ],
   "service": "boat",
   "neutral": "private_vessel",
   "nouns": [
    "a boat",
    "a punt",
    "a kayak"
   ],
   "word": "a boat",
   "para": "something to take out on the water",
   "request": "I need {thing} for {size} on {day}.",
   "constraint": "{price}, and I want to leave from the {place}.",
   "size": {
    "field": "hours",
    "values": [
     "1",
     "2",
     "3",
     "4"
    ],
    "phrases": [
     "one hour",
     "two hours",
     "three hours",
     "four hours"
    ]
   },
   "price": {
    "field": "price",
    "values": [
     "low",
     "moderate",
     "high"
    ],
    "phrases": [
     "It should be cheap",
     "A moderate price is fine",
     "I am happy to pay a lot"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "boat booking assistant",
   "role": "traveller"
  },
  "letter": {
   "collision": "letter",
   "others": [
    "email",
    "fax"
   ],
   "service": "letter",
   "neutral": "postal_item",
   "nouns": [
    "a letter",
    "an email",
    "a fax"
   ],
   "word": "a letter",
   "para": "something in writing",
   "request": "I need to send {thing} to {size} by {day}.",
   "constraint": "{price}, and the language should be {place}.",
   "size": {
    "field": "recipients",
    "values": [
     "1",
     "2",
     "3"
    ],
    "phrases": [
     "one person",
     "two people",
     "three people"
    ]
   },
   "price": {
    "field": "price",
    "values": [
     "low",
     "moderate",
     "high"
    ],
    "phrases": [
     "It should be cheap",
     "A moderate price is fine",
     "I am happy to pay a lot"
    ]
   },
   "place": {
    "field": "language",
    "values": [
     "english",
     "french",
     "german",
     "spanish",
     "italian"
    ],
    "phrases": [
     "English",
     "French",
     "German",
     "Spanish",
     "Italian"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday"
    ]
   },
   "assistant": "letter sending assistant",
   "role": "customer"
  },
  "coffee": {
   "collision": "coffee",
   "others": [
    "tea",
    "hot chocolate"
   ],
   "service": "coffee",
   "neutral": "bean_brew",
   "nouns": [
    "coffee",
    "tea",
    "hot chocolate"
   ],
   "word": "coffee",
   "para": "something warm to drink",
   "request": "I want to arrange {thing} for a meeting of {size} on {day} morning.",
   "constraint": "{price}, and the meeting is in the {place}.",
   "size": {
    "field": "people",
    "values": [
     "2",
     "3",
     "4",
     "5",
     "6"
    ],
    "phrases": [
     "two people",
     "three people",
     "four people",
     "five people",
     "six people"
    ]
   },
   "price": {
    "field": "price",
    "values": [
     "low",
     "moderate",
     "high"
    ],
    "phrases": [
     "It should be cheap",
     "A moderate price is fine",
     "I am happy to pay a lot"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "coffee ordering assistant",
   "role": "traveller"
  },
  "camera": {
   "collision": "camera",
   "others": [
    "camcorder",
    "webcam"
   ],
   "service": "camera",
   "neutral": "photo_device",
   "nouns": [
    "a camera",
    "a camcorder",
    "a webcam"
   ],
   "word": "a camera",
   "para": "something to take pictures or video with",
   "request": "I want to hire {thing} for {size} from {day}.",
   "constraint": "{price}, and the pick-up should be in the {place}.",
   "size": {
    "field": "days",
    "values": [
     "1",
     "2",
     "3",
     "4"
    ],
    "phrases": [
     "one day",
     "two days",
     "three days",
     "four days"
    ]
   },
   "price": {
    "field": "price",
    "values": [
     "low",
     "moderate",
     "high"
    ],
    "phrases": [
     "It should be cheap",
     "A moderate price is fine",
     "I am happy to pay a lot"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "camera hire assistant",
   "role": "traveller"
  },
  "hotel": {
   "collision": "hotel",
   "others": [
    "guesthouse",
    "hostel"
   ],
   "service": "hotel",
   "neutral": "serviced_property",
   "nouns": [
    "a hotel",
    "a guesthouse",
    "a hostel"
   ],
   "word": "a hotel",
   "para": "a place to stay",
   "request": "I need {thing} for {size} from {day}.",
   "constraint": "The place should be {price} and in the {place}.",
   "size": {
    "field": "people",
    "values": [
     "1",
     "2",
     "3"
    ],
    "phrases": [
     "one person",
     "two people",
     "three people"
    ]
   },
   "price": {
    "field": "pricerange",
    "values": [
     "cheap",
     "moderate",
     "expensive"
    ],
    "phrases": [
     "cheap",
     "moderately priced",
     "expensive"
    ]
   },
   "place": {
    "field": "area",
    "values": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ],
    "phrases": [
     "centre",
     "north",
     "south",
     "east",
     "west"
    ]
   },
   "days": {
    "field": "day",
    "values": [
     "monday",
     "tuesday",
     "wednesday",
     "thursday",
     "friday",
     "saturday",
     "sunday"
    ],
    "phrases": [
     "Monday",
     "Tuesday",
     "Wednesday",
     "Thursday",
     "Friday",
     "Saturday",
     "Sunday"
    ]
   },
   "assistant": "hotel booking assistant",
   "role": "traveller"
  }
 },
 "requests_per_read": 1920,
 "calibration_requests_per_read": 160,
 "requests_sha256": "200df66153104739eed6ad5c6d01afcd78f92447a30702451e03ab3f5ebf9557"
}
```
