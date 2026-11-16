## The service run: search failures under the original tool and the two rewrites (post hoc)

No model call. Stored first calls of the steering run (one per request and tool). Fit rule: the frozen briefsearch.fits on the corpus goal record. Rates: share of valid reads. Change: steered minus original, points, 95% cluster bootstrap over requests (2,000 draws, seed 20261112).

Groups: {"open": {"n": 448, "only_guesthouses_fit": 254, "only_hotels_fit": 136, "both_fit": 58, "none_fits": 0}, "guesthouse": {"n": 47, "a_guesthouse_fits": 47}, "specific": {"n": 59, "a_hotel_fits": 59}}

| Agent | Set | Failure | Original | Rewrite H | Change H [95%] | Rewrite G | Change G [95%] |
|---|---|---|---|---|---|---|---|
| sonnet | open (448) | hotel-only failure | 10.3% (46/448) | 14.1% (63/448) | +3.8 [+2.0, +5.6] | 15.8% (71/448) | +5.6 [+3.6, +7.8] |
| sonnet | open (448) | guesthouse-only failure | 0.0% (0/448) | 0.0% (0/448) | +0.0 [+0.0, +0.0] | 3.1% (14/448) | +3.1 [+1.6, +4.9] |
| sonnet | open (448) | any failure | 10.3% (46/448) | 14.1% (63/448) | +3.8 [+2.0, +5.6] | 19.0% (85/448) | +8.7 [+6.0, +11.4] |
| sonnet | guesthouse (47) | hotel-only failure | 48.9% (23/47) | 59.6% (28/47) | +10.6 [+2.1, +21.3] | 68.1% (32/47) | +19.1 [+8.5, +31.9] |
| sonnet | specific (59) | guesthouse-only failure | 0.0% (0/59) | 0.0% (0/59) | +0.0 [+0.0, +0.0] | 5.1% (3/59) | +5.1 [+0.0, +11.9] |
| haiku | open (448) | hotel-only failure | 3.1% (14/448) | 18.3% (82/448) | +15.2 [+11.8, +18.8] | 16.1% (72/448) | +12.9 [+9.8, +16.3] |
| haiku | open (448) | guesthouse-only failure | 0.0% (0/448) | 0.0% (0/448) | +0.0 [+0.0, +0.0] | 5.6% (25/448) | +5.6 [+3.6, +7.6] |
| haiku | open (448) | any failure | 3.1% (14/448) | 18.3% (82/448) | +15.2 [+11.8, +18.8] | 21.7% (97/448) | +18.5 [+15.0, +22.3] |
| haiku | guesthouse (47) | hotel-only failure | 12.8% (6/47) | 74.5% (35/47) | +61.7 [+46.8, +74.5] | 66.0% (31/47) | +53.2 [+38.3, +66.0] |
| haiku | specific (59) | guesthouse-only failure | 0.0% (0/59) | 0.0% (0/59) | +0.0 [+0.0, +0.0] | 33.9% (20/59) | +33.9 [+22.0, +45.8] |

### Rewrite H: texts that mention a later search (word check; no person checked it)

- sonnet: 554 reads; 83 with text; 2 mention a later search; 0 invalid reads (two or more calls make a read invalid)
  - ers_sonnet-MUL2552-th-1: "Since the traveller has not stated any preferences yet, I'll search with no constraints. The type is also unspecified, so I'll start with hotels as suggested."
  - ers_sonnet-MUL2286-th-1: "Unlike when the traveller states a type, no accommodation type was mentioned here, so I'll search hotels first as suggested."
- haiku: 554 reads; 254 with text; 43 mention a later search; 0 invalid reads (two or more calls make a read invalid)
  - ers_haiku-PMUL0245-th-1: 'Let me work through the traveller\'s final requirements for the hotel search.\n\n- Internet: they need free wifi, so "yes".\n- Price range: cheap.\n- Stars: 4.\n- Parking: the traveller first said they didn\'t need parking, then later asked for free parking with the suggested hotel. The final stated prefer'
  - ers_haiku-PMUL0424-th-1: 'Looking at the request: moderately priced, free parking required. "Condo style hotel" is not one of the accommodation types (hotel or guesthouse), and the traveller did not explicitly say hotel or guesthouse, so type is left unrestricted in the sense of no stated preference. Per the guidance, I\'ll s'
  - ers_haiku-PMUL0391-th-1: 'Traveller wants a hotel in the north, no specific requirements otherwise. Price, stars, parking, internet not stated, so null. Type not stated: search hotels first.'
  - ers_haiku-MUL2288-th-1: "I'd be happy to help find a hotel. Since you haven't mentioned your hotel requirements (area, price range, stars, type, parking, or internet), I'll search with those open, but first I need to confirm: do you have any preferences for the hotel's area, price range, star rating, accommodation type, par"
  - ers_haiku-PMUL1757-th-1: "No conversation context beyond this request, so only internet is stated: free wifi required. Everything else is unspecified (null), and accommodation type is unstated so I'll search hotels first."
  - ers_haiku-PMUL2842-th-1: "No requirements were given beyond wanting a hotel quickly, so I'll leave everything open except the accommodation type, which I'll set to hotel as the first search."
  - ers_haiku-PMUL0309-th-1: "The traveller wants a hotel near the restaurant in the centre. No price range, stars, parking, or internet requirements were stated, so those are null. Accommodation type was not specified, so I'll search hotels first."
  - ers_haiku-PMUL1885-th-1: "Searching for cheap hotels in the north of Cambridge. The traveller did not state an accommodation type, stars, parking, or internet requirements, so those are null, and I'll start with hotels as the suggested first search."
