## Forward release test: option values in the Sonnet answers (post hoc)

No model call. Stored tool calls of the forward release test, Sonnet, one answer per prefix and arm. Arm t0: the original tool; arm tedit: the edited tool ("any" renamed dont_care; at least one value in each list). The system text names "any" in both arms.

- t0: answers 554; answers with any 59; answers with dont_care (any spelling) 0; answers with quoted dont_care 0; answers with an empty list 0; no single call 1; fields with any {"internet": 12, "parking": 15, "area": 21, "pricerange": 17, "type": 3, "stars": 3}; fields with dont_care {}
- tedit: answers 554; answers with any 0; answers with dont_care (any spelling) 64; answers with quoted dont_care 22; answers with an empty list 0; answers changed by the mapping back 42; changes in the type field 1; hotel value changed by the mapping back 0; fields with any {}; fields with dont_care {"pricerange": 18, "stars": 3, "parking": 16, "internet": 15, "area": 20, "type": 3}

Variant: the 22 tedit answers with a quoted dont_care count as missing (2,000 draws, registered seed, level 98.75%):
- open: 432 pairs, change +3.94 [+1.39, +6.71], unresolved
- specific: 56 pairs, change +1.79 [+0.00, +7.14], unresolved
- model decision: hold
