"""E3 (PROTOCOL.md): the draft annotator prompt on the 123 P4 dialogues, 3 reads, claude-opus-5-5 at effort medium.

The system prompt is codebook.md (the task, the codebook, and the output schema). The user turn is one dialogue in the
P4 format. The annotator sees no gold value and no model output.
Run:  python3 -I annot/e3.py estimate
"""
import importlib.util
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True  # the P4 and P5 modules sit in folders that E3 must not write to

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
PROTOTYPES = EXPLORE.parent
sys.path.insert(0, str(EXPLORE / "lib"))
import anth  # noqa: E402

CODEBOOK = HERE / "codebook.md"
MODEL, EFFORT, MAX_TOKENS = "claude-opus-5-5", "medium", 16000
READS = (1, 2, 3)
FIELDS = ("name", "area", "pricerange", "stars", "type", "parking", "internet")
SUBTAGS = {"clear": ("SELECTION",), "ambiguous": ("WORD_COLLISION", "feature_question", "relaxation", "vague_word"),
           "outside_form": ()}
UNCLEAR_SENTENCE = (" If the traveller's words allow more than one reasonable reading for a field, write \"unclear\" for "
                    "that field instead of choosing a reading.")
OFFER_SENTENCE = " An option that the traveller only accepted from the assistant's offers is not a requirement."


def load_p5():
    """The P5 module, which also loads the P4 module as its attribute p4."""
    saved = sys.argv
    sys.argv = [saved[0], str(anth.DATA)]  # P4 and P5 read the data folder from sys.argv when they are imported
    try:
        spec = importlib.util.spec_from_file_location("p5_unclear_run", PROTOTYPES / "p5_unclear" / "run.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.argv = saved
    return module


def p_main(p5):
    """The p_main prompt of PLAN.md SI-05: the P5 prompt with the "unclear" switch off, plus the offer sentence (SI-02)."""
    assert UNCLEAR_SENTENCE in p5.SYSTEM, "the P5 prompt changed"
    return p5.SYSTEM.replace(UNCLEAR_SENTENCE, OFFER_SENTENCE)


def hotel_names():
    return sorted(h["name"] for h in json.loads((anth.DATA / "hotel_db.json").read_text()))


def allowed(p4):
    return {"name": tuple(hotel_names()), **{f: tuple(v) for f, v in p4.ALLOWED.items()}}


def p4_ids():
    return sorted({json.loads(line)["id"] for line in (PROTOTYPES / "p4_multiwoz" / "raw.jsonl").read_text().splitlines()})


def complete_turn_quotes(text, data, exempt):
    """Quoted strings that equal a complete MultiWOZ turn. PLAN.md SI-01 keeps complete turns out of the codebook."""
    norm = lambda s: s.strip().lower().rstrip(".?!")  # noqa: E731
    turns = {norm(t["text"]) for d in data.values() for t in d["log"]}
    return sorted({q for q in re.findall(r'"([^"\n]+)"', text) if norm(q) in turns and norm(q) not in exempt})


def custom_id(dialogue_id, read):
    return f"{dialogue_id.removesuffix('.json')}_r{read}"


def parse_id(cid):
    stem, read = cid.rsplit("_r", 1)
    return f"{stem}.json", int(read)


def build():
    data = anth.multiwoz()
    p5 = load_p5()
    p4 = p5.p4
    assert tuple(p4.FIELDS) == FIELDS[1:], p4.FIELDS
    ids = p4_ids()
    assert len(ids) == 123, len(ids)
    anth.assert_outside_trackp(ids, data)
    prompt = CODEBOOK.read_text()
    assert p_main(p5) in prompt, "codebook.md does not quote the p_main prompt exactly"
    exempt = {"any", "null", "unclear", *FIELDS, *SUBTAGS, *(v for vs in allowed(p4).values() for v in vs)}
    quoted = complete_turn_quotes(prompt, data, exempt)
    assert not quoted, f"codebook.md quotes complete MultiWOZ turns: {quoted}"
    return [anth.request(custom_id(i, k), MODEL, EFFORT, MAX_TOKENS, user=p4.dialogue_text(data[i]), system=prompt)
            for i in ids for k in READS]


if __name__ == "__main__":
    anth.main("e3", build, planning_out=4000, account="anthropic_old")
