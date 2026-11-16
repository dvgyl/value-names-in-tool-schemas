"""Amendment R10-7 (PROTOCOL.md): the returned flag. Exploratory, for the paper.

Question: when the search tool says that its type filter alone made the result empty, does the agent widen the search
or tell the traveller? Step 2 of experiment A (stage2.py) kept the stage-1 system text, which says "Call search_hotels one
time, and write no other text". This run removes that limit.

Sample (`sample`): the stage-1 rows of era1_<model> (Sonnet, Haiku, Opus), arm t0, whose call is a valid search, whose
type keeps hotel and not guesthouse (gold.hides_guesthouse), and whose relaxation check is flagged
(briefsearch.relaxation: the search finds no venue, and the same search without its type finds 1 or more venues).
Requests (`build`): as stage2.requests, with three changes. (1) The top-level system text is `multi_system("t0")`: the
two sentences that limit the agent to one call are replaced (MULTI_ASK, MULTI_END). (2) The stored assistant content is
sent without its thinking blocks (only Opus has some), because a changed system text binds them to another conversation
prefix, and the API then rejects them (synchronous call) or drops them (batch). (3) Two arms per stage-1 row, in the same
batch: "plain" (the tool result of stage2.py, unchanged) and "flag" (the same text, a line break, and `flag_line(n)`,
n = the count of the search without its type; all n venues are guesthouses). The R10-2 operator message stays.
Outcome (`classify`): "widen" (a new search whose type does not hide guesthouses), "kept" (a new search with the
hotel-only filter), "tell" (a text answer that matches GUEST_OR_LIMITED of a_analyze.py or TYPE_QUESTION), "other"
(another text answer), "neither" (no call and no text), "invalid". Recovery = widen or tell.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import models  # noqa: E402
import stage2  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

AMENDMENT = "### R10-7 "
MODELS = ("sonnet", "haiku", "opus")
ARMS = ("plain", "flag")
ACCOUNT = "anthropic_r9b"
MAX_BOUND = 8.00  # USD per run (pilot or batch)

# The new sentences of the agent's system text (also used by amendment R10-8, r10/turns.py).
MULTI_ASK = "Search for hotels that meet the traveller's requirements with the tool search_hotels."
MULTI_END = "You may call search_hotels more than one time. When you are ready, answer the traveller."


def multi_system(arm="t0"):
    """The tool system text of experiment A (tools.tool_system) without the limit to one call."""
    text = zforms.once(tools.FORM_TEXT[arm], tools.ASK_OLD, MULTI_ASK)
    return zforms.once(text, tools.END_OLD, MULTI_END)


def flag_line(n):
    """The one line that the flag arm adds after the tool result. n >= 1."""
    assert n >= 1
    if n == 1:
        return "No hotel matches. 1 guesthouse matches the other filters; the type filter alone removed it."
    return f"No hotel matches. {n} guesthouses match the other filters; the type filter alone removed them."


NEW_TEXTS = (MULTI_ASK, MULTI_END, flag_line(1), flag_line(2))

# The outcome word rules. GUEST_OR_LIMITED is the rule of r10/analysis/a_analyze.py (copied, not changed). TYPE_QUESTION
# is new: a sentence that ends with "?" and asks about the type of place.
GUEST_OR_LIMITED = re.compile(r"guest ?houses?|only hotels|hotels only", re.I)
TYPE_QUESTION = re.compile(r"\b(type|kind|sort)s? of (place|accommodation|lodging|property|properties|stay)\b|"
                           r"\bother (types?|kinds?) of\b|\bbed and breakfasts?\b|\bb ?& ?bs?\b|"
                           r"\b(instead of|other than|not just|not only|besides) (a )?hotels?\b", re.I)
QUESTION = re.compile(r"[^.?!\n]*\?")
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}


def asks_type(text):
    return any(TYPE_QUESTION.search(q) for q in QUESTION.findall(text or ""))


def sample(model, db=None):
    """[(stage-1 row, parsed fields, n)] of era1_<model>, sorted by custom_id. n = the count without the type."""
    db = db or gold.hotel_db()
    out = []
    for row in stage2.rows_of(EXPLORE / f"era1_{model}", "raw"):
        if row.get("type", "succeeded") != "succeeded" or "-t0-" not in row["custom_id"]:
            continue
        kind, fields = tools.parse_call(row, "t0")
        if kind != "search" or not gold.hides_guesthouse(fields.get("type")):
            continue
        rel = bs.relaxation(fields, db)
        if not rel["flag"]:
            continue
        removed = bs.search(db, {**fields, "type": None})
        assert all(v["type"] == "guesthouse" for v in removed), row["custom_id"]
        out.append((row, fields, rel["count_without_type"]))
    return sorted(out, key=lambda x: x[0]["custom_id"])


def strip_thinking(content):
    return [b for b in content if b.get("type") not in ("thinking", "redacted_thinking")]


def build(name, model, reads, data, g):
    """Arms plain and flag for each sampled stage-1 row (one read each; `reads` must be 1)."""
    assert reads == 1 and model in MODELS, (name, model, reads)
    db = gold.hotel_db()
    stage1 = stage2.build_stage1(model, f"era1_{model}")
    system = multi_system("t0")
    out = []
    for row, fields, n in sample(model, db):
        result = json.dumps(bs.result_rows(bs.search(db, fields)))
        assert json.loads(result)["total"] == 0
        first = stage1[row["custom_id"]]["params"]
        call = row["tool_calls"][0]
        _, did, _, read = row["custom_id"].split("-")
        for arm in ARMS:
            content = result if arm == "plain" else result + "\n" + flag_line(n)
            messages = [first["messages"][0], {"role": "assistant", "content": strip_thinking(row["content"])},
                        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": call["id"],
                                                      "content": content}]},
                        {"role": "system", "content": stage2.STEP2_TEXT}]
            out.append(models.request(model, f"{name}-{did}-{arm}-{read}", None, system, None,
                                      tools=tools.TOOLS["t0"], messages=messages, cell=arm))
    return out


def classify(row):
    """(kind, details) of one step-2 answer row; kind as in the module text."""
    if row.get("type", "succeeded") != "succeeded":
        return "invalid", "failed"
    if row.get("stop") in CUT:
        return "invalid", "cut"
    if row.get("tool_calls"):
        kind, fields = tools.parse_call(row, "t0")
        if kind != "search":
            return "invalid", f"call {kind}"
        return ("kept" if gold.hides_guesthouse(fields.get("type")) else "widen"), fields.get("type")
    text = (row.get("text") or "").strip()
    if not text:
        return "neither", None
    guest, question = bool(GUEST_OR_LIMITED.search(text)), asks_type(text)
    if guest or question:
        return "tell", {"word": guest, "type_question": question}
    return "other", None


def amendment_text():
    import runs
    text = runs.PROTOCOL.read_text().split(runs.AMEND, 1)[-1]
    if AMENDMENT not in text:
        return None
    body = text.split(AMENDMENT, 1)[1]
    ends = [i for i in (body.find("\n## "), body.find("\n### ")) if i >= 0]
    return AMENDMENT + (body[:min(ends)] if ends else body)


def check_amendment():
    """R10-7 is in PROTOCOL.md under the round-10 amendments and holds each new text verbatim."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    missing = [t for t in (MULTI_ASK, MULTI_END, flag_line(1), flag_line(2).replace("2 guesthouses", "N guesthouses"))
               if t not in flat]
    if missing:
        sys.exit(f"Not run. R10-7 does not hold the text {missing[0]!r} verbatim.")


if __name__ == "__main__":
    db = gold.hotel_db()
    for m in MODELS:
        s = sample(m, db)
        print(m, len(s), "rows,", len({r["custom_id"].split("-")[1] for r, _, _ in s}), "dialogues,",
              sum(any(b.get("type") == "thinking" for b in r["content"]) for r, _, _ in s), "with a thinking block")
    print(multi_system("t0"))
