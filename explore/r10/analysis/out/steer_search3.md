# The steering runs when the agent can search again (R10-23)

Exploratory, fixed in the protocol before the run. Changes: cell − t0 in points, paired by prefix, 95% cluster bootstrap over prefixes. Repair band ±3 points.

## Predictions

| Prediction | Result per model |
|---|---|
| Q1 | {"haiku": "holds", "sol": "holds", "luna": "holds"} |
| Q2 | {"haiku": "holds", "sol": "holds", "luna": "holds"} |
| Q3 | {"haiku": "holds", "sol": "holds", "luna": "holds"} |
| Q4 | {"haiku": "holds", "sol": "holds", "luna": "holds"} |
| Q5 | {"haiku": "holds"} |

## Exclusion: first search and last search

| Model | Set and exclusion | Cell | First: rate | First: change [95%] | Last: rate | Last: change [95%] | Category | (Last − first) − t0 [95%] |
|---|---|---|---|---|---|---|---|---|
| haiku | open | hotel-only | t0 | 2.0% (9/447) | | 1.1% (5/448) | | | |
| haiku | open | hotel-only | h1 | 19.4% (87/448) | +17.2 [+13.6, +20.8] | 12.3% (55/448) | +11.2 [+8.3, +14.3] (up 51, down 1) | persists | -6.3 [-8.9, -3.8] |
| haiku | open | hotel-only | g1 | 15.2% (68/448) | +13.0 [+9.8, +16.3] | 15.0% (67/448) | +13.8 [+10.5, +17.4] (up 63, down 1) | persists | +0.7 [-0.4, +1.8] |
| haiku | open | guesthouse-only | t0 | 0.0% (0/447) | | 0.0% (0/448) | | | |
| haiku | open | guesthouse-only | h1 | 0.0% (0/448) | +0.0 [+0.0, +0.0] | 0.0% (0/448) | +0.0 [+0.0, +0.0] (up 0, down 0) | repaired | +0.0 [+0.0, +0.0] |
| haiku | open | guesthouse-only | g1 | 5.6% (25/448) | +5.6 [+3.6, +7.8] | 2.7% (12/448) | +2.7 [+1.3, +4.2] (up 12, down 0) | unresolved | -2.9 [-4.7, -1.3] |
| haiku | open | either | t0 | 2.0% (9/447) | | 1.1% (5/448) | | | |
| haiku | open | either | h1 | 19.4% (87/448) | +17.2 [+13.6, +20.8] | 12.3% (55/448) | +11.2 [+8.3, +14.3] (up 51, down 1) | persists | -6.3 [-8.9, -3.8] |
| haiku | open | either | g1 | 20.8% (93/448) | +18.6 [+15.0, +22.1] | 17.6% (79/448) | +16.5 [+13.2, +20.3] (up 75, down 1) | persists | -2.2 [-4.3, -0.2] |
| sol | open | hotel-only | t0 | 17.2% (77/447) | | 17.0% (76/447) | | | |
| sol | open | hotel-only | h1 | 42.8% (190/444) | +25.5 [+21.4, +29.6] | 34.0% (151/444) | +16.9 [+13.3, +20.5] (up 76, down 1) | persists | -8.6 [-11.3, -6.1] |
| sol | open | hotel-only | g1 | 46.4% (207/446) | +29.2 [+25.2, +33.7] | 46.2% (206/446) | +29.2 [+25.2, +33.7] (up 130, down 0) | persists | +0.0 [-0.7, +0.7] |
| sol | open | guesthouse-only | t0 | 0.0% (0/447) | | 0.0% (0/447) | | | |
| sol | open | guesthouse-only | h1 | 0.0% (0/444) | +0.0 [+0.0, +0.0] | 0.0% (0/444) | +0.0 [+0.0, +0.0] (up 0, down 0) | repaired | +0.0 [+0.0, +0.0] |
| sol | open | guesthouse-only | g1 | 6.1% (27/446) | +6.1 [+4.0, +8.3] | 0.2% (1/446) | +0.2 [+0.0, +0.7] (up 1, down 0) | repaired | -5.8 [-8.1, -3.8] |
| sol | open | either | t0 | 17.2% (77/447) | | 17.0% (76/447) | | | |
| sol | open | either | h1 | 42.8% (190/444) | +25.5 [+21.4, +29.6] | 34.0% (151/444) | +16.9 [+13.3, +20.5] (up 76, down 1) | persists | -8.6 [-11.3, -6.1] |
| sol | open | either | g1 | 52.5% (234/446) | +35.3 [+30.8, +39.6] | 46.4% (207/446) | +29.4 [+25.4, +33.9] (up 131, down 0) | persists | -5.8 [-8.1, -3.6] |
| sol | guesthouse | hotel-only | t0 | 73.9% (34/46) | | 73.9% (34/46) | | | |
| sol | guesthouse | hotel-only | h1 | 93.6% (44/47) | +19.6 [+8.7, +30.4] | 87.2% (41/47) | +13.0 [+4.3, +21.7] (up 6, down 0) | persists | -6.5 [-13.0, +0.0] |
| sol | guesthouse | hotel-only | g1 | 78.7% (37/47) | +4.3 [+0.0, +10.9] | 78.7% (37/47) | +4.3 [+0.0, +10.9] (up 2, down 0) | unresolved | +0.0 [+0.0, +0.0] |
| sol | specific | guesthouse-only | t0 | 0.0% (0/59) | | 0.0% (0/59) | | | |
| sol | specific | guesthouse-only | h1 | 0.0% (0/59) | +0.0 [+0.0, +0.0] | 0.0% (0/59) | +0.0 [+0.0, +0.0] (up 0, down 0) | repaired | +0.0 [+0.0, +0.0] |
| sol | specific | guesthouse-only | g1 | 5.1% (3/59) | +5.1 [+0.0, +11.9] | 1.7% (1/59) | +1.7 [+0.0, +5.1] (up 1, down 0) | unresolved | -3.4 [-8.5, +0.0] |
| luna | open | hotel-only | t0 | 8.4% (75/895) | | 8.4% (75/895) | | | |
| luna | open | hotel-only | h1 | 35.1% (314/895) | +26.7 [+22.8, +30.7] | 30.9% (277/895) | +22.5 [+19.0, +26.3] (up 120, down 1) | persists | -4.1 [-6.1, -2.5] |
| luna | open | hotel-only | g1 | 21.2% (190/896) | +12.8 [+9.9, +15.8] | 20.8% (186/896) | +12.4 [+9.6, +15.4] (up 69, down 0) | persists | -0.4 [-1.1, +0.1] |
| luna | open | guesthouse-only | t0 | 0.0% (0/895) | | 0.0% (0/895) | | | |
| luna | open | guesthouse-only | h1 | 0.0% (0/895) | +0.0 [+0.0, +0.0] | 0.1% (1/895) | +0.1 [+0.0, +0.3] (up 1, down 0) | repaired | +0.1 [+0.0, +0.3] |
| luna | open | guesthouse-only | g1 | 10.2% (91/896) | +10.2 [+7.6, +12.8] | 4.8% (43/896) | +4.8 [+3.0, +6.8] (up 23, down 0) | persists | -5.4 [-7.4, -3.5] |
| luna | open | either | t0 | 8.4% (75/895) | | 8.4% (75/895) | | | |
| luna | open | either | h1 | 35.1% (314/895) | +26.7 [+22.8, +30.7] | 31.1% (278/895) | +22.7 [+19.1, +26.5] (up 121, down 1) | persists | -4.0 [-6.0, -2.3] |
| luna | open | either | g1 | 31.4% (281/896) | +23.0 [+19.4, +26.6] | 25.6% (229/896) | +17.2 [+14.0, +20.6] (up 92, down 0) | persists | -5.8 [-7.8, -3.8] |
| luna | guesthouse | hotel-only | t0 | 38.3% (36/94) | | 38.3% (36/94) | | | |
| luna | guesthouse | hotel-only | h1 | 79.8% (75/94) | +41.5 [+27.7, +55.3] | 70.2% (66/94) | +31.9 [+19.1, +44.7] (up 18, down 1) | persists | -9.6 [-18.1, -3.2] |
| luna | guesthouse | hotel-only | g1 | 58.5% (55/94) | +20.2 [+9.6, +31.9] | 56.4% (53/94) | +18.1 [+6.4, +29.8] (up 11, down 2) | persists | -2.1 [-5.3, +0.0] |
| luna | specific | guesthouse-only | t0 | 0.0% (0/118) | | 0.0% (0/118) | | | |
| luna | specific | guesthouse-only | h1 | 1.7% (2/118) | +1.7 [+0.0, +5.1] | 1.7% (2/118) | +1.7 [+0.0, +5.1] (up 1, down 0) | unresolved | +0.0 [+0.0, +0.0] |
| luna | specific | guesthouse-only | g1 | 35.6% (42/118) | +35.6 [+22.9, +47.5] | 25.4% (30/118) | +25.4 [+15.3, +36.4] (up 17, down 0) | persists | -10.2 [-18.6, -2.5] |

## Panel on the open set (description; mean over the models of each prefix)

| Exclusion | Cell | Search | Prefixes | Change [95%] |
|---|---|---|---:|---|
| hotel-only | h1 | first | 448 | +23.0 [+20.3, +25.7] |
| hotel-only | h1 | last | 448 | +16.8 [+14.4, +19.2] |
| hotel-only | g1 | first | 448 | +18.3 [+16.0, +20.5] |
| hotel-only | g1 | last | 448 | +18.4 [+16.2, +20.8] |
| either | h1 | first | 448 | +23.0 [+20.3, +25.7] |
| either | h1 | last | 448 | +16.9 [+14.5, +19.3] |
| either | g1 | first | 448 | +25.5 [+23.2, +28.0] |
| either | g1 | last | 448 | +21.0 [+18.7, +23.4] |

## Behaviour (descriptions)

- haiku: conversation status {"complete": 1344}
  - t0: searches per conversation {"0": 36, "1": 406, "2": 6}; searched again 6/448; widened after a one-type first search 4/28; switched to the other type 0/28; open set, first-search exclusion (either) {"n": 9, "searched_again": 4, "widened": 4, "last_still_excludes": 5}; tells after a first hotel-only exclusion 7/9; tells after a last hotel-only exclusion 3/5; last search is a guesthouse-only exclusion 0; last type {"None": 424, "hotel": 18, "guesthouse": 6}
  - h1: searches per conversation {"0": 54, "1": 345, "2": 49}; searched again 49/448; widened after a one-type first search 36/184; switched to the other type 9/184; open set, first-search exclusion (either) {"n": 87, "searched_again": 34, "widened": 26, "last_still_excludes": 54}; tells after a first hotel-only exclusion 57/87; tells after a last hotel-only exclusion 25/55; last search is a guesthouse-only exclusion 0; last type {"hotel": 130, "None": 299, "guesthouse": 19}
  - g1: searches per conversation {"0": 49, "1": 361, "2": 38}; searched again 38/448; widened after a one-type first search 23/219; switched to the other type 1/219; open set, first-search exclusion (either) {"n": 93, "searched_again": 21, "widened": 16, "last_still_excludes": 77}; tells after a first hotel-only exclusion 26/68; tells after a last hotel-only exclusion 24/67; last search is a guesthouse-only exclusion 12; last type {"guesthouse": 57, "hotel": 140, "None": 251}
- sol: conversation status {"complete": 1654, "failed": 8}
  - t0: searches per conversation {"1": 550, "2": 2}; searched again 2/552; widened after a one-type first search 1/231; switched to the other type 0/231; open set, first-search exclusion (either) {"n": 77, "searched_again": 1, "widened": 1, "last_still_excludes": 76}; tells after a first hotel-only exclusion 19/77; tells after a last hotel-only exclusion 18/76; last search is a guesthouse-only exclusion 0; last type {"hotel": 226, "None": 322, "guesthouse": 4}
  - h1: searches per conversation {"1": 506, "2": 44}; searched again 44/550; widened after a one-type first search 39/461; switched to the other type 3/461; open set, first-search exclusion (either) {"n": 190, "searched_again": 40, "widened": 37, "last_still_excludes": 151}; tells after a first hotel-only exclusion 79/190; tells after a last hotel-only exclusion 48/151; last search is a guesthouse-only exclusion 0; last type {"hotel": 405, "None": 128, "guesthouse": 17}
  - g1: searches per conversation {"0": 4, "1": 516, "2": 32}; searched again 32/552; widened after a one-type first search 29/542; switched to the other type 3/542; open set, first-search exclusion (either) {"n": 234, "searched_again": 27, "widened": 25, "last_still_excludes": 207}; tells after a first hotel-only exclusion 59/207; tells after a last hotel-only exclusion 58/206; last search is a guesthouse-only exclusion 1; last type {"hotel": 448, "None": 39, "guesthouse": 65}
- luna: conversation status {"complete": 3322, "failed": 2}
  - t0: searches per conversation {"0": 4, "1": 1100, "2": 3}; searched again 3/1107; widened after a one-type first search 1/247; switched to the other type 0/247; open set, first-search exclusion (either) {"n": 75, "searched_again": 0, "widened": 0, "last_still_excludes": 75}; tells after a first hotel-only exclusion 1/75; tells after a last hotel-only exclusion 1/75; last search is a guesthouse-only exclusion 0; last type {"None": 860, "hotel": 229, "guesthouse": 18}
  - h1: searches per conversation {"0": 4, "1": 1004, "2": 99}; searched again 99/1107; widened after a one-type first search 50/818; switched to the other type 10/818; open set, first-search exclusion (either) {"n": 314, "searched_again": 46, "widened": 29, "last_still_excludes": 277}; tells after a first hotel-only exclusion 59/314; tells after a last hotel-only exclusion 24/277; last search is a guesthouse-only exclusion 1; last type {"None": 337, "hotel": 697, "guesthouse": 73}
  - g1: searches per conversation {"0": 5, "1": 919, "2": 183, "3": 1}; searched again 184/1108; widened after a one-type first search 95/827; switched to the other type 14/827; open set, first-search exclusion (either) {"n": 281, "searched_again": 87, "widened": 47, "last_still_excludes": 227}; tells after a first hotel-only exclusion 12/190; tells after a last hotel-only exclusion 7/186; last search is a guesthouse-only exclusion 43; last type {"guesthouse": 287, "None": 373, "hotel": 448}

## Stored single-call references (description; other batches, the one-search text)

| Model | Run | Cell | Open set, hotel-only | Open set, either |
|---|---|---|---|---|
| haiku | ers_haiku | t0 | 3.3% (15/448) | 3.3% (15/448) |
| haiku | ers_haiku | h1 | 18.3% (82/448) | 18.3% (82/448) |
| haiku | ers_haiku | g1 | 16.1% (72/448) | 21.7% (97/448) |
| haiku | erm_haiku | h1 | 18.5% (83/448) | 18.5% (83/448) |
| haiku | erm_haiku | t0 | 2.9% (13/448) | 2.9% (13/448) |
| haiku | erm_haiku | g1 | 16.5% (74/448) | 21.9% (98/448) |
| sol | era1_sol | t0 | 18.0% (161/896) | 18.0% (161/896) |
| luna | era1_luna | t0 | 9.5% (85/896) | 9.5% (85/896) |
