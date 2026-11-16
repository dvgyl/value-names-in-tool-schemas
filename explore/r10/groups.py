"""Dialogue groups and the two id asserts of round 10 (ACTION-PLAN.md section 2.5).

`groups(data)` gives the dialogue lists of experiments B, H and I and asserts every size. `write_ids()` writes
`r10/ids.json` once. `assert_unprotected` stops a run that reads a protected dialogue. `assert_new_text` stops a
constructed text that copies a sentence of a Track C or Track I item. This module reads MultiWOZ and item texts only.
It reads no answer and no model output.
"""
import json
import pathlib
import re
import sys

EXPLORE = pathlib.Path(__file__).resolve().parents[1]
for _sub in ("r10", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / _sub))
import gold  # noqa: E402
import textedit  # noqa: E402
import zruns  # noqa: E402
from gold import anth  # noqa: E402

IDS = EXPLORE / "r10" / "ids.json"
NATURAL = EXPLORE / "r9" / "natural" / "ids.json"
WAVE1 = EXPLORE / "main" / "wave1_ids.json"
SIZES = {"s1t": 994, "s3": 490, "s2": 545, "booked": 554, "ins": 233}
PARTS = ("ins_assistant_hotel", "ins_clean")
# The files whose item texts a constructed text must not copy: (path, how to read it, the keys that hold text).
ITEM_FILES = (
    (EXPLORE / "main" / "track_c" / "items.jsonl", "jsonl", ("text",)),
    (EXPLORE / "main" / "track_i" / "items.json", "json", ("text",)),
    (EXPLORE / "main" / "track_i" / "prompts.jsonl", "jsonl", ("user",)),
    (EXPLORE / "main" / "track_c_paraphrase" / "paraphrases.jsonl", "jsonl", ("text",)),
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
SPEAKER = re.compile(r"^(?:traveller|assistant|user|report)\s*:\s*", re.I)
MIN_WORDS = 4


def groups(data, verbose=True):
    """{"s1t", "s3", "s2", "booked", "ins", "ins_assistant_hotel", "ins_clean"} -> sorted lists of dialogue ids."""
    natural = json.loads(NATURAL.read_text())["groups"]
    out = {"s1t": natural["S1t"], "s3": natural["S3"], "s2": natural["S2"], "booked": list(zruns.groups(data).booked)}
    out["ins"] = [i for i in gold.dialogue_sets(data)["256"] if any(textedit.has_phrase(t) for t in gold.traveller(data[i]))]
    says = [i for i in out["ins"] if any(gold.WORD.search(t["text"]) for k, t in enumerate(data[i]["log"]) if k % 2)]
    out["ins_assistant_hotel"] = says
    out["ins_clean"] = [i for i in out["ins"] if i not in set(says)]
    assert {k: len(out[k]) for k in SIZES} == SIZES, {k: len(out[k]) for k in SIZES}
    assert len(says) + len(out["ins_clean"]) == 233 and says
    if verbose:
        print(f"ins: {len(out['ins'])} dialogues; an assistant turn says hotel in {len(says)}; "
              f"no turn says hotel in {len(out['ins_clean'])}")
    return out


def write_ids(data=None):
    """Write r10/ids.json once. A rerun checks that the rule gives the same lists and never overwrites the file."""
    g = groups(data or anth.multiwoz())
    if IDS.exists():
        assert json.loads(IDS.read_text()) == g, "the rule gives other lists than r10/ids.json; the file stays as it is"
        return IDS
    with open(IDS, "x") as f:  # "x" fails if the file exists
        json.dump(g, f, indent=1)
    return IDS


def protected(data):
    """The id sets of the four protected lists."""
    val, test = anth.splits()
    wave1 = json.loads(WAVE1.read_text())
    return {"pool": set(anth.trackp_pool(data)), "validation": set(val), "test": set(test), "gate": set(wave1["gate"]),
            "wave1_pool": set(wave1["pool"])}


def assert_unprotected(ids, data):
    """Raise ValueError if an id is in the Track P pool, the validation or test split, or `gate` or `pool` of wave1."""
    lists = protected(data)
    hits = {name: sorted(set(ids) & s) for name, s in lists.items() if set(ids) & s}
    if hits:
        raise ValueError("protected dialogue ids: " + "; ".join(f"{n}: {len(v)} (first {v[0]})" for n, v in hits.items()))


def sentences(text):
    """The sentences of a text with 4 or more words, lower case, without punctuation at the ends."""
    out = []
    for part in SENTENCE_SPLIT.split(text):
        part = SPEAKER.sub("", part.strip()).strip(" \t\"'.,;:!?")
        if len(part.split()) >= MIN_WORDS:
            out.append(" ".join(part.lower().split()))
    return out


def item_sentences():
    """The sentences of the item texts and inputs of Track C, Track I and the Track C paraphrase arm."""
    found = set()
    for path, kind, keys in ITEM_FILES:
        if not path.exists():  # repository copy: the main-study item files are withheld (README.md, section 8)
            continue
        rows = json.loads(path.read_text()) if kind == "json" else map(json.loads, path.read_text().splitlines())
        for row in rows:
            for key in keys:
                found.update(sentences(row[key]))
    if not found and not getattr(item_sentences, "noted", False):  # repository copy: the item files are withheld
        item_sentences.noted = True
        print("note: the main-study item files are withheld; assert_new_text checks nothing", file=sys.stderr)
    return found


def assert_new_text(texts):
    """Raise ValueError if a sentence of 4 or more words of a text occurs in an item text of the files in ITEM_FILES."""
    known = item_sentences()
    copied = sorted({s for text in texts for s in sentences(text) if s in known})
    if copied:
        raise ValueError(f"{len(copied)} copied sentence(s), first: {copied[0]!r}")


if __name__ == "__main__":
    print(write_ids())
