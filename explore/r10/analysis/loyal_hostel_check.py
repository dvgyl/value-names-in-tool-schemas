"""Check whether the word "hostel" changes any clear or strict group of the clear rule (no model call, no network).

Runs the fixed rule r10/analysis/clear_rule.py on its six sets and lists every matched sentence whose match uses
"hostel". Then it relabels each dialogue with a copy of the rule whose guesthouse kind words omit "hostel", and counts
the dialogues whose main or strict label changes.
Usage (from explore/): python3 -I r10/analysis/loyal_hostel_check.py. It prints the counts.
This file is a copy of the project script hostel_check.py with the paths of the study folder; the results are the same.
"""
import pathlib
import re
import sys

EXPLORE = str(pathlib.Path(__file__).resolve().parents[2])  # explore/
sys.path.insert(0, EXPLORE + "/r10/analysis")
import clear_rule as cr  # noqa: E402

data, sets = cr.sets()

# A copy of the compiled patterns without "hostel" in the guesthouse kind words.
kind2 = dict(cr.KIND)
kind2["guesthouse"] = kind2["guesthouse"].replace("|hostels?", "")
assert "hostel" not in kind2["guesthouse"]
compiled2 = {(want, name): re.compile(tpl.format(want=kind2[want], other=kind2[cr.OTHER[want]]), re.I)
             for want in kind2 for name, _, tpl in cr.PATTERNS}


def sentence_matches2(sentence):
    if sentence.rstrip().endswith("?") and cr.VENUE_QUESTION.search(sentence):
        return []
    out = []
    for (want, name), rx in compiled2.items():
        if any(not cr._guarded(name, want, sentence, m) for m in rx.finditer(sentence)):
            out.append((want, name))
    return out


def matches2(d, prefix_end=None):
    out = []
    for i, text in cr.traveller_turns(d, prefix_end):
        for s in cr.sentences(text):
            out += [(i, s, want, name) for want, name in sentence_matches2(s)]
    return out


for name, units in sets.items():
    hostel_sentences, changed_main, changed_strict = [], 0, 0
    for d, end in units:
        found = cr.matches(data[d], end)
        found2 = matches2(data[d], end)
        hostel_sentences += [(d, s) for _, s, _, _ in found if re.search(r"hostel", s, re.I)]
        if cr.label_of(found) != cr.label_of(found2):
            changed_main += 1
        if cr.label_of(found, cr.STRICT_FAMILIES) != cr.label_of(found2, cr.STRICT_FAMILIES):
            changed_strict += 1
    print(f"{name}: {len(units)} units; matched sentences with 'hostel': {len(hostel_sentences)}; "
          f"main labels changed: {changed_main}; strict labels changed: {changed_strict}")
    for d, s in hostel_sentences:
        print(f"    {d}: {s}")
